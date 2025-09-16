#!/usr/bin/env python3
"""
Comprehensive Unit Tests for catalog.py
Generated: 2025-08-24

This module provides comprehensive unit testing for the CatalogWindow class
and its associated functionality using pytest framework with mock testing.
"""

import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PyQt5.QtWidgets import QApplication

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    from src.tools.file_management.catalog import CatalogWindow
except ImportError as e:
    pytest.skip(f"Cannot import catalog module: {e}", allow_module_level=True)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app here as it might be used by other tests


@pytest.fixture
def catalog_window(qapp):
    """Create CatalogWindow instance for testing."""
    with patch('src.tools.file_management.catalog.StandardWindow'):
        window = CatalogWindow()
        yield window
        if hasattr(window, 'close'):
            window.close()


@pytest.fixture
def temp_directory():
    """Create temporary directory with test files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test files and subdirectories
    test_files = [
        'test_file1.txt',
        'test_file2.py',
        'hidden_file.hidden',
        '.hidden_dotfile'
    ]
    
    for filename in test_files:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Test content for {filename}")
    
    # Create subdirectory with files
    sub_dir = os.path.join(temp_dir, 'subdir')
    os.makedirs(sub_dir)
    
    sub_files = [
        'sub_file1.txt',
        'sub_file2.doc',
        '.hidden_sub_file'
    ]
    
    for filename in sub_files:
        file_path = os.path.join(sub_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Sub directory content for {filename}")
    
    yield temp_dir
    
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass


@pytest.fixture
def mock_file_dialog():
    """Mock file dialog responses."""
    with patch('src.tools.file_management.catalog.QFileDialog') as mock:
        yield mock


@pytest.fixture
def mock_message_box():
    """Mock message box responses."""
    with patch('src.tools.file_management.catalog.QMessageBox') as mock:
        yield mock


@pytest.fixture
def mock_webbrowser():
    """Mock webbrowser module."""
    with patch('src.tools.file_management.catalog.webbrowser') as mock:
        yield mock


class TestCatalogWindow:
    """Test cases for CatalogWindow class functionality."""

    def test_catalog_window_initialization(self, catalog_window):
        """Test CatalogWindow initialization and basic attributes."""
        assert hasattr(catalog_window, 'current_directory')
        assert hasattr(catalog_window, 'last_catalog_path')
        assert catalog_window.current_directory == ""
        assert catalog_window.last_catalog_path == ""

    def test_setup_menu_callbacks(self, catalog_window):
        """Test menu callback setup functionality."""
        # Mock menu_manager
        catalog_window.menu_manager = Mock()
        
        catalog_window._setup_menu_callbacks()
        
        # Verify callback registrations
        expected_callbacks = [
            ('new_catalog', 'clear_directory'),
            ('save_catalog', 'generate_catalog'),
            ('open_catalog', 'open_catalog'),
            ('export_catalog', 'export_catalog_settings'),
            ('show_user_guide', 'show_help'),
            ('show_preferences', 'show_preferences'),
            ('refresh', 'refresh_view')
        ]
        
        for callback_name, method_name in expected_callbacks:
            catalog_window.menu_manager.register_callback.assert_any_call(
                callback_name,
                getattr(catalog_window, method_name)
            )

    def test_clear_directory(self, catalog_window):
        """Test directory clearing functionality."""
        # Setup initial state
        catalog_window.current_directory = "/test/path"
        catalog_window.directory_edit = Mock()
        catalog_window.file_list = Mock()
        catalog_window.file_info_text = Mock()
        catalog_window.status_label = Mock()
        catalog_window.open_catalog_button = Mock()
        
        catalog_window.clear_directory()
        
        assert catalog_window.current_directory == ""
        catalog_window.directory_edit.clear.assert_called_once()
        catalog_window.file_list.clear.assert_called_once()
        catalog_window.file_info_text.clear.assert_called_once()
        catalog_window.status_label.setText.assert_called_with(
            "Select a directory to begin"
        )
        catalog_window.open_catalog_button.setEnabled.assert_called_with(False)

    def test_export_catalog_settings_success(self, catalog_window, 
                                           mock_file_dialog, mock_message_box,
                                           temp_directory):
        """Test successful catalog settings export."""
        # Setup mocks
        test_file = os.path.join(temp_directory, 'test_settings.json')
        mock_file_dialog.getSaveFileName.return_value = (test_file, '')
        
        # Setup window state
        catalog_window.current_directory = temp_directory
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = True
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = False
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = True
        
        catalog_window.export_catalog_settings()
        
        # Verify file was created
        assert os.path.exists(test_file)
        
        # Verify content
        with open(test_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
        expected_settings = {
            'directory': temp_directory,
            'recursive': True,
            'show_sizes': True,
            'show_dates': False,
            'show_hidden': True
        }
        
        assert settings == expected_settings
        mock_message_box.information.assert_called()

    def test_export_catalog_settings_failure(self, catalog_window,
                                            mock_file_dialog, mock_message_box):
        """Test catalog settings export failure handling."""
        # Setup mocks for failure scenario
        mock_file_dialog.getSaveFileName.return_value = ('', '')
        
        catalog_window.export_catalog_settings()
        
        # Should not show any message box if no file selected
        mock_message_box.information.assert_not_called()
        mock_message_box.warning.assert_not_called()

    def test_show_help(self, catalog_window, mock_message_box):
        """Test help dialog display."""
        catalog_window.show_help()
        
        mock_message_box.information.assert_called_once()
        call_args = mock_message_box.information.call_args
        assert "File Catalog Help" in call_args[0][1]
        assert "How to Create File Catalogs" in call_args[0][2]

    def test_show_preferences(self, catalog_window, mock_message_box):
        """Test preferences dialog display."""
        catalog_window.show_preferences()
        
        mock_message_box.information.assert_called_once()
        call_args = mock_message_box.information.call_args
        assert "Catalog Preferences" in call_args[0][1]
        assert "Default output formats" in call_args[0][2]

    def test_refresh_view_with_directory(self, catalog_window):
        """Test view refresh with selected directory."""
        catalog_window.current_directory = "/test/path"
        catalog_window.load_directory_preview = Mock()
        
        catalog_window.refresh_view()
        
        catalog_window.load_directory_preview.assert_called_once()

    def test_refresh_view_without_directory(self, catalog_window, 
                                          mock_message_box):
        """Test view refresh without selected directory."""
        catalog_window.current_directory = ""
        
        catalog_window.refresh_view()
        
        mock_message_box.information.assert_called_once()
        call_args = mock_message_box.information.call_args
        assert "Select a directory first" in call_args[0][2]

    def test_browse_directory(self, catalog_window, mock_file_dialog, 
                            temp_directory):
        """Test directory browsing functionality."""
        mock_file_dialog.getExistingDirectory.return_value = temp_directory
        catalog_window.directory_edit = Mock()
        catalog_window.load_directory_preview = Mock()
        
        catalog_window.browse_directory()
        
        assert catalog_window.current_directory == temp_directory
        catalog_window.directory_edit.setText.assert_called_with(temp_directory)
        catalog_window.load_directory_preview.assert_called_once()

    def test_browse_directory_cancelled(self, catalog_window, mock_file_dialog):
        """Test directory browsing cancellation."""
        mock_file_dialog.getExistingDirectory.return_value = ""
        catalog_window.directory_edit = Mock()
        catalog_window.load_directory_preview = Mock()
        original_directory = catalog_window.current_directory
        
        catalog_window.browse_directory()
        
        assert catalog_window.current_directory == original_directory
        catalog_window.directory_edit.setText.assert_not_called()
        catalog_window.load_directory_preview.assert_not_called()

    def test_load_directory_preview_success(self, catalog_window, temp_directory):
        """Test successful directory preview loading."""
        catalog_window.current_directory = temp_directory
        catalog_window.file_list = Mock()
        catalog_window.status_label = Mock()
        catalog_window._load_files_preview = Mock(return_value=5)
        catalog_window._update_status_after_load = Mock()
        
        catalog_window.load_directory_preview()
        
        catalog_window.file_list.clear.assert_called_once()
        catalog_window.status_label.setText.assert_called_with(
            f"Loading: {temp_directory}"
        )
        catalog_window._load_files_preview.assert_called_once()
        catalog_window._update_status_after_load.assert_called_with(5)

    def test_load_directory_preview_error(self, catalog_window, 
                                        mock_message_box):
        """Test directory preview loading error handling."""
        catalog_window.current_directory = "/nonexistent/path"
        catalog_window.file_list = Mock()
        catalog_window.status_label = Mock()
        catalog_window._load_files_preview = Mock(
            side_effect=Exception("Test error")
        )
        
        catalog_window.load_directory_preview()
        
        mock_message_box.warning.assert_called()
        catalog_window.status_label.setText.assert_called_with(
            "Error loading directory"
        )

    def test_load_files_preview_recursive(self, catalog_window):
        """Test files preview loading in recursive mode."""
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = True
        catalog_window._load_recursive_files = Mock(return_value=10)
        catalog_window._load_single_directory_files = Mock()
        
        result = catalog_window._load_files_preview()
        
        assert result == 10
        catalog_window._load_recursive_files.assert_called_once()
        catalog_window._load_single_directory_files.assert_not_called()

    def test_load_files_preview_non_recursive(self, catalog_window):
        """Test files preview loading in non-recursive mode."""
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = False
        catalog_window._load_recursive_files = Mock()
        catalog_window._load_single_directory_files = Mock(return_value=5)
        
        result = catalog_window._load_files_preview()
        
        assert result == 5
        catalog_window._load_recursive_files.assert_not_called()
        catalog_window._load_single_directory_files.assert_called_once()

    @patch('src.tools.file_management.catalog.QListWidgetItem')
    def test_load_recursive_files(self, mock_list_item, catalog_window, 
                                temp_directory):
        """Test recursive files loading."""
        catalog_window.current_directory = temp_directory
        catalog_window.file_list = Mock()
        catalog_window._should_skip_hidden_file = Mock(return_value=False)
        
        file_count = catalog_window._load_recursive_files()
        
        assert file_count > 0
        assert catalog_window.file_list.addItem.call_count == file_count

    @patch('src.tools.file_management.catalog.QListWidgetItem')
    def test_load_single_directory_files(self, mock_list_item, catalog_window,
                                       temp_directory):
        """Test single directory files loading."""
        catalog_window.current_directory = temp_directory
        catalog_window.file_list = Mock()
        catalog_window._should_skip_hidden_file = Mock(return_value=False)
        
        file_count = catalog_window._load_single_directory_files()
        
        assert file_count > 0
        assert catalog_window.file_list.addItem.call_count == file_count

    def test_should_skip_hidden_file_show_hidden(self, catalog_window):
        """Test hidden file skipping with show hidden enabled."""
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = True
        
        result = catalog_window._should_skip_hidden_file('.hidden_file')
        
        assert result is False

    def test_should_skip_hidden_file_hide_hidden(self, catalog_window):
        """Test hidden file skipping with show hidden disabled."""
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = False
        
        result = catalog_window._should_skip_hidden_file('.hidden_file')
        
        assert result is True

    def test_should_skip_hidden_file_normal_file(self, catalog_window):
        """Test hidden file skipping with normal file."""
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = False
        
        result = catalog_window._should_skip_hidden_file('normal_file.txt')
        
        assert result is False

    def test_update_status_after_load_under_limit(self, catalog_window):
        """Test status update with file count under limit."""
        catalog_window.status_label = Mock()
        
        catalog_window._update_status_after_load(50)
        
        catalog_window.status_label.setText.assert_called_with(
            "Ready: 50 files found"
        )

    def test_update_status_after_load_over_limit(self, catalog_window):
        """Test status update with file count over limit."""
        catalog_window.status_label = Mock()
        
        catalog_window._update_status_after_load(100)
        
        catalog_window.status_label.setText.assert_called_with(
            "Preview: 100+ files (showing first 100)"
        )

    def test_show_file_info_existing_file(self, catalog_window, temp_directory):
        """Test file info display for existing file."""
        catalog_window.current_directory = temp_directory
        catalog_window.file_info_text = Mock()
        
        # Create mock item
        item = Mock()
        item.text.return_value = "test_file1.txt"
        
        catalog_window.show_file_info(item)
        
        catalog_window.file_info_text.setText.assert_called()
        call_args = catalog_window.file_info_text.setText.call_args[0][0]
        assert "test_file1.txt" in call_args
        assert "Size:" in call_args
        assert "Modified:" in call_args

    def test_show_file_info_nonexistent_file(self, catalog_window):
        """Test file info display for nonexistent file."""
        catalog_window.current_directory = "/test/path"
        catalog_window.file_info_text = Mock()
        
        # Create mock item
        item = Mock()
        item.text.return_value = "nonexistent.txt"
        
        catalog_window.show_file_info(item)
        
        catalog_window.file_info_text.setText.assert_called()
        call_args = catalog_window.file_info_text.setText.call_args[0][0]
        assert "File not found" in call_args

    def test_generate_catalog_no_directory(self, catalog_window, mock_message_box):
        """Test catalog generation with no directory selected."""
        catalog_window.current_directory = ""
        
        catalog_window.generate_catalog()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "select a directory" in call_args[2].lower()

    def test_generate_catalog_nonexistent_directory(self, catalog_window,
                                                   mock_message_box):
        """Test catalog generation with nonexistent directory."""
        catalog_window.current_directory = "/nonexistent/path"
        
        catalog_window.generate_catalog()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "does not exist" in call_args[2].lower()

    @patch('src.tools.file_management.catalog.datetime')
    def test_generate_catalog_success(self, mock_datetime, catalog_window,
                                    temp_directory, mock_message_box):
        """Test successful catalog generation."""
        # Setup datetime mock
        mock_datetime.now.return_value.strftime.return_value = "20250824_120000"
        
        catalog_window.current_directory = temp_directory
        catalog_window.status_label = Mock()
        catalog_window.open_catalog_button = Mock()
        catalog_window.create_html_catalog = Mock(return_value="<html></html>")
        
        # Mock the message box to return "No"
        mock_message_box.question.return_value = mock_message_box.No
        
        catalog_window.generate_catalog()
        
        # Check that catalog was generated
        assert catalog_window.last_catalog_path != ""
        assert catalog_window.last_catalog_path.endswith('.html')
        catalog_window.open_catalog_button.setEnabled.assert_called_with(True)
        catalog_window.create_html_catalog.assert_called_once()

    def test_generate_catalog_with_open(self, catalog_window, temp_directory,
                                      mock_message_box):
        """Test catalog generation with immediate opening."""
        catalog_window.current_directory = temp_directory
        catalog_window.status_label = Mock()
        catalog_window.open_catalog_button = Mock()
        catalog_window.create_html_catalog = Mock(return_value="<html></html>")
        catalog_window.open_catalog = Mock()
        
        # Mock the message box to return "Yes"
        mock_message_box.question.return_value = mock_message_box.Yes
        
        catalog_window.generate_catalog()
        
        catalog_window.open_catalog.assert_called_once()

    @patch('src.tools.file_management.catalog.datetime')
    def test_create_html_catalog(self, mock_datetime, catalog_window):
        """Test HTML catalog creation."""
        # Setup datetime mock
        mock_datetime.now.return_value.strftime.return_value = "2025-08-24 12:00:00"
        
        catalog_window.current_directory = "/test/path"
        catalog_window._create_html_header = Mock(return_value="<header>")
        catalog_window._create_html_table_header = Mock(return_value="<table>")
        catalog_window._create_html_file_entries = Mock(return_value="<rows>")
        catalog_window._create_html_footer = Mock(return_value="</html>")
        
        result = catalog_window.create_html_catalog()
        
        expected = "<header><table><rows></html>"
        assert result == expected
        
        catalog_window._create_html_header.assert_called_once()
        catalog_window._create_html_table_header.assert_called_once()
        catalog_window._create_html_file_entries.assert_called_once()
        catalog_window._create_html_footer.assert_called_once()

    def test_create_html_header(self, catalog_window):
        """Test HTML header creation."""
        catalog_window.current_directory = "/test/MyProject"
        catalog_window._get_options_text = Mock(return_value="Recursive, Sizes")
        
        result = catalog_window._create_html_header("MyProject", "2025-08-24 12:00:00")
        
        assert "<title>File Catalog - MyProject</title>" in result
        assert "/test/MyProject" in result
        assert "2025-08-24 12:00:00" in result
        assert "Recursive, Sizes" in result

    def test_get_options_text_all_options(self, catalog_window):
        """Test options text generation with all options enabled."""
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = True
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = True
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = True
        
        result = catalog_window._get_options_text()
        
        expected_options = ["Recursive", "Sizes", "Dates", "Hidden files"]
        for option in expected_options:
            assert option in result

    def test_get_options_text_no_options(self, catalog_window):
        """Test options text generation with no options enabled."""
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = False
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = False
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = False
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = False
        
        result = catalog_window._get_options_text()
        
        assert result == "None"

    def test_create_html_table_header_all_columns(self, catalog_window):
        """Test HTML table header with all columns enabled."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = True
        
        result = catalog_window._create_html_table_header()
        
        assert "<th>File Name</th>" in result
        assert "<th>Size</th>" in result
        assert "<th>Modified</th>" in result

    def test_create_html_table_header_minimal_columns(self, catalog_window):
        """Test HTML table header with minimal columns."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = False
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = False
        
        result = catalog_window._create_html_table_header()
        
        assert "<th>File Name</th>" in result
        assert "<th>Size</th>" not in result
        assert "<th>Modified</th>" not in result

    def test_create_html_file_entries_recursive(self, catalog_window):
        """Test HTML file entries creation in recursive mode."""
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = True
        catalog_window._process_recursive_files = Mock(
            return_value=("<tr>recursive</tr>", 5)
        )
        catalog_window._process_single_directory_files = Mock()
        
        result = catalog_window._create_html_file_entries()
        
        assert result == "<tr>recursive</tr>"
        catalog_window._process_recursive_files.assert_called_once()
        catalog_window._process_single_directory_files.assert_not_called()

    def test_create_html_file_entries_non_recursive(self, catalog_window):
        """Test HTML file entries creation in non-recursive mode."""
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = False
        catalog_window._process_recursive_files = Mock()
        catalog_window._process_single_directory_files = Mock(
            return_value=("<tr>single</tr>", 3)
        )
        
        result = catalog_window._create_html_file_entries()
        
        assert result == "<tr>single</tr>"
        catalog_window._process_recursive_files.assert_not_called()
        catalog_window._process_single_directory_files.assert_called_once()

    def test_process_recursive_files(self, catalog_window, temp_directory):
        """Test recursive files processing."""
        catalog_window.current_directory = temp_directory
        catalog_window._should_skip_hidden_file = Mock(return_value=False)
        catalog_window.create_file_row = Mock(return_value="<tr>test</tr>")
        
        file_entries, file_count = catalog_window._process_recursive_files()
        
        assert file_count > 0
        assert "<tr>test</tr>" in file_entries
        assert catalog_window.create_file_row.call_count == file_count

    def test_process_single_directory_files(self, catalog_window, temp_directory):
        """Test single directory files processing."""
        catalog_window.current_directory = temp_directory
        catalog_window._should_skip_hidden_file = Mock(return_value=False)
        catalog_window.create_file_row = Mock(return_value="<tr>test</tr>")
        
        file_entries, file_count = catalog_window._process_single_directory_files()
        
        assert file_count > 0
        assert "<tr>test</tr>" in file_entries
        assert catalog_window.create_file_row.call_count == file_count

    def test_create_html_footer(self, catalog_window, temp_directory):
        """Test HTML footer creation."""
        catalog_window.current_directory = temp_directory
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = False
        catalog_window._should_skip_hidden_file = Mock(return_value=False)
        
        result = catalog_window._create_html_footer()
        
        assert "</tbody>" in result
        assert "</table>" in result
        assert "Total Files:" in result
        assert "</html>" in result

    def test_create_file_row_with_all_info(self, catalog_window, temp_directory):
        """Test file row creation with all information enabled."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = True
        
        test_file = os.path.join(temp_directory, "test_file1.txt")
        
        result = catalog_window.create_file_row(test_file, "test_file1.txt")
        
        assert "test_file1.txt" in result
        assert "B" in result or "KB" in result  # Size information
        assert "2025" in result  # Date information (current year)
        assert "<tr>" in result and "</tr>" in result

    def test_create_file_row_minimal_info(self, catalog_window, temp_directory):
        """Test file row creation with minimal information."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = False
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = False
        
        test_file = os.path.join(temp_directory, "test_file1.txt")
        
        result = catalog_window.create_file_row(test_file, "test_file1.txt")
        
        assert "test_file1.txt" in result
        assert "<tr>" in result and "</tr>" in result
        # Should only have file name column
        assert result.count("<td") == 1

    def test_create_file_row_error_handling(self, catalog_window):
        """Test file row creation error handling."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = True
        
        nonexistent_file = "/nonexistent/file.txt"
        
        result = catalog_window.create_file_row(nonexistent_file, "file.txt")
        
        assert "file.txt" in result
        assert "Error:" in result
        assert "<tr>" in result and "</tr>" in result

    def test_open_catalog_success(self, catalog_window, mock_webbrowser, 
                                temp_directory):
        """Test successful catalog opening."""
        catalog_path = os.path.join(temp_directory, "test_catalog.html")
        with open(catalog_path, 'w') as f:
            f.write("<html></html>")
            
        catalog_window.last_catalog_path = catalog_path
        
        catalog_window.open_catalog()
        
        mock_webbrowser.open.assert_called_once()
        call_args = mock_webbrowser.open.call_args[0][0]
        assert catalog_path in call_args

    def test_open_catalog_no_file(self, catalog_window, mock_message_box):
        """Test catalog opening with no file available."""
        catalog_window.last_catalog_path = ""
        
        catalog_window.open_catalog()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "No catalog file available" in call_args[2]

    def test_open_catalog_file_not_exists(self, catalog_window, mock_message_box):
        """Test catalog opening with non-existent file."""
        catalog_window.last_catalog_path = "/nonexistent/catalog.html"
        
        catalog_window.open_catalog()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "No catalog file available" in call_args[2]

    def test_open_catalog_webbrowser_error(self, catalog_window, mock_webbrowser,
                                         mock_message_box, temp_directory):
        """Test catalog opening with webbrowser error."""
        catalog_path = os.path.join(temp_directory, "test_catalog.html")
        with open(catalog_path, 'w') as f:
            f.write("<html></html>")
            
        catalog_window.last_catalog_path = catalog_path
        mock_webbrowser.open.side_effect = Exception("Browser error")
        
        catalog_window.open_catalog()
        
        mock_message_box.warning.assert_called()
        call_args = mock_message_box.warning.call_args[0]
        assert "Could not open catalog" in call_args[2]


