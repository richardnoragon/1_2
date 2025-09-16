#!/usr/bin/env python3
"""
Comprehensive Unit Tests for find_duplicate_files.py
Created: 2025-08-24

Test Coverage:
- DuplicateFinderApp class initialization and UI components
- Directory selection and file scanning functionality
- Duplicate detection using MD5 hash comparison
- Results display and error handling
- Menu integration and callback functionality
- Edge cases: empty directories, permission errors, large files
- Mock data testing with various file structures
"""

import pytest
import tempfile
import os
import hashlib
from unittest.mock import patch
from pathlib import Path

# PyQt5 imports for GUI testing
from PyQt5.QtWidgets import QApplication

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.tools.analysis.find_duplicate_files import (
        DuplicateFinderApp, main
    )
except ImportError as e:
    pytest.skip(f"Cannot import find_duplicate_files module: {e}",
                allow_module_level=True)


class TestDuplicateFinderApp:
    """Test suite for DuplicateFinderApp class."""

    @pytest.fixture(scope="session")
    def app(self):
        """Create QApplication instance for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def duplicate_finder_app(self, app):
        """Create DuplicateFinderApp instance for testing."""
        with patch('src.tools.analysis.find_duplicate_files.'
                   'STANDARD_WINDOW_AVAILABLE', False):
            finder_app = DuplicateFinderApp()
        yield finder_app

    def test_duplicate_finder_app_initialization(self, duplicate_finder_app):
        """Test DuplicateFinderApp initialization and attributes."""
        assert duplicate_finder_app is not None
        assert hasattr(duplicate_finder_app, 'duplicates')
        assert duplicate_finder_app.duplicates == {}
        assert hasattr(duplicate_finder_app, 'selected_directory')
        assert duplicate_finder_app.selected_directory is None

    def test_window_title_setting(self, duplicate_finder_app):
        """Test window title is set correctly."""
        expected_title = "Duplicate Finder - Richard's File Utilities"
        assert duplicate_finder_app.windowTitle() == expected_title

    def test_ui_components_creation(self, duplicate_finder_app):
        """Test UI components are created properly."""
        assert hasattr(duplicate_finder_app, 'dir_label')
        assert hasattr(duplicate_finder_app, 'results_list')
        assert duplicate_finder_app.dir_label.text() == "No directory selected"

    def test_select_directory_success(self, duplicate_finder_app):
        """Test successful directory selection."""
        test_dir = "/test/directory/path"
        
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory',
                   return_value=test_dir):
            duplicate_finder_app.select_directory()
            
        assert duplicate_finder_app.selected_directory == test_dir
        assert f"Selected: {test_dir}" in duplicate_finder_app.dir_label.text()

    def test_select_directory_cancel(self, duplicate_finder_app):
        """Test directory selection cancellation."""
        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory',
                   return_value=""):
            original_dir = duplicate_finder_app.selected_directory
            duplicate_finder_app.select_directory()
            
        assert duplicate_finder_app.selected_directory == original_dir

    def test_find_duplicates_no_directory(self, duplicate_finder_app):
        """Test find_duplicates behavior when no directory is selected."""
        duplicate_finder_app.selected_directory = None
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            duplicate_finder_app.find_duplicates()
            mock_warning.assert_called_once()

    def test_prepare_scan(self, duplicate_finder_app):
        """Test scan preparation functionality."""
        # Add some items to results list
        duplicate_finder_app.results_list.addItem("Previous result")
        
        with patch('PyQt5.QtWidgets.QApplication.processEvents'):
            duplicate_finder_app._prepare_scan()
        
        # Check results list was cleared and scanning message added
        assert duplicate_finder_app.results_list.count() == 1
        assert "Scanning for duplicates..." in \
               duplicate_finder_app.results_list.item(0).text()

    def test_get_file_hash_success(self, duplicate_finder_app):
        """Test successful file hash calculation."""
        # Create temporary file with known content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            test_content = "Test file content for hashing"
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Calculate expected hash
            expected_hash = hashlib.md5(test_content.encode()).hexdigest()
            
            # Test hash calculation
            result_hash = duplicate_finder_app._get_file_hash(temp_file_path)
            assert result_hash == expected_hash
            
        finally:
            os.unlink(temp_file_path)

    def test_get_file_hash_file_not_found(self, duplicate_finder_app):
        """Test file hash calculation with non-existent file."""
        non_existent_path = "/path/to/non/existent/file.txt"
        result = duplicate_finder_app._get_file_hash(non_existent_path)
        assert result is None

    def test_get_file_hash_permission_error(self, duplicate_finder_app):
        """Test file hash calculation with permission denied."""
        side_effect = PermissionError("Access denied")
        with patch('builtins.open', side_effect=side_effect):
            result = duplicate_finder_app._get_file_hash("/some/file.txt")
            assert result is None

    def test_scan_for_duplicates_empty_directory(self, duplicate_finder_app):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            assert duplicates == []

    def test_scan_for_duplicates_no_duplicates(self, duplicate_finder_app):
        """Test scanning directory with unique files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create unique files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")
            
            with open(file1_path, 'w') as f:
                f.write("Unique content 1")
            with open(file2_path, 'w') as f:
                f.write("Unique content 2")
            
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            assert duplicates == []

    def test_scan_for_duplicates_with_duplicates(self, duplicate_finder_app):
        """Test scanning directory with duplicate files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create duplicate files
            duplicate_content = "Identical content for both files"
            
            file1_path = os.path.join(temp_dir, "original.txt")
            file2_path = os.path.join(temp_dir, "duplicate.txt")
            
            with open(file1_path, 'w') as f:
                f.write(duplicate_content)
            with open(file2_path, 'w') as f:
                f.write(duplicate_content)
            
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            
            assert len(duplicates) == 1
            original, duplicate = duplicates[0]
            expected_files = ["original.txt", "duplicate.txt"]
            assert os.path.basename(original) in expected_files
            assert os.path.basename(duplicate) in expected_files

    def test_scan_for_duplicates_nested_dirs(self, duplicate_finder_app):
        """Test scanning nested directories for duplicates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure with duplicates
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)
            
            duplicate_content = "Nested duplicate content"
            
            file1_path = os.path.join(temp_dir, "root_file.txt")
            file2_path = os.path.join(subdir, "nested_file.txt")
            
            with open(file1_path, 'w') as f:
                f.write(duplicate_content)
            with open(file2_path, 'w') as f:
                f.write(duplicate_content)
            
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            
            assert len(duplicates) == 1

    def test_display_results_no_duplicates(self, duplicate_finder_app):
        """Test displaying results when no duplicates found."""
        duplicate_finder_app._display_results([])
        
        assert duplicate_finder_app.results_list.count() == 1
        assert "No duplicates found." in \
               duplicate_finder_app.results_list.item(0).text()

    def test_display_results_with_duplicates(self, duplicate_finder_app):
        """Test displaying results with duplicates found."""
        test_duplicates = [
            ("/path/to/original.txt", "/path/to/duplicate.txt"),
            ("/path/to/file1.doc", "/path/to/file2.doc")
        ]
        
        duplicate_finder_app._display_results(test_duplicates)
        
        # Should have header + (original + duplicate + separator) * 2
        expected_items = 1 + (3 * 2)  # 7 items total
        assert duplicate_finder_app.results_list.count() == expected_items
        
        # Check header
        header_text = duplicate_finder_app.results_list.item(0).text()
        assert "Found 2 duplicate pairs:" in header_text

    def test_clear_results(self, duplicate_finder_app):
        """Test clearing duplicate scan results."""
        # Set up some data
        duplicate_finder_app.duplicates = {"test": "data"}
        duplicate_finder_app.results_list.addItem("Test item")
        
        duplicate_finder_app.clear_results()
        
        assert duplicate_finder_app.duplicates == {}
        assert duplicate_finder_app.results_list.count() == 0

    def test_show_help(self, duplicate_finder_app):
        """Test showing help dialog."""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            duplicate_finder_app.show_help()
            mock_info.assert_called_once()
            
            # Check that help content contains expected elements
            call_args = mock_info.call_args[0]
            assert "Duplicate Finder Help" in call_args[1]
            assert "How to Find Duplicates:" in call_args[2]

    def test_show_preferences(self, duplicate_finder_app):
        """Test showing preferences dialog."""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            duplicate_finder_app.show_preferences()
            mock_info.assert_called_once()
            
            call_args = mock_info.call_args[0]
            assert "Duplicate Finder Preferences" in call_args[1]

    def test_refresh_view(self, duplicate_finder_app):
        """Test refreshing view clears results."""
        # Set up some data
        duplicate_finder_app.duplicates = {"test": "data"}
        duplicate_finder_app.results_list.addItem("Test item")
        
        duplicate_finder_app.refresh_view()
        
        assert duplicate_finder_app.duplicates == {}
        assert duplicate_finder_app.results_list.count() == 0

    def test_find_duplicates_exception_handling(self, duplicate_finder_app):
        """Test exception handling during duplicate finding."""
        duplicate_finder_app.selected_directory = "/valid/path"
        
        with patch.object(duplicate_finder_app, '_scan_for_duplicates',
                          side_effect=Exception("Test error")):
            with patch('PyQt5.QtWidgets.QMessageBox.critical') as mock_crit:
                duplicate_finder_app.find_duplicates()
                mock_crit.assert_called_once()

    def test_fallback_mode_initialization(self):
        """Test initialization in fallback mode."""
        with patch('src.tools.analysis.find_duplicate_files.'
                   'STANDARD_WINDOW_AVAILABLE', False):
            app = DuplicateFinderApp()
            assert app is not None
            assert hasattr(app, 'duplicates')

    def test_menu_callbacks_setup(self, duplicate_finder_app):
        """Test menu callbacks setup when StandardWindow is available."""
        if hasattr(duplicate_finder_app, 'menu_manager'):
            # Verify menu callbacks are set up
            assert hasattr(duplicate_finder_app, '_setup_menu_callbacks')


