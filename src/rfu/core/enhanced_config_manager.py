"""
Enhanced Configuration Manager with SQLite Database Support

This module extends the existing configuration manager to use SQLite
for persistent storage while maintaining backward compatibility.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union
from threading import Lock

# Import the database manager
try:
    from .database_manager import get_database_manager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class EnhancedConfigManager:
    """Enhanced configuration manager with database backend."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EnhancedConfigManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the enhanced configuration manager."""
        if not self._initialized:
            self._setup_config()
            self._initialized = True
    
    def _setup_config(self):
        """Setup configuration management."""
        # Initialize database manager if available
        self.use_database = DATABASE_AVAILABLE
        if self.use_database:
            try:
                self.db_manager = get_database_manager()
                self.logger = logging.getLogger('RFU.EnhancedConfigManager')
                self.logger.info("Enhanced ConfigManager with database support initialized")
            except Exception as e:
                self.logger = logging.getLogger('RFU.EnhancedConfigManager')
                self.logger.error(f"Failed to initialize database: {e}")
                self.use_database = False
        
        # Fallback to file-based configuration
        if not self.use_database:
            self.config_dir = Path('config')
            self.config_dir.mkdir(exist_ok=True)
            self.config_file = self.config_dir / 'rfu_config.json'
            self.config: Dict[str, Any] = {}
            self.logger = logging.getLogger('RFU.EnhancedConfigManager')
            self._load_file_config()
            self.logger.info("Enhanced ConfigManager with file support initialized")
        
        # Migration flag
        self._migrated_to_db = False
        
        # If database is available but we have file config, migrate
        if self.use_database and not self._migrated_to_db:
            self._check_and_migrate_from_file_to_database()
    
    def _check_and_migrate_from_file_to_database(self):
        """Check if migration is needed and perform it safely."""
        try:
            # Check if already migrated
            existing_migration = self.db_manager.execute_query(
                "SELECT value FROM app_settings WHERE section = ? AND key = ?",
                ('system', 'migrated_from_file')
            )
            
            if existing_migration and existing_migration[0].get('value') == 'true':
                self._migrated_to_db = True
                self.logger.info("Configuration already migrated to database")
                return
            
            # Check if file exists and has content to migrate
            if not self.config_file.exists():
                self.logger.info("No file configuration to migrate")
                return
                
            # Perform migration
            self._migrate_from_file_to_database()
            
        except Exception as e:
            self.logger.error(f"Failed to check migration status: {e}")
            # Continue with file-based config as fallback
            self.use_database = False
    
    def _load_file_config(self):
        """Load configuration from JSON file (fallback)."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.config = {}
                self._ensure_default_sections()
                self.save_config()
        except Exception as e:
            self.logger.error(f"Failed to load file configuration: {e}")
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
            'database': {
                'enable_database_logging': True,
                'log_retention_days': 90,
                'backup_retention_days': 30,
                'auto_backup': True,
                'vacuum_on_startup': False
            },
            'tools': {
                'default_directory': str(Path.home()),
                'remember_last_directory': True,
                'show_hidden_files': False,
                'confirm_destructive_operations': True,
                'auto_refresh_file_lists': True,
                'track_file_history': True
            }
        }
        
        if self.use_database:
            # Store defaults in database
            for section, section_defaults in defaults.items():
                for key, default_value in section_defaults.items():
                    existing = self.get_setting(section, key)
                    if existing is None:
                        self.set_setting(section, key, default_value)
        else:
            # Store defaults in file
            for section, section_defaults in defaults.items():
                if section not in self.config:
                    self.config[section] = {}
                
                for key, default_value in section_defaults.items():
                    if key not in self.config[section]:
                        self.config[section][key] = default_value
    
    def _migrate_from_file_to_database(self):
        """Migrate configuration from file to database with proper validation."""
        try:
            if not self.config_file.exists():
                self.logger.warning("No config file found for migration")
                return
                
            # Create backup before migration
            backup_path = self.config_file.with_suffix('.json.pre_migration_backup')
            shutil.copy2(self.config_file, backup_path)
            self.logger.info(f"Created migration backup: {backup_path}")
            
            # Load and validate file config
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            if not isinstance(file_config, dict):
                raise ValueError("Invalid config file format")
            
            # Migrate each setting to database
            migration_count = 0
            for section, settings in file_config.items():
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        try:
                            self._store_setting_in_database(section, key, value)
                            migration_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to migrate {section}.{key}: {e}")
            
            # Mark migration as complete
            migration_query = """
                INSERT OR REPLACE INTO app_settings 
                (section, key, value, value_type) 
                VALUES (?, ?, ?, ?)
            """
            self.db_manager.execute_update(
                migration_query,
                ('system', 'migrated_from_file', 'true', 'boolean')
            )
            
            # Archive old config file
            archive_path = self.config_file.with_suffix('.json.migrated')
            self.config_file.rename(archive_path)
            
            self._migrated_to_db = True
            self.logger.info(f"Successfully migrated {migration_count} settings "
                           f"from file to database")
            
        except Exception as e:
            self.logger.error(f"Failed to migrate configuration: {e}")
            # Restore backup if migration failed
            backup_path = self.config_file.with_suffix('.json.pre_migration_backup')
            if backup_path.exists() and not self.config_file.exists():
                backup_path.rename(self.config_file)
                self.logger.info("Restored config file from backup")
            raise
    
    def _determine_value_type(self, value: Any) -> str:
        """Determine the type of a configuration value."""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, (dict, list)):
            return 'json'
        else:
            return 'string'
    
    def _convert_value_for_storage(self, value: Any) -> str:
        """Convert a value to string for database storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        else:
            return str(value)
    
    def _convert_value_from_storage(self, value: str, value_type: str) -> Any:
        """Convert a value from database storage to its proper type."""
        try:
            if value_type == 'boolean':
                return value.lower() in ('true', '1', 'yes')
            elif value_type == 'integer':
                return int(value)
            elif value_type == 'float':
                return float(value)
            elif value_type == 'json':
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return value
    
    def _store_setting_in_database(self, section: str, key: str, value: Any):
        """Store a setting in the database."""
        value_type = self._determine_value_type(value)
        value_str = self._convert_value_for_storage(value)
        
        self.db_manager.execute_update(
            """INSERT OR REPLACE INTO app_settings 
               (section, key, value, value_type) VALUES (?, ?, ?, ?)""",
            (section, key, value_str, value_type)
        )
    
    def get_setting(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get a configuration setting."""
        try:
            if self.use_database:
                if key is None:
                    # Get entire section
                    query = "SELECT key, value, value_type FROM app_settings WHERE section = ?"
                    results = self.db_manager.execute_query(query, (section,))
                    section_data = {}
                    for row in results:
                        section_data[row['key']] = self._convert_value_from_storage(
                            row['value'], row['value_type']
                        )
                    return section_data if section_data else default
                else:
                    # Get specific setting
                    query = "SELECT value, value_type FROM app_settings WHERE section = ? AND key = ?"
                    results = self.db_manager.execute_query(query, (section, key))
                    if results:
                        return self._convert_value_from_storage(
                            results[0]['value'], results[0]['value_type']
                        )
                    return default
            else:
                # Fallback to file-based config
                if section not in self.config:
                    return default
                
                if key is None:
                    return self.config[section]
                
                return self.config[section].get(key, default)
                
        except Exception as e:
            self.logger.error(f"Error getting setting {section}.{key}: {e}")
            return default
    
    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """Set a configuration setting with recursion protection."""
        try:
            if self.use_database:
                self._store_setting_in_database(section, key, value)
                self.logger.debug(f"Set database setting {section}.{key} = {value}")
                return True
            else:
                # Fallback to file-based config
                if section not in self.config:
                    self.config[section] = {}
                
                self.config[section][key] = value
                
                # Auto-save if enabled - prevent recursion
                # Don't call get_setting here to avoid infinite recursion
                auto_save = True  # Default value
                if ('general' in self.config and
                        'auto_save_config' in self.config['general']):
                    auto_save = self.config['general']['auto_save_config']
                
                if auto_save:
                    self.save_config()
                
                msg = f"Set file setting {section}.{key} = {value}"
                self.logger.debug(msg)
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting {section}.{key}: {e}")
            return False
    
    def remove_setting(self, section: str, key: str) -> bool:
        """Remove a configuration setting."""
        try:
            if self.use_database:
                affected = self.db_manager.execute_update(
                    "DELETE FROM app_settings WHERE section = ? AND key = ?",
                    (section, key)
                )
                self.logger.info(f"Removed database setting {section}.{key}")
                return affected > 0
            else:
                # Fallback to file-based config
                if section in self.config and key in self.config[section]:
                    del self.config[section][key]
                    
                    # Auto-save if enabled
                    if self.get_setting('general', 'auto_save_config', True):
                        self.save_config()
                    
                    self.logger.info(f"Removed file setting {section}.{key}")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing {section}.{key}: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self.get_setting(section, None, {})
    
    def save_config(self) -> bool:
        """Save configuration (only needed for file-based fallback)."""
        if not self.use_database:
            try:
                self.config_dir.mkdir(exist_ok=True)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                msg = f"File configuration saved to {self.config_file}"
                self.logger.debug(msg)
                return True
            except Exception as e:
                self.logger.error(f"Failed to save file configuration: {e}")
                return False
        return True  # Database saves automatically
    
    def export_config(self, export_path: Union[str, Path]) -> bool:
        """Export configuration to a file."""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.use_database:
                # Export from database
                query = ("SELECT section, key, value, value_type "
                         "FROM app_settings ORDER BY section, key")
                results = self.db_manager.execute_query(query)
                
                config_data = {}
                for row in results:
                    section = row['section']
                    key = row['key']
                    value = self._convert_value_from_storage(
                        row['value'], row['value_type'])
                    
                    if section not in config_data:
                        config_data[section] = {}
                    config_data[section][key] = value
            else:
                # Export from file
                config_data = self.config
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to {export_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about the configuration system."""
        info = {
            'backend': 'database' if self.use_database else 'file',
            'migrated_to_database': self._migrated_to_db
        }
        
        if self.use_database:
            db_info = self.db_manager.get_database_info()
            info.update({
                'database_file': db_info.get('database_file'),
                'database_size_mb': db_info.get('database_size_mb'),
                'total_settings': db_info.get('table_counts', {}).get('app_settings', 0)
            })
        else:
            info.update({
                'config_file': str(self.config_file),
                'file_exists': self.config_file.exists(),
                'total_settings': sum(
                    len(section) for section in self.config.values())
            })
        
        return info


# Global instance
_enhanced_config_manager = None


def get_enhanced_config_manager() -> EnhancedConfigManager:
    """Get the global EnhancedConfigManager instance."""
    global _enhanced_config_manager
    if _enhanced_config_manager is None:
        _enhanced_config_manager = EnhancedConfigManager()
    return _enhanced_config_manager
