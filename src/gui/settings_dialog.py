import logging

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Import with fallback handling
try:
    from src.config.config_manager import ConfigManager
except ImportError:
    try:
        from core.config_manager import ConfigManager
    except ImportError:
        # Fallback minimal config manager
        class ConfigManager:
            def __init__(self):
                self.settings = {}

            def get_setting(self, key, default=None):
                return self.settings.get(key, default)

            def set_setting(self, key, value):
                self.settings[key] = value

            def reset_to_defaults(self):
                self.settings = {}


try:
    from src.core.preferences.manager import PreferenceManager
    from src.core.preferences.migration import PreferenceMigrationHelper
except ImportError:
    try:
        from core.preferences.manager import PreferenceManager
        from core.preferences.migration import PreferenceMigrationHelper
    except ImportError:
        PreferenceManager = None
        PreferenceMigrationHelper = None  # type: ignore


try:
    from core.error_handler import get_error_handler
    from gui.common.base_window import BaseWindow
    from gui.common.dialogs import (
        get_existing_directory,
        show_error_dialog,
        show_info_dialog,
    )

    # Get error handler instance
    error_handler = get_error_handler()
except ImportError:
    # Fallback implementations
    BaseWindow = object

    def show_error_dialog(message, title="Error", parent=None):
        QMessageBox.critical(parent, title, message)

    def show_info_dialog(message, title="Information", parent=None):
        QMessageBox.information(parent, title, message)

    def get_existing_directory(title, directory="", parent=None):
        return QFileDialog.getExistingDirectory(parent, title, directory)

    error_handler = None


