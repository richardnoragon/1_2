# RFU Multi-Pane File Explorer - Developer Guide

## Overview

This guide provides comprehensive information for developers who want to contribute to, extend, or integrate with the RFU Multi-Pane File Explorer. It covers the codebase structure, development setup, coding standards, and extension mechanisms.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Architecture Patterns](#architecture-patterns)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Contributing Guidelines](#contributing-guidelines)
7. [Extension Development](#extension-development)
8. [Debugging and Profiling](#debugging-and-profiling)

## Development Setup

### Prerequisites

- Python 3.9+ (recommended: 3.11+)
- Git for version control
- IDE with Python support (recommended: VS Code, PyCharm)

### Environment Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd rfu-file-explorer
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv rfuenv
   
   # Windows
   rfuenv\Scripts\activate
   
   # macOS/Linux
   source rfuenv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Core dependencies
   pip install -r requirements.txt
   
   # Development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Development Dependencies**
   ```bash
   pip install pytest>=7.0
   pip install pytest-qt>=4.0
   pip install pytest-cov>=4.0
   pip install black>=22.0
   pip install flake8>=5.0
   pip install mypy>=1.0
   pip install sphinx>=5.0
   ```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./rfuenv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true
    }
}
```

#### PyCharm Configuration

1. Set project interpreter to virtual environment
2. Enable pytest as test runner
3. Configure Black as code formatter
4. Enable type checking with mypy

## Project Structure

### Directory Layout

```
src/rfu/file_explorer/
├── __init__.py                 # Package initialization
├── main_application.py         # Application entry point
├── database/                   # Data layer
│   ├── __init__.py
│   ├── schema.py              # Database schema and migrations
│   └── cache_manager.py       # Caching system
├── models/                     # Business logic layer
│   ├── __init__.py
│   ├── drive_manager.py       # Drive detection
│   └── enhanced_file_model.py # File system models
├── ui/                        # User interface layer
│   ├── __init__.py
│   ├── pane_manager.py        # Pane management
│   ├── file_explorer_pane.py  # Main file explorer
│   └── custom_widgets.py      # Custom UI components
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── directory_watcher.py   # File system monitoring
└── tests/                     # Test suite
    ├── __init__.py
    ├── conftest.py            # Test fixtures
    ├── test_database.py       # Database tests
    ├── test_ui.py             # UI tests
    ├── test_performance.py    # Performance tests
    └── test_comprehensive.py  # Integration tests
```

### Module Dependencies

```
main_application.py
├── ui/
│   ├── pane_manager.py
│   ├── file_explorer_pane.py
│   └── custom_widgets.py
├── models/
│   ├── drive_manager.py
│   └── enhanced_file_model.py
├── database/
│   ├── schema.py
│   └── cache_manager.py
└── utils/
    └── directory_watcher.py
```

### Design Patterns Used

#### Singleton Pattern
- `ConfigManager`: Global configuration management
- `DatabaseSchema`: Single database connection

#### Observer Pattern
- `DirectoryWatcher`: File system change notifications
- Signal/Slot system: UI event handling

#### Factory Pattern
- `PaneManager`: Dynamic pane creation
- `FileTypeHandler`: File type processing

#### Command Pattern
- File operations: Copy, move, delete, rename
- Menu actions: Undo/redo support

#### Model-View Pattern
- `EnhancedFileSystemModel`: Data model
- `FileExplorerPane`: View component

## Architecture Patterns

### Layered Architecture

The application follows a layered architecture pattern:

1. **Presentation Layer** (`ui/`)
   - User interface components
   - Event handling
   - User interaction logic

2. **Business Logic Layer** (`models/`)
   - Core functionality
   - Business rules
   - Data processing

3. **Data Access Layer** (`database/`)
   - Database operations
   - Cache management
   - Data persistence

4. **Utility Layer** (`utils/`)
   - Cross-cutting concerns
   - Helper functions
   - System integration

### Component Communication

```python
# Signal-based communication example
class FileExplorerPane(QWidget):
    # Define signals
    file_selected = pyqtSignal(str)
    path_changed = pyqtSignal(str)
    
    def select_file(self, file_path: str):
        # Emit signal to notify other components
        self.file_selected.emit(file_path)

# Connect signals in main application
def setup_connections(self):
    pane.file_selected.connect(property_panel.show_file_info)
    pane.path_changed.connect(status_bar.update_path)
```

### Error Handling Strategy

```python
# Centralized error handling
class ErrorHandler:
    """Centralized error handling and logging."""
    
    @staticmethod
    def handle_exception(exc: Exception, context: str = ""):
        """Handle exceptions with logging and user notification."""
        logger.error(f"Error in {context}: {exc}", exc_info=True)
        
        # Show user-friendly error message
        if isinstance(exc, PermissionError):
            show_error_dialog("Permission denied", "Insufficient permissions")
        elif isinstance(exc, FileNotFoundError):
            show_error_dialog("File not found", "The requested file was not found")
        else:
            show_error_dialog("Unexpected error", str(exc))

# Usage in components
try:
    perform_file_operation()
except Exception as e:
    ErrorHandler.handle_exception(e, "file_operation")
```

## Coding Standards

### Python Code Style

Follow PEP 8 with these specific guidelines:

#### Naming Conventions
```python
# Classes: PascalCase
class FileExplorerPane:
    pass

# Functions and variables: snake_case
def get_file_info():
    file_path = "/path/to/file"

# Constants: UPPER_SNAKE_CASE
MAX_CACHE_SIZE = 10000

# Private members: leading underscore
class CacheManager:
    def __init__(self):
        self._cache_data = {}
        self.__secret_key = "private"
```

#### Type Hints
```python
from typing import List, Dict, Optional, Union, Callable

def process_files(file_paths: List[str], 
                 callback: Optional[Callable[[str], None]] = None) -> Dict[str, bool]:
    """Process multiple files with optional callback.
    
    Args:
        file_paths: List of file paths to process
        callback: Optional callback function for each file
        
    Returns:
        Dictionary mapping file paths to success status
    """
    results: Dict[str, bool] = {}
    
    for file_path in file_paths:
        try:
            # Process file
            success = True
            if callback:
                callback(file_path)
        except Exception:
            success = False
        
        results[file_path] = success
    
    return results
```

#### Documentation Standards
```python
class CacheManager:
    """High-performance cache with TTL and LRU eviction.
    
    This class provides a caching system with time-to-live (TTL) expiration
    and least-recently-used (LRU) eviction policies. It supports both
    in-memory and persistent storage.
    
    Attributes:
        max_cache_size: Maximum number of cached items
        default_ttl: Default time-to-live in seconds
        
    Example:
        >>> cache = CacheManager(database, max_cache_size=1000)
        >>> cache.put("key", {"data": "value"}, ttl=3600)
        >>> data = cache.get("key")
    """
    
    def put(self, key: str, data: Dict[str, Any], ttl: Optional[float] = None) -> bool:
        """Store item in cache with optional TTL.
        
        Args:
            key: Unique cache key
            data: Data to store (must be JSON serializable)
            ttl: Time to live in seconds, uses default if None
            
        Returns:
            True if item was stored successfully
            
        Raises:
            ValueError: If key is empty or data is not serializable
            CacheError: If cache storage fails
        """
```

### Qt/GUI Code Standards

#### Widget Initialization
```python
class CustomWidget(QWidget):
    """Custom widget following standard patterns."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Initialize UI components."""
        self.layout = QVBoxLayout()
        self.button = QPushButton("Click me")
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
    
    def setup_connections(self):
        """Connect signals and slots."""
        self.button.clicked.connect(self.on_button_clicked)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.on_button_clicked)
    
    def on_button_clicked(self):
        """Handle button click."""
        pass
