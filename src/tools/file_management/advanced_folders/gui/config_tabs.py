"""
Advanced Folders Configuration Tabs

Enterprise-grade configuration tab implementations for the Advanced Folders
feature. Provides specialized interfaces for different configuration aspects:
- General: Basic folder settings and directory management
- Search: Advanced search parameters and indexing options
- Filters: File type filters and exclusion patterns
- Display: View options and presentation settings

Each tab follows enterprise UI patterns with comprehensive validation,
accessibility support, and professional styling.

Author: RFU Development Team
Version: 1.0.0
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator, QValidator
    from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpinBox,
        QSplitter,
        QTabWidget,
        QTextEdit,
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

# Import constants and styling
try:
    from .constants import (
        Accessibility,
        Colors,
        FileTypes,
        Fonts,
        Icons,
        Layout,
        SearchConfig,
        Styles,
        Validation,
    )
except ImportError:
    # Fallback constants
    class Colors:
        PRIMARY_BLUE = "#3498db"
        BACKGROUND_MAIN = "#ffffff"
        TEXT_PRIMARY = "#2c3e50"

    class Layout:
        CONTENT_MARGIN = 20
        SECTION_SPACING = 15

    class Icons:
        ADD = "+"
        REMOVE = "-"
        SETTINGS = "⚙"


# Import backend models
try:
    from ..core import FolderConfiguration, SearchParameter, ValidationResult

    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

    class FolderConfiguration:
        pass

    class ValidationResult:
        def __init__(self, is_valid=True, errors=None):
            self.is_valid = is_valid
            self.errors = errors or []


# Import logging
try:
    from src.log_manager import get_log_manager

    logger = get_log_manager().get_logger("AdvancedFolders.ConfigTabs")
except ImportError:
    logger = logging.getLogger(__name__)


class BaseConfigTab(QWidget):
    """
    Base class for configuration tabs.

    Provides common functionality including validation, data management,
    and accessibility features that all configuration tabs inherit.
    """

    # Signal emitted when tab data changes
    data_changed = pyqtSignal()

    def __init__(self, configuration=None, mode="create", parent=None):
        """
        Initialize base configuration tab.

        Args:
            configuration: FolderConfiguration object
            mode: Dialog mode ('create', 'edit', 'view')
            parent: Parent widget
        """
        super().__init__(parent)

        self.configuration = configuration
        self.mode = mode
        self.is_read_only = mode == "view"
        self.validation_errors = []

        # Setup the tab interface
        self._setup_ui()
        self._setup_validation()
        self._setup_accessibility()

        # Load configuration if provided
        if configuration:
            self.load_configuration(configuration)

    def _setup_ui(self):
        """Setup the basic UI structure. Override in subclasses."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN,
            Layout.CONTENT_MARGIN,
        )
        layout.setSpacing(Layout.SECTION_SPACING)

    def _setup_validation(self):
        """Setup validation for the tab. Override in subclasses."""
        pass

    def _setup_accessibility(self):
        """Setup accessibility features. Override in subclasses."""
        pass

    def load_configuration(self, configuration):
        """Load configuration data into the tab. Override in subclasses."""
        self.configuration = configuration

    def get_data(self):
        """Get configuration data from the tab. Override in subclasses."""
        return {}

    def validate(self):
        """Validate tab data. Override in subclasses."""
        return []

    def set_read_only(self, read_only=True):
        """Set the tab to read-only mode."""
        self.is_read_only = read_only
        # Implementation depends on subclass widgets

    def _emit_data_changed(self):
        """Emit data changed signal."""
        self.data_changed.emit()


