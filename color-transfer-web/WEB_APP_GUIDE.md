# Color Transfer Web Application - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Documentation](#api-documentation)
6. [Customization](#customization)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Color Transfer Web Application provides a modern, user-friendly interface for performing image-to-image color transfer. Built with Flask (Python) and TailwindCSS, it combines powerful backend processing with a sleek, responsive frontend.

### Key Features

✅ **Modern UI Design**
- Clean, minimalistic interface
- Responsive layout (mobile, tablet, desktop)
- Smooth animations and transitions
- Intuitive user experience

✅ **Drag & Drop Upload**
- Drag-and-drop file upload
- Click to browse alternative
- Real-time image preview
- File validation

✅ **Fast Processing**
- Efficient LAB color space algorithm
- Parallel processing support
- Progress indicators
- Error handling

✅ **Security**
- File type validation
- Size limits (16MB default)
- Secure filename generation
- Automatic cleanup

✅ **Additional Pages**
- Gallery of recent transformations
- About page with technical details
- Custom error pages (404, 500)

---

## Architecture

### Backend (Flask)

```
app.py
├── Routes
│   ├── GET  /           → Home page
│   ├── POST /upload     → Process images
│   ├── GET  /download   → Download result
│   ├── GET  /gallery    → View gallery
│   └── GET  /about      → About page
│
├── File Handling
│   ├── Upload validation
│   ├── Secure filename generation
│   ├── Image processing (color_transfer)
│   └── Automatic cleanup
│
└── Error Handling
    ├── 404 Not Found
    ├── 413 File Too Large
    └── 500 Internal Error
```

### Frontend (TailwindCSS + JavaScript)

```
Templates
├── base.html          → Base layout with navigation
├── index.html         → Main upload interface
├── gallery.html       → Recent results gallery
├── about.html         → Technical information
├── 404.html          → Not found error
└── 500.html          → Server error

Static Assets
├── js/main.js        → Upload logic, AJAX, drag-drop
└── static/
    ├── uploads/      → Temporary uploaded files
    └── results/      → Processed images
```

### Color Transfer Algorithm

1. **Convert to LAB color space**
   - RGB → LAB conversion
   - Separates luminance from color

2. **Compute statistics**
   - Mean and standard deviation
   - For each channel (L, a, b)

3. **Transfer colors**
   - Match target statistics to source
   - Scale and shift color values

4. **Convert back to RGB**
   - LAB → RGB conversion
   - Clip to valid range [0, 255]

---

## Installation

### Quick Start

```bash
# Navigate to directory
cd color-transfer-web

# Run setup script (Linux/Mac)
./run.sh

# Start application
python app.py
```

### Manual Installation

**1. Prerequisites**
```bash
# Python 3.10+
python --version

# pip
pip --version
```

**2. Create Virtual Environment**
```bash
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configuration**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**5. Run Application**
```bash
# Development mode
python app.py

# Production mode
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Usage

### Basic Workflow

1. **Navigate to Home Page**
   - Open `http://localhost:5000`
   - Scroll to upload section

2. **Upload Source Image**
   - Drag & drop or click to browse
   - This provides the color scheme
   - Preview appears after selection

3. **Upload Target Image**
   - Drag & drop or click to browse
   - This image will be transformed
   - Preview appears after selection

4. **Process Images**
   - Click "Transform Images" button
   - Wait for processing (1-3 seconds)
   - View results in comparison grid

5. **Download Result**
   - Click "Download Result" button
   - Image saved to Downloads folder
   - Or transform another image

### Gallery

- View recent transformations
- Download previous results
- Automatic display of last 10 results

### About Page

- Learn how the algorithm works
- View technical specifications
- Explore use cases

---

## API Documentation

### POST /upload

Upload and process two images.

**Request:**
```http
POST /upload HTTP/1.1
Content-Type: multipart/form-data

source: <source_image_file>
target: <target_image_file>
```

**Success Response (200):**
```json
{
  "success": true,
  "source_url": "/static/uploads/20250106_123456_abc123.jpg",
  "target_url": "/static/uploads/20250106_123456_def456.jpg",
  "result_url": "/static/results/result_20250106_123456_ghi789.png",
  "source_dims": "1920x1080",
  "target_dims": "1920x1080",
  "result_dims": "1920x1080",
  "result_filename": "result_20250106_123456_ghi789.png"
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "error": "Error message description"
}
```

### GET /download/<filename>

Download a processed image.

**Request:**
```http
GET /download/result_20250106_123456_ghi789.png HTTP/1.1
```

**Response:**
- File download with proper headers
- Filename: `color_transfer_result_20250106_123456_ghi789.png`

---

## Customization

### Theme Colors

Edit `app/templates/base.html`:

```html
<script>
    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    primary: {
                        500: '#0ea5e9',  // Change this
                        600: '#0284c7',  // And this
                    },
                }
            }
        }
    }
</script>
```

### File Size Limit

Edit `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Cleanup Interval

Edit the `cleanup_old_files()` function in `app.py`:

```python
one_hour_ago = current_time - 7200  # 2 hours
```

### Allowed File Types

Edit `app.py`:

```python
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff'}
```

### Custom Logo

Replace the icon in navigation:

```html
<!-- In base.html -->
<div class="w-10 h-10 gradient-bg rounded-lg">
    <img src="/static/logo.png" alt="Logo">
</div>
```

---

## Deployment

### Production Server (Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With custom configuration
gunicorn -c gunicorn_config.py app:app
```

**gunicorn_config.py:**
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
errorlog = "logs/error.log"
accesslog = "logs/access.log"
loglevel = "info"
```

### Nginx Reverse Proxy

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/color-transfer-web/app/static;
        expires 30d;
    }
}
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p app/static/uploads app/static/results

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./app/static/uploads:/app/app/static/uploads
      - ./app/static/results:/app/app/static/results
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    restart: unless-stopped
```

**Build and Run:**
```bash
docker-compose up -d
```

---

## Troubleshooting

### Common Issues

**1. OpenCV Import Error**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

# macOS
brew install opencv

# Verify installation
python -c "import cv2; print(cv2.__version__)"
```

**2. Port Already in Use**

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 8000
```

**3. File Upload Fails**

- **Check file size**: Default limit is 16MB
- **Verify format**: PNG, JPG, JPEG, BMP, WEBP only
- **Check permissions**: Ensure write access to uploads/results folders
- **Disk space**: Verify sufficient disk space

```bash
# Check permissions
ls -la app/static/uploads
ls -la app/static/results

# Fix permissions
chmod 755 app/static/uploads
chmod 755 app/static/results
```

**4. Images Not Displaying**

- **Clear browser cache**: Hard refresh (Ctrl+Shift+R)
- **Check static file serving**: Verify Flask static folder configuration
- **Inspect network tab**: Look for 404 errors in browser DevTools

**5. Slow Processing**

- **Resize large images**: Add preprocessing to resize images
- **Increase workers**: Use more Gunicorn workers
- **Optimize algorithm**: Add caching or parallel processing

---

## Performance Optimization

### Backend Optimization

1. **Image Preprocessing**
```python
def resize_if_large(img, max_dimension=2000):
    height, width = img.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(img, (new_width, new_height))
    return img
```

2. **Caching Results**
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def process_images(source_path, target_path):
    # ... processing logic
```

3. **Async Processing**
```python
from celery import Celery

celery = Celery(app.name, broker='redis://localhost:6379')

@celery.task
def process_images_async(source_path, target_path):
    # ... processing logic
```

### Frontend Optimization

1. **Image Compression**
```javascript
// Compress before upload
function compressImage(file, maxSize) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                // ... compression logic
                resolve(canvas.toBlob());
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}
```

2. **Lazy Loading**
```html
<img loading="lazy" src="..." alt="...">
```

---

## Security Best Practices

1. **Environment Variables**
   - Never commit `.env` file
   - Use strong SECRET_KEY
   - Rotate keys regularly

2. **File Validation**
   - Whitelist file extensions
   - Verify MIME types
   - Scan for malware (optional)

3. **Rate Limiting**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
def upload_images():
    # ... upload logic
```

4. **HTTPS**
   - Use SSL/TLS in production
   - Redirect HTTP to HTTPS
   - Use HSTS headers

---

## Monitoring

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

---

## Support & Contributing

### Getting Help

- Check this documentation
- Review code comments
- Open an issue on GitHub

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

**Built with Flask & TailwindCSS | © 2025**
