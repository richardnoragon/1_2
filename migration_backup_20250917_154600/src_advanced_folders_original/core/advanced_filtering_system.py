"""
Advanced Filtering Options System for Advanced Folders - Week 7 Implementation.

Enterprise-grade filtering engine providing sophisticated filter combinations,
date ranges, size filters, custom filter chains, and filter persistence
with comprehensive validation and performance optimization.

Features:
- Multi-criteria filtering with logical operators (AND, OR, NOT)
- Date range filtering with flexible time specifications
- Size filtering with human-readable units and ranges
- Custom filter chains with save/load functionality
- Filter composition and transformation
- Performance-optimized filter execution
- Filter validation and conflict detection
- Cross-platform compatibility
- Comprehensive error handling and diagnostics
"""

import json
import logging
import operator
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ..exceptions.advanced_folders_exceptions import (ConfigurationException,
                                                      SearchException,
                                                      ValidationException)


class FilterType(Enum):
    """Types of filters available in the system."""
    FILENAME = "filename"
    FILEPATH = "filepath"
    FILESIZE = "filesize"
    MODIFIED_DATE = "modified_date"
    CREATED_DATE = "created_date"
    ACCESSED_DATE = "accessed_date"
    FILE_EXTENSION = "file_extension"
    CONTENT_TYPE = "content_type"
    PERMISSIONS = "permissions"
    OWNER = "owner"
    ATTRIBUTES = "attributes"
    CONTENT = "content"
    CUSTOM = "custom"


