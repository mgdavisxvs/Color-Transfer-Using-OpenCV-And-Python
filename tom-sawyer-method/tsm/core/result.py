"""
Result data structures for TSM framework.

This module defines the data structures for worker outputs and aggregated results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid


class ResultStatus(Enum):
    """Status of a worker result."""
    SUCCESS = "success"
    FAILED = "failed"
    ANOMALY = "anomaly"
    TIMEOUT = "timeout"


@dataclass
class WorkerResult:
    """
    Result from a single worker execution.

    Attributes:
        worker_id: Unique identifier for the worker
        value: The output value from the worker
        confidence: Confidence score (0.0 to 1.0)
        processing_time_ms: Time taken to process in milliseconds
        status: Status of the execution
        metadata: Additional information about the execution
        timestamp: When the result was generated
        trace_id: Distributed tracing identifier
    """
    worker_id: str
    value: Any
    confidence: float
    processing_time_ms: float
    status: ResultStatus = ResultStatus.SUCCESS
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate result after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")

        if self.processing_time_ms < 0:
            raise ValueError(f"Processing time cannot be negative: {self.processing_time_ms}")

    def is_valid(self) -> bool:
        """Check if the result is valid and usable."""
        return self.status == ResultStatus.SUCCESS and self.confidence > 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "worker_id": self.worker_id,
            "value": self.value,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "status": self.status.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id,
        }


@dataclass
class AggregatedResult:
    """
    Result after aggregating multiple worker outputs.

    Attributes:
        value: The aggregated output value
        confidence: Overall confidence score
        worker_results: Individual worker results used in aggregation
        weights: Weights applied to each worker
        aggregation_method: Name of the aggregation strategy used
        processing_time_ms: Total processing time
        metadata: Additional information
        timestamp: When aggregation was completed
        trace_id: Distributed tracing identifier
    """
    value: Any
    confidence: float
    worker_results: List[WorkerResult]
    weights: Dict[str, float]
    aggregation_method: str
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate aggregated result."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")

    @property
    def num_workers(self) -> int:
        """Get number of workers that contributed to this result."""
        return len(self.worker_results)

    @property
    def valid_workers(self) -> int:
        """Get number of workers with valid results."""
        return sum(1 for r in self.worker_results if r.is_valid())

    @property
    def average_worker_confidence(self) -> float:
        """Calculate average confidence across all workers."""
        if not self.worker_results:
            return 0.0
        return sum(r.confidence for r in self.worker_results) / len(self.worker_results)

    def get_worker_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of worker results."""
        if not self.worker_results:
            return {}

        valid_results = [r for r in self.worker_results if r.is_valid()]

        return {
            "total_workers": self.num_workers,
            "valid_workers": len(valid_results),
            "failed_workers": self.num_workers - len(valid_results),
            "average_confidence": self.average_worker_confidence,
            "min_confidence": min((r.confidence for r in valid_results), default=0.0),
            "max_confidence": max((r.confidence for r in valid_results), default=0.0),
            "average_processing_time_ms": sum(r.processing_time_ms for r in self.worker_results) / self.num_workers,
            "total_processing_time_ms": self.processing_time_ms,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated result to dictionary format."""
        return {
            "value": self.value,
            "confidence": self.confidence,
            "worker_results": [r.to_dict() for r in self.worker_results],
            "weights": self.weights,
            "aggregation_method": self.aggregation_method,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata,
            "statistics": self.get_worker_statistics(),
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id,
        }
