"""
RightPane: Container for right pane tabs (Preview/Properties).

Provides tab switching between file preview and properties with
automatic updates based on center pane selection.
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from src.file_explorer.models.right_pane_tab import RightPaneTab
from src.file_explorer.services.explorer_preferences import (
    get_explorer_preferences,
)
from src.file_explorer.ui.preview_widget import PreviewWidget
from src.file_explorer.ui.properties_widget import PropertiesWidget


class RightPane(QWidget):
    """Container widget for right pane tabs."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the right pane container.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.RightPane")
        self._preferences = get_explorer_preferences()

        self.setup_ui()
        self.restore_default_tab()

        self.logger.info("RightPane initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create and add tab widgets
        self.preview_widget = PreviewWidget()
        self.properties_widget = PropertiesWidget()

        self.tab_widget.addTab(self.preview_widget, RightPaneTab.PREVIEW.value)
        self.tab_widget.addTab(self.properties_widget, RightPaneTab.PROPERTIES.value)

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tab_widget)

    def restore_default_tab(self):
        """Restore the default tab from preferences."""
        try:
            prefs = self._preferences.load_user_preferences()
            default_tab = getattr(prefs, "right_default_tab", RightPaneTab.PREVIEW)

            # Map tab enum to index
            tab_index_map = {
                RightPaneTab.PREVIEW: 0,
                RightPaneTab.PROPERTIES: 1,
            }

            index = tab_index_map.get(default_tab, 0)  # Default to Preview
            self.tab_widget.setCurrentIndex(index)

            self.logger.debug(f"Restored default tab: {default_tab.value}")

        except Exception as e:
            self.logger.error(f"Error restoring default tab: {e}")
            # Default to Preview tab (index 0)
            self.tab_widget.setCurrentIndex(0)

    def on_tab_changed(self, index: int):
        """
        Handle tab change event.

        Args:
            index: New tab index
        """
        # Map index to tab enum
        tab_map = {
            0: RightPaneTab.PREVIEW,
            1: RightPaneTab.PROPERTIES,
        }

        tab = tab_map.get(index)
        if tab:
            self.logger.debug(f"Right pane tab changed to: {tab.value}")

    def on_file_selected(self, file_path: str):
        """
        Handle file selection from center pane.

        Args:
            file_path: Path to selected file
        """
        try:
            # Update both widgets
            self.preview_widget.preview_file(file_path)
            self.properties_widget.show_properties(file_path)

            self.logger.debug(f"File selected: {file_path}")

        except Exception as e:
            self.logger.error(f"Error handling file selection: {e}")

    def get_preview_widget(self) -> PreviewWidget:
        """Get the preview widget."""
        return self.preview_widget

    def get_properties_widget(self) -> PropertiesWidget:
        """Get the properties widget."""
        return self.properties_widget

    def clear(self):
        """Clear both preview and properties."""
        self.preview_widget.clear()
        self.properties_widget.clear()
