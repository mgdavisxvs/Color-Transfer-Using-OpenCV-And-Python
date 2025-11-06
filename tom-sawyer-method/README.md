# Tom Sawyer Method (TSM) Framework

**Version:** 0.1.0
**Status:** In Development

---

## Overview

The Tom Sawyer Method (TSM) is an enterprise-grade intelligent ensemble AI framework that orchestrates self-managing teams of specialized "workers" (AI algorithms, sensors, or analysis modules) to solve complex problems through:

- **Intelligent Aggregation** - Combines outputs using sophisticated strategies
- **Adaptive Resource Allocation** - Dynamically adjusts based on problem complexity
- **Continuous Learning** - Bayesian weight learning from performance history
- **High Reliability** - Fault tolerance, graceful degradation, and anomaly detection
- **Full Observability** - Comprehensive KPI tracking and audit logging

### Key Innovation

Self-managing teams of AI specialists that learn, adapt, and maintain high reliability through collective intelligence, inspired by Tom Sawyer's ability to delegate and coordinate diverse skills effectively.

---

## Features

### ✅ Implemented (Core Framework)

- **Worker Management** (FR1.1.x)
  - Abstract Worker base class with standardized interface
  - Worker Pool for parallel execution
  - Worker variation formula for ensemble diversity
  - Configurable worker parameters and lifecycle management

- **Aggregation Oracle** (FR1.2.x)
  - Multiple aggregation strategies:
    - Weighted Average (numerical)
    - Majority Voting (categorical)
    - Confidence-Based (best result)
    - Median (robust to outliers)
  - Bayesian Weight Learning with exponential moving average
  - Adaptive learning rate based on performance stability
  - Dynamic weight application during aggregation

- **Result Structures**
  - Comprehensive WorkerResult with confidence, timing, and metadata
  - AggregatedResult with statistics and traceability
  - Status tracking and validation

### 🚧 In Development

- **Adaptive Intelligence Layer** (FR1.3.x)
  - Complexity assessment (Shannon Entropy, feature-based)
  - Dynamic resource allocation
  - Selective specialist activation

- **Operational Security & Reliability** (FR1.4.x)
  - Graceful degradation under resource constraints
  - Anomaly detection (statistical outlier rejection)
  - Fault isolation and quarantine

- **Performance Monitoring** (FR1.5.x)
  - KPI tracking and storage
  - Performance reporting and dashboards
  - Structured audit logging

- **Configuration & API**
  - YAML-based configuration
  - REST API with FastAPI
  - Client SDK

### 📋 Planned

- Example implementations:
  - Fraud detection
  - Quality control
  - Predictive maintenance
  - Recommendation systems
- Comprehensive test suite
- Full documentation
- Deployment scripts (Docker, Kubernetes)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  TSM Framework                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Data Ingestion → Worker Pool → Adaptive Engine     │
│                         ↓                            │
│                  Aggregation Oracle                  │
│                         ↓                            │
│             Reliability & Security Layer             │
│                         ↓                            │
│          Performance Monitoring & Audit              │
│                         ↓                            │
│             Configuration & API Gateway              │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd tom-sawyer-method

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

---

## Quick Start

### Basic Usage

```python
from tsm.core.worker import Worker, WorkerPool, WorkerConfig
from tsm.core.aggregator import Aggregator, WeightedAverageAggregation
from tsm.core.learner import BayesianWeightLearner
from tsm.core.result import WorkerResult

# Define a custom worker
class MyWorker(Worker):
    def process(self, data):
        # Your algorithm here
        return data * 2

    def get_confidence(self, data, result):
        # Calculate confidence
        return 0.95

# Create worker pool
pool = WorkerPool(max_workers=10)

# Register workers
for i in range(5):
    worker = MyWorker(
        worker_id=f"worker_{i}",
        config=WorkerConfig(
            worker_id=f"worker_{i}",
            worker_type="MyWorker"
        )
    )
    pool.register_worker(worker)

# Execute workers in parallel
data = 42
results = pool.execute_parallel(data)

# Create aggregator with learning
learner = BayesianWeightLearner(alpha=0.1)
strategy = WeightedAverageAggregation(use_confidence=True)
aggregator = Aggregator(strategy=strategy, weight_learner=learner)

# Aggregate results
final_result = aggregator.aggregate(results)

print(f"Result: {final_result.value}")
print(f"Confidence: {final_result.confidence}")
print(f"Workers used: {final_result.num_workers}")
```

### With Weight Learning

```python
from tsm.core.learner import PerformanceMetric

# Simulate performance feedback
for worker_id in ["worker_0", "worker_1", "worker_2"]:
    metric = PerformanceMetric(
        worker_id=worker_id,
        predicted=predicted_value,
        actual=actual_value,
        confidence=0.9,
        accuracy=0.95  # Calculated based on your metric
    )
    learner.update_weight(worker_id, metric)

# Weights are automatically applied in next aggregation
final_result = aggregator.aggregate(results)
```

---

## Project Structure

