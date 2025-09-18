"""
Secure Delete Configuration Management Module

This module provides comprehensive configuration management for secure delete
operations with hub integration and persistent settings.

Migrated from: secure_delete.py configuration handling
Target: file_utilities_2 package integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SecureDeleteSettings:
    """Data class for secure delete settings."""
    default_passes: int = 3
    max_passes: int = 35
    chunk_size: int = 1024 * 1024  # 1MB
    enable_hub_integration: bool = True
    enable_progress_reporting: bool = True
    enable_resource_management: bool = True
    log_level: str = "INFO"
    auto_cleanup: bool = True
    confirm_deletion: bool = True
    show_detailed_progress: bool = True
    preserve_timestamps: bool = False
    secure_rename_passes: int = 3


class SecureDeleteConfig:
    """
    Configuration manager for secure delete operations.
    
    Provides persistent configuration storage, validation, and hub integration
    for secure delete settings and preferences.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory path
        """
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self.config_file = self.config_dir / "secure_delete_config.json"
        self.logger = logging.getLogger(__name__)
        
        # Default settings
        self.settings = SecureDeleteSettings()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing configuration
        self.load_config()
        
        self.logger.info(f"SecureDeleteConfig initialized with config dir: {self.config_dir}")
    
    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory."""
        if os.name == 'nt':  # Windows
            config_base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        else:  # Unix-like systems
            config_base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        
        return config_base / 'file_utilities_2' / 'secure_delete'
    
    def load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update settings with loaded data
                for key, value in config_data.get('settings', {}).items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)
                
                self.logger.info("Configuration loaded successfully")
                return True
            else:
                self.logger.info("No existing configuration found, using defaults")
                self.save_config()  # Save default configuration
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            config_data = {
                'metadata': {
                    'version': '1.0.0',
                    'created': datetime.now().isoformat(),
                    'description': 'Secure Delete Configuration'
                },
                'settings': asdict(self.settings)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value.
        
        Args:
            key: Setting key name
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a specific setting value.
        
        Args:
            key: Setting key name
            value: Value to set
            
        Returns:
            True if set successfully, False otherwise
        """
        try:
            if hasattr(self.settings, key):
                # Validate the value
                if self._validate_setting(key, value):
                    setattr(self.settings, key, value)
                    self.save_config()
                    self.logger.info(f"Setting updated: {key} = {value}")
                    return True
                else:
                    self.logger.error(f"Invalid value for setting {key}: {value}")
                    return False
            else:
                self.logger.error(f"Unknown setting key: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {e}")
            return False
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """
        Validate a setting value.
        
        Args:
            key: Setting key name
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if key == 'default_passes':
                return isinstance(value, int) and 1 <= value <= self.settings.max_passes
            elif key == 'max_passes':
                return isinstance(value, int) and 1 <= value <= 100
            elif key == 'chunk_size':
                return isinstance(value, int) and 1024 <= value <= 100 * 1024 * 1024  # 1KB to 100MB
            elif key == 'log_level':
                return value in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            elif key == 'secure_rename_passes':
                return isinstance(value, int) and 0 <= value <= 10
            elif key in ['enable_hub_integration', 'enable_progress_reporting', 
                        'enable_resource_management', 'auto_cleanup', 'confirm_deletion',
                        'show_detailed_progress', 'preserve_timestamps']:
                return isinstance(value, bool)
            else:
                return True  # Allow unknown settings for future compatibility
                
        except Exception:
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all current settings.
        
        Returns:
            Dictionary of all settings
        """
        return asdict(self.settings)
    
    def update_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """
        Update multiple settings at once.
        
        Args:
            settings_dict: Dictionary of settings to update
            
        Returns:
            True if all updates successful, False otherwise
        """
        try:
            # Validate all settings first
            for key, value in settings_dict.items():
                if hasattr(self.settings, key):
                    if not self._validate_setting(key, value):
                        self.logger.error(f"Invalid value for setting {key}: {value}")
                        return False
                else:
                    self.logger.warning(f"Unknown setting key: {key}")
            
            # Apply all settings
            for key, value in settings_dict.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            self.save_config()
            self.logger.info(f"Updated {len(settings_dict)} settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to default values.
        
        Returns:
            True if reset successful, False otherwise
        """
        try:
            self.settings = SecureDeleteSettings()
            self.save_config()
            self.logger.info("Settings reset to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset settings: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            export_data = {
                'metadata': {
                    'version': '1.0.0',
                    'exported': datetime.now().isoformat(),
                    'source': str(self.config_file),
                    'description': 'Exported Secure Delete Configuration'
                },
                'settings': asdict(self.settings)
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate and import settings
            settings_data = import_data.get('settings', {})
            if self.update_settings(settings_data):
                self.logger.info(f"Configuration imported from: {import_path}")
                return True
            else:
                self.logger.error("Failed to validate imported settings")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get configuration information and metadata.
        
        Returns:
            Dictionary containing configuration information
        """
        return {
            'config_dir': str(self.config_dir),
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists(),
            'settings_count': len(asdict(self.settings)),
            'last_modified': datetime.fromtimestamp(
                self.config_file.stat().st_mtime
            ).isoformat() if self.config_file.exists() else None
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate current configuration.
        
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate each setting
            for key, value in asdict(self.settings).items():
                if not self._validate_setting(key, value):
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Invalid value for {key}: {value}")
            
            # Check for logical inconsistencies
            if self.settings.default_passes > self.settings.max_passes:
                validation_results['valid'] = False
                validation_results['errors'].append(
                    "default_passes cannot be greater than max_passes"
                )
            
            # Add warnings for potentially problematic settings
            if self.settings.chunk_size > 50 * 1024 * 1024:  # 50MB
                validation_results['warnings'].append(
                    "Large chunk size may impact performance"
                )
            
            if self.settings.default_passes > 7:
                validation_results['warnings'].append(
                    "High default passes may significantly slow operations"
                )
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Validation error: {e}")
        
        return validation_results


# Global configuration instance
_config_instance: Optional[SecureDeleteConfig] = None


def get_config() -> SecureDeleteConfig:
    """
    Get the global configuration instance.
    
    Returns:
        SecureDeleteConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = SecureDeleteConfig()
    return _config_instance


def initialize_config(config_dir: Optional[str] = None) -> SecureDeleteConfig:
    """
    Initialize the global configuration instance.
    
    Args:
        config_dir: Custom configuration directory
        
    Returns:
        SecureDeleteConfig instance
    """
    global _config_instance
    _config_instance = SecureDeleteConfig(config_dir)
    return _config_instance