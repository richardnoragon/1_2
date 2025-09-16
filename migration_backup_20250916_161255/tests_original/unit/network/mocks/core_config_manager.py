"""
Core Config Manager Mock for Network Module Testing

This module provides a comprehensive mock implementation of core.config_manager
to enable real implementation testing of the Network Complex Module.

Priority: URGENT - Resolves 0% coverage crisis across 2,400+ lines
"""

from datetime import datetime
from typing import Any, Dict, Optional, Union


class MockConfigManager:
    """Mock ConfigManager for network module testing."""
    
    def __init__(self):
        """Initialize mock config manager with network-specific defaults."""
        self.config = {
            'network_connectivity': {
                'general': {
                    'default_timeout': 5000,
                    'max_concurrent_operations': 10,
                    'enable_logging': True,
                    'log_level': 'INFO',
                    'auto_save_results': True,
                    'results_retention_days': 30,
                    'enable_security_validation': True,
                    'enable_performance_monitoring': True
                },
                'wifi_analyzer': {
                    'scan_interval': 30,
                    'max_networks': 100,
                    'security_scan_enabled': True,
                    'channel_analysis_enabled': True,
                    'signal_strength_threshold': -70
                },
                'port_scanner': {
                    'default_scan_policy': 'normal',
                    'max_ports_per_scan': 1000,
                    'connection_timeout': 3000,
                    'enable_service_detection': True,
                    'enable_vulnerability_assessment': True,
                    'aggressive_scan_enabled': False
                },
                'security': {
                    'enable_cve_detection': True,
                    'vulnerability_db_path': '/tmp/network_vulns.db',
                    'security_level': 'high',
                    'blocked_targets': ['127.0.0.1', '::1'],
                    'max_scan_rate': 100
                }
            }
        }
        self._config_file_path = None
        self._last_saved = datetime.now()
    
    def get_setting(self, section: str, key: Optional[str] = None,
                    default: Any = None) -> Any:
        """
        Get configuration setting.
        
        Args:
            section: Configuration section name
            key: Setting key (can be nested with dots)
            default: Default value if setting not found
            
        Returns:
            Configuration value or default
        """
        try:
            # Get section
            if section not in self.config:
                return default
            
            section_data = self.config[section]
            
            # If no key specified, return entire section
            if key is None:
                return section_data
            
            # Handle nested keys (e.g., 'general.default_timeout')
            if '.' in key:
                keys = key.split('.')
                current = section_data
                for k in keys:
                    if isinstance(current, dict) and k in current:
                        current = current[k]
                    else:
                        return default
                return current
            
            # Simple key lookup
            return section_data.get(key, default)
            
        except Exception:
            return default
    
    def set_setting(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration setting.
        
        Args:
            section: Configuration section name
            key: Setting key (can be nested with dots)
            value: Value to set
        """
        try:
            # Create section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}
            
            # Handle nested keys
            if '.' in key:
                keys = key.split('.')
                current = self.config[section]
                
                # Navigate to parent of target key
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                # Set the final key
                current[keys[-1]] = value
            else:
                # Simple key setting
                section_value = self.config[section].get(key)
                if (isinstance(value, dict) and 
                        isinstance(section_value, dict)):
                    # Merge dictionaries
                    section_value.update(value)
                else:
                    self.config[section][key] = value
                    
        except Exception as e:
            print(f"Error setting config {section}.{key}: {e}")
    
    def save_config(self) -> bool:
        """
        Save configuration (mock implementation).
        
        Returns:
            True if save successful
        """
        try:
            self._last_saved = datetime.now()
            return True
        except Exception:
            return False
    
    def load_config(self) -> bool:
        """
        Load configuration (mock implementation).
        
        Returns:
            True if load successful
        """
        return True
    
    def get_profiles(self, utility_name: str) -> list:
        """
        Get configuration profiles for a utility.
        
        Args:
            utility_name: Name of the utility
            
        Returns:
            List of profile names
        """
        profiles_key = f"{utility_name}_profiles"
        profiles_data = self.config.get('profiles', {})
        return list(profiles_data.get(profiles_key, {}).keys())
    
    def save_profile(self, name: str, utility_name: str,
                     settings: Dict[str, Any]) -> bool:
        """
        Save a configuration profile.
        
        Args:
            name: Profile name
            utility_name: Utility name
            settings: Profile settings
            
        Returns:
            True if save successful
        """
        try:
            if 'profiles' not in self.config:
                self.config['profiles'] = {}
            
            profiles_key = f"{utility_name}_profiles"
            if profiles_key not in self.config['profiles']:
                self.config['profiles'][profiles_key] = {}
            
            self.config['profiles'][profiles_key][name] = settings
            return True
        except Exception:
            return False
    
    def load_profile(self, name: str,
                     utility_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a configuration profile.
        
        Args:
            name: Profile name
            utility_name: Utility name
            
        Returns:
            Profile settings or None
        """
        try:
            profiles_key = f"{utility_name}_profiles"
            profiles_data = self.config.get('profiles', {})
            utility_profiles = profiles_data.get(profiles_key, {})
            return utility_profiles.get(name)
        except Exception:
            return None
    
    def delete_profile(self, name: str, utility_name: str) -> bool:
        """
        Delete a configuration profile.
        
        Args:
            name: Profile name
            utility_name: Utility name
            
        Returns:
            True if delete successful
        """
        try:
            profiles_key = f"{utility_name}_profiles"
            profiles_data = self.config.get('profiles', {})
            utility_profiles = profiles_data.get(profiles_key, {})
            if utility_profiles.pop(name, None) is not None:
                return True
            return False
        except Exception:
            return False
    
    def update_config(self, section: str, settings: Dict[str, Any]) -> None:
        """
        Update multiple configuration settings.
        
        Args:
            section: Configuration section
            settings: Dictionary of settings to update
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(settings)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.__init__()


# Global instance for use in mocking
config_manager = MockConfigManager()


class ConfigManager(MockConfigManager):
    """Alias for MockConfigManager to match real interface."""
    pass