"""
Custom logging module for LLM Monitor
"""

import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class LLMLogger:
    """
    Custom logger for LLM monitoring and fine-tuning
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        log_filename: Optional[str] = None,
        module_name: str = "llm_monitor"
    ):
        """
        Initialize the logger
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_filename: Name of the log file (default: current date)
            module_name: Name of the module for the logger
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.module_name = module_name
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set log filename if not provided
        if log_filename is None:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            log_filename = f"{current_date}.log"
        
        self.log_filepath = os.path.join(log_dir, log_filename)
        
        # Configure logger
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(log_level)
        self.logger.handlers = []  # Clear existing handlers
        
        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
        )
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_filepath)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(log_level)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.info(f"Logger initialized. Logs will be saved to: {self.log_filepath}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def log_model_input(self, model_name: str, inputs: Dict[str, Any]):
        """
        Log model input for monitoring
        
        Args:
            model_name: Name of the model
            inputs: Model inputs
        """
        self.info(f"Model Input [{model_name}]: {inputs}")
    
    def log_model_output(self, model_name: str, outputs: Dict[str, Any], metrics: Optional[Dict[str, Any]] = None):
        """
        Log model output and metrics for monitoring
        
        Args:
            model_name: Name of the model
            outputs: Model outputs
            metrics: Performance metrics (latency, token usage, etc.)
        """
        self.info(f"Model Output [{model_name}]: {outputs}")
        
        if metrics:
            self.info(f"Model Metrics [{model_name}]: {metrics}")
    
    def log_exception(self, exception: Exception, context: Optional[str] = None):
        """
        Log exception with context
        
        Args:
            exception: Exception object
            context: Additional context information
        """
        if context:
            self.error(f"Exception in {context}: {str(exception)}")
        else:
            self.error(f"Exception: {str(exception)}")
        
        import traceback
        self.error(traceback.format_exc())


# Create a default logger instance
default_logger = LLMLogger()

# Convenience functions using the default logger
def debug(message: str):
    default_logger.debug(message)

def info(message: str):
    default_logger.info(message)

def warning(message: str):
    default_logger.warning(message)

def error(message: str):
    default_logger.error(message)

def critical(message: str):
    default_logger.critical(message)

def log_model_input(model_name: str, inputs: Dict[str, Any]):
    default_logger.log_model_input(model_name, inputs)

def log_model_output(model_name: str, outputs: Dict[str, Any], metrics: Optional[Dict[str, Any]] = None):
    default_logger.log_model_output(model_name, outputs, metrics)

def log_exception(exception: Exception, context: Optional[str] = None):
    default_logger.log_exception(exception, context)
