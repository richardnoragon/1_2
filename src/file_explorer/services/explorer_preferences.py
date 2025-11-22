"""Explorer preference persistence backed by PreferenceManager.

Provides a small facade around :class:`PreferenceManager` so explorer-facing
services can read and write the consolidated ``UserPreferences`` model without
having to know about the underlying storage details.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from src.config_manager import get_config_manager
from src.core.preferences.manager import PreferenceManager
from src.core.preferences.store import PreferencesStore
from src.database.database_manager import DatabaseManager
from src.file_explorer.models.user_preferences import UserPreferences

_LOGGER = logging.getLogger("RFU.FileExplorer.ExplorerPreferences")


class ExplorerPreferences:
    """Typed accessor for explorer-specific preferences."""

    CATEGORY = "module_settings/explorer/preferences"
    KEY_STATE = "state"
    SCHEMA_VERSION = "2.0.0"

    def __init__(
        self,
        *,
        manager: Optional[PreferenceManager] = None,
        store: Optional[PreferencesStore] = None,
        config_dir: Optional[Path] = None,
        user_id: Optional[str] = None,
    ) -> None:
        self._config_dir = Path(config_dir) if config_dir else None

        if manager is not None:
            self.manager = manager
        else:
            if store is None:
                store = self._create_store(config_dir=self._config_dir)
            self.manager = PreferenceManager(store=store, user_id=user_id)

        self.store = self.manager.store

    # ------------------------------------------------------------------
    # Public API
    def load_user_preferences(self) -> UserPreferences:
        """Load the explorer preference payload from the preference store."""

        payload = self._load_state_payload()
        if payload is not None:
            try:
                return UserPreferences.from_dict(payload)
            except Exception as exc:  # noqa: BLE001
                _LOGGER.warning("Explorer preference payload invalid: %s", exc)
                self._delete_state()

        fallback = self._load_from_config_manager()
        if fallback is not None:
            try:
                self.save_user_preferences(fallback)
            except Exception:  # noqa: BLE001
                _LOGGER.debug(
                    "Failed to persist config-manager explorer fallback",
                    exc_info=True,
                )
            return fallback

        return UserPreferences.create_defaults()

    def save_user_preferences(self, prefs: UserPreferences) -> None:
        """Persist the consolidated explorer preferences."""

        if not isinstance(prefs, UserPreferences):
            raise TypeError("Expected UserPreferences instance")

        payload = prefs.to_dict()
        payload["schema_version"] = self.SCHEMA_VERSION
        self.manager.set(self.CATEGORY, self.KEY_STATE, payload)

    def reset_to_defaults(self) -> UserPreferences:
        """Reset preferences to defaults and persist them."""

        defaults = UserPreferences.create_defaults()
        self.save_user_preferences(defaults)
        return defaults

    # ------------------------------------------------------------------
    # Internals
    def _load_state_payload(self) -> Optional[Dict[str, Any]]:
        raw = self.manager.get(self.CATEGORY, self.KEY_STATE, default=None)
        if isinstance(raw, dict):
            payload = dict(raw)
            payload.pop("schema_version", None)
            return payload
        if raw is not None:
            _LOGGER.debug("Unexpected explorer preference payload type: %s", type(raw))
        return None

    def _delete_state(self) -> None:
        try:
            self.store.delete(self.manager.user_id, self.CATEGORY, self.KEY_STATE)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Unable to delete explorer preference state", exc_info=True)

    def _load_from_config_manager(self) -> Optional[UserPreferences]:
        """Fallback to legacy JSON configuration if still present."""

        config_manager = self._resolve_config_manager()
        if config_manager is None:
            return None

        try:
            data = config_manager.get_setting("multi_pane_explorer", default=None)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Config manager unavailable for explorer fallback")
            return None

        if data is None:
            return None

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return None

        if not isinstance(data, dict):
            return None

        data = dict(data)
        data.pop("schema_version", None)

        try:
            return UserPreferences.from_dict(data)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Config manager explorer payload invalid", exc_info=True)
            return None

    def _resolve_config_manager(self):
        if self._config_dir is None:
            return get_config_manager()
        return self._create_test_config_manager(self._config_dir)

    @staticmethod
    def _create_test_config_manager(config_dir: Path):
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "rfu_config.json"

        class TestConfigManager:
            def __init__(self, config_file: Path):
                self.config_file = config_file
                self.config = {}
                if config_file.exists():
                    try:
                        self.config = json.loads(config_file.read_text())
                    except Exception:  # noqa: BLE001
                        self.config = {}

            def get_setting(self, key, default=None):
                return self.config.get(key, default)

            def set_setting(self, key, value):
                self.config[key] = value
                with open(self.config_file, "w", encoding="utf-8") as handle:
                    json.dump(self.config, handle, indent=2)

        return TestConfigManager(config_file)

    @staticmethod
    def _create_store(config_dir: Optional[Path]) -> PreferencesStore:
        if config_dir is None:
            return PreferencesStore()

        db_path = Path(config_dir) / "rfu_preferences.db"
        instance = getattr(DatabaseManager, "_instance", None)
        if instance is None:
            manager = DatabaseManager(db_path)
        else:
            manager = DatabaseManager()
            current_path = getattr(manager, "db_file", None)
            if current_path != db_path:
                manager.close_all_connections()
                DatabaseManager._instance = None
                manager = DatabaseManager(db_path)
        return PreferencesStore(manager)


_EXPLORER_PREFS_SINGLETON: Optional["ExplorerPreferences"] = None


def get_explorer_preferences() -> "ExplorerPreferences":
    """Return the shared :class:`ExplorerPreferences` instance."""

    global _EXPLORER_PREFS_SINGLETON
    if _EXPLORER_PREFS_SINGLETON is None:
        _EXPLORER_PREFS_SINGLETON = ExplorerPreferences()
    return _EXPLORER_PREFS_SINGLETON


__all__ = ["ExplorerPreferences", "get_explorer_preferences"]
