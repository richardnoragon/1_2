import unittest
from PyQt5.QtWidgets import QDialog
from settings_dialog import SettingsDialog
from config_manager import ConfigManager
from tests.test_gui_base import BaseGuiTest
import os

class TestSettingsDialog(BaseGuiTest):
    """Test cases for settings dialog functionality"""
    
    def setUp(self):
        super().setUp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)
        self.dialog = SettingsDialog(self.config_manager)

    def test_dialog_initialization(self):
        """Test settings dialog initialization"""
        # Verify dialog properties
        self.assertIsInstance(self.dialog, QDialog)
        self.assertTrue(hasattr(self.dialog, 'config_manager'))
        
        # Verify initial widget states
        self.assertTrue(self.dialog.theme_combo.count() > 0)
        self.assertTrue(self.dialog.language_combo.count() > 0)
        self.assertIsNotNone(self.dialog.ok_button)
        self.assertIsNotNone(self.dialog.cancel_button)

    def test_load_settings(self):
        """Test loading settings into dialog"""
        # Set test configuration
        test_config = {
            'theme': 'dark',
            'language': 'de',
            'show_hidden': True,
            'backup_enabled': True,
            'max_recent_files': 5
        }
        self.config_manager.save_config(test_config)
        
        # Create new dialog to load settings
        dialog = SettingsDialog(self.config_manager)
        
        # Verify settings are loaded correctly
        self.assertEqual(dialog.theme_combo.currentText(), 'dark')
        self.assertEqual(dialog.language_combo.currentText(), 'de')
        self.assertTrue(dialog.show_hidden_check.isChecked())
        self.assertTrue(dialog.backup_check.isChecked())
        self.assertEqual(dialog.recent_files_spin.value(), 5)

    def test_save_settings(self):
        """Test saving settings from dialog"""
        # Change settings in dialog
        self.select_in_combo(self.dialog.theme_combo, 'dark')
        self.select_in_combo(self.dialog.language_combo, 'de')
        self.dialog.show_hidden_check.setChecked(True)
        self.dialog.backup_check.setChecked(True)
        self.dialog.recent_files_spin.setValue(7)
        
        # Accept dialog to save settings
        self.click_button(self.dialog.ok_button)
        
        # Verify settings were saved
        config = self.config_manager.get_config()
        self.assertEqual(config['theme'], 'dark')
        self.assertEqual(config['language'], 'de')
        self.assertTrue(config['show_hidden'])
        self.assertTrue(config['backup_enabled'])
        self.assertEqual(config['max_recent_files'], 7)

    def test_cancel_settings(self):
        """Test canceling settings changes"""
        # Store original settings
        original_config = self.config_manager.get_config()
        
        # Change settings in dialog
        self.select_in_combo(self.dialog.theme_combo, 'dark')
        self.select_in_combo(self.dialog.language_combo, 'de')
        
        # Cancel dialog
        self.click_button(self.dialog.cancel_button)
        
        # Verify settings were not changed
        config = self.config_manager.get_config()
        self.assertEqual(config, original_config)

    def test_invalid_settings(self):
        """Test handling of invalid settings"""
        # Try to set invalid value for max recent files
        self.dialog.recent_files_spin.setValue(-1)
        
        # Try to save settings
        self.click_button(self.dialog.ok_button)
        
        # Verify error is shown
        self.assertTrue(self.verify_status_message(
            self.dialog.status_bar,
            "Invalid value for maximum recent files"
        ))
        
        # Verify dialog stays open
        self.assertTrue(self.dialog.isVisible())

    def test_reset_defaults(self):
        """Test resetting settings to defaults"""
        # Change settings
        self.select_in_combo(self.dialog.theme_combo, 'dark')
        self.select_in_combo(self.dialog.language_combo, 'de')
        
        # Click reset button
        self.click_button(self.dialog.reset_button)
        
        # Verify settings are reset to defaults
        self.assertEqual(self.dialog.theme_combo.currentText(), 'light')
        self.assertEqual(self.dialog.language_combo.currentText(), 'en')
        self.assertFalse(self.dialog.show_hidden_check.isChecked())

    def test_apply_settings(self):
        """Test applying settings without closing dialog"""
        # Change settings
        self.select_in_combo(self.dialog.theme_combo, 'dark')
        self.select_in_combo(self.dialog.language_combo, 'de')
        
        # Click apply button
        self.click_button(self.dialog.apply_button)
        
        # Verify settings are saved
        config = self.config_manager.get_config()
        self.assertEqual(config['theme'], 'dark')
        self.assertEqual(config['language'], 'de')
        
        # Verify dialog stays open
        self.assertTrue(self.dialog.isVisible())

    def test_settings_validation(self):
        """Test validation of settings combinations"""
        # Set incompatible settings
        self.dialog.backup_check.setChecked(True)
        self.dialog.backup_location_edit.setText("")  # Empty backup location
        
        # Try to save
        self.click_button(self.dialog.ok_button)
        
        # Verify error is shown
        self.assertTrue(self.verify_status_message(
            self.dialog.status_bar,
            "Backup location required when backup is enabled"
        ))
        
        # Verify dialog stays open
        self.assertTrue(self.dialog.isVisible())

    def test_dynamic_controls(self):
        """Test dynamic enabling/disabling of controls"""
        # Enable backup
        self.dialog.backup_check.setChecked(True)
        
        # Verify backup location becomes enabled
        self.assertTrue(self.verify_widget_enabled(
            self.dialog.backup_location_edit
        ))
        
        # Disable backup
        self.dialog.backup_check.setChecked(False)
        
        # Verify backup location becomes disabled
        self.assertTrue(self.verify_widget_enabled(
            self.dialog.backup_location_edit,
            expected_enabled=False
        ))

if __name__ == '__main__':
    unittest.main()