class TestMainFunction:
    """Test cases for main function and standalone execution."""

    @patch('src.tools.file_management.catalog.QApplication')
    @patch('src.tools.file_management.catalog.CatalogWindow')
    @patch('src.tools.file_management.catalog.sys.exit')
    def test_main_function_execution(self, mock_exit, mock_window_class, 
                                   mock_app_class):
        """Test main function execution flow."""
        from src.tools.file_management.catalog import main
        
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

    def test_empty_directory_handling(self, catalog_window):
        """Test handling of empty directories."""
        with tempfile.TemporaryDirectory() as empty_dir:
            catalog_window.current_directory = empty_dir
            catalog_window.file_list = Mock()
            catalog_window._should_skip_hidden_file = Mock(return_value=False)
            
            file_count = catalog_window._load_single_directory_files()
            
            assert file_count == 0

    def test_very_large_file_size_formatting(self, catalog_window, temp_directory):
        """Test file size formatting for very large files."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = False
        
        # Create a test file and mock its stat to return large size
        test_file = os.path.join(temp_directory, "large_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
            
        with patch('os.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024 * 1024 * 1024 * 5  # 5GB
            mock_stat.return_value.st_mtime = 1693747200  # Mock timestamp
            
            result = catalog_window.create_file_row(test_file, "large_file.txt")
            
            assert "GB" in result
            assert "5.0 GB" in result

    def test_unicode_filename_handling(self, catalog_window):
        """Test handling of Unicode filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with Unicode name
            unicode_name = "测试文件_éñáme.txt"
            unicode_file = os.path.join(temp_dir, unicode_name)
            with open(unicode_file, 'w', encoding='utf-8') as f:
                f.write("Unicode test content")
                
            catalog_window.current_directory = temp_dir
            catalog_window.show_sizes_check = Mock()
            catalog_window.show_sizes_check.isChecked.return_value = False
            catalog_window.show_dates_check = Mock()
            catalog_window.show_dates_check.isChecked.return_value = False
            
            result = catalog_window.create_file_row(unicode_file, unicode_name)
            
            assert unicode_name in result

    def test_permission_denied_file_access(self, catalog_window):
        """Test handling of permission denied errors."""
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = True
        
        with patch('os.stat', side_effect=PermissionError("Access denied")):
            result = catalog_window.create_file_row("/restricted/file.txt", 
                                                  "file.txt")
            
            assert "Error:" in result
            assert "file.txt" in result

    def test_file_info_display_large_file(self, catalog_window, temp_directory):
        """Test file info display for large files."""
        catalog_window.current_directory = temp_directory
        catalog_window.file_info_text = Mock()
        
        # Mock large file stat
        with patch('os.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024 * 1024 * 10  # 10MB
            mock_stat.return_value.st_mtime = 1693747200
            
            item = Mock()
            item.text.return_value = "test_file1.txt"
            
            catalog_window.show_file_info(item)
            
            catalog_window.file_info_text.setText.assert_called()
            call_args = catalog_window.file_info_text.setText.call_args[0][0]
            assert "10.0 MB" in call_args

    def test_recursive_loading_with_limit(self, catalog_window):
        """Test recursive file loading with 100-file limit."""
        catalog_window.file_list = Mock()
        catalog_window._should_skip_hidden_file = Mock(return_value=False)
        
        # Create a large temporary directory structure
        with tempfile.TemporaryDirectory() as large_dir:
            # Create more than 100 files
            for i in range(150):
                file_path = os.path.join(large_dir, f"file_{i:03d}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Content {i}")
                    
            catalog_window.current_directory = large_dir
            
            file_count = catalog_window._load_recursive_files()
            
            # Should be limited to 100 files
            assert file_count == 100

    def test_export_settings_json_error(self, catalog_window, mock_file_dialog,
                                      mock_message_box):
        """Test export settings with JSON encoding error."""
        mock_file_dialog.getSaveFileName.return_value = ('/test/path.json', '')
        
        # Setup window state with problematic data
        catalog_window.current_directory = "/test/path"
        catalog_window.recursive_check = Mock()
        catalog_window.recursive_check.isChecked.return_value = True
        catalog_window.show_sizes_check = Mock()
        catalog_window.show_sizes_check.isChecked.return_value = True
        catalog_window.show_dates_check = Mock()
        catalog_window.show_dates_check.isChecked.return_value = True
        catalog_window.show_hidden_check = Mock()
        catalog_window.show_hidden_check.isChecked.return_value = True
        
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            catalog_window.export_catalog_settings()
            
            mock_message_box.warning.assert_called()
            call_args = mock_message_box.warning.call_args[0]
            assert "Failed to export settings" in call_args[2]

    def test_catalog_generation_write_error(self, catalog_window, temp_directory,
                                          mock_message_box):
        """Test catalog generation with file write error."""
        catalog_window.current_directory = temp_directory
        catalog_window.status_label = Mock()
        catalog_window.create_html_catalog = Mock(return_value="<html></html>")
        
        with patch('builtins.open', side_effect=PermissionError("Write denied")):
            catalog_window.generate_catalog()
            
            mock_message_box.warning.assert_called()
            call_args = mock_message_box.warning.call_args[0]
            assert "Failed to generate catalog" in call_args[2]
            
            catalog_window.status_label.setText.assert_called_with(
                "Catalog generation failed"
            )
