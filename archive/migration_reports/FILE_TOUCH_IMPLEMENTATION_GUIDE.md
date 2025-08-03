# File Touch Utility - Implementation Guide
**Richard's File Utilities Hub - File Touch Integration**

**Document Version:** 1.0  
**Created:** 2025-07-28  
**Status:** Implementation Guide  
**Related Documents:** 
- [FILE_TOUCH_COMPREHENSIVE_MIGRATION_PLAN.md](FILE_TOUCH_COMPREHENSIVE_MIGRATION_PLAN.md)
- [FILE_TOUCH_TECHNICAL_SPECIFICATIONS.md](FILE_TOUCH_TECHNICAL_SPECIFICATIONS.md)

---

## Implementation Overview

This guide provides step-by-step implementation instructions for migrating the file touch utility to the file_utilities_2 architecture. Each phase includes detailed code examples, configuration templates, and validation procedures.

---

## Phase 1: Project Setup and Analysis

### 1.1 Create Backup and Migration Workspace

```bash
# Create backup directory
mkdir -p backup/file_touch_migration/$(date +%Y-%m-%d_%H-%M-%S)

# Backup original files
cp file_touch.py backup/file_touch_migration/$(date +%Y-%m-%d_%H-%M-%S)/
cp file_touch.ui backup/file_touch_migration/$(date +%Y-%m-%d_%H-%M-%S)/
cp file_touch_files.md backup/file_touch_migration/$(date +%Y-%m-%d_%H-%M-%S)/

# Create migration workspace
mkdir -p migration_workspace/file_touch
```

### 1.2 Dependency Analysis Script

```python
# migration_workspace/analyze_dependencies.py
"""
File Touch Dependency Analysis Script
"""

import ast
import os
from pathlib import Path
from typing import Set, Dict, List

class DependencyAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports = set()
        self.dependencies = {}
        
    def analyze_file(self) -> Dict[str, any]:
        """Analyze file dependencies."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.add(node.module)
                    
        return {
            'file': self.file_path,
            'imports': list(self.imports),
            'total_imports': len(self.imports),
            'external_dependencies': self._categorize_imports()
        }
    
    def _categorize_imports(self) -> Dict[str, List[str]]:
        """Categorize imports by type."""
        categories = {
            'standard_library': [],
            'pyqt5': [],
            'local_modules': [],
            'third_party': []
        }
        
        standard_libs = {'os', 'sys', 'datetime', 'platform', 'typing'}
        
        for imp in self.imports:
            if imp in standard_libs or imp.startswith(('os.', 'sys.', 'datetime.')):
                categories['standard_library'].append(imp)
            elif imp.startswith('PyQt5'):
                categories['pyqt5'].append(imp)
            elif imp in ['gui.common.base_window', 'gui.common.dialogs', 'config_manager']:
                categories['local_modules'].append(imp)
            else:
                categories['third_party'].append(imp)
                
        return categories

# Run analysis
if __name__ == "__main__":
    analyzer = DependencyAnalyzer('file_touch.py')
    results = analyzer.analyze_file()
    
    print("File Touch Dependency Analysis")
    print("=" * 40)
    print(f"Total imports: {results['total_imports']}")
    print("\nDependency Categories:")
    for category, deps in results['external_dependencies'].items():
        print(f"  {category}: {len(deps)} dependencies")
        for dep in deps:
            print(f"    - {dep}")
```

### 1.3 Current Architecture Analysis

```python
# migration_workspace/architecture_analyzer.py
"""
Current Architecture Analysis for File Touch
"""

import re
from pathlib import Path
from typing import Dict, List

class ArchitectureAnalyzer:
    def __init__(self):
        self.classes = {}
        self.methods = {}
        self.signals = {}
        
    def analyze_current_structure(self, file_path: str) -> Dict[str, any]:
        """Analyze current file touch structure."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
        classes = re.findall(class_pattern, content)
        
        # Extract methods
        method_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        methods = re.findall(method_pattern, content)
        
        # Extract signals
        signal_pattern = r'(\w+)\s*=\s*pyqtSignal\([^)]*\)'
        signals = re.findall(signal_pattern, content)
        
        return {
            'classes': classes,
            'methods': methods,
            'signals': signals,
            'total_lines': len(content.split('\n')),
            'complexity_score': self._calculate_complexity(content)
        }
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate basic complexity score."""
        # Simple complexity based on control structures
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except']
        score = 0
        for keyword in complexity_keywords:
            score += content.count(f' {keyword} ')
        return score

# Usage
analyzer = ArchitectureAnalyzer()
results = analyzer.analyze_current_structure('file_touch.py')
print("Current Architecture Analysis:")
print(f"Classes: {results['classes']}")
print(f"Methods: {len(results['methods'])}")
print(f"Signals: {results['signals']}")
print(f"Complexity Score: {results['complexity_score']}")
```

