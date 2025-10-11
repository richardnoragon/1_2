"""
BookmarksWidget: Display and manage bookmarks for tools and locations.

Shows bookmarked tools in top section and bookmarked locations in bottom section.
"""

import logging
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.file_explorer.models.bookmark import BookmarkType
from src.file_explorer.services.bookmark_service import get_bookmark_service


class BookmarksWidget(QWidget):
    """Widget displaying bookmarked tools and locations."""

    # Signal emitted when user clicks a bookmark
    bookmark_clicked = pyqtSignal(str, str)  # (type, target)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the bookmarks widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.BookmarksWidget")
        self.bookmark_service = get_bookmark_service()

        self.setup_ui()
        self.load_bookmarks()

        self.logger.info("BookmarksWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for tools/locations sections
        splitter = QSplitter(Qt.Vertical)

        # Tools section
        tools_container = QWidget()
        tools_layout = QVBoxLayout(tools_container)
        tools_layout.setContentsMargins(5, 5, 5, 5)

        tools_label = QLabel("Bookmarked Tools")
        tools_label.setStyleSheet("font-weight: bold;")
        tools_layout.addWidget(tools_label)

        self.tools_list = QListWidget()
        self.tools_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tools_list.customContextMenuRequested.connect(self.show_tools_context_menu)
        self.tools_list.itemDoubleClicked.connect(self.on_tool_clicked)
        tools_layout.addWidget(self.tools_list)

        splitter.addWidget(tools_container)

        # Locations section
        locations_container = QWidget()
        locations_layout = QVBoxLayout(locations_container)
        locations_layout.setContentsMargins(5, 5, 5, 5)

        locations_label = QLabel("Bookmarked Locations")
        locations_label.setStyleSheet("font-weight: bold;")
        locations_layout.addWidget(locations_label)

        self.locations_list = QListWidget()
        self.locations_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.locations_list.customContextMenuRequested.connect(
            self.show_locations_context_menu
        )
        self.locations_list.itemDoubleClicked.connect(self.on_location_clicked)
        locations_layout.addWidget(self.locations_list)

        splitter.addWidget(locations_container)

        # Set initial splitter sizes (50/50)
        splitter.setSizes([1, 1])

        layout.addWidget(splitter)

    def load_bookmarks(self):
        """Load bookmarks from service and populate lists."""
        try:
            # Load tool bookmarks
            self.tools_list.clear()
            tool_bookmarks = self.bookmark_service.get_bookmarks(BookmarkType.TOOL)

            for bookmark in tool_bookmarks:
                item = QListWidgetItem(bookmark.name)
                item.setData(Qt.UserRole, bookmark)
                self.tools_list.addItem(item)

            # Load location bookmarks
            self.locations_list.clear()
            location_bookmarks = self.bookmark_service.get_bookmarks(
                BookmarkType.LOCATION
            )

            for bookmark in location_bookmarks:
                item = QListWidgetItem(bookmark.name)
                item.setData(Qt.UserRole, bookmark)
                item.setToolTip(bookmark.target)
                self.locations_list.addItem(item)

            self.logger.debug(
                f"Loaded {len(tool_bookmarks)} tool bookmarks "
                f"and {len(location_bookmarks)} location bookmarks"
            )

        except Exception as e:
            self.logger.error(f"Error loading bookmarks: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load bookmarks: {e}",
            )

    def show_tools_context_menu(self, position):
        """
        Show context menu for tools list.

        Args:
            position: Menu position
        """
        item = self.tools_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        remove_action = menu.addAction("Remove Bookmark")

        action = menu.exec_(self.tools_list.mapToGlobal(position))

        if action == remove_action:
            self.remove_bookmark(item)

    def show_locations_context_menu(self, position):
        """
        Show context menu for locations list.

        Args:
            position: Menu position
        """
        item = self.locations_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        remove_action = menu.addAction("Remove Bookmark")

        action = menu.exec_(self.locations_list.mapToGlobal(position))

        if action == remove_action:
            self.remove_bookmark(item)

    def remove_bookmark(self, item: QListWidgetItem):
        """
        Remove a bookmark.

        Args:
            item: List widget item containing bookmark
        """
        try:
            bookmark = item.data(Qt.UserRole)
            if bookmark:
                success = self.bookmark_service.delete_bookmark(bookmark.id)
                if success:
                    # Remove from UI
                    if bookmark.bookmark_type == BookmarkType.TOOL:
                        row = self.tools_list.row(item)
                        self.tools_list.takeItem(row)
                    else:
                        row = self.locations_list.row(item)
                        self.locations_list.takeItem(row)

                    self.logger.info(f"Removed bookmark: {bookmark.name}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to remove bookmark")

        except Exception as e:
            self.logger.error(f"Error removing bookmark: {e}")
            QMessageBox.warning(self, "Error", f"Failed to remove bookmark: {e}")

    def on_tool_clicked(self, item: QListWidgetItem):
        """
        Handle tool bookmark click.

        Args:
            item: Clicked item
        """
        bookmark = item.data(Qt.UserRole)
        if bookmark:
            self.bookmark_clicked.emit("tool", bookmark.target)
            self.logger.debug(f"Tool bookmark clicked: {bookmark.name}")

    def on_location_clicked(self, item: QListWidgetItem):
        """
        Handle location bookmark click.

        Args:
            item: Clicked item
        """
        bookmark = item.data(Qt.UserRole)
        if bookmark:
            self.bookmark_clicked.emit("location", bookmark.target)
            self.logger.debug(f"Location bookmark clicked: {bookmark.name}")

    def refresh(self):
        """Refresh the bookmarks display."""
        self.load_bookmarks()