class SettingsDialog(QDialog):
    """A class that handles settings dialog and inherits from QDialog."""

    def __init__(self, parent=None):
        """init.
        Args:
            parent (Any): Description of parent"""
        super().__init__(parent)
        self.logger = logging.getLogger("RFU.SettingsDialog")
        self.config = ConfigManager()
        self.preference_manager = self._init_preference_manager()
        self._migration_helper = (
            PreferenceMigrationHelper(
                preference_manager=self.preference_manager,
                config_manager=self.config,
                logger=self.logger,
            )
            if PreferenceMigrationHelper is not None
            else None
        )
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        # Main layout
        layout = QVBoxLayout(self)

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("Settings categories")
        tab_widget.addTab(self.create_general_tab(), "General")
        tab_widget.addTab(self.create_duplicates_tab(), "Duplicates")
        tab_widget.addTab(self.create_secure_delete_tab(), "Secure Delete")
        tab_widget.addTab(self.create_compression_tab(), "Compression")
        tab_widget.addTab(self.create_sync_tab(), "Sync")
        tab_widget.addTab(self.create_catalog_tab(), "Catalog")
        tab_widget.addTab(self.create_organize_tab(), "Organize")
        tab_widget.addTab(self._create_appearance_tab(), "Appearance")

        self.tab_widget = tab_widget  # expose for subclass addTab() (T035)
        layout.addWidget(tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        reset_button = QPushButton("Reset All")
        reset_button.setAccessibleName("Reset all settings to defaults")
        reset_button.setMinimumHeight(44)
        reset_button.clicked.connect(self.reset_all_settings)
        save_button = QPushButton("Save")
        save_button.setAccessibleName("Save settings")
        save_button.setMinimumHeight(44)
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.setAccessibleName("Cancel and close settings")
        cancel_button.setMinimumHeight(44)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def create_general_tab(self):
        """Create the General settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("Theme selection")
        self.theme_combo.setMinimumHeight(44)
        self.theme_combo.addItems(["light", "dark"])
        layout.addRow("Theme:", self.theme_combo)

        # Default directory
        dir_layout = QHBoxLayout()
        self.default_dir_edit = QLineEdit()
        self.default_dir_edit.setAccessibleName("Default directory path")
        browse_button = QPushButton("Browse...")
        browse_button.setAccessibleName("Browse for default directory")
        browse_button.setMinimumHeight(44)
        browse_button.clicked.connect(self.browse_default_dir)
        dir_layout.addWidget(self.default_dir_edit)
        dir_layout.addWidget(browse_button)
        layout.addRow("Default Directory:", dir_layout)

        # Recent entries limit
        self.recent_spin = QSpinBox()
        self.recent_spin.setAccessibleName("Maximum recent entries")
        self.recent_spin.setMinimumHeight(44)
        self.recent_spin.setRange(1, 50)
        layout.addRow("Max Recent Entries:", self.recent_spin)

        # Logging settings
        self.log_level_combo = QComboBox()
        self.log_level_combo.setAccessibleName("Logging level")
        self.log_level_combo.setMinimumHeight(44)
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        layout.addRow("Logging Level:", self.log_level_combo)

        self.debug_check = QCheckBox("Enable Debug Logging")
        self.debug_check.setAccessibleName("Enable debug logging")
        self.debug_check.setMinimumHeight(44)

        return tab

    def create_duplicates_tab(self):
        """Create the Duplicates settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Hash algorithm
        self.hash_algo_combo = QComboBox()
        self.hash_algo_combo.setAccessibleName("Default hash algorithm")
        self.hash_algo_combo.setMinimumHeight(44)
        self.hash_algo_combo.addItems(["md5", "sha1", "sha256", "sha512"])
        layout.addRow("Default Hash:", self.hash_algo_combo)

        # Min file size
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setAccessibleName("Minimum file size in KB")
        self.min_size_spin.setMinimumHeight(44)
        self.min_size_spin.setRange(0, 1000000)
        self.min_size_spin.setSuffix(" KB")
        layout.addRow("Minimum File Size:", self.min_size_spin)

        # Skip system files
        self.skip_system_check = QCheckBox()
        self.skip_system_check.setAccessibleName("Skip system files")
        self.skip_system_check.setMinimumHeight(44)

        return tab

    def create_secure_delete_tab(self):
        """Create the Secure Delete settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Default passes
        self.default_passes_spin = QSpinBox()
        self.default_passes_spin.setAccessibleName("Default secure delete passes")
        self.default_passes_spin.setMinimumHeight(44)
        self.default_passes_spin.setRange(1, 35)
        layout.addRow("Default Passes:", self.default_passes_spin)

        # Maximum passes
        self.max_passes_spin = QSpinBox()
        self.max_passes_spin.setAccessibleName("Maximum secure delete passes")
        self.max_passes_spin.setMinimumHeight(44)
        self.max_passes_spin.setRange(1, 35)
        layout.addRow("Maximum Passes:", self.max_passes_spin)

        return tab

    def create_compression_tab(self):
        """Create the Compression settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Default format
        self.format_combo = QComboBox()
        self.format_combo.setAccessibleName("Default compression format")
        self.format_combo.setMinimumHeight(44)
        self.format_combo.addItems(["zip", "7z", "tar.gz", "tar.bz2"])
        layout.addRow("Default Format:", self.format_combo)

        # Compression level
        self.compression_spin = QSpinBox()
        self.compression_spin.setAccessibleName("Default compression level")
        self.compression_spin.setMinimumHeight(44)
        self.compression_spin.setRange(0, 9)
        layout.addRow("Default Level:", self.compression_spin)

        # Password protection
        self.password_check = QCheckBox()
        self.password_check.setAccessibleName("Use password protection for compression")
        self.password_check.setMinimumHeight(44)
        layout.addRow("Use Password Protection:", self.password_check)

        return tab

    def create_sync_tab(self):
        """Create the Sync settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Sync mode
        self.sync_mode_combo = QComboBox()
        self.sync_mode_combo.setAccessibleName("Default sync mode")
        self.sync_mode_combo.setMinimumHeight(44)
        self.sync_mode_combo.addItems(["two_way", "mirror", "update"])
        layout.addRow("Default Mode:", self.sync_mode_combo)

        # Create backups
        self.backup_check = QCheckBox()
        self.backup_check.setAccessibleName("Create backups during sync")
        self.backup_check.setMinimumHeight(44)
        layout.addRow("Create Backups:", self.backup_check)

        # Skip newer
        self.skip_newer_check = QCheckBox()
        self.skip_newer_check.setAccessibleName("Skip newer files during sync")
        self.skip_newer_check.setMinimumHeight(44)
        layout.addRow("Skip Newer Files:", self.skip_newer_check)

        return tab

    def create_catalog_tab(self):
        """Create the Catalog settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Recursive by default
        self.catalog_recursive_check = QCheckBox()
        self.catalog_recursive_check.setAccessibleName("Catalog recursively by default")
        self.catalog_recursive_check.setMinimumHeight(44)
        layout.addRow("Recursive by Default:", self.catalog_recursive_check)

        # Check duplicates
        self.catalog_duplicates_check = QCheckBox()
        self.catalog_duplicates_check.setAccessibleName(
            "Check for duplicates during catalog"
        )
        self.catalog_duplicates_check.setMinimumHeight(44)
        layout.addRow("Check Duplicates:", self.catalog_duplicates_check)

        # Show file sizes
        self.show_sizes_check = QCheckBox()
        self.show_sizes_check.setAccessibleName("Show file sizes in catalog")
        self.show_sizes_check.setMinimumHeight(44)
        layout.addRow("Show File Sizes:", self.show_sizes_check)

        # Show dates
        self.show_dates_check = QCheckBox()
        self.show_dates_check.setAccessibleName("Show dates in catalog")
        self.show_dates_check.setMinimumHeight(44)
        layout.addRow("Show Dates:", self.show_dates_check)

        # Sort settings
        self.sort_by_combo = QComboBox()
        self.sort_by_combo.setAccessibleName("Default sort field")
        self.sort_by_combo.setMinimumHeight(44)
        self.sort_by_combo.addItems(["name", "size", "date"])
        layout.addRow("Default Sort By:", self.sort_by_combo)

        self.sort_order_combo = QComboBox()
        self.sort_order_combo.setAccessibleName("Default sort order")
        self.sort_order_combo.setMinimumHeight(44)
        self.sort_order_combo.addItems(["ascending", "descending"])
        layout.addRow("Default Sort Order:", self.sort_order_combo)

        return tab

    def create_organize_tab(self):
        """Create the Organize settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Recursive by default
        self.organize_recursive_check = QCheckBox()
        self.organize_recursive_check.setAccessibleName(
            "Organize files recursively by default"
        )
        self.organize_recursive_check.setMinimumHeight(44)
        layout.addRow("Recursive by Default:", self.organize_recursive_check)

        # Create category folders
        self.category_folders_check = QCheckBox()
        self.category_folders_check.setAccessibleName(
            "Create category folders when organizing"
        )
        self.category_folders_check.setMinimumHeight(44)
        layout.addRow("Create Category Folders:", self.category_folders_check)

        # Move files
        self.move_files_check = QCheckBox()
        self.move_files_check.setAccessibleName("Move files when organizing")
        self.move_files_check.setMinimumHeight(44)
        layout.addRow("Move Files:", self.move_files_check)

        return tab

    def browse_default_dir(self):
        """Open directory browser for default directory selection."""
        directory = get_existing_directory(
            "Select Default Directory",
            directory=self.default_dir_edit.text(),
            parent=self,
        )
        if directory:
            self.default_dir_edit.setText(str(directory))

    def load_settings(self):
        """Load current settings into the UI."""
        try:
            # General settings
            self.theme_combo.setCurrentText(self._load_theme_preference())
            self.default_dir_edit.setText(self._load_default_directory())
            self.recent_spin.setValue(
                self.config.get_setting("general", "max_recent_entries", 10)
            )
            self.log_level_combo.setCurrentText(
                self.config.get_setting("general", "logging_level", "INFO")
            )
            self.debug_check.setChecked(
                self.config.get_setting(
                    "general",
                    "enable_debug_logging",
                    False,
                )
            )

            # Duplicates settings
            self.hash_algo_combo.setCurrentText(
                self.config.get_setting(
                    "duplicates", "default_hash_algorithm", "sha256"
                )
            )
            self.min_size_spin.setValue(
                self.config.get_setting("duplicates", "min_file_size", 1024)
            )
            self.skip_system_check.setChecked(
                self.config.get_setting(
                    "duplicates",
                    "skip_system_files",
                    True,
                )
            )

            # Secure Delete settings
            self.default_passes_spin.setValue(
                self.config.get_setting("secure_delete", "default_passes", 3)
            )
            self.max_passes_spin.setValue(
                self.config.get_setting("secure_delete", "max_passes", 35)
            )

            # Compression settings
            self.format_combo.setCurrentText(
                self.config.get_setting("compression", "default_format", "zip")
            )
            self.compression_spin.setValue(
                self.config.get_setting(
                    "compression",
                    "default_compression_level",
                    6,
                )
            )
            self.password_check.setChecked(
                self.config.get_setting(
                    "compression",
                    "use_password_protection",
                    False,
                )
            )

            # Sync settings
            self.sync_mode_combo.setCurrentText(
                self.config.get_setting("sync", "default_mode", "two_way")
            )
            self.backup_check.setChecked(
                self.config.get_setting("sync", "create_backups", True)
            )
            self.skip_newer_check.setChecked(
                self.config.get_setting("sync", "skip_newer_files", False)
            )

            # Catalog settings
            self.catalog_recursive_check.setChecked(
                self.config.get_setting(
                    "catalog",
                    "recursive_by_default",
                    True,
                )
            )
            self.catalog_duplicates_check.setChecked(
                self.config.get_setting("catalog", "check_duplicates", False)
            )
            self.show_sizes_check.setChecked(
                self.config.get_setting("catalog", "show_file_sizes", True)
            )
            self.show_dates_check.setChecked(
                self.config.get_setting("catalog", "show_dates", True)
            )
            self.sort_by_combo.setCurrentText(
                self.config.get_setting("catalog", "default_sort_by", "name")
            )
            self.sort_order_combo.setCurrentText(
                self.config.get_setting(
                    "catalog",
                    "default_sort_order",
                    "ascending",
                )
            )

            # Organize settings
            self.organize_recursive_check.setChecked(
                self.config.get_setting(
                    "organize",
                    "recursive_by_default",
                    False,
                )
            )
            self.category_folders_check.setChecked(
                self.config.get_setting(
                    "organize",
                    "create_category_folders",
                    True,
                )
            )
            self.move_files_check.setChecked(
                self.config.get_setting("organize", "move_files", True)
            )
        except Exception as e:
            show_error_dialog(
                f"Failed to load settings: {str(e)}",
                title="Error",
                parent=self,
            )

    def save_settings(self):
        """Save settings from the UI to configuration."""
        try:
            # General settings
            self._save_theme_preference(self.theme_combo.currentText())
            self._save_default_directory(self.default_dir_edit.text())
            self.config.set_setting(
                "general", "max_recent_entries", self.recent_spin.value()
            )
            self.config.set_setting(
                "general", "logging_level", self.log_level_combo.currentText()
            )
            self.config.set_setting(
                "general", "enable_debug_logging", self.debug_check.isChecked()
            )

            # Duplicates settings
            self.config.set_setting(
                "duplicates",
                "default_hash_algorithm",
                self.hash_algo_combo.currentText(),
            )
            self.config.set_setting(
                "duplicates", "min_file_size", self.min_size_spin.value()
            )
            self.config.set_setting(
                "duplicates",
                "skip_system_files",
                self.skip_system_check.isChecked(),
            )

            # Secure Delete settings
            self.config.set_setting(
                "secure_delete",
                "default_passes",
                self.default_passes_spin.value(),
            )
            self.config.set_setting(
                "secure_delete", "max_passes", self.max_passes_spin.value()
            )

            # Compression settings
            self.config.set_setting(
                "compression",
                "default_format",
                self.format_combo.currentText(),
            )
            self.config.set_setting(
                "compression",
                "default_compression_level",
                self.compression_spin.value(),
            )
            self.config.set_setting(
                "compression",
                "use_password_protection",
                self.password_check.isChecked(),
            )

            # Sync settings
            self.config.set_setting(
                "sync", "default_mode", self.sync_mode_combo.currentText()
            )
            self.config.set_setting(
                "sync", "create_backups", self.backup_check.isChecked()
            )
            self.config.set_setting(
                "sync", "skip_newer_files", self.skip_newer_check.isChecked()
            )

            # Catalog settings
            self.config.set_setting(
                "catalog",
                "recursive_by_default",
                self.catalog_recursive_check.isChecked(),
            )
            self.config.set_setting(
                "catalog",
                "check_duplicates",
                self.catalog_duplicates_check.isChecked(),
            )
            self.config.set_setting(
                "catalog", "show_file_sizes", self.show_sizes_check.isChecked()
            )
            self.config.set_setting(
                "catalog", "show_dates", self.show_dates_check.isChecked()
            )
            self.config.set_setting(
                "catalog", "default_sort_by", self.sort_by_combo.currentText()
            )
            self.config.set_setting(
                "catalog",
                "default_sort_order",
                self.sort_order_combo.currentText(),
            )

            # Organize settings
            self.config.set_setting(
                "organize",
                "recursive_by_default",
                self.organize_recursive_check.isChecked(),
            )
            self.config.set_setting(
                "organize",
                "create_category_folders",
                self.category_folders_check.isChecked(),
            )
            self.config.set_setting(
                "organize", "move_files", self.move_files_check.isChecked()
            )

            self.accept()
            show_info_dialog(
                "Settings saved successfully", title="Success", parent=self
            )

        except Exception as e:
            show_error_dialog(
                f"Failed to save settings: {str(e)}",
                title="Error",
                parent=self,
            )

    def _init_preference_manager(self):
        if PreferenceManager is None:
            return None
        try:
            return PreferenceManager()
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                "PreferenceManager unavailable for settings dialog: %s", exc
            )
            return None

    def _load_theme_preference(self) -> str:
        fallback = self.config.get_setting("general", "theme", "light")
        if self._migration_helper is None:
            return str(fallback or "light")
        return self._migration_helper.load_theme(str(fallback or "light"))

    def _save_theme_preference(self, theme_name: str) -> None:
        helper = self._migration_helper
        if helper is None:
            self.logger.warning(
                "PreferenceManager migration helper unavailable; theme '%s'"
                " not persisted",
                theme_name,
            )
            return
        helper.save_theme(theme_name)

    def _load_default_directory(self) -> str:
        fallback = self.config.get_setting("general", "default_directory", "")
        if self._migration_helper is None:
            return str(fallback or "")
        return self._migration_helper.load_default_directory(str(fallback or ""))

    def _save_default_directory(self, directory: str) -> None:
        helper = self._migration_helper
        if helper is None:
            self.logger.warning(
                "PreferenceManager migration helper unavailable; default"
                " directory '%s' not persisted",
                directory,
            )
            return
        helper.save_default_directory(directory)

    def reset_all_settings(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self.config.reset_to_defaults()
                self.load_settings()
                show_info_dialog(
                    "All settings reset to defaults",
                    title="Success",
                    parent=self,
                )
            except Exception as e:
                show_error_dialog(
                    f"Failed to reset settings: {str(e)}",
                    title="Error",
                    parent=self,
                )

    # T034 — Appearance tab
    def _create_appearance_tab(self) -> QWidget:
        """Create the UAP Appearance settings tab (T034)."""
        try:
            from src.gui.widgets.uap_appearance_widget import (
                UAPAppearanceWidget,
            )

            container = QWidget()
            layout = QVBoxLayout(container)
            self._uap_widget = UAPAppearanceWidget()
            layout.addWidget(self._uap_widget)
            return container
        except Exception as exc:
            self.logger.warning("Could not load UAPAppearanceWidget: %s", exc)
            fallback = QWidget()
            layout = QVBoxLayout(fallback)
            from PyQt5.QtWidgets import QLabel

            layout.addWidget(QLabel("Appearance settings unavailable."))
            return fallback

    # T035 — Public addTab() for tool subclasses
    def addTab(self, widget: QWidget, label: str) -> None:
        """Allow subclasses to add their own tabs to the settings dialog."""
        self.tab_widget.addTab(widget, label)
