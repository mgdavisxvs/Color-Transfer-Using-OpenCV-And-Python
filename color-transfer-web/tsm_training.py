"""
TSM Training System

This module provides comprehensive training capabilities for the Tom Sawyer Method,
including dataset management, batch training, validation, and performance tracking.
"""

import json
import pickle
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
import cv2

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'tom-sawyer-method'))
from tsm.core.learner import PerformanceMetric, BayesianWeightLearner
from tsm.core.worker import WorkerPool
from tsm.core.result import WorkerResult


@dataclass
class TrainingExample:
    """A single training example with ground truth."""
    example_id: str
    source_path: str
    target_path: str
    ground_truth_path: str  # User-provided desired output
    created_at: str
    metadata: Dict[str, Any]
    worker_results: Optional[Dict[str, Any]] = None
    validation_scores: Optional[Dict[str, float]] = None


@dataclass
class TrainingSession:
    """Information about a training session."""
    session_id: str
    start_time: str
    end_time: Optional[str]
    num_examples: int
    epochs: int
    learning_rate: float
    initial_weights: Dict[str, float]
    final_weights: Dict[str, float]
    metrics_history: List[Dict[str, Any]]
    status: str  # 'running', 'completed', 'failed'


class TrainingDataManager:
    """
    Manages training datasets for TSM.

    Stores training examples with ground truth and provides
    efficient retrieval for batch training.
    """

    def __init__(self, db_path: str = "tsm_training.db"):
        """
        Initialize training data manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for training data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Training examples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_examples (
                example_id TEXT PRIMARY KEY,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                ground_truth_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                worker_results TEXT,
                validation_scores TEXT
            )
        """)

        # Training sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                num_examples INTEGER,
                epochs INTEGER,
                learning_rate REAL,
                initial_weights TEXT,
                final_weights TEXT,
                metrics_history TEXT,
                status TEXT
            )
        """)

        # Training metrics table (for detailed tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_metrics (
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
            )
        """)

        conn.commit()
        conn.close()

    def add_example(self, example: TrainingExample) -> bool:
        """
        Add a training example to the dataset.

        Args:
            example: TrainingExample to add

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO training_examples
                (example_id, source_path, target_path, ground_truth_path,
                 created_at, metadata, worker_results, validation_scores)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                example.example_id,
                example.source_path,
                example.target_path,
                example.ground_truth_path,
                example.created_at,
                json.dumps(example.metadata),
                json.dumps(example.worker_results) if example.worker_results else None,
                json.dumps(example.validation_scores) if example.validation_scores else None
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error adding example: {e}")
            return False

    def get_example(self, example_id: str) -> Optional[TrainingExample]:
        """Get a training example by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM training_examples WHERE example_id = ?
        """, (example_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return TrainingExample(
                example_id=row[0],
                source_path=row[1],
                target_path=row[2],
                ground_truth_path=row[3],
                created_at=row[4],
                metadata=json.loads(row[5]) if row[5] else {},
                worker_results=json.loads(row[6]) if row[6] else None,
                validation_scores=json.loads(row[7]) if row[7] else None
            )
        return None

    def get_all_examples(self, limit: Optional[int] = None) -> List[TrainingExample]:
        """Get all training examples."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM training_examples ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        examples = []
        for row in rows:
            examples.append(TrainingExample(
                example_id=row[0],
                source_path=row[1],
                target_path=row[2],
                ground_truth_path=row[3],
                created_at=row[4],
                metadata=json.loads(row[5]) if row[5] else {},
                worker_results=json.loads(row[6]) if row[6] else None,
                validation_scores=json.loads(row[7]) if row[7] else None
            ))

        return examples

    def update_example_results(self, example_id: str,
                               worker_results: Dict[str, Any],
                               validation_scores: Dict[str, float]):
        """Update worker results and validation scores for an example."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE training_examples
            SET worker_results = ?, validation_scores = ?
            WHERE example_id = ?
        """, (
            json.dumps(worker_results),
            json.dumps(validation_scores),
            example_id
        ))

        conn.commit()
        conn.close()

    def save_session(self, session: TrainingSession):
        """Save a training session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO training_sessions
            (session_id, start_time, end_time, num_examples, epochs,
             learning_rate, initial_weights, final_weights, metrics_history, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.start_time,
            session.end_time,
            session.num_examples,
            session.epochs,
            session.learning_rate,
            json.dumps(session.initial_weights),
            json.dumps(session.final_weights),
            json.dumps(session.metrics_history),
            session.status
        ))

        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> Optional[TrainingSession]:
        """Get a training session by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM training_sessions WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return TrainingSession(
                session_id=row[0],
                start_time=row[1],
                end_time=row[2],
                num_examples=row[3],
                epochs=row[4],
                learning_rate=row[5],
                initial_weights=json.loads(row[6]),
                final_weights=json.loads(row[7]),
                metrics_history=json.loads(row[8]),
                status=row[9]
            )
        return None

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics about the training dataset."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM training_examples")
        total_examples = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM training_sessions")
        total_sessions = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM training_examples
            WHERE worker_results IS NOT NULL
        """)
        processed_examples = cursor.fetchone()[0]

        conn.close()

        return {
            'total_examples': total_examples,
            'processed_examples': processed_examples,
            'unprocessed_examples': total_examples - processed_examples,
            'total_sessions': total_sessions
        }


class TrainingEngine:
    """
    Training engine for TSM workers.

    Handles batch training with ground truth data, validation,
    and performance tracking.
    """

    def __init__(self,
                 worker_pool: WorkerPool,
                 weight_learner: BayesianWeightLearner,
                 data_manager: TrainingDataManager):
        """
        Initialize training engine.

        Args:
            worker_pool: WorkerPool to train
            weight_learner: BayesianWeightLearner to update
            data_manager: TrainingDataManager for data access
        """
        self.worker_pool = worker_pool
        self.weight_learner = weight_learner
        self.data_manager = data_manager

    def calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate similarity between two images.

        Uses a combination of SSIM, MSE, and histogram comparison.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Ensure same size
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Convert to LAB for perceptual comparison
        img1_lab = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB).astype(float)
        img2_lab = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB).astype(float)

        # Calculate MSE
        mse = np.mean((img1_lab - img2_lab) ** 2)
        max_mse = 255.0 ** 2 * 3  # Max possible MSE for 3 channels
        mse_similarity = 1.0 - (mse / max_mse)

        # Calculate histogram similarity for each channel
        hist_similarities = []
        for i in range(3):
            hist1 = cv2.calcHist([img1_lab[:,:,i].astype(np.uint8)], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([img2_lab[:,:,i].astype(np.uint8)], [0], None, [256], [0, 256])

            # Normalize histograms
            hist1 = hist1 / hist1.sum()
            hist2 = hist2 / hist2.sum()

            # Compare using correlation
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            hist_similarities.append(max(0.0, similarity))

        hist_similarity = np.mean(hist_similarities)

        # Combined score (weighted average)
        final_similarity = 0.6 * mse_similarity + 0.4 * hist_similarity

        return float(np.clip(final_similarity, 0.0, 1.0))

    def train_on_example(self, example: TrainingExample) -> Dict[str, float]:
        """
        Train on a single example with ground truth.

        Args:
            example: TrainingExample with ground truth

        Returns:
            Dictionary of accuracy scores per worker
        """
        # Load images
        source_img = cv2.imread(example.source_path)
        target_img = cv2.imread(example.target_path)
        ground_truth_img = cv2.imread(example.ground_truth_path)

        if any(img is None for img in [source_img, target_img, ground_truth_img]):
            raise ValueError("Failed to load images")

        # Execute workers
        data = {'source': source_img, 'target': target_img}
        worker_results = self.worker_pool.execute_parallel(data)

        # Calculate accuracy for each worker
        accuracies = {}
        for result in worker_results:
            if result.is_valid():
                # Calculate similarity to ground truth
                accuracy = self.calculate_similarity(result.value, ground_truth_img)
                accuracies[result.worker_id] = accuracy

                # Update weights
                metric = PerformanceMetric(
                    worker_id=result.worker_id,
                    predicted=result.value,
                    actual=ground_truth_img,
                    confidence=result.confidence,
                    accuracy=accuracy
                )
                self.weight_learner.update_weight(result.worker_id, metric)

        return accuracies

    def train_batch(self,
                   examples: List[TrainingExample],
                   epochs: int = 1,
                   verbose: bool = True) -> TrainingSession:
        """
        Train on a batch of examples.

        Args:
            examples: List of training examples
            epochs: Number of training epochs
            verbose: Whether to print progress

        Returns:
            TrainingSession with results
        """
        import uuid

        session_id = str(uuid.uuid4())
        start_time = datetime.utcnow().isoformat()

        # Save initial weights
        initial_weights = self.weight_learner.get_all_weights().copy()

        metrics_history = []

        if verbose:
            print(f"Starting training session {session_id}")
            print(f"Examples: {len(examples)}, Epochs: {epochs}")
            print(f"Initial weights: {initial_weights}")

        # Training loop
        for epoch in range(epochs):
            epoch_metrics = {
                'epoch': epoch,
                'example_accuracies': [],
                'worker_accuracies': {},
                'avg_accuracy': 0.0
            }

            if verbose:
                print(f"\nEpoch {epoch + 1}/{epochs}")

            for i, example in enumerate(examples):
                try:
                    # Train on example
                    accuracies = self.train_on_example(example)
                    epoch_metrics['example_accuracies'].append(accuracies)

                    # Aggregate worker accuracies
                    for worker_id, accuracy in accuracies.items():
                        if worker_id not in epoch_metrics['worker_accuracies']:
                            epoch_metrics['worker_accuracies'][worker_id] = []
                        epoch_metrics['worker_accuracies'][worker_id].append(accuracy)

                    if verbose and (i + 1) % max(1, len(examples) // 10) == 0:
                        print(f"  Progress: {i + 1}/{len(examples)} examples")

                except Exception as e:
                    if verbose:
                        print(f"  Error on example {example.example_id}: {e}")

            # Calculate epoch statistics
            if epoch_metrics['example_accuracies']:
                all_accuracies = [
                    acc for example_accs in epoch_metrics['example_accuracies']
                    for acc in example_accs.values()
                ]
                epoch_metrics['avg_accuracy'] = np.mean(all_accuracies)

                # Average worker accuracies
                for worker_id in epoch_metrics['worker_accuracies']:
                    worker_accs = epoch_metrics['worker_accuracies'][worker_id]
                    epoch_metrics['worker_accuracies'][worker_id] = np.mean(worker_accs)

            metrics_history.append(epoch_metrics)

            if verbose:
                print(f"  Epoch {epoch + 1} complete - Avg accuracy: {epoch_metrics['avg_accuracy']:.4f}")

        # Save final weights
        final_weights = self.weight_learner.get_all_weights().copy()

        if verbose:
            print(f"\nTraining complete!")
            print(f"Final weights: {final_weights}")
            print("\nWeight changes:")
            for worker_id in final_weights:
                initial = initial_weights.get(worker_id, 1.0)
                final = final_weights[worker_id]
                change = final - initial
                print(f"  {worker_id}: {initial:.4f} -> {final:.4f} ({change:+.4f})")

        # Create session object
        session = TrainingSession(
            session_id=session_id,
            start_time=start_time,
            end_time=datetime.utcnow().isoformat(),
            num_examples=len(examples),
            epochs=epochs,
            learning_rate=self.weight_learner.alpha,
            initial_weights=initial_weights,
            final_weights=final_weights,
            metrics_history=metrics_history,
            status='completed'
        )

        # Save session
        self.data_manager.save_session(session)

        return session

    def validate(self, examples: List[TrainingExample]) -> Dict[str, Any]:
        """
        Validate current model on examples without updating weights.

        Args:
            examples: List of validation examples

        Returns:
            Validation metrics
        """
        validation_results = {
            'num_examples': len(examples),
            'worker_accuracies': {},
            'avg_accuracy': 0.0,
            'per_example': []
        }

        for example in examples:
            # Load images
            source_img = cv2.imread(example.source_path)
            target_img = cv2.imread(example.target_path)
            ground_truth_img = cv2.imread(example.ground_truth_path)

            if any(img is None for img in [source_img, target_img, ground_truth_img]):
                continue

            # Execute workers (no weight updates)
            data = {'source': source_img, 'target': target_img}
            worker_results = self.worker_pool.execute_parallel(data)

            example_accuracies = {}
            for result in worker_results:
                if result.is_valid():
                    accuracy = self.calculate_similarity(result.value, ground_truth_img)
                    example_accuracies[result.worker_id] = accuracy

                    if result.worker_id not in validation_results['worker_accuracies']:
                        validation_results['worker_accuracies'][result.worker_id] = []
                    validation_results['worker_accuracies'][result.worker_id].append(accuracy)

            validation_results['per_example'].append({
                'example_id': example.example_id,
                'accuracies': example_accuracies
            })

        # Calculate averages
        if validation_results['worker_accuracies']:
            all_accuracies = [
                acc for accs in validation_results['worker_accuracies'].values()
                for acc in accs
            ]
            validation_results['avg_accuracy'] = np.mean(all_accuracies)

            for worker_id in validation_results['worker_accuracies']:
                worker_accs = validation_results['worker_accuracies'][worker_id]
                validation_results['worker_accuracies'][worker_id] = {
                    'mean': np.mean(worker_accs),
                    'std': np.std(worker_accs),
                    'min': np.min(worker_accs),
                    'max': np.max(worker_accs)
                }

        return validation_results


class TrainingManager:
    """
    High-level manager for TSM training operations.

    Coordinates data management, training, and validation.
    """

    def __init__(self,
                 worker_pool: WorkerPool,
                 weight_learner: BayesianWeightLearner,
                 db_path: str = "tsm_training.db"):
        """Initialize training manager."""
        self.data_manager = TrainingDataManager(db_path)
        self.training_engine = TrainingEngine(worker_pool, weight_learner, self.data_manager)
        self.worker_pool = worker_pool
        self.weight_learner = weight_learner

    def add_training_example(self,
                            source_path: str,
                            target_path: str,
                            ground_truth_path: str,
                            metadata: Optional[Dict] = None) -> TrainingExample:
        """Add a new training example."""
        import uuid

        example = TrainingExample(
            example_id=str(uuid.uuid4()),
            source_path=source_path,
            target_path=target_path,
            ground_truth_path=ground_truth_path,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )

        self.data_manager.add_example(example)
        return example

    def train(self,
              num_examples: Optional[int] = None,
              epochs: int = 1,
              validation_split: float = 0.2,
              verbose: bool = True) -> Dict[str, Any]:
        """
        Train the model with optional validation.

        Args:
            num_examples: Number of examples to use (None = all)
            epochs: Number of training epochs
            validation_split: Fraction of data for validation
            verbose: Print progress

        Returns:
            Training results with validation metrics
        """
        # Get examples
        all_examples = self.data_manager.get_all_examples(limit=num_examples)

        if not all_examples:
            raise ValueError("No training examples available")

        # Split into train/validation
        num_val = int(len(all_examples) * validation_split)
        val_examples = all_examples[:num_val] if num_val > 0 else []
        train_examples = all_examples[num_val:]

        if verbose:
            print(f"Training on {len(train_examples)} examples")
            if val_examples:
                print(f"Validating on {len(val_examples)} examples")

        # Train
        session = self.training_engine.train_batch(
            train_examples,
            epochs=epochs,
            verbose=verbose
        )

        # Validate if we have validation examples
        validation_results = None
        if val_examples:
            if verbose:
                print("\nRunning validation...")
            validation_results = self.training_engine.validate(val_examples)
            if verbose:
                print(f"Validation accuracy: {validation_results['avg_accuracy']:.4f}")

        return {
            'session': asdict(session),
            'validation': validation_results
        }

    def export_weights(self, filepath: str):
        """Export current weights to file."""
        weights = {
            'weights': self.weight_learner.get_all_weights(),
            'alpha': self.weight_learner.alpha,
            'exported_at': datetime.utcnow().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(weights, f, indent=2)

    def import_weights(self, filepath: str):
        """Import weights from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        for worker_id, weight in data['weights'].items():
            self.weight_learner.weights[worker_id] = weight

    def get_training_progress(self) -> Dict[str, Any]:
        """Get overall training progress and statistics."""
        stats = self.data_manager.get_dataset_stats()

        current_weights = self.weight_learner.get_all_weights()
        worker_stats = {}

        for worker_id, weight in current_weights.items():
            learner_stats = self.weight_learner.get_statistics(worker_id)
            worker_stats[worker_id] = {
                'current_weight': weight,
                'stats': learner_stats if learner_stats else {}
            }

        return {
            'dataset_stats': stats,
            'worker_stats': worker_stats,
            'current_weights': current_weights
        }
