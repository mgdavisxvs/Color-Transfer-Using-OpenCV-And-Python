// Color Transfer Web App - Main JavaScript

let sourceFile = null;
let targetFile = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupDropZones();
    setupFileInputs();
    setupForm();
});

// Setup drag and drop zones
function setupDropZones() {
    setupDropZone('source');
    setupDropZone('target');
}

function setupDropZone(type) {
    const dropZone = document.getElementById(`${type}-drop-zone`);
    const fileInput = document.getElementById(`${type}-input`);

    // Click to browse
    dropZone.addEventListener('click', (e) => {
        if (!e.target.closest('button')) {
            fileInput.click();
        }
    });

    // Drag over
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    // Drag leave
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    // Drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0], type);
        }
    });
}

// Setup file inputs
function setupFileInputs() {
    document.getElementById('source-input').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0], 'source');
        }
    });

    document.getElementById('target-input').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0], 'target');
        }
    });
}

// Handle file selection
function handleFile(file, type) {
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type. Please upload PNG, JPG, JPEG, BMP, or WEBP images.');
        return;
    }

    // Validate file size (16MB)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File is too large. Maximum size is 16MB.');
        return;
    }

    // Store file
    if (type === 'source') {
        sourceFile = file;
    } else {
        targetFile = file;
    }

    // Show preview
    showPreview(file, type);

    // Update button state
    updateProcessButton();
}

// Show image preview
function showPreview(file, type) {
    const reader = new FileReader();

    reader.onload = function(e) {
        const placeholder = document.getElementById(`${type}-placeholder`);
        const preview = document.getElementById(`${type}-preview`);
        const img = preview.querySelector('img');
        const filename = document.getElementById(`${type}-filename`);

        img.src = e.target.result;
        filename.textContent = file.name;

        placeholder.classList.add('hidden');
        preview.classList.remove('hidden');
    };

    reader.readAsDataURL(file);
}

// Clear source image
function clearSource() {
    sourceFile = null;
    document.getElementById('source-input').value = '';
    document.getElementById('source-placeholder').classList.remove('hidden');
    document.getElementById('source-preview').classList.add('hidden');
    updateProcessButton();
}

// Clear target image
function clearTarget() {
    targetFile = null;
    document.getElementById('target-input').value = '';
    document.getElementById('target-placeholder').classList.remove('hidden');
    document.getElementById('target-preview').classList.add('hidden');
    updateProcessButton();
}

// Update process button state
function updateProcessButton() {
    const button = document.getElementById('process-button');
    if (sourceFile && targetFile) {
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}

// Setup form submission
function setupForm() {
    const form = document.getElementById('upload-form');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!sourceFile || !targetFile) {
            showError('Please upload both source and target images.');
            return;
        }

        // Hide any previous errors or results
        hideError();
        hideResults();

        // Show loading indicator
        showLoading();

        // Create form data
        const formData = new FormData();
        formData.append('source', sourceFile);
        formData.append('target', targetFile);

        try {
            // Send request
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // Hide loading
            hideLoading();

            if (data.success) {
                // Show results
                showResults(data);
            } else {
                // Show error
                showError(data.error);
            }
        } catch (error) {
            hideLoading();
            showError('An error occurred while processing your images. Please try again.');
            console.error('Error:', error);
        }
    });
}

// Show loading indicator
function showLoading() {
    document.getElementById('loading-indicator').classList.remove('hidden');
    document.getElementById('process-button').disabled = true;

    // Scroll to loading indicator
    document.getElementById('loading-indicator').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Hide loading indicator
function hideLoading() {
    document.getElementById('loading-indicator').classList.add('hidden');
    document.getElementById('process-button').disabled = false;
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    errorText.textContent = message;
    errorDiv.classList.remove('hidden');

    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide error message
function hideError() {
    document.getElementById('error-message').classList.add('hidden');
}

// Show results
function showResults(data) {
    const resultsSection = document.getElementById('results-section');

    // Set images
    document.getElementById('result-source-img').src = data.source_url;
    document.getElementById('result-target-img').src = data.target_url;
    document.getElementById('result-img').src = data.result_url;

    // Set dimensions
    document.getElementById('result-source-dims').textContent = data.source_dims;
    document.getElementById('result-target-dims').textContent = data.target_dims;
    document.getElementById('result-dims').textContent = data.result_dims;

    // Set download link
    document.getElementById('download-button').href = `/download/${data.result_filename}`;

    // Show results section
    resultsSection.classList.remove('hidden');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Hide results
function hideResults() {
    document.getElementById('results-section').classList.add('hidden');
}

// Reset form
function resetForm() {
    // Clear files
    clearSource();
    clearTarget();

    // Hide results
    hideResults();
    hideError();

    // Scroll to top
    document.getElementById('upload').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Add smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
