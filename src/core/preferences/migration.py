"""Helpers for migrating legacy JSON preferences to PreferenceManager."""

from __future__ import annotations

import logging
from typing import Iterable, Optional, Sequence

try:  # pragma: no cover - PreferenceManager may not be available at import
    from src.core.preferences.manager import PreferenceManager
except Exception:  # pragma: no cover - fallback for circular import/test harness
    PreferenceManager = None  # type: ignore


class PreferenceMigrationHelper:
    """Orchestrate PreferenceManager migrations for legacy ConfigManager keys."""

    _THEME_KEY = ("general", "theme")
    _DEFAULT_DIR_KEY = ("general", "default_directory")
    _RECENT_DIRS_KEY = ("general", "recent_directories")

    def __init__(
        self,
        *,
        preference_manager: Optional[PreferenceManager],
        config_manager,
        logger: logging.Logger,
    ) -> None:
        self._preference_manager = preference_manager
        self._config_manager = config_manager
        self._logger = logger

    # ------------------------------------------------------------------
    # Theme helpers
    # ------------------------------------------------------------------
    def load_theme(self, fallback: str) -> str:
        theme = fallback
        manager = self._preference_manager
        if manager is not None:
            try:
                candidate = manager.get_theme(default=fallback)
            except Exception as exc:  # pragma: no cover - defensive guard
                self._logger.warning(
                    "Unable to load theme from PreferenceManager: %s", exc
                )
            else:
                if isinstance(candidate, str) and candidate.strip():
                    theme = candidate
        return str(theme or "light")

    def save_theme(self, theme: str) -> bool:
        normalized = (theme or "").strip().lower() or "light"
        manager = self._preference_manager
        if manager is not None:
            try:
                manager.set_theme(normalized)
                self._clear_legacy_keys([self._THEME_KEY])
                return True
            except Exception as exc:  # pragma: no cover - defensive guard
                self._logger.warning(
                    "Unable to persist theme via PreferenceManager: %s", exc
                )
        self._clear_legacy_keys([self._THEME_KEY])
        return False

    # ------------------------------------------------------------------
    # Directory helpers
    # ------------------------------------------------------------------
    def load_default_directory(self, fallback: str) -> str:
        manager = self._preference_manager
        if manager is not None:
            try:
                prefs = manager.get_directory_prefs()
            except Exception as exc:  # pragma: no cover - defensive guard
                self._logger.warning(
                    "Unable to load directory prefs from PreferenceManager: %s",
                    exc,
                )
            else:
                if isinstance(prefs, dict):
                    default_root = prefs.get("default_root")
                    if isinstance(default_root, str) and default_root.strip():
                        return default_root
        return str(fallback or "")

    def save_default_directory(self, directory: str) -> bool:
        target = str(directory or "").strip()
        manager = self._preference_manager
        if manager is not None:
            try:
                manager.set_directory_prefs(default_root=target)
                self._clear_legacy_keys([self._DEFAULT_DIR_KEY])
                return True
            except Exception as exc:  # pragma: no cover - defensive guard
                self._logger.warning(
                    "Unable to persist default directory via PreferenceManager: %s",
                    exc,
                )
        self._clear_legacy_keys([self._DEFAULT_DIR_KEY])
        return False

    def load_recent_directories(self, fallback: Sequence[str]) -> list[str]:
        manager = self._preference_manager
        if manager is not None:
            try:
                prefs = manager.get_directory_prefs()
            except Exception as exc:  # pragma: no cover - defensive guard
                self._logger.warning(
                    "Unable to load recent directories via PreferenceManager: %s",
                    exc,
                )
            else:
                if isinstance(prefs, dict):
                    recent = prefs.get("recent")
                    if isinstance(recent, Sequence):
                        return [str(path) for path in recent if path]
        return [str(path) for path in fallback if path]

    def save_recent_directories(self, directories: Sequence[str]) -> bool:
        values = [str(path) for path in directories if str(path)]
        manager = self._preference_manager
        if manager is not None:
            try:
                manager.set_directory_prefs(recent=list(values))
                self._clear_legacy_keys([self._RECENT_DIRS_KEY])
                return True
            except Exception as exc:  # pragma: no cover - defensive guard
                self._logger.warning(
                    "Unable to persist recent directories via PreferenceManager: %s",
                    exc,
                )
        self._clear_legacy_keys([self._RECENT_DIRS_KEY])
        return False

    # ------------------------------------------------------------------
    # Legacy helpers
    # ------------------------------------------------------------------
    def _clear_legacy_keys(self, keys: Iterable[tuple[str, str]]) -> None:
        config = self._config_manager
        if config is None:
            return

        remover = getattr(config, "remove_setting", None)
        for section, key in keys:
            removed = False
            if callable(remover):
                try:
                    removed = bool(remover(section, key))
                except Exception as exc:  # pragma: no cover - defensive guard
                    self._logger.debug(
                        "Failed to remove legacy setting %s.%s: %s",
                        section,
                        key,
                        exc,
                    )
            if removed:
                continue

            # Best-effort manual removal when remove_setting is unavailable
            storage = getattr(config, "config", None)
            if isinstance(storage, dict):
                section_data = storage.get(section)
                if isinstance(section_data, dict) and key in section_data:
                    section_data.pop(key, None)
                    saver = getattr(config, "save_config", None)
                    try:
                        if callable(saver):
                            saver()
                    except Exception:  # pragma: no cover - defensive guard
                        self._logger.debug(
                            "Failed to persist removal of legacy setting %s.%s",
                            section,
                            key,
                            exc_info=True,
                        )


__all__ = ["PreferenceMigrationHelper"]
