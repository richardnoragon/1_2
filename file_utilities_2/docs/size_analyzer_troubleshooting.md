# Size Analyzer Troubleshooting Guide

## Table of Contents

1. [Common Issues and Solutions](#common-issues-and-solutions)
2. [Installation Problems](#installation-problems)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)
5. [GUI Problems](#gui-problems)
6. [Hub Integration Issues](#hub-integration-issues)
7. [Configuration Problems](#configuration-problems)
8. [Export and Import Issues](#export-and-import-issues)
9. [Platform-Specific Issues](#platform-specific-issues)
10. [Debugging Techniques](#debugging-techniques)
11. [Log Analysis](#log-analysis)
12. [Getting Help](#getting-help)

---

## Common Issues and Solutions

### Quick Diagnosis Checklist

Before diving into specific troubleshooting, run through this quick checklist:

- [ ] **Python Version**: Ensure Python 3.7+ is installed
- [ ] **Dependencies**: All required packages are installed
- [ ] **Permissions**: User has read access to target directories
- [ ] **Disk Space**: Sufficient disk space for analysis and temporary files
- [ ] **Memory**: Adequate RAM for the dataset size
- [ ] **PyQt5**: GUI framework is properly installed and configured

### Most Common Issues

#### 1. Application Won't Start
**Symptoms**: Application fails to launch or crashes immediately

**Quick Solutions**:
```bash
# Check Python version
python --version

# Verify PyQt5 installation
python -c "import PyQt5; print('PyQt5 OK')"

# Check all dependencies
pip list | grep -E "(PyQt5|pathlib|typing)"

# Reinstall if needed
pip uninstall PyQt5
pip install PyQt5>=5.15.0
```

#### 2. Analysis Hangs or Freezes
**Symptoms**: Analysis starts but never completes

**Quick Solutions**:
- Check if analyzing a very large directory (>100GB)
- Verify sufficient memory is available
- Look for circular symbolic links
- Check for permission issues on subdirectories

#### 3. Incorrect Results
**Symptoms**: File counts or sizes don't match expectations

**Quick Solutions**:
- Verify directory path is correct
- Check for hidden files being included/excluded
- Ensure no files are being modified during analysis
- Verify symbolic link handling settings

---

## Installation Problems

### PyQt5 Installation Issues

#### Problem: PyQt5 Installation Fails
```bash
ERROR: Failed building wheel for PyQt5
```

**Solution 1: Use Pre-compiled Wheels**
```bash
# Update pip first
pip install --upgrade pip

# Install from PyPI with pre-compiled wheels
pip install PyQt5>=5.15.0 --only-binary=all

# If still failing, try specific version
pip install PyQt5==5.15.7
```

**Solution 2: Platform-Specific Installation**
```bash
# Windows
pip install PyQt5 --find-links https://download.qt.io/snapshots/ci/pyqt/5.15/

# macOS with Homebrew
brew install pyqt5
pip install PyQt5

# Ubuntu/Debian
sudo apt-get install python3-pyqt5
pip install PyQt5
```

#### Problem: Missing Qt Platform Plugin
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**Solution**:
```bash
# Linux
sudo apt-get install libxcb-xinerama0 libxcb-cursor0

# Set Qt platform if needed
export QT_QPA_PLATFORM=xcb

# Alternative: Use offscreen platform for headless
export QT_QPA_PLATFORM=offscreen
```

### Dependency Conflicts

#### Problem: Version Conflicts
```bash
ERROR: pip's dependency resolver does not currently consider all the packages
```

**Solution**:
```bash
# Create clean virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # Linux/macOS
# or
fresh_env\Scripts\activate  # Windows

# Install with specific versions
pip install PyQt5==5.15.7
pip install -r requirements.txt
```

### Permission Issues

#### Problem: Permission Denied During Installation
```bash
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Install for user only
pip install --user PyQt5

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install PyQt5
```

---

## Runtime Errors

### File System Errors

#### Problem: FileNotFoundError
```python
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/directory'
```

**Diagnosis**:
```python
import os
from pathlib import Path

def diagnose_path_issue(path):
    """Diagnose path-related issues."""
    print(f"Checking path: {path}")
    print(f"Path exists: {os.path.exists(path)}")
    print(f"Is directory: {os.path.isdir(path)}")
    print(f"Is readable: {os.access(path, os.R_OK)}")
    print(f"Absolute path: {os.path.abspath(path)}")
    
    # Check parent directory
    parent = Path(path).parent
    print(f"Parent exists: {parent.exists()}")
    print(f"Parent readable: {os.access(parent, os.R_OK)}")
```

**Solutions**:
1. **Verify Path**: Ensure the path is correct and exists
2. **Check Permissions**: Verify read permissions on directory
3. **Handle Spaces**: Ensure paths with spaces are properly quoted
4. **Network Paths**: For network drives, ensure they're mounted

#### Problem: PermissionError
```python
PermissionError: [Errno 13] Permission denied: '/restricted/directory'
```

**Solutions**:
```bash
# Check current permissions
ls -la /path/to/directory

# Grant read permissions (if you own the directory)
chmod +r /path/to/directory

# Run with elevated permissions (not recommended)
sudo python size_analyzer.py

# Better: Copy files to accessible location
cp -r /restricted/directory ~/accessible_copy
```

### Memory Errors

#### Problem: MemoryError or Out of Memory
```python
MemoryError: Unable to allocate array
```

**Diagnosis**:
```python
import psutil

def check_memory_usage():
    """Check current memory usage."""
    memory = psutil.virtual_memory()
    print(f"Total memory: {memory.total / 1024**3:.2f} GB")
    print(f"Available memory: {memory.available / 1024**3:.2f} GB")
    print(f"Memory usage: {memory.percent}%")
    
    process = psutil.Process()
    print(f"Process memory: {process.memory_info().rss / 1024**2:.2f} MB")
```

**Solutions**:
1. **Increase Virtual Memory**: Configure larger swap file
2. **Process in Chunks**: Analyze subdirectories separately
3. **Reduce Scope**: Exclude large subdirectories temporarily
4. **Use 64-bit Python**: Ensure 64-bit Python for large datasets

```python
# Memory-efficient analysis
def analyze_large_directory_safe(self, path, max_memory_mb=500):
    """Analyze large directory with memory limits."""
    import psutil
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024**2
    
    for root, dirs, files in os.walk(path):
        # Check memory usage periodically
        current_memory = process.memory_info().rss / 1024**2
        memory_used = current_memory - initial_memory
        
        if memory_used > max_memory_mb:
            print(f"Memory limit reached: {memory_used:.2f}MB")
            break
        
        # Process files in current directory
        for filename in files:
            # Process individual file
            pass
```

### Threading Issues

#### Problem: GUI Freezes During Analysis
**Symptoms**: Interface becomes unresponsive during long operations

**Solution**:
```python
from PyQt5.QtCore import QThread, pyqtSignal

class AnalysisWorker(QThread):
    """Worker thread for background analysis."""
    
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path
        self.should_stop = False
    
    def run(self):
        """Run analysis in background thread."""
        try:
            analyzer = SizeAnalyzer()
            analyzer.set_progress_callback(self._progress_callback)
            
            results = analyzer.analyze_directory(self.directory_path)
            
            if not self.should_stop:
                self.finished.emit(results)
                
        except Exception as e:
            self.error.emit(str(e))
    
    def _progress_callback(self, percentage, message):
        """Handle progress updates."""
        if not self.should_stop:
            self.progress.emit(percentage, message)
    
    def stop(self):
        """Stop the analysis."""
        self.should_stop = True
```

---

## Performance Issues

### Slow Analysis Performance

#### Problem: Analysis Takes Too Long
**Symptoms**: Analysis of moderate-sized directories takes excessive time

**Diagnosis**:
```python
import time
import cProfile

def profile_analysis(directory_path):
    """Profile analysis performance."""
    profiler = cProfile.Profile()
    
    start_time = time.time()
    profiler.enable()
    
    analyzer = SizeAnalyzer()
    results = analyzer.analyze_directory(directory_path)
    
    profiler.disable()
    end_time = time.time()
    
    print(f"Analysis took: {end_time - start_time:.2f} seconds")
    print(f"Files processed: {results['file_count']}")
    print(f"Rate: {results['file_count'] / (end_time - start_time):.2f} files/sec")
    
    # Print top time-consuming functions
    profiler.print_stats(sort='cumulative')
```

**Solutions**:

1. **Optimize File System Access**:
```python
def optimized_file_scan(self, directory_path):
    """Optimized file scanning with reduced system calls."""
    files = []
    
    # Use os.scandir for better performance
    with os.scandir(directory_path) as entries:
        for entry in entries:
            if entry.is_file(follow_symlinks=False):
                stat_info = entry.stat(follow_symlinks=False)
                files.append({
                    'name': entry.name,
                    'path': entry.path,
                    'size': stat_info.st_size,
                    'modified': stat_info.st_mtime
                })
    
    return files
```

2. **Implement Caching**:
```python
from functools import lru_cache

class CachedSizeAnalyzer:
    """Size analyzer with caching for repeated operations."""
    
    @lru_cache(maxsize=1000)
    def get_file_info(self, file_path, mtime):
        """Cache file information based on modification time."""
        stat_info = os.stat(file_path)
        return {
            'size': stat_info.st_size,
            'modified': stat_info.st_mtime
        }
```

3. **Parallel Processing**:
```python
import concurrent.futures
from multiprocessing import cpu_count

def parallel_directory_analysis(self, directory_path):
    """Analyze directory using parallel processing."""
    subdirs = [d for d in os.listdir(directory_path) 
              if os.path.isdir(os.path.join(directory_path, d))]
    
    max_workers = min(cpu_count(), len(subdirs))
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(self._analyze_single_directory, 
                          os.path.join(directory_path, subdir)): subdir
            for subdir in subdirs
        }
        
        results = {}
        for future in concurrent.futures.as_completed(futures):
            subdir = futures[future]
            try:
                results[subdir] = future.result()
            except Exception as e:
                print(f"Error analyzing {subdir}: {e}")
    
    return results
```

### High Memory Usage

#### Problem: Excessive Memory Consumption
**Symptoms**: Application uses more memory than expected

**Diagnosis**:
```python
import tracemalloc
import gc

def diagnose_memory_usage():
    """Diagnose memory usage patterns."""
    # Start tracing
    tracemalloc.start()
    
    # Run analysis
    analyzer = SizeAnalyzer()
    results = analyzer.analyze_directory("/test/directory")
    
    # Get memory statistics
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024**2:.2f} MB")
    print(f"Peak memory usage: {peak / 1024**2:.2f} MB")
    
    # Get top memory consumers
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("Top 10 memory consumers:")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()
```

**Solutions**:

1. **Use Generators Instead of Lists**:
```python
def memory_efficient_file_scan(self, directory_path):
    """Memory-efficient file scanning using generators."""
    def file_generator():
        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    stat_info = os.stat(file_path)
                    yield {
                        'name': filename,
                        'path': file_path,
                        'size': stat_info.st_size
                    }
                except OSError:
                    continue
    
    return file_generator()
```

2. **Process Data in Chunks**:
```python
def chunked_analysis(self, directory_path, chunk_size=1000):
    """Process files in chunks to limit memory usage."""
    chunk = []
    total_size = 0
    file_count = 0
    
    for file_info in self.memory_efficient_file_scan(directory_path):
        chunk.append(file_info)
        
        if len(chunk) >= chunk_size:
            # Process chunk
            chunk_stats = self._process_chunk(chunk)
            total_size += chunk_stats['total_size']
            file_count += chunk_stats['file_count']
            
            # Clear chunk to free memory
            chunk.clear()
            gc.collect()  # Force garbage collection
    
    # Process remaining files
    if chunk:
        chunk_stats = self._process_chunk(chunk)
        total_size += chunk_stats['total_size']
        file_count += chunk_stats['file_count']
    
    return {'total_size': total_size, 'file_count': file_count}
```

---

## GUI Problems

### Display Issues

#### Problem: GUI Elements Not Displaying Correctly
**Symptoms**: Missing buttons, incorrect layouts, or rendering issues

**Diagnosis**:
```python
def diagnose_gui_issues():
    """Diagnose GUI-related issues."""
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QT_VERSION_STR
    from PyQt5.Qt import PYQT_VERSION_STR
    
    print(f"Qt Version: {QT_VERSION_STR}")
    print(f"PyQt Version: {PYQT_VERSION_STR}")
    
    app = QApplication.instance()
    if app:
        print(f"Application style: {app.style().objectName()}")
        print(f"Available styles: {QApplication.instance().style().objectName()}")
```

**Solutions**:

1. **Force Style Refresh**:
```python
def fix_gui_display(self):
    """Fix GUI display issues."""
    # Force style refresh
    self.setStyleSheet("")
    self.setStyleSheet(self.styleSheet())
    
    # Update layout
    self.layout().update()
    self.update()
    self.repaint()
```

2. **Check Theme Compatibility**:
```python
def validate_theme_compatibility(self):
    """Validate theme compatibility."""
    try:
        from file_utilities_2.gui.themes import ThemeManager
        theme_manager = ThemeManager()
        
        # Test theme loading
        theme_manager.apply_theme("default")
        print("Theme loading successful")
        
    except Exception as e:
        print(f"Theme loading failed: {e}")
        # Fall back to system theme
        self.setStyleSheet("")
```

#### Problem: Progress Bar Not Updating
**Symptoms**: Progress bar remains static during analysis

**Solution**:
```python
from PyQt5.QtCore import QTimer

class FixedProgressBar:
    """Progress bar with forced updates."""
    
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._force_update)
        self.update_timer.start(100)  # Update every 100ms
    
    def set_progress(self, value):
        """Set progress with forced update."""
        self.progress_bar.setValue(value)
        self._force_update()
    
    def _force_update(self):
        """Force GUI update."""
        self.progress_bar.update()
        self.progress_bar.repaint()
        QApplication.processEvents()
```

### Signal/Slot Issues

#### Problem: Signals Not Being Emitted or Received
**Symptoms**: GUI doesn't respond to events or updates

**Diagnosis**:
```python
def debug_signals(self):
    """Debug signal/slot connections."""
    from PyQt5.QtCore import QObject
    
    # Check if signals are connected
    analyzer = self.analyzer
    
    # List all connections
    print("Signal connections:")
    for signal_name in dir(analyzer):
        signal = getattr(analyzer, signal_name)
        if hasattr(signal, 'connect'):
            print(f"  {signal_name}: {signal}")
    
    # Test signal emission
    def test_slot(value):
        print(f"Signal received: {value}")
    
    analyzer.progress_percentage.connect(test_slot)
    analyzer.progress_percentage.emit(50)  # Test emission
```

**Solutions**:

1. **Verify Signal Connections**:
```python
def setup_signals_safely(self):
    """Set up signal connections with error handling."""
    try:
        # Disconnect existing connections
        self.analyzer.progress_percentage.disconnect()
        self.analyzer.analysis_complete.disconnect()
        
        # Reconnect with error handling
        self.analyzer.progress_percentage.connect(
            self.update_progress, 
            Qt.QueuedConnection
        )
        self.analyzer.analysis_complete.connect(
            self.on_analysis_complete,
            Qt.QueuedConnection
        )
        
        print("Signals connected successfully")
        
    except Exception as e:
        print(f"Signal connection failed: {e}")
```

2. **Use Queued Connections for Thread Safety**:
```python
from PyQt5.QtCore import Qt

# Use queued connections for cross-thread signals
self.worker.progress.connect(
    self.update_progress, 
    Qt.QueuedConnection
)
```

---

## Hub Integration Issues

### Connection Problems

#### Problem: Cannot Connect to Hub
**Symptoms**: Hub integration fails to establish connection

**Diagnosis**:
```python
def diagnose_hub_connection(self):
    """Diagnose hub connection issues."""
    try:
        from file_utilities_2.integration.hub_connector import HubConnector
        
        connector = HubConnector()
        
        # Test basic connectivity
        if hasattr(connector, 'test_connection'):
            result = connector.test_connection()
            print(f"Hub connection test: {result}")
        
        # Check hub instance
        if self.hub_instance:
            print(f"Hub instance available: {type(self.hub_instance)}")
        else:
            print("No hub instance available")
            
    except ImportError as e:
        print(f"Hub connector import failed: {e}")
    except Exception as e:
        print(f"Hub connection error: {e}")
```

**Solutions**:

1. **Implement Connection Retry**:
```python
import time

def connect_to_hub_with_retry(self, max_retries=3, delay=1.0):
    """Connect to hub with retry logic."""
    for attempt in range(max_retries):
        try:
            success = self.hub_connector.connect()
            if success:
                print(f"Connected to hub on attempt {attempt + 1}")
                return True
                
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
    
    print("Failed to connect to hub after all retries")
    return False
```

2. **Graceful Degradation**:
```python
def initialize_with_fallback(self):
    """Initialize with hub fallback."""
    try:
        # Try hub integration
        self.hub_connector = HubConnector()
        self.hub_available = self.hub_connector.connect()
        
        if self.hub_available:
            print("Hub integration active")
        else:
            print("Hub not available, running in standalone mode")
            
    except Exception as e:
        print(f"Hub integration failed: {e}")
        self.hub_available = False
        print("Running in standalone mode")
```

### Message Passing Issues

#### Problem: Messages Not Being Sent/Received
**Symptoms**: Hub communication appears to work but messages are lost

**Diagnosis**:
```python
def test_hub_messaging(self):
    """Test hub messaging functionality."""
    if not self.hub_available:
        print("Hub not available for testing")
        return
    
    # Test message sending
    test_message = {
        'type': 'test',
        'timestamp': time.time(),
        'data': 'test_data'
    }
    
    try:
        result = self.hub_connector.send_message(test_message)
        print(f"Message send result: {result}")
        
        # Test message receiving
        received = self.hub_connector.receive_messages()
        print(f"Received messages: {len(received)}")
        
    except Exception as e:
        print(f"Messaging test failed: {e}")
```

**Solutions**:

1. **Add Message Validation**:
```python
def send_message_safely(self, message):
    """Send message with validation and error handling."""
    # Validate message format
    required_fields = ['type', 'timestamp', 'source']
    for field in required_fields:
        if field not in message:
            raise ValueError(f"Missing required field: {field}")
    
    # Add metadata
    message['source'] = 'size_analyzer'
    message['timestamp'] = time.time()
    
    try:
        result = self.hub_connector.send_message(message)
        if not result:
            print("Message sending failed")
        return result
        
    except Exception as e:
        print(f"Message send error: {e}")
        return False
```

2. **Implement Message Queue**:
```python
from queue import Queue
import threading

class ReliableHubConnector:
    """Hub connector with reliable messaging."""
    
    def __init__(self):
        self.message_queue = Queue()
        self.sender_thread = threading.Thread(target=self._message_sender)
        self.sender_thread.daemon = True
        self.sender_thread.start()
    
    def queue_message(self, message):
        """Queue message for reliable delivery."""
        self.message_queue.put(message)
    
    def _message_sender(self):
        """Background thread for message sending."""
        while True:
            try:
                message = self.message_queue.get(timeout=1)
                self._send_with_retry(message)
                self.message_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Message sender error: {e}")
    
    def _send_with_retry(self, message, max_retries=3):
        """Send message with retry logic."""
        for attempt in range(max_retries):
            try:
                if self.hub_connector.send_message(message):
                    return True
                    
            except Exception as e:
                print(f"Send attempt {attempt + 1} failed: {e}")
                time.sleep(0.5 * (attempt + 1))
        
        print(f"Failed to send message after {max_retries} attempts")
        return False
```

---

## Configuration Problems

### Settings Not Persisting

#### Problem: Configuration Changes Don't Save
**Symptoms**: Settings revert to defaults after restart

**Diagnosis**:
```python
def diagnose_config_issues(self):
    """Diagnose configuration persistence issues."""
    from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
    
    config = SizeAnalyzerConfig()
    
    # Check config file location
    config_path = config.get_config_file_path()
    print(f"Config file path: {config_path}")
    print(f"Config file exists: {os.path.exists(config_path)}")
    
    # Check permissions
    config_dir = os.path.dirname(config_path)
    print(f"Config directory writable: {os.access(config_dir, os.W_OK)}")
    
    # Test write operation
    try:
        config.set_setting('test', 'test_key', 'test_value')
        config.save_settings()
        print("Config write test: SUCCESS")
        
        # Test read operation
        config2 = SizeAnalyzerConfig()
        value = config2.get_setting('test', 'test_key')
        print(f"Config read test: {value}")
        
    except Exception as e:
        print(f"Config test failed: {e}")
```

**Solutions**:

1. **Ensure Directory Exists**:
```python
def ensure_config_directory(self):
    """Ensure configuration directory exists."""
    config_dir = os.path.dirname(self.config_file_path)
    
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, exist_ok=True)
            print(f"Created config directory: {config_dir}")
        except OSError as e:
            print(f"Failed to create config directory: {e}")
            # Fall back to temp directory
            import tempfile
            self.config_file_path = os.path.join(
                tempfile.gettempdir(), 
                'size_analyzer_config.json'
            )
```

2. **Atomic File Writing**:
```python
import tempfile
import shutil

def save_settings_atomic(self):
    """Save settings using atomic write operation."""
    config_data = self._get_config_data()
    
    # Write to temporary file first
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', 
            dir=os.path.dirname(self.config_file_path),
            delete=False
        ) as temp_file:
            json.dump(config_data, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        # Atomic move to final location
        shutil.move(temp_file_path, self.config_file_path)
        print("Configuration saved successfully")
        
    except Exception as e:
        print(f"Failed to save configuration: {e}")
        # Clean up temp file if it exists
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
```

### Invalid Configuration Values

#### Problem: Configuration Contains Invalid Values
**Symptoms**: Application behaves unexpectedly due to bad config

**Solution**:
```python
def validate_and_fix_config(self):
    """Validate configuration and fix invalid values."""
    config_schema = {
        'analysis': {
            'default_top_files_count': {'type': int, 'min': 1, 'max': 1000, 'default': 10},
            'include_hidden_files': {'type': bool, 'default': False},
            'follow_symlinks': {'type': bool, 'default': False}
        },
        'performance': {
            'max_memory_usage_mb': {'type': int, 'min': 100, 'max': 8192, 'default': 512},
            'worker_thread_count': {'type': int, 'min': 1, 'max': 16, 'default': 4}
        }
    }
    
    fixed_count = 0
    
    for section, settings in config_schema.items():
        for key, constraints in settings.items():
            current_value = self.get_setting(section, key)
            
            # Validate type
            if not isinstance(current_value, constraints['type']):
                print(f"Invalid type for {section}.{key}: {type(current_value)}")
                self.set_setting(section, key, constraints['default'])
                fixed_count += 1
                continue
            
            # Validate range for numeric values
            if constraints['type'] in (int, float):
                if 'min' in constraints and current_value < constraints['min']:
                    print(f"Value too low for {section}.{key}: {current_value}")
                    self.set_setting(section, key, constraints['min'])
                    fixed_count += 1
                elif 'max' in constraints and current_value > constraints['max']:
                    print(f"Value too high for {section}.{key}: {current_value}")
                    self.set_setting(section, key, constraints['max'])
                    fixed_count += 1
    
    if fixed_count > 0:
        print(f"Fixed {fixed_count} configuration issues")
        self.save_settings()
```

---

## Export and Import Issues

### Export Failures

#### Problem: Export Operation Fails
**Symptoms**: Export dialog appears but no file is created

**Diagnosis**:
```python
def diagnose_export_issues(self, export_path, data):
    """Diagnose export-related issues."""
    # Check export path
    export_dir = os.path.dirname(export_path)
    print(f"Export directory: {export_dir}")
    print(f"Directory exists: {os.path.exists(export_dir)}")
    print(f"Directory writable: {os.access(export_dir, os.W_OK)}")
    
    # Check data validity
    print(f"Data type: {type(data)}")
    print(f"Data size: {len(str(data))} characters")
    
    # Check available disk space
    import shutil
    free_space = shutil.disk_usage(export_dir).free
    print(f"Free disk space: {free_space / 1024**2:.2f} MB")
    
    # Test write permissions
    test_file = os.path.join(export_dir, 'test_write.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.unlink(test_file)
        print("Write permission test: PASSED")
    except Exception as e:
        print(f"Write permission test: FAILED - {e}")
```

**Solutions**:

1. **Robust Export Function**:
```python
def export_data_robust(self, data, file_path, format='json'):
    """Export data with comprehensive error handling."""
    try:
        # Ensure directory exists
        export_dir = os.path.dirname(file_path)
        if not