"""
Core data models for Advanced Folders functionality.

This module defines the primary data structures and business logic
for folder configurations, search parameters, and related entities.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger('RFU.AdvancedFolders.Models')


class ScanStatus(Enum):
    """Enumeration for folder scan status."""
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    ERROR = "error"


class ParameterType(Enum):
    """Enumeration for search parameter types."""
    DIRECTORY = "directory"
    FILE_PATTERN = "file_pattern"
    CONTENT_SEARCH = "content_search"
    DATE_RANGE = "date_range"
    SIZE_RANGE = "size_range"
    FILE_TYPE = "file_type"
    EXCLUSION = "exclusion"


class ParameterOperator(Enum):
    """Enumeration for search parameter operators."""
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class SearchParameter:
    """
    Individual search parameter configuration.
    
    Represents a single search criteria with type, value, and operator.
    """
    parameter_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameter_type: ParameterType = ParameterType.FILE_PATTERN
    parameter_key: str = ""
    parameter_value: str = ""
    parameter_operator: ParameterOperator = ParameterOperator.EQUALS
    is_enabled: bool = True
    priority_order: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate parameter after initialization."""
        if not self.parameter_key:
            raise ValueError("Parameter key cannot be empty")
        if not self.parameter_value:
            raise ValueError("Parameter value cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['parameter_type'] = self.parameter_type.value
        data['parameter_operator'] = self.parameter_operator.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SearchParameter:
        """Create instance from dictionary."""
        data = data.copy()
        data['parameter_type'] = ParameterType(data['parameter_type'])
        data['parameter_operator'] = ParameterOperator(data['parameter_operator'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

    def matches_criteria(self, value: Any) -> bool:
        """
        Check if a value matches this parameter's criteria.
        
        Args:
            value: Value to test against this parameter
            
        Returns:
            bool: True if value matches the criteria
        """
        str_value = str(value).lower()
        param_value = self.parameter_value.lower()
        
        if self.parameter_operator == ParameterOperator.EQUALS:
            return str_value == param_value
        elif self.parameter_operator == ParameterOperator.CONTAINS:
            return param_value in str_value
        elif self.parameter_operator == ParameterOperator.STARTS_WITH:
            return str_value.startswith(param_value)
        elif self.parameter_operator == ParameterOperator.ENDS_WITH:
            return str_value.endswith(param_value)
        elif self.parameter_operator == ParameterOperator.REGEX:
            import re
            try:
                return bool(re.search(param_value, str_value, re.IGNORECASE))
            except re.error:
                logger.warning(f"Invalid regex pattern: {param_value}")
                return False
        
        return False


@dataclass
class FolderConfiguration:
    """
    Main folder configuration class.
    
    Represents a complete advanced folder with all search parameters
    and metadata.
    """
    folder_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    folder_name: str = ""
    description: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    last_scan_at: Optional[datetime] = None
    scan_status: ScanStatus = ScanStatus.PENDING
    total_files: int = 0
    total_size_bytes: int = 0
    configuration_version: int = 1
    search_parameters: List[SearchParameter] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.folder_name.strip():
            raise ValueError("Folder name cannot be empty")
        
        # Ensure folder name is unique (this would be enforced at database level)
        if len(self.folder_name) > 255:
            raise ValueError("Folder name too long (max 255 characters)")

    def add_search_parameter(self, param: SearchParameter) -> None:
        """
        Add a search parameter to this folder configuration.
        
        Args:
            param: SearchParameter to add
        """
        if not isinstance(param, SearchParameter):
            raise TypeError("Parameter must be SearchParameter instance")
        
        # Check for duplicate parameter keys within same type
        existing = [p for p in self.search_parameters 
                   if p.parameter_type == param.parameter_type 
                   and p.parameter_key == param.parameter_key]
        
        if existing:
            logger.warning(f"Duplicate parameter key {param.parameter_key} "
                          f"for type {param.parameter_type}")
        
        self.search_parameters.append(param)
        self.updated_at = datetime.now()

    def remove_search_parameter(self, parameter_id: str) -> bool:
        """
        Remove a search parameter by ID.
        
        Args:
            parameter_id: ID of parameter to remove
            
        Returns:
            bool: True if parameter was removed
        """
        original_count = len(self.search_parameters)
        self.search_parameters = [p for p in self.search_parameters 
                                 if p.parameter_id != parameter_id]
        
        if len(self.search_parameters) < original_count:
            self.updated_at = datetime.now()
            return True
        return False

    def get_search_parameters_by_type(self, 
                                     param_type: ParameterType) -> List[SearchParameter]:
        """
        Get all search parameters of a specific type.
        
        Args:
            param_type: Type of parameters to retrieve
            
        Returns:
            List of matching SearchParameter instances
        """
        return [p for p in self.search_parameters 
                if p.parameter_type == param_type and p.is_enabled]

    def get_directories(self) -> List[str]:
        """Get all configured directory paths."""
        dir_params = self.get_search_parameters_by_type(ParameterType.DIRECTORY)
        return [p.parameter_value for p in dir_params]

    def get_file_patterns(self) -> List[str]:
        """Get all configured file patterns."""
        pattern_params = self.get_search_parameters_by_type(ParameterType.FILE_PATTERN)
        return [p.parameter_value for p in pattern_params]

    def get_exclusion_patterns(self) -> List[str]:
        """Get all configured exclusion patterns."""
        exclusion_params = self.get_search_parameters_by_type(ParameterType.EXCLUSION)
        return [p.parameter_value for p in exclusion_params]

    def update_scan_status(self, status: ScanStatus, 
                          file_count: Optional[int] = None,
                          size_bytes: Optional[int] = None) -> None:
        """
        Update the scan status and statistics.
        
        Args:
            status: New scan status
            file_count: Updated file count (optional)
            size_bytes: Updated size in bytes (optional)
        """
        self.scan_status = status
        self.last_scan_at = datetime.now()
        self.updated_at = datetime.now()
        
        if file_count is not None:
            self.total_files = file_count
        if size_bytes is not None:
            self.total_size_bytes = size_bytes

    def generate_config_hash(self) -> str:
        """
        Generate a hash of the configuration for change detection.
        
        Returns:
            str: SHA-256 hash of configuration
        """
        # Create a stable representation for hashing
        config_data = {
            'folder_name': self.folder_name,
            'description': self.description,
            'parameters': sorted([p.to_dict() for p in self.search_parameters],
                               key=lambda x: x['parameter_id'])
        }
        
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['scan_status'] = self.scan_status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['last_scan_at'] = (self.last_scan_at.isoformat() 
                               if self.last_scan_at else None)
        data['search_parameters'] = [p.to_dict() for p in self.search_parameters]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FolderConfiguration:
        """Create instance from dictionary."""
        data = data.copy()
        data['scan_status'] = ScanStatus(data['scan_status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        if data.get('last_scan_at'):
            data['last_scan_at'] = datetime.fromisoformat(data['last_scan_at'])
        
        # Convert search parameters
        param_dicts = data.pop('search_parameters', [])
        data['search_parameters'] = [SearchParameter.from_dict(p) 
                                   for p in param_dicts]
        
        return cls(**data)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> FolderConfiguration:
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> List[str]:
        """
        Validate the configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not self.folder_name.strip():
            errors.append("Folder name is required")
        
        if len(self.folder_name) > 255:
            errors.append("Folder name too long (max 255 characters)")
        
        # Validate we have at least one directory parameter
        directories = self.get_directories()
        if not directories:
            errors.append("At least one directory must be specified")
        
        # Validate directory paths exist (basic check)
        from pathlib import Path
        for directory in directories:
            if not Path(directory).exists():
                errors.append(f"Directory does not exist: {directory}")
        
        # Validate search parameters
        for param in self.search_parameters:
            try:
                # Basic parameter validation
                if not param.parameter_key:
                    errors.append("Search parameter key cannot be empty")
                if not param.parameter_value:
                    errors.append("Search parameter value cannot be empty")
            except Exception as e:
                errors.append(f"Invalid search parameter: {e}")
        
        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0


@dataclass
class FileMetadata:
    """
    File metadata for search results.
    
    Represents metadata about a file found in a search.
    """
    file_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str = ""
    file_name: str = ""
    file_extension: str = ""
    directory_path: str = ""
    file_size: int = 0
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    accessed_date: Optional[datetime] = None
    file_hash: Optional[str] = None
    mime_type: Optional[str] = None
    file_permissions: Optional[str] = None
    is_hidden: bool = False
    is_system: bool = False
    content_summary: Optional[str] = None
    metadata_extracted_at: datetime = field(default_factory=datetime.now)
    scan_session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format
        for field_name, value in data.items():
            if isinstance(value, datetime):
                data[field_name] = value.isoformat()
            elif value is None:
                data[field_name] = None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FileMetadata:
        """Create instance from dictionary."""
        data = data.copy()
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_date', 'modified_date', 'accessed_date', 
                          'metadata_extracted_at']
        for field_name in datetime_fields:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)


class ConfigurationManager:
    """
    Manager for Advanced Folders configurations.
    
    Handles creation, validation, persistence, and management of
    folder configurations with enterprise-grade patterns.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.configurations: Dict[str, FolderConfiguration] = {}
        self.logger = logging.getLogger('RFU.AdvancedFolders.ConfigManager')
    
    def create_folder_configuration(self, name: str, 
                                   description: str = "") -> FolderConfiguration:
        """
        Create a new folder configuration.
        
        Args:
            name: Unique name for the folder
            description: Optional description
            
        Returns:
            FolderConfiguration: New configuration instance
            
        Raises:
            ValueError: If name already exists or is invalid
        """
        if not name.strip():
            raise ValueError("Folder name cannot be empty")
        
        # Check for duplicate names
        if self.get_configuration_by_name(name):
            raise ValueError(f"Folder configuration '{name}' already exists")
        
        config = FolderConfiguration(
            folder_name=name.strip(),
            description=description.strip()
        )
        
        self.configurations[config.folder_id] = config
        self.logger.info(f"Created folder configuration: {name}")
        
        return config
    
    def get_configuration(self, folder_id: str) -> Optional[FolderConfiguration]:
        """Get configuration by ID."""
        return self.configurations.get(folder_id)
    
    def get_configuration_by_name(self, name: str) -> Optional[FolderConfiguration]:
        """Get configuration by name."""
        for config in self.configurations.values():
            if config.folder_name == name:
                return config
        return None
    
    def update_configuration(self, folder_id: str, 
                           updates: Dict[str, Any]) -> bool:
        """
        Update an existing configuration.
        
        Args:
            folder_id: ID of configuration to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if update was successful
        """
        config = self.get_configuration(folder_id)
        if not config:
            return False
        
        for field, value in updates.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        config.updated_at = datetime.now()
        self.logger.info(f"Updated configuration: {config.folder_name}")
        
        return True
    
    def delete_configuration(self, folder_id: str) -> bool:
        """
        Delete a configuration.
        
        Args:
            folder_id: ID of configuration to delete
            
        Returns:
            bool: True if deletion was successful
        """
        if folder_id in self.configurations:
            config = self.configurations.pop(folder_id)
            self.logger.info(f"Deleted configuration: {config.folder_name}")
            return True
        return False
    
    def list_configurations(self, active_only: bool = True) -> List[FolderConfiguration]:
        """
        List all configurations.
        
        Args:
            active_only: If True, only return active configurations
            
        Returns:
            List of FolderConfiguration instances
        """
        configs = list(self.configurations.values())
        if active_only:
            configs = [c for c in configs if c.is_active]
        
        return sorted(configs, key=lambda x: x.folder_name)
    
    def validate_all_configurations(self) -> Dict[str, List[str]]:
        """
        Validate all configurations.
        
        Returns:
            Dictionary mapping configuration names to validation errors
        """
        validation_results = {}
        
        for config in self.configurations.values():
            errors = config.validate()
            if errors:
                validation_results[config.folder_name] = errors
        
        return validation_results
    
    def export_configurations(self) -> Dict[str, Any]:
        """
        Export all configurations to dictionary.
        
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            'export_version': '1.0.0',
            'export_timestamp': datetime.now().isoformat(),
            'configurations': [config.to_dict() 
                             for config in self.configurations.values()]
        }
    
    def import_configurations(self, data: Dict[str, Any], 
                            overwrite: bool = False) -> List[str]:
        """
        Import configurations from dictionary.
        
        Args:
            data: Dictionary containing configuration data
            overwrite: If True, overwrite existing configurations
            
        Returns:
            List of imported configuration names
        """
        imported = []
        
        configurations = data.get('configurations', [])
        for config_data in configurations:
            try:
                config = FolderConfiguration.from_dict(config_data)
                
                # Check for existing configuration
                existing = self.get_configuration_by_name(config.folder_name)
                if existing and not overwrite:
                    self.logger.warning(f"Skipping existing configuration: "
                                      f"{config.folder_name}")
                    continue
                
                if existing and overwrite:
                    # Remove existing configuration
                    self.delete_configuration(existing.folder_id)
                
                self.configurations[config.folder_id] = config
                imported.append(config.folder_name)
                
            except Exception as e:
                self.logger.error(f"Failed to import configuration: {e}")
        
        return imported