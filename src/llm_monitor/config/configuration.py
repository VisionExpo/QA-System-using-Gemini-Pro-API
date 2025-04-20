"""
Configuration module for LLM Monitor
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from ..utils.logger import default_logger


@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_dir: str = "logs"
    console_log: bool = True
    file_log: bool = True
    log_format: str = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    track_latency: bool = True
    track_tokens: bool = True
    track_inputs: bool = True
    track_outputs: bool = True
    metrics_file: str = "metrics.json"


@dataclass
class ModelConfig:
    """Model configuration"""
    model_name: str = "default-model"
    model_type: str = "llm"
    api_key_env: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)


@dataclass
class FineTuningConfig:
    """Fine-tuning configuration"""
    enabled: bool = False
    base_model: str = "mistralai/Mistral-7B-v0.1"
    output_dir: str = "models/fine_tuned"
    use_qlora: bool = True
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    num_epochs: int = 3
    learning_rate: float = 3e-4
    batch_size: int = 4
    micro_batch_size: int = 1


@dataclass
class Config:
    """Main configuration"""
    project_name: str = "llm_monitor"
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    fine_tuning: FineTuningConfig = field(default_factory=FineTuningConfig)
    artifacts_dir: str = "artifacts"


class ConfigurationManager:
    """
    Configuration manager for LLM Monitor
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        default_logger.info(f"Configuration loaded from {config_path}")
    
    def _load_config(self) -> Config:
        """
        Load configuration from file
        
        Returns:
            Config object
        """
        if not os.path.exists(self.config_path):
            default_logger.warning(f"Configuration file not found at {self.config_path}. Using default configuration.")
            return Config()
        
        try:
            with open(self.config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            
            # Create Config object
            config = Config(
                project_name=config_dict.get("project_name", "llm_monitor"),
                artifacts_dir=config_dict.get("artifacts_dir", "artifacts")
            )
            
            # Load logging config
            if "logging" in config_dict:
                logging_dict = config_dict["logging"]
                config.logging = LoggingConfig(
                    log_level=logging_dict.get("log_level", "INFO"),
                    log_dir=logging_dict.get("log_dir", "logs"),
                    console_log=logging_dict.get("console_log", True),
                    file_log=logging_dict.get("file_log", True),
                    log_format=logging_dict.get("log_format", "%(asctime)s | %(levelname)s | %(module)s | %(message)s")
                )
            
            # Load models config
            if "models" in config_dict:
                for model_name, model_dict in config_dict["models"].items():
                    monitoring_dict = model_dict.get("monitoring", {})
                    monitoring_config = MonitoringConfig(
                        enabled=monitoring_dict.get("enabled", True),
                        track_latency=monitoring_dict.get("track_latency", True),
                        track_tokens=monitoring_dict.get("track_tokens", True),
                        track_inputs=monitoring_dict.get("track_inputs", True),
                        track_outputs=monitoring_dict.get("track_outputs", True),
                        metrics_file=monitoring_dict.get("metrics_file", "metrics.json")
                    )
                    
                    model_config = ModelConfig(
                        model_name=model_name,
                        model_type=model_dict.get("model_type", "llm"),
                        api_key_env=model_dict.get("api_key_env"),
                        timeout=model_dict.get("timeout", 30),
                        max_retries=model_dict.get("max_retries", 3),
                        monitoring=monitoring_config
                    )
                    
                    config.models[model_name] = model_config
            
            # Load fine-tuning config
            if "fine_tuning" in config_dict:
                ft_dict = config_dict["fine_tuning"]
                config.fine_tuning = FineTuningConfig(
                    enabled=ft_dict.get("enabled", False),
                    base_model=ft_dict.get("base_model", "mistralai/Mistral-7B-v0.1"),
                    output_dir=ft_dict.get("output_dir", "models/fine_tuned"),
                    use_qlora=ft_dict.get("use_qlora", True),
                    lora_r=ft_dict.get("lora_r", 8),
                    lora_alpha=ft_dict.get("lora_alpha", 16),
                    lora_dropout=ft_dict.get("lora_dropout", 0.05),
                    num_epochs=ft_dict.get("num_epochs", 3),
                    learning_rate=ft_dict.get("learning_rate", 3e-4),
                    batch_size=ft_dict.get("batch_size", 4),
                    micro_batch_size=ft_dict.get("micro_batch_size", 1)
                )
            
            return config
            
        except Exception as e:
            default_logger.error(f"Error loading configuration: {str(e)}")
            return Config()
    
    def get_config(self) -> Config:
        """
        Get configuration
        
        Returns:
            Config object
        """
        return self.config
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """
        Get configuration for a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelConfig object or None if not found
        """
        return self.config.models.get(model_name)
    
    def save_config(self, config: Config):
        """
        Save configuration to file
        
        Args:
            config: Config object to save
        """
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Convert config to dictionary
        config_dict = {
            "project_name": config.project_name,
            "artifacts_dir": config.artifacts_dir,
            "logging": {
                "log_level": config.logging.log_level,
                "log_dir": config.logging.log_dir,
                "console_log": config.logging.console_log,
                "file_log": config.logging.file_log,
                "log_format": config.logging.log_format
            },
            "models": {},
            "fine_tuning": {
                "enabled": config.fine_tuning.enabled,
                "base_model": config.fine_tuning.base_model,
                "output_dir": config.fine_tuning.output_dir,
                "use_qlora": config.fine_tuning.use_qlora,
                "lora_r": config.fine_tuning.lora_r,
                "lora_alpha": config.fine_tuning.lora_alpha,
                "lora_dropout": config.fine_tuning.lora_dropout,
                "num_epochs": config.fine_tuning.num_epochs,
                "learning_rate": config.fine_tuning.learning_rate,
                "batch_size": config.fine_tuning.batch_size,
                "micro_batch_size": config.fine_tuning.micro_batch_size
            }
        }
        
        # Add models
        for model_name, model_config in config.models.items():
            config_dict["models"][model_name] = {
                "model_type": model_config.model_type,
                "api_key_env": model_config.api_key_env,
                "timeout": model_config.timeout,
                "max_retries": model_config.max_retries,
                "monitoring": {
                    "enabled": model_config.monitoring.enabled,
                    "track_latency": model_config.monitoring.track_latency,
                    "track_tokens": model_config.monitoring.track_tokens,
                    "track_inputs": model_config.monitoring.track_inputs,
                    "track_outputs": model_config.monitoring.track_outputs,
                    "metrics_file": model_config.monitoring.metrics_file
                }
            }
        
        # Save to file
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
            
            default_logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            default_logger.error(f"Error saving configuration: {str(e)}")
            raise