---

## Phase 2: Architecture Design and Planning

### 2.1 Target Directory Structure Creation

```bash
# Create target directory structure
mkdir -p file_utilities_2/core
mkdir -p file_utilities_2/gui/icons
mkdir -p file_utilities_2/tests
mkdir -p file_utilities_2/docs
mkdir -p file_utilities_2/templates/file_touch
```

### 2.2 Architecture Design Templates

```python
# migration_workspace/architecture_template.py
"""
File Touch Architecture Template
"""

from typing import Protocol, Dict, Any
from abc import ABC, abstractmethod

class FileTouchLogicProtocol(Protocol):
    """Protocol for file touch logic interface."""
    
    def get_file_timestamps(self, filepath: str) -> None: ...
    def set_file_timestamps(self, filepath: str, atime: int, mtime: int) -> None: ...
    def validate_file_access(self, filepath: str) -> bool: ...

class FileTouchConfigProtocol(Protocol):
    """Protocol for file touch configuration interface."""
    
    def get_setting(self, subsection: str, key: str, default: Any = None) -> Any: ...
    def set_setting(self, subsection: str, key: str, value: Any) -> bool: ...
    def get_profile(self, profile_name: str) -> Dict[str, Any]: ...
    def save_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool: ...

class FileTouchGUIProtocol(Protocol):
    """Protocol for file touch GUI interface."""
    
    def browse_file(self) -> None: ...
    def refresh_timestamps(self) -> None: ...
    def apply_changes(self) -> None: ...
    def save_profile(self) -> None: ...
    def load_profile(self, profile_name: str) -> None: ...
```

---

## Phase 3: Core Logic Migration

### 3.1 Create Core Logic Module

