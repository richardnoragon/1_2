"""
Error Handling Framework for PDF Tools Hub
Provides unified error handling, user-friendly messages, and recovery suggestions.
"""

import traceback
import sys
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import QObject, pyqtSignal
from log_config import setup_logger

logger = setup_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors."""
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_FORMAT = "invalid_format"
    CORRUPTED_FILE = "corrupted_file"
    INSUFFICIENT_SPACE = "insufficient_space"
    NETWORK_ERROR = "network_error"
    DEPENDENCY_MISSING = "dependency_missing"
    CONFIGURATION_ERROR = "configuration_error"
    TOOL_ERROR = "tool_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorInfo:
    """Information about an error."""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    message: str
    technical_details: str
    suggestions: List[str]
    tool_name: Optional[str] = None
    file_path: Optional[str] = None
    operation_id: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class ErrorRecoveryAction:
    """Represents a recovery action for an error."""
    
    def __init__(self, name: str, description: str, 
                 action: Callable, icon: Optional[str] = None):
        self.name = name
        self.description = description
        self.action = action
        self.icon = icon
    
    def execute(self) -> bool:
        """Execute the recovery action."""
        try:
            return self.action()
        except Exception as e:
            logger.error(f"Recovery action '{self.name}' failed: {e}")
            return False


class ErrorManager(QObject):
    """
    Centralized error handling manager for PDF tools.
    
    Provides unified error handling, user-friendly messages,
    recovery suggestions, and error reporting.
    """
    
    # Signals for error events
    error_occurred = pyqtSignal(str, str, str)  # error_id, title, message
    error_resolved = pyqtSignal(str)  # error_id
    
    def __init__(self):
        super().__init__()
        self.errors: Dict[str, ErrorInfo] = {}
        self.error_counter = 0
        self.error_handlers: Dict[ErrorCategory, Callable] = {}
        self.recovery_actions: Dict[str, List[ErrorRecoveryAction]] = {}
        
        # Register default error handlers
        self._register_default_handlers()
        
        logger.info("Error Manager initialized")
    
    def _register_default_handlers(self):
        """Register default error handlers for common error types."""
        self.register_error_handler(
            ErrorCategory.FILE_NOT_FOUND, 
            self._handle_file_not_found
        )
        self.register_error_handler(
            ErrorCategory.PERMISSION_DENIED, 
            self._handle_permission_denied
        )
        self.register_error_handler(
            ErrorCategory.INVALID_FORMAT, 
            self._handle_invalid_format
        )
        self.register_error_handler(
            ErrorCategory.CORRUPTED_FILE, 
            self._handle_corrupted_file
        )
        self.register_error_handler(
            ErrorCategory.DEPENDENCY_MISSING, 
            self._handle_dependency_missing
        )
    
    def register_error_handler(self, category: ErrorCategory, 
                              handler: Callable[[Exception, Dict], ErrorInfo]):
        """Register a custom error handler for a category."""
        self.error_handlers[category] = handler
        logger.debug(f"Registered error handler for {category.value}")
    
    def handle_error(self, exception: Exception, context: Dict[str, Any] = None,
                    parent_widget: Optional[QWidget] = None) -> str:
        """
        Handle an error and return error ID.
        
        Args:
            exception: The exception that occurred
            context: Additional context information
            parent_widget: Parent widget for error dialogs
            
        Returns:
            Unique error ID
        """
        if context is None:
            context = {}
        
        # Generate error ID
        self.error_counter += 1
        error_id = f"error_{self.error_counter}"
        
        # Categorize the error
        category = self._categorize_error(exception, context)
        
        # Get error handler
        handler = self.error_handlers.get(category, self._handle_unknown_error)
        
        try:
            # Generate error info
            error_info = handler(exception, context)
            error_info.error_id = error_id
            error_info.category = category
            
            # Store error
            self.errors[error_id] = error_info
            
            # Log error
            self._log_error(error_info)
            
            # Show user dialog if parent widget provided
            if parent_widget:
                self._show_error_dialog(error_info, parent_widget)
            
            # Emit signal
            self.error_occurred.emit(error_id, error_info.title, error_info.message)
            
            return error_id
            
        except Exception as e:
            logger.critical(f"Error in error handler: {e}", exc_info=True)
            # Fallback error handling
            fallback_id = f"fallback_{self.error_counter}"
            self._handle_fallback_error(fallback_id, exception, e)
            return fallback_id
    
    def _categorize_error(self, exception: Exception, 
                         context: Dict[str, Any]) -> ErrorCategory:
        """Categorize an error based on exception type and context."""
        exception_type = type(exception).__name__
        exception_message = str(exception).lower()
        
        # File-related errors
        if isinstance(exception, FileNotFoundError):
            return ErrorCategory.FILE_NOT_FOUND
        elif isinstance(exception, PermissionError):
            return ErrorCategory.PERMISSION_DENIED
        elif 'no space left' in exception_message:
            return ErrorCategory.INSUFFICIENT_SPACE
        
        # PDF-specific errors
        elif any(keyword in exception_message for keyword in 
                ['invalid pdf', 'corrupted', 'damaged', 'not a pdf']):
            return ErrorCategory.CORRUPTED_FILE
        elif 'format' in exception_message:
            return ErrorCategory.INVALID_FORMAT
        
        # Import/dependency errors
        elif isinstance(exception, ImportError) or isinstance(exception, ModuleNotFoundError):
            return ErrorCategory.DEPENDENCY_MISSING
        
        # Network errors
        elif any(keyword in exception_message for keyword in 
                ['network', 'connection', 'timeout', 'unreachable']):
            return ErrorCategory.NETWORK_ERROR
        
        # Configuration errors
        elif 'config' in exception_message or 'setting' in exception_message:
            return ErrorCategory.CONFIGURATION_ERROR
        
        # Tool-specific errors
        elif context.get('tool_name'):
            return ErrorCategory.TOOL_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    def _handle_file_not_found(self, exception: Exception, 
                              context: Dict[str, Any]) -> ErrorInfo:
        """Handle file not found errors."""
        file_path = context.get('file_path', 'Unknown file')
        
        return ErrorInfo(
            error_id="",  # Will be set by caller
            category=ErrorCategory.FILE_NOT_FOUND,
            severity=ErrorSeverity.ERROR,
            title="File Not Found",
            message=f"The file '{file_path}' could not be found.",
            technical_details=str(exception),
            suggestions=[
                "Check if the file path is correct",
                "Verify the file exists and hasn't been moved or deleted",
                "Check if you have permission to access the file location",
                "Try browsing for the file using the file dialog"
            ],
            file_path=file_path
        )
    
    def _handle_permission_denied(self, exception: Exception, 
                                 context: Dict[str, Any]) -> ErrorInfo:
        """Handle permission denied errors."""
        file_path = context.get('file_path', 'Unknown file')
        
        return ErrorInfo(
            error_id="",
            category=ErrorCategory.PERMISSION_DENIED,
            severity=ErrorSeverity.ERROR,
            title="Permission Denied",
            message=f"Access denied to '{file_path}'. You don't have sufficient permissions.",
            technical_details=str(exception),
            suggestions=[
                "Run the application as administrator",
                "Check file permissions and ownership",
                "Close any applications that might be using the file",
                "Copy the file to a location you have write access to"
            ],
            file_path=file_path
        )
    
    def _handle_invalid_format(self, exception: Exception, 
                              context: Dict[str, Any]) -> ErrorInfo:
        """Handle invalid format errors."""
        file_path = context.get('file_path', 'Unknown file')
        
        return ErrorInfo(
            error_id="",
            category=ErrorCategory.INVALID_FORMAT,
            severity=ErrorSeverity.ERROR,
            title="Invalid File Format",
            message=f"The file '{file_path}' is not in a valid format or is corrupted.",
            technical_details=str(exception),
            suggestions=[
                "Verify the file is a valid PDF document",
                "Try opening the file in a PDF viewer to check if it's corrupted",
                "If the file is corrupted, try to obtain a new copy",
                "Check if the file extension matches the actual file type"
            ],
            file_path=file_path
        )
    
    def _handle_corrupted_file(self, exception: Exception, 
                              context: Dict[str, Any]) -> ErrorInfo:
        """Handle corrupted file errors."""
        file_path = context.get('file_path', 'Unknown file')
        
        return ErrorInfo(
            error_id="",
            category=ErrorCategory.CORRUPTED_FILE,
            severity=ErrorSeverity.ERROR,
            title="Corrupted File",
            message=f"The file '{file_path}' appears to be corrupted or damaged.",
            technical_details=str(exception),
            suggestions=[
                "Try to obtain a new copy of the file",
                "Use PDF repair tools to fix the corruption",
                "Check if the file was completely downloaded",
                "Verify the file wasn't modified by malware"
            ],
            file_path=file_path
        )
    
    def _handle_dependency_missing(self, exception: Exception, 
                                  context: Dict[str, Any]) -> ErrorInfo:
        """Handle missing dependency errors."""
        module_name = getattr(exception, 'name', 'Unknown module')
        
        return ErrorInfo(
            error_id="",
            category=ErrorCategory.DEPENDENCY_MISSING,
            severity=ErrorSeverity.CRITICAL,
            title="Missing Dependency",
            message=f"Required module '{module_name}' is not installed.",
            technical_details=str(exception),
            suggestions=[
                f"Install the missing module: pip install {module_name}",
                "Check the requirements.txt file for all dependencies",
                "Verify your Python environment is properly configured",
                "Contact support if the issue persists"
            ]
        )
    
    def _handle_unknown_error(self, exception: Exception, 
                             context: Dict[str, Any]) -> ErrorInfo:
        """Handle unknown errors."""
        return ErrorInfo(
            error_id="",
            category=ErrorCategory.UNKNOWN_ERROR,
            severity=ErrorSeverity.ERROR,
            title="Unexpected Error",
            message="An unexpected error occurred during the operation.",
            technical_details=f"{type(exception).__name__}: {str(exception)}",
            suggestions=[
                "Try the operation again",
                "Restart the application if the problem persists",
                "Check the log files for more details",
                "Contact support with the error details"
            ],
            tool_name=context.get('tool_name'),
            operation_id=context.get('operation_id')
        )
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error information."""
        log_message = (
            f"Error {error_info.error_id}: {error_info.title} - "
            f"{error_info.message}"
        )
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Log technical details at debug level
        logger.debug(f"Technical details for {error_info.error_id}: {error_info.technical_details}")
    
    def _show_error_dialog(self, error_info: ErrorInfo, parent: QWidget):
        """Show error dialog to user."""
        # Determine dialog icon based on severity
        if error_info.severity == ErrorSeverity.CRITICAL:
            icon = QMessageBox.Critical
        elif error_info.severity == ErrorSeverity.ERROR:
            icon = QMessageBox.Critical
        elif error_info.severity == ErrorSeverity.WARNING:
            icon = QMessageBox.Warning
        else:
            icon = QMessageBox.Information
        
        # Create message box
        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(error_info.title)
        msg_box.setText(error_info.message)
        
        # Add suggestions as detailed text
        if error_info.suggestions:
            suggestions_text = "Suggestions:\n" + "\n".join(
                f"• {suggestion}" for suggestion in error_info.suggestions
            )
            msg_box.setDetailedText(suggestions_text)
        
        # Add technical details button
        if error_info.technical_details:
            msg_box.setInformativeText(
                "Click 'Show Details' for technical information."
            )
        
        msg_box.exec_()
    
    def _handle_fallback_error(self, error_id: str, original_exception: Exception, 
                              handler_exception: Exception):
        """Handle errors that occur in error handlers."""
        logger.critical(
            f"Fallback error handling for {error_id}: "
            f"Original: {original_exception}, Handler error: {handler_exception}",
            exc_info=True
        )
        
        # Create minimal error info
        fallback_error = ErrorInfo(
            error_id=error_id,
            category=ErrorCategory.UNKNOWN_ERROR,
            severity=ErrorSeverity.CRITICAL,
            title="Critical Error",
            message="A critical error occurred in the error handling system.",
            technical_details=f"Original: {original_exception}\nHandler: {handler_exception}",
            suggestions=["Restart the application", "Contact technical support"]
        )
        
        self.errors[error_id] = fallback_error
    
    def get_error_info(self, error_id: str) -> Optional[ErrorInfo]:
        """Get error information by ID."""
        return self.errors.get(error_id)
    
    def resolve_error(self, error_id: str):
        """Mark an error as resolved."""
        if error_id in self.errors:
            logger.info(f"Error resolved: {error_id}")
            self.error_resolved.emit(error_id)
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorInfo]:
        """Get recent errors."""
        sorted_errors = sorted(
            self.errors.values(), 
            key=lambda x: x.timestamp or 0, 
            reverse=True
        )
        return sorted_errors[:count]
    
    def clear_old_errors(self, max_age_hours: int = 24):
        """Clear old errors."""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for error_id, error_info in self.errors.items():
            if (error_info.timestamp and 
                current_time - error_info.timestamp > max_age_seconds):
                to_remove.append(error_id)
        
        for error_id in to_remove:
            del self.errors[error_id]
        
        if to_remove:
            logger.info(f"Cleared {len(to_remove)} old errors")


