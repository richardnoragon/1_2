"""Preference adapters bridging GUI interactions to PreferenceManager."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from src.core.preferences.manager import PreferenceManager
from src.file_explorer.models.hub_interface_mode import HubInterfaceMode
from src.file_explorer.services.explorer_preferences import (
    ExplorerPreferences,
    get_explorer_preferences,
)

ManagerFactory = Callable[[], PreferenceManager]
LegacyFactory = Callable[[], ExplorerPreferences]


class HubPreferencesAdapter:
    """Adapter that persists hub-centric preferences via PreferenceManager."""

    _CATEGORY = "module_settings/hub"
    _INTERFACE_KEY = "interface_mode"

    def __init__(
        self,
        *,
        manager_factory: Optional[ManagerFactory] = None,
        legacy_factory: Optional[LegacyFactory] = None,
    ) -> None:
        self._logger = logging.getLogger("RFU.HubPreferencesAdapter")
        self._manager_factory = manager_factory or PreferenceManager
        self._legacy_factory = legacy_factory
        self._manager = self._create_manager(self._manager_factory)
        self._legacy_preferences: Optional[ExplorerPreferences] = None

    def _create_manager(self, factory: ManagerFactory) -> Optional[PreferenceManager]:
        try:
            manager = factory()
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._logger.debug("PreferenceManager unavailable: %s", exc)
            return None
        return manager

    def _get_legacy_preferences(self) -> Optional[ExplorerPreferences]:
        if self._legacy_preferences is not None:
            return self._legacy_preferences

        factory = self._legacy_factory or get_explorer_preferences

        try:
            self._legacy_preferences = factory()
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._logger.debug("Legacy explorer preferences unavailable: %s", exc)
            self._legacy_preferences = None

        return self._legacy_preferences

    def is_available(self) -> bool:
        """Return True when the PreferenceManager dependency is ready."""

        return self._manager is not None

    # ------------------------------------------------------------------
    # Hub interface mode helpers
    # ------------------------------------------------------------------
    def has_interface_mode(self) -> bool:
        """Return True when an interface mode preference is stored."""

        if self._manager:
            try:
                values = self._manager.get_category(self._CATEGORY)
            except Exception as exc:  # pragma: no cover - defensive fallback
                self._logger.debug(
                    "Unable to inspect hub preferences; assuming missing: %s",
                    exc,
                )
            else:
                return self._INTERFACE_KEY in values

        legacy = self._get_legacy_preferences()
        if not legacy:
            return False
        try:
            prefs = legacy.load_user_preferences()
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._logger.debug(
                "Legacy preference load failed while checking interface mode: %s",
                exc,
            )
            return False
        mode = getattr(prefs, "hub_interface_mode", None) or getattr(
            prefs, "active_hub_mode", None
        )
        return isinstance(mode, HubInterfaceMode)

    def load_interface_mode(self, default: HubInterfaceMode) -> HubInterfaceMode:
        """Load the persisted interface mode or return *default*."""

        if self._manager:
            try:
                raw_value = self._manager.get(
                    self._CATEGORY,
                    self._INTERFACE_KEY,
                    default.value,
                )
                return HubInterfaceMode(raw_value)
            except Exception as exc:  # pragma: no cover - defensive fallback
                self._logger.warning(
                    "Failed to read hub interface mode preference; falling back: %s",
                    exc,
                )

        return self._load_interface_mode_legacy(default)

    def _load_interface_mode_legacy(
        self, default: HubInterfaceMode
    ) -> HubInterfaceMode:
        legacy = self._get_legacy_preferences()
        if not legacy:
            return default
        try:
            prefs = legacy.load_user_preferences()
            mode = getattr(prefs, "hub_interface_mode", None) or getattr(
                prefs, "active_hub_mode", None
            )
            if isinstance(mode, HubInterfaceMode):
                return mode
            if isinstance(mode, str):
                return HubInterfaceMode.from_string(mode)
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._logger.warning(
                "Legacy preference load failed; using default interface mode: %s",
                exc,
            )
        return default

    def save_interface_mode(self, mode: HubInterfaceMode) -> None:
        """Persist the supplied interface *mode* when possible."""

        if self._manager:
            try:
                self._manager.set(
                    self._CATEGORY,
                    self._INTERFACE_KEY,
                    mode.value,
                )
                return
            except Exception as exc:  # pragma: no cover - defensive fallback
                self._logger.warning(
                    "Unable to persist hub interface mode via manager;"
                    " falling back: %s",
                    exc,
                )

        self._save_interface_mode_legacy(mode)

    def _save_interface_mode_legacy(self, mode: HubInterfaceMode) -> None:
        legacy = self._get_legacy_preferences()
        if not legacy:
            return
        try:
            prefs = legacy.load_user_preferences()
            target_attr = "hub_interface_mode"
            if hasattr(prefs, "hub_interface_mode"):
                target_attr = "hub_interface_mode"
            elif hasattr(prefs, "active_hub_mode"):
                target_attr = "active_hub_mode"
            setattr(prefs, target_attr, mode)
            legacy.save_user_preferences(prefs)
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._logger.warning(
                "Legacy preference persistence failed; mode '%s' not saved: %s",
                mode.value,
                exc,
            )
