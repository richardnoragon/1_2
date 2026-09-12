"""
Core data models for Advanced Folders feature.

This module defines the data structures and management classes for
folder configurations, search parameters, and persistent storage.
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

try:
    from src.config.config_manager import get_config_manager
except Exception:  # pragma: no cover
    get_config_manager = None


class SortCriteria(Enum):
    """Enumeration of available sort criteria."""

    ALPHABETICAL = "alphabetical"
    FILE_SIZE = "file_size"
    FILE_TYPE = "file_type"
    CREATION_DATE = "creation_date"
    MODIFICATION_DATE = "modification_date"
    ACCESS_DATE = "access_date"


class SearchScope(Enum):
    """Enumeration of search scope options."""

    FILE_NAME = "file_name"
    FILE_CONTENT = "file_content"
    FILE_METADATA = "file_metadata"
    ALL_ATTRIBUTES = "all_attributes"


@dataclass
class SearchParameters:
    """Search parameters for folder content filtering."""

    # File name pattern matching
    filename_pattern: str = ""
    use_regex: bool = False
    case_sensitive: bool = False

    # Content search
    content_search: str = ""
    search_scope: SearchScope = SearchScope.FILE_NAME

    # Date filtering
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    date_criteria: str = "modified"  # modified, created, accessed

    # Size filtering
    size_min: int = 0  # bytes
    size_max: Optional[int] = None  # bytes

    # File type filtering
    include_extensions: Set[str] = field(default_factory=set)
    exclude_extensions: Set[str] = field(default_factory=set)
    include_mime_types: Set[str] = field(default_factory=set)

    # Advanced options
    include_subdirectories: bool = True
    follow_symbolic_links: bool = True
    include_hidden_files: bool = False
    monitor_changes: bool = True
    search_depth: int = -1  # -1 for unlimited
    max_results: int = 10000

    # Performance options
    index_content: bool = True
    cache_results: bool = True
    search_archives: bool = False
    include_network_locations: bool = True

    # Legacy compatibility fields
    path: str = ""
    file_extensions: List[str] = field(default_factory=list)
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    recursive: bool = True
    include_hidden: bool = False
    max_depth: int = -1

    def __post_init__(self):
        """Normalize legacy and modern field names to a single representation."""
        if self.file_extensions and not self.include_extensions:
            self.include_extensions = set(self.file_extensions)
        elif self.include_extensions and not self.file_extensions:
            self.file_extensions = sorted(self.include_extensions)

        if self.path and not self.include_hidden and self.include_hidden_files:
            self.include_hidden = self.include_hidden_files
        if self.modified_after and not self.date_from:
            self.date_from = self.modified_after
        if self.modified_before and not self.date_to:
            self.date_to = self.modified_before
        if self.max_depth != -1 and self.search_depth == -1:
            self.search_depth = self.max_depth
        if self.recursive and self.search_depth == -1:
            self.search_depth = -1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)

        # Handle datetime serialization
        if self.date_from:
            data["date_from"] = self.date_from.isoformat()
        if self.date_to:
            data["date_to"] = self.date_to.isoformat()
        if self.modified_after:
            data["modified_after"] = self.modified_after.isoformat()
        if self.modified_before:
            data["modified_before"] = self.modified_before.isoformat()

        # Preserve legacy ordering when available; sets are otherwise normalized
        # to a stable list for compatibility with older serialized payloads.
        data["include_extensions"] = sorted(self.include_extensions)
        data["exclude_extensions"] = sorted(self.exclude_extensions)
        data["include_mime_types"] = sorted(self.include_mime_types)
        ordered_extensions = list(self.file_extensions) if self.file_extensions else sorted(self.include_extensions)
        data["file_extensions"] = ordered_extensions

        # Handle enum
        data["search_scope"] = self.search_scope.value
        data["path"] = self.path
        data["include_hidden"] = self.include_hidden or self.include_hidden_files
        data["recursive"] = self.recursive
        data["max_depth"] = self.max_depth if self.max_depth != -1 else self.search_depth

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchParameters":
        """Create instance from dictionary."""
        normalized = dict(data)

        # Handle datetime deserialization
        for key in ("date_from", "date_to", "modified_after", "modified_before"):
            value = normalized.get(key)
            if value:
                normalized[key] = datetime.fromisoformat(value)

        # Handle sets
        for key in ("include_extensions", "exclude_extensions", "include_mime_types"):
            if key in normalized:
                normalized[key] = set(normalized[key])

        # Legacy compatibility fields
        if "include_extensions" in normalized:
            normalized["include_extensions"] = set(normalized["include_extensions"])
        if "file_extensions" in normalized:
            file_extensions = list(normalized["file_extensions"])
            normalized["file_extensions"] = file_extensions
            if "include_extensions" not in normalized or not normalized["include_extensions"]:
                normalized["include_extensions"] = set(file_extensions)
        elif "include_extensions" in normalized:
            normalized["file_extensions"] = list(normalized["include_extensions"])
        if "path" in normalized:
            normalized["path"] = str(normalized["path"])
        if "recursive" in normalized and "include_subdirectories" not in normalized:
            normalized["include_subdirectories"] = normalized["recursive"]
        if "include_hidden" in normalized and "include_hidden_files" not in normalized:
            normalized["include_hidden_files"] = normalized["include_hidden"]
        if "max_depth" in normalized and "search_depth" not in normalized:
            normalized["search_depth"] = normalized["max_depth"]

        # Handle enum
        if "search_scope" in normalized:
            normalized["search_scope"] = SearchScope(normalized["search_scope"])

        return cls(**normalized)


@dataclass
class FolderStatistics:
    """Statistics for a folder configuration."""

    total_files: int = 0
    total_size: int = 0  # bytes
    last_scan_time: Optional[datetime] = None
    scan_duration: float = 0.0  # seconds
    file_type_breakdown: Dict[str, int] = field(default_factory=dict)
    size_breakdown: Dict[str, int] = field(default_factory=dict)
    growth_trends: Dict[str, Any] = field(default_factory=dict)
    last_scan: Optional[datetime] = None
    average_file_size: int = 0
    largest_file_size: int = 0
    smallest_file_size: int = 0
    file_types: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Backward-compatible alias normalization."""
        if self.last_scan is not None and self.last_scan_time is None:
            self.last_scan_time = self.last_scan
        if self.last_scan_time is not None and self.last_scan is None:
            self.last_scan = self.last_scan_time
        if not self.file_type_breakdown and self.file_types:
            self.file_type_breakdown = dict(self.file_types)
        if not self.file_types and self.file_type_breakdown:
            self.file_types = dict(self.file_type_breakdown)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        if self.last_scan_time:
            data["last_scan_time"] = self.last_scan_time.isoformat()
        if self.last_scan:
            data["last_scan"] = self.last_scan.isoformat()
        if self.file_type_breakdown:
            data["file_type_breakdown"] = dict(self.file_type_breakdown)
        if self.file_types:
            data["file_types"] = dict(self.file_types)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FolderStatistics":
        """Create instance from dictionary."""
        normalized = dict(data)
        for key in ("last_scan_time", "last_scan"):
            if normalized.get(key):
                normalized[key] = datetime.fromisoformat(normalized[key])
        if "file_types" in normalized and not normalized.get("file_type_breakdown"):
            normalized["file_type_breakdown"] = dict(normalized["file_types"])
        if "file_type_breakdown" in normalized and not normalized.get("file_types"):
            normalized["file_types"] = dict(normalized["file_type_breakdown"])
        return cls(**normalized)