class GeneralConfigTab(BaseConfigTab):
    """
    General configuration tab for basic folder settings.

    Provides interface for:
    - Folder name and description
    - Target directories management
    - Basic folder options
    - Monitoring settings
    """

    def __init__(self, configuration=None, mode="create", parent=None):
        """Initialize general configuration tab."""
        self.name_edit = None
        self.description_edit = None
        self.directories_list = None
        self.add_directory_btn = None
        self.remove_directory_btn = None
        self.browse_directory_btn = None
        self.include_subdirs_cb = None
        self.follow_symlinks_cb = None
        self.include_hidden_cb = None
        self.monitor_changes_cb = None

        super().__init__(configuration, mode, parent)

    def _setup_ui(self):
        """Setup the general configuration interface."""
        super()._setup_ui()
        layout = self.layout()

        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(Layout.SECTION_SPACING)

        # Basic information section
        basic_group = self._create_basic_info_section()
        content_layout.addWidget(basic_group)

        # Directory management section
        directories_group = self._create_directories_section()
        content_layout.addWidget(directories_group)

        # Options section
        options_group = self._create_options_section()
        content_layout.addWidget(options_group)

        # Add stretch at bottom
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _create_basic_info_section(self):
        """Create the basic information section."""
        group = _ui_widget(QGroupBox, 'Legacy.sd094b334d8099b1e', 'setTitle')
        group.setStyleSheet(Styles.GROUP_BOX_STYLE)

        layout = QGridLayout(group)
        layout.setSpacing(Layout.ITEM_SPACING)
        layout.setContentsMargins(15, 20, 15, 15)

        # Folder name  (CP-9b)
        self.name_edit = TextInput(
            label="Folder Name",
            placeholder="Enter a unique name for this folder configuration",
            accessible_name="Folder name",
        )
        self.name_edit.set_validator(
            lambda t: (
                (True, "") if t.strip() else (False, "Folder name cannot be empty")
            )
        )
        self.name_edit.textChanged.connect(self._emit_data_changed)
        layout.addWidget(self.name_edit, 0, 0, 1, 2)

        # Description
        layout.addWidget(_ui_widget(QLabel, 'Legacy.s0cf2814604b4c9ad', 'setText'), 1, 0, Qt.AlignTop)
        self.description_edit = QTextEdit()
        _ui_bind(self.description_edit, 'setPlaceholderText', 'Legacy.s25bb43f0cbb98d0f')
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setStyleSheet(Styles.INPUT_FIELD_STYLE)
        _ui_bind(self.description_edit, 'setAccessibleName', 'Legacy.secb23c94b16ceb31')
        self.description_edit.textChanged.connect(self._emit_data_changed)
        layout.addWidget(self.description_edit, 1, 1)

        # Set column stretch
        layout.setColumnStretch(1, 1)

        return group

    def _create_directories_section(self):
        """Create the directories management section."""
        group = _ui_widget(QGroupBox, 'Legacy.s64c9a4190cb96231', 'setTitle')
        group.setStyleSheet(Styles.GROUP_BOX_STYLE)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(Layout.ITEM_SPACING)

        # Description label
        desc_label = _ui_widget(QLabel, 'Legacy.sf7acc1742e562a2d', 'setText')
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; margin-bottom: 10px;"
        )
        layout.addWidget(desc_label)

        # Directory list and controls
        list_layout = QHBoxLayout()

        # Directory list
        self.directories_list = QListWidget()
        self.directories_list.setStyleSheet(Styles.LIST_WIDGET_STYLE)
        self.directories_list.setMinimumHeight(150)
        self.directories_list.setSelectionMode(QListWidget.ExtendedSelection)
        _ui_bind(self.directories_list, 'setAccessibleName', 'Legacy.s03259fefb2f8f211')
        list_layout.addWidget(self.directories_list)

        # Control buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(Layout.BUTTON_SPACING)

        self.add_directory_btn = PrimaryButton(f"{Icons.ADD} Add Directory")
        self.add_directory_btn.clicked.connect(self._add_directory)
        buttons_layout.addWidget(self.add_directory_btn)

        self.browse_directory_btn = _ui_widget(SecondaryButton, 'Legacy.s164ea737a236749b', 'setText')
        self.browse_directory_btn.clicked.connect(self._browse_directory)
        buttons_layout.addWidget(self.browse_directory_btn)

        self.remove_directory_btn = SecondaryButton(f"{Icons.REMOVE} Remove")
        self.remove_directory_btn.clicked.connect(self._remove_directory)
        self.remove_directory_btn.setEnabled(False)
        buttons_layout.addWidget(self.remove_directory_btn)

        buttons_layout.addStretch()

        list_layout.addLayout(buttons_layout)
        layout.addLayout(list_layout)

        # Connect selection change
        self.directories_list.itemSelectionChanged.connect(
            self._on_directory_selection_changed
        )

        return group

    def _create_options_section(self):
        """Create the folder options section."""
        group = _ui_widget(QGroupBox, 'Legacy.s3bd6f324c537f6ab', 'setTitle')
        group.setStyleSheet(Styles.GROUP_BOX_STYLE)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(Layout.ITEM_SPACING)

        # Create checkboxes
        self.include_subdirs_cb = _ui_widget(QCheckBox, 'Legacy.s7fe3b250ab4b4940', 'setText')
        self.include_subdirs_cb.setChecked(True)
        self.include_subdirs_cb.setStyleSheet(Styles.CHECKBOX_STYLE)
        _ui_bind(self.include_subdirs_cb, 'setAccessibleName', 'Legacy.s7fe3b250ab4b4940')
        self.include_subdirs_cb.setMinimumHeight(44)  # A11Y-8c
        self.include_subdirs_cb.stateChanged.connect(self._emit_data_changed)
        layout.addWidget(self.include_subdirs_cb)

        self.follow_symlinks_cb = _ui_widget(QCheckBox, 'Legacy.s0d9c8c49befb0764', 'setText')
        self.follow_symlinks_cb.setStyleSheet(Styles.CHECKBOX_STYLE)
        _ui_bind(self.follow_symlinks_cb, 'setAccessibleName', 'Legacy.s0d9c8c49befb0764')
        self.follow_symlinks_cb.setMinimumHeight(44)  # A11Y-8c
        self.follow_symlinks_cb.stateChanged.connect(self._emit_data_changed)
        layout.addWidget(self.follow_symlinks_cb)

        self.include_hidden_cb = _ui_widget(QCheckBox, 'Legacy.sb7df2de4db3d21a7', 'setText')
        self.include_hidden_cb.setStyleSheet(Styles.CHECKBOX_STYLE)
        _ui_bind(self.include_hidden_cb, 'setAccessibleName', 'Legacy.sb7df2de4db3d21a7')
        self.include_hidden_cb.setMinimumHeight(44)  # A11Y-8c
        self.include_hidden_cb.stateChanged.connect(self._emit_data_changed)
        layout.addWidget(self.include_hidden_cb)

        self.monitor_changes_cb = _ui_widget(QCheckBox, 'Legacy.s11942846032ebbdf', 'setText')
        self.monitor_changes_cb.setChecked(True)
        self.monitor_changes_cb.setStyleSheet(Styles.CHECKBOX_STYLE)
        _ui_bind(self.monitor_changes_cb, 'setAccessibleName', 'Legacy.s11942846032ebbdf')
        self.monitor_changes_cb.setMinimumHeight(44)  # A11Y-8c
        self.monitor_changes_cb.stateChanged.connect(self._emit_data_changed)
        layout.addWidget(self.monitor_changes_cb)

        return group

    def _add_directory(self):
        """Add a new directory manually."""
        from PyQt5.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(
            self,
            "Add Directory",
            "Enter directory path:",
            QLineEdit.Normal,
            "",
        )

        if ok and text.strip():
            path = Path(text.strip())
            if path.exists() and path.is_dir():
                self._add_directory_to_list(str(path))
            else:
                Modal(
                    "Invalid Directory",
                    f"The directory '{text}' does not exist or is not a directory.",
                    ["OK"],
                    self,
                ).exec_()

    def _browse_directory(self):
        """Browse for a directory using file dialog."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec_() == QFileDialog.Accepted:
            selected_dirs = dialog.selectedFiles()
            for directory in selected_dirs:
                self._add_directory_to_list(directory)

    def _add_directory_to_list(self, directory_path):
        """Add a directory to the list widget."""
        # Check for duplicates
        for i in range(self.directories_list.count()):
            if self.directories_list.item(i).text() == directory_path:
                return

        # Add to list
        item = QListWidgetItem(directory_path)
        item.setToolTip(directory_path)
        self.directories_list.addItem(item)
        self._emit_data_changed()

        logger.debug(f"Added directory: {directory_path}")

    def _remove_directory(self):
        """Remove selected directories from the list."""
        selected_items = self.directories_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = self.directories_list.row(item)
            self.directories_list.takeItem(row)

        self._emit_data_changed()
        self._on_directory_selection_changed()

    def _on_directory_selection_changed(self):
        """Handle directory selection changes."""
        has_selection = bool(self.directories_list.selectedItems())
        self.remove_directory_btn.setEnabled(has_selection and not self.is_read_only)

    def load_configuration(self, configuration):
        """Load configuration data into the general tab."""
        super().load_configuration(configuration)

        if not configuration:
            return

        try:
            # Load basic information
            if hasattr(configuration, "name"):
                self.name_edit.setText(configuration.name or "")

            if hasattr(configuration, "description"):
                self.description_edit.setPlainText(configuration.description or "")

            # Load directories
            if hasattr(configuration, "directories"):
                self.directories_list.clear()
                for directory in configuration.directories or []:
                    self._add_directory_to_list(directory)

            # Load options
            if hasattr(configuration, "include_subdirectories"):
                self.include_subdirs_cb.setChecked(configuration.include_subdirectories)

            if hasattr(configuration, "follow_symlinks"):
                self.follow_symlinks_cb.setChecked(configuration.follow_symlinks)

            if hasattr(configuration, "include_hidden"):
                self.include_hidden_cb.setChecked(configuration.include_hidden)

            if hasattr(configuration, "monitor_changes"):
                self.monitor_changes_cb.setChecked(configuration.monitor_changes)

            logger.debug("General configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading general configuration: {str(e)}")

    def get_data(self):
        """Get configuration data from the general tab."""
        directories = []
        for i in range(self.directories_list.count()):
            directories.append(self.directories_list.item(i).text())

        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "directories": directories,
            "include_subdirectories": self.include_subdirs_cb.isChecked(),
            "follow_symlinks": self.follow_symlinks_cb.isChecked(),
            "include_hidden": self.include_hidden_cb.isChecked(),
            "monitor_changes": self.monitor_changes_cb.isChecked(),
        }

    def validate(self):
        """Validate general configuration data."""
        errors = []

        # Validate name
        name = self.name_edit.text().strip()
        if not name:
            errors.append("Folder name is required")
        elif len(name) > Validation.MAX_FOLDER_NAME_LENGTH:
            errors.append(
                f"Folder name cannot exceed {Validation.MAX_FOLDER_NAME_LENGTH} characters"
            )

        # Validate description length
        description = self.description_edit.toPlainText().strip()
        if len(description) > Validation.MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"Description cannot exceed {Validation.MAX_DESCRIPTION_LENGTH} characters"
            )

        # Validate directories
        if self.directories_list.count() == 0:
            errors.append("At least one directory must be specified")

        # Validate directory paths
        for i in range(self.directories_list.count()):
            directory = self.directories_list.item(i).text()
            path = Path(directory)
            if not path.exists():
                errors.append(f"Directory does not exist: {directory}")
            elif not path.is_dir():
                errors.append(f"Path is not a directory: {directory}")

        return errors

    def set_read_only(self, read_only=True):
        """Set the general tab to read-only mode."""
        super().set_read_only(read_only)

        self.name_edit.setReadOnly(read_only)
        self.description_edit.setReadOnly(read_only)
        self.add_directory_btn.setEnabled(not read_only)
        self.browse_directory_btn.setEnabled(not read_only)
        self.remove_directory_btn.setEnabled(
            not read_only and bool(self.directories_list.selectedItems())
        )
        self.include_subdirs_cb.setEnabled(not read_only)
        self.follow_symlinks_cb.setEnabled(not read_only)
        self.include_hidden_cb.setEnabled(not read_only)
        self.monitor_changes_cb.setEnabled(not read_only)


class SearchConfigTab(BaseConfigTab):
    """
    Search configuration tab for advanced search parameters.

    Provides interface for:
    - Search scope and parameters
    - Content search options
    - Indexing configuration
    - Performance settings
    """

    def __init__(self, configuration=None, mode="create", parent=None):
        """Initialize search configuration tab."""
        super().__init__(configuration, mode, parent)

    def _setup_ui(self):
        """Setup the search configuration interface."""
        super()._setup_ui()
        layout = self.layout()

        # Placeholder for search configuration
        placeholder_label = _ui_widget(QLabel, 'Legacy.s3539abd116c0f831', 'setText')
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setFont(Fonts.heading_font())
        placeholder_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; padding: 50px;"
        )

        layout.addWidget(placeholder_label)
        layout.addStretch()


class FiltersConfigTab(BaseConfigTab):
    """
    File type filters configuration tab.

    Provides interface for:
    - File type categories
    - Custom extensions
    - Exclusion patterns
    - MIME type filters
    """

    def __init__(self, configuration=None, mode="create", parent=None):
        """Initialize filters configuration tab."""
        super().__init__(configuration, mode, parent)

    def _setup_ui(self):
        """Setup the filters configuration interface."""
        super()._setup_ui()
        layout = self.layout()

        # Placeholder for filters configuration
        placeholder_label = _ui_widget(QLabel, 'Legacy.s73f69ee14fbc89db', 'setText')
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setFont(Fonts.heading_font())
        placeholder_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; padding: 50px;"
        )

        layout.addWidget(placeholder_label)
        layout.addStretch()


class DisplayConfigTab(BaseConfigTab):
    """
    Display options configuration tab.

    Provides interface for:
    - View mode settings
    - Column configuration
    - Sorting options
    - Presentation preferences
    """

    def __init__(self, configuration=None, mode="create", parent=None):
        """Initialize display configuration tab."""
        super().__init__(configuration, mode, parent)

    def _setup_ui(self):
        """Setup the display configuration interface."""
        super()._setup_ui()
        layout = self.layout()

        # Placeholder for display configuration
        placeholder_label = _ui_widget(QLabel, 'Legacy.s46aaaf0b7949e5b5', 'setText')
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setFont(Fonts.heading_font())
        placeholder_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; padding: 50px;"
        )

        layout.addWidget(placeholder_label)
        layout.addStretch()


# Testing support
if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication, QTabWidget

    app = QApplication(sys.argv)

    # Create test tab widget
    tab_widget = QTabWidget()
    _ui_bind(tab_widget, 'setAccessibleName', 'Legacy.s43bf3a65b21a189d')

    # Add tabs
    general_tab = GeneralConfigTab()
    search_tab = SearchConfigTab()
    filters_tab = FiltersConfigTab()
    display_tab = DisplayConfigTab()

    tab_widget.addTab(general_tab, "General")
    tab_widget.addTab(search_tab, "Search")
    tab_widget.addTab(filters_tab, "Filters")
    tab_widget.addTab(display_tab, "Display")

    tab_widget.resize(800, 600)
    tab_widget.show()

    sys.exit(app.exec_())
