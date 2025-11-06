"""
Aggregation strategies for combining worker outputs.

This module implements the Aggregation Oracle (Master Conductor) that intelligently
combines outputs from multiple workers using various strategies.

Implements FR1.2.1 - Aggregation Function Definition and FR1.2.3 - Dynamic Weight Application.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np
from scipy import stats

from tsm.core.result import WorkerResult, AggregatedResult, ResultStatus
from tsm.core.learner import WeightLearner

logger = logging.getLogger(__name__)


class AggregationStrategy(ABC):
    """
    Abstract base class for aggregation strategies.
    """

    @abstractmethod
    def aggregate(self,
                  results: List[WorkerResult],
                  weights: Optional[Dict[str, float]] = None) -> AggregatedResult:
        """
        Aggregate worker results into a single result.

        Args:
            results: List of worker results
            weights: Optional weights for each worker

        Returns:
            Aggregated result
        """
        pass

    def _filter_valid_results(self, results: List[WorkerResult]) -> List[WorkerResult]:
        """Filter out invalid results."""
        return [r for r in results if r.is_valid()]

    def _get_weights(self,
                     results: List[WorkerResult],
                     provided_weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Get weights for each worker.

        Args:
            results: List of worker results
            provided_weights: Optional provided weights

        Returns:
            Dictionary of weights
        """
        if provided_weights:
            return {r.worker_id: provided_weights.get(r.worker_id, 1.0) for r in results}
        else:
            # Equal weights if none provided
            return {r.worker_id: 1.0 for r in results}


class WeightedAverageAggregation(AggregationStrategy):
    """
    Weighted average aggregation for numerical outputs.

    Combines numerical results using weighted average, where weights are based on
    both learned weights and confidence scores.
    """

    def __init__(self, use_confidence: bool = True):
        """
        Initialize weighted average aggregation.

        Args:
            use_confidence: Whether to factor in confidence scores
        """
        self.use_confidence = use_confidence

    def aggregate(self,
                  results: List[WorkerResult],
                  weights: Optional[Dict[str, float]] = None) -> AggregatedResult:
        """Aggregate using weighted average."""
        start_time = time.time()

        # Filter valid results
        valid_results = self._filter_valid_results(results)

        if not valid_results:
            return AggregatedResult(
                value=None,
                confidence=0.0,
                worker_results=results,
                weights={},
                aggregation_method="weighted_average",
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": "No valid results to aggregate"}
            )

        # Get base weights
        base_weights = self._get_weights(valid_results, weights)

        # Calculate effective weights (base weight * confidence)
        effective_weights = {}
        for result in valid_results:
            base_weight = base_weights[result.worker_id]
            if self.use_confidence:
                effective_weights[result.worker_id] = base_weight * result.confidence
            else:
                effective_weights[result.worker_id] = base_weight

        # Normalize weights
        total_weight = sum(effective_weights.values())
        if total_weight > 0:
            normalized_weights = {
                wid: w / total_weight for wid, w in effective_weights.items()
            }
        else:
            normalized_weights = {
                wid: 1.0 / len(effective_weights) for wid in effective_weights
            }

        # Calculate weighted average
        try:
            weighted_sum = sum(
                result.value * normalized_weights[result.worker_id]
                for result in valid_results
            )

            # Calculate overall confidence
            overall_confidence = sum(
                result.confidence * normalized_weights[result.worker_id]
                for result in valid_results
            )

            processing_time = (time.time() - start_time) * 1000

            return AggregatedResult(
                value=weighted_sum,
                confidence=overall_confidence,
                worker_results=results,
                weights=normalized_weights,
                aggregation_method="weighted_average",
                processing_time_ms=processing_time,
                metadata={
                    "valid_results": len(valid_results),
                    "total_results": len(results),
                    "use_confidence": self.use_confidence,
                }
            )

        except TypeError as e:
            # Handle non-numerical values
            logger.error(f"Cannot compute weighted average: {e}")
            return AggregatedResult(
                value=None,
                confidence=0.0,
                worker_results=results,
                weights={},
                aggregation_method="weighted_average",
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": f"Non-numerical values: {e}"}
            )