```

#### Signal Usage
```python
class FileOperationWidget(QWidget):
    """Widget that performs file operations."""
    
    # Define signals at class level
    operation_started = pyqtSignal(str)  # operation_name
    operation_progress = pyqtSignal(int, int)  # current, total
    operation_completed = pyqtSignal(bool, str)  # success, message
    
    def perform_operation(self, operation: str):
        """Perform file operation with progress signals."""
        self.operation_started.emit(operation)
        
        try:
            # Perform operation with progress updates
            for i in range(100):
                self.operation_progress.emit(i, 100)
                # Do work
            
            self.operation_completed.emit(True, "Operation completed successfully")
            
        except Exception as e:
            self.operation_completed.emit(False, str(e))
```

## Testing Guidelines

### Test Structure

#### Unit Tests
```python
class TestCacheManager:
    """Unit tests for CacheManager class."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        return CacheManager(db, max_cache_size=100)
    
    def test_put_and_get(self, cache_manager):
        """Test basic put and get operations."""
        key = "test_key"
        data = {"test": "data"}
        
        assert cache_manager.put(key, data)
        retrieved = cache_manager.get(key)
        assert retrieved == data
    
    def test_ttl_expiration(self, cache_manager):
        """Test TTL expiration functionality."""
        key = "expire_key"
        data = {"temporary": True}
        
        cache_manager.put(key, data, ttl=0.1)
        assert cache_manager.get(key) == data
        
        time.sleep(0.2)
        assert cache_manager.get(key) is None
```

#### Integration Tests
```python
class TestUIIntegration:
    """Integration tests for UI components."""
    
    @pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt not available")
    def test_pane_coordination(self, qapp, mock_filesystem):
        """Test coordination between multiple panes."""
        # Create pane manager
        manager = PaneManager()
        
        # Add two panes
        config1 = PaneConfiguration("pane1", PaneType.FILE_EXPLORER, "Left")
        config2 = PaneConfiguration("pane2", PaneType.FILE_EXPLORER, "Right")
        
        pane1 = manager.add_pane(config1)
        pane2 = manager.add_pane(config2)
        
        # Test file operation coordination
        test_files = [str(mock_filesystem.base_path / "test.txt")]
        pane1.copy_files(test_files)
        pane2.paste_files()
        
        # Verify results
        assert pane2.has_file("test.txt")
```

#### Performance Tests
```python
class TestPerformance:
    """Performance benchmarks and stress tests."""
    
    def test_large_directory_performance(self, large_directory, performance_monitor):
        """Test performance with large directories."""
        performance_monitor.start_measurement("large_dir_load")
        
        # Load large directory
        model = EnhancedFileSystemModel()
        model.setRootPath(str(large_directory))
        
        duration = performance_monitor.end_measurement("large_dir_load")
        assert duration < 5.0  # Should load in under 5 seconds
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    -v
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    gui: marks tests as requiring GUI
    integration: marks tests as integration tests
    performance: marks tests as performance benchmarks
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m gui         # Run only GUI tests
pytest -m performance # Run performance tests

# Run with coverage
pytest --cov=src/rfu/file_explorer --cov-report=html

# Run tests in parallel
pytest -n auto  # Requires pytest-xdist
```

## Contributing Guidelines

### Git Workflow

#### Branch Naming
- `feature/feature-name`: New features
- `bugfix/issue-description`: Bug fixes
- `hotfix/critical-issue`: Critical fixes
- `refactor/component-name`: Code refactoring
- `docs/documentation-update`: Documentation changes

#### Commit Messages
```
type(scope): brief description

Detailed explanation of changes made and why.

Fixes #issue-number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement Changes**
   - Write code following standards
   - Add comprehensive tests
   - Update documentation

3. **Pre-commit Checks**
   ```bash
   # Format code
   black src/ tests/
   
   # Lint code
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   
   # Run tests
   pytest
   ```

4. **Submit Pull Request**
   - Clear title and description
   - Reference related issues
   - Include test results
   - Request code review

### Code Review Guidelines

#### What to Review
- Code correctness and logic
- Performance implications
- Security considerations
- Test coverage
- Documentation quality
- Code style compliance

#### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Error handling is robust

## Extension Development

### Creating Custom Panes

```python
from src.rfu.file_explorer.ui.pane_manager import PaneConfiguration, PaneType
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class LogViewerPane(QWidget):
    """Example custom pane for viewing log files."""
    
    def __init__(self, config: PaneConfiguration):
        super().__init__()
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize log viewer UI."""
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
    
    def load_log_file(self, file_path: str):
        """Load and display log file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                self.text_edit.setPlainText(content)
        except Exception as e:
            self.text_edit.setPlainText(f"Error loading log file: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        self.text_edit.clear()

# Register custom pane type
class LogViewerPaneType(PaneType):
    LOG_VIEWER = "log_viewer"

def create_log_viewer(config: PaneConfiguration) -> QWidget:
    return LogViewerPane(config)

# Add to application
pane_manager.register_pane_type(LogViewerPaneType.LOG_VIEWER, create_log_viewer)
```

### Plugin Development

```python
from src.rfu.file_explorer.core.plugin import Plugin
from src.rfu.file_explorer.core.plugin_manager import PluginManager

class ExamplePlugin(Plugin):
    """Example plugin implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "Demonstrates plugin development"
        self.author = "Developer Name"
    
    def initialize(self, application):
        """Initialize plugin with application context."""
        self.application = application
        
        # Add menu items
        self.add_menu_actions()
        
        # Register custom file handlers
        self.register_file_handlers()
    
    def add_menu_actions(self):
        """Add plugin actions to application menu."""
        menu_manager = self.application.menu_manager
        
        menu_manager.add_action(
            "Tools",
            "Example Action",
            self.execute_example_action,
            shortcut="Ctrl+Shift+E"
        )
    
    def register_file_handlers(self):
        """Register custom file type handlers."""
        from src.rfu.file_explorer.models.file_type_manager import FileTypeManager
        
        file_type_manager = FileTypeManager.get_instance()
        file_type_manager.register_handler(CustomFileHandler())
    
    def execute_example_action(self):
        """Execute plugin's main action."""
        # Plugin functionality implementation
        pass
    
    def cleanup(self):
        """Clean up plugin resources."""
        # Remove menu items, disconnect signals, etc.
        pass

