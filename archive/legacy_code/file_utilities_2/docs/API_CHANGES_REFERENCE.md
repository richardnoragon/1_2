# API Changes Reference - File Utilities 2 Migration

## Overview

This document provides a comprehensive reference for all API changes, enhancements, and additions made during the file_utilities_2 migration. All changes maintain 100% backward compatibility while providing significant new functionality.

## Table of Contents

1. [Signal API Changes](#signal-api-changes)
2. [Method Enhancements](#method-enhancements)
3. [New Classes and Components](#new-classes-and-components)
4. [Import Path Changes](#import-path-changes)
5. [Configuration and Parameters](#configuration-and-parameters)
6. [Backward Compatibility Guide](#backward-compatibility-guide)
7. [Migration Examples](#migration-examples)

## Signal API Changes

### Core Logic Signals ([`ChecksumLogic`](../core/check_sum.py))

#### Existing Signals (Preserved)
```python
# All original signals maintained with identical behavior
progress_updated = pyqtSignal(int, int)  # current_bytes, total_bytes
result_ready = pyqtSignal(dict)          # results dictionary
error_occurred = pyqtSignal(str)         # error message
finished = pyqtSignal()                  # operation completion
```

#### New Signals (Added)
```python
# Enhanced progress tracking signals
progress_percentage = pyqtSignal(int)        # percentage (0-100)
progress_message = pyqtSignal(str)           # detailed status message
milestone_reached = pyqtSignal(str, int)     # milestone_name, percentage
time_estimate = pyqtSignal(str)              # estimated time remaining
```

### Signal Usage Examples

#### Basic Progress Tracking (Original - Still Works)
```python
def update_progress(current, total):
    percentage = int((current / total) * 100) if total > 0 else 0
    print(f"Progress: {percentage}%")

checksummer.progress_updated.connect(update_progress)
```

#### Enhanced Progress Tracking (New)
```python
def update_percentage(percentage):
    progress_bar.setValue(percentage)

def update_status(message):
    status_label.setText(message)

def update_milestone(milestone, percentage):
    print(f"Milestone: {milestone} ({percentage}%)")

def update_eta(estimate):
    eta_label.setText(estimate)

# Connect enhanced signals
checksummer.progress_percentage.connect(update_percentage)
checksummer.progress_message.connect(update_status)
checksummer.milestone_reached.connect(update_milestone)
checksummer.time_estimate.connect(update_eta)
```

## Method Enhancements

### Constructor Enhancements

#### Original Constructor (Preserved)
```python
def __init__(self, target_path, algorithm, expected_checksum=None,
             checksum_file_path=None, mode='calculate'):
```

#### Enhanced Internal State (New)
```python
# New internal state variables for progress tracking
self._start_time = None          # Operation start time
self._bytes_processed = 0        # Bytes processed so far
self._total_bytes = 0           # Total bytes to process
```

### Enhanced Methods

#### [`stop()`](../core/check_sum.py:52) Method Enhancement
```python
# Original behavior preserved
def stop(self):
    """Stop the current operation."""
    self._is_running = False
    # New: Enhanced user feedback
    self.progress_message.emit("Operation cancelled by user")
```

#### [`run()`](../core/check_sum.py:57) Method Enhancement
```python
# Original structure preserved with enhanced milestone tracking
def run(self):
    """Main execution method to be run in a thread."""
    import time
    try:
        self._is_running = True
        self._start_time = time.time()  # New: Track start time
        results = {}

        # New: Initial milestone
        self.milestone_reached.emit("Starting operation", 0)
        self.progress_message.emit(f"Initializing {self.mode}...")

        if self.mode == 'calculate_file':
            # New: Milestone tracking
            self.milestone_reached.emit("Calculating file checksum", 10)
            checksum = self._calculate_file_checksum(self.target_path)
            if checksum:
                results[self.target_path] = checksum
                # New: Completion milestone
                self.milestone_reached.emit("File checksum completed", 100)
        # ... other modes with similar enhancements
```

### File Processing Enhancement

#### [`_calculate_file_checksum()`](../core/check_sum.py:104) Method
```python
# Significantly enhanced with detailed progress tracking
def _calculate_file_checksum(self, file_path):
    """Calculates the checksum for a single file with detailed progress."""
    import time
    if not self._is_running:
        return None
    
    hasher = hashlib.new(self.algorithm)
    try:
        file_size = os.path.getsize(file_path)
        self._total_bytes = file_size
        self._bytes_processed = 0
        
        # New: Initial progress message
        self.progress_message.emit(f"Reading file: {os.path.basename(file_path)}")
        
        with open(file_path, 'rb') as f:
            start_time = time.time()
            last_update_time = start_time
            
            while self._is_running:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                hasher.update(chunk)
                self._bytes_processed += len(chunk)
                
                current_time = time.time()
                
                # New: Throttled progress updates every 0.1 seconds
                if (current_time - last_update_time >= 0.1 or
                    self._bytes_processed == file_size):
                    
                    percentage = int((self._bytes_processed / file_size) * 100)
                    # New: Enhanced progress signals
                    self.progress_percentage.emit(percentage)
                    self.progress_updated.emit(self._bytes_processed, file_size)
                    
                    # New: Time estimation
                    if self._bytes_processed > 0:
                        elapsed = current_time - start_time
                        rate = self._bytes_processed / elapsed
                        remaining_bytes = file_size - self._bytes_processed
                        if rate > 0 and remaining_bytes > 0:
                            eta_seconds = remaining_bytes / rate
                            if eta_seconds > 60:
                                eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                            else:
                                eta_str = f"{int(eta_seconds)}s"
                            self.time_estimate.emit(f"ETA: {eta_str}")
                    
                    # New: Detailed status messages
                    mb_processed = self._bytes_processed / (1024 * 1024)
                    mb_total = file_size / (1024 * 1024)
                    self.progress_message.emit(
                        f"Processing: {mb_processed:.1f}/{mb_total:.1f} MB ({percentage}%)"
                    )
                    
                    last_update_time = current_time

            if not self._is_running:
                return None
                
            # New: Final progress update
            self.progress_percentage.emit(100)
            self.progress_message.emit("Finalizing checksum calculation...")
            
            return hasher.hexdigest()
```

## New Classes and Components

### [`ChecksumWindow`](../gui/check_sum_standardized.py:17) - Standardized GUI

#### New Features
```python
class ChecksumWindow(QMainWindow):
    """Standardized checksum utility window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checksum Utility")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # New: Standard theme application
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        self._setup_ui()
        self.checksum_thread = None
        self.cancel_button = None
        # New: Progress timer for UI updates
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress_display)
```

#### Enhanced Progress UI
```python
def _show_progress_ui(self):
    """Show progress UI elements."""
    self.progress_group.setVisible(True)
    self.progress_bar.setVisible(True)
    self.progress_bar.setRange(0, 100)
    self.progress_bar.setValue(0)
    self.progress_message.setVisible(True)
    self.time_estimate_label.setVisible(True)
    
    # Disable action buttons and show cancel
    self.calculate_btn.setEnabled(False)
    self.verify_btn.setEnabled(False)
    self.clear_btn.setEnabled(False)
    self.cancel_button.setVisible(True)

def _hide_progress_ui(self):
    """Hide progress UI elements."""
    self.progress_group.setVisible(False)
    self.progress_bar.setVisible(False)
    self.progress_message.setVisible(False)
    self.time_estimate_label.setVisible(False)
    
    # Re-enable action buttons and hide cancel
    self.calculate_btn.setEnabled(True)
    self.verify_btn.setEnabled(True)
    self.clear_btn.setEnabled(True)
    self.cancel_button.setVisible(False)
```

#### Enhanced Signal Connections
```python
def _connect_thread_signals(self):
    """Connect enhanced thread signals."""
    self.checksum_thread.progress_percentage.connect(
        self.progress_bar.setValue
    )
    self.checksum_thread.progress_message.connect(
        self.progress_message.setText
    )
    self.checksum_thread.milestone_reached.connect(
        self._on_milestone_reached
    )
    self.checksum_thread.time_estimate.connect(
        self.time_estimate_label.setText
    )
    self.checksum_thread.error_occurred.connect(self.on_error)
    self.checksum_thread.finished.connect(self._on_thread_finished)
```

### [`EnhancedChecksumThread`](../gui/check_sum_standardized.py:372) - Enhanced Threading

#### New Threading Capabilities
```python
class EnhancedChecksumThread(QThread):
    """Enhanced thread for calculating checksums with real-time progress."""
    
    # New: Comprehensive signal set
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_percentage = pyqtSignal(int)
    progress_message = pyqtSignal(str)
    milestone_reached = pyqtSignal(str, int)
    time_estimate = pyqtSignal(str)
    
    def __init__(self, file_path, algorithm, expected_checksum=None):
        super().__init__()
        self.file_path = file_path
        self.algorithm = algorithm
        self.expected_checksum = expected_checksum
        self.checksum_logic = None
        self._cancelled = False
    
    # New: Cancellation support
    def cancel(self):
        """Cancel the current operation."""
        self._cancelled = True
        if self.checksum_logic:
            self.checksum_logic.stop()
```

#### Enhanced Result Processing
```python
def _handle_result(self, results):
    """Handle results from ChecksumLogic and format for GUI."""
    try:
        if self._cancelled:
            return
            
        file_path = self.file_path
        
        if self.expected_checksum:
            # Verification mode
            status = results.get(file_path, "ERROR")
            is_valid = status == "OK"
            
            result = {
                'file_path': file_path,
                'algorithm': self.algorithm,
                'is_valid': is_valid,
                'expected': self.expected_checksum,
                'actual': results.get('calculated_checksum', ''),
                'status': status
            }
        else:
            # Calculation mode
            checksum = results.get(file_path, '')
            
            result = {
                'file_path': file_path,
                'algorithm': self.algorithm,
                'checksum': checksum
            }
        
        self.result_ready.emit(result)
        
    except Exception as e:
        self.error_occurred.emit(f"Error processing results: {e}")
```

## Import Path Changes

### Original Import Paths (Still Supported)
```python
# Original imports continue to work
from check_sum import ChecksumLogic, VALID_ALGORITHMS
from check_sum_gui import ChecksumGUI
```

### Enhanced Import Paths (Recommended)
```python
# Enhanced package imports
from file_utilities_2 import ChecksumLogic, VALID_ALGORITHMS
from file_utilities_2.core.check_sum import ChecksumLogic, VALID_ALGORITHMS
from file_utilities_2.gui.check_sum_gui import ChecksumGUI
from file_utilities_2.gui.check_sum_standardized import ChecksumWindow, EnhancedChecksumThread
```

### Package-Level Exports
```python
# file_utilities_2/__init__.py
__all__ = [
    "__version__",
    "__author__",
    # Core checksum functionality
    "ChecksumLogic",
    "VALID_ALGORITHMS",
    # GUI components
    "ChecksumGUI",
    "ChecksumWindow",
    "MyGUI",
]
```

## Configuration and Parameters

### Enhanced Constructor Parameters

#### Original Parameters (Preserved)
```python
ChecksumLogic(
    target_path,           # str: Path to file or directory
    algorithm,             # str: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
    expected_checksum,     # str: Expected checksum for verification (optional)
    checksum_file_path,    # str: Path to checksum file (optional)
    mode                   # str: Operation mode ('calculate', 'verify', etc.)
)
```

#### Enhanced Mode Options
```python
# Enhanced mode specifications
modes = [
    'calculate_file',      # Calculate checksum for single file
    'calculate_dir',       # Calculate checksums for directory
    'verify_file',         # Verify single file against expected checksum
    'verify_dir'           # Verify directory against checksum file
]
```

### Algorithm Support

#### Supported Algorithms
```python
VALID_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512']

# Algorithm selection examples
checksummer = ChecksumLogic(file_path, 'sha256')    # SHA-256 (recommended)
checksummer = ChecksumLogic(file_path, 'md5')       # MD5 (legacy support)
checksummer = ChecksumLogic(file_path, 'sha1')      # SHA-1 (legacy support)
checksummer = ChecksumLogic(file_path, 'sha512')    # SHA-512 (high security)
```

## Backward Compatibility Guide

### Existing Code Compatibility

#### No Changes Required
```python
# This code works exactly as before
from check_sum import ChecksumLogic

checksummer = ChecksumLogic('/path/to/file.txt', 'sha256')
checksummer.progress_updated.connect(lambda c, t: print(f"{c}/{t}"))
result = checksummer.calculate_sha256('/path/to/file.txt')
```

#### Optional Enhancements
```python
# Enhanced features can be added incrementally
from file_utilities_2.core.check_sum import ChecksumLogic

checksummer = ChecksumLogic('/path/to/file.txt', 'sha256', mode='calculate_file')

# Original signals still work
checksummer.progress_updated.connect(lambda c, t: print(f"{c}/{t}"))

# New signals provide additional information
checksummer.progress_percentage.connect(lambda p: print(f"{p}%"))
checksummer.progress_message.connect(lambda m: print(f"Status: {m}"))
checksummer.milestone_reached.connect(lambda m, p: print(f"Milestone: {m} ({p}%)"))
checksummer.time_estimate.connect(lambda e: print(f"ETA: {e}"))

# Run with enhanced progress tracking
checksummer.run()
```

### GUI Compatibility

#### Original GUI (Preserved)
```python
# Original GUI continues to work
from check_sum_gui import ChecksumGUI
window = ChecksumGUI()
window.show()
```

#### Enhanced GUI (New)
```python
# Enhanced GUI with modern features
from file_utilities_2.gui.check_sum_standardized import ChecksumWindow
window = ChecksumWindow()
window.show()
```

## Migration Examples

### Basic Migration Example

#### Before (Original)
```python
import sys
from PyQt5.QtWidgets import QApplication
from check_sum import ChecksumLogic

def progress_callback(current, total):
    percentage = int((current / total) * 100) if total > 0 else 0
    print(f"Progress: {percentage}%")

app = QApplication(sys.argv)
checksummer = ChecksumLogic('/path/to/file.txt', 'sha256')
checksummer.progress_updated.connect(progress_callback)
checksum = checksummer.calculate_sha256('/path/to/file.txt')
print(f"Checksum: {checksum}")
```

#### After (Enhanced)
```python
import sys
from PyQt5.QtWidgets import QApplication
from file_utilities_2.core.check_sum import ChecksumLogic

def progress_callback(current, total):
    percentage = int((current / total) * 100) if total > 0 else 0
    print(f"Progress: {percentage}%")

def percentage_callback(percentage):
    print(f"Percentage: {percentage}%")

def status_callback(message):
    print(f"Status: {message}")

def milestone_callback(milestone, percentage):
    print(f"Milestone: {milestone} ({percentage}%)")

def eta_callback(estimate):
    print(f"ETA: {estimate}")

app = QApplication(sys.argv)
checksummer = ChecksumLogic('/path/to/file.txt', 'sha256', mode='calculate_file')

# Original signal (still works)
checksummer.progress_updated.connect(progress_callback)

# Enhanced signals (new functionality)
checksummer.progress_percentage.connect(percentage_callback)
checksummer.progress_message.connect(status_callback)
checksummer.milestone_reached.connect(milestone_callback)
checksummer.time_estimate.connect(eta_callback)

# Run with enhanced progress tracking
checksummer.run()
```

### GUI Migration Example

#### Before (Original)
```python
import sys
from PyQt5.QtWidgets import QApplication
from check_sum_gui import ChecksumGUI

app = QApplication(sys.argv)
window = ChecksumGUI()
window.show()
sys.exit(app.exec_())
```

#### After (Enhanced)
```python
import sys
from PyQt5.QtWidgets import QApplication
from file_utilities_2.gui.check_sum_standardized import ChecksumWindow

app = QApplication(sys.argv)
window = ChecksumWindow()
window.show()
sys.exit(app.exec_())
```

### Advanced Migration Example

#### Enhanced Threading with Cancellation
```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from file_utilities_2.gui.check_sum_standardized import EnhancedChecksumThread

class AdvancedChecksumWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Checksum Tool")
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")
        self.eta_label = QLabel("")
        self.calculate_btn = QPushButton("Calculate")
        self.cancel_btn = QPushButton("Cancel")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.eta_label)
        layout.addWidget(self.calculate_btn)
        layout.addWidget(self.cancel_btn)
        
        # Connect signals
        self.calculate_btn.clicked.connect(self.start_calculation)
        self.cancel_btn.clicked.connect(self.cancel_calculation)
        
        self.checksum_thread = None
        
    def start_calculation(self):
        """Start checksum calculation with enhanced progress tracking."""
        file_path = '/path/to/large/file.bin'  # Example file
        
        self.checksum_thread = EnhancedChecksumThread(file_path, 'sha256')
        
        # Connect all enhanced signals
        self.checksum_thread.progress_percentage.connect(self.progress_bar.setValue)
        self.checksum_thread.progress_message.connect(self.status_label.setText)
        self.checksum_thread.milestone_reached.connect(self.on_milestone)
        self.checksum_thread.time_estimate.connect(self.eta_label.setText)
        self.checksum_thread.result_ready.connect(self.on_result)
        self.checksum_thread.error_occurred.connect(self.on_error)
        self.checksum_thread.finished.connect(self.on_finished)
        
        self.calculate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.checksum_thread.start()
    
    def cancel_calculation(self):
        """Cancel the current calculation."""
        if self.checksum_thread and self.checksum_thread.isRunning():
            self.checksum_thread.cancel()
            self.status_label.setText("Cancelling...")
    
    def on_milestone(self, milestone, percentage):
        """Handle milestone updates."""
        print(f"Milestone: {milestone} ({percentage}%)")
    
    def on_result(self, result):
        """Handle calculation results."""
        checksum = result.get('checksum', 'N/A')
        print(f"Checksum: {checksum}")
        self.status_label.setText(f"Complete: {checksum}")
    
    def on_error(self, error):
        """Handle errors."""
        print(f"Error: {error}")
        self.status_label.setText(f"Error: {error}")
    
    def on_finished(self):
        """Handle completion."""
        self.calculate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdvancedChecksumWindow()
    window.show()
    sys.exit(app.exec_())
```

## Summary

The file_utilities_2 migration provides significant enhancements while maintaining complete backward compatibility:

### Key Benefits
- ✅ **Enhanced Progress Tracking**: Real-time percentage, status messages, milestones, and ETA
- ✅ **Modern PyQt5 Architecture**: Updated patterns and best practices
- ✅ **Improved User Experience**: Cancellation support and responsive UI
- ✅ **Comprehensive Testing**: Extensive test coverage with PyQt5 compatibility tests
- ✅ **Quality Assurance**: Enterprise-grade QA framework and standards

### Migration Path
- **No Changes Required**: Existing code continues to work unchanged
- **Incremental Enhancement**: New features can be adopted gradually
- **Full Migration**: Complete migration to enhanced APIs for maximum benefit

### Compatibility Guarantee
- **100% Backward Compatibility**: All existing APIs preserved
- **Additive Enhancements**: New features don't break existing functionality
- **Clear Migration Path**: Step-by-step guidance for adopting new features

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-26  
**Related Documents**: [MIGRATION_TECHNICAL_DOCUMENTATION.md](MIGRATION_TECHNICAL_DOCUMENTATION.md)