# Global instance
_error_manager_instance: Optional[ErrorManager] = None


def get_error_manager() -> ErrorManager:
    """Get the global error manager instance."""
    global _error_manager_instance
    if _error_manager_instance is None:
        _error_manager_instance = ErrorManager()
    return _error_manager_instance


# Convenience functions for easy integration
def handle_error(exception: Exception, context: Dict[str, Any] = None,
                parent_widget: Optional[QWidget] = None) -> str:
    """Handle an error and return error ID."""
    return get_error_manager().handle_error(exception, context, parent_widget)


def get_error_info(error_id: str) -> Optional[ErrorInfo]:
    """Get error information by ID."""
    return get_error_manager().get_error_info(error_id)


def resolve_error(error_id: str):
    """Mark an error as resolved."""
    get_error_manager().resolve_error(error_id)


# Decorator for automatic error handling
def handle_errors(tool_name: str = None, show_dialog: bool = True):
    """Decorator for automatic error handling in tool methods."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'tool_name': tool_name or func.__name__,
                    'function': func.__name__,
                    'args': str(args)[:100],  # Limit length
                    'kwargs': str(kwargs)[:100]
                }
                
                parent_widget = None
                if show_dialog and args and hasattr(args[0], 'parent'):
                    parent_widget = args[0].parent()
                
                error_id = handle_error(e, context, parent_widget)
                logger.error(f"Error in {func.__name__}: {error_id}")
                
                # Re-raise for caller to handle if needed
                raise
        
        return wrapper
    return decorator


if __name__ == '__main__':
    # Test the error manager
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    
    # Create error manager
    em = get_error_manager()
    
    # Test different error types
    try:
        raise FileNotFoundError("test.pdf not found")
    except Exception as e:
        error_id = handle_error(e, {'file_path': 'test.pdf'}, window)
        print(f"Handled error: {error_id}")
    
    try:
        raise PermissionError("Access denied")
    except Exception as e:
        error_id = handle_error(e, {'file_path': 'protected.pdf'}, window)
        print(f"Handled error: {error_id}")
    
    # Test decorator
    @handle_errors(tool_name="test_tool")
    def test_function():
        raise ValueError("Test error")
    
    try:
        test_function()
    except Exception:
        print("Decorator handled error")
    
    print("Error manager test completed")