class TestMainFunction:
    """Test suite for main function."""
    
    def test_main_function_basic_import(self):
        """Test main function is properly defined and importable."""
        # Simply test that we can import and access the main function
        assert callable(main)
        assert main.__name__ == 'main'
        # This is safer than trying to execute it in test environment


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    @pytest.fixture(scope="session")
    def app(self):
        """Create QApplication instance for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def duplicate_finder_app(self, app):
        """Create DuplicateFinderApp instance for testing."""
        with patch('src.tools.analysis.find_duplicate_files.'
                   'STANDARD_WINDOW_AVAILABLE', False):
            finder_app = DuplicateFinderApp()
        yield finder_app

    def test_large_file_handling(self, duplicate_finder_app):
        """Test handling of large files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a moderately large file
            large_file_path = os.path.join(temp_dir, "large_file.bin")
            
            # Write 1MB of data
            with open(large_file_path, 'wb') as f:
                data = b'A' * (1024 * 1024)  # 1MB of 'A' characters
                f.write(data)
            
            # Test hash calculation
            result_hash = duplicate_finder_app._get_file_hash(large_file_path)
            assert result_hash is not None
            assert len(result_hash) == 32  # MD5 hash length

    def test_unicode_filename_handling(self, duplicate_finder_app):
        """Test handling of files with Unicode names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with Unicode name
            unicode_filename = "测试文件_тест_🔥.txt"
            unicode_file_path = os.path.join(temp_dir, unicode_filename)
            
            try:
                with open(unicode_file_path, 'w', encoding='utf-8') as f:
                    f.write("Unicode content")
                
                duplicate_finder_app.selected_directory = temp_dir
                duplicates = duplicate_finder_app._scan_for_duplicates()
                
                # Should handle Unicode filenames without errors
                assert isinstance(duplicates, list)
                
            except (OSError, UnicodeError):
                # Skip test if filesystem doesn't support Unicode names
                pytest.skip("Filesystem doesn't support Unicode filenames")

    def test_deeply_nested_directory_structure(self, duplicate_finder_app):
        """Test scanning deeply nested directory structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create deeply nested structure
            current_dir = temp_dir
            for i in range(10):  # 10 levels deep
                current_dir = os.path.join(current_dir, f"level_{i}")
                os.makedirs(current_dir)
            
            # Create test file in deepest directory
            test_file = os.path.join(current_dir, "deep_file.txt")
            with open(test_file, 'w') as f:
                f.write("Deep nested content")
            
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            
            # Should handle deep nesting without errors
            assert isinstance(duplicates, list)

    def test_binary_file_handling(self, duplicate_finder_app):
        """Test handling of binary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create binary file
            binary_file_path = os.path.join(temp_dir, "binary_file.bin")
            binary_data = bytes(range(256))  # All possible byte values
            
            with open(binary_file_path, 'wb') as f:
                f.write(binary_data)
            
            # Test hash calculation for binary file
            result_hash = duplicate_finder_app._get_file_hash(binary_file_path)
            assert result_hash is not None
            
            # Verify hash is correct
            expected_hash = hashlib.md5(binary_data).hexdigest()
            assert result_hash == expected_hash

    def test_empty_file_handling(self, duplicate_finder_app):
        """Test handling of empty files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty files
            empty_file1 = os.path.join(temp_dir, "empty1.txt")
            empty_file2 = os.path.join(temp_dir, "empty2.txt")
            
            # Create empty files
            open(empty_file1, 'w').close()
            open(empty_file2, 'w').close()
            
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            
            # Empty files should be detected as duplicates
            assert len(duplicates) == 1

    def test_mixed_file_types_scanning(self, duplicate_finder_app):
        """Test scanning directory with mixed file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files of different types
            files_data = [
                ("text_file.txt", "Text content"),
                ("json_file.json", '{"key": "value"}'),
                ("markdown_file.md", "# Markdown Header"),
                ("python_file.py", "print('Hello World')")
            ]
            
            for filename, content in files_data:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            duplicate_finder_app.selected_directory = temp_dir
            duplicates = duplicate_finder_app._scan_for_duplicates()
            
            # Should handle mixed file types without errors
            assert isinstance(duplicates, list)

    def test_symlink_handling(self, duplicate_finder_app):
        """Test handling of symbolic links."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create original file
            original_file = os.path.join(temp_dir, "original.txt")
            with open(original_file, 'w') as f:
                f.write("Original content")
            
            # Create symlink (skip on Windows if not supported)
            try:
                symlink_file = os.path.join(temp_dir, "symlink.txt")
                os.symlink(original_file, symlink_file)
                
                duplicate_finder_app.selected_directory = temp_dir
                duplicates = duplicate_finder_app._scan_for_duplicates()
                
                # Should handle symlinks gracefully
                assert isinstance(duplicates, list)
                
            except (OSError, NotImplementedError):
                # Skip test if symlinks not supported
                pytest.skip("Symbolic links not supported on this platform")

    def test_scan_with_permission_errors(self, duplicate_finder_app):
        """Test scanning with some files having permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create accessible file
            good_file = os.path.join(temp_dir, "accessible.txt")
            with open(good_file, 'w') as f:
                f.write("Accessible content")
            
            duplicate_finder_app.selected_directory = temp_dir
            
            # Mock _get_file_hash to simulate permission error for some files
            original_get_hash = duplicate_finder_app._get_file_hash
            
            def mock_get_hash(file_path):
                if "inaccessible" in file_path:
                    return None  # Simulate permission error
                return original_get_hash(file_path)
            
            with patch.object(duplicate_finder_app, '_get_file_hash',
                              side_effect=mock_get_hash):
                duplicates = duplicate_finder_app._scan_for_duplicates()
                
                # Should handle permission errors gracefully
                assert isinstance(duplicates, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])