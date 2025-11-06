#!/usr/bin/env python3
"""
Color Transfer Web Application

A modern web interface for image-to-image color transfer using Flask and TailwindCSS.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import cv2
import numpy as np

# Import the improved color transfer algorithm
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from algorithm_improved import color_transfer

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'app' / 'static' / 'uploads'
app.config['RESULTS_FOLDER'] = Path(__file__).parent / 'app' / 'static' / 'results'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

# Ensure directories exist
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['RESULTS_FOLDER'].mkdir(parents=True, exist_ok=True)


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


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_images():
    """Handle image upload and processing."""
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

        # Perform color transfer
        result_img = color_transfer(source_img, target_img)

        # Save result
        result_filename = f"result_{generate_unique_filename('output.png')}"
        result_path = app.config['RESULTS_FOLDER'] / result_filename
        cv2.imwrite(str(result_path), result_img)

        # Get image dimensions
        source_dims = f"{source_img.shape[1]}x{source_img.shape[0]}"
        target_dims = f"{target_img.shape[1]}x{target_img.shape[0]}"
        result_dims = f"{result_img.shape[1]}x{result_img.shape[0]}"

        return jsonify({
            'success': True,
            'source_url': url_for('static', filename=f'uploads/{source_filename}'),
            'target_url': url_for('static', filename=f'uploads/{target_filename}'),
            'result_url': url_for('static', filename=f'results/{result_filename}'),
            'source_dims': source_dims,
            'target_dims': target_dims,
            'result_dims': result_dims,
            'result_filename': result_filename
        })

    except Exception as e:
        app.logger.error(f"Error processing images: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred while processing images: {str(e)}'
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
            app.config['RESULTS_FOLDER'].glob('result_*.png'),
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

        return render_template('gallery.html', results=results)

    except Exception as e:
        app.logger.error(f"Error loading gallery: {str(e)}")
        return render_template('gallery.html', results=[])


@app.route('/about')
def about():
    """Display about page."""
    return render_template('about.html')


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


# Cleanup old files periodically (optional)
@app.before_request
def cleanup_old_files():
    """Clean up old uploaded and result files (older than 1 hour)."""
    try:
        import time
        current_time = time.time()
        one_hour_ago = current_time - 3600

        for folder in [app.config['UPLOAD_FOLDER'], app.config['RESULTS_FOLDER']]:
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
