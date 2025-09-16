#!/usr/bin/env python3
"""
Comprehensive Unit Tests for file_finder.py
Generated: 2025-08-24

This module provides comprehensive unit testing for the FileFinderGUI class
and its associated functionality using pytest framework with mock testing.
"""

import os
import sys
import tempfile
import shutil
import csv
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PyQt5.QtWidgets import QApplication

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    from src.tools.file_management.file_finder import FileFinderGUI
except ImportError as e:
    pytest.skip(
        f"Cannot import file_finder module: {e}", 
        allow_module_level=True
    )


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app here as it might be used by other tests


@pytest.fixture
def file_finder_window(qapp):
    """Create FileFinderGUI instance for testing."""
    with patch('src.tools.file_management.file_finder.StandardWindow'):
        window = FileFinderGUI()
        yield window
        if hasattr(window, 'close'):
            window.close()


@pytest.fixture
def temp_directory():
    """Create temporary directory with test files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test files with various patterns
    test_files = [
        'document.txt',
        'image.jpg',
        'data.csv',
        'script.py',
        'archive.zip',
        'config.ini',
        'readme.md',
        'test_file.txt',
        'sample.pdf'
    ]
    
    for filename in test_files:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Test content for {filename}")
    
    # Create subdirectory with more files
    sub_dir = os.path.join(temp_dir, 'subdirectory')
    os.makedirs(sub_dir)
    
    sub_files = [
        'nested_document.txt',
        'nested_image.png',
        'nested_script.py',
        'nested_data.json'
    ]
    
    for filename in sub_files:
        file_path = os.path.join(sub_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Nested content for {filename}")
    
    # Create another subdirectory level
    deep_dir = os.path.join(sub_dir, 'deep')
    os.makedirs(deep_dir)
    
    deep_file = os.path.join(deep_dir, 'deep_file.txt')
    with open(deep_file, 'w', encoding='utf-8') as f:
        f.write("Deep nested content")
    
    yield temp_dir
    
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass


@pytest.fixture
def mock_file_dialog():
    """Mock file dialog responses."""
    file_dialog_path = 'src.tools.file_management.file_finder.QFileDialog'
    with patch(file_dialog_path) as mock:
        yield mock


@pytest.fixture
def mock_message_box():
    """Mock message box responses."""
    message_box_path = 'src.tools.file_management.file_finder.QMessageBox'
    with patch(message_box_path) as mock:
        yield mock


@pytest.fixture
def mock_os_operations():
    """Mock operating system operations."""
    startfile_path = 'src.tools.file_management.file_finder.os.startfile'
    system_path = 'src.tools.file_management.file_finder.os.system'
    with patch(startfile_path) as mock_startfile, \
         patch(system_path) as mock_system:
        yield {
            'startfile': mock_startfile,
            'system': mock_system
        }


class TestFileFinderGUI:
    """Test cases for FileFinderGUI class functionality."""

    def test_file_finder_initialization(self, file_finder_window):
        """Test FileFinderGUI initialization and basic attributes."""
        assert hasattr(file_finder_window, 'current_directory')
        assert file_finder_window.current_directory == ""

    def test_setup_menu_callbacks(self, file_finder_window):
        """Test menu callback setup functionality."""
        # Mock menu_manager
        file_finder_window.menu_manager = Mock()
        
        file_finder_window._setup_menu_callbacks()
        
        # Verify callback registrations
        expected_callbacks = [
            ('new_search', 'clear_results'),
            ('save_results', 'save_search_results'),
            ('export_results', 'export_search_results')
        ]
        
        for callback_name, method_name in expected_callbacks:
            file_finder_window.menu_manager.register_callback.assert_any_call(
                callback_name,
                getattr(file_finder_window, method_name)
            )

    def test_browse_directory(self, file_finder_window, mock_file_dialog, 
                             temp_directory):
        """Test directory browsing functionality."""
        mock_file_dialog.getExistingDirectory.return_value = temp_directory
        file_finder_window.directory_edit = Mock()
        
        file_finder_window.browse_directory()
        
        assert file_finder_window.current_directory == temp_directory
        file_finder_window.directory_edit.setText.assert_called_with(temp_directory)

    def test_browse_directory_cancelled(self, file_finder_window, mock_file_dialog):
        """Test directory browsing cancellation."""
        mock_file_dialog.getExistingDirectory.return_value = ""
        file_finder_window.directory_edit = Mock()
        original_directory = file_finder_window.current_directory
        
        file_finder_window.browse_directory()
        
        assert file_finder_window.current_directory == original_directory
        file_finder_window.directory_edit.setText.assert_not_called()

    def test_start_search_no_directory(self, file_finder_window, mock_message_box):
        """Test search with no directory selected."""
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = ""
        
        file_finder_window.start_search()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "select a directory" in call_args[2].lower()

    def test_start_search_nonexistent_directory(self, file_finder_window, 
                                              mock_message_box):
        """Test search with nonexistent directory."""
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = "/nonexistent"
        
        file_finder_window.start_search()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "does not exist" in call_args[2].lower()

    def test_start_search_recursive_success(self, file_finder_window, temp_directory):
        """Test successful recursive search."""
        # Setup window controls
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.txt"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Verify results were added
        assert file_finder_window.results_list.addItem.call_count > 0
        file_finder_window.results_label.setText.assert_called()
        call_args = file_finder_window.results_label.setText.call_args[0][0]
        assert "Found" in call_args and "file(s)" in call_args

    def test_start_search_non_recursive_success(self, file_finder_window, 
                                              temp_directory):
        """Test successful non-recursive search."""
        # Setup window controls
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.py"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = False
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Verify results were added (should find script.py in root)
        assert file_finder_window.results_list.addItem.call_count > 0
        file_finder_window.results_label.setText.assert_called()

    def test_start_search_no_results(self, file_finder_window, temp_directory):
        """Test search with no matching results."""
        # Setup window controls
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.nonexistent"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        file_finder_window.results_label.setText.assert_called_with(
            "No files found matching the criteria"
        )

    def test_start_search_empty_pattern(self, file_finder_window, temp_directory):
        """Test search with empty pattern defaults to *.*"""
        # Setup window controls
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = ""
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = False
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Should find all files since pattern defaults to *.*
        assert file_finder_window.results_list.addItem.call_count > 0

    def test_show_file_info_existing_file(self, file_finder_window, temp_directory):
        """Test file info display for existing file."""
        file_finder_window.file_info_text = Mock()
        file_finder_window.open_button = Mock()
        file_finder_window.open_folder_button = Mock()
        
        # Create mock item
        item = Mock()
        test_file = os.path.join(temp_directory, "document.txt")
        item.text.return_value = test_file
        
        file_finder_window.show_file_info(item)
        
        file_finder_window.file_info_text.setText.assert_called()
        call_args = file_finder_window.file_info_text.setText.call_args[0][0]
        assert "document.txt" in call_args
        assert "Size:" in call_args
        assert "Modified:" in call_args
        file_finder_window.open_button.setEnabled.assert_called_with(True)
        file_finder_window.open_folder_button.setEnabled.assert_called_with(True)

    def test_show_file_info_nonexistent_file(self, file_finder_window):
        """Test file info display for nonexistent file."""
        file_finder_window.file_info_text = Mock()
        file_finder_window.open_button = Mock()
        file_finder_window.open_folder_button = Mock()
        
        # Create mock item
        item = Mock()
        item.text.return_value = "/nonexistent/file.txt"
        
        file_finder_window.show_file_info(item)
        
        file_finder_window.file_info_text.setText.assert_called()
        call_args = file_finder_window.file_info_text.setText.call_args[0][0]
        assert "Error reading file information" in call_args
        file_finder_window.open_button.setEnabled.assert_called_with(False)
        file_finder_window.open_folder_button.setEnabled.assert_called_with(False)

    def test_open_file_double_click(self, file_finder_window, temp_directory,
                                   mock_os_operations):
        """Test opening file via double-click."""
        item = Mock()
        test_file = os.path.join(temp_directory, "document.txt")
        item.text.return_value = test_file
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'win32'):
            file_finder_window.open_file(item)
            
        mock_os_operations['startfile'].assert_called_with(test_file)

    def test_open_selected_file(self, file_finder_window, temp_directory,
                               mock_os_operations):
        """Test opening currently selected file."""
        file_finder_window.results_list = Mock()
        item = Mock()
        test_file = os.path.join(temp_directory, "document.txt")
        item.text.return_value = test_file
        file_finder_window.results_list.currentItem.return_value = item
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'win32'):
            file_finder_window.open_selected_file()
            
        mock_os_operations['startfile'].assert_called_with(test_file)

    def test_open_selected_file_no_selection(self, file_finder_window, 
                                           mock_os_operations):
        """Test opening file with no selection."""
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.currentItem.return_value = None
        
        file_finder_window.open_selected_file()
        
        mock_os_operations['startfile'].assert_not_called()

    def test_open_file_folder(self, file_finder_window, temp_directory,
                             mock_os_operations):
        """Test opening folder containing selected file."""
        file_finder_window.results_list = Mock()
        item = Mock()
        test_file = os.path.join(temp_directory, "document.txt")
        item.text.return_value = test_file
        file_finder_window.results_list.currentItem.return_value = item
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'win32'):
            file_finder_window.open_file_folder()
            
        mock_os_operations['startfile'].assert_called_with(temp_directory)

    def test_open_file_with_system_windows(self, file_finder_window, temp_directory,
                                          mock_os_operations):
        """Test opening file on Windows platform."""
        test_file = os.path.join(temp_directory, "document.txt")
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'win32'):
            file_finder_window.open_file_with_system(test_file)
            
        mock_os_operations['startfile'].assert_called_with(test_file)

    def test_open_file_with_system_macos(self, file_finder_window, temp_directory,
                                        mock_os_operations):
        """Test opening file on macOS platform."""
        test_file = os.path.join(temp_directory, "document.txt")
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'darwin'):
            file_finder_window.open_file_with_system(test_file)
            
        expected_command = f'open "{test_file}"'
        mock_os_operations['system'].assert_called_with(expected_command)

    def test_open_file_with_system_linux(self, file_finder_window, temp_directory,
                                        mock_os_operations):
        """Test opening file on Linux platform."""
        test_file = os.path.join(temp_directory, "document.txt")
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'linux'):
            file_finder_window.open_file_with_system(test_file)
            
        expected_command = f'xdg-open "{test_file}"'
        mock_os_operations['system'].assert_called_with(expected_command)

    def test_open_file_with_system_error(self, file_finder_window, mock_message_box,
                                        mock_os_operations):
        """Test file opening error handling."""
        mock_os_operations['startfile'].side_effect = Exception("File not found")
        
        with patch('src.tools.file_management.file_finder.sys.platform', 'win32'):
            file_finder_window.open_file_with_system("/nonexistent/file.txt")
            
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "Could not open file" in call_args[2]

    def test_clear_results(self, file_finder_window):
        """Test clearing search results."""
        file_finder_window.results_list = Mock()
        file_finder_window.file_info_text = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.open_button = Mock()
        file_finder_window.open_folder_button = Mock()
        
        file_finder_window.clear_results()
        
        file_finder_window.results_list.clear.assert_called_once()
        file_finder_window.file_info_text.clear.assert_called_once()
        file_finder_window.results_label.setText.assert_called_with(
            "No search performed yet"
        )
        file_finder_window.open_button.setEnabled.assert_called_with(False)
        file_finder_window.open_folder_button.setEnabled.assert_called_with(False)

    def test_save_search_results_no_results(self, file_finder_window, mock_message_box):
        """Test saving search results with no results."""
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 0
        
        file_finder_window.save_search_results()
        
        mock_message_box.information.assert_called()
        call_args = mock_message_box.information.call_args[0]
        assert "No search results" in call_args[2]

    def test_save_search_results_success(self, file_finder_window, mock_file_dialog,
                                        mock_message_box, temp_directory):
        """Test successful search results saving."""
        # Setup mocks
        save_file = os.path.join(temp_directory, "results.txt")
        mock_file_dialog.getSaveFileName.return_value = (save_file, '')
        
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 2
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value = "*.txt"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.current_directory = temp_directory
        
        # Create mock items
        item1 = Mock()
        item1.text.return_value = "/path/file1.txt"
        item2 = Mock()
        item2.text.return_value = "/path/file2.txt"
        file_finder_window.results_list.item.side_effect = [item1, item2]
        
        file_finder_window.save_search_results()
        
        # Verify file was created
        assert os.path.exists(save_file)
        
        # Verify content
        with open(save_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        assert "File Finder Search Results" in content
        assert temp_directory in content
        assert "*.txt" in content
        assert "Total Results: 2" in content
        assert "/path/file1.txt" in content
        assert "/path/file2.txt" in content
        
        mock_message_box.information.assert_called()

    def test_save_search_results_file_error(self, file_finder_window,
                                           mock_file_dialog, mock_message_box):
        """Test search results saving with file error."""
        mock_file_dialog.getSaveFileName.return_value = ('/invalid/path.txt', '')
        
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 1
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value = "*.txt"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.current_directory = "/test"
        
        item = Mock()
        item.text.return_value = "/path/file.txt"
        file_finder_window.results_list.item.return_value = item
        
        file_finder_window.save_search_results()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "Failed to save results" in call_args[2]

    def test_save_search_results_cancelled(self, file_finder_window,
                                          mock_file_dialog, mock_message_box):
        """Test search results saving cancellation."""
        mock_file_dialog.getSaveFileName.return_value = ('', '')
        
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 1
        
        file_finder_window.save_search_results()
        
        # Should not show any message when cancelled
        mock_message_box.information.assert_not_called()
        mock_message_box.warning.assert_not_called()

    def test_export_search_results_no_results(self, file_finder_window, 
                                             mock_message_box):
        """Test exporting search results with no results."""
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 0
        
        file_finder_window.export_search_results()
        
        mock_message_box.information.assert_called()
        call_args = mock_message_box.information.call_args[0]
        assert "No search results" in call_args[2]

    def test_export_search_results_success(self, file_finder_window, mock_file_dialog,
                                          mock_message_box, temp_directory):
        """Test successful search results export to CSV."""
        # Setup mocks
        export_file = os.path.join(temp_directory, "results.csv")
        mock_file_dialog.getSaveFileName.return_value = (export_file, '')
        
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 1
        
        # Create mock item with existing file
        test_file = os.path.join(temp_directory, "document.txt")
        item = Mock()
        item.text.return_value = test_file
        file_finder_window.results_list.item.return_value = item
        
        file_finder_window.export_search_results()
        
        # Verify CSV file was created
        assert os.path.exists(export_file)
        
        # Verify CSV content
        with open(export_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        assert len(rows) >= 2  # Header + at least one data row
        assert rows[0] == ['File Path', 'File Name', 'Directory', 'Size', 'Modified']
        assert test_file in rows[1][0]
        assert "document.txt" in rows[1][1]
        
        mock_message_box.information.assert_called()

    def test_export_search_results_file_stat_error(self, file_finder_window,
                                                   mock_file_dialog, mock_message_box,
                                                   temp_directory):
        """Test export with file stat error handling."""
        # Setup mocks
        export_file = os.path.join(temp_directory, "results.csv")
        mock_file_dialog.getSaveFileName.return_value = (export_file, '')
        
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 1
        
        # Create mock item with nonexistent file
        item = Mock()
        item.text.return_value = "/nonexistent/file.txt"
        file_finder_window.results_list.item.return_value = item
        
        file_finder_window.export_search_results()
        
        # Verify CSV file was created
        assert os.path.exists(export_file)
        
        # Verify CSV content handles error gracefully
        with open(export_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        assert len(rows) >= 2  # Header + at least one data row
        assert "Unknown" in rows[1][3]  # Size should be "Unknown"
        assert "Unknown" in rows[1][4]  # Modified should be "Unknown"

    def test_export_search_results_write_error(self, file_finder_window,
                                              mock_file_dialog, mock_message_box):
        """Test export with file write error."""
        mock_file_dialog.getSaveFileName.return_value = ('/invalid/path.csv', '')
        
        file_finder_window.results_list = Mock()
        file_finder_window.results_list.count.return_value = 1
        
        item = Mock()
        item.text.return_value = "/path/file.txt"
        file_finder_window.results_list.item.return_value = item
        
        file_finder_window.export_search_results()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "Failed to export results" in call_args[2]

    def test_show_preferences(self, file_finder_window, mock_message_box):
        """Test preferences dialog display."""
        file_finder_window.show_preferences()
        
        mock_message_box.information.assert_called()
        call_args = mock_message_box.information.call_args[0]
        assert "File Finder Preferences" in call_args[1]
        assert "Default search patterns" in call_args[2]

    def test_refresh_view_with_directory(self, file_finder_window):
        """Test view refresh with selected directory."""
        file_finder_window.current_directory = "/test/path"
        file_finder_window.start_search = Mock()
        
        file_finder_window.refresh_view()
        
        file_finder_window.start_search.assert_called_once()

    def test_refresh_view_without_directory(self, file_finder_window, 
                                          mock_message_box):
        """Test view refresh without selected directory."""
        file_finder_window.current_directory = ""
        
        file_finder_window.refresh_view()
        
        mock_message_box.information.assert_called()
        call_args = mock_message_box.information.call_args[0]
        assert "Select a directory first" in call_args[2]


class TestMainFunction:
    """Test cases for main function and standalone execution."""

    @patch('src.tools.file_management.file_finder.QApplication')
    @patch('src.tools.file_management.file_finder.FileFinderGUI')
    @patch('src.tools.file_management.file_finder.sys.exit')
    def test_main_function_execution(self, mock_exit, mock_window_class, 
                                   mock_app_class):
        """Test main function execution flow."""
        from src.tools.file_management.file_finder import main
        
        mock_app = Mock()
        mock_app.exec_.return_value = 0
        mock_app_class.return_value = mock_app
        
        mock_window = Mock()
        mock_window_class.return_value = mock_window
        
        main()
        
        mock_app_class.assert_called_once()
        mock_window_class.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app.exec_.assert_called_once()
        mock_exit.assert_called_once_with(0)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_directory_search(self, file_finder_window):
        """Test search in empty directory."""
        with tempfile.TemporaryDirectory() as empty_dir:
            # Setup window controls
            file_finder_window.directory_edit = Mock()
            file_finder_window.directory_edit.text.return_value.strip.return_value = empty_dir
            file_finder_window.pattern_edit = Mock()
            file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.*"
            file_finder_window.recursive_check = Mock()
            file_finder_window.recursive_check.isChecked.return_value = True
            file_finder_window.results_list = Mock()
            file_finder_window.results_label = Mock()
            file_finder_window.clear_results = Mock()
            
            file_finder_window.start_search()
            
            file_finder_window.results_label.setText.assert_called_with(
                "No files found matching the criteria"
            )

    def test_search_with_special_characters_pattern(self, file_finder_window, 
                                                   temp_directory):
        """Test search with special characters in pattern."""
        # Create file with special characters
        special_file = os.path.join(temp_directory, "file[test].txt")
        with open(special_file, 'w') as f:
            f.write("test")
            
        # Setup window controls
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*[test]*"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = False
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Should handle special characters gracefully
        file_finder_window.results_list.addItem.assert_called()

    def test_search_with_unicode_filenames(self, file_finder_window):
        """Test search with Unicode filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with Unicode name
            unicode_file = os.path.join(temp_dir, "测试文件.txt")
            with open(unicode_file, 'w', encoding='utf-8') as f:
                f.write("Unicode test content")
                
            # Setup window controls
            file_finder_window.directory_edit = Mock()
            file_finder_window.directory_edit.text.return_value.strip.return_value = temp_dir
            file_finder_window.pattern_edit = Mock()
            file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.txt"
            file_finder_window.recursive_check = Mock()
            file_finder_window.recursive_check.isChecked.return_value = False
            file_finder_window.results_list = Mock()
            file_finder_window.results_label = Mock()
            file_finder_window.clear_results = Mock()
            
            file_finder_window.start_search()
            
            # Should find Unicode filename
            file_finder_window.results_list.addItem.assert_called()

    def test_search_permission_denied_directory(self, file_finder_window, 
                                               mock_message_box):
        """Test search in directory with permission issues."""
        # Setup window controls with inaccessible directory
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = "/root"
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.*"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        # Mock os.walk to raise PermissionError
        with patch('os.walk', side_effect=PermissionError("Access denied")):
            file_finder_window.start_search()
            
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "Search failed" in call_args[2]

    def test_file_size_formatting_large_file(self, file_finder_window, temp_directory):
        """Test file size formatting for large files."""
        file_finder_window.file_info_text = Mock()
        file_finder_window.open_button = Mock()
        file_finder_window.open_folder_button = Mock()
        
        test_file = os.path.join(temp_directory, "document.txt")
        
        # Mock large file stat
        with patch('os.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024 * 1024 * 1024 * 2  # 2GB
            mock_stat.return_value.st_mtime = 1693747200
            
            item = Mock()
            item.text.return_value = test_file
            
            file_finder_window.show_file_info(item)
            
            file_finder_window.file_info_text.setText.assert_called()
            call_args = file_finder_window.file_info_text.setText.call_args[0][0]
            assert "2.0 GB" in call_args

    def test_case_insensitive_pattern_matching(self, file_finder_window, 
                                              temp_directory):
        """Test case-insensitive pattern matching."""
        # Create files with mixed case
        mixed_case_file = os.path.join(temp_directory, "TestFile.TXT")
        with open(mixed_case_file, 'w') as f:
            f.write("test")
            
        # Setup window controls with lowercase pattern
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.txt"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = False
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Should find file despite case difference
        file_finder_window.results_list.addItem.assert_called()

    def test_deep_directory_structure_search(self, file_finder_window, temp_directory):
        """Test search in deeply nested directory structure."""
        # The temp_directory fixture already creates a deep structure
        # Setup window controls for recursive search
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "deep_file.txt"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Should find the deeply nested file
        file_finder_window.results_list.addItem.assert_called()

    def test_multiple_pattern_wildcards(self, file_finder_window, temp_directory):
        """Test search with multiple wildcards in pattern."""
        # Setup window controls with complex pattern
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = temp_directory
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*test*"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        file_finder_window.start_search()
        
        # Should find files matching the pattern
        file_finder_window.results_list.addItem.assert_called()

    def test_search_exception_handling(self, file_finder_window, mock_message_box):
        """Test search with general exception handling."""
        # Setup window controls
        file_finder_window.directory_edit = Mock()
        file_finder_window.directory_edit.text.return_value.strip.return_value = "/valid/path"
        file_finder_window.pattern_edit = Mock()
        file_finder_window.pattern_edit.text.return_value.strip.return_value = "*.*"
        file_finder_window.recursive_check = Mock()
        file_finder_window.recursive_check.isChecked.return_value = True
        file_finder_window.results_list = Mock()
        file_finder_window.results_label = Mock()
        file_finder_window.clear_results = Mock()
        
        # Mock os.path.exists to return True but os.walk to raise exception
        with patch('os.path.exists', return_value=True), \
             patch('os.walk', side_effect=Exception("General error")):
            file_finder_window.start_search()
            
        mock_message_box.warning.assert_called()
        file_finder_window.results_label.setText.assert_called_with("Search failed")