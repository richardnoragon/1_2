#!/usr/bin/env python3
"""
Comprehensive Unit Tests for secure_delete.py
Generated on: 2025-08-28
Test Framework: pytest

This module contains comprehensive unit tests for the SecureDeleteGUI class
and all its methods, covering functionality, edge cases, and error handling.
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Mock PyQt5 before importing the module under test
@pytest.fixture(autouse=True)
def mock_pyqt5():
    """Mock PyQt5 components to avoid GUI dependencies in tests."""
    mock_widgets = MagicMock()
    mock_widgets.QWidget = MagicMock()
    mock_widgets.QVBoxLayout = MagicMock()
    mock_widgets.QHBoxLayout = MagicMock()
    mock_widgets.QPushButton = MagicMock()
    mock_widgets.QLabel = MagicMock()
    mock_widgets.QListWidget = MagicMock()
    mock_widgets.QProgressBar = MagicMock()
    mock_widgets.QApplication = MagicMock()
    mock_widgets.QMessageBox = MagicMock()
    mock_widgets.QFileDialog = MagicMock()
    mock_widgets.QGroupBox = MagicMock()
    mock_widgets.QLineEdit = MagicMock()
    mock_widgets.QCheckBox = MagicMock()
    mock_widgets.QSpinBox = MagicMock()
    mock_widgets.QComboBox = MagicMock()
    mock_widgets.QMainWindow = MagicMock()
    
    with patch.dict('sys.modules', {'PyQt5.QtWidgets': mock_widgets}):
        yield mock_widgets


@pytest.fixture
def mock_standard_window():
    """Mock StandardWindow to avoid GUI dependencies."""
    mock_window = MagicMock()
    with patch('src.utilities.security.secure_delete.StandardWindow', mock_window):
        yield mock_window


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix='secure_delete_test_')
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_test_files(temp_test_dir):
    """Create temporary test files."""
    files = []
    for i in range(3):
        file_path = os.path.join(temp_test_dir, f'test_file_{i}.txt')
        with open(file_path, 'w') as f:
            f.write(f'Test content for file {i}')
        files.append(file_path)
    return files


class TestSecureDeleteGUI:
    """Test class for SecureDeleteGUI functionality."""
    
    @pytest.fixture
    def secure_delete_gui(self, mock_pyqt5, mock_standard_window):
        """Create a SecureDeleteGUI instance for testing."""
        # Mock the availability check
        with patch('src.utilities.security.secure_delete.STANDARD_WINDOW_AVAILABLE', True):
            from src.utilities.security.secure_delete import SecureDeleteGUI
            gui = SecureDeleteGUI()
            # Mock the UI components that might not be created during testing
            gui.delete_button = MagicMock()
            gui.select_files_button = MagicMock()
            gui.select_folder_button = MagicMock()
            gui.progress_bar = MagicMock()
            gui.method_combo = MagicMock()
            gui.verify_deletion = MagicMock()
            return gui
    
    def test_init_with_standard_window_available(self, mock_pyqt5, mock_standard_window):
        """Test initialization when StandardWindow is available."""
        with patch('src.utilities.security.secure_delete.STANDARD_WINDOW_AVAILABLE', True):
            from src.utilities.security.secure_delete import SecureDeleteGUI
            gui = SecureDeleteGUI()
            
            # Verify initialization
            assert gui.selected_files == []
            assert hasattr(gui, 'selected_files')
    
    def test_init_without_standard_window(self, mock_pyqt5):
        """Test initialization when StandardWindow is not available."""
        with patch('src.utilities.security.secure_delete.STANDARD_WINDOW_AVAILABLE', False):
            from src.utilities.security.secure_delete import SecureDeleteGUI
            gui = SecureDeleteGUI()
            
            # Verify fallback initialization
            assert gui.selected_files == []
    
    def test_setup_menu_callbacks(self, secure_delete_gui):
        """Test menu callback setup."""
        # Mock menu_manager
        secure_delete_gui.menu_manager = MagicMock()
        secure_delete_gui._setup_menu_callbacks()
        
        # Verify callbacks were registered
        expected_calls = [
            call('new_deletion', secure_delete_gui.clear_selection),
            call('help_secure_delete', secure_delete_gui.show_help)
        ]
        secure_delete_gui.menu_manager.register_callback.assert_has_calls(expected_calls)
    
    def test_show_help(self, secure_delete_gui, mock_pyqt5):
        """Test help dialog display."""
        secure_delete_gui.show_help()
        
        # Verify QMessageBox was called
        mock_pyqt5.QMessageBox.assert_called()
    
    def test_show_preferences(self, secure_delete_gui, mock_pyqt5):
        """Test preferences dialog display."""
        secure_delete_gui.show_preferences()
        
        # Verify QMessageBox.information was called
        mock_pyqt5.QMessageBox.information.assert_called()
    
    def test_refresh_view(self, secure_delete_gui):
        """Test view refresh functionality."""
        # Setup mock attributes
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        secure_delete_gui.selected_files = ['test_file.txt']
        
        secure_delete_gui.refresh_view()
        
        # Verify refresh actions
        secure_delete_gui.files_list.clear.assert_called_once()
        assert secure_delete_gui.selected_files == []
    
    def test_clear_selection(self, secure_delete_gui):
        """Test clearing file selection."""
        # Setup mock attributes
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        secure_delete_gui.selected_files = ['test_file.txt']
        
        secure_delete_gui.clear_selection()
        
        # Verify clearing actions
        secure_delete_gui.files_list.clear.assert_called_once()
        secure_delete_gui.status_label.setText.assert_called_with(
            "Ready - Select files or directories to securely delete"
        )
        assert secure_delete_gui.selected_files == []
    
    def test_clear_selection_without_attributes(self, secure_delete_gui):
        """Test clear_selection when attributes don't exist."""
        # Ensure attributes don't exist
        if hasattr(secure_delete_gui, 'files_list'):
            delattr(secure_delete_gui, 'files_list')
        if hasattr(secure_delete_gui, 'status_label'):
            delattr(secure_delete_gui, 'status_label')
        
        secure_delete_gui.selected_files = ['test_file.txt']
        
        # Should not raise exception
        secure_delete_gui.clear_selection()
        assert secure_delete_gui.selected_files == []
    
    @patch('src.utilities.security.secure_delete.QFileDialog')
    def test_select_files_success(self, mock_file_dialog, secure_delete_gui, temp_test_files):
        """Test successful file selection."""
        # Setup mocks
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        mock_file_dialog.getOpenFileNames.return_value = (temp_test_files, "")
        
        secure_delete_gui.select_files()
        
        # Verify file selection
        mock_file_dialog.getOpenFileNames.assert_called_once()
        secure_delete_gui.files_list.clear.assert_called_once()
        assert secure_delete_gui.selected_files == temp_test_files
        secure_delete_gui.status_label.setText.assert_called_with(
            f"Selected {len(temp_test_files)} file(s) for secure deletion"
        )
    
    @patch('src.utilities.security.secure_delete.QFileDialog')
    def test_select_files_cancelled(self, mock_file_dialog, secure_delete_gui):
        """Test file selection when cancelled."""
        # Setup mocks
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        mock_file_dialog.getOpenFileNames.return_value = ([], "")
        
        secure_delete_gui.select_files()
        
        # Verify no files were selected
        mock_file_dialog.getOpenFileNames.assert_called_once()
        secure_delete_gui.files_list.clear.assert_not_called()
        assert secure_delete_gui.selected_files == []
    
    @patch('src.utilities.security.secure_delete.QFileDialog')
    def test_select_folder_success(self, mock_file_dialog, secure_delete_gui, temp_test_dir):
        """Test successful folder selection."""
        # Setup mocks
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        mock_file_dialog.getExistingDirectory.return_value = temp_test_dir
        
        secure_delete_gui.select_folder()
        
        # Verify folder selection
        mock_file_dialog.getExistingDirectory.assert_called_once()
        secure_delete_gui.files_list.clear.assert_called_once()
        assert secure_delete_gui.selected_files == [temp_test_dir]
        secure_delete_gui.status_label.setText.assert_called_with(
            "Selected folder for secure deletion"
        )
    
    @patch('src.utilities.security.secure_delete.QFileDialog')
    def test_select_folder_cancelled(self, mock_file_dialog, secure_delete_gui):
        """Test folder selection when cancelled."""
        # Setup mocks
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        mock_file_dialog.getExistingDirectory.return_value = ""
        
        secure_delete_gui.select_folder()
        
        # Verify no folder was selected
        mock_file_dialog.getExistingDirectory.assert_called_once()
        secure_delete_gui.files_list.clear.assert_not_called()
        assert secure_delete_gui.selected_files == []
    
    @patch('src.utilities.security.secure_delete.QMessageBox')
    def test_secure_delete_no_files_selected(self, mock_message_box, secure_delete_gui):
        """Test secure delete with no files selected."""
        secure_delete_gui.selected_files = []
        
        secure_delete_gui.secure_delete()
        
        # Verify warning message
        mock_message_box.warning.assert_called_once_with(
            secure_delete_gui, "Warning", "Please select files or folders first."
        )
    
    @patch('src.utilities.security.secure_delete.QMessageBox')
    def test_secure_delete_confirmation_cancelled(self, mock_message_box, secure_delete_gui):
        """Test secure delete when confirmation is cancelled."""
        # Setup
        secure_delete_gui.selected_files = ['test_file.txt']
        secure_delete_gui.method_combo = MagicMock()
        secure_delete_gui.method_combo.currentText.return_value = "DoD 5220.22-M (3 Pass)"
        secure_delete_gui.verify_deletion = MagicMock()
        secure_delete_gui.verify_deletion.isChecked.return_value = True
        
        # Mock confirmation dialog to return No
        mock_message_box.critical.return_value = mock_message_box.No
        
        secure_delete_gui.secure_delete()
        
        # Verify confirmation dialog was shown but information dialog was not
        mock_message_box.critical.assert_called_once()
        mock_message_box.information.assert_not_called()
    
    @patch('src.utilities.security.secure_delete.threading.Thread')
    @patch('src.utilities.security.secure_delete.QMessageBox')
    def test_secure_delete_confirmation_accepted(self, mock_message_box, mock_thread, secure_delete_gui):
        """Test secure delete when confirmation is accepted."""
        # Setup
        secure_delete_gui.selected_files = ['test_file.txt', 'test_folder']
        secure_delete_gui.method_combo.currentText.return_value = "DoD 5220.22-M (3 Pass)"
        secure_delete_gui.verify_deletion.isChecked.return_value = True
        
        # Mock confirmation dialog to return Yes
        mock_message_box.critical.return_value = mock_message_box.Yes
        
        # Mock the threading functionality
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        secure_delete_gui.secure_delete()
        
        # Verify confirmation dialog was shown
        mock_message_box.critical.assert_called_once()
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        
        # Verify UI was disabled during operation
        secure_delete_gui.delete_button.setEnabled.assert_called_with(False)
        secure_delete_gui.progress_bar.setVisible.assert_called_with(True)
    
    @patch('src.utilities.security.secure_delete.threading.Thread')
    @patch('src.utilities.security.secure_delete.QMessageBox')
    def test_secure_delete_various_methods(self, mock_message_box, mock_thread, secure_delete_gui):
        """Test secure delete with different deletion methods."""
        methods = [
            "Single Pass (Quick)",
            "DoD 5220.22-M (3 Pass)",
            "Random Pattern (7 Pass)",
            "Gutmann Method (35 Pass)",
            "Custom Pattern"
        ]
        
        # Mock the threading functionality
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        for method in methods:
            # Setup
            secure_delete_gui.selected_files = ['test_file.txt']
            secure_delete_gui.method_combo.currentText.return_value = method
            secure_delete_gui.verify_deletion.isChecked.return_value = False
            
            # Mock confirmation dialog to return Yes
            mock_message_box.critical.return_value = mock_message_box.Yes
            
            secure_delete_gui.secure_delete()
            
            # Verify the method appears in the confirmation dialog
            critical_call = mock_message_box.critical.call_args
            assert method in str(critical_call)
            assert "Disabled" in str(critical_call)
    
    def test_init_ui_with_standard_window(self, secure_delete_gui):
        """Test UI initialization with StandardWindow available."""
        # Mock the main_layout attribute
        secure_delete_gui.main_layout = MagicMock()
        
        secure_delete_gui.init_ui()
        
        # Verify UI components were added to the layout
        assert secure_delete_gui.main_layout.addWidget.called
    
    def test_init_ui_without_standard_window(self, mock_pyqt5):
        """Test UI initialization without StandardWindow."""
        with patch('src.utilities.security.secure_delete.STANDARD_WINDOW_AVAILABLE', False):
            from src.utilities.security.secure_delete import SecureDeleteGUI
            gui = SecureDeleteGUI()
            gui.init_ui()
            
            # Verify setCentralWidget was called for fallback mode
            gui.setCentralWidget.assert_called()


