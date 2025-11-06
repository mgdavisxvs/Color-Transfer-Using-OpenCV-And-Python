"""
Probabilistic Weight Learning for TSM framework.

This module implements the Performance Review System using Bayesian methods
to continuously learn and adjust worker weights based on historical performance.

Implements FR1.2.2 - Probabilistic Weight Learning (Performance Review System).
"""

import logging
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """
    Performance metric for a worker.

    Attributes:
        worker_id: Worker identifier
        predicted: Predicted value
        actual: Actual/ground truth value
        confidence: Confidence score
        accuracy: Calculated accuracy (0.0 to 1.0)
        timestamp: When metric was recorded
    """
    worker_id: str
    predicted: Any
    actual: Any
    confidence: float
    accuracy: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class WeightLearner(ABC):
    """
    Abstract base class for weight learning strategies.
    """

    @abstractmethod
    def update_weight(self, worker_id: str, metric: PerformanceMetric) -> float:
        """
        Update weight for a worker based on new performance metric.

        Args:
            worker_id: Worker identifier
            metric: Performance metric

        Returns:
            Updated weight
        """
        pass

    @abstractmethod
    def get_weight(self, worker_id: str) -> float:
        """
        Get current weight for a worker.

        Args:
            worker_id: Worker identifier

        Returns:
            Current weight
        """
        pass

    @abstractmethod
    def get_all_weights(self) -> Dict[str, float]:
        """Get weights for all workers."""
        pass


