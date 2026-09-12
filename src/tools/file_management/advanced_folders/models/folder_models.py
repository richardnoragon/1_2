"""Compatibility aliases for legacy ``models.folder_models`` imports."""

from ..core.folder_models import (
    ConfigurationManager,
    FileMetadata,
    ParameterOperator,
    ParameterType,
    ScanStatus,
    SearchFilter,
    SearchParameter,
    ValidationResult,
)
from .folder_configuration import FolderConfiguration

__all__ = [
    "ConfigurationManager",
    "FileMetadata",
    "FolderConfiguration",
    "ParameterOperator",
    "ParameterType",
    "ScanStatus",
    "SearchFilter",
    "SearchParameter",
    "ValidationResult",
]