class MajorityVotingAggregation(AggregationStrategy):
    """
    Majority voting aggregation for categorical outputs.

    Selects the most common output value, weighted by worker weights and confidence.
    """

    def __init__(self, use_confidence: bool = True):
        """
        Initialize majority voting aggregation.

        Args:
            use_confidence: Whether to factor in confidence scores
        """
        self.use_confidence = use_confidence

    def aggregate(self,
                  results: List[WorkerResult],
                  weights: Optional[Dict[str, float]] = None) -> AggregatedResult:
        """Aggregate using majority voting."""
        start_time = time.time()

        # Filter valid results
        valid_results = self._filter_valid_results(results)

        if not valid_results:
            return AggregatedResult(
                value=None,
                confidence=0.0,
                worker_results=results,
                weights={},
                aggregation_method="majority_voting",
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": "No valid results to aggregate"}
            )

        # Get base weights
        base_weights = self._get_weights(valid_results, weights)

        # Count votes with weights
        vote_scores: Dict[Any, float] = {}
        vote_confidence: Dict[Any, List[float]] = {}

        for result in valid_results:
            value = result.value
            base_weight = base_weights[result.worker_id]

            if self.use_confidence:
                score = base_weight * result.confidence
            else:
                score = base_weight

            vote_scores[value] = vote_scores.get(value, 0.0) + score

            if value not in vote_confidence:
                vote_confidence[value] = []
            vote_confidence[value].append(result.confidence)

        # Find winner
        winner = max(vote_scores.items(), key=lambda x: x[1])
        winning_value = winner[0]
        winning_score = winner[1]

        # Calculate confidence
        total_score = sum(vote_scores.values())
        confidence = winning_score / total_score if total_score > 0 else 0.0

        # Calculate agreement (what percentage agreed with winner)
        agreement = len([r for r in valid_results if r.value == winning_value]) / len(valid_results)

        processing_time = (time.time() - start_time) * 1000

        return AggregatedResult(
            value=winning_value,
            confidence=confidence,
            worker_results=results,
            weights=base_weights,
            aggregation_method="majority_voting",
            processing_time_ms=processing_time,
            metadata={
                "valid_results": len(valid_results),
                "total_results": len(results),
                "vote_distribution": vote_scores,
                "agreement": agreement,
                "use_confidence": self.use_confidence,
            }
        )


class ConfidenceBasedAggregation(AggregationStrategy):
    """
    Confidence-based aggregation that selects the result with highest confidence.

    Selects the single best result based on weighted confidence score.
    """

    def aggregate(self,
                  results: List[WorkerResult],
                  weights: Optional[Dict[str, float]] = None) -> AggregatedResult:
        """Aggregate by selecting highest confidence result."""
        start_time = time.time()

        # Filter valid results
        valid_results = self._filter_valid_results(results)

        if not valid_results:
            return AggregatedResult(
                value=None,
                confidence=0.0,
                worker_results=results,
                weights={},
                aggregation_method="confidence_based",
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": "No valid results to aggregate"}
            )

        # Get weights
        base_weights = self._get_weights(valid_results, weights)

        # Calculate weighted confidence scores
        best_result = None
        best_score = -1.0

        for result in valid_results:
            score = result.confidence * base_weights[result.worker_id]
            if score > best_score:
                best_score = score
                best_result = result

        processing_time = (time.time() - start_time) * 1000

        return AggregatedResult(
            value=best_result.value,
            confidence=best_result.confidence,
            worker_results=results,
            weights=base_weights,
            aggregation_method="confidence_based",
            processing_time_ms=processing_time,
            metadata={
                "valid_results": len(valid_results),
                "total_results": len(results),
                "selected_worker": best_result.worker_id,
                "weighted_confidence": best_score,
            }
        )


