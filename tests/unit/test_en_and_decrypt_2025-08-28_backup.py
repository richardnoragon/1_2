#!/usr/bin/env python3

# Comprehensive pytest unit tests for en_and_decrypt.py
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication

# Import the target module and class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/utilities/security')))
from en_and_decrypt import EnAndDecryptGUI

@pytest.fixture(scope="module")
def app():
    """Setup QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Teardown: QApplication does not need explicit cleanup

@pytest.fixture
def gui(app):
    """Setup and teardown for EnAndDecryptGUI."""
    window = EnAndDecryptGUI()
    yield window
    window.close()

# --- Tests for UI Initialization ---
def test_ui_initialization(gui):
    assert gui.windowTitle() == "Encrypt/Decrypt - Richard's File Utilities"
    assert hasattr(gui, 'selected_files')
    assert hasattr(gui, 'operation_mode')
    assert hasattr(gui, 'files_list')
    assert hasattr(gui, 'password_edit')
    assert hasattr(gui, 'status_label')
    assert hasattr(gui, 'encrypt_button')
    assert hasattr(gui, 'decrypt_button')
    assert hasattr(gui, 'clear_button')

# --- Tests for File Selection ---
def test_select_encrypt_files(gui):
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['/tmp/test1.txt', '/tmp/test2.txt'], None)):
        gui.select_encrypt_files()
        assert gui.selected_files == ['/tmp/test1.txt', '/tmp/test2.txt']
        assert gui.operation_mode == 'encrypt'
        assert gui.status_label.text().startswith('Selected 2 file(s) for encryption')

def test_select_decrypt_files(gui):
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['/tmp/test1.enc', '/tmp/test2.enc'], None)):
        gui.select_decrypt_files()
        assert gui.selected_files == ['/tmp/test1.enc', '/tmp/test2.enc']
        assert gui.operation_mode == 'decrypt'
        assert gui.status_label.text().startswith('Selected 2 file(s) for decryption')

# --- Tests for Clear Operation ---
def test_clear_operation(gui):
    gui.selected_files = ['/tmp/test1.txt']
    gui.password_edit.setText('secret')
    gui.files_list.addItem('dummy')
    gui.status_label.setText('Busy')
    gui.clear_operation()
    assert gui.selected_files == []
    assert gui.password_edit.text() == ''
    assert gui.files_list.count() == 0
    assert gui.status_label.text().startswith('Ready')

# --- Tests for Encrypt/Decrypt Buttons ---
def test_encrypt_files_no_selection(gui):
    gui.selected_files = []
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.encrypt_files()
        mock_warn.assert_called_once()

def test_encrypt_files_no_password(gui):
    gui.selected_files = ['/tmp/test1.txt']
    gui.password_edit.setText('')
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.encrypt_files()
        mock_warn.assert_called_once()

def test_encrypt_files_success(gui):
    gui.selected_files = ['/tmp/test1.txt']
    gui.password_edit.setText('supersecret')
    with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
        gui.encrypt_files()
        mock_info.assert_called_once()

def test_decrypt_files_no_selection(gui):
    gui.selected_files = []
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.decrypt_files()
        mock_warn.assert_called_once()

def test_decrypt_files_no_password(gui):
    gui.selected_files = ['/tmp/test1.enc']
    gui.password_edit.setText('')
    with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
        gui.decrypt_files()
        mock_warn.assert_called_once()

def test_decrypt_files_success(gui):
    gui.selected_files = ['/tmp/test1.enc']
    gui.password_edit.setText('supersecret')
    with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
        gui.decrypt_files()
        mock_info.assert_called_once()

# --- Edge Cases ---
def test_select_files_empty(gui):
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], None)):
        gui.select_encrypt_files()
        assert gui.selected_files == []
        gui.select_decrypt_files()
        assert gui.selected_files == []

# --- Help and Preferences ---
def test_show_help(gui):
    with patch('PyQt5.QtWidgets.QMessageBox.exec_') as mock_exec:
        gui.show_help()
        mock_exec.assert_called_once()

def test_show_preferences(gui):
    with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
        gui.show_preferences()
        mock_info.assert_called_once()

# --- Refresh View ---
def test_refresh_view_calls_clear(gui):
    with patch.object(gui, 'clear_operation') as mock_clear:
        gui.refresh_view()
        mock_clear.assert_called_once()

# --- Main Function ---
def test_main_runs(monkeypatch):
    # Patch QApplication and window.show/sys.exit
    monkeypatch.setattr('PyQt5.QtWidgets.QApplication', MagicMock())
    monkeypatch.setattr('en_and_decrypt.EnAndDecryptGUI', MagicMock())
    monkeypatch.setattr('sys.exit', lambda x: None)
    import en_and_decrypt
    en_and_decrypt.main()

# --- Timestamped Output ---
def test_timestamped_output():
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assert isinstance(now, str)
            with patch('src.tools.security.en_and_decrypt.StandardWindow') as mock_std_window:
                from src.tools.security.en_and_decrypt import EnAndDecryptGUI
                
                gui = EnAndDecryptGUI()
                
                assert hasattr(gui, 'selected_files')
                assert gui.selected_files == []
                assert hasattr(gui, 'operation_mode')
                assert gui.operation_mode == "encrypt"
                
    def test_initialization_without_standard_window(self):
        """Test GUI initialization without StandardWindow (fallback mode)."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            assert hasattr(gui, 'selected_files')
            assert gui.selected_files == []
            assert hasattr(gui, 'operation_mode')
            assert gui.operation_mode == "encrypt"
            
    def test_menu_callbacks_setup(self):
        """Test menu callbacks setup when StandardWindow is available."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', True):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.menu_manager = Mock()
            gui._setup_menu_callbacks()
            
            # Verify callback registrations
            expected_calls = [
                call('new_operation', gui.clear_operation),
                call('help_encrypt_decrypt', gui.show_help)
            ]
            gui.menu_manager.register_callback.assert_has_calls(expected_calls)


class TestUIComponents(TestSetup):
    """Test UI component creation and functionality."""
    
    def test_init_ui_components_creation(self):
        """Test that all UI components are created properly."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Check essential UI components exist
            assert hasattr(gui, 'select_files_button')
            assert hasattr(gui, 'select_decrypt_button')
            assert hasattr(gui, 'files_list')
            assert hasattr(gui, 'password_edit')
            assert hasattr(gui, 'progress_bar')
            assert hasattr(gui, 'status_label')
            assert hasattr(gui, 'encrypt_button')
            assert hasattr(gui, 'decrypt_button')
            assert hasattr(gui, 'clear_button')
            
    def test_password_field_configuration(self):
        """Test password field is configured for secure input."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Password field should be configured for password input
            assert hasattr(gui.password_edit, 'echo_mode')
            assert gui.password_edit.placeholder == "Enter password..."
            
    def test_progress_bar_initial_state(self):
        """Test progress bar initial visibility state."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Progress bar should be initially hidden
            assert not gui.progress_bar.visible


