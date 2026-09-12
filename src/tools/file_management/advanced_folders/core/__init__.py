"""Core compatibility exports for Advanced Folders.

This package historically exposed model symbols from ``core``. The active
implementations live in ``models`` and ``validation``; these re-exports keep
legacy imports stable.
"""

from .folder_models import (
    ConfigurationManager,
    FileMetadata,
    SearchFilter,
    SearchParameter,
    ValidationResult,
)
from ..models.folder_configuration import FolderConfiguration

__all__ = [
    "ConfigurationManager",
    "FileMetadata",
    "FolderConfiguration",
    "SearchFilter",
    "SearchParameter",
    "ValidationResult",
]
