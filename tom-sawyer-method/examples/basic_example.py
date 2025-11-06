#!/usr/bin/env python3
"""
Basic example demonstrating the Tom Sawyer Method framework.

This example shows how to:
1. Create custom workers
2. Set up a worker pool
3. Execute workers in parallel
4. Aggregate results with learned weights
5. Update weights based on performance
"""

import random
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tsm.core.worker import Worker, WorkerPool, WorkerConfig
from tsm.core.aggregator import (
    Aggregator,
    WeightedAverageAggregation,
    MajorityVotingAggregation,
)
from tsm.core.learner import BayesianWeightLearner, PerformanceMetric


class SimpleNumericalWorker(Worker):
    """
    A simple worker that performs numerical analysis.

    This worker adds a bias to the input and returns the result.
    Different workers can have different biases for diversity.
    """

    def __init__(self, worker_id: str, config: WorkerConfig):
        super().__init__(worker_id, config)
        self.bias = config.parameters.get("bias", 0.0)
        self.noise_level = config.parameters.get("noise_level", 0.1)

    def process(self, data: float) -> float:
        """Process numerical data with bias and noise."""
        # Add bias and random noise
        noise = random.uniform(-self.noise_level, self.noise_level)
        result = data + self.bias + noise
        return result

    def get_confidence(self, data: float, result: float) -> float:
        """Calculate confidence based on noise level."""
        # Lower noise = higher confidence
        confidence = 1.0 - self.noise_level
        return max(0.0, min(1.0, confidence))


class ClassificationWorker(Worker):
    """
    A simple worker that classifies values as 'low', 'medium', or 'high'.

    Different workers use different thresholds for classification.
    """

    def __init__(self, worker_id: str, config: WorkerConfig):
        super().__init__(worker_id, config)
        self.low_threshold = config.parameters.get("low_threshold", 30.0)
        self.high_threshold = config.parameters.get("high_threshold", 70.0)

    def process(self, data: float) -> str:
        """Classify data into categories."""
        if data < self.low_threshold:
            return "low"
        elif data < self.high_threshold:
            return "medium"
        else:
            return "high"

    def get_confidence(self, data: float, result: str) -> float:
        """Calculate confidence based on distance from thresholds."""
        # Higher confidence when far from thresholds
        if result == "low":
            distance = abs(data - self.low_threshold)
            confidence = min(1.0, distance / 10.0)
        elif result == "high":
            distance = abs(data - self.high_threshold)
            confidence = min(1.0, distance / 10.0)
        else:  # medium
            distance = min(
                abs(data - self.low_threshold),
                abs(data - self.high_threshold)
            )
            confidence = min(1.0, distance / 10.0)

        return max(0.3, confidence)


def example_numerical_prediction():
    """Example: Numerical prediction with weighted averaging."""
    print("=" * 60)
    print("Example 1: Numerical Prediction with Weighted Averaging")
    print("=" * 60)

    # Create worker pool
    pool = WorkerPool(max_workers=10)

    # Create workers with different biases (variations)
    worker_configs = [
        {"worker_id": "worker_0", "bias": 0.0, "noise_level": 0.05},
        {"worker_id": "worker_1", "bias": 1.0, "noise_level": 0.10},
        {"worker_id": "worker_2", "bias": -1.0, "noise_level": 0.10},
        {"worker_id": "worker_3", "bias": 0.5, "noise_level": 0.15},
        {"worker_id": "worker_4", "bias": -0.5, "noise_level": 0.15},
    ]

    for config in worker_configs:
        worker = SimpleNumericalWorker(
            worker_id=config["worker_id"],
            config=WorkerConfig(
                worker_id=config["worker_id"],
                worker_type="SimpleNumericalWorker",
                parameters={
                    "bias": config["bias"],
                    "noise_level": config["noise_level"]
                }
            )
        )
        pool.register_worker(worker)

    print(f"\nRegistered {len(pool.workers)} workers")

    # Create Bayesian weight learner
    learner = BayesianWeightLearner(alpha=0.2, prior_weight=1.0)

    # Create aggregator with weighted average strategy
    strategy = WeightedAverageAggregation(use_confidence=True)
    aggregator = Aggregator(strategy=strategy, weight_learner=learner)

    # Simulate multiple predictions
    print("\nRunning predictions...")
    test_cases = [
        (50.0, 50.2),  # (input, expected_output)
        (100.0, 100.1),
        (25.0, 25.0),
        (75.0, 74.9),
        (60.0, 60.3),
    ]

    for i, (input_value, expected_output) in enumerate(test_cases):
        print(f"\n--- Prediction {i + 1} ---")
        print(f"Input: {input_value:.2f}, Expected: {expected_output:.2f}")

        # Execute workers
        results = pool.execute_parallel(input_value)

        # Aggregate results
        final_result = aggregator.aggregate(results)

        print(f"Aggregated Result: {final_result.value:.2f}")
        print(f"Confidence: {final_result.confidence:.3f}")
        print(f"Workers used: {final_result.num_workers}")

        # Simulate feedback and update weights
        error = abs(final_result.value - expected_output)
        accuracy = max(0.0, 1.0 - error / 10.0)  # Simple accuracy metric

        for result in results:
            if result.is_valid():
                individual_error = abs(result.value - expected_output)
                individual_accuracy = max(0.0, 1.0 - individual_error / 10.0)

                metric = PerformanceMetric(
                    worker_id=result.worker_id,
                    predicted=result.value,
                    actual=expected_output,
                    confidence=result.confidence,
                    accuracy=individual_accuracy,
                )
                learner.update_weight(result.worker_id, metric)

    # Show final weights
    print("\n" + "=" * 60)
    print("Final Learned Weights:")
    print("=" * 60)
    for worker_id, weight in learner.get_all_weights().items():
        stats = learner.get_statistics(worker_id)
        print(f"{worker_id}: {weight:.4f} "
              f"(mean accuracy: {stats['mean_accuracy']:.3f})")

    # Show pool statistics
    print("\n" + "=" * 60)
    print("Worker Pool Statistics:")
    print("=" * 60)
    pool_stats = pool.get_pool_statistics()
    print(f"Total executions: {pool_stats['total_executions']}")
    print(f"Total failures: {pool_stats['total_failures']}")
    print(f"Failure rate: {pool_stats['overall_failure_rate']:.2%}")