```python
# file_utilities_2/core/file_touch_logic.py
"""
File Touch Core Logic Module

Enhanced file timestamp manipulation with file_utilities_2 integration.
"""

import os
import platform
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from file_utilities_2.integration.hub_connector import HubIntegratedTool
from .file_touch_config import FileTouchConfig
from .file_touch_logging import get_file_touch_logger


class FileTouchLogic(HubIntegratedTool):
    """Enhanced file touch logic with hub integration."""
    
    # Enhanced signals for hub integration
    timestamps_fetched = pyqtSignal(dict)  # {access, modification, creation}
    operation_result = pyqtSignal(bool, str)  # success, message
    error_occurred = pyqtSignal(str)  # error_message
    progress_updated = pyqtSignal(int, str)  # percentage, status
    finished = pyqtSignal()  # operation_complete
    
    def __init__(self, config: FileTouchConfig = None):
        """Initialize file touch logic with hub integration."""
        super().__init__("file_touch")
        
        self.config = config or FileTouchConfig()
        self.logger = get_file_touch_logger()
        self._is_running = False
        self._operation_timeout = self.config.get_setting('operations', 'operation_timeout', 30)
        
        # Setup operation timer
        self._timeout_timer = QTimer()
        self._timeout_timer.timeout.connect(self._handle_timeout)
        self._timeout_timer.setSingleShot(True)
        
        # Report tool started
        self.report_tool_started({
            'version': '2.0.0',
            'features': ['timestamp_modification', 'profile_management', 'hub_integration'],
            'config_loaded': True
        })
        
        self.logger.log_core_logic('info', "File Touch Logic initialized with hub integration")
    
    def stop(self) -> None:
        """Stop the current operation."""
        if self._is_running:
            self._is_running = False
            self._timeout_timer.stop()
            self.logger.log_core_logic('info', "Operation stopped by user request")
            self.report_tool_progress(0, "Operation cancelled")
    
    def get_file_timestamps(self, filepath: str) -> None:
        """
        Fetches access, modification, and creation timestamps for a file.
        Enhanced with hub integration and comprehensive error handling.
        """
        if self._is_running:
            self.error_occurred.emit("Another operation is already in progress")
            return
            
        self._is_running = True
        self._timeout_timer.start(self._operation_timeout * 1000)
        
        try:
            # Report operation start
            self.report_tool_progress(10, f"Analyzing file: {os.path.basename(filepath)}")
            self.logger.log_file_operation('get_timestamps', filepath, True)
            
            # Validate file
            if not self._validate_file_path(filepath):
                return
                
            self.report_tool_progress(30, "Reading file metadata")
            
            # Get file statistics
            stat_result = os.stat(filepath)
            
            self.report_tool_progress(60, "Processing timestamps")
            
            # Access Time (atime)
            atime_ts = stat_result.st_atime
            atime_dt = datetime.fromtimestamp(atime_ts, tz=timezone.utc).astimezone()
            
            # Modification Time (mtime)
            mtime_ts = stat_result.st_mtime
            mtime_dt = datetime.fromtimestamp(mtime_ts, tz=timezone.utc).astimezone()
            
            # Creation Time (platform-specific)
            ctime_dt = self._get_creation_time(stat_result)
            
            self.report_tool_progress(90, "Formatting results")
            
            result = {
                'access': atime_dt,
                'modification': mtime_dt,
                'creation': ctime_dt,
                'file_size': stat_result.st_size,
                'file_mode': stat_result.st_mode
            }
            
            self.report_tool_progress(100, "Timestamps retrieved successfully")
            
            # Emit results
            self.timestamps_fetched.emit(result)
            self.operation_result.emit(True, "Timestamps fetched successfully")
            
            # Log success
            self.logger.log_core_logic('info', f"Successfully retrieved timestamps for {filepath}")
            
        except FileNotFoundError as e:
            self._handle_error("File not found", str(e), filepath)
        except PermissionError as e:
            self._handle_error("Permission denied", str(e), filepath)
        except Exception as e:
            self._handle_error("Unexpected error", str(e), filepath)
        finally:
            self._cleanup_operation()
    
    def set_file_timestamps(self, filepath: str, atime: int = None, mtime: int = None) -> None:
        """
        Sets the access and modification timestamps for a file.
        Enhanced with backup, validation, and hub integration.
        """
        if self._is_running:
            self.error_occurred.emit("Another operation is already in progress")
            return
            
        self._is_running = True
        self._timeout_timer.start(self._operation_timeout * 1000)
        
        try:
            # Report operation start
            self.report_tool_progress(10, f"Preparing to modify: {os.path.basename(filepath)}")
            
            # Validate inputs
            if not self._validate_file_path(filepath):
                return
                
            if atime is None and mtime is None:
                self._handle_error("Invalid input", "No timestamps specified for modification", filepath)
                return
                
            self.report_tool_progress(20, "Validating file access")
            
            # Check if backup is needed
            backup_data = None
            if self.config.get_setting('operations', 'backup_before_changes', False):
                backup_data = self._create_timestamp_backup(filepath)
                
            self.report_tool_progress(40, "Reading current timestamps")
            
            # Get current timestamps
            current_stat = os.stat(filepath)
            target_atime = atime if atime is not None else current_stat.st_atime
            target_mtime = mtime if mtime is not None else current_stat.st_mtime
            
            self.report_tool_progress(60, "Applying timestamp changes")
            
            # Apply timestamps
            os.utime(filepath, (target_atime, target_mtime))
            
            self.report_tool_progress(80, "Verifying changes")
            
            # Verify the changes
            if self.config.get_setting('operations', 'validate_timestamps', True):
                self._verify_timestamp_changes(filepath, target_atime, target_mtime)
                
            self.report_tool_progress(100, "Timestamps updated successfully")
            
            # Log the operation
            self.logger.log_timestamp_change(
                filepath, 
                {'atime': current_stat.st_atime, 'mtime': current_stat.st_mtime},
                {'atime': target_atime, 'mtime': target_mtime}
            )
            
            # Broadcast file modification event
            self.hub_connector.broadcast_event('file_modified', {
                'filepath': filepath,
                'operation': 'timestamp_change',
                'tool': 'file_touch'
            })
            
            self.operation_result.emit(True, f"Timestamps updated successfully for {os.path.basename(filepath)}")
            
        except FileNotFoundError as e:
            self._handle_error("File not found", str(e), filepath)
        except PermissionError as e:
            self._handle_error("Permission denied", str(e), filepath)
        except Exception as e:
            self._handle_error("Unexpected error", str(e), filepath)
        finally:
            self._cleanup_operation()
    
    def batch_process_files(self, filepaths: List[str], operation: str, settings: Dict[str, Any]) -> None:
        """Process multiple files in batch."""
        if self._is_running:
            self.error_occurred.emit("Another operation is already in progress")
            return
            
        self._is_running = True
        total_files = len(filepaths)
        processed = 0
        errors = []
        
        try:
            self.report_tool_progress(0, f"Starting batch operation on {total_files} files")
            
            for i, filepath in enumerate(filepaths):
                if not self._is_running:  # Check for cancellation
                    break
                    
                try:
                    progress = int((i / total_files) * 100)
                    self.report_tool_progress(progress, f"Processing {os.path.basename(filepath)}")
                    
                    if operation == 'get_timestamps':
                        self.get_file_timestamps(filepath)
                    elif operation == 'set_timestamps':
                        atime = settings.get('atime')
                        mtime = settings.get('mtime')
                        self.set_file_timestamps(filepath, atime, mtime)
                        
                    processed += 1
                    
                except Exception as e:
                    errors.append(f"{filepath}: {str(e)}")
                    self.logger.log_error(f"Batch processing error for {filepath}", e)
                    
            # Report completion
            success_rate = (processed / total_files) * 100 if total_files > 0 else 0
            message = f"Batch operation completed: {processed}/{total_files} files processed ({success_rate:.1f}%)"
            
            if errors:
                message += f", {len(errors)} errors"
                
            self.report_tool_progress(100, message)
            self.operation_result.emit(len(errors) == 0, message)
            
        except Exception as e:
            self._handle_error("Batch operation failed", str(e), "multiple files")
        finally:
            self._cleanup_operation()
    
    def _validate_file_path(self, filepath: str) -> bool:
        """Validate file path for security and accessibility."""
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                self._handle_error("File not found", f"File does not exist: {filepath}", filepath)
                return False
                
            # Check if it's actually a file
            if not os.path.isfile(filepath):
                self._handle_error("Invalid file", f"Path is not a file: {filepath}", filepath)
                return False
                
            # Security validation
            if self.config.get_setting('operations', 'validate_file_paths', True):
                # Prevent path traversal attacks
                normalized_path = os.path.normpath(filepath)
                if '..' in normalized_path:
                    self._handle_error("Security violation", "Path traversal detected", filepath)
                    return False
                    
            return True
            
        except Exception as e:
            self._handle_error("Validation error", str(e), filepath)
            return False
    
    def _get_creation_time(self, stat_result) -> Optional[datetime]:
        """Get creation time in a platform-specific way."""
        try:
            ctime_dt = None
            
            # Try to get birth time (macOS, BSD)
            if hasattr(stat_result, 'st_birthtime') and stat_result.st_birthtime:
                ctime_ts = stat_result.st_birthtime
                ctime_dt = datetime.fromtimestamp(ctime_ts, tz=timezone.utc).astimezone()
            elif platform.system() == "Windows":
                # On Windows, ctime is creation time
                ctime_ts = stat_result.st_ctime
                ctime_dt = datetime.fromtimestamp(ctime_ts, tz=timezone.utc).astimezone()
            # On Linux, ctime is change time, not creation time
            
            return ctime_dt
            
        except Exception as e:
            self.logger.log_error("Error getting creation time", e)
            return None
    
    def _create_timestamp_backup(self, filepath: str) -> Dict[str, float]:
        """Create a backup of current timestamps."""
        try:
            stat_result = os.stat(filepath)
            backup = {
                'atime': stat_result.st_atime,
                'mtime': stat_result.st_mtime,
                'ctime': stat_result.st_ctime,
                'backup_time': datetime.now().timestamp()
            }
            
            self.logger.log_core_logic('debug', f"Created timestamp backup for {filepath}")
            return backup
            
        except Exception as e:
            self.logger.log_error(f"Failed to create backup for {filepath}", e)
            return {}
    
    def _verify_timestamp_changes(self, filepath: str, expected_atime: float, expected_mtime: float) -> bool:
        """Verify that timestamp changes were applied correctly."""
        try:
            stat_result = os.stat(filepath)
            
            # Allow small tolerance for floating point precision
            tolerance = 1.0  # 1 second tolerance
            
            atime_ok = abs(stat_result.st_atime - expected_atime) <= tolerance
            mtime_ok = abs(stat_result.st_mtime - expected_mtime) <= tolerance
            
            if not (atime_ok and mtime_ok):
                self.logger.log_error(
                    f"Timestamp verification failed for {filepath}",
                    None,
                    {
                        'expected_atime': expected_atime,
                        'actual_atime': stat_result.st_atime,
                        'expected_mtime': expected_mtime,
                        'actual_mtime': stat_result.st_mtime
                    }
                )
                return False
                
            return True
            
        except Exception as e:
            self.logger.log_error(f"Timestamp verification error for {filepath}", e)
            return False
    
    def _handle_error(self, error_type: str, message: str, filepath: str = None):
        """Handle errors with comprehensive logging and reporting."""
        full_message = f"{error_type}: {message}"
        if filepath:
            full_message += f" (File: {filepath})"
            
        # Log the error
        self.logger.log_error(full_message)
        
        # Report to hub
        self.report_tool_error(full_message, {
            'error_type': error_type,
            'filepath': filepath,
            'timestamp': datetime.now().isoformat()
        })
        
        # Emit error signal
        self.error_occurred.emit(full_message)
        self.operation_result.emit(False, full_message)
    
    def _handle_timeout(self):
        """Handle operation timeout."""
        if self._is_running:
            self._handle_error("Operation timeout", f"Operation exceeded {self._operation_timeout} seconds")
            self._cleanup_operation()
    
    def _cleanup_operation(self):
        """Clean up after operation completion."""
        self._is_running = False
        self._timeout_timer.stop()
        self.finished.emit()
        
        # Report operation completion
        self.report_tool_progress(100, "Operation completed")
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop()
        self._timeout_timer.stop()
        self.cleanup_hub_integration()
        self.logger.log_core_logic('info', "File Touch Logic cleaned up")
```

