"""Legacy folder-model compatibility definitions.

Several integration components import model classes from
``advanced_folders.core.folder_models``. The canonical model modules changed,
so this file provides a stable compatibility layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..validation.validator_framework import ValidationResult


@dataclass
class SearchFilter:
    """Simple search-filter container for legacy imports."""

    field: str = ""
    operator: str = "="
    value: Any = None


@dataclass
class SearchParameter:
    """Generic search parameter model used by legacy integration code."""

    query: str = ""
    filters: Dict[str, Any] = field(default_factory=dict)
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    limit: Optional[int] = None
    offset: int = 0
    parameter_type: "ParameterType" = None
    parameter_operator: "ParameterOperator" = None

    def __post_init__(self) -> None:
        if self.parameter_type is None:
            self.parameter_type = ParameterType.NAME
        if self.parameter_operator is None:
            self.parameter_operator = ParameterOperator.CONTAINS


class ParameterType(str, Enum):
    """Legacy parameter type enum for DB serialization/deserialization."""

    NAME = "name"
    CONTENT = "content"
    EXTENSION = "extension"
    PATH = "path"
    SIZE = "size"
    DATE_MODIFIED = "date_modified"


class ParameterOperator(str, Enum):
    """Legacy operator enum for query persistence compatibility."""

    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


class ScanStatus(str, Enum):
    """Legacy scan status enum used by database integration code."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FileMetadata:
    """Flexible file metadata model used by legacy and modern call sites."""

    file_id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    file_extension: str = ""
    directory_path: str = ""
    file_size: int = 0
    created_date: Optional[Any] = None
    modified_date: Optional[Any] = None
    accessed_date: Optional[Any] = None
    file_hash: Optional[str] = None
    mime_type: Optional[str] = None
    file_permissions: Optional[str] = None
    is_hidden: bool = False
    is_system: bool = False
    content_summary: Optional[str] = None
    metadata_extracted_at: Optional[datetime] = None
    scan_session_id: Optional[str] = None


class ConfigurationManager:
    """Minimal in-memory configuration manager compatibility class."""

    def __init__(self):
        self._settings: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._settings)


__all__ = [
    "ConfigurationManager",
    "FileMetadata",
    "ParameterOperator",
    "ParameterType",
    "ScanStatus",
    "SearchFilter",
    "SearchParameter",
    "ValidationResult",
]
