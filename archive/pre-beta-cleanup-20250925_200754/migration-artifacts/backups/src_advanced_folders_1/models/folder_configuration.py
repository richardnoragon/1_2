"""
FolderConfiguration model for Advanced Folders feature.

This module defines the core FolderConfiguration model that represents
a configured advanced folder with its search parameters, metadata,
and persistence capabilities.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..exceptions import ConfigurationException, ValidationException
from ..validation.validator_framework import ValidationFramework


class FolderType(Enum):
    """Enumeration of supported folder types."""
    SMART_FOLDER = "smart_folder"
    SEARCH_FOLDER = "search_folder"
    VIRTUAL_FOLDER = "virtual_folder"
    DYNAMIC_FOLDER = "dynamic_folder"


class MonitoringMode(Enum):
    """File system monitoring modes."""
    NONE = "none"
    BASIC = "basic"
    FULL = "full"
    REAL_TIME = "real_time"


class IndexingStrategy(Enum):
    """Indexing strategies for folder contents."""
    NONE = "none"
    METADATA_ONLY = "metadata_only"
    CONTENT_BASIC = "content_basic"
    CONTENT_FULL = "content_full"


@dataclass
class DirectoryTarget:
    """Represents a target directory for folder configuration."""
    
    path: str
    include_subdirectories: bool = True
    follow_symlinks: bool = False
    max_depth: Optional[int] = None
    exclude_patterns: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate directory target after initialization."""
        if not self.path:
            raise ValidationException(
                "Directory path cannot be empty",
                field_name="path",
                field_value=self.path
            )
        
        # Normalize path
        self.path = str(Path(self.path).resolve())
        
        # Validate max_depth
        if self.max_depth is not None and self.max_depth < 1:
            raise ValidationException(
                "Maximum depth must be at least 1",
                field_name="max_depth",
                field_value=self.max_depth
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DirectoryTarget':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class PerformanceSettings:
    """Performance-related settings for folder configuration."""
    
    max_results: int = 10000
    cache_ttl_minutes: int = 30
    search_timeout_seconds: int = 60
    memory_limit_mb: int = 500
    parallel_workers: int = 4
    batch_size: int = 1000
    
    def __post_init__(self):
        """Validate performance settings."""
        if self.max_results < 1:
            raise ValidationException(
                "Maximum results must be at least 1",
                field_name="max_results",
                field_value=self.max_results
            )
        
        if self.cache_ttl_minutes < 0:
            raise ValidationException(
                "Cache TTL cannot be negative",
                field_name="cache_ttl_minutes",
                field_value=self.cache_ttl_minutes
            )
        
        if self.search_timeout_seconds < 1:
            raise ValidationException(
                "Search timeout must be at least 1 second",
                field_name="search_timeout_seconds",
                field_value=self.search_timeout_seconds
            )
        
        if self.memory_limit_mb < 50:
            raise ValidationException(
                "Memory limit must be at least 50 MB",
                field_name="memory_limit_mb",
                field_value=self.memory_limit_mb
            )
        
        if self.parallel_workers < 1:
            raise ValidationException(
                "Parallel workers must be at least 1",
                field_name="parallel_workers",
                field_value=self.parallel_workers
            )
        
        if self.batch_size < 1:
            raise ValidationException(
                "Batch size must be at least 1",
                field_name="batch_size",
                field_value=self.batch_size
            )


@dataclass
class SecuritySettings:
    """Security-related settings for folder configuration."""
    
    respect_file_permissions: bool = True
    include_hidden_files: bool = False
    include_system_files: bool = False
    encrypted_paths_only: bool = False
    require_authentication: bool = False
    access_control_list: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecuritySettings':
        """Create instance from dictionary."""
        return cls(**data)


class FolderConfiguration:
    """
    Advanced folder configuration with comprehensive validation and metadata.
    
    This class represents a complete folder configuration including search
    parameters, target directories, performance settings, and metadata.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        folder_type: FolderType = FolderType.SMART_FOLDER,
        folder_id: Optional[str] = None
    ):
        """
        Initialize folder configuration.
        
        Args:
            name: Human-readable folder name
            description: Optional folder description
            folder_type: Type of advanced folder
            folder_id: Unique identifier (auto-generated if not provided)
        """
        # Core identification
        self.folder_id = folder_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.folder_type = folder_type
        
        # Timestamps
        self.created_at = datetime.now(timezone.utc)
        self.modified_at = self.created_at
        self.last_accessed_at = self.created_at
        
        # Configuration components
        self.target_directories: List[DirectoryTarget] = []
        self.performance_settings = PerformanceSettings()
        self.security_settings = SecuritySettings()
        
        # Search and monitoring settings
        self.monitoring_mode = MonitoringMode.BASIC
        self.indexing_strategy = IndexingStrategy.METADATA_ONLY
        self.auto_refresh_enabled = True
        self.auto_refresh_interval_minutes = 15
        
        # Metadata and statistics
        self.metadata: Dict[str, Any] = {}
        self.tags: Set[str] = set()
        self.last_scan_count = 0
        self.last_scan_time: Optional[datetime] = None
        self.total_size_bytes = 0
        
        # State management
        self.is_active = True
        self.is_persistent = True
        self.version = 1
        
        # Initialize validation framework
        self._validator = ValidationFramework()
        
        # Validate initial state
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate the complete configuration."""
        try:
            # Validate name
            if not self.name or not self.name.strip():
                raise ValidationException(
                    "Folder name cannot be empty",
                    field_name="name",
                    field_value=self.name
                )
            
            if len(self.name) > 255:
                raise ValidationException(
                    "Folder name cannot exceed 255 characters",
                    field_name="name",
                    field_value=self.name
                )
            
            # Validate folder_id format
            try:
                uuid.UUID(self.folder_id)
            except ValueError:
                raise ValidationException(
                    "Invalid folder ID format",
                    field_name="folder_id",
                    field_value=self.folder_id
                )
            
            # Validate auto refresh interval
            if self.auto_refresh_interval_minutes < 1:
                raise ValidationException(
                    "Auto refresh interval must be at least 1 minute",
                    field_name="auto_refresh_interval_minutes",
                    field_value=self.auto_refresh_interval_minutes
                )
            
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Configuration validation failed: {str(e)}",
                cause=e
            )
    
    def add_target_directory(
        self,
        path: Union[str, Path],
        include_subdirectories: bool = True,
        follow_symlinks: bool = False,
        max_depth: Optional[int] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> DirectoryTarget:
        """
        Add a target directory to the configuration.
        
        Args:
            path: Directory path
            include_subdirectories: Whether to include subdirectories
            follow_symlinks: Whether to follow symbolic links
            max_depth: Maximum recursion depth
            exclude_patterns: Patterns to exclude
            
        Returns:
            Created DirectoryTarget instance
            
        Raises:
            ValidationException: If directory configuration is invalid
        """
        target = DirectoryTarget(
            path=str(path),
            include_subdirectories=include_subdirectories,
            follow_symlinks=follow_symlinks,
            max_depth=max_depth,
            exclude_patterns=exclude_patterns or []
        )
        
        # Check for duplicates
        existing_paths = {t.path for t in self.target_directories}
        if target.path in existing_paths:
            raise ValidationException(
                f"Directory '{target.path}' already exists in configuration",
                field_name="path",
                field_value=target.path
            )
        
        self.target_directories.append(target)
        self._update_modified_time()
        
        return target
    
    def remove_target_directory(self, path: Union[str, Path]) -> bool:
        """
        Remove a target directory from the configuration.
        
        Args:
            path: Directory path to remove
            
        Returns:
            True if directory was removed, False if not found
        """
        path_str = str(Path(path).resolve())
        original_count = len(self.target_directories)
        
        self.target_directories = [
            target for target in self.target_directories
            if target.path != path_str
        ]
        
        removed = len(self.target_directories) < original_count
        if removed:
            self._update_modified_time()
        
        return removed
    
    def update_performance_settings(self, **kwargs) -> None:
        """Update performance settings with validation."""
        # Create new settings with updates
        current_settings = asdict(self.performance_settings)
        current_settings.update(kwargs)
        
        # Validate new settings
        new_settings = PerformanceSettings(**current_settings)
        
        # Apply if validation passes
        self.performance_settings = new_settings
        self._update_modified_time()
    
    def update_security_settings(self, **kwargs) -> None:
        """Update security settings with validation."""
        current_settings = asdict(self.security_settings)
        current_settings.update(kwargs)
        
        self.security_settings = SecuritySettings(**current_settings)
        self._update_modified_time()
    
    def add_tag(self, tag: str) -> bool:
        """
        Add a tag to the folder configuration.
        
        Args:
            tag: Tag to add
            
        Returns:
            True if tag was added, False if already exists
        """
        if not tag or not tag.strip():
            raise ValidationException(
                "Tag cannot be empty",
                field_name="tag",
                field_value=tag
            )
        
        tag = tag.strip().lower()
        if tag not in self.tags:
            self.tags.add(tag)
            self._update_modified_time()
            return True
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the folder configuration.
        
        Args:
            tag: Tag to remove
            
        Returns:
            True if tag was removed, False if not found
        """
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_modified_time()
            return True
        return False
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update metadata with a key-value pair.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if not key or not key.strip():
            raise ValidationException(
                "Metadata key cannot be empty",
                field_name="key",
                field_value=key
            )
        
        self.metadata[key.strip()] = value
        self._update_modified_time()
    
    def remove_metadata(self, key: str) -> bool:
        """
        Remove metadata by key.
        
        Args:
            key: Metadata key to remove
            
        Returns:
            True if key was removed, False if not found
        """
        if key in self.metadata:
            del self.metadata[key]
            self._update_modified_time()
            return True
        return False
    
    def update_scan_statistics(self, file_count: int, total_size: int) -> None:
        """
        Update scan statistics.
        
        Args:
            file_count: Number of files found in last scan
            total_size: Total size in bytes
        """
        self.last_scan_count = file_count
        self.last_scan_time = datetime.now(timezone.utc)
        self.total_size_bytes = total_size
        self.last_accessed_at = datetime.now(timezone.utc)
    
    def _update_modified_time(self) -> None:
        """Update the modified timestamp."""
        self.modified_at = datetime.now(timezone.utc)
        self.version += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary representation.
        
        Returns:
            Dictionary with complete configuration data
        """
        return {
            # Core identification
            "folder_id": self.folder_id,
            "name": self.name,
            "description": self.description,
            "folder_type": self.folder_type.value,
            
            # Timestamps
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            
            # Configuration components
            "target_directories": [target.to_dict() for target in self.target_directories],
            "performance_settings": asdict(self.performance_settings),
            "security_settings": self.security_settings.to_dict(),
            
            # Search and monitoring
            "monitoring_mode": self.monitoring_mode.value,
            "indexing_strategy": self.indexing_strategy.value,
            "auto_refresh_enabled": self.auto_refresh_enabled,
            "auto_refresh_interval_minutes": self.auto_refresh_interval_minutes,
            
            # Metadata and statistics
            "metadata": self.metadata.copy(),
            "tags": list(self.tags),
            "last_scan_count": self.last_scan_count,
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "total_size_bytes": self.total_size_bytes,
            
            # State management
            "is_active": self.is_active,
            "is_persistent": self.is_persistent,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderConfiguration':
        """
        Create configuration from dictionary representation.
        
        Args:
            data: Dictionary with configuration data
            
        Returns:
            FolderConfiguration instance
        """
        try:
            # Create base instance
            config = cls(
                name=data["name"],
                description=data.get("description", ""),
                folder_type=FolderType(data["folder_type"]),
                folder_id=data["folder_id"]
            )
            
            # Restore timestamps
            config.created_at = datetime.fromisoformat(data["created_at"])
            config.modified_at = datetime.fromisoformat(data["modified_at"])
            config.last_accessed_at = datetime.fromisoformat(data["last_accessed_at"])
            
            # Restore target directories
            config.target_directories = [
                DirectoryTarget.from_dict(target_data)
                for target_data in data.get("target_directories", [])
            ]
            
            # Restore settings
            if "performance_settings" in data:
                config.performance_settings = PerformanceSettings(**data["performance_settings"])
            
            if "security_settings" in data:
                config.security_settings = SecuritySettings.from_dict(data["security_settings"])
            
            # Restore monitoring and indexing
            if "monitoring_mode" in data:
                config.monitoring_mode = MonitoringMode(data["monitoring_mode"])
            
            if "indexing_strategy" in data:
                config.indexing_strategy = IndexingStrategy(data["indexing_strategy"])
            
            config.auto_refresh_enabled = data.get("auto_refresh_enabled", True)
            config.auto_refresh_interval_minutes = data.get("auto_refresh_interval_minutes", 15)
            
            # Restore metadata and statistics
            config.metadata = data.get("metadata", {}).copy()
            config.tags = set(data.get("tags", []))
            config.last_scan_count = data.get("last_scan_count", 0)
            
            if data.get("last_scan_time"):
                config.last_scan_time = datetime.fromisoformat(data["last_scan_time"])
            
            config.total_size_bytes = data.get("total_size_bytes", 0)
            
            # Restore state
            config.is_active = data.get("is_active", True)
            config.is_persistent = data.get("is_persistent", True)
            config.version = data.get("version", 1)
            
            return config
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to create configuration from dictionary: {str(e)}",
                cause=e
            )
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Convert configuration to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        try:
            return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationException(
                f"Failed to serialize configuration to JSON: {str(e)}",
                cause=e
            )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FolderConfiguration':
        """
        Create configuration from JSON string.
        
        Args:
            json_str: JSON string with configuration data
            
        Returns:
            FolderConfiguration instance
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ConfigurationException(
                f"Invalid JSON format: {str(e)}",
                cause=e
            )
        except Exception as e:
            raise ConfigurationException(
                f"Failed to create configuration from JSON: {str(e)}",
                cause=e
            )
    
    def clone(self, new_name: Optional[str] = None) -> 'FolderConfiguration':
        """
        Create a copy of this configuration.
        
        Args:
            new_name: Name for the cloned configuration
            
        Returns:
            New FolderConfiguration instance
        """
        clone_data = self.to_dict()
        
        # Update for clone
        clone_data["folder_id"] = str(uuid.uuid4())
        clone_data["name"] = new_name or f"{self.name} (Copy)"
        clone_data["version"] = 1
        
        # Reset timestamps
        now = datetime.now(timezone.utc)
        clone_data["created_at"] = now.isoformat()
        clone_data["modified_at"] = now.isoformat()
        clone_data["last_accessed_at"] = now.isoformat()
        
        # Reset statistics
        clone_data["last_scan_count"] = 0
        clone_data["last_scan_time"] = None
        clone_data["total_size_bytes"] = 0
        
        return self.from_dict(clone_data)
    
    def validate_integrity(self) -> bool:
        """
        Validate configuration integrity.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValidationException: If validation fails
        """
        try:
            # Re-validate current state
            self._validate_configuration()
            
            # Validate target directories
            if not self.target_directories:
                raise ValidationException(
                    "At least one target directory must be configured"
                )
            
            for target in self.target_directories:
                path = Path(target.path)
                if not path.exists():
                    raise ValidationException(
                        f"Target directory does not exist: {target.path}",
                        field_name="target_directory",
                        field_value=target.path
                    )
                
                if not path.is_dir():
                    raise ValidationException(
                        f"Target path is not a directory: {target.path}",
                        field_name="target_directory",
                        field_value=target.path
                    )
            
            return True
            
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                f"Integrity validation failed: {str(e)}",
                cause=e
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            "folder_id": self.folder_id,
            "name": self.name,
            "folder_type": self.folder_type.value,
            "target_directories_count": len(self.target_directories),
            "target_paths": [target.path for target in self.target_directories],
            "tags": list(self.tags),
            "is_active": self.is_active,
            "last_scan_count": self.last_scan_count,
            "total_size_mb": round(self.total_size_bytes / (1024 * 1024), 2),
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "version": self.version
        }
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"FolderConfiguration(id={self.folder_id[:8]}, name='{self.name}', type={self.folder_type.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"FolderConfiguration("
            f"folder_id='{self.folder_id}', "
            f"name='{self.name}', "
            f"type={self.folder_type.value}, "
            f"targets={len(self.target_directories)}, "
            f"version={self.version})"
        )
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on folder_id."""
        if not isinstance(other, FolderConfiguration):
            return False
        return self.folder_id == other.folder_id
    
    def __hash__(self) -> int:
        """Hash based on folder_id."""
        return hash(self.folder_id)