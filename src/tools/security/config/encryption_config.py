"""
Configuration management for encryption operations.

This module handles persistent storage of user preferences, validation of
settings, and coordination with hub configuration system.
"""

import os
import json
import logging
from typing import Dict, Any, List
from pathlib import Path


class EncryptionConfig:
    """
    Configuration management for encryption operations.

    Handles persistent storage of user preferences, validation of settings,
    and coordination with hub configuration system.
    """

    DEFAULT_CONFIG_SCHEMA = {
        "user_preferences": {
            "default_key_directory": "",
            "auto_generate_key_names": True,
            "confirm_overwrite": True,
            "show_progress_details": True,
            "remember_last_directory": True,
        },
        "security_settings": {
            "secure_key_storage": True,
            "key_derivation_iterations": 100000,
            "secure_delete_temp_files": True,
            "audit_all_operations": True,
        },
        "performance_settings": {
            "buffer_size": 8192,
            "progress_update_frequency": 100,
            "max_memory_usage": 1073741824,  # 1GB
            "concurrent_operations_limit": 1,
        },
        "ui_settings": {
            "window_size": (800, 600),
            "window_position": None,
            "theme_preference": "system",
            "show_advanced_options": False,
        },
        "hub_integration": {
            "enable_hub_communication": True,
            "report_progress_to_hub": True,
            "coordinate_resources": True,
            "sync_configuration": True,
        },
    }

    def __init__(self, config_path: str = None, hub_instance=None):
        """
        Initialize configuration management.

        Args:
            config_path: Optional custom config file path
            hub_instance: Optional hub instance for synchronization
        """
        self.hub_instance = hub_instance
        self.config_path = config_path or self._get_default_config_path()
        self._config = {}
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        app_data = os.path.expanduser("~/.rfu_hub")
        return os.path.join(app_data, "encryption_config.json")

    def _preference_store(self):
        from src.core.preferences.legacy_json import LegacyJSONPreferences
        return LegacyJSONPreferences("encryption", self.DEFAULT_CONFIG_SCHEMA)

    def _load_config(self):
        """Import legacy values once; native JSON is retained unchanged."""
        self._config = self._preference_store().load(self.config_path)

    def _save_config(self):
        self._preference_store().save(self._config)

    def get_setting(self, key: str, default=None) -> Any:
        """
        Get configuration setting with dot notation support.

        Args:
            key: Setting key (supports dot notation like
                 'user_preferences.default_key_directory')
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        try:
            keys = key.split(".")
            value = self._config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value
        except Exception:
            return default

    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set configuration setting with validation.

        Args:
            key: Setting key (supports dot notation)
            value: Setting value

        Returns:
            bool: True if setting was valid and saved, False otherwise

        Raises:
            ValueError: If value fails validation
            TypeError: If value type is incorrect
        """
        try:
            # Validate the setting
            if not self._validate_setting(key, value):
                raise ValueError(f"Invalid value for setting {key}: {value}")

            # Navigate to the correct location in config
            keys = key.split(".")
            config_ref = self._config

            # Navigate to parent
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]

            # Set the value
            config_ref[keys[-1]] = value

            # Save configuration
            self._save_config()

            # Sync with hub if available
            if self.hub_instance and self.get_setting(
                "hub_integration.sync_configuration", True
            ):
                self._sync_with_hub()

            return True

        except Exception as e:
            logging.error(f"Failed to set setting {key}: {e}")
            return False

    def _validate_setting(self, key: str, value: Any) -> bool:
        """Validate a setting value."""
        try:
            # Get the expected type from default schema
            default_value = self._get_default_value(key)
            if default_value is None:
                return True  # Allow new settings

            # Type validation
            if not isinstance(value, type(default_value)):
                return False

            # Specific validations
            if key == "performance_settings.buffer_size":
                return isinstance(value, int) and 1024 <= value <= 1048576
            elif key == "performance_settings.progress_update_frequency":
                return isinstance(value, int) and 10 <= value <= 1000
            elif key == "performance_settings.max_memory_usage":
                return isinstance(value, int) and value > 0
            elif key == "security_settings.key_derivation_iterations":
                return isinstance(value, int) and value >= 10000
            elif key == "ui_settings.window_size":
                return (
                    isinstance(value, (list, tuple))
                    and len(value) == 2
                    and all(isinstance(x, int) and x > 0 for x in value)
                )

            return True

        except Exception:
            return False

    def _get_default_value(self, key: str):
        """Get default value for a setting key."""
        try:
            keys = key.split(".")
            value = self.DEFAULT_CONFIG_SCHEMA

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None

            return value
        except Exception:
            return None

    def validate_settings(self) -> List[Dict[str, str]]:
        """
        Validate all configuration settings.

        Returns:
            List of validation issues, each containing:
                - 'key': Setting key with issue
                - 'issue': Description of the problem
                - 'severity': 'error', 'warning', or 'info'
                - 'suggestion': Suggested fix
        """
        issues = []

        try:
            # Check all settings in current config
            for section, settings in self._config.items():
                if isinstance(settings, dict):
                    for setting_key, value in settings.items():
                        full_key = f"{section}.{setting_key}"

                        if not self._validate_setting(full_key, value):
                            issues.append(
                                {
                                    "key": full_key,
                                    "issue": f"Invalid value: {value}",
                                    "severity": "error",
                                    "suggestion": (
                                        f"Reset to default: "
                                        f"{self._get_default_value(full_key)}"
                                    ),
                                }
                            )

            # Check for missing required settings
            for section, settings in self.DEFAULT_CONFIG_SCHEMA.items():
                if section not in self._config:
                    issues.append(
                        {
                            "key": section,
                            "issue": "Missing configuration section",
                            "severity": "warning",
                            "suggestion": "Reset to default configuration",
                        }
                    )
                elif isinstance(settings, dict):
                    for setting_key in settings:
                        if setting_key not in self._config[section]:
                            full_key = f"{section}.{setting_key}"
                            issues.append(
                                {
                                    "key": full_key,
                                    "issue": "Missing setting",
                                    "severity": "info",
                                    "suggestion": f"Add default value: "
                                    f"{settings[setting_key]}",
                                }
                            )

        except Exception as e:
            issues.append(
                {
                    "key": "general",
                    "issue": f"Configuration validation error: {e}",
                    "severity": "error",
                    "suggestion": "Reset to default configuration",
                }
            )

        return issues

    def reset_to_defaults(self, section: str = None) -> bool:
        """
        Reset configuration to default values.

        Args:
            section: Optional section to reset (resets all if None)

        Returns:
            bool: True if reset successful
        """
        try:
            if section:
                if section in self.DEFAULT_CONFIG_SCHEMA:
                    self._config[section] = self.DEFAULT_CONFIG_SCHEMA[
                        section
                    ].copy()
                else:
                    return False
            else:
                self._config = self.DEFAULT_CONFIG_SCHEMA.copy()

            self._save_config()
            return True

        except Exception as e:
            logging.error(f"Failed to reset configuration: {e}")
            return False

    def export_config(
        self, file_path: str, include_sensitive: bool = False
    ) -> bool:
        """
        Export configuration to file.

        Args:
            file_path: Target export file path
            include_sensitive: Whether to include sensitive settings

        Returns:
            bool: True if export successful
        """
        try:
            export_config = self._config.copy()

            if not include_sensitive:
                # Remove sensitive settings
                sensitive_keys = [
                    "security_settings.key_derivation_iterations",
                    "hub_integration",
                ]

                for key in sensitive_keys:
                    keys = key.split(".")
                    config_ref = export_config

                    for k in keys[:-1]:
                        if k in config_ref:
                            config_ref = config_ref[k]
                        else:
                            break
                    else:
                        if keys[-1] in config_ref:
                            del config_ref[keys[-1]]

            # Add export metadata
            export_data = {
                "export_timestamp": str(Path().cwd()),
                "export_version": "1.0",
                "include_sensitive": include_sensitive,
                "configuration": export_config,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            logging.error(f"Failed to export configuration: {e}")
            return False

    def import_config(self, file_path: str, merge: bool = True) -> bool:
        """
        Import configuration from file.

        Args:
            file_path: Source import file path
            merge: Whether to merge with existing config or replace

        Returns:
            bool: True if import successful

        Raises:
            FileNotFoundError: If import file doesn't exist
            ValueError: If import file format is invalid
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Import file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            # Validate import format
            if "configuration" not in import_data:
                raise ValueError("Invalid import file format")

            imported_config = import_data["configuration"]

            if merge:
                # Merge with existing configuration
                self._merge_config(imported_config)
            else:
                # Replace configuration
                self._config = imported_config

            # Validate imported configuration
            issues = self.validate_settings()
            if any(issue["severity"] == "error" for issue in issues):
                logging.warning("Imported configuration has validation errors")

            self._save_config()
            return True

        except Exception as e:
            logging.error(f"Failed to import configuration: {e}")
            raise

    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing."""
        for section, settings in new_config.items():
            if section not in self._config:
                self._config[section] = {}

            if isinstance(settings, dict):
                for key, value in settings.items():
                    self._config[section][key] = value
            else:
                self._config[section] = settings

    def _sync_with_hub(self):
        """Synchronize configuration with hub."""
        try:
            if self.hub_instance and hasattr(
                self.hub_instance, "sync_tool_config"
            ):
                self.hub_instance.sync_tool_config("encryption", self._config)
        except Exception as e:
            logging.warning(f"Failed to sync config with hub: {e}")

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences section."""
        return self.get_setting("user_preferences", {})

    def get_security_settings(self) -> Dict[str, Any]:
        """Get security settings section."""
        return self.get_setting("security_settings", {})

    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance settings section."""
        return self.get_setting("performance_settings", {})

    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI settings section."""
        return self.get_setting("ui_settings", {})

    def get_hub_settings(self) -> Dict[str, Any]:
        """Get hub integration settings section."""
        return self.get_setting("hub_integration", {})
