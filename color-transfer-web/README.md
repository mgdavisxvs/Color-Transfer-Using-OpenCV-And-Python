# Color Transfer Web Application

A modern, minimalistic web interface for image-to-image color transfer built with Flask and TailwindCSS.

![Color Transfer Demo](https://via.placeholder.com/800x400?text=Color+Transfer+Web+App)

---

## Features

- **🎨 Modern UI** - Clean, minimalistic design with TailwindCSS
- **📤 Drag & Drop** - Intuitive file upload with drag-and-drop support
- **⚡ Fast Processing** - Efficient image processing with OpenCV
- **📱 Responsive** - Works perfectly on desktop, tablet, and mobile
- **🔒 Secure** - Automatic file cleanup and secure file handling
- **🖼️ Gallery** - View recent transformations
- **📥 Download** - Easy download of processed images

---

## Technology Stack

### Backend
- **Flask** - Lightweight Python web framework
- **OpenCV** - Image processing library
- **NumPy** - Numerical computing

### Frontend
- **TailwindCSS** - Utility-first CSS framework
- **Vanilla JavaScript** - No framework dependencies
- **Font Awesome** - Icon library

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   cd Color-Transfer-Using-OpenCV-And-Python/color-transfer-web
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Linux/Mac
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

---

## Project Structure

```
color-transfer-web/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env                           # Environment variables (create this)
├── app/
│   ├── templates/                 # HTML templates
│   │   ├── base.html             # Base template
│   │   ├── index.html            # Home page
│   │   ├── gallery.html          # Gallery page
│   │   ├── about.html            # About page
│   │   ├── 404.html              # 404 error page
│   │   └── 500.html              # 500 error page
│   │
│   └── static/                    # Static files
│       ├── js/
│       │   └── main.js           # Main JavaScript
│       ├── css/                  # Custom CSS (if needed)
│       ├── uploads/              # Uploaded images (auto-created)
│       └── results/              # Processed images (auto-created)
│
└── config/                        # Configuration files
```

---

## Usage

### Basic Usage

1. **Upload Images**
   - Click or drag-and-drop a **source image** (provides the color scheme)
   - Click or drag-and-drop a **target image** (to be transformed)

2. **Process**
   - Click "Transform Images" button
   - Wait for processing (usually takes 1-3 seconds)

3. **Download**
   - View the result in the comparison grid
   - Click "Download Result" to save the transformed image

### Advanced Configuration

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Server Configuration
HOST=0.0.0.0
PORT=5000

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
UPLOAD_FOLDER=app/static/uploads
RESULTS_FOLDER=app/static/results
```

---

## API Endpoints

### `GET /`
Home page with upload interface

### `POST /upload`
Process images and return results

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `source`: Source image file
  - `target`: Target image file

**Response:**
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

### `GET /download/<filename>`
Download a processed image

### `GET /gallery`
View gallery of recent transformations

### `GET /about`
About page with technical information

---

## Development

### Running in Development Mode

```bash
# With debug mode enabled
python app.py

# Or with Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### Running in Production

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With more workers
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
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

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t color-transfer-web .
docker run -p 5000:5000 color-transfer-web
```

---

## Features in Detail

### Drag and Drop Upload
- Intuitive drag-and-drop interface
- Visual feedback during drag
- Preview images before processing
- Support for multiple image formats (PNG, JPG, JPEG, BMP, WEBP)

### Image Processing
- LAB color space conversion
- Statistical color matching
- Mean and standard deviation transfer
- Division by zero protection
- Intensity clipping

### Security Features
- File type validation
- File size limits (16MB default)
- Secure filename generation
- Automatic cleanup (files older than 1 hour)
- No arbitrary code execution

### User Experience
- Responsive design for all devices
- Loading indicators
- Error messages with helpful information
- Smooth animations
- Clean, modern interface

---

## Customization

### Changing Colors

Edit the TailwindCSS configuration in `app/templates/base.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    500: '#your-color',
                    600: '#your-darker-color',
                }
            }
        }
    }
}
```

### Adding Custom Styles

Create `app/static/css/custom.css` and link it in the base template.

### Modifying the Algorithm

Edit `algorithm_improved.py` to adjust the color transfer parameters or add new features.

---

## Troubleshooting

### OpenCV Import Error
```bash
# Install system dependencies on Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

# On macOS
brew install opencv
```

### Port Already in Use
```bash
# Change port in app.py or use:
python app.py --port 8000
```

### File Upload Fails
- Check file size (default limit: 16MB)
- Verify file format (PNG, JPG, JPEG, BMP, WEBP)
- Check disk space for uploads folder

---

## Performance Optimization

### For Production

1. **Use a production server**
   ```bash
   gunicorn -w 4 app:app
   ```

2. **Enable caching**
   - Add Flask-Caching
   - Cache processed results

3. **Optimize images**
   - Resize large images before processing
   - Compress output images

4. **Use CDN**
   - Serve static files from CDN
   - Reduce server load

---

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

This project is part of the Color Transfer repository.

---

## Acknowledgments

- **Flask** - Web framework
- **TailwindCSS** - CSS framework
- **OpenCV** - Image processing
- **Font Awesome** - Icons

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation
- Review the code comments

---

**Built with ❤️ using Flask & TailwindCSS**
