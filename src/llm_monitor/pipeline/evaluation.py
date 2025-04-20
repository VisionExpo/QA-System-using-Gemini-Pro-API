"""
Evaluation pipeline for LLM Monitor
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

from ..utils.logger import LLMLogger, default_logger


class EvaluationMetrics:
    """
    Evaluation metrics for LLM models
    """
    
    @staticmethod
    def exact_match(prediction: str, reference: str) -> float:
        """
        Calculate exact match score
        
        Args:
            prediction: Predicted text
            reference: Reference text
            
        Returns:
            1.0 if exact match, 0.0 otherwise
        """
        return float(prediction.strip() == reference.strip())
    
    @staticmethod
    def token_overlap(prediction: str, reference: str) -> float:
        """
        Calculate token overlap (F1 score)
        
        Args:
            prediction: Predicted text
            reference: Reference text
            
        Returns:
            F1 score of token overlap
        """
        pred_tokens = set(prediction.lower().split())
        ref_tokens = set(reference.lower().split())
        
        if not pred_tokens and not ref_tokens:
            return 1.0
        
        if not pred_tokens or not ref_tokens:
            return 0.0
        
        common_tokens = pred_tokens.intersection(ref_tokens)
        precision = len(common_tokens) / len(pred_tokens)
        recall = len(common_tokens) / len(ref_tokens)
        
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * precision * recall / (precision + recall)
        return f1
    
    @staticmethod
    def semantic_similarity(prediction: str, reference: str, model=None) -> float:
        """
        Calculate semantic similarity using embeddings
        
        Args:
            prediction: Predicted text
            reference: Reference text
            model: Embedding model (if None, tries to use sentence-transformers)
            
        Returns:
            Cosine similarity between embeddings
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use provided model or load default
            embedding_model = model or SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embeddings
            pred_embedding = embedding_model.encode([prediction])[0]
            ref_embedding = embedding_model.encode([reference])[0]
            
            # Calculate cosine similarity
            similarity = np.dot(pred_embedding, ref_embedding) / (
                np.linalg.norm(pred_embedding) * np.linalg.norm(ref_embedding)
            )
            
            return float(similarity)
            
        except ImportError:
            default_logger.warning("sentence-transformers not installed. Falling back to token overlap.")
            return EvaluationMetrics.token_overlap(prediction, reference)