```
tom-sawyer-method/
├── README.md                          # This file
├── requirements.txt                   # Core dependencies
├── requirements-dev.txt               # Development dependencies
├── setup.py                           # Package setup (TBD)
├── TSM_IMPLEMENTATION_ANALYSIS.md    # Detailed technical analysis
├── tsm/                              # Main package
│   ├── __init__.py
│   ├── core/                         # Core components
│   │   ├── __init__.py
│   │   ├── worker.py                 # Worker base class and pool
│   │   ├── aggregator.py             # Aggregation strategies
│   │   ├── learner.py                # Weight learning
│   │   └── result.py                 # Result data structures
│   ├── intelligence/                 # Adaptive intelligence (TBD)
│   ├── reliability/                  # Reliability features (TBD)
│   ├── monitoring/                   # Monitoring & audit (TBD)
│   ├── config/                       # Configuration (TBD)
│   ├── api/                          # REST API (TBD)
│   ├── storage/                      # Storage backends (TBD)
│   └── utils/                        # Utilities (TBD)
├── examples/                         # Example implementations (TBD)
├── tests/                            # Test suite (TBD)
├── docs/                             # Documentation (TBD)
└── config/                           # Configuration files (TBD)
```

---

## Core Components

### Worker

Abstract base class for all workers. Implement `process()` and `get_confidence()` methods.

```python
class Worker(ABC):
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process input data and return result."""
        pass

    @abstractmethod
    def get_confidence(self, data: Any, result: Any) -> float:
        """Calculate confidence score (0.0 to 1.0)."""
        pass
```

### WorkerPool

Manages and orchestrates workers for parallel execution.

**Key Methods:**
- `register_worker(worker)` - Add worker to pool
- `execute_parallel(data, worker_ids=None)` - Execute workers in parallel
- `create_variations(worker, strategy, num)` - Create worker variations
- `get_pool_statistics()` - Get performance statistics

### Aggregation Strategies

Multiple strategies for combining worker outputs:

- **WeightedAverageAggregation** - For numerical outputs
- **MajorityVotingAggregation** - For categorical outputs
- **ConfidenceBasedAggregation** - Select best result
- **MedianAggregation** - Robust to outliers

### BayesianWeightLearner

Continuously learns worker weights using Bayesian update rule:

```
w_i(t+1) = w_i(t) * (1 - α) + accuracy_i(t) * α
```

**Features:**
- Configurable learning rate (α)
- Confidence-scaled updates
- Performance statistics tracking
- State persistence (save/load)

**Adaptive Variant:** `AdaptiveBayesianLearner` adjusts learning rate based on performance stability.

---

## Configuration

Configuration via `WorkerConfig`:

```python
config = WorkerConfig(
    worker_id="my_worker_1",
    worker_type="MyWorkerClass",
    parameters={
        "threshold": 0.75,
        "model_path": "/path/to/model"
    },
    enabled=True,
    timeout_seconds=30.0,
    retry_attempts=3
)
```

---

## Performance

### Design Targets

- **Latency:** < 50ms for critical paths (99th percentile)
- **Throughput:** 10,000+ transactions/second
- **Scalability:** Linear scaling up to 100 nodes
- **Reliability:** 99.99% uptime

### Current Status

Core framework complete with efficient parallel execution and minimal overhead. Full performance benchmarking pending.

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=tsm --cov-report=html

# Specific test file
pytest tests/unit/test_worker.py
```

### Code Quality

```bash
# Format code
black tsm/
isort tsm/

# Type checking
mypy tsm/

# Linting
pylint tsm/
flake8 tsm/
```

---

## Roadmap

### Phase 1: Core Foundation ✅ (Current)
- [x] Worker base class and pool management
- [x] Aggregation strategies
- [x] Bayesian weight learning
- [x] Result structures
- [x] Basic documentation

### Phase 2: Intelligence Layer (In Progress)
- [ ] Complexity assessment
- [ ] Resource allocator
- [ ] Specialist selector

### Phase 3: Reliability & Security
- [ ] Graceful degradation
- [ ] Anomaly detection
- [ ] Fault isolation

### Phase 4: Monitoring & Observability
- [ ] KPI tracking
- [ ] Audit logging
- [ ] Performance reporting

### Phase 5: API & Integration
- [ ] REST API
- [ ] Client SDK
- [ ] Storage backends

### Phase 6: Examples & Documentation
- [ ] Fraud detection example
- [ ] Quality control example
- [ ] Predictive maintenance example
- [ ] Comprehensive docs

---

## Use Cases

### Fraud Detection
Multiple fraud detection algorithms working together with adaptive resource allocation for high-value transactions.

### Quality Control
Ensemble of visual inspection algorithms for manufacturing defect detection with fault tolerance.

### Predictive Maintenance
Multiple sensor analysis modules predicting equipment failures with selective specialist activation.

### Personalized Recommendations
Diverse recommendation engines combined with continuous learning from user feedback.

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

---

## License

[TBD]

---

## Contact

For questions or support, please open an issue on GitHub.

---

## Acknowledgments

Based on the Software Requirements Specification for the Tom Sawyer Method, implementing an intelligent, adaptive, and resilient problem-solving framework for diverse application domains.

---

**Status:** Core framework complete, additional features in active development.