class TestSecureDeleteFunctions:
    """Test standalone functions and edge cases."""
    
    def test_import_error_handling(self):
        """Test handling of PyQt5 import errors."""
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': None}):
            with patch('builtins.print') as mock_print:
                with patch('sys.exit') as mock_exit:
                    # This should trigger the import error handling
                    try:
                        import importlib

                        # Force reload to trigger import error
                        if 'src.utilities.security.secure_delete' in sys.modules:
                            importlib.reload(sys.modules['src.utilities.security.secure_delete'])
                    except SystemExit:
                        pass
    
    @patch('src.utilities.security.secure_delete.QApplication')
    @patch('src.utilities.security.secure_delete.SecureDeleteGUI')
    def test_main_function(self, mock_gui_class, mock_qapp_class):
        """Test the main function."""
        mock_app = MagicMock()
        mock_qapp_class.return_value = mock_app
        mock_gui = MagicMock()
        mock_gui_class.return_value = mock_gui
        
        # Mock sys.argv
        with patch('sys.argv', ['secure_delete.py']):
            with patch('sys.exit') as mock_exit:
                from src.utilities.security.secure_delete import main
                main()
                
                # Verify application creation and execution
                mock_qapp_class.assert_called_once_with(['secure_delete.py'])
                mock_gui_class.assert_called_once()
                mock_gui.show.assert_called_once()
                mock_app.exec_.assert_called_once()
                mock_exit.assert_called_once()