class EvaluationPipeline:
    """
    Pipeline for evaluating LLM models
    """
    
    def __init__(
        self,
        model_name: str,
        data_dir: str = "artifacts/data",
        output_dir: str = "artifacts/evaluation",
        logger: Optional[LLMLogger] = None
    ):
        """
        Initialize evaluation pipeline
        
        Args:
            model_name: Name of the model to evaluate
            data_dir: Directory containing evaluation data
            output_dir: Directory to save evaluation results
            logger: Custom logger instance
        """
        self.model_name = model_name
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.logger = logger or default_logger
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Evaluation pipeline initialized for model: {model_name}")
    
    def evaluate(
        self,
        prediction_func: Callable[[str], str],
        eval_data_file: str,
        metrics: List[str] = ["exact_match", "token_overlap"],
        input_key: str = "input",
        reference_key: str = "output",
        batch_size: int = 10,
        max_samples: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate model on dataset
        
        Args:
            prediction_func: Function that takes input text and returns prediction
            eval_data_file: File containing evaluation data
            metrics: List of metrics to calculate
            input_key: Key for input field in data
            reference_key: Key for reference field in data
            batch_size: Batch size for evaluation
            max_samples: Maximum number of samples to evaluate (None for all)
            output_file: File to save evaluation results (default: {model_name}_eval_{timestamp}.json)
            
        Returns:
            Dictionary with evaluation results
        """
        self.logger.info(f"Evaluating model {self.model_name} on {eval_data_file}")
        
        eval_data_path = os.path.join(self.data_dir, eval_data_file)
        
        if not os.path.exists(eval_data_path):
            raise FileNotFoundError(f"Evaluation data file not found: {eval_data_path}")
        
        # Load evaluation data
        with open(eval_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Evaluation data must be a list of dictionaries")
        
        # Limit samples if specified
        if max_samples is not None:
            data = data[:max_samples]
        
        self.logger.info(f"Loaded {len(data)} samples for evaluation")
        
        # Initialize results
        results = {
            "model_name": self.model_name,
            "dataset": eval_data_file,
            "timestamp": datetime.now().isoformat(),
            "metrics": {metric: 0.0 for metric in metrics},
            "samples": []
        }
        
        # Process in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(data)-1)//batch_size + 1}")
            
            for item in batch:
                input_text = item.get(input_key, "")
                reference = item.get(reference_key, "")
                
                if not input_text:
                    self.logger.warning(f"Empty input text in sample, skipping")
                    continue
                
                # Get prediction
                try:
                    prediction = prediction_func(input_text)
                    
                    # Calculate metrics
                    sample_metrics = {}
                    
                    if "exact_match" in metrics:
                        sample_metrics["exact_match"] = EvaluationMetrics.exact_match(prediction, reference)
                    
                    if "token_overlap" in metrics:
                        sample_metrics["token_overlap"] = EvaluationMetrics.token_overlap(prediction, reference)
                    
                    if "semantic_similarity" in metrics:
                        sample_metrics["semantic_similarity"] = EvaluationMetrics.semantic_similarity(prediction, reference)
                    
                    # Add sample result
                    results["samples"].append({
                        "input": input_text,
                        "reference": reference,
                        "prediction": prediction,
                        "metrics": sample_metrics
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing sample: {str(e)}")
                    continue
        
        # Calculate average metrics
        for metric in metrics:
            values = [sample["metrics"].get(metric, 0.0) for sample in results["samples"] if metric in sample["metrics"]]
            if values:
                results["metrics"][metric] = sum(values) / len(values)
        
        # Save results
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.model_name}_eval_{timestamp}.json"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Evaluation completed. Results saved to {output_path}")
        
        # Log summary
        self.logger.info(f"Evaluation summary for {self.model_name}:")
        for metric, value in results["metrics"].items():
            self.logger.info(f"  {metric}: {value:.4f}")
        
        return results
    
    def compare_models(
        self,
        eval_results_files: List[str],
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare evaluation results from multiple models
        
        Args:
            eval_results_files: List of evaluation results files
            output_file: File to save comparison results (default: model_comparison_{timestamp}.json)
            
        Returns:
            Dictionary with comparison results
        """
        self.logger.info(f"Comparing evaluation results from {len(eval_results_files)} models")
        
        models_results = []
        
        for file in eval_results_files:
            file_path = os.path.join(self.output_dir, file)
            
            if not os.path.exists(file_path):
                self.logger.warning(f"Results file not found: {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            models_results.append(results)
        
        if not models_results:
            raise ValueError("No valid evaluation results files found")
        
        # Extract metrics
        all_metrics = set()
        for results in models_results:
            all_metrics.update(results.get("metrics", {}).keys())
        
        # Create comparison
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "models": [results.get("model_name", "unknown") for results in models_results],
            "metrics": {metric: [] for metric in all_metrics},
            "rankings": {metric: [] for metric in all_metrics}
        }
        
        # Collect metrics
        for results in models_results:
            model_name = results.get("model_name", "unknown")
            metrics = results.get("metrics", {})
            
            for metric in all_metrics:
                value = metrics.get(metric, float('nan'))
                comparison["metrics"].setdefault(metric, []).append({
                    "model": model_name,
                    "value": value
                })
        
        # Calculate rankings
        for metric in all_metrics:
            values = [(item["model"], item["value"]) for item in comparison["metrics"][metric]]
            # Sort by value in descending order (higher is better)
            ranked = sorted(values, key=lambda x: x[1], reverse=True)
            
            comparison["rankings"][metric] = [
                {"model": model, "value": value, "rank": i+1}
                for i, (model, value) in enumerate(ranked)
            ]
        
        # Save comparison
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"model_comparison_{timestamp}.json"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        
        self.logger.info(f"Model comparison completed. Results saved to {output_path}")
        
        # Log summary
        self.logger.info("Model comparison summary:")
        for metric in all_metrics:
            self.logger.info(f"  {metric} ranking:")
            for item in comparison["rankings"][metric]:
                self.logger.info(f"    Rank {item['rank']}: {item['model']} ({item['value']:.4f})")
        
        return comparison
