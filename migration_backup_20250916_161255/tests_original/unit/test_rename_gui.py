"""
Test suite for the consolidated RenameGUI implementation.

This test suite validates all functionality of the migrated and consolidated
rename GUI, ensuring PyQt5 compatibility and proper integration with the
file_utilities_2 architecture.
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# PyQt5 imports for testing
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Import the consolidated rename GUI
from file_utilities_2.gui.rename_gui import RenameGUI


class TestRenameGUI(unittest.TestCase):
    """Test cases for the consolidated RenameGUI class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with QApplication."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test files
        self.test_files = [
            "test_file_1.txt",
            "test_file_2.jpg", 
            "test_file_3.mp3",
            "document.pdf",
            "image.png"
        ]
        
        for filename in self.test_files:
            test_file = self.test_dir / filename
            test_file.write_text("test content")
        
        # Mock the UI loading to avoid file dependencies
        with patch('file_utilities_2.gui.rename_gui.uic.loadUi'):
            with patch.object(RenameGUI, '_setup_models'):
                with patch.object(RenameGUI, '_setup_metadata_formats'):
                    with patch.object(RenameGUI, '_apply_standardized_theming'):
                        with patch.object(RenameGUI, '_connect_signals'):
                            self.rename_gui = RenameGUI()
        
        # Mock UI components
        self._setup_mock_ui_components()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # Close the GUI window
        if hasattr(self, 'rename_gui'):
            self.rename_gui.close()
    
    def _setup_mock_ui_components(self):
        """Setup mock UI components for testing."""
        # Mock UI elements
        self.rename_gui.listView = Mock()
        self.rename_gui.selectView = Mock()
        self.rename_gui.nameEdit = Mock()
        self.rename_gui.filterEdit = Mock()
        self.rename_gui.metadataFormatCombo = Mock()
        
        # Mock radio buttons
        self.rename_gui.addPrefixRadio = Mock()
        self.rename_gui.removePrefixRadio = Mock()
        self.rename_gui.addSuffixRadio = Mock()
        self.rename_gui.removeSuffixRadio = Mock()
        self.rename_gui.newNameRadio = Mock()
        self.rename_gui.lowerCaseRadio = Mock()
        self.rename_gui.radioButton = Mock()  # Upper case radio
        self.rename_gui.adddateprefixRadio = Mock()
        self.rename_gui.adddatesuffixRadio = Mock()
        self.rename_gui.metadataRadio = Mock()
        
        # Mock buttons
        self.rename_gui.filterButton = Mock()
        self.rename_gui.selectButton = Mock()
        self.rename_gui.removeButton = Mock()
        self.rename_gui.applyButton = Mock()
        
        # Mock menu actions
        self.rename_gui.actionSelect = Mock()
        self.rename_gui.actionExit = Mock()
    
    def test_initialization(self):
        """Test RenameGUI initialization."""
        self.assertIsInstance(self.rename_gui, RenameGUI)
        self.assertEqual(self.rename_gui._current_dir, Path("."))
        self.assertEqual(self.rename_gui._selected_files, [])
        self.assertIsNotNone(self.rename_gui._file_list_model)
        self.assertIsNotNone(self.rename_gui._selection_model)
    
    def test_date_formats_constant(self):
        """Test that DATE_FORMATS constant is properly defined."""
        expected_formats = [
            "YYYY-MM-DD_HHMMSS",
            "YYYYMMDD_HHMMSS", 
            "DD-MM-YYYY_HHMMSS",
            "YYYY-MM-DD",
            "YYYYMMDD"
        ]
        self.assertEqual(RenameGUI.DATE_FORMATS, expected_formats)
    
    @patch('file_utilities_2.gui.rename_gui.Path')
    def test_get_rename_icon(self, mock_path):
        """Test rename icon path resolution."""
        # Mock icon path exists
        mock_icon_path = Mock()
        mock_icon_path.exists.return_value = True
        mock_path.return_value.__truediv__.return_value = mock_icon_path
        
        icon_path = self.rename_gui._get_rename_icon()
        self.assertIsInstance(icon_path, str)
    
    def test_get_files_in_directory(self):
        """Test getting files from directory."""
        self.rename_gui._current_dir = self.test_dir
        files = self.rename_gui._get_files_in_directory()
        
        self.assertEqual(len(files), len(self.test_files))
        for filename in self.test_files:
            self.assertIn(filename, files)
    
    def test_get_files_in_nonexistent_directory(self):
        """Test getting files from non-existent directory."""
        self.rename_gui._current_dir = Path("/nonexistent/directory")
        files = self.rename_gui._get_files_in_directory()
        self.assertEqual(files, [])
    
    def test_get_filtered_files(self):
        """Test file filtering functionality."""
        self.rename_gui._current_dir = self.test_dir
        
        # Test filtering by extension
        filtered_files = self.rename_gui._get_filtered_files("txt")
        self.assertEqual(len(filtered_files), 1)
        self.assertIn("test_file_1.txt", filtered_files)
        
        # Test filtering by partial name
        filtered_files = self.rename_gui._get_filtered_files("test_file")
        self.assertEqual(len(filtered_files), 3)
    
    def test_add_to_selection(self):
        """Test adding files to selection."""
        filename = "test_file.txt"
        self.rename_gui._add_to_selection(filename)
        
        self.assertIn(filename, self.rename_gui._selected_files)
        self.rename_gui._selection_model.appendRow.assert_called_once()
    
    def test_clear_selection(self):
        """Test clearing selection."""
        # Add some files to selection first
        self.rename_gui._selected_files = ["file1.txt", "file2.txt"]
        
        self.rename_gui._clear_selection()
        
        self.assertEqual(self.rename_gui._selected_files, [])
        self.rename_gui._selection_model.clear.assert_called_once()
    
    def test_get_rename_mode_and_params_prefix(self):
        """Test getting rename mode and parameters for prefix mode."""
        # Setup mocks for prefix mode
        self.rename_gui.nameEdit.text.return_value = "prefix_"
        self.rename_gui.addPrefixRadio.isChecked.return_value = True
        self.rename_gui.metadataRadio.isChecked.return_value = False
        self.rename_gui.removePrefixRadio.isChecked.return_value = False
        self.rename_gui.addSuffixRadio.isChecked.return_value = False
        self.rename_gui.removeSuffixRadio.isChecked.return_value = False
        self.rename_gui.newNameRadio.isChecked.return_value = False
        self.rename_gui.lowerCaseRadio.isChecked.return_value = False
        self.rename_gui.radioButton.isChecked.return_value = False
        self.rename_gui.adddateprefixRadio.isChecked.return_value = False
        self.rename_gui.adddatesuffixRadio.isChecked.return_value = False
        
        mode, text, date_format = self.rename_gui._get_rename_mode_and_params()
        
        self.assertEqual(mode, "prefix")
        self.assertEqual(text, "prefix_")
        self.assertIsNone(date_format)
    
    def test_get_rename_mode_and_params_metadata(self):
        """Test getting rename mode and parameters for metadata mode."""
        # Setup mocks for metadata mode
        self.rename_gui.nameEdit.text.return_value = ""
        self.rename_gui.metadataRadio.isChecked.return_value = True
        self.rename_gui.metadataFormatCombo.currentText.return_value = "YYYY-MM-DD"
        self.rename_gui.addPrefixRadio.isChecked.return_value = False
        self.rename_gui.removePrefixRadio.isChecked.return_value = False
        self.rename_gui.addSuffixRadio.isChecked.return_value = False
        self.rename_gui.removeSuffixRadio.isChecked.return_value = False
        self.rename_gui.newNameRadio.isChecked.return_value = False
        self.rename_gui.lowerCaseRadio.isChecked.return_value = False
        self.rename_gui.radioButton.isChecked.return_value = False
        self.rename_gui.adddateprefixRadio.isChecked.return_value = False
        self.rename_gui.adddatesuffixRadio.isChecked.return_value = False
        
        mode, text, date_format = self.rename_gui._get_rename_mode_and_params()
        
        self.assertEqual(mode, "metadata")
        self.assertEqual(text, "")
        self.assertEqual(date_format, "YYYY-MM-DD")
    
    def test_validate_rename_params_valid(self):
        """Test validation of valid rename parameters."""
        # Test valid prefix mode
        result = self.rename_gui._validate_rename_params("prefix", "test_")
        self.assertTrue(result)
        
        # Test valid case mode (no text required)
        result = self.rename_gui._validate_rename_params("lower", "")
        self.assertTrue(result)
    
    def test_validate_rename_params_invalid(self):
        """Test validation of invalid rename parameters."""
        with patch.object(self.rename_gui, 'show_warning_dialog'):
            # Test invalid prefix mode (no text)
            result = self.rename_gui._validate_rename_params("prefix", "")
            self.assertFalse(result)
            
            # Test no mode selected
            result = self.rename_gui._validate_rename_params(None, "text")
            self.assertFalse(result)
    
    @patch('file_utilities_2.gui.rename_gui.FileRenamer')
    def test_perform_rename_operation(self, mock_file_renamer):
        """Test performing rename operation."""
        # Setup test data
        self.rename_gui._current_dir = self.test_dir
        self.rename_gui._selected_files = ["test_file_1.txt", "test_file_2.jpg"]
        
        # Mock FileRenamer.rename_files to return success
        mock_file_renamer.rename_files.return_value = [True, True]
        
        # Mock UI methods
        with patch.object(self.rename_gui, 'show_status_message'):
            with patch.object(self.rename_gui, '_show_rename_results'):
                with patch.object(self.rename_gui, '_clear_selection'):
                    with patch.object(self.rename_gui, '_update_file_list'):
                        
                        self.rename_gui._perform_rename_operation(
                            "prefix", "test_", None
                        )
                        
                        # Verify FileRenamer was called
                        mock_file_renamer.rename_files.assert_called_once()
                        
                        # Verify UI updates were called
                        self.rename_gui._clear_selection.assert_called_once()
                        self.rename_gui._update_file_list.assert_called_once()
    
    def test_show_rename_results_all_success(self):
        """Test showing rename results for all successful renames."""
        with patch.object(self.rename_gui, 'show_info_dialog') as mock_info:
            with patch.object(self.rename_gui, 'show_status_message'):
                self.rename_gui._show_rename_results(3, 3)
                mock_info.assert_called_once()
    
    def test_show_rename_results_all_failed(self):
        """Test showing rename results for all failed renames."""
        with patch.object(self.rename_gui, 'show_error_dialog') as mock_error:
            with patch.object(self.rename_gui, 'show_status_message'):
                self.rename_gui._show_rename_results(0, 3)
                mock_error.assert_called_once()
    
    def test_show_rename_results_partial_success(self):
        """Test showing rename results for partial success."""
        with patch.object(self.rename_gui, 'show_warning_dialog') as mock_warning:
            with patch.object(self.rename_gui, 'show_status_message'):
                self.rename_gui._show_rename_results(2, 3)
                mock_warning.assert_called_once()
    
    @patch('file_utilities_2.gui.rename_gui.QMessageBox')
    def test_confirm_rename_operation_yes(self, mock_msgbox):
        """Test confirming rename operation - user says yes."""
        mock_msgbox.question.return_value = mock_msgbox.Yes
        self.rename_gui._selected_files = ["file1.txt", "file2.txt"]
        
        result = self.rename_gui._confirm_rename_operation()
        self.assertTrue(result)
    
    @patch('file_utilities_2.gui.rename_gui.QMessageBox')
    def test_confirm_rename_operation_no(self, mock_msgbox):
        """Test confirming rename operation - user says no."""
        mock_msgbox.question.return_value = mock_msgbox.No
        self.rename_gui._selected_files = ["file1.txt", "file2.txt"]
        
        result = self.rename_gui._confirm_rename_operation()
        self.assertFalse(result)
    
    def test_load_directory_success(self):
        """Test successful directory loading."""
        with patch.object(self.rename_gui, 'get_directory_path') as mock_get_dir:
            with patch.object(self.rename_gui, '_update_file_list'):
                with patch.object(self.rename_gui, 'show_status_message'):
                    
                    mock_get_dir.return_value = str(self.test_dir)
                    
                    self.rename_gui.load_directory()
                    
                    self.assertEqual(self.rename_gui._current_dir, self.test_dir)
                    self.rename_gui._update_file_list.assert_called_once()
    
    def test_load_directory_cancelled(self):
        """Test directory loading when user cancels."""
        with patch.object(self.rename_gui, 'get_directory_path') as mock_get_dir:
            mock_get_dir.return_value = ""  # User cancelled
            
            original_dir = self.rename_gui._current_dir
            self.rename_gui.load_directory()
            
            # Directory should remain unchanged
            self.assertEqual(self.rename_gui._current_dir, original_dir)