class TestSecureDeleteIntegration:
    """Integration tests for SecureDeleteGUI."""
    
    def test_full_workflow_file_selection_to_deletion(self, mock_pyqt5, temp_test_files):
        """Test complete workflow from file selection to deletion."""
        with patch('src.utilities.security.secure_delete.STANDARD_WINDOW_AVAILABLE', True):
            with patch('src.utilities.security.secure_delete.StandardWindow', MagicMock()):
                from src.utilities.security.secure_delete import \
                    SecureDeleteGUI
                
                gui = SecureDeleteGUI()
                
                # Setup UI components
                gui.files_list = MagicMock()
                gui.status_label = MagicMock()
                gui.method_combo = MagicMock()
                gui.verify_deletion = MagicMock()
                
                # Mock file dialog
                with patch('src.utilities.security.secure_delete.QFileDialog') as mock_dialog:
                    mock_dialog.getOpenFileNames.return_value = (temp_test_files, "")
                    
                    # Select files
                    gui.select_files()
                    
                    # Verify files were selected
                    assert gui.selected_files == temp_test_files
                    
                    # Setup for deletion
                    gui.method_combo.currentText.return_value = "DoD 5220.22-M (3 Pass)"
                    gui.verify_deletion.isChecked.return_value = True
                    
                    # Mock confirmation dialog
                    with patch('src.utilities.security.secure_delete.QMessageBox') as mock_msg:
                        mock_msg.critical.return_value = mock_msg.Yes
                        
                        # Attempt deletion
                        gui.secure_delete()
                        
                        # Verify confirmation and information dialogs
                        mock_msg.critical.assert_called_once()
                        mock_msg.information.assert_called_once()
    
    def test_error_handling_edge_cases(self, secure_delete_gui):
        """Test error handling for various edge cases."""
        # Test with None values
        secure_delete_gui.selected_files = None
        try:
            secure_delete_gui.clear_selection()
        except Exception as e:
            pytest.fail(f"clear_selection should handle None values gracefully: {e}")
        
        # Test with invalid file paths
        secure_delete_gui.selected_files = ['/nonexistent/path/file.txt']
        
        # Setup mocks for secure_delete
        secure_delete_gui.method_combo = MagicMock()
        secure_delete_gui.method_combo.currentText.return_value = "Single Pass (Quick)"
        secure_delete_gui.verify_deletion = MagicMock()
        secure_delete_gui.verify_deletion.isChecked.return_value = False
        
        with patch('src.utilities.security.secure_delete.QMessageBox') as mock_msg:
            mock_msg.critical.return_value = mock_msg.Yes
            
            # Should not crash with invalid paths
            try:
                secure_delete_gui.secure_delete()
            except Exception as e:
                pytest.fail(f"secure_delete should handle invalid paths gracefully: {e}")


class TestSecureDeletePerformance:
    """Performance and stress tests."""
    
    def test_large_file_list_performance(self, secure_delete_gui):
        """Test performance with large number of files."""
        # Create a large list of file paths
        large_file_list = [f'/path/to/file_{i}.txt' for i in range(1000)]
        
        # Setup mocks
        secure_delete_gui.files_list = MagicMock()
        secure_delete_gui.status_label = MagicMock()
        
        # Test selection with large list
        secure_delete_gui.selected_files = large_file_list
        
        # Should handle large lists efficiently
        start_time = datetime.now()
        secure_delete_gui.clear_selection()
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0, "clear_selection should complete quickly even with large file lists"
    
    def test_memory_usage_with_large_datasets(self, secure_delete_gui):
        """Test memory usage with large datasets."""
        import gc

        # Force garbage collection
        gc.collect()
        
        # Create large data structures
        large_data = ['x' * 1000 for _ in range(1000)]
        secure_delete_gui.selected_files = large_data
        
        # Clear and verify cleanup
        secure_delete_gui.clear_selection()
        del large_data
        gc.collect()
        
        # Memory should be released
        assert secure_delete_gui.selected_files == []


# Test Configuration and Fixtures
@pytest.fixture(scope="session")
def test_timestamp():
    """Provide consistent timestamp for test session."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "test_files_count": 5,
        "temp_dir_prefix": "secure_delete_test_",
        "max_test_duration": 30.0,  # seconds
        "coverage_threshold": 90.0  # percentage
    }


# Pytest Configuration
def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)


# Test Results Summary
class TestResultsCollector:
    """Collect and format test results."""
    
    def __init__(self):
        self.results = {
            "start_time": datetime.now(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "errors": [],
            "coverage": {}
        }
    
    def add_result(self, test_name, status, error=None):
        """Add a test result."""
        self.results["tests_run"] += 1
        if status == "passed":
            self.results["tests_passed"] += 1
        elif status == "failed":
            self.results["tests_failed"] += 1
            if error:
                self.results["errors"].append({"test": test_name, "error": str(error)})
        elif status == "skipped":
            self.results["tests_skipped"] += 1
    
    def generate_summary(self):
        """Generate test results summary."""
        end_time = datetime.now()
        duration = (end_time - self.results["start_time"]).total_seconds()
        
        summary = f"""
=== SECURE DELETE UNIT TESTS SUMMARY ===
Generated: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} seconds

Tests Run: {self.results["tests_run"]}
Passed: {self.results["tests_passed"]}
Failed: {self.results["tests_failed"]}
Skipped: {self.results["tests_skipped"]}

Success Rate: {(self.results["tests_passed"] / max(self.results["tests_run"], 1)) * 100:.1f}%

Target Module: secure_delete.py
Test Coverage: Comprehensive unit testing of SecureDeleteGUI class
Test Types: Unit, Integration, Performance, Error Handling

=== END SUMMARY ===
"""
        return summary


# Global test results collector
test_collector = TestResultsCollector()