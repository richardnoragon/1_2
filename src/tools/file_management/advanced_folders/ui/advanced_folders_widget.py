"""
Advanced Folders Widget for RFU Integration.

This module provides the main GUI widget for Advanced Folders functionality
that integrates seamlessly with the existing RFU hub architecture.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src directory to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from PyQt5.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtGui import QCursor, QFont, QIcon, QPixmap
    from PyQt5.QtWidgets import (
        QAbstractItemView,
        QAction,
        QCheckBox,
        QComboBox,
        QDateEdit,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QListWidget,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSpinBox,
        QSplitter,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import (
        DestructiveButton,
        PrimaryButton,
        SecondaryButton,
    )
    from src.gui.components.inputs import TextInput
    from src.gui.components.modal import ConfirmationModal, Modal
    from src.gui.themes import ThemeManager, Typography, token

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Create mock classes for environments without PyQt5

    class QDialog:
        pass

    class QWidget:
        pass

    def pyqtSignal(*args, **kwargs):
        """Mock pyqtSignal for non-PyQt5 environments."""
        return None

    Qt = None
    QThread = None
    QTimer = None
    QDate = None
    QCursor = None
    QFont = None
    QIcon = None
    QPixmap = None
    PrimaryButton = QPushButton if PYQT5_AVAILABLE else None
    SecondaryButton = QPushButton if PYQT5_AVAILABLE else None
    DestructiveButton = QPushButton if PYQT5_AVAILABLE else None
    ConfirmationModal = None
    Modal = None

# Import RFU core components
try:
    from gui.standard_window import StandardWindow
    from src.config.config_manager import get_config_manager
except ImportError:
    # Fallback imports for development
    try:
        from src.config.config_manager import get_config_manager
        from src.gui.standard_window import StandardWindow
    except ImportError:
        get_config_manager = None
        StandardWindow = QWidget if PYQT5_AVAILABLE else object

# Import Advanced Folders core
try:
    from ..core.folder_configuration import (
        FolderConfiguration,
        FolderConfigurationManager,
        SearchParameters,
    )
    from ..core.search_engine import FileResult, SearchEngine, SearchProgress
except ImportError:
    # Fallback for absolute imports
    from tools.file_management.advanced_folders.core.folder_configuration import (
        FolderConfiguration,
        FolderConfigurationManager,
        SearchParameters,
    )
    from tools.file_management.advanced_folders.core.search_engine import (
        FileResult,
        SearchEngine,
        SearchProgress,
    )


class FolderConfigurationDialog(QDialog):
    """Dialog for creating and editing folder configurations."""

    def __init__(self, parent=None, config: Optional[FolderConfiguration] = None):
        """Initialize configuration dialog.

        Args:
            parent: Parent widget
            config: Optional existing configuration to edit
        """
        super().__init__(parent)
        self.config = config
        self.is_editing = config is not None

        self.setWindowTitle(
            "Edit Folder Configuration"
            if self.is_editing
            else "New Folder Configuration"
        )
        self.setMinimumSize(600, 500)

        self.setup_ui()

        if self.config:
            self.load_configuration()

    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Create tab widget for different configuration sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Folder configuration tabs")
        layout.addWidget(self.tab_widget)

        # General tab
        self.create_general_tab()

        # Directories tab
        self.create_directories_tab()

        # Search tab
        self.create_search_tab()

        # Advanced tab
        self.create_advanced_tab()

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_general_tab(self):
        """Create general configuration tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Folder name  (CP-9b)
        self.name_edit = TextInput(
            label="Name",
            placeholder="Enter folder name",
            accessible_name="Folder name",
        )
        self.name_edit.set_validator(
            lambda t: (True, "") if t.strip() else (False, "Name cannot be empty")
        )
        layout.addRow(self.name_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Optional description")
        self.description_edit.setAccessibleName("Folder description")
        layout.addRow("Description:", self.description_edit)

        # Color scheme
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItems(
            ["Default", "Blue", "Green", "Orange", "Purple", "Red"]
        )
        self.color_scheme_combo.setAccessibleName("Folder color scheme")
        layout.addRow("Color Scheme:", self.color_scheme_combo)

        # Auto-refresh settings
        refresh_group = QGroupBox("Auto-Refresh Settings")
        refresh_layout = QVBoxLayout(refresh_group)

        self.auto_refresh_cb = QCheckBox("Enable automatic refresh")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.setAccessibleName("Enable automatic refresh")
        refresh_layout.addWidget(self.auto_refresh_cb)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Refresh interval:"))
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setMinimum(30)
        self.refresh_interval_spin.setMaximum(3600)
        self.refresh_interval_spin.setValue(300)
        self.refresh_interval_spin.setSuffix(" seconds")
        self.refresh_interval_spin.setAccessibleName("Refresh interval in seconds")
        interval_layout.addWidget(self.refresh_interval_spin)
        interval_layout.addStretch()
        refresh_layout.addLayout(interval_layout)

        layout.addRow(refresh_group)

        self.tab_widget.addTab(tab, "General")

    def create_directories_tab(self):
        """Create directories configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Directory list
        dir_group = QGroupBox("Directory Paths")
        dir_layout = QVBoxLayout(dir_group)

        self.directories_list = QListWidget()
        self.directories_list.setAccessibleName("Configured directory paths")
        dir_layout.addWidget(self.directories_list)

        # Directory buttons
        dir_buttons = QHBoxLayout()

        self.add_dir_btn = SecondaryButton("Add Directory")
        self.add_dir_btn.clicked.connect(self.add_directory)
        dir_buttons.addWidget(self.add_dir_btn)

        self.remove_dir_btn = SecondaryButton("Remove Selected")
        self.remove_dir_btn.clicked.connect(self.remove_directory)
        dir_buttons.addWidget(self.remove_dir_btn)

        dir_buttons.addStretch()
        dir_layout.addLayout(dir_buttons)

        layout.addWidget(dir_group)

        # Directory options
        options_group = QGroupBox("Directory Options")
        options_layout = QVBoxLayout(options_group)

        self.include_subdirs_cb = QCheckBox("Include subdirectories")
        self.include_subdirs_cb.setChecked(True)
        self.include_subdirs_cb.setAccessibleName("Include subdirectories")
        options_layout.addWidget(self.include_subdirs_cb)

        self.follow_links_cb = QCheckBox("Follow symbolic links")
        self.follow_links_cb.setChecked(True)
        self.follow_links_cb.setAccessibleName("Follow symbolic links")
        options_layout.addWidget(self.follow_links_cb)

        self.include_hidden_cb = QCheckBox("Include hidden files")
        self.include_hidden_cb.setAccessibleName("Include hidden files")
        options_layout.addWidget(self.include_hidden_cb)

        self.monitor_changes_cb = QCheckBox("Monitor for changes")
        self.monitor_changes_cb.setChecked(True)
        self.monitor_changes_cb.setAccessibleName("Monitor for changes")
        options_layout.addWidget(self.monitor_changes_cb)

        layout.addWidget(options_group)

        self.tab_widget.addTab(tab, "Directories")

    def create_search_tab(self):
        """Create search configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File name pattern
        pattern_group = QGroupBox("File Name Pattern")
        pattern_layout = QFormLayout(pattern_group)

        self.filename_pattern_edit = TextInput(
            label="Pattern",
            placeholder="Enter pattern (e.g., *.txt)",
            accessible_name="Filename pattern",
        )
        pattern_layout.addRow(self.filename_pattern_edit)

        pattern_options = QHBoxLayout()
        self.use_regex_cb = QCheckBox("Use regular expressions")
        self.use_regex_cb.setAccessibleName("Use regular expressions")
        pattern_options.addWidget(self.use_regex_cb)

        self.case_sensitive_cb = QCheckBox("Case sensitive")
        self.case_sensitive_cb.setAccessibleName("Case sensitive search")
        pattern_options.addWidget(self.case_sensitive_cb)
        pattern_options.addStretch()

        pattern_layout.addRow(pattern_options)
        layout.addWidget(pattern_group)

        # Content search
        content_group = QGroupBox("Content Search")
        content_layout = QFormLayout(content_group)

        self.content_search_edit = TextInput(
            label="Search term",
            placeholder="Search within file content",
            accessible_name="Content search term",
        )
        content_layout.addRow(self.content_search_edit)

        self.index_content_cb = QCheckBox("Index file contents for faster searching")
        self.index_content_cb.setChecked(True)
        self.index_content_cb.setAccessibleName(
            "Index file contents for faster searching"
        )
        content_layout.addRow(self.index_content_cb)

        layout.addWidget(content_group)

        # Date range
        date_group = QGroupBox("Date Range")
        date_layout = QFormLayout(date_group)

        self.date_from_edit = QDateEdit()
        self.date_from_edit.setDate(QDate.currentDate().addYears(-1))
        self.date_from_edit.setCalendarPopup(True)
        date_layout.addRow("From:", self.date_from_edit)

        self.date_to_edit = QDateEdit()
        self.date_to_edit.setDate(QDate.currentDate())
        self.date_to_edit.setCalendarPopup(True)
        date_layout.addRow("To:", self.date_to_edit)

        self.date_criteria_combo = QComboBox()
        self.date_criteria_combo.addItems(
            ["Modified Date", "Created Date", "Accessed Date"]
        )
        self.date_criteria_combo.setAccessibleName("Date criteria type")
        date_layout.addRow("Date Type:", self.date_criteria_combo)

        layout.addWidget(date_group)

        # File size
        size_group = QGroupBox("File Size")
        size_layout = QFormLayout(size_group)

        size_min_layout = QHBoxLayout()
        self.size_min_spin = QSpinBox()
        self.size_min_spin.setMaximum(999999)
        self.size_min_spin.setSuffix(" KB")
        self.size_min_spin.setAccessibleName("Minimum file size in kilobytes")
        size_min_layout.addWidget(self.size_min_spin)
        size_min_layout.addStretch()
        size_layout.addRow("Minimum size:", size_min_layout)

        size_max_layout = QHBoxLayout()
        self.size_max_spin = QSpinBox()
        self.size_max_spin.setMaximum(999999)
        self.size_max_spin.setValue(100)
        self.size_max_spin.setSuffix(" MB")
        self.size_max_spin.setAccessibleName("Maximum file size in megabytes")
        size_max_layout.addWidget(self.size_max_spin)
        size_max_layout.addStretch()
        size_layout.addRow("Maximum size:", size_max_layout)

        layout.addWidget(size_group)

        self.tab_widget.addTab(tab, "Search Parameters")

    def create_advanced_tab(self):
        """Create advanced configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Performance options
        perf_group = QGroupBox("Performance Options")
        perf_layout = QFormLayout(perf_group)

        self.cache_results_cb = QCheckBox("Cache search results")
        self.cache_results_cb.setChecked(True)
        self.cache_results_cb.setAccessibleName("Cache search results")
        perf_layout.addRow(self.cache_results_cb)

        self.search_archives_cb = QCheckBox("Search compressed archives")
        self.search_archives_cb.setAccessibleName("Search compressed archives")
        perf_layout.addRow(self.search_archives_cb)

        self.include_network_cb = QCheckBox("Include network locations")
        self.include_network_cb.setChecked(True)
        self.include_network_cb.setAccessibleName("Include network locations")
        perf_layout.addRow(self.include_network_cb)

        depth_layout = QHBoxLayout()
        self.search_depth_spin = QSpinBox()
        self.search_depth_spin.setMinimum(-1)
        self.search_depth_spin.setMaximum(50)
        self.search_depth_spin.setValue(-1)
        self.search_depth_spin.setSpecialValueText("Unlimited")
        self.search_depth_spin.setAccessibleName("Search depth limit")
        depth_layout.addWidget(self.search_depth_spin)
        depth_layout.addStretch()
        perf_layout.addRow("Search depth:", depth_layout)

        max_results_layout = QHBoxLayout()
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setMinimum(100)
        self.max_results_spin.setMaximum(100000)
        self.max_results_spin.setValue(10000)
        self.max_results_spin.setAccessibleName("Maximum search results")
        max_results_layout.addWidget(self.max_results_spin)
        max_results_layout.addStretch()
        perf_layout.addRow("Maximum results:", max_results_layout)

        layout.addWidget(perf_group)

        # File type filters
        filter_group = QGroupBox("File Type Filters")
        filter_layout = QVBoxLayout(filter_group)

        # Include extensions  (CP-9b)
        self.include_ext_edit = TextInput(
            label="Include extensions",
            placeholder="e.g., .txt,.pdf,.docx",
            accessible_name="Include file extensions",
            accessible_description="Comma-separated list of extensions to include, e.g. .txt,.pdf",
        )
        self.include_ext_edit.set_validator(
            lambda t: (
                (True, "")
                if not t.strip()
                else (
                    (True, "")
                    if all(
                        p.strip().startswith(".") and len(p.strip()) > 1
                        for p in t.split(",")
                        if p.strip()
                    )
                    else (
                        False,
                        "Each extension must start with a dot (e.g. .txt,.pdf)",
                    )
                )
            )
        )
        filter_layout.addWidget(self.include_ext_edit)

        # Exclude extensions  (CP-9b)
        self.exclude_ext_edit = TextInput(
            label="Exclude extensions",
            placeholder="e.g., .tmp,.log,.bak",
            accessible_name="Exclude file extensions",
            accessible_description="Comma-separated list of extensions to exclude, e.g. .tmp,.log",
        )
        self.exclude_ext_edit.set_validator(
            lambda t: (
                (True, "")
                if not t.strip()
                else (
                    (True, "")
                    if all(
                        p.strip().startswith(".") and len(p.strip()) > 1
                        for p in t.split(",")
                        if p.strip()
                    )
                    else (
                        False,
                        "Each extension must start with a dot (e.g. .tmp,.log)",
                    )
                )
            )
        )
        filter_layout.addWidget(self.exclude_ext_edit)

        layout.addWidget(filter_group)

        layout.addStretch()

        self.tab_widget.addTab(tab, "Advanced")

    def add_directory(self):
        """Add directory to the list."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directories_list.addItem(directory)

    def remove_directory(self):
        """Remove selected directory from the list."""
        current_row = self.directories_list.currentRow()
        if current_row >= 0:
            self.directories_list.takeItem(current_row)

    def load_configuration(self):
        """Load existing configuration into the dialog."""
        if not self.config:
            return

        # General tab
        self.name_edit.setText(self.config.name)
        self.description_edit.setPlainText(self.config.description)
        self.color_scheme_combo.setCurrentText(self.config.color_scheme.title())

        self.auto_refresh_cb.setChecked(self.config.auto_refresh)
        self.refresh_interval_spin.setValue(self.config.refresh_interval)

        # Directories tab
        for directory in self.config.directory_paths:
            self.directories_list.addItem(directory)

        params = self.config.search_parameters

        self.include_subdirs_cb.setChecked(params.include_subdirectories)
        self.follow_links_cb.setChecked(params.follow_symbolic_links)
        self.include_hidden_cb.setChecked(params.include_hidden_files)
        self.monitor_changes_cb.setChecked(params.monitor_changes)

        # Search tab
        self.filename_pattern_edit.setText(params.filename_pattern)
        self.use_regex_cb.setChecked(params.use_regex)
        self.case_sensitive_cb.setChecked(params.case_sensitive)

        self.content_search_edit.setText(params.content_search)
        self.index_content_cb.setChecked(params.index_content)

        if params.date_from:
            self.date_from_edit.setDate(
                QDate.fromString(params.date_from.date().isoformat(), Qt.ISODate)
            )
        if params.date_to:
            self.date_to_edit.setDate(
                QDate.fromString(params.date_to.date().isoformat(), Qt.ISODate)
            )

        # Advanced tab
        self.cache_results_cb.setChecked(params.cache_results)
        self.search_archives_cb.setChecked(params.search_archives)
        self.include_network_cb.setChecked(params.include_network_locations)
        self.search_depth_spin.setValue(params.search_depth)
        self.max_results_spin.setValue(params.max_results)

        # File type filters
        if params.include_extensions:
            self.include_ext_edit.setText(",".join(params.include_extensions))
        if params.exclude_extensions:
            self.exclude_ext_edit.setText(",".join(params.exclude_extensions))

    def get_configuration(self) -> FolderConfiguration:
        """Get configuration from dialog fields.

        Returns:
            FolderConfiguration: The configuration
        """
        # Create or update configuration
        if self.config:
            config = self.config
        else:
            config = FolderConfiguration()

        # General settings
        config.name = self.name_edit.text().strip()
        config.description = self.description_edit.toPlainText().strip()
        config.color_scheme = self.color_scheme_combo.currentText().lower()
        config.auto_refresh = self.auto_refresh_cb.isChecked()
        config.refresh_interval = self.refresh_interval_spin.value()

        # Directory paths
        config.directory_paths = []
        for i in range(self.directories_list.count()):
            config.directory_paths.append(self.directories_list.item(i).text())

        # Search parameters
        params = SearchParameters()

        params.filename_pattern = self.filename_pattern_edit.text().strip()
        params.use_regex = self.use_regex_cb.isChecked()
        params.case_sensitive = self.case_sensitive_cb.isChecked()

        params.content_search = self.content_search_edit.text().strip()
        params.index_content = self.index_content_cb.isChecked()

        params.date_from = self.date_from_edit.date().toPyDate()
        params.date_to = self.date_to_edit.date().toPyDate()
        params.date_criteria = (
            self.date_criteria_combo.currentText().lower().replace(" date", "")
        )

        params.size_min = (
            self.size_min_spin.value() * 1024
            if self.size_min_spin.value() > 0
            else None
        )
        params.size_max = (
            self.size_max_spin.value() * 1024 * 1024
            if self.size_max_spin.value() > 0
            else None
        )

        params.include_subdirectories = self.include_subdirs_cb.isChecked()
        params.follow_symbolic_links = self.follow_links_cb.isChecked()
        params.include_hidden_files = self.include_hidden_cb.isChecked()
        params.monitor_changes = self.monitor_changes_cb.isChecked()

        params.cache_results = self.cache_results_cb.isChecked()
        params.search_archives = self.search_archives_cb.isChecked()
        params.include_network_locations = self.include_network_cb.isChecked()
        params.search_depth = self.search_depth_spin.value()
        params.max_results = self.max_results_spin.value()

        # File type filters
        include_text = self.include_ext_edit.text().strip()
        if include_text:
            params.include_extensions = set(
                ext.strip() for ext in include_text.split(",") if ext.strip()
            )

        exclude_text = self.exclude_ext_edit.text().strip()
        if exclude_text:
            params.exclude_extensions = set(
                ext.strip() for ext in exclude_text.split(",") if ext.strip()
            )

        config.search_parameters = params
        config.modified_date = datetime.now()

        return config


class AdvancedFoldersWidget(StandardWindow if StandardWindow != QWidget else QWidget):
    """Main Advanced Folders widget for RFU integration."""

    # Signals
    folder_selected = pyqtSignal(str)  # folder_id
    search_completed = pyqtSignal(list)  # List[FileResult]

    def __init__(self, config_manager=None):
        """Initialize the Advanced Folders widget.

        Args:
            config_manager: Optional ConfigManager instance
        """
        super().__init__()

        # Handle config manager with fallback
        if config_manager:
            self.config_manager = config_manager
        elif get_config_manager is not None:
            self.config_manager = get_config_manager()
        else:
            self.config_manager = None

        self.folder_manager = FolderConfigurationManager(self.config_manager)
        self.search_engine = SearchEngine(enable_caching=True)

        self.current_folder: Optional[FolderConfiguration] = None
        self.search_results: List[FileResult] = []

        self.setWindowTitle("Advanced Folders")
        self.setMinimumSize(1000, 700)

        self.setup_ui()
        self.setup_connections()
        self.load_folders()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_current_folder)

        # Register theme-change callback for live re-theming
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def setup_ui(self):
        """Setup the main UI."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Toolbar
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)

        # Main content splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Left panel - folder list
        self.create_folder_panel()
        self.main_splitter.addWidget(self.folder_panel)

        # Right panel - search results
        self.create_results_panel()
        self.main_splitter.addWidget(self.results_panel)

        # Set splitter proportions
        self.main_splitter.setSizes([300, 700])

        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.status_bar.showMessage("Ready")

    def create_toolbar(self):
        """Create toolbar with actions."""
        self.toolbar = QFrame()
        toolbar_layout = QHBoxLayout(self.toolbar)

        # New folder button
        self.new_folder_btn = SecondaryButton("📁 New Folder")
        self.new_folder_btn.clicked.connect(self.create_new_folder)
        toolbar_layout.addWidget(self.new_folder_btn)

        # Edit folder button
        self.edit_folder_btn = SecondaryButton("✏️ Edit")
        self.edit_folder_btn.clicked.connect(self.edit_current_folder)
        self.edit_folder_btn.setEnabled(False)
        toolbar_layout.addWidget(self.edit_folder_btn)

        # Delete folder button
        self.delete_folder_btn = DestructiveButton("🗑️ Delete")
        self.delete_folder_btn.set_confirmation_callback(
            lambda: ConfirmationModal(
                "Confirm Folder Deletion",
                "Delete this folder configuration? This cannot be undone.",
                "Delete",
                "Cancel",
                self,
            ).exec_()
            == QDialog.Accepted
        )
        self.delete_folder_btn.action_confirmed.connect(self.delete_current_folder)
        self.delete_folder_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_folder_btn)

        toolbar_layout.addWidget(QFrame())  # Separator

        # Refresh button
        self.refresh_btn = SecondaryButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_current_folder)
        self.refresh_btn.setEnabled(False)
        toolbar_layout.addWidget(self.refresh_btn)

        # Search button
        self.search_btn = PrimaryButton("🔍 Search")
        self.search_btn.clicked.connect(self.execute_search)
        self.search_btn.setEnabled(False)
        toolbar_layout.addWidget(self.search_btn)

        toolbar_layout.addStretch()

        # Quick search
        self.quick_search_edit = QLineEdit()
        self.quick_search_edit.setPlaceholderText("Quick search...")
        self.quick_search_edit.setMaximumWidth(200)
        self.quick_search_edit.returnPressed.connect(self.quick_search)
        self.quick_search_edit.setAccessibleName("Quick search")
        toolbar_layout.addWidget(self.quick_search_edit)

        # Settings button
        self.settings_btn = SecondaryButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        toolbar_layout.addWidget(self.settings_btn)

    def create_folder_panel(self):
        """Create left panel with folder list."""
        self.folder_panel = QFrame()
        layout = QVBoxLayout(self.folder_panel)

        # Panel title
        title_label = QLabel("Advanced Folders")
        title_label.setFont(Typography.h3())
        layout.addWidget(title_label)

        # Folder list
        self.folder_list = QTreeWidget()
        self.folder_list.setHeaderLabels(["Name", "Directories", "Files"])
        self.folder_list.setAccessibleName("Advanced folders list")
        self.folder_list.itemClicked.connect(self.on_folder_selected)
        layout.addWidget(self.folder_list)

        # Folder statistics
        self.stats_label = QLabel("No folder selected")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet(
            f"background-color: {token('surface')}; padding: 10px; border-radius: 5px;"
        )
        layout.addWidget(self.stats_label)

    def create_results_panel(self):
        """Create right panel with search results."""
        self.results_panel = QFrame()
        layout = QVBoxLayout(self.results_panel)

        # Results header
        header_layout = QHBoxLayout()
        self.results_label = QLabel("Search Results")
        self.results_label.setFont(Typography.h3())
        header_layout.addWidget(self.results_label)

        header_layout.addStretch()

        # Export button
        self.export_btn = SecondaryButton("📤 Export")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        header_layout.addWidget(self.export_btn)

        layout.addLayout(header_layout)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.setAccessibleName("Search results")

        # Set columns
        columns = ["Name", "Path", "Size", "Type", "Modified"]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)

        # Configure column widths
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Path
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Modified

        layout.addWidget(self.results_table)

        # Results summary
        self.results_summary = QLabel("No results")
        layout.addWidget(self.results_summary)

    def setup_connections(self):
        """Setup signal connections."""
        # Search engine progress callback
        self.search_engine.set_progress_callback(self.on_search_progress)

        # Folder manager events (if available)
        # self.folder_manager.folder_created.connect(self.on_folder_created)

    def load_folders(self):
        """Load folders into the list."""
        self.folder_list.clear()

        folders = self.folder_manager.list_folders()

        for folder in folders:
            item = QTreeWidgetItem(
                [
                    folder.name,
                    str(len(folder.directory_paths)),
                    str(folder.statistics.total_files),
                ]
            )
            item.setData(0, Qt.UserRole, folder.folder_id)
            self.folder_list.addTopLevelItem(item)

        self.folder_list.resizeColumnToContents(0)
        self.folder_list.resizeColumnToContents(1)
        self.folder_list.resizeColumnToContents(2)

    def on_folder_selected(self, item, column):
        """Handle folder selection.

        Args:
            item: Selected tree item
            column: Selected column
        """
        folder_id = item.data(0, Qt.UserRole)
        self.current_folder = self.folder_manager.get_folder(folder_id)

        if self.current_folder:
            self.folder_selected.emit(folder_id)
            self.update_folder_stats()
            self.enable_folder_actions(True)

            # Start auto-refresh if enabled
            if self.current_folder.auto_refresh:
                self.refresh_timer.start(self.current_folder.refresh_interval * 1000)
            else:
                self.refresh_timer.stop()

    def update_folder_stats(self):
        """Update folder statistics display."""
        if not self.current_folder:
            self.stats_label.setText("No folder selected")
            return

        stats = self.current_folder.statistics

        stats_text = f"""
        <b>{self.current_folder.name}</b><br>
        <i>{self.current_folder.description}</i><br><br>
        
        <b>Directories:</b> {len(self.current_folder.directory_paths)}<br>
        <b>Total Files:</b> {stats.total_files:,}<br>
        <b>Total Size:</b> {self.format_size(stats.total_size)}<br>
        <b>Last Scan:</b> {stats.last_scan_time.strftime('%Y-%m-%d %H:%M') if stats.last_scan_time else 'Never'}<br>
        """

        self.stats_label.setText(stats_text)

    def enable_folder_actions(self, enabled: bool):
        """Enable/disable folder action buttons.

        Args:
            enabled: Whether to enable the buttons
        """
        self.edit_folder_btn.setEnabled(enabled)
        self.delete_folder_btn.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)

    def create_new_folder(self):
        """Create a new folder configuration."""
        dialog = FolderConfigurationDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_configuration()

            # Validate configuration
            errors = config.validate()
            if errors:
                Modal(
                    "Validation Error",
                    "Configuration has errors:\n\n" + "\n".join(errors),
                    ["OK"],
                    self,
                ).exec_()
                return

            # Save configuration
            try:
                self.folder_manager._configurations[config.folder_id] = config
                self.folder_manager.save_configurations()

                self.load_folders()
                self.status_bar.showMessage(f"Created folder: {config.name}")

            except Exception as e:
                Modal(
                    "Error",
                    f"Failed to create folder:\n{str(e)}",
                    ["OK"],
                    self,
                ).exec_()

    def edit_current_folder(self):
        """Edit the current folder configuration."""
        if not self.current_folder:
            return

        dialog = FolderConfigurationDialog(self, self.current_folder)

        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_configuration()

            # Validate configuration
            errors = config.validate()
            if errors:
                Modal(
                    "Validation Error",
                    "Configuration has errors:\n\n" + "\n".join(errors),
                    ["OK"],
                    self,
                ).exec_()
                return

            # Save configuration
            try:
                self.folder_manager._configurations[config.folder_id] = config
                self.folder_manager.save_configurations()

                self.current_folder = config
                self.load_folders()
                self.update_folder_stats()
                self.status_bar.showMessage(f"Updated folder: {config.name}")

            except Exception as e:
                Modal(
                    "Error",
                    f"Failed to update folder:\n{str(e)}",
                    ["OK"],
                    self,
                ).exec_()

    def delete_current_folder(self):
        """Delete the current folder configuration."""
        if not self.current_folder:
            return

        try:
            self.folder_manager.delete_folder(self.current_folder.folder_id)

            self.current_folder = None
            self.enable_folder_actions(False)
            self.clear_results()
            self.load_folders()
            self.stats_label.setText("No folder selected")
            self.status_bar.showMessage("Folder deleted")

        except Exception as e:
            Modal(
                "Error",
                f"Failed to delete folder:\n{str(e)}",
                ["OK"],
                self,
            ).exec_()

    def refresh_current_folder(self):
        """Refresh the current folder."""
        if self.current_folder:
            self.execute_search()

    def auto_refresh_current_folder(self):
        """Auto-refresh current folder if enabled."""
        if self.current_folder and self.current_folder.auto_refresh:
            self.execute_search()

    def execute_search(self):
        """Execute search for current folder."""
        if not self.current_folder:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.search_btn.setEnabled(False)
        self.status_bar.showMessage("Searching...")

        # Execute search asynchronously
        self.search_engine.async_search(
            self.current_folder,
            self.on_search_completed,
            self.on_search_progress,
        )

    def on_search_progress(self, progress: SearchProgress):
        """Handle search progress updates.

        Args:
            progress: Search progress information
        """
        if progress.total_files > 0:
            percentage = int((progress.files_processed / progress.total_files) * 100)
            self.progress_bar.setValue(percentage)

        self.status_bar.showMessage(
            f"Searching... {progress.files_processed} files processed, "
            f"{progress.matches_found} matches found"
        )

    def on_search_completed(self, results: List[FileResult]):
        """Handle search completion.

        Args:
            results: Search results
        """
        self.search_results = results
        self.search_completed.emit(results)

        # Update UI
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)
        self.export_btn.setEnabled(len(results) > 0)

        # Update results table
        self.populate_results_table(results)

        # Update statistics
        if self.current_folder:
            self.current_folder.statistics.total_files = len(results)
            self.current_folder.statistics.last_scan_time = datetime.now()
            self.folder_manager.save_configurations()
            self.update_folder_stats()

        self.status_bar.showMessage(f"Search completed: {len(results)} files found")

    def populate_results_table(self, results: List[FileResult]):
        """Populate results table with search results.

        Args:
            results: List of FileResult objects
        """
        self.results_table.setRowCount(len(results))

        for row, result in enumerate(results):
            # Name
            name_item = QTableWidgetItem(result.file_name)
            name_item.setData(Qt.UserRole, result)
            self.results_table.setItem(row, 0, name_item)

            # Path
            path_item = QTableWidgetItem(str(result.file_path.parent))
            self.results_table.setItem(row, 1, path_item)

            # Size
            size_item = QTableWidgetItem(self.format_size(result.file_size))
            size_item.setData(Qt.UserRole, result.file_size)
            self.results_table.setItem(row, 2, size_item)

            # Type
            type_item = QTableWidgetItem(result.file_type)
            self.results_table.setItem(row, 3, type_item)

            # Modified
            modified_item = QTableWidgetItem(
                result.modified_date.strftime("%Y-%m-%d %H:%M")
            )
            modified_item.setData(Qt.UserRole, result.modified_date)
            self.results_table.setItem(row, 4, modified_item)

        # Update summary
        total_size = sum(result.file_size for result in results)
        self.results_summary.setText(
            f"{len(results):,} files found, Total size: {self.format_size(total_size)}"
        )

    def clear_results(self):
        """Clear search results."""
        self.results_table.setRowCount(0)
        self.search_results = []
        self.export_btn.setEnabled(False)
        self.results_summary.setText("No results")

    def quick_search(self):
        """Perform quick search."""
        search_term = self.quick_search_edit.text().strip()

        if not search_term or not self.current_folder:
            return

        # Update search parameters for quick search
        original_pattern = self.current_folder.search_parameters.filename_pattern
        self.current_folder.search_parameters.filename_pattern = f"*{search_term}*"

        # Execute search
        self.execute_search()

        # Restore original pattern
        self.current_folder.search_parameters.filename_pattern = original_pattern

    def export_results(self):
        """Export search results."""
        if not self.search_results:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            f"advanced_folders_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)",
        )

        if filename:
            try:
                if filename.endswith(".json"):
                    self.export_to_json(filename)
                else:
                    self.export_to_csv(filename)

                self.status_bar.showMessage(f"Results exported to {filename}")

            except Exception as e:
                Modal(
                    "Export Error",
                    f"Failed to export results:\n{str(e)}",
                    ["OK"],
                    self,
                ).exec_()

    def export_to_csv(self, filename: str):
        """Export results to CSV file.

        Args:
            filename: Output filename
        """
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "Name",
                    "Path",
                    "Size",
                    "Type",
                    "Created",
                    "Modified",
                    "Accessed",
                ]
            )

            # Write data
            for result in self.search_results:
                writer.writerow(
                    [
                        result.file_name,
                        str(result.file_path),
                        result.file_size,
                        result.file_type,
                        result.created_date.isoformat(),
                        result.modified_date.isoformat(),
                        result.accessed_date.isoformat(),
                    ]
                )

    def export_to_json(self, filename: str):
        """Export results to JSON file.

        Args:
            filename: Output filename
        """
        import json

        data = {
            "export_timestamp": datetime.now().isoformat(),
            "folder_name": (self.current_folder.name if self.current_folder else ""),
            "total_results": len(self.search_results),
            "results": [result.to_dict() for result in self.search_results],
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def show_settings(self):
        """Show Advanced Folders settings."""
        # TODO: Implement settings dialog
        Modal(
            "Settings",
            "Advanced Folders settings dialog will be implemented in the next phase.",
            ["OK"],
            self,
        ).exec_()

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size for display.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math

        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        return f"{s} {size_names[i]}"

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-driven stylesheets when theme variant changes."""
        if hasattr(self, "stats_label"):
            self.stats_label.setStyleSheet(
                f"background-color: {token('surface')}; padding: 10px; border-radius: 5px;"
            )
        for _btn in (
            "search_btn",
            "new_folder_btn",
            "edit_folder_btn",
            "refresh_btn",
            "settings_btn",
            "export_btn",
            "add_dir_btn",
            "remove_dir_btn",
        ):
            btn = getattr(self, _btn, None)
            if btn is not None:
                btn._apply_style()
        if hasattr(self, "delete_folder_btn"):
            self.delete_folder_btn._apply_destructive_style()


# Integration class for RFU Hub
class AdvancedFoldersGUI(AdvancedFoldersWidget):
    """Integration wrapper for RFU Hub compatibility."""

    def __init__(self, config_manager=None):
        """Initialize for RFU Hub integration.

        Args:
            config_manager: ConfigManager instance from RFU
        """
        super().__init__(config_manager)

        # Update window title for integration
        self.setWindowTitle("Advanced Folders - RFU")

        # Track tool usage if database is available
        self.track_tool_usage()

    def track_tool_usage(self):
        """Track tool usage for RFU analytics."""
        try:
            # Try to import database manager
            from standalone_database_manager import DatabaseManager

            db_manager = DatabaseManager()
            if db_manager.is_available():
                db_manager.track_tool_usage(
                    tool_name="Advanced Folders",
                    action="opened",
                    details={"timestamp": datetime.now().isoformat()},
                )
        except ImportError:
            pass  # Database tracking not available
