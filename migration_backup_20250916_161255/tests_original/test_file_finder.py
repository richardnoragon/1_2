import unittest
from PyQt5.QtWidgets import QDialog
# MIGRATION UPDATE: Updated imports for file finder migration to file_utilities_1
# Changed from: from file_finder import FileFinderGUI, FileFinder
# Changed to: from file_utilities_1 import FileFinderWindow and from file_finder import FileFinder
# Reason: FileFinderGUI has been migrated to file_utilities_1 as FileFinderWindow
# FileFinder wrapper class remains in root for backward compatibility
from file_utilities_1 import FileFinderWindow
from file_finder import FileFinder
from config_manager import ConfigManager
from tests.test_gui_base import BaseGuiTest
import os
import shutil

from core.error_handler import error_handler


class TestFileFinder(BaseGuiTest):
    """Test cases for File Finder utility"""
    
    def setUp(self):
        """setup."""
        super().setUp()
        # Create test directory structure
        self.test_files = self.create_test_files()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)
        self.finder = FileFinder(self.config_manager)
        
    def create_test_files(self):
        """Create test files and directories"""
        files = {
            'doc1.txt': 'content1',
            'doc2.txt': 'content2',
            'image.jpg': b'fake image data',
            'subdir/doc3.txt': 'content3',
            'subdir/deep/doc4.txt': 'content4',
            '.hidden.txt': 'hidden content'
        }
        
        for path, content in files.items():
            full_path = os.path.join(self.test_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            mode = 'w' if isinstance(content, str) else 'wb'
            with open(full_path, mode) as f:
                f.write(content)
                
        return files

    def test_finder_initialization(self):
        """Test File Finder initialization"""
        # Verify dialog properties
        self.assertIsInstance(self.finder, QDialog)
        self.assertTrue(hasattr(self.finder, 'config_manager'))
        
        # Verify essential widgets exist
        self.assertIsNotNone(self.finder.search_dir)
        self.assertIsNotNone(self.finder.pattern_edit)
        self.assertIsNotNone(self.finder.search_button)
        self.assertIsNotNone(self.finder.results_list)

    def test_basic_search(self):
        """Test basic file search functionality"""
        # Set search directory
        self.enter_text(self.finder.search_dir, self.test_dir)
        
        # Set search pattern
        self.enter_text(self.finder.pattern_edit, "*.txt")
        
        # Click search
        self.click_button(self.finder.search_button)
        
        # Verify results
        self.assertTrue(self.wait_for(
            lambda: self.finder.results_list.count() == 4  # excluding hidden
        ))
        
        results = [
            self.finder.results_list.item(i).text()
            for i in range(self.finder.results_list.count())
        ]
        
        self.assertIn("doc1.txt", results)
        self.assertIn("doc2.txt", results)
        self.assertIn("doc3.txt", results)
        self.assertIn("doc4.txt", results)

    def test_recursive_search(self):
        """Test recursive search functionality"""
        # Set search directory
        self.enter_text(self.finder.search_dir, self.test_dir)
        
        # Enable recursive search
        self.finder.recursive_check.setChecked(True)
        
        # Set search pattern
        self.enter_text(self.finder.pattern_edit, "doc*.txt")
        
        # Click search
        self.click_button(self.finder.search_button)
        
        # Verify results include files from subdirectories
        results = [
            self.finder.results_list.item(i).text()
            for i in range(self.finder.results_list.count())
        ]
        
        self.assertTrue(any("subdir" in r for r in results))
        self.assertTrue(any("deep" in r for r in results))

    def test_hidden_files(self):
        """Test hidden files search functionality"""
        # Set search directory
        self.enter_text(self.finder.search_dir, self.test_dir)
        
        # Enable hidden files
        self.finder.show_hidden_check.setChecked(True)
        
        # Set search pattern
        self.enter_text(self.finder.pattern_edit, "*.txt")
        
        # Click search
        self.click_button(self.finder.search_button)
        
        # Verify hidden files are included
        results = [
            self.finder.results_list.item(i).text()
            for i in range(self.finder.results_list.count())
        ]
        
        self.assertIn(".hidden.txt", results)

    def test_file_type_filter(self):
        """Test file type filtering"""
        # Set search directory
        self.enter_text(self.finder.search_dir, self.test_dir)
        
        # Select image files
        self.select_in_combo(self.finder.type_combo, "Images")
        
        # Click search
        self.click_button(self.finder.search_button)
        
        # Verify only image files are found
        results = [
            self.finder.results_list.item(i).text()
            for i in range(self.finder.results_list.count())
        ]
        
        self.assertIn("image.jpg", results)
        self.assertNotIn("doc1.txt", results)

    def test_size_filter(self):
        """Test file size filtering"""
        # Set search directory
        self.enter_text(self.finder.search_dir, self.test_dir)
        
        # Set size filter
        self.finder.min_size_spin.setValue(1)  # 1 KB
        self.finder.max_size_spin.setValue(100)  # 100 KB
        
        # Click search
        self.click_button(self.finder.search_button)
        
        # Verify results are size filtered
        self.assertTrue(self.wait_for(
            lambda: all(
                1024 <= os.path.getsize(os.path.join(self.test_dir, 
                    self.finder.results_list.item(i).text())) <= 102400
                for i in range(self.finder.results_list.count())
            )
        ))

    def test_date_filter(self):
        """Test file date filtering"""
        # Set search directory
        self.enter_text(self.finder.search_dir, self.test_dir)
        
        # Set date filter to today
        today = self.finder.date_edit.date()
        self.finder.date_edit.setDate(today)
        self.finder.use_date_check.setChecked(True)
        
        # Click search
        self.click_button(self.finder.search_button)
        
        # Verify results are date filtered
        results = [
            self.finder.results_list.item(i).text()
            for i in range(self.finder.results_list.count())
        ]
        
        # All files should be found since we just created them
        self.assertGreater(len(results), 0)

    def test_result_actions(self):
        """Test actions on search results"""
        # Perform search
        self.enter_text(self.finder.search_dir, self.test_dir)
        self.enter_text(self.finder.pattern_edit, "*.txt")
        self.click_button(self.finder.search_button)
        
        # Select first result
        first_item = self.finder.results_list.item(0)
        self.finder.results_list.setCurrentItem(first_item)
        
        # Test open action
        self.click_button(self.finder.open_button)
        # Verify open attempt (specific verification depends on system)
        
        # Test copy path action
        self.click_button(self.finder.copy_path_button)
        # Verify path is in clipboard
        self.assertTrue(self.wait_for(
            lambda: os.path.exists(self.app.clipboard().text())
        ))

    def test_invalid_search(self):
        """Test handling of invalid search parameters"""
        # Try search without directory
        self.click_button(self.finder.search_button)
        
        # Verify error message
        self.assertTrue(self.verify_status_message(
            self.finder.status_bar,
            "Please select a search directory"
        ))
        
        # Try invalid pattern
        self.enter_text(self.finder.search_dir, self.test_dir)
        self.enter_text(self.finder.pattern_edit, "[invalid")
        self.click_button(self.finder.search_button)
        
        # Verify error message
        self.assertTrue(self.verify_status_message(
            self.finder.status_bar,
            "Invalid search pattern"
        ))

    def test_search_cancellation(self):
        """Test search cancellation"""
        # Start search in directory with many files
        many_files_dir = os.path.join(self.test_dir, "many_files")
        os.makedirs(many_files_dir)
        for i in range(1000):
            with open(os.path.join(many_files_dir, f"file{i}.txt"), 'w') as f:
                f.write("content")
        
        self.enter_text(self.finder.search_dir, many_files_dir)
        self.click_button(self.finder.search_button)
        
        # Cancel search
        self.click_button(self.finder.cancel_button)
        
        # Verify search was cancelled
        self.assertTrue(self.verify_status_message(
            self.finder.status_bar,
            "Search cancelled"
        ))
        
        # Clean up
        shutil.rmtree(many_files_dir)

    def test_save_load_settings(self):
        """Test saving and loading search settings"""
        # Configure settings
        self.enter_text(self.finder.search_dir, self.test_dir)
        self.enter_text(self.finder.pattern_edit, "*.txt")
        self.finder.recursive_check.setChecked(True)
        self.finder.show_hidden_check.setChecked(True)
        
        # Save settings
        self.finder.save_settings()
        
        # Create new finder instance
        new_finder = FileFinder(self.config_manager)
        
        # Verify settings are loaded
        self.assertEqual(new_finder.search_dir.text(), self.test_dir)
        self.assertEqual(new_finder.pattern_edit.text(), "*.txt")
        self.assertTrue(new_finder.recursive_check.isChecked())
        self.assertTrue(new_finder.show_hidden_check.isChecked())

if __name__ == '__main__':
    unittest.main()