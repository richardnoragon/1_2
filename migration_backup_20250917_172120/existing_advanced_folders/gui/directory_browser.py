"""
Advanced Directory Browser Widget

Enterprise-grade directory selection and management widget for the Advanced
Folders feature. Provides comprehensive directory browsing capabilities with
validation, path management, and professional UI patterns.

Features:
- Native directory browsing with tree view
- Multi-selection support for directory management
- Real-time path validation and error handling
- Integrated add/remove functionality with confirmation
- Professional styling and accessibility support
- Cross-platform path handling and compatibility

Author: RFU Development Team
Version: 1.0.0
"""

import logging
import os
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton,
        QLabel, QLineEdit, QGroupBox, QSplitter, QListWidget,
        QListWidgetItem, QMessageBox, QFileDialog, QFrame,
        QCheckBox, QComboBox, QProgressBar, QMenu, QAction,
        QApplication, QAbstractItemView, QHeaderView
    )
    from PyQt5.QtCore import (
        Qt, pyqtSignal, QDir, QFileSystemWatcher, QTimer,
        QModelIndex, QItemSelectionModel, QAbstractItemModel
    )
    from PyQt5.QtGui import (
        QFileSystemModel, QStandardItemModel, QStandardItem,
        QFont, QIcon, QPalette, QPixmap
    )
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    QWidget = object
    pyqtSignal = None

# Import constants and styling
try:
    from .constants import (
        Colors, Fonts, Layout, Icons, Styles, Validation,
        Accessibility
    )
except ImportError:
    # Fallback constants
    class Colors:
        PRIMARY_BLUE = "#3498db"
        BACKGROUND_MAIN = "#ffffff"
        TEXT_PRIMARY = "#2c3e50"
        TEXT_ERROR = "#e74c3c"
    
    class Layout:
        CONTENT_MARGIN = 20
        SECTION_SPACING = 15
    
    class Icons:
        ADD = "+"
        REMOVE = "-"
        FOLDER_OPEN = "📁"

# Import logging
try:
    from src.log_manager import get_log_manager
    logger = get_log_manager().get_logger('AdvancedFolders.DirectoryBrowser')
except ImportError:
    logger = logging.getLogger(__name__)


