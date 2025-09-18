"""
Unit tests for Advanced Folders error handling infrastructure.

Tests the centralized error handling system with logging integration,
monitoring capabilities, and graceful degradation strategies.
"""

import threading
from unittest.mock import Mock

import pytest

from src.tools.file_management.advanced_folders_legacy.error_handling.error_handler import (
    ErrorHandler, GracefulDegradation, get_degradation_manager,
    get_error_handler, handle_errors, safe_execute, with_fallback)
from src.tools.file_management.advanced_folders_legacy.exceptions.advanced_folders_exceptions import (
    AdvancedFoldersException, FileSystemException, PerformanceException,
    RepositoryException, ValidationException)


class TestErrorHandler:
    """Test ErrorHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.error_handler = ErrorHandler(self.mock_logger)
    
    def test_basic_initialization(self):
        """Test basic error handler initialization."""
        assert self.error_handler.logger == self.mock_logger
        assert self.error_handler.error_counts == {}
        assert self.error_handler.error_history == []
        assert self.error_handler.max_history_size == 1000
    
    def test_handle_advanced_folders_exception(self):
        """Test handling AdvancedFoldersException."""
        context = {"operation": "test_op"}
        exception = ValidationException(
            "Test validation error", context=context
        )
        
        # Handle without reraising
        result = self.error_handler.handle_exception(
            exception, reraise=False
        )
        
        assert result == exception
        assert len(self.error_handler.error_history) == 1
        assert self.error_handler.error_counts["ValidationException"] == 1
    
    def test_handle_generic_exception(self):
        """Test handling generic Python exception."""
        exception = ValueError("Generic error")
        context = {"file_path": "/test/path"}
        
        # Should wrap in AdvancedFoldersException
        with pytest.raises(AdvancedFoldersException) as exc_info:
            self.error_handler.handle_exception(
                exception, context=context, operation="test_op", reraise=True
            )
        
        wrapped_exception = exc_info.value
        assert "Validation error" in wrapped_exception.message
        assert wrapped_exception.cause == exception
        assert wrapped_exception.context["operation"] == "test_op"
    
    def test_filesystem_exception_wrapping(self):
        """Test wrapping filesystem-related exceptions."""
        exception = FileNotFoundError("File not found")
        
        with pytest.raises(FileSystemException):
            self.error_handler.handle_exception(exception, reraise=True)
    
    def test_performance_exception_wrapping(self):
        """Test wrapping performance-related exceptions."""
        exception = TimeoutError("Operation timeout")
        
        with pytest.raises(PerformanceException):
            self.error_handler.handle_exception(exception, reraise=True)
    
    def test_error_logging(self):
        """Test error logging functionality."""
        exception = ValidationException("Test error")
        
        self.error_handler.handle_exception(exception, reraise=False)
        
        # Should have logged the error
        self.mock_logger.warning.assert_called_once()
        
        # Check log message format
        call_args = self.mock_logger.warning.call_args
        log_message = call_args[0][0]
        assert exception.error_code in log_message
        assert "Test error" in log_message
    
    def test_error_statistics(self):
        """Test error statistics tracking."""
        # Generate some errors
        exceptions = [
            ValidationException("Error 1"),
            ValidationException("Error 2"),
            RepositoryException("Error 3"),
            PerformanceException("Error 4")
        ]
        
        for exc in exceptions:
            self.error_handler.handle_exception(exc, reraise=False)
        
        stats = self.error_handler.get_error_statistics()
        
        assert stats["total_errors"] == 4
        assert stats["error_counts"]["ValidationException"] == 2
        assert stats["error_counts"]["RepositoryException"] == 1
        assert stats["error_counts"]["PerformanceException"] == 1
        assert stats["history_size"] == 4
    
    def test_recent_errors(self):
        """Test recent errors retrieval."""
        # Generate some errors
        for i in range(5):
            exc = ValidationException(f"Error {i}")
            self.error_handler.handle_exception(exc, reraise=False)
        
        recent_errors = self.error_handler.get_recent_errors(limit=3)
        
        assert len(recent_errors) == 3
        assert recent_errors[-1]["message"] == "Error 4"  # Most recent
        assert recent_errors[0]["message"] == "Error 2"   # Oldest of the 3
    
    def test_error_history_limit(self):
        """Test error history size limit."""
        # Set small limit for testing
        self.error_handler.max_history_size = 3
        
        # Generate more errors than limit
        for i in range(5):
            exc = ValidationException(f"Error {i}")
            self.error_handler.handle_exception(exc, reraise=False)
        
        # Should maintain limit
        assert len(self.error_handler.error_history) == 3
        
        # Should keep most recent errors
        messages = [error["message"] for error in self.error_handler.error_history]
        assert "Error 2" in messages
        assert "Error 3" in messages
        assert "Error 4" in messages
        assert "Error 0" not in messages
        assert "Error 1" not in messages
    
    def test_clear_history(self):
        """Test clearing error history."""
        # Generate some errors
        for i in range(3):
            exc = ValidationException(f"Error {i}")
            self.error_handler.handle_exception(exc, reraise=False)
        
        # Clear history
        self.error_handler.clear_history()
        
        assert len(self.error_handler.error_history) == 0
        assert len(self.error_handler.error_counts) == 0
    
    def test_concurrent_error_handling(self):
        """Test concurrent error handling."""
        results = []
        threads = []
        
        def worker(thread_id):
            try:
                exc = ValidationException(f"Error from thread {thread_id}")
                self.error_handler.handle_exception(exc, reraise=False)
                results.append(f"success_{thread_id}")
            except Exception as e:
                results.append(f"error_{thread_id}_{str(e)}")
        
        # Start multiple threads
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All should succeed
        success_count = len([r for r in results if r.startswith("success")])
        assert success_count == 5
        
        # Should have all errors in history
        assert len(self.error_handler.error_history) == 5


class TestGracefulDegradation:
    """Test GracefulDegradation class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_error_handler = Mock()
        self.degradation = GracefulDegradation(self.mock_error_handler)
    
    def test_basic_initialization(self):
        """Test basic graceful degradation initialization."""
        assert self.degradation.error_handler == self.mock_error_handler
        assert self.degradation.fallback_strategies == {}
        assert self.degradation.degradation_active == {}
    
    def test_register_fallback(self):
        """Test registering fallback strategy."""
        def fallback_func():
            return "fallback_result"
        
        self.degradation.register_fallback(
            "test_operation",
            fallback_func,
            [ValueError, TypeError]
        )
        
        assert "test_operation" in self.degradation.fallback_strategies
        strategy = self.degradation.fallback_strategies["test_operation"]
        assert strategy["function"] is fallback_func
        assert strategy["conditions"] == [ValueError, TypeError]
    
    def test_successful_operation_no_fallback(self):
        """Test successful operation without fallback."""
        def primary_func(value):
            return value * 2
        
        result = self.degradation.execute_with_fallback(
            "test_op", primary_func, 5
        )
        
        assert result == 10
        assert not self.degradation.is_degraded("test_op")
    
    def test_fallback_execution(self):
        """Test fallback execution on primary failure."""
        def primary_func():
            raise ValueError("Primary failed")
        
        def fallback_func():
            return "fallback_result"
        
        self.degradation.register_fallback(
            "test_op", fallback_func, [ValueError]
        )
        
        result = self.degradation.execute_with_fallback(
            "test_op", primary_func
        )
        
        assert result == "fallback_result"
        assert self.degradation.is_degraded("test_op")
    
    def test_fallback_condition_mismatch(self):
        """Test that fallback only triggers for specified exceptions."""
        def primary_func():
            raise TypeError("Primary failed")
        
        def fallback_func():
            return "fallback_result"
        
        # Register fallback only for ValueError
        self.degradation.register_fallback(
            "test_op", fallback_func, [ValueError]
        )
        
        # Should not use fallback for TypeError
        with pytest.raises(TypeError):
            self.degradation.execute_with_fallback(
                "test_op", primary_func
            )
    
    def test_no_fallback_registered(self):
        """Test behavior when no fallback is registered."""
        def primary_func():
            raise ValueError("Primary failed")
        
        # Should reraise original exception
        with pytest.raises(ValueError):
            self.degradation.execute_with_fallback(
                "test_op", primary_func
            )
    
    def test_fallback_failure(self):
        """Test behavior when fallback also fails."""
        def primary_func():
            raise ValueError("Primary failed")
        
        def fallback_func():
            raise RuntimeError("Fallback failed")
        
        self.degradation.register_fallback(
            "test_op", fallback_func, [ValueError]
        )
        
        # Should reraise original exception when fallback fails
        with pytest.raises(ValueError):
            self.degradation.execute_with_fallback(
                "test_op", primary_func
            )
    
    def test_recovery_from_degraded_state(self):
        """Test recovery from degraded state."""
        call_count = 0
        
        def primary_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First call fails")
            return "success"
        
        def fallback_func():
            return "fallback_result"
        
        self.degradation.register_fallback(
            "test_op", fallback_func, [ValueError]
        )
        
        # First call should use fallback
        result1 = self.degradation.execute_with_fallback(
            "test_op", primary_func
        )
        assert result1 == "fallback_result"
        assert self.degradation.is_degraded("test_op")
        
        # Second call should succeed and clear degraded state
        result2 = self.degradation.execute_with_fallback(
            "test_op", primary_func
        )
        assert result2 == "success"
        assert not self.degradation.is_degraded("test_op")
    
    def test_degradation_status(self):
        """Test degradation status tracking."""
        def failing_func():
            raise ValueError("Failed")
        
        def fallback_func():
            return "fallback"
        
        # Register multiple operations
        operations = ["op1", "op2", "op3"]
        for op in operations:
            self.degradation.register_fallback(op, fallback_func, [ValueError])
        
        # Trigger degradation for some operations
        self.degradation.execute_with_fallback("op1", failing_func)
        self.degradation.execute_with_fallback("op3", failing_func)
        
        status = self.degradation.get_degradation_status()
        
        assert status["op1"] is True
        assert status.get("op2", False) is False
        assert status["op3"] is True


