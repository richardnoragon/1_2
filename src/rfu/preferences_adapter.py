"""Preference adapters bridging GUI interactions to PreferenceManager.

NOTE: The src.file_explorer module has been removed due to stability issues.
This adapter now uses simplified string-based interface mode handling.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Callable, Optional

from src.core.preferences.manager import PreferenceManager


class HubInterfaceMode(Enum):
    """Hub interface mode enumeration.

    Simplified replacement for the removed file_explorer module's
    HubInterfaceMode class.
    """

    TABBED = "tabbed"
    MULTI_PANE = "multi_pane"

    @classmethod
    def from_string(cls, value: str) -> "HubInterfaceMode":
        """Convert a string value to HubInterfaceMode."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.TABBED


ManagerFactory = Callable[[], PreferenceManager]


class HubPreferencesAdapter:
    """Adapter that persists hub-centric preferences via PreferenceManager."""

    _CATEGORY = "module_settings/hub"
    _INTERFACE_KEY = "interface_mode"

    def __init__(
        self,
        *,
        manager_factory: Optional[ManagerFactory] = None,
        legacy_factory: Optional[Callable] = None,
    ) -> None:
        self._logger = logging.getLogger("RFU.HubPreferencesAdapter")
        self._manager_factory = manager_factory or PreferenceManager
        # Legacy factory no longer used - file_explorer removed
        self._legacy_factory = None
        self._manager = self._create_manager(self._manager_factory)

    def _create_manager(self, factory: ManagerFactory) -> Optional[PreferenceManager]:
        try:
            manager = factory()
        except Exception as exc:
            self._logger.debug("PreferenceManager unavailable: %s", exc)
            return None
        return manager

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
            except Exception as exc:
                self._logger.debug("Unable to inspect hub preferences: %s", exc)
            else:
                return self._INTERFACE_KEY in values
        return False

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
            except Exception as exc:
                self._logger.warning("Failed to read hub interface mode: %s", exc)
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
            except Exception as exc:
                self._logger.warning("Unable to persist hub interface mode: %s", exc)
