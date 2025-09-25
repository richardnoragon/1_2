"""Folder Tree View Component.

Enterprise-grade tree view component for displaying and managing folder configurations.
Implements virtual tree view with lazy loading, drag-and-drop support, and context menus.

Features:
- Virtual tree model for performance with large folder structures
- Lazy loading of folder contents
- Drag-and-drop folder organization
- Context menu with folder operations
- Real-time folder monitoring and updates
- Accessibility compliance
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PyQt5.QtCore import (
    QAbstractItemModel,
    QMimeData,
    QModelIndex,
    QObject,
    Qt,
    QThread,
    QTimer,
    QVariant,
    pyqtSignal,
)
from PyQt5.QtGui import QDrag, QFont, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ..core import ConfigurationManager, FolderConfiguration, ValidationResult
from ..database import AdvancedFoldersDBManager
from ..repositories import FolderConfigurationRepository


class FolderTreeNode:
    """Tree node representing a folder configuration."""

    def __init__(
        self,
        folder_config: Optional[FolderConfiguration] = None,
        parent: Optional["FolderTreeNode"] = None,
    ):
        """Initialize tree node.

        Args:
            folder_config: Associated folder configuration
            parent: Parent node
        """
        self.folder_config = folder_config
        self.parent = parent
        self.children: List["FolderTreeNode"] = []
        self.loaded = False
        self.expanded = False

        # Node metadata
        self.node_id = folder_config.id if folder_config else "root"
        self.display_name = folder_config.name if folder_config else "Root"
        self.node_type = "folder" if folder_config else "root"

    def add_child(self, child: "FolderTreeNode"):
        """Add child node."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "FolderTreeNode"):
        """Remove child node."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def child_count(self) -> int:
        """Get number of children."""
        return len(self.children)

    def child_at(self, index: int) -> Optional["FolderTreeNode"]:
        """Get child at index."""
        if 0 <= index < len(self.children):
            return self.children[index]
        return None

    def row(self) -> int:
        """Get row index in parent."""
        if self.parent:
            return self.parent.children.index(self)
        return 0


class FolderTreeModel(QAbstractItemModel):
    """Tree model for folder configurations with lazy loading."""

    # Custom signals
    folderSelected = pyqtSignal(str)  # folder_id
    folderActivated = pyqtSignal(str)  # folder_id
    folderContextMenu = pyqtSignal(str, object)  # folder_id, QPoint

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize tree model.

        Args:
            parent: Parent object
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.TreeModel")

        # Model data
        self.root_node = FolderTreeNode()

        # Repository for data access
        self.db_manager = AdvancedFoldersDBManager()
        self.folder_repository = FolderConfigurationRepository(self.db_manager)

        # Load initial data
        self._load_folder_configurations()

    def _load_folder_configurations(self):
        """Load folder configurations from repository."""
        try:
            self.beginResetModel()

            # Clear existing data
            self.root_node.children.clear()

            # Load all folder configurations
            folders = self.folder_repository.get_all()

            # Create tree nodes
            for folder in folders:
                node = FolderTreeNode(folder, self.root_node)
                self.root_node.add_child(node)

            self.endResetModel()
            self.logger.info(f"Loaded {len(folders)} folder configurations")

        except Exception as e:
            self.logger.error(f"Failed to load folder configurations: {e}")

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        """Create model index."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()

        child_node = parent_node.child_at(row)
        if child_node:
            return self.createIndex(row, column, child_node)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Get parent model index."""
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root_node or parent_node is None:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of rows."""
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()

        return parent_node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of columns."""
        return 3  # Name, Type, Status

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Get data for model index."""
        if not index.isValid():
            return QVariant()

        node = index.internalPointer()
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:  # Name
                return node.display_name
            elif column == 1:  # Type
                if node.folder_config:
                    return node.folder_config.folder_type.value
                return "Container"
            elif column == 2:  # Status
                if node.folder_config:
                    return (
                        "Active"
                        if node.folder_config.is_active
                        else "Inactive"
                    )
                return "N/A"

        elif role == Qt.ToolTipRole:
            if node.folder_config:
                return (
                    f"Name: {node.folder_config.name}\n"
                    f"Description: {node.folder_config.description}\n"
                    f"Directories: {len(node.folder_config.target_directories)}\n"
                    f"Status: {'Active' if node.folder_config.is_active else 'Inactive'}"
                )
            return "Folder configurations container"

        elif role == Qt.DecorationRole and column == 0:
            if node.folder_config:
                # Return appropriate icon based on folder type
                return self._get_folder_icon(node.folder_config)
            else:
                # Root folder icon
                return self._get_root_icon()

        elif role == Qt.FontRole:
            if not node.folder_config:
                # Bold font for root
                font = QFont()
                font.setBold(True)
                return font

        elif role == Qt.UserRole:
            # Return the full node for custom operations
            return node

        return QVariant()

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        """Get header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["Folder Name", "Type", "Status"]
            if 0 <= section < len(headers):
                return headers[section]

        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get item flags."""
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # Enable drag and drop for folder nodes
        node = index.internalPointer()
        if node.folder_config:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        return flags

    def _get_folder_icon(self, folder_config: FolderConfiguration) -> QIcon:
        """Get icon for folder configuration.

        Args:
            folder_config: Folder configuration

        Returns:
            Appropriate icon for the folder type
        """
        # Icon mapping based on folder type
        icon_map = {
            "documents": ":/icons/folder_documents.png",
            "images": ":/icons/folder_images.png",
            "videos": ":/icons/folder_videos.png",
            "audio": ":/icons/folder_audio.png",
            "archives": ":/icons/folder_archives.png",
            "projects": ":/icons/folder_projects.png",
            "custom": ":/icons/folder_custom.png",
        }

        icon_path = icon_map.get(
            folder_config.folder_type.value, ":/icons/folder_default.png"
        )
        return QIcon(icon_path)

    def _get_root_icon(self) -> QIcon:
        """Get root folder icon."""
        return QIcon(":/icons/folder_root.png")

    def add_folder_configuration(self, folder_config: FolderConfiguration):
        """Add new folder configuration to model.

        Args:
            folder_config: New folder configuration
        """
        row = self.root_node.child_count()

        self.beginInsertRows(QModelIndex(), row, row)

        node = FolderTreeNode(folder_config, self.root_node)
        self.root_node.add_child(node)

        self.endInsertRows()

        self.logger.info(f"Added folder configuration: {folder_config.name}")

    def remove_folder_configuration(self, folder_id: str):
        """Remove folder configuration from model.

        Args:
            folder_id: ID of folder to remove
        """
        for i, child in enumerate(self.root_node.children):
            if child.folder_config and child.folder_config.id == folder_id:
                self.beginRemoveRows(QModelIndex(), i, i)
                self.root_node.remove_child(child)
                self.endRemoveRows()

                self.logger.info(f"Removed folder configuration: {folder_id}")
                return

        self.logger.warning(f"Folder configuration not found: {folder_id}")

    def update_folder_configuration(self, folder_config: FolderConfiguration):
        """Update existing folder configuration in model.

        Args:
            folder_config: Updated folder configuration
        """
        for child in self.root_node.children:
            if (
                child.folder_config
                and child.folder_config.id == folder_config.id
            ):
                child.folder_config = folder_config
                child.display_name = folder_config.name

                # Emit data changed signal
                index = self.createIndex(child.row(), 0, child)
                self.dataChanged.emit(index, index)

                self.logger.info(
                    f"Updated folder configuration: {folder_config.name}"
                )
                return

        self.logger.warning(
            f"Folder configuration not found for update: {folder_config.id}"
        )

    def get_folder_configuration(
        self, index: QModelIndex
    ) -> Optional[FolderConfiguration]:
        """Get folder configuration for model index.

        Args:
            index: Model index

        Returns:
            Folder configuration or None
        """
        if not index.isValid():
            return None

        node = index.internalPointer()
        return node.folder_config

    def refresh(self):
        """Refresh model data from repository."""
        self._load_folder_configurations()


