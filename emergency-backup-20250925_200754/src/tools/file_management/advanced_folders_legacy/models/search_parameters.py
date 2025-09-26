"""
SearchParameters model for Advanced Folders feature.

This module defines the SearchParameters model that encapsulates
all search criteria, filters, and options for folder searches.
"""

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set, Union

from ..exceptions import ValidationException
from ..validation.validator_framework import ValidationFramework


class SearchType(Enum):
    """Types of search operations."""

    FILE_NAME = "file_name"
    CONTENT = "content"
    METADATA = "metadata"
    COMBINED = "combined"


class SizeUnit(Enum):
    """File size units."""

    BYTES = "bytes"
    KB = "kb"
    MB = "mb"
    GB = "gb"
    TB = "tb"


class DateField(Enum):
    """Date fields for filtering."""

    CREATED = "created"
    MODIFIED = "modified"
    ACCESSED = "accessed"


class SortField(Enum):
    """Fields available for sorting results."""

    NAME = "name"
    SIZE = "size"
    DATE_CREATED = "date_created"
    DATE_MODIFIED = "date_modified"
    DATE_ACCESSED = "date_accessed"
    EXTENSION = "extension"
    PATH = "path"
    RELEVANCE = "relevance"


class SortOrder(Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class LogicalOperator(Enum):
    """Logical operators for combining criteria."""

    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class FileTypeFilter:
    """File type filtering configuration."""

    include_extensions: Set[str] = field(default_factory=set)
    exclude_extensions: Set[str] = field(default_factory=set)
    include_mime_types: Set[str] = field(default_factory=set)
    exclude_mime_types: Set[str] = field(default_factory=set)

    # Predefined categories
    include_documents: bool = False
    include_images: bool = False
    include_videos: bool = False
    include_audio: bool = False
    include_archives: bool = False
    include_executables: bool = False

    def __post_init__(self):
        """Normalize and validate file type filter."""
        # Normalize extensions (remove dots, convert to lowercase)
        self.include_extensions = {
            ext.lower().lstrip(".") for ext in self.include_extensions
        }
        self.exclude_extensions = {
            ext.lower().lstrip(".") for ext in self.exclude_extensions
        }

        # Normalize MIME types
        self.include_mime_types = {
            mime.lower().strip() for mime in self.include_mime_types
        }
        self.exclude_mime_types = {
            mime.lower().strip() for mime in self.exclude_mime_types
        }

    def get_category_extensions(self) -> Set[str]:
        """Get extensions for selected categories."""
        extensions = set()

        if self.include_documents:
            extensions.update(
                [
                    "txt",
                    "doc",
                    "docx",
                    "pdf",
                    "rtf",
                    "odt",
                    "xls",
                    "xlsx",
                    "ods",
                    "ppt",
                    "pptx",
                    "odp",
                ]
            )

        if self.include_images:
            extensions.update(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "bmp",
                    "tiff",
                    "svg",
                    "webp",
                    "ico",
                    "psd",
                    "raw",
                ]
            )

        if self.include_videos:
            extensions.update(
                [
                    "mp4",
                    "avi",
                    "mkv",
                    "mov",
                    "wmv",
                    "flv",
                    "webm",
                    "m4v",
                    "mpg",
                    "mpeg",
                    "3gp",
                ]
            )

        if self.include_audio:
            extensions.update(
                [
                    "mp3",
                    "wav",
                    "flac",
                    "aac",
                    "ogg",
                    "wma",
                    "m4a",
                    "opus",
                    "aiff",
                    "au",
                ]
            )

        if self.include_archives:
            extensions.update(
                [
                    "zip",
                    "rar",
                    "7z",
                    "tar",
                    "gz",
                    "bz2",
                    "xz",
                    "cab",
                    "ace",
                    "arj",
                ]
            )

        if self.include_executables:
            extensions.update(
                [
                    "exe",
                    "msi",
                    "deb",
                    "rpm",
                    "dmg",
                    "pkg",
                    "app",
                    "appx",
                    "snap",
                ]
            )

        return extensions

    def matches_extension(self, extension: str) -> bool:
        """Check if extension matches filter criteria."""
        ext = extension.lower().lstrip(".")

        # Get all included extensions (explicit + categories)
        all_included = self.include_extensions | self.get_category_extensions()

        # If no includes specified, assume all are included
        if not all_included:
            return ext not in self.exclude_extensions

        # Must be in included and not in excluded
        return ext in all_included and ext not in self.exclude_extensions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "include_extensions": list(self.include_extensions),
            "exclude_extensions": list(self.exclude_extensions),
            "include_mime_types": list(self.include_mime_types),
            "exclude_mime_types": list(self.exclude_mime_types),
            "include_documents": self.include_documents,
            "include_images": self.include_images,
            "include_videos": self.include_videos,
            "include_audio": self.include_audio,
            "include_archives": self.include_archives,
            "include_executables": self.include_executables,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileTypeFilter":
        """Create instance from dictionary."""
        return cls(
            include_extensions=set(data.get("include_extensions", [])),
            exclude_extensions=set(data.get("exclude_extensions", [])),
            include_mime_types=set(data.get("include_mime_types", [])),
            exclude_mime_types=set(data.get("exclude_mime_types", [])),
            include_documents=data.get("include_documents", False),
            include_images=data.get("include_images", False),
            include_videos=data.get("include_videos", False),
            include_audio=data.get("include_audio", False),
            include_archives=data.get("include_archives", False),
            include_executables=data.get("include_executables", False),
        )


