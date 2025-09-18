"""
Unit tests for Advanced Folders exception hierarchy.

Tests the comprehensive exception system with error codes,
context preservation, and structured error information.
"""

from datetime import datetime, timezone
from typing import Any, Dict

import pytest

from src.tools.file_management.advanced_folders_legacy.exceptions.advanced_folders_exceptions import (
    AdvancedFoldersException, ConfigurationException, FileSystemException,
    PerformanceException, RepositoryException, SearchException,
    ValidationException)


class TestAdvancedFoldersException:
    """Test the base AdvancedFoldersException class."""
    
    def test_basic_exception_creation(self):
        """Test basic exception creation."""
        exception = AdvancedFoldersException("Test error")
        
        assert str(exception) == "Test error"
        assert exception.message == "Test error"
        assert exception.error_code.startswith("AF")
        assert exception.context == {}
        assert exception.suggestion is None
        assert exception.cause is None
    
    def test_exception_with_context(self):
        """Test exception creation with context."""
        context = {
            "operation": "test_operation",
            "file_path": "/test/path",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        exception = AdvancedFoldersException(
            "Test error with context",
            context=context
        )
        
        assert exception.context == context
        assert exception.context["operation"] == "test_operation"
    
    def test_exception_with_suggestion(self):
        """Test exception creation with suggestion."""
        suggestion = "Try checking the file permissions"
        exception = AdvancedFoldersException(
            "Permission denied",
            suggestion=suggestion
        )
        
        assert exception.suggestion == suggestion
    
    def test_exception_with_cause(self):
        """Test exception creation with cause."""
        original_error = ValueError("Original error")
        exception = AdvancedFoldersException(
            "Wrapped error",
            cause=original_error
        )
        
        assert exception.cause == original_error
        assert isinstance(exception.__cause__, ValueError)
    
    def test_exception_full_context(self):
        """Test exception with all parameters."""
        context = {"operation": "full_test"}
        suggestion = "Full test suggestion"
        cause = RuntimeError("Full test cause")
        
        exception = AdvancedFoldersException(
            "Full test error",
            context=context,
            suggestion=suggestion,
            cause=cause
        )
        
        assert exception.message == "Full test error"
        assert exception.context == context
        assert exception.suggestion == suggestion
        assert exception.cause == cause


class TestValidationException:
    """Test ValidationException specific functionality."""
    
    def test_validation_exception_creation(self):
        """Test ValidationException creation."""
        exception = ValidationException("Invalid input")
        
        assert isinstance(exception, AdvancedFoldersException)
        assert exception.error_code.startswith("VLD")
        assert "validation" in exception.message.lower() or "Invalid input" in exception.message
    
    def test_validation_exception_with_field(self):
        """Test ValidationException with field context."""
        context = {
            "field": "email",
            "value": "invalid_email",
            "validation_rule": "email_format"
        }
        
        exception = ValidationException(
            "Invalid email format",
            context=context,
            suggestion="Provide a valid email address"
        )
        
        assert exception.context["field"] == "email"
        assert "email" in exception.suggestion.lower()
    
    def test_validation_exception_error_code_uniqueness(self):
        """Test that ValidationException error codes are unique."""
        exc1 = ValidationException("Error 1")
        exc2 = ValidationException("Error 2")
        
        assert exc1.error_code != exc2.error_code
        assert exc1.error_code.startswith("VLD")
        assert exc2.error_code.startswith("VLD")


class TestRepositoryException:
    """Test RepositoryException specific functionality."""
    
    def test_repository_exception_creation(self):
        """Test RepositoryException creation."""
        exception = RepositoryException("Database connection failed")
        
        assert isinstance(exception, AdvancedFoldersException)
        assert exception.error_code.startswith("REPO")
    
    def test_repository_exception_with_sql_context(self):
        """Test RepositoryException with SQL context."""
        context = {
            "sql_query": "SELECT * FROM configurations",
            "table": "configurations",
            "operation": "select"
        }
        
        exception = RepositoryException(
            "SQL execution failed",
            context=context,
            suggestion="Check database connectivity"
        )
        
        assert exception.context["sql_query"] == "SELECT * FROM configurations"
        assert "database" in exception.suggestion.lower()


class TestConfigurationException:
    """Test ConfigurationException specific functionality."""
    
    def test_configuration_exception_creation(self):
        """Test ConfigurationException creation."""
        exception = ConfigurationException("Invalid configuration")
        
        assert isinstance(exception, AdvancedFoldersException)
        assert exception.error_code.startswith("CFG")
    
    def test_configuration_exception_with_config_context(self):
        """Test ConfigurationException with configuration context."""
        context = {
            "config_file": "/path/to/config.json",
            "config_section": "advanced_folders",
            "invalid_key": "max_depth"
        }
        
        exception = ConfigurationException(
            "Invalid configuration value",
            context=context,
            suggestion="Check configuration documentation"
        )
        
        assert exception.context["config_file"] == "/path/to/config.json"


class TestSearchException:
    """Test SearchException specific functionality."""
    
    def test_search_exception_creation(self):
        """Test SearchException creation."""
        exception = SearchException("Search query failed")
        
        assert isinstance(exception, AdvancedFoldersException)
        assert exception.error_code.startswith("SRCH")
    
    def test_search_exception_with_query_context(self):
        """Test SearchException with search query context."""
        context = {
            "query": "*.pdf AND size:>1MB",
            "search_path": "/documents",
            "timeout": 30
        }
        
        exception = SearchException(
            "Search timeout exceeded",
            context=context,
            suggestion="Try a more specific search query"
        )
        
        assert exception.context["query"] == "*.pdf AND size:>1MB"
        assert "timeout" in exception.message.lower()


class TestFileSystemException:
    """Test FileSystemException specific functionality."""
    
    def test_filesystem_exception_creation(self):
        """Test FileSystemException creation."""
        exception = FileSystemException("File not found")
        
        assert isinstance(exception, AdvancedFoldersException)
        assert exception.error_code.startswith("FS")
    
    def test_filesystem_exception_with_path_context(self):
        """Test FileSystemException with file path context."""
        context = {
            "file_path": "/path/to/missing/file.txt",
            "operation": "read",
            "permissions": "644"
        }
        
        exception = FileSystemException(
            "Permission denied",
            context=context,
            suggestion="Check file permissions and ownership"
        )
        
        assert exception.context["file_path"] == "/path/to/missing/file.txt"
        assert "permission" in exception.suggestion.lower()


class TestPerformanceException:
    """Test PerformanceException specific functionality."""
    
    def test_performance_exception_creation(self):
        """Test PerformanceException creation."""
        exception = PerformanceException("Operation too slow")
        
        assert isinstance(exception, AdvancedFoldersException)
        assert exception.error_code.startswith("PERF")
    
    def test_performance_exception_with_metrics_context(self):
        """Test PerformanceException with performance metrics."""
        context = {
            "operation": "folder_scan",
            "duration_seconds": 45.2,
            "threshold_seconds": 30.0,
            "files_processed": 1500
        }
        
        exception = PerformanceException(
            "Scan operation exceeded timeout",
            context=context,
            suggestion="Consider reducing search scope or increasing timeout"
        )
        
        assert exception.context["duration_seconds"] == 45.2
        assert "timeout" in exception.suggestion.lower()


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from AdvancedFoldersException."""
        exception_classes = [
            ValidationException,
            RepositoryException,
            ConfigurationException,
            SearchException,
            FileSystemException,
            PerformanceException
        ]
        
        for exc_class in exception_classes:
            exception = exc_class("Test message")
            assert isinstance(exception, AdvancedFoldersException)
            assert isinstance(exception, Exception)
    
    def test_exception_error_code_prefixes(self):
        """Test that each exception type has correct error code prefix."""
        test_cases = [
            (ValidationException, "VLD"),
            (RepositoryException, "REPO"),
            (ConfigurationException, "CFG"),
            (SearchException, "SRCH"),
            (FileSystemException, "FS"),
            (PerformanceException, "PERF")
        ]
        
        for exc_class, expected_prefix in test_cases:
            exception = exc_class("Test message")
            assert exception.error_code.startswith(expected_prefix)
    
    def test_exception_can_be_caught_as_base(self):
        """Test that specific exceptions can be caught as base type."""
        with pytest.raises(AdvancedFoldersException):
            raise ValidationException("Test validation error")
        
        with pytest.raises(AdvancedFoldersException):
            raise RepositoryException("Test repository error")
    
    def test_exception_context_preservation(self):
        """Test that context is preserved through exception hierarchy."""
        context = {"test_key": "test_value"}
        
        try:
            raise ValidationException("Test error", context=context)
        except AdvancedFoldersException as e:
            assert e.context == context
            assert e.context["test_key"] == "test_value"


class TestExceptionEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_exception_with_none_message(self):
        """Test exception creation with None message."""
        exception = AdvancedFoldersException(None)
        assert exception.message == "None"
        assert str(exception) == "None"
    
    def test_exception_with_empty_message(self):
        """Test exception creation with empty message."""
        exception = AdvancedFoldersException("")
        assert exception.message == ""
        assert str(exception) == ""
    
    def test_exception_with_none_context(self):
        """Test exception creation with None context."""
        exception = AdvancedFoldersException("Test", context=None)
        assert exception.context == {}
    
    def test_exception_with_large_context(self):
        """Test exception with large context dictionary."""
        large_context = {f"key_{i}": f"value_{i}" for i in range(1000)}
        
        exception = AdvancedFoldersException("Test", context=large_context)
        assert len(exception.context) == 1000
        assert exception.context["key_500"] == "value_500"
    
    def test_exception_serialization_friendly(self):
        """Test that exceptions don't break with complex objects in context."""
        # This shouldn't raise an exception even with complex objects
        context = {
            "datetime": datetime.now(),
            "path": "/test/path",
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        exception = AdvancedFoldersException("Test", context=context)
        assert exception.context["path"] == "/test/path"
        assert exception.context["list"] == [1, 2, 3]


if __name__ == "__main__":
    pytest.main([__file__])