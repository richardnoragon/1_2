import sys
from typing import Optional, Any
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from config_manager import ConfigManager
from log_manager import LogManager
from gui.common.base_dialog import BaseDialog
from gui.common.dialogs import get_existing_directory
import os


class SettingsDialog(BaseDialog):
    """A class that handles settings dialog and inherits from BaseDialog."""
    def __init__(self, parent: Optional[Any] = None) -> None:
        """Initialize the settings dialog.
        Args:
            parent: Parent widget for the dialog
        """
        super().__init__()
        ui_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "settings_dialog.ui"
        )
        uic.loadUi(ui_file, self)
        
        self.config = ConfigManager()
        self.log_manager = LogManager()
        
        # Add logging level combo box items
        self.loggingLevelCombo.addItems(['INFO', 'DEBUG', 'WARNING', 'ERROR'])
        
        self.load_settings()
        
        # Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        apply_btn = self.buttonBox.button(self.buttonBox.Apply)
        reset_btn = self.buttonBox.button(self.buttonBox.Reset)
        apply_btn.clicked.connect(self.apply_settings)
        reset_btn.clicked.connect(self.reset_settings)
        self.browseDirButton.clicked.connect(self.browse_directory)
        
    def load_settings(self) -> None:
        """Load current settings into UI."""
        # General
        theme = self.config.get_setting("general", "theme").capitalize()
        self.themeCombo.setCurrentText(theme)
        default_dir = self.config.get_setting("general", "default_directory")
        self.defaultDirEdit.setText(default_dir)
        
        # Load logging settings
        logging_level = self.config.get_setting(
            "general", "logging_level", "INFO"
        )
        debug_logging = self.config.get_setting(
            "general", "enable_debug_logging", False
        )
        
        self.loggingLevelCombo.setCurrentText(logging_level)
        self.enableDebugCheck.setChecked(debug_logging)
        
        # Duplicates
        hash_algo = self.config.get_setting(
            "duplicates", "default_hash_algorithm"
        ).upper()
        if hash_algo == "SHA256":
            hash_algo = "SHA-256"  # Fix display name
        self.hashCombo.setCurrentText(hash_algo)
        min_size = self.config.get_setting("duplicates", "min_file_size")
        self.minSizeSpin.setValue(min_size)
        skip_system = self.config.get_setting(
            "duplicates", "skip_system_files"
        )
        self.skipSystemCheck.setChecked(skip_system)
        
        # Secure Delete
        passes = self.config.get_setting("secure_delete", "default_passes")
        self.passesSpin.setValue(passes)
        
        # Compression
        format_name = self.config.get_setting(
            "compression", "default_format"
        ).upper()
        self.formatCombo.setCurrentText(format_name)
        level = self.config.get_setting(
            "compression", "default_compression_level"
        )
        self.levelSlider.setValue(level)
        
        # Sync
        mode_map = {
            "two_way": "Two-Way",
            "mirror": "Mirror",
            "update": "Update"
        }
        mode = self.config.get_setting("sync", "default_mode")
        self.syncModeCombo.setCurrentText(mode_map.get(mode, "Two-Way"))
        backups = self.config.get_setting("sync", "create_backups")
        self.backupsCheck.setChecked(backups)
        skip_newer = self.config.get_setting("sync", "skip_newer_files")
        self.skipNewerCheck.setChecked(skip_newer)
        
        # Catalog
        recursive = self.config.get_setting("catalog", "recursive_by_default")
        self.recursiveCheck.setChecked(recursive)
        duplicates = self.config.get_setting("catalog", "check_duplicates")
        self.duplicatesCheck.setChecked(duplicates)
        show_sizes = self.config.get_setting("catalog", "show_file_sizes")
        self.showSizesCheck.setChecked(show_sizes)
        show_dates = self.config.get_setting("catalog", "show_dates")
        self.showDatesCheck.setChecked(show_dates)
        sort_by = self.config.get_setting(
            "catalog", "default_sort_by"
        ).capitalize()
        self.sortByCombo.setCurrentText(sort_by)
        
        # Organize
        org_recursive = self.config.get_setting(
            "organize", "recursive_by_default"
        )
        self.orgRecursiveCheck.setChecked(org_recursive)
        create_folders = self.config.get_setting(
            "organize", "create_category_folders"
        )
        self.createFoldersCheck.setChecked(create_folders)
        move_files = self.config.get_setting("organize", "move_files")
        self.moveFilesCheck.setChecked(move_files)
    
    def apply_settings(self) -> None:
        """Save current UI state to config."""
        # General
        theme = self.themeCombo.currentText().lower()
        self.config.set_setting("general", "theme", theme)
        default_dir = self.defaultDirEdit.text()
        self.config.set_setting("general", "default_directory", default_dir)
        
        # Logging settings
        logging_level = self.loggingLevelCombo.currentText()
        debug_enabled = self.enableDebugCheck.isChecked()
        
        self.config.set_setting("general", "logging_level", logging_level)
        self.config.set_setting(
            "general", "enable_debug_logging", debug_enabled
        )
        
        # Duplicates
        hash_algo = self.hashCombo.currentText().replace("-", "").lower()
        self.config.set_setting(
            "duplicates", "default_hash_algorithm", hash_algo
        )
        min_size = self.minSizeSpin.value()
        self.config.set_setting("duplicates", "min_file_size", min_size)
        skip_system = self.skipSystemCheck.isChecked()
        self.config.set_setting(
            "duplicates", "skip_system_files", skip_system
        )
        
        # Secure Delete
        passes = self.passesSpin.value()
        self.config.set_setting("secure_delete", "default_passes", passes)
        
        # Compression
        format_name = self.formatCombo.currentText().lower()
        self.config.set_setting("compression", "default_format", format_name)
        level = self.levelSlider.value()
        self.config.set_setting(
            "compression", "default_compression_level", level
        )
        
        # Sync
        mode_map = {
            "Two-Way": "two_way",
            "Mirror": "mirror",
            "Update": "update"
        }
        sync_mode = mode_map[self.syncModeCombo.currentText()]
        self.config.set_setting("sync", "default_mode", sync_mode)
        backups = self.backupsCheck.isChecked()
        self.config.set_setting("sync", "create_backups", backups)
        skip_newer = self.skipNewerCheck.isChecked()
        self.config.set_setting("sync", "skip_newer_files", skip_newer)
        
        # Catalog
        recursive = self.recursiveCheck.isChecked()
        self.config.set_setting("catalog", "recursive_by_default", recursive)
        duplicates = self.duplicatesCheck.isChecked()
        self.config.set_setting("catalog", "check_duplicates", duplicates)
        show_sizes = self.showSizesCheck.isChecked()
        self.config.set_setting("catalog", "show_file_sizes", show_sizes)
        show_dates = self.showDatesCheck.isChecked()
        self.config.set_setting("catalog", "show_dates", show_dates)
        sort_by = self.sortByCombo.currentText().lower()
        self.config.set_setting("catalog", "default_sort_by", sort_by)
        
        # Organize
        org_recursive = self.orgRecursiveCheck.isChecked()
        self.config.set_setting(
            "organize", "recursive_by_default", org_recursive
        )
        create_folders = self.createFoldersCheck.isChecked()
        self.config.set_setting(
            "organize", "create_category_folders", create_folders
        )
        move_files = self.moveFilesCheck.isChecked()
        self.config.set_setting(
            "organize", "move_files", move_files
        )
    
    def reset_settings(self) -> None:
        """Reset all settings to defaults."""
        self.config.reset_to_defaults()
        self.load_settings()
    
    def browse_directory(self) -> None:
        """Open directory browser dialog."""
        directory = get_existing_directory(self, "Select Default Directory")
        if directory:
            self.defaultDirEdit.setText(directory)
    
    def accept(self) -> None:
        """Called when OK button is clicked."""
        self.apply_settings()
        super().accept()


def main() -> None:
    """Main function to run the settings dialog."""
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
