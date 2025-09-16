"""
Comprehensive Unit Tests for Network GUI Module

Test file: test_network_gui_2025-08-29.py
Target module: src/utilities/network/gui.py
Generated: 2025-08-29
Framework: pytest with PyQt5 testing

This test suite provides comprehensive coverage for all functions and methods
in the network GUI module, including edge cases, mock data, and error scenarios.
"""

import ipaddress
import json
import os
import socket
import sys
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Suppress Qt warnings during testing
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

# Add source directory to path
sys.path.insert(0, r'c:\Users\richardi\1_2\src')

# PyQt5 imports with testing support
try:
    import pytest_qt
    from PyQt5.QtCore import QMutex, QMutexLocker, Qt, QThread
    from PyQt5.QtGui import QColor
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QLabel,
                                 QLineEdit, QMessageBox, QProgressBar,
                                 QPushButton, QSpinBox, QTableWidget,
                                 QTableWidgetItem, QTextEdit, QWidget)
    
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt5 not available", allow_module_level=True)

# Import target module components
try:
    from utilities.network.gui import (DEFAULT_SPEED_LABEL, BandwidthData,
                                       NetworkScanResult, NetworkToolsWindow,
                                       NetworkWorkerThread)
    MODULE_AVAILABLE = True
except ImportError as e:
    MODULE_AVAILABLE = False
    pytest.skip(f"Cannot import network GUI module: {e}", allow_module_level=True)

if not (PYQT_AVAILABLE and MODULE_AVAILABLE):
    pytest.skip("Required modules not available", allow_module_level=True)


class TestNetworkScanResult:
    """Test NetworkScanResult dataclass."""
    
    def test_network_scan_result_creation(self):
        """Test creating NetworkScanResult with required fields."""
        result = NetworkScanResult(
            target="192.168.1.1",
            port=80,
            state="open",
            service="HTTP"
        )
        
        assert result.target == "192.168.1.1"
        assert result.port == 80
        assert result.state == "open"
        assert result.service == "HTTP"
        assert result.banner == ""
        assert result.timestamp is None
    
    def test_network_scan_result_with_optional_fields(self):
        """Test creating NetworkScanResult with all fields."""
        timestamp = datetime.now()
        result = NetworkScanResult(
            target="example.com",
            port=443,
            state="open",
            service="HTTPS",
            banner="Server: nginx/1.18.0",
            timestamp=timestamp
        )
        
        assert result.target == "example.com"
        assert result.port == 443
        assert result.state == "open"
        assert result.service == "HTTPS"
        assert result.banner == "Server: nginx/1.18.0"
        assert result.timestamp == timestamp
    
    def test_network_scan_result_different_states(self):
        """Test NetworkScanResult with different port states."""
        states = ["open", "closed", "filtered"]
        
        for state in states:
            result = NetworkScanResult(
                target="test.com",
                port=22,
                state=state,
                service="SSH"
            )
            assert result.state == state


class TestBandwidthData:
    """Test BandwidthData dataclass."""
    
    def test_bandwidth_data_creation(self):
        """Test creating BandwidthData with all fields."""
        timestamp = datetime.now()
        data = BandwidthData(
            timestamp=timestamp,
            download_speed=1024.5,
            upload_speed=512.3,
            total_download=1048576,
            total_upload=524288
        )
        
        assert data.timestamp == timestamp
        assert data.download_speed == 1024.5
        assert data.upload_speed == 512.3
        assert data.total_download == 1048576
        assert data.total_upload == 524288
    
    def test_bandwidth_data_zero_values(self):
        """Test BandwidthData with zero values."""
        timestamp = datetime.now()
        data = BandwidthData(
            timestamp=timestamp,
            download_speed=0.0,
            upload_speed=0.0,
            total_download=0,
            total_upload=0
        )
        
        assert data.download_speed == 0.0
        assert data.upload_speed == 0.0
        assert data.total_download == 0
        assert data.total_upload == 0
    
    def test_bandwidth_data_large_values(self):
        """Test BandwidthData with large values."""
        timestamp = datetime.now()
        data = BandwidthData(
            timestamp=timestamp,
            download_speed=1000000.0,  # 1 GB/s
            upload_speed=500000.0,     # 500 MB/s
            total_download=1073741824000,  # 1 TB
            total_upload=536870912000      # 500 GB
        )
        
        assert data.download_speed == 1000000.0
        assert data.upload_speed == 500000.0
        assert data.total_download == 1073741824000
        assert data.total_upload == 536870912000


