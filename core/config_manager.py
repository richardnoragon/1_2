import json
from pathlib import Path
from typing import Any, Dict, Optional
import logging
import shutil
import os

from core.error_handler import get_error_handler

# Get error handler instance
error_handler = get_error_handler()



class ConfigManager:
    """A class that handles config manager."""
    _instance = None
    
    def __new__(cls, config_file=None):
        """new.
        Args:
            cls (Any): Description of cls
            config_file (str, optional): Path to config file"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize(config_file)
        return cls._instance
    
    def _initialize(self, config_file=None):
        """Initialize the configuration manager."""
        if config_file:
            self.config_path = Path(config_file)
        else:
            self.config_path = Path(__file__).parent.parent / 'configuration.json'
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger('RFU.ConfigManager')
        self.logger.info('Initializing configuration manager')
        self.load_config()
        
        # Initialize profiles section if not exists
        if 'profiles' not in self.config:
            self.config['profiles'] = {}
            self.save_config()  # Call without arguments
    
    def load_config(self) -> None:
        """Load the configuration from file."""
        try:
            config_path = Path(self.config_path) if isinstance(self.config_path, str) else self.config_path
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                    self.logger.info('Configuration loaded successfully')
            else:
                self.logger.warning(
                    'No configuration file found, creating default'
                )
                self.reset_to_defaults()
        except Exception as e:
            self.logger.error(
                f'Error loading configuration: {str(e)}',
                exc_info=True
            )
            self.reset_to_defaults()
    
    def save_config(self, config_data: Dict[str, Any] = None, validate_required: bool = False) -> None:
        """Save the configuration to file.
        
        Args:
            config_data: Configuration dictionary to save. If None, saves current config.
            validate_required: Whether to validate required fields are present.
        """
        try:
            if config_data is not None:
                # Validate types if config_data is provided
                self._validate_config_types(config_data)
                
                # Validate required fields if requested
                if validate_required:
                    self._validate_required_fields(config_data)
                
                # Store flat config directly for test compatibility
                self.config.update(config_data)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info('Configuration saved successfully')
        except Exception as e:
            self.logger.error(
                f'Error saving configuration: {str(e)}',
                exc_info=True
            )
            raise
    
    def _validate_config_types(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration value types."""
        type_rules = {
            'theme': str,
            'language': str,
            'show_hidden': bool
        }
        
        for key, expected_type in type_rules.items():
            if key in config_data and not isinstance(config_data[key], expected_type):
                raise ValueError(f"'{key}' must be of type {expected_type.__name__}")
    
    def _validate_required_fields(self, config_data: Dict[str, Any]) -> None:
        """Validate that required fields are present."""
        required_fields = ['theme', 'language']
        
        for field in required_fields:
            if field not in config_data:
                raise ValueError(f"Required field '{field}' is missing")
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a setting value from the configuration."""
        try:
            value = self.config.get(section, {}).get(key, default)
            self.logger.debug(f'Retrieved setting {section}.{key}: {value}')
            return value
        except Exception:
            self.logger.warning(
                f'Failed to get {section}.{key}, using default: {default}'
            )
            return default
    
    def set_setting(self, section: str, key: str, value: Any) -> None:
        """Set a setting value in the configuration."""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
            self.save_config()  # Call without arguments to save current config
            self.logger.info(f'Updated setting {section}.{key} to {value}')
        except Exception as e:
            self.logger.error(
                f'Error setting {section}.{key}: {str(e)}',
                exc_info=True
            )
    
    def add_recent_directory(self, directory: str) -> None:
        """Add a directory to recent directories list."""
        if not directory:
            return
            
        recent = self.config.get('general', {}).get('recent_directories', [])
        max_entries = self.config.get('general', {}).get('max_recent_entries', 10)
        
        # Remove if already exists and add to front
        if directory in recent:
            recent.remove(directory)
        recent.insert(0, directory)
        
        # Keep only max_entries
        if 'general' not in self.config:
            self.config['general'] = {}
        self.config['general']['recent_directories'] = recent[:max_entries]
        self.save_config()  # Call without arguments
        self.logger.info(f'Added recent directory: {directory}')
    
    def get_recent_directories(self) -> list:
        """Get list of recent directories."""
        recent_directories = self.config.get('general', {}).get('recent_directories', [])
        self.logger.debug(
            f'Retrieved recent directories: {recent_directories}'
        )
        return recent_directories
    
    def reset_section(self, section: str) -> None:
        """Reset a section to default values."""
        defaults = {
            "general": {
                "theme": "light",
                "language": "en",
                "default_directory": "",
                "recent_directories": [],
                "max_recent_entries": 10,
                "logging_level": "INFO",
                "enable_debug_logging": False,
                "show_hidden": False
            },
            "duplicates": {
                "default_hash_algorithm": "sha256",
                "min_file_size": 1024,
                "skip_system_files": True
            },
            "secure_delete": {
                "default_passes": 3,
                "max_passes": 35
            },
            "compression": {
                "default_format": "zip",
                "default_compression_level": 6,
                "use_password_protection": False
            },
            "sync": {
                "default_mode": "two_way",
                "create_backups": True,
                "skip_newer_files": False
            },
            "catalog": {
                "recursive_by_default": True,
                "check_duplicates": False,
                "show_file_sizes": True,
                "show_dates": True,
                "default_sort_by": "name",
                "default_sort_order": "ascending"
            },
            "organize": {
                "recursive_by_default": False,
                "create_category_folders": True,
                "move_files": True
            }
        }
        
        if section in defaults:
            self.config[section] = defaults[section].copy()
            self.save_config()  # Call without arguments
            self.logger.info(f'Reset section {section} to default values')
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        # For test compatibility, set flat defaults
        self.config = {
            'theme': 'light',
            'language': 'en',
            'show_hidden': False,
            'profiles': {}
        }
        
        # Also add nested structure for existing functionality
        sections = [
            "general", "duplicates", "secure_delete", "compression",
            "sync", "catalog", "organize"
        ]
        for section in sections:
            self.reset_section(section)
        self.logger.info('Reset all sections to default values')

    def save_profile(
        self, profile_name: str, module_name: str, settings: dict
    ) -> None:
        """Save a profile for a specific module."""
        try:
            if 'profiles' not in self.config:
                self.config['profiles'] = {}
            
            if module_name not in self.config['profiles']:
                self.config['profiles'][module_name] = {}
                
            self.config['profiles'][module_name][profile_name] = settings
            self.save_config()  # Call without arguments
            self.logger.info(
                f'Saved profile {profile_name} for module {module_name}'
            )
        except Exception as e:
            self.logger.error(
                f'Error saving profile: {str(e)}',
                exc_info=True
            )

    def load_profile(
        self, profile_name: str, module_name: str
    ) -> Optional[dict]:
        """Load a profile for a specific module."""
        try:
            profiles = self.config.get('profiles', {})
            module_profiles = profiles.get(module_name, {})
            return module_profiles.get(profile_name)
        except Exception as e:
            self.logger.error(
                f'Error loading profile: {str(e)}',
                exc_info=True
            )
            return None

    def get_profiles(self, module_name: str) -> list:
        """Get list of available profiles for a module."""
        try:
            profiles = self.config.get('profiles', {})
            module_profiles = profiles.get(module_name, {})
            return list(module_profiles.keys())
        except Exception as e:
            self.logger.error(
                f'Error getting profiles: {str(e)}',
                exc_info=True
            )
            return []

    def delete_profile(self, profile_name: str, module_name: str) -> bool:
        """Delete a profile for a specific module."""
        try:
            profiles = self.config.get('profiles', {})
            if (module_name in profiles and
                    profile_name in profiles[module_name]):
                del self.config['profiles'][module_name][profile_name]
                self.save_config()  # Call without arguments
                self.logger.info(
                    f'Deleted profile {profile_name} from {module_name}'
                )
                return True
            return False
        except Exception as e:
            self.logger.error(
                f'Error deleting profile: {str(e)}',
                exc_info=True
            )
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration dictionary."""
        # For test compatibility, return a flat config with expected structure
        if not self.config:
            return {
                'theme': 'light',
                'language': 'en',
                'show_hidden': False
            }
        
        # Extract flat config for tests that expect this format
        flat_config = {}
        
        # Map from nested structure to flat for tests
        if 'general' in self.config:
            general = self.config['general']
            flat_config['theme'] = general.get('theme', 'light')
            flat_config['language'] = general.get('language', 'en')
            flat_config['show_hidden'] = general.get('show_hidden', False)
        else:
            # Add defaults
            flat_config.update({
                'theme': 'light',
                'language': 'en',
                'show_hidden': False
            })
            
        # If there are top-level keys, include them as well
        for key, value in self.config.items():
            if not isinstance(value, dict):
                flat_config[key] = value
        
        return flat_config
    
    def update_config(self, key: str, value: Any) -> None:
        """Update a single configuration value."""
        self.config[key] = value
        self.save_config()
    
    def update_multiple(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(updates)
        self.save_config()
    
    def create_backup(self) -> str:
        """Create a backup of the current configuration file.
        
        Returns:
            Path to the backup file.
        """
        import datetime
        
        # Ensure config_path is a Path object
        config_path = Path(self.config_path) if isinstance(self.config_path, str) else self.config_path
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f'{config_path.stem}_backup_{timestamp}.json'
        backup_path = config_path.parent / backup_name
        
        if config_path.exists():
            shutil.copy2(config_path, backup_path)
        
        return str(backup_path)
    
    def restore_from_backup(self, backup_file: str) -> None:
        """Restore configuration from a backup file."""
        backup_path = Path(backup_file)
        config_path = Path(self.config_path) if isinstance(self.config_path, str) else self.config_path
        
        if backup_path.exists():
            shutil.copy2(backup_path, config_path)
            self.load_config()