@dataclass
class SizeFilter:
    """File size filtering configuration."""

    min_size: Optional[int] = None  # Size in bytes
    max_size: Optional[int] = None  # Size in bytes
    unit: SizeUnit = SizeUnit.BYTES

    def __post_init__(self):
        """Validate size filter."""
        if self.min_size is not None and self.min_size < 0:
            raise ValidationException(
                "Minimum size cannot be negative",
                field_name="min_size",
                field_value=self.min_size,
            )

        if self.max_size is not None and self.max_size < 0:
            raise ValidationException(
                "Maximum size cannot be negative",
                field_name="max_size",
                field_value=self.max_size,
            )

        if (
            self.min_size is not None
            and self.max_size is not None
            and self.min_size > self.max_size
        ):
            raise ValidationException(
                "Minimum size cannot be greater than maximum size",
                field_name="min_size",
                field_value=self.min_size,
            )

    @classmethod
    def from_human_readable(
        cls,
        min_size_str: Optional[str] = None,
        max_size_str: Optional[str] = None,
    ) -> "SizeFilter":
        """
        Create size filter from human-readable strings.

        Args:
            min_size_str: Minimum size (e.g., "10MB", "1.5GB")
            max_size_str: Maximum size (e.g., "100MB", "2GB")

        Returns:
            SizeFilter instance
        """

        def parse_size(size_str: str) -> int:
            """Parse human-readable size to bytes."""
            if not size_str:
                return None

            size_str = size_str.strip().upper()

            # Extract number and unit
            match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$", size_str)
            if not match:
                raise ValidationException(
                    f"Invalid size format: {size_str}",
                    suggestion="Use format like '10MB', '1.5GB', etc.",
                )

            value = float(match.group(1))
            unit_str = match.group(2)

            # Convert to bytes
            multipliers = {
                "B": 1,
                "KB": 1024,
                "MB": 1024**2,
                "GB": 1024**3,
                "TB": 1024**4,
            }

            # Default to bytes if no unit specified
            multiplier = multipliers.get(unit_str, 1)

            return int(value * multiplier)

        min_bytes = parse_size(min_size_str) if min_size_str else None
        max_bytes = parse_size(max_size_str) if max_size_str else None

        return cls(min_size=min_bytes, max_size=max_bytes)

    def matches_size(self, size_bytes: int) -> bool:
        """Check if file size matches filter criteria."""
        if self.min_size is not None and size_bytes < self.min_size:
            return False

        if self.max_size is not None and size_bytes > self.max_size:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "min_size": self.min_size,
            "max_size": self.max_size,
            "unit": self.unit.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SizeFilter":
        """Create instance from dictionary."""
        return cls(
            min_size=data.get("min_size"),
            max_size=data.get("max_size"),
            unit=SizeUnit(data.get("unit", "bytes")),
        )