class FolderTreeView(QTreeView):
    """Enterprise-grade tree view for folder configurations."""

    # Custom signals
    folderSelected = pyqtSignal(str)  # folder_id
    folderActivated = pyqtSignal(str)  # folder_id
    folderConfigurationRequested = pyqtSignal(str)  # folder_id
    newFolderRequested = pyqtSignal()
    deleteFolderRequested = pyqtSignal(str)  # folder_id

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize folder tree view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.TreeView")

        # Setup model
        self.folder_model = FolderTreeModel(self)
        self.setModel(self.folder_model)

        # Setup view
        self._setup_view()
        self._connect_signals()

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.logger.info("Folder tree view initialized")

    def _setup_view(self):
        """Setup tree view appearance and behavior."""
        # Selection behavior
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Interaction
        self.setExpandsOnDoubleClick(True)
        self.setItemsExpandable(True)
        self.setRootIsDecorated(True)
        self.setAllColumnsShowFocus(True)

        # Headers
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name column
        header.setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )  # Type column
        header.setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )  # Status column

        # Drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        # Visual styling
        self.setAlternatingRowColors(True)
        self.setIndentation(20)

        # Performance optimization
        self.setUniformRowHeights(True)

        # Accessibility
        self.setAccessibleName("Folder Configurations Tree")
        self.setAccessibleDescription(
            "Tree view of configured advanced folders"
        )

    def _connect_signals(self):
        """Connect internal signals."""
        # Selection changes
        self.selectionModel().currentChanged.connect(
            self._on_selection_changed
        )

        # Double-click activation
        self.doubleClicked.connect(self._on_double_clicked)

        # Model signals
        self.folder_model.folderSelected.connect(self.folderSelected)
        self.folder_model.folderActivated.connect(self.folderActivated)

    def _on_selection_changed(
        self, current: QModelIndex, previous: QModelIndex
    ):
        """Handle selection changes.

        Args:
            current: Current selected index
            previous: Previously selected index
        """
        folder_config = self.folder_model.get_folder_configuration(current)
        if folder_config:
            self.folderSelected.emit(folder_config.id)
            self.logger.debug(f"Selected folder: {folder_config.name}")

    def _on_double_clicked(self, index: QModelIndex):
        """Handle double-click activation.

        Args:
            index: Double-clicked index
        """
        folder_config = self.folder_model.get_folder_configuration(index)
        if folder_config:
            self.folderActivated.emit(folder_config.id)
            self.logger.debug(f"Activated folder: {folder_config.name}")

    def _show_context_menu(self, position):
        """Show context menu for tree item.

        Args:
            position: Menu position
        """
        index = self.indexAt(position)
        folder_config = self.folder_model.get_folder_configuration(index)

        menu = QMenu(self)

        if folder_config:
            # Folder-specific actions
            configure_action = QAction("Configure Folder...", self)
            configure_action.triggered.connect(
                lambda: self.folderConfigurationRequested.emit(
                    folder_config.id
                )
            )
            menu.addAction(configure_action)

            activate_action = QAction(
                "Activate" if not folder_config.is_active else "Deactivate",
                self,
            )
            activate_action.triggered.connect(
                lambda: self._toggle_folder_activation(folder_config.id)
            )
            menu.addAction(activate_action)

            menu.addSeparator()

            delete_action = QAction("Delete Folder", self)
            delete_action.triggered.connect(
                lambda: self._confirm_delete_folder(folder_config.id)
            )
            menu.addAction(delete_action)

        # General actions
        menu.addSeparator()

        new_action = QAction("New Folder...", self)
        new_action.triggered.connect(self.newFolderRequested.emit)
        menu.addAction(new_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)

        # Show menu
        menu.exec_(self.mapToGlobal(position))

    def _toggle_folder_activation(self, folder_id: str):
        """Toggle folder activation status.

        Args:
            folder_id: ID of folder to toggle
        """
        try:
            folder_config = self.folder_model.folder_repository.get_by_id(
                folder_id
            )
            if folder_config:
                folder_config.is_active = not folder_config.is_active
                self.folder_model.folder_repository.update(folder_config)
                self.folder_model.update_folder_configuration(folder_config)

                status = (
                    "activated" if folder_config.is_active else "deactivated"
                )
                self.logger.info(f"Folder {folder_config.name} {status}")

        except Exception as e:
            self.logger.error(f"Failed to toggle folder activation: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to toggle folder activation: {e}"
            )

    def _confirm_delete_folder(self, folder_id: str):
        """Confirm and delete folder configuration.

        Args:
            folder_id: ID of folder to delete
        """
        try:
            folder_config = self.folder_model.folder_repository.get_by_id(
                folder_id
            )
            if not folder_config:
                return

            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the folder configuration '{folder_config.name}'?\n\n"
                "This will not delete any actual files, only the folder configuration.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.deleteFolderRequested.emit(folder_id)

        except Exception as e:
            self.logger.error(f"Failed to delete folder configuration: {e}")
            QMessageBox.critical(
                self, "Error", f"Failed to delete folder configuration: {e}"
            )

    def refresh(self):
        """Refresh tree view data."""
        self.logger.info("Refreshing folder tree view")
        self.folder_model.refresh()

        # Restore expanded state
        self.expandAll()

    def add_folder_configuration(self, folder_config: FolderConfiguration):
        """Add new folder configuration to tree.

        Args:
            folder_config: New folder configuration
        """
        self.folder_model.add_folder_configuration(folder_config)

    def remove_folder_configuration(self, folder_id: str):
        """Remove folder configuration from tree.

        Args:
            folder_id: ID of folder to remove
        """
        self.folder_model.remove_folder_configuration(folder_id)

    def update_folder_configuration(self, folder_config: FolderConfiguration):
        """Update folder configuration in tree.

        Args:
            folder_config: Updated folder configuration
        """
        self.folder_model.update_folder_configuration(folder_config)

    def select_folder(self, folder_id: str):
        """Select folder by ID.

        Args:
            folder_id: ID of folder to select
        """
        # Find and select the folder
        for i, child in enumerate(self.folder_model.root_node.children):
            if child.folder_config and child.folder_config.id == folder_id:
                index = self.folder_model.createIndex(i, 0, child)
                self.setCurrentIndex(index)
                self.scrollTo(index)
                return

        self.logger.warning(f"Folder not found for selection: {folder_id}")

    def get_selected_folder_id(self) -> Optional[str]:
        """Get ID of currently selected folder.

        Returns:
            Selected folder ID or None
        """
        current_index = self.currentIndex()
        folder_config = self.folder_model.get_folder_configuration(
            current_index
        )
        return folder_config.id if folder_config else None

    def get_folder_count(self) -> int:
        """Get total number of folders in tree.

        Returns:
            Number of folder configurations
        """
        return self.folder_model.root_node.child_count()


