"""
Centralized error handling system for Advanced Folders feature.

This module provides comprehensive error handling infrastructure with
logging integration, monitoring capabilities, and graceful degradation.
"""

import functools
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from ..exceptions import (
    AdvancedFoldersException,
    ConfigurationException,
    FileSystemException,
    PerformanceException,
    RepositoryException,
    SearchException,
    ValidationException,
)


class ErrorHandler:
    """
    Centralized error handler with logging and monitoring capabilities.

    Provides structured error handling with context preservation,
    automatic logging, and graceful degradation strategies.
    """

    def __init__(self, logger=None):
        """
        Initialize error handler.

        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger
        self.error_counts: Dict[str, int] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000

        # Error type mappings for categorization
        self.error_type_mapping = {
            "validation": ValidationException,
            "repository": RepositoryException,
            "configuration": ConfigurationException,
            "search": SearchException,
            "filesystem": FileSystemException,
            "performance": PerformanceException,
        }

        # Default error messages
        self.default_messages = {
            ValidationException: "A validation error occurred",
            RepositoryException: "A database operation failed",
            ConfigurationException: "A configuration error occurred",
            SearchException: "A search operation failed",
            FileSystemException: "A file system operation failed",
            PerformanceException: "A performance issue was detected",
            AdvancedFoldersException: "An advanced folders error occurred",
        }

    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        reraise: bool = True,
    ) -> Optional[AdvancedFoldersException]:
        """
        Handle an exception with logging and context preservation.

        Args:
            exception: Exception to handle
            context: Additional context information
            operation: Name of operation that failed
            reraise: Whether to reraise the exception

        Returns:
            Processed AdvancedFoldersException if not reraised
        """
        # Get or create AdvancedFoldersException
        if isinstance(exception, AdvancedFoldersException):
            af_exception = exception
        else:
            af_exception = self._wrap_exception(exception, context, operation)

        # Log the error
        self._log_error(af_exception, context, operation)

        # Update error statistics
        self._update_error_stats(af_exception)

        # Add to error history
        self._add_to_history(af_exception, context, operation)

        if reraise:
            raise af_exception
        else:
            return af_exception

    def _wrap_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
    ) -> AdvancedFoldersException:
        """
        Wrap a generic exception in AdvancedFoldersException.

        Args:
            exception: Original exception
            context: Additional context
            operation: Operation name

        Returns:
            Wrapped AdvancedFoldersException
        """
        # Determine appropriate exception type
        exception_type = type(exception).__name__
        message = str(exception)

        # Enhanced context
        enhanced_context = {
            "original_exception": exception_type,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if context:
            enhanced_context.update(context)

        # Create appropriate wrapped exception
        if isinstance(
            exception, (OSError, FileNotFoundError, PermissionError)
        ):
            return FileSystemException(
                message=f"File system error: {message}",
                context=enhanced_context,
                cause=exception,
            )
        elif isinstance(exception, (ValueError, TypeError)):
            return ValidationException(
                message=f"Validation error: {message}",
                context=enhanced_context,
                cause=exception,
            )
        elif "timeout" in message.lower() or "performance" in message.lower():
            return PerformanceException(
                message=f"Performance issue: {message}",
                context=enhanced_context,
                cause=exception,
            )
        else:
            return AdvancedFoldersException(
                message=f"Unexpected error: {message}",
                context=enhanced_context,
                cause=exception,
            )

    def _log_error(
        self,
        exception: AdvancedFoldersException,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
    ) -> None:
        """
        Log error with appropriate level and detail.

        Args:
            exception: Exception to log
            context: Additional context
            operation: Operation name
        """
        if not self.logger:
            return

        # Determine log level based on exception type
        if isinstance(exception, ValidationException):
            log_level = "warning"
        elif isinstance(exception, PerformanceException):
            log_level = "warning"
        elif isinstance(
            exception, (RepositoryException, ConfigurationException)
        ):
            log_level = "error"
        else:
            log_level = "error"

        # Build log message
        log_message = f"[{exception.error_code}] {exception.message}"
        if operation:
            log_message = f"{operation}: {log_message}"

        # Build context for logging
        log_context = {
            "error_code": exception.error_code,
            "exception_type": type(exception).__name__,
            "operation": operation,
        }
        if exception.context:
            log_context.update(exception.context)
        if context:
            log_context.update(context)

        # Log with appropriate level
        log_method = getattr(self.logger, log_level, self.logger.error)
        log_method(log_message, extra={"context": log_context})

        # Log stack trace for critical errors
        if log_level == "error" and exception.cause:
            self.logger.debug(
                f"Stack trace for {exception.error_code}",
                exc_info=exception.cause,
            )

    def _update_error_stats(self, exception: AdvancedFoldersException) -> None:
        """
        Update error statistics for monitoring.

        Args:
            exception: Exception to track
        """
        error_type = type(exception).__name__
        self.error_counts[error_type] = (
            self.error_counts.get(error_type, 0) + 1
        )

        # Also track by error code
        if exception.error_code:
            self.error_counts[exception.error_code] = (
                self.error_counts.get(exception.error_code, 0) + 1
            )

    def _add_to_history(
        self,
        exception: AdvancedFoldersException,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
    ) -> None:
        """
        Add error to history for analysis.

        Args:
            exception: Exception to add
            context: Additional context
            operation: Operation name
        """
        error_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_code": exception.error_code,
            "exception_type": type(exception).__name__,
            "message": exception.message,
            "operation": operation,
            "context": dict(exception.context) if exception.context else {},
            "suggestion": exception.suggestion,
        }

        if context:
            error_record["context"].update(context)

        self.error_history.append(error_record)

        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size :]

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics for monitoring.

        Returns:
            Dictionary with error statistics
        """
        total_errors = sum(self.error_counts.values())

        return {
            "total_errors": total_errors,
            "error_counts": dict(self.error_counts),
            "recent_errors": len(
                [
                    e
                    for e in self.error_history
                    if (
                        datetime.now(timezone.utc)
                        - datetime.fromisoformat(e["timestamp"])
                    ).total_seconds()
                    < 3600
                ]
            ),
            "history_size": len(self.error_history),
        }

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent errors for analysis.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of recent error records
        """
        return self.error_history[-limit:] if self.error_history else []

    def clear_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler(logger=None) -> ErrorHandler:
    """
    Get global error handler instance.

    Args:
        logger: Logger instance to use

    Returns:
        ErrorHandler instance
    """
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler(logger)
    elif logger and _error_handler.logger != logger:
        _error_handler.logger = logger
    return _error_handler


def handle_errors(
    operation: Optional[str] = None,
    reraise: bool = True,
    context: Optional[Dict[str, Any]] = None,
    fallback_return: Any = None,
):
    """
    Decorator for automatic error handling.

    Args:
        operation: Name of operation for context
        reraise: Whether to reraise exceptions
        context: Additional context information
        fallback_return: Value to return if error occurs and not reraising

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error handler
                error_handler = get_error_handler()

                # Build context
                error_context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }
                if context:
                    error_context.update(context)

                # Handle the error
                if reraise:
                    error_handler.handle_exception(
                        e,
                        error_context,
                        operation or func.__name__,
                        reraise=True,
                    )
                else:
                    error_handler.handle_exception(
                        e,
                        error_context,
                        operation or func.__name__,
                        reraise=False,
                    )
                    return fallback_return

        return wrapper

    return decorator


