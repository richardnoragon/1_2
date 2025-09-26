"""
Enterprise-grade configuration management system for network connectivity modules.
Implements the ConfigManager architecture as specified in the Critical Test Execution
Blockers Resolution Strategy.
"""

import hashlib
import json
import logging
import shutil
import threading
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class ValidationError:
    """Configuration validation error."""
    path: str
    message: str
    value: Any
    rule: str


@dataclass
class BackupInfo:
    """Configuration backup information."""
    backup_id: str
    name: str
    created_at: datetime
    file_path: str
    checksum: str
    size_bytes: int


class ConfigValidator:
    """Advanced configuration validation engine."""
    
    def __init__(self):
        self.logger = logging.getLogger('NetworkConfig.Validator')
        self.schemas: Dict[str, Dict] = {}
        self.validation_rules: Dict[str, List[Callable]] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self._setup_default_schemas()
    
    def _setup_default_schemas(self):
        """Setup default validation schemas for network modules."""
        # Network connectivity general schema
        self.schemas['network_connectivity.general'] = {
            'default_timeout': {'type': int, 'min': 1000, 'max': 60000},
            'max_concurrent_operations': {'type': int, 'min': 1, 'max': 100},
            'log_level': {'type': str, 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']},
            'enable_notifications': {'type': bool},
            'auto_start_services': {'type': bool}
        }
        
        # WiFi Analyzer schema
        self.schemas['network_connectivity.wifi_analyzer'] = {
            'scan_interval': {'type': int, 'min': 5000, 'max': 300000},
            'signal_threshold': {'type': int, 'min': -100, 'max': -30},
            'security_assessment': {'type': bool},
            'oui_database_update': {'type': bool}
        }
        
        # Port Scanner schema
        self.schemas['network_connectivity.port_scanner'] = {
            'scan_timeout': {'type': int, 'min': 100, 'max': 30000},
            'max_threads': {'type': int, 'min': 1, 'max': 1000},
            'service_detection': {'type': bool},
            'vulnerability_assessment': {'type': bool}
        }
        
        # Bandwidth Monitor schema
        self.schemas['network_connectivity.bandwidth_monitor'] = {
            'monitoring_interval': {'type': int, 'min': 100, 'max': 10000},
            'alert_threshold_mbps': {'type': (int, float), 'min': 0.1},
            'data_retention_days': {'type': int, 'min': 1, 'max': 365}
        }
        
        # LAN File Transfer schema
        self.schemas['network_connectivity.lan_file_transfer'] = {
            'default_port': {'type': int, 'min': 1024, 'max': 65535},
            'encryption_enabled': {'type': bool},
            'compression_enabled': {'type': bool},
            'max_file_size_mb': {'type': int, 'min': 1, 'max': 10240}
        }
    
    def register_schema(self, module: str, schema: Dict) -> None:
        """Register validation schema for a module."""
        self.schemas[module] = schema
        self.logger.debug(f"Registered schema for module: {module}")
    
    def add_validation_rule(self, path: str, rule: Callable) -> None:
        """Add custom validation rule for a configuration path."""
        if path not in self.validation_rules:
            self.validation_rules[path] = []
        self.validation_rules[path].append(rule)
        self.logger.debug(f"Added validation rule for path: {path}")
    
    def validate_full_config(self, config: Dict) -> List[ValidationError]:
        """Validate complete configuration against all schemas."""
        errors = []
        
        for module_path, schema in self.schemas.items():
            try:
                module_config = self._get_nested_value(config, module_path)
                if module_config is not None:
                    module_errors = self._validate_against_schema(
                        module_config, schema, module_path
                    )
                    errors.extend(module_errors)
            except KeyError:
                # Module config doesn't exist, which is okay for optional modules
                continue
            except Exception as e:
                errors.append(ValidationError(
                    path=module_path,
                    message=f"Schema validation error: {e}",
                    value=None,
                    rule="schema_validation"
                ))
        
        # Apply custom validation rules
        for path, rules in self.validation_rules.items():
            try:
                value = self._get_nested_value(config, path)
                if value is not None:
                    for rule in rules:
                        try:
                            if not rule(value):
                                errors.append(ValidationError(
                                    path=path,
                                    message="Custom validation rule failed",
                                    value=value,
                                    rule="custom_rule"
                                ))
                        except Exception as e:
                            errors.append(ValidationError(
                                path=path,
                                message=f"Custom rule error: {e}",
                                value=value,
                                rule="custom_rule_error"
                            ))
            except KeyError:
                continue
        
        return errors
    
    def validate_setting(self, module: str, key: str, value: Any) -> List[ValidationError]:
        """Validate a single setting value."""
        errors = []
        
        # Find matching schema
        schema = None
        full_path = f"{module}.{key}" if key else module
        
        for schema_path, schema_def in self.schemas.items():
            if schema_path == full_path:
                schema = schema_def
                break
            elif schema_path.startswith(module) and key in schema_def:
                schema = {key: schema_def[key]}
                break
        
        if schema:
            validation_errors = self._validate_against_schema(
                {key: value} if key else value, schema, full_path
            )
            errors.extend(validation_errors)
        
        return errors
    
    def _validate_against_schema(self, data: Dict, schema: Dict, base_path: str) -> List[ValidationError]:
        """Validate data against a schema definition."""
        errors = []
        
        for field, constraints in schema.items():
            if field in data:
                value = data[field]
                field_path = f"{base_path}.{field}"
                
                # Type validation
                if 'type' in constraints:
                    expected_type = constraints['type']
                    if not isinstance(value, expected_type):
                        errors.append(ValidationError(
                            path=field_path,
                            message=f"Expected type {expected_type.__name__}, got {type(value).__name__}",
                            value=value,
                            rule="type_validation"
                        ))
                        continue
                
                # Range validation for numeric types
                if isinstance(value, (int, float)):
                    if 'min' in constraints and value < constraints['min']:
                        errors.append(ValidationError(
                            path=field_path,
                            message=f"Value {value} is below minimum {constraints['min']}",
                            value=value,
                            rule="min_value"
                        ))
                    
                    if 'max' in constraints and value > constraints['max']:
                        errors.append(ValidationError(
                            path=field_path,
                            message=f"Value {value} is above maximum {constraints['max']}",
                            value=value,
                            rule="max_value"
                        ))
                
                # Choice validation for strings
                if 'choices' in constraints and value not in constraints['choices']:
                    errors.append(ValidationError(
                        path=field_path,
                        message=f"Value '{value}' not in allowed choices: {constraints['choices']}",
                        value=value,
                        rule="choices_validation"
                    ))
        
        return errors
    
    def _get_nested_value(self, config: Dict, path: str) -> Any:
        """Get value from nested configuration using dot notation."""
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError(f"Path {path} not found")
        
        return value


class ConfigPersistence:
    """Multi-format configuration persistence with backup support."""
    
    SUPPORTED_FORMATS = {
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml'
    }
    
    def __init__(self, config_path: Union[str, Path]):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger('NetworkConfig.Persistence')
        self.backup_dir = self.config_path.parent / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
    
    def save_configuration(self, config: Dict, format_type: str = 'json') -> bool:
        """Save configuration to file in specified format."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == 'json':
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
            elif format_type in ('yaml', 'yml'):
                try:
                    import yaml
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                except ImportError:
                    self.logger.warning("PyYAML not available, falling back to JSON")
                    return self.save_configuration(config, 'json')
            elif format_type == 'toml':
                try:
                    import toml
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        toml.dump(config, f)
                except ImportError:
                    self.logger.warning("toml not available, falling back to JSON")
                    return self.save_configuration(config, 'json')
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_configuration(self, validate: bool = True) -> Dict:
        """Load configuration from file."""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                return {}
            
            file_ext = self.config_path.suffix.lower()
            format_type = self.SUPPORTED_FORMATS.get(file_ext, 'json')
            
            if format_type == 'json':
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif format_type == 'yaml':
                try:
                    import yaml
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                except ImportError:
                    self.logger.error("PyYAML not available for YAML configuration")
                    return {}
            elif format_type == 'toml':
                try:
                    import toml
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        config = toml.load(f)
                except ImportError:
                    self.logger.error("toml not available for TOML configuration")
                    return {}
            else:
                self.logger.error(f"Unsupported configuration format: {file_ext}")
                return {}
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return config or {}
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return {}
    
    def create_backup(self, backup_name: str) -> str:
        """Create a backup of the current configuration."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError("No configuration file to backup")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = hashlib.md5(f"{backup_name}_{timestamp}".encode()).hexdigest()[:8]
            backup_filename = f"{self.config_path.stem}_backup_{backup_id}_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Copy current config to backup
            shutil.copy2(self.config_path, backup_path)
            
            self.logger.info(f"Configuration backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available configuration backups."""
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("*_backup_*.json"):
                try:
                    stat = backup_file.stat()
                    
                    # Calculate checksum
                    checksum = hashlib.sha256(backup_file.read_bytes()).hexdigest()
                    
                    # Extract backup ID from filename
                    parts = backup_file.stem.split('_backup_')
                    backup_id = parts[1].split('_')[0] if len(parts) > 1 else "unknown"
                    
                    backup_info = BackupInfo(
                        backup_id=backup_id,
                        name=backup_file.stem,
                        created_at=datetime.fromtimestamp(stat.st_mtime),
                        file_path=str(backup_file),
                        checksum=checksum,
                        size_bytes=stat.st_size
                    )
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process backup file {backup_file}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
        
        return sorted(backups, key=lambda x: x.created_at, reverse=True)
    
    def restore_backup(self, backup_id: str) -> bool:
        """Restore configuration from a backup."""
        try:
            backups = self.list_backups()
            backup_to_restore = None
            
            for backup in backups:
                if backup.backup_id == backup_id:
                    backup_to_restore = backup
                    break
            
            if not backup_to_restore:
                raise ValueError(f"Backup with ID {backup_id} not found")
            
            backup_path = Path(backup_to_restore.file_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Verify backup integrity
            current_checksum = hashlib.sha256(backup_path.read_bytes()).hexdigest()
            if current_checksum != backup_to_restore.checksum:
                raise ValueError("Backup file checksum mismatch - file may be corrupted")
            
            # Create backup of current config before restore
            if self.config_path.exists():
                self.create_backup("pre_restore_backup")
            
            # Restore from backup
            shutil.copy2(backup_path, self.config_path)
            
            self.logger.info(f"Configuration restored from backup: {backup_to_restore.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False


class DependencyInjector:
    """Advanced dependency injection framework for modular architecture."""
    
    def __init__(self):
        self.logger = logging.getLogger('NetworkConfig.DependencyInjector')
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._initializers: List[Callable] = []
        self._shutdown_handlers: List[Callable] = []
        self._lock = threading.RLock()
    
    def register_service(self, name: str, service_class: type, singleton: bool = True) -> None:
        """Register a service class for dependency injection."""
        with self._lock:
            if singleton:
                self._services[name] = service_class
            else:
                self._factories[name] = service_class
            
            self.logger.debug(f"Registered service: {name} (singleton={singleton})")
    
    def register_factory(self, name: str, factory: Callable) -> None:
        """Register a factory function for service creation."""
        with self._lock:
            self._factories[name] = factory
            self.logger.debug(f"Registered factory: {name}")
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance."""
        with self._lock:
            self._singletons[name] = instance
            self.logger.debug(f"Registered singleton instance: {name}")
    
    def get_service(self, name: str) -> Any:
        """Get service instance by name."""
        with self._lock:
            # Check singletons first
            if name in self._singletons:
                return self._singletons[name]
            
            # Check singleton services
            if name in self._services:
                if name not in self._singletons:
                    service_class = self._services[name]
                    instance = service_class()
                    self._singletons[name] = instance
                return self._singletons[name]
            
            # Check factories
            if name in self._factories:
                factory = self._factories[name]
                return factory()
            
            raise KeyError(f"Service not found: {name}")
    
    def add_initializer(self, initializer: Callable) -> None:
        """Add initialization function to be called during startup."""
        self._initializers.append(initializer)
        self.logger.debug("Added initializer function")
    
    def add_shutdown_handler(self, handler: Callable) -> None:
        """Add shutdown handler to be called during cleanup."""
        self._shutdown_handlers.append(handler)
        self.logger.debug("Added shutdown handler")
    
    def initialize_all(self) -> None:
        """Initialize all registered services and run initializers."""
        with self._lock:
            try:
                # Run initializers
                for initializer in self._initializers:
                    try:
                        initializer()
                        self.logger.debug("Initializer executed successfully")
                    except Exception as e:
                        self.logger.error(f"Initializer failed: {e}")
                
                # Initialize singleton services
                for name in self._services:
                    try:
                        self.get_service(name)
                        self.logger.debug(f"Service initialized: {name}")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize service {name}: {e}")
                
                self.logger.info("Dependency injection initialization completed")
                
            except Exception as e:
                self.logger.error(f"Dependency injection initialization failed: {e}")
                raise
    
    def shutdown_all(self) -> None:
        """Shutdown all services and run shutdown handlers."""
        with self._lock:
            # Run shutdown handlers
            for handler in self._shutdown_handlers:
                try:
                    handler()
                    self.logger.debug("Shutdown handler executed successfully")
                except Exception as e:
                    self.logger.error(f"Shutdown handler failed: {e}")
            
            # Clear singletons
            for name, instance in self._singletons.items():
                try:
                    if hasattr(instance, 'shutdown'):
                        instance.shutdown()
                except Exception as e:
                    self.logger.error(f"Failed to shutdown service {name}: {e}")
            
            self._singletons.clear()
            self.logger.info("Dependency injection shutdown completed")


class ConfigManager:
    """Enterprise-grade configuration management system for network connectivity modules."""
    
    def __init__(self, config_path: Optional[str] = None):
        # Setup logging
        self.logger = logging.getLogger('NetworkConfig.Manager')
        
        # Configuration path
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to network connectivity config in the module directory
            module_dir = Path(__file__).parent.parent
            self.config_path = module_dir / 'config' / 'network_connectivity.json'
        
        # Core components
        self.validator = ConfigValidator()
        self.persistence = ConfigPersistence(self.config_path)
        self.dependency_injector = DependencyInjector()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration data
        self._config: Dict[str, Any] = {}
        
        # Change callbacks
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the configuration manager."""
        try:
            self.load_config()
            self._setup_default_services()
            self.logger.info("ConfigManager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ConfigManager: {e}")
            raise
    
    def _setup_default_services(self):
        """Setup default dependency injection services."""
        # Register the config manager itself
        self.dependency_injector.register_singleton('config_manager', self)
        
        # Register validator and persistence services
        self.dependency_injector.register_singleton('config_validator', self.validator)
        self.dependency_injector.register_singleton('config_persistence', self.persistence)
    
    def load_config(self) -> None:
        """Load configuration from file."""
        with self._lock:
            try:
                self._config = self.persistence.load_configuration()
                
                # Ensure network_connectivity section exists
                if 'network_connectivity' not in self._config:
                    self._config['network_connectivity'] = self._get_default_network_config()
                    self.save_config()
                
                # Validate loaded configuration
                errors = self.validator.validate_full_config(self._config)
                if errors:
                    self.logger.warning(f"Configuration validation warnings: {len(errors)} issues found")
                    for error in errors[:5]:  # Log first 5 errors
                        self.logger.warning(f"  {error.path}: {error.message}")
                
                self.logger.info("Configuration loaded successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
                self.reset_to_defaults()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        with self._lock:
            try:
                # Validate before saving
                errors = self.validator.validate_full_config(self._config)
                if errors:
                    self.logger.warning(f"Saving configuration with {len(errors)} validation issues")
                
                # Save to file
                success = self.persistence.save_configuration(self._config)
                if success:
                    self.logger.info("Configuration saved successfully")
                else:
                    raise Exception("Failed to save configuration to file")
                
            except Exception as e:
                self.logger.error(f"Failed to save configuration: {e}")
                raise
    
    def get_setting(self, module: str, key: str = "", default: Any = None) -> Any:
        """Get a configuration setting value.
        
        Args:
            module: Module name (e.g., 'network_connectivity', 'wifi_analyzer')
            key: Setting key within the module (empty for entire module config)
            default: Default value if setting not found
            
        Returns:
            Configuration value or default
        """
        with self._lock:
            try:
                # Navigate to module configuration
                if module not in self._config:
                    self.logger.debug(f"Module '{module}' not found in configuration")
                    return default
                
                module_config = self._config[module]
                
                if not key:
                    # Return entire module configuration
                    return module_config
                
                # Navigate through nested keys (support dot notation)
                keys = key.split('.')
                value = module_config
                
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        self.logger.debug(f"Key '{key}' not found in module '{module}'")
                        return default
                
                self.logger.debug(f"Retrieved setting {module}.{key}: {value}")
                return value
                
            except Exception as e:
                self.logger.error(f"Failed to get setting {module}.{key}: {e}")
                return default
    
    def set_setting(self, module: str, key: str, value: Any) -> bool:
        """Set a configuration setting value.
        
        Args:
            module: Module name
            key: Setting key within the module
            value: Value to set
            
        Returns:
            True if setting was successful
        """
        with self._lock:
            try:
                # Ensure module exists
                if module not in self._config:
                    self._config[module] = {}
                
                # Validate the new value
                validation_errors = self.validator.validate_setting(module, key, value)
                if validation_errors:
                    error_messages = [error.message for error in validation_errors]
                    self.logger.warning(f"Setting validation warnings for {module}.{key}: {error_messages}")
                
                # Navigate through nested keys and set value
                keys = key.split('.')
                config_section = self._config[module]
                
                # Create nested structure if needed
                for k in keys[:-1]:
                    if k not in config_section:
                        config_section[k] = {}
                    config_section = config_section[k]
                
                # Set the final value
                final_key = keys[-1]
                old_value = config_section.get(final_key)
                config_section[final_key] = value
                
                # Save configuration
                self.save_config()
                
                # Trigger change callbacks
                self._trigger_callbacks(module, key, old_value, value)
                
                self.logger.info(f"Set setting {module}.{key} = {value}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to set setting {module}.{key}: {e}")
                return False
    
    def has_setting(self, module: str, key: str = "") -> bool:
        """Check if a configuration setting exists.
        
        Args:
            module: Module name
            key: Setting key within the module (empty to check if module exists)
            
        Returns:
            True if setting exists
        """
        with self._lock:
            try:
                if module not in self._config:
                    return False
                
                if not key:
                    return True
                
                # Check nested keys
                keys = key.split('.')
                value = self._config[module]
                
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return False
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to check setting {module}.{key}: {e}")
                return False
    
    def delete_setting(self, module: str, key: str = "") -> bool:
        """Delete a configuration setting.
        
        Args:
            module: Module name
            key: Setting key within the module (empty to delete entire module)
            
        Returns:
            True if deletion was successful
        """
        with self._lock:
            try:
                if module not in self._config:
                    return False
                
                if not key:
                    # Delete entire module
                    del self._config[module]
                else:
                    # Delete specific key
                    keys = key.split('.')
                    config_section = self._config[module]
                    
                    # Navigate to parent section
                    for k in keys[:-1]:
                        if isinstance(config_section, dict) and k in config_section:
                            config_section = config_section[k]
                        else:
                            return False
                    
                    # Delete final key
                    final_key = keys[-1]
                    if isinstance(config_section, dict) and final_key in config_section:
                        old_value = config_section[final_key]
                        del config_section[final_key]
                        
                        # Trigger change callbacks
                        self._trigger_callbacks(module, key, old_value, None)
                    else:
                        return False
                
                # Save configuration
                self.save_config()
                
                self.logger.info(f"Deleted setting {module}.{key}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete setting {module}.{key}: {e}")
                return False
    
    def get(self, key: str, default=None):
        """Simple get method for compatibility with validation scripts."""
        # Use a default module for simple key access
        return self.get_setting('validation', key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Simple set method for compatibility with validation scripts."""
        # Use a default module for simple key access
        return self.set_setting('validation', key, value)
    
    def register_callback(self, module: str, callback: Callable) -> None:
        """Register a callback for configuration changes.
        
        Args:
            module: Module name to monitor
            callback: Function to call when module configuration changes
                     Signature: callback(module, key, old_value, new_value)
        """
        with self._lock:
            self._callbacks[module].append(callback)
            self.logger.debug(f"Registered callback for module: {module}")
    
    def unregister_callback(self, module: str, callback: Callable) -> None:
        """Unregister a configuration change callback.
        
        Args:
            module: Module name
            callback: Callback function to remove
        """
        with self._lock:
            try:
                self._callbacks[module].remove(callback)
                self.logger.debug(f"Unregistered callback for module: {module}")
            except ValueError:
                self.logger.warning(f"Callback not found for module: {module}")
    
    def _trigger_callbacks(self, module: str, key: str, old_value: Any, new_value: Any) -> None:
        """Trigger registered callbacks for configuration changes."""
        try:
            for callback in self._callbacks[module]:
                try:
                    callback(module, key, old_value, new_value)
                except Exception as e:
                    self.logger.error(f"Callback error for {module}.{key}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to trigger callbacks: {e}")
    
    def validate_configuration(self, config: Dict = None) -> List[ValidationError]:
        """Validate configuration against all schemas.
        
        Args:
            config: Configuration to validate (current config if None)
            
        Returns:
            List of validation errors
        """
        if config is None:
            config = self._config
        
        return self.validator.validate_full_config(config)
    
    def backup_configuration(self, backup_name: str) -> str:
        """Create a backup of the current configuration.
        
        Args:
            backup_name: Name for the backup
            
        Returns:
            Path to the backup file
        """
        try:
            # Ensure configuration is saved before backup
            self.save_config()
            
            backup_path = self.persistence.create_backup(backup_name)
            self.logger.info(f"Configuration backup created: {backup_name}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise
    
    def restore_configuration(self, backup_id: str) -> bool:
        """Restore configuration from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            True if restoration was successful
        """
        try:
            success = self.persistence.restore_backup(backup_id)
            if success:
                # Reload configuration from restored file
                self.load_config()
                self.logger.info(f"Configuration restored from backup: {backup_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available configuration backups.
        
        Returns:
            List of backup information
        """
        return self.persistence.list_backups()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        with self._lock:
            try:
                self._config = {
                    'network_connectivity': self._get_default_network_config()
                }
                
                self.save_config()
                self.logger.info("Configuration reset to defaults")
                
            except Exception as e:
                self.logger.error(f"Failed to reset configuration: {e}")
                raise
    
    def _get_default_network_config(self) -> Dict[str, Any]:
        """Get default network connectivity configuration."""
        return {
            "general": {
                "default_timeout": 30000,
                "max_concurrent_operations": 10,
                "log_level": "INFO",
                "enable_notifications": True,
                "auto_start_services": True,
                "data_cache_timeout": 30,
                "max_history_entries": 1000
            },
            "wifi_analyzer": {
                "scan_interval": 30000,
                "signal_threshold": -70,
                "security_assessment": True,
                "oui_database_update": True,
                "enable_interference_detection": True,
                "enable_channel_analysis": True,
                "data_retention_hours": 24,
                "max_access_points": 1000
            },
            "port_scanner": {
                "scan_timeout": 5000,
                "max_threads": 100,
                "service_detection": True,
                "vulnerability_assessment": True,
                "common_ports": [21, 22, 23, 25, 53, 80, 110, 443, 993, 995],
                "enable_banner_grabbing": True,
                "stealth_mode": False
            },
            "bandwidth_monitor": {
                "monitoring_interval": 1000,
                "alert_threshold_mbps": 100.0,
                "data_retention_days": 30,
                "enable_alerts": True,
                "enable_real_time_chart": True,
                "chart_update_interval": 2000
            },
            "lan_file_transfer": {
                "default_port": 8765,
                "encryption_enabled": True,
                "compression_enabled": True,
                "max_file_size_mb": 1024,
                "connection_timeout": 30,
                "transfer_timeout": 300,
                "max_concurrent_transfers": 3
            },
            "security": {
                "require_admin_for_scans": False,
                "enable_scan_logging": True,
                "alert_on_suspicious_activity": True,
                "security_level": "moderate",
                "audit_trail_enabled": True
            },
            "performance": {
                "enable_performance_monitoring": True,
                "max_memory_usage_mb": 512,
                "max_cpu_usage_percent": 25,
                "enable_background_operations": True,
                "thread_pool_size": "auto"
            }
        }
    
    @contextmanager
    def _atomic_operation(self):
        """Context manager for atomic configuration updates."""
        with self._lock:
            # Create backup before operation
            backup_config = self._config.copy()
            try:
                yield
                # Operation successful, save configuration
                self.save_config()
            except Exception:
                # Operation failed, restore backup
                self._config = backup_config
                raise
    
    def get_dependency_injector(self) -> DependencyInjector:
        """Get the dependency injection container.
        
        Returns:
            DependencyInjector instance
        """
        return self.dependency_injector
    
    def shutdown(self) -> None:
        """Shutdown the configuration manager."""
        try:
            # Save any pending changes
            self.save_config()
            
            # Shutdown dependency injection container
            self.dependency_injector.shutdown_all()
            
            self.logger.info("ConfigManager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during ConfigManager shutdown: {e}")


# Module registry for network tools
class NetworkModuleRegistry:
    """Registration system for network connectivity modules."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger('NetworkConfig.ModuleRegistry')
        self.modules: Dict[str, Any] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.initialization_order: List[str] = []
    
    def register_module(self, name: str, module_class: type, dependencies: List[str] = None) -> bool:
        """Register a network module.
        
        Args:
            name: Module name
            module_class: Module class
            dependencies: List of dependency module names
            
        Returns:
            True if registration was successful
        """
        try:
            self.modules[name] = module_class
            self.dependencies[name] = dependencies or []
            
            # Register module with dependency injector
            self.config_manager.get_dependency_injector().register_service(
                name, module_class, singleton=True
            )
            
            self.logger.info(f"Registered network module: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register module {name}: {e}")
            return False
    
    def initialize_modules(self) -> List[str]:
        """Initialize all registered modules in dependency order.
        
        Returns:
            List of modules that failed to initialize
        """
        failed_modules = []
        
        try:
            # Calculate initialization order based on dependencies
            self._calculate_initialization_order()
            
            # Initialize modules in order
            for module_name in self.initialization_order:
                try:
                    module_instance = self.config_manager.get_dependency_injector().get_service(module_name)
                    
                    # Initialize module if it has an initialize method
                    if hasattr(module_instance, 'initialize'):
                        module_instance.initialize()
                    
                    self.logger.info(f"Initialized network module: {module_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize module {module_name}: {e}")
                    failed_modules.append(module_name)
            
        except Exception as e:
            self.logger.error(f"Module initialization failed: {e}")
            # If order calculation fails, try to initialize all modules
            for module_name in self.modules:
                if module_name not in failed_modules:
                    failed_modules.append(module_name)
        
        return failed_modules
    
    def _calculate_initialization_order(self):
        """Calculate module initialization order based on dependencies."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        self.initialization_order = []
        
        def visit(module_name: str):
            if module_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {module_name}")
            
            if module_name not in visited:
                temp_visited.add(module_name)
                
                # Visit dependencies first
                for dependency in self.dependencies.get(module_name, []):
                    if dependency in self.modules:
                        visit(dependency)
                
                temp_visited.remove(module_name)
                visited.add(module_name)
                self.initialization_order.append(module_name)
        
        # Visit all modules
        for module_name in self.modules:
            if module_name not in visited:
                visit(module_name)
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get initialized module instance.
        
        Args:
            name: Module name
            
        Returns:
            Module instance or None if not found
        """
        try:
            return self.config_manager.get_dependency_injector().get_service(name)
        except KeyError:
            return None
    
    def shutdown_modules(self) -> None:
        """Shutdown all registered modules."""
        # Shutdown in reverse order
        for module_name in reversed(self.initialization_order):
            try:
                module_instance = self.get_module(module_name)
                if module_instance and hasattr(module_instance, 'shutdown'):
                    module_instance.shutdown()
                
                self.logger.info(f"Shutdown network module: {module_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to shutdown module {module_name}: {e}")


# Global instance for module compatibility
_global_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global ConfigManager instance for backward compatibility.
    
    Returns:
        ConfigManager instance
    """
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    
    return _global_config_manager