@dataclass
class FolderConfiguration:
    """Configuration for an advanced folder."""

    # Core identification
    folder_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    path: str = ""
    enabled: bool = True

    # Directory configuration
    directory_paths: List[str] = field(default_factory=list)

    # Search configuration
    search_parameters: SearchParameters = field(default_factory=SearchParameters)

    # Sort configuration
    sort_criteria: SortCriteria = SortCriteria.ALPHABETICAL
    sort_ascending: bool = True

    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None

    # Statistics
    statistics: FolderStatistics = field(default_factory=FolderStatistics)

    # Advanced options
    auto_refresh: bool = True
    refresh_interval: int = 300  # seconds
    enable_preview: bool = True
    color_scheme: str = "default"

    def __post_init__(self):
        """Keep legacy and modern field names synchronized."""
        if not self.folder_id:
            self.folder_id = self.id or str(uuid.uuid4())
        if not self.id:
            self.id = self.folder_id
        if self.id != self.folder_id:
            self.id = self.folder_id
        self.folder_id = self.id

        if self.path and not self.directory_paths:
            self.directory_paths = [self.path]
        if not self.path and self.directory_paths:
            self.path = self.directory_paths[0]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "folder_id": self.folder_id,
            "id": self.folder_id,
            "name": self.name,
            "description": self.description,
            "path": self.path or (self.directory_paths[0] if self.directory_paths else ""),
            "directory_paths": self.directory_paths,
            "search_parameters": self.search_parameters.to_dict(),
            "sort_criteria": self.sort_criteria.value,
            "sort_ascending": self.sort_ascending,
            "created_date": self.created_date.isoformat(),
            "modified_date": self.modified_date.isoformat(),
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "statistics": self.statistics.to_dict(),
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "enable_preview": self.enable_preview,
            "color_scheme": self.color_scheme,
            "enabled": self.enabled,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FolderConfiguration":
        """Create instance from dictionary."""
        normalized = dict(data)
        folder_id = normalized.get("folder_id") or normalized.get("id") or str(uuid.uuid4())
        normalized["folder_id"] = folder_id
        normalized["id"] = folder_id

        if "path" in normalized and "directory_paths" not in normalized:
            normalized["directory_paths"] = [normalized["path"]]
        if "directory_paths" in normalized and not normalized.get("path"):
            normalized["path"] = normalized["directory_paths"][0] if normalized["directory_paths"] else ""

        # Handle datetime fields
        for key in ("created_date", "modified_date", "last_accessed"):
            if key in normalized and normalized[key]:
                normalized[key] = datetime.fromisoformat(normalized[key])

        if "search_parameters" in normalized and normalized["search_parameters"]:
            normalized["search_parameters"] = SearchParameters.from_dict(
                normalized["search_parameters"]
            )

        # Handle statistics (optional for backward compatibility)
        if "statistics" in normalized:
            normalized["statistics"] = FolderStatistics.from_dict(normalized["statistics"])
        else:
            normalized["statistics"] = FolderStatistics()

        if "sort_criteria" in normalized and normalized["sort_criteria"]:
            normalized["sort_criteria"] = SortCriteria(normalized["sort_criteria"])

        return cls(**normalized)

    def update_access_time(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.now()
        self.modified_date = datetime.now()

    def validate(self) -> List[str]:
        """Validate configuration and return list of validation errors."""
        errors = []

        if not self.name.strip():
            errors.append("Folder name cannot be empty")

        if not self.directory_paths:
            errors.append("At least one directory path must be specified")

        # Validate directory paths
        for path in self.directory_paths:
            if not path.strip():
                errors.append("Directory path cannot be empty")
            elif not Path(path).exists():
                errors.append(f"Directory path does not exist: {path}")

        # Validate search parameters
        if self.search_parameters.max_results <= 0:
            errors.append("Maximum results must be greater than 0")

        if self.search_parameters.search_depth == 0:
            errors.append("Search depth cannot be 0")

        if self.refresh_interval < 30:
            errors.append("Refresh interval must be at least 30 seconds")

        return errors


class FolderConfigurationManager:
    """Manager for folder configurations with persistence."""

    def __init__(self, config_manager=None, config_file: Union[str, Path, None] = None):
        """Initialize the configuration manager.

        Args:
            config_manager: Optional ConfigManager instance for persistence
            config_file: Optional path override for persistence
        """
        if config_manager is None:
            try:
                from src.config import config_manager as config_manager_module

                config_manager = config_manager_module.get_config_manager()
            except Exception:
                if get_config_manager is not None:
                    try:
                        config_manager = get_config_manager()
                    except Exception:
                        config_manager = None
                else:
                    config_manager = None

        self.config_manager = config_manager
        self.logger = logging.getLogger("AdvancedFolders.ConfigManager")
        self._configurations: Dict[str, FolderConfiguration] = {}
        self._config_file = Path(config_file) if config_file else Path("config/advanced_folders.json")
        self.config_file = self._config_file

        # Load existing configurations
        self.load_configurations()

    def _load_from_config_manager(self) -> List[FolderConfiguration]:
        """Load folder configurations from the shared RFU config manager."""
        if self.config_manager is None:
            return list(self._configurations.values())

        raw_configs = self.config_manager.get_setting(
            "advanced_folders", "configurations", []
        )
        if not isinstance(raw_configs, list):
            return list(self._configurations.values())

        loaded: List[FolderConfiguration] = []
        for item in raw_configs:
            if not isinstance(item, dict):
                continue
            try:
                config = FolderConfiguration.from_dict(item)
                loaded.append(config)
            except Exception as exc:
                self.logger.warning(
                    "Failed to decode advanced folder configuration from config manager: %s",
                    exc,
                )

        self._configurations = {config.folder_id: config for config in loaded}
        return loaded

    def _save_to_config_manager(self, configurations: Optional[List[FolderConfiguration]] = None) -> None:
        """Persist folder configurations back into the RFU config manager."""
        if self.config_manager is None:
            return

        items = configurations if configurations is not None else list(self._configurations.values())
        payload = [config.to_dict() for config in items]
        self.config_manager.set_setting("advanced_folders", "configurations", payload)

    @property
    def config_file(self) -> Path:
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        self._config_file = Path(value)
        self._configurations = {}
        if self._config_file.exists():
            self.load_configurations()

    def save_configuration(self, config: FolderConfiguration) -> bool:
        """Backward-compatible method for saving a single configuration."""
        self._configurations[config.folder_id] = config
        return self.save_configurations()

    def update_configuration(self, config: FolderConfiguration) -> bool:
        """Backward-compatible method for updating a single configuration."""
        self._configurations[config.folder_id] = config
        return self.save_configurations()

    def delete_configuration(self, folder_id: str) -> bool:
        """Backward-compatible method for deleting a configuration."""
        if folder_id in self._configurations:
            self._configurations.pop(folder_id)
            return self.save_configurations()
        return False

    def create_folder(
        self,
        name: str,
        description: str = "",
        directory_paths: List[str] = None,
    ) -> FolderConfiguration:
        """Create a new folder configuration.

        Args:
            name: Folder name
            description: Optional description
            directory_paths: List of directory paths to include

        Returns:
            FolderConfiguration: The created configuration
        """
        config = FolderConfiguration(
            name=name,
            description=description,
            directory_paths=directory_paths or [],
        )

        self._configurations[config.folder_id] = config
        self.save_configurations()

        self.logger.info(f"Created folder configuration: {name}")
        return config

    def get_folder(self, folder_id: str) -> Optional[FolderConfiguration]:
        """Get folder configuration by ID.

        Args:
            folder_id: Folder configuration ID

        Returns:
            FolderConfiguration or None if not found
        """
        config = self._configurations.get(folder_id)
        if config:
            config.update_access_time()
            self.save_configurations()
        return config

    def get_folder_by_name(self, name: str) -> Optional[FolderConfiguration]:
        """Get folder configuration by name.

        Args:
            name: Folder name

        Returns:
            FolderConfiguration or None if not found
        """
        for config in self._configurations.values():
            if config.name == name:
                config.update_access_time()
                self.save_configurations()
                return config
        return None

    def list_folders(self) -> List[FolderConfiguration]:
        """Get list of all folder configurations.

        Returns:
            List of FolderConfiguration objects
        """
        return list(self._configurations.values())

    def update_folder(self, folder_id: str, updates: Dict[str, Any]) -> bool:
        """Update folder configuration.

        Args:
            folder_id: Folder configuration ID
            updates: Dictionary of updates to apply

        Returns:
            bool: True if update was successful
        """
        if folder_id not in self._configurations:
            self.logger.error(f"Folder not found: {folder_id}")
            return False

        config = self._configurations[folder_id]

        # Apply updates
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)

        config.modified_date = datetime.now()
        self.save_configurations()

        self.logger.info(f"Updated folder configuration: {config.name}")
        return True

    def delete_folder(self, folder_id: str, dry_run: bool = False) -> bool:
        """Delete folder configuration.

        Args:
            folder_id: Folder configuration ID
            dry_run: When True, validates the deletion without modifying data.

        Returns:
            bool: True if deletion was successful (or would succeed)
        """
        if folder_id in self._configurations:
            if dry_run:
                self.logger.debug(
                    f"Dry run: would delete folder configuration: "
                    f"{self._configurations[folder_id].name}"
                )
            else:
                config = self._configurations.pop(folder_id)
                self.save_configurations()
                self.logger.info(f"Deleted folder configuration: {config.name}")
            return True
        else:
            self.logger.error(f"Folder not found: {folder_id}")
            return False

    def save_configurations(self, dry_run: bool = False) -> bool:
        """Save configurations to file.

        Args:
            dry_run: When True, validates the data structure without writing
                     any files to disk.

        Returns:
            bool: True if save was successful (or would succeed)
        """
        try:
            # Convert configurations to serializable format
            data = {
                "version": "1.0",
                "configurations": {
                    folder_id: config.to_dict()
                    for folder_id, config in self._configurations.items()
                },
                "export_timestamp": datetime.now().isoformat(),
            }

            if dry_run:
                self.logger.debug(
                    "Dry run: configuration serialisation validated; "
                    "no file written."
                )
                return True

            # Ensure config directory exists
            self._config_file.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug("Configurations saved successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save configurations: {e}")
            return False

    def load_configurations(self) -> List[FolderConfiguration]:
        """Load configurations from file.

        Returns:
            List[FolderConfiguration]: loaded configurations. This preserves
            the legacy list-based API while still populating the manager state.
        """
        try:
            if not self._config_file.exists():
                self.logger.info("No existing configuration file found")
                return list(self._configurations.values())

            with open(self._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load configurations
            configurations = data.get("configurations", {})
            self._configurations = {}

            for folder_id, config_data in configurations.items():
                try:
                    config = FolderConfiguration.from_dict(config_data)
                    self._configurations[folder_id] = config
                except Exception as e:
                    self.logger.error(f"Failed to load configuration {folder_id}: {e}")

            self.logger.info(f"Loaded {len(self._configurations)} configurations")
            return list(self._configurations.values())

        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            return list(self._configurations.values())

    def export_configurations(self, export_path: Union[str, Path]) -> bool:
        """Export configurations to a file.

        Args:
            export_path: Path to export file

        Returns:
            bool: True if export was successful
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0",
                "export_timestamp": datetime.now().isoformat(),
                "configurations": {
                    folder_id: config.to_dict()
                    for folder_id, config in self._configurations.items()
                },
            }

            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Configurations exported to {export_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export configurations: {e}")
            return False

    def import_configurations(
        self, import_path: Union[str, Path], merge: bool = True
    ) -> bool:
        """Import configurations from a file.

        Args:
            import_path: Path to import file
            merge: If True, merge with existing configurations.
                  If False, replace all configurations.

        Returns:
            bool: True if import was successful
        """
        try:
            import_file = Path(import_path)

            if not import_file.exists():
                self.logger.error(f"Import file not found: {import_file}")
                return False

            with open(import_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate import data
            if "configurations" not in data:
                self.logger.error("Invalid import file format")
                return False

            # Import configurations
            imported_configs = {}
            for folder_id, config_data in data["configurations"].items():
                try:
                    config = FolderConfiguration.from_dict(config_data)
                    imported_configs[folder_id] = config
                except Exception as e:
                    self.logger.error(
                        f"Failed to import configuration {folder_id}: {e}"
                    )

            # Apply configurations
            if not merge:
                self._configurations = imported_configs
            else:
                self._configurations.update(imported_configs)

            # Save merged configurations
            self.save_configurations()

            self.logger.info(f"Imported {len(imported_configs)} configurations")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import configurations: {e}")
            return False

    def backup_configurations(self, backup_path: Union[str, Path] = None) -> bool:
        """Create backup of configurations.

        Args:
            backup_path: Optional backup file path

        Returns:
            bool: True if backup was successful
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = (
                self._config_file.parent / f"advanced_folders_backup_{timestamp}.json"
            )

        return self.export_configurations(backup_path)

    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration statistics.

        Returns:
            Dictionary with configuration statistics
        """
        total_configs = len(self._configurations)
        total_directories = sum(
            len(config.directory_paths) for config in self._configurations.values()
        )

        # Calculate other statistics
        stats = {
            "total_configurations": total_configs,
            "total_directories": total_directories,
            "configurations_with_auto_refresh": sum(
                1 for config in self._configurations.values() if config.auto_refresh
            ),
            "configurations_with_content_search": sum(
                1
                for config in self._configurations.values()
                if config.search_parameters.index_content
            ),
            "average_refresh_interval": (
                (
                    sum(
                        config.refresh_interval
                        for config in self._configurations.values()
                    )
                    / total_configs
                )
                if total_configs > 0
                else 0
            ),
        }

        return stats
