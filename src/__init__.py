"""
Richard's File Utilities - Source Code Package

Main package for Richard's File Utilities containing all source code modules.
This package provides a comprehensive suite of file management and
analysis tools.
"""

import sys
from pathlib import Path

# Ensure the src directory is in the Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

"""
Richard's File Utilities - Source Code Package

Main package for Richard's File Utilities containing all source code modules.
This package provides a comprehensive suite of file management and
analysis tools.
"""

import sys
from pathlib import Path

# Ensure the src directory is in the Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Create missing core structure if needed for main.py
try:
    core_dir = Path(__file__).parent / "core"
    constants_file = core_dir / "constants.py"
    error_handler_file = core_dir / "error_handler.py"
    
    if not constants_file.exists() or not error_handler_file.exists():
        print("🏗️ Creating missing src/core structure...")
        
        # Create directory
        core_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = core_dir / "__init__.py"
        init_content = '''"""
Core constants and configuration for Richard's File Utilities.
"""

from .constants import (
    APP_NAME, JSON_FILES_FILTER, IMPORT_ERROR, SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER
)

# Import error handler now available in src/core
from .error_handler import error_handler

__all__ = [
    "APP_NAME", "JSON_FILES_FILTER", "IMPORT_ERROR", "SECURITY_TEST",
    "SUGGESTED_SOLUTIONS_HEADER", "error_handler"
]
'''
        if not init_file.exists():
            init_file.write_text(init_content, encoding='utf-8')
        
        # Create constants.py
        constants_content = '''"""
Constants for Richard's File Utilities Main Application.
"""

# Application Identity
APP_NAME = "Richard's File Utilities"

# File Dialog Filters
JSON_FILES_FILTER = "JSON Files (*.json);;All Files (*)"

# Error Messages
IMPORT_ERROR = "Import Error"
SECURITY_TEST = "Security Test"

# UI Headers
SUGGESTED_SOLUTIONS_HEADER = "Suggested Solutions"

# Version Information
APP_VERSION = "3.0.0"
APP_ORGANIZATION = "Richard's File Utilities"
'''
        if not constants_file.exists():
            constants_file.write_text(constants_content, encoding='utf-8')
        
        # Create error_handler.py with QObject-based implementation
        error_handler_content = '''"""
Error handling utilities for Richard's File Utilities.

This module provides centralized error handling and logging functionality.
"""

import sys
import traceback
import logging
from typing import Optional, Callable, Any
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QObject, pyqtSignal


class ErrorHandler(QObject):
    """Centralized error handler for the application."""
    
    error_occurred = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rfu_errors.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.error(f"Uncaught exception: {error_msg}")
        
        # Show error dialog if GUI is available
        app = QApplication.instance()
        if app:
            self.show_error_dialog("Unexpected Error", str(exc_value))
    
    def show_error_dialog(self, title: str, message: str, details: Optional[str] = None):
        """Show an error dialog to the user."""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if details:
                msg_box.setDetailedText(details)
            
            msg_box.exec_()
            self.error_occurred.emit(title, message)
        except Exception as e:
            # Fallback to console if GUI fails
            print(f"Error showing dialog: {e}")
            print(f"Original error - {title}: {message}")
    
    def show_warning_dialog(self, title: str, message: str):
        """Show a warning dialog to the user."""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.exec_()
        except Exception as e:
            print(f"Error showing warning: {e}")
            print(f"Warning - {title}: {message}")
    
    def show_info_dialog(self, title: str, message: str):
        """Show an info dialog to the user."""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.exec_()
        except Exception as e:
            print(f"Error showing info: {e}")
            print(f"Info - {title}: {message}")
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log an error message."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}")
        else:
            self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(message)


def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.log_error(f"Error executing {func.__name__}", e)
        return None


def handle_gui_error(func: Callable) -> Callable:
    """Decorator for handling GUI errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_handler.show_error_dialog(
                "GUI Error",
                f"An error occurred in {func.__name__}: {str(e)}"
            )
            return None
    return wrapper


# Global error handler instance
error_handler = ErrorHandler()

# Set up global exception handling
sys.excepthook = error_handler.handle_exception
'''
        if not error_handler_file.exists():
            error_handler_file.write_text(error_handler_content, encoding='utf-8')
        
        print(f"✅ Created {core_dir}")
        print(f"✅ Created {init_file}")
        print(f"✅ Created {constants_file}")
        print(f"✅ Created {error_handler_file}")
        print("✅ Core structure created successfully!")
        print("✅ main.py can now import from src.core.constants")
        print("✅ Error handler moved to src.core.error_handler")

except Exception as e:
    print(f"Note: Could not auto-create core structure: {e}")
    print("Please run: python scripts/maintenance/organize_src_folder.py")

# Package metadata
__version__ = "3.0.0"
__author__ = "Richard's File Utilities"
__description__ = "Comprehensive file management and analysis utilities"


def safe_import_package(package_name):
    """Safely import a package with error handling."""
    try:
        return __import__(package_name, fromlist=[package_name])
    except ImportError as e:
        print(f"Warning: Could not import package {package_name}: {e}")
        return None


# Import main packages
utilities = safe_import_package("utilities")
rfu = safe_import_package("rfu")
legacy = safe_import_package("legacy")

__all__ = ["utilities", "rfu", "legacy"]


def get_package_info():
    """Return information about available packages."""
    return {
        'utilities': utilities is not None,
        'rfu': rfu is not None,
        'legacy': legacy is not None,
        'version': __version__,
        'description': __description__
    }