### 3.2 Enhanced Error Handling

```python
# file_utilities_2/core/file_touch_errors.py
"""
File Touch Error Handling Module
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class FileTouchErrorType(Enum):
    """Error types for File Touch operations."""
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_TIMESTAMP = "invalid_timestamp"
    OPERATION_TIMEOUT = "operation_timeout"
    CONFIGURATION_ERROR = "configuration_error"
    HUB_COMMUNICATION_ERROR = "hub_communication_error"
    VALIDATION_ERROR = "validation_error"
    SECURITY_VIOLATION = "security_violation"

class FileTouchError(Exception):
    """Custom exception for File Touch operations."""
    
    def __init__(self, error_type: FileTouchErrorType, message: str, 
                 filepath: str = None, details: Dict[str, Any] = None):
        self.error_type = error_type
        self.message = message
        self.filepath = filepath
        self.details = details or {}
        self.timestamp = datetime.now()
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            'error_type': self.error_type.value,
            'message': self.message,
            'filepath': self.filepath,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class FileTouchErrorHandler:
    """Error handler for File Touch operations."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.error_history = []
    
    def handle_error(self, error: FileTouchError) -> Dict[str, Any]:
        """Handle and log error."""
        error_dict = error.to_dict()
        self.error_history.append(error_dict)
        
        if self.logger:
            self.logger.log_error(
                f"{error.error_type.value}: {error.message}",
                error,
                error.details
            )
        
        return error_dict
    
    def get_recovery_suggestion(self, error_type: FileTouchErrorType) -> str:
        """Get recovery suggestion for error type."""
        suggestions = {
            FileTouchErrorType.FILE_NOT_FOUND: "Verify the file path and ensure the file exists",
            FileTouchErrorType.PERMISSION_DENIED: "Check file permissions and run with appropriate privileges",
            FileTouchErrorType.INVALID_TIMESTAMP: "Verify timestamp format and range",
            FileTouchErrorType.OPERATION_TIMEOUT: "Try again or increase timeout setting",
            FileTouchErrorType.CONFIGURATION_ERROR: "Check configuration file and reset if necessary",
            FileTouchErrorType.HUB_COMMUNICATION_ERROR: "Check hub connection and restart if needed",
            FileTouchErrorType.VALIDATION_ERROR: "Verify input data and file integrity",
            FileTouchErrorType.SECURITY_VIOLATION: "Check file path for security issues"
        }
        
        return suggestions.get(error_type, "Contact support for assistance")
```

