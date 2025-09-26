"""
Custom exception hierarchy for Advanced Folders feature.

This module defines a comprehensive exception hierarchy that provides
clear error categorization and detailed error information for all
Advanced Folders operations.
"""

from typing import Any, Dict, Optional


class AdvancedFoldersException(Exception):
    """
    Base exception for all Advanced Folders related errors.
    
    Provides structured error information with context and suggestions.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            context: Additional context information
            suggestion: Suggested resolution or next steps
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "AF_GENERAL_ERROR"
        self.context = context or {}
        self.suggestion = suggestion
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "suggestion": self.suggestion,
            "cause": str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        """String representation with error code and context."""
        parts = [f"[{self.error_code}] {self.message}"]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        
        return " | ".join(parts)


class ValidationException(AdvancedFoldersException):
    """
    Exception raised when data validation fails.
    
    Used for all validation-related errors including field validation,
    business rule violations, and data integrity issues.
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Any = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize validation exception.
        
        Args:
            message: Validation error message
            field_name: Name of the field that failed validation
            field_value: Value that failed validation
            validation_rule: Name of the validation rule that failed
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "field_name": field_name,
            "field_value": field_value,
            "validation_rule": validation_rule
        })
        
        error_code = kwargs.get('error_code', "AF_VALIDATION_ERROR")
        suggestion = kwargs.get('suggestion') or self._get_validation_suggestion(validation_rule)
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )
    
    def _get_validation_suggestion(self, validation_rule: Optional[str]) -> Optional[str]:
        """Get suggestion based on validation rule."""
        suggestions = {
            "required": "Please provide a value for this required field.",
            "path_exists": "Please ensure the specified path exists and is accessible.",
            "max_length": "Please reduce the length of the input.",
            "min_length": "Please provide a longer input.",
            "regex": "Please ensure the input matches the required format.",
            "unique": "Please provide a unique value that doesn't already exist.",
            "range": "Please provide a value within the allowed range."
        }
        return suggestions.get(validation_rule, "Please check the input value and try again.")


