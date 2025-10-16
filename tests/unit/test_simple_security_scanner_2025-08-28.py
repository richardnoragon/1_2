#!/usr/bin/env python3
"""
Comprehensive Unit Tests for security_scanner.py
Generated on: 2025-08-28
Test Framework: pytest

This module contains comprehensive unit tests for the SecurityScanWorker and 
SimpleSecurityScannerGUI classes, covering functionality, edge cases, error handling,
network operations, file system operations, and platform-specific behavior.
"""

import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

# Add the source directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Mock PyQt5 before importing the module under test
@pytest.fixture(autouse=True)
def mock_pyqt5():
    """Mock PyQt5 components to avoid GUI dependencies in tests."""
    mock_widgets = MagicMock()
    mock_core = MagicMock()
    mock_gui = MagicMock()
    
    # Mock all PyQt5 widgets used in the module
    mock_widgets.QMainWindow = MagicMock()
    mock_widgets.QWidget = MagicMock()
    mock_widgets.QVBoxLayout = MagicMock()
    mock_widgets.QHBoxLayout = MagicMock()
    mock_widgets.QPushButton = MagicMock()
    mock_widgets.QLabel = MagicMock()
    mock_widgets.QProgressBar = MagicMock()
    mock_widgets.QApplication = MagicMock()
    mock_widgets.QMessageBox = MagicMock()
    mock_widgets.QGroupBox = MagicMock()
    mock_widgets.QTextEdit = MagicMock()
    mock_widgets.QCheckBox = MagicMock()
    mock_widgets.QTabWidget = MagicMock()
    
    # Mock Qt core components
    mock_core.Qt = MagicMock()
    mock_core.Qt.AlignCenter = 0x0004
    mock_core.QThread = MagicMock()
    mock_core.pyqtSignal = MagicMock()
    
    # Mock Qt GUI components
    mock_gui.QFont = MagicMock()
    mock_gui.QFont.Bold = 75
    
    with patch.dict('sys.modules', {
        'PyQt5.QtWidgets': mock_widgets,
        'PyQt5.QtCore': mock_core,
        'PyQt5.QtGui': mock_gui
    }):
        yield {
            'widgets': mock_widgets,
            'core': mock_core,
            'gui': mock_gui
        }


