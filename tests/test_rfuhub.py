import unittest
from PyQt5.QtWidgets import QMainWindow
from rfuhub import RFUHub
from settings_dialog import SettingsDialog
from config_manager import ConfigManager
from tests.test_gui_base import BaseGuiTest
import os

class TestRFUHub(BaseGuiTest):
    """Test cases for RFU Hub main window functionality"""
    
    def setUp(self):
        super().setUp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)
        self.hub = RFUHub(self.config_manager)

    def test_hub_initialization(self):
        """Test RFU Hub initialization"""
        # Verify main window properties
        self.assertIsInstance(self.hub, QMainWindow)
        self.assertTrue(hasattr(self.hub, 'config_manager'))
        
        # Verify essential widgets exist
        self.assertIsNotNone(self.hub.utility_list)
        self.assertIsNotNone(self.hub.settings_button)
        self.assertIsNotNone(self.hub.status_bar)

    def test_utility_list_population(self):
        """Test utility list is populated correctly"""
        # Get list of utilities
        utility_count = self.hub.utility_list.count()
        
        # Verify essential utilities are present
        utilities = [
            self.hub.utility_list.item(i).text()
            for i in range(utility_count)
        ]
        
        essential_utilities = [
            "File Finder",
            "File Organizer",
            "Duplicate Finder",
            "File Sync",
            "File Permissions",
            "Size Analyzer"
        ]
        
        for utility in essential_utilities:
            self.assertIn(utility, utilities)

    def test_utility_launch(self):
        """Test launching utilities"""
        # Select File Finder utility
        self.select_in_list(self.hub.utility_list, "File Finder")
        
        # Launch utility
        self.click_button(self.hub.launch_button)
        
        # Verify utility window is shown
        self.assertTrue(self.wait_for(
            lambda: any(w.windowTitle() == "File Finder" 
                      for w in self.app.topLevelWidgets())
        ))

    def test_settings_dialog(self):
        """Test opening settings dialog"""
        # Click settings button
        self.click_button(self.hub.settings_button)
        
        # Verify settings dialog is shown
        dialog = self.capture_dialog(
            lambda: None,  # Dialog already triggered
            SettingsDialog
        )
        self.assertIsNotNone(dialog)

    def test_recent_files(self):
        """Test recent files functionality"""
        # Create test files
        test_files = [
            os.path.join(self.test_dir, f"test{i}.txt")
            for i in range(3)
        ]
        for file in test_files:
            with open(file, 'w') as f:
                f.write("test content")
        
        # Add files to recent list
        for file in test_files:
            self.hub.add_recent_file(file)
        
        # Verify files appear in recent menu
        recent_actions = self.hub.recent_menu.actions()
        self.assertEqual(len(recent_actions), len(test_files))
        
        for file, action in zip(reversed(test_files), recent_actions):
            self.assertEqual(action.data(), file)

    def test_theme_change(self):
        """Test theme changing functionality"""
        # Change theme in config
        self.config_manager.update_config('theme', 'dark')
        
        # Trigger theme update
        self.hub.apply_theme()
        
        # Verify theme is applied
        self.assertTrue(self.wait_for(
            lambda: "dark" in self.hub.styleSheet().lower()
        ))

    def test_language_change(self):
        """Test language changing functionality"""
        # Change language in config
        self.config_manager.update_config('language', 'de')
        
        # Trigger language update
        self.hub.apply_language()
        
        # Verify language is applied (check a known translation)
        self.assertTrue(self.wait_for(
            lambda: "Datei" in self.hub.file_menu.title()
        ))

    def test_utility_search(self):
        """Test utility search functionality"""
        # Enter search text
        self.enter_text(self.hub.search_box, "sync")
        
        # Verify filtered results
        visible_items = [
            self.hub.utility_list.item(i).text()
            for i in range(self.hub.utility_list.count())
            if not self.hub.utility_list.item(i).isHidden()
        ]
        
        self.assertIn("File Sync", visible_items)
        self.assertNotIn("File Finder", visible_items)

    def test_status_messages(self):
        """Test status bar message functionality"""
        # Launch a utility
        self.select_in_list(self.hub.utility_list, "File Finder")
        self.click_button(self.hub.launch_button)
        
        # Verify status message
        self.assertTrue(self.verify_status_message(
            self.hub.status_bar,
            "Launching File Finder"
        ))

    def test_window_state_persistence(self):
        """Test window state persistence"""
        # Change window state
        new_size = (800, 600)
        self.hub.resize(*new_size)
        
        # Save state
        self.hub.save_window_state()
        
        # Create new hub instance
        new_hub = RFUHub(self.config_manager)
        
        # Verify state is restored
        self.assertEqual(
            (new_hub.width(), new_hub.height()),
            new_size
        )

    def test_error_handling(self):
        """Test error handling in hub"""
        # Try to launch non-existent utility
        with self.assertRaises(ValueError):
            self.hub.launch_utility("Non-existent Utility")
        
        # Verify error message shown
        self.assertTrue(self.verify_status_message(
            self.hub.status_bar,
            "Error: Utility not found"
        ))

if __name__ == '__main__':
    unittest.main()