class TestGlobalFunctions:
    """Test global error handling functions."""
    
    def test_get_error_handler_singleton(self):
        """Test global error handler singleton."""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        
        assert handler1 is handler2  # Same instance
    
    def test_get_degradation_manager_singleton(self):
        """Test global degradation manager singleton."""
        manager1 = get_degradation_manager()
        manager2 = get_degradation_manager()
        
        assert manager1 is manager2  # Same instance
    
    def test_handle_errors_decorator(self):
        """Test handle_errors decorator."""
        @handle_errors(operation="test_operation", reraise=False)
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        assert result is None  # Should return None when not reraising
    
    def test_handle_errors_decorator_with_reraise(self):
        """Test handle_errors decorator with reraise."""
        @handle_errors(operation="test_operation", reraise=True)
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(AdvancedFoldersException):
            test_function()
    
    def test_handle_errors_decorator_with_fallback_return(self):
        """Test handle_errors decorator with fallback return value."""
        @handle_errors(
            operation="test_operation",
            reraise=False,
            fallback_return="fallback_value"
        )
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        assert result == "fallback_value"
    
    def test_safe_execute_function(self):
        """Test safe_execute function."""
        def test_function(value):
            if value < 0:
                raise ValueError("Negative value")
            return value * 2
        
        # Successful execution
        result = safe_execute(test_function, 5)
        assert result == 10
        
        # Failed execution with fallback
        result = safe_execute(
            test_function, -1,
            fallback_return="error_occurred"
        )
        assert result == "error_occurred"
    
    def test_with_fallback_decorator(self):
        """Test with_fallback decorator."""
        def fallback_function(*args, **kwargs):
            return "fallback_executed"
        
        @with_fallback(
            "test_operation",
            fallback_func=fallback_function,
            conditions=[ValueError]
        )
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        assert result == "fallback_executed"
    
    def test_with_fallback_decorator_no_fallback(self):
        """Test with_fallback decorator without explicit fallback function."""
        @with_fallback("test_operation")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"


class TestErrorHandlingEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_error_handler_with_none_logger(self):
        """Test error handler with None logger."""
        handler = ErrorHandler(logger=None)
        
        # Should not raise exception
        exception = ValidationException("Test error")
        handler.handle_exception(exception, reraise=False)
        
        assert len(handler.error_history) == 1
    
    def test_error_with_circular_reference(self):
        """Test error handling with circular references in context."""
        class CircularRef:
            def __init__(self):
                self.ref = self
        
        circular_obj = CircularRef()
        context = {"circular": circular_obj}
        
        handler = ErrorHandler()
        exception = ValidationException("Test error", context=context)
        
        # Should handle gracefully without infinite recursion
        handler.handle_exception(exception, reraise=False)
        
        assert len(handler.error_history) == 1
    
    def test_extremely_large_error_context(self):
        """Test handling of extremely large error context."""
        large_context = {f"key_{i}": f"value_{i}" * 1000 for i in range(100)}
        
        handler = ErrorHandler()
        exception = ValidationException("Test error", context=large_context)
        
        # Should handle large context without issues
        handler.handle_exception(exception, reraise=False)
        
        assert len(handler.error_history) == 1
    
    def test_concurrent_degradation_management(self):
        """Test concurrent degradation management."""
        degradation = GracefulDegradation()
        results = []
        threads = []
        
        def fallback_function():
            return "fallback"
        
        def worker(thread_id):
            try:
                # Register fallback
                degradation.register_fallback(
                    f"op_{thread_id}",
                    fallback_function,
                    [ValueError]
                )
                
                # Execute with fallback
                def failing_func():
                    raise ValueError(f"Error from thread {thread_id}")
                
                result = degradation.execute_with_fallback(
                    f"op_{thread_id}",
                    failing_func
                )
                results.append(f"success_{thread_id}_{result}")
            except Exception as e:
                results.append(f"error_{thread_id}_{str(e)}")
        
        # Start multiple threads
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All should succeed with fallback
        success_count = len([r for r in results if r.startswith("success")])
        assert success_count == 5
        
        # All operations should be degraded
        for i in range(5):
            assert degradation.is_degraded(f"op_{i}")


if __name__ == "__main__":
    pytest.main([__file__])