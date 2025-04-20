"""
LangSmith monitoring service for QA System using Gemini API
Handles tracing and monitoring of LLM calls
"""

import os
import logging
import time
import uuid
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Import LangSmith with error handling
try:
    from langsmith import Client
    from langsmith.run_trees import RunTree
    langsmith_available = True
    logger.info("LangSmith package successfully imported")
except ImportError:
    langsmith_available = False
    logger.warning("LangSmith not installed. Monitoring functionality will be unavailable.")

class LangSmithMonitor:
    """Manager for LangSmith monitoring operations"""

    def __init__(self, project_name: str = "qa-system-gemini"):
        """
        Initialize LangSmith Monitor
        
        Args:
            project_name: Name of the project in LangSmith
        """
        self.project_name = project_name
        self.is_connected = False
        self.client = None
        
        # Check if LangSmith is available
        if not langsmith_available:
            logger.error("LangSmith not available. Install langsmith package.")
            return
            
        # Check for API key
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if not api_key:
            logger.warning("LANGCHAIN_API_KEY not found in environment variables.")
            logger.warning("Set LANGCHAIN_API_KEY to enable LangSmith monitoring.")
            return
            
        # Initialize LangSmith client
        try:
            self.client = Client(api_key=api_key)
            self.is_connected = True
            logger.info(f"Successfully connected to LangSmith with project: {project_name}")
            
            # Create project if it doesn't exist
            try:
                projects = self.client.list_projects()
                if project_name not in [p.name for p in projects]:
                    self.client.create_project(project_name)
                    logger.info(f"Created new LangSmith project: {project_name}")
            except Exception as e:
                logger.warning(f"Could not create project: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error connecting to LangSmith: {str(e)}")
            
    def trace(self, 
              run_type: str = "llm", 
              name: Optional[str] = None,
              tags: Optional[List[str]] = None):
        """
        Decorator to trace function calls in LangSmith
        
        Args:
            run_type: Type of run (llm, chain, tool)
            name: Name of the run
            tags: List of tags to apply to the run
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.is_connected:
                    # If LangSmith is not connected, just run the function
                    return func(*args, **kwargs)
                    
                # Extract inputs
                inputs = {}
                
                # Handle different input patterns
                if len(args) > 0:
                    inputs["args"] = args
                
                # Add kwargs to inputs
                inputs.update(kwargs)
                
                # Generate run name if not provided
                run_name = name or f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Start timing
                start_time = time.time()
                
                # Create run tree
                run_id = str(uuid.uuid4())
                
                try:
                    # Call the function
                    result = func(*args, **kwargs)
                    
                    # Calculate execution time
                    execution_time = time.time() - start_time
                    
                    # Process outputs
                    outputs = {}
                    if hasattr(result, "text"):
                        outputs["text"] = result.text
                    elif hasattr(result, "__dict__"):
                        outputs = result.__dict__
                    else:
                        outputs["result"] = result
                        
                    # Log successful run
                    self._log_run(
                        run_id=run_id,
                        run_type=run_type,
                        name=run_name,
                        inputs=inputs,
                        outputs=outputs,
                        error=None,
                        execution_time=execution_time,
                        tags=tags or []
                    )
                    
                    return result
                    
                except Exception as e:
                    # Calculate execution time
                    execution_time = time.time() - start_time
                    
                    # Log failed run
                    self._log_run(
                        run_id=run_id,
                        run_type=run_type,
                        name=run_name,
                        inputs=inputs,
                        outputs={},
                        error=str(e),
                        execution_time=execution_time,
                        tags=tags or []
                    )
                    
                    # Re-raise the exception
                    raise
                    
            return wrapper
        return decorator
        
    def _log_run(self,
                run_id: str,
                run_type: str,
                name: str,
                inputs: Dict[str, Any],
                outputs: Dict[str, Any],
                error: Optional[str],
                execution_time: float,
                tags: List[str]):
        """
        Log a run to LangSmith
        
        Args:
            run_id: Unique ID for the run
            run_type: Type of run (llm, chain, tool)
            name: Name of the run
            inputs: Input data
            outputs: Output data
            error: Error message if any
            execution_time: Execution time in seconds
            tags: List of tags
        """
        try:
            # Create run tree
            run = RunTree(
                id=run_id,
                name=name,
                run_type=run_type,
                inputs=inputs,
                outputs=outputs if not error else {},
                error=error,
                start_time=datetime.now().timestamp() - execution_time,
                end_time=datetime.now().timestamp(),
                extra={
                    "execution_time": execution_time
                },
                tags=tags
            )
            
            # Submit run to LangSmith
            self.client.create_run(
                project_name=self.project_name,
                run=run
            )
            
            logger.info(f"Logged run to LangSmith: {name} ({run_id})")
            
        except Exception as e:
            logger.error(f"Error logging run to LangSmith: {str(e)}")
            
    def log_feedback(self, run_id: str, key: str, score: float, comment: Optional[str] = None):
        """
        Log feedback for a run
        
        Args:
            run_id: ID of the run
            key: Feedback key (e.g., "relevance", "accuracy")
            score: Feedback score (0-1)
            comment: Optional comment
        """
        if not self.is_connected:
            logger.warning("LangSmith not connected. Cannot log feedback.")
            return
            
        try:
            self.client.create_feedback(
                run_id=run_id,
                key=key,
                score=score,
                comment=comment
            )
            logger.info(f"Logged feedback for run {run_id}: {key}={score}")
        except Exception as e:
            logger.error(f"Error logging feedback to LangSmith: {str(e)}")

# Create a singleton instance
langsmith_monitor = LangSmithMonitor()

def get_langsmith_monitor():
    """Get the LangSmith monitor instance"""
    return langsmith_monitor
