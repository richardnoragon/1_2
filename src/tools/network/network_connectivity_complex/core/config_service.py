"""Advanced configuration service for network connectivity tools."""

import hashlib
import json
import logging
import shutil
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .config_manager import ConfigManager
from .logging_integration import get_network_logging_manager


class ConfigurationEvent(Enum):
    """Configuration event types."""

    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    PROFILE_DELETED = "profile_deleted"
    PROFILE_SWITCHED = "profile_switched"
    CONFIG_UPDATED = "config_updated"
    CONFIG_VALIDATED = "config_validated"
    CONFIG_MIGRATED = "config_migrated"
    CONFIG_BACKED_UP = "config_backed_up"
    CONFIG_RESTORED = "config_restored"


@dataclass
class ConfigurationProfile:
    """Configuration profile data structure."""

    name: str
    description: str
    use_case: str  # home, enterprise, security_audit, custom
    created_at: datetime
    updated_at: datetime
    version: str
    settings: Dict[str, Any]
    is_active: bool = False
    is_default: bool = False
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ConfigurationBackup:
    """Configuration backup metadata."""

    backup_id: str
    name: str
    description: str
    created_at: datetime
    config_version: str
    file_path: str
    checksum: str
    size_bytes: int


class ConfigurationValidator:
    """Advanced configuration validation system."""

    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            "ConfigValidator"
        )
        self._validation_rules: Dict[str, List[Callable]] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default validation rules."""
        # General settings validation
        self.add_validation_rule(
            "general.default_timeout",
            [
                lambda x: isinstance(x, int) and 1000 <= x <= 60000,
                "Timeout must be integer between 1000 and 60000 ms",
            ],
        )

        self.add_validation_rule(
            "general.max_concurrent_operations",
            [
                lambda x: isinstance(x, int) and 1 <= x <= 100,
                "Max concurrent operations must be integer between 1 and 100",
            ],
        )

        self.add_validation_rule(
            "general.log_level",
            [
                lambda x: x
                in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            ],
        )

        # Bandwidth monitor validation
        self.add_validation_rule(
            "bandwidth_monitor.monitoring_interval",
            [
                lambda x: isinstance(x, int) and 100 <= x <= 10000,
                "Monitoring interval must be integer between 100 and 10000 ms",
            ],
        )

        self.add_validation_rule(
            "bandwidth_monitor.alert_threshold_mbps",
            [
                lambda x: isinstance(x, (int, float)) and x >= 0.1,
                "Alert threshold must be number >= 0.1 Mbps",
            ],
        )

        # Port scanner validation
        self.add_validation_rule(
            "port_scanner.scan_timeout",
            [
                lambda x: isinstance(x, int) and 100 <= x <= 30000,
                "Scan timeout must be integer between 100 and 30000 ms",
            ],
        )

        self.add_validation_rule(
            "port_scanner.max_threads",
            [
                lambda x: isinstance(x, int) and 1 <= x <= 1000,
                "Max threads must be integer between 1 and 1000",
            ],
        )

        # Security validation
        self.add_validation_rule(
            "security.security_level",
            [
                lambda x: x in ["strict", "moderate", "permissive"],
                "Security level must be one of: strict, moderate, permissive",
            ],
        )

    def add_validation_rule(self, path: str, rule: List[Union[Callable, str]]):
        """Add a validation rule for a configuration path.

        Args:
            path: Configuration path (e.g., 'general.timeout')
            rule: List containing [validation_function, error_message]
        """
        if path not in self._validation_rules:
            self._validation_rules[path] = []
        self._validation_rules[path].append(rule)

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration against all rules.

        Args:
            config: Configuration dictionary to validate

        Returns:
            List of validation error messages
        """
        errors = []

        for path, rules in self._validation_rules.items():
            try:
                value = self._get_nested_value(config, path)
                if value is not None:
                    for rule in rules:
                        validator_func, error_msg = rule
                        if not validator_func(value):
                            errors.append(f"{path}: {error_msg}")
            except KeyError:
                # Path doesn't exist in config, which is okay for optional settings
                continue
            except Exception as e:
                errors.append(f"{path}: Validation error - {e}")

        return errors

    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """Get value from nested configuration using dot notation."""
        keys = path.split(".")
        value = config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError(f"Path {path} not found")

        return value