class TestNetworkWorkerThread:
    """Test NetworkWorkerThread functionality."""
    
    @pytest.fixture
    def worker_thread(self):
        """Create a worker thread instance for testing."""
        return NetworkWorkerThread("port_scan", {"target": "127.0.0.1", "ports": [80, 443]})
    
    def test_worker_thread_initialization(self, worker_thread):
        """Test worker thread initialization."""
        assert worker_thread.operation_type == "port_scan"
        assert worker_thread.parameters["target"] == "127.0.0.1"
        assert worker_thread.parameters["ports"] == [80, 443]
        assert worker_thread.is_cancelled is False
        assert isinstance(worker_thread._mutex, QMutex)
    
    def test_worker_thread_cancel(self, worker_thread):
        """Test worker thread cancellation."""
        assert worker_thread.is_cancelled is False
        worker_thread.cancel()
        assert worker_thread.is_cancelled is True
    
    @patch('utilities.network.gui.socket.socket')
    def test_scan_port_open(self, mock_socket, worker_thread):
        """Test _scan_port method with open port."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        result = worker_thread._scan_port("127.0.0.1", 80, "tcp_connect")
        
        assert result["state"] == "open"
        assert result["service"] == "HTTP"
        mock_sock.connect_ex.assert_called_once_with(("127.0.0.1", 80))
        mock_sock.close.assert_called_once()
    
    @patch('utilities.network.gui.socket.socket')
    def test_scan_port_closed(self, mock_socket, worker_thread):
        """Test _scan_port method with closed port."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        result = worker_thread._scan_port("127.0.0.1", 8080, "tcp_connect")
        
        assert result["state"] == "closed"
        assert result["service"] == ""
    
    @patch('utilities.network.gui.socket.socket')
    def test_scan_port_exception(self, mock_socket, worker_thread):
        """Test _scan_port method with exception."""
        mock_socket.side_effect = Exception("Connection failed")
        
        result = worker_thread._scan_port("127.0.0.1", 80, "tcp_connect")
        
        assert result["state"] == "filtered"
        assert result["service"] == ""
    
    def test_get_service_name(self, worker_thread):
        """Test _get_service_name method."""
        test_cases = [
            (21, "FTP"),
            (22, "SSH"),
            (80, "HTTP"),
            (443, "HTTPS"),
            (3389, "RDP"),
            (9999, "Unknown")
        ]
        
        for port, expected_service in test_cases:
            assert worker_thread._get_service_name(port) == expected_service
    
    @patch('utilities.network.gui.socket.socket')
    def test_ping_host_alive(self, mock_socket, worker_thread):
        """Test _ping_host method with alive host."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        result = worker_thread._ping_host("127.0.0.1")
        
        assert result is True
    
    @patch('utilities.network.gui.socket.socket')
    def test_ping_host_dead(self, mock_socket, worker_thread):
        """Test _ping_host method with dead host."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        result = worker_thread._ping_host("192.168.1.254")
        
        assert result is False
    
    @patch('utilities.network.gui.socket.socket')
    def test_ping_host_exception(self, mock_socket, worker_thread):
        """Test _ping_host method with exception."""
        mock_socket.side_effect = Exception("Network unreachable")
        
        result = worker_thread._ping_host("10.0.0.1")
        
        assert result is False
    
    @patch('utilities.network.gui.socket.socket')
    def test_test_connectivity_success(self, mock_socket, worker_thread):
        """Test _test_connectivity method with successful connection."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        result = worker_thread._test_connectivity("google.com")
        
        assert result["reachable"] is True
        assert "response_time" in result
        assert result["response_time"] > 0
    
    @patch('utilities.network.gui.socket.socket')
    def test_test_connectivity_failure(self, mock_socket, worker_thread):
        """Test _test_connectivity method with connection failure."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        result = worker_thread._test_connectivity("unreachable.com")
        
        assert result["reachable"] is False
        assert "response_time" in result
    
    @patch('utilities.network.gui.socket.socket')
    def test_test_connectivity_exception(self, mock_socket, worker_thread):
        """Test _test_connectivity method with exception."""
        mock_socket.side_effect = Exception("DNS resolution failed")
        
        result = worker_thread._test_connectivity("invalid.domain")
        
        assert result["reachable"] is False
        assert result["response_time"] == 0
        assert "error" in result
        assert "DNS resolution failed" in result["error"]
    
    def test_run_port_scan_signals(self, worker_thread, qtbot):
        """Test port scan operation signals."""
        with patch.object(worker_thread, '_scan_port') as mock_scan:
            mock_scan.return_value = {"state": "open", "service": "HTTP"}
            
            # Connect signal spies
            with qtbot.waitSignal(worker_thread.operation_completed, timeout=5000):
                worker_thread._run_port_scan()
    
    def test_run_wifi_scan_signals(self, worker_thread, qtbot):
        """Test WiFi scan operation signals."""
        # Connect signal spies
        with qtbot.waitSignal(worker_thread.operation_completed, timeout=5000):
            worker_thread._run_wifi_scan()
    
    def test_run_bandwidth_monitor_cancelled(self, worker_thread):
        """Test bandwidth monitor with immediate cancellation."""
        worker_thread.parameters = {"duration": 10, "interval": 1}
        worker_thread.cancel()  # Cancel before running
        
        with patch.object(worker_thread, 'msleep'):
            worker_thread._run_bandwidth_monitor()
    
    @patch('utilities.network.gui.ipaddress.IPv4Network')
    def test_run_network_discovery_invalid_network(self, mock_network, worker_thread):
        """Test network discovery with invalid network."""
        mock_network.side_effect = ValueError("Invalid network")
        worker_thread.parameters = {"network": "invalid"}
        
        with patch.object(worker_thread, 'error_occurred') as mock_error:
            worker_thread._run_network_discovery()
            mock_error.emit.assert_called_once()
    
    def test_run_connectivity_test_empty_targets(self, worker_thread):
        """Test connectivity test with empty targets."""
        worker_thread.parameters = {"targets": []}
        
        with patch.object(worker_thread, 'operation_completed') as mock_completed:
            worker_thread._run_connectivity_test()
            mock_completed.emit.assert_called_once_with(True, "Connectivity test completed")