class MedianAggregation(AggregationStrategy):
    """
    Median aggregation for numerical outputs.

    Uses median to be robust against outliers.
    """

    def aggregate(self,
                  results: List[WorkerResult],
                  weights: Optional[Dict[str, float]] = None) -> AggregatedResult:
        """Aggregate using median."""
        start_time = time.time()

        # Filter valid results
        valid_results = self._filter_valid_results(results)

        if not valid_results:
            return AggregatedResult(
                value=None,
                confidence=0.0,
                worker_results=results,
                weights={},
                aggregation_method="median",
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": "No valid results to aggregate"}
            )

        try:
            # Extract values and confidences
            values = [r.value for r in valid_results]
            confidences = [r.confidence for r in valid_results]

            # Calculate median
            median_value = np.median(values)

            # Calculate median absolute deviation for confidence
            mad = np.median(np.abs(values - median_value))

            # Confidence based on consistency (lower MAD = higher confidence)
            # Normalize to 0-1 range
            if len(values) > 1:
                value_range = np.max(values) - np.min(values)
                if value_range > 0:
                    confidence = 1.0 - min(mad / value_range, 1.0)
                else:
                    confidence = 1.0  # All values are same
            else:
                confidence = confidences[0]

            # Average with worker confidences
            avg_worker_confidence = np.mean(confidences)
            overall_confidence = (confidence + avg_worker_confidence) / 2.0

            processing_time = (time.time() - start_time) * 1000

            return AggregatedResult(
                value=float(median_value),
                confidence=overall_confidence,
                worker_results=results,
                weights=self._get_weights(valid_results, weights),
                aggregation_method="median",
                processing_time_ms=processing_time,
                metadata={
                    "valid_results": len(valid_results),
                    "total_results": len(results),
                    "mad": float(mad),
                    "value_range": float(np.max(values) - np.min(values)) if len(values) > 1 else 0.0,
                }
            )

        except (TypeError, ValueError) as e:
            logger.error(f"Cannot compute median: {e}")
            return AggregatedResult(
                value=None,
                confidence=0.0,
                worker_results=results,
                weights={},
                aggregation_method="median",
                processing_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": f"Non-numerical values: {e}"}
            )


class Aggregator:
    """
    Main aggregator class that manages aggregation strategies and weight learning.

    This is the Aggregation Oracle (Master Conductor) that coordinates the
    aggregation process with learned weights.
    """

    def __init__(self,
                 strategy: AggregationStrategy,
                 weight_learner: Optional[WeightLearner] = None):
        """
        Initialize aggregator.

        Args:
            strategy: Aggregation strategy to use
            weight_learner: Optional weight learner for adaptive weights
        """
        self.strategy = strategy
        self.weight_learner = weight_learner
        self.logger = logging.getLogger(f"{__name__}.Aggregator")

    def aggregate(self, results: List[WorkerResult]) -> AggregatedResult:
        """
        Aggregate worker results using learned weights.

        Args:
            results: List of worker results

        Returns:
            Aggregated result
        """
        # Get learned weights if available
        if self.weight_learner:
            weights = self.weight_learner.get_all_weights()
            self.logger.debug(f"Using learned weights: {weights}")
        else:
            weights = None

        # Perform aggregation
        aggregated = self.strategy.aggregate(results, weights)

        self.logger.info(
            f"Aggregated {len(results)} results using {aggregated.aggregation_method}, "
            f"confidence: {aggregated.confidence:.3f}"
        )

        return aggregated

    def set_strategy(self, strategy: AggregationStrategy) -> None:
        """Change aggregation strategy."""
        self.strategy = strategy
        self.logger.info(f"Changed aggregation strategy to {strategy.__class__.__name__}")

    def set_weight_learner(self, learner: WeightLearner) -> None:
        """Set or update weight learner."""
        self.weight_learner = learner
        self.logger.info(f"Set weight learner to {learner.__class__.__name__}")