def example_classification():
    """Example: Classification with majority voting."""
    print("\n\n" + "=" * 60)
    print("Example 2: Classification with Majority Voting")
    print("=" * 60)

    # Create worker pool
    pool = WorkerPool(max_workers=5)

    # Create workers with different thresholds
    worker_configs = [
        {"worker_id": "classifier_1", "low_threshold": 33.0, "high_threshold": 66.0},
        {"worker_id": "classifier_2", "low_threshold": 30.0, "high_threshold": 70.0},
        {"worker_id": "classifier_3", "low_threshold": 35.0, "high_threshold": 65.0},
    ]

    for config in worker_configs:
        worker = ClassificationWorker(
            worker_id=config["worker_id"],
            config=WorkerConfig(
                worker_id=config["worker_id"],
                worker_type="ClassificationWorker",
                parameters={
                    "low_threshold": config["low_threshold"],
                    "high_threshold": config["high_threshold"]
                }
            )
        )
        pool.register_worker(worker)

    print(f"\nRegistered {len(pool.workers)} classifiers")

    # Create aggregator with majority voting
    learner = BayesianWeightLearner(alpha=0.15)
    strategy = MajorityVotingAggregation(use_confidence=True)
    aggregator = Aggregator(strategy=strategy, weight_learner=learner)

    # Test classifications
    test_cases = [
        (25.0, "low"),
        (50.0, "medium"),
        (80.0, "high"),
        (35.0, "medium"),
        (68.0, "high"),
    ]

    for i, (input_value, expected_class) in enumerate(test_cases):
        print(f"\n--- Classification {i + 1} ---")
        print(f"Input: {input_value:.2f}, Expected: {expected_class}")

        # Execute workers
        results = pool.execute_parallel(input_value)

        # Aggregate results
        final_result = aggregator.aggregate(results)

        print(f"Predicted Class: {final_result.value}")
        print(f"Confidence: {final_result.confidence:.3f}")
        print(f"Vote distribution: {final_result.metadata.get('vote_distribution', {})}")
        print(f"Agreement: {final_result.metadata.get('agreement', 0.0):.2%}")

        # Update weights based on correctness
        for result in results:
            if result.is_valid():
                accuracy = 1.0 if result.value == expected_class else 0.0

                metric = PerformanceMetric(
                    worker_id=result.worker_id,
                    predicted=result.value,
                    actual=expected_class,
                    confidence=result.confidence,
                    accuracy=accuracy,
                )
                learner.update_weight(result.worker_id, metric)

    # Show final weights
    print("\n" + "=" * 60)
    print("Final Learned Weights:")
    print("=" * 60)
    for worker_id, weight in learner.get_all_weights().items():
        stats = learner.get_statistics(worker_id)
        print(f"{worker_id}: {weight:.4f} "
              f"(mean accuracy: {stats['mean_accuracy']:.3f})")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " Tom Sawyer Method - Basic Examples ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")

    # Run examples
    example_numerical_prediction()
    example_classification()

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
