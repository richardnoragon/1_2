"""
Advanced Folders Feature for Richard's File Utilities.

This module provides enterprise-grade folder management capabilities with
intelligent search, filtering, and organization features.

Architecture:
- Models: Core data structures and business logic
- Validation: Comprehensive data validation framework
- Repository: Data access layer with CRUD operations
- Exceptions: Custom exception hierarchy
- Services: Business logic and orchestration
"""

from .exceptions.advanced_folders_exceptions import (AdvancedFoldersException,
                                                     ConfigurationException,
                                                     RepositoryException,
                                                     ValidationException)
from .models.folder_configuration import FolderConfiguration
from .models.search_parameters import SearchParameters
from .repository.folder_repository import FolderRepository
from .validation.validator_framework import ValidationFramework

__version__ = "1.0.0"
__author__ = "Richard's File Utilities Team"

__all__ = [
    "FolderConfiguration",
    "SearchParameters", 
    "ValidationFramework",
    "FolderRepository",
    "AdvancedFoldersException",
    "ValidationException",
    "RepositoryException",
    "ConfigurationException"
]