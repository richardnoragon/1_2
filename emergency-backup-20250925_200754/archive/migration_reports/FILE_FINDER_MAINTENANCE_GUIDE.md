# FileFinderWindow Maintenance Guide
**Development and Maintenance Guidelines for the Migrated FileFinderWindow**

**Document Version:** 1.0  
**Created:** 2025-01-26  
**Migration Status:** Completed Successfully  
**Package Location:** `file_utilities_1/file_finder.py`  

---

## Table of Contents

1. [Overview](#overview)
2. [Development Guidelines](#development-guidelines)
3. [Testing Guidelines](#testing-guidelines)
4. [Migration Lessons Learned](#migration-lessons-learned)
5. [Code Style and Architecture Patterns](#code-style-and-architecture-patterns)
6. [Adding New Features](#adding-new-features)
7. [Maintaining Package Consistency](#maintaining-package-consistency)
8. [Performance Optimization](#performance-optimization)
9. [Error Handling Best Practices](#error-handling-best-practices)
10. [Future Enhancement Roadmap](#future-enhancement-roadmap)

---

## Overview

This maintenance guide provides comprehensive guidelines for future development and maintenance of the FileFinderWindow component within the `file_utilities_1` package. The guidelines are based on lessons learned from the successful migration and established best practices.

### Current Status
✅ **Migration completed successfully** with zero breaking changes  
✅ **All critical issues resolved** (pathlib import, UI loading, error handling)  
✅ **100% backward compatibility** maintained through wrapper pattern  
✅ **Comprehensive testing** with 87/87 tests passing  
✅ **Enhanced architecture** with improved organization and maintainability  

### Maintenance Principles
- **Backward Compatibility:** Always maintain compatibility with existing integrations
- **Code Quality:** Follow established patterns and maintain high code quality
- **Testing First:** Comprehensive testing for all changes
- **Documentation:** Keep documentation current and comprehensive
- **Performance:** Maintain or improve performance with each change

---

## Development Guidelines

### 1. How to Add New Features to FileFinderWindow

#### 1.1 Feature Planning Process

**Step 1: Requirements Analysis**
```markdown
1. Define the feature requirements clearly
2. Identify integration points with existing functionality
3. Assess impact on backward compatibility
4. Plan testing strategy
5. Document expected behavior
```

**Step 2: Design Considerations**
```markdown
1. Follow existing architectural patterns
2. Maintain consistency with BaseWindow inheritance
3. Consider UI/UX impact
4. Plan for error handling
5. Design for testability
```

**Step 3: Implementation Guidelines**
```markdown
1. Create feature branch from main
2. Implement following established patterns
3. Add comprehensive tests
4. Update documentation
5. Test backward compatibility
```

#### 1.2 Adding New Search Capabilities

**Example: Adding Regular Expression Search**

```python
# 1. Add method to FileFinderWindow class
def search_with_regex(self, pattern: str, content: str) -> bool:
    """Search content using regular expression pattern.
    
    Args:
        pattern: Regular expression pattern
        content: Content to search
        
    Returns:
        True if pattern matches, False otherwise
        
    Raises:
        re.error: If pattern is invalid
    """
    try:
        import re
        return bool(re.search(pattern, content, re.IGNORECASE))
    except re.error as e:
        self.logger.error(f"Invalid regex pattern '{pattern}': {e}")
        return False

# 2. Integrate with existing search methods
def search_file_content(self, file_path: str, search_text: str) -> bool:
    """Enhanced to support regex if enabled."""
    if self.regex_enabled:  # New UI checkbox
        return self.search_with_regex(search_text, file_content)
    else:
        # Existing implementation
        return search_text.lower() in file_content.lower()

# 3. Add UI controls (in _set_initial_state)
self.regex_check = QCheckBox("Use Regular Expressions")
self.regex_check.setToolTip("Enable regular expression pattern matching")

# 4. Update FileFinder wrapper for test compatibility
def __init__(self, config_manager=None):
    # ... existing code ...
    self.regex_check = QCheckBox("Use Regular Expressions")
    # Map to GUI checkbox
    self.regex_check.stateChanged.connect(
        lambda state: self.gui.regex_check.setChecked(state == 2)
    )
```

### 2. Best Practices for Maintaining file_utilities_1 Package Consistency

#### 2.1 Package Structure Standards

**Directory Organization:**
```
file_utilities_1/
├── __init__.py                 # Package exports and metadata
├── {utility_name}.py          # Main implementation
├── {utility_name}.ui          # UI definition
└── icons/                     # Utility-specific icons
    └── {utility_name}.png
```

**Naming Conventions:**
- **Classes:** `{UtilityName}Window` (e.g., `FileFinderWindow`, `CatalogWindow`)
- **Files:** `{utility_name}.py` (e.g., `file_finder.py`, `catalog.py`)
- **UI Files:** `{utility_name}.ui` (e.g., `file_finder.ui`, `catalog.ui`)
- **Icons:** `{utility_name}.png` or descriptive names

#### 2.2 Class Architecture Standards

**Base Class Inheritance:**
```python
from gui.common.base_window import BaseWindow

class NewUtilityWindow(BaseWindow):
    """Follow the established pattern."""
    
    def __init__(self, config_manager=None) -> None:
        """Standard constructor signature."""
        super().__init__()
        self.config_manager = config_manager
        self.logger = LogManager().get_logger('NewUtility')
        
        self._init_models()
        self._setup_ui()
        self._setup_icons()
        self._connect_signals()
        self._set_initial_state()
```

**Required Methods Pattern:**
```python
def _init_models(self) -> None:
    """Initialize data models and internal state."""
    pass

def _setup_ui(self) -> None:
    """Initialize and load the UI file."""
    try:
        ui_file = Path(__file__).parent / "new_utility.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"UI file not found: {ui_file}")
        uic.loadUi(str(ui_file), self)
    except Exception as e:
        show_error_dialog(f"Failed to initialize UI: {e}", "Error", self)
        sys.exit(1)

def _setup_icons(self) -> None:
    """Setup icons and UI styling."""
    pass

def _connect_signals(self) -> None:
    """Connect UI signals to their respective slots."""
    pass

def _set_initial_state(self) -> None:
    """Set the initial state of UI elements."""
    pass
```

---

## Testing Guidelines

### 1. How to Add New Tests for FileFinderWindow Functionality

#### 1.1 Test Structure Standards

**Test File Organization:**
```
tests/
├── test_file_finder.py         # Main functionality tests
├── test_file_finder_integration.py  # Integration tests
├── test_file_finder_ui.py      # UI-specific tests
└── test_file_finder_performance.py  # Performance tests
```

**Test Class Structure:**
```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from file_utilities_1 import FileFinderWindow
from file_finder import FileFinder  # Backward compatibility

class TestFileFinderWindow(unittest.TestCase):
    """Test FileFinderWindow functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = Mock()
        self.finder = FileFinderWindow(self.config_manager)
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'finder'):
            self.finder.close()
    
    def test_initialization(self):
        """Test proper initialization."""
        self.assertIsNotNone(self.finder)
        self.assertEqual(self.finder.config_manager, self.config_manager)
        
    def test_new_feature(self):
        """Test new feature functionality."""
        # Test implementation
        pass
```

### 2. Integration Testing Procedures for New Features

#### 2.1 RFU Hub Integration Testing

**Integration Test Template:**
```python
class TestRFUHubIntegration(unittest.TestCase):
    """Test integration with RFU Hub."""
    
    @patch('file_utilities_1.FileFinderWindow')
    def test_rfuhub_import(self, mock_finder):
        """Test RFU Hub can import and instantiate FileFinderWindow."""
        from rfuhub import MyGUI
        
        hub = MyGUI()
        hub.open_file_finder()
        
        mock_finder.assert_called_once()
        mock_finder.return_value.show.assert_called_once()
```

### 3. Regression Testing Requirements

#### 3.1 Automated Regression Test Suite

**Regression Test Checklist:**
```python
class TestRegression(unittest.TestCase):
    """Comprehensive regression testing."""
    
    def test_all_imports_work(self):
        """Test all import patterns work."""
        # New imports
        from file_utilities_1 import FileFinderWindow
        from file_utilities_1.file_finder import FileFinderWindow as FFW
        
        # Backward compatible imports
        from file_finder import FileFinder
        
        # All should work without errors
        self.assertTrue(True)
    
    def test_existing_functionality_preserved(self):
        """Test all existing functionality still works."""
        finder = FileFinderWindow()
        
        # Test core methods exist and are callable
        core_methods = [
            'select_directory', 'search', 'open_file', 'show_metadata',
            'get_files', 'search_file_content'
        ]
        for method in core_methods:
            self.assertTrue(hasattr(finder, method))
            self.assertTrue(callable(getattr(finder, method)))
```

---

## Migration Lessons Learned

### 1. Key Insights from This Migration Project

#### 1.1 Critical Success Factors

**1. Comprehensive Planning**
- **Lesson:** Detailed migration planning prevented major issues
- **Application:** Always create comprehensive migration plans for future moves
- **Evidence:** Zero breaking changes achieved through careful planning

**2. Backward Compatibility First**
- **Lesson:** Maintaining backward compatibility is crucial for adoption
- **Application:** Always provide compatibility layers for existing integrations
- **Evidence:** 100% test compatibility maintained through wrapper pattern

**3. Incremental Testing**
- **Lesson:** Test each phase before proceeding to the next
- **Application:** Implement comprehensive testing at each migration step
- **Evidence:** 87/87 tests passing with systematic testing approach

#### 1.2 Technical Insights

**1. Relative Path Resolution**
```python
# LESSON: Use relative paths for package resources
# BEFORE (problematic):
super().__init__(os.path.join(SCRIPT_DIR, 'file_finder.ui'))

# AFTER (robust):
ui_file = Path(__file__).parent / "file_finder.ui"
uic.loadUi(str(ui_file), self)
```

**2. Import Dependency Management**
```python
# LESSON: Verify all imports are present and correct
# CRITICAL FIXES APPLIED:
import pathlib  # Was missing, caused runtime error
import traceback  # Was missing, limited error handling
```

### 2. Best Practices for Future Package Migrations

#### 2.1 Pre-Migration Checklist

**Planning Phase:**
```markdown
□ Create comprehensive migration plan
□ Identify all integration points
□ Analyze dependencies and imports
□ Plan backward compatibility strategy
□ Design testing approach
□ Prepare rollback procedures
```

#### 2.2 Migration Execution Best Practices

**Phase-by-Phase Approach:**
```markdown
Phase 1: Preparation and Setup
- Create target directory structure
- Backup original files
- Fix critical issues in place

Phase 2: Core Migration
- Move files to new location
- Update import statements
- Fix path resolution issues
- Rename classes for consistency

Phase 3: Integration Updates
- Update all integration points
- Modify test imports
- Create compatibility wrappers

Phase 4: Testing and Validation
- Run comprehensive test suite
- Perform integration testing
- Validate UI functionality
- Test error handling

Phase 5: Documentation and Cleanup
- Update documentation
- Clean up temporary files
- Finalize migration logs
```

### 3. Common Pitfalls and How to Avoid Them

#### 3.1 Import and Dependency Issues

**Pitfall: Missing Import Dependencies**
```python
# PROBLEM: Using modules without importing them
file_info = pathlib.Path(full_path)  # pathlib not imported

# SOLUTION: Systematic import verification
import pathlib  # Add missing imports
from pathlib import Path  # Use consistent import style
```

**Prevention Strategy:**
- Use static analysis tools to check imports
- Test import statements in isolation
- Maintain import dependency documentation

#### 3.2 Path Resolution Problems

**Pitfall: Hardcoded File Paths**
```python
# PROBLEM: Hardcoded paths break in new structure
super().__init__(os.path.join(SCRIPT_DIR, 'file_finder.ui'))

# SOLUTION: Relative path resolution
ui_file = Path(__file__).parent / "file_finder.ui"
```

**Prevention Strategy:**
- Always use relative paths for package resources
- Test path resolution in different environments
- Implement robust error handling for missing files

---

## Code Style and Architecture Patterns

### 1. Established Patterns to Follow

#### 1.1 Class Design Patterns

**BaseWindow Inheritance Pattern:**
```python
class UtilityWindow(BaseWindow):
    """Standard utility window pattern."""
    
    def __init__(self, config_manager=None) -> None:
        """Standard constructor pattern."""
        super().__init__()
        self.config_manager = config_manager
        self.logger = LogManager().get_logger('UtilityName')
        self.logger.info('Initializing Utility')
        
        # Standard initialization sequence
        self._init_models()
        self._setup_ui()
        self._setup_icons()
        self._connect_signals()
        self._set_initial_state()
```

#### 1.2 Error Handling Patterns

**Standard Error Handling:**
```python
def operation_with_error_handling(self, parameter: str) -> bool:
    """Standard error handling pattern."""
    try:
        # Main operation logic
        result = self.perform_operation(parameter)
        self.logger.info(f'Operation completed successfully: {parameter}')
        return result
        
    except FileNotFoundError:
        self.logger.error(f'File not found: {parameter}')
        self.show_user_error(f'File not found: {parameter}')
        return False
        
    except PermissionError:
        self.logger.error(f'Permission denied: {parameter}')
        self.show_user_error(f'Permission denied: {parameter}')
        return False
        
    except Exception as e:
        self.logger.error(f'Unexpected error in operation: {e}', exc_info=True)
        self.show_user_error(f'Operation failed: {str(e)}')
        return False

def show_user_error(self, message: str) -> None:
    """Standard user error display."""
    show_error_dialog(self, "Error", message)
    self.statusbar.showMessage(f"Error: {message}", 5000)
```

#### 1.3 Configuration Management Patterns

**Settings Management Pattern:**
```python
class UtilityWindow(BaseWindow):
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.default_settings = {
            'window_width': 800,
            'window_height': 600,
            'last_directory': '',
            'auto_save': True
        }
        self.load_settings()
    
    def load_settings(self) -> None:
        """Load settings with defaults."""
        if not self.config_manager:
            self.settings = self.default_settings.copy()
            return
        
        saved_settings = self.config_manager.get_config('utility_name', {})
        self.settings = {**self.default_settings, **saved_settings}
        
        # Apply settings to UI
        self.resize(self.settings['window_width'], self.settings['window_height'])
        if self.settings['last_directory']:
            self.directory = self.settings['last_directory']
    
    def save_settings(self) -> None:
        """Save current settings."""
        if not self.config_manager:
            return
        
        self.settings.update({
            'window_width': self.width(),
            'window_height': self.height(),
            'last_directory': getattr(self, 'directory', ''),
        })
        
        self.config_manager.update_config('utility_name', self.settings)
```

---

## Adding New Features

### 1. Feature Development Workflow

#### 1.1 Planning New Features

**Feature Request Template:**
```markdown
## Feature Request: [Feature Name]

### Description
Brief description of the feature and its purpose.

### Requirements
- Functional requirement 1
- Functional requirement 2
- Non-functional requirements (performance, usability)

### Integration Points
- How it integrates with existing functionality
- Impact on UI/UX
- Backward compatibility considerations

### Testing Strategy
- Unit tests required
- Integration tests required
- UI tests required
- Performance tests required

### Implementation Plan
1. Step 1: Design and architecture
2. Step 2: Core implementation
3. Step 3: UI integration
4. Step 4: Testing
5. Step 5: Documentation
```

#### 1.2 Implementation Guidelines

**Feature Implementation Checklist:**
```markdown
□ Follow established architectural patterns
□ Maintain BaseWindow inheritance structure
□ Implement proper error handling
□ Add comprehensive logging
□ Create unit tests
□ Update FileFinder wrapper for compatibility
□ Update documentation
□ Test backward compatibility
□ Verify performance impact
□ Update package exports if needed
```

### 2. Common Feature Types and Patterns

#### 2.1 Adding New File Type Support

**Template for New File Type:**
```python
# 1. Extend file type detection
def get_files(self, ...):
    """Add new file type to extensions."""
    extensions = []
    if office:
        extensions.extend(['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt'])
    if media:
        extensions.extend(['mp3', 'mp4', 'avi', 'mkv', 'jpg', 'png', 'gif'])
    if new_type:  # Add new file type
        extensions.extend(['ext1', 'ext2', 'ext3'])
    if all_files:
        extensions = ['*']

# 2. Add content search support
def search_new_type_content(self, file_path: str, search_text: str) -> bool:
    """Search content in new file type."""
    try:
        # Implementation specific to file type
        return self._search_specific_format(file_path, search_text)
    except Exception as e:
        self.logger.error(f"Error searching {file_path}: {e}")
        return False

# 3. Update UI
def _set_initial_state(self):
    # ... existing code ...
    self.new_type_checkBox = QCheckBox("New File Type")
    # Add to layout and connect signals

# 4. Update wrapper for compatibility
def __init__(self, config_manager=None):
    # ... existing code ...
    self.new_type_check = QCheckBox("New File Type")
    # Connect to GUI checkbox
```

#### 2.2 Adding New Search Filters

**Template for New Filter:**
```python
# 1. Add filter logic
def apply_new_filter(self, file_path: str, filter_value: Any) -> bool:
    """Apply new filter to file."""
    try:
        # Filter implementation
        return self._check_filter_condition(file_path, filter_value)
    except Exception as e:
        self.logger.error(f"Error applying filter to {file_path}: {e}")
        return True  # Include file if filter fails

# 2. Integrate with search
def get_files(self, ...):
    """Enhanced with new filter."""
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            
            # Existing filters
            if not self.in_date_range(...):
                continue
            
            # New filter
            if not self.apply_new_filter(file_path, filter_value):
                continue
            
            files.append(relative_path)

# 3. Add UI controls
def _set_initial_state(self):
    # ... existing code ...
    self.new_filter_widget = QWidget()  # Appropriate widget type
    # Configure and add to layout
```

---

## Maintaining Package Consistency

### 1. Package Organization Standards

#### 1.1 File Naming and Structure

**Consistent Naming Pattern:**
```
file_utilities_1/
├── __init__.py
├── catalog.py              # CatalogWindow
├── catalog.ui
├── file_finder.py          # FileFinderWindow
├── file_finder.ui
├── new_utility.py          # NewUtilityWindow
├── new_utility.ui
└── icons/
    ├── catalog.png
    ├── folder.png
    ├── search.png
    └── new_utility.png
```

#### 1.2 Class Naming Standards

**Naming Convention Rules:**
- **Main Classes:** `{UtilityName}Window` (inherits from BaseWindow)
- **Logic Classes:** `{UtilityName}Logic` (core functionality)
- **Wrapper Classes:** `{UtilityName}` (backward compatibility)

**Example:**
```python
# Main implementation
class FileFinderWindow(BaseWindow):
    """Main GUI implementation."""
    pass

# Core logic (if separated)
class FileFinderLogic:
    """Core business logic."""
    pass

# Backward compatibility wrapper
class FileFinder(QDialog):
    """Backward compatibility wrapper."""
    def __init__(self, config_manager=None):
        self.gui = FileFinderWindow(config_manager)
```

### 2. Integration Standards

#### 2.1 Package Export Standards

**__init__.py Template:**
```python
"""
File Utilities Package 1

This package contains file management utilities including:
- catalog.py: File catalog generator with HTML report functionality
- file_finder.py: Advanced file search and metadata viewer
- new_utility.py: Description of new utility functionality
"""

from .catalog import CatalogWindow
from .file_finder import FileFinderWindow
from .new_utility import NewUtilityWindow

__all__ = ['CatalogWindow', 'FileFinderWindow', 'NewUtilityWindow']

# Package metadata
__version__ = '1.0.0'
__author__ = 'Development Team'
__description__ = 'File management utilities package'
```

#### 2.2 RFU Hub Integration Standards

**Integration Method Template:**
```python
# In rfuhub.py
def open_new_utility(self) -> None:
    """Open new utility."""
    try:
        from file_utilities_1 import NewUtilityWindow
        self.new_utility_window = NewUtilityWindow()
        self.new_utility_window.show()
    except ImportError as e:
        print(f"Error loading new utility: {e}")
        # Optional: Show user-friendly error dialog
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(
            self, "Utility Not Available",
            f"New Utility could not be loaded: {e}"
        )
```

---

## Performance Optimization

### 1. Performance Monitoring Guidelines

#### 1.1 Performance Metrics to Track

**Key Performance Indicators:**
```python
import time
import psutil
import os

class PerformanceMonitor:
    """Monitor FileFinderWindow performance."""
    
    def __init__(self):
        self.start_time = None
        self.memory_start = None
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.memory_start = process.memory_info().rss
    
    def end_monitoring(self, operation_name: str):
        """End monitoring and log results."""
        if self.start_time is None:
            return
        
        duration = time.time() - self.start_time
        process = psutil.Process(os.getpid())
        memory_end = process.memory_info().rss
        memory_delta = memory_end - self.memory_start
        
        print(f"{operation_name} Performance:")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Memory Delta: {memory_delta / 1024 / 1024:.2f} MB")

# Usage in FileFinderWindow
def search(self):
    """Search with performance monitoring."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    try:
        # Existing search logic
        files = self.get_files(...)
        # Update UI
        for file_path in files:
            self.model.appendRow(QStandardItem(file_path))
    finally:
        monitor.end_monitoring("File Search")
```

#### 1.2 Performance Optimization Techniques

**Search Optimization:**
```python
def get_files_optimized(self, ...):
    """Optimized file search with early filtering."""
    files = []
    
    # Pre-compile regex patterns if using regex
    if self.use_regex and hasattr(self, 'pattern'):
        try:
            import re
            compiled_pattern = re.compile(self.pattern, re.IGNORECASE)
        except re.error:
            compiled_pattern = None
    
    # Use os.scandir for better performance than os.walk
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file():
                    # Early filtering to avoid unnecessary processing
                    if not self._quick_filter_check(entry.name, extensions):
                        continue
                    
                    # More expensive checks only if needed
                    if not self.in_date_range(entry.path, ...):
                        continue
                    
                    files.append(os.path.relpath(entry.path, directory))
                elif entry.is_dir() and recursive:
                    # Recursive call for subdirectories
                    subfiles = self.get_files_optimized(entry.path, ...)
                    files.extend(subfiles)
    except PermissionError:
        self.logger.warning(f"Permission denied accessing {directory}")
    
    return files

def _quick_filter_check(self, filename: str, extensions: List[str]) -> bool:
    """Quick filename-based filtering."""
    if extensions == ['*']:
        return True
    
    if '.' not in filename:
        return False
    
    file_ext = filename.split('.')[-1].lower()
    return file_ext in extensions
```

### 2. Memory Management

#### 2.1 Efficient Data Handling

**Large Result Set Management:**
```python
class FileFinderWindow(BaseWindow):
    def __init__(self, config_manager=None):
        super().__init__()
        self.max_results = 10000  # Limit results to prevent memory issues
        self.result_batch_size = 100  # Process results in batches
    
    def search(self):
        """Search with memory-efficient result handling."""
        self.model.clear()
        self.meta_model.removeRows(0, self.meta_model.rowCount())
        
        files = self.get_files(...)
        
        # Limit results to prevent memory issues
        if len(files) > self.max_results:
            files = files[:self.max_results]
            self.statusbar.showMessage(
                f"Showing first {self.max_results} of {len(files)} results",
                5000
            )
        
        # Add results in batches to keep UI responsive
        self._add_results_in_batches(files)
    
    def _add_results_in_batches(self, files: List[str]):
        """Add results to model in batches."""
        from PyQt5.QtCore import QTimer
        
        self.current_batch = 0
        self.files_to_add = files
        
        # Use timer to add results progressively
        self.batch_timer = QTimer()
        self.batch_timer.timeout.connect(self._add_next_batch)
        self.batch_timer.start(10)  # Add batch every 10ms
    
    def _add_next_batch(self):
        """Add next batch of results."""
        start_idx = self.current_batch * self.result_batch_size
        end_idx = min(start_idx + self.result_batch_size, len(self.files_to_add))
        
        if start_idx >= len(self.files_to_add):
            self.batch_timer.stop()
            self.statusbar.showMessage(
                f"Found {len(self.files_to_add)} files", 3000
            )
            return
        
        # Add batch to model
        for i in range(start_idx, end_idx):
            self.model.appendRow(QStandardItem(self.files_to_add[i]))
        
        self.current_batch += 1
        
        # Update progress
        progress = (end_idx / len(self.files_to_add)) * 100
        self.progress_widget.setValue(int(progress))
```

---

## Error Handling Best Practices

### 1. Comprehensive Error Handling Strategy

#### 1.1 Error Classification and Handling

**Error Categories and Responses:**
```python
class FileFinderWindow(BaseWindow):
    def handle_error(self, error: Exception, context: str, file_path: str = None):
        """Centralized error handling."""
        error_type = type(error).__name__
        
        if isinstance(error, FileNotFoundError):
            self._handle_file_not_found(error, context, file_path)
        elif isinstance(error, PermissionError):
            self._handle_permission_error(error, context, file_path)
        elif isinstance(error, OSError):
            self._handle_os_error(error, context, file_path)
        elif isinstance(error, ImportError):
            self._handle_import_error(error, context)
        else:
            self._handle_unexpected_error(error, context, file_path)
    
    def _handle_file_not_found(self, error: FileNotFoundError, context: str, file_path: str):
        """Handle file not found errors."""
        message = f"File not found in {context}"
        if file_path:
            message += f": {file_path}"
        
        self.logger.warning(message)
        self.statusbar.showMessage(message, 3000)
        # Don't show dialog for common file operations
    
    def _handle_permission_error(self, error: PermissionError, context: str, file_path: str):
        """Handle permission errors."""
        message = f"Permission denied in {context}"
        if file_path:
            message += f": {file_path}"
        
        self.logger.error(message)
        self.statusbar.showMessage(message, 5000)
        # Show dialog for critical operations only
        if context in ['ui_loading', 'configuration']:
            show_error_dialog(self, "Permission Error", message)
    
    def _handle_unexpected_error(self, error: Exception, context: str, file_path: str):
        """Handle unexpected errors."""
        message = f"Unexpected error in {context}: {str(error)}"
        if file_path:
            message += f" (file: {file_path})"
        
        self.logger.error(message, exc_info=True)
        show_error_dialog(self, "Unexpected Error", message)
```

#### 1.2 User-Friendly Error Messages

**Error Message Guidelines:**
```python
def show_user_friendly_error(self, error_type: str, details: str = None):