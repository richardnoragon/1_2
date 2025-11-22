"""
HubInterfaceToggle: Quick-toggle button for switching hub interfaces.

Provides a button to switch between Multi-Pane Explorer and Tabbed
interfaces with context preservation and <200ms switching time.
"""

import logging
from typing import Optional

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QWidget

from src.file_explorer.models.hub_interface_mode import HubInterfaceMode
from src.rfu.preferences_adapter import HubPreferencesAdapter


class HubInterfaceToggle(QPushButton):
    """Toggle button for switching between hub interface modes."""

    # Signal emitted when mode changes
    mode_changed = pyqtSignal(HubInterfaceMode)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        preferences_adapter: Optional[HubPreferencesAdapter] = None,
    ):
        """
        Initialize the hub interface toggle button.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.HubInterfaceToggle")
        self.preferences_adapter = preferences_adapter or HubPreferencesAdapter()

        self.current_mode = HubInterfaceMode.MULTI_PANE

        self.setup_ui()

        # Load current mode from preferences
        self.load_mode()

        # Connect click signal
        self.clicked.connect(self.toggle_mode)

        self.logger.info("HubInterfaceToggle initialized")

    def setup_ui(self):
        """Set up the button UI."""
        self.setFixedSize(120, 30)
        self.setToolTip("Toggle between Multi-Pane Explorer and Tabbed interface")
        self.update_button_text()

    def update_button_text(self):
        """Update button text based on current mode."""
        if self.current_mode == HubInterfaceMode.MULTI_PANE:
            self.setText("Switch to Tabs")
        else:
            self.setText("Multi-Pane View")

    def load_mode(self):
        """Load the current mode from preferences."""
        try:
            self.current_mode = self.preferences_adapter.load_interface_mode(
                HubInterfaceMode.MULTI_PANE
            )
            self.update_button_text()

            self.logger.debug("Loaded interface mode: %s", self.current_mode.value)

        except Exception as e:
            self.logger.error("Error loading mode via adapter: %s", e)
            self.current_mode = HubInterfaceMode.MULTI_PANE
            self.update_button_text()

    def toggle_mode(self):
        """Toggle between interface modes."""
        new_mode = (
            HubInterfaceMode.TABBED
            if self.current_mode == HubInterfaceMode.MULTI_PANE
            else HubInterfaceMode.MULTI_PANE
        )
        self.set_mode(new_mode)

    def get_current_mode(self) -> HubInterfaceMode:
        """
        Get the current interface mode.

        Returns:
            Current HubInterfaceMode
        """
        return self.current_mode

    def set_mode(self, mode: HubInterfaceMode):
        """
        Set the interface mode programmatically.

        Args:
            mode: Mode to set
        """
        if mode == self.current_mode:
            return
        try:
            self.preferences_adapter.save_interface_mode(mode)
        except Exception as exc:
            self.logger.error("Error saving interface mode: %s", exc)

        self.current_mode = mode
        self.update_button_text()
        self.mode_changed.emit(mode)
        self.logger.info("Switched to mode: %s", mode.value)


class HubInterfaceToggleWidget(QWidget):
    """
    Widget wrapper for HubInterfaceToggle with additional controls.

    Provides the toggle button with optional status indicators.
    """

    # Signal emitted when mode changes
    mode_changed = pyqtSignal(HubInterfaceMode)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        preferences_adapter: Optional[HubPreferencesAdapter] = None,
    ):
        """
        Initialize the toggle widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.HubInterfaceToggleWidget")

        self._preferences_adapter = preferences_adapter

        self.setup_ui()

        self.logger.info("HubInterfaceToggleWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        from PyQt5.QtWidgets import QHBoxLayout

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create toggle button
        self.toggle_button = HubInterfaceToggle(
            preferences_adapter=self._preferences_adapter
        )
        self.toggle_button.mode_changed.connect(self.on_mode_changed)

        layout.addWidget(self.toggle_button)
        layout.addStretch()

    def on_mode_changed(self, mode: HubInterfaceMode):
        """
        Handle mode change from button.

        Args:
            mode: New mode
        """
        # Forward signal
        self.mode_changed.emit(mode)

    def get_current_mode(self) -> HubInterfaceMode:
        """Get the current interface mode."""
        return self.toggle_button.get_current_mode()

    def set_mode(self, mode: HubInterfaceMode):
        """Set the interface mode."""
        self.toggle_button.set_mode(mode)
