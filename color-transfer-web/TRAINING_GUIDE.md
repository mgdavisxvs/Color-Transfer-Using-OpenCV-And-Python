# TSM Training System - Complete Guide

## Overview

The TSM Training System enables **explicit training** of the ensemble AI system using ground truth data. Users can create labeled datasets, run batch training, validate performance, and track learning progress over time.

---

## 🎯 Key Features

### 1. **Dataset Management**
- ✅ Add training examples with ground truth
- ✅ Store examples in SQLite database
- ✅ Track metadata and validation scores
- ✅ Efficient retrieval for batch operations

### 2. **Batch Training**
- ✅ Train on multiple examples
- ✅ Multiple epochs support
- ✅ Automatic train/validation split
- ✅ Progress tracking

### 3. **Ground Truth Validation**
- ✅ Compare worker outputs to desired results
- ✅ Calculate similarity scores (MSE + Histogram)
- ✅ Update weights based on performance

### 4. **Performance Tracking**
- ✅ Training session history
- ✅ Per-worker accuracy metrics
- ✅ Weight evolution over time
- ✅ Validation results

### 5. **Weight Management**
- ✅ Export trained weights
- ✅ Import pre-trained weights
- ✅ Reset to defaults
- ✅ Persistent storage

---

## 📊 Architecture

```
User provides ground truth images
           ↓
TrainingDataManager (SQLite)
           ↓
TrainingEngine
    ├── Execute workers on examples
    ├── Compare results to ground truth
    ├── Calculate similarity scores
    └── Update Bayesian weights
           ↓
TrainingSession (saved)
    ├── Initial weights
    ├── Final weights
    ├── Metrics history
    └── Performance data
           ↓
Improved TSM Model
```

---

## 🚀 Quick Start

### 1. Enable Training in App

Add to `app_tsm.py`:

```python
from training_routes import training_bp, init_training

# After creating worker_pool and weight_learner
init_training(worker_pool, weight_learner, db_path="tsm_training.db")

# Register blueprint
app.register_blueprint(training_bp)
```

### 2. Create Training Example

```python
from tsm_training import TrainingManager

# Initialize
training_manager = TrainingManager(worker_pool, weight_learner)

# Add example
example = training_manager.add_training_example(
    source_path="path/to/source.jpg",
    target_path="path/to/target.jpg",
    ground_truth_path="path/to/desired_output.jpg",
    metadata={'description': 'Sunset color transfer'}
)
```

### 3. Run Training

```python
# Train on all examples
results = training_manager.train(
    epochs=3,
    validation_split=0.2,
    verbose=True
)

print(f"Training complete!")
print(f"Initial weights: {results['session']['initial_weights']}")
print(f"Final weights: {results['session']['final_weights']}")
print(f"Validation accuracy: {results['validation']['avg_accuracy']:.4f}")
```

---

## 📡 API Endpoints

### POST `/training/add-example`

Add a new training example.

**Form Data:**
```
source: Image file (source colors)
target: Image file (to be transformed)
ground_truth: Image file (desired output)
metadata: JSON string (optional)
```

**Response:**
```json
{
  "success": true,
  "example_id": "uuid",
  "message": "Training example added successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/training/add-example \
  -F "source=@source.jpg" \
  -F "target=@target.jpg" \
  -F "ground_truth=@desired_output.jpg" \
  -F 'metadata={"quality": "high", "style": "sunset"}'
```

---

### GET `/training/examples`

Get all training examples.

**Query Parameters:**
- `limit` (optional): Maximum number of examples to return

**Response:**
```json
{
  "success": true,
  "examples": [
    {
      "example_id": "uuid",
      "created_at": "2025-11-06T10:30:00",
      "metadata": {...},
      "has_results": true
    }
  ],
  "total": 42
}
```

---

### POST `/training/train`

Start a training session.

**JSON Body:**
```json
{
  "num_examples": 20,
  "epochs": 3,
  "validation_split": 0.2,
  "verbose": false
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "session": {
      "session_id": "uuid",
      "num_examples": 20,
      "epochs": 3,
      "initial_weights": {...},
      "final_weights": {...},
      "metrics_history": [...]
    },
    "validation": {
      "avg_accuracy": 0.87,
      "worker_accuracies": {...}
    }
  },
  "message": "Training completed successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 5,
    "validation_split": 0.2,
    "verbose": true
  }'
```

---

### POST `/training/validate`

Validate current model.

