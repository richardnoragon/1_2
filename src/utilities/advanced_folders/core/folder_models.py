"""
Mock Backend Models for GUI Testing

Provides mock implementations of the backend models that the GUI components
depend on, allowing for isolated GUI testing without full backend implementation.

Author: RFU Development Team
Version: 1.0.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationStatus(Enum):
    """Validation status enumeration."""
    VALID = "valid"
    WARNING = "warning" 
    ERROR = "error"


@dataclass
class ValidationResult:
    """Mock validation result for testing."""
    is_valid: bool = True
    errors: List[str] = None
    warnings: List[str] = None
    status: ValidationStatus = ValidationStatus.VALID
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        
        # Update status based on errors/warnings
        if self.errors:
            self.is_valid = False
            self.status = ValidationStatus.ERROR
        elif self.warnings:
            self.status = ValidationStatus.WARNING


@dataclass 
class FolderConfiguration:
    """Mock folder configuration for testing."""
    name: str = ""
    description: str = ""
    directories: List[str] = None
    include_subdirectories: bool = True
    follow_symlinks: bool = False
    include_hidden: bool = False
    monitor_changes: bool = True
    file_filters: List[str] = None
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.directories is None:
            self.directories = []
        if self.file_filters is None:
            self.file_filters = []
        if self.exclude_patterns is None:
            self.exclude_patterns = []
    
    def validate(self) -> ValidationResult:
        """Validate the configuration."""
        errors = []
        warnings = []
        
        # Name validation
        if not self.name or not self.name.strip():
            errors.append("Configuration name is required")
        elif len(self.name) > 255:
            errors.append("Configuration name cannot exceed 255 characters")
        
        # Directory validation
        if not self.directories:
            errors.append("At least one directory must be selected")
        
        # Check for invalid characters in name
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in self.name for char in invalid_chars):
            errors.append("Configuration name contains invalid characters")
        
        # Warnings
        if len(self.directories) > 10:
            warnings.append("Large number of directories may impact performance")
        
        if self.follow_symlinks:
            warnings.append("Following symlinks may cause infinite loops")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'directories': self.directories,
            'include_subdirectories': self.include_subdirectories,
            'follow_symlinks': self.follow_symlinks,
            'include_hidden': self.include_hidden,
            'monitor_changes': self.monitor_changes,
            'file_filters': self.file_filters,
            'exclude_patterns': self.exclude_patterns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderConfiguration':
        """Create from dictionary."""
        return cls(**data)


class ConfigurationManager:
    """Mock configuration manager for testing."""
    
    def __init__(self):
        self._configurations = {}
        self._next_id = 1
    
    def create_configuration(self, config: FolderConfiguration) -> int:
        """Create a new configuration."""
        config_id = self._next_id
        self._configurations[config_id] = config
        self._next_id += 1
        return config_id
    
    def get_configuration(self, config_id: int) -> Optional[FolderConfiguration]:
        """Get configuration by ID."""
        return self._configurations.get(config_id)
    
    def update_configuration(self, config_id: int, config: FolderConfiguration) -> bool:
        """Update existing configuration."""
        if config_id in self._configurations:
            self._configurations[config_id] = config
            return True
        return False
    
    def delete_configuration(self, config_id: int) -> bool:
        """Delete configuration."""
        if config_id in self._configurations:
            del self._configurations[config_id]
            return True
        return False
    
    def list_configurations(self) -> List[FolderConfiguration]:
        """List all configurations."""
        return list(self._configurations.values())
    
    def validate_configuration(self, config: FolderConfiguration) -> ValidationResult:
        """Validate a configuration."""
        return config.validate()


# Mock search and filter classes
class SearchFilter:
    """Mock search filter for testing."""
    
    def __init__(self, pattern: str = "", include_subdirs: bool = True):
        self.pattern = pattern
        self.include_subdirs = include_subdirs
        
    def matches(self, file_path: str) -> bool:
        """Check if file matches filter."""
        return self.pattern.lower() in file_path.lower()


class FileTypeFilter:
    """Mock file type filter for testing."""
    
    def __init__(self, file_types: List[str] = None):
        self.file_types = file_types or []
    
    def matches(self, file_path: str) -> bool:
        """Check if file matches type filter."""
        if not self.file_types:
            return True
        
        file_ext = file_path.split('.')[-1].lower()
        return file_ext in [ft.lower() for ft in self.file_types]


# Export mock classes for testing
__all__ = [
    'ValidationResult',
    'ValidationStatus', 
    'FolderConfiguration',
    'ConfigurationManager',
    'SearchFilter',
    'FileTypeFilter'
]