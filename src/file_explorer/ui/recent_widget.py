"""
RecentWidget: Display recent tools and locations with click-to-launch.

Shows recently used tools in top section and recently visited locations
in bottom section.
"""

import logging
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.file_explorer.models.recent_item import RecentItemType
from src.file_explorer.services.recent_items_service import (
    get_recent_items_service,
)


class RecentWidget(QWidget):
    """Widget displaying recent tools and locations."""

    # Signal emitted when user clicks a recent item
    recent_clicked = pyqtSignal(str, str)  # (type, target)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the recent widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.RecentWidget")
        self.recent_service = get_recent_items_service()

        self.setup_ui()
        self.load_recent_items()

        self.logger.info("RecentWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for tools/locations sections
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Tools section
        tools_container = QWidget()
        tools_layout = QVBoxLayout(tools_container)
        tools_layout.setContentsMargins(5, 5, 5, 5)

        tools_label = QLabel("Recent Tools")
        tools_label.setStyleSheet("font-weight: bold;")
        tools_layout.addWidget(tools_label)

        self.tools_list = QListWidget()
        self.tools_list.itemDoubleClicked.connect(self.on_tool_clicked)
        tools_layout.addWidget(self.tools_list)

        splitter.addWidget(tools_container)

        # Locations section
        locations_container = QWidget()
        locations_layout = QVBoxLayout(locations_container)
        locations_layout.setContentsMargins(5, 5, 5, 5)

        locations_label = QLabel("Recent Locations")
        locations_label.setStyleSheet("font-weight: bold;")
        locations_layout.addWidget(locations_label)

        self.locations_list = QListWidget()
        self.locations_list.itemDoubleClicked.connect(self.on_location_clicked)
        locations_layout.addWidget(self.locations_list)

        splitter.addWidget(locations_container)

        # Set initial splitter sizes (50/50)
        splitter.setSizes([1, 1])

        layout.addWidget(splitter)

    def load_recent_items(self):
        """Load recent items from service and populate lists."""
        try:
            # Load recent tools
            self.tools_list.clear()
            recent_tools = self.recent_service.get_recent_tools()

            for recent_item in recent_tools:
                item = QListWidgetItem(recent_item.name)
                item.setData(Qt.ItemDataRole.UserRole, recent_item)
                item.setToolTip(
                    f"{recent_item.name}\n" f"Last used: {recent_item.timestamp}"
                )
                self.tools_list.addItem(item)

            # Load recent locations
            self.locations_list.clear()
            recent_locations = self.recent_service.get_recent_locations()

            for recent_item in recent_locations:
                item = QListWidgetItem(recent_item.name)
                item.setData(Qt.ItemDataRole.UserRole, recent_item)
                item.setToolTip(recent_item.target)
                self.locations_list.addItem(item)

            self.logger.debug(
                f"Loaded {len(recent_tools)} recent tools "
                f"and {len(recent_locations)} recent locations"
            )

        except Exception as e:
            self.logger.error(f"Error loading recent items: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load recent items: {e}",
            )

    def on_tool_clicked(self, item: QListWidgetItem):
        """
        Handle tool click - launch the tool.

        Args:
            item: Clicked item
        """
        recent_item = item.data(Qt.ItemDataRole.UserRole)
        if recent_item:
            self.recent_clicked.emit("tool", recent_item.target)
            self.logger.debug(f"Recent tool clicked: {recent_item.name}")

    def on_location_clicked(self, item: QListWidgetItem):
        """
        Handle location click - navigate to location.

        Args:
            item: Clicked item
        """
        recent_item = item.data(Qt.ItemDataRole.UserRole)
        if recent_item:
            self.recent_clicked.emit("location", recent_item.target)
            self.logger.debug(f"Recent location clicked: {recent_item.name}")

    def refresh(self):
        """Refresh the recent items display."""
        self.load_recent_items()
