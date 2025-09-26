"""
Theme Security Configuration Manager for RFU Hub

Provides centralized configuration management for all theme security:
- Encryption parameters and key management settings
- Backup policies and retention rules
- Access control rules and permissions
- Recovery strategies and corruption handling
- Audit logging configuration
"""

import logging
import json
import os
import sqlite3
from typing import Dict, Any, Optional, Union
from pathlib import Path
import datetime


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ThemeSecurityConfig:
    """
    Centralized configuration manager for theme security system.
    
    This class manages all configuration settings for encryption,
    access control, backups, recovery, and other security components.
    """
    
    def __init__(self, config_file: str = "config/theme_security.json",
                 database_path: str = "data/theme_security.db"):
        """
        Initialize the Theme Security Configuration Manager.
        
        Args:
            config_file: Path to the configuration file
            database_path: Path to the security database
        """
        self.logger = logging.getLogger('RFU.ThemeSecurityConfig')
        self.config_file = Path(config_file)
        self.database_path = database_path
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Default configuration values
        self.default_config = self._get_default_config()
        
        # Current configuration (loaded from file and database)
        self.config = {}
        
        # Load configuration
        self._load_configuration()
        
        self.logger.info("Theme Security Configuration Manager initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'encryption': {
                'algorithm': 'AES-256-GCM',
                'key_derivation': 'PBKDF2-SHA256',
                'key_iterations': 100000,
                'key_rotation_interval_days': 30,
                'require_encryption': True,
                'encryption_version': 1,
                'master_key_backup_enabled': True
            },
            'access_control': {
                'require_authentication': True,
                'max_failed_attempts': 3,
                'lockout_duration_seconds': 300,
                'session_timeout_seconds': 3600,
                'audit_logging_enabled': True,
                'rate_limit_enabled': True,
                'rate_limit_window_seconds': 60,
                'rate_limit_max_requests': 10,
                'ip_whitelisting_enabled': False,
                'geo_blocking_enabled': False
            },
            'backup': {
                'auto_backup_enabled': True,
                'backup_interval_hours': 24,
                'max_backups_per_theme': 10,
                'retention_days': 30,
                'compress_backups': True,
                'verify_backups': True,
                'backup_on_save': True,
                'backup_on_load': False,
                'cleanup_interval_hours': 168,
                'backup_encryption_enabled': True,
                'offsite_backup_enabled': False
            },
            'integrity': {
                'validation_enabled': True,
                'validation_algorithm': 'HMAC-SHA256',
                'corruption_detection_enabled': True,
                'auto_repair_enabled': True,
                'integrity_check_interval_hours': 24,
                'checksum_verification_enabled': True,
                'structural_validation_enabled': True,
                'content_validation_enabled': True
            },
            'recovery': {
                'auto_recovery_enabled': True,
                'corruption_threshold': 0.1,
                'max_recovery_attempts': 3,
                'recovery_timeout_seconds': 30,
                'prefer_recent_backups': True,
                'enable_repair_attempts': True,
                'fallback_to_default': True,
                'safe_mode_enabled': True,
                'recovery_strategies': [
                    'backup_restore', 'repair_attempt', 
                    'default_theme', 'safe_mode'
                ]
            },
            'logging': {
                'audit_log_enabled': True,
                'audit_retention_days': 365,
                'log_level': 'INFO',
                'log_sensitive_data': False,
                'log_to_file': True,
                'log_to_database': True,
                'log_rotation_enabled': True,
                'max_log_file_size_mb': 100
            },
            'performance': {
                'cache_enabled': True,
                'cache_size_mb': 50,
                'cache_ttl_seconds': 3600,
                'connection_pool_size': 10,
                'query_timeout_seconds': 30,
                'batch_size': 100,
                'index_optimization_enabled': True
            },
            'security': {
                'security_level': 'high',
                'paranoid_mode': False,
                'data_sanitization_enabled': True,
                'input_validation_strict': True,
                'output_encoding_enabled': True,
                'csrf_protection_enabled': True,
                'timing_attack_protection': True
            }
        }
    
    def _load_configuration(self) -> None:
        """Load configuration from file and database."""
        try:
            # Start with default configuration
            self.config = self.default_config.copy()
            
            # Load from file if it exists
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r') as f:
                        file_config = json.load(f)
                    
                    # Deep merge file configuration
                    self._deep_merge(self.config, file_config)
                    config_file = self.config_file
                    msg = f"Loaded configuration from {config_file}"
                    self.logger.info(msg)
                    
                except (json.JSONDecodeError, IOError) as e:
                    self.logger.warning(f"Failed to load config file: {e}")
            
            # Load from database if available
            try:
                db_config = self._load_from_database()
                if db_config:
                    self._deep_merge(self.config, db_config)
                    self.logger.debug("Loaded configuration from database")
            except Exception as e:
                msg = "Failed to load config from database"
                self.logger.warning(f"{msg}: {e}")
            
        except Exception as e:
            self.logger.error(f"Configuration loading failed: {e}")
            self.config = self.default_config.copy()
    
    def _load_from_database(self) -> Optional[Dict[str, Any]]:
        """Load configuration from database."""
        try:
            if not os.path.exists(self.database_path):
                return None
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Check if config table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='theme_security_config'
                """)
                
                if not cursor.fetchone():
                    return None
                
                # Load all configuration entries
                cursor.execute("""
                    SELECT config_key, config_value, config_type
                    FROM theme_security_config
                """)
                
                db_config = {}
                for row in cursor.fetchall():
                    key, value, config_type = row
                    
                    # Convert value based on type
                    if config_type == 'boolean':
                        value = value.lower() in ('true', '1', 'yes')
                    elif config_type == 'integer':
                        value = int(value)
                    elif config_type == 'json':
                        value = json.loads(value)
                    # string values remain as-is
                    
                    # Set nested configuration value
                    self._set_nested_value(db_config, key, value)
                
                return db_config
                
        except Exception as e:
            self.logger.error(f"Database config loading failed: {e}")
            return None
    
    def _deep_merge(self, base: Dict[str, Any],
                    overlay: Dict[str, Any]) -> None:
        """Deep merge overlay dictionary into base dictionary."""
        for key, value in overlay.items():
            if (key in base and isinstance(base[key], dict) and
                    isinstance(value, dict)):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _set_nested_value(self, config: Dict[str, Any],
                          key: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'encryption.algorithm')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = value[k]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, persist: bool = True) -> bool:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'encryption.algorithm')
            value: Value to set
            persist: Whether to persist to database
            
        Returns:
            True if value was set successfully
        """
        try:
            keys = key.split('.')
            current = self.config
            
            # Navigate to parent dictionary
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            
            # Persist to database if requested
            if persist:
                self._persist_to_database(key, value)
            
            self.logger.info(f"Set configuration: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set configuration {key}: {e}")
            return False
    
    def _persist_to_database(self, key: str, value: Any) -> None:
        """Persist configuration value to database."""
        try:
            if not os.path.exists(self.database_path):
                return
            
            # Determine value type and convert to string
            if isinstance(value, bool):
                config_type = 'boolean'
                config_value = 'true' if value else 'false'
            elif isinstance(value, int):
                config_type = 'integer'
                config_value = str(value)
            elif isinstance(value, (dict, list)):
                config_type = 'json'
                config_value = json.dumps(value)
            else:
                config_type = 'string'
                config_value = str(value)
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='theme_security_config'
                """)
                
                if not cursor.fetchone():
                    return  # Table doesn't exist yet
                
                # Insert or update configuration
                cursor.execute("""
                    INSERT OR REPLACE INTO theme_security_config
                    (config_key, config_value, config_type, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, config_value, config_type))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to persist config to database: {e}")
    
    def save_to_file(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if configuration was saved successfully
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def reload(self) -> bool:
        """
        Reload configuration from file and database.
        
        Returns:
            True if configuration was reloaded successfully
        """
        try:
            self._load_configuration()
            self.logger.info("Configuration reloaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration for completeness and correctness.
        
        Returns:
            Dictionary with validation results
        """
        try:
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # Check required sections exist
            required_sections = ['encryption', 'access_control', 'backup', 'integrity', 'recovery']
            for section in required_sections:
                if section not in self.config:
                    validation_results['errors'].append(f"Missing required section: {section}")
                    validation_results['valid'] = False
            
            # Validate encryption configuration
            encryption = self.config.get('encryption', {})
            if encryption.get('key_iterations', 0) < 10000:
                validation_results['warnings'].append("Key iterations below recommended minimum (10000)")
            
            # Validate access control configuration
            access_control = self.config.get('access_control', {})
            if access_control.get('max_failed_attempts', 0) < 1:
                validation_results['errors'].append("max_failed_attempts must be at least 1")
                validation_results['valid'] = False
            
            # Validate backup configuration
            backup = self.config.get('backup', {})
            if backup.get('retention_days', 0) < 1:
                validation_results['errors'].append("backup retention_days must be at least 1")
                validation_results['valid'] = False
            
            # Validate recovery configuration
            recovery = self.config.get('recovery', {})
            if not recovery.get('recovery_strategies'):
                validation_results['errors'].append("At least one recovery strategy must be defined")
                validation_results['valid'] = False
            
            return validation_results
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation failed: {e}"],
                'warnings': [],
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., 'encryption', 'backup')
            
        Returns:
            Dictionary with section configuration
        """
        return self.config.get(section, {})
    
    def update_section(self, section: str, config: Dict[str, Any], persist: bool = True) -> bool:
        """
        Update an entire configuration section.
        
        Args:
            section: Section name
            config: New configuration for the section
            persist: Whether to persist to database
            
        Returns:
            True if section was updated successfully
        """
        try:
            self.config[section] = config
            
            if persist:
                # Persist each key in the section
                for key, value in config.items():
                    full_key = f"{section}.{key}"
                    self._persist_to_database(full_key, value)
            
            self.logger.info(f"Updated configuration section: {section}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update section {section}: {e}")
            return False
    
    def reset_to_defaults(self, section: Optional[str] = None) -> bool:
        """
        Reset configuration to defaults.
        
        Args:
            section: Optional section to reset (resets all if None)
            
        Returns:
            True if reset was successful
        """
        try:
            if section:
                if section in self.default_config:
                    self.config[section] = self.default_config[section].copy()
                    self.logger.info(f"Reset section {section} to defaults")
                else:
                    self.logger.warning(f"Unknown section: {section}")
                    return False
            else:
                self.config = self.default_config.copy()
                self.logger.info("Reset all configuration to defaults")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def export_config(self, file_path: Optional[str] = None) -> str:
        """
        Export current configuration to JSON string or file.
        
        Args:
            file_path: Optional file path to save exported config
            
        Returns:
            JSON string representation of configuration
        """
        try:
            config_json = json.dumps(self.config, indent=2, sort_keys=True)
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(config_json)
                self.logger.info(f"Configuration exported to {file_path}")
            
            return config_json
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return "{}"
    
    def import_config(self, config_data: Union[str, Dict[str, Any]], 
                     merge: bool = True) -> bool:
        """
        Import configuration from JSON string or dictionary.
        
        Args:
            config_data: JSON string or dictionary with configuration
            merge: Whether to merge with existing config or replace
            
        Returns:
            True if import was successful
        """
        try:
            if isinstance(config_data, str):
                imported_config = json.loads(config_data)
            else:
                imported_config = config_data
            
            if merge:
                self._deep_merge(self.config, imported_config)
            else:
                self.config = imported_config
            
            self.logger.info("Configuration imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_security_profile(self) -> str:
        """
        Get current security profile based on configuration.
        
        Returns:
            Security profile name ('low', 'medium', 'high', 'paranoid')
        """
        try:
            # Calculate security score based on various settings
            score = 0
            
            # Encryption settings
            if self.get('encryption.require_encryption', False):
                score += 20
            if self.get('encryption.key_iterations', 0) >= 100000:
                score += 15
            
            # Access control settings
            if self.get('access_control.require_authentication', False):
                score += 20
            if self.get('access_control.max_failed_attempts', 10) <= 3:
                score += 10
            if self.get('access_control.audit_logging_enabled', False):
                score += 10
            
            # Backup settings
            if self.get('backup.auto_backup_enabled', False):
                score += 10
            if self.get('backup.verify_backups', False):
                score += 10
            
            # Recovery settings
            if self.get('recovery.auto_recovery_enabled', False):
                score += 5
            
            # Determine profile
            if score >= 80:
                return 'paranoid'
            elif score >= 60:
                return 'high'
            elif score >= 40:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            self.logger.error(f"Failed to calculate security profile: {e}")
            return 'unknown'