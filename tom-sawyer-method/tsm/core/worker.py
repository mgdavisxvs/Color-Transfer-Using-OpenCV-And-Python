"""
Worker base class and worker pool management for TSM framework.

This module provides the foundation for creating specialized workers and managing
them in a pool for parallel execution.
"""

import logging
import time
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from tsm.core.result import WorkerResult, ResultStatus

logger = logging.getLogger(__name__)


class WorkerStatus(Enum):
    """Status of a worker in the pool."""
    IDLE = "idle"
    ACTIVE = "active"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    DISABLED = "disabled"


@dataclass
class WorkerConfig:
    """
    Configuration for a worker.

    Attributes:
        worker_id: Unique identifier for the worker
        worker_type: Type/class name of the worker
        parameters: Worker-specific configuration parameters
        input_schema: Expected input data schema
        output_schema: Expected output data schema
        thresholds: Performance thresholds
        enabled: Whether worker is enabled
        timeout_seconds: Maximum execution time
        retry_attempts: Number of retry attempts on failure
    """
    worker_id: str
    worker_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True
    timeout_seconds: float = 30.0
    retry_attempts: int = 3


class Worker(ABC):
    """
    Abstract base class for all TSM workers.

    A worker is a specialized algorithm, sensor interface, or data analysis module
    that processes input data and returns a result with confidence score.
    """

    def __init__(self, worker_id: str, config: Optional[WorkerConfig] = None):
        """
        Initialize worker.

        Args:
            worker_id: Unique identifier for this worker
            config: Worker configuration
        """
        self.worker_id = worker_id
        self.config = config or WorkerConfig(worker_id=worker_id, worker_type=self.__class__.__name__)
        self.status = WorkerStatus.IDLE
        self.execution_count = 0
        self.failure_count = 0
        self.total_processing_time_ms = 0.0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process input data and return result.

        This is the main method that must be implemented by all workers.

        Args:
            data: Input data to process

        Returns:
            Processed result

        Raises:
            Exception: If processing fails
        """
        pass

    @abstractmethod
    def get_confidence(self, data: Any, result: Any) -> float:
        """
        Calculate confidence score for the result.

        Args:
            data: Original input data
            result: Processed result

        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass

    def execute(self, data: Any, trace_id: Optional[str] = None) -> WorkerResult:
        """
        Execute worker with full error handling and timing.

        Args:
            data: Input data to process
            trace_id: Optional trace ID for distributed tracing

        Returns:
            WorkerResult with status, timing, and metadata
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        start_time = time.time()
        self.status = WorkerStatus.ACTIVE
        self.execution_count += 1

        try:
            # Process data
            result_value = self.process(data)

            # Calculate confidence
            confidence = self.get_confidence(data, result_value)

            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            self.total_processing_time_ms += processing_time_ms

            # Create result
            result = WorkerResult(
                worker_id=self.worker_id,
                value=result_value,
                confidence=confidence,
                processing_time_ms=processing_time_ms,
                status=ResultStatus.SUCCESS,
                trace_id=trace_id,
                metadata={
                    "worker_type": self.__class__.__name__,
                    "execution_count": self.execution_count,
                    "parameters": self.config.parameters,
                }
            )

            self.status = WorkerStatus.IDLE
            self.logger.debug(f"Worker {self.worker_id} completed successfully in {processing_time_ms:.2f}ms")

            return result

        except Exception as e:
            self.failure_count += 1
            self.status = WorkerStatus.FAILED
            processing_time_ms = (time.time() - start_time) * 1000

            self.logger.error(f"Worker {self.worker_id} failed: {str(e)}", exc_info=True)

            return WorkerResult(
                worker_id=self.worker_id,
                value=None,
                confidence=0.0,
                processing_time_ms=processing_time_ms,
                status=ResultStatus.FAILED,
                trace_id=trace_id,
                metadata={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "failure_count": self.failure_count,
                }
            )

    def apply_variation(self, variation_params: Dict[str, Any]) -> 'Worker':
        """
        Create a variation of this worker with modified parameters.

        This implements the Worker Variation Formula (FR1.1.3).

        Args:
            variation_params: Parameters to modify

        Returns:
            New worker instance with varied parameters
        """
        # Create a copy of current config
        varied_config = WorkerConfig(
            worker_id=f"{self.worker_id}_var_{uuid.uuid4().hex[:8]}",
            worker_type=self.config.worker_type,
            parameters={**self.config.parameters, **variation_params},
            input_schema=self.config.input_schema,
            output_schema=self.config.output_schema,
            thresholds=self.config.thresholds,
            enabled=self.config.enabled,
            timeout_seconds=self.config.timeout_seconds,
            retry_attempts=self.config.retry_attempts,
        )

        # Create new worker instance
        return self.__class__(varied_config.worker_id, varied_config)

    def get_statistics(self) -> Dict[str, Any]:
        """Get worker performance statistics."""
        return {
            "worker_id": self.worker_id,
            "worker_type": self.__class__.__name__,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "failure_count": self.failure_count,
            "failure_rate": self.failure_count / max(self.execution_count, 1),
            "average_processing_time_ms": self.total_processing_time_ms / max(self.execution_count, 1),
            "total_processing_time_ms": self.total_processing_time_ms,
        }


class WorkerPool:
    """
    Manages a pool of workers for parallel execution.

    Implements FR1.1.4 - Worker Deployment & Orchestration.
    """

    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize worker pool.

        Args:
            max_workers: Maximum number of parallel workers (None = CPU count)
        """
        self.workers: Dict[str, Worker] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(f"{__name__}.WorkerPool")

    def register_worker(self, worker: Worker) -> None:
        """
        Register a worker in the pool.

        Args:
            worker: Worker instance to register
        """
        if worker.worker_id in self.workers:
            self.logger.warning(f"Worker {worker.worker_id} already registered, replacing")

        self.workers[worker.worker_id] = worker
        self.logger.info(f"Registered worker: {worker.worker_id} ({worker.__class__.__name__})")

    def unregister_worker(self, worker_id: str) -> None:
        """
        Unregister a worker from the pool.

        Args:
            worker_id: ID of worker to remove
        """
        if worker_id in self.workers:
            del self.workers[worker_id]
            self.logger.info(f"Unregistered worker: {worker_id}")

    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Get a worker by ID."""
        return self.workers.get(worker_id)

    def get_active_workers(self) -> List[Worker]:
        """Get list of enabled and healthy workers."""
        return [
            worker for worker in self.workers.values()
            if worker.config.enabled and worker.status not in [WorkerStatus.QUARANTINED, WorkerStatus.DISABLED]
        ]

    def execute_parallel(self, data: Any, worker_ids: Optional[List[str]] = None,
                        trace_id: Optional[str] = None) -> List[WorkerResult]:
        """
        Execute multiple workers in parallel on the same data.

        Args:
            data: Input data to process
            worker_ids: Specific worker IDs to use (None = all active workers)
            trace_id: Optional trace ID for distributed tracing

        Returns:
            List of WorkerResult objects
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        # Determine which workers to execute
        if worker_ids:
            workers_to_execute = [self.workers[wid] for wid in worker_ids if wid in self.workers]
        else:
            workers_to_execute = self.get_active_workers()

        if not workers_to_execute:
            self.logger.warning("No active workers available for execution")
            return []

        self.logger.info(f"Executing {len(workers_to_execute)} workers in parallel (trace_id: {trace_id})")

        # Submit all workers for parallel execution
        futures = {
            self.executor.submit(worker.execute, data, trace_id): worker
            for worker in workers_to_execute
        }

        # Collect results as they complete
        results = []
        for future in as_completed(futures):
            worker = futures[future]
            try:
                result = future.result(timeout=worker.config.timeout_seconds)
                results.append(result)
            except TimeoutError:
                self.logger.error(f"Worker {worker.worker_id} timed out")
                results.append(WorkerResult(
                    worker_id=worker.worker_id,
                    value=None,
                    confidence=0.0,
                    processing_time_ms=worker.config.timeout_seconds * 1000,
                    status=ResultStatus.TIMEOUT,
                    trace_id=trace_id,
                ))
            except Exception as e:
                self.logger.error(f"Worker {worker.worker_id} raised exception: {str(e)}")
                results.append(WorkerResult(
                    worker_id=worker.worker_id,
                    value=None,
                    confidence=0.0,
                    processing_time_ms=0.0,
                    status=ResultStatus.FAILED,
                    trace_id=trace_id,
                    metadata={"error": str(e)}
                ))

        return results

    def create_variations(self, worker: Worker, variation_strategy: Callable[[Dict[str, Any]], List[Dict[str, Any]]],
                         num_variations: int = 3) -> List[Worker]:
        """
        Create multiple variations of a worker.

        Implements the Worker Variation Formula (FR1.1.3).

        Args:
            worker: Base worker to create variations from
            variation_strategy: Function that generates variation parameters
            num_variations: Number of variations to create

        Returns:
            List of worker variations
        """
        base_params = worker.config.parameters
        variation_params_list = variation_strategy(base_params, num_variations)

        variations = []
        for variation_params in variation_params_list:
            varied_worker = worker.apply_variation(variation_params)
            variations.append(varied_worker)
            self.register_worker(varied_worker)

        self.logger.info(f"Created {len(variations)} variations of worker {worker.worker_id}")
        return variations

    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get statistics for the entire worker pool."""
        total_executions = sum(w.execution_count for w in self.workers.values())
        total_failures = sum(w.failure_count for w in self.workers.values())

        status_counts = {}
        for worker in self.workers.values():
            status = worker.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_workers": len(self.workers),
            "active_workers": len(self.get_active_workers()),
            "total_executions": total_executions,
            "total_failures": total_failures,
            "overall_failure_rate": total_failures / max(total_executions, 1),
            "status_distribution": status_counts,
            "worker_statistics": [w.get_statistics() for w in self.workers.values()],
        }

    def shutdown(self) -> None:
        """Shutdown the worker pool and cleanup resources."""
        self.logger.info("Shutting down worker pool")
        self.executor.shutdown(wait=True)
        self.workers.clear()
