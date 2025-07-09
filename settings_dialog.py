import sys
from PyQt5.QtWidgets import QFileDialog, QComboBox, QCheckBox, QApplication
from PyQt5 import uic
from config_manager import ConfigManager
from log_manager import LogManager
from gui.common.base_dialog import BaseDialog
from gui.common.dialogs import get_existing_directory
import os

class SettingsDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__()
        ui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_dialog.ui")
        uic.loadUi(ui_file, self)
        
        self.config = ConfigManager()
        self.log_manager = LogManager()
        
        # Add logging level combo box items
        self.loggingLevelCombo.addItems(['INFO', 'DEBUG', 'WARNING', 'ERROR'])
        
        self.load_settings()
        
        # Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(self.buttonBox.Apply).clicked.connect(self.apply_settings)
        self.buttonBox.button(self.buttonBox.Reset).clicked.connect(self.reset_settings)
        self.browseDirButton.clicked.connect(self.browse_directory)
        
    def load_settings(self):
        """Load current settings into UI."""
        # General
        self.themeCombo.setCurrentText(self.config.get_setting("general", "theme").capitalize())
        self.defaultDirEdit.setText(self.config.get_setting("general", "default_directory"))
        
        # Load logging settings
        logging_level = self.config.get_setting("general", "logging_level", "INFO")
        debug_logging = self.config.get_setting("general", "enable_debug_logging", False)
        
        self.loggingLevelCombo.setCurrentText(logging_level)
        self.enableDebugCheck.setChecked(debug_logging)
        
        # Duplicates
        hash_algo = self.config.get_setting("duplicates", "default_hash_algorithm").upper()
        if (hash_algo == "SHA256"): hash_algo = "SHA-256"  # Fix display name
        self.hashCombo.setCurrentText(hash_algo)
        self.minSizeSpin.setValue(self.config.get_setting("duplicates", "min_file_size"))
        self.skipSystemCheck.setChecked(self.config.get_setting("duplicates", "skip_system_files"))
        
        # Secure Delete
        self.passesSpin.setValue(self.config.get_setting("secure_delete", "default_passes"))
        
        # Compression
        self.formatCombo.setCurrentText(self.config.get_setting("compression", "default_format").upper())
        self.levelSlider.setValue(self.config.get_setting("compression", "default_compression_level"))
        
        # Sync
        mode_map = {"two_way": "Two-Way", "mirror": "Mirror", "update": "Update"}
        mode = self.config.get_setting("sync", "default_mode")
        self.syncModeCombo.setCurrentText(mode_map.get(mode, "Two-Way"))
        self.backupsCheck.setChecked(self.config.get_setting("sync", "create_backups"))
        self.skipNewerCheck.setChecked(self.config.get_setting("sync", "skip_newer_files"))
        
        # Catalog
        self.recursiveCheck.setChecked(self.config.get_setting("catalog", "recursive_by_default"))
        self.duplicatesCheck.setChecked(self.config.get_setting("catalog", "check_duplicates"))
        self.showSizesCheck.setChecked(self.config.get_setting("catalog", "show_file_sizes"))
        self.showDatesCheck.setChecked(self.config.get_setting("catalog", "show_dates"))
        self.sortByCombo.setCurrentText(self.config.get_setting("catalog", "default_sort_by").capitalize())
        
        # Organize
        self.orgRecursiveCheck.setChecked(self.config.get_setting("organize", "recursive_by_default"))
        self.createFoldersCheck.setChecked(self.config.get_setting("organize", "create_category_folders"))
        self.moveFilesCheck.setChecked(self.config.get_setting("organize", "move_files"))
    
    def apply_settings(self):
        """Save current UI state to config."""
        # General
        self.config.set_setting("general", "theme", self.themeCombo.currentText().lower())
        self.config.set_setting("general", "default_directory", self.defaultDirEdit.text())
        
        # Logging settings
        logging_level = self.loggingLevelCombo.currentText()
        debug_enabled = self.enableDebugCheck.isChecked()
        
        self.config.set_setting("general", "logging_level", logging_level)
        self.config.set_setting("general", "enable_debug_logging", debug_enabled)
        
        # Apply logging settings immediately
        if debug_enabled:
            self.log_manager.set_level("DEBUG")
        else:
            self.log_manager.set_level(logging_level)
        
        # Duplicates
        hash_algo = self.hashCombo.currentText().replace("-", "").lower()
        self.config.set_setting("duplicates", "default_hash_algorithm", hash_algo)
        self.config.set_setting("duplicates", "min_file_size", self.minSizeSpin.value())
        self.config.set_setting("duplicates", "skip_system_files", self.skipSystemCheck.isChecked())
        
        # Secure Delete
        self.config.set_setting("secure_delete", "default_passes", self.passesSpin.value())
        
        # Compression
        self.config.set_setting("compression", "default_format", self.formatCombo.currentText().lower())
        self.config.set_setting("compression", "default_compression_level", self.levelSlider.value())
        
        # Sync
        mode_map = {"Two-Way": "two_way", "Mirror": "mirror", "Update": "update"}
        self.config.set_setting("sync", "default_mode", 
                              mode_map[self.syncModeCombo.currentText()])
        self.config.set_setting("sync", "create_backups", self.backupsCheck.isChecked())
        self.config.set_setting("sync", "skip_newer_files", self.skipNewerCheck.isChecked())
        
        # Catalog
        self.config.set_setting("catalog", "recursive_by_default", self.recursiveCheck.isChecked())
        self.config.set_setting("catalog", "check_duplicates", self.duplicatesCheck.isChecked())
        self.config.set_setting("catalog", "show_file_sizes", self.showSizesCheck.isChecked())
        self.config.set_setting("catalog", "show_dates", self.showDatesCheck.isChecked())
        self.config.set_setting("catalog", "default_sort_by", 
                              self.sortByCombo.currentText().lower())
        
        # Organize
        self.config.set_setting("organize", "recursive_by_default", 
                              self.orgRecursiveCheck.isChecked())
        self.config.set_setting("organize", "create_category_folders", 
                              self.createFoldersCheck.isChecked())
        self.config.set_setting("organize", "move_files", self.moveFilesCheck.isChecked())
    
    def reset_settings(self):
        """Reset all settings to defaults."""
        self.config.reset_to_defaults()
        self.load_settings()
    
    def browse_directory(self):
        """Open directory browser dialog."""
        directory = get_existing_directory(self, "Select Default Directory")
        if directory:
            self.defaultDirEdit.setText(directory)
    
    def accept(self):
        """Called when OK button is clicked."""
        self.apply_settings()
        super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