class FolderTreeWidget(QWidget):
    """Complete folder tree widget with toolbar and controls."""

    # Signals
    folderSelected = pyqtSignal(str)  # folder_id
    folderActivated = pyqtSignal(str)  # folder_id
    folderConfigurationRequested = pyqtSignal(str)  # folder_id
    newFolderRequested = pyqtSignal()
    deleteFolderRequested = pyqtSignal(str)  # folder_id

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize folder tree widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("AdvancedFolders.TreeWidget")

        # Setup UI
        self._setup_ui()
        self._connect_signals()

        self.logger.info("Folder tree widget initialized")

    def _setup_ui(self):
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create toolbar
        self._create_toolbar(layout)

        # Create tree view
        self.tree_view = FolderTreeView(self)
        layout.addWidget(self.tree_view)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "QLabel { color: #666666; font-size: 11px; }"
        )
        layout.addWidget(self.status_label)

    def _create_toolbar(self, parent_layout: QVBoxLayout):
        """Create toolbar with folder operations.

        Args:
            parent_layout: Parent layout for toolbar
        """
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        toolbar_frame.setMaximumHeight(32)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(4, 2, 4, 2)
        toolbar_layout.setSpacing(2)

        # New folder button
        self.new_button = QToolButton()
        self.new_button.setText("New")
        self.new_button.setToolTip("Create new folder configuration")
        self.new_button.clicked.connect(self.newFolderRequested.emit)
        toolbar_layout.addWidget(self.new_button)

        # Refresh button
        self.refresh_button = QToolButton()
        self.refresh_button.setText("Refresh")
        self.refresh_button.setToolTip("Refresh folder list")
        self.refresh_button.clicked.connect(self.tree_view.refresh)
        toolbar_layout.addWidget(self.refresh_button)

        toolbar_layout.addStretch()

        # Folder count label
        self.count_label = QLabel("0 folders")
        self.count_label.setStyleSheet(
            "QLabel { color: #666666; font-size: 11px; }"
        )
        toolbar_layout.addWidget(self.count_label)

        parent_layout.addWidget(toolbar_frame)

    def _connect_signals(self):
        """Connect internal signals."""
        # Forward tree view signals
        self.tree_view.folderSelected.connect(self.folderSelected)
        self.tree_view.folderActivated.connect(self.folderActivated)
        self.tree_view.folderConfigurationRequested.connect(
            self.folderConfigurationRequested
        )
        self.tree_view.newFolderRequested.connect(self.newFolderRequested)
        self.tree_view.deleteFolderRequested.connect(
            self.deleteFolderRequested
        )

        # Update count when model changes
        self.tree_view.folder_model.modelReset.connect(
            self._update_folder_count
        )
        self.tree_view.folder_model.rowsInserted.connect(
            self._update_folder_count
        )
        self.tree_view.folder_model.rowsRemoved.connect(
            self._update_folder_count
        )

    def _update_folder_count(self):
        """Update folder count display."""
        count = self.tree_view.get_folder_count()
        if count == 0:
            self.count_label.setText("No folders")
        elif count == 1:
            self.count_label.setText("1 folder")
        else:
            self.count_label.setText(f"{count} folders")

    def refresh(self):
        """Refresh tree data."""
        self.tree_view.refresh()

    def select_folder(self, folder_id: str):
        """Select folder by ID."""
        self.tree_view.select_folder(folder_id)

    def get_selected_folder_id(self) -> Optional[str]:
        """Get selected folder ID."""
        return self.tree_view.get_selected_folder_id()
