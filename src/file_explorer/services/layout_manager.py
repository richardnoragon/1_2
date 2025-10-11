"""
LayoutManager: Orchestrate pane layout configuration.

This service manages the arrangement and state of center panes in the
Multi-Pane Explorer.
"""

import logging
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from src.file_explorer.models.pane_configuration import PaneConfiguration
from src.file_explorer.services.preference_service import (
    PreferenceService,
    get_preference_service,
)


class LayoutManager(QObject):
    """Service for orchestrating pane layout configuration."""

    # Signal emitted when layout changes
    layout_changed = pyqtSignal(PaneConfiguration)

    def __init__(self, preference_service=None, config_dir=None):
        """
        Initialize the layout manager.

        Args:
            preference_service: Optional PreferenceService instance
            config_dir: Optional configuration directory for testing
        """
        super().__init__()

        self.logger = logging.getLogger("RFU.FileExplorer.LayoutManager")

        if config_dir:
            self.preference_service = PreferenceService(config_dir)
        else:
            self.preference_service = preference_service or get_preference_service()

        self._current_config: Optional[PaneConfiguration] = None
        self.logger.info("LayoutManager initialized")

    def apply_configuration(self, config: PaneConfiguration) -> None:
        """
        Apply a pane configuration to the UI.

        Args:
            config: Pane configuration to apply

        Raises:
            ValueError: If configuration invalid
        """
        try:
            # Validate configuration
            config.validate()

            # Store current configuration
            self._current_config = config

            # Emit layout changed signal
            self.layout_changed.emit(config)

            # Persist configuration
            prefs = self.preference_service.load_preferences()
            prefs.pane_config = config
            self.preference_service.save_preferences(prefs)

            self.logger.info(
                f"Applied configuration: {config.pane_count} panes, "
                f"{config.layout_type.value} layout"
            )

        except (ValueError, AttributeError) as e:
            self.logger.error(f"Invalid configuration: {e}")
            raise ValueError(f"Invalid configuration: {e}") from e
        except Exception as e:
            self.logger.error(f"Error applying configuration: {e}")
            raise

    def get_current_configuration(self) -> PaneConfiguration:
        """
        Get the active pane configuration.

        Returns:
            PaneConfiguration: Current configuration
        """
        if self._current_config is None:
            # Load from preferences
            try:
                prefs = self.preference_service.load_preferences()
                self._current_config = prefs.pane_config
            except Exception as e:
                self.logger.error(f"Error loading current configuration: {e}")
                # Return default
                from src.file_explorer.models.pane_configuration import (
                    LayoutType,
                )

                self._current_config = PaneConfiguration(1, LayoutType.DISABLED, {})

        return self._current_config

    def save_splitter_states(
        self, splitter_states: Optional[dict[str, bytes]] = None
    ) -> None:
        """
        Capture current splitter positions.

        Args:
            splitter_states: Optional dictionary mapping splitter names to
                           saved states. If None, current states preserved.
        """
        try:
            # Get current configuration
            current_config = self.get_current_configuration()

            # Update splitter states if provided
            if splitter_states:
                current_config.splitter_states.update(splitter_states)

            # Persist immediately
            prefs = self.preference_service.load_preferences()
            prefs.pane_config = current_config
            self.preference_service.save_preferences(prefs)

            state_count = len(splitter_states) if splitter_states else 0
            self.logger.debug(f"Saved {state_count} splitter states")

        except Exception as e:
            self.logger.error(f"Error saving splitter states: {e}")


# Singleton instance
_layout_manager: Optional[LayoutManager] = None


def get_layout_manager() -> LayoutManager:
    """
    Get the singleton layout manager instance.

    Returns:
        LayoutManager: The layout manager instance
    """
    global _layout_manager
    if _layout_manager is None:
        _layout_manager = LayoutManager()
    return _layout_manager
