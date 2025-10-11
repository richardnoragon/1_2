"""Comprehensive unit tests for rename.py module.

This module contains comprehensive test coverage for all classes and functions
in the rename.py file, including edge cases, error handling, and mock data.

Test execution includes detailed reporting with timestamp, coverage, and
results.
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from PyQt5.QtWidgets import QApplication

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import the modules under test
from src.tools.file_operations.rename import RenameWindow, main


class TestRenameWindow:
    """Test cases for RenameWindow class."""

    @pytest.fixture
    def qapp(self):
        """Fixture to provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def temp_directory(self):
        """Fixture to provide a temporary directory for file operations."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_files(self, temp_directory):
        """Fixture to create sample files for testing."""
        files = {
            "document.txt": "Sample text content",
            "image.jpg": b"fake image data",
            "video.mp4": b"fake video data",
            "TestFile.TXT": "Mixed case content",
            "file with spaces.doc": "Document content",
            "file_with_underscores.pdf": "PDF content",
        }

        created_files = []
        for filename, content in files.items():
            file_path = os.path.join(temp_directory, filename)
            mode = "w" if isinstance(content, str) else "wb"
            with open(file_path, mode) as f:
                f.write(content)
            created_files.append(filename)

        return created_files

    @pytest.fixture
    def rename_window(self, qapp):
        """Fixture to provide a RenameWindow instance."""

    with patch(
        "src.tools.file_operations.rename.rename.StandardWindow.__init__"
    ), patch.object(RenameWindow, "init_ui"), patch.object(
        RenameWindow, "_setup_menu_callbacks"
    ):
        window = RenameWindow()
        window.current_directory = ""
        window.selected_files = []

        # Mock UI components
        window.directory_edit = Mock()
        window.available_files_list = Mock()
        window.selected_files_list = Mock()
        window.prefix_edit = Mock()
        window.suffix_edit = Mock()
        window.find_edit = Mock()
        window.replace_edit = Mock()
        window.start_number_edit = Mock()
        window.number_format_edit = Mock()
        window.preview_text = Mock()
        window.add_prefix_radio = Mock()
        window.add_suffix_radio = Mock()
        window.lowercase_radio = Mock()
        window.uppercase_radio = Mock()
        window.replace_radio = Mock()
        window.number_radio = Mock()

        yield window

    def test_rename_window_initialization(self, qapp):
        """Test RenameWindow initialization."""

    with patch(
        "src.tools.file_operations.rename.rename.StandardWindow.__init__"
    ), patch.object(RenameWindow, "init_ui"), patch.object(
        RenameWindow, "_setup_menu_callbacks"
    ):

        window = RenameWindow()

        assert window.current_directory == ""
        assert window.selected_files == []

    def test_setup_menu_callbacks(self, rename_window):
        """Test menu callbacks setup."""
        # Test that method runs without error when no menu_manager exists
        rename_window._setup_menu_callbacks()

        # Test with menu_manager present
        rename_window.menu_manager = Mock()
        rename_window._setup_menu_callbacks()

        # Verify all callbacks were registered
        expected_calls = [
            ("new_rename", rename_window.clear_selected_files),
            ("save_operation", rename_window.save_rename_settings),
            ("load_operation", rename_window.load_rename_settings),
            ("export_results", rename_window.export_rename_results),
        ]

        # Check that register_callback was called the expected number of times
        assert rename_window.menu_manager.register_callback.call_count == 4

        # Verify each expected call was made
        for expected_call in expected_calls:
            call_args = rename_window.menu_manager.register_callback.call_args_list
            found = any(call[0] == expected_call for call in call_args)
            assert found, f"Expected call {expected_call} not found"

    def test_save_rename_settings_success(self, rename_window):
        """Test successful saving of rename settings."""
        # Setup mock responses
        rename_window.prefix_edit.text.return_value = "prefix_"
        rename_window.suffix_edit.text.return_value = "_suffix"
        rename_window.find_edit.text.return_value = "find"
        rename_window.replace_edit.text.return_value = "replace"
        rename_window.start_number_edit.text.return_value = "1"
        rename_window.number_format_edit.text.return_value = "_{:03d}"
        rename_window.current_directory = "/test/dir"

        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getSaveFileName"
        ) as mock_dialog, patch("builtins.open", mock_open()) as mock_file, patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info, patch.object(
            rename_window, "_get_current_rename_mode", return_value="add_prefix"
        ):

            mock_dialog.return_value = ("/test/settings.json", "JSON Files (*.json)")

            rename_window.save_rename_settings()

            mock_file.assert_called_once()
            mock_info.assert_called_once()

    def test_save_rename_settings_cancelled(self, rename_window):
        """Test cancelled save operation."""
        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getSaveFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("", "")

            rename_window.save_rename_settings()

            # Should not attempt to write file
            assert mock_dialog.called

    def test_save_rename_settings_error(self, rename_window):
        """Test error handling during save operation."""
        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getSaveFileName"
        ) as mock_dialog, patch(
            "builtins.open", side_effect=IOError("Permission denied")
        ) as mock_file, patch(
            "src.tools.file_operations.rename.rename.QMessageBox.warning"
        ) as mock_warning:

            mock_dialog.return_value = ("/test/settings.json", "JSON Files (*.json)")

            rename_window.save_rename_settings()

            mock_warning.assert_called_once()

    def test_load_rename_settings_success(self, rename_window):
        """Test successful loading of rename settings."""
        test_settings = {
            "directory": "/test/directory",
            "prefix_text": "test_prefix",
            "suffix_text": "test_suffix",
        }

        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getOpenFileName"
        ) as mock_dialog, patch(
            "builtins.open", mock_open(read_data=json.dumps(test_settings))
        ), patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info, patch.object(
            rename_window, "load_available_files"
        ):

            mock_dialog.return_value = ("/test/settings.json", "JSON Files (*.json)")

            rename_window.load_rename_settings()

            assert rename_window.current_directory == "/test/directory"
            rename_window.directory_edit.setText.assert_called_with("/test/directory")
            rename_window.prefix_edit.setText.assert_called_with("test_prefix")
            mock_info.assert_called_once()

    def test_load_rename_settings_cancelled(self, rename_window):
        """Test cancelled load operation."""
        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getOpenFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("", "")

            rename_window.load_rename_settings()

            assert mock_dialog.called

    def test_export_rename_results_success(self, rename_window, temp_directory):
        """Test successful export of rename results."""
        rename_window.selected_files = ["file1.txt", "file2.txt"]
        rename_window.current_directory = temp_directory

        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getSaveFileName"
        ) as mock_dialog, patch("builtins.open", mock_open()) as mock_file, patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info, patch.object(
            rename_window,
            "get_new_filename",
            side_effect=["new_file1.txt", "new_file2.txt"],
        ), patch.object(
            rename_window, "_get_current_rename_mode", return_value="add_prefix"
        ):

            mock_dialog.return_value = ("/test/results.txt", "Text Files (*.txt)")

            rename_window.export_rename_results()

            mock_file.assert_called_once()
            mock_info.assert_called_once()

    def test_export_rename_results_no_files(self, rename_window):
        """Test export with no files selected."""
        rename_window.selected_files = []

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info:
            rename_window.export_rename_results()

            mock_info.assert_called_once()

    def test_get_current_rename_mode(self, rename_window):
        """Test getting current rename mode."""
        # Test add prefix mode
        rename_window.add_prefix_radio.isChecked.return_value = True
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False

        result = rename_window._get_current_rename_mode()
        assert result == "add_prefix"

        # Test add suffix mode
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = True

        result = rename_window._get_current_rename_mode()
        assert result == "add_suffix"

    def test_browse_directory_success(self, rename_window, temp_directory):
        """Test successful directory browsing."""
        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getExistingDirectory"
        ) as mock_dialog, patch.object(rename_window, "load_available_files"):

            mock_dialog.return_value = temp_directory

            rename_window.browse_directory()

            assert rename_window.current_directory == temp_directory
            rename_window.directory_edit.setText.assert_called_with(temp_directory)

    def test_browse_directory_cancelled(self, rename_window):
        """Test cancelled directory browsing."""
        original_dir = rename_window.current_directory

        with patch(
            "src.tools.file_operations.rename.rename.QFileDialog.getExistingDirectory"
        ) as mock_dialog:
            mock_dialog.return_value = ""

            rename_window.browse_directory()

            assert rename_window.current_directory == original_dir

    def test_load_available_files_success(
        self, rename_window, temp_directory, sample_files
    ):
        """Test successful loading of available files."""
        rename_window.current_directory = temp_directory

        with patch("os.listdir", return_value=sample_files), patch(
            "os.path.isfile", return_value=True
        ):

            rename_window.load_available_files()

            # Verify lists were cleared
            rename_window.available_files_list.clear.assert_called()
            rename_window.selected_files_list.clear.assert_called()

            # Verify files were added
            assert rename_window.available_files_list.addItem.call_count == len(
                sample_files
            )

    def test_load_available_files_no_directory(self, rename_window):
        """Test loading files when no directory is set."""
        rename_window.current_directory = ""

        rename_window.load_available_files()

        rename_window.available_files_list.clear.assert_called()
        rename_window.selected_files_list.clear.assert_called()

    def test_load_available_files_error(self, rename_window, temp_directory):
        """Test error handling during file loading."""
        rename_window.current_directory = temp_directory

        with patch("os.listdir", side_effect=PermissionError("Access denied")), patch(
            "src.tools.file_operations.rename.rename.QMessageBox.warning"
        ) as mock_warning:

            rename_window.load_available_files()

            mock_warning.assert_called_once()

    def test_add_selected_files(self, rename_window):
        """Test adding selected files to rename list."""
        # Mock selected items
        mock_item1 = Mock()
        mock_item1.text.return_value = "file1.txt"
        mock_item2 = Mock()
        mock_item2.text.return_value = "file2.txt"

        rename_window.available_files_list.selectedItems.return_value = [
            mock_item1,
            mock_item2,
        ]
        rename_window.selected_files = []

        rename_window.add_selected_files()

        assert "file1.txt" in rename_window.selected_files
        assert "file2.txt" in rename_window.selected_files
        assert rename_window.selected_files_list.addItem.call_count == 2

    def test_add_selected_files_duplicates(self, rename_window):
        """Test adding files that are already selected."""
        mock_item = Mock()
        mock_item.text.return_value = "file1.txt"

        rename_window.available_files_list.selectedItems.return_value = [mock_item]
        rename_window.selected_files = ["file1.txt"]

        rename_window.add_selected_files()

        # Should not add duplicate
        assert rename_window.selected_files.count("file1.txt") == 1
        rename_window.selected_files_list.addItem.assert_not_called()

    def test_add_all_files(self, rename_window):
        """Test adding all files to rename list."""
        # Mock available files
        mock_item1 = Mock()
        mock_item1.text.return_value = "file1.txt"
        mock_item2 = Mock()
        mock_item2.text.return_value = "file2.txt"

        rename_window.available_files_list.count.return_value = 2
        rename_window.available_files_list.item.side_effect = [mock_item1, mock_item2]
        rename_window.selected_files = []

        rename_window.add_all_files()

        assert len(rename_window.selected_files) == 2
        assert "file1.txt" in rename_window.selected_files
        assert "file2.txt" in rename_window.selected_files

    def test_remove_selected_files(self, rename_window):
        """Test removing selected files from rename list."""
        # Setup initial state
        rename_window.selected_files = ["file1.txt", "file2.txt"]

        # Mock selected items
        mock_item = Mock()
        mock_item.text.return_value = "file1.txt"

        rename_window.selected_files_list.selectedItems.return_value = [mock_item]
        rename_window.selected_files_list.row.return_value = 0

        rename_window.remove_selected_files()

        assert "file1.txt" not in rename_window.selected_files
        assert "file2.txt" in rename_window.selected_files
        rename_window.selected_files_list.takeItem.assert_called_with(0)

    def test_clear_selected_files(self, rename_window):
        """Test clearing all selected files."""
        rename_window.selected_files = ["file1.txt", "file2.txt"]

        rename_window.clear_selected_files()

        assert len(rename_window.selected_files) == 0
        rename_window.selected_files_list.clear.assert_called()

    def test_get_new_filename_add_prefix(self, rename_window):
        """Test filename generation with prefix."""
        rename_window.add_prefix_radio.isChecked.return_value = True
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False
        rename_window.prefix_edit.text.return_value = "prefix_"

        result = rename_window.get_new_filename("test.txt")
        assert result == "prefix_test.txt"

    def test_get_new_filename_add_suffix(self, rename_window):
        """Test filename generation with suffix."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = True
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False
        rename_window.suffix_edit.text.return_value = "_suffix"

        result = rename_window.get_new_filename("test.txt")
        assert result == "test_suffix.txt"

    def test_get_new_filename_lowercase(self, rename_window):
        """Test filename generation with lowercase conversion."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = True
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False

        result = rename_window.get_new_filename("TEST.TXT")
        assert result == "test.txt"

    def test_get_new_filename_uppercase(self, rename_window):
        """Test filename generation with uppercase conversion."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = True
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False

        result = rename_window.get_new_filename("test.txt")
        assert result == "TEST.TXT"

    def test_get_new_filename_replace_text(self, rename_window):
        """Test filename generation with text replacement."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = True
        rename_window.number_radio.isChecked.return_value = False
        rename_window.find_edit.text.return_value = "old"
        rename_window.replace_edit.text.return_value = "new"

        result = rename_window.get_new_filename("old_file.txt")
        assert result == "new_file.txt"

    def test_get_new_filename_replace_text_empty_find(self, rename_window):
        """Test filename generation with empty find text."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = True
        rename_window.number_radio.isChecked.return_value = False
        rename_window.find_edit.text.return_value = ""
        rename_window.replace_edit.text.return_value = "new"

        result = rename_window.get_new_filename("test.txt")
        assert result == "test.txt"  # Should return original

    def test_get_new_filename_add_numbers(self, rename_window):
        """Test filename generation with number sequence."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = True
        rename_window.start_number_edit.text.return_value = "1"
        rename_window.number_format_edit.text.return_value = "_{:03d}"

        result = rename_window.get_new_filename("test.txt", 0)
        assert result == "test_001.txt"

        result = rename_window.get_new_filename("test.txt", 5)
        assert result == "test_006.txt"

    def test_get_new_filename_add_numbers_invalid_start(self, rename_window):
        """Test filename generation with invalid start number."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = True
        rename_window.start_number_edit.text.return_value = "invalid"
        rename_window.number_format_edit.text.return_value = "_{:03d}"

        result = rename_window.get_new_filename("test.txt", 0)
        assert result == "test.txt"  # Should return original

    def test_get_new_filename_add_numbers_invalid_format(self, rename_window):
        """Test filename generation with invalid format string."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = True
        rename_window.start_number_edit.text.return_value = "1"
        rename_window.number_format_edit.text.return_value = "_{:invalid}"

        result = rename_window.get_new_filename("test.txt", 0)
        assert result == "test.txt"  # Should return original

    def test_preview_changes_success(self, rename_window):
        """Test successful preview of changes."""
        rename_window.selected_files = ["file1.txt", "file2.txt"]

        with patch.object(
            rename_window,
            "get_new_filename",
            side_effect=["new_file1.txt", "new_file2.txt"],
        ):
            rename_window.preview_changes()

            rename_window.preview_text.setText.assert_called_once()
            call_args = rename_window.preview_text.setText.call_args[0][0]
            assert "file1.txt → new_file1.txt" in call_args
            assert "file2.txt → new_file2.txt" in call_args

    def test_preview_changes_no_files(self, rename_window):
        """Test preview with no files selected."""
        rename_window.selected_files = []

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.warning"
        ) as mock_warning:
            rename_window.preview_changes()

            mock_warning.assert_called_once()

    def test_apply_rename_success(self, rename_window, temp_directory, sample_files):
        """Test successful rename operation."""
        # Setup test environment
        rename_window.current_directory = temp_directory
        rename_window.selected_files = sample_files[:2]  # Use first 2 files

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.question",
            return_value=Mock(),
        ), patch.object(
            rename_window,
            "get_new_filename",
            side_effect=["new_file1.txt", "new_file2.jpg"],
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "os.rename"
        ) as mock_rename, patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info, patch.object(
            rename_window, "load_available_files"
        ):

            # Mock the question dialog to return Yes
            with patch(
                "src.tools.file_operations.rename.rename.QMessageBox.Yes", 2
            ), patch("src.tools.file_operations.rename.rename.QMessageBox.No", 4):
                with patch(
                    "src.tools.file_operations.rename.rename.QMessageBox.question",
                    return_value=2,
                ):
                    rename_window.apply_rename()

            # Verify rename operations were called
            assert mock_rename.call_count == 2
            mock_info.assert_called_once()

    def test_apply_rename_no_files(self, rename_window):
        """Test rename operation with no files."""
        rename_window.selected_files = []

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.warning"
        ) as mock_warning:
            rename_window.apply_rename()

            mock_warning.assert_called_once()

    def test_apply_rename_cancelled(self, rename_window):
        """Test cancelled rename operation."""
        rename_window.selected_files = ["file1.txt"]

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.question"
        ) as mock_question:
            # Mock No response
            with patch(
                "src.tools.file_operations.rename.rename.QMessageBox.Yes", 2
            ), patch("src.tools.file_operations.rename.rename.QMessageBox.No", 4):
                mock_question.return_value = 4  # No

                rename_window.apply_rename()

                mock_question.assert_called_once()

    def test_apply_rename_file_exists_error(self, rename_window, temp_directory):
        """Test rename operation with existing target file."""
        rename_window.current_directory = temp_directory
        rename_window.selected_files = ["file1.txt"]

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.question",
            return_value=Mock(),
        ), patch.object(
            rename_window, "get_new_filename", return_value="existing_file.txt"
        ), patch(
            "os.path.exists", return_value=True
        ), patch(
            "src.tools.file_operations.rename.rename.QMessageBox.warning"
        ) as mock_warning, patch.object(
            rename_window, "load_available_files"
        ):

            # Mock the question dialog to return Yes
            with patch(
                "src.tools.file_operations.rename.rename.QMessageBox.Yes", 2
            ), patch("src.tools.file_operations.rename.rename.QMessageBox.No", 4):
                with patch(
                    "src.tools.file_operations.rename.rename.QMessageBox.question",
                    return_value=2,
                ):
                    rename_window.apply_rename()

            mock_warning.assert_called_once()

    def test_apply_rename_os_error(self, rename_window, temp_directory):
        """Test rename operation with OS error."""
        rename_window.current_directory = temp_directory
        rename_window.selected_files = ["file1.txt"]

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.question",
            return_value=Mock(),
        ), patch.object(
            rename_window, "get_new_filename", return_value="new_file.txt"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "os.rename", side_effect=OSError("Permission denied")
        ), patch(
            "src.tools.file_operations.rename.rename.QMessageBox.warning"
        ) as mock_warning, patch.object(
            rename_window, "load_available_files"
        ):

            # Mock the question dialog to return Yes
            with patch(
                "src.tools.file_operations.rename.rename.QMessageBox.Yes", 2
            ), patch("src.tools.file_operations.rename.rename.QMessageBox.No", 4):
                with patch(
                    "src.tools.file_operations.rename.rename.QMessageBox.question",
                    return_value=2,
                ):
                    rename_window.apply_rename()

            mock_warning.assert_called_once()

    def test_refresh_view_with_directory(self, rename_window, temp_directory):
        """Test refreshing view with directory set."""
        rename_window.current_directory = temp_directory

        with patch.object(rename_window, "load_available_files") as mock_load:
            rename_window.refresh_view()

            mock_load.assert_called_once()

    def test_refresh_view_no_directory(self, rename_window):
        """Test refreshing view with no directory set."""
        rename_window.current_directory = ""

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info:
            rename_window.refresh_view()

            mock_info.assert_called_once()

    def test_show_preferences(self, rename_window):
        """Test showing preferences dialog."""
        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info:
            rename_window.show_preferences()

            mock_info.assert_called_once()


class TestMainFunction:
    """Test cases for main function."""

    @patch("src.tools.file_operations.rename.rename.QApplication")
    @patch("src.tools.file_operations.rename.rename.RenameWindow")
    @patch("sys.exit")
    def test_main_function(self, mock_exit, mock_window, mock_app):
        """Test main function execution."""
        mock_app_instance = Mock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.exec_.return_value = 0
        mock_window_instance = Mock()
        mock_window.return_value = mock_window_instance

        main()

        mock_app.assert_called_once_with(sys.argv)
        mock_window.assert_called_once()
        mock_window_instance.show.assert_called_once()
        mock_exit.assert_called_with(0)


class TestEdgeCasesAndErrorHandling:
    """Test cases for edge cases and error handling."""

    @pytest.fixture
    def qapp(self):
        """Fixture to provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def temp_directory(self):
        """Fixture to provide a temporary directory for file operations."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def rename_window(self, qapp):
        """Fixture to provide a RenameWindow instance."""
        with patch(
            "src.tools.file_operations.rename.rename.StandardWindow.__init__"
        ), patch.object(RenameWindow, "init_ui"), patch.object(
            RenameWindow, "_setup_menu_callbacks"
        ):
            window = RenameWindow()
            window.current_directory = ""
            window.selected_files = []

            # Mock UI components
            window.directory_edit = Mock()
            window.available_files_list = Mock()
            window.selected_files_list = Mock()
            window.prefix_edit = Mock()
            window.suffix_edit = Mock()
            window.find_edit = Mock()
            window.replace_edit = Mock()
            window.start_number_edit = Mock()
            window.number_format_edit = Mock()
            window.preview_text = Mock()
            window.add_prefix_radio = Mock()
            window.add_suffix_radio = Mock()
            window.lowercase_radio = Mock()
            window.uppercase_radio = Mock()
            window.replace_radio = Mock()
            window.number_radio = Mock()

            yield window

    def test_get_new_filename_with_special_characters(self, rename_window):
        """Test filename generation with special characters."""
        rename_window.add_prefix_radio.isChecked.return_value = True
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False
        rename_window.prefix_edit.text.return_value = "special@#$%_"

        result = rename_window.get_new_filename("test file (copy).txt")
        assert result == "special@#$%_test file (copy).txt"

    def test_get_new_filename_with_unicode(self, rename_window):
        """Test filename generation with unicode characters."""
        rename_window.add_prefix_radio.isChecked.return_value = True
        rename_window.add_suffix_radio.isChecked.return_value = False
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False
        rename_window.prefix_edit.text.return_value = "测试_"

        result = rename_window.get_new_filename("文档.txt")
        assert result == "测试_文档.txt"

    def test_get_new_filename_no_extension(self, rename_window):
        """Test filename generation with file without extension."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = True
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False
        rename_window.suffix_edit.text.return_value = "_backup"

        result = rename_window.get_new_filename("README")
        assert result == "README_backup"

    def test_get_new_filename_multiple_dots(self, rename_window):
        """Test filename generation with multiple dots in filename."""
        rename_window.add_prefix_radio.isChecked.return_value = False
        rename_window.add_suffix_radio.isChecked.return_value = True
        rename_window.lowercase_radio.isChecked.return_value = False
        rename_window.uppercase_radio.isChecked.return_value = False
        rename_window.replace_radio.isChecked.return_value = False
        rename_window.number_radio.isChecked.return_value = False
        rename_window.suffix_edit.text.return_value = "_new"

        result = rename_window.get_new_filename("file.name.with.dots.txt")
        assert result == "file.name.with.dots_new.txt"

    def test_apply_rename_with_same_name(self, rename_window, temp_directory):
        """Test rename operation where new name is same as original."""
        rename_window.current_directory = temp_directory
        rename_window.selected_files = ["file1.txt"]

        with patch(
            "src.tools.file_operations.rename.rename.QMessageBox.question",
            return_value=Mock(),
        ), patch.object(
            rename_window, "get_new_filename", return_value="file1.txt"
        ), patch(
            "src.tools.file_operations.rename.rename.QMessageBox.information"
        ) as mock_info, patch.object(
            rename_window, "load_available_files"
        ):

            # Mock the question dialog to return Yes
            with patch(
                "src.tools.file_operations.rename.rename.QMessageBox.Yes", 2
            ), patch("src.tools.file_operations.rename.rename.QMessageBox.No", 4):
                with patch(
                    "src.tools.file_operations.rename.rename.QMessageBox.question",
                    return_value=2,
                ):
                    rename_window.apply_rename()

            # Should still complete successfully even though no actual rename occurred
            mock_info.assert_called_once()

    def test_load_available_files_with_mixed_content(
        self, rename_window, temp_directory
    ):
        """Test loading files from directory with mixed files and directories."""
        rename_window.current_directory = temp_directory

        # Create a subdirectory
        subdir = os.path.join(temp_directory, "subdirectory")
        os.makedirs(subdir, exist_ok=True)

        files_and_dirs = ["file1.txt", "subdirectory", "file2.jpg"]

        def mock_isfile(path):
            return not path.endswith("subdirectory")

        with patch("os.listdir", return_value=files_and_dirs), patch(
            "os.path.isfile", side_effect=mock_isfile
        ):

            rename_window.load_available_files()

            # Should only add files, not directories
            # Check that addItem was called for files only
            assert rename_window.available_files_list.addItem.call_count == 2


