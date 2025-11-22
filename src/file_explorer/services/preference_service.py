"""PreferenceService backed by the canonical PreferenceManager."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from src.file_explorer.models.user_preferences import UserPreferences

from .explorer_preferences import ExplorerPreferences


class ValidationError(ValueError):
    """Raised when preferences validation fails."""


class PreferenceService:
    """Compatibility wrapper that delegates to :class:`ExplorerPreferences`."""

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        *,
        explorer_preferences: Optional[ExplorerPreferences] = None,
    ) -> None:
        self.logger = logging.getLogger("RFU.FileExplorer.PreferenceService")
        self.preferences = explorer_preferences or ExplorerPreferences(
            config_dir=config_dir
        )

    def load_preferences(self) -> UserPreferences:
        """Return stored explorer preferences or defaults on failure."""

        try:
            prefs = self.preferences.load_user_preferences()
            self.logger.info("Explorer preferences loaded")
            return prefs
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Error loading explorer preferences: %s", exc)
            return UserPreferences.create_defaults()

    def save_preferences(self, prefs: UserPreferences) -> None:
        """Persist explorer preferences via the canonical preference store."""

        if not isinstance(prefs, UserPreferences):
            raise ValidationError(f"Expected UserPreferences, got {type(prefs)}")

        try:
            self.preferences.save_user_preferences(prefs)
            self.logger.info("Explorer preferences saved")
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Error saving explorer preferences: %s", exc)
            raise

    def reset_to_defaults(self) -> UserPreferences:
        """Reset explorer preferences to defaults and persist them."""

        try:
            defaults = self.preferences.reset_to_defaults()
            self.logger.info("Explorer preferences reset to defaults")
            return defaults
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Error resetting explorer preferences: %s", exc)
            return UserPreferences.create_defaults()


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
