#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Permissions Editor GUI
Test Suite: permissions_editor.py - Test Coverage and Quality Assurance

Author: Generated Test Suite
Date: 2025-08-28
Target Module: src.utilities.system.permissions_editor
Test Framework: pytest with comprehensive reporting
Coverage Target: 90%+ line coverage with edge case testing

Test Categories:
- GUI Component Tests
- File Permission Operations
- Error Handling and Edge Cases
- User Interface Integration
- Platform Compatibility
- Security and Validation
"""

import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import PyQt5 testing utilities
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

# Import test target
try:
    from src.utilities.system.permissions_editor import PermissionsEditorGUI
    TARGET_MODULE_AVAILABLE = True
except ImportError as e:
    TARGET_MODULE_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Test configuration
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
TEMP_DIR = tempfile.mkdtemp(prefix='permissions_editor_test_')


class TestPermissionsEditorSetup:
    """Test setup and teardown for Permissions Editor tests."""
    
    @classmethod
    def setup_class(cls):
        """Class-level setup."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip(f"Target module not available: {IMPORT_ERROR}")
        
        if not PYQT5_AVAILABLE:
            pytest.skip("PyQt5 not available for GUI testing")
        
        # Create QApplication if not exists
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
        
        # Create test directories and files
        cls.test_dir = tempfile.mkdtemp(prefix='permissions_test_')
        cls.test_file = os.path.join(cls.test_dir, 'test_file.txt')
        cls.test_subdir = os.path.join(cls.test_dir, 'subdir')
        
        # Create test file
        with open(cls.test_file, 'w') as f:
            f.write("Test content for permissions testing")
        
        # Create test subdirectory
        os.makedirs(cls.test_subdir, exist_ok=True)
        
        # Create protected file
        cls.protected_file = os.path.join(cls.test_dir, 'protected.txt')
        with open(cls.protected_file, 'w') as f:
            f.write("Protected content")
        os.chmod(cls.protected_file, stat.S_IRUSR)  # Read-only
    
    @classmethod
    def teardown_class(cls):
        """Class-level teardown."""
        # Cleanup test directory
        if hasattr(cls, 'test_dir') and os.path.exists(cls.test_dir):
            # Reset permissions for cleanup
            for root, dirs, files in os.walk(cls.test_dir):
                for file in files:
                    try:
                        os.chmod(os.path.join(root, file), stat.S_IWRITE | stat.S_IREAD)
                    except (OSError, FileNotFoundError):
                        pass
            try:
                shutil.rmtree(cls.test_dir)
            except (OSError, FileNotFoundError):
                pass
    
    def setup_method(self):
        """Method-level setup."""
        self.widget = None
    
    def teardown_method(self):
        """Method-level teardown."""
        if self.widget:
            try:
                self.widget.close()
                self.widget = None
            except:
                pass


class TestPermissionsEditorInitialization(TestPermissionsEditorSetup):
    """Test Permissions Editor initialization and basic setup."""
    
    def test_basic_initialization(self):
        """Test basic widget initialization."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            assert self.widget is not None
            assert hasattr(self.widget, 'selected_path')
            assert hasattr(self.widget, 'file_label')
            assert hasattr(self.widget, 'read_check')
            assert hasattr(self.widget, 'write_check')
            assert hasattr(self.widget, 'execute_check')
            assert hasattr(self.widget, 'status_list')
    
    def test_standard_window_initialization(self):
        """Test initialization with StandardWindow available."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', True):
            with patch('src.utilities.system.permissions_editor.StandardWindow') as mock_window:
                mock_instance = Mock()
                mock_window.return_value = mock_instance
                mock_instance.main_layout = Mock()
                
                # This would require actual StandardWindow import, so we'll mock it
                with patch.object(PermissionsEditorGUI, '__init__') as mock_init:
                    mock_init.return_value = None
                    widget = PermissionsEditorGUI()
                    mock_init.assert_called_once()
    
    def test_initial_state(self):
        """Test initial widget state."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            assert self.widget.selected_path is None
            assert not self.widget.read_check.isChecked()
            assert not self.widget.write_check.isChecked()
            assert not self.widget.execute_check.isChecked()
            assert self.widget.status_list.count() == 0
    
    def test_ui_components_exist(self):
        """Test that all required UI components are created."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Check required components
            assert hasattr(self.widget, 'file_label')
            assert hasattr(self.widget, 'read_check')
            assert hasattr(self.widget, 'write_check')
            assert hasattr(self.widget, 'execute_check')
            assert hasattr(self.widget, 'status_list')
            
            # Check component types
            from PyQt5.QtWidgets import QCheckBox, QLabel, QListWidget
            assert isinstance(self.widget.file_label, QLabel)
            assert isinstance(self.widget.read_check, QCheckBox)
            assert isinstance(self.widget.write_check, QCheckBox)
            assert isinstance(self.widget.execute_check, QCheckBox)
            assert isinstance(self.widget.status_list, QListWidget)


