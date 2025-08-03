# Size Analyzer Testing and Validation Documentation

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Test Suite Architecture](#test-suite-architecture)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Test Scenarios](#test-scenarios)
6. [Performance Testing](#performance-testing)
7. [Integration Testing](#integration-testing)
8. [Validation Procedures](#validation-procedures)
9. [Continuous Integration](#continuous-integration)
10. [Test Data Management](#test-data-management)
11. [Quality Metrics](#quality-metrics)
12. [Troubleshooting Tests](#troubleshooting-tests)

---

## Testing Overview

The Size Analyzer testing suite provides comprehensive validation of all migration aspects, ensuring production readiness through multiple testing levels and methodologies.

### Testing Philosophy

- **Comprehensive Coverage**: >95% code coverage for critical components
- **Multiple Test Levels**: Unit, integration, end-to-end, and performance tests
- **Automated Validation**: Continuous integration with automated test execution
- **Real-World Scenarios**: Testing with realistic data sets and usage patterns
- **Performance Assurance**: Benchmark testing and scalability validation
- **Quality Gates**: Strict quality criteria for production deployment

### Testing Objectives

1. **Functional Validation**: Ensure all features work as specified
2. **Performance Verification**: Meet established performance benchmarks
3. **Integration Validation**: Verify seamless component interaction
4. **Regression Prevention**: Detect breaking changes early
5. **Quality Assurance**: Maintain high code quality standards
6. **Production Readiness**: Validate deployment compatibility

---

## Test Suite Architecture

### Test Module Organization

```
file_utilities_2/tests/
├── conftest.py                          # Test configuration and fixtures
├── test_size_analyzer_core.py           # Core logic tests
├── test_size_analyzer_gui.py            # GUI component tests
├── test_size_analyzer_integration.py    # Hub integration tests
├── test_size_analyzer_config.py         # Configuration tests
├── test_size_analyzer_imports.py        # Import compatibility tests
├── test_size_analyzer_performance.py    # Performance tests
└── test_data/                          # Test data files
    ├── small_dataset/
    ├── medium_dataset/
    └── large_dataset/
```

### Test Categories

#### 1. Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Core logic, configuration, utilities
- **Coverage Target**: >98% for core components

#### 2. Integration Tests
- **Purpose**: Test component interactions
- **Scope**: GUI-core integration, hub communication
- **Coverage Target**: >95% for integration points

#### 3. End-to-End Tests
- **Purpose**: Test complete user workflows
- **Scope**: Full analysis workflows, export functionality
- **Coverage Target**: 100% for critical user paths

#### 4. Performance Tests
- **Purpose**: Validate performance characteristics
- **Scope**: Analysis speed, memory usage, scalability
- **Coverage Target**: All performance benchmarks

#### 5. Compatibility Tests
- **Purpose**: Ensure cross-platform compatibility
- **Scope**: Python versions, operating systems
- **Coverage Target**: All supported platforms

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Ensure test environment is set up
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Basic Test Execution

#### Run All Tests
```bash
# Run complete test suite
pytest tests/

# Run with verbose output
pytest -v tests/

# Run with coverage report
pytest --cov=file_utilities_2 --cov-report=html tests/
```

#### Run Specific Test Categories
```bash
# Core logic tests only
pytest tests/test_size_analyzer_core.py

# GUI tests only
pytest tests/test_size_analyzer_gui.py

# Integration tests only
pytest tests/test_size_analyzer_integration.py

# Performance tests only
pytest tests/test_size_analyzer_performance.py
```

#### Run Tests by Markers
```bash
# Run only fast tests
pytest -m "not slow" tests/

# Run only integration tests
pytest -m "integration" tests/

# Run only performance tests
pytest -m "performance" tests/

# Run only GUI tests
pytest -m "gui" tests/
```

### Advanced Test Options

#### Parallel Test Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/

# Run with specific number of workers
pytest -n 4 tests/
```

#### Test Filtering
```bash
# Run tests matching pattern
pytest -k "test_analyze_directory" tests/

# Run failed tests only
pytest --lf tests/

# Run tests that failed in last run
pytest --ff tests/

# Stop on first failure
pytest -x tests/
```

#### Coverage Analysis
```bash
# Generate HTML coverage report
pytest --cov=file_utilities_2 --cov-report=html tests/

# Generate XML coverage report (for CI)
pytest --cov=file_utilities_2 --cov-report=xml tests/

# Show missing lines
pytest --cov=file_utilities_2 --cov-report=term-missing tests/
```

---

## Test Categories

### Core Logic Tests (`test_size_analyzer_core.py`)

#### Test Classes and Methods

```python
class TestSizeAnalyzer:
    """Test core SizeAnalyzer functionality."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        
    def test_analyze_directory_basic(self):
        """Test basic directory analysis."""
        
    def test_analyze_directory_with_filters(self):
        """Test analysis with file filters."""
        
    def test_file_type_analysis(self):
        """Test file type categorization."""
        
    def test_largest_files_identification(self):
        """Test largest files detection."""
        
    def test_directory_tree_generation(self):
        """Test directory tree structure."""
        
    def test_size_formatting(self):
        """Test human-readable size formatting."""
        
    def test_export_functionality(self):
        """Test JSON export capabilities."""
        
    def test_progress_tracking(self):
        """Test progress signal emissions."""
        
    def test_cancellation_support(self):
        """Test operation cancellation."""
        
    def test_error_handling(self):
        """Test error scenarios and exceptions."""
        
    def test_performance_metrics(self):
        """Test performance metrics collection."""

class TestSizeAnalyzerWorker:
    """Test worker thread functionality."""
    
    def test_worker_initialization(self):
        """Test worker thread setup."""
        
    def test_worker_execution(self):
        """Test analysis execution in worker."""
        
    def test_worker_cancellation(self):
        """Test worker thread cancellation."""
        
    def test_worker_error_handling(self):
        """Test worker error scenarios."""
```

#### Example Test Implementation

```python
def test_analyze_directory_basic(self, test_directory, size_analyzer):
    """Test basic directory analysis functionality."""
    # Arrange
    expected_file_count = 10
    expected_min_size = 1000
    
    # Act
    results = size_analyzer.analyze_directory(str(test_directory))
    
    # Assert
    assert results['path'] == str(test_directory)
    assert results['file_count'] == expected_file_count
    assert results['total_size'] >= expected_min_size
    assert 'files' in results
    assert 'file_types' in results
    assert 'largest_files' in results
    assert 'directory_tree' in results
    assert 'performance_metrics' in results

def test_size_formatting(self, size_analyzer):
    """Test human-readable size formatting."""
    test_cases = [
        (0, "0.0 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1048576, "1.0 MB"),
        (1073741824, "1.0 GB"),
        (1099511627776, "1.0 TB")
    ]
    
    for size_bytes, expected in test_cases:
        result = size_analyzer.format_size(size_bytes)
        assert result == expected, f"Expected {expected}, got {result} for {size_bytes} bytes"
```

### GUI Tests (`test_size_analyzer_gui.py`)

#### Test Classes and Methods

```python
class TestSizeAnalyzerGUI:
    """Test GUI component functionality."""
    
    def test_gui_initialization(self):
        """Test GUI component initialization."""
        
    def test_theme_integration(self):
        """Test theme manager integration."""
        
    def test_directory_selection(self):
        """Test directory browsing functionality."""
        
    def test_analysis_workflow(self):
        """Test complete analysis workflow."""
        
    def test_progress_visualization(self):
        """Test progress bar and status updates."""
        
    def test_results_display(self):
        """Test results presentation."""
        
    def test_export_functionality(self):
        """Test export dialog and functionality."""
        
    def test_signal_connections(self):
        """Test signal/slot connections."""
        
    def test_error_handling_ui(self):
        """Test error dialog presentation."""
        
    def test_window_management(self):
        """Test window lifecycle management."""

class TestHubIntegration:
    """Test hub integration in GUI."""
    
    def test_hub_registration(self):
        """Test tool registration with hub."""
        
    def test_hub_communication(self):
        """Test bidirectional hub communication."""
        
    def test_resource_coordination(self):
        """Test resource request handling."""
        
    def test_event_broadcasting(self):
        """Test event broadcasting to hub."""
```

#### Example GUI Test Implementation

```python
def test_analysis_workflow(self, qtbot, size_analyzer_gui, test_directory):
    """Test complete analysis workflow."""
    # Arrange
    gui = size_analyzer_gui
    gui.selected_directory = str(test_directory)
    gui.directory_line_edit.setText(str(test_directory))
    
    # Track signals
    analysis_complete_spy = qtbot.QSignalSpy(gui.analyzer.analysis_complete)
    
    # Act
    qtbot.mouseClick(gui.analyze_button, Qt.LeftButton)
    
    # Wait for analysis completion (with timeout)
    qtbot.waitSignal(gui.analyzer.analysis_complete, timeout=30000)
    
    # Assert
    assert len(analysis_complete_spy) == 1
    assert gui.current_analysis is not None
    assert gui.export_button.isEnabled()
    assert gui.analyze_button.isEnabled()
```

### Integration Tests (`test_size_analyzer_integration.py`)

#### Test Classes and Methods

```python
class TestHubConnector:
    """Test hub connector functionality."""
    
    def test_hub_connector_initialization(self):
        """Test hub connector setup."""
        
    def test_tool_registration(self):
        """Test tool registration process."""
        
    def test_message_communication(self):
        """Test message sending and receiving."""
        
    def test_progress_reporting(self):
        """Test progress reporting to hub."""
        
    def test_event_broadcasting(self):
        """Test event broadcasting."""
        
    def test_resource_coordination(self):
        """Test resource request handling."""
        
    def test_error_recovery(self):
        """Test error handling and recovery."""

class TestEndToEndIntegration:
    """Test complete integration scenarios."""
    
    def test_full_analysis_with_hub(self):
        """Test complete analysis with hub integration."""
        
    def test_concurrent_operations(self):
        """Test multiple simultaneous operations."""
        
    def test_resource_contention(self):
        """Test resource sharing scenarios."""
```

### Performance Tests (`test_size_analyzer_performance.py`)

#### Test Classes and Methods

```python
class TestPerformanceBenchmarks:
    """Test performance against established benchmarks."""
    
    def test_small_directory_performance(self):
        """Test performance with small datasets."""
        
    def test_medium_directory_performance(self):
        """Test performance with medium datasets."""
        
    def test_large_directory_performance(self):
        """Test performance with large datasets."""
        
    def test_memory_usage(self):
        """Test memory usage patterns."""
        
    def test_scalability(self):
        """Test scalability with increasing dataset sizes."""

class TestResourceManagement:
    """Test resource usage and management."""
    
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations."""
        
    def test_cpu_usage_monitoring(self):
        """Test CPU usage patterns."""
        
    def test_file_handle_management(self):
        """Test file handle cleanup."""
```

#### Example Performance Test

```python
@pytest.mark.performance
def test_large_directory_performance(self, large_test_directory, size_analyzer):
    """Test performance with large directory (10,000+ files)."""
    import time
    import psutil
    
    # Arrange
    process = psutil.Process()
    start_memory = process.memory_info().rss
    
    # Act
    start_time = time.time()
    results = size_analyzer.analyze_directory(str(large_test_directory))
    end_time = time.time()
    
    end_memory = process.memory_info().rss
    
    # Assert performance benchmarks
    duration = end_time - start_time
    memory_used = (end_memory - start_memory) / 1024 / 1024  # MB
    files_per_second = results['file_count'] / duration
    
    assert duration < 30.0, f"Analysis took {duration:.2f}s, expected <30s"
    assert memory_used < 500, f"Memory usage {memory_used:.2f}MB, expected <500MB"
    assert files_per_second > 300, f"Processing rate {files_per_second:.2f} files/s, expected >300"
    
    # Verify results quality
    assert results['file_count'] > 10000
    assert results['total_size'] > 0
    assert len(results['largest_files']) > 0
```

---

## Test Scenarios

### Functional Test Scenarios

#### 1. Empty Directory Analysis
```python
def test_empty_directory_analysis(self, empty_directory, size_analyzer):
    """Test analysis of empty directory."""
    results = size_analyzer.analyze_directory(str(empty_directory))
    
    assert results['file_count'] == 0
    assert results['total_size'] == 0
    assert results['directory_count'] == 0
    assert len(results['files']) == 0
    assert len(results['largest_files']) == 0
```

#### 2. Single File Directory
```python
def test_single_file_directory(self, single_file_directory, size_analyzer):
    """Test analysis of directory with single file."""
    results = size_analyzer.analyze_directory(str(single_file_directory))
    
    assert results['file_count'] == 1
    assert results['total_size'] > 0
    assert len(results['files']) == 1
    assert len(results['largest_files']) == 1
```

#### 3. Deep Directory Structure
```python
def test_deep_directory_structure(self, deep_directory, size_analyzer):
    """Test analysis of deeply nested directory structure."""
    results = size_analyzer.analyze_directory(str(deep_directory))
    
    assert results['file_count'] > 0
    assert results['directory_count'] > 10  # Deep nesting
    assert 'directory_tree' in results
    assert results['directory_tree']['children']  # Has nested structure
```

#### 4. Mixed File Types
```python
def test_mixed_file_types(self, mixed_files_directory, size_analyzer):
    """Test analysis with various file types."""
    results = size_analyzer.analyze_directory(str(mixed_files_directory))
    
    file_types = results['file_types']
    assert '.txt' in file_types
    assert '.jpg' in file_types
    assert '.pdf' in file_types
    assert '.mp4' in file_types
    
    # Verify statistics
    for ext, stats in file_types.items():
        assert stats['count'] > 0
        assert stats['total_size'] > 0
        assert stats['average_size'] > 0
```

#### 5. Special Characters and Unicode
```python
def test_unicode_filenames(self, unicode_directory, size_analyzer):
    """Test handling of Unicode and special characters."""
    results = size_analyzer.analyze_directory(str(unicode_directory))
    
    assert results['file_count'] > 0
    
    # Check for files with special characters
    unicode_files = [f for f in results['files'] 
                    if any(ord(c) > 127 for c in f['name'])]
    assert len(unicode_files) > 0, "Should handle Unicode filenames"
```

### Error Handling Scenarios

#### 1. Non-existent Directory
```python
def test_nonexistent_directory(self, size_analyzer):
    """Test error handling for non-existent directory."""
    with pytest.raises(FileNotFoundError):
        size_analyzer.analyze_directory("/nonexistent/directory")
```

#### 2. Permission Denied
```python
@pytest.mark.skipif(os.name == 'nt', reason="Permission test not applicable on Windows")
def test_permission_denied(self, restricted_directory, size_analyzer):
    """Test handling of permission denied scenarios."""
    # Should not raise exception, but handle gracefully
    results = size_analyzer.analyze_directory(str(restricted_directory))
    assert isinstance(results, dict)
    # May have partial results
```

#### 3. Circular Symlinks
```python
@pytest.mark.skipif(os.name == 'nt', reason="Symlink test not applicable on Windows")
def test_circular_symlinks(self, circular_symlink_directory, size_analyzer):
    """Test handling of circular symbolic links."""
    # Should not cause infinite loop
    results = size_analyzer.analyze_directory(str(circular_symlink_directory))
    assert isinstance(results, dict)
    assert results['file_count'] >= 0
```

### Performance Scenarios

#### 1. Large File Count
```python
@pytest.mark.performance
@pytest.mark.slow
def test_large_file_count_performance(self, many_files_directory, size_analyzer):
    """Test performance with many small files."""
    import time
    
    start_time = time.time()
    results = size_analyzer.analyze_directory(str(many_files_directory))
    duration = time.time() - start_time
    
    files_per_second = results['file_count'] / duration
    assert files_per_second > 500, f"Processing rate too slow: {files_per_second:.2f} files/s"
```

#### 2. Large File Sizes
```python
@pytest.mark.performance
@pytest.mark.slow
def test_large_file_sizes_performance(self, large_files_directory, size_analyzer):
    """Test performance with large files."""
    import time
    
    start_time = time.time()
    results = size_analyzer.analyze_directory(str(large_files_directory))
    duration = time.time() - start_time
    
    bytes_per_second = results['total_size'] / duration
    assert bytes_per_second > 100 * 1024 * 1024, f"Byte processing rate too slow: {bytes_per_second:.2f} B/s"
```

---

## Performance Testing

### Performance Test Framework

```python
import time
import psutil
import threading
from contextlib import contextmanager

class PerformanceMonitor:
    """Monitor performance metrics during test execution."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        self.peak_memory = self.start_memory
        self.monitoring = True
        
        # Start memory monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_memory)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring and return metrics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss
        
        return {
            'duration': end_time - self.start_time,
            'memory_used': (end_memory - self.start_memory) / 1024 / 1024,  # MB
            'peak_memory': (self.peak_memory - self.start_memory) / 1024 / 1024,  # MB
            'cpu_percent': self.process.cpu_percent()
        }
    
    def _monitor_memory(self):
        """Monitor memory usage in background thread."""
        while self.monitoring:
            current_memory = self.process.memory_info().rss
            self.peak_memory = max(self.peak_memory, current_memory)
            time.sleep(0.1)

@contextmanager
def performance_monitor():
    """Context manager for performance monitoring."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    try:
        yield monitor
    finally:
        metrics = monitor.stop_monitoring()
        return metrics
```

### Performance Test Examples

```python
@pytest.mark.performance
def test_analysis_performance_benchmarks(self, test_datasets, size_analyzer):
    """Test analysis performance against established benchmarks."""
    
    benchmarks = {
        'small': {'max_time': 5, 'max_memory': 50, 'min_rate': 50},
        'medium': {'max_time': 15, 'max_memory': 100, 'min_rate': 100},
        'large': {'max_time': 30, 'max_memory': 200, 'min_rate': 300}
    }
    
    for dataset_name, dataset_path in test_datasets.items():
        if dataset_name not in benchmarks:
            continue
            
        benchmark = benchmarks[dataset_name]
        
        with performance_monitor() as monitor:
            results = size_analyzer.analyze_directory(str(dataset_path))
        
        metrics = monitor.stop_monitoring()
        
        # Validate performance benchmarks
        assert metrics['duration'] <= benchmark['max_time'], \
            f"{dataset_name}: Analysis took {metrics['duration']:.2f}s, expected <={benchmark['max_time']}s"
        
        assert metrics['peak_memory'] <= benchmark['max_memory'], \
            f"{dataset_name}: Peak memory {metrics['peak_memory']:.2f}MB, expected <={benchmark['max_memory']}MB"
        
        files_per_second = results['file_count'] / metrics['duration']
        assert files_per_second >= benchmark['min_rate'], \
            f"{dataset_name}: Processing rate {files_per_second:.2f} files/s, expected >={benchmark['min_rate']}"

@pytest.mark.performance
def test_memory_leak_detection(self, medium_test_directory, size_analyzer):
    """Test for memory leaks in repeated operations."""
    import gc
    
    initial_memory = psutil.Process().memory_info().rss
    
    # Perform multiple analyses
    for i in range(10):
        results = size_analyzer.analyze_directory(str(medium_test_directory))
        
        # Force garbage collection
        gc.collect()
        
        # Check memory growth
        current_memory = psutil.Process().memory_info().rss
        memory_growth = (current_memory - initial_memory) / 1024 / 1024  # MB
        
        # Allow some memory growth, but not excessive
        assert memory_growth < 100, f"Iteration {i}: Memory growth {memory_growth:.2f}MB, possible leak"

@pytest.mark.performance
def test_concurrent_analysis_performance(self, test_directories, size_analyzer):
    """Test performance with concurrent analysis operations."""
    import concurrent.futures
    import threading
    
    def analyze_directory(directory):
        """Analyze directory and return metrics."""
        start_time = time.time()
        results = size_analyzer.analyze_directory(str(directory))
        duration = time.time() - start_time
        return {
            'directory': str(directory),
            'duration': duration,
            'file_count': results['file_count']
        }
    
    # Run concurrent analyses
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(analyze_directory, directory) 
                  for directory in test_directories[:3]]
        
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Validate that concurrent operations don't significantly degrade performance
    for result in results:
        files_per_second = result['file_count'] / result['duration']
        assert files_per_second > 50, f"Concurrent analysis too slow: {files_per_second:.2f} files/s"
```

---

## Integration Testing

### Hub Integration Tests

```python
class MockHub:
    """Mock hub for testing integration."""
    
    def __init__(self):
        self.registered_tools = {}
        self.messages = []
        self.resources = {'cpu': True, 'memory': True, 'disk': True}
    
    def register_tool(self, tool_name, tool_instance):
        """Register tool with mock hub."""
        self.registered_tools[tool_name] = tool_instance
        return True
    
    def receive_message(self, message):
        """Receive message from tool."""
        self.messages.append(message)
    
    def request_resource(self, tool_name, resource_type, requirements):
        """Handle resource request."""
        return self.resources.get(resource_type, False)
    
    def broadcast_event(self, tool_name, event_type, event_data):
        """Handle event broadcast."""
        self.messages.append({
            'type': 'broadcast',
            'tool': tool_name,
            'event_type': event_type,
            'data': event_data
        })

@pytest.fixture
def mock_hub():
    """Create mock hub for testing."""
    return MockHub()

def test_hub_integration_workflow(self, mock_hub, test_directory):
    """Test complete hub integration workflow."""
    from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
    
    # Create GUI with hub integration
    gui = SizeAnalyzerGUI(hub_instance=mock_hub)
    
    # Test registration
    success = gui.register_with_hub(mock_hub)
    assert success
    assert "Size Analyzer" in mock_hub.registered_tools
    
    # Test resource request
    resource_granted = gui.request_hub_resources("cpu", {
        "operation": "directory_analysis",
        "priority": "normal"
    })
    assert resource_granted
    
    # Test status reporting
    gui.report_status_to_hub("analyzing", {"directory": str(test_directory)})
    
    # Verify messages were sent
    assert len(mock_hub.messages) > 0
    
    # Test event broadcasting
    gui.broadcast_hub_event("test_event", {"test_data": "value"})
    
    # Verify broadcast was received
    broadcast_messages = [msg for msg in mock_hub.messages if msg.get('type') == 'broadcast']
    assert len(broadcast_messages) > 0
```

### Component Integration Tests

```python
def test_core_gui_integration(self, qtbot, test_directory):
    """Test integration between core logic and GUI components."""
    from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
    
    # Create GUI
    gui = SizeAnalyzerGUI()
    
    # Set up signal spies
    progress_spy = qtbot.QSignalSpy(gui.analyzer.progress_percentage)
    complete_spy = qtbot.QSignalSpy(gui.analyzer.analysis_complete)
    
    # Set directory and start analysis
    gui.selected_directory = str(test_directory)
    gui._start_analysis()
    
    # Wait for completion
    qtbot.waitSignal(gui.analyzer.analysis_complete, timeout=30000)
    
    # Verify signals were emitted
    assert len(progress_spy) > 0, "Progress signals should be emitted"
    assert len(complete_spy) == 1, "Analysis complete signal should be emitted once"
    
    # Verify GUI state
    assert gui.current_analysis is not None
    assert gui.export_button.isEnabled()

def test_configuration_integration(self, size_analyzer):
    """Test integration with configuration system."""
    from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
    
    # Create configuration
    config = SizeAnalyzerConfig()
    
    # Update settings
    config.set_setting('analysis', 'default_top_files_count', 15)
    config.set_setting('performance', 'max_memory_usage_mb', 128)
    
    # Verify settings are applied
    top_files = config.get_setting('analysis', 'default_top_files_count')
    assert top_files == 15
    
    memory_limit = config.get_setting('performance', 'max_memory_usage_mb')
    assert memory_limit == 128
```

---

## Validation Procedures

### Pre-Release Validation Checklist

#### Functional Validation
- [ ] All unit tests pass (>95% coverage)
- [ ] All integration tests pass
- [ ] All performance benchmarks met
- [ ] GUI functionality validated
- [ ] Hub integration verified
- [ ] Configuration management tested
- [ ] Export functionality validated
- [ ] Error handling verified

#### Performance Validation
- [ ] Small directory analysis <5 seconds
- [ ] Medium directory analysis <15 seconds
- [ ] Large directory analysis <30 seconds
- [ ] Memory usage <500MB for large datasets
- [ ] No memory leaks detected
- [ ] CPU usage reasonable
- [ ] Concurrent operations supported

#### Compatibility Validation
- [ ] Python 3.7+ compatibility
- [ ] PyQt5 5.15+ compatibility
- [ ] Windows 10+ compatibility
- [ ] Linux (Ubuntu 18.04+) compatibility
- [ ] macOS 10.14+ compatibility
- [ ] Cross-platform file handling

#### Integration Validation
- [ ] Hub registration successful
- [ ] Resource coordination working
- [ ] Event broadcasting functional
- [ ] Progress reporting accurate
- [ ] Error propagation correct
- [ ] Configuration synchronization

### Validation Scripts

#### Automated Validation Script

```python
#!/usr/bin/env python3
"""
Size Analyzer Validation Script
Comprehensive validation of all components and functionality.
"""

import sys
import os
import tempfile
import time
from pathlib import Path

def validate_imports():
    """Validate all required imports."""
    print("Validating imports...")
    
    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
        from file_utilities_2.integration.hub_connector import HubConnector
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def validate_core_functionality():
    """Validate core analysis functionality."""
    print("Validating core functionality...")
    
    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
        
        # Create test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = []
            for i in range(5):
                file_path =