class ConfigurationMigrator:
    """Configuration migration system."""

    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            "ConfigMigrator"
        )
        self._migrations: Dict[str, Callable] = {}
        self._setup_migrations()

    def _setup_migrations(self):
        """Setup configuration migrations."""
        self._migrations["1.0.0"] = self._migrate_to_1_0_0
        self._migrations["1.1.0"] = self._migrate_to_1_1_0
        self._migrations["1.2.0"] = self._migrate_to_1_2_0

    def migrate_config(
        self, config: Dict[str, Any], from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Migrate configuration from one version to another.

        Args:
            config: Configuration to migrate
            from_version: Source version
            to_version: Target version

        Returns:
            Migrated configuration
        """
        self.logger.info(
            f"Migrating configuration from {from_version} to {to_version}"
        )

        # Apply migrations in order
        current_config = config.copy()

        # Simple version-based migration for now
        if from_version < to_version:
            for version, migration_func in self._migrations.items():
                if from_version < version <= to_version:
                    current_config = migration_func(current_config)
                    self.logger.info(f"Applied migration to version {version}")

        return current_config

    def _migrate_to_1_0_0(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migration to version 1.0.0."""
        # Add new fields introduced in 1.0.0
        if "network_connectivity" in config:
            nc_config = config["network_connectivity"]

            # Add notification settings if missing
            if "general" in nc_config:
                general = nc_config["general"]
                if "enable_notifications" not in general:
                    general["enable_notifications"] = True
                if "notification_sound" not in general:
                    general["notification_sound"] = True

        return config

    def _migrate_to_1_1_0(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migration to version 1.1.0."""
        # Add performance monitoring settings
        if "network_connectivity" in config:
            nc_config = config["network_connectivity"]

            if "performance" not in nc_config:
                nc_config["performance"] = {
                    "enable_performance_monitoring": True,
                    "max_memory_usage_mb": 512,
                    "max_cpu_usage_percent": 25,
                }

        return config

    def _migrate_to_1_2_0(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migration to version 1.2.0."""
        # Add advanced security settings
        if "network_connectivity" in config:
            nc_config = config["network_connectivity"]

            if "security" in nc_config:
                security = nc_config["security"]
                if "audit_trail_enabled" not in security:
                    security["audit_trail_enabled"] = True
                if "encrypt_stored_data" not in security:
                    security["encrypt_stored_data"] = False

        return config


class ConfigurationService:
    """Advanced configuration management service for network connectivity tools."""

    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            "ConfigService"
        )
        self.config_manager = ConfigManager()
        self.validator = ConfigurationValidator()
        self.migrator = ConfigurationMigrator()

        # Threading
        self._lock = threading.RLock()

        # Profiles
        self._profiles: Dict[str, ConfigurationProfile] = {}
        self._active_profile: Optional[str] = None

        # Backups
        self._backups: Dict[str, ConfigurationBackup] = {}

        # Event callbacks
        self._event_callbacks: Dict[ConfigurationEvent, List[Callable]] = {}

        # Configuration cache
        self._config_cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_timeout = 30  # seconds

        # Initialize
        self._initialize()

    def _initialize(self):
        """Initialize the configuration service."""
        try:
            self._load_profiles()
            self._load_backups()
            self._ensure_default_profile()
            self.logger.info("Configuration service initialized successfully")
        except Exception as e:
            self.logger.error(
                f"Failed to initialize configuration service: {e}"
            )
            raise

    def _load_profiles(self):
        """Load configuration profiles from storage."""
        try:
            profiles_data = self.config_manager.get_setting(
                "network_connectivity", "profiles", {}
            )

            for profile_name, profile_data in profiles_data.items():
                try:
                    # Convert datetime strings back to datetime objects
                    if "created_at" in profile_data:
                        profile_data["created_at"] = datetime.fromisoformat(
                            profile_data["created_at"]
                        )
                    if "updated_at" in profile_data:
                        profile_data["updated_at"] = datetime.fromisoformat(
                            profile_data["updated_at"]
                        )

                    profile = ConfigurationProfile(**profile_data)
                    self._profiles[profile_name] = profile

                    if profile.is_active:
                        self._active_profile = profile_name

                except Exception as e:
                    self.logger.error(
                        f"Failed to load profile {profile_name}: {e}"
                    )

            self.logger.info(
                f"Loaded {len(self._profiles)} configuration profiles"
            )

        except Exception as e:
            self.logger.error(f"Failed to load profiles: {e}")

    def _load_backups(self):
        """Load backup metadata from storage."""
        try:
            backups_data = self.config_manager.get_setting(
                "network_connectivity", "backups", {}
            )

            for backup_id, backup_data in backups_data.items():
                try:
                    # Convert datetime strings back to datetime objects
                    if "created_at" in backup_data:
                        backup_data["created_at"] = datetime.fromisoformat(
                            backup_data["created_at"]
                        )

                    backup = ConfigurationBackup(**backup_data)
                    self._backups[backup_id] = backup

                except Exception as e:
                    self.logger.error(
                        f"Failed to load backup {backup_id}: {e}"
                    )

            self.logger.info(
                f"Loaded {len(self._backups)} configuration backups"
            )

        except Exception as e:
            self.logger.error(f"Failed to load backups: {e}")

    def _ensure_default_profile(self):
        """Ensure a default profile exists."""
        if not self._profiles:
            self.create_profile(
                name="Default",
                description="Default network connectivity configuration",
                use_case="home",
                settings=self._get_default_settings(),
                set_as_active=True,
                set_as_default=True,
            )

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        from .config_integration import get_network_config_manager

        config_manager = get_network_config_manager()
        return config_manager.config_manager.get_setting(
            "network_connectivity", {}
        )

    def _save_profiles(self):
        """Save profiles to storage."""
        try:
            profiles_data = {}

            for profile_name, profile in self._profiles.items():
                profile_dict = asdict(profile)
                # Convert datetime objects to strings for JSON serialization
                profile_dict["created_at"] = profile.created_at.isoformat()
                profile_dict["updated_at"] = profile.updated_at.isoformat()
                profiles_data[profile_name] = profile_dict

            self.config_manager.set_setting(
                "network_connectivity", "profiles", profiles_data
            )

        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")
            raise

    def _save_backups(self):
        """Save backup metadata to storage."""
        try:
            backups_data = {}

            for backup_id, backup in self._backups.items():
                backup_dict = asdict(backup)
                # Convert datetime objects to strings for JSON serialization
                backup_dict["created_at"] = backup.created_at.isoformat()
                backups_data[backup_id] = backup_dict

            self.config_manager.set_setting(
                "network_connectivity", "backups", backups_data
            )

        except Exception as e:
            self.logger.error(f"Failed to save backups: {e}")
            raise

    def create_profile(
        self,
        name: str,
        description: str,
        use_case: str,
        settings: Dict[str, Any],
        set_as_active: bool = False,
        set_as_default: bool = False,
        tags: List[str] = None,
    ) -> bool:
        """Create a new configuration profile.

        Args:
            name: Profile name
            description: Profile description
            use_case: Use case (home, enterprise, security_audit, custom)
            settings: Configuration settings
            set_as_active: Whether to set as active profile
            set_as_default: Whether to set as default profile
            tags: Optional tags for the profile

        Returns:
            True if created successfully
        """
        with self._lock:
            try:
                if name in self._profiles:
                    raise ValueError(f"Profile '{name}' already exists")

                # Validate settings
                validation_errors = self.validator.validate_config(settings)
                if validation_errors:
                    raise ValueError(f"Invalid settings: {validation_errors}")

                # Create profile
                now = datetime.now()
                profile = ConfigurationProfile(
                    name=name,
                    description=description,
                    use_case=use_case,
                    created_at=now,
                    updated_at=now,
                    version="1.2.0",
                    settings=settings.copy(),
                    is_active=set_as_active,
                    is_default=set_as_default,
                    tags=tags or [],
                )

                # If setting as default, remove default flag from other profiles
                if set_as_default:
                    for p in self._profiles.values():
                        p.is_default = False

                # If setting as active, deactivate other profiles
                if set_as_active:
                    for p in self._profiles.values():
                        p.is_active = False
                    self._active_profile = name

                self._profiles[name] = profile
                self._save_profiles()

                self._trigger_event(
                    ConfigurationEvent.PROFILE_CREATED,
                    {"profile_name": name, "use_case": use_case},
                )

                self.logger.info(f"Created configuration profile: {name}")
                return True

            except Exception as e:
                self.logger.error(f"Failed to create profile {name}: {e}")
                return False

    def update_profile(self, name: str, **kwargs) -> bool:
        """Update an existing configuration profile.

        Args:
            name: Profile name
            **kwargs: Fields to update

        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                if name not in self._profiles:
                    raise ValueError(f"Profile '{name}' does not exist")

                profile = self._profiles[name]

                # Update fields
                for field, value in kwargs.items():
                    if hasattr(profile, field):
                        if field == "settings" and value:
                            # Validate settings if updating
                            validation_errors = self.validator.validate_config(
                                value
                            )
                            if validation_errors:
                                raise ValueError(
                                    f"Invalid settings: {validation_errors}"
                                )

                        setattr(profile, field, value)

                profile.updated_at = datetime.now()
                self._save_profiles()

                self._trigger_event(
                    ConfigurationEvent.PROFILE_UPDATED, {"profile_name": name}
                )

                self.logger.info(f"Updated configuration profile: {name}")
                return True

            except Exception as e:
                self.logger.error(f"Failed to update profile {name}: {e}")
                return False

    def delete_profile(self, name: str) -> bool:
        """Delete a configuration profile.

        Args:
            name: Profile name

        Returns:
            True if deleted successfully
        """
        with self._lock:
            try:
                if name not in self._profiles:
                    raise ValueError(f"Profile '{name}' does not exist")

                profile = self._profiles[name]

                # Cannot delete active profile
                if profile.is_active:
                    raise ValueError("Cannot delete active profile")

                # Cannot delete default profile
                if profile.is_default:
                    raise ValueError("Cannot delete default profile")

                del self._profiles[name]
                self._save_profiles()

                self._trigger_event(
                    ConfigurationEvent.PROFILE_DELETED, {"profile_name": name}
                )

                self.logger.info(f"Deleted configuration profile: {name}")
                return True

            except Exception as e:
                self.logger.error(f"Failed to delete profile {name}: {e}")
                return False

    def switch_profile(self, name: str) -> bool:
        """Switch to a different configuration profile.

        Args:
            name: Profile name to switch to

        Returns:
            True if switched successfully
        """
        with self._lock:
            try:
                if name not in self._profiles:
                    raise ValueError(f"Profile '{name}' does not exist")

                # Deactivate current profile
                if self._active_profile:
                    self._profiles[self._active_profile].is_active = False

                # Activate new profile
                profile = self._profiles[name]
                profile.is_active = True
                self._active_profile = name

                # Apply profile settings
                self._apply_profile_settings(profile.settings)

                self._save_profiles()
                self._clear_cache()

                self._trigger_event(
                    ConfigurationEvent.PROFILE_SWITCHED,
                    {
                        "profile_name": name,
                        "previous_profile": self._active_profile,
                    },
                )

                self.logger.info(f"Switched to configuration profile: {name}")
                return True

            except Exception as e:
                self.logger.error(f"Failed to switch to profile {name}: {e}")
                return False

    def _apply_profile_settings(self, settings: Dict[str, Any]):
        """Apply profile settings to the configuration manager."""
        try:
            # Update the main configuration with profile settings
            current_config = self.config_manager.get_setting(
                "network_connectivity", {}
            )

            # Deep merge settings
            merged_config = self._deep_merge(current_config, settings)

            # Set the updated configuration
            self.config_manager.set_setting(
                "network_connectivity", "", merged_config
            )

        except Exception as e:
            self.logger.error(f"Failed to apply profile settings: {e}")
            raise

    def _deep_merge(
        self, base: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_profiles(self) -> List[ConfigurationProfile]:
        """Get list of all configuration profiles.

        Returns:
            List of configuration profiles
        """
        with self._lock:
            return list(self._profiles.values())

    def get_profile(self, name: str) -> Optional[ConfigurationProfile]:
        """Get a specific configuration profile.

        Args:
            name: Profile name

        Returns:
            Configuration profile or None if not found
        """
        with self._lock:
            return self._profiles.get(name)

    def get_active_profile(self) -> Optional[ConfigurationProfile]:
        """Get the currently active configuration profile.

        Returns:
            Active configuration profile or None
        """
        with self._lock:
            if self._active_profile:
                return self._profiles.get(self._active_profile)
            return None

    def create_backup(self, name: str, description: str = "") -> str:
        """Create a configuration backup.

        Args:
            name: Backup name
            description: Backup description

        Returns:
            Backup ID
        """
        with self._lock:
            try:
                # Generate backup ID
                backup_id = hashlib.md5(
                    f"{name}_{datetime.now().isoformat()}".encode()
                ).hexdigest()[:8]

                # Get current configuration
                current_config = self.config_manager.get_setting(
                    "network_connectivity", {}
                )

                # Create backup file
                backup_dir = Path.cwd() / "backups" / "network_connectivity"
                backup_dir.mkdir(parents=True, exist_ok=True)

                backup_file = backup_dir / f"config_backup_{backup_id}.json"

                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(current_config, f, indent=2, ensure_ascii=False)

                # Calculate checksum
                checksum = hashlib.sha256(backup_file.read_bytes()).hexdigest()

                # Create backup metadata
                backup = ConfigurationBackup(
                    backup_id=backup_id,
                    name=name,
                    description=description,
                    created_at=datetime.now(),
                    config_version="1.2.0",
                    file_path=str(backup_file),
                    checksum=checksum,
                    size_bytes=backup_file.stat().st_size,
                )

                self._backups[backup_id] = backup
                self._save_backups()

                self._trigger_event(
                    ConfigurationEvent.CONFIG_BACKED_UP,
                    {"backup_id": backup_id, "backup_name": name},
                )

                self.logger.info(
                    f"Created configuration backup: {name} ({backup_id})"
                )
                return backup_id

            except Exception as e:
                self.logger.error(f"Failed to create backup {name}: {e}")
                raise

    def restore_backup(self, backup_id: str) -> bool:
        """Restore configuration from a backup.

        Args:
            backup_id: Backup ID to restore

        Returns:
            True if restored successfully
        """
        with self._lock:
            try:
                if backup_id not in self._backups:
                    raise ValueError(f"Backup '{backup_id}' does not exist")

                backup = self._backups[backup_id]
                backup_file = Path(backup.file_path)

                if not backup_file.exists():
                    raise FileNotFoundError(
                        f"Backup file not found: {backup.file_path}"
                    )

                # Verify checksum
                current_checksum = hashlib.sha256(
                    backup_file.read_bytes()
                ).hexdigest()
                if current_checksum != backup.checksum:
                    raise ValueError(
                        "Backup file checksum mismatch - file may be corrupted"
                    )

                # Load backup configuration
                with open(backup_file, "r", encoding="utf-8") as f:
                    backup_config = json.load(f)

                # Validate backup configuration
                validation_errors = self.validator.validate_config(
                    backup_config
                )
                if validation_errors:
                    self.logger.warning(
                        f"Backup validation warnings: {validation_errors}"
                    )

                # Apply backup configuration
                self.config_manager.set_setting(
                    "network_connectivity", "", backup_config
                )

                # Reload profiles and clear cache
                self._load_profiles()
                self._clear_cache()

                self._trigger_event(
                    ConfigurationEvent.CONFIG_RESTORED,
                    {"backup_id": backup_id, "backup_name": backup.name},
                )

                self.logger.info(
                    f"Restored configuration from backup: {backup.name}"
                )
                return True

            except Exception as e:
                self.logger.error(f"Failed to restore backup {backup_id}: {e}")
                return False

    def get_backups(self) -> List[ConfigurationBackup]:
        """Get list of all configuration backups.

        Returns:
            List of configuration backups
        """
        with self._lock:
            return list(self._backups.values())

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a configuration backup.

        Args:
            backup_id: Backup ID to delete

        Returns:
            True if deleted successfully
        """
        with self._lock:
            try:
                if backup_id not in self._backups:
                    raise ValueError(f"Backup '{backup_id}' does not exist")

                backup = self._backups[backup_id]
                backup_file = Path(backup.file_path)

                # Delete backup file
                if backup_file.exists():
                    backup_file.unlink()

                # Remove from metadata
                del self._backups[backup_id]
                self._save_backups()

                self.logger.info(
                    f"Deleted configuration backup: {backup.name}"
                )
                return True

            except Exception as e:
                self.logger.error(f"Failed to delete backup {backup_id}: {e}")
                return False

    def validate_configuration(
        self, config: Dict[str, Any] = None
    ) -> List[str]:
        """Validate configuration.

        Args:
            config: Configuration to validate (current config if None)

        Returns:
            List of validation errors
        """
        if config is None:
            config = self.config_manager.get_setting(
                "network_connectivity", {}
            )

        errors = self.validator.validate_config(config)

        self._trigger_event(
            ConfigurationEvent.CONFIG_VALIDATED,
            {"errors_count": len(errors), "is_valid": len(errors) == 0},
        )

        return errors

    def migrate_configuration(
        self, from_version: str, to_version: str
    ) -> bool:
        """Migrate configuration between versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            True if migrated successfully
        """
        with self._lock:
            try:
                current_config = self.config_manager.get_setting(
                    "network_connectivity", {}
                )

                # Perform migration
                migrated_config = self.migrator.migrate_config(
                    current_config, from_version, to_version
                )

                # Validate migrated configuration
                validation_errors = self.validator.validate_config(
                    migrated_config
                )
                if validation_errors:
                    self.logger.warning(
                        f"Migration validation warnings: {validation_errors}"
                    )

                # Apply migrated configuration
                self.config_manager.set_setting(
                    "network_connectivity", "", migrated_config
                )

                # Clear cache
                self._clear_cache()

                self._trigger_event(
                    ConfigurationEvent.CONFIG_MIGRATED,
                    {"from_version": from_version, "to_version": to_version},
                )

                self.logger.info(
                    f"Migrated configuration from {from_version} to {to_version}"
                )
                return True

            except Exception as e:
                self.logger.error(f"Failed to migrate configuration: {e}")
                return False

    def export_configuration(
        self,
        file_path: str,
        include_profiles: bool = True,
        include_backups: bool = False,
    ) -> bool:
        """Export configuration to file.

        Args:
            file_path: Export file path
            include_profiles: Whether to include profiles
            include_backups: Whether to include backup metadata

        Returns:
            True if exported successfully
        """
        try:
            export_data = {
                "configuration": self.config_manager.get_setting(
                    "network_connectivity", {}
                ),
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "1.2.0",
            }

            if include_profiles:
                profiles_data = {}
                for name, profile in self._profiles.items():
                    profile_dict = asdict(profile)
                    profile_dict["created_at"] = profile.created_at.isoformat()
                    profile_dict["updated_at"] = profile.updated_at.isoformat()
                    profiles_data[name] = profile_dict
                export_data["profiles"] = profiles_data

            if include_backups:
                backups_data = {}
                for backup_id, backup in self._backups.items():
                    backup_dict = asdict(backup)
                    backup_dict["created_at"] = backup.created_at.isoformat()
                    backups_data[backup_id] = backup_dict
                export_data["backups"] = backups_data

            # Write export file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Exported configuration to: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False

    def import_configuration(
        self,
        file_path: str,
        import_profiles: bool = True,
        import_backups: bool = False,
        validate: bool = True,
    ) -> bool:
        """Import configuration from file.

        Args:
            file_path: Import file path
            import_profiles: Whether to import profiles
            import_backups: Whether to import backup metadata
            validate: Whether to validate imported configuration

        Returns:
            True if imported successfully
        """
        with self._lock:
            try:
                # Load import file
                with open(file_path, "r", encoding="utf-8") as f:
                    import_data = json.load(f)

                # Validate structure
                if "configuration" not in import_data:
                    raise ValueError(
                        "Invalid import file: missing configuration section"
                    )

                config = import_data["configuration"]

                # Validate configuration if requested
                if validate:
                    validation_errors = self.validator.validate_config(config)
                    if validation_errors:
                        raise ValueError(
                            f"Invalid configuration: {validation_errors}"
                        )

                # Import configuration
                self.config_manager.set_setting(
                    "network_connectivity", "", config
                )

                # Import profiles if requested
                if import_profiles and "profiles" in import_data:
                    for profile_name, profile_data in import_data[
                        "profiles"
                    ].items():
                        try:
                            # Convert datetime strings back to datetime objects
                            profile_data["created_at"] = (
                                datetime.fromisoformat(
                                    profile_data["created_at"]
                                )
                            )
                            profile_data["updated_at"] = (
                                datetime.fromisoformat(
                                    profile_data["updated_at"]
                                )
                            )

                            profile = ConfigurationProfile(**profile_data)
                            self._profiles[profile_name] = profile

                        except Exception as e:
                            self.logger.error(
                                f"Failed to import profile {profile_name}: {e}"
                            )

                # Import backups if requested
                if import_backups and "backups" in import_data:
                    for backup_id, backup_data in import_data[
                        "backups"
                    ].items():
                        try:
                            # Convert datetime strings back to datetime objects
                            backup_data["created_at"] = datetime.fromisoformat(
                                backup_data["created_at"]
                            )

                            backup = ConfigurationBackup(**backup_data)
                            self._backups[backup_id] = backup

                        except Exception as e:
                            self.logger.error(
                                f"Failed to import backup {backup_id}: {e}"
                            )

                # Save imported data
                if import_profiles:
                    self._save_profiles()
                if import_backups:
                    self._save_backups()

                # Clear cache
                self._clear_cache()

                self.logger.info(f"Imported configuration from: {file_path}")
                return True

            except Exception as e:
                self.logger.error(f"Failed to import configuration: {e}")
                return False

    def get_configuration(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get current configuration with caching.

        Args:
            use_cache: Whether to use cached configuration

        Returns:
            Current configuration dictionary
        """
        with self._lock:
            now = datetime.now()

            # Check cache validity
            if (
                use_cache
                and self._config_cache
                and self._cache_timestamp
                and (now - self._cache_timestamp).total_seconds()
                < self._cache_timeout
            ):
                return self._config_cache.copy()

            # Load fresh configuration
            config = self.config_manager.get_setting(
                "network_connectivity", {}
            )

            # Update cache
            self._config_cache = config.copy()
            self._cache_timestamp = now

            return config

    def update_configuration(
        self, updates: Dict[str, Any], validate: bool = True
    ) -> bool:
        """Update configuration with real-time notifications.

        Args:
            updates: Configuration updates
            validate: Whether to validate updates

        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                # Get current configuration
                current_config = self.get_configuration(use_cache=False)

                # Apply updates
                updated_config = self._deep_merge(current_config, updates)

                # Validate if requested
                if validate:
                    validation_errors = self.validator.validate_config(
                        updated_config
                    )
                    if validation_errors:
                        raise ValueError(
                            f"Invalid configuration updates: {validation_errors}"
                        )

                # Apply updates
                self.config_manager.set_setting(
                    "network_connectivity", "", updated_config
                )

                # Clear cache
                self._clear_cache()

                # Update active profile if exists
                if self._active_profile:
                    active_profile = self._profiles[self._active_profile]
                    active_profile.settings = updated_config.copy()
                    active_profile.updated_at = datetime.now()
                    self._save_profiles()

                self._trigger_event(
                    ConfigurationEvent.CONFIG_UPDATED,
                    {"updates": list(updates.keys())},
                )

                self.logger.info(
                    f"Updated configuration: {list(updates.keys())}"
                )
                return True

            except Exception as e:
                self.logger.error(f"Failed to update configuration: {e}")
                return False

    def _clear_cache(self):
        """Clear configuration cache."""
        self._config_cache = {}
        self._cache_timestamp = None

    def add_event_callback(
        self,
        event: ConfigurationEvent,
        callback: Callable[[Dict[str, Any]], None],
    ):
        """Add event callback.

        Args:
            event: Configuration event type
            callback: Callback function
        """
        if event not in self._event_callbacks:
            self._event_callbacks[event] = []
        self._event_callbacks[event].append(callback)

    def remove_event_callback(
        self,
        event: ConfigurationEvent,
        callback: Callable[[Dict[str, Any]], None],
    ):
        """Remove event callback.

        Args:
            event: Configuration event type
            callback: Callback function to remove
        """
        if event in self._event_callbacks:
            try:
                self._event_callbacks[event].remove(callback)
            except ValueError:
                pass

    def _trigger_event(self, event: ConfigurationEvent, data: Dict[str, Any]):
        """Trigger configuration event.

        Args:
            event: Event type
            data: Event data
        """
        if event in self._event_callbacks:
            for callback in self._event_callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary.

        Returns:
            Configuration summary dictionary
        """
        with self._lock:
            active_profile = self.get_active_profile()

            return {
                "total_profiles": len(self._profiles),
                "active_profile": (
                    active_profile.name if active_profile else None
                ),
                "total_backups": len(self._backups),
                "configuration_valid": len(self.validate_configuration()) == 0,
                "last_updated": (
                    active_profile.updated_at.isoformat()
                    if active_profile
                    else None
                ),
                "cache_status": {
                    "cached": bool(self._config_cache),
                    "cache_age_seconds": (
                        (
                            datetime.now() - self._cache_timestamp
                        ).total_seconds()
                        if self._cache_timestamp
                        else None
                    ),
                },
            }


# Global instance for easy access
_config_service = None


def get_config_service() -> ConfigurationService:
    """Get global configuration service instance.

    Returns:
        ConfigurationService instance
    """
    global _config_service

    if _config_service is None:
        _config_service = ConfigurationService()

    return _config_service