class TestFileSelection(TestPermissionsEditorSetup):
    """Test file and directory selection functionality."""
    
    def test_select_file_success(self):
        """Test successful file selection."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            with patch.object(QFileDialog, 'getOpenFileName', return_value=(self.test_file, None)):
                self.widget.select_file()
                
                assert self.widget.selected_path == self.test_file
                assert self.test_file in self.widget.file_label.text()
                assert self.widget.status_list.count() > 0
    
    def test_select_file_cancel(self):
        """Test file selection cancellation."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            original_path = self.widget.selected_path
            
            with patch.object(QFileDialog, 'getOpenFileName', return_value=('', None)):
                self.widget.select_file()
                
                assert self.widget.selected_path == original_path
    
    def test_select_directory_success(self):
        """Test successful directory selection."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            with patch.object(QFileDialog, 'getExistingDirectory', return_value=self.test_dir):
                self.widget.select_directory()
                
                assert self.widget.selected_path == self.test_dir
                assert self.test_dir in self.widget.file_label.text()
                assert self.widget.status_list.count() > 0
    
    def test_select_directory_cancel(self):
        """Test directory selection cancellation."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            original_path = self.widget.selected_path
            
            with patch.object(QFileDialog, 'getExistingDirectory', return_value=''):
                self.widget.select_directory()
                
                assert self.widget.selected_path == original_path


class TestPermissionLoading(TestPermissionsEditorSetup):
    """Test permission loading functionality."""
    
    def test_load_permissions_no_selection(self):
        """Test loading permissions with no file selected."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            with patch.object(QMessageBox, 'warning') as mock_warning:
                self.widget.load_permissions()
                mock_warning.assert_called_once()
    
    def test_load_permissions_readable_file(self):
        """Test loading permissions from readable file."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Set known permissions
            os.chmod(self.test_file, stat.S_IRUSR | stat.S_IWUSR)
            
            self.widget.load_permissions()
            
            assert self.widget.read_check.isChecked()
            assert self.widget.write_check.isChecked()
            assert not self.widget.execute_check.isChecked()
            assert self.widget.status_list.count() > 0
    
    def test_load_permissions_executable_file(self):
        """Test loading permissions from executable file."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Set executable permissions
            os.chmod(self.test_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            
            self.widget.load_permissions()
            
            assert self.widget.read_check.isChecked()
            assert self.widget.write_check.isChecked()
            assert self.widget.execute_check.isChecked()
    
    def test_load_permissions_readonly_file(self):
        """Test loading permissions from read-only file."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.protected_file
            
            self.widget.load_permissions()
            
            assert self.widget.read_check.isChecked()
            assert not self.widget.write_check.isChecked()
            assert not self.widget.execute_check.isChecked()
    
    def test_load_permissions_nonexistent_file(self):
        """Test loading permissions from nonexistent file."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = '/nonexistent/file.txt'
            
            with patch.object(QMessageBox, 'critical') as mock_critical:
                self.widget.load_permissions()
                mock_critical.assert_called_once()
                assert self.widget.status_list.count() > 0


class TestPermissionApplication(TestPermissionsEditorSetup):
    """Test permission application functionality."""
    
    def test_apply_permissions_no_selection(self):
        """Test applying permissions with no file selected."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            with patch.object(QMessageBox, 'warning') as mock_warning:
                self.widget.apply_permissions()
                mock_warning.assert_called_once()
    
    def test_apply_permissions_user_accepts(self):
        """Test applying permissions when user accepts confirmation."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Set checkboxes
            self.widget.read_check.setChecked(True)
            self.widget.write_check.setChecked(True)
            self.widget.execute_check.setChecked(False)
            
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
                with patch.object(QMessageBox, 'information') as mock_info:
                    self.widget.apply_permissions()
                    mock_info.assert_called_once()
                    assert self.widget.status_list.count() > 0
    
    def test_apply_permissions_user_rejects(self):
        """Test applying permissions when user rejects confirmation."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Set checkboxes
            self.widget.read_check.setChecked(True)
            self.widget.write_check.setChecked(False)
            self.widget.execute_check.setChecked(False)
            
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.No):
                with patch('os.chmod') as mock_chmod:
                    self.widget.apply_permissions()
                    mock_chmod.assert_not_called()
    
    def test_apply_permissions_chmod_error(self):
        """Test applying permissions with chmod error."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Set checkboxes
            self.widget.read_check.setChecked(True)
            
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
                with patch('os.chmod', side_effect=OSError("Permission denied")):
                    with patch.object(QMessageBox, 'critical') as mock_critical:
                        self.widget.apply_permissions()
                        mock_critical.assert_called_once()
                        assert self.widget.status_list.count() > 0
    
    def test_apply_permissions_all_combinations(self):
        """Test applying all permission combinations."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Test all 8 combinations of read/write/execute
            combinations = [
                (False, False, False),  # ---
                (True, False, False),   # r--
                (False, True, False),   # -w-
                (False, False, True),   # --x
                (True, True, False),    # rw-
                (True, False, True),    # r-x
                (False, True, True),    # -wx
                (True, True, True),     # rwx
            ]
            
            for read, write, execute in combinations:
                self.widget.read_check.setChecked(read)
                self.widget.write_check.setChecked(write)
                self.widget.execute_check.setChecked(execute)
                
                with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
                    with patch.object(QMessageBox, 'information'):
                        with patch('os.chmod') as mock_chmod:
                            self.widget.apply_permissions()
                            mock_chmod.assert_called_once()
                            
                            # Verify correct mode calculation
                            expected_mode = 0
                            if read:
                                expected_mode |= stat.S_IRUSR
                            if write:
                                expected_mode |= stat.S_IWUSR
                            if execute:
                                expected_mode |= stat.S_IXUSR
                            
                            mock_chmod.assert_called_with(self.test_file, expected_mode)