class TestSecurityScanWorker:
    """Test class for SecurityScanWorker functionality."""
    
    @pytest.fixture
    def security_scan_worker(self, mock_pyqt5):
        """Create a SecurityScanWorker instance for testing."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        scan_types = ["system_info", "network_ports", "file_permissions", "running_processes"]
        return SecurityScanWorker(scan_types)
    
    def test_init_with_scan_types(self, mock_pyqt5, security_scan_worker):
        """Test SecurityScanWorker initialization with scan types."""
        assert security_scan_worker is not None
        assert security_scan_worker.scan_types == ["system_info", "network_ports", "file_permissions", "running_processes"]
    
    def test_init_with_empty_scan_types(self, mock_pyqt5):
        """Test SecurityScanWorker initialization with empty scan types."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        worker = SecurityScanWorker([])
        assert worker.scan_types == []
    
    def test_init_with_single_scan_type(self, mock_pyqt5):
        """Test SecurityScanWorker initialization with single scan type."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        worker = SecurityScanWorker(["system_info"])
        assert worker.scan_types == ["system_info"]
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    def test_scan_system_info_success(self, mock_platform, security_scan_worker):
        """Test successful system information scanning."""
        # Mock platform module
        mock_platform.system.return_value = "Windows"
        mock_platform.release.return_value = "10"
        mock_platform.machine.return_value = "AMD64"
        mock_platform.python_version.return_value = "3.9.0"
        
        # Mock socket.gethostname
        with patch('tools.security.security_scanner.security_scanner.socket.gethostname', return_value="TestHost"):
            result = security_scan_worker.scan_system_info()
        
        # Verify result contains expected information
        assert "=== SYSTEM INFORMATION ===" in result
        assert "Operating System: Windows 10" in result
        assert "Machine Type: AMD64" in result
        assert "Python Version: 3.9.0" in result
        assert "Hostname: TestHost" in result
        assert "Windows Defender Status" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    def test_scan_system_info_linux(self, mock_platform, security_scan_worker):
        """Test system information scanning on Linux."""
        # Mock platform module for Linux
        mock_platform.system.return_value = "Linux"
        mock_platform.release.return_value = "5.4.0"
        mock_platform.machine.return_value = "x86_64"
        mock_platform.python_version.return_value = "3.8.5"
        
    with patch('tools.security.security_scanner.security_scanner.socket.gethostname', return_value="LinuxHost"):
            result = security_scan_worker.scan_system_info()
        
        assert "Operating System: Linux 5.4.0" in result
        assert "Windows Defender Status" not in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    def test_scan_system_info_exception_handling(self, mock_platform, security_scan_worker):
        """Test system information scanning with exception."""
        # Mock platform to raise exception
        mock_platform.system.side_effect = Exception("Platform error")
        
        result = security_scan_worker.scan_system_info()
        assert "System info scan error: Platform error" in result
    
    @patch('tools.security.security_scanner.security_scanner.socket')
    def test_scan_network_ports_success(self, mock_socket, security_scan_worker):
        """Test successful network port scanning."""
        # Mock socket operations
        mock_sock = MagicMock()
        mock_socket.socket.return_value = mock_sock
        mock_socket.AF_INET = socket.AF_INET
        mock_socket.SOCK_STREAM = socket.SOCK_STREAM
        
        # Mock some ports as open (return 0) and others as closed (return 1)
        mock_sock.connect_ex.side_effect = lambda addr: 0 if addr[1] in [80, 443] else 1
        
        result = security_scan_worker.scan_network_ports()
        
        # Verify result
        assert "=== NETWORK PORT SCAN ===" in result
        assert "Open ports found: 80, 443" in result
        assert "⚠️  Review open ports for security implications" in result
        
        # Verify socket operations
        assert mock_socket.socket.call_count >= 1
        assert mock_sock.settimeout.call_count >= 1
        assert mock_sock.close.call_count >= 1
    
    @patch('tools.security.security_scanner.security_scanner.socket')
    def test_scan_network_ports_no_open_ports(self, mock_socket, security_scan_worker):
        """Test network port scanning with no open ports."""
        # Mock socket operations
        mock_sock = MagicMock()
        mock_socket.socket.return_value = mock_sock
        mock_socket.AF_INET = socket.AF_INET
        mock_socket.SOCK_STREAM = socket.SOCK_STREAM
        
        # Mock all ports as closed (return 1)
        mock_sock.connect_ex.return_value = 1
        
        result = security_scan_worker.scan_network_ports()
        
        assert "=== NETWORK PORT SCAN ===" in result
        assert "✅ No common ports found open on localhost" in result
    
    @patch('tools.security.security_scanner.security_scanner.socket')
    def test_scan_network_ports_exception_handling(self, mock_socket, security_scan_worker):
        """Test network port scanning with exception."""
        # Mock socket to raise exception
        mock_socket.socket.side_effect = Exception("Network error")
        
        result = security_scan_worker.scan_network_ports()
        assert "Network scan error: Network error" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.os')
    def test_scan_file_permissions_windows(self, mock_os, mock_platform, security_scan_worker):
        """Test file permissions scanning on Windows."""
        # Mock platform
        mock_platform.system.return_value = "Windows"
        
        # Mock os.path.expanduser and os.path.exists
        mock_os.path.expanduser.side_effect = lambda path: path.replace("~", "C:\\Users\\Test")
        mock_os.path.exists.return_value = True
        
        # Mock os.access
        mock_os.access.return_value = True
        mock_os.R_OK = 4
        mock_os.W_OK = 2
        mock_os.X_OK = 1
        
        result = security_scan_worker.scan_file_permissions()
        
        assert "=== FILE PERMISSIONS CHECK ===" in result
        assert "C:\\Users\\Test\\Documents: RWX" in result
        assert "C:\\Users\\Test\\Downloads: RWX" in result
        assert "C:\\Windows\\System32: RWX" in result
        assert "✅ File permission scan completed" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.os')
    def test_scan_file_permissions_unix(self, mock_os, mock_platform, security_scan_worker):
        """Test file permissions scanning on Unix-like systems."""
        # Mock platform
        mock_platform.system.return_value = "Linux"
        
        # Mock os.path.expanduser and os.path.exists
        mock_os.path.expanduser.side_effect = lambda path: path.replace("~", "/home/test")
        mock_os.path.exists.return_value = True
        
        # Mock os.access - only readable, not writable
        def mock_access(path, mode):
            if mode == 4:  # R_OK
                return True
            elif mode == 2:  # W_OK
                return False
            elif mode == 1:  # X_OK
                return True
            return False
        
        mock_os.access.side_effect = mock_access
        mock_os.R_OK = 4
        mock_os.W_OK = 2
        mock_os.X_OK = 1
        
        result = security_scan_worker.scan_file_permissions()
        
        assert "=== FILE PERMISSIONS CHECK ===" in result
        assert "/home/test/Documents: RX" in result
        assert "/etc: RX" in result
        assert "/var: RX" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.os')
    def test_scan_file_permissions_nonexistent_directory(self, mock_os, mock_platform, security_scan_worker):
        """Test file permissions scanning with nonexistent directory."""
        # Mock platform
        mock_platform.system.return_value = "Windows"
        
        # Mock os.path.expanduser and os.path.exists
        mock_os.path.expanduser.side_effect = lambda path: path.replace("~", "C:\\Users\\Test")
        mock_os.path.exists.return_value = False
        
        result = security_scan_worker.scan_file_permissions()
        
        assert "=== FILE PERMISSIONS CHECK ===" in result
        assert "✅ File permission scan completed" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.os')
    def test_scan_file_permissions_access_error(self, mock_os, mock_platform, security_scan_worker):
        """Test file permissions scanning with access error."""
        # Mock platform
        mock_platform.system.return_value = "Windows"
        
        # Mock os.path.expanduser and os.path.exists
        mock_os.path.expanduser.side_effect = lambda path: path.replace("~", "C:\\Users\\Test")
        mock_os.path.exists.return_value = True
        
        # Mock os.access to raise exception
        mock_os.access.side_effect = Exception("Access denied")
        
        result = security_scan_worker.scan_file_permissions()
        
        assert "Error checking permissions - Access denied" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.subprocess')
    def test_scan_running_processes_windows(self, mock_subprocess, mock_platform, security_scan_worker):
        """Test running processes scanning on Windows."""
        # Mock platform
        mock_platform.system.return_value = "Windows"
        
        # Mock subprocess output
        mock_output = """Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