class LogicalOperator(Enum):
    """Logical operators for combining filters."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"


class ComparisonOperator(Enum):
    """Comparison operators for filter criteria."""
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX_MATCH = "regex_match"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"


class SizeUnit(Enum):
    """Units for file size measurements."""
    BYTES = ("B", 1)
    KILOBYTES = ("KB", 1024)
    MEGABYTES = ("MB", 1024**2)
    GIGABYTES = ("GB", 1024**3)
    TERABYTES = ("TB", 1024**4)
    PETABYTES = ("PB", 1024**5)
    
    def __init__(self, symbol: str, multiplier: int):
        self.symbol = symbol
        self.multiplier = multiplier


@dataclass
class FilterCriterion:
    """Individual filter criterion with validation."""
    
    filter_type: FilterType
    field_name: str
    operator: ComparisonOperator
    value: Any
    case_sensitive: bool = False
    negate: bool = False
    enabled: bool = True
    description: str = ""
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate filter criterion after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate the filter criterion."""
        if not self.field_name:
            raise ValidationException(
                "Field name cannot be empty",
                field_name="field_name",
                field_value=self.field_name,
                validation_rule="non_empty"
            )
        
        # Validate operator compatibility with filter type
        if self.filter_type == FilterType.FILESIZE:
            if self.operator not in [
                ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS,
                ComparisonOperator.LESS_THAN, ComparisonOperator.LESS_EQUAL,
                ComparisonOperator.GREATER_THAN,
                ComparisonOperator.GREATER_EQUAL,
                ComparisonOperator.BETWEEN, ComparisonOperator.NOT_BETWEEN
            ]:
                raise ValidationException(
                    f"Operator {self.operator.value} not compatible "
                    f"with size filter",
                    field_name="operator",
                    field_value=self.operator.value,
                    validation_rule="operator_compatibility"
                )
        
        # Validate date filters
        if self.filter_type in [
            FilterType.MODIFIED_DATE, FilterType.CREATED_DATE,
            FilterType.ACCESSED_DATE
        ]:
            if isinstance(self.value, str):
                try:
                    datetime.fromisoformat(self.value.replace('Z', '+00:00'))
                except ValueError:
                    raise ValidationException(
                        f"Invalid date format: {self.value}",
                        field_name="value",
                        field_value=self.value,
                        validation_rule="date_format"
                    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['filter_type'] = self.filter_type.value
        data['operator'] = self.operator.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterCriterion':
        """Create from dictionary."""
        data = data.copy()
        data['filter_type'] = FilterType(data['filter_type'])
        data['operator'] = ComparisonOperator(data['operator'])
        return cls(**data)


@dataclass
class FilterGroup:
    """Group of filter criteria with logical operations."""
    
    criteria: List[FilterCriterion] = field(default_factory=list)
    operator: LogicalOperator = LogicalOperator.AND
    name: str = ""
    description: str = ""
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    
    def add_criterion(self, criterion: FilterCriterion) -> None:
        """Add a filter criterion to the group."""
        criterion.validate()
        self.criteria.append(criterion)
    
    def remove_criterion(self, index: int) -> None:
        """Remove a criterion by index."""
        if 0 <= index < len(self.criteria):
            del self.criteria[index]
        else:
            raise IndexError(f"Criterion index {index} out of range")
    
    def get_enabled_criteria(self) -> List[FilterCriterion]:
        """Get only enabled criteria."""
        return [c for c in self.criteria if c.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'criteria': [c.to_dict() for c in self.criteria],
            'operator': self.operator.value,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterGroup':
        """Create from dictionary."""
        data = data.copy()
        data['criteria'] = [
            FilterCriterion.from_dict(c) for c in data['criteria']
        ]
        data['operator'] = LogicalOperator(data['operator'])
        return cls(**data)


@dataclass
class FilterChain:
    """Chain of filter groups with complex logical operations."""
    
    groups: List[FilterGroup] = field(default_factory=list)
    name: str = ""
    description: str = ""
    version: str = "1.0"
    author: str = ""
    tags: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    usage_count: int = 0
    
    def add_group(self, group: FilterGroup) -> None:
        """Add a filter group to the chain."""
        self.groups.append(group)
        self.last_modified = time.time()
    
    def remove_group(self, index: int) -> None:
        """Remove a group by index."""
        if 0 <= index < len(self.groups):
            del self.groups[index]
            self.last_modified = time.time()
        else:
            raise IndexError(f"Group index {index} out of range")
    
    def get_enabled_groups(self) -> List[FilterGroup]:
        """Get only enabled groups."""
        return [g for g in self.groups if g.enabled]
    
    def get_all_criteria(self) -> List[FilterCriterion]:
        """Get all criteria from all groups."""
        criteria = []
        for group in self.groups:
            criteria.extend(group.criteria)
        return criteria
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'groups': [g.to_dict() for g in self.groups],
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'tags': list(self.tags),
            'created_at': self.created_at,
            'last_modified': self.last_modified,
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterChain':
        """Create from dictionary."""
        data = data.copy()
        data['groups'] = [FilterGroup.from_dict(g) for g in data['groups']]
        data['tags'] = set(data.get('tags', []))
        return cls(**data)


class FilterEvaluator(ABC):
    """Abstract base class for filter evaluators."""
    
    @abstractmethod
    def evaluate(
        self,
        criterion: FilterCriterion,
        file_info: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a filter criterion against file information.
        
        Args:
            criterion: Filter criterion to evaluate
            file_info: Dictionary containing file information
            
        Returns:
            True if criterion matches, False otherwise
        """
        pass


class StandardFilterEvaluator(FilterEvaluator):
    """Standard implementation of filter evaluation logic."""
    
    def __init__(self):
        """Initialize standard filter evaluator."""
        self.logger = logging.getLogger('RFU.StandardFilterEvaluator')
        
        # Operator implementations
        self.operators = {
            ComparisonOperator.EQUALS: operator.eq,
            ComparisonOperator.NOT_EQUALS: operator.ne,
            ComparisonOperator.LESS_THAN: operator.lt,
            ComparisonOperator.LESS_EQUAL: operator.le,
            ComparisonOperator.GREATER_THAN: operator.gt,
            ComparisonOperator.GREATER_EQUAL: operator.ge,
            ComparisonOperator.CONTAINS: self._contains,
            ComparisonOperator.NOT_CONTAINS: self._not_contains,
            ComparisonOperator.STARTS_WITH: self._starts_with,
            ComparisonOperator.ENDS_WITH: self._ends_with,
            ComparisonOperator.REGEX_MATCH: self._regex_match,
            ComparisonOperator.IN: self._in,
            ComparisonOperator.NOT_IN: self._not_in,
            ComparisonOperator.BETWEEN: self._between,
            ComparisonOperator.NOT_BETWEEN: self._not_between,
        }
    
    def evaluate(
        self, 
        criterion: FilterCriterion, 
        file_info: Dict[str, Any]
    ) -> bool:
        """Evaluate filter criterion against file information."""
        if not criterion.enabled:
            return True
        
        # Get field value from file info
        field_value = self._get_field_value(criterion, file_info)
        if field_value is None:
            return False
        
        # Apply case sensitivity for string operations
        if isinstance(field_value, str) and not criterion.case_sensitive:
            field_value = field_value.lower()
            if isinstance(criterion.value, str):
                criterion.value = criterion.value.lower()
        
        # Evaluate using appropriate operator
        try:
            result = self.operators[criterion.operator](
                field_value, criterion.value
            )
            
            # Apply negation if specified
            if criterion.negate:
                result = not result
            
            return result
            
        except Exception as e:
            self.logger.warning(
                f"Filter evaluation error for {criterion.field_name}: {str(e)}"
            )
            return False
    
    def _get_field_value(
        self,
        criterion: FilterCriterion,
        file_info: Dict[str, Any]
    ) -> Any:
        """Extract field value from file info based on filter type."""
        field_name = criterion.field_name
        
        if criterion.filter_type == FilterType.FILENAME:
            return file_info.get('name', '')
        
        elif criterion.filter_type == FilterType.FILEPATH:
            return file_info.get('path', '')
        
        elif criterion.filter_type == FilterType.FILESIZE:
            return file_info.get('size', 0)
        
        elif criterion.filter_type == FilterType.MODIFIED_DATE:
            return file_info.get('modified_time', 0)
        
        elif criterion.filter_type == FilterType.CREATED_DATE:
            return file_info.get('created_time', 0)
        
        elif criterion.filter_type == FilterType.ACCESSED_DATE:
            return file_info.get('accessed_time', 0)
        
        elif criterion.filter_type == FilterType.FILE_EXTENSION:
            path = file_info.get('path', '')
            return Path(path).suffix.lstrip('.')
        
        elif criterion.filter_type == FilterType.CONTENT_TYPE:
            return file_info.get('content_type', '')
        
        elif criterion.filter_type == FilterType.PERMISSIONS:
            return file_info.get('permissions', '')
        
        elif criterion.filter_type == FilterType.OWNER:
            return file_info.get('owner', '')
        
        elif criterion.filter_type == FilterType.ATTRIBUTES:
            return file_info.get('attributes', {})
        
        elif criterion.filter_type == FilterType.CONTENT:
            return file_info.get('content', '')
        
        else:
            # Custom field
            return file_info.get(field_name)
    
    def _contains(self, field_value: str, criterion_value: str) -> bool:
        """Check if field contains criterion value."""
        return criterion_value in field_value
    
    def _not_contains(self, field_value: str, criterion_value: str) -> bool:
        """Check if field does not contain criterion value."""
        return criterion_value not in field_value
    
    def _starts_with(self, field_value: str, criterion_value: str) -> bool:
        """Check if field starts with criterion value."""
        return field_value.startswith(criterion_value)
    
    def _ends_with(self, field_value: str, criterion_value: str) -> bool:
        """Check if field ends with criterion value."""
        return field_value.endswith(criterion_value)
    
    def _regex_match(self, field_value: str, pattern: str) -> bool:
        """Check if field matches regex pattern."""
        import re
        try:
            return bool(re.search(pattern, field_value))
        except re.error:
            return False
    
    def _in(self, field_value: Any, criterion_value: List[Any]) -> bool:
        """Check if field value is in criterion list."""
        return field_value in criterion_value
    
    def _not_in(self, field_value: Any, criterion_value: List[Any]) -> bool:
        """Check if field value is not in criterion list."""
        return field_value not in criterion_value
    
    def _between(
        self, 
        field_value: Union[int, float], 
        range_value: Tuple[Union[int, float], Union[int, float]]
    ) -> bool:
        """Check if field value is between range values."""
        min_val, max_val = range_value
        return min_val <= field_value <= max_val
    
    def _not_between(
        self, 
        field_value: Union[int, float], 
        range_value: Tuple[Union[int, float], Union[int, float]]
    ) -> bool:
        """Check if field value is not between range values."""
        return not self._between(field_value, range_value)


class SizeParser:
    """Utility for parsing human-readable file sizes."""
    
    def __init__(self):
        """Initialize size parser."""
        self.units = {unit.symbol: unit for unit in SizeUnit}
        
        # Alternative unit representations
        self.unit_aliases = {
            'BYTE': SizeUnit.BYTES,
            'BYTES': SizeUnit.BYTES,
            'K': SizeUnit.KILOBYTES,
            'KB': SizeUnit.KILOBYTES,
            'KILOBYTE': SizeUnit.KILOBYTES,
            'KILOBYTES': SizeUnit.KILOBYTES,
            'M': SizeUnit.MEGABYTES,
            'MB': SizeUnit.MEGABYTES,
            'MEGABYTE': SizeUnit.MEGABYTES,
            'MEGABYTES': SizeUnit.MEGABYTES,
            'G': SizeUnit.GIGABYTES,
            'GB': SizeUnit.GIGABYTES,
            'GIGABYTE': SizeUnit.GIGABYTES,
            'GIGABYTES': SizeUnit.GIGABYTES,
            'T': SizeUnit.TERABYTES,
            'TB': SizeUnit.TERABYTES,
            'TERABYTE': SizeUnit.TERABYTES,
            'TERABYTES': SizeUnit.TERABYTES,
        }
    
    def parse_size(self, size_str: str) -> int:
        """
        Parse human-readable size string to bytes.
        
        Args:
            size_str: Size string like "10MB", "1.5GB", "512KB"
            
        Returns:
            Size in bytes
            
        Raises:
            ValidationException: If size format is invalid
        """
        size_str = size_str.strip().upper()
        
        # Handle numeric-only values (assume bytes)
        if size_str.isdigit():
            return int(size_str)
        
        # Extract numeric part and unit part
        import re
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([A-Z]+)$', size_str)
        if not match:
            raise ValidationException(
                f"Invalid size format: {size_str}",
                field_name="size",
                field_value=size_str,
                validation_rule="size_format"
            )
        
        value_str, unit_str = match.groups()
        
        try:
            value = float(value_str)
        except ValueError:
            raise ValidationException(
                f"Invalid numeric value: {value_str}",
                field_name="size_value",
                field_value=value_str,
                validation_rule="numeric"
            )
        
        # Find unit
        unit = self.unit_aliases.get(unit_str)
        if not unit:
            raise ValidationException(
                f"Unknown size unit: {unit_str}",
                field_name="size_unit",
                field_value=unit_str,
                validation_rule="valid_unit"
            )
        
        return int(value * unit.multiplier)
    
    def format_size(self, size_bytes: int) -> str:
        """
        Format bytes to human-readable string.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human-readable size string
        """
        if size_bytes == 0:
            return "0 B"
        
        # Find appropriate unit
        for unit in reversed(list(SizeUnit)):
            if size_bytes >= unit.multiplier:
                value = size_bytes / unit.multiplier
                if value == int(value):
                    return f"{int(value)} {unit.symbol}"
                else:
                    return f"{value:.1f} {unit.symbol}"
        
        return f"{size_bytes} B"


class DateParser:
    """Utility for parsing date expressions and ranges."""
    
    def __init__(self):
        """Initialize date parser."""
        self.relative_patterns = {
            'today': lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            'yesterday': lambda: (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            'this_week': lambda: datetime.now() - timedelta(days=datetime.now().weekday()),
            'last_week': lambda: datetime.now() - timedelta(days=datetime.now().weekday() + 7),
            'this_month': lambda: datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            'last_month': lambda: (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1),
            'this_year': lambda: datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            'last_year': lambda: datetime.now().replace(year=datetime.now().year-1, month=1, day=1),
        }
    
    def parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string (ISO format, relative expressions, etc.)
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValidationException: If date format is invalid
        """
        date_str = date_str.strip().lower()
        
        # Handle relative expressions
        if date_str in self.relative_patterns:
            return self.relative_patterns[date_str]()
        
        # Handle relative offsets (e.g., "7 days ago", "2 weeks ago")
        import re
        offset_match = re.match(r'^(\d+)\s+(days?|weeks?|months?|years?)\s+ago$', date_str)
        if offset_match:
            value, unit = offset_match.groups()
            value = int(value)
            
            if unit.startswith('day'):
                return datetime.now() - timedelta(days=value)
            elif unit.startswith('week'):
                return datetime.now() - timedelta(weeks=value)
            elif unit.startswith('month'):
                return datetime.now() - timedelta(days=value * 30)  # Approximate
            elif unit.startswith('year'):
                return datetime.now() - timedelta(days=value * 365)  # Approximate
        
        # Handle ISO format
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Handle common formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValidationException(
            f"Invalid date format: {date_str}",
            field_name="date",
            field_value=date_str,
            validation_rule="date_format"
        )
    
    def parse_date_range(
        self, 
        range_str: str
    ) -> Tuple[datetime, datetime]:
        """
        Parse date range string.
        
        Args:
            range_str: Range string like "2023-01-01 to 2023-12-31"
            
        Returns:
            Tuple of (start_date, end_date)
        """
        # Handle range separators
        separators = [' to ', ' - ', '..', ',']
        
        for sep in separators:
            if sep in range_str:
                parts = range_str.split(sep, 1)
                if len(parts) == 2:
                    start_date = self.parse_date(parts[0].strip())
                    end_date = self.parse_date(parts[1].strip())
                    
                    if start_date > end_date:
                        start_date, end_date = end_date, start_date
                    
                    return start_date, end_date
        
        raise ValidationException(
            f"Invalid date range format: {range_str}",
            field_name="date_range",
            field_value=range_str,
            validation_rule="range_format"
        )


class AdvancedFilterEngine:
    """
    Enterprise advanced filtering engine with comprehensive capabilities.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize advanced filter engine.
        
        Args:
            config_dir: Directory for storing filter configurations
        """
        self.config_dir = Path(config_dir or "config/filters")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.evaluator = StandardFilterEvaluator()
        self.size_parser = SizeParser()
        self.date_parser = DateParser()
        
        # Filter storage
        self.filter_chains: Dict[str, FilterChain] = {}
        self.predefined_filters: Dict[str, FilterChain] = {}
        
        # Performance tracking
        self.evaluation_stats = {
            'total_evaluations': 0,
            'total_time_ms': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        self.logger = logging.getLogger('RFU.AdvancedFilterEngine')
        
        # Initialize predefined filters
        self._init_predefined_filters()
        
        # Load saved filter chains
        self._load_filter_chains()
        
        self.logger.info("Advanced filter engine initialized")
    
    def _init_predefined_filters(self) -> None:
        """Initialize predefined filter templates."""
        # Common file type filters
        image_filter = FilterChain(
            name="Image Files",
            description="Filter for common image file formats",
            tags={"image", "media", "graphics"}
        )
        image_group = FilterGroup(name="Image Extensions")
        image_group.add_criterion(FilterCriterion(
            filter_type=FilterType.FILE_EXTENSION,
            field_name="extension",
            operator=ComparisonOperator.IN,
            value=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "svg"],
            description="Common image file extensions"
        ))
        image_filter.add_group(image_group)
        self.predefined_filters["image_files"] = image_filter
        
        # Large files filter
        large_files = FilterChain(
            name="Large Files",
            description="Files larger than 100MB",
            tags={"size", "large", "cleanup"}
        )
        large_group = FilterGroup(name="Size Criteria")
        large_group.add_criterion(FilterCriterion(
            filter_type=FilterType.FILESIZE,
            field_name="size",
            operator=ComparisonOperator.GREATER_THAN,
            value=100 * 1024 * 1024,  # 100MB in bytes
            description="Files larger than 100MB"
        ))
        large_files.add_group(large_group)
        self.predefined_filters["large_files"] = large_files
        
        # Recent files filter
        recent_files = FilterChain(
            name="Recent Files",
            description="Files modified in the last 7 days",
            tags={"date", "recent", "activity"}
        )
        recent_group = FilterGroup(name="Date Criteria")
        week_ago = datetime.now() - timedelta(days=7)
        recent_group.add_criterion(FilterCriterion(
            filter_type=FilterType.MODIFIED_DATE,
            field_name="modified_time",
            operator=ComparisonOperator.GREATER_THAN,
            value=week_ago.timestamp(),
            description="Modified in the last 7 days"
        ))
        recent_files.add_group(recent_group)
        self.predefined_filters["recent_files"] = recent_files
        
        # Empty files filter
        empty_files = FilterChain(
            name="Empty Files",
            description="Files with zero bytes",
            tags={"size", "empty", "cleanup"}
        )
        empty_group = FilterGroup(name="Size Criteria")
        empty_group.add_criterion(FilterCriterion(
            filter_type=FilterType.FILESIZE,
            field_name="size",
            operator=ComparisonOperator.EQUALS,
            value=0,
            description="Files with zero size"
        ))
        empty_files.add_group(empty_group)
        self.predefined_filters["empty_files"] = empty_files
    
    def create_filter_chain(self, name: str, description: str = "") -> FilterChain:
        """
        Create a new filter chain.
        
        Args:
            name: Name for the filter chain
            description: Description of the filter chain
            
        Returns:
            New FilterChain object
        """
        if name in self.filter_chains:
            raise ConfigurationException(
                f"Filter chain '{name}' already exists",
                setting_name="filter_chain_name",
                setting_value=name
            )
        
        filter_chain = FilterChain(name=name, description=description)
        
        with self._lock:
            self.filter_chains[name] = filter_chain
        
        self.logger.info(f"Created filter chain: {name}")
        return filter_chain
    
    def save_filter_chain(self, chain: FilterChain) -> None:
        """
        Save a filter chain to disk.
        
        Args:
            chain: FilterChain to save
        """
        if not chain.name:
            raise ValidationException(
                "Filter chain must have a name to be saved",
                field_name="name",
                field_value=chain.name,
                validation_rule="non_empty"
            )
        
        file_path = self.config_dir / f"{chain.name}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chain.to_dict(), f, indent=2, default=str)
            
            with self._lock:
                self.filter_chains[chain.name] = chain
            
            self.logger.info(f"Saved filter chain: {chain.name}")
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to save filter chain: {str(e)}",
                setting_name="filter_chain_save",
                setting_value=chain.name
            )
    
    def load_filter_chain(self, name: str) -> Optional[FilterChain]:
        """
        Load a filter chain from disk.
        
        Args:
            name: Name of the filter chain to load
            
        Returns:
            Loaded FilterChain or None if not found
        """
        file_path = self.config_dir / f"{name}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chain = FilterChain.from_dict(data)
            
            with self._lock:
                self.filter_chains[name] = chain
            
            return chain
            
        except Exception as e:
            self.logger.error(f"Failed to load filter chain {name}: {str(e)}")
            return None
    
    def _load_filter_chains(self) -> None:
        """Load all saved filter chains from disk."""
        if not self.config_dir.exists():
            return
        
        for file_path in self.config_dir.glob("*.json"):
            if file_path.is_file():
                name = file_path.stem
                try:
                    self.load_filter_chain(name)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to load filter chain {name}: {str(e)}"
                    )
    
    def delete_filter_chain(self, name: str) -> bool:
        """
        Delete a filter chain.
        
        Args:
            name: Name of the filter chain to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.config_dir / f"{name}.json"
        
        with self._lock:
            if name in self.filter_chains:
                del self.filter_chains[name]
        
        if file_path.exists():
            try:
                file_path.unlink()
                self.logger.info(f"Deleted filter chain: {name}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete filter chain file: {str(e)}")
        
        return False
    
    def apply_filter_chain(
        self,
        chain: FilterChain,
        file_infos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Apply a filter chain to a list of file information.
        
        Args:
            chain: FilterChain to apply
            file_infos: List of file information dictionaries
            
        Returns:
            Filtered list of file information
        """
        start_time = time.time()
        
        try:
            chain.usage_count += 1
            enabled_groups = chain.get_enabled_groups()
            
            if not enabled_groups:
                return file_infos
            
            filtered_files = []
            
            for file_info in file_infos:
                if self._evaluate_groups(enabled_groups, file_info):
                    filtered_files.append(file_info)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            with self._lock:
                self.evaluation_stats['total_evaluations'] += len(file_infos)
                self.evaluation_stats['total_time_ms'] += execution_time_ms
            
            self.logger.debug(
                f"Filter chain '{chain.name}' processed {len(file_infos)} files, "
                f"returned {len(filtered_files)} results in {execution_time_ms:.2f}ms"
            )
            
            return filtered_files
            
        except Exception as e:
            self.logger.error(
                f"Error applying filter chain '{chain.name}': {str(e)}"
            )
            raise SearchException(
                f"Filter execution failed: {str(e)}",
                search_type="filter_chain",
                search_parameters={"chain_name": chain.name}
            )
    
    def _evaluate_groups(
        self,
        groups: List[FilterGroup],
        file_info: Dict[str, Any]
    ) -> bool:
        """Evaluate multiple filter groups against file information."""
        if not groups:
            return True
        
        # For now, use AND logic between groups
        # TODO: Implement configurable group-level operators
        for group in groups:
            if not self._evaluate_group(group, file_info):
                return False
        
        return True
    
    def _evaluate_group(
        self,
        group: FilterGroup,
        file_info: Dict[str, Any]
    ) -> bool:
        """Evaluate a filter group against file information."""
        criteria = group.get_enabled_criteria()
        
        if not criteria:
            return True
        
        if group.operator == LogicalOperator.AND:
            return all(
                self.evaluator.evaluate(criterion, file_info)
                for criterion in criteria
            )
        
        elif group.operator == LogicalOperator.OR:
            return any(
                self.evaluator.evaluate(criterion, file_info)
                for criterion in criteria
            )
        
        elif group.operator == LogicalOperator.NOT:
            # NOT operator applies to all criteria
            return not any(
                self.evaluator.evaluate(criterion, file_info)
                for criterion in criteria
            )
        
        elif group.operator == LogicalOperator.XOR:
            # XOR: exactly one criterion should match
            matches = sum(
                1 for criterion in criteria
                if self.evaluator.evaluate(criterion, file_info)
            )
            return matches == 1
        
        return False
    
    def get_filter_chains(self) -> Dict[str, FilterChain]:
        """Get all available filter chains."""
        with self._lock:
            return self.filter_chains.copy()
    
    def get_predefined_filters(self) -> Dict[str, FilterChain]:
        """Get predefined filter templates."""
        return self.predefined_filters.copy()
    
    def create_size_filter(
        self,
        operator: ComparisonOperator,
        size_spec: str,
        description: str = ""
    ) -> FilterCriterion:
        """
        Create a size filter criterion.
        
        Args:
            operator: Comparison operator
            size_spec: Size specification (e.g., "10MB", "1.5GB")
            description: Optional description
            
        Returns:
            FilterCriterion for size filtering
        """
        size_bytes = self.size_parser.parse_size(size_spec)
        
        return FilterCriterion(
            filter_type=FilterType.FILESIZE,
            field_name="size",
            operator=operator,
            value=size_bytes,
            description=description or f"File size {operator.value} {size_spec}"
        )
    
    def create_date_filter(
        self,
        date_type: FilterType,
        operator: ComparisonOperator,
        date_spec: str,
        description: str = ""
    ) -> FilterCriterion:
        """
        Create a date filter criterion.
        
        Args:
            date_type: Type of date filter (MODIFIED_DATE, CREATED_DATE, etc.)
            operator: Comparison operator
            date_spec: Date specification (e.g., "2023-01-01", "7 days ago")
            description: Optional description
            
        Returns:
            FilterCriterion for date filtering
        """
        if date_type not in [FilterType.MODIFIED_DATE, FilterType.CREATED_DATE, 
                           FilterType.ACCESSED_DATE]:
            raise ValidationException(
                f"Invalid date filter type: {date_type}",
                field_name="date_type",
                field_value=date_type.value,
                validation_rule="valid_date_type"
            )
        
        if operator == ComparisonOperator.BETWEEN:
            start_date, end_date = self.date_parser.parse_date_range(date_spec)
            value = (start_date.timestamp(), end_date.timestamp())
        else:
            date_obj = self.date_parser.parse_date(date_spec)
            value = date_obj.timestamp()
        
        field_map = {
            FilterType.MODIFIED_DATE: "modified_time",
            FilterType.CREATED_DATE: "created_time",
            FilterType.ACCESSED_DATE: "accessed_time"
        }
        
        return FilterCriterion(
            filter_type=date_type,
            field_name=field_map[date_type],
            operator=operator,
            value=value,
            description=description or f"{date_type.value} {operator.value} {date_spec}"
        )
    
    def validate_filter_chain(self, chain: FilterChain) -> Dict[str, Any]:
        """
        Validate a filter chain for conflicts and issues.
        
        Args:
            chain: FilterChain to validate
            
        Returns:
            Validation report
        """
        report = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check for empty chain
        if not chain.groups:
            report['warnings'].append("Filter chain has no groups")
            return report
        
        # Check each group
        for i, group in enumerate(chain.groups):
            if not group.criteria:
                report['warnings'].append(f"Group {i} has no criteria")
                continue
            
            # Check for conflicting criteria within group
            if group.operator == LogicalOperator.AND:
                for j, criterion in enumerate(group.criteria):
                    for k, other_criterion in enumerate(group.criteria[j+1:], j+1):
                        if self._check_criterion_conflict(criterion, other_criterion):
                            report['issues'].append(
                                f"Conflicting criteria in group {i}: "
                                f"criterion {j} and {k}"
                            )
                            report['valid'] = False
        
        # Performance warnings
        total_criteria = len(chain.get_all_criteria())
        if total_criteria > 20:
            report['warnings'].append(
                f"Large number of criteria ({total_criteria}) may impact performance"
            )
        
        # Suggestions for optimization
        regex_count = sum(
            1 for criterion in chain.get_all_criteria()
            if criterion.operator == ComparisonOperator.REGEX_MATCH
        )
        if regex_count > 5:
            report['suggestions'].append(
                "Consider combining multiple regex patterns into fewer, "
                "more efficient patterns"
            )
        
        return report
    
    def _check_criterion_conflict(
        self,
        criterion1: FilterCriterion,
        criterion2: FilterCriterion
    ) -> bool:
        """Check if two criteria conflict with each other."""
        # Same field with conflicting operators
        if (criterion1.field_name == criterion2.field_name and
            criterion1.filter_type == criterion2.filter_type):
            
            # Check for impossible combinations
            if (criterion1.operator == ComparisonOperator.EQUALS and
                criterion2.operator == ComparisonOperator.NOT_EQUALS and
                criterion1.value == criterion2.value):
                return True
            
            # Size conflicts
            if criterion1.filter_type == FilterType.FILESIZE:
                if (criterion1.operator == ComparisonOperator.GREATER_THAN and
                    criterion2.operator == ComparisonOperator.LESS_THAN and
                    criterion1.value >= criterion2.value):
                    return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get filter engine statistics."""
        with self._lock:
            stats = self.evaluation_stats.copy()
        
        # Calculate derived statistics
        if stats['total_evaluations'] > 0:
            stats['avg_evaluation_time_ms'] = (
                stats['total_time_ms'] / stats['total_evaluations']
            )
        else:
            stats['avg_evaluation_time_ms'] = 0.0
        
        # Filter chain statistics
        stats['total_filter_chains'] = len(self.filter_chains)
        stats['predefined_filters'] = len(self.predefined_filters)
        
        # Usage statistics
        chain_usage = {
            name: chain.usage_count
            for name, chain in self.filter_chains.items()
        }
        stats['chain_usage'] = dict(
            sorted(chain_usage.items(), key=lambda x: x[1], reverse=True)
        )
        
        return stats