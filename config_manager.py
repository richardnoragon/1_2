import json
from pathlib import Path
from typing import Any, Dict, Optional
import logging


class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the configuration manager."""
        self.config_path = Path(__file__).parent / 'configuration.json'
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger('RFU.ConfigManager')
        self.logger.info('Initializing configuration manager')
        self.load_config()
        
        # Initialize profiles section if not exists
        if 'profiles' not in self.config:
            self.config['profiles'] = {}
            self.save_config()
    
    def load_config(self) -> None:
        """Load the configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
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
    
    def save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info('Configuration saved successfully')
        except Exception as e:
            self.logger.error(
                f'Error saving configuration: {str(e)}',
                exc_info=True
            )
    
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
            self.save_config()
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
            
        recent = self.config['general']['recent_directories']
        max_entries = self.config['general']['max_recent_entries']
        
        # Remove if already exists and add to front
        if directory in recent:
            recent.remove(directory)
        recent.insert(0, directory)
        
        # Keep only max_entries
        self.config['general']['recent_directories'] = recent[:max_entries]
        self.save_config()
        self.logger.info(f'Added recent directory: {directory}')
    
    def get_recent_directories(self) -> list:
        """Get list of recent directories."""
        recent_directories = self.config['general']['recent_directories']
        self.logger.debug(
            f'Retrieved recent directories: {recent_directories}'
        )
        return recent_directories
    
    def reset_section(self, section: str) -> None:
        """Reset a section to default values."""
        defaults = {
            "general": {
                "theme": "light",
                "default_directory": "",
                "recent_directories": [],
                "max_recent_entries": 10,
                "logging_level": "INFO",
                "enable_debug_logging": False
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
            self.save_config()
            self.logger.info(f'Reset section {section} to default values')
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
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
        """Save a profile for a specific module.
        
        Args:
            profile_name: Name of the profile
            module_name: Name of the module (e.g., 'rename', 'sync', 'catalog')
            settings: Dictionary containing the profile settings
        """
        try:
            if 'profiles' not in self.config:
                self.config['profiles'] = {}
            
            if module_name not in self.config['profiles']:
                self.config['profiles'][module_name] = {}
                
            self.config['profiles'][module_name][profile_name] = settings
            self.save_config()
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
        """Load a profile for a specific module.
        
        Args:
            profile_name: Name of the profile to load
            module_name: Name of the module
            
        Returns:
            Dictionary containing the profile settings or None if not found
        """
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
        """Get list of available profiles for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            List of profile names
        """
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
        """Delete a profile for a specific module.
        
        Args:
            profile_name: Name of the profile to delete
            module_name: Name of the module
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profiles = self.config.get('profiles', {})
            if (module_name in profiles and
                    profile_name in profiles[module_name]):
                del self.config['profiles'][module_name][profile_name]
                self.save_config()
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


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from settings_dialog import SettingsDialog
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())