# Plugin loading
plugin_manager = PluginManager()
plugin_manager.load_plugin(ExamplePlugin())
```

## Debugging and Profiling

### Logging Configuration

```python
import logging
from src.rfu.file_explorer.core.log_manager import LogManager

# Configure logging
log_manager = LogManager()
logger = log_manager.get_logger(__name__)

# Usage in components
class FileExplorerPane:
    def __init__(self):
        self.logger = log_manager.get_logger(self.__class__.__name__)
    
    def load_directory(self, path: str):
        """Load directory with logging."""
        self.logger.info(f"Loading directory: {path}")
        
        try:
            # Directory loading logic
            self.logger.debug(f"Successfully loaded {file_count} files")
        except Exception as e:
            self.logger.error(f"Failed to load directory {path}: {e}", exc_info=True)
```

### Performance Profiling

```python
import cProfile
import pstats
from src.rfu.file_explorer.utils.profiler import ProfileManager

# Profile specific operations
def profile_directory_loading():
    """Profile directory loading performance."""
    profiler = cProfile.Profile()
    
    profiler.enable()
    # Perform operation to profile
    load_large_directory()
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Memory profiling
from src.rfu.file_explorer.utils.memory_profiler import MemoryProfiler

def profile_memory_usage():
    """Profile memory usage patterns."""
    profiler = MemoryProfiler()
    
    profiler.start()
    
    # Perform memory-intensive operations
    cache_manager = CacheManager(database, max_cache_size=50000)
    for i in range(10000):
        cache_manager.put(f"key_{i}", {"data": f"value_{i}"})
    
    memory_report = profiler.stop()
    print(f"Peak memory usage: {memory_report.peak_memory_mb:.1f} MB")
```

### Debug Tools

#### Qt Inspector
```python
# Enable Qt debugging
import os
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.debug=true'

# Debug widget hierarchy
from PyQt5.QtCore import QCoreApplication
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
```

#### Debug Mode
```python
# Run application in debug mode
if __name__ == '__main__':
    import sys
    
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Enable Qt debug output
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
    
    # Create main application with debug features
    main_app = MainApplication(debug=True)
    main_app.show()
    
    sys.exit(app.exec_())
```

---

**Developer Guide Version**: 1.0.0  
**Last Updated**: 2025-09-12  
**Target Audience**: Contributors, Plugin Developers, Integrators