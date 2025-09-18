"""
Configuration management for Richard's File Utilities.

This module provides centralized configuration management with support for
multiple configuration sections, default values, and automatic persistence.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from threading import Lock
import logging


class ConfigManager:
    """Centralized configuration manager with singleton pattern."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration manager."""
        if not self._initialized:
            self._setup_config()
            self._initialized = True
    
    def _setup_config(self):
        """Setup configuration management."""
        # Configuration directory and file
        self.config_dir = Path('config')
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'rfu_config.json'
        
        # Initialize configuration dictionary
        self.config: Dict[str, Any] = {}
        
        # Setup logging
        self.logger = logging.getLogger('RFU.ConfigManager')
        
        # Load existing configuration or create defaults
        self._load_config()
        
        # Ensure default sections exist
        self._ensure_default_sections()
        
        # Save to ensure file exists with defaults
        self.save_config()
        
        self.logger.info("ConfigManager initialized successfully")
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(
                    f"Configuration loaded from {self.config_file}"
                )
            else:
                self.config = {}
                self.logger.info(
                    "No existing configuration found, using defaults"
                )
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.config = {}
    
    def _ensure_default_sections(self):
        """Ensure default configuration sections exist."""
        defaults = {
            'general': {
                'logging_level': 'INFO',
                'enable_debug_logging': False,
                'auto_save_config': True,
                'theme': 'light',
                'language': 'en',
                'check_for_updates': True
            },
            'gui': {
                'window_width': 900,
                'window_height': 700,
                'remember_window_position': True,
                'show_status_bar': True,
                'show_toolbar': True,
                'font_size': 12,
                'font_family': 'Segoe UI'
            },
            'logging': {
                'enable_file_logging': True,
                'enable_console_logging': True,
                'log_file_max_size_mb': 10,
                'log_file_backup_count': 5,
                'enable_tool_logging': True,
                'log_format': (
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            },
            'tools': {
                'default_directory': str(Path.home()),
                'remember_last_directory': True,
                'show_hidden_files': False,
                'confirm_destructive_operations': True,
                'auto_refresh_file_lists': True
            },
            'network_connectivity': {},
            'pdf_tools': {},
            'privacy_tools': {},
            'software_maintenance': {}
        }
        
        # Add missing sections and settings
        for section, section_defaults in defaults.items():
            if section not in self.config:
                self.config[section] = {}
            
            for key, default_value in section_defaults.items():
                if key not in self.config[section]:
                    self.config[section][key] = default_value
    
    def get_setting(self, section: str, key: Optional[str] = None,
                    default: Any = None) -> Any:
        """
        Get a configuration setting.
        
        Args:
            section: Configuration section name
            key: Setting key (if None, returns entire section)
            default: Default value if setting not found
            
        Returns:
            Configuration value or default
        """
        try:
            if section not in self.config:
                self.logger.warning(
                    f"Configuration section '{section}' not found"
                )
                return default
            
            if key is None:
                return self.config[section]
            
            if key not in self.config[section]:
                self.logger.debug(
                    f"Configuration key '{section}.{key}' not found, "
                    f"using default: {default}"
                )
                return default
            
            return self.config[section][key]
            
        except Exception as e:
            self.logger.error(f"Error getting setting {section}.{key}: {e}")
            return default
    
    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """
        Set a configuration setting.
        
        Args:
            section: Configuration section name
            key: Setting key
            value: Setting value
            
        Returns:
            bool: True if setting was saved successfully
        """
        try:
            # Ensure section exists
            if section not in self.config:
                self.config[section] = {}
            
            # Set the value
            self.config[section][key] = value
            
            # Auto-save if enabled
            if self.get_setting('general', 'auto_save_config', True):
                self.save_config()
            
            self.logger.debug(f"Set configuration {section}.{key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting {section}.{key}: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary with section settings
        """
        return self.config.get(section, {})
    
    def set_section(self, section: str, settings: Dict[str, Any]) -> bool:
        """
        Set an entire configuration section.
        
        Args:
            section: Section name
            settings: Dictionary with section settings
            
        Returns:
            bool: True if section was saved successfully
        """
        try:
            self.config[section] = settings.copy()
            
            # Auto-save if enabled
            if self.get_setting('general', 'auto_save_config', True):
                self.save_config()
            
            self.logger.info(f"Set configuration section '{section}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting section {section}: {e}")
            return False
    
    def remove_setting(self, section: str, key: str) -> bool:
        """
        Remove a configuration setting.
        
        Args:
            section: Configuration section name
            key: Setting key
            
        Returns:
            bool: True if setting was removed successfully
        """
        try:
            if section in self.config and key in self.config[section]:
                del self.config[section][key]
                
                # Auto-save if enabled
                if self.get_setting('general', 'auto_save_config', True):
                    self.save_config()
                
                self.logger.info(f"Removed configuration {section}.{key}")
                return True
            else:
                self.logger.warning(
                    f"Configuration {section}.{key} not found for removal"
                )
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing {section}.{key}: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if configuration was saved successfully
        """
        try:
            # Ensure directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Write configuration file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            bool: True if configuration was loaded successfully
        """
        try:
            self._load_config()
            self._ensure_default_sections()
            self.logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            bool: True if reset was successful
        """
        try:
            self.config = {}
            self._ensure_default_sections()
            self.save_config()
            self.logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all configuration settings.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def export_config(self, export_path: Union[str, Path]) -> bool:
        """
        Export configuration to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            bool: True if export was successful
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to {export_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: Union[str, Path]) -> bool:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            bool: True if import was successful
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                self.logger.error(f"Import file not found: {import_file}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported configuration
            if not isinstance(imported_config, dict):
                self.logger.error("Invalid configuration format")
                return False
            
            # Merge with current configuration
            self.config.update(imported_config)
            self._ensure_default_sections()
            self.save_config()
            
            self.logger.info(f"Configuration imported from {import_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the configuration.
        
        Returns:
            Dictionary with configuration information
        """
        return {
            'config_file': str(self.config_file),
            'config_dir': str(self.config_dir),
            'sections': list(self.config.keys()),
            'total_settings': sum(
                len(section) for section in self.config.values()
            ),
            'file_exists': self.config_file.exists(),
            'file_size_bytes': (
                self.config_file.stat().st_size 
                if self.config_file.exists() else 0
            )
        }


# Global instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager