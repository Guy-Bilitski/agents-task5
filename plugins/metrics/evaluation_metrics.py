"""
Evaluation Metric Plugins.

This module provides pluggable evaluation metrics for experiment results.
Each metric computes a specific aspect of model performance.

Available Metrics:
    - ExactMatchMetric: Exact string matching
    - ContainsMetric: Substring containment
    - F1ScoreMetric: Token-level F1 score
    - LatencyMetric: Response time statistics

Usage:
    from common.plugins import metric_registry

    metric = metric_registry.create_instance("exact_match")
    result = metric.compute(predictions, references)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.plugins import BaseMetricPlugin, plugin


@plugin(name="exact_match", metadata={
    "description": "Exact string matching metric",
    "version": "1.0.0"
})
class ExactMatchMetric(BaseMetricPlugin):
    """
    Exact match evaluation metric.

    Computes the percentage of predictions that exactly match
    the reference (case-insensitive by default).
    """

    PLUGIN_NAME = "exact_match"

    def __init__(self, case_sensitive: bool = False, strip_whitespace: bool = True):
        """
        Initialize exact match metric.

        Args:
            case_sensitive: Whether to use case-sensitive matching
            strip_whitespace: Whether to strip whitespace before comparison
        """
        self.case_sensitive = case_sensitive
        self.strip_whitespace = strip_whitespace

    @property
    def name(self) -> str:
        return "exact_match"

    @property
    def higher_is_better(self) -> bool:
        return True

    def compute(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> Dict[str, float]:
        """
        Compute exact match accuracy.

        Args:
            predictions: Model predictions
            references: Ground truth references

        Returns:
            Dict with 'exact_match' score
        """
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have same length")

        if not predictions:
            return {"exact_match": 0.0}

        matches = 0
        for pred, ref in zip(predictions, references):
            p = pred.strip() if self.strip_whitespace else pred
            r = ref.strip() if self.strip_whitespace else ref

            if not self.case_sensitive:
                p = p.lower()
                r = r.lower()

            if p == r:
                matches += 1

        accuracy = matches / len(predictions)
        return {
            "exact_match": accuracy,
            "matches": matches,
            "total": len(predictions)
        }


@plugin(name="contains", metadata={
    "description": "Substring containment metric",
    "version": "1.0.0"
})
class ContainsMetric(BaseMetricPlugin):
    """
    Containment evaluation metric.

    Checks if the reference string is contained within the prediction.
    Useful for evaluating open-ended responses.
    """

    PLUGIN_NAME = "contains"

    def __init__(self, case_sensitive: bool = False):
        """
        Initialize contains metric.

        Args:
            case_sensitive: Whether to use case-sensitive matching
        """
        self.case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "contains"

    @property
    def higher_is_better(self) -> bool:
        return True

    def compute(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> Dict[str, float]:
        """
        Compute containment accuracy.

        Args:
            predictions: Model predictions
            references: Expected substrings

        Returns:
            Dict with 'contains' score
        """
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have same length")

        if not predictions:
            return {"contains": 0.0}

        matches = 0
        for pred, ref in zip(predictions, references):
            p = pred if self.case_sensitive else pred.lower()
            r = ref if self.case_sensitive else ref.lower()

            if r in p:
                matches += 1

        accuracy = matches / len(predictions)
        return {
            "contains": accuracy,
            "matches": matches,
            "total": len(predictions)
        }


@plugin(name="f1_score", metadata={
    "description": "Token-level F1 score",
    "version": "1.0.0"
})
class F1ScoreMetric(BaseMetricPlugin):
    """
    Token-level F1 score metric.

    Computes precision, recall, and F1 score based on token overlap
    between predictions and references.
    """

    PLUGIN_NAME = "f1_score"

    def __init__(self, case_sensitive: bool = False):
        """
        Initialize F1 metric.

        Args:
            case_sensitive: Whether to use case-sensitive comparison
        """
        self.case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "f1_score"

    @property
    def higher_is_better(self) -> bool:
        return True

    def compute(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> Dict[str, float]:
        """
        Compute token-level F1 score.

        Args:
            predictions: Model predictions
            references: Ground truth references

        Returns:
            Dict with 'precision', 'recall', 'f1' scores
        """
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have same length")

        if not predictions:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        for pred, ref in zip(predictions, references):
            p_tokens = self._tokenize(pred)
            r_tokens = self._tokenize(ref)

            if not p_tokens or not r_tokens:
                continue

            common = p_tokens & r_tokens
            precision = len(common) / len(p_tokens) if p_tokens else 0
            recall = len(common) / len(r_tokens) if r_tokens else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            total_precision += precision
            total_recall += recall
            total_f1 += f1

        n = len(predictions)
        return {
            "precision": total_precision / n,
            "recall": total_recall / n,
            "f1": total_f1 / n
        }

    def _tokenize(self, text: str) -> set:
        """Tokenize text into words."""
        if not self.case_sensitive:
            text = text.lower()
        return set(text.split())


@plugin(name="latency", metadata={
    "description": "Response latency statistics",
    "version": "1.0.0"
})
class LatencyMetric(BaseMetricPlugin):
    """
    Latency statistics metric.

    Computes mean, standard deviation, min, and max latency
    from a list of latency measurements.
    """

    PLUGIN_NAME = "latency"

    @property
    def name(self) -> str:
        return "latency"

    @property
    def higher_is_better(self) -> bool:
        return False  # Lower latency is better

    def compute(
        self,
        predictions: List[str],
        references: List[str],
        latencies: List[float] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Compute latency statistics.

        Args:
            predictions: Not used (for interface compatibility)
            references: Not used (for interface compatibility)
            latencies: List of latency measurements

        Returns:
            Dict with latency statistics
        """
        if latencies is None:
            latencies = kwargs.get("latencies", [])

        if not latencies:
            return {
                "latency_mean": 0.0,
                "latency_std": 0.0,
                "latency_min": 0.0,
                "latency_max": 0.0
            }

        mean = sum(latencies) / len(latencies)
        variance = sum((x - mean) ** 2 for x in latencies) / len(latencies)
        std = variance ** 0.5

        return {
            "latency_mean": mean,
            "latency_std": std,
            "latency_min": min(latencies),
            "latency_max": max(latencies),
            "latency_count": len(latencies)
        }


@plugin(name="token_efficiency", metadata={
    "description": "Token usage efficiency metric",
    "version": "1.0.0"
})
class TokenEfficiencyMetric(BaseMetricPlugin):
    """
    Token efficiency metric.

    Measures how efficiently tokens are used by comparing
    accuracy achieved per token consumed.
    """

    PLUGIN_NAME = "token_efficiency"

    @property
    def name(self) -> str:
        return "token_efficiency"

    @property
    def higher_is_better(self) -> bool:
        return True  # Higher efficiency is better

    def compute(
        self,
        predictions: List[str],
        references: List[str],
        token_counts: List[int] = None,
        accuracies: List[float] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Compute token efficiency.

        Args:
            predictions: Model predictions
            references: Ground truth references
            token_counts: Tokens used per prediction
            accuracies: Accuracy per prediction (0 or 1)

        Returns:
            Dict with efficiency metrics
        """
        token_counts = token_counts or kwargs.get("token_counts", [])
        accuracies = accuracies or kwargs.get("accuracies", [])

        if not token_counts or not accuracies:
            return {
                "tokens_per_correct": 0.0,
                "accuracy_per_1k_tokens": 0.0
            }

        total_tokens = sum(token_counts)
        total_correct = sum(1 for a in accuracies if a > 0.5)

        tokens_per_correct = total_tokens / max(total_correct, 1)
        accuracy_per_1k = (total_correct / len(accuracies)) / (total_tokens / 1000) if total_tokens > 0 else 0

        return {
            "tokens_per_correct": tokens_per_correct,
            "accuracy_per_1k_tokens": accuracy_per_1k,
            "total_tokens": total_tokens,
            "total_correct": total_correct
        }
