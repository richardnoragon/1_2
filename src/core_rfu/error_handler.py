"""
Centralized error handling module for graceful error management across all modules.
"""

import logging
import traceback
from typing import Optional, Any, Dict
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox


class ErrorHandler:
    """A class that handles error handler."""

    _instance = None

    def __new__(cls):
        """new.
        Args:
            cls (Any): Description of cls"""
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the error handler singleton."""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "rfu.log"

        # Configure logging
        logging.basicConfig(
            filename=str(self.log_file),
            level=logging.ERROR,
            format="%(asctime)s [%(levelname)s] %(message)s - File: %(filename)s, Line: %(lineno)d",
        )
        self.logger = logging.getLogger(__name__)

    def handle_error(
        self,
        error: Exception,
        operation: str,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        show_dialog: bool = True,
    ) -> bool:
        """
        Handle an error gracefully, log it, and optionally show a user dialog.

        Args:
            error: The exception that was caught
            operation: Description of the operation that failed
            user_message: Optional custom message to show to the user
            context: Optional dictionary with additional context
            show_dialog: Whether to show an error dialog to the user

        Returns:
            bool: False if error occurred, True if handled successfully
        """
        # Build error message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_details = f"Operation: {operation}\nError: {str(error)}\n"
        if context:
            error_details += f"Context: {context}\n"
        error_details += f"Traceback:\n{traceback.format_exc()}"

        # Log the error
        self.logger.error(error_details)

        # Show user dialog if requested
        if show_dialog:
            default_msg = f"An error occurred while {operation}.\nThe error has been logged."
            msg = user_message if user_message else default_msg
            self._show_error_dialog(msg)

        return False

    def _show_error_dialog(self, message: str):
        """Show an error dialog to the user."""
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText(message)
        dialog.setWindowTitle("Error")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()


# Global instance and accessor
_error_handler = None


def get_error_handler():
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


# Create the global instance that will be imported by other modules
error_handler = get_error_handler()