System Idle Process              0 Services                   0          4 K
System                           4 Services                   0      1,234 K
smss.exe                       123 Services                   0        567 K
csrss.exe                      456 Services                   0      2,345 K"""
        
        mock_subprocess.check_output.return_value = mock_output
        
        result = security_scan_worker.scan_running_processes()
        
        assert "=== RUNNING PROCESSES ANALYSIS ===" in result
        assert "Top running processes:" in result
        assert "System" in result
        assert "smss.exe" in result
        assert "✅ Process analysis completed" in result
        
        # Verify subprocess was called with correct command
        mock_subprocess.check_output.assert_called_with(['tasklist'], universal_newlines=True)
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.subprocess')
    def test_scan_running_processes_unix(self, mock_subprocess, mock_platform, security_scan_worker):
        """Test running processes scanning on Unix-like systems."""
        # Mock platform
        mock_platform.system.return_value = "Linux"
        
        # Mock subprocess output
        mock_output = """USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  19356  1234 ?        Ss   08:00   0:01 /sbin/init
root         2  0.0  0.0      0     0 ?        S    08:00   0:00 [kthreadd]
root         3  0.0  0.0      0     0 ?        S    08:00   0:00 [ksoftirqd/0]"""
        
        mock_subprocess.check_output.return_value = mock_output
        
        result = security_scan_worker.scan_running_processes()
        
        assert "=== RUNNING PROCESSES ANALYSIS ===" in result
        assert "Top running processes:" in result
        assert "/sbin/init" in result
        assert "kthreadd" in result
        assert "✅ Process analysis completed" in result
        
        # Verify subprocess was called with correct command
        mock_subprocess.check_output.assert_called_with(['ps', 'aux'], universal_newlines=True)
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    @patch('tools.security.security_scanner.security_scanner.subprocess')
    def test_scan_running_processes_exception(self, mock_subprocess, mock_platform, security_scan_worker):
        """Test running processes scanning with subprocess exception."""
        # Mock platform
        mock_platform.system.return_value = "Windows"
        
        # Mock subprocess to raise exception
        mock_subprocess.check_output.side_effect = Exception("Command failed")
        
        result = security_scan_worker.scan_running_processes()
        
        assert "Could not retrieve process list" in result
    
    @patch('tools.security.security_scanner.security_scanner.platform')
    def test_scan_running_processes_exception_handling(self, mock_platform, security_scan_worker):
        """Test running processes scanning with general exception."""
        # Mock platform to raise exception
        mock_platform.system.side_effect = Exception("Platform error")
        
        result = security_scan_worker.scan_running_processes()
        assert "Process scan error: Platform error" in result
    
    def test_run_method_all_scans(self, mock_pyqt5, security_scan_worker):
        """Test the run method with all scan types."""
        # Mock all scan methods
        security_scan_worker.scan_system_info = MagicMock(return_value="System info result")
        security_scan_worker.scan_network_ports = MagicMock(return_value="Network ports result")
        security_scan_worker.scan_file_permissions = MagicMock(return_value="File permissions result")
        security_scan_worker.scan_running_processes = MagicMock(return_value="Running processes result")
        
        # Mock signals
        security_scan_worker.progress_updated = MagicMock()
        security_scan_worker.status_updated = MagicMock()
        security_scan_worker.result_ready = MagicMock()
        
        security_scan_worker.run()
        
        # Verify all scan methods were called
        security_scan_worker.scan_system_info.assert_called_once()
        security_scan_worker.scan_network_ports.assert_called_once()
        security_scan_worker.scan_file_permissions.assert_called_once()
        security_scan_worker.scan_running_processes.assert_called_once()
        
        # Verify signals were emitted
        assert security_scan_worker.progress_updated.emit.call_count >= 4
        assert security_scan_worker.status_updated.emit.call_count >= 4
        security_scan_worker.result_ready.emit.assert_called_once()
    
    def test_run_method_unknown_scan_type(self, mock_pyqt5):
        """Test the run method with unknown scan type."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        worker = SecurityScanWorker(["unknown_scan"])
        
        # Mock signals
        worker.progress_updated = MagicMock()
        worker.status_updated = MagicMock()
        worker.result_ready = MagicMock()
        
        worker.run()
        
        # Verify unknown scan type is handled
        worker.result_ready.emit.assert_called_once()
        result_call = worker.result_ready.emit.call_args[0][0]
        assert "Unknown scan type: unknown_scan" in result_call