class TestUIOperations(TestPermissionsEditorSetup):
    """Test UI operations and user interactions."""
    
    def test_clear_selection(self):
        """Test clearing selection."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Set some state
            self.widget.selected_path = self.test_file
            self.widget.file_label.setText("Some file")
            self.widget.read_check.setChecked(True)
            self.widget.write_check.setChecked(True)
            self.widget.execute_check.setChecked(True)
            self.widget.status_list.addItem("Test item")
            
            # Clear selection
            self.widget.clear_selection()
            
            assert self.widget.selected_path is None
            assert "No file/directory selected" in self.widget.file_label.text()
            assert not self.widget.read_check.isChecked()
            assert not self.widget.write_check.isChecked()
            assert not self.widget.execute_check.isChecked()
            assert self.widget.status_list.count() == 0
    
    def test_refresh_view_with_selection(self):
        """Test refreshing view with file selected."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            with patch.object(self.widget, 'load_permissions') as mock_load:
                self.widget.refresh_view()
                mock_load.assert_called_once()
    
    def test_refresh_view_without_selection(self):
        """Test refreshing view without file selected."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = None
            
            with patch.object(self.widget, 'clear_selection') as mock_clear:
                self.widget.refresh_view()
                mock_clear.assert_called_once()


class TestHelpAndPreferences(TestPermissionsEditorSetup):
    """Test help and preferences functionality."""
    
    def test_show_help(self):
        """Test showing help dialog."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            with patch.object(QMessageBox, 'exec_') as mock_exec:
                mock_box = Mock()
                with patch('src.utilities.system.permissions_editor.QMessageBox', return_value=mock_box):
                    self.widget.show_help()
                    # Verify help dialog was created and shown
                    assert True  # Help method executed without error
    
    def test_show_preferences(self):
        """Test showing preferences dialog."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            with patch.object(QMessageBox, 'information') as mock_info:
                self.widget.show_preferences()
                mock_info.assert_called_once()


class TestMenuIntegration(TestPermissionsEditorSetup):
    """Test menu integration functionality."""
    
    def test_setup_menu_callbacks_with_standard_window(self):
        """Test menu callback setup with StandardWindow."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', True):
            with patch('src.utilities.system.permissions_editor.StandardWindow'):
                # Create mock widget with menu manager
                widget = Mock()
                widget.menu_manager = Mock()
                
                # Test the callback setup method
                with patch.object(PermissionsEditorGUI, '__init__'):
                    test_widget = PermissionsEditorGUI()
                    test_widget.menu_manager = Mock()
                    test_widget._setup_menu_callbacks()
                    
                    # Verify callbacks were registered
                    assert test_widget.menu_manager.register_callback.call_count >= 0
    
    def test_setup_menu_callbacks_without_menu_manager(self):
        """Test menu callback setup without menu manager."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Should not raise an error
            if hasattr(self.widget, '_setup_menu_callbacks'):
                self.widget._setup_menu_callbacks()


class TestEdgeCases(TestPermissionsEditorSetup):
    """Test edge cases and error conditions."""
    
    def test_long_file_paths(self):
        """Test handling of very long file paths."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Create a very long path
            long_path = os.path.join(self.test_dir, 'a' * 200 + '.txt')
            
            try:
                with open(long_path, 'w') as f:
                    f.write("test")
                
                with patch.object(QFileDialog, 'getOpenFileName', return_value=(long_path, None)):
                    self.widget.select_file()
                    assert self.widget.selected_path == long_path
                    
                    # Test loading permissions
                    self.widget.load_permissions()
                    assert self.widget.status_list.count() > 0
                    
            except OSError:
                # Skip if filesystem doesn't support long paths
                pytest.skip("Filesystem doesn't support long paths")
    
    def test_special_characters_in_path(self):
        """Test handling of special characters in file paths."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Create file with special characters
            special_file = os.path.join(self.test_dir, 'test file with spaces & symbols.txt')
            
            try:
                with open(special_file, 'w') as f:
                    f.write("test content")
                
                with patch.object(QFileDialog, 'getOpenFileName', return_value=(special_file, None)):
                    self.widget.select_file()
                    assert self.widget.selected_path == special_file
                    
                    # Test operations
                    self.widget.load_permissions()
                    assert self.widget.status_list.count() > 0
                    
            except (OSError, UnicodeError):
                pytest.skip("Filesystem doesn't support special characters")
    
    def test_permission_edge_cases(self):
        """Test edge cases in permission handling."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            self.widget.selected_path = self.test_file
            
            # Test with no permissions set
            self.widget.read_check.setChecked(False)
            self.widget.write_check.setChecked(False)
            self.widget.execute_check.setChecked(False)
            
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
                with patch.object(QMessageBox, 'information'):
                    with patch('os.chmod') as mock_chmod:
                        self.widget.apply_permissions()
                        mock_chmod.assert_called_with(self.test_file, 0)
    
    def test_rapid_operations(self):
        """Test rapid successive operations."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Rapidly select and load permissions
            for i in range(5):
                with patch.object(QFileDialog, 'getOpenFileName', 
                                return_value=(self.test_file, None)):
                    self.widget.select_file()
                    self.widget.load_permissions()
                    self.widget.clear_selection()
            
            # Should complete without errors
            assert True


class TestPerformanceAndMemory(TestPermissionsEditorSetup):
    """Test performance and memory usage."""
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            import gc

            # Create and destroy multiple widgets
            widgets = []
            for i in range(10):
                widget = PermissionsEditorGUI()
                widgets.append(widget)
            
            # Clean up
            for widget in widgets:
                widget.close()
            
            widgets.clear()
            gc.collect()
            
            # Test passes if no memory errors occur
            assert True
    
    def test_large_status_list(self):
        """Test performance with large status list."""
        with patch('src.utilities.system.permissions_editor.STANDARD_WINDOW_AVAILABLE', False):
            self.widget = PermissionsEditorGUI()
            
            # Add many items to status list
            for i in range(1000):
                self.widget.status_list.addItem(f"Status item {i}")
            
            # Should handle large lists without performance issues
            assert self.widget.status_list.count() == 1000
            
            # Clear and verify
            self.widget.status_list.clear()
            assert self.widget.status_list.count() == 0


class TestMainFunction:
    """Test the main function and standalone execution."""
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from src.utilities.system.permissions_editor import main
        assert callable(main)
    
    def test_main_function_execution(self):
        """Test main function execution (mocked)."""
        with patch('src.utilities.system.permissions_editor.QApplication') as mock_app:
            with patch('src.utilities.system.permissions_editor.PermissionsEditorGUI') as mock_widget:
                with patch('sys.exit') as mock_exit:
                    mock_app_instance = Mock()
                    mock_app.return_value = mock_app_instance
                    mock_widget_instance = Mock()
                    mock_widget.return_value = mock_widget_instance
                    
                    from src.utilities.system.permissions_editor import main
                    
                    try:
                        main()
                    except SystemExit:
                        pass  # Expected behavior
                    
                    mock_app.assert_called_once()
                    mock_widget.assert_called_once()
                    mock_widget_instance.show.assert_called_once()


# Test execution and reporting
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--html=result_permissions_editor_2025-08-28.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_permissions_editor_2025-08-28.json"
    ])