---

## Phase 4: GUI Migration and Integration

### 4.1 Create GUI Module

```python
# file_utilities_2/gui/file_touch_gui.py
"""
File Touch GUI Module

Standardized file touch GUI using file_utilities_2 components.
"""

import os
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (QComboBox, QLabel, QInputDialog, QMessageBox, 
                             QFileDialog, QProgressBar, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5 import uic

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager, Colors, Fonts
from file_utilities_2.core.file_touch_logic import FileTouchLogic
from file_utilities_2.core.file_touch_config import FileTouchConfig
from file_utilities_2.core.file_touch_logging import get_file_touch_logger


class FileTouchGUI(StandardWindow):
    """Standardized file touch GUI with full integration."""
    
    def __init__(self):
        """Initialize File Touch GUI with enhanced integration."""
        super().__init__(
            title="File Touch - Timestamp Editor",
            icon_path=self._get_file_touch_icon()
        )
        
        # Initialize components
        self.config = FileTouchConfig()
        self.logic = FileTouchLogic(self.config)
        self.logger = get_file_touch_logger()
        
        # UI state
        self.current_file = None
        self.operation_in_progress = False
        
        # Setup GUI
        self._load_ui()
        self._setup_components()
        self._connect_signals()
        self._apply_theme()
        self._restore_window_state()
        
        # Initialize profiles
        self._update_profile_list()
        
        # Setup status monitoring
        self._setup_status_monitoring()
        
        self.logger.log_gui_event('info', "File Touch GUI initialized successfully")
        
        # Show window
        self.show()
    
    def _get_file_touch_icon(self) -> str:
        """Get File Touch icon path."""
        icon_path = self.config.get_resource_path('icon_path')
        if not icon_path or not os.path.exists(icon_path):
            # Fallback to default icon
            return os.path.join(os.path.dirname(__file__), 'icons', 'file_touch.png')
        return icon_path
    
    def _load_ui(self) -> None:
        """Load UI file using file_utilities_2 pattern."""
        ui_file = self.config.get_resource_path('ui_file')
        if not ui_file or not os.path.exists(ui_file):
            # Fallback to local UI file
            ui_file = os.path.join(os.path.dirname(__file__), "file_touch.ui")
        
        try:
            uic.loadUi(ui_file, self)
            self.logger.log_gui_event('info', f"UI loaded from {ui_file}")
        except Exception as e:
            self.logger.log_error(f"Failed to load UI file: {ui_file}", e)
            self._create_ui_programmatically()
    
    def _create_ui_programmatically(self):
        """Create UI programmatically if .ui file is not available."""
        self.logger.log_gui_event('warning', "Creating UI programmatically")
        
        # This would contain the programmatic UI creation
        # Similar to the existing file_touch.py but with StandardWindow integration
        # Implementation details would go here...
        
    def _setup_components(self) -> None:
        """Setup additional GUI components."""
        # Enable drag and drop
        self.setAcceptDrops(True)
        if hasattr(self, 'filePathEdit'):
            self.filePathEdit.setAcceptDrops(True)
        
        # Add profile management to toolbar if it exists
        if hasattr(self, 'toolBar'):
            self._setup_profile_toolbar()
        
        # Setup progress monitoring
        self._setup_progress_display()
        
        # Configure datetime editors
        self._setup_datetime_editors()
        
        # Set initial state
        self._set_initial_state()
    
    def _setup_profile_toolbar(self):
        """Setup profile management in toolbar."""
        # Profile combo box
        self.profileCombo = QComboBox(self)
        self.profileCombo.setMinimumWidth(150)
        ThemeManager.style_input_field(self.profileCombo)
        
        # Add to toolbar
        self.toolBar.addWidget(QLabel("Profile: "))
        self