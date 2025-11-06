/**
 * Training Dashboard JavaScript
 * Handles all frontend interactions for the TSM training system
 */

// State management
const state = {
    sourceFile: null,
    targetFile: null,
    groundTruthFile: null,
    weightsFile: null,
    currentTab: 'dataset',
    examples: [],
    sessions: [],
    stats: {}
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeDropZones();
    initializeForms();
    loadStatistics();
    loadExamples();
    loadWeights();
    loadSessions();
});

/**
 * Tab Management
 */
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabId}`).classList.add('active');

    state.currentTab = tabId;

    // Load data for the active tab
    if (tabId === 'dataset') {
        loadExamples();
    } else if (tabId === 'weights') {
        loadWeights();
    } else if (tabId === 'sessions') {
        loadSessions();
    }
}

/**
 * Drop Zone Initialization
 */
function initializeDropZones() {
    const dropZones = [
        { id: 'source', inputId: 'source-input', previewId: 'source-preview', nameId: 'source-name' },
        { id: 'target', inputId: 'target-input', previewId: 'target-preview', nameId: 'target-name' },
        { id: 'ground-truth', inputId: 'ground-truth-input', previewId: 'ground-truth-preview', nameId: 'ground-truth-name' }
    ];

    dropZones.forEach(zone => {
        const dropZone = document.getElementById(`${zone.id}-dropzone`);
        const input = document.getElementById(zone.inputId);

        // Click to select file
        dropZone.addEventListener('click', () => input.click());

        // Drag and drop handlers
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-primary-500', 'bg-primary-50');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-primary-500', 'bg-primary-50');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-primary-500', 'bg-primary-50');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleImageFile(files[0], zone);
            }
        });

        // Input change handler
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleImageFile(e.target.files[0], zone);
            }
        });
    });
}

function handleImageFile(file, zone) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showNotification('error', 'Invalid file type', 'Please select an image file');
        return;
    }

    // Store file in state
    if (zone.id === 'source') {
        state.sourceFile = file;
    } else if (zone.id === 'target') {
        state.targetFile = file;
    } else if (zone.id === 'ground-truth') {
        state.groundTruthFile = file;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById(zone.previewId);
        const img = preview.querySelector('img');
        const name = document.getElementById(zone.nameId);

        img.src = e.target.result;
        name.textContent = file.name;
        preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);

    // Check if all files are selected
    checkAddExampleButton();
}

function checkAddExampleButton() {
    const btn = document.getElementById('add-example-btn');
    btn.disabled = !(state.sourceFile && state.targetFile && state.groundTruthFile);
}

/**
 * Form Initialization
 */
function initializeForms() {
    // Add Example Form
    document.getElementById('add-example-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await addTrainingExample();
    });

    // Training Form
    document.getElementById('training-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await startTraining();
    });

    // Import Weights Form
    document.getElementById('select-weights-btn').addEventListener('click', () => {
        document.getElementById('weights-file-input').click();
    });

    document.getElementById('weights-file-input').addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            state.weightsFile = e.target.files[0];
            document.getElementById('weights-filename').textContent = `Selected: ${state.weightsFile.name}`;
            document.getElementById('import-weights-btn').classList.remove('hidden');
        }
    });

    document.getElementById('import-weights-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await importWeights();
    });

    // Button handlers
    document.getElementById('refresh-examples-btn').addEventListener('click', loadExamples);
    document.getElementById('validate-btn').addEventListener('click', runValidation);
    document.getElementById('reset-weights-btn').addEventListener('click', resetWeights);
    document.getElementById('refresh-sessions-btn').addEventListener('click', loadSessions);
}

/**
 * Statistics Loading
 */
async function loadStatistics() {
    try {
        const response = await fetch('/training/dataset-stats');
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;
            document.getElementById('stat-total-examples').textContent = stats.total_examples || 0;
            document.getElementById('stat-training-sessions').textContent = stats.total_sessions || 0;

            if (stats.average_accuracy !== null) {
                document.getElementById('stat-avg-accuracy').textContent =
                    `${(stats.average_accuracy * 100).toFixed(1)}%`;
            }

            if (stats.best_worker) {
                document.getElementById('stat-best-worker').textContent =
                    stats.best_worker.replace('_', ' ');
            }

            state.stats = stats;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Training Examples Management
 */
async function addTrainingExample() {
    const btn = document.getElementById('add-example-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Adding...';

    try {
        const formData = new FormData();
        formData.append('source', state.sourceFile);
        formData.append('target', state.targetFile);
        formData.append('ground_truth', state.groundTruthFile);

        // Add metadata if provided
        const metadataInput = document.getElementById('metadata-input').value.trim();
        if (metadataInput) {
            try {
                JSON.parse(metadataInput); // Validate JSON
                formData.append('metadata', metadataInput);
            } catch (e) {
                showNotification('warning', 'Invalid metadata', 'Metadata must be valid JSON. Ignoring metadata.');
            }
        }

        const response = await fetch('/training/add-example', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showNotification('success', 'Success!', 'Training example added successfully');

            // Reset form
            state.sourceFile = null;
            state.targetFile = null;
            state.groundTruthFile = null;

            document.querySelectorAll('[id$="-preview"]').forEach(el => el.classList.add('hidden'));
            document.getElementById('metadata-input').value = '';
            document.getElementById('add-example-form').reset();

            // Reload examples and stats
            await loadExamples();
            await loadStatistics();
        } else {
            showNotification('error', 'Error', data.error || 'Failed to add training example');
        }
    } catch (error) {
        showNotification('error', 'Error', 'Failed to add training example');
        console.error('Error adding example:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus mr-2"></i>Add Training Example';
        checkAddExampleButton();
    }
}

async function loadExamples() {
    try {
        const response = await fetch('/training/examples?limit=50');
        const data = await response.json();

        if (data.success) {
            state.examples = data.examples;
            displayExamples(data.examples);
        }
    } catch (error) {
        console.error('Error loading examples:', error);
    }
}

function displayExamples(examples) {
    const container = document.getElementById('examples-list');
    const noExamples = document.getElementById('no-examples');

    if (examples.length === 0) {
        container.innerHTML = '';
        noExamples.classList.remove('hidden');
        return;
    }

    noExamples.classList.add('hidden');

    container.innerHTML = examples.map(example => `
        <div class="example-card">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Example ${example.example_id.substring(0, 8)}</span>
                ${example.has_results ? '<span class="worker-badge bg-green-100 text-green-800">Trained</span>' : '<span class="worker-badge bg-gray-100 text-gray-600">Untrained</span>'}
            </div>
            <div class="text-xs text-gray-500 mb-2">
                <i class="fas fa-clock mr-1"></i>${new Date(example.created_at).toLocaleString()}
            </div>
            ${example.metadata && Object.keys(example.metadata).length > 0 ? `
                <div class="text-xs text-gray-600 mt-2">
                    ${Object.entries(example.metadata).map(([key, value]) =>
                        `<span class="inline-block bg-gray-100 px-2 py-1 rounded mr-1 mb-1">${key}: ${value}</span>`
                    ).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

/**
 * Training Session Management
 */
async function startTraining() {
    const btn = document.getElementById('start-training-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Training...';

    const progressSection = document.getElementById('training-progress');
    progressSection.classList.remove('hidden');

    try {
        const numExamples = document.getElementById('num-examples-input').value;
        const epochs = parseInt(document.getElementById('epochs-input').value);
        const validationSplit = parseFloat(document.getElementById('validation-split-input').value);
        const verbose = document.getElementById('verbose-input').checked;

        const requestData = {
            epochs,
            validation_split: validationSplit,
            verbose
        };

        if (numExamples) {
            requestData.num_examples = parseInt(numExamples);
        }

        // Simulate progress (real implementation would use WebSocket or polling)
        updateTrainingProgress(20, 'Loading training examples...');

        const response = await fetch('/training/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        updateTrainingProgress(80, 'Processing results...');

        const data = await response.json();

        if (data.success) {
            updateTrainingProgress(100, 'Training complete!');
            displayTrainingResults(data.results);
            showNotification('success', 'Training Complete!', 'Worker weights have been updated');

            // Reload stats and weights
            await loadStatistics();
            await loadWeights();
        } else {
            showNotification('error', 'Training Failed', data.error || 'An error occurred during training');
        }
    } catch (error) {
        showNotification('error', 'Error', 'Failed to complete training');
        console.error('Training error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play mr-2"></i>Start Training';
    }
}

function updateTrainingProgress(percent, message) {
    document.getElementById('training-progress-bar').style.width = `${percent}%`;
    document.getElementById('training-progress-text').textContent = `${percent}%`;

    if (message) {
        const resultsDiv = document.getElementById('training-results');
        const messageEl = document.createElement('div');
        messageEl.className = 'text-sm text-gray-600';
        messageEl.innerHTML = `<i class="fas fa-check-circle text-green-500 mr-2"></i>${message}`;
        resultsDiv.appendChild(messageEl);
    }
}

function displayTrainingResults(results) {
    const resultsDiv = document.getElementById('training-results');

    const session = results.session;
    const validation = results.validation;

    resultsDiv.innerHTML = `
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-bold text-green-800 mb-2">Training Session Complete</h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="text-gray-600">Examples Trained:</span>
                    <span class="font-medium ml-2">${session.num_examples}</span>
                </div>
                <div>
                    <span class="text-gray-600">Epochs:</span>
                    <span class="font-medium ml-2">${session.epochs}</span>
                </div>
                <div>
                    <span class="text-gray-600">Avg Accuracy:</span>
                    <span class="font-medium ml-2">${(session.average_accuracy * 100).toFixed(2)}%</span>
                </div>
                <div>
                    <span class="text-gray-600">Duration:</span>
                    <span class="font-medium ml-2">${session.duration ? session.duration.toFixed(2) + 's' : 'N/A'}</span>
                </div>
            </div>
        </div>

        ${validation ? `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                <h4 class="font-bold text-blue-800 mb-2">Validation Results</h4>
                <div class="text-sm">
                    <div class="mb-2">
                        <span class="text-gray-600">Examples Validated:</span>
                        <span class="font-medium ml-2">${validation.num_examples}</span>
                    </div>
                    <div>
                        <span class="text-gray-600">Avg Validation Accuracy:</span>
                        <span class="font-medium ml-2">${(validation.average_accuracy * 100).toFixed(2)}%</span>
                    </div>
                </div>
            </div>
        ` : ''}
    `;
}

/**
 * Validation
 */
async function runValidation() {
    const btn = document.getElementById('validate-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Validating...';

    try {
        const response = await fetch('/training/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (data.success) {
            displayValidationResults(data.validation_results);
            showNotification('success', 'Validation Complete', 'Model validation finished successfully');
        } else {
            showNotification('error', 'Validation Failed', data.error || 'Failed to run validation');
        }
    } catch (error) {
        showNotification('error', 'Error', 'Failed to run validation');
        console.error('Validation error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Run Validation';
    }
}

function displayValidationResults(results) {
    document.getElementById('no-validation').classList.add('hidden');
    document.getElementById('validation-results').classList.remove('hidden');

    const metricsContainer = document.getElementById('validation-metrics');
    metricsContainer.innerHTML = `
        <div class="stat-card">
            <div class="text-2xl font-bold text-primary-600 mb-1">${results.num_examples}</div>
            <div class="text-sm text-gray-600">Examples Validated</div>
        </div>
        <div class="stat-card">
            <div class="text-2xl font-bold text-green-600 mb-1">${(results.average_accuracy * 100).toFixed(2)}%</div>
            <div class="text-sm text-gray-600">Average Accuracy</div>
        </div>
        <div class="stat-card">
            <div class="text-2xl font-bold text-blue-600 mb-1">${results.best_worker.replace('_', ' ')}</div>
            <div class="text-sm text-gray-600">Best Worker</div>
        </div>
    `;

    const performanceContainer = document.getElementById('worker-performance');
    performanceContainer.innerHTML = `
        <h4 class="font-bold text-lg mb-3">Worker Performance</h4>
        <div class="space-y-2">
            ${Object.entries(results.worker_accuracies).map(([workerId, accuracy]) => `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span class="font-medium">${workerId.replace('_', ' ')}</span>
                    <div class="flex items-center space-x-3">
                        <div class="w-32 bg-gray-200 rounded-full h-2">
                            <div class="progress-bar" style="width: ${accuracy * 100}%"></div>
                        </div>
                        <span class="text-sm font-bold text-gray-700">${(accuracy * 100).toFixed(2)}%</span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Weights Management
 */
async function loadWeights() {
    try {
        const response = await fetch('/worker-stats');
        const data = await response.json();

        if (data.success) {
            displayWeights(data.weights);
        }
    } catch (error) {
        console.error('Error loading weights:', error);
    }
}

function displayWeights(weights) {
    const container = document.getElementById('weights-list');

    const sortedWeights = Object.entries(weights).sort((a, b) => b[1] - a[1]);

    container.innerHTML = sortedWeights.map(([workerId, weight]) => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <span class="font-medium text-gray-700">${workerId.replace('_', ' ')}</span>
            <div class="flex items-center space-x-3">
                <div class="w-32 bg-gray-200 rounded-full h-2">
                    <div class="progress-bar" style="width: ${Math.min(weight * 100, 100)}%"></div>
                </div>
                <span class="text-sm font-bold text-gray-700 w-12 text-right">${weight.toFixed(3)}</span>
            </div>
        </div>
    `).join('');
}

async function importWeights() {
    if (!state.weightsFile) return;

    const btn = document.getElementById('import-weights-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Importing...';

    try {
        const formData = new FormData();
        formData.append('file', state.weightsFile);

        const response = await fetch('/training/weights/import', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showNotification('success', 'Weights Imported', 'Worker weights have been updated');
            await loadWeights();

            // Reset form
            state.weightsFile = null;
            document.getElementById('weights-filename').textContent = '';
            document.getElementById('import-weights-form').reset();
            btn.classList.add('hidden');
        } else {
            showNotification('error', 'Import Failed', data.error || 'Failed to import weights');
        }
    } catch (error) {
        showNotification('error', 'Error', 'Failed to import weights');
        console.error('Import error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check mr-2"></i>Import';
    }
}

async function resetWeights() {
    if (!confirm('Are you sure you want to reset all worker weights to default (1.0)? This action cannot be undone.')) {
        return;
    }

    const btn = document.getElementById('reset-weights-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Resetting...';

    try {
        const response = await fetch('/training/reset-weights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (data.success) {
            showNotification('success', 'Weights Reset', 'All worker weights have been reset to 1.0');
            await loadWeights();
        } else {
            showNotification('error', 'Reset Failed', data.error || 'Failed to reset weights');
        }
    } catch (error) {
        showNotification('error', 'Error', 'Failed to reset weights');
        console.error('Reset error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-undo mr-2"></i>Reset All Weights';
    }
}

/**
 * Sessions History
 */
async function loadSessions() {
    try {
        const response = await fetch('/training/sessions');
        const data = await response.json();

        if (data.success) {
            state.sessions = data.sessions;
            displaySessions(data.sessions);
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

function displaySessions(sessions) {
    const container = document.getElementById('sessions-list');
    const noSessions = document.getElementById('no-sessions');

    if (sessions.length === 0) {
        container.innerHTML = '';
        noSessions.classList.remove('hidden');
        return;
    }

    noSessions.classList.add('hidden');

    container.innerHTML = sessions.map(session => `
        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-3">
                <div>
                    <span class="font-bold text-lg">Session ${session.session_id.substring(0, 8)}</span>
                    <span class="ml-2 worker-badge ${session.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                        ${session.status}
                    </span>
                </div>
                <span class="text-sm text-gray-500">
                    <i class="fas fa-clock mr-1"></i>${new Date(session.start_time).toLocaleString()}
                </span>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                    <div class="text-gray-500">Examples</div>
                    <div class="font-medium">${session.num_examples}</div>
                </div>
                <div>
                    <div class="text-gray-500">Epochs</div>
                    <div class="font-medium">${session.epochs}</div>
                </div>
                <div>
                    <div class="text-gray-500">Learning Rate</div>
                    <div class="font-medium">${session.learning_rate.toFixed(3)}</div>
                </div>
                <div>
                    <div class="text-gray-500">Duration</div>
                    <div class="font-medium">
                        ${session.end_time ?
                            `${((new Date(session.end_time) - new Date(session.start_time)) / 1000).toFixed(1)}s` :
                            'In progress'}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Notifications
 */
function showNotification(type, title, message) {
    const notification = document.getElementById('notification');
    const icon = document.getElementById('notification-icon');
    const titleEl = document.getElementById('notification-title');
    const messageEl = document.getElementById('notification-message');

    // Configure based on type
    const configs = {
        success: {
            bgColor: 'bg-green-100',
            iconClass: 'fa-check-circle text-green-600',
            titleColor: 'text-green-800',
            messageColor: 'text-green-600'
        },
        error: {
            bgColor: 'bg-red-100',
            iconClass: 'fa-exclamation-circle text-red-600',
            titleColor: 'text-red-800',
            messageColor: 'text-red-600'
        },
        warning: {
            bgColor: 'bg-yellow-100',
            iconClass: 'fa-exclamation-triangle text-yellow-600',
            titleColor: 'text-yellow-800',
            messageColor: 'text-yellow-600'
        },
        info: {
            bgColor: 'bg-blue-100',
            iconClass: 'fa-info-circle text-blue-600',
            titleColor: 'text-blue-800',
            messageColor: 'text-blue-600'
        }
    };

    const config = configs[type] || configs.info;

    // Apply styles
    const notificationInner = notification.querySelector('div');
    notificationInner.className = `rounded-lg shadow-lg p-4 flex items-center space-x-3 ${config.bgColor}`;

    icon.className = `fas text-xl ${config.iconClass}`;
    titleEl.className = `font-medium ${config.titleColor}`;
    titleEl.textContent = title;

    messageEl.className = `text-sm ${config.messageColor}`;
    messageEl.textContent = message;

    // Show notification
    notification.classList.remove('hidden');

    // Auto-hide after 5 seconds
    setTimeout(hideNotification, 5000);
}

function hideNotification() {
    document.getElementById('notification').classList.add('hidden');
}

// Make hideNotification global for onclick handler
window.hideNotification = hideNotification;
