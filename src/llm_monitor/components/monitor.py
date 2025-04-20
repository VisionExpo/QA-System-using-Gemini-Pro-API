"""
LLM Monitoring components
"""

import time
import json
import os
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime

from ..utils.logger import LLMLogger, default_logger

class LLMMonitor:
    """
    Monitor for LLM applications
    """
    
    def __init__(
        self,
        model_name: str,
        logger: Optional[LLMLogger] = None,
        log_dir: str = "logs/llm_monitor",
        metrics_file: str = "metrics.json",
        track_latency: bool = True,
        track_tokens: bool = True,
        track_inputs: bool = True,
        track_outputs: bool = True,
        input_processor: Optional[Callable] = None,
        output_processor: Optional[Callable] = None
    ):
        """
        Initialize LLM Monitor
        
        Args:
            model_name: Name of the model being monitored
            logger: Custom logger instance (uses default if None)
            log_dir: Directory to store monitoring logs
            metrics_file: File to store metrics data
            track_latency: Whether to track latency metrics
            track_tokens: Whether to track token usage
            track_inputs: Whether to track model inputs
            track_outputs: Whether to track model outputs
            input_processor: Function to process inputs before logging (for PII removal, etc.)
            output_processor: Function to process outputs before logging
        """
        self.model_name = model_name
        self.logger = logger or default_logger
        self.log_dir = log_dir
        self.metrics_file = os.path.join(log_dir, metrics_file)
        
        self.track_latency = track_latency
        self.track_tokens = track_tokens
        self.track_inputs = track_inputs
        self.track_outputs = track_outputs
        
        self.input_processor = input_processor
        self.output_processor = output_processor
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize metrics storage
        self.metrics_history = self._load_metrics_history()
        
        self.logger.info(f"LLM Monitor initialized for model: {model_name}")
    
    def _load_metrics_history(self) -> List[Dict[str, Any]]:
        """Load metrics history from file if it exists"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading metrics history: {str(e)}")
                return []
        return []
    
    def _save_metrics_history(self):
        """Save metrics history to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics history: {str(e)}")
    
    def _process_input(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process inputs using the input processor if available"""
        if self.input_processor and callable(self.input_processor):
            return self.input_processor(inputs)
        return inputs
    
    def _process_output(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process outputs using the output processor if available"""
        if self.output_processor and callable(self.output_processor):
            return self.output_processor(outputs)
        return outputs
    
    def monitor(self, func: Callable) -> Callable:
        """
        Decorator to monitor LLM function calls
        
        Args:
            func: Function to monitor
            
        Returns:
            Wrapped function with monitoring
        """
        def wrapper(*args, **kwargs):
            # Track start time for latency calculation
            start_time = time.time()
            
            # Process and log inputs
            inputs = kwargs.copy()
            if self.track_inputs:
                processed_inputs = self._process_input(inputs)
                self.logger.log_model_input(self.model_name, processed_inputs)
            
            # Call the original function
            try:
                result = func(*args, **kwargs)
                
                # Calculate metrics
                metrics = {}
                
                if self.track_latency:
                    latency = time.time() - start_time
                    metrics["latency"] = latency
                
                if self.track_tokens and hasattr(result, "usage"):
                    metrics["input_tokens"] = getattr(result.usage, "prompt_tokens", 0)
                    metrics["output_tokens"] = getattr(result.usage, "completion_tokens", 0)
                    metrics["total_tokens"] = getattr(result.usage, "total_tokens", 0)
                
                # Process and log outputs
                if self.track_outputs:
                    # Convert result to dict if it's not already
                    if not isinstance(result, dict):
                        if hasattr(result, "__dict__"):
                            output_dict = result.__dict__
                        else:
                            output_dict = {"result": str(result)}
                    else:
                        output_dict = result
                    
                    processed_outputs = self._process_output(output_dict)
                    self.logger.log_model_output(self.model_name, processed_outputs, metrics)
                
                # Store metrics with timestamp
                metric_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model_name,
                    "metrics": metrics
                }
                self.metrics_history.append(metric_entry)
                self._save_metrics_history()
                
                return result
                
            except Exception as e:
                self.logger.log_exception(e, f"Error in {self.model_name} execution")
                raise
        
        return wrapper
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of collected metrics
        
        Returns:
            Dictionary with metrics summary
        """
        if not self.metrics_history:
            return {"message": "No metrics collected yet"}
        
        # Calculate average latency
        latencies = [entry["metrics"].get("latency", 0) for entry in self.metrics_history 
                    if "latency" in entry["metrics"]]
        
        # Calculate token usage
        input_tokens = [entry["metrics"].get("input_tokens", 0) for entry in self.metrics_history 
                       if "input_tokens" in entry["metrics"]]
        
        output_tokens = [entry["metrics"].get("output_tokens", 0) for entry in self.metrics_history 
                        if "output_tokens" in entry["metrics"]]
        
        total_tokens = [entry["metrics"].get("total_tokens", 0) for entry in self.metrics_history 
                       if "total_tokens" in entry["metrics"]]
        
        summary = {
            "model": self.model_name,
            "total_requests": len(self.metrics_history),
            "metrics": {}
        }
        
        if latencies:
            summary["metrics"]["avg_latency"] = sum(latencies) / len(latencies)
            summary["metrics"]["min_latency"] = min(latencies)
            summary["metrics"]["max_latency"] = max(latencies)
        
        if input_tokens:
            summary["metrics"]["total_input_tokens"] = sum(input_tokens)
            summary["metrics"]["avg_input_tokens"] = sum(input_tokens) / len(input_tokens)
        
        if output_tokens:
            summary["metrics"]["total_output_tokens"] = sum(output_tokens)
            summary["metrics"]["avg_output_tokens"] = sum(output_tokens) / len(output_tokens)
        
        if total_tokens:
            summary["metrics"]["total_tokens_used"] = sum(total_tokens)
            summary["metrics"]["avg_tokens_per_request"] = sum(total_tokens) / len(total_tokens)
        
        return summary