**JSON Body:**
```json
{
  "example_ids": ["uuid1", "uuid2"]  // optional
}
```

**Response:**
```json
{
  "success": true,
  "validation_results": {
    "num_examples": 10,
    "avg_accuracy": 0.85,
    "worker_accuracies": {
      "standard_transfer": {
        "mean": 0.82,
        "std": 0.08,
        "min": 0.65,
        "max": 0.95
      }
    }
  }
}
```

---

### GET `/training/progress`

Get training progress and statistics.

**Response:**
```json
{
  "success": true,
  "progress": {
    "dataset_stats": {
      "total_examples": 50,
      "processed_examples": 45,
      "unprocessed_examples": 5,
      "total_sessions": 3
    },
    "worker_stats": {
      "standard_transfer": {
        "current_weight": 1.08,
        "stats": {
          "mean_accuracy": 0.85,
          "update_count": 45
        }
      }
    },
    "current_weights": {...}
  }
}
```

---

### GET `/training/weights/export`

Export current weights to JSON file.

**Response:** Downloads `tsm_weights_YYYYMMDD_HHMMSS.json`

**cURL Example:**
```bash
curl http://localhost:5000/training/weights/export -o weights.json
```

---

### POST `/training/weights/import`

Import weights from JSON file.

**Form Data:**
```
file: Weights JSON file
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/training/weights/import \
  -F "file=@weights.json"
```

---

### POST `/training/reset-weights`

Reset all weights to default.

**JSON Body (optional):**
```json
{
  "default_weight": 1.0
}
```

---

## 💻 Python Usage Examples

### Example 1: Basic Training Workflow

```python
from tsm_training import TrainingManager
from tsm.core.worker import WorkerPool
from tsm.core.learner import BayesianWeightLearner
from tsm_workers import create_color_transfer_workers

# Setup
worker_pool = WorkerPool(max_workers=10)
for worker in create_color_transfer_workers():
    worker_pool.register_worker(worker)

weight_learner = BayesianWeightLearner(alpha=0.15)
training_manager = TrainingManager(worker_pool, weight_learner)

# Add training examples
for i in range(10):
    training_manager.add_training_example(
        source_path=f"data/source_{i}.jpg",
        target_path=f"data/target_{i}.jpg",
        ground_truth_path=f"data/ground_truth_{i}.jpg",
        metadata={'index': i}
    )

# Train
results = training_manager.train(epochs=5, validation_split=0.2, verbose=True)

# Check results
print(f"Final accuracy: {results['validation']['avg_accuracy']:.4f}")
print(f"Best worker: {max(results['session']['final_weights'].items(), key=lambda x: x[1])}")
```

---

### Example 2: Incremental Training

```python
# Train in batches
batch_size = 5
all_examples = training_manager.data_manager.get_all_examples()

for i in range(0, len(all_examples), batch_size):
    batch = all_examples[i:i+batch_size]

    session = training_manager.training_engine.train_batch(
        batch,
        epochs=1,
        verbose=True
    )

    print(f"Batch {i//batch_size + 1} complete")
    print(f"Avg accuracy: {session.metrics_history[-1]['avg_accuracy']:.4f}")

# Export weights after training
training_manager.export_weights("trained_weights.json")
```

---

### Example 3: Validation and Analysis

```python
# Get all examples
examples = training_manager.data_manager.get_all_examples()

# Validate current model
validation_results = training_manager.training_engine.validate(examples)

# Analyze worker performance
print("\nWorker Performance:")
print("-" * 50)
for worker_id, stats in validation_results['worker_accuracies'].items():
    print(f"{worker_id:30} {stats['mean']:.4f} ± {stats['std']:.4f}")

# Find best and worst workers
workers_sorted = sorted(
    validation_results['worker_accuracies'].items(),
    key=lambda x: x[1]['mean'],
    reverse=True
)

print(f"\nBest worker:  {workers_sorted[0][0]} ({workers_sorted[0][1]['mean']:.4f})")
print(f"Worst worker: {workers_sorted[-1][0]} ({workers_sorted[-1][1]['mean']:.4f})")
```

---

## 📊 Similarity Calculation

The training system uses a sophisticated similarity metric combining:

### 1. Mean Squared Error (MSE)
```python
mse = np.mean((img1_lab - img2_lab) ** 2)
mse_similarity = 1.0 - (mse / max_mse)
```

