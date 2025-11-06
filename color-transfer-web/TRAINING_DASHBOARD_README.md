# Training Dashboard - Quick Start Guide

A comprehensive web interface for training and managing the Tom Sawyer Method (TSM) color transfer system.

![Training Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Flask](https://img.shields.io/badge/Flask-2.3+-blue)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-38bdf8)

---

## Overview

The Training Dashboard provides a complete web-based interface for:

- 📊 **Dataset Management** - Upload and organize training examples
- 🎓 **Training Sessions** - Configure and run model training
- ✅ **Validation** - Test model performance against ground truth
- ⚖️ **Weight Management** - Export, import, and reset worker weights
- 📈 **History Tracking** - Monitor training progress over time

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.9+
python --version

# Required packages
pip install flask opencv-python numpy
```

### 2. Start the Application

```bash
cd color-transfer-web
python app_tsm.py
```

### 3. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5000/training/dashboard
```

---

## Features at a Glance

### 📊 Statistics Dashboard

Four key metrics displayed at the top:

| Metric | Description |
|--------|-------------|
| **Training Examples** | Total labeled examples in dataset |
| **Training Sessions** | Number of completed training runs |
| **Average Accuracy** | Overall model performance |
| **Best Worker** | Top performing algorithm |

### 🗂️ Five Main Tabs

#### 1. Dataset Tab

**Add Training Examples:**
- Drag-and-drop three images:
  * Source image (what you start with)
  * Target image (style reference)
  * Ground truth (desired result)
- Optional JSON metadata for categorization
- Real-time image preview

**View Dataset:**
- Grid view of all training examples
- Status indicators (trained/untrained)
- Timestamp and metadata display
- Refresh to reload

#### 2. Training Tab

**Configure Training:**
- **Examples:** Number to train on (or use all)
- **Epochs:** Training passes through dataset
- **Validation Split:** Percentage held out for testing
- **Verbose:** Detailed logging option

**Monitor Progress:**
- Real-time progress bar
- Training status updates
- Results summary with accuracy metrics
- Validation results display

#### 3. Validation Tab

**Run Validation:**
- Test current model against all examples
- Compare predictions to ground truth
- Worker-by-worker performance breakdown

**View Results:**
- Average accuracy across dataset
- Best performing worker identification
- Visual progress bars for each worker
- Detailed metrics

#### 4. Weights Tab

**Current Weights:**
- All workers listed with current weights
- Visual progress bars
- Sorted by performance

**Management:**
- **Export:** Download weights as JSON
- **Import:** Restore weights from file
- **Reset:** Return all weights to default (1.0)

#### 5. History Tab

**Session Tracking:**
- All past training sessions
- Configuration details (epochs, examples, learning rate)
- Performance metrics
- Duration and timestamps

---

## Common Workflows

### Workflow 1: First Training Session

```
1. Add Training Examples (Dataset Tab)
   ↓ Upload source, target, and ground truth images
   ↓ Repeat for 10-20 examples

2. Configure Training (Training Tab)
   ↓ Set epochs: 1
   ↓ Set validation split: 0.2 (20% for validation)
   ↓ Click "Start Training"

3. Monitor Progress
   ↓ Watch progress bar
   ↓ Review results when complete

4. Validate Model (Validation Tab)
   ↓ Click "Run Validation"
   ↓ Check which workers improved

5. Export Weights (Weights Tab)
   ↓ Download trained weights
   ↓ Save as backup
```

### Workflow 2: Iterative Improvement

```
1. Check Current Performance (Validation Tab)
   ↓ Run validation to establish baseline

2. Add More Examples (Dataset Tab)
   ↓ Focus on problematic cases
   ↓ Add diverse scenarios

3. Train Additional Epochs (Training Tab)
   ↓ Set epochs: 3-5
   ↓ Use all examples
   ↓ Higher validation split: 0.3

4. Compare Results (History Tab)
   ↓ View session history
   ↓ Compare accuracy improvements
   ↓ Track best configuration

5. Export if Improved (Weights Tab)
   ↓ Save successful weights
   ↓ Or reset and try different approach
```

### Workflow 3: Experiment and Rollback

```
1. Export Current Weights (Weights Tab)
   ↓ Backup working configuration

2. Run Experiment (Training Tab)
   ↓ Try aggressive learning (more epochs)
   ↓ Or different example subset

3. Evaluate Results (Validation Tab)
   ↓ Check if accuracy improved

4. Decision:
   ↓ If better: Export new weights
   ↓ If worse: Import original weights
```

---

## Training Best Practices

### Dataset Quality

✅ **Good Examples:**
- Clear, high-resolution images
- Diverse color palettes
- Varied complexity (simple to complex)
- Consistent ground truth quality

❌ **Avoid:**
- Blurry or low-quality images
- Corrupted files
- Extreme resolutions
- Ambiguous ground truth

### Training Configuration

**For Small Datasets (< 50 examples):**
```
Epochs: 5-10
Validation Split: 0.2-0.3
Verbose: true (for monitoring)
```

**For Medium Datasets (50-500 examples):**
```
Epochs: 3-5
Validation Split: 0.2
Verbose: false (faster)
```

**For Large Datasets (> 500 examples):**
```
Epochs: 1-3
Validation Split: 0.1-0.2
Batch by category if metadata used
```

### Validation Strategy

- Run validation after every training session
- Compare results to previous sessions
- Look for consistent improvement
- Watch for overfitting (training accuracy high, validation low)

### Weight Management

**Export Weights:**
- After successful training
- Before experiments
- After milestones (e.g., 90% accuracy)
- When switching datasets

**Reset Weights:**
- If performance degrades significantly
- When starting new project
- If weights become imbalanced

---

## API Integration

For programmatic access, all dashboard features are available via REST API:

### Add Training Example

```bash
curl -X POST http://localhost:5000/training/add-example \
  -F "source=@source.jpg" \
  -F "target=@target.jpg" \
  -F "ground_truth=@ground_truth.jpg" \
  -F 'metadata={"category": "landscape"}'
```

### Start Training

```bash
curl -X POST http://localhost:5000/training/train \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 5,
    "validation_split": 0.2,
    "verbose": false
  }'
```

### Run Validation

```bash
curl -X POST http://localhost:5000/training/validate \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Get Statistics

```bash
curl http://localhost:5000/training/dataset-stats
```

See [TRAINING_GUIDE.md](TRAINING_GUIDE.md) for complete API documentation.

---

## Troubleshooting

### Dashboard Won't Load

**Problem:** 404 error when accessing `/training/dashboard`

**Solution:**
```bash
# Ensure using app_tsm.py (not app.py)
python app_tsm.py

# Check training routes are registered
# Look for this in startup logs:
# "Training blueprint registered"
```

### Upload Fails

**Problem:** "Failed to add training example"

**Solutions:**
1. Check file types (must be images: jpg, png, bmp, webp)
2. Verify file sizes (max 16MB)
3. Ensure all three files selected
4. Check disk space in upload folders

### Training Doesn't Start

**Problem:** Training button does nothing or errors

**Solutions:**
1. Ensure at least one training example exists
2. Check browser console for JavaScript errors
3. Verify backend is running (no 500 errors)
4. Review app logs for Python errors

### Weights Not Saving

**Problem:** Weights reset after restart

**Solution:**
```bash
# Check weights file exists and has write permissions
ls -la tsm_weights.json

# If missing, it will be created on first training
# If no write permission:
chmod 644 tsm_weights.json
```

### Database Errors

**Problem:** SQLite database errors

**Solution:**
```bash
# Delete and recreate database
rm tsm_training.db

# Restart application (will auto-create tables)
python app_tsm.py
```

### Performance Issues

**Problem:** Dashboard slow with many examples

**Solutions:**
1. Pagination already limits to 50 examples
2. Consider upgrading to PostgreSQL
3. Archive old examples
4. Optimize image sizes before upload

---

## File Locations

Understanding where files are stored:

```
color-transfer-web/
├── app/static/
│   ├── uploads/              # Uploaded source/target images
│   ├── results/              # Processed results
│   └── training_data/        # Training example images
│
├── tsm_training.db           # SQLite database (all training data)
├── tsm_weights.json          # Current worker weights
└── logs/                     # Application logs (if configured)
```

### Cleanup

Files are automatically cleaned up after 1 hour. To manually clean:

```bash
# Remove old uploads
find app/static/uploads -type f -mmin +60 -delete

# Remove old results
find app/static/results -type f -mmin +60 -delete

# Training data is NOT auto-deleted (permanent dataset)
```

---

## Performance Tips

### Optimize Training Speed

1. **Reduce Image Sizes:**
   ```python
   # Resize images before uploading
   # Target: 1024x1024 or smaller
   ```

2. **Use Fewer Workers:**
   ```python
   # In tsm_workers.py, comment out workers you don't need
   # Fewer workers = faster training
   ```

3. **Batch Training:**
   ```bash
   # Train on subsets, then combine
   # Train on category 1, then category 2
   ```

### Optimize Storage

1. **Compress Training Images:**
   - Use JPG instead of PNG (smaller)
   - Reduce quality to 85% (minimal visual loss)

2. **Archive Old Sessions:**
   ```sql
   -- Remove old sessions from database
   DELETE FROM training_sessions
   WHERE start_time < date('now', '-30 days');
   ```

3. **Upgrade Database:**
   ```bash
   # For production, use PostgreSQL
   pip install psycopg2-binary
   # Update connection string in tsm_training.py
   ```

---

## Production Deployment

### Environment Variables

```bash
export SECRET_KEY="your-production-secret-key-here"
export DATABASE_URL="postgresql://user:pass@localhost/tsm_training"
export MAX_UPLOAD_SIZE="16777216"  # 16MB in bytes
```

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app_tsm:app

# With timeout for long training sessions
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 app_tsm:app
```

### Using Docker

```bash
# Build image
docker build -t tsm-training-dashboard .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY="production-key" \
  tsm-training-dashboard
```

### Using Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name training.example.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Important for training (long-running requests)
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }

    location /static {
        alias /path/to/app/static;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Security Considerations

### Recommended for Production

1. **Authentication:**
   ```python
   # Add Flask-Login or similar
   pip install flask-login
   # Protect /training/* routes
   ```

2. **Rate Limiting:**
   ```python
   # Add Flask-Limiter
   pip install flask-limiter
   # Limit training requests
   ```

3. **HTTPS:**
   ```bash
   # Use Let's Encrypt with Nginx
   certbot --nginx -d training.example.com
   ```

4. **CSRF Protection:**
   ```python
   # Add Flask-WTF
   pip install flask-wtf
   # Enable CSRF tokens
   ```

---

## Monitoring

### Application Health

```bash
# Check if app is running
curl http://localhost:5000/

# Check API health
curl http://localhost:5000/worker-stats

# Monitor training
tail -f logs/app.log
```

### Database Monitoring

```bash
# Check database size
du -h tsm_training.db

# Count records
sqlite3 tsm_training.db "SELECT COUNT(*) FROM training_examples;"

# View recent sessions
sqlite3 tsm_training.db "SELECT * FROM training_sessions ORDER BY start_time DESC LIMIT 5;"
```

### Performance Monitoring

```python
# Add logging to track training times
import time

start = time.time()
# ... training code ...
duration = time.time() - start
app.logger.info(f"Training took {duration:.2f}s")
```

---

## Resources

### Documentation

- [TRAINING_GUIDE.md](TRAINING_GUIDE.md) - Detailed API and usage guide
- [TRAINING_DASHBOARD_SUMMARY.md](TRAINING_DASHBOARD_SUMMARY.md) - Complete technical documentation
- [TSM_INTEGRATION_SUMMARY.md](TSM_INTEGRATION_SUMMARY.md) - TSM framework details

### Code Files

- `training_dashboard.html` - UI components (600+ lines)
- `training_dashboard.js` - Frontend logic (800+ lines)
- `training_routes.py` - REST API endpoints (400+ lines)
- `tsm_training.py` - Training backend (900+ lines)

### External Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [OpenCV Documentation](https://docs.opencv.org/)

---

## Support

### Getting Help

1. **Check Documentation:**
   - Review this README
   - Check TRAINING_GUIDE.md for API details
   - Read TRAINING_DASHBOARD_SUMMARY.md for technical info

2. **Debug Checklist:**
   - Check browser console for JavaScript errors
   - Review Flask logs for Python errors
   - Verify all files exist in correct locations
   - Ensure database has write permissions

3. **Common Issues:**
   - Training fails: Check example images are valid
   - Upload fails: Verify file types and sizes
   - Dashboard blank: Check Flask app is running
   - Weights not loading: Check tsm_weights.json exists

---

## Contributing

### Adding Features

The dashboard is designed to be extensible:

1. **New Tab:**
   - Add HTML section in `training_dashboard.html`
   - Add tab button to navigation
   - Implement functions in `training_dashboard.js`
   - Add API endpoints in `training_routes.py`

2. **New Metric:**
   - Add calculation to `tsm_training.py`
   - Add endpoint to `training_routes.py`
   - Add display in `training_dashboard.html`
   - Update load function in `training_dashboard.js`

3. **New Worker:**
   - Add class to `tsm_workers.py`
   - Register in `create_color_transfer_workers()`
   - Worker automatically appears in dashboard

---

## License

This project is part of the Color Transfer Using OpenCV and Python repository.

---

## Changelog

### Version 1.0 (November 6, 2025)
- ✨ Initial release
- ✅ Complete training dashboard UI
- ✅ Dataset management
- ✅ Training sessions
- ✅ Validation
- ✅ Weight management
- ✅ Session history
- ✅ Statistics dashboard
- ✅ Responsive design
- ✅ API integration
- ✅ Comprehensive documentation

---

**Built with ❤️ using Flask, TailwindCSS, and OpenCV**

For questions or issues, please review the documentation or check the application logs.

**Ready to start training? Navigate to `/training/dashboard` and begin!**
