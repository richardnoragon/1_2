"""Exception hierarchy init module."""

from .advanced_folders_exceptions import (AdvancedFoldersException,
                                          ConfigurationException,
                                          FileSystemException,
                                          PerformanceException,
                                          PermissionException,
                                          RepositoryException, SearchException,
                                          ValidationException, config_error,
                                          filesystem_error, performance_error,
                                          repository_error, search_error,
                                          validation_error)

__all__ = [
    "AdvancedFoldersException",
    "ValidationException",
    "RepositoryException",
    "ConfigurationException",
    "SearchException",
    "FileSystemException",
    "PerformanceException",
    "PermissionException",
    "validation_error",
    "repository_error",
    "config_error",
    "search_error",
    "filesystem_error",
    "performance_error"
]

