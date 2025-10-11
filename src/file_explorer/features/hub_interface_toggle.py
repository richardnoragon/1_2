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
from src.file_explorer.services.preference_service import (
    get_preference_service,
)


class HubInterfaceToggle(QPushButton):
    """Toggle button for switching between hub interface modes."""

    # Signal emitted when mode changes
    mode_changed = pyqtSignal(HubInterfaceMode)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the hub interface toggle button.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.HubInterfaceToggle")
        self.preference_service = get_preference_service()

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
            prefs = self.preference_service.load_preferences()
            self.current_mode = prefs.hub_interface_mode
            self.update_button_text()

            self.logger.debug(f"Loaded interface mode: {self.current_mode.value}")

        except Exception as e:
            self.logger.error(f"Error loading mode: {e}")
            # Default to multi-pane
            self.current_mode = HubInterfaceMode.MULTI_PANE
            self.update_button_text()

    def toggle_mode(self):
        """Toggle between interface modes."""
        try:
            # Toggle mode
            if self.current_mode == HubInterfaceMode.MULTI_PANE:
                new_mode = HubInterfaceMode.TABBED
            else:
                new_mode = HubInterfaceMode.MULTI_PANE

            # Save to preferences
            prefs = self.preference_service.load_preferences()
            prefs.hub_interface_mode = new_mode
            self.preference_service.save_preferences(prefs)

            # Update internal state
            self.current_mode = new_mode
            self.update_button_text()

            # Emit signal for UI to respond
            self.mode_changed.emit(new_mode)

            self.logger.info(f"Switched to mode: {new_mode.value}")

        except Exception as e:
            self.logger.error(f"Error toggling mode: {e}")

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
        if mode != self.current_mode:
            self.toggle_mode()


class HubInterfaceToggleWidget(QWidget):
    """
    Widget wrapper for HubInterfaceToggle with additional controls.

    Provides the toggle button with optional status indicators.
    """

    # Signal emitted when mode changes
    mode_changed = pyqtSignal(HubInterfaceMode)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the toggle widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.HubInterfaceToggleWidget")

        self.setup_ui()

        self.logger.info("HubInterfaceToggleWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        from PyQt5.QtWidgets import QHBoxLayout

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create toggle button
        self.toggle_button = HubInterfaceToggle()
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
