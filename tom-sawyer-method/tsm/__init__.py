"""
Tom Sawyer Method (TSM) - Intelligent Ensemble AI Framework

An enterprise-grade framework for orchestrating self-managing teams of AI specialists
that learn, adapt, and maintain high reliability through collective intelligence.
"""

__version__ = "0.1.0"
__author__ = "TSM Development Team"

from tsm.core.worker import Worker, WorkerPool, WorkerResult, WorkerStatus
from tsm.core.aggregator import Aggregator, AggregationStrategy
from tsm.core.learner import WeightLearner, BayesianWeightLearner
from tsm.config.schema import TSMConfig, WorkerConfig

__all__ = [
    "Worker",
    "WorkerPool",
    "WorkerResult",
    "WorkerStatus",
    "Aggregator",
    "AggregationStrategy",
    "WeightLearner",
    "BayesianWeightLearner",
    "TSMConfig",
    "WorkerConfig",
]
