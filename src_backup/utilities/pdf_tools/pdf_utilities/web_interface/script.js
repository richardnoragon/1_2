// PDF Tools Hub - Batch Processor JavaScript

class PDFBatchProcessor {
    constructor() {
        this.selectedFiles = [];
        this.currentJobId = null;
        this.processingStatus = {
            isRunning: false,
            isPaused: false,
            totalFiles: 0,
            completedFiles: 0,
            failedFiles: 0,
            currentFile: null,
            startTime: null,
            results: []
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.updateConcurrentJobsDisplay();
        this.loadOperationParameters();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                this.switchTab(tabId);
            });
        });

        // File input
        const fileInput = document.getElementById('file-input');
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        // Operation type change
        const operationType = document.getElementById('operation-type');
        operationType.addEventListener('change', (e) => {
            this.loadOperationParameters(e.target.value);
        });

        // Concurrent jobs slider
        const concurrentJobs = document.getElementById('concurrent-jobs');
        concurrentJobs.addEventListener('input', (e) => {
            this.updateConcurrentJobsDisplay(e.target.value);
        });

        // Upload area click
        const uploadArea = document.getElementById('upload-area');
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('upload-area');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = Array.from(e.dataTransfer.files).filter(file => 
                file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
            );
            
            if (files.length > 0) {
                this.handleFileSelection(files);
            } else {
                this.showStatusMessage('Please select only PDF files.', 'warning');
            }
        });
    }

    handleFileSelection(files) {
        const validFiles = Array.from(files).filter(file => 
            file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
        );

        if (validFiles.length === 0) {
            this.showStatusMessage('No valid PDF files selected.', 'warning');
            return;
        }

        // Add new files to selection
        validFiles.forEach(file => {
            if (!this.selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                this.selectedFiles.push(file);
            }
        });

        this.updateFileList();
        this.showStatusMessage(`Added ${validFiles.length} PDF file(s).`, 'success');
    }

    updateFileList() {
        const fileListContainer = document.getElementById('file-list-container');
        const fileList = document.getElementById('file-list');

        if (this.selectedFiles.length === 0) {
            fileListContainer.style.display = 'none';
            return;
        }

        fileListContainer.style.display = 'block';
        fileList.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-file-pdf file-icon"></i>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${this.formatFileSize(file.size)} • ${file.type || 'PDF Document'}</p>
                    </div>
                </div>
                <button class="btn btn-danger btn-sm" onclick="batchProcessor.removeFile(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            fileList.appendChild(fileItem);
        });
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.showStatusMessage('File removed.', 'info');
    }

    clearFiles() {
        this.selectedFiles = [];
        this.updateFileList();
        this.showStatusMessage('All files cleared.', 'info');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    switchTab(tabId) {
        // Validation before switching
        if (tabId === 'configure' && this.selectedFiles.length === 0) {
            this.showStatusMessage('Please select PDF files first.', 'warning');
            return;
        }

        if (tabId === 'process' && this.selectedFiles.length === 0) {
            this.showStatusMessage('Please select PDF files first.', 'warning');
            return;
        }

        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`).classList.add('active');

        // Update processing stats when switching to process tab
        if (tabId === 'process') {
            this.updateProcessingStats();
        }
    }

    updateConcurrentJobsDisplay(value) {
        const slider = document.getElementById('concurrent-jobs');
        const display = document.getElementById('concurrent-jobs-value');
        const currentValue = value || slider.value;
        display.textContent = currentValue;
    }

    loadOperationParameters(operationType) {
        const operation = operationType || document.getElementById('operation-type').value;
        const paramsContainer = document.getElementById('operation-params');
        
        let paramsHTML = '<h3><i class="fas fa-cogs"></i> Operation Parameters</h3>';

        switch (operation) {
            case 'split':
                paramsHTML += `
                    <div class="config-grid">
                        <div class="config-section">
                            <label>Split Method:</label>
                            <select class="form-control" id="split-method">
                                <option value="pages">By Page Count</option>
                                <option value="ranges">By Page Ranges</option>
                                <option value="single">Single Pages</option>
                            </select>
                        </div>
                        <div class="config-section">
                            <label>Pages per File:</label>
                            <input type="number" class="form-control" id="pages-per-file" value="1" min="1">
                        </div>
                    </div>
                `;
                break;

            case 'compress':
                paramsHTML += `
                    <div class="config-grid">
                        <div class="config-section">
                            <label>Compression Level:</label>
                            <input type="range" class="range-input" id="compression-level" min="0" max="100" value="50">
                            <span class="range-value" id="compression-level-value">50%</span>
                        </div>
                        <div class="config-section">
                            <label>Image Quality:</label>
                            <select class="form-control" id="image-quality">
                                <option value="high">High Quality</option>
                                <option value="medium">Medium Quality</option>
                                <option value="low">Low Quality</option>
                            </select>
                        </div>
                    </div>
                `;
                break;

            case 'watermark':
                paramsHTML += `
                    <div class="config-grid">
                        <div class="config-section">
                            <label>Watermark Text:</label>
                            <input type="text" class="form-control" id="watermark-text" placeholder="Enter watermark text">
                        </div>
                        <div class="config-section">
                            <label>Opacity:</label>
                            <input type="range" class="range-input" id="watermark-opacity" min="0" max="100" value="50">
                            <span class="range-value" id="watermark-opacity-value">50%</span>
                        </div>
                        <div class="config-section">
                            <label>Position:</label>
                            <select class="form-control" id="watermark-position">
                                <option value="center">Center</option>
                                <option value="top-left">Top Left</option>
                                <option value="top-right">Top Right</option>
                                <option value="bottom-left">Bottom Left</option>
                                <option value="bottom-right">Bottom Right</option>
                            </select>
                        </div>
                    </div>
                `;
                break;

            case 'encrypt':
                paramsHTML += `
                    <div class="config-grid">
                        <div class="config-section">
                            <label>Password:</label>
                            <input type="password" class="form-control" id="encrypt-password" placeholder="Enter password">
                        </div>
                        <div class="config-section">
                            <label>Encryption Level:</label>
                            <select class="form-control" id="encryption-level">
                                <option value="128">128-bit</option>
                                <option value="256">256-bit</option>
                            </select>
                        </div>
                    </div>
                `;
                break;

            default:
                paramsHTML += '<p>No additional parameters required for this operation.</p>';
        }

        paramsContainer.innerHTML = paramsHTML;

        // Setup range input listeners
        this.setupRangeInputs();
    }

    setupRangeInputs() {
        document.querySelectorAll('.range-input').forEach(input => {
            const updateValue = () => {
                const valueDisplay = document.getElementById(input.id + '-value');
                if (valueDisplay) {
                    valueDisplay.textContent = input.value + (input.id.includes('opacity') || input.id.includes('compression') ? '%' : '');
                }
            };
            
            input.addEventListener('input', updateValue);
            updateValue(); // Initial update
        });
    }

    selectOutputDirectory() {
        // In a real implementation, this would open a directory picker
        // For demo purposes, we'll simulate it
        const directory = prompt('Enter output directory path:', './output');
        if (directory) {
            document.getElementById('output-directory').value = directory;
            this.showStatusMessage('Output directory selected.', 'success');
        }
    }

    updateProcessingStats() {
        document.getElementById('total-files').textContent = this.selectedFiles.length;
        document.getElementById('completed-files').textContent = this.processingStatus.completedFiles;
        document.getElementById('failed-files').textContent = this.processingStatus.failedFiles;
        
        // Update estimated time
        if (this.processingStatus.isRunning && this.processingStatus.startTime) {
            const elapsed = (Date.now() - this.processingStatus.startTime) / 1000;
            const avgTimePerFile = elapsed / Math.max(this.processingStatus.completedFiles, 1);
            const remainingFiles = this.selectedFiles.length - this.processingStatus.completedFiles - this.processingStatus.failedFiles;
            const estimatedTime = Math.round(avgTimePerFile * remainingFiles);
            
            document.getElementById('estimated-time').textContent = this.formatTime(estimatedTime);
        } else {
            document.getElementById('estimated-time').textContent = '--';
        }
    }

    formatTime(seconds) {
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds}s`;
    }

    async startProcessing() {
        if (this.selectedFiles.length === 0) {
            this.showStatusMessage('No files selected for processing.', 'warning');
            return;
        }

        // Validate configuration
        const config = this.getProcessingConfig();
        if (!this.validateConfig(config)) {
            return;
        }

        // Initialize processing
        this.processingStatus = {
            isRunning: true,
            isPaused: false,
            totalFiles: this.selectedFiles.length,
            completedFiles: 0,
            failedFiles: 0,
            currentFile: null,
            startTime: Date.now(),
            results: []
        };

        // Update UI
        this.updateProcessingControls();
        this.updateProcessingStats();
        this.addLogEntry('Starting batch processing...', 'info');

        // Start processing files
        try {
            await this.processFiles(config);
        } catch (error) {
            this.addLogEntry(`Processing failed: ${error.message}`, 'error');
            this.showStatusMessage('Processing failed. Check the log for details.', 'error');
        } finally {
            this.processingStatus.isRunning = false;
            this.updateProcessingControls();
        }
    }

    getProcessingConfig() {
        const operationType = document.getElementById('operation-type').value;
        const outputDirectory = document.getElementById('output-directory').value;
        const priority = document.getElementById('priority').value;
        const concurrentJobs = parseInt(document.getElementById('concurrent-jobs').value);

        const config = {
            operation: operationType,
            outputDirectory: outputDirectory || './output',
            priority: priority,
            concurrentJobs: concurrentJobs,
            parameters: {}
        };

        // Add operation-specific parameters
        switch (operationType) {
            case 'split':
                config.parameters.method = document.getElementById('split-method')?.value || 'pages';
                config.parameters.pagesPerFile = parseInt(document.getElementById('pages-per-file')?.value || 1);
                break;
            case 'compress':
                config.parameters.compressionLevel = parseInt(document.getElementById('compression-level')?.value || 50);
                config.parameters.imageQuality = document.getElementById('image-quality')?.value || 'medium';
                break;
            case 'watermark':
                config.parameters.text = document.getElementById('watermark-text')?.value || '';
                config.parameters.opacity = parseInt(document.getElementById('watermark-opacity')?.value || 50);
                config.parameters.position = document.getElementById('watermark-position')?.value || 'center';
                break;
            case 'encrypt':
                config.parameters.password = document.getElementById('encrypt-password')?.value || '';
                config.parameters.encryptionLevel = document.getElementById('encryption-level')?.value || '128';
                break;
        }

        return config;
    }

    validateConfig(config) {
        if (!config.outputDirectory) {
            this.showStatusMessage('Please specify an output directory.', 'warning');
            return false;
        }

        // Operation-specific validation
        switch (config.operation) {
            case 'watermark':
                if (!config.parameters.text) {
                    this.showStatusMessage('Please enter watermark text.', 'warning');
                    return false;
                }
                break;
            case 'encrypt':
                if (!config.parameters.password) {
                    this.showStatusMessage('Please enter a password for encryption.', 'warning');
                    return false;
                }
                break;
        }

        return true;
    }

    async processFiles(config) {
        const batchSize = config.concurrentJobs;
        
        for (let i = 0; i < this.selectedFiles.length; i += batchSize) {
            if (!this.processingStatus.isRunning) break;
            
            // Wait if paused
            while (this.processingStatus.isPaused) {
                await this.sleep(100);
            }

            const batch = this.selectedFiles.slice(i, i + batchSize);
            const promises = batch.map(file => this.processFile(file, config));
            
            await Promise.allSettled(promises);
        }

        // Complete processing
        this.completeProcessing();
    }

    async processFile(file, config) {
        this.processingStatus.currentFile = file.name;
        this.updateCurrentFileDisplay();
        this.addLogEntry(`Processing: ${file.name}`, 'info');

        try {
            // Simulate file processing with progress updates
            await this.simulateFileProcessing(file, config);
            
            this.processingStatus.completedFiles++;
            this.processingStatus.results.push({
                file: file.name,
                status: 'success',
                outputPath: `${config.outputDirectory}/${file.name}`,
                processingTime: Math.random() * 5 + 1 // Simulated time
            });
            
            this.addLogEntry(`Completed: ${file.name}`, 'success');
            
        } catch (error) {
            this.processingStatus.failedFiles++;
            this.processingStatus.results.push({
                file: file.name,
                status: 'error',
                error: error.message,
                processingTime: 0
            });
            
            this.addLogEntry(`Failed: ${file.name} - ${error.message}`, 'error');
        }

        this.updateProcessingStats();
        this.updateOverallProgress();
    }

    async simulateFileProcessing(file, config) {
        // Simulate processing time based on file size and operation
        const baseTime = Math.min(file.size / 1000000, 5); // Max 5 seconds
        const operationMultiplier = {
            'split': 1,
            'merge': 1.5,
            'compress': 2,
            'extract_text': 1.2,
            'extract_images': 2.5,
            'watermark': 1.8,
            'encrypt': 1.3,
            'convert_to_images': 3
        };
        
        const totalTime = baseTime * (operationMultiplier[config.operation] || 1) * 1000;
        const steps = 20;
        const stepTime = totalTime / steps;

        for (let i = 0; i <= steps; i++) {
            if (!this.processingStatus.isRunning) {
                throw new Error('Processing cancelled');
            }

            // Wait if paused
            while (this.processingStatus.isPaused) {
                await this.sleep(100);
            }

            const progress = (i / steps) * 100;
            this.updateCurrentFileProgress(progress);
            
            // Simulate occasional errors
            if (Math.random() < 0.05 && i > 5) { // 5% chance of error after 25% progress
                throw new Error('Simulated processing error');
            }

            await this.sleep(stepTime);
        }
    }

    updateCurrentFileDisplay() {
        const currentFileName = document.getElementById('current-file-name');
        currentFileName.textContent = this.processingStatus.currentFile || 'Ready to start...';
    }

    updateCurrentFileProgress(progress) {
        const progressFill = document.getElementById('current-file-progress');
        const progressText = document.getElementById('current-file-progress-text');
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `${Math.round(progress)}%`;
    }

    updateOverallProgress() {
        const totalProcessed = this.processingStatus.completedFiles + this.processingStatus.failedFiles;
        const progress = (totalProcessed / this.processingStatus.totalFiles) * 100;
        
        const progressFill = document.getElementById('overall-progress');
        const progressText = document.getElementById('overall-progress-text');
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `${Math.round(progress)}%`;
    }

    updateProcessingControls() {
        const startBtn = document.getElementById('start-btn');
        const pauseBtn = document.getElementById('pause-btn');
        const cancelBtn = document.getElementById('cancel-btn');

        if (this.processingStatus.isRunning) {
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            cancelBtn.disabled = false;
            
            if (this.processingStatus.isPaused) {
                pauseBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
            } else {
                pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
            }
        } else {
            startBtn.disabled = false;
            pauseBtn.disabled = true;
            cancelBtn.disabled = true;
        }
    }

    pauseProcessing() {
        if (this.processingStatus.isRunning) {
            this.processingStatus.isPaused = !this.processingStatus.isPaused;
            this.updateProcessingControls();
            
            const action = this.processingStatus.isPaused ? 'paused' : 'resumed';
            this.addLogEntry(`Processing ${action}.`, 'warning');
            this.showStatusMessage(`Processing ${action}.`, 'info');
        }
    }

    cancelProcessing() {
        if (this.processingStatus.isRunning) {
            this.processingStatus.isRunning = false;
            this.processingStatus.isPaused = false;
            this.updateProcessingControls();
            this.addLogEntry('Processing cancelled by user.', 'warning');
            this.showStatusMessage('Processing cancelled.', 'warning');
        }
    }

    completeProcessing() {
        const totalTime = (Date.now() - this.processingStatus.startTime) / 1000;
        this.addLogEntry(`Batch processing completed in ${this.formatTime(Math.round(totalTime))}.`, 'success');
        
        // Update results tab
        this.updateResultsDisplay();
        
        // Show completion message
        const successCount = this.processingStatus.completedFiles;
        const errorCount = this.processingStatus.failedFiles;
        
        if (errorCount === 0) {
            this.showStatusMessage(`All ${successCount} files processed successfully!`, 'success');
        } else {
            this.showStatusMessage(`Processing completed: ${successCount} successful, ${errorCount} failed.`, 'warning');
        }
        
        // Auto-switch to results tab
        this.switchTab('results');
    }

    updateResultsDisplay() {
        const resultsSummary = document.getElementById('results-summary');
        const resultsActions = document.getElementById('results-actions');
        const resultsList = document.getElementById('results-list');
        
        // Show summary
        resultsSummary.style.display = 'block';
        resultsActions.style.display = 'flex';
        
        // Update summary cards
        document.getElementById('success-count').textContent = this.processingStatus.completedFiles;
        document.getElementById('error-count').textContent = this.processingStatus.failedFiles;
        
        const totalTime = (Date.now() - this.processingStatus.startTime) / 1000;
        document.getElementById('total-time').textContent = this.formatTime(Math.round(totalTime));
        
        // Update results list
        resultsList.innerHTML = '';
        
        this.processingStatus.results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            
            const statusIcon = result.status === 'success' ? 
                '<i class="fas fa-check"></i>' : 
                '<i class="fas fa-times"></i>';
            
            resultItem.innerHTML = `
                <div class="result-info">
                    <div class="result-status ${result.status}">
                        ${statusIcon}
                    </div>
                    <div class="result-details">
                        <h4>${result.file}</h4>
                        <p>${result.status === 'success' ? 
                            `Processed in ${this.formatTime(Math.round(result.processingTime))}` : 
                            `Error: ${result.error}`}</p>
                    </div>
                </div>
                ${result.status === 'success' ? 
                    `<button class="btn btn-outline btn-sm" onclick="batchProcessor.downloadFile('${result.outputPath}')">
                        <i class="fas fa-download"></i> Download
                    </button>` : 
                    '<span class="text-danger">Failed</span>'}
            `;
            
            resultsList.appendChild(resultItem);
        });
    }

    downloadFile(filePath) {
        // In a real implementation, this would trigger a file download
        this.showStatusMessage(`Downloading: ${filePath}`, 'info');
        console.log('Download file:', filePath);
    }

    downloadAllResults() {
        const successfulResults = this.processingStatus.results.filter(r => r.status === 'success');
        if (successfulResults.length === 0) {
            this.showStatusMessage('No successful results to download.', 'warning');
            return;
        }
        
        // In a real implementation, this would create a zip file of all results
        this.showStatusMessage(`Downloading ${successfulResults.length} processed files...`, 'info');
        console.log('Download all results:', successfulResults);
    }

    downloadReport() {
        // Generate and download processing report
        const report = this.generateProcessingReport();
        const blob = new Blob([report], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch_processing_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showStatusMessage('Processing report downloaded.', 'success');
    }

    generateProcessingReport() {
        const config = this.getProcessingConfig();
        const totalTime = (Date.now() - this.processingStatus.startTime) / 1000;
        
        let report = `PDF Batch Processing Report\n`;
        report += `Generated: ${new Date().toLocaleString()}\n\n`;
        report += `Configuration:\n`;
        report += `- Operation: ${config.operation}\n`;
        report += `- Output Directory: ${config.outputDirectory}\n`;
        report += `- Priority: ${config.priority}\n`;
        report += `- Concurrent Jobs: ${config.concurrentJobs}\n\n`;
        report += `Results Summary:\n`;
        report += `- Total Files: ${this.processingStatus.totalFiles}\n`;
        report += `- Successful: ${this.processingStatus.completedFiles}\n`;
        report += `- Failed: ${this.processingStatus.failedFiles}\n`;
        report += `- Total Time: ${this.formatTime(Math.round(totalTime))}\n\n`;
        report += `Detailed Results:\n`;
        
        this.processingStatus.results.forEach((result, index) => {
            report += `${index + 1}. ${result.file}\n`;
            report += `   Status: ${result.status}\n`;
            if (result.status === 'success') {
                report += `   Output: ${result.outputPath}\n`;
                report += `   Time: ${this.formatTime(Math.round(result.processingTime))}\n`;
            } else {
                report += `   Error: ${result.error}\n`;
            }
            report += `\n`;
        });
        
        return report;
    }

    resetProcessor() {
        // Reset all state
        this.selectedFiles = [];
        this.currentJobId = null;
        this.processingStatus = {
            isRunning: false,
            isPaused: false,
            totalFiles: 0,
            completedFiles: 0,
            failedFiles: 0,
            currentFile: null,
            startTime: null,
            results: []
        };
        
        // Reset UI
        this.updateFileList();
        this.updateProcessingStats();
        this.updateProcessingControls();
        this.updateCurrentFileProgress(0);
        this.updateOverallProgress();
        
        // Clear log
        const logContainer = document.getElementById('processing-log');
        logContainer.innerHTML = `
            <div class="log-entry info">
                <span class="log-time">[Ready]</span>
                <span class="log-message">Batch processor ready. Click "Start Processing" to begin.</span>
            </div>
        `;
        
        // Hide results
        document.getElementById('results-summary').style.display = 'none';
        document.getElementById('results-actions').style.display = 'none';
        
        // Switch to upload tab
        this.switchTab('upload');
        
        this.showStatusMessage('Batch processor reset.', 'info');
    }

    addLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('processing-log');
        const timestamp = new Date().toLocaleTimeString();
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = `
            <span class="log-time">[${timestamp}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    showStatusMessage(message, type = 'info') {
        const statusMessages = document.getElementById('status-messages');
        
        const messageElement = document.createElement('div');
        messageElement.className = `status-message ${type}`;
        messageElement.textContent = message;
        
        statusMessages.appendChild(messageElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 5000);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global functions for HTML onclick handlers
function switchTab(tabId) {
    batchProcessor.switchTab(tabId);
}

function clearFiles() {
    batchProcessor.clearFiles();
}

function selectOutputDirectory() {
    batchProcessor.selectOutputDirectory();
}

function startProcessing() {
    batchProcessor.startProcessing();
}

function pauseProcessing() {
    batchProcessor.pauseProcessing();
}

function cancelProcessing() {
    batchProcessor.cancelProcessing();
}

function downloadAllResults() {
    batchProcessor.downloadAllResults();
}

function downloadReport() {
    batchProcessor.downloadReport();
}

function resetProcessor() {
    batchProcessor.resetProcessor();
}

// Initialize the batch processor when the page loads
let batchProcessor;

document.addEventListener('DOMContentLoaded', function() {
    batchProcessor = new PDFBatchProcessor();
    
    // Add some initial log entries
    batchProcessor.addLogEntry('PDF Batch Processor initialized.', 'success');
    batchProcessor.addLogEntry('Ready to process PDF files.', 'info');
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PDFBatchProcessor;
}