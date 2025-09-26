# This file has been moved to src/core/error_handler.py
# All functionality has been transferred to the new location.
# Please use: from src.core.error_handler import error_handler

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