class RepositoryException(AdvancedFoldersException):
    """
    Exception raised for database and repository operation errors.
    
    Used for all data persistence related errors including connection issues,
    query failures, and transaction problems.
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table_name: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize repository exception.
        
        Args:
            message: Repository error message
            operation: Database operation that failed (SELECT, INSERT, etc.)
            table_name: Name of the database table involved
            query: SQL query that failed (truncated for security)
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "operation": operation,
            "table_name": table_name,
            "query": query[:100] + "..." if query and len(query) > 100 else query
        })
        
        error_code = kwargs.get('error_code', "AF_REPOSITORY_ERROR")
        suggestion = kwargs.get('suggestion') or self._get_repository_suggestion(operation)
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )
    
    def _get_repository_suggestion(self, operation: Optional[str]) -> Optional[str]:
        """Get suggestion based on repository operation."""
        suggestions = {
            "SELECT": "Check if the database is accessible and the query is valid.",
            "INSERT": "Verify that all required fields are provided and constraints are met.",
            "UPDATE": "Ensure the record exists and you have permission to modify it.",
            "DELETE": "Verify the record exists and you have permission to delete it.",
            "CREATE": "Check database permissions and table schema.",
            "DROP": "Verify you have permission to drop the table."
        }
        return suggestions.get(operation, "Check database connectivity and permissions.")


class ConfigurationException(AdvancedFoldersException):
    """
    Exception raised for configuration-related errors.
    
    Used for configuration loading, validation, and persistence errors.
    """
    
    def __init__(
        self,
        message: str,
        config_section: Optional[str] = None,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration exception.
        
        Args:
            message: Configuration error message
            config_section: Configuration section name
            config_key: Configuration key name
            config_file: Configuration file path
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "config_section": config_section,
            "config_key": config_key,
            "config_file": config_file
        })
        
        error_code = kwargs.get('error_code', "AF_CONFIG_ERROR")
        suggestion = kwargs.get('suggestion') or "Check configuration file syntax and permissions."
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )


class SearchException(AdvancedFoldersException):
    """
    Exception raised for search operation errors.
    
    Used for search execution failures, index corruption, and performance issues.
    """
    
    def __init__(
        self,
        message: str,
        search_query: Optional[str] = None,
        folder_id: Optional[str] = None,
        search_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize search exception.
        
        Args:
            message: Search error message
            search_query: Search query that failed
            folder_id: ID of the folder being searched
            search_type: Type of search operation
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "search_query": search_query,
            "folder_id": folder_id,
            "search_type": search_type
        })
        
        error_code = kwargs.get('error_code', "AF_SEARCH_ERROR")
        suggestion = kwargs.get('suggestion') or "Simplify the search query or check folder accessibility."
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )


class FileSystemException(AdvancedFoldersException):
    """
    Exception raised for file system operation errors.
    
    Used for file access issues, permission problems, and I/O errors.
    """
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize file system exception.
        
        Args:
            message: File system error message
            file_path: Path of the file that caused the error
            operation: File system operation that failed
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "file_path": file_path,
            "operation": operation
        })
        
        error_code = kwargs.get('error_code', "AF_FILESYSTEM_ERROR")
        suggestion = kwargs.get('suggestion') or "Check file permissions and path accessibility."
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )


class PerformanceException(AdvancedFoldersException):
    """
    Exception raised for performance-related issues.
    
    Used for timeout errors, memory issues, and resource exhaustion.
    """
    
    def __init__(
        self,
        message: str,
        operation_timeout: Optional[float] = None,
        memory_usage_mb: Optional[float] = None,
        resource_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize performance exception.
        
        Args:
            message: Performance error message
            operation_timeout: Timeout value that was exceeded
            memory_usage_mb: Memory usage in MB when error occurred
            resource_type: Type of resource that was exhausted
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "operation_timeout": operation_timeout,
            "memory_usage_mb": memory_usage_mb,
            "resource_type": resource_type
        })
        
        error_code = kwargs.get('error_code', "AF_PERFORMANCE_ERROR")
        suggestion = kwargs.get('suggestion') or "Consider reducing operation scope or increasing timeout limits."
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )


class PermissionException(AdvancedFoldersException):
    """
    Exception raised for permission and access control errors.
    
    Used specifically for file system permission denials and access violations.
    """
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        required_permission: Optional[str] = None,
        current_user: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize permission exception.
        
        Args:
            message: Permission error message
            file_path: Path that couldn't be accessed
            required_permission: Permission that was required
            current_user: Current user attempting the operation
            **kwargs: Additional arguments for base exception
        """
        context = kwargs.get('context', {})
        context.update({
            "file_path": file_path,
            "required_permission": required_permission,
            "current_user": current_user
        })
        
        error_code = kwargs.get('error_code', "AF_PERMISSION_ERROR")
        suggestion = kwargs.get('suggestion') or "Check file permissions and run with appropriate privileges."
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggestion=suggestion,
            cause=kwargs.get('cause')
        )


# Convenience functions for creating common exceptions
def validation_error(message: str, field_name: Optional[str] = None, **kwargs) -> ValidationException:
    """Create a validation exception with standard formatting."""
    return ValidationException(message, field_name=field_name, **kwargs)


def repository_error(message: str, operation: Optional[str] = None, **kwargs) -> RepositoryException:
    """Create a repository exception with standard formatting."""
    return RepositoryException(message, operation=operation, **kwargs)


def config_error(message: str, section: Optional[str] = None, **kwargs) -> ConfigurationException:
    """Create a configuration exception with standard formatting."""
    return ConfigurationException(message, config_section=section, **kwargs)


def search_error(message: str, query: Optional[str] = None, **kwargs) -> SearchException:
    """Create a search exception with standard formatting."""
    return SearchException(message, search_query=query, **kwargs)


def filesystem_error(message: str, path: Optional[str] = None, **kwargs) -> FileSystemException:
    """Create a file system exception with standard formatting."""
    return FileSystemException(message, file_path=path, **kwargs)


def performance_error(message: str, timeout: Optional[float] = None, **kwargs) -> PerformanceException:
    """Create a performance exception with standard formatting."""
    return PerformanceException(message, operation_timeout=timeout, **kwargs)