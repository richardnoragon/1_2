# Size Analyzer API Reference

## Overview

This document provides comprehensive API reference for the Size Analyzer components within the file_utilities_2 ecosystem. The API is designed with clear separation of concerns, providing distinct interfaces for core logic, GUI components, configuration management, and hub integration.

## Table of Contents

1. [Core Logic API](#core-logic-api)
2. [GUI Components API](#gui-components-api)
3. [Configuration API](#configuration-api)
4. [Hub Integration API](#hub-integration-api)
5. [Worker Thread API](#worker-thread-api)
6. [Signal Reference](#signal-reference)
7. [Data Structures](#data-structures)
8. [Error Handling](#error-handling)
9. [Usage Examples](#usage-examples)

---

## Core Logic API

### SizeAnalyzer Class

**Module**: `file_utilities_2.core.size_analyzer_logic`

The `SizeAnalyzer` class provides the core business logic for directory size analysis without GUI dependencies.

#### Constructor

```python
def __init__(self, hub_connector=None):
    """
    Initialize the SizeAnalyzer with optional hub integration.
    
    Args:
        hub_connector (HubConnector, optional): Hub connector for integration
        
    Attributes:
        _is_running (bool): Whether analysis is currently running
        _should_cancel (bool): Whether cancellation has been requested
        _current_analysis (dict): Current analysis results
        _hub_connector (HubConnector): Hub connector instance
        _performance_metrics (dict): Performance tracking data
        _resource_usage (dict): Resource usage statistics
    """
```

#### Core Methods

##### analyze_directory()

```python
def analyze_directory(self, directory_path: str,
                     top_files_count: int = 10,
                     include_extensions: Optional[List[str]] = None,
                     progress_callback: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
    """
    Analyze a directory and return comprehensive statistics.
    
    This is the main analysis method that provides complete directory
    analysis with progress tracking and filtering capabilities.
    
    Args:
        directory_path (str): Path to directory to analyze
        top_files_count (int, optional): Number of largest files to include. Defaults to 10.
        include_extensions (List[str], optional): List of file extensions to include. 
                                                 None includes all files.
        progress_callback (Callable[[int], None], optional): Callback for progress updates
        
    Returns:
        Dict[str, Any]: Comprehensive analysis results containing:
            - path (str): Analyzed directory path
            - total_size (int): Total size in bytes
            - file_count (int): Number of files analyzed
            - directory_count (int): Number of directories found
            - files (List[Dict]): Detailed file information
            - file_types (Dict): File type statistics
            - largest_files (List[Dict]): Largest files list
            - directory_tree (Dict): Directory tree structure
            - performance_metrics (Dict): Analysis performance data
            
    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
        PermissionError: If directory cannot be accessed
        
    Signals Emitted:
        - progress_updated(int, int): Current and total progress
        - progress_percentage(int): Progress percentage (0-100)
        - progress_message(str): Detailed status message
        - milestone_reached(str, int): Milestone description and percentage
        - analysis_complete(dict): Complete analysis results
        - error_occurred(str): Error messages
        
    Example:
        >>> analyzer = SizeAnalyzer()
        >>> results = analyzer.analyze_directory("/home/user/documents")
        >>> print(f"Total size: {analyzer.format_size(results['total_size'])}")
    """
```

##### format_size()

```python
def format_size(self, size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Converts byte values to appropriate units (B, KB, MB, GB, TB)
    with one decimal place precision.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB", "2.3 GB")
        
    Example:
        >>> analyzer = SizeAnalyzer()
        >>> analyzer.format_size(1536)
        '1.5 KB'
        >>> analyzer.format_size(2147483648)
        '2.0 GB'
    """
```

##### export_analysis()

```python
def export_analysis(self, analysis: Dict[str, Any], export_path: str) -> None:
    """
    Export analysis results to a JSON file.
    
    Serializes analysis results with metadata and exports to specified path.
    Handles datetime serialization and adds export metadata.
    
    Args:
        analysis (Dict[str, Any]): Analysis results dictionary
        export_path (str): Path where to save the export file
        
    Raises:
        IOError: If file cannot be written
        ValueError: If analysis data is invalid
        
    Signals Emitted:
        - progress_message(str): Export status message
        - error_occurred(str): Export error message
        
    Example:
        >>> analyzer = SizeAnalyzer()
        >>> results = analyzer.analyze_directory("/path/to/dir")
        >>> analyzer.export_analysis(results, "analysis_results.json")
    """
```

##### cancel_operation()

```python
def cancel_operation(self) -> None:
    """
    Cancel the current analysis operation.
    
    Sets cancellation flag and emits cancellation signal.
    The analysis will stop at the next safe checkpoint.
    
    Signals Emitted:
        - progress_message(str): Cancellation status
        - operation_cancelled(): Cancellation notification
        
    Example:
        >>> analyzer = SizeAnalyzer()
        >>> # Start analysis in another thread
        >>> analyzer.cancel_operation()  # Cancel from main thread
    """
```

#### Hub Integration Methods

##### set_hub_connector()

```python
def set_hub_connector(self, hub_connector) -> None:
    """
    Set the hub connector for this analyzer.
    
    Args:
        hub_connector (HubConnector): Hub connector instance
        
    Example:
        >>> from file_utilities_2.integration.hub_connector import HubConnector
        >>> hub = HubConnector("Size Analyzer")
        >>> analyzer.set_hub_connector(hub)
    """
```

##### get_performance_metrics()

```python
def get_performance_metrics(self) -> Dict[str, Any]:
    """
    Get current performance metrics.
    
    Returns:
        Dict[str, Any]: Performance metrics containing:
            - start_time (datetime): Analysis start time
            - end_time (datetime): Analysis end time
            - files_per_second (float): File processing rate
            - bytes_per_second (float): Byte processing rate
            - peak_memory_usage (int): Peak memory usage in bytes
            
    Example:
        >>> metrics = analyzer.get_performance_metrics()
        >>> print(f"Processing rate: {metrics['files_per_second']:.2f} files/sec")
    """
```

##### update_resource_usage()

```python
def update_resource_usage(self, cpu_usage: float = 0,
                         memory_usage: float = 0, 
                         disk_io: float = 0) -> None:
    """
    Update resource usage statistics.
    
    Args:
        cpu_usage (float, optional): CPU usage percentage. Defaults to 0.
        memory_usage (float, optional): Memory usage in MB. Defaults to 0.
        disk_io (float, optional): Disk I/O rate in MB/s. Defaults to 0.
        
    Example:
        >>> analyzer.update_resource_usage(cpu_usage=45.2, memory_usage=128.5)
    """
```

#### Utility Methods

##### is_running()

```python
def is_running(self) -> bool:
    """
    Check if an analysis operation is currently running.
    
    Returns:
        bool: True if analysis is running, False otherwise
        
    Example:
        >>> if analyzer.is_running():
        ...     print("Analysis in progress...")
    """
```

---

## GUI Components API

### SizeAnalyzerGUI Class

**Module**: `file_utilities_2.gui.size_analyzer_gui`

The `SizeAnalyzerGUI` class provides the modern PyQt5 user interface with comprehensive hub integration.

#### Constructor

```python
def __init__(self, hub_instance=None):
    """
    Initialize the Size Analyzer GUI with hub integration.
    
    Args:
        hub_instance (object, optional): Hub instance for integration
        
    Attributes:
        analyzer (SizeAnalyzer): Core analyzer instance
        worker_thread (SizeAnalyzerWorker): Worker thread for analysis
        current_analysis (dict): Current analysis results
        selected_directory (str): Currently selected directory
        hub_connector (HubConnector): Hub integration connector
        hub_instance (object): Hub instance reference
    """
```

#### Hub Integration Methods

##### register_with_hub()

```python
def register_with_hub(self, hub_instance) -> bool:
    """
    Register tool with central hub for communication.
    
    Args:
        hub_instance (object): Hub instance to register with
        
    Returns:
        bool: True if registration successful, False otherwise
        
    Signals Emitted:
        - tool_started(str): Tool name when registration succeeds
        
    Example:
        >>> gui = SizeAnalyzerGUI()
        >>> success = gui.register_with_hub(hub_instance)
        >>> if success:
        ...     print("Successfully registered with hub")
    """
```

##### report_status_to_hub()

```python
def report_status_to_hub(self, status: str, details: Dict[str, Any] = None) -> None:
    """
    Report current status to hub.
    
    Args:
        status (str): Current tool status ('ready', 'analyzing', 'completed', etc.)
        details (Dict[str, Any], optional): Additional status details
        
    Signals Emitted:
        - tool_status_changed(str, str): Tool name and status
        
    Example:
        >>> gui.report_status_to_hub("analyzing", {"directory": "/path/to/dir"})
    """
```

##### request_hub_resources()

```python
def request_hub_resources(self, resource_type: str,
                         requirements: Dict[str, Any] = None) -> bool:
    """
    Request shared resources from hub.
    
    Args:
        resource_type (str): Type of resource requested ('cpu', 'memory', 'disk')
        requirements (Dict[str, Any], optional): Resource requirements specification
        
    Returns:
        bool: True if resource granted, False otherwise
        
    Signals Emitted:
        - hub_resource_granted(str, dict): Resource type and details
        
    Example:
        >>> requirements = {"operation": "directory_analysis", "priority": "normal"}
        >>> granted = gui.request_hub_resources("cpu", requirements)
    """
```

##### broadcast_hub_event()

```python
def broadcast_hub_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
    """
    Broadcast event to other tools through hub.
    
    Args:
        event_type (str): Type of event to broadcast
        event_data (Dict[str, Any]): Event data to broadcast
        
    Example:
        >>> gui.broadcast_hub_event("analysis_completed", {
        ...     "tool": "Size Analyzer",
        ...     "directory": "/analyzed/path",
        ...     "results": analysis_results
        ... })
    """
```

#### UI Interaction Methods

##### _browse_directory()

```python
@pyqtSlot()
def _browse_directory(self) -> None:
    """
    Handle directory browsing user interaction.
    
    Opens directory selection dialog and updates UI with selected directory.
    
    Signals Emitted:
        - Updates UI components with selected directory
        
    Example:
        # Connected to browse button click
        self.browse_button.clicked.connect(self._browse_directory)
    """
```

##### _start_analysis()

```python
@pyqtSlot()
def _start_analysis(self) -> None:
    """
    Start the directory analysis process.
    
    Validates selected directory, requests hub resources, and starts
    analysis in worker thread.
    
    Signals Emitted:
        - tool_started(str): Tool name when analysis starts
        
    Example:
        # Connected to analyze button click
        self.analyze_button.clicked.connect(self._start_analysis)
    """
```

##### _export_results()

```python
@pyqtSlot()
def _export_results(self) -> None:
    """
    Export analysis results to file.
    
    Opens file save dialog and exports current analysis results.
    
    Example:
        # Connected to export button click
        self.export_button.clicked.connect(self._export_results)
    """
```

---

## Configuration API

### SizeAnalyzerConfig Class

**Module**: `file_utilities_2.core.size_analyzer_config`

The `SizeAnalyzerConfig` class provides comprehensive configuration management with settings persistence.

#### Constructor

```python
def __init__(self, config_manager: Optional[ConfigManager] = None):
    """
    Initialize the Size Analyzer configuration manager.
    
    Args:
        config_manager (ConfigManager, optional): Configuration manager instance
        
    Attributes:
        config_manager (ConfigManager): Configuration manager
        logger (Logger): Configuration logger
        section_name (str): Configuration section name
        defaults (dict): Default configuration values
    """
```

#### Configuration Methods

##### get_setting()

```python
def get_setting(self, subsection: str, key: str, default: Any = None) -> Any:
    """
    Get a specific setting value.
    
    Args:
        subsection (str): Configuration subsection name
        key (str): Setting key
        default (Any, optional): Default value if not found
        
    Returns:
        Any: Setting value or default
        
    Example:
        >>> config = SizeAnalyzerConfig()
        >>> top_files = config.get_setting('analysis', 'default_top_files_count', 20)
    """
```

##### set_setting()

```python
def set_setting(self, subsection: str, key: str, value: Any) -> bool:
    """
    Set a specific setting value.
    
    Args:
        subsection (str): Configuration subsection name
        key (str): Setting key
        value (Any): Setting value
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> config.set_setting('analysis', 'default_top_files_count', 25)
    """
```

##### get_resource_path()

```python
def get_resource_path(self, resource_name: str) -> str:
    """
    Get the path for a specific resource.
    
    Args:
        resource_name (str): Name of the resource
        
    Returns:
        str: Absolute path to the resource
        
    Example:
        >>> icon_path = config.get_resource_path('icon_path')
        >>> print(f"Icon located at: {icon_path}")
    """
```

##### validate_configuration()

```python
def validate_configuration(self) -> Dict[str, list]:
    """
    Validate the current configuration and return any issues.
    
    Returns:
        Dict[str, list]: Dictionary with 'errors', 'warnings', and 'info' lists
        
    Example:
        >>> issues = config.validate_configuration()
        >>> if issues['errors']:
        ...     print("Configuration errors found:", issues['errors'])
    """
```

#### Specialized Methods

##### add_recent_directory()

```python
def add_recent_directory(self, directory: str) -> bool:
    """
    Add a directory to the recent directories list.
    
    Args:
        directory (str): Directory path to add
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> config.add_recent_directory('/home/user/documents')
    """
```

##### save_window_geometry()

```python
def save_window_geometry(self, width: int, height: int, 
                        x: int = None, y: int = None) -> bool:
    """
    Save window geometry settings.
    
    Args:
        width (int): Window width
        height (int): Window height
        x (int, optional): Window x position
        y (int, optional): Window y position
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> config.save_window_geometry(800, 600, 100, 100)
    """
```

---

## Hub Integration API

### HubConnector Class

**Module**: `file_utilities_2.integration.hub_connector`

The `HubConnector` class provides comprehensive hub integration and communication capabilities.

#### Constructor

```python
def __init__(self, tool_name: str, hub_instance=None):
    """
    Initialize hub connector.
    
    Args:
        tool_name (str): Name of the tool using this connector
        hub_instance (object, optional): Reference to the hub instance
        
    Attributes:
        tool_name (str): Tool name
        hub_instance (object): Hub instance reference
        is_connected (bool): Connection status
        is_registered (bool): Registration status
        config (SharedConfiguration): Shared configuration
        logger (HubEventLogger): Event logger
        tool_state (dict): Tool state tracking
    """
```

#### Communication Methods

##### register_with_hub()

```python
def register_with_hub(self, hub_instance=None) -> bool:
    """
    Register tool with central hub for communication.
    
    Args:
        hub_instance (object, optional): Hub instance to register with
        
    Returns:
        bool: True if registration successful, False otherwise
        
    Signals Emitted:
        - tool_registered(str): Tool name
        - hub_connection_status(bool): Connection status
        
    Example:
        >>> connector = HubConnector("Size Analyzer")
        >>> success = connector.register_with_hub(hub_instance)
    """
```

##### report_progress_to_hub()

```python
def report_progress_to_hub(self, percentage: int, message: str = "") -> None:
    """
    Report progress to hub's central progress tracking system.
    
    Args:
        percentage (int): Progress percentage (0-100)
        message (str, optional): Progress message
        
    Example:
        >>> connector.report_progress_to_hub(50, "Processing files...")
    """
```

##### broadcast_event()

```python
def broadcast_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
    """
    Broadcast event to other tools through hub.
    
    Args:
        event_type (str): Type of event
        event_data (Dict[str, Any]): Event data
        
    Example:
        >>> connector.broadcast_event("analysis_completed", {
        ...     "tool": "Size Analyzer",
        ...     "results": analysis_data
        ... })
    """
```

---

## Worker Thread API

### SizeAnalyzerWorker Class

**Module**: `file_utilities_2.core.size_analyzer_logic`

The `SizeAnalyzerWorker` class provides thread-safe execution of analysis operations.

#### Constructor

```python
def __init__(self, analyzer: SizeAnalyzer, directory_path: str,
             hub_connector=None, **kwargs):
    """
    Initialize the worker thread with hub integration.
    
    Args:
        analyzer (SizeAnalyzer): SizeAnalyzer instance to use
        directory_path (str): Directory to analyze
        hub_connector (HubConnector, optional): Hub connector for integration
        **kwargs: Additional arguments for analyze_directory
        
    Attributes:
        analyzer (SizeAnalyzer): Analyzer instance
        directory_path (str): Directory path
        kwargs (dict): Analysis arguments
        hub_connector (HubConnector): Hub connector
    """
```

#### Thread Methods

##### run()

```python
def run(self) -> None:
    """
    Run the analysis in the worker thread.
    
    Executes directory analysis with progress callbacks and error handling.
    
    Signals Emitted:
        - analysis_finished(dict): Analysis results
        - analysis_error(str): Error message
        - progress_update(int): Progress percentage
        - status_update(str): Status message
    """
```

##### cancel()

```python
def cancel(self) -> None:
    """
    Cancel the analysis operation.
    
    Safely terminates the worker thread and cleans up resources.
    
    Example:
        >>> worker = SizeAnalyzerWorker(analyzer, "/path/to/dir")
        >>> worker.start()
        >>> # Later...
        >>> worker.cancel()
    """
```

---

## Signal Reference

### Core Logic Signals

#### SizeAnalyzer Signals

```python
# Progress tracking signals
progress_updated = pyqtSignal(int, int)        # current, total
progress_percentage = pyqtSignal(int)          # percentage (0-100)
progress_message = pyqtSignal(str)             # detailed status message
milestone_reached = pyqtSignal(str, int)       # milestone desc, percentage
time_estimate = pyqtSignal(str)                # estimated time remaining

# Completion and error signals
analysis_complete = pyqtSignal(dict)           # complete analysis results
error_occurred = pyqtSignal(str)               # error messages
operation_cancelled = pyqtSignal()             # cancellation notification
```

### GUI Signals

#### SizeAnalyzerGUI Signals

```python
# Hub notification signals
tool_started = pyqtSignal(str)                 # tool name
tool_completed = pyqtSignal(str, dict)         # tool name, results
tool_error = pyqtSignal(str, str)              # tool name, error message
tool_progress = pyqtSignal(str, int, str)      # tool name, percentage, message
tool_status_changed = pyqtSignal(str, str)     # tool name, status

# Hub integration events
hub_connection_changed = pyqtSignal(bool)      # connection status
hub_resource_granted = pyqtSignal(str, dict)  # resource type, details
hub_event_received = pyqtSignal(str, dict)    # event type, data
```

### Hub Integration Signals

#### HubConnector Signals

```python
# Hub communication signals
hub_message_received = pyqtSignal(object)     # HubMessage
hub_connection_status = pyqtSignal(bool)      # connected/disconnected
hub_resource_available = pyqtSignal(str, dict) # resource_type, details
hub_broadcast_received = pyqtSignal(str, dict) # event_type, data

# Tool registration signals
tool_registered = pyqtSignal(str)             # tool_name
tool_unregistered = pyqtSignal(str)           # tool_name
tool_status_changed = pyqtSignal(str, str)    # tool_name, status
```

---

## Data Structures

### Analysis Result Structure

```python
{
    'path': str,                    # Analyzed directory path
    'total_size': int,              # Total size in bytes
    'file_count': int,              # Number of files
    'directory_count': int,         # Number of directories
    'files': [                      # File information list
        {
            'name': str,            # File name
            'path': str,            # Full file path
            'size': int,            # File size in bytes
            'extension': str,       # File extension
            'modified': float       # Modification timestamp
        }
    ],
    'file_types': {                 # File type statistics
        '.ext': {
            'count': int,           # Number of files
            'total_size': int,      # Total size in bytes
            'average_size': float   # Average file size
        }
    },
    'largest_files': [              # Largest files list
        {
            'name': str,            # File name
            'path': str,            # Full file path
            'size': int             # File size in bytes
        }
    ],
    'directory_tree': {             # Directory tree structure
        'name': str,                # Directory name
        'path': str,                # Directory path
        'size': int,                # Directory total size
        'children': {}              # Child directories/files
    },
    'performance_metrics': {        # Performance data
        'start_time': datetime,     # Analysis start time
        'end_time': datetime,       # Analysis end time
        'files_per_second': float,  # Processing rate
        'bytes_per_second': float,  # Byte processing rate
        'peak_memory_usage': int    # Peak memory usage
    }
}
```

### Configuration Structure

```python
{
    'general': {
        'module_path': str,         # Module path
        'class_name': str,          # Class name
        'last_opened_directory': str, # Last directory
        'recent_directories': list,  # Recent directories
        'enable_logging': bool      # Logging enabled
    },
    'analysis': {
        'default_top_files_count': int,     # Top files count
        'progress_update_interval': int,    # Update interval
        'include_hidden_files': bool,       # Include hidden files
        'enable_file_type_analysis': bool   # File type analysis
    },
    'performance': {
        'max_memory_usage_mb': int,         # Memory limit
        'max_cpu_usage_percent': int,       # CPU limit
        'operation_timeout_seconds': int    # Timeout
    }
}
```

### Hub Message Structure

```python
{
    'message_id': str,              # Unique message ID
    'message_type': str,            # Message type
    'tool_name': str,               # Source tool name
    'data': dict,                   # Message data
    'timestamp': str                # ISO timestamp
}
```

---

## Error Handling

### Exception Types

#### Core Exceptions

```python
# File system errors
FileNotFoundError          # Directory not found
NotADirectoryError        # Path is not a directory
PermissionError           # Access denied

# Analysis errors
ValueError                # Invalid parameters
RuntimeError              # Analysis runtime error
IOError                   # Export/import errors
```

#### Custom Exceptions

```python
class SizeAnalyzerError(Exception):
    """Base exception for Size Analyzer errors."""
    pass

class AnalysisError(SizeAnalyzerError):
    """Exception raised during analysis operations."""
    pass

class ConfigurationError(SizeAnalyzerError):
    """Exception raised for configuration issues."""
    pass

class HubIntegrationError(SizeAnalyzerError):
    """Exception raised for hub integration issues."""
    pass
```

### Error Handling Patterns

#### Try-Catch Pattern

```python
try:
    analyzer = SizeAnalyzer()
    results = analyzer.analyze_directory("/path/to/directory")
except FileNotFoundError as e:
    print(f"Directory not found: {e}")
except PermissionError as e:
    print(f"Permission denied: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Signal-Based Error Handling

```python
def handle_error(error_message: str):
    """Handle analysis errors."""
    print(f"Analysis error: {error_message}")
    # Implement error recovery logic

analyzer = SizeAnalyzer()
analyzer.error_occurred.connect(handle_error)
```

---

## Usage Examples

### Basic Usage

#### Simple Directory Analysis

```python
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

# Create analyzer
analyzer = SizeAnalyzer()

# Analyze directory
results = analyzer.analyze_directory("/home/user/documents")

# Display results
print(f"Total size: {analyzer.format_size(results['total_size'])}")
print(f"File count: {results['file_count']}")
print(f"Directory count: {results['directory_count']}")

# Export results
analyzer.export_analysis(results, "analysis_results.json")
```

#### GUI Application

```python
import sys
from PyQt5.QtWidgets import QApplication
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

# Create application
app = QApplication(sys.argv)

# Create and show GUI
window = SizeAnalyzerGUI()
window.show()

# Run application
sys.exit(app.exec_())
```

### Advanced Usage

#### With Progress Tracking

```python
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

def progress_callback(percentage):
    print(f"Progress: {percentage}%")

def status_callback(message):
    print(f"Status: {message}")

# Create analyzer with callbacks
analyzer = SizeAnalyzer()
analyzer.progress_percentage.connect(progress_callback)
analyzer.progress_message.connect(status_callback)

# Analyze with progress tracking
results = analyzer.analyze_directory(
    "/large/directory",
    progress_callback=progress_callback
)
```

#### With Hub Integration

```python
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
from file_utilities_2.integration.hub_connector import HubConnector

# Create hub connector
hub_connector = HubConnector("Size Analyzer")

# Create GUI with hub integration
gui = SizeAnalyzerGUI(hub_instance=hub_connector)

# Register with hub
success = gui.register_with_hub(hub_connector)
if success:
    print("Successfully registered with hub")

# Show GUI
gui.show()
```

#### Configuration Management

```python
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig

# Create configuration manager
config = SizeAnalyzerConfig()

# Get settings
top_files_count = config.get_setting('analysis', 'default_top_files_count', 20)
enable_logging = config.get_setting('general', 'enable_logging', True)

# Update settings
config.set_setting('analysis', 'default_top_files_count', 25)
config.set_setting('performance', 'max_memory_usage_mb', 512)

# Validate configuration
issues = config.validate_configuration()
if issues['errors']:
    print("Configuration errors:", issues['errors'])
```

#### Worker Thread Usage

```python
from PyQt5.QtCore import QObject, pyqtSlot
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker

class AnalysisController(QObject):
    def __init__(self):
        super().__init__()
        self.analyzer = SizeAnalyzer()
        self.worker = None
    
    def start_analysis(self, directory_path):
        """Start analysis in worker thread."""
        self.worker = SizeAnalyzerWorker(self.analyzer, directory_path)
        
        # Connect signals
        self.worker.analysis_finished.connect(self.on_analysis_complete)
        self.worker.analysis_error.connect(self.on_analysis_error)
        self.worker.progress_update.connect(self.on_progress_update)
        
        # Start worker
        self.worker.start()
    
    @pyqtSlot(dict)
    def on_analysis_complete(self, results):
        """Handle analysis completion."""
        print(f"Analysis complete: {len(results['files'])} files analyzed")
    
    @pyqtSlot(str)
    def on_analysis_error(self, error_message):
        """Handle analysis error."""
        print(f"Analysis error: {error_message}")
    
    @pyqtSlot(int)
    def on_progress_update(self, percentage):
        """Handle progress update."""
        print(f"Progress: {percentage}%")

# Usage
controller = AnalysisController()
controller.start_analysis("/path/to/directory")
```

---

## Version Information

**API Version**: 2.0.0  
**Last Updated**: January 27, 2025  
**Compatibility**: Python 3.7+, PyQt5 5.15+  
**Module Path**: `file_utilities_2`

---

## See Also

- [Installation Guide](size_analyzer_installation.md)
- [Testing Documentation](size_analyzer_