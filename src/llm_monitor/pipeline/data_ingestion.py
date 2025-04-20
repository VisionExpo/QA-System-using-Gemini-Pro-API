"""
Data ingestion pipeline for LLM Monitor
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..utils.logger import LLMLogger, default_logger


class DataIngestionPipeline:
    """
    Pipeline for data ingestion
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        output_dir: str = "artifacts/data",
        logger: Optional[LLMLogger] = None
    ):
        """
        Initialize data ingestion pipeline
        
        Args:
            data_dir: Directory containing raw data
            output_dir: Directory to save processed data
            logger: Custom logger instance
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.logger = logger or default_logger
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Data ingestion pipeline initialized. Data dir: {data_dir}, Output dir: {output_dir}")
    
    def ingest_json_data(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        filter_func: Optional[callable] = None,
        transform_func: Optional[callable] = None
    ) -> str:
        """
        Ingest JSON data
        
        Args:
            input_file: Input JSON file
            output_file: Output file name (default: same as input with timestamp)
            filter_func: Function to filter data
            transform_func: Function to transform data
            
        Returns:
            Path to the processed data file
        """
        self.logger.info(f"Ingesting JSON data from {input_file}")
        
        input_path = os.path.join(self.data_dir, input_file)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{filename}_{timestamp}.json"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            # Load input data
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded {len(data) if isinstance(data, list) else 'non-list'} items from {input_file}")
            
            # Apply filter if provided
            if filter_func and callable(filter_func) and isinstance(data, list):
                data = [item for item in data if filter_func(item)]
                self.logger.info(f"Filtered to {len(data)} items")
            
            # Apply transformation if provided
            if transform_func and callable(transform_func):
                data = transform_func(data)
                self.logger.info(f"Transformed data")
            
            # Save processed data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved processed data to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error ingesting JSON data: {str(e)}")
            raise
    
    def ingest_csv_data(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        filter_func: Optional[callable] = None,
        transform_func: Optional[callable] = None,
        **kwargs
    ) -> str:
        """
        Ingest CSV data
        
        Args:
            input_file: Input CSV file
            output_file: Output file name (default: same as input with timestamp)
            filter_func: Function to filter data
            transform_func: Function to transform data
            **kwargs: Additional arguments for pandas.read_csv
            
        Returns:
            Path to the processed data file
        """
        self.logger.info(f"Ingesting CSV data from {input_file}")
        
        input_path = os.path.join(self.data_dir, input_file)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{filename}_{timestamp}.csv"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            # Load input data
            df = pd.read_csv(input_path, **kwargs)
            
            self.logger.info(f"Loaded {len(df)} rows from {input_file}")
            
            # Apply filter if provided
            if filter_func and callable(filter_func):
                df = df[df.apply(filter_func, axis=1)]
                self.logger.info(f"Filtered to {len(df)} rows")
            
            # Apply transformation if provided
            if transform_func and callable(transform_func):
                df = transform_func(df)
                self.logger.info(f"Transformed data")
            
            # Save processed data
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Saved processed data to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error ingesting CSV data: {str(e)}")
            raise
    
    def convert_to_instruction_format(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        instruction_template: str = "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}",
        instruction_key: str = "instruction",
        input_key: str = "input",
        output_key: str = "output"
    ) -> str:
        """
        Convert data to instruction format for fine-tuning
        
        Args:
            input_file: Input JSON file
            output_file: Output file name (default: instruction_data with timestamp)
            instruction_template: Template for formatting instructions
            instruction_key: Key for instruction field
            input_key: Key for input field
            output_key: Key for output field
            
        Returns:
            Path to the processed data file
        """
        self.logger.info(f"Converting data to instruction format from {input_file}")
        
        input_path = os.path.join(self.data_dir, input_file)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"instruction_data_{timestamp}.json"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            # Load input data
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Input data must be a list of dictionaries")
            
            self.logger.info(f"Loaded {len(data)} items from {input_file}")
            
            # Convert to instruction format
            instruction_data = []
            
            for item in data:
                instruction = item.get(instruction_key, "")
                input_text = item.get(input_key, "")
                output_text = item.get(output_key, "")
                
                formatted_text = instruction_template.format(
                    instruction=instruction,
                    input=input_text,
                    output=output_text
                )
                
                instruction_data.append({
                    "text": formatted_text
                })
            
            # Save processed data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(instruction_data, f, indent=2)
            
            self.logger.info(f"Converted {len(instruction_data)} items to instruction format. Saved to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error converting to instruction format: {str(e)}")
            raise