### 2. Histogram Correlation
```python
for each LAB channel:
    hist1 = calculate_histogram(img1[:,:,channel])
    hist2 = calculate_histogram(img2[:,:,channel])
    similarity = cv2.compareHist(hist1, hist2, CORREL)
```

### 3. Combined Score
```python
final_similarity = 0.6 × mse_similarity + 0.4 × hist_similarity
```

**Result:** Value between 0.0 (completely different) and 1.0 (identical)

---

## 🎯 Training Strategies

### Strategy 1: Curated Dataset

**Best for:** Production deployment

```python
# Carefully select diverse examples
examples = [
    ('sunset.jpg', 'beach.jpg', 'sunset_beach.jpg'),
    ('vintage.jpg', 'portrait.jpg', 'vintage_portrait.jpg'),
    ('vibrant.jpg', 'landscape.jpg', 'vibrant_landscape.jpg'),
    # ... more diverse examples
]

for source, target, gt in examples:
    training_manager.add_training_example(source, target, gt)

# Train with many epochs
results = training_manager.train(epochs=10, validation_split=0.2)
```

### Strategy 2: Continuous Learning

**Best for:** Ongoing improvement

```python
# Add examples as users provide feedback
@app.route('/result-feedback', methods=['POST'])
def result_feedback():
    data = request.json

    if data['rating'] >= 4:  # User liked the result
        # Add as training example
        training_manager.add_training_example(
            source_path=data['source_path'],
            target_path=data['target_path'],
            ground_truth_path=data['result_path'],
            metadata={'rating': data['rating']}
        )

        # Periodic retraining
        if should_retrain():
            training_manager.train(epochs=1, verbose=False)
```

### Strategy 3: A/B Testing

**Best for:** Experimental improvements

```python
# Save current weights
training_manager.export_weights("weights_baseline.json")

# Train with different parameters
for alpha in [0.1, 0.15, 0.2]:
    # Reset and train
    training_manager.weight_learner.alpha = alpha
    training_manager.reset_weights()

    results = training_manager.train(epochs=5, validation_split=0.3)

    print(f"Alpha {alpha}: Accuracy {results['validation']['avg_accuracy']:.4f}")

# Choose best alpha, restore those weights
```

---

## 📈 Monitoring Training Progress

### Track Learning Curves

```python
session = training_manager.data_manager.get_session(session_id)

# Extract epoch-wise metrics
epochs = []
accuracies = []

for epoch_data in session.metrics_history:
    epochs.append(epoch_data['epoch'])
    accuracies.append(epoch_data['avg_accuracy'])

# Plot learning curve
import matplotlib.pyplot as plt

plt.plot(epochs, accuracies)
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training Progress')
plt.grid(True)
plt.show()
```

### Monitor Weight Evolution

```python
# Get all sessions
sessions = training_manager.data_manager.get_all_sessions()

for session in sessions:
    print(f"\nSession {session.session_id}")
    print(f"Duration: {session.start_time} to {session.end_time}")

    for worker_id in session.initial_weights:
        initial = session.initial_weights[worker_id]
        final = session.final_weights[worker_id]
        change = final - initial

        print(f"  {worker_id}: {initial:.4f} → {final:.4f} ({change:+.4f})")
```

---

## 🔧 Database Schema

### Training Examples Table

```sql
CREATE TABLE training_examples (
    example_id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    ground_truth_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata TEXT,  -- JSON
    worker_results TEXT,  -- JSON
    validation_scores TEXT  -- JSON
);
```

### Training Sessions Table

```sql
CREATE TABLE training_sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT,
    num_examples INTEGER,
    epochs INTEGER,
    learning_rate REAL,
    initial_weights TEXT,  -- JSON
    final_weights TEXT,  -- JSON
    metrics_history TEXT,  -- JSON
    status TEXT
);
```

### Training Metrics Table

```sql
CREATE TABLE training_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    epoch INTEGER,
    example_id TEXT,
    worker_id TEXT,
    accuracy REAL,
    confidence REAL,
    loss REAL,
    timestamp TEXT,
    FOREIGN KEY (session_id) REFERENCES training_sessions(session_id)
);
```

---

## 🎓 Best Practices

### 1. Dataset Quality
✅ Use diverse examples
✅ Include edge cases
✅ Ensure ground truth quality
✅ Balance dataset distribution

### 2. Training Parameters
✅ Start with small learning rate (0.1-0.15)
✅ Use validation split (15-25%)
✅ Multiple epochs (3-10)
✅ Monitor convergence