def safe_execute(
    func: Callable,
    *args,
    operation: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    fallback_return: Any = None,
    **kwargs,
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Function arguments
        operation: Operation name for context
        context: Additional context
        fallback_return: Value to return on error
        **kwargs: Function keyword arguments

    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler = get_error_handler()

        error_context = {
            "function": func.__name__,
            "module": getattr(func, "__module__", "unknown"),
        }
        if context:
            error_context.update(context)

        error_handler.handle_exception(
            e, error_context, operation or func.__name__, reraise=False
        )

        return fallback_return


class GracefulDegradation:
    """
    Provides graceful degradation strategies for failed operations.

    Implements fallback mechanisms and recovery strategies to maintain
    system stability when non-critical operations fail.
    """

    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize graceful degradation manager.

        Args:
            error_handler: Error handler for logging failures
        """
        self.error_handler = error_handler or get_error_handler()
        self.fallback_strategies: Dict[str, Callable] = {}
        self.degradation_active: Dict[str, bool] = {}

    def register_fallback(
        self,
        operation: str,
        fallback_func: Callable,
        conditions: Optional[List[Type[Exception]]] = None,
    ) -> None:
        """
        Register a fallback strategy for an operation.

        Args:
            operation: Name of operation
            fallback_func: Function to call as fallback
            conditions: Exception types that trigger fallback
        """
        self.fallback_strategies[operation] = {
            "function": fallback_func,
            "conditions": conditions or [Exception],
        }

    def execute_with_fallback(
        self,
        operation: str,
        primary_func: Callable,
        *args,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """
        Execute function with fallback on failure.

        Args:
            operation: Operation name
            primary_func: Primary function to execute
            *args: Function arguments
            context: Additional context
            **kwargs: Function keyword arguments

        Returns:
            Result from primary or fallback function
        """
        try:
            # Try primary function
            result = primary_func(*args, **kwargs)

            # Reset degradation flag on success
            if self.degradation_active.get(operation):
                self.degradation_active[operation] = False
                if self.error_handler.logger:
                    self.error_handler.logger.info(
                        f"Operation '{operation}' recovered from degraded state"
                    )

            return result

        except Exception as e:
            # Check if we have a fallback for this operation
            if operation not in self.fallback_strategies:
                raise

            fallback_config = self.fallback_strategies[operation]

            # Check if exception type matches fallback conditions
            if not any(
                isinstance(e, exc_type)
                for exc_type in fallback_config["conditions"]
            ):
                raise

            # Log degradation
            if not self.degradation_active.get(operation):
                self.degradation_active[operation] = True
                if self.error_handler.logger:
                    self.error_handler.logger.warning(
                        f"Activating fallback for operation '{operation}': {str(e)}"
                    )

            # Execute fallback
            try:
                return fallback_config["function"](*args, **kwargs)
            except Exception as fallback_error:
                # Log fallback failure
                self.error_handler.handle_exception(
                    fallback_error,
                    context={"operation": operation, "fallback_failed": True},
                    operation=f"{operation}_fallback",
                    reraise=False,
                )

                # Reraise original exception
                raise e

    def is_degraded(self, operation: str) -> bool:
        """
        Check if operation is in degraded state.

        Args:
            operation: Operation name

        Returns:
            True if operation is degraded
        """
        return self.degradation_active.get(operation, False)

    def get_degradation_status(self) -> Dict[str, bool]:
        """
        Get degradation status for all operations.

        Returns:
            Dictionary mapping operation names to degradation status
        """
        return dict(self.degradation_active)


# Global graceful degradation manager
_degradation_manager: Optional[GracefulDegradation] = None


def get_degradation_manager() -> GracefulDegradation:
    """Get global degradation manager instance."""
    global _degradation_manager
    if _degradation_manager is None:
        _degradation_manager = GracefulDegradation()
    return _degradation_manager


def with_fallback(
    operation: str,
    fallback_func: Optional[Callable] = None,
    conditions: Optional[List[Type[Exception]]] = None,
):
    """
    Decorator for functions with fallback capabilities.

    Args:
        operation: Operation name
        fallback_func: Fallback function
        conditions: Exception types that trigger fallback

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            degradation_manager = get_degradation_manager()

            if fallback_func:
                # Register fallback if provided
                degradation_manager.register_fallback(
                    operation, fallback_func, conditions
                )

            return degradation_manager.execute_with_fallback(
                operation, func, *args, **kwargs
            )

        return wrapper

    return decorator
