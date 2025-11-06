#!/usr/bin/env python3
"""
Color Transfer Web Application with Tom Sawyer Method Integration

A modern web interface using TSM ensemble intelligence for superior
color transfer results through multiple specialized workers.
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import cv2
import numpy as np

# Import TSM framework
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'tom-sawyer-method'))
from tsm.core.worker import WorkerPool
from tsm.core.aggregator import Aggregator, WeightedAverageAggregation
from tsm.core.learner import BayesianWeightLearner

# Import TSM color transfer workers
from tsm_workers import create_color_transfer_workers

# Import training routes
from training_routes import training_bp, init_training

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'app' / 'static' / 'uploads'
app.config['RESULTS_FOLDER'] = Path(__file__).parent / 'app' / 'static' / 'results'
app.config['WORKER_RESULTS_FOLDER'] = Path(__file__).parent / 'app' / 'static' / 'worker_results'
app.config['WEIGHTS_FILE'] = Path(__file__).parent / 'tsm_weights.json'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

# Ensure directories exist
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['RESULTS_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['WORKER_RESULTS_FOLDER'].mkdir(parents=True, exist_ok=True)

# Initialize TSM components
worker_pool = WorkerPool(max_workers=10)
weight_learner = BayesianWeightLearner(alpha=0.15, prior_weight=1.0)
aggregator = Aggregator(
    strategy=WeightedAverageAggregation(use_confidence=True),
    weight_learner=weight_learner
)

# Register workers
for worker in create_color_transfer_workers():
    worker_pool.register_worker(worker)

# Initialize training system
init_training(worker_pool, weight_learner, db_path="tsm_training.db")

# Register training blueprint
app.register_blueprint(training_bp)

# Load saved weights if they exist
if app.config['WEIGHTS_FILE'].exists():
    try:
        with open(app.config['WEIGHTS_FILE'], 'r') as f:
            saved_weights = json.load(f)
            for worker_id, weight in saved_weights.items():
                weight_learner.weights[worker_id] = weight
        app.logger.info(f"Loaded weights for {len(saved_weights)} workers")
    except Exception as e:
        app.logger.warning(f"Could not load weights: {e}")


def save_weights():
    """Save current worker weights."""
    try:
        with open(app.config['WEIGHTS_FILE'], 'w') as f:
            json.dump(weight_learner.weights, f, indent=2)
    except Exception as e:
        app.logger.warning(f"Could not save weights: {e}")


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def generate_unique_filename(original_filename):
    """Generate a unique filename with timestamp and UUID."""
    ext = original_filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}.{ext}"


def aggregate_images(worker_results):
    """
    Aggregate multiple worker result images using weighted averaging.

    Args:
        worker_results: List of WorkerResult objects with image arrays

    Returns:
        Aggregated image as numpy array
    """
    if not worker_results:
        return None

    # Get valid results
    valid_results = [r for r in worker_results if r.is_valid()]
    if not valid_results:
        return None

    # Get normalized weights
    weights = weight_learner.get_normalized_weights(
        [r.worker_id for r in valid_results]
    )

    # Weight images
    weighted_sum = None
    total_weight = 0.0

    for result in valid_results:
        weight = weights.get(result.worker_id, 0.0) * result.confidence

        if weighted_sum is None:
            weighted_sum = result.value.astype(float) * weight
        else:
            weighted_sum += result.value.astype(float) * weight

        total_weight += weight

    # Normalize
    if total_weight > 0:
        aggregated = (weighted_sum / total_weight).astype(np.uint8)
    else:
        # Fallback to simple average
        aggregated = np.mean([r.value for r in valid_results], axis=0).astype(np.uint8)

    return aggregated


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index_tsm.html')


@app.route('/upload', methods=['POST'])
def upload_images():
    """Handle image upload and processing with TSM."""
    try:
        # Validate request
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Both source and target images are required'
            }), 400

        source_file = request.files['source']
        target_file = request.files['target']

        # Validate files
        if source_file.filename == '' or target_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        if not allowed_file(source_file.filename) or not allowed_file(target_file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
            }), 400

        # Save uploaded files
        source_filename = generate_unique_filename(source_file.filename)
        target_filename = generate_unique_filename(target_file.filename)

        source_path = app.config['UPLOAD_FOLDER'] / source_filename
        target_path = app.config['UPLOAD_FOLDER'] / target_filename

        source_file.save(source_path)
        target_file.save(target_path)

        # Load images
        source_img = cv2.imread(str(source_path))
        target_img = cv2.imread(str(target_path))

        if source_img is None or target_img is None:
            return jsonify({
                'success': False,
                'error': 'Failed to load images. Please ensure they are valid image files.'
            }), 400

        # Prepare data for workers
        data = {
            'source': source_img,
            'target': target_img
        }

        # Execute workers in parallel
        trace_id = str(uuid.uuid4())
        worker_results = worker_pool.execute_parallel(data, trace_id=trace_id)

        # Save individual worker results
        worker_info = []
        for result in worker_results:
            if result.is_valid():
                # Save worker result image
                worker_filename = f"worker_{result.worker_id}_{generate_unique_filename('result.png')}"
                worker_path = app.config['WORKER_RESULTS_FOLDER'] / worker_filename
                cv2.imwrite(str(worker_path), result.value)

                worker_info.append({
                    'worker_id': result.worker_id,
                    'confidence': float(result.confidence),
                    'processing_time_ms': float(result.processing_time_ms),
                    'url': url_for('static', filename=f'worker_results/{worker_filename}'),
                    'weight': float(weight_learner.get_weight(result.worker_id))
                })

        # Aggregate results using TSM
        aggregated_img = aggregate_images(worker_results)

        if aggregated_img is None:
            return jsonify({
                'success': False,
                'error': 'No valid worker results to aggregate'
            }), 500

        # Save aggregated result
        result_filename = f"tsm_result_{generate_unique_filename('output.png')}"
        result_path = app.config['RESULTS_FOLDER'] / result_filename
        cv2.imwrite(str(result_path), aggregated_img)

        # Get aggregated result metadata
        aggregated_result = aggregator.aggregate(worker_results)

        # Get image dimensions
        source_dims = f"{source_img.shape[1]}x{source_img.shape[0]}"
        target_dims = f"{target_img.shape[1]}x{target_img.shape[0]}"
        result_dims = f"{aggregated_img.shape[1]}x{aggregated_img.shape[0]}"

        # Get pool statistics
        pool_stats = worker_pool.get_pool_statistics()

        response = {
            'success': True,
            'source_url': url_for('static', filename=f'uploads/{source_filename}'),
            'target_url': url_for('static', filename=f'uploads/{target_filename}'),
            'result_url': url_for('static', filename=f'results/{result_filename}'),
            'source_dims': source_dims,
            'target_dims': target_dims,
            'result_dims': result_dims,
            'result_filename': result_filename,
            'tsm_enabled': True,
            'workers': worker_info,
            'aggregation': {
                'confidence': float(aggregated_result.confidence),
                'num_workers': aggregated_result.num_workers,
                'valid_workers': aggregated_result.valid_workers,
                'average_confidence': float(aggregated_result.average_worker_confidence),
                'method': aggregated_result.aggregation_method,
                'processing_time_ms': float(aggregated_result.processing_time_ms)
            },
            'statistics': {
                'total_workers': pool_stats['total_workers'],
                'active_workers': pool_stats['active_workers'],
                'total_executions': pool_stats['total_executions']
            }
        }

        # Save weights after processing
        save_weights()

        return jsonify(response)

    except Exception as e:
        app.logger.error(f"Error processing images: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'An error occurred while processing images: {str(e)}'
        }), 500


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Handle user feedback to improve TSM learning.

    Users can rate results, which updates worker weights.
    """
    try:
        data = request.get_json()

        rating = data.get('rating', 0)  # 1-5 stars
        trace_id = data.get('trace_id')
        worker_id = data.get('worker_id')

        if not all([rating, trace_id, worker_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # Convert rating to accuracy (0.0 to 1.0)
        accuracy = rating / 5.0

        # Update worker weight based on feedback
        from tsm.core.learner import PerformanceMetric

        metric = PerformanceMetric(
            worker_id=worker_id,
            predicted=None,  # Not applicable for user feedback
            actual=None,
            confidence=1.0,  # High confidence in user feedback
            accuracy=accuracy
        )

        weight_learner.update_weight(worker_id, metric)
        save_weights()

        return jsonify({
            'success': True,
            'message': 'Feedback recorded',
            'new_weight': float(weight_learner.get_weight(worker_id))
        })

    except Exception as e:
        app.logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/worker-stats')
def worker_stats():
    """Get current worker statistics and weights."""
    try:
        stats = worker_pool.get_pool_statistics()

        # Add current weights
        workers_detailed = []
        weights = {}
        for worker_stat in stats['worker_statistics']:
            worker_id = worker_stat['worker_id']
            learner_stats = weight_learner.get_statistics(worker_id)
            current_weight = float(weight_learner.get_weight(worker_id))

            detailed = {
                **worker_stat,
                'current_weight': current_weight,
                'learner_stats': learner_stats if learner_stats else {}
            }
            workers_detailed.append(detailed)
            weights[worker_id] = current_weight

        return jsonify({
            'success': True,
            'weights': weights,
            'statistics': {
                **stats,
                'worker_statistics': workers_detailed
            }
        })

    except Exception as e:
        app.logger.error(f"Error getting worker stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download/<filename>')
def download_result(filename):
    """Download processed image."""
    try:
        return send_from_directory(
            app.config['RESULTS_FOLDER'],
            filename,
            as_attachment=True,
            download_name=f"color_transfer_{filename}"
        )
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404


@app.route('/gallery')
def gallery():
    """Display gallery of recent transformations."""
    try:
        # Get recent results (last 10)
        results = []
        result_files = sorted(
            app.config['RESULTS_FOLDER'].glob('tsm_result_*.png'),
            key=os.path.getmtime,
            reverse=True
        )[:10]

        for result_file in result_files:
            results.append({
                'filename': result_file.name,
                'url': url_for('static', filename=f'results/{result_file.name}'),
                'timestamp': datetime.fromtimestamp(
                    result_file.stat().st_mtime
                ).strftime('%Y-%m-%d %H:%M:%S')
            })

        return render_template('gallery_tsm.html', results=results)

    except Exception as e:
        app.logger.error(f"Error loading gallery: {str(e)}")
        return render_template('gallery_tsm.html', results=[])


@app.route('/about')
def about():
    """Display about page."""
    return render_template('about_tsm.html')


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(f"Internal error: {str(error)}")
    return render_template('500.html'), 500


# Cleanup old files periodically
@app.before_request
def cleanup_old_files():
    """Clean up old uploaded and result files (older than 1 hour)."""
    try:
        import time
        current_time = time.time()
        one_hour_ago = current_time - 3600

        for folder in [app.config['UPLOAD_FOLDER'],
                      app.config['RESULTS_FOLDER'],
                      app.config['WORKER_RESULTS_FOLDER']]:
            for file_path in folder.glob('*.*'):
                if file_path.stat().st_mtime < one_hour_ago:
                    file_path.unlink()
    except Exception as e:
        app.logger.warning(f"Cleanup error: {str(e)}")


if __name__ == '__main__':
    # Run in debug mode for development
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