@pytest.fixture
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def network_window(qapp, qtbot):
    """Create NetworkToolsWindow instance for testing."""
    with patch('utilities.network.gui.StandardWindow', QWidget):
        window = NetworkToolsWindow()
        qtbot.addWidget(window)
        return window


class TestNetworkToolsWindow:
    """Test NetworkToolsWindow functionality."""
    
    def test_window_initialization(self, network_window):
        """Test window initialization."""
        assert network_window.windowTitle() == "Network Tools - Enhanced"
        assert network_window.worker_thread is None
        assert isinstance(network_window.scan_results, list)
        assert isinstance(network_window.bandwidth_data, list)
    
    def test_window_geometry(self, network_window):
        """Test window geometry settings."""
        geometry = network_window.geometry()
        assert geometry.width() == 1400
        assert geometry.height() == 900
    
    def test_ui_components_exist(self, network_window):
        """Test that all UI components exist."""
        # Check main components
        assert hasattr(network_window, 'tab_widget')
        assert hasattr(network_window, 'progress_bar')
        assert hasattr(network_window, 'lbl_status')
        
        # Check port scanner components
        assert hasattr(network_window, 'edit_target')
        assert hasattr(network_window, 'edit_ports')
        assert hasattr(network_window, 'combo_scan_type')
        assert hasattr(network_window, 'table_scan_results')
        assert hasattr(network_window, 'btn_start_scan')
        
        # Check bandwidth monitor components
        assert hasattr(network_window, 'spin_duration')
        assert hasattr(network_window, 'spin_interval')
        assert hasattr(network_window, 'btn_start_monitor')
        assert hasattr(network_window, 'lbl_download_speed')
        assert hasattr(network_window, 'lbl_upload_speed')
        assert hasattr(network_window, 'text_bandwidth_log')
        
        # Check network discovery components
        assert hasattr(network_window, 'edit_network')
        assert hasattr(network_window, 'btn_discover')
        assert hasattr(network_window, 'table_hosts')
        
        # Check connectivity test components
        assert hasattr(network_window, 'text_targets')
        assert hasattr(network_window, 'btn_test_connectivity')
        assert hasattr(network_window, 'table_connectivity')
        
        # Check WiFi analyzer components
        assert hasattr(network_window, 'btn_scan_wifi')
        assert hasattr(network_window, 'chk_show_hidden')
        assert hasattr(network_window, 'table_wifi')
        
        # Check control buttons
        assert hasattr(network_window, 'btn_cancel')
        assert hasattr(network_window, 'btn_export')
        assert hasattr(network_window, 'btn_clear')
    
    def test_tab_widget_tabs(self, network_window):
        """Test tab widget contains expected tabs."""
        tab_widget = network_window.tab_widget
        expected_tabs = [
            "Port Scanner",
            "Bandwidth Monitor", 
            "Network Discovery",
            "Connectivity Test",
            "WiFi Analyzer"
        ]
        
        assert tab_widget.count() == len(expected_tabs)
        
        for i, expected_tab in enumerate(expected_tabs):
            assert tab_widget.tabText(i) == expected_tab
    
    def test_port_scanner_default_values(self, network_window):
        """Test port scanner default values."""
        assert network_window.edit_target.placeholderText() == "192.168.1.1 or example.com"
        assert network_window.edit_ports.text() == "22,80,443,21,25,53,110,143,993,995,3389,5900"
        assert network_window.combo_scan_type.currentText() == "TCP Connect"
        assert network_window.chk_service_detection.isChecked() is True
        assert network_window.chk_banner_grab.isChecked() is False
        assert network_window.chk_stealth_mode.isChecked() is False
    
    def test_bandwidth_monitor_default_values(self, network_window):
        """Test bandwidth monitor default values."""
        assert network_window.spin_duration.value() == 60
        assert network_window.spin_interval.value() == 1
        assert network_window.lbl_download_speed.text() == DEFAULT_SPEED_LABEL
        assert network_window.lbl_upload_speed.text() == DEFAULT_SPEED_LABEL
    
    def test_network_discovery_default_values(self, network_window):
        """Test network discovery default values."""
        assert network_window.edit_network.text() == "192.168.1.0/24"
        assert network_window.edit_network.placeholderText() == "192.168.1.0/24"
    
    def test_connectivity_test_default_values(self, network_window):
        """Test connectivity test default values."""
        expected_targets = "8.8.8.8\ngoogle.com\nbing.com\ncloudflare.com"
        assert network_window.text_targets.toPlainText() == expected_targets
    
    def test_control_panel_initial_state(self, network_window):
        """Test control panel initial state."""
        assert network_window.progress_bar.isVisible() is False
        assert network_window.lbl_status.text() == "Ready"
        assert network_window.btn_cancel.isEnabled() is False
    
    def test_start_port_scan_empty_target(self, network_window, qtbot):
        """Test port scan with empty target."""
        network_window.edit_target.setText("")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            network_window.start_port_scan()
            mock_warning.assert_called_once()
    
    def test_start_port_scan_invalid_ports(self, network_window, qtbot):
        """Test port scan with invalid ports."""
        network_window.edit_target.setText("127.0.0.1")
        network_window.edit_ports.setText("abc,def")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            network_window.start_port_scan()
            mock_warning.assert_called_once()
    
    def test_start_port_scan_valid_input(self, network_window, qtbot):
        """Test port scan with valid input."""
        network_window.edit_target.setText("127.0.0.1")
        network_window.edit_ports.setText("80,443")
        
        with patch.object(network_window, 'start_operation') as mock_start:
            network_window.start_port_scan()
            mock_start.assert_called_once()
            
            # Verify parameters
            args, kwargs = mock_start.call_args
            assert args[0] == "port_scan"
            assert args[1]["target"] == "127.0.0.1"
            assert args[1]["ports"] == [80, 443]
    
    def test_start_bandwidth_monitor(self, network_window):
        """Test starting bandwidth monitor."""
        network_window.spin_duration.setValue(30)
        network_window.spin_interval.setValue(2)
        
        with patch.object(network_window, 'start_operation') as mock_start:
            network_window.start_bandwidth_monitor()
            mock_start.assert_called_once()
            
            args, kwargs = mock_start.call_args
            assert args[0] == "bandwidth_monitor"
            assert args[1]["duration"] == 30
            assert args[1]["interval"] == 2
    
    def test_start_network_discovery_empty_network(self, network_window):
        """Test network discovery with empty network."""
        network_window.edit_network.setText("")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            network_window.start_network_discovery()
            mock_warning.assert_called_once()
    
    def test_start_network_discovery_valid_input(self, network_window):
        """Test network discovery with valid input."""
        network_window.edit_network.setText("10.0.0.0/24")
        
        with patch.object(network_window, 'start_operation') as mock_start:
            network_window.start_network_discovery()
            mock_start.assert_called_once()
            
            args, kwargs = mock_start.call_args
            assert args[0] == "network_discovery"
            assert args[1]["network"] == "10.0.0.0/24"
    
    def test_start_connectivity_test_empty_targets(self, network_window):
        """Test connectivity test with empty targets."""
        network_window.text_targets.setPlainText("")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            network_window.start_connectivity_test()
            mock_warning.assert_called_once()
    
    def test_start_connectivity_test_valid_targets(self, network_window):
        """Test connectivity test with valid targets."""
        network_window.text_targets.setPlainText("8.8.8.8\ngoogle.com")
        
        with patch.object(network_window, 'start_operation') as mock_start:
            network_window.start_connectivity_test()
            mock_start.assert_called_once()
            
            args, kwargs = mock_start.call_args
            assert args[0] == "connectivity_test"
            assert args[1]["targets"] == ["8.8.8.8", "google.com"]
    
    def test_start_wifi_scan(self, network_window):
        """Test starting WiFi scan."""
        network_window.chk_show_hidden.setChecked(True)
        
        with patch.object(network_window, 'start_operation') as mock_start:
            network_window.start_wifi_scan()
            mock_start.assert_called_once()
            
            args, kwargs = mock_start.call_args
            assert args[0] == "wifi_scan"
            assert args[1]["show_hidden"] is True
    
    def test_start_operation_already_running(self, network_window):
        """Test starting operation when one is already running."""
        mock_thread = Mock()
        mock_thread.isRunning.return_value = True
        network_window.worker_thread = mock_thread
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            network_window.start_operation("port_scan", {})
            mock_warning.assert_called_once()
    
    def test_start_operation_success(self, network_window):
        """Test successful operation start."""
        network_window.worker_thread = None
        
        with patch('utilities.network.gui.NetworkWorkerThread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread
            
            network_window.start_operation("port_scan", {"target": "127.0.0.1"})
            
            # Verify thread creation and setup
            mock_thread_class.assert_called_once_with("port_scan", {"target": "127.0.0.1"})
            mock_thread.start.assert_called_once()
            
            # Verify UI state changes
            assert network_window.btn_cancel.isEnabled() is True
            assert network_window.progress_bar.isVisible() is True
    
    def test_cancel_operation(self, network_window):
        """Test canceling operation."""
        mock_thread = Mock()
        network_window.worker_thread = mock_thread
        
        network_window.cancel_operation()
        
        mock_thread.cancel.assert_called_once()
        mock_thread.wait.assert_called_once()
    
    def test_on_progress_updated(self, network_window):
        """Test progress update handling."""
        network_window.on_progress_updated(75, "Processing...")
        
        assert network_window.progress_bar.value() == 75
        assert network_window.lbl_status.text() == "Processing..."
    
    def test_on_scan_result_port_scan(self, network_window):
        """Test handling port scan results."""
        result = {
            "target": "127.0.0.1",
            "port": 80,
            "state": "open",
            "service": "HTTP",
            "banner": "Apache/2.4"
        }
        
        with patch.object(network_window, 'add_port_scan_result') as mock_add:
            network_window.on_scan_result(result)
            mock_add.assert_called_once_with(result)
    
    def test_on_scan_result_wifi_scan(self, network_window):
        """Test handling WiFi scan results."""
        result = {
            "ssid": "MyNetwork",
            "signal": -45,
            "security": "WPA2"
        }
        
        with patch.object(network_window, 'add_wifi_result') as mock_add:
            network_window.on_scan_result(result)
            mock_add.assert_called_once_with(result)
    
    def test_on_scan_result_network_discovery(self, network_window):
        """Test handling network discovery results."""
        result = {
            "ip": "192.168.1.100",
            "hostname": "host-100",
            "status": "alive",
            "response_time": 15
        }
        
        with patch.object(network_window, 'add_host_result') as mock_add:
            network_window.on_scan_result(result)
            mock_add.assert_called_once_with(result)
    
    def test_on_scan_result_connectivity_test(self, network_window):
        """Test handling connectivity test results."""
        result = {
            "target": "google.com",
            "reachable": True,
            "response_time": 25.5,
            "error": ""
        }
        
        with patch.object(network_window, 'add_connectivity_result') as mock_add:
            network_window.on_scan_result(result)
            mock_add.assert_called_once_with(result)
    
    def test_on_bandwidth_data(self, network_window):
        """Test handling bandwidth data."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "download_speed": 1048576,  # 1 MB/s
            "upload_speed": 524288      # 0.5 MB/s
        }
        
        network_window.on_bandwidth_data(data)
        
        assert "1.00 MB/s" in network_window.lbl_download_speed.text()
        assert "0.50 MB/s" in network_window.lbl_upload_speed.text()
    
    def test_on_operation_completed_success(self, network_window):
        """Test successful operation completion."""
        network_window.on_operation_completed(True, "Scan completed")
        
        assert "Completed: Scan completed" in network_window.lbl_status.text()
        assert network_window.btn_cancel.isEnabled() is False
        assert network_window.progress_bar.isVisible() is False
    
    def test_on_operation_completed_failure(self, network_window):
        """Test failed operation completion."""
        with patch.object(QMessageBox, 'warning') as mock_warning:
            network_window.on_operation_completed(False, "Operation failed")
            mock_warning.assert_called_once()
    
    def test_on_error_occurred(self, network_window):
        """Test error handling."""
        with patch.object(QMessageBox, 'critical') as mock_critical:
            network_window.on_error_occurred("Network error occurred")
            mock_critical.assert_called_once()
    
    def test_add_port_scan_result(self, network_window):
        """Test adding port scan result to table."""
        result = {
            "target": "127.0.0.1",
            "port": 80,
            "state": "open",
            "service": "HTTP",
            "banner": "Apache"
        }
        
        initial_rows = network_window.table_scan_results.rowCount()
        network_window.add_port_scan_result(result)
        
        assert network_window.table_scan_results.rowCount() == initial_rows + 1
        
        # Check if data was added correctly
        last_row = network_window.table_scan_results.rowCount() - 1
        assert network_window.table_scan_results.item(last_row, 0).text() == "127.0.0.1"
        assert network_window.table_scan_results.item(last_row, 1).text() == "80"
        assert network_window.table_scan_results.item(last_row, 2).text() == "open"
        assert network_window.table_scan_results.item(last_row, 3).text() == "HTTP"
        assert network_window.table_scan_results.item(last_row, 4).text() == "Apache"
    
    def test_add_port_scan_result_color_coding(self, network_window):
        """Test port scan result color coding."""
        test_cases = [
            ("open", QColor(76, 175, 80, 100)),
            ("closed", QColor(244, 67, 54, 100)),
            ("filtered", QColor(255, 152, 0, 100))
        ]
        
        for state, expected_color in test_cases:
            result = {
                "target": "127.0.0.1",
                "port": 80,
                "state": state,
                "service": "HTTP",
                "banner": ""
            }
            
            initial_rows = network_window.table_scan_results.rowCount()
            network_window.add_port_scan_result(result)
            
            last_row = network_window.table_scan_results.rowCount() - 1
            state_item = network_window.table_scan_results.item(last_row, 2)
            
            assert state_item.background().color() == expected_color
    
    def test_add_wifi_result(self, network_window):
        """Test adding WiFi result to table."""
        result = {
            "ssid": "MyNetwork",
            "signal": -45,
            "security": "WPA2"
        }
        
        initial_rows = network_window.table_wifi.rowCount()
        network_window.add_wifi_result(result)
        
        assert network_window.table_wifi.rowCount() == initial_rows + 1
        
        last_row = network_window.table_wifi.rowCount() - 1
        assert network_window.table_wifi.item(last_row, 0).text() == "MyNetwork"
        assert network_window.table_wifi.item(last_row, 1).text() == "-45 dBm"
        assert network_window.table_wifi.item(last_row, 2).text() == "WPA2"
    
    def test_add_host_result(self, network_window):
        """Test adding host discovery result to table."""
        result = {
            "ip": "192.168.1.100",
            "hostname": "host-100",
            "status": "alive",
            "response_time": 15
        }
        
        initial_rows = network_window.table_hosts.rowCount()
        network_window.add_host_result(result)
        
        assert network_window.table_hosts.rowCount() == initial_rows + 1
        
        last_row = network_window.table_hosts.rowCount() - 1
        assert network_window.table_hosts.item(last_row, 0).text() == "192.168.1.100"
        assert network_window.table_hosts.item(last_row, 1).text() == "host-100"
        assert network_window.table_hosts.item(last_row, 2).text() == "alive"
        assert network_window.table_hosts.item(last_row, 3).text() == "15"
        
        # Check color coding for alive status
        status_item = network_window.table_hosts.item(last_row, 2)
        assert status_item.background().color() == QColor(76, 175, 80, 100)
    
    def test_add_connectivity_result(self, network_window):
        """Test adding connectivity result to table."""
        result = {
            "target": "google.com",
            "reachable": True,
            "response_time": 25.5,
            "error": ""
        }
        
        initial_rows = network_window.table_connectivity.rowCount()
        network_window.add_connectivity_result(result)
        
        assert network_window.table_connectivity.rowCount() == initial_rows + 1
        
        last_row = network_window.table_connectivity.rowCount() - 1
        assert network_window.table_connectivity.item(last_row, 0).text() == "google.com"
        assert network_window.table_connectivity.item(last_row, 1).text() == "Yes"
        assert network_window.table_connectivity.item(last_row, 2).text() == "25.50"
        assert network_window.table_connectivity.item(last_row, 3).text() == ""
        
        # Check color coding for reachable status
        reachable_item = network_window.table_connectivity.item(last_row, 1)
        assert reachable_item.background().color() == QColor(76, 175, 80, 100)
    
    def test_add_connectivity_result_unreachable(self, network_window):
        """Test adding unreachable connectivity result."""
        result = {
            "target": "unreachable.com",
            "reachable": False,
            "response_time": 0,
            "error": "Connection timeout"
        }
        
        initial_rows = network_window.table_connectivity.rowCount()
        network_window.add_connectivity_result(result)
        
        last_row = network_window.table_connectivity.rowCount() - 1
        assert network_window.table_connectivity.item(last_row, 1).text() == "No"
        assert network_window.table_connectivity.item(last_row, 3).text() == "Connection timeout"
        
        # Check color coding for unreachable status
        reachable_item = network_window.table_connectivity.item(last_row, 1)
        assert reachable_item.background().color() == QColor(244, 67, 54, 100)
    
    def test_clear_operation_results_port_scan(self, network_window):
        """Test clearing port scan results."""
        # Add some data first
        network_window.table_scan_results.insertRow(0)
        network_window.table_scan_results.setItem(0, 0, QTableWidgetItem("test"))
        
        network_window.clear_operation_results("port_scan")
        assert network_window.table_scan_results.rowCount() == 0
    
    def test_clear_operation_results_bandwidth_monitor(self, network_window):
        """Test clearing bandwidth monitor results."""
        # Set some data first
        network_window.text_bandwidth_log.setText("Test log data")
        network_window.lbl_download_speed.setText("5.0 MB/s")
        network_window.lbl_upload_speed.setText("2.0 MB/s")
        
        network_window.clear_operation_results("bandwidth_monitor")
        
        assert network_window.text_bandwidth_log.toPlainText() == ""
        assert network_window.lbl_download_speed.text() == DEFAULT_SPEED_LABEL
        assert network_window.lbl_upload_speed.text() == DEFAULT_SPEED_LABEL
    
    def test_clear_results(self, network_window):
        """Test clearing all results."""
        # Add some data to tables
        for table in [network_window.table_scan_results, network_window.table_wifi,
                     network_window.table_hosts, network_window.table_connectivity]:
            table.insertRow(0)
            table.setItem(0, 0, QTableWidgetItem("test"))
        
        network_window.text_bandwidth_log.setText("Test log")
        network_window.lbl_download_speed.setText("5.0 MB/s")
        network_window.lbl_status.setText("Test status")
        
        network_window.clear_results()
        
        # Check all tables are cleared
        for table in [network_window.table_scan_results, network_window.table_wifi,
                     network_window.table_hosts, network_window.table_connectivity]:
            assert table.rowCount() == 0
        
        # Check other components are reset
        assert network_window.text_bandwidth_log.toPlainText() == ""
        assert network_window.lbl_download_speed.text() == DEFAULT_SPEED_LABEL
        assert network_window.lbl_upload_speed.text() == DEFAULT_SPEED_LABEL
        assert network_window.lbl_status.text() == "Ready"
    
    @patch('utilities.network.gui.QFileDialog.getSaveFileName')
    @patch('builtins.open', new_callable=MagicMock)
    def test_export_results_success(self, mock_open, mock_file_dialog, network_window):
        """Test successful results export."""
        mock_file_dialog.return_value = ("test_results.txt", "Text Files (*.txt)")
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch.object(QMessageBox, 'information') as mock_info:
            network_window.export_results()
            
            mock_file_dialog.assert_called_once()
            mock_open.assert_called_once_with("test_results.txt", 'w')
            mock_info.assert_called_once()
    
    @patch('utilities.network.gui.QFileDialog.getSaveFileName')
    def test_export_results_cancelled(self, mock_file_dialog, network_window):
        """Test export cancelled by user."""
        mock_file_dialog.return_value = ("", "")
        
        with patch('builtins.open') as mock_open:
            network_window.export_results()
            mock_open.assert_not_called()
    
    @patch('utilities.network.gui.QFileDialog.getSaveFileName')
    @patch('builtins.open', new_callable=MagicMock)
    def test_export_results_error(self, mock_open, mock_file_dialog, network_window):
        """Test export with file error."""
        mock_file_dialog.return_value = ("test_results.txt", "Text Files (*.txt)")
        mock_open.side_effect = IOError("Permission denied")
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            network_window.export_results()
            mock_critical.assert_called_once()
    
    def test_export_table_data_empty_table(self, network_window):
        """Test exporting empty table data."""
        from io import StringIO
        file_handle = StringIO()
        
        network_window.export_table_data(file_handle, "Empty Table", network_window.table_scan_results)
        
        # Should write nothing for empty table
        assert file_handle.getvalue() == ""
    
    def test_export_table_data_with_data(self, network_window):
        """Test exporting table with data."""
        from io import StringIO

        # Add test data to table
        table = network_window.table_scan_results
        table.insertRow(0)
        table.setItem(0, 0, QTableWidgetItem("127.0.0.1"))
        table.setItem(0, 1, QTableWidgetItem("80"))
        table.setItem(0, 2, QTableWidgetItem("open"))
        table.setItem(0, 3, QTableWidgetItem("HTTP"))
        table.setItem(0, 4, QTableWidgetItem("Apache"))
        
        file_handle = StringIO()
        network_window.export_table_data(file_handle, "Test Table", table)
        
        content = file_handle.getvalue()
        assert "Test Table:" in content
        assert "127.0.0.1" in content
        assert "HTTP" in content
    
    def test_close_event_no_operation(self, network_window, qtbot):
        """Test close event with no running operation."""
        from PyQt5.QtGui import QCloseEvent
        
        event = QCloseEvent()
        network_window.closeEvent(event)
        
        assert event.isAccepted()
    
    def test_close_event_with_operation_accept(self, network_window, qtbot):
        """Test close event with running operation - user accepts."""
        from PyQt5.QtGui import QCloseEvent
        
        mock_thread = Mock()
        mock_thread.isRunning.return_value = True
        network_window.worker_thread = mock_thread
        
        event = QCloseEvent()
        
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
            with patch.object(network_window, 'cancel_operation') as mock_cancel:
                network_window.closeEvent(event)
                mock_cancel.assert_called_once()
        
        assert event.isAccepted()
    
    def test_close_event_with_operation_reject(self, network_window, qtbot):
        """Test close event with running operation - user rejects."""
        from PyQt5.QtGui import QCloseEvent
        
        mock_thread = Mock()
        mock_thread.isRunning.return_value = True
        network_window.worker_thread = mock_thread
        
        event = QCloseEvent()
        
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.No):
            network_window.closeEvent(event)
        
        assert not event.isAccepted()


class TestNetworkGUIIntegration:
    """Integration tests for network GUI components."""
    
    def test_full_port_scan_workflow(self, network_window, qtbot):
        """Test complete port scan workflow."""
        # Set up scan parameters
        network_window.edit_target.setText("127.0.0.1")
        network_window.edit_ports.setText("80,443")
        
        # Mock the worker thread
        with patch('utilities.network.gui.NetworkWorkerThread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread.isRunning.return_value = False
            mock_thread_class.return_value = mock_thread
            
            # Start scan
            network_window.start_port_scan()
            
            # Verify thread was created and started
            assert mock_thread.start.called
            assert network_window.worker_thread == mock_thread
            
            # Simulate scan result
            result = {
                "target": "127.0.0.1",
                "port": 80,
                "state": "open",
                "service": "HTTP"
            }
            network_window.on_scan_result(result)
            
            # Verify result was added to table
            assert network_window.table_scan_results.rowCount() == 1
            
            # Simulate completion
            network_window.on_operation_completed(True, "Scan completed")
            
            # Verify UI state
            assert network_window.btn_cancel.isEnabled() is False
            assert network_window.progress_bar.isVisible() is False
    
    def test_bandwidth_monitoring_workflow(self, network_window, qtbot):
        """Test bandwidth monitoring workflow."""
        # Set parameters
        network_window.spin_duration.setValue(10)
        network_window.spin_interval.setValue(1)
        
        with patch('utilities.network.gui.NetworkWorkerThread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread
            
            # Start monitoring
            network_window.start_bandwidth_monitor()
            
            # Simulate bandwidth data
            data = {
                "timestamp": datetime.now().isoformat(),
                "download_speed": 2097152,  # 2 MB/s
                "upload_speed": 1048576     # 1 MB/s
            }
            network_window.on_bandwidth_data(data)
            
            # Check UI updates
            assert "2.00 MB/s" in network_window.lbl_download_speed.text()
            assert "1.00 MB/s" in network_window.lbl_upload_speed.text()
            assert network_window.text_bandwidth_log.toPlainText() != ""
    
    def test_error_handling_workflow(self, network_window, qtbot):
        """Test error handling in workflows."""
        with patch.object(QMessageBox, 'critical') as mock_critical:
            network_window.on_error_occurred("Test error message")
            mock_critical.assert_called_once()
            
            # Verify operation is cleaned up
            assert network_window.btn_cancel.isEnabled() is False
            assert network_window.progress_bar.isVisible() is False


# Performance and stress tests
class TestNetworkGUIPerformance:
    """Performance tests for network GUI."""
    
    def test_large_port_scan_results(self, network_window):
        """Test handling large number of port scan results."""
        # Add many results
        for i in range(1000):
            result = {
                "target": f"192.168.1.{i % 255}",
                "port": 80 + (i % 100),
                "state": "open" if i % 3 == 0 else "closed",
                "service": "HTTP",
                "banner": f"Server-{i}"
            }
            network_window.add_port_scan_result(result)
        
        assert network_window.table_scan_results.rowCount() == 1000
    
    def test_bandwidth_data_accumulation(self, network_window):
        """Test bandwidth data accumulation over time."""
        # Simulate rapid bandwidth updates
        for i in range(100):
            data = {
                "timestamp": datetime.now().isoformat(),
                "download_speed": 1048576 * (i + 1),
                "upload_speed": 524288 * (i + 1)
            }
            network_window.on_bandwidth_data(data)
        
        # Verify log contains all entries
        log_content = network_window.text_bandwidth_log.toPlainText()
        assert log_content.count('[') == 100  # Each entry has timestamp in brackets


# Edge cases and error conditions
class TestNetworkGUIEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_ip_addresses(self, network_window):
        """Test handling of invalid IP addresses."""
        invalid_ips = [
            "999.999.999.999",
            "192.168.1",
            "not.an.ip",
            "",
            "192.168.1.1.1"
        ]
        
        for invalid_ip in invalid_ips:
            network_window.edit_target.setText(invalid_ip)
            # The GUI should handle these gracefully
            # Actual validation happens in the worker thread
    
    def test_extreme_values(self, network_window):
        """Test handling of extreme values."""
        # Test very large port numbers
        network_window.edit_ports.setText("65535,65536,100000")
        
        # Test extreme durations
        network_window.spin_duration.setValue(3600)  # 1 hour
        network_window.spin_interval.setValue(60)    # 1 minute
        
        # Test very large networks
        network_window.edit_network.setText("0.0.0.0/0")  # Entire IPv4 space
    
    def test_unicode_and_special_characters(self, network_window):
        """Test handling of unicode and special characters."""
        special_inputs = [
            "münchen.de",
            "测试.cn",
            "example.com/路径",
            "host-with-émojis-🔥.com"
        ]
        
        for special_input in special_inputs:
            network_window.edit_target.setText(special_input)
            # GUI should handle these without crashing
    
    def test_memory_cleanup(self, network_window):
        """Test memory cleanup after operations."""
        # Start and cancel multiple operations
        for _ in range(10):
            with patch('utilities.network.gui.NetworkWorkerThread') as mock_thread_class:
                mock_thread = Mock()
                mock_thread.isRunning.return_value = True
                mock_thread_class.return_value = mock_thread
                
                network_window.start_operation("port_scan", {"target": "127.0.0.1"})
                network_window.cancel_operation()
        
        # Worker thread should be cleaned up
        assert network_window.worker_thread is None


if __name__ == "__main__":
    # Configure pytest for this test file
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--html=result_network_gui_2025-08-29.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_network_gui_2025-08-29.json",
        "--cov=utilities.network.gui",
        "--cov-report=html:coverage_network_gui_2025-08-29",
        "--cov-report=json:coverage_network_gui_2025-08-29.json",
        "--junitxml=result_network_gui_2025-08-29_junit.xml"
    ])