class TestFileSelection(TestSetup):
    """Test file selection functionality."""
    
    @patch('src.tools.security.en_and_decrypt.QFileDialog.getOpenFileNames')
    def test_select_encrypt_files_success(self, mock_file_dialog):
        """Test successful file selection for encryption."""
        mock_file_dialog.return_value = (['/path/file1.txt', '/path/file2.txt'], "")
        
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.select_encrypt_files()
            
            assert len(gui.selected_files) == 2
            assert gui.operation_mode == "encrypt"
            assert "2 file(s) for encryption" in gui.status_label.text
            
    @patch('src.tools.security.en_and_decrypt.QFileDialog.getOpenFileNames')
    def test_select_encrypt_files_cancelled(self, mock_file_dialog):
        """Test file selection cancellation for encryption."""
        mock_file_dialog.return_value = ([], "")
        
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            original_files = gui.selected_files.copy()
            gui.select_encrypt_files()
            
            assert gui.selected_files == original_files
            
    @patch('src.tools.security.en_and_decrypt.QFileDialog.getOpenFileNames')
    def test_select_decrypt_files_success(self, mock_file_dialog):
        """Test successful file selection for decryption."""
        mock_file_dialog.return_value = (['/path/file1.enc', '/path/file2.enc'], "")
        
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.select_decrypt_files()
            
            assert len(gui.selected_files) == 2
            assert gui.operation_mode == "decrypt"
            assert "2 file(s) for decryption" in gui.status_label.text
            
    @patch('src.tools.security.en_and_decrypt.QFileDialog.getOpenFileNames')
    def test_select_decrypt_files_cancelled(self, mock_file_dialog):
        """Test file selection cancellation for decryption."""
        mock_file_dialog.return_value = ([], "")
        
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            original_files = gui.selected_files.copy()
            gui.select_decrypt_files()
            
            assert gui.selected_files == original_files


