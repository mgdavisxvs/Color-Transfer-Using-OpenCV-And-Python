"""
Training routes for TSM-enabled Flask application.

This module adds training capabilities to the Flask app,
including dataset management, batch training, and validation.
"""

import os
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import cv2

from tsm_training import TrainingManager, TrainingExample

# Create Blueprint
training_bp = Blueprint('training', __name__, url_prefix='/training')

# Global training manager (will be initialized by app)
training_manager = None


def init_training(worker_pool, weight_learner, db_path="tsm_training.db"):
    """Initialize training manager."""
    global training_manager
    training_manager = TrainingManager(worker_pool, weight_learner, db_path)


@training_bp.route('/dashboard')
def training_dashboard():
    """Render training dashboard."""
    return render_template('training_dashboard.html')


@training_bp.route('/add-example', methods=['POST'])
def add_training_example():
    """
    Add a new training example with ground truth.

    Expected form data:
    - source: Source image file
    - target: Target image file
    - ground_truth: Ground truth result image
    - metadata: Optional JSON metadata
    """
    try:
        # Validate files
        if not all(key in request.files for key in ['source', 'target', 'ground_truth']):
            return jsonify({
                'success': False,
                'error': 'Missing required files (source, target, ground_truth)'
            }), 400

        source_file = request.files['source']
        target_file = request.files['target']
        ground_truth_file = request.files['ground_truth']

        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            import json
            metadata = json.loads(request.form['metadata'])

        # Generate unique filenames
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]

        # Save files to training folder
        training_folder = Path('app/static/training_data')
        training_folder.mkdir(parents=True, exist_ok=True)

        source_filename = f"source_{timestamp}_{unique_id}.png"
        target_filename = f"target_{timestamp}_{unique_id}.png"
        gt_filename = f"ground_truth_{timestamp}_{unique_id}.png"

        source_path = training_folder / source_filename
        target_path = training_folder / target_filename
        gt_path = training_folder / gt_filename

        source_file.save(source_path)
        target_file.save(target_path)
        ground_truth_file.save(gt_path)

        # Add to training dataset
        example = training_manager.add_training_example(
            source_path=str(source_path),
            target_path=str(target_path),
            ground_truth_path=str(gt_path),
            metadata=metadata
        )

        return jsonify({
            'success': True,
            'example_id': example.example_id,
            'message': 'Training example added successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/examples', methods=['GET'])
def get_training_examples():
    """Get all training examples."""
    try:
        limit = request.args.get('limit', type=int)
        examples = training_manager.data_manager.get_all_examples(limit=limit)

        return jsonify({
            'success': True,
            'examples': [
                {
                    'example_id': ex.example_id,
                    'created_at': ex.created_at,
                    'metadata': ex.metadata,
                    'has_results': ex.worker_results is not None
                }
                for ex in examples
            ],
            'total': len(examples)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/example/<example_id>', methods=['GET'])
def get_training_example(example_id):
    """Get details of a specific training example."""
    try:
        example = training_manager.data_manager.get_example(example_id)

        if not example:
            return jsonify({
                'success': False,
                'error': 'Example not found'
            }), 404

        return jsonify({
            'success': True,
            'example': {
                'example_id': example.example_id,
                'source_path': example.source_path,
                'target_path': example.target_path,
                'ground_truth_path': example.ground_truth_path,
                'created_at': example.created_at,
                'metadata': example.metadata,
                'worker_results': example.worker_results,
                'validation_scores': example.validation_scores
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/train', methods=['POST'])
def start_training():
    """
    Start a training session.

    Expected JSON body:
    {
        "num_examples": int (optional),
        "epochs": int (default: 1),
        "validation_split": float (default: 0.2),
        "verbose": bool (default: false)
    }
    """
    try:
        data = request.get_json() or {}

        num_examples = data.get('num_examples')
        epochs = data.get('epochs', 1)
        validation_split = data.get('validation_split', 0.2)
        verbose = data.get('verbose', False)

        # Run training
        results = training_manager.train(
            num_examples=num_examples,
            epochs=epochs,
            validation_split=validation_split,
            verbose=verbose
        )

        return jsonify({
            'success': True,
            'results': results,
            'message': 'Training completed successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/validate', methods=['POST'])
def validate_model():
    """
    Validate current model on examples.

    Expected JSON body:
    {
        "example_ids": list of example IDs (optional, uses all if not provided)
    }
    """
    try:
        data = request.get_json() or {}
        example_ids = data.get('example_ids')

        # Get examples
        if example_ids:
            examples = [
                training_manager.data_manager.get_example(eid)
                for eid in example_ids
            ]
            examples = [ex for ex in examples if ex is not None]
        else:
            examples = training_manager.data_manager.get_all_examples()

        if not examples:
            return jsonify({
                'success': False,
                'error': 'No examples found for validation'
            }), 400

        # Run validation
        validation_results = training_manager.training_engine.validate(examples)

        return jsonify({
            'success': True,
            'validation_results': validation_results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/progress', methods=['GET'])
def get_training_progress():
    """Get overall training progress and statistics."""
    try:
        progress = training_manager.get_training_progress()

        return jsonify({
            'success': True,
            'progress': progress
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/sessions', methods=['GET'])
def get_training_sessions():
    """Get all training sessions."""
    try:
        # Get sessions from database
        conn = training_manager.data_manager.db_path
        import sqlite3

        conn = sqlite3.connect(conn)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, start_time, end_time, num_examples,
                   epochs, learning_rate, status
            FROM training_sessions
            ORDER BY start_time DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        sessions = []
        for row in rows:
            sessions.append({
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'num_examples': row[3],
                'epochs': row[4],
                'learning_rate': row[5],
                'status': row[6]
            })

        return jsonify({
            'success': True,
            'sessions': sessions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/session/<session_id>', methods=['GET'])
def get_training_session(session_id):
    """Get details of a specific training session."""
    try:
        session = training_manager.data_manager.get_session(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        from dataclasses import asdict
        return jsonify({
            'success': True,
            'session': asdict(session)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/weights/export', methods=['GET'])
def export_weights():
    """Export current weights to JSON file."""
    try:
        import tempfile
        import json
        from flask import send_file

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            weights = {
                'weights': training_manager.weight_learner.get_all_weights(),
                'alpha': training_manager.weight_learner.alpha,
                'exported_at': datetime.now().isoformat()
            }
            json.dump(weights, f, indent=2)
            temp_path = f.name

        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"tsm_weights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/weights/import', methods=['POST'])
def import_weights():
    """Import weights from JSON file."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Read weights
        import json
        weights_data = json.load(file)

        # Import weights
        for worker_id, weight in weights_data['weights'].items():
            training_manager.weight_learner.weights[worker_id] = weight

        return jsonify({
            'success': True,
            'message': 'Weights imported successfully',
            'imported_weights': weights_data['weights']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/dataset-stats', methods=['GET'])
def get_dataset_stats():
    """Get statistics about the training dataset."""
    try:
        stats = training_manager.data_manager.get_dataset_stats()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@training_bp.route('/reset-weights', methods=['POST'])
def reset_weights():
    """Reset all worker weights to default (1.0)."""
    try:
        # Get data if provided
        data = request.get_json() or {}
        default_weight = data.get('default_weight', 1.0)

        # Reset all weights
        for worker_id in training_manager.worker_pool.workers.keys():
            training_manager.weight_learner.weights[worker_id] = default_weight

        # Clear history
        training_manager.weight_learner.history.clear()
        training_manager.weight_learner.update_count.clear()

        return jsonify({
            'success': True,
            'message': 'Weights reset successfully',
            'new_weights': training_manager.weight_learner.get_all_weights()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