class TestRenameGUIIntegration(unittest.TestCase):
    """Integration tests for RenameGUI with actual file operations."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with QApplication."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        # Create temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test files with different extensions
        self.test_files = {
            "document.txt": "Sample text content",
            "image.jpg": "fake image content",
            "audio.mp3": "fake audio content",
            "data.csv": "col1,col2\nval1,val2"
        }
        
        for filename, content in self.test_files.items():
            test_file = self.test_dir / filename
            test_file.write_text(content)
    
    def tearDown(self):
        """Clean up after integration tests."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('file_utilities_2.gui.rename_gui.uic.loadUi')
    def test_file_operations_integration(self, mock_load_ui):
        """Test integration with actual file operations."""
        # This test would require more complex setup to avoid UI dependencies
        # For now, we'll test the core logic integration
        
        with patch.object(RenameGUI, '_setup_models'):
            with patch.object(RenameGUI, '_setup_metadata_formats'):
                with patch.object(RenameGUI, '_apply_standardized_theming'):
                    with patch.object(RenameGUI, '_connect_signals'):
                        rename_gui = RenameGUI()
        
        # Test directory file listing
        rename_gui._current_dir = self.test_dir
        files = rename_gui._get_files_in_directory()
        
        self.assertEqual(len(files), len(self.test_files))
        for filename in self.test_files.keys():
            self.assertIn(filename, files)


def main():
    """Run the test suite."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestRenameGUI))
    test_suite.addTest(unittest.makeSuite(TestRenameGUIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())