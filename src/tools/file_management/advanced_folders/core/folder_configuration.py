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
    size_min: Optional[int] = None  # bytes
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        
        # Handle datetime serialization
        if self.date_from:
            data['date_from'] = self.date_from.isoformat()
        if self.date_to:
            data['date_to'] = self.date_to.isoformat()
            
        # Handle sets
        data['include_extensions'] = list(self.include_extensions)
        data['exclude_extensions'] = list(self.exclude_extensions)
        data['include_mime_types'] = list(self.include_mime_types)
        
        # Handle enum
        data['search_scope'] = self.search_scope.value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchParameters':
        """Create instance from dictionary."""
        # Handle datetime deserialization
        if 'date_from' in data and data['date_from']:
            data['date_from'] = datetime.fromisoformat(data['date_from'])
        if 'date_to' in data and data['date_to']:
            data['date_to'] = datetime.fromisoformat(data['date_to'])
            
        # Handle sets
        if 'include_extensions' in data:
            data['include_extensions'] = set(data['include_extensions'])
        if 'exclude_extensions' in data:
            data['exclude_extensions'] = set(data['exclude_extensions'])
        if 'include_mime_types' in data:
            data['include_mime_types'] = set(data['include_mime_types'])
            
        # Handle enum
        if 'search_scope' in data:
            data['search_scope'] = SearchScope(data['search_scope'])
            
        return cls(**data)


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        if self.last_scan_time:
            data['last_scan_time'] = self.last_scan_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderStatistics':
        """Create instance from dictionary."""
        if 'last_scan_time' in data and data['last_scan_time']:
            data['last_scan_time'] = datetime.fromisoformat(
                data['last_scan_time']
            )
        return cls(**data)


@dataclass
class FolderConfiguration:
    """Configuration for an advanced folder."""
    
    # Core identification
    folder_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Directory configuration
    directory_paths: List[str] = field(default_factory=list)
    
    # Search configuration
    search_parameters: SearchParameters = field(
        default_factory=SearchParameters
    )
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            'folder_id': self.folder_id,
            'name': self.name,
            'description': self.description,
            'directory_paths': self.directory_paths,
            'search_parameters': self.search_parameters.to_dict(),
            'sort_criteria': self.sort_criteria.value,
            'sort_ascending': self.sort_ascending,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'last_accessed': (
                self.last_accessed.isoformat() 
                if self.last_accessed else None
            ),
            'statistics': self.statistics.to_dict(),
            'auto_refresh': self.auto_refresh,
            'refresh_interval': self.refresh_interval,
            'enable_preview': self.enable_preview,
            'color_scheme': self.color_scheme
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderConfiguration':
        """Create instance from dictionary."""
        # Handle datetime fields
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['modified_date'] = datetime.fromisoformat(data['modified_date'])
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(
                data['last_accessed']
            )
        
        # Handle nested objects
        data['search_parameters'] = SearchParameters.from_dict(
            data['search_parameters']
        )
        
        # Handle statistics (optional for backward compatibility)
        if 'statistics' in data:
            data['statistics'] = FolderStatistics.from_dict(data['statistics'])
        else:
            # Create default statistics if missing
            data['statistics'] = FolderStatistics()
            
        data['sort_criteria'] = SortCriteria(data['sort_criteria'])
        
        return cls(**data)
    
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
    
    def __init__(self, config_manager=None):
        """Initialize the configuration manager.
        
        Args:
            config_manager: Optional ConfigManager instance for persistence
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger('AdvancedFolders.ConfigManager')
        self._configurations: Dict[str, FolderConfiguration] = {}
        self._config_file = Path("config/advanced_folders.json")
        
        # Load existing configurations
        self.load_configurations()
    
    def create_folder(self, name: str, description: str = "", 
                     directory_paths: List[str] = None) -> FolderConfiguration:
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
            directory_paths=directory_paths or []
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
    
    def update_folder(self, folder_id: str, 
                     updates: Dict[str, Any]) -> bool:
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
    
    def delete_folder(self, folder_id: str) -> bool:
        """Delete folder configuration.
        
        Args:
            folder_id: Folder configuration ID
            
        Returns:
            bool: True if deletion was successful
        """
        if folder_id in self._configurations:
            config = self._configurations.pop(folder_id)
            self.save_configurations()
            self.logger.info(f"Deleted folder configuration: {config.name}")
            return True
        else:
            self.logger.error(f"Folder not found: {folder_id}")
            return False
    
    def save_configurations(self) -> bool:
        """Save configurations to file.
        
        Returns:
            bool: True if save was successful
        """
        try:
            # Ensure config directory exists
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert configurations to serializable format
            data = {
                'version': '1.0',
                'configurations': {
                    folder_id: config.to_dict()
                    for folder_id, config in self._configurations.items()
                },
                'export_timestamp': datetime.now().isoformat()
            }
            
            # Write to file
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Configurations saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configurations: {e}")
            return False
    
    def load_configurations(self) -> bool:
        """Load configurations from file.
        
        Returns:
            bool: True if load was successful
        """
        try:
            if not self._config_file.exists():
                self.logger.info("No existing configuration file found")
                return True
            
            with open(self._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load configurations
            configurations = data.get('configurations', {})
            self._configurations = {}
            
            for folder_id, config_data in configurations.items():
                try:
                    config = FolderConfiguration.from_dict(config_data)
                    self._configurations[folder_id] = config
                except Exception as e:
                    self.logger.error(
                        f"Failed to load configuration {folder_id}: {e}"
                    )
            
            self.logger.info(
                f"Loaded {len(self._configurations)} configurations"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            return False
    
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
                'version': '1.0',
                'export_timestamp': datetime.now().isoformat(),
                'configurations': {
                    folder_id: config.to_dict()
                    for folder_id, config in self._configurations.items()
                }
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configurations exported to {export_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configurations: {e}")
            return False
    
    def import_configurations(self, import_path: Union[str, Path],
                            merge: bool = True) -> bool:
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
            
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate import data
            if 'configurations' not in data:
                self.logger.error("Invalid import file format")
                return False
            
            # Import configurations
            imported_configs = {}
            for folder_id, config_data in data['configurations'].items():
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
            
            self.logger.info(
                f"Imported {len(imported_configs)} configurations"
            )
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
            backup_path = self._config_file.parent / f"advanced_folders_backup_{timestamp}.json"
        
        return self.export_configurations(backup_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration statistics.
        
        Returns:
            Dictionary with configuration statistics
        """
        total_configs = len(self._configurations)
        total_directories = sum(
            len(config.directory_paths) 
            for config in self._configurations.values()
        )
        
        # Calculate other statistics
        stats = {
            'total_configurations': total_configs,
            'total_directories': total_directories,
            'configurations_with_auto_refresh': sum(
                1 for config in self._configurations.values()
                if config.auto_refresh
            ),
            'configurations_with_content_search': sum(
                1 for config in self._configurations.values()
                if config.search_parameters.index_content
            ),
            'average_refresh_interval': (
                sum(config.refresh_interval 
                    for config in self._configurations.values()) / 
                total_configs
            ) if total_configs > 0 else 0
        }
        
        return stats