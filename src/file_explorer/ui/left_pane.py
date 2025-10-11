"""
LeftPane: Container for left pane tabs (Bookmarks/Recent/Tools).

Provides tab switching between bookmarks, recent items, and tools
with preference restoration.
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from src.file_explorer.models.left_pane_tab import LeftPaneTab
from src.file_explorer.services.preference_service import (
    get_preference_service,
)
from src.file_explorer.ui.bookmarks_widget import BookmarksWidget
from src.file_explorer.ui.recent_widget import RecentWidget
from src.file_explorer.ui.tools_widget import ToolsWidget


class LeftPane(QWidget):
    """Container widget for left pane tabs."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the left pane container.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.LeftPane")
        self.preference_service = get_preference_service()

        self.setup_ui()
        self.restore_default_tab()

        self.logger.info("LeftPane initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create and add tab widgets
        self.bookmarks_widget = BookmarksWidget()
        self.recent_widget = RecentWidget()
        self.tools_widget = ToolsWidget()

        self.tab_widget.addTab(self.bookmarks_widget, LeftPaneTab.BOOKMARKS.value)
        self.tab_widget.addTab(self.recent_widget, LeftPaneTab.RECENT.value)
        self.tab_widget.addTab(self.tools_widget, LeftPaneTab.TOOLS.value)

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tab_widget)

    def restore_default_tab(self):
        """Restore the default tab from preferences."""
        try:
            prefs = self.preference_service.load_preferences()
            default_tab = prefs.default_left_tab

            # Map tab enum to index
            tab_index_map = {
                LeftPaneTab.BOOKMARKS: 0,
                LeftPaneTab.RECENT: 1,
                LeftPaneTab.TOOLS: 2,
            }

            index = tab_index_map.get(default_tab, 1)  # Default to Recent
            self.tab_widget.setCurrentIndex(index)

            self.logger.debug(f"Restored default tab: {default_tab.value}")

        except Exception as e:
            self.logger.error(f"Error restoring default tab: {e}")
            # Default to Recent tab (index 1)
            self.tab_widget.setCurrentIndex(1)

    def on_tab_changed(self, index: int):
        """
        Handle tab change event.

        Args:
            index: New tab index
        """
        # Map index to tab enum
        tab_map = {
            0: LeftPaneTab.BOOKMARKS,
            1: LeftPaneTab.RECENT,
            2: LeftPaneTab.TOOLS,
        }

        tab = tab_map.get(index)
        if tab:
            self.logger.debug(f"Left pane tab changed to: {tab.value}")

    def get_bookmarks_widget(self) -> BookmarksWidget:
        """Get the bookmarks widget."""
        return self.bookmarks_widget

    def get_recent_widget(self) -> RecentWidget:
        """Get the recent widget."""
        return self.recent_widget

    def get_tools_widget(self) -> ToolsWidget:
        """Get the tools widget."""
        return self.tools_widget

    def refresh(self):
        """Refresh all tab widgets."""
        self.bookmarks_widget.refresh()
        self.recent_widget.refresh()
        self.tools_widget.refresh()
