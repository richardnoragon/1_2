"""
Recent Tab Widget for Multi-Pane File Explorer

This module implements a comprehensive Recent tab that displays:
1. Upper section: Recently accessed directories and file locations
2. Lower section: Recently used tools and utilities

Features:
- Chronologically ordered lists with timestamps
- Hover tooltips with full path information
- Right-click context menus for pinning functionality
- Configurable history limits
- Automatic cleanup of inaccessible locations
- Visual consistency with existing tabs
- Quick navigation and one-click relaunch functionality
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class RecentTabWidget(QWidget):
    """
    Comprehensive Recent tab widget with vertically split layout.

    Features:
    - Upper section: Recent directories with navigation
    - Lower section: Recent tools with relaunch functionality
    - Data persistence and automatic cleanup
    - Interactive features (tooltips, context menus, pinning)
    """

    # Signals
    directoryNavigationRequested = pyqtSignal(str)  # path
    toolLaunchRequested = pyqtSignal(str, str)  # tool_name, module_path
    itemPinned = pyqtSignal(str, str)  # item_type, item_path
    itemUnpinned = pyqtSignal(str, str)  # item_type, item_path

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)

        # Configuration
        self.config_manager = config_manager
        self.logger = logging.getLogger("RFU.RecentTab")

        # Data storage
        self.recent_directories: List[Dict] = []
        self.recent_tools: List[Dict] = []
        self.pinned_directories: List[str] = []
        self.pinned_tools: List[str] = []

        # Configuration settings
        self.max_recent_directories = 50
        self.max_recent_tools = 30
        self.cleanup_interval_hours = 24
        self.max_item_age_days = 30

        # UI components
        self.directories_tree = None
        self.tools_tree = None
        self.splitter = None

        # Initialize
        self._setup_ui()
        self._load_configuration()
        self._load_recent_data()
        self._setup_cleanup_timer()

        self.logger.info("RecentTabWidget initialized successfully")

    def _setup_ui(self):
        """Setup the user interface with vertically split layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create vertical splitter
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)

        # Create upper section (recent directories)
        directories_section = self._create_directories_section()
        self.splitter.addWidget(directories_section)

        # Create lower section (recent tools)
        tools_section = self._create_tools_section()
        self.splitter.addWidget(tools_section)

        # Set initial splitter sizes (60% directories, 40% tools)
        self.splitter.setSizes([300, 200])

        main_layout.addWidget(self.splitter)

        # Apply consistent styling
        self._apply_styling()

    def _create_directories_section(self):
        """Create the upper section for recent directories."""
        # Container frame
        container = QFrame()
        container.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header with title and controls
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("📁 Recent Directories")
        title_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                padding: 4px;
            }
        """
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Clear button
        clear_dirs_btn = QPushButton("Clear")
        clear_dirs_btn.setMaximumWidth(60)
        clear_dirs_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """
        )
        clear_dirs_btn.clicked.connect(self._clear_recent_directories)
        header_layout.addWidget(clear_dirs_btn)

        layout.addLayout(header_layout)

        # Directory tree widget
        self.directories_tree = QTreeWidget()
        self.directories_tree.setHeaderLabels(
            ["Path", "Last Accessed", "Access Count"]
        )
        self.directories_tree.setAlternatingRowColors(True)
        self.directories_tree.setSortingEnabled(True)
        self.directories_tree.setRootIsDecorated(False)

        # Configure column widths
        header = self.directories_tree.header()
        header.resizeSection(0, 220)  # Path
        header.resizeSection(1, 100)  # Last Accessed
        header.resizeSection(2, 80)  # Access Count
        header.setStretchLastSection(False)

        # Connect signals
        self.directories_tree.itemDoubleClicked.connect(
            self._on_directory_activated
        )
        self.directories_tree.itemEntered.connect(self._show_directory_tooltip)

        # Enable custom context menu
        self.directories_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.directories_tree.customContextMenuRequested.connect(
            self._show_directory_context_menu
        )

        layout.addWidget(self.directories_tree, 1)

        return container

    def _create_tools_section(self):
        """Create the lower section for recent tools."""
        # Container frame
        container = QFrame()
        container.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header with title and controls
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("🔧 Recent Tools")
        title_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                padding: 4px;
            }
        """
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Clear button
        clear_tools_btn = QPushButton("Clear")
        clear_tools_btn.setMaximumWidth(60)
        clear_tools_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """
        )
        clear_tools_btn.clicked.connect(self._clear_recent_tools)
        header_layout.addWidget(clear_tools_btn)

        layout.addLayout(header_layout)

        # Tools tree widget
        self.tools_tree = QTreeWidget()
        self.tools_tree.setHeaderLabels(
            ["Tool Name", "Category", "Last Used", "Usage Count"]
        )
        self.tools_tree.setAlternatingRowColors(True)
        self.tools_tree.setSortingEnabled(True)
        self.tools_tree.setRootIsDecorated(False)

        # Configure column widths
        header = self.tools_tree.header()
        header.resizeSection(0, 140)  # Tool Name
        header.resizeSection(1, 100)  # Category
        header.resizeSection(2, 100)  # Last Used
        header.resizeSection(3, 80)  # Usage Count
        header.setStretchLastSection(False)

        # Connect signals
        self.tools_tree.itemDoubleClicked.connect(self._on_tool_activated)
        self.tools_tree.itemEntered.connect(self._show_tool_tooltip)

        # Enable custom context menu
        self.tools_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tools_tree.customContextMenuRequested.connect(
            self._show_tool_context_menu
        )

        layout.addWidget(self.tools_tree, 1)

        return container

    def _apply_styling(self):
        """Apply consistent styling to match existing tabs."""
        # Main widget styling
        self.setStyleSheet(
            """
            QWidget {
                background-color: #ffffff;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 12px;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e1e8ed;
                border-radius: 4px;
            }
        """
        )

        # Tree widget styling
        tree_style = """
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e1e8ed;
                selection-background-color: #007ACC;
                selection-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #e9ecef;
                font-size: 11px;
            }
            QTreeWidget::item {
                height: 24px;
                padding: 2px 4px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #007ACC;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
            }
            QTreeWidget::item:alternate {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                border: 1px solid #e1e8ed;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 11px;
            }
        """

        if self.directories_tree:
            self.directories_tree.setStyleSheet(tree_style)
        if self.tools_tree:
            self.tools_tree.setStyleSheet(tree_style)

    def _load_configuration(self):
        """Load configuration settings."""
        if self.config_manager:
            try:
                recent_config = (
                    self.config_manager.get_section("recent_tab") or {}
                )

                self.max_recent_directories = recent_config.get(
                    "max_directories", 50
                )
                self.max_recent_tools = recent_config.get("max_tools", 30)
                self.cleanup_interval_hours = recent_config.get(
                    "cleanup_interval_hours", 24
                )
                self.max_item_age_days = recent_config.get(
                    "max_item_age_days", 30
                )

                self.logger.info(
                    f"Configuration loaded: max_dirs={self.max_recent_directories}, max_tools={self.max_recent_tools}"
                )

            except Exception as e:
                self.logger.warning(f"Error loading configuration: {e}")

    def _load_recent_data(self):
        """Load recent data from persistent storage."""
        try:
            # Get data directory
            data_dir = self._get_data_directory()
            recent_file = data_dir / "recent_data.json"

            if recent_file.exists():
                with open(recent_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.recent_directories = data.get("directories", [])
                self.recent_tools = data.get("tools", [])
                self.pinned_directories = data.get("pinned_directories", [])
                self.pinned_tools = data.get("pinned_tools", [])

                # Cleanup old data
                self._cleanup_old_data()

                # Refresh displays
                self._refresh_directories_display()
                self._refresh_tools_display()

                self.logger.info(
                    f"Loaded {len(self.recent_directories)} directories and {len(self.recent_tools)} tools"
                )
            else:
                self.logger.info("No recent data file found, starting fresh")

        except Exception as e:
            self.logger.error(f"Error loading recent data: {e}")

    def _save_recent_data(self):
        """Save recent data to persistent storage."""
        try:
            data_dir = self._get_data_directory()
            data_dir.mkdir(parents=True, exist_ok=True)

            recent_file = data_dir / "recent_data.json"

            data = {
                "directories": self.recent_directories,
                "tools": self.recent_tools,
                "pinned_directories": self.pinned_directories,
                "pinned_tools": self.pinned_tools,
                "last_updated": datetime.now().isoformat(),
            }

            with open(recent_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug("Recent data saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving recent data: {e}")

    def _get_data_directory(self) -> Path:
        """Get the data directory for storing recent data."""
        if self.config_manager and hasattr(
            self.config_manager, "get_config_dir"
        ):
            config_dir = Path(self.config_manager.get_config_dir())
        else:
            # Fallback to user config directory
            config_dir = Path.home() / ".rfu"

        return config_dir / "recent"

    def _setup_cleanup_timer(self):
        """Setup timer for automatic cleanup of old data."""
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_old_data)
        # Run cleanup every hour
        self.cleanup_timer.start(self.cleanup_interval_hours * 60 * 60 * 1000)

    def _cleanup_old_data(self):
        """Remove old and inaccessible items from recent data."""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(days=self.max_item_age_days)

            # Cleanup directories
            cleaned_dirs = []
            for dir_data in self.recent_directories:
                try:
                    # Check if directory still exists
                    dir_path = Path(dir_data["path"])
                    if not dir_path.exists():
                        self.logger.debug(
                            f"Removing inaccessible directory: {dir_data['path']}"
                        )
                        continue

                    # Check age
                    last_accessed = datetime.fromisoformat(
                        dir_data["last_accessed"]
                    )
                    if (
                        last_accessed < cutoff_time
                        and dir_data["path"] not in self.pinned_directories
                    ):
                        self.logger.debug(
                            f"Removing old directory: {dir_data['path']}"
                        )
                        continue

                    cleaned_dirs.append(dir_data)

                except Exception as e:
                    self.logger.warning(
                        f"Error checking directory {dir_data.get('path')}: {e}"
                    )
                    continue

            # Cleanup tools (tools don't have accessibility check, just age)
            cleaned_tools = []
            for tool_data in self.recent_tools:
                try:
                    last_used = datetime.fromisoformat(tool_data["last_used"])
                    if (
                        last_used < cutoff_time
                        and tool_data["name"] not in self.pinned_tools
                    ):
                        self.logger.debug(
                            f"Removing old tool: {tool_data['name']}"
                        )
                        continue

                    cleaned_tools.append(tool_data)

                except Exception as e:
                    self.logger.warning(
                        f"Error checking tool {tool_data.get('name')}: {e}"
                    )
                    continue

            # Update data
            dirs_removed = len(self.recent_directories) - len(cleaned_dirs)
            tools_removed = len(self.recent_tools) - len(cleaned_tools)

            self.recent_directories = cleaned_dirs
            self.recent_tools = cleaned_tools

            if dirs_removed > 0 or tools_removed > 0:
                self.logger.info(
                    f"Cleanup completed: removed {dirs_removed} directories and {tools_removed} tools"
                )
                self._save_recent_data()
                self._refresh_directories_display()
                self._refresh_tools_display()

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def add_recent_directory(self, path: str):
        """Add a directory to the recent list."""
        try:
            dir_path = Path(path)
            if not dir_path.exists() or not dir_path.is_dir():
                return

            path_str = str(dir_path.resolve())
            current_time = datetime.now()

            # Check if already exists
            existing_index = -1
            for i, dir_data in enumerate(self.recent_directories):
                if dir_data["path"] == path_str:
                    existing_index = i
                    break

            if existing_index >= 0:
                # Update existing entry
                self.recent_directories[existing_index][
                    "last_accessed"
                ] = current_time.isoformat()
                self.recent_directories[existing_index]["access_count"] += 1

                # Move to front if not pinned
                if path_str not in self.pinned_directories:
                    item = self.recent_directories.pop(existing_index)
                    self.recent_directories.insert(0, item)
            else:
                # Add new entry
                dir_data = {
                    "path": path_str,
                    "name": dir_path.name or str(dir_path),
                    "last_accessed": current_time.isoformat(),
                    "access_count": 1,
                }
                self.recent_directories.insert(0, dir_data)

            # Maintain size limit
            if len(self.recent_directories) > self.max_recent_directories:
                # Remove oldest non-pinned items
                self.recent_directories = [
                    item
                    for item in self.recent_directories
                    if item["path"] in self.pinned_directories
                ][
                    : self.max_recent_directories // 2
                ] + self.recent_directories[
                    : self.max_recent_directories // 2
                ]

            self._save_recent_data()
            self._refresh_directories_display()

            self.logger.debug(f"Added recent directory: {path_str}")

        except Exception as e:
            self.logger.error(f"Error adding recent directory {path}: {e}")

    def add_recent_tool(
        self, tool_name: str, category: str = "Unknown", module_path: str = ""
    ):
        """Add a tool to the recent list."""
        try:
            current_time = datetime.now()

            # Check if already exists
            existing_index = -1
            for i, tool_data in enumerate(self.recent_tools):
                if tool_data["name"] == tool_name:
                    existing_index = i
                    break

            if existing_index >= 0:
                # Update existing entry
                self.recent_tools[existing_index][
                    "last_used"
                ] = current_time.isoformat()
                self.recent_tools[existing_index]["usage_count"] += 1

                # Move to front if not pinned
                if tool_name not in self.pinned_tools:
                    item = self.recent_tools.pop(existing_index)
                    self.recent_tools.insert(0, item)
            else:
                # Add new entry
                tool_data = {
                    "name": tool_name,
                    "category": category,
                    "module_path": module_path,
                    "last_used": current_time.isoformat(),
                    "usage_count": 1,
                }
                self.recent_tools.insert(0, tool_data)

            # Maintain size limit
            if len(self.recent_tools) > self.max_recent_tools:
                # Remove oldest non-pinned items
                self.recent_tools = [
                    item
                    for item in self.recent_tools
                    if item["name"] in self.pinned_tools
                ][: self.max_recent_tools // 2] + self.recent_tools[
                    : self.max_recent_tools // 2
                ]

            self._save_recent_data()
            self._refresh_tools_display()

            self.logger.debug(f"Added recent tool: {tool_name}")

        except Exception as e:
            self.logger.error(f"Error adding recent tool {tool_name}: {e}")

    def _refresh_directories_display(self):
        """Refresh the directories tree widget display."""
        if not self.directories_tree:
            return

        try:
            self.directories_tree.clear()

            # Sort: pinned first, then by last accessed
            sorted_dirs = sorted(
                self.recent_directories,
                key=lambda x: (
                    x["path"] not in self.pinned_directories,  # Pinned first
                    -datetime.fromisoformat(
                        x["last_accessed"]
                    ).timestamp(),  # Most recent first
                ),
            )

            for dir_data in sorted_dirs:
                try:
                    path = dir_data["path"]
                    name = dir_data["name"]
                    last_accessed = datetime.fromisoformat(
                        dir_data["last_accessed"]
                    )
                    access_count = dir_data["access_count"]

                    # Format last accessed time
                    now = datetime.now()
                    if (now - last_accessed).days == 0:
                        time_str = last_accessed.strftime("%H:%M")
                    elif (now - last_accessed).days == 1:
                        time_str = "Yesterday"
                    elif (now - last_accessed).days < 7:
                        time_str = last_accessed.strftime("%A")
                    else:
                        time_str = last_accessed.strftime("%Y-%m-%d")

                    # Create tree item
                    item = QTreeWidgetItem([name, time_str, str(access_count)])

                    # Store full path in item data
                    item.setData(0, Qt.UserRole, path)

                    # Style pinned items
                    if path in self.pinned_directories:
                        item.setIcon(
                            0,
                            self.style().standardIcon(
                                self.style().SP_DialogSaveButton
                            ),
                        )
                        for col in range(3):
                            item.setForeground(col, Qt.blue)
                    else:
                        item.setIcon(
                            0,
                            self.style().standardIcon(self.style().SP_DirIcon),
                        )

                    # Set tooltip
                    item.setToolTip(
                        0,
                        f"Full path: {path}\nLast accessed: {last_accessed.strftime('%Y-%m-%d %H:%M:%S')}\nAccess count: {access_count}",
                    )

                    self.directories_tree.addTopLevelItem(item)

                except Exception as e:
                    self.logger.warning(f"Error adding directory item: {e}")
                    continue

            self.logger.debug(
                f"Refreshed directories display with {len(sorted_dirs)} items"
            )

        except Exception as e:
            self.logger.error(f"Error refreshing directories display: {e}")

    def _refresh_tools_display(self):
        """Refresh the tools tree widget display."""
        if not self.tools_tree:
            return

        try:
            self.tools_tree.clear()

            # Sort: pinned first, then by last used
            sorted_tools = sorted(
                self.recent_tools,
                key=lambda x: (
                    x["name"] not in self.pinned_tools,  # Pinned first
                    -datetime.fromisoformat(
                        x["last_used"]
                    ).timestamp(),  # Most recent first
                ),
            )

            for tool_data in sorted_tools:
                try:
                    name = tool_data["name"]
                    category = tool_data["category"]
                    last_used = datetime.fromisoformat(tool_data["last_used"])
                    usage_count = tool_data["usage_count"]
                    module_path = tool_data.get("module_path", "")

                    # Format last used time
                    now = datetime.now()
                    if (now - last_used).days == 0:
                        time_str = last_used.strftime("%H:%M")
                    elif (now - last_used).days == 1:
                        time_str = "Yesterday"
                    elif (now - last_used).days < 7:
                        time_str = last_used.strftime("%A")
                    else:
                        time_str = last_used.strftime("%Y-%m-%d")

                    # Create tree item
                    item = QTreeWidgetItem(
                        [name, category, time_str, str(usage_count)]
                    )

                    # Store tool data in item
                    item.setData(
                        0,
                        Qt.UserRole,
                        {
                            "name": name,
                            "category": category,
                            "module_path": module_path,
                            "last_used": tool_data["last_used"],
                            "usage_count": usage_count,
                        },
                    )

                    # Style pinned items
                    if name in self.pinned_tools:
                        item.setIcon(
                            0,
                            self.style().standardIcon(
                                self.style().SP_DialogSaveButton
                            ),
                        )
                        for col in range(4):
                            item.setForeground(col, Qt.blue)
                    else:
                        # Set category-based icon
                        if "file" in category.lower():
                            item.setIcon(
                                0,
                                self.style().standardIcon(
                                    self.style().SP_FileIcon
                                ),
                            )
                        elif "security" in category.lower():
                            item.setIcon(
                                0,
                                self.style().standardIcon(
                                    self.style().SP_VistaShield
                                ),
                            )
                        else:
                            item.setIcon(
                                0,
                                self.style().standardIcon(
                                    self.style().SP_ComputerIcon
                                ),
                            )

                    # Set tooltip
                    item.setToolTip(
                        0,
                        f"Tool: {name}\nCategory: {category}\nLast used: {last_used.strftime('%Y-%m-%d %H:%M:%S')}\nUsage count: {usage_count}",
                    )

                    self.tools_tree.addTopLevelItem(item)

                except Exception as e:
                    self.logger.warning(f"Error adding tool item: {e}")
                    continue

            self.logger.debug(
                f"Refreshed tools display with {len(sorted_tools)} items"
            )

        except Exception as e:
            self.logger.error(f"Error refreshing tools display: {e}")

    def _on_directory_activated(self, item, column):
        """Handle directory activation (double-click)."""
        try:
            if item:
                path = item.data(0, Qt.UserRole)
                if path and Path(path).exists():
                    self.directoryNavigationRequested.emit(path)
                    self.logger.info(f"Directory navigation requested: {path}")
                else:
                    QMessageBox.warning(
                        self,
                        "Directory Not Found",
                        f"The directory no longer exists:\n{path}",
                    )
                    # Remove from recent list
                    self._remove_directory(path)
        except Exception as e:
            self.logger.error(f"Error activating directory: {e}")

    def _on_tool_activated(self, item, column):
        """Handle tool activation (double-click)."""
        try:
            if item:
                tool_data = item.data(0, Qt.UserRole)
                if isinstance(tool_data, dict):
                    tool_name = tool_data.get("name", "")
                    module_path = tool_data.get("module_path", "")

                    self.toolLaunchRequested.emit(tool_name, module_path)
                    self.logger.info(f"Tool launch requested: {tool_name}")

                    # Update usage count
                    self.add_recent_tool(
                        tool_name,
                        tool_data.get("category", "Unknown"),
                        module_path,
                    )
        except Exception as e:
            self.logger.error(f"Error activating tool: {e}")

    def _show_directory_tooltip(self, item, column):
        """Show tooltip for directory item on hover."""
        # Tooltip is already set in _refresh_directories_display
        pass

    def _show_tool_tooltip(self, item, column):
        """Show tooltip for tool item on hover."""
        # Tooltip is already set in _refresh_tools_display
        pass

    def _show_directory_context_menu(self, position):
        """Show context menu for directory items."""
        try:
            item = self.directories_tree.itemAt(position)
            if not item:
                return

            path = item.data(0, Qt.UserRole)
            if not path:
                return

            menu = QMenu(self)

            # Navigate action
            navigate_action = QAction("📁 Navigate Here", self)
            navigate_action.triggered.connect(
                lambda: self._on_directory_activated(item, 0)
            )
            menu.addAction(navigate_action)

            menu.addSeparator()

            # Pin/Unpin action
            is_pinned = path in self.pinned_directories
            if is_pinned:
                pin_action = QAction("📌 Unpin", self)
                pin_action.triggered.connect(
                    lambda: self._unpin_directory(path)
                )
            else:
                pin_action = QAction("📍 Pin", self)
                pin_action.triggered.connect(lambda: self._pin_directory(path))
            menu.addAction(pin_action)

            menu.addSeparator()

            # Remove action
            remove_action = QAction("🗑️ Remove from Recent", self)
            remove_action.triggered.connect(
                lambda: self._remove_directory(path)
            )
            menu.addAction(remove_action)

            # Show file explorer action
            explore_action = QAction("🔍 Show in Explorer", self)
            explore_action.triggered.connect(
                lambda: self._show_in_explorer(path)
            )
            menu.addAction(explore_action)

            menu.exec_(self.directories_tree.mapToGlobal(position))

        except Exception as e:
            self.logger.error(f"Error showing directory context menu: {e}")

    def _show_tool_context_menu(self, position):
        """Show context menu for tool items."""
        try:
            item = self.tools_tree.itemAt(position)
            if not item:
                return

            tool_data = item.data(0, Qt.UserRole)
            if not isinstance(tool_data, dict):
                return

            tool_name = tool_data.get("name", "")

            menu = QMenu(self)

            # Launch action
            launch_action = QAction("🚀 Launch Tool", self)
            launch_action.triggered.connect(
                lambda: self._on_tool_activated(item, 0)
            )
            menu.addAction(launch_action)

            menu.addSeparator()

            # Pin/Unpin action
            is_pinned = tool_name in self.pinned_tools
            if is_pinned:
                pin_action = QAction("📌 Unpin", self)
                pin_action.triggered.connect(
                    lambda: self._unpin_tool(tool_name)
                )
            else:
                pin_action = QAction("📍 Pin", self)
                pin_action.triggered.connect(lambda: self._pin_tool(tool_name))
            menu.addAction(pin_action)

            menu.addSeparator()

            # Remove action
            remove_action = QAction("🗑️ Remove from Recent", self)
            remove_action.triggered.connect(
                lambda: self._remove_tool(tool_name)
            )
            menu.addAction(remove_action)

            menu.exec_(self.tools_tree.mapToGlobal(position))

        except Exception as e:
            self.logger.error(f"Error showing tool context menu: {e}")

    def _pin_directory(self, path: str):
        """Pin a directory to keep it in the recent list."""
        if path not in self.pinned_directories:
            self.pinned_directories.append(path)
            self._save_recent_data()
            self._refresh_directories_display()
            self.itemPinned.emit("directory", path)
            self.logger.info(f"Pinned directory: {path}")

    def _unpin_directory(self, path: str):
        """Unpin a directory."""
        if path in self.pinned_directories:
            self.pinned_directories.remove(path)
            self._save_recent_data()
            self._refresh_directories_display()
            self.itemUnpinned.emit("directory", path)
            self.logger.info(f"Unpinned directory: {path}")

    def _pin_tool(self, tool_name: str):
        """Pin a tool to keep it in the recent list."""
        if tool_name not in self.pinned_tools:
            self.pinned_tools.append(tool_name)
            self._save_recent_data()
            self._refresh_tools_display()
            self.itemPinned.emit("tool", tool_name)
            self.logger.info(f"Pinned tool: {tool_name}")

    def _unpin_tool(self, tool_name: str):
        """Unpin a tool."""
        if tool_name in self.pinned_tools:
            self.pinned_tools.remove(tool_name)
            self._save_recent_data()
            self._refresh_tools_display()
            self.itemUnpinned.emit("tool", tool_name)
            self.logger.info(f"Unpinned tool: {tool_name}")

    def _remove_directory(self, path: str):
        """Remove a directory from the recent list."""
        self.recent_directories = [
            d for d in self.recent_directories if d["path"] != path
        ]
        if path in self.pinned_directories:
            self.pinned_directories.remove(path)
        self._save_recent_data()
        self._refresh_directories_display()
        self.logger.info(f"Removed directory from recent: {path}")

    def _remove_tool(self, tool_name: str):
        """Remove a tool from the recent list."""
        self.recent_tools = [
            t for t in self.recent_tools if t["name"] != tool_name
        ]
        if tool_name in self.pinned_tools:
            self.pinned_tools.remove(tool_name)
        self._save_recent_data()
        self._refresh_tools_display()
        self.logger.info(f"Removed tool from recent: {tool_name}")

    def _show_in_explorer(self, path: str):
        """Show directory in system file explorer."""
        try:
            import platform
            import subprocess

            system = platform.system()
            if system == "Windows":
                subprocess.Popen(["explorer", path])
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux
                subprocess.Popen(["xdg-open", path])

            self.logger.info(f"Opened in explorer: {path}")

        except Exception as e:
            self.logger.error(f"Error opening in explorer: {e}")
            QMessageBox.warning(
                self, "Error", f"Could not open in file explorer:\n{e}"
            )

    def _clear_recent_directories(self):
        """Clear all recent directories (except pinned)."""
        try:
            # Keep only pinned directories
            self.recent_directories = [
                d
                for d in self.recent_directories
                if d["path"] in self.pinned_directories
            ]

            self._save_recent_data()
            self._refresh_directories_display()

            QMessageBox.information(
                self,
                "Cleared",
                "Recent directories cleared (pinned items preserved)",
            )
            self.logger.info("Cleared recent directories")

        except Exception as e:
            self.logger.error(f"Error clearing recent directories: {e}")

    def _clear_recent_tools(self):
        """Clear all recent tools (except pinned)."""
        try:
            # Keep only pinned tools
            self.recent_tools = [
                t for t in self.recent_tools if t["name"] in self.pinned_tools
            ]

            self._save_recent_data()
            self._refresh_tools_display()

            QMessageBox.information(
                self,
                "Cleared",
                "Recent tools cleared (pinned items preserved)",
            )
            self.logger.info("Cleared recent tools")

        except Exception as e:
            self.logger.error(f"Error clearing recent tools: {e}")

    def closeEvent(self, event):
        """Handle widget close event."""
        try:
            # Save data before closing
            self._save_recent_data()

            # Stop cleanup timer
            if hasattr(self, "cleanup_timer"):
                self.cleanup_timer.stop()

            super().closeEvent(event)

        except Exception as e:
            self.logger.error(f"Error during close: {e}")
            super().closeEvent(event)


# Test application for standalone testing
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Create test widget
    widget = RecentTabWidget()
    widget.setMinimumSize(500, 600)
    widget.show()

    # Add some test data
    widget.add_recent_directory(str(Path.home()))
    widget.add_recent_directory(str(Path.home() / "Documents"))
    widget.add_recent_directory(str(Path.home() / "Downloads"))

    widget.add_recent_tool(
        "File Finder",
        "File Management",
        "src.tools.file_management.file_finder",
    )
    widget.add_recent_tool(
        "Duplicate Finder", "Analysis", "src.tools.analysis.duplicate_finder"
    )
    widget.add_recent_tool(
        "Secure Delete", "Security", "src.tools.security.secure_delete"
    )

    sys.exit(app.exec_())