@dataclass
class DateFilter:
    """Date-based filtering configuration."""

    field: DateField = DateField.MODIFIED
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    relative_days: Optional[int] = None  # Last N days

    def __post_init__(self):
        """Validate and process date filter."""
        # Convert relative days to absolute dates
        if self.relative_days is not None:
            if self.relative_days < 0:
                raise ValidationException(
                    "Relative days cannot be negative",
                    field_name="relative_days",
                    field_value=self.relative_days,
                )

            now = datetime.now(timezone.utc)
            self.from_date = now - timedelta(days=self.relative_days)
            self.to_date = now

        # Validate date range
        if (
            self.from_date is not None
            and self.to_date is not None
            and self.from_date > self.to_date
        ):
            raise ValidationException(
                "From date cannot be after to date",
                field_name="from_date",
                field_value=self.from_date,
            )

        # Ensure timezone awareness
        if self.from_date and self.from_date.tzinfo is None:
            self.from_date = self.from_date.replace(tzinfo=timezone.utc)

        if self.to_date and self.to_date.tzinfo is None:
            self.to_date = self.to_date.replace(tzinfo=timezone.utc)

    def matches_date(self, file_date: datetime) -> bool:
        """Check if file date matches filter criteria."""
        if file_date.tzinfo is None:
            file_date = file_date.replace(tzinfo=timezone.utc)

        if self.from_date and file_date < self.from_date:
            return False

        if self.to_date and file_date > self.to_date:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field": self.field.value,
            "from_date": (
                self.from_date.isoformat() if self.from_date else None
            ),
            "to_date": self.to_date.isoformat() if self.to_date else None,
            "relative_days": self.relative_days,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DateFilter":
        """Create instance from dictionary."""
        from_date = None
        to_date = None

        if data.get("from_date"):
            from_date = datetime.fromisoformat(data["from_date"])

        if data.get("to_date"):
            to_date = datetime.fromisoformat(data["to_date"])

        return cls(
            field=DateField(data.get("field", "modified")),
            from_date=from_date,
            to_date=to_date,
            relative_days=data.get("relative_days"),
        )


