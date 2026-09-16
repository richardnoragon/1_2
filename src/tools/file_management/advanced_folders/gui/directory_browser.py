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
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from PyQt5.QtCore import (
        QAbstractItemModel,
        QDir,
        QFileSystemWatcher,
        QItemSelectionModel,
        QModelIndex,
        Qt,
        QTimer,
        pyqtSignal,
    )
    from PyQt5.QtGui import (
        QFileSystemModel,
        QFont,
        QIcon,
        QPalette,
        QPixmap,
        QStandardItem,
        QStandardItemModel,
    )
    from PyQt5.QtWidgets import (
        QAbstractItemView,
        QAction,
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMenu,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSplitter,
        QTreeView,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.inputs import TextInput

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    QWidget = object
    pyqtSignal = None
    PrimaryButton = None
    SecondaryButton = None

try:
    from src.gui.components.modal import Modal
except ImportError:
    Modal = None

try:
    from src.gui.components.toast import ToastNotification
except ImportError:
    ToastNotification = None

# Import constants and styling
try:
    from .constants import (
        Accessibility,
        Colors,
        Fonts,
        Icons,
        Layout,
        Styles,
        Validation,
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

    logger = get_log_manager().get_logger("AdvancedFolders.DirectoryBrowser")
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
    directory_selected = pyqtSignal(str)  # Selected directory path
    validation_error = pyqtSignal(str)  # Error message
    path_validated = pyqtSignal(str, bool)  # Path, is_valid

    def __init__(self, parent=None, initial_directories=None, mode="multi"):
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
        self._toast = None

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
        header_group = _ui_widget(QGroupBox, 'Legacy.s30d2d5574cce5ea3', 'setTitle')
        header_group.setStyleSheet(Styles.GROUP_BOX_STYLE)
        header_group.setMaximumHeight(120)

        layout = QVBoxLayout(header_group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(Layout.ITEM_SPACING)

        # Path input section  (CP-9b)
        self.path_edit = TextInput(
            label="Directory Path",
            placeholder="Enter or browse for directory path...",
            accessible_name="Directory path",
            accessible_description="Filesystem path — enter manually or use Browse",
        )
        self.path_edit.set_validator(
            lambda t: (True, "") if t.strip() else (False, "Path cannot be empty")
        )
        self.path_edit.textChanged.connect(self._on_path_changed)
        layout.addWidget(self.path_edit)

        # Control buttons
        buttons_layout = QHBoxLayout()

        self.browse_button = SecondaryButton(f"{Icons.FOLDER_OPEN} Browse")
        self.browse_button.clicked.connect(self._browse_directory)
        buttons_layout.addWidget(self.browse_button)

        self.validate_button = _ui_widget(SecondaryButton, 'Legacy.sc5dc2be72f2a7044', 'setText')
        self.validate_button.clicked.connect(self._validate_current_path)
        buttons_layout.addWidget(self.validate_button)

        self.add_button = PrimaryButton(f"{Icons.ADD} Add Directory")
        self.add_button.clicked.connect(self._add_current_directory)
        self.add_button.setEnabled(False)
        buttons_layout.addWidget(self.add_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        return header_group

    def _create_content_area(self):
        """Create the main content area with directory tree and selected list."""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Directory tree browser
        tree_widget = self._create_tree_browser()
        splitter.addWidget(tree_widget)

        # Selected directories list
        list_widget = self._create_selected_list()
        splitter.addWidget(list_widget)

        # Set splitter proportions (60% tree, 40% list)
        splitter.setSizes([400, 250])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        return splitter

    def _create_tree_browser(self):
        """Create the directory tree browser."""
        tree_group = _ui_widget(QGroupBox, 'Legacy.s1858f6ccbc7787e8', 'setTitle')
        tree_group.setStyleSheet(Styles.GROUP_BOX_STYLE)

        layout = QVBoxLayout(tree_group)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(5)

        # Tree view
        self.directory_tree = QTreeView()
        self.directory_tree.setHeaderHidden(True)
        self.directory_tree.setRootIsDecorated(True)
        self.directory_tree.setAlternatingRowColors(True)
        self.directory_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.directory_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Apply styling
        self.directory_tree.setStyleSheet(
            f"""
            QTreeView {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                background-color: {Colors.BACKGROUND_MAIN};
                alternate-background-color: {Colors.BACKGROUND_SECONDARY};
                selection-background-color: {Colors.BACKGROUND_SELECTED};
                outline: none;
            }}

            QTreeView::item {{
                padding: 4px 8px;
                border-bottom: 1px solid {Colors.BORDER_LIGHT};
            }}

            QTreeView::item:selected {{
                background-color: {Colors.BACKGROUND_SELECTED};
                color: {Colors.TEXT_PRIMARY};
            }}

            QTreeView::item:hover:!selected {{
                background-color: {Colors.BACKGROUND_HOVER};
            }}
        """
        )

        layout.addWidget(self.directory_tree)

        return tree_group

    def _create_selected_list(self):
        """Create the selected directories list."""
        list_group = _ui_widget(QGroupBox, 'Legacy.s6af7276c46eaf5c8', 'setTitle')
        list_group.setStyleSheet(Styles.GROUP_BOX_STYLE)

        layout = QVBoxLayout(list_group)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(Layout.ITEM_SPACING)

        # Selected directories list
        self.selected_list = QListWidget()
        self.selected_list.setStyleSheet(Styles.LIST_WIDGET_STYLE)
        self.selected_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.selected_list.setMinimumHeight(200)
        _ui_bind(self.selected_list, 'setAccessibleName', 'Legacy.s8137428a9969234f')
        layout.addWidget(self.selected_list)

        # List control buttons
        list_buttons_layout = QHBoxLayout()

        self.remove_button = SecondaryButton(f"{Icons.REMOVE} Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected_directories)
        self.remove_button.setEnabled(False)
        list_buttons_layout.addWidget(self.remove_button)

        clear_button = _ui_widget(SecondaryButton, 'Legacy.sddceb7adfdb8816e', 'setText')
        clear_button.clicked.connect(self._clear_all_directories)
        list_buttons_layout.addWidget(clear_button)

        list_buttons_layout.addStretch()
        layout.addLayout(list_buttons_layout)

        # Directory count label
        self.count_label = _ui_widget(QLabel, 'Legacy.sf6d9c91d506bf099', 'setText')
        self.count_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; "
        )
        font_tokens.bind(self.count_label, "font.body")
        layout.addWidget(self.count_label)

        return list_group

    def _create_status_section(self):
        """Create the status information section."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setLineWidth(1)
        status_frame.setFixedHeight(30)

        layout = QHBoxLayout(status_frame)
        layout.setContentsMargins(10, 5, 10, 5)

        # Status label
        self.status_label = _ui_widget(QLabel, 'Legacy.s9e75dadea64f4b77', 'setText')
        self.status_label.setFont(Fonts.label_font())
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.status_label.setVisible(False)  # replaced by ToastNotification
        self._toast = (
            ToastNotification(self, role="info") if ToastNotification else None
        )

        layout.addWidget(self.status_label)
        layout.addStretch()

        return status_frame

    def _setup_file_system_model(self):
        """Setup the file system model for the tree view."""
        if not PYQT5_AVAILABLE:
            return

        try:
            self.fs_model = QFileSystemModel()
            self.fs_model.setRootPath(QDir.rootPath())
            self.fs_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)

            # Set the model to the tree view
            if self.directory_tree:
                self.directory_tree.setModel(self.fs_model)

                # Hide unnecessary columns (only show name)
                self.directory_tree.hideColumn(1)  # Size
                self.directory_tree.hideColumn(2)  # Type
                self.directory_tree.hideColumn(3)  # Date Modified

                # Set root index
                root_index = self.fs_model.index(QDir.rootPath())
                self.directory_tree.setRootIndex(root_index)

                # Expand to show some directories initially
                self.directory_tree.expand(root_index)

            logger.debug("File system model setup completed")

        except Exception as e:
            logger.error(f"Error setting up file system model: {str(e)}")
            self._update_status(
                f"Error initializing directory browser: {str(e)}", is_error=True
            )

    def _setup_connections(self):
        """Setup signal connections."""
        if not PYQT5_AVAILABLE:
            return

        # Tree selection change
        if self.directory_tree and self.directory_tree.selectionModel():
            self.directory_tree.selectionModel().selectionChanged.connect(
                self._on_tree_selection_changed
            )

        # List selection change
        if self.selected_list:
            self.selected_list.itemSelectionChanged.connect(
                self._on_list_selection_changed
            )

        # Double-click on tree to add directory
        if self.directory_tree:
            self.directory_tree.doubleClicked.connect(self._on_tree_double_click)

    def _setup_validation(self):
        """Setup path validation system."""
        # Create validation timer for debounced validation
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_current_path)

    def _setup_accessibility(self):
        """Setup accessibility features."""
        # Set accessible names and descriptions
        _ui_bind(self, 'setAccessibleName', 'Legacy.sf257f6b403d10328')
        _ui_bind(self, 'setAccessibleDescription', 'Legacy.sa88c5cdf57718450')

        if self.directory_tree:
            _ui_bind(self.directory_tree, 'setAccessibleName', 'Legacy.sa253a2a7702d956f')
            _ui_bind(self.directory_tree, 'setAccessibleDescription', 'Legacy.s4d29769a4ebd235e')

        if self.selected_list:
            _ui_bind(self.selected_list, 'setAccessibleName', 'Legacy.sc4a27bcf73041d15')
            _ui_bind(self.selected_list, 'setAccessibleDescription', 'Legacy.s91d9539afc728996')

        if self.path_edit:
            _ui_bind(self.path_edit, 'setAccessibleName', 'Legacy.sb5a377572fde8bde')
            _ui_bind(self.path_edit, 'setAccessibleDescription', 'Legacy.s6752e3e5454d7dbf')

    def _browse_directory(self):
        """Open directory browse dialog."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        _ui_bind(dialog, 'setWindowTitle', 'Legacy.s220c3fe6289ca828')

        # Set starting directory
        current_path = self.path_edit.text().strip()
        if current_path and Path(current_path).exists():
            dialog.setDirectory(current_path)
        else:
            dialog.setDirectory(QDir.homePath())

        if dialog.exec_() == QFileDialog.Accepted:
            selected_dirs = dialog.selectedFiles()
            if selected_dirs:
                directory_path = selected_dirs[0]
                self.path_edit.setText(directory_path)
                self._validate_current_path()
                logger.debug(f"Directory selected via browse: {directory_path}")

    def _add_current_directory(self):
        """Add the current path to the selected directories."""
        current_path = self.path_edit.text().strip()
        if not current_path:
            return

        # Validate path
        path = Path(current_path)
        if not path.exists():
            self._show_error("Directory does not exist")
            return

        if not path.is_dir():
            self._show_error("Path is not a directory")
            return

        # Check for duplicates
        normalized_path = str(path.resolve())
        if normalized_path in self.selected_directories:
            self._show_error("Directory is already selected")
            return

        # Check directory limit
        if len(self.selected_directories) >= self.max_directories:
            self._show_error(f"Maximum {self.max_directories} directories allowed")
            return

        # Add to selected directories
        self.selected_directories.add(normalized_path)
        self._update_selected_list()
        self.path_edit.clear()
        self.add_button.setEnabled(False)

        # Emit signal
        self.directories_changed.emit(list(self.selected_directories))

        self._update_status(f"Added directory: {Path(normalized_path).name}")
        logger.info(f"Directory added: {normalized_path}")

    def _remove_selected_directories(self):
        """Remove selected directories from the list."""
        selected_items = self.selected_list.selectedItems()
        if not selected_items:
            return

        # Confirm removal if multiple items
        if len(selected_items) > 1:
            if (
                Modal(
                    "Remove Directories",
                    f"Remove {len(selected_items)} selected directories?",
                    ["Yes", "No"],
                    self,
                ).exec_()
                != QDialog.Accepted
            ):
                return

        # Remove directories
        for item in selected_items:
            directory_path = item.text()
            self.selected_directories.discard(directory_path)

        self._update_selected_list()

        # Emit signal
        self.directories_changed.emit(list(self.selected_directories))

        self._update_status(f"Removed {len(selected_items)} directories")
        logger.info(f"Removed {len(selected_items)} directories")

    def _clear_all_directories(self):
        """Clear all selected directories."""
        if not self.selected_directories:
            return

        # Confirm clear operation
        if (
            Modal(
                "Clear All Directories",
                f"Remove all {len(self.selected_directories)} selected directories?",
                ["Yes", "No"],
                self,
            ).exec_()
            == QDialog.Accepted
        ):
            self.selected_directories.clear()
            self._update_selected_list()

            # Emit signal
            self.directories_changed.emit(list(self.selected_directories))

            self._update_status("All directories cleared")
            logger.info("All directories cleared")

    def _validate_current_path(self):
        """Validate the current path in the input field."""
        current_path = self.path_edit.text().strip()

        if not current_path:
            self.add_button.setEnabled(False)
            self._update_status("Enter a directory path")
            return

        try:
            path = Path(current_path)

            # Check if path exists
            if not path.exists():
                self.add_button.setEnabled(False)
                self._update_status("Directory does not exist", is_error=True)
                self.path_validated.emit(current_path, False)
                return

            # Check if it's a directory
            if not path.is_dir():
                self.add_button.setEnabled(False)
                self._update_status("Path is not a directory", is_error=True)
                self.path_validated.emit(current_path, False)
                return

            # Check for duplicates
            normalized_path = str(path.resolve())
            if normalized_path in self.selected_directories:
                self.add_button.setEnabled(False)
                self._update_status("Directory already selected", is_error=True)
                self.path_validated.emit(current_path, False)
                return

            # Check directory limit
            if len(self.selected_directories) >= self.max_directories:
                self.add_button.setEnabled(False)
                self._update_status(
                    f"Maximum {self.max_directories} directories allowed", is_error=True
                )
                self.path_validated.emit(current_path, False)
                return

            # Path is valid
            self.add_button.setEnabled(not self.is_read_only)
            self._update_status(f"Valid directory: {path.name}")
            self.path_validated.emit(current_path, True)

        except Exception as e:
            self.add_button.setEnabled(False)
            error_msg = f"Path validation error: {str(e)}"
            self._update_status(error_msg, is_error=True)
            self.path_validated.emit(current_path, False)
            logger.error(error_msg)

    def _update_selected_list(self):
        """Update the selected directories list widget."""
        self.selected_list.clear()

        for directory in sorted(self.selected_directories):
            item = QListWidgetItem(directory)
            item.setToolTip(directory)
            # Add icon based on directory type
            item.setText(f"{Icons.FOLDER_OPEN} {directory}")
            self.selected_list.addItem(item)

        # Update count label
        count = len(self.selected_directories)
        self.count_label.setText(
            f"{count} director{'y' if count == 1 else 'ies'} selected"
        )

        # Update button states
        self._on_list_selection_changed()

    def _update_status(self, message, is_error=False):
        """Update the status label."""
        if self._toast:
            self._toast.show_message(message, "error" if is_error else "info")

    def _show_error(self, message):
        """Show an error message."""
        self._update_status(message, is_error=True)
        self.validation_error.emit(message)

    def _on_path_changed(self, text):
        """Handle path input changes."""
        # Trigger delayed validation
        if self.validation_timer:
            self.validation_timer.start(500)  # 500ms delay

    def _on_tree_selection_changed(self, selected, deselected):
        """Handle tree view selection changes."""
        if not self.directory_tree or not self.fs_model:
            return

        # Get selected index
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            file_path = self.fs_model.filePath(index)

            # Update path input
            self.path_edit.setText(file_path)
            self._validate_current_path()

            # Emit selection signal
            self.directory_selected.emit(file_path)
            logger.debug(f"Tree selection changed: {file_path}")

    def _on_tree_double_click(self, index):
        """Handle double-click on tree view."""
        if not self.fs_model:
            return

        file_path = self.fs_model.filePath(index)
        self.path_edit.setText(file_path)
        self._validate_current_path()

        # Auto-add if valid
        if self.add_button.isEnabled():
            self._add_current_directory()

    def _on_list_selection_changed(self):
        """Handle selected directories list selection changes."""
        has_selection = bool(self.selected_list.selectedItems())
        self.remove_button.setEnabled(has_selection and not self.is_read_only)

    # Public interface methods

    def get_directories(self) -> List[str]:
        """Get the list of selected directories."""
        return list(self.selected_directories)

    def set_directories(self, directories: List[str]):
        """Set the selected directories list."""
        self.selected_directories.clear()

        for directory in directories:
            try:
                path = Path(directory)
                if path.exists() and path.is_dir():
                    normalized_path = str(path.resolve())
                    self.selected_directories.add(normalized_path)
                else:
                    logger.warning(f"Invalid directory skipped: {directory}")
            except Exception as e:
                logger.error(f"Error processing directory {directory}: {str(e)}")

        self._update_selected_list()
        self.directories_changed.emit(list(self.selected_directories))
        logger.info(f"Set {len(self.selected_directories)} directories")

    def add_directory(self, directory_path: str) -> bool:
        """Add a directory to the selection."""
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                return False

            normalized_path = str(path.resolve())
            if normalized_path not in self.selected_directories:
                if len(self.selected_directories) < self.max_directories:
                    self.selected_directories.add(normalized_path)
                    self._update_selected_list()
                    self.directories_changed.emit(list(self.selected_directories))
                    return True

            return False

        except Exception as e:
            logger.error(f"Error adding directory {directory_path}: {str(e)}")
            return False

    def remove_directory(self, directory_path: str) -> bool:
        """Remove a directory from the selection."""
        try:
            path = Path(directory_path)
            normalized_path = str(path.resolve())

            if normalized_path in self.selected_directories:
                self.selected_directories.remove(normalized_path)
                self._update_selected_list()
                self.directories_changed.emit(list(self.selected_directories))
                return True

            return False

        except Exception as e:
            logger.error(f"Error removing directory {directory_path}: {str(e)}")
            return False

    def clear_directories(self):
        """Clear all selected directories."""
        self.selected_directories.clear()
        self._update_selected_list()
        self.directories_changed.emit(list(self.selected_directories))
        logger.info("All directories cleared")

    def set_read_only(self, read_only=True):
        """Set the widget to read-only mode."""
        self.is_read_only = read_only

        # Update UI components
        if self.path_edit:
            self.path_edit.setReadOnly(read_only)

        if self.add_button:
            self.add_button.setEnabled(not read_only)

        if self.remove_button:
            self.remove_button.setEnabled(
                not read_only and bool(self.selected_list.selectedItems())
            )

        if self.browse_button:
            self.browse_button.setEnabled(not read_only)

    def set_max_directories(self, max_count: int):
        """Set the maximum number of directories allowed."""
        self.max_directories = max(1, min(max_count, 1000))  # Reasonable limits
        logger.debug(f"Maximum directories set to {self.max_directories}")

    def get_directory_count(self) -> int:
        """Get the current number of selected directories."""
        return len(self.selected_directories)

    def validate_directories(self) -> List[str]:
        """Validate all selected directories and return any errors."""
        errors = []

        if not self.selected_directories:
            errors.append("At least one directory must be selected")
            return errors

        for directory in self.selected_directories:
            try:
                path = Path(directory)
                if not path.exists():
                    errors.append(f"Directory does not exist: {directory}")
                elif not path.is_dir():
                    errors.append(f"Path is not a directory: {directory}")
                # Additional validation can be added here

            except Exception as e:
                errors.append(f"Error validating {directory}: {str(e)}")

        return errors


# Testing support
if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create test widget
    widget = DirectoryBrowserWidget()
    widget.resize(800, 600)
    widget.show()

    # Connect signals for testing
    widget.directories_changed.connect(
        lambda dirs: print(f"Directories changed: {dirs}")
    )
    widget.directory_selected.connect(lambda path: print(f"Directory selected: {path}"))