class DirectoryBrowserWidget(QWidget):
    """
    Enterprise-grade directory browser widget.
    
    Provides comprehensive directory selection and management capabilities
    with professional UI patterns, validation, and accessibility support.
    
    Signals:
        directories_changed: Emitted when directory list changes
        directory_selected: Emitted when a directory is selected in browser
        validation_error: Emitted when validation fails
        path_validated: Emitted when path validation completes
    """
    
    # Signals for external integration
    directories_changed = pyqtSignal(list)  # List of directory paths
    directory_selected = pyqtSignal(str)    # Selected directory path
    validation_error = pyqtSignal(str)      # Error message
    path_validated = pyqtSignal(str, bool)  # Path, is_valid
    
    def __init__(self, parent=None, initial_directories=None, mode='multi'):
        """
        Initialize the directory browser widget.
        
        Args:
            parent: Parent widget
            initial_directories: List of initial directory paths
            mode: Selection mode ('single', 'multi')
        """
        super().__init__(parent)
        
        # Configuration
        self.mode = mode
        self.is_read_only = False
        self.max_directories = Validation.MAX_DIRECTORY_PATHS
        
        # Internal state
        self.selected_directories: Set[str] = set()
        self.file_system_watcher = None
        self.validation_timer = None
        
        # UI components
        self.directory_tree = None
        self.selected_list = None
        self.path_edit = None
        self.add_button = None
        self.remove_button = None
        self.browse_button = None
        self.validate_button = None
        self.status_label = None
        
        # File system model
        self.fs_model = None
        
        # Initialize the widget
        self._setup_ui()
        self._setup_file_system_model()
        self._setup_connections()
        self._setup_validation()
        self._setup_accessibility()
        
        # Load initial directories
        if initial_directories:
            self.set_directories(initial_directories)
        
        logger.info(f"DirectoryBrowserWidget initialized in {mode} mode")
    
    def _setup_ui(self):
        """Setup the main user interface."""
        if not PYQT5_AVAILABLE:
            return
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(Layout.SECTION_SPACING)
        
        # Create header section
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)
        
        # Create main content with splitter
        content_splitter = self._create_content_area()
        main_layout.addWidget(content_splitter, 1)
        
        # Create status section
        status_widget = self._create_status_section()
        main_layout.addWidget(status_widget)
    
    def _create_header(self):
        """Create the header section with path input and controls."""
        header_group = QGroupBox("Directory Selection")\n        header_group.setStyleSheet(Styles.GROUP_BOX_STYLE)\n        header_group.setMaximumHeight(120)\n        \n        layout = QVBoxLayout(header_group)\n        layout.setContentsMargins(15, 20, 15, 15)\n        layout.setSpacing(Layout.ITEM_SPACING)\n        \n        # Path input section\n        path_layout = QHBoxLayout()\n        \n        path_label = QLabel("Directory Path:")\n        path_label.setFont(Fonts.label_font())\n        path_layout.addWidget(path_label)\n        \n        self.path_edit = QLineEdit()\n        self.path_edit.setPlaceholderText("Enter or browse for directory path...")\n        self.path_edit.setStyleSheet(Styles.INPUT_FIELD_STYLE)\n        self.path_edit.textChanged.connect(self._on_path_changed)\n        path_layout.addWidget(self.path_edit)\n        \n        layout.addLayout(path_layout)\n        \n        # Control buttons\n        buttons_layout = QHBoxLayout()\n        \n        self.browse_button = QPushButton(f"{Icons.FOLDER_OPEN} Browse")\n        self.browse_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n        self.browse_button.clicked.connect(self._browse_directory)\n        buttons_layout.addWidget(self.browse_button)\n        \n        self.validate_button = QPushButton("✓ Validate")\n        self.validate_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n        self.validate_button.clicked.connect(self._validate_current_path)\n        buttons_layout.addWidget(self.validate_button)\n        \n        self.add_button = QPushButton(f"{Icons.ADD} Add Directory")\n        self.add_button.setStyleSheet(Styles.BUTTON_PRIMARY_STYLE)\n        self.add_button.clicked.connect(self._add_current_directory)\n        self.add_button.setEnabled(False)\n        buttons_layout.addWidget(self.add_button)\n        \n        buttons_layout.addStretch()\n        layout.addLayout(buttons_layout)\n        \n        return header_group\n    \n    def _create_content_area(self):\n        \"\"\"Create the main content area with directory tree and selected list.\"\"\"\n        splitter = QSplitter(Qt.Horizontal)\n        splitter.setChildrenCollapsible(False)\n        \n        # Directory tree browser\n        tree_widget = self._create_tree_browser()\n        splitter.addWidget(tree_widget)\n        \n        # Selected directories list\n        list_widget = self._create_selected_list()\n        splitter.addWidget(list_widget)\n        \n        # Set splitter proportions (60% tree, 40% list)\n        splitter.setSizes([400, 250])\n        splitter.setStretchFactor(0, 3)\n        splitter.setStretchFactor(1, 2)\n        \n        return splitter\n    \n    def _create_tree_browser(self):\n        \"\"\"Create the directory tree browser.\"\"\"\n        tree_group = QGroupBox(\"Directory Browser\")\n        tree_group.setStyleSheet(Styles.GROUP_BOX_STYLE)\n        \n        layout = QVBoxLayout(tree_group)\n        layout.setContentsMargins(10, 15, 10, 10)\n        layout.setSpacing(5)\n        \n        # Tree view\n        self.directory_tree = QTreeView()\n        self.directory_tree.setHeaderHidden(True)\n        self.directory_tree.setRootIsDecorated(True)\n        self.directory_tree.setAlternatingRowColors(True)\n        self.directory_tree.setSelectionMode(QAbstractItemView.SingleSelection)\n        self.directory_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)\n        \n        # Apply styling\n        self.directory_tree.setStyleSheet(f\"\"\"\n            QTreeView {{\n                border: 1px solid {Colors.BORDER_LIGHT};\n                border-radius: 4px;\n                background-color: {Colors.BACKGROUND_MAIN};\n                alternate-background-color: {Colors.BACKGROUND_SECONDARY};\n                selection-background-color: {Colors.BACKGROUND_SELECTED};\n                outline: none;\n            }}\n            \n            QTreeView::item {{\n                padding: 4px 8px;\n                border-bottom: 1px solid {Colors.BORDER_LIGHT};\n            }}\n            \n            QTreeView::item:selected {{\n                background-color: {Colors.BACKGROUND_SELECTED};\n                color: {Colors.TEXT_PRIMARY};\n            }}\n            \n            QTreeView::item:hover:!selected {{\n                background-color: {Colors.BACKGROUND_HOVER};\n            }}\n        \"\"\")\n        \n        layout.addWidget(self.directory_tree)\n        \n        return tree_group\n    \n    def _create_selected_list(self):\n        \"\"\"Create the selected directories list.\"\"\"\n        list_group = QGroupBox(\"Selected Directories\")\n        list_group.setStyleSheet(Styles.GROUP_BOX_STYLE)\n        \n        layout = QVBoxLayout(list_group)\n        layout.setContentsMargins(10, 15, 10, 10)\n        layout.setSpacing(Layout.ITEM_SPACING)\n        \n        # Selected directories list\n        self.selected_list = QListWidget()\n        self.selected_list.setStyleSheet(Styles.LIST_WIDGET_STYLE)\n        self.selected_list.setSelectionMode(QListWidget.ExtendedSelection)\n        self.selected_list.setMinimumHeight(200)\n        layout.addWidget(self.selected_list)\n        \n        # List control buttons\n        list_buttons_layout = QHBoxLayout()\n        \n        self.remove_button = QPushButton(f\"{Icons.REMOVE} Remove Selected\")\n        self.remove_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n        self.remove_button.clicked.connect(self._remove_selected_directories)\n        self.remove_button.setEnabled(False)\n        list_buttons_layout.addWidget(self.remove_button)\n        \n        clear_button = QPushButton(\"Clear All\")\n        clear_button.setStyleSheet(Styles.BUTTON_SECONDARY_STYLE)\n        clear_button.clicked.connect(self._clear_all_directories)\n        list_buttons_layout.addWidget(clear_button)\n        \n        list_buttons_layout.addStretch()\n        layout.addLayout(list_buttons_layout)\n        \n        # Directory count label\n        self.count_label = QLabel(\"0 directories selected\")\n        self.count_label.setStyleSheet(f\"color: {Colors.TEXT_SECONDARY}; font-size: 9pt;\")\n        layout.addWidget(self.count_label)\n        \n        return list_group\n    \n    def _create_status_section(self):\n        \"\"\"Create the status information section.\"\"\"\n        status_frame = QFrame()\n        status_frame.setFrameStyle(QFrame.StyledPanel)\n        status_frame.setLineWidth(1)\n        status_frame.setFixedHeight(30)\n        \n        layout = QHBoxLayout(status_frame)\n        layout.setContentsMargins(10, 5, 10, 5)\n        \n        # Status label\n        self.status_label = QLabel(\"Ready to select directories\")\n        self.status_label.setFont(Fonts.label_font())\n        self.status_label.setStyleSheet(f\"color: {Colors.TEXT_SECONDARY};\")\n        \n        layout.addWidget(self.status_label)\n        layout.addStretch()\n        \n        return status_frame\n    \n    def _setup_file_system_model(self):\n        \"\"\"Setup the file system model for the tree view.\"\"\"\n        if not PYQT5_AVAILABLE:\n            return\n        \n        try:\n            self.fs_model = QFileSystemModel()\n            self.fs_model.setRootPath(QDir.rootPath())\n            self.fs_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)\n            \n            # Set the model to the tree view\n            if self.directory_tree:\n                self.directory_tree.setModel(self.fs_model)\n                \n                # Hide unnecessary columns (only show name)\n                self.directory_tree.hideColumn(1)  # Size\n                self.directory_tree.hideColumn(2)  # Type\n                self.directory_tree.hideColumn(3)  # Date Modified\n                \n                # Set root index\n                root_index = self.fs_model.index(QDir.rootPath())\n                self.directory_tree.setRootIndex(root_index)\n                \n                # Expand to show some directories initially\n                self.directory_tree.expand(root_index)\n            \n            logger.debug(\"File system model setup completed\")\n            \n        except Exception as e:\n            logger.error(f\"Error setting up file system model: {str(e)}\")\n            self._update_status(f\"Error initializing directory browser: {str(e)}\", is_error=True)\n    \n    def _setup_connections(self):\n        \"\"\"Setup signal connections.\"\"\"\n        if not PYQT5_AVAILABLE:\n            return\n        \n        # Tree selection change\n        if self.directory_tree and self.directory_tree.selectionModel():\n            self.directory_tree.selectionModel().selectionChanged.connect(\n                self._on_tree_selection_changed\n            )\n        \n        # List selection change\n        if self.selected_list:\n            self.selected_list.itemSelectionChanged.connect(\n                self._on_list_selection_changed\n            )\n        \n        # Double-click on tree to add directory\n        if self.directory_tree:\n            self.directory_tree.doubleClicked.connect(self._on_tree_double_click)\n    \n    def _setup_validation(self):\n        \"\"\"Setup path validation system.\"\"\"\n        # Create validation timer for debounced validation\n        self.validation_timer = QTimer()\n        self.validation_timer.setSingleShot(True)\n        self.validation_timer.timeout.connect(self._validate_current_path)\n    \n    def _setup_accessibility(self):\n        \"\"\"Setup accessibility features.\"\"\"\n        # Set accessible names and descriptions\n        self.setAccessibleName(\"Directory Browser Widget\")\n        self.setAccessibleDescription(\n            \"Browse and select directories for folder configuration\"\n        )\n        \n        if self.directory_tree:\n            self.directory_tree.setAccessibleName(\"Directory Tree Browser\")\n            self.directory_tree.setAccessibleDescription(\n                \"Browse file system directories\"\n            )\n        \n        if self.selected_list:\n            self.selected_list.setAccessibleName(\"Selected Directories List\")\n            self.selected_list.setAccessibleDescription(\n                \"List of selected directories for configuration\"\n            )\n        \n        if self.path_edit:\n            self.path_edit.setAccessibleName(\"Directory Path Input\")\n            self.path_edit.setAccessibleDescription(\n                \"Enter directory path manually\"\n            )\n    \n    def _browse_directory(self):\n        \"\"\"Open directory browse dialog.\"\"\"\n        dialog = QFileDialog(self)\n        dialog.setFileMode(QFileDialog.Directory)\n        dialog.setOption(QFileDialog.ShowDirsOnly, True)\n        dialog.setWindowTitle(\"Select Directory\")\n        \n        # Set starting directory\n        current_path = self.path_edit.text().strip()\n        if current_path and Path(current_path).exists():\n            dialog.setDirectory(current_path)\n        else:\n            dialog.setDirectory(QDir.homePath())\n        \n        if dialog.exec_() == QFileDialog.Accepted:\n            selected_dirs = dialog.selectedFiles()\n            if selected_dirs:\n                directory_path = selected_dirs[0]\n                self.path_edit.setText(directory_path)\n                self._validate_current_path()\n                logger.debug(f\"Directory selected via browse: {directory_path}\")\n    \n    def _add_current_directory(self):\n        \"\"\"Add the current path to the selected directories.\"\"\"\n        current_path = self.path_edit.text().strip()\n        if not current_path:\n            return\n        \n        # Validate path\n        path = Path(current_path)\n        if not path.exists():\n            self._show_error(\"Directory does not exist\")\n            return\n        \n        if not path.is_dir():\n            self._show_error(\"Path is not a directory\")\n            return\n        \n        # Check for duplicates\n        normalized_path = str(path.resolve())\n        if normalized_path in self.selected_directories:\n            self._show_error(\"Directory is already selected\")\n            return\n        \n        # Check directory limit\n        if len(self.selected_directories) >= self.max_directories:\n            self._show_error(f\"Maximum {self.max_directories} directories allowed\")\n            return\n        \n        # Add to selected directories\n        self.selected_directories.add(normalized_path)\n        self._update_selected_list()\n        self.path_edit.clear()\n        self.add_button.setEnabled(False)\n        \n        # Emit signal\n        self.directories_changed.emit(list(self.selected_directories))\n        \n        self._update_status(f\"Added directory: {Path(normalized_path).name}\")\n        logger.info(f\"Directory added: {normalized_path}\")\n    \n    def _remove_selected_directories(self):\n        \"\"\"Remove selected directories from the list.\"\"\"\n        selected_items = self.selected_list.selectedItems()\n        if not selected_items:\n            return\n        \n        # Confirm removal if multiple items\n        if len(selected_items) > 1:\n            reply = QMessageBox.question(\n                self,\n                \"Remove Directories\",\n                f\"Remove {len(selected_items)} selected directories?\",\n                QMessageBox.Yes | QMessageBox.No,\n                QMessageBox.Yes\n            )\n            if reply != QMessageBox.Yes:\n                return\n        \n        # Remove directories\n        for item in selected_items:\n            directory_path = item.text()\n            self.selected_directories.discard(directory_path)\n        \n        self._update_selected_list()\n        \n        # Emit signal\n        self.directories_changed.emit(list(self.selected_directories))\n        \n        self._update_status(f\"Removed {len(selected_items)} directories\")\n        logger.info(f\"Removed {len(selected_items)} directories\")\n    \n    def _clear_all_directories(self):\n        \"\"\"Clear all selected directories.\"\"\"\n        if not self.selected_directories:\n            return\n        \n        # Confirm clear operation\n        reply = QMessageBox.question(\n            self,\n            \"Clear All Directories\",\n            f\"Remove all {len(self.selected_directories)} selected directories?\",\n            QMessageBox.Yes | QMessageBox.No,\n            QMessageBox.No\n        )\n        \n        if reply == QMessageBox.Yes:\n            self.selected_directories.clear()\n            self._update_selected_list()\n            \n            # Emit signal\n            self.directories_changed.emit(list(self.selected_directories))\n            \n            self._update_status(\"All directories cleared\")\n            logger.info(\"All directories cleared\")\n    \n    def _validate_current_path(self):\n        \"\"\"Validate the current path in the input field.\"\"\"\n        current_path = self.path_edit.text().strip()\n        \n        if not current_path:\n            self.add_button.setEnabled(False)\n            self._update_status(\"Enter a directory path\")\n            return\n        \n        try:\n            path = Path(current_path)\n            \n            # Check if path exists\n            if not path.exists():\n                self.add_button.setEnabled(False)\n                self._update_status(\"Directory does not exist\", is_error=True)\n                self.path_validated.emit(current_path, False)\n                return\n            \n            # Check if it's a directory\n            if not path.is_dir():\n                self.add_button.setEnabled(False)\n                self._update_status(\"Path is not a directory\", is_error=True)\n                self.path_validated.emit(current_path, False)\n                return\n            \n            # Check for duplicates\n            normalized_path = str(path.resolve())\n            if normalized_path in self.selected_directories:\n                self.add_button.setEnabled(False)\n                self._update_status(\"Directory already selected\", is_error=True)\n                self.path_validated.emit(current_path, False)\n                return\n            \n            # Check directory limit\n            if len(self.selected_directories) >= self.max_directories:\n                self.add_button.setEnabled(False)\n                self._update_status(f\"Maximum {self.max_directories} directories allowed\", is_error=True)\n                self.path_validated.emit(current_path, False)\n                return\n            \n            # Path is valid\n            self.add_button.setEnabled(not self.is_read_only)\n            self._update_status(f\"Valid directory: {path.name}\")\n            self.path_validated.emit(current_path, True)\n            \n        except Exception as e:\n            self.add_button.setEnabled(False)\n            error_msg = f\"Path validation error: {str(e)}\"\n            self._update_status(error_msg, is_error=True)\n            self.path_validated.emit(current_path, False)\n            logger.error(error_msg)\n    \n    def _update_selected_list(self):\n        \"\"\"Update the selected directories list widget.\"\"\"\n        self.selected_list.clear()\n        \n        for directory in sorted(self.selected_directories):\n            item = QListWidgetItem(directory)\n            item.setToolTip(directory)\n            # Add icon based on directory type\n            item.setText(f\"{Icons.FOLDER_OPEN} {directory}\")\n            self.selected_list.addItem(item)\n        \n        # Update count label\n        count = len(self.selected_directories)\n        self.count_label.setText(f\"{count} director{'y' if count == 1 else 'ies'} selected\")\n        \n        # Update button states\n        self._on_list_selection_changed()\n    \n    def _update_status(self, message, is_error=False):\n        \"\"\"Update the status label.\"\"\"\n        if self.status_label:\n            self.status_label.setText(message)\n            if is_error:\n                self.status_label.setStyleSheet(f\"color: {Colors.TEXT_ERROR};\")\n            else:\n                self.status_label.setStyleSheet(f\"color: {Colors.TEXT_SECONDARY};\")\n    \n    def _show_error(self, message):\n        \"\"\"Show an error message.\"\"\"\n        self._update_status(message, is_error=True)\n        self.validation_error.emit(message)\n    \n    def _on_path_changed(self, text):\n        \"\"\"Handle path input changes.\"\"\"\n        # Trigger delayed validation\n        if self.validation_timer:\n            self.validation_timer.start(500)  # 500ms delay\n    \n    def _on_tree_selection_changed(self, selected, deselected):\n        \"\"\"Handle tree view selection changes.\"\"\"\n        if not self.directory_tree or not self.fs_model:\n            return\n        \n        # Get selected index\n        indexes = selected.indexes()\n        if indexes:\n            index = indexes[0]\n            file_path = self.fs_model.filePath(index)\n            \n            # Update path input\n            self.path_edit.setText(file_path)\n            self._validate_current_path()\n            \n            # Emit selection signal\n            self.directory_selected.emit(file_path)\n            logger.debug(f\"Tree selection changed: {file_path}\")\n    \n    def _on_tree_double_click(self, index):\n        \"\"\"Handle double-click on tree view.\"\"\"\n        if not self.fs_model:\n            return\n        \n        file_path = self.fs_model.filePath(index)\n        self.path_edit.setText(file_path)\n        self._validate_current_path()\n        \n        # Auto-add if valid\n        if self.add_button.isEnabled():\n            self._add_current_directory()\n    \n    def _on_list_selection_changed(self):\n        \"\"\"Handle selected directories list selection changes.\"\"\"\n        has_selection = bool(self.selected_list.selectedItems())\n        self.remove_button.setEnabled(has_selection and not self.is_read_only)\n    \n    # Public interface methods\n    \n    def get_directories(self) -> List[str]:\n        \"\"\"Get the list of selected directories.\"\"\"\n        return list(self.selected_directories)\n    \n    def set_directories(self, directories: List[str]):\n        \"\"\"Set the selected directories list.\"\"\"\n        self.selected_directories.clear()\n        \n        for directory in directories:\n            try:\n                path = Path(directory)\n                if path.exists() and path.is_dir():\n                    normalized_path = str(path.resolve())\n                    self.selected_directories.add(normalized_path)\n                else:\n                    logger.warning(f\"Invalid directory skipped: {directory}\")\n            except Exception as e:\n                logger.error(f\"Error processing directory {directory}: {str(e)}\")\n        \n        self._update_selected_list()\n        self.directories_changed.emit(list(self.selected_directories))\n        logger.info(f\"Set {len(self.selected_directories)} directories\")\n    \n    def add_directory(self, directory_path: str) -> bool:\n        \"\"\"Add a directory to the selection.\"\"\"\n        try:\n            path = Path(directory_path)\n            if not path.exists() or not path.is_dir():\n                return False\n            \n            normalized_path = str(path.resolve())\n            if normalized_path not in self.selected_directories:\n                if len(self.selected_directories) < self.max_directories:\n                    self.selected_directories.add(normalized_path)\n                    self._update_selected_list()\n                    self.directories_changed.emit(list(self.selected_directories))\n                    return True\n            \n            return False\n            \n        except Exception as e:\n            logger.error(f\"Error adding directory {directory_path}: {str(e)}\")\n            return False\n    \n    def remove_directory(self, directory_path: str) -> bool:\n        \"\"\"Remove a directory from the selection.\"\"\"\n        try:\n            path = Path(directory_path)\n            normalized_path = str(path.resolve())\n            \n            if normalized_path in self.selected_directories:\n                self.selected_directories.remove(normalized_path)\n                self._update_selected_list()\n                self.directories_changed.emit(list(self.selected_directories))\n                return True\n            \n            return False\n            \n        except Exception as e:\n            logger.error(f\"Error removing directory {directory_path}: {str(e)}\")\n            return False\n    \n    def clear_directories(self):\n        \"\"\"Clear all selected directories.\"\"\"\n        self.selected_directories.clear()\n        self._update_selected_list()\n        self.directories_changed.emit(list(self.selected_directories))\n        logger.info(\"All directories cleared\")\n    \n    def set_read_only(self, read_only=True):\n        \"\"\"Set the widget to read-only mode.\"\"\"\n        self.is_read_only = read_only\n        \n        # Update UI components\n        if self.path_edit:\n            self.path_edit.setReadOnly(read_only)\n        \n        if self.add_button:\n            self.add_button.setEnabled(not read_only)\n        \n        if self.remove_button:\n            self.remove_button.setEnabled(not read_only and bool(self.selected_list.selectedItems()))\n        \n        if self.browse_button:\n            self.browse_button.setEnabled(not read_only)\n    \n    def set_max_directories(self, max_count: int):\n        \"\"\"Set the maximum number of directories allowed.\"\"\"\n        self.max_directories = max(1, min(max_count, 1000))  # Reasonable limits\n        logger.debug(f\"Maximum directories set to {self.max_directories}\")\n    \n    def get_directory_count(self) -> int:\n        \"\"\"Get the current number of selected directories.\"\"\"\n        return len(self.selected_directories)\n    \n    def validate_directories(self) -> List[str]:\n        \"\"\"Validate all selected directories and return any errors.\"\"\"\n        errors = []\n        \n        if not self.selected_directories:\n            errors.append(\"At least one directory must be selected\")\n            return errors\n        \n        for directory in self.selected_directories:\n            try:\n                path = Path(directory)\n                if not path.exists():\n                    errors.append(f\"Directory does not exist: {directory}\")\n                elif not path.is_dir():\n                    errors.append(f\"Path is not a directory: {directory}\")\n                # Additional validation can be added here\n                \n            except Exception as e:\n                errors.append(f\"Error validating {directory}: {str(e)}\")\n        \n        return errors\n\n\n# Testing support\nif __name__ == \"__main__\":\n    import sys\n    from PyQt5.QtWidgets import QApplication\n    \n    app = QApplication(sys.argv)\n    \n    # Create test widget\n    widget = DirectoryBrowserWidget()\n    widget.resize(800, 600)\n    widget.show()\n    \n    # Connect signals for testing\n    widget.directories_changed.connect(\n        lambda dirs: print(f\"Directories changed: {dirs}\")\n    )\n    widget.directory_selected.connect(\n        lambda path: print(f\"Directory selected: {path}\")\n    )\n    \n    sys.exit(app.exec_())