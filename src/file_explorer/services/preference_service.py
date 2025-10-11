"""
PreferenceService: Manage user preferences persistence for Multi-Pane Explorer.

This service handles loading, saving, and resetting user preferences using
the ConfigManager for JSON persistence.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from src.config_manager import get_config_manager
from src.file_explorer.models.user_preferences import UserPreferences


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""

    pass


class ValidationError(ValueError):
    """Raised when preferences validation fails."""

    pass


class PreferenceService:
    """Service for managing user preferences persistence."""

    CONFIG_KEY = "multi_pane_explorer"
    SCHEMA_VERSION = "1.0.0"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the preference service.

        Args:
            config_dir: Optional configuration directory for testing.
                       If None, uses the global ConfigManager.
        """
        self.logger = logging.getLogger("RFU.FileExplorer.PreferenceService")
        self.config_dir = config_dir

        if config_dir:
            # For testing: use a custom config manager
            # Create a temporary config manager that uses the test directory
            self.config_manager = self._create_test_config_manager(config_dir)
        else:
            # Production: use the global config manager
            self.config_manager = get_config_manager()

        self.logger.info("PreferenceService initialized")

    def _create_test_config_manager(self, config_dir: Path):
        """
        Create a test configuration manager for testing.

        Args:
            config_dir: Directory to use for configuration

        Returns:
            ConfigManager-like object for testing
        """
        from src.config_manager import ConfigManager

        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create a config manager instance with custom config path
        config_file = config_dir / "rfu_config.json"

        # Simple config manager mock for testing
        class TestConfigManager:
            def __init__(self, config_file):
                self.config_file = config_file
                self.config = {}
                if config_file.exists():
                    import json

                    try:
                        with open(config_file, "r") as f:
                            self.config = json.load(f)
                    except Exception:
                        self.config = {}

            def get_setting(self, key, default=None):
                return self.config.get(key, default)

            def set_setting(self, key, value):
                self.config[key] = value
                self._save()

            def _save(self):
                import json

                with open(self.config_file, "w") as f:
                    json.dump(self.config, f, indent=2)

        return TestConfigManager(config_file)

    def load_preferences(self) -> UserPreferences:
        """
        Load user preferences from configuration storage.

        Returns:
            UserPreferences: Loaded preferences or defaults if none exist

        Raises:
            ConfigurationError: If validation fails after migration attempts
        """
        try:
            # Get configuration data
            config_data = self.config_manager.get_setting(self.CONFIG_KEY, default=None)

            if config_data is None:
                self.logger.info("No existing configuration found, returning defaults")
                return self._get_default_preferences()

            # Validate schema version
            schema_version = config_data.get("schema_version", "1.0.0")
            if schema_version != self.SCHEMA_VERSION:
                self.logger.warning(
                    f"Schema version mismatch: {schema_version} vs {self.SCHEMA_VERSION}"
                )
                # Apply migrations if needed
                config_data = self._migrate_schema(config_data, schema_version)

            # Convert to UserPreferences object
            try:
                preferences = UserPreferences.from_dict(config_data)
                self.logger.info("Preferences loaded successfully")
                return preferences
            except (ValueError, KeyError, TypeError) as e:
                self.logger.error(f"Failed to parse preferences: {e}")
                raise ConfigurationError(f"Configuration validation failed: {e}") from e

        except ConfigurationError:
            raise
        except Exception as e:
            self.logger.error(f"Error loading preferences: {e}")
            # Return defaults on any error
            return self._get_default_preferences()

    def save_preferences(self, prefs: UserPreferences) -> None:
        """
        Persist user preferences to configuration storage.

        Args:
            prefs: UserPreferences object to save

        Raises:
            ValidationError: If preferences validation fails
            IOError: If write fails
        """
        try:
            # Validate preferences
            if not isinstance(prefs, UserPreferences):
                raise ValidationError(f"Expected UserPreferences, got {type(prefs)}")

            # Convert to dictionary
            prefs_dict = prefs.to_dict()

            # Add schema version
            prefs_dict["schema_version"] = self.SCHEMA_VERSION

            # Save to configuration
            self.config_manager.set_setting(self.CONFIG_KEY, prefs_dict)

            self.logger.info("Preferences saved successfully")

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")
            raise IOError(f"Failed to save preferences: {e}") from e

    def reset_to_defaults(self) -> UserPreferences:
        """
        Reset all preferences to factory defaults.

        Returns:
            UserPreferences: Default preferences
        """
        try:
            self.logger.info("Resetting preferences to defaults")

            # Create default preferences
            defaults = self._get_default_preferences()

            # Save to configuration
            self.save_preferences(defaults)

            self.logger.info("Preferences reset to defaults successfully")
            return defaults

        except Exception as e:
            self.logger.error(f"Error resetting preferences: {e}")
            # Still return defaults even if save failed
            return self._get_default_preferences()

    def _get_default_preferences(self) -> UserPreferences:
        """
        Get default preferences.

        Returns:
            UserPreferences: Factory default preferences
        """
        return UserPreferences.create_defaults()

    def _migrate_schema(self, config_data: dict, from_version: str) -> dict:
        """
        Migrate configuration schema to current version.

        Args:
            config_data: Configuration data to migrate
            from_version: Source schema version

        Returns:
            dict: Migrated configuration data
        """
        self.logger.info(
            f"Migrating schema from {from_version} to {self.SCHEMA_VERSION}"
        )

        # Future migrations will be added here
        # For now, just update the schema version
        config_data["schema_version"] = self.SCHEMA_VERSION

        return config_data


# Singleton instance
_preference_service: Optional[PreferenceService] = None


def get_preference_service() -> PreferenceService:
    """
    Get the singleton preference service instance.

    Returns:
        PreferenceService: The preference service instance
    """
    global _preference_service
    if _preference_service is None:
        _preference_service = PreferenceService()
    return _preference_service