@dataclass
class ContentSearchOptions:
    """Options for content-based search."""

    case_sensitive: bool = False
    whole_words_only: bool = False
    use_regex: bool = False
    include_metadata: bool = True
    search_inside_archives: bool = False
    max_file_size_mb: int = (
        100  # Don't search content of files larger than this
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentSearchOptions":
        """Create instance from dictionary."""
        return cls(**data)


class SearchParameters:
    """
    Comprehensive search parameters for Advanced Folders.

    This class encapsulates all search criteria, filters, and options
    for performing file searches within advanced folders.
    """

    def __init__(
        self,
        search_type: SearchType = SearchType.FILE_NAME,
        query: str = "",
        folder_id: Optional[str] = None,
    ):
        """
        Initialize search parameters.

        Args:
            search_type: Type of search to perform
            query: Search query string
            folder_id: ID of folder to search (if None, searches all folders)
        """
        # Basic search configuration
        self.search_type = search_type
        self.query = query
        self.folder_id = folder_id

        # Query processing options
        self.use_regex = False
        self.case_sensitive = False
        self.whole_words_only = False
        self.fuzzy_search = False
        self.fuzzy_threshold = 0.8

        # Filter configurations
        self.file_type_filter = FileTypeFilter()
        self.size_filter: Optional[SizeFilter] = None
        self.date_filters: List[DateFilter] = []

        # Path filtering
        self.include_paths: List[str] = []
        self.exclude_paths: List[str] = []
        self.exclude_patterns: List[str] = []

        # Content search options
        self.content_search_options = ContentSearchOptions()

        # Result configuration
        self.max_results = 10000
        self.offset = 0
        self.sort_field = SortField.RELEVANCE
        self.sort_order = SortOrder.DESC

        # Performance options
        self.timeout_seconds = 30
        self.parallel_search = True
        self.use_cache = True
        self.cache_ttl_minutes = 30

        # Advanced options
        self.include_hidden_files = False
        self.include_system_files = False
        self.follow_symlinks = False
        self.search_archives = False

        # Initialize validation
        self._validator = ValidationFramework()

        # Validate initial state
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate search parameters."""
        try:
            # Validate query for regex if enabled
            if self.use_regex and self.query:
                try:
                    re.compile(self.query)
                except re.error as e:
                    raise ValidationException(
                        f"Invalid regular expression: {str(e)}",
                        field_name="query",
                        field_value=self.query,
                    )

            # Validate fuzzy threshold
            if not 0.0 <= self.fuzzy_threshold <= 1.0:
                raise ValidationException(
                    "Fuzzy threshold must be between 0.0 and 1.0",
                    field_name="fuzzy_threshold",
                    field_value=self.fuzzy_threshold,
                )

            # Validate max results
            if self.max_results < 1:
                raise ValidationException(
                    "Maximum results must be at least 1",
                    field_name="max_results",
                    field_value=self.max_results,
                )

            # Validate offset
            if self.offset < 0:
                raise ValidationException(
                    "Offset cannot be negative",
                    field_name="offset",
                    field_value=self.offset,
                )

            # Validate timeout
            if self.timeout_seconds < 1:
                raise ValidationException(
                    "Timeout must be at least 1 second",
                    field_name="timeout_seconds",
                    field_value=self.timeout_seconds,
                )

            # Validate cache TTL
            if self.cache_ttl_minutes < 0:
                raise ValidationException(
                    "Cache TTL cannot be negative",
                    field_name="cache_ttl_minutes",
                    field_value=self.cache_ttl_minutes,
                )

        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Parameter validation failed: {str(e)}", cause=e
            )

    def set_query(self, query: str, use_regex: bool = False) -> None:
        """
        Set search query with validation.

        Args:
            query: Search query string
            use_regex: Whether to treat query as regular expression
        """
        self.query = query
        self.use_regex = use_regex
        self._validate_parameters()

    def add_file_type_extension(
        self, extension: str, include: bool = True
    ) -> None:
        """
        Add file extension to type filter.

        Args:
            extension: File extension (with or without dot)
            include: Whether to include (True) or exclude (False)
        """
        ext = extension.lower().lstrip(".")

        if include:
            self.file_type_filter.include_extensions.add(ext)
            self.file_type_filter.exclude_extensions.discard(ext)
        else:
            self.file_type_filter.exclude_extensions.add(ext)
            self.file_type_filter.include_extensions.discard(ext)

    def set_file_type_categories(self, **categories) -> None:
        """
        Set file type categories in filter.

        Args:
            **categories: Category flags (documents=True, images=False, etc.)
        """
        for category, value in categories.items():
            if hasattr(self.file_type_filter, f"include_{category}"):
                setattr(self.file_type_filter, f"include_{category}", value)

    def set_size_filter(
        self, min_size: Optional[str] = None, max_size: Optional[str] = None
    ) -> None:
        """
        Set size filter using human-readable strings.

        Args:
            min_size: Minimum size (e.g., "10MB")
            max_size: Maximum size (e.g., "1GB")
        """
        if min_size or max_size:
            self.size_filter = SizeFilter.from_human_readable(
                min_size, max_size
            )
        else:
            self.size_filter = None

    def add_date_filter(
        self,
        field: DateField = DateField.MODIFIED,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        relative_days: Optional[int] = None,
    ) -> None:
        """
        Add date filter to search parameters.

        Args:
            field: Date field to filter on
            from_date: Start date for range
            to_date: End date for range
            relative_days: Filter to last N days
        """
        date_filter = DateFilter(
            field=field,
            from_date=from_date,
            to_date=to_date,
            relative_days=relative_days,
        )

        # Replace existing filter for same field
        self.date_filters = [f for f in self.date_filters if f.field != field]
        self.date_filters.append(date_filter)

    def remove_date_filter(self, field: DateField) -> bool:
        """
        Remove date filter for specific field.

        Args:
            field: Date field to remove filter for

        Returns:
            True if filter was removed
        """
        original_count = len(self.date_filters)
        self.date_filters = [f for f in self.date_filters if f.field != field]
        return len(self.date_filters) < original_count

    def add_path_pattern(self, pattern: str, include: bool = True) -> None:
        """
        Add path pattern for filtering.

        Args:
            pattern: Path pattern (supports wildcards)
            include: Whether to include (True) or exclude (False)
        """
        if include:
            if pattern not in self.include_paths:
                self.include_paths.append(pattern)
        else:
            if pattern not in self.exclude_patterns:
                self.exclude_patterns.append(pattern)

    def remove_path_pattern(self, pattern: str, include: bool = True) -> bool:
        """
        Remove path pattern.

        Args:
            pattern: Path pattern to remove
            include: Whether from include (True) or exclude (False) list

        Returns:
            True if pattern was removed
        """
        try:
            if include:
                self.include_paths.remove(pattern)
            else:
                self.exclude_patterns.remove(pattern)
            return True
        except ValueError:
            return False

    def set_content_search_options(self, **options) -> None:
        """
        Update content search options.

        Args:
            **options: Content search option updates
        """
        for key, value in options.items():
            if hasattr(self.content_search_options, key):
                setattr(self.content_search_options, key, value)

    def set_sorting(
        self,
        field: SortField = SortField.RELEVANCE,
        order: SortOrder = SortOrder.DESC,
    ) -> None:
        """
        Set result sorting options.

        Args:
            field: Field to sort by
            order: Sort order (ascending/descending)
        """
        self.sort_field = field
        self.sort_order = order

    def set_pagination(
        self, offset: int = 0, max_results: int = 10000
    ) -> None:
        """
        Set result pagination options.

        Args:
            offset: Number of results to skip
            max_results: Maximum number of results to return
        """
        self.offset = offset
        self.max_results = max_results
        self._validate_parameters()

    def matches_file(self, file_info: Dict[str, Any]) -> bool:
        """
        Check if file matches all search criteria.

        Args:
            file_info: Dictionary with file information

        Returns:
            True if file matches all criteria
        """
        # Check file type filter
        if "extension" in file_info:
            if not self.file_type_filter.matches_extension(
                file_info["extension"]
            ):
                return False

        # Check size filter
        if self.size_filter and "size" in file_info:
            if not self.size_filter.matches_size(file_info["size"]):
                return False

        # Check date filters
        for date_filter in self.date_filters:
            date_field_map = {
                DateField.CREATED: "created_date",
                DateField.MODIFIED: "modified_date",
                DateField.ACCESSED: "accessed_date",
            }

            field_name = date_field_map.get(date_filter.field)
            if field_name in file_info:
                file_date = file_info[field_name]
                if isinstance(file_date, str):
                    file_date = datetime.fromisoformat(file_date)

                if not date_filter.matches_date(file_date):
                    return False

        # Check path patterns
        if "path" in file_info:
            file_path = str(file_info["path"])

            # If include paths specified, file must match at least one
            if self.include_paths:
                matches_include = any(
                    Path(file_path).match(pattern)
                    for pattern in self.include_paths
                )
                if not matches_include:
                    return False

            # File must not match any exclude patterns
            if self.exclude_patterns:
                matches_exclude = any(
                    Path(file_path).match(pattern)
                    for pattern in self.exclude_patterns
                )
                if matches_exclude:
                    return False

        return True

    def get_query_hash(self) -> str:
        """
        Generate hash of search parameters for caching.

        Returns:
            Hash string representing current parameters
        """
        import hashlib

        # Create deterministic representation
        param_dict = self.to_dict()
        param_str = str(sorted(param_dict.items()))

        return hashlib.md5(param_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search parameters to dictionary representation.

        Returns:
            Dictionary with complete search parameters
        """
        return {
            # Basic configuration
            "search_type": self.search_type.value,
            "query": self.query,
            "folder_id": self.folder_id,
            # Query options
            "use_regex": self.use_regex,
            "case_sensitive": self.case_sensitive,
            "whole_words_only": self.whole_words_only,
            "fuzzy_search": self.fuzzy_search,
            "fuzzy_threshold": self.fuzzy_threshold,
            # Filters
            "file_type_filter": self.file_type_filter.to_dict(),
            "size_filter": (
                self.size_filter.to_dict() if self.size_filter else None
            ),
            "date_filters": [f.to_dict() for f in self.date_filters],
            # Path filtering
            "include_paths": self.include_paths.copy(),
            "exclude_paths": self.exclude_paths.copy(),
            "exclude_patterns": self.exclude_patterns.copy(),
            # Content search
            "content_search_options": self.content_search_options.to_dict(),
            # Results
            "max_results": self.max_results,
            "offset": self.offset,
            "sort_field": self.sort_field.value,
            "sort_order": self.sort_order.value,
            # Performance
            "timeout_seconds": self.timeout_seconds,
            "parallel_search": self.parallel_search,
            "use_cache": self.use_cache,
            "cache_ttl_minutes": self.cache_ttl_minutes,
            # Advanced options
            "include_hidden_files": self.include_hidden_files,
            "include_system_files": self.include_system_files,
            "follow_symlinks": self.follow_symlinks,
            "search_archives": self.search_archives,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchParameters":
        """
        Create search parameters from dictionary representation.

        Args:
            data: Dictionary with search parameters

        Returns:
            SearchParameters instance
        """
        # Create base instance
        params = cls(
            search_type=SearchType(data.get("search_type", "file_name")),
            query=data.get("query", ""),
            folder_id=data.get("folder_id"),
        )

        # Restore query options
        params.use_regex = data.get("use_regex", False)
        params.case_sensitive = data.get("case_sensitive", False)
        params.whole_words_only = data.get("whole_words_only", False)
        params.fuzzy_search = data.get("fuzzy_search", False)
        params.fuzzy_threshold = data.get("fuzzy_threshold", 0.8)

        # Restore filters
        if "file_type_filter" in data and data["file_type_filter"]:
            params.file_type_filter = FileTypeFilter.from_dict(
                data["file_type_filter"]
            )

        if "size_filter" in data and data["size_filter"]:
            params.size_filter = SizeFilter.from_dict(data["size_filter"])

        if "date_filters" in data:
            params.date_filters = [
                DateFilter.from_dict(f) for f in data["date_filters"]
            ]

        # Restore path filtering
        params.include_paths = data.get("include_paths", [])
        params.exclude_paths = data.get("exclude_paths", [])
        params.exclude_patterns = data.get("exclude_patterns", [])

        # Restore content search options
        if "content_search_options" in data:
            params.content_search_options = ContentSearchOptions.from_dict(
                data["content_search_options"]
            )

        # Restore results configuration
        params.max_results = data.get("max_results", 10000)
        params.offset = data.get("offset", 0)
        params.sort_field = SortField(data.get("sort_field", "relevance"))
        params.sort_order = SortOrder(data.get("sort_order", "desc"))

        # Restore performance options
        params.timeout_seconds = data.get("timeout_seconds", 30)
        params.parallel_search = data.get("parallel_search", True)
        params.use_cache = data.get("use_cache", True)
        params.cache_ttl_minutes = data.get("cache_ttl_minutes", 30)

        # Restore advanced options
        params.include_hidden_files = data.get("include_hidden_files", False)
        params.include_system_files = data.get("include_system_files", False)
        params.follow_symlinks = data.get("follow_symlinks", False)
        params.search_archives = data.get("search_archives", False)

        return params

    def clone(self) -> "SearchParameters":
        """
        Create a copy of these search parameters.

        Returns:
            New SearchParameters instance with same configuration
        """
        return self.from_dict(self.to_dict())

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the search parameters.

        Returns:
            Dictionary with search parameter summary
        """
        return {
            "search_type": self.search_type.value,
            "query": (
                self.query[:50] + "..." if len(self.query) > 50 else self.query
            ),
            "folder_id": self.folder_id,
            "has_file_type_filter": bool(
                self.file_type_filter.include_extensions
                or self.file_type_filter.include_documents
                or self.file_type_filter.include_images
                or self.file_type_filter.include_videos
                or self.file_type_filter.include_audio
            ),
            "has_size_filter": self.size_filter is not None,
            "date_filters_count": len(self.date_filters),
            "path_patterns_count": len(self.include_paths)
            + len(self.exclude_patterns),
            "max_results": self.max_results,
            "sort_field": self.sort_field.value,
            "timeout_seconds": self.timeout_seconds,
        }

    def __str__(self) -> str:
        """String representation of search parameters."""
        return f"SearchParameters(type={self.search_type.value}, query='{self.query}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"SearchParameters("
            f"search_type={self.search_type.value}, "
            f"query='{self.query}', "
            f"folder_id={self.folder_id}, "
            f"max_results={self.max_results})"
        )