### 3. Validation
✅ Validate before deployment
✅ Test on held-out data
✅ Check individual worker performance
✅ Verify weight changes make sense

### 4. Weight Management
✅ Export weights after successful training
✅ Keep baseline weights as backup
✅ Document weight changes
✅ Version control weight files

---

## 🚨 Troubleshooting

### Issue: Low Training Accuracy

**Possible Causes:**
- Poor ground truth quality
- Insufficient training examples
- Learning rate too high/low
- Workers not suitable for task

**Solutions:**
```python
# 1. Check dataset quality
examples = training_manager.data_manager.get_all_examples()
for ex in examples[:5]:
    # Visually inspect
    source = cv2.imread(ex.source_path)
    target = cv2.imread(ex.target_path)
    gt = cv2.imread(ex.ground_truth_path)
    # Display and verify quality

# 2. Adjust learning rate
training_manager.weight_learner.alpha = 0.1  # Lower

# 3. More training examples
# Add at least 20-30 diverse examples
```

### Issue: Weights Not Updating

**Check:**
```python
# Before training
initial = training_manager.weight_learner.get_all_weights()

# Train
training_manager.train(epochs=3, verbose=True)

# After training
final = training_manager.weight_learner.get_all_weights()

# Compare
for worker_id in initial:
    print(f"{worker_id}: {initial[worker_id]:.4f} → {final[worker_id]:.4f}")
```

### Issue: Database Errors

```bash
# Check database
sqlite3 tsm_training.db ".schema"

# Verify integrity
sqlite3 tsm_training.db "PRAGMA integrity_check;"

# Backup and recreate if needed
cp tsm_training.db tsm_training_backup.db
rm tsm_training.db
# Database will be recreated on next run
```

---

## 🎯 Example Use Cases

### Use Case 1: Style Transfer for Photography

```python
# Train for specific photography styles
styles = ['vintage', 'modern', 'film', 'digital']

for style in styles:
    # Add 10 examples per style
    for i in range(10):
        training_manager.add_training_example(
            source_path=f"styles/{style}/source_{i}.jpg",
            target_path=f"styles/{style}/target_{i}.jpg",
            ground_truth_path=f"styles/{style}/output_{i}.jpg",
            metadata={'style': style}
        )

# Train
results = training_manager.train(epochs=5)
```

### Use Case 2: Quality Control

```python
# Train to recognize "good" color transfers
def is_good_transfer(similarity_score):
    return similarity_score > 0.85

# Only add high-quality examples
for result in production_results:
    if is_good_transfer(result.quality_score):
        training_manager.add_training_example(
            source_path=result.source,
            target_path=result.target,
            ground_truth_path=result.output,
            metadata={'quality': 'high', 'score': result.quality_score}
        )
```

---

## 📚 Advanced Topics

### Custom Similarity Metrics

```python
# Extend TrainingEngine
class CustomTrainingEngine(TrainingEngine):
    def calculate_similarity(self, img1, img2):
        # Your custom metric
        # e.g., perceptual hash, LPIPS, etc.
        return custom_similarity_score
```

### Weighted Training Examples

```python
# Weight important examples more
for example in high_priority_examples:
    # Train multiple times
    for _ in range(3):
        training_manager.training_engine.train_on_example(example)
```

### Transfer Learning

```python
# Load pre-trained weights
training_manager.import_weights("pretrained_weights.json")

# Fine-tune on specific domain
results = training_manager.train(
    num_examples=10,
    epochs=2,  # Few epochs for fine-tuning
    validation_split=0.1
)
```

---

## 📊 Expected Results

### Typical Training Progress

```
Initial State:
  All weights: ~1.0
  Avg accuracy: ~0.75-0.80

After 10 examples (1 epoch):
  Weight range: 0.9-1.1
  Avg accuracy: ~0.80-0.85

After 30 examples (3 epochs):
  Weight range: 0.85-1.15
  Avg accuracy: ~0.85-0.90

After 100 examples (5 epochs):
  Weight range: 0.75-1.25
  Avg accuracy: ~0.90-0.95
  Clear worker hierarchy established
```

---

## 🎉 Summary

The TSM Training System provides:

✅ **Explicit Training** with ground truth data
✅ **Batch Processing** for efficiency
✅ **Validation** for quality assurance
✅ **Progress Tracking** for transparency
✅ **Weight Management** for reproducibility
✅ **REST API** for integration
✅ **Database Storage** for persistence

**Start training your TSM model today for superior results!**
