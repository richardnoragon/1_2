"""
ToolsWidget: Display all RFU tools with search and bookmark functionality.

Shows all available RFU tools with search/filter capability and context
menu to bookmark tools.
"""

import logging
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from src.file_explorer.models.bookmark import Bookmark, BookmarkType
from src.file_explorer.services.bookmark_service import get_bookmark_service
from src.file_explorer.services.tools_discovery_service import (
    get_tools_discovery_service,
)


class ToolsWidget(QWidget):
    """Widget displaying all RFU tools with search."""

    # Signal emitted when user clicks a tool
    tool_clicked = pyqtSignal(str)  # tool_name

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the tools widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.ToolsWidget")
        self.tools_service = get_tools_discovery_service()
        self.bookmark_service = get_bookmark_service()

        self.all_tools = []  # Cache of all tools

        self.setup_ui()
        self.load_tools()

        self.logger.info("ToolsWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tools...")
        self.search_input.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_input)

        # Tools list
        self.tools_list = QListWidget()
        self.tools_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tools_list.customContextMenuRequested.connect(self.show_context_menu)
        self.tools_list.itemDoubleClicked.connect(self.on_tool_clicked)
        layout.addWidget(self.tools_list)

    def load_tools(self):
        """Load tools from service and populate list."""
        try:
            self.all_tools = self.tools_service.get_all_tools()
            self.populate_list(self.all_tools)

            self.logger.debug(f"Loaded {len(self.all_tools)} tools")

        except Exception as e:
            self.logger.error(f"Error loading tools: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load tools: {e}",
            )

    def populate_list(self, tools):
        """
        Populate the list with tools.

        Args:
            tools: List of Tool objects
        """
        self.tools_list.clear()

        for tool in tools:
            item = QListWidgetItem(tool.name)
            item.setData(Qt.ItemDataRole.UserRole, tool)
            item.setToolTip(tool.description)
            self.tools_list.addItem(item)

    def on_search_changed(self, text: str):
        """
        Handle search text change.

        Args:
            text: Search text
        """
        if not text:
            # Show all tools
            self.populate_list(self.all_tools)
        else:
            # Filter tools
            filtered_tools = self.tools_service.search_tools(text)
            self.populate_list(filtered_tools)

    def show_context_menu(self, position):
        """
        Show context menu for tools list.

        Args:
            position: Menu position
        """
        item = self.tools_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        bookmark_action = menu.addAction("Bookmark this tool")

        action = menu.exec_(self.tools_list.mapToGlobal(position))

        if action == bookmark_action:
            self.bookmark_tool(item)

    def bookmark_tool(self, item: QListWidgetItem):
        """
        Bookmark a tool.

        Args:
            item: List widget item containing tool
        """
        try:
            tool = item.data(Qt.ItemDataRole.UserRole)
            if tool:
                # Create bookmark
                bookmark = Bookmark.create(
                    name=tool.name,
                    bookmark_type=BookmarkType.TOOL,
                    target=tool.name,
                )

                saved_bookmark = self.bookmark_service.create_bookmark(bookmark)

                if saved_bookmark:
                    self.logger.info(f"Bookmarked tool: {tool.name}")
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Tool '{tool.name}' bookmarked successfully",
                    )
                else:
                    QMessageBox.warning(self, "Error", "Failed to bookmark tool")

        except Exception as e:
            self.logger.error(f"Error bookmarking tool: {e}")
            QMessageBox.warning(self, "Error", f"Failed to bookmark tool: {e}")

    def on_tool_clicked(self, item: QListWidgetItem):
        """
        Handle tool click - launch the tool.

        Args:
            item: Clicked item
        """
        tool = item.data(Qt.ItemDataRole.UserRole)
        if tool:
            self.tool_clicked.emit(tool.name)
            self.logger.debug(f"Tool clicked: {tool.name}")

    def refresh(self):
        """Refresh the tools display."""
        self.load_tools()