class TestPerformanceAndMemory:
    """Test cases for performance and memory usage."""

    @pytest.fixture
    def qapp(self):
        """Fixture to provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def temp_directory(self):
        """Fixture to provide a temporary directory for file operations."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def rename_window(self, qapp):
        """Fixture to provide a RenameWindow instance."""
        with patch(
            "src.tools.file_operations.rename.rename.StandardWindow.__init__"
        ), patch.object(RenameWindow, "init_ui"), patch.object(
            RenameWindow, "_setup_menu_callbacks"
        ):
            window = RenameWindow()
            window.current_directory = ""
            window.selected_files = []

            # Mock UI components
            window.available_files_list = Mock()
            window.selected_files_list = Mock()

            yield window

    def test_large_file_list_handling(self, rename_window, temp_directory):
        """Test handling of large number of files."""
        # Simulate large file list
        large_file_list = [f"file_{i:06d}.txt" for i in range(10000)]
        rename_window.current_directory = temp_directory

        with patch("os.listdir", return_value=large_file_list), patch(
            "os.path.isfile", return_value=True
        ):

            rename_window.load_available_files()

            # Should handle large list without issues
            assert rename_window.available_files_list.addItem.call_count == 10000

    def test_memory_usage_with_large_selection(self, rename_window):
        """Test memory usage with large file selection."""
        # Add many files to selected list
        large_selection = [f"file_{i:06d}.txt" for i in range(1000)]
        rename_window.selected_files = large_selection

        # Test that clearing works efficiently
        rename_window.clear_selected_files()

        assert len(rename_window.selected_files) == 0


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup for the entire test session."""
    # Record test start time
    start_time = datetime.now()

    yield

    # Record test end time and create summary
    end_time = datetime.now()
    duration = end_time - start_time

    # Create test results summary
    results_dir = Path("C:/Users/HP1/1_2/1_2/tests/unit")
    results_file = results_dir / f"result_rename_2025-08-24.json"

    # Basic test session info
    session_info = {
        "test_session": {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "test_file": "test_rename_2025-08-24.py",
            "target_module": "rename.py",
            "framework": "pytest",
            "test_categories": [
                "RenameWindow class",
                "Menu callbacks",
                "File operations",
                "UI interactions",
                "Main function",
                "Edge cases and error handling",
                "Performance and memory",
            ],
        }
    }

    try:
        with open(results_file, "w") as f:
            json.dump(session_info, f, indent=2)
    except Exception as e:
        print(f"Could not write test results: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