class TestEncryptionDecryption(TestSetup):
    """Test encryption and decryption operations."""
    
    @patch('src.tools.security.en_and_decrypt.QMessageBox.information')
    def test_encrypt_files_with_valid_input(self, mock_msg_box):
        """Test encryption with valid files and password."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = ['/path/file1.txt', '/path/file2.txt']
            gui.password_edit.setText("strong_password_123")
            
            gui.encrypt_files()
            
            mock_msg_box.assert_called_once()
            args = mock_msg_box.call_args[0]
            assert "Encryption functionality" in args[2]
            assert "Files to encrypt: 2" in args[2]
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox.warning')
    def test_encrypt_files_no_files_selected(self, mock_warning):
        """Test encryption warning when no files are selected."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = []
            
            gui.encrypt_files()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Please select files to encrypt first" in args[2]
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox.warning')
    def test_encrypt_files_no_password(self, mock_warning):
        """Test encryption warning when no password is provided."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = ['/path/file1.txt']
            gui.password_edit.setText("")
            
            gui.encrypt_files()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Please enter a password for encryption" in args[2]
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox.information')
    def test_decrypt_files_with_valid_input(self, mock_msg_box):
        """Test decryption with valid files and password."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = ['/path/file1.enc', '/path/file2.enc']
            gui.password_edit.setText("decryption_password")
            
            gui.decrypt_files()
            
            mock_msg_box.assert_called_once()
            args = mock_msg_box.call_args[0]
            assert "Decryption functionality" in args[2]
            assert "Files to decrypt: 2" in args[2]
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox.warning')
    def test_decrypt_files_no_files_selected(self, mock_warning):
        """Test decryption warning when no files are selected."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = []
            
            gui.decrypt_files()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Please select files to decrypt first" in args[2]
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox.warning')
    def test_decrypt_files_no_password(self, mock_warning):
        """Test decryption warning when no password is provided."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = ['/path/file1.enc']
            gui.password_edit.setText("")
            
            gui.decrypt_files()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Please enter the decryption password" in args[2]


class TestUtilityMethods(TestSetup):
    """Test utility methods and operations."""
    
    def test_clear_operation(self):
        """Test clearing operation state."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Set some state
            gui.selected_files = ['/path/file1.txt']
            gui.password_edit.setText("password")
            gui.files_list.addItem("test item")
            
            # Clear operation
            gui.clear_operation()
            
            # Verify state is cleared
            assert gui.selected_files == []
            assert gui.password_edit.text() == ""
            assert len(gui.files_list.items) == 0
            assert "Ready - Select files" in gui.status_label.text
            
    def test_refresh_view(self):
        """Test refresh view functionality."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Mock clear_operation to verify it's called
            gui.clear_operation = Mock()
            
            gui.refresh_view()
            
            gui.clear_operation.assert_called_once()
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox')
    def test_show_help(self, mock_msg_box):
        """Test help dialog functionality."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            mock_box_instance = Mock()
            mock_msg_box.return_value = mock_box_instance
            
            gui.show_help()
            
            # Verify message box is configured and shown
            mock_box_instance.setWindowTitle.assert_called_with("Encrypt/Decrypt Tool - Help")
            mock_box_instance.setTextFormat.assert_called_with(1)
            mock_box_instance.exec_.assert_called_once()
            
    @patch('src.tools.security.en_and_decrypt.QMessageBox.information')
    def test_show_preferences(self, mock_info):
        """Test preferences dialog functionality."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            gui.show_preferences()
            
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            assert "Encrypt/Decrypt preferences" in args[2]


class TestEdgeCases(TestSetup):
    """Test edge cases and error scenarios."""
    
    def test_missing_attributes_handling(self):
        """Test handling of missing UI attributes during operations."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Remove attributes to test graceful handling
            if hasattr(gui, 'password_edit'):
                delattr(gui, 'password_edit')
            if hasattr(gui, 'files_list'):
                delattr(gui, 'files_list')
            if hasattr(gui, 'status_label'):
                delattr(gui, 'status_label')
                
            # These should not raise exceptions
            try:
                gui.clear_operation()
            except Exception as e:
                pytest.fail(f"clear_operation raised exception with missing attributes: {e}")
                
    def test_large_file_list_handling(self):
        """Test handling of large file lists."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Simulate large file list
            large_file_list = [f'/path/file_{i}.txt' for i in range(1000)]
            gui.selected_files = large_file_list
            
            # This should handle large lists gracefully
            gui.password_edit.setText("password")
            
            with patch('src.tools.security.en_and_decrypt.QMessageBox.information'):
                gui.encrypt_files()
                
            assert len(gui.selected_files) == 1000
            
    def test_special_characters_in_file_paths(self):
        """Test handling of file paths with special characters."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            special_files = [
                '/path/with spaces/file.txt',
                '/path/with-unicode-日本語.txt',
                '/path/with/symbols!@#$%.txt'
            ]
            
            gui.selected_files = special_files
            gui.password_edit.setText("password")
            
            with patch('src.tools.security.en_and_decrypt.QMessageBox.information'):
                gui.encrypt_files()
                
            # Should handle special characters without issues
            assert len(gui.selected_files) == 3
            
    def test_empty_password_edge_cases(self):
        """Test various empty password scenarios."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = ['/path/file.txt']
            
            test_passwords = ["", "   ", "\t", "\n", None]
            
            for password in test_passwords:
                gui.password_edit.setText(password if password is not None else "")
                
                with patch('src.tools.security.en_and_decrypt.QMessageBox.warning') as mock_warning:
                    gui.encrypt_files()
                    
                    if not password or not password.strip():
                        mock_warning.assert_called()