class BayesianWeightLearner(WeightLearner):
    """
    Bayesian weight learner using exponential moving average.

    Implements the Bayesian Update Rule for continuous weight adaptation.

    The weight is updated using:
        w_i(t+1) = w_i(t) * (1 - alpha) + accuracy_i(t) * alpha

    Where:
        - w_i(t) is the current weight
        - accuracy_i(t) is the recent accuracy
        - alpha is the learning rate
    """

    def __init__(self,
                 alpha: float = 0.1,
                 prior_weight: float = 1.0,
                 min_weight: float = 0.01,
                 confidence_scaling: bool = True):
        """
        Initialize Bayesian weight learner.

        Args:
            alpha: Learning rate (0 to 1), higher = faster adaptation
            prior_weight: Initial weight for new workers
            min_weight: Minimum allowed weight
            confidence_scaling: Whether to scale updates by confidence
        """
        if not 0.0 < alpha <= 1.0:
            raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

        if prior_weight <= 0:
            raise ValueError(f"Prior weight must be positive, got {prior_weight}")

        self.alpha = alpha
        self.prior_weight = prior_weight
        self.min_weight = min_weight
        self.confidence_scaling = confidence_scaling

        # Worker weights (posterior probabilities)
        self.weights: Dict[str, float] = {}

        # Performance history
        self.history: Dict[str, list] = {}

        # Statistics
        self.update_count: Dict[str, int] = {}

        self.logger = logging.getLogger(f"{__name__}.BayesianWeightLearner")

    def get_weight(self, worker_id: str) -> float:
        """Get current weight for a worker."""
        return self.weights.get(worker_id, self.prior_weight)

    def get_all_weights(self) -> Dict[str, float]:
        """Get weights for all workers."""
        return self.weights.copy()

    def get_normalized_weights(self, worker_ids: Optional[list] = None) -> Dict[str, float]:
        """
        Get normalized weights that sum to 1.0.

        Args:
            worker_ids: Specific workers to normalize (None = all)

        Returns:
            Dictionary of normalized weights
        """
        if worker_ids is None:
            worker_ids = list(self.weights.keys())

        if not worker_ids:
            return {}

        # Get weights for specified workers
        weights = {wid: self.get_weight(wid) for wid in worker_ids}

        # Normalize
        total = sum(weights.values())
        if total > 0:
            normalized = {wid: w / total for wid, w in weights.items()}
        else:
            # Equal weights if all are zero
            normalized = {wid: 1.0 / len(worker_ids) for wid in worker_ids}

        return normalized

    def update_weight(self, worker_id: str, metric: PerformanceMetric) -> float:
        """
        Update weight using Bayesian update rule.

        Args:
            worker_id: Worker identifier
            metric: Performance metric

        Returns:
            Updated weight
        """
        # Get current weight (prior)
        current_weight = self.get_weight(worker_id)

        # Calculate effective learning rate
        if self.confidence_scaling:
            # Scale learning rate by confidence
            effective_alpha = self.alpha * metric.confidence
        else:
            effective_alpha = self.alpha

        # Bayesian update: posterior = prior * (1 - alpha) + likelihood * alpha
        new_weight = current_weight * (1 - effective_alpha) + metric.accuracy * effective_alpha

        # Enforce minimum weight
        new_weight = max(new_weight, self.min_weight)

        # Update weight
        self.weights[worker_id] = new_weight

        # Update history
        if worker_id not in self.history:
            self.history[worker_id] = []
        self.history[worker_id].append(metric)

        # Update statistics
        self.update_count[worker_id] = self.update_count.get(worker_id, 0) + 1

        self.logger.debug(
            f"Updated weight for {worker_id}: {current_weight:.4f} -> {new_weight:.4f} "
            f"(accuracy: {metric.accuracy:.4f}, confidence: {metric.confidence:.4f})"
        )

        return new_weight

    def batch_update(self, metrics: Dict[str, list]) -> Dict[str, float]:
        """
        Batch update weights for multiple workers.

        Args:
            metrics: Dictionary mapping worker_id to list of PerformanceMetric

        Returns:
            Dictionary of updated weights
        """
        updated_weights = {}
        for worker_id, worker_metrics in metrics.items():
            for metric in worker_metrics:
                updated_weights[worker_id] = self.update_weight(worker_id, metric)

        return updated_weights

    def get_statistics(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance statistics for a worker.

        Args:
            worker_id: Worker identifier

        Returns:
            Dictionary of statistics or None if no history
        """
        if worker_id not in self.history or not self.history[worker_id]:
            return None

        history = self.history[worker_id]
        accuracies = [m.accuracy for m in history]
        confidences = [m.confidence for m in history]

        return {
            "worker_id": worker_id,
            "current_weight": self.get_weight(worker_id),
            "update_count": self.update_count.get(worker_id, 0),
            "mean_accuracy": np.mean(accuracies),
            "std_accuracy": np.std(accuracies),
            "min_accuracy": np.min(accuracies),
            "max_accuracy": np.max(accuracies),
            "mean_confidence": np.mean(confidences),
            "recent_accuracy": np.mean(accuracies[-10:]) if len(accuracies) >= 10 else np.mean(accuracies),
            "trend": "improving" if len(accuracies) > 5 and
                    np.mean(accuracies[-5:]) > np.mean(accuracies[:-5]) else "stable",
        }

    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all workers."""
        return {
            worker_id: self.get_statistics(worker_id)
            for worker_id in self.weights.keys()
        }

    def reset_worker(self, worker_id: str) -> None:
        """
        Reset weight and history for a worker.

        Args:
            worker_id: Worker identifier
        """
        if worker_id in self.weights:
            del self.weights[worker_id]
        if worker_id in self.history:
            del self.history[worker_id]
        if worker_id in self.update_count:
            del self.update_count[worker_id]

        self.logger.info(f"Reset worker {worker_id}")

    def save_state(self, filepath: str) -> None:
        """
        Save learner state to file.

        Args:
            filepath: Path to save state
        """
        state = {
            "alpha": self.alpha,
            "prior_weight": self.prior_weight,
            "min_weight": self.min_weight,
            "confidence_scaling": self.confidence_scaling,
            "weights": self.weights,
            "update_count": self.update_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        self.logger.info(f"Saved learner state to {filepath}")

    def load_state(self, filepath: str) -> None:
        """
        Load learner state from file.

        Args:
            filepath: Path to load state from
        """
        with open(filepath, 'r') as f:
            state = json.load(f)

        self.alpha = state.get("alpha", self.alpha)
        self.prior_weight = state.get("prior_weight", self.prior_weight)
        self.min_weight = state.get("min_weight", self.min_weight)
        self.confidence_scaling = state.get("confidence_scaling", self.confidence_scaling)
        self.weights = state.get("weights", {})
        self.update_count = state.get("update_count", {})

        self.logger.info(f"Loaded learner state from {filepath}")


class AdaptiveBayesianLearner(BayesianWeightLearner):
    """
    Adaptive Bayesian learner that adjusts learning rate based on performance stability.

    When a worker's performance is stable, learning rate decreases.
    When performance is volatile, learning rate increases.
    """

    def __init__(self,
                 initial_alpha: float = 0.2,
                 min_alpha: float = 0.01,
                 max_alpha: float = 0.5,
                 stability_window: int = 10,
                 **kwargs):
        """
        Initialize adaptive learner.

        Args:
            initial_alpha: Initial learning rate
            min_alpha: Minimum learning rate
            max_alpha: Maximum learning rate
            stability_window: Window size for calculating stability
            **kwargs: Additional arguments for BayesianWeightLearner
        """
        super().__init__(alpha=initial_alpha, **kwargs)

        self.initial_alpha = initial_alpha
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.stability_window = stability_window

        # Per-worker learning rates
        self.worker_alphas: Dict[str, float] = {}

    def _calculate_stability(self, worker_id: str) -> float:
        """
        Calculate stability of worker performance.

        Returns coefficient of variation (lower = more stable).
        """
        if worker_id not in self.history or len(self.history[worker_id]) < self.stability_window:
            return 1.0  # Assume unstable for new workers

        recent = self.history[worker_id][-self.stability_window:]
        accuracies = [m.accuracy for m in recent]

        mean = np.mean(accuracies)
        std = np.std(accuracies)

        # Coefficient of variation (CV)
        if mean > 0:
            cv = std / mean
        else:
            cv = 1.0

        return cv

    def _adapt_alpha(self, worker_id: str) -> float:
        """
        Adapt learning rate based on performance stability.

        Args:
            worker_id: Worker identifier

        Returns:
            Adapted alpha value
        """
        stability = self._calculate_stability(worker_id)

        # High stability (low CV) -> lower alpha
        # Low stability (high CV) -> higher alpha
        adapted_alpha = self.min_alpha + (self.max_alpha - self.min_alpha) * stability

        # Clamp to bounds
        adapted_alpha = max(self.min_alpha, min(self.max_alpha, adapted_alpha))

        return adapted_alpha

    def update_weight(self, worker_id: str, metric: PerformanceMetric) -> float:
        """Update weight with adaptive learning rate."""
        # Adapt alpha for this worker
        self.worker_alphas[worker_id] = self._adapt_alpha(worker_id)

        # Temporarily set alpha
        original_alpha = self.alpha
        self.alpha = self.worker_alphas[worker_id]

        # Perform update
        new_weight = super().update_weight(worker_id, metric)

        # Restore original alpha
        self.alpha = original_alpha

        return new_weight

    def get_alpha(self, worker_id: str) -> float:
        """Get current adaptive alpha for a worker."""
        return self.worker_alphas.get(worker_id, self.initial_alpha)
