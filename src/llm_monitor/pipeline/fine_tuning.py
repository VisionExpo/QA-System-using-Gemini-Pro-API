"""
Fine-tuning pipeline for LLM Monitor
"""

import os
import subprocess
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from ..utils.logger import LLMLogger, default_logger
from ..components.fine_tuning import FineTuningConfig, FineTuningManager, DatasetPreparation


class FineTuningPipeline:
    """
    Pipeline for fine-tuning LLM models
    """
    
    def __init__(
        self,
        config: FineTuningConfig,
        data_dir: str = "artifacts/data",
        output_dir: Optional[str] = None,
        logger: Optional[LLMLogger] = None
    ):
        """
        Initialize fine-tuning pipeline
        
        Args:
            config: Fine-tuning configuration
            data_dir: Directory containing processed data
            output_dir: Directory to save fine-tuned models (default: from config)
            logger: Custom logger instance
        """
        self.config = config
        self.data_dir = data_dir
        self.output_dir = output_dir or config.output_dir
        self.logger = logger or default_logger
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize fine-tuning manager
        self.manager = FineTuningManager(config, logger)
        
        # Initialize dataset preparation
        self.dataset_prep = DatasetPreparation(data_dir, self.output_dir, logger)
        
        self.logger.info(f"Fine-tuning pipeline initialized for model: {config.base_model}")
    
    def prepare_dataset(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        dataset_type: str = "instruction",
        **kwargs
    ) -> str:
        """
        Prepare dataset for fine-tuning
        
        Args:
            input_file: Input data file
            output_file: Output file name (default: processed_{input_file})
            dataset_type: Type of dataset (instruction or chat)
            **kwargs: Additional arguments for dataset preparation
            
        Returns:
            Path to the processed dataset
        """
        self.logger.info(f"Preparing {dataset_type} dataset from {input_file}")
        
        if output_file is None:
            filename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"processed_{filename}.json"
        
        input_path = os.path.join(self.data_dir, input_file)
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if dataset_type == "instruction":
            self.dataset_prep.prepare_instruction_dataset(
                input_file=input_file,
                output_file=output_file,
                **kwargs
            )
        elif dataset_type == "chat":
            self.dataset_prep.prepare_chat_dataset(
                input_file=input_file,
                output_file=output_file,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")
        
        return os.path.join(self.output_dir, output_file)
    
    def generate_training_script(
        self,
        dataset_path: str,
        script_name: str = "train.py"
    ) -> str:
        """
        Generate training script
        
        Args:
            dataset_path: Path to the processed dataset
            script_name: Name of the training script
            
        Returns:
            Path to the training script
        """
        script_path = os.path.join(self.output_dir, script_name)
        self.manager.generate_training_script(dataset_path, script_path)
        return script_path
    
    def generate_inference_script(
        self,
        script_name: str = "inference.py"
    ) -> str:
        """
        Generate inference script
        
        Args:
            script_name: Name of the inference script
            
        Returns:
            Path to the inference script
        """
        script_path = os.path.join(self.output_dir, script_name)
        self.manager.generate_inference_script(script_path)
        return script_path
    
    def run_training(
        self,
        script_path: str,
        requirements: List[str] = None
    ) -> int:
        """
        Run training script
        
        Args:
            script_path: Path to the training script
            requirements: List of requirements to install before training
            
        Returns:
            Return code from the training process
        """
        self.logger.info(f"Running training script: {script_path}")
        
        # Install requirements if provided
        if requirements:
            req_file = os.path.join(self.output_dir, "requirements.txt")
            with open(req_file, 'w') as f:
                f.write("\n".join(requirements))
            
            self.logger.info(f"Installing requirements from {req_file}")
            subprocess.run(["pip", "install", "-r", req_file], check=True)
        
        # Run training script
        process = subprocess.run(["python", script_path], check=False)
        
        if process.returncode == 0:
            self.logger.info("Training completed successfully")
        else:
            self.logger.error(f"Training failed with return code {process.returncode}")
        
        return process.returncode
    
    def run_full_pipeline(
        self,
        input_file: str,
        dataset_type: str = "instruction",
        run_training: bool = True,
        requirements: List[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Run the full fine-tuning pipeline
        
        Args:
            input_file: Input data file
            dataset_type: Type of dataset (instruction or chat)
            run_training: Whether to run the training script
            requirements: List of requirements to install before training
            **kwargs: Additional arguments for dataset preparation
            
        Returns:
            Dictionary with paths to generated files
        """
        self.logger.info(f"Running full fine-tuning pipeline for {input_file}")
        
        # Prepare dataset
        dataset_path = self.prepare_dataset(
            input_file=input_file,
            dataset_type=dataset_type,
            **kwargs
        )
        
        # Generate training script
        train_script = self.generate_training_script(dataset_path)
        
        # Generate inference script
        inference_script = self.generate_inference_script()
        
        result = {
            "dataset": dataset_path,
            "train_script": train_script,
            "inference_script": inference_script,
            "model_dir": self.output_dir
        }
        
        # Run training if requested
        if run_training:
            return_code = self.run_training(train_script, requirements)
            result["training_success"] = (return_code == 0)
        
        return result