class TestSimpleSecurityScannerGUI:
    """Test class for SimpleSecurityScannerGUI functionality."""
    
    @pytest.fixture
    def security_scanner_gui(self, mock_pyqt5):
        """Create a SimpleSecurityScannerGUI instance for testing."""
        from tools.security.security_scanner.security_scanner import \
            SimpleSecurityScannerGUI
        return SimpleSecurityScannerGUI()
    
    def test_init_basic_initialization(self, mock_pyqt5, security_scanner_gui):
        """Test basic initialization of SimpleSecurityScannerGUI."""
        assert security_scanner_gui is not None
        
        # Verify window title and size settings
        security_scanner_gui.setWindowTitle.assert_called_with(
            "Security Scanner - Richard's File Utilities"
        )
        security_scanner_gui.setMinimumSize.assert_called_with(800, 700)
        security_scanner_gui.resize.assert_called_with(900, 800)
    
    def test_init_styling_applied(self, mock_pyqt5, security_scanner_gui):
        """Test that styling is properly applied during initialization."""
        # Verify setStyleSheet was called
        security_scanner_gui.setStyleSheet.assert_called_once()
        
        # Get the style sheet content
        style_call = security_scanner_gui.setStyleSheet.call_args[0][0]
        
        # Verify key styling elements
        assert "QMainWindow" in style_call
        assert "background-color" in style_call
        assert "QPushButton" in style_call
        assert "#FF6B35" in style_call  # Button color
    
    def test_setup_ui_method_called(self, mock_pyqt5, security_scanner_gui):
        """Test that _setup_ui method is called during initialization."""
        # Verify _setup_ui was called by checking if UI components were set up
        security_scanner_gui.setCentralWidget.assert_called_once()
    
    def test_start_scan_with_all_options(self, mock_pyqt5, security_scanner_gui):
        """Test start_scan with all scan options selected."""
        # Mock checkbox states - all selected
        security_scanner_gui.system_info_check = MagicMock()
        security_scanner_gui.network_ports_check = MagicMock()
        security_scanner_gui.file_permissions_check = MagicMock()
        security_scanner_gui.running_processes_check = MagicMock()
        security_scanner_gui.start_scan_btn = MagicMock()
        security_scanner_gui.progress_bar = MagicMock()
        security_scanner_gui.results_text = MagicMock()
        
        security_scanner_gui.system_info_check.isChecked.return_value = True
        security_scanner_gui.network_ports_check.isChecked.return_value = True
        security_scanner_gui.file_permissions_check.isChecked.return_value = True
        security_scanner_gui.running_processes_check.isChecked.return_value = True
        
        # Mock SecurityScanWorker
        with patch('tools.security.security_scanner.security_scanner.SecurityScanWorker') as mock_worker_class:
            mock_worker = MagicMock()
            mock_worker_class.return_value = mock_worker
            
            security_scanner_gui.start_scan()
            
            # Verify worker was created with correct scan types
            expected_scan_types = ["system_info", "network_ports", "file_permissions", "running_processes"]
            mock_worker_class.assert_called_once_with(expected_scan_types)
            
            # Verify UI updates
            security_scanner_gui.start_scan_btn.setEnabled.assert_called_with(False)
            security_scanner_gui.progress_bar.setVisible.assert_called_with(True)
            security_scanner_gui.progress_bar.setValue.assert_called_with(0)
            security_scanner_gui.results_text.clear.assert_called_once()
    
    def test_start_scan_with_partial_options(self, mock_pyqt5, security_scanner_gui):
        """Test start_scan with only some scan options selected."""
        # Mock checkbox states - only system info and network ports
        security_scanner_gui.system_info_check = MagicMock()
        security_scanner_gui.network_ports_check = MagicMock()
        security_scanner_gui.file_permissions_check = MagicMock()
        security_scanner_gui.running_processes_check = MagicMock()
        security_scanner_gui.start_scan_btn = MagicMock()
        security_scanner_gui.progress_bar = MagicMock()
        security_scanner_gui.results_text = MagicMock()
        
        security_scanner_gui.system_info_check.isChecked.return_value = True
        security_scanner_gui.network_ports_check.isChecked.return_value = True
        security_scanner_gui.file_permissions_check.isChecked.return_value = False
        security_scanner_gui.running_processes_check.isChecked.return_value = False
        
        with patch('tools.security.security_scanner.security_scanner.SecurityScanWorker') as mock_worker_class:
            security_scanner_gui.start_scan()
            
            # Verify worker was created with correct scan types
            expected_scan_types = ["system_info", "network_ports"]
            mock_worker_class.assert_called_once_with(expected_scan_types)
    
    def test_start_scan_no_options_selected(self, mock_pyqt5, security_scanner_gui):
        """Test start_scan with no scan options selected."""
        # Mock checkbox states - none selected
        security_scanner_gui.system_info_check = MagicMock()
        security_scanner_gui.network_ports_check = MagicMock()
        security_scanner_gui.file_permissions_check = MagicMock()
        security_scanner_gui.running_processes_check = MagicMock()
        
        security_scanner_gui.system_info_check.isChecked.return_value = False
        security_scanner_gui.network_ports_check.isChecked.return_value = False
        security_scanner_gui.file_permissions_check.isChecked.return_value = False
        security_scanner_gui.running_processes_check.isChecked.return_value = False
        
        security_scanner_gui.start_scan()
        
        # Verify warning was shown
        mock_pyqt5['widgets'].QMessageBox.warning.assert_called_once_with(
            security_scanner_gui, "Warning", "Please select at least one scan type!"
        )
    
    def test_update_progress(self, security_scanner_gui):
        """Test progress bar update."""
        security_scanner_gui.progress_bar = MagicMock()
        
        security_scanner_gui.update_progress(50)
        
        security_scanner_gui.progress_bar.setValue.assert_called_once_with(50)
    
    def test_update_status(self, security_scanner_gui):
        """Test status label update."""
        security_scanner_gui.status_label = MagicMock()
        
        security_scanner_gui.update_status("Scanning network ports...")
        
        security_scanner_gui.status_label.setText.assert_called_once_with("Scanning network ports...")
    
    def test_display_results(self, security_scanner_gui):
        """Test results display."""
        security_scanner_gui.results_text = MagicMock()
        
        test_results = "Test scan results"
        security_scanner_gui.display_results(test_results)
        
        security_scanner_gui.results_text.setPlainText.assert_called_once_with(test_results)
    
    def test_scan_finished(self, security_scanner_gui):
        """Test scan completion handling."""
        security_scanner_gui.start_scan_btn = MagicMock()
        security_scanner_gui.progress_bar = MagicMock()
        security_scanner_gui.status_label = MagicMock()
        
        security_scanner_gui.scan_finished()
        
        security_scanner_gui.start_scan_btn.setEnabled.assert_called_once_with(True)
        security_scanner_gui.progress_bar.setVisible.assert_called_once_with(False)
        security_scanner_gui.status_label.setText.assert_called_once_with("Scan completed")
    
    def test_clear_results(self, security_scanner_gui):
        """Test results clearing."""
        security_scanner_gui.results_text = MagicMock()
        security_scanner_gui.status_label = MagicMock()
        
        security_scanner_gui.clear_results()
        
        security_scanner_gui.results_text.clear.assert_called_once()
        security_scanner_gui.status_label.setText.assert_called_once_with("Results cleared")


class TestSimpleSecurityScannerEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def worker_single_scan(self, mock_pyqt5):
        """Create a SecurityScanWorker instance for testing."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        return SecurityScanWorker(["system_info"])
    
    def test_empty_subprocess_output(self, mock_pyqt5, worker_single_scan):
        """Test handling of empty subprocess output."""
        with patch('tools.security.security_scanner.security_scanner.platform.system', return_value="Windows"):
            with patch('tools.security.security_scanner.security_scanner.subprocess.check_output', return_value=""):
                result = worker_single_scan.scan_running_processes()
                
                assert "=== RUNNING PROCESSES ANALYSIS ===" in result
                assert "✅ Process analysis completed" in result
    
    def test_network_timeout_simulation(self, mock_pyqt5, worker_single_scan):
        """Test network scanning with timeout simulation."""
        with patch('tools.security.security_scanner.security_scanner.socket') as mock_socket:
            # Simulate socket timeout
            mock_sock = MagicMock()
            mock_socket.socket.return_value = mock_sock
            mock_sock.connect_ex.side_effect = socket.timeout("Connection timeout")
            
            # Should handle timeout gracefully
            result = worker_single_scan.scan_network_ports()
            assert "Network scan error" in result
    
    def test_file_permission_with_special_characters(self, mock_pyqt5, worker_single_scan):
        """Test file permission scanning with special characters in paths."""
        with patch('tools.security.security_scanner.security_scanner.platform.system', return_value="Windows"):
            with patch('tools.security.security_scanner.security_scanner.os.path.expanduser') as mock_expanduser:
                with patch('tools.security.security_scanner.security_scanner.os.path.exists', return_value=True):
                    with patch('tools.security.security_scanner.security_scanner.os.access', return_value=True):
                        # Test path with special characters
                        mock_expanduser.return_value = "C:\\Users\\Test (Special)\\Documents"
                        
                        result = worker_single_scan.scan_file_permissions()
                        assert "✅ File permission scan completed" in result


class TestSimpleSecurityScannerIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def gui_for_integration(self, mock_pyqt5):
        """Create a SimpleSecurityScannerGUI instance for testing."""
        from tools.security.security_scanner.security_scanner import \
            SimpleSecurityScannerGUI
        return SimpleSecurityScannerGUI()
    
    def test_complete_scan_workflow(self, mock_pyqt5, gui_for_integration):
        """Test complete scan workflow from start to finish."""
        # Setup UI mocks
        gui_for_integration.system_info_check = MagicMock()
        gui_for_integration.network_ports_check = MagicMock()
        gui_for_integration.file_permissions_check = MagicMock()
        gui_for_integration.running_processes_check = MagicMock()
        gui_for_integration.start_scan_btn = MagicMock()
        gui_for_integration.progress_bar = MagicMock()
        gui_for_integration.results_text = MagicMock()
        gui_for_integration.status_label = MagicMock()
        
        # Configure scan options
        gui_for_integration.system_info_check.isChecked.return_value = True
        gui_for_integration.network_ports_check.isChecked.return_value = False
        gui_for_integration.file_permissions_check.isChecked.return_value = False
        gui_for_integration.running_processes_check.isChecked.return_value = False
        
        # Mock worker and its methods
        with patch('tools.security.security_scanner.security_scanner.SecurityScanWorker') as mock_worker_class:
            mock_worker = MagicMock()
            mock_worker_class.return_value = mock_worker
            
            # Start scan
            gui_for_integration.start_scan()
            
            # Simulate progress updates
            gui_for_integration.update_progress(25)
            gui_for_integration.update_progress(50)
            gui_for_integration.update_progress(100)
            
            # Simulate status updates
            gui_for_integration.update_status("Scanning system information...")
            gui_for_integration.update_status("Scan completed")
            
            # Simulate results
            test_results = "=== SYSTEM INFORMATION ===\nTest results"
            gui_for_integration.display_results(test_results)
            
            # Simulate scan completion
            gui_for_integration.scan_finished()
            
            # Verify workflow
            mock_worker_class.assert_called_once_with(["system_info"])
            gui_for_integration.progress_bar.setValue.assert_called_with(100)
            gui_for_integration.results_text.setPlainText.assert_called_with(test_results)
            gui_for_integration.start_scan_btn.setEnabled.assert_called_with(True)


class TestSimpleSecurityScannerErrorHandling:
    """Test error handling and exception scenarios."""
    
    def test_import_error_handling(self):
        """Test handling of PyQt5 import errors."""
        # Test that the module handles import errors gracefully
        with patch.dict('sys.modules', {'PyQt5.QtWidgets': None}):
            with patch('builtins.print') as mock_print:
                with patch('sys.exit') as mock_exit:
                    try:
                        # Force module reload to trigger import error
                        if 'tools.security.security_scanner.security_scanner' in sys.modules:
                            del sys.modules['tools.security.security_scanner.security_scanner']
                        
                        # This should trigger the import error handling
                        import tools.security.security_scanner.security_scanner
                    except SystemExit:
                        # Expected behavior when PyQt5 is not available
                        pass
    
    @patch('tools.security.security_scanner.security_scanner.QApplication')
    @patch('tools.security.security_scanner.security_scanner.SimpleSecurityScannerGUI')
    def test_main_function_execution(self, mock_gui_class, mock_qapp_class):
        """Test the main function execution."""
        mock_app = MagicMock()
        mock_qapp_class.return_value = mock_app
        mock_gui = MagicMock()
        mock_gui_class.return_value = mock_gui
        
        # Mock sys.argv and sys.exit
        with patch('sys.argv', ['simple_security_scanner.py']):
            with patch('sys.exit') as mock_exit:
                from tools.security.security_scanner.security_scanner import main
                main()
                
                # Verify application creation and execution
                mock_qapp_class.assert_called_once_with(['simple_security_scanner.py'])
                mock_gui_class.assert_called_once()
                mock_gui.show.assert_called_once()
                mock_app.exec_.assert_called_once()
                mock_exit.assert_called_once()


class TestSimpleSecurityScannerPerformance:
    """Performance and stress tests."""
    
    @pytest.fixture
    def worker_for_performance(self, mock_pyqt5):
        """Create a SecurityScanWorker instance for testing."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        return SecurityScanWorker(["network_ports"])
    
    @pytest.mark.slow
    def test_network_scan_performance(self, worker_for_performance):
        """Test network scanning performance with many ports."""
        start_time = time.time()
        
        with patch('tools.security.security_scanner.security_scanner.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.socket.return_value = mock_sock
            mock_socket.AF_INET = socket.AF_INET
            mock_socket.SOCK_STREAM = socket.SOCK_STREAM
            mock_sock.connect_ex.return_value = 1  # All ports closed
            
            result = worker_for_performance.scan_network_ports()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly even with many ports
        assert duration < 5.0, f"Network scan took too long: {duration:.3f}s"
        assert "=== NETWORK PORT SCAN ===" in result
    
    @pytest.mark.slow
    def test_large_process_list_performance(self, worker_for_performance):
        """Test performance with large process list."""
        # Generate large mock process output
        large_output = "Header\n" + "\n".join([f"process_{i}.exe" for i in range(1000)])
        
        start_time = time.time()
        
        with patch('tools.security.security_scanner.security_scanner.platform.system', return_value="Windows"):
            with patch('tools.security.security_scanner.security_scanner.subprocess.check_output', return_value=large_output):
                result = worker_for_performance.scan_running_processes()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle large output efficiently
        assert duration < 2.0, f"Process scan took too long: {duration:.3f}s"
        assert "✅ Process analysis completed" in result


class TestSimpleSecurityScannerSecurity:
    """Security-focused tests."""
    
    @pytest.fixture
    def worker_for_security(self, mock_pyqt5):
        """Create a SecurityScanWorker instance for testing."""
        from tools.security.security_scanner.security_scanner import \
            SecurityScanWorker
        return SecurityScanWorker(["network_ports"])
    
    def test_network_scan_localhost_only(self, worker_for_security):
        """Test that network scan only targets localhost."""
        with patch('tools.security.security_scanner.security_scanner.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.socket.return_value = mock_sock
            mock_socket.AF_INET = socket.AF_INET
            mock_socket.SOCK_STREAM = socket.SOCK_STREAM
            
            worker_for_security.scan_network_ports()
            
            # Verify all connect_ex calls are to localhost
            for call in mock_sock.connect_ex.call_args_list:
                addr = call[0][0]
                assert addr[0] == 'localhost', f"Unexpected target: {addr[0]}"
    
    def test_file_permission_safe_directories(self, worker_for_security):
        """Test that file permission scan only checks safe directories."""
        with patch('tools.security.security_scanner.security_scanner.platform.system', return_value="Windows"):
            with patch('tools.security.security_scanner.security_scanner.os.path.expanduser') as mock_expanduser:
                with patch('tools.security.security_scanner.security_scanner.os.path.exists', return_value=True):
                    with patch('tools.security.security_scanner.security_scanner.os.access', return_value=True):
                        worker_for_security.scan_file_permissions()
                        
                        # Verify only safe directories are checked
                        safe_dirs = ["Documents", "Downloads", "System32"]
                        for call in mock_expanduser.call_args_list:
                            path = call[0][0]
                            assert any(safe_dir in path for safe_dir in safe_dirs), f"Unsafe directory: {path}"


# Test Configuration and Fixtures
@pytest.fixture(scope="session")
def test_timestamp():
    """Provide consistent timestamp for test session."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "test_timeout": 30.0,  # seconds
        "coverage_threshold": 95.0,  # percentage
        "max_network_ports": 20,
        "max_processes": 10
    }


@pytest.fixture
def sample_scan_results():
    """Provide sample scan results for testing."""
    return {
        "system_info": """=== SYSTEM INFORMATION ===
Operating System: Windows 10
Machine Type: AMD64
Python Version: 3.9.0
Hostname: TestHost""",
        "network_ports": """=== NETWORK PORT SCAN ===
Open ports found: 80, 443
⚠️  Review open ports for security implications""",
        "file_permissions": """=== FILE PERMISSIONS CHECK ===
C:\\Users\\Test\\Documents: RWX
C:\\Users\\Test\\Downloads: RWX
✅ File permission scan completed""",
        "running_processes": """=== RUNNING PROCESSES ANALYSIS ===
Top running processes:
  System                           4 Services
  smss.exe                       123 Services
✅ Process analysis completed"""
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
    config.addinivalue_line(
        "markers", "security: marks tests as security-related tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.performance)
        elif "security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        elif "error_handling" in item.nodeid:
            item.add_marker(pytest.mark.unit)
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
=== SIMPLE SECURITY SCANNER UNIT TESTS SUMMARY ===
Generated: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} seconds

Tests Run: {self.results["tests_run"]}
Passed: {self.results["tests_passed"]}
Failed: {self.results["tests_failed"]}
Skipped: {self.results["tests_skipped"]}

Success Rate: {(self.results["tests_passed"] / max(self.results["tests_run"], 1)) * 100:.1f}%

Target Module: simple_security_scanner.py
Test Coverage: Comprehensive unit testing of SecurityScanWorker and SimpleSecurityScannerGUI classes
Test Types: Unit, Integration, Performance, Security, Error Handling

Functionality Tested:
✓ SecurityScanWorker Thread Operations
✓ System Information Scanning (Windows/Linux)
✓ Network Port Scanning (localhost security)
✓ File Permission Checking (safe directories)
✓ Running Process Analysis (platform-specific)
✓ GUI Initialization and Styling
✓ Scan Control and Progress Management
✓ Error Handling and Exception Management
✓ Performance with Large Datasets
✓ Security-focused Testing
✓ Complete Workflow Integration
✓ Import Error Handling
✓ Main Function Execution

=== END SUMMARY ===
"""
        return summary


# Global test results collector
test_collector = TestResultsCollector()


# Additional Utility Functions for Testing
def validate_scan_result_format(result, expected_header):
    """Validate that a scan result has the expected format."""
    lines = result.split('\n')
    if not lines:
        return False, "Empty result"
    
    if expected_header not in lines[0]:
        return False, f"Missing expected header: {expected_header}"
    
    return True, "Valid scan result format"


def check_network_scan_security(mock_calls):
    """Check that network scan only targets safe addresses."""
    safe_addresses = ['localhost', '127.0.0.1']
    
    for call in mock_calls:
        if hasattr(call, 'args') and len(call.args) > 0:
            addr = call.args[0]
            if isinstance(addr, tuple) and len(addr) > 0:
                if addr[0] not in safe_addresses:
                    return False, f"Unsafe network target: {addr[0]}"
    
    return True, "Network scan targets are safe"


def measure_scan_performance(func, *args, **kwargs):
    """Measure execution time of scan functions."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


# Test Data Validation
class TestDataValidator:
    """Validate test data and results."""
    
    @staticmethod
    def validate_system_info_result(result):
        """Validate system information scan result."""
        required_fields = [
            "Operating System:",
            "Machine Type:",
            "Python Version:",
            "Hostname:"
        ]
        
        for field in required_fields:
            if field not in result:
                return False, f"Missing required field: {field}"
        
        return True, "Valid system info result"
    
    @staticmethod
    def validate_network_scan_result(result):
        """Validate network scan result."""
        if "=== NETWORK PORT SCAN ===" not in result:
            return False, "Missing network scan header"
        
        if not ("Open ports found:" in result or "No common ports found open" in result):
            return False, "Missing port scan results"
        
        return True, "Valid network scan result"
    
    @staticmethod
    def validate_file_permissions_result(result):
        """Validate file permissions scan result."""
        if "=== FILE PERMISSIONS CHECK ===" not in result:
            return False, "Missing file permissions header"
        
        if "✅ File permission scan completed" not in result:
            return False, "Missing completion indicator"
        
        return True, "Valid file permissions result"
    
    @staticmethod
    def validate_process_scan_result(result):
        """Validate running processes scan result."""
        if "=== RUNNING PROCESSES ANALYSIS ===" not in result:
            return False, "Missing process analysis header"
        
        if "✅ Process analysis completed" not in result:
            return False, "Missing completion indicator"
        
        return True, "Valid process scan result"


if __name__ == "__main__":
    """Allow running tests directly."""
    import pytest
    pytest.main([__file__, "-v"])