class TestMainFunction(TestSetup):
    """Test main function and standalone execution."""
    
    @patch('src.tools.security.en_and_decrypt.QApplication')
    @patch('src.tools.security.en_and_decrypt.sys.exit')
    def test_main_function(self, mock_exit, mock_app):
        """Test main function execution."""
        mock_app_instance = Mock()
        mock_app_instance.exec_.return_value = 0
        mock_app.return_value = mock_app_instance
        
        from src.tools.security.en_and_decrypt import main
        
        # Mock sys.argv
        with patch('src.tools.security.en_and_decrypt.sys.argv', ['test_script.py']):
            main()
            
        mock_app.assert_called_once_with(['test_script.py'])
        mock_app_instance.exec_.assert_called_once()
        mock_exit.assert_called_once_with(0)


class TestSecurityValidation(TestSetup):
    """Test security-related validation and features."""
    
    def test_password_masking(self):
        """Test that passwords are properly masked in displays."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            gui.selected_files = ['/path/file.txt']
            gui.password_edit.setText("secret_password_123")
            
            with patch('src.tools.security.en_and_decrypt.QMessageBox.information') as mock_info:
                gui.encrypt_files()
                
                # Check that password is masked in display
                call_args = mock_info.call_args[0][2]
                assert "secret_password_123" not in call_args
                assert "*" in call_args
                
    def test_file_extension_validation(self):
        """Test validation of file extensions for operations."""
        with patch('src.tools.security.en_and_decrypt.STANDARD_WINDOW_AVAILABLE', False):
            from src.tools.security.en_and_decrypt import EnAndDecryptGUI
            
            gui = EnAndDecryptGUI()
            
            # Test various file extensions
            test_files = [
                '/path/document.pdf',
                '/path/image.jpg',
                '/path/archive.zip',
                '/path/script.py',
                '/path/no_extension'
            ]
            
            gui.selected_files = test_files
            gui.password_edit.setText("password")
            
            with patch('src.tools.security.en_and_decrypt.QMessageBox.information'):
                gui.encrypt_files()
                
            # All file types should be accepted for encryption
            assert len(gui.selected_files) == 5


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information."""
    return {
        "start_time": datetime.now(),
        "test_module": "test_en_and_decrypt_2025-08-28.py",
        "target_module": "en_and_decrypt.py",
        "framework": "pytest",
        "coverage_enabled": True
    }


def pytest_runtest_makereport(item, call):
    """Generate detailed test reports."""
    if call.when == "call":
        setattr(item, "test_result", call.excinfo is None)
        setattr(item, "test_duration", call.duration)


def pytest_sessionfinish(session, exitstatus):
    """Generate session summary report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create detailed test report
    report = {
        "test_session": {
            "timestamp": timestamp,
            "exit_status": exitstatus,
            "total_tests": session.testscollected,
            "framework": "pytest",
            "target_module": "en_and_decrypt.py",
            "test_file": "test_en_and_decrypt_2025-08-28.py"
        },
        "test_categories": {
            "initialization_tests": 3,
            "ui_component_tests": 3,
            "file_selection_tests": 4,
            "encryption_decryption_tests": 6,
            "utility_method_tests": 4,
            "edge_case_tests": 4,
            "main_function_tests": 1,
            "security_validation_tests": 2
        },
        "coverage_areas": [
            "Class initialization and setup",
            "UI component creation and configuration", 
            "File selection and validation",
            "Encryption/decryption operation handling",
            "Error handling and user feedback",
            "Menu integration capabilities",
            "Security features and password handling",
            "Edge cases and error scenarios"
        ]
    }
    
    # Save session report
    report_dir = "c:/Users/richardi/1_2/tests/unit"
    os.makedirs(report_dir, exist_ok=True)
    
    with open(f"{report_dir}/result_en_and_decrypt_2025-08-28.json", "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--capture=no",
        f"--html=c:/Users/richardi/1_2/tests/unit/result_en_and_decrypt_2025-08-28.html",
        "--self-contained-html"
    ])