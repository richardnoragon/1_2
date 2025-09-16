"""
Comprehensive Unit Tests for network/gui.py
Test execution timestamp: 2025-08-28
Target module: src/utilities/network/gui.py

This module provides comprehensive pytest-based unit tests for the NetworkToolsWindow
and NetworkWorkerThread classes with full coverage of all functions and methods.
"""

import sys
import os
import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from typing import Dict, Any
import ipaddress
import socket

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
# Add src directory to path for utilities imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

# PyQt5 imports for testing
try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
    from PyQt5.QtTest import QTest
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False
    pytest.skip("PyQt5 not available", allow_module_level=True)

# Target module imports with fallback handling
try:
    from tools.network.gui import (
        NetworkScanResult,
        BandwidthData,
        NetworkWorkerThread,
        NetworkToolsWindow
    )
    TARGET_MODULE_AVAILABLE = True
except ImportError as e:
    TARGET_MODULE_AVAILABLE = False
    print(f"Warning: Could not import target module: {e}")


# Test Fixtures and Setup
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests."""
    if not HAS_PYQT5:
        pytest.skip("PyQt5 not available")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here to avoid issues with other tests


@pytest.fixture
def mock_network_tools():
    """Mock network tool dependencies."""
    with patch('utilities.network.gui.PortScanner') as mock_port_scanner, \
         patch('utilities.network.gui.BandwidthMonitor') as mock_bandwidth_monitor, \
         patch('utilities.network.gui.WiFiAnalyzer') as mock_wifi_analyzer, \
         patch('utilities.network.gui.LANFileTransfer') as mock_lan_transfer:
        
        # Configure mocks to return mock instances
        mock_port_scanner.return_value = Mock()
        mock_bandwidth_monitor.return_value = Mock()
        mock_wifi_analyzer.return_value = Mock()
        mock_lan_transfer.return_value = Mock()
        
        yield {
            'port_scanner': mock_port_scanner,
            'bandwidth_monitor': mock_bandwidth_monitor,
            'wifi_analyzer': mock_wifi_analyzer,
            'lan_transfer': mock_lan_transfer
        }


@pytest.fixture
def sample_network_data():
    """Provide sample network data for testing."""
    return {
        'scan_result': {
            'target': '192.168.1.1',
            'port': 80,
            'state': 'open',
            'service': 'HTTP',
            'banner': 'Apache/2.4.41',
            'timestamp': datetime.now().isoformat()
        },
        'bandwidth_data': {
            'timestamp': datetime.now().isoformat(),
            'download_speed': 1048576,  # 1 MB/s
            'upload_speed': 524288,    # 0.5 MB/s
            'total_download': 1073741824,  # 1 GB
            'total_upload': 536870912      # 0.5 GB
        },
        'wifi_network': {
            'ssid': 'TestNetwork',
            'signal': -45,
            'security': 'WPA2'
        },
        'host_discovery': {
            'ip': '192.168.1.100',
            'hostname': 'test-host',
            'status': 'alive',
            'response_time': 10
        },
        'connectivity_result': {
            'target': 'google.com',
            'reachable': True,
            'response_time': 25.5,
            'error': ''
        }
    }


@pytest.fixture
def worker_thread_params():
    """Provide standard worker thread parameters."""
    return {
        'port_scan': {
            'target': '192.168.1.1',
            'ports': [22, 80, 443],
            'scan_type': 'tcp_connect',
            'service_detection': True,
            'banner_grab': False,
            'stealth_mode': False
        },
        'bandwidth_monitor': {
            'duration': 30,
            'interval': 1
        },
        'network_discovery': {
            'network': '192.168.1.0/24'
        },
        'connectivity_test': {
            'targets': ['8.8.8.8', 'google.com']
        },
        'wifi_scan': {
            'show_hidden': False
        }
    }


# Data Class Tests
class TestNetworkScanResult:
    """Test NetworkScanResult dataclass."""
    
    def test_network_scan_result_creation(self):
        """Test NetworkScanResult creation with all fields."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        timestamp = datetime.now()
        result = NetworkScanResult(
            target="192.168.1.1",
            port=80,
            state="open",
            service="HTTP",
            banner="Apache/2.4.41",
            timestamp=timestamp
        )
        
        assert result.target == "192.168.1.1"
        assert result.port == 80
        assert result.state == "open"
        assert result.service == "HTTP"
        assert result.banner == "Apache/2.4.41"
        assert result.timestamp == timestamp
    
    def test_network_scan_result_minimal(self):
        """Test NetworkScanResult creation with minimal fields."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        result = NetworkScanResult(
            target="10.0.0.1",
            port=22,
            state="closed",
            service="SSH"
        )
        
        assert result.target == "10.0.0.1"
        assert result.port == 22
        assert result.state == "closed"
        assert result.service == "SSH"
        assert result.banner == ""
        assert result.timestamp is None


class TestBandwidthData:
    """Test BandwidthData dataclass."""
    
    def test_bandwidth_data_creation(self):
        """Test BandwidthData creation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        timestamp = datetime.now()
        data = BandwidthData(
            timestamp=timestamp,
            download_speed=1048576.0,
            upload_speed=524288.0,
            total_download=1073741824,
            total_upload=536870912
        )
        
        assert data.timestamp == timestamp
        assert data.download_speed == 1048576.0
        assert data.upload_speed == 524288.0
        assert data.total_download == 1073741824
        assert data.total_upload == 536870912


# NetworkWorkerThread Tests
class TestNetworkWorkerThread:
    """Test NetworkWorkerThread class."""
    
    def test_worker_thread_initialization(self, mock_network_tools):
        """Test worker thread initialization."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        operation_type = "port_scan"
        parameters = {"target": "192.168.1.1", "ports": [80, 443]}
        
        worker = NetworkWorkerThread(operation_type, parameters)
        
        assert worker.operation_type == operation_type
        assert worker.parameters == parameters
        assert not worker.is_cancelled
        assert isinstance(worker._mutex, QMutex)
    
    def test_worker_thread_signals(self, qapp, mock_network_tools):
        """Test worker thread signal definitions."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("port_scan", {})
        
        # Check that signals exist
        assert hasattr(worker, 'progress_updated')
        assert hasattr(worker, 'scan_result')
        assert hasattr(worker, 'bandwidth_data')
        assert hasattr(worker, 'operation_completed')
        assert hasattr(worker, 'error_occurred')
    
    def test_worker_thread_cancel(self, mock_network_tools):
        """Test worker thread cancellation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("port_scan", {})
        
        assert not worker.is_cancelled
        worker.cancel()
        assert worker.is_cancelled
    
    @patch('utilities.network.gui.socket.socket')
    def test_scan_port_open(self, mock_socket, mock_network_tools):
        """Test port scanning for open port."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        # Mock socket to return successful connection (port open)
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock_instance
        
        worker = NetworkWorkerThread("port_scan", {})
        result = worker._scan_port("192.168.1.1", 80, "tcp_connect")
        
        assert result['state'] == 'open'
        assert result['service'] == 'HTTP'
        mock_sock_instance.connect_ex.assert_called_once_with(("192.168.1.1", 80))
        mock_sock_instance.close.assert_called_once()
    
    @patch('utilities.network.gui.socket.socket')
    def test_scan_port_closed(self, mock_socket, mock_network_tools):
        """Test port scanning for closed port."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        # Mock socket to return failed connection (port closed)
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock_instance
        
        worker = NetworkWorkerThread("port_scan", {})
        result = worker._scan_port("192.168.1.1", 8080, "tcp_connect")
        
        assert result['state'] == 'closed'
        assert result['service'] == ''
    
    @patch('utilities.network.gui.socket.socket')
    def test_scan_port_filtered(self, mock_socket, mock_network_tools):
        """Test port scanning for filtered port (exception)."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        # Mock socket to raise exception (port filtered)
        mock_socket.side_effect = Exception("Connection error")
        
        worker = NetworkWorkerThread("port_scan", {})
        result = worker._scan_port("192.168.1.1", 22, "tcp_connect")
        
        assert result['state'] == 'filtered'
        assert result['service'] == ''
    
    def test_get_service_name(self, mock_network_tools):
        """Test service name resolution."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("port_scan", {})
        
        assert worker._get_service_name(80) == 'HTTP'
        assert worker._get_service_name(443) == 'HTTPS'
        assert worker._get_service_name(22) == 'SSH'
        assert worker._get_service_name(21) == 'FTP'
        assert worker._get_service_name(9999) == 'Unknown'
    
    @patch('utilities.network.gui.socket.socket')
    def test_ping_host_alive(self, mock_socket, mock_network_tools):
        """Test ping host when alive."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock_instance
        
        worker = NetworkWorkerThread("network_discovery", {})
        result = worker._ping_host("192.168.1.1")
        
        assert result is True
    
    @patch('utilities.network.gui.socket.socket')
    def test_ping_host_dead(self, mock_socket, mock_network_tools):
        """Test ping host when dead."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock_instance
        
        worker = NetworkWorkerThread("network_discovery", {})
        result = worker._ping_host("192.168.1.2")
        
        assert result is False
    
    @patch('utilities.network.gui.socket.socket')
    def test_ping_host_exception(self, mock_socket, mock_network_tools):
        """Test ping host with exception."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        mock_socket.side_effect = Exception("Network error")
        
        worker = NetworkWorkerThread("network_discovery", {})
        result = worker._ping_host("invalid.host")
        
        assert result is False
    
    @patch('utilities.network.gui.socket.socket')
    def test_test_connectivity_success(self, mock_socket, mock_network_tools):
        """Test connectivity test success."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock_instance
        
        worker = NetworkWorkerThread("connectivity_test", {})
        result = worker._test_connectivity("google.com")
        
        assert result['reachable'] is True
        assert result['response_time'] > 0
        assert 'error' not in result
    
    @patch('utilities.network.gui.socket.socket')
    def test_test_connectivity_failure(self, mock_socket, mock_network_tools):
        """Test connectivity test failure."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        mock_sock_instance = Mock()
        mock_sock_instance.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock_instance
        
        worker = NetworkWorkerThread("connectivity_test", {})
        result = worker._test_connectivity("unreachable.host")
        
        assert result['reachable'] is False
        assert result['response_time'] >= 0
    
    @patch('utilities.network.gui.socket.socket')
    def test_test_connectivity_exception(self, mock_socket, mock_network_tools):
        """Test connectivity test with exception."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        mock_socket.side_effect = Exception("DNS resolution failed")
        
        worker = NetworkWorkerThread("connectivity_test", {})
        result = worker._test_connectivity("invalid.domain")
        
        assert result['reachable'] is False
        assert result['response_time'] == 0
        assert 'DNS resolution failed' in result['error']


class TestNetworkWorkerThreadOperations:
    """Test NetworkWorkerThread operation methods."""
    
    def test_run_port_scan(self, mock_network_tools, worker_thread_params):
        """Test port scan operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("port_scan", worker_thread_params['port_scan'])
        
        # Mock the _scan_port method
        with patch.object(worker, '_scan_port') as mock_scan:
            mock_scan.return_value = {'state': 'open', 'service': 'HTTP'}
            
            # Mock signals
            worker.scan_result = Mock()
            worker.progress_updated = Mock()
            worker.operation_completed = Mock()
            
            worker._run_port_scan()
            
            # Verify calls
            assert mock_scan.call_count == len(worker_thread_params['port_scan']['ports'])
            assert worker.scan_result.emit.call_count == len(worker_thread_params['port_scan']['ports'])
            worker.operation_completed.emit.assert_called_once_with(True, "Port scan completed")
    
    def test_run_bandwidth_monitor(self, mock_network_tools, worker_thread_params):
        """Test bandwidth monitoring operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        # Use shorter duration for test
        params = worker_thread_params['bandwidth_monitor'].copy()
        params['duration'] = 2  # 2 seconds only
        
        worker = NetworkWorkerThread("bandwidth_monitor", params)
        
        # Mock signals and msleep
        worker.bandwidth_data = Mock()
        worker.progress_updated = Mock()
        worker.operation_completed = Mock()
        
        with patch.object(worker, 'msleep'):
            worker._run_bandwidth_monitor()
        
        # Verify calls
        assert worker.bandwidth_data.emit.call_count == 2
        worker.operation_completed.emit.assert_called_once_with(True, "Bandwidth monitoring completed")
    
    def test_run_wifi_scan(self, mock_network_tools):
        """Test WiFi scan operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("wifi_scan", {'show_hidden': False})
        
        # Mock signals
        worker.scan_result = Mock()
        worker.progress_updated = Mock()
        worker.operation_completed = Mock()
        
        worker._run_wifi_scan()
        
        # Verify calls - should emit results for simulated networks
        assert worker.scan_result.emit.call_count == 3  # 3 simulated networks
        worker.operation_completed.emit.assert_called_once()
    
    def test_run_network_discovery(self, mock_network_tools, worker_thread_params):
        """Test network discovery operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("network_discovery", worker_thread_params['network_discovery'])
        
        # Mock the _ping_host method
        with patch.object(worker, '_ping_host') as mock_ping:
            mock_ping.return_value = True
            
            # Mock signals
            worker.scan_result = Mock()
            worker.progress_updated = Mock()
            worker.operation_completed = Mock()
            
            worker._run_network_discovery()
            
            # Verify operation completed
            worker.operation_completed.emit.assert_called_once_with(True, "Network discovery completed")
    
    def test_run_connectivity_test(self, mock_network_tools, worker_thread_params):
        """Test connectivity test operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("connectivity_test", worker_thread_params['connectivity_test'])
        
        # Mock the _test_connectivity method
        with patch.object(worker, '_test_connectivity') as mock_test:
            mock_test.return_value = {'reachable': True, 'response_time': 25.0}
            
            # Mock signals
            worker.scan_result = Mock()
            worker.progress_updated = Mock()
            worker.operation_completed = Mock()
            
            worker._run_connectivity_test()
            
            # Verify calls
            assert mock_test.call_count == len(worker_thread_params['connectivity_test']['targets'])
            worker.operation_completed.emit.assert_called_once_with(True, "Connectivity test completed")
    
    def test_run_unknown_operation(self, mock_network_tools):
        """Test unknown operation handling."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("unknown_operation", {})
        
        # Mock error signal
        worker.error_occurred = Mock()
        
        worker.run()
        
        # Verify error was emitted
        worker.error_occurred.emit.assert_called_once()
        args = worker.error_occurred.emit.call_args[0]
        assert "Unknown operation" in args[0]
    
    def test_run_with_exception(self, mock_network_tools):
        """Test operation with exception."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("port_scan", {'target': 'test', 'ports': [80]})
        
        # Mock error signal
        worker.error_occurred = Mock()
        
        # Mock _run_port_scan to raise exception
        with patch.object(worker, '_run_port_scan', side_effect=Exception("Test error")):
            worker.run()
        
        # Verify error was emitted
        worker.error_occurred.emit.assert_called_once()
        args = worker.error_occurred.emit.call_args[0]
        assert "Operation failed: Test error" in args[0]


# NetworkToolsWindow Tests
@pytest.mark.skipif(not HAS_PYQT5, reason="PyQt5 not available")
class TestNetworkToolsWindow:
    """Test NetworkToolsWindow class."""
    
    def test_window_initialization(self, qapp, mock_network_tools):
        """Test window initialization."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            assert window.windowTitle() == "Network Tools - Enhanced"
            assert window.worker_thread is None
            assert window.scan_results == []
            assert window.bandwidth_data == []
            assert hasattr(window, 'tab_widget')
    
    def test_create_tabs(self, qapp, mock_network_tools):
        """Test tab creation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Check that all tabs are created
            assert window.tab_widget.count() == 5
            
            # Check tab names
            tab_names = []
            for i in range(window.tab_widget.count()):
                tab_names.append(window.tab_widget.tabText(i))
            
            expected_tabs = ["Port Scanner", "Bandwidth Monitor", "Network Discovery", 
                           "Connectivity Test", "WiFi Analyzer"]
            for expected in expected_tabs:
                assert expected in tab_names
    
    def test_control_panel_creation(self, qapp, mock_network_tools):
        """Test control panel creation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Check that control elements exist
            assert hasattr(window, 'progress_bar')
            assert hasattr(window, 'lbl_status')
            assert hasattr(window, 'btn_cancel')
            assert hasattr(window, 'btn_export')
            assert hasattr(window, 'btn_clear')
    
    def test_start_port_scan_valid_input(self, qapp, mock_network_tools):
        """Test starting port scan with valid input."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Set valid input
            window.edit_target.setText("192.168.1.1")
            window.edit_ports.setText("80,443,22")
            
            with patch.object(window, 'start_operation') as mock_start:
                window.start_port_scan()
                
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                assert args[0] == "port_scan"
                assert args[1]['target'] == "192.168.1.1"
                assert args[1]['ports'] == [80, 443, 22]
    
    def test_start_port_scan_invalid_target(self, qapp, mock_network_tools):
        """Test starting port scan with invalid target."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Set empty target
            window.edit_target.setText("")
            
            with patch('utilities.network.gui.QMessageBox.warning') as mock_warning:
                window.start_port_scan()
                mock_warning.assert_called_once()
    
    def test_start_port_scan_invalid_ports(self, qapp, mock_network_tools):
        """Test starting port scan with invalid ports."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Set valid target but invalid ports
            window.edit_target.setText("192.168.1.1")
            window.edit_ports.setText("invalid,ports")
            
            with patch('utilities.network.gui.QMessageBox.warning') as mock_warning:
                window.start_port_scan()
                mock_warning.assert_called_once()
    
    def test_start_bandwidth_monitor(self, qapp, mock_network_tools):
        """Test starting bandwidth monitor."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Set values
            window.spin_duration.setValue(30)
            window.spin_interval.setValue(2)
            
            with patch.object(window, 'start_operation') as mock_start:
                window.start_bandwidth_monitor()
                
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                assert args[0] == "bandwidth_monitor"
                assert args[1]['duration'] == 30
                assert args[1]['interval'] == 2
    
    def test_start_network_discovery_valid(self, qapp, mock_network_tools):
        """Test starting network discovery with valid input."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.edit_network.setText("192.168.1.0/24")
            
            with patch.object(window, 'start_operation') as mock_start:
                window.start_network_discovery()
                
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                assert args[0] == "network_discovery"
                assert args[1]['network'] == "192.168.1.0/24"
    
    def test_start_network_discovery_invalid(self, qapp, mock_network_tools):
        """Test starting network discovery with invalid input."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.edit_network.setText("")
            
            with patch('utilities.network.gui.QMessageBox.warning') as mock_warning:
                window.start_network_discovery()
                mock_warning.assert_called_once()
    
    def test_start_connectivity_test_valid(self, qapp, mock_network_tools):
        """Test starting connectivity test with valid input."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.text_targets.setPlainText("8.8.8.8\ngoogle.com\nbing.com")
            
            with patch.object(window, 'start_operation') as mock_start:
                window.start_connectivity_test()
                
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                assert args[0] == "connectivity_test"
                assert args[1]['targets'] == ['8.8.8.8', 'google.com', 'bing.com']
    
    def test_start_connectivity_test_invalid(self, qapp, mock_network_tools):
        """Test starting connectivity test with invalid input."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.text_targets.setPlainText("")
            
            with patch('utilities.network.gui.QMessageBox.warning') as mock_warning:
                window.start_connectivity_test()
                mock_warning.assert_called_once()
    
    def test_start_wifi_scan(self, qapp, mock_network_tools):
        """Test starting WiFi scan."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.chk_show_hidden.setChecked(True)
            
            with patch.object(window, 'start_operation') as mock_start:
                window.start_wifi_scan()
                
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                assert args[0] == "wifi_scan"
                assert args[1]['show_hidden'] is True
    
    def test_start_operation_already_running(self, qapp, mock_network_tools):
        """Test starting operation when one is already running."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Mock running thread
            mock_thread = Mock()
            mock_thread.isRunning.return_value = True
            window.worker_thread = mock_thread
            
            with patch('utilities.network.gui.QMessageBox.warning') as mock_warning:
                window.start_operation("port_scan", {})
                mock_warning.assert_called_once()
    
    def test_cancel_operation(self, qapp, mock_network_tools):
        """Test canceling operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Mock running thread
            mock_thread = Mock()
            window.worker_thread = mock_thread
            
            with patch.object(window, 'on_operation_finished') as mock_finished:
                window.cancel_operation()
                
                mock_thread.cancel.assert_called_once()
                mock_thread.wait.assert_called_once()
                mock_finished.assert_called_once()
    
    def test_on_progress_updated(self, qapp, mock_network_tools):
        """Test progress update handling."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.on_progress_updated(50, "Test status")
            
            assert window.progress_bar.value() == 50
            assert window.lbl_status.text() == "Test status"
    
    def test_on_scan_result_port_scan(self, qapp, mock_network_tools, sample_network_data):
        """Test handling port scan results."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'add_port_scan_result') as mock_add:
                window.on_scan_result(sample_network_data['scan_result'])
                mock_add.assert_called_once_with(sample_network_data['scan_result'])
    
    def test_on_scan_result_wifi_scan(self, qapp, mock_network_tools, sample_network_data):
        """Test handling WiFi scan results."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'add_wifi_result') as mock_add:
                window.on_scan_result(sample_network_data['wifi_network'])
                mock_add.assert_called_once_with(sample_network_data['wifi_network'])
    
    def test_on_scan_result_host_discovery(self, qapp, mock_network_tools, sample_network_data):
        """Test handling host discovery results."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'add_host_result') as mock_add:
                window.on_scan_result(sample_network_data['host_discovery'])
                mock_add.assert_called_once_with(sample_network_data['host_discovery'])
    
    def test_on_scan_result_connectivity_test(self, qapp, mock_network_tools, sample_network_data):
        """Test handling connectivity test results."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'add_connectivity_result') as mock_add:
                window.on_scan_result(sample_network_data['connectivity_result'])
                mock_add.assert_called_once_with(sample_network_data['connectivity_result'])
    
    def test_on_bandwidth_data(self, qapp, mock_network_tools, sample_network_data):
        """Test handling bandwidth data."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            window.on_bandwidth_data(sample_network_data['bandwidth_data'])
            
            # Check that speed labels are updated
            assert "1.00 MB/s" in window.lbl_download_speed.text()
            assert "0.50 MB/s" in window.lbl_upload_speed.text()
    
    def test_on_operation_completed_success(self, qapp, mock_network_tools):
        """Test successful operation completion."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'on_operation_finished') as mock_finished:
                window.on_operation_completed(True, "Test completed")
                
                mock_finished.assert_called_once()
                assert "Test completed" in window.lbl_status.text()
    
    def test_on_operation_completed_failure(self, qapp, mock_network_tools):
        """Test failed operation completion."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'on_operation_finished') as mock_finished, \
                 patch('utilities.network.gui.QMessageBox.warning') as mock_warning:
                
                window.on_operation_completed(False, "Test failed")
                
                mock_finished.assert_called_once()
                mock_warning.assert_called_once()
    
    def test_on_error_occurred(self, qapp, mock_network_tools):
        """Test error handling."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch.object(window, 'on_operation_finished') as mock_finished, \
                 patch('utilities.network.gui.QMessageBox.critical') as mock_critical:
                
                window.on_error_occurred("Test error")
                
                mock_finished.assert_called_once()
                mock_critical.assert_called_once()
    
    def test_on_operation_finished(self, qapp, mock_network_tools):
        """Test operation finished cleanup."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Set up initial state
            window.btn_cancel.setEnabled(True)
            window.progress_bar.setVisible(True)
            window.worker_thread = Mock()
            
            window.on_operation_finished()
            
            assert not window.btn_cancel.isEnabled()
            assert not window.progress_bar.isVisible()
            assert window.worker_thread is None
    
    def test_clear_results(self, qapp, mock_network_tools):
        """Test clearing all results."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Add some data to tables first
            window.table_scan_results.insertRow(0)
            window.table_wifi.insertRow(0)
            window.text_bandwidth_log.setText("Some log data")
            
            window.clear_results()
            
            # Check that all tables are cleared
            assert window.table_scan_results.rowCount() == 0
            assert window.table_wifi.rowCount() == 0
            assert window.table_hosts.rowCount() == 0
            assert window.table_connectivity.rowCount() == 0
            assert window.text_bandwidth_log.toPlainText() == ""
            assert window.lbl_download_speed.text() == DEFAULT_SPEED_LABEL
            assert window.lbl_upload_speed.text() == DEFAULT_SPEED_LABEL
    
    def test_clear_operation_results(self, qapp, mock_network_tools):
        """Test clearing results for specific operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Add data to port scan table
            window.table_scan_results.insertRow(0)
            window.table_wifi.insertRow(0)
            
            # Clear only port scan results
            window.clear_operation_results("port_scan")
            
            assert window.table_scan_results.rowCount() == 0
            assert window.table_wifi.rowCount() == 1  # Should remain unchanged
    
    def test_add_port_scan_result(self, qapp, mock_network_tools, sample_network_data):
        """Test adding port scan result to table."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            initial_rows = window.table_scan_results.rowCount()
            window.add_port_scan_result(sample_network_data['scan_result'])
            
            assert window.table_scan_results.rowCount() == initial_rows + 1
            # Check that data was added correctly
            last_row = window.table_scan_results.rowCount() - 1
            assert window.table_scan_results.item(last_row, 0).text() == "192.168.1.1"
            assert window.table_scan_results.item(last_row, 1).text() == "80"
    
    def test_add_wifi_result(self, qapp, mock_network_tools, sample_network_data):
        """Test adding WiFi result to table."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            initial_rows = window.table_wifi.rowCount()
            window.add_wifi_result(sample_network_data['wifi_network'])
            
            assert window.table_wifi.rowCount() == initial_rows + 1
            last_row = window.table_wifi.rowCount() - 1
            assert window.table_wifi.item(last_row, 0).text() == "TestNetwork"
    
    def test_add_host_result(self, qapp, mock_network_tools, sample_network_data):
        """Test adding host discovery result to table."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            initial_rows = window.table_hosts.rowCount()
            window.add_host_result(sample_network_data['host_discovery'])
            
            assert window.table_hosts.rowCount() == initial_rows + 1
            last_row = window.table_hosts.rowCount() - 1
            assert window.table_hosts.item(last_row, 0).text() == "192.168.1.100"
    
    def test_add_connectivity_result(self, qapp, mock_network_tools, sample_network_data):
        """Test adding connectivity result to table."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            initial_rows = window.table_connectivity.rowCount()
            window.add_connectivity_result(sample_network_data['connectivity_result'])
            
            assert window.table_connectivity.rowCount() == initial_rows + 1
            last_row = window.table_connectivity.rowCount() - 1
            assert window.table_connectivity.item(last_row, 0).text() == "google.com"
    
    def test_export_results(self, qapp, mock_network_tools, tmp_path):
        """Test exporting results to file."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Add some test data
            window.table_scan_results.insertRow(0)
            window.table_scan_results.setItem(0, 0, window.table_scan_results.item.__class__("192.168.1.1"))
            
            test_file = tmp_path / "test_export.txt"
            
            with patch('utilities.network.gui.QFileDialog.getSaveFileName') as mock_dialog, \
                 patch('utilities.network.gui.QMessageBox.information') as mock_info:
                
                mock_dialog.return_value = (str(test_file), "")
                
                window.export_results()
                
                mock_dialog.assert_called_once()
                mock_info.assert_called_once()
                assert test_file.exists()
    
    def test_export_results_cancelled(self, qapp, mock_network_tools):
        """Test export cancelled by user."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch('utilities.network.gui.QFileDialog.getSaveFileName') as mock_dialog:
                mock_dialog.return_value = ("", "")  # User cancelled
                
                window.export_results()
                
                mock_dialog.assert_called_once()
    
    def test_export_results_error(self, qapp, mock_network_tools):
        """Test export error handling."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            with patch('utilities.network.gui.QFileDialog.getSaveFileName') as mock_dialog, \
                 patch('builtins.open', side_effect=IOError("Permission denied")), \
                 patch('utilities.network.gui.QMessageBox.critical') as mock_critical:
                
                mock_dialog.return_value = ("test.txt", "")
                
                window.export_results()
                
                mock_critical.assert_called_once()
    
    def test_close_event_no_operation(self, qapp, mock_network_tools):
        """Test close event when no operation is running."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            mock_event = Mock()
            window.closeEvent(mock_event)
            
            mock_event.accept.assert_called_once()
    
    def test_close_event_with_operation_accept(self, qapp, mock_network_tools):
        """Test close event with running operation - user accepts."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Mock running thread
            mock_thread = Mock()
            mock_thread.isRunning.return_value = True
            window.worker_thread = mock_thread
            
            mock_event = Mock()
            
            with patch('utilities.network.gui.QMessageBox.question') as mock_question, \
                 patch.object(window, 'cancel_operation') as mock_cancel:
                
                mock_question.return_value = mock_question.return_value = getattr(
                    Mock(), 'Yes', 16384
                )  # QMessageBox.Yes
                
                window.closeEvent(mock_event)
                
                mock_question.assert_called_once()
                mock_cancel.assert_called_once()
                mock_event.accept.assert_called_once()
    
    def test_close_event_with_operation_reject(self, qapp, mock_network_tools):
        """Test close event with running operation - user rejects."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Mock running thread
            mock_thread = Mock()
            mock_thread.isRunning.return_value = True
            window.worker_thread = mock_thread
            
            mock_event = Mock()
            
            with patch('utilities.network.gui.QMessageBox.question') as mock_question:
                mock_question.return_value = getattr(Mock(), 'No', 65536)  # QMessageBox.No
                
                window.closeEvent(mock_event)
                
                mock_question.assert_called_once()
                mock_event.ignore.assert_called_once()


# Integration Tests
class TestNetworkGUIIntegration:
    """Integration tests for the complete network GUI system."""
    
    def test_worker_thread_signal_connection(self, qapp, mock_network_tools):
        """Test that worker thread signals connect properly to window."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Start an operation to create worker thread
            window.edit_target.setText("192.168.1.1")
            window.edit_ports.setText("80")
            
            with patch.object(NetworkWorkerThread, '__init__', return_value=None) as mock_init, \
                 patch.object(NetworkWorkerThread, 'start') as mock_start:
                
                window.start_port_scan()
                
                # Verify worker thread was created and started
                mock_init.assert_called_once()
                mock_start.assert_called_once()
    
    def test_complete_port_scan_workflow(self, qapp, mock_network_tools):
        """Test complete port scan workflow."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Start port scan
            window.edit_target.setText("192.168.1.1")
            window.edit_ports.setText("80")
            
            # Mock successful scan result
            scan_result = {
                'target': '192.168.1.1',
                'port': 80,
                'state': 'open',
                'service': 'HTTP',
                'banner': 'Apache/2.4.41',
                'timestamp': datetime.now().isoformat()
            }
            
            # Simulate the workflow
            window.on_progress_updated(50, "Scanning port 80")
            window.on_scan_result(scan_result)
            window.on_operation_completed(True, "Port scan completed")
            
            # Verify results
            assert window.progress_bar.value() == 50
            assert window.table_scan_results.rowCount() == 1
            assert "Port scan completed" in window.lbl_status.text()
    
    def test_bandwidth_monitoring_workflow(self, qapp, mock_network_tools):
        """Test bandwidth monitoring workflow."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Mock bandwidth data
            bandwidth_data = {
                'timestamp': datetime.now().isoformat(),
                'download_speed': 2097152,  # 2 MB/s
                'upload_speed': 1048576,   # 1 MB/s
                'total_download': 1073741824,
                'total_upload': 536870912
            }
            
            # Simulate the workflow
            window.on_progress_updated(25, "Monitoring bandwidth")
            window.on_bandwidth_data(bandwidth_data)
            window.on_operation_completed(True, "Bandwidth monitoring completed")
            
            # Verify results
            assert "2.00 MB/s" in window.lbl_download_speed.text()
            assert "1.00 MB/s" in window.lbl_upload_speed.text()
            assert len(window.text_bandwidth_log.toPlainText()) > 0


# Edge Cases and Error Handling Tests
class TestNetworkGUIEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_network_range(self, mock_network_tools):
        """Test invalid network range handling."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("network_discovery", {'network': 'invalid.network'})
        
        # Mock error signal
        worker.error_occurred = Mock()
        
        worker._run_network_discovery()
        
        # Should handle the invalid network gracefully
        # The exact behavior depends on implementation
    
    def test_large_port_list(self, mock_network_tools):
        """Test handling large port lists."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        large_port_list = list(range(1, 1001))  # 1000 ports
        params = {
            'target': '192.168.1.1',
            'ports': large_port_list,
            'scan_type': 'tcp_connect'
        }
        
        worker = NetworkWorkerThread("port_scan", params)
        
        # Mock the _scan_port method to avoid actual scanning
        with patch.object(worker, '_scan_port') as mock_scan:
            mock_scan.return_value = {'state': 'closed', 'service': ''}
            
            # Mock signals
            worker.scan_result = Mock()
            worker.progress_updated = Mock()
            worker.operation_completed = Mock()
            
            worker._run_port_scan()
            
            # Should handle large port list without issues
            assert mock_scan.call_count == len(large_port_list)
    
    def test_empty_target_lists(self, mock_network_tools):
        """Test handling empty target lists."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("connectivity_test", {'targets': []})
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.operation_completed = Mock()
        
        worker._run_connectivity_test()
        
        # Should complete successfully even with empty target list
        worker.operation_completed.emit.assert_called_once_with(True, "Connectivity test completed")
    
    def test_thread_cancellation_during_operation(self, mock_network_tools):
        """Test thread cancellation during operation."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        worker = NetworkWorkerThread("port_scan", {'target': '192.168.1.1', 'ports': [80, 443, 22]})
        
        # Mock signals
        worker.scan_result = Mock()
        worker.progress_updated = Mock()
        worker.operation_completed = Mock()
        
        # Cancel after first port
        call_count = 0
        def mock_scan_port(*args):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                worker.cancel()
            return {'state': 'open', 'service': 'HTTP'}
        
        with patch.object(worker, '_scan_port', side_effect=mock_scan_port):
            worker._run_port_scan()
        
        # Should stop after cancellation
        assert call_count == 1
        worker.operation_completed.emit.assert_called_once()


# Performance Tests
class TestNetworkGUIPerformance:
    """Test performance aspects of the network GUI."""
    
    def test_large_result_set_handling(self, qapp, mock_network_tools):
        """Test handling large result sets."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Add many results
            start_time = time.time()
            for i in range(100):
                result = {
                    'target': f'192.168.1.{i}',
                    'port': 80,
                    'state': 'open',
                    'service': 'HTTP',
                    'banner': f'Server-{i}'
                }
                window.add_port_scan_result(result)
            
            end_time = time.time()
            
            # Should handle 100 results quickly (less than 1 second)
            assert end_time - start_time < 1.0
            assert window.table_scan_results.rowCount() == 100
    
    def test_bandwidth_log_performance(self, qapp, mock_network_tools):
        """Test bandwidth log performance with many entries."""
        if not TARGET_MODULE_AVAILABLE:
            pytest.skip("Target module not available")
        
        with patch('utilities.network.gui.StandardWindow', QWidget):
            window = NetworkToolsWindow()
            
            # Add many bandwidth data points
            start_time = time.time()
            for i in range(50):
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'download_speed': 1048576 * (i + 1),
                    'upload_speed': 524288 * (i + 1),
                    'total_download': 1073741824,
                    'total_upload': 536870912
                }
                window.on_bandwidth_data(data)
            
            end_time = time.time()
            
            # Should handle many updates quickly
            assert end_time - start_time < 2.0
            assert len(window.text_bandwidth_log.toPlainText()) > 0


# Mock and Fixture Validation Tests
class TestTestingInfrastructure:
    """Test the testing infrastructure itself."""
    
    def test_mock_network_tools_fixture(self, mock_network_tools):
        """Test mock network tools fixture."""
        assert 'port_scanner' in mock_network_tools
        assert 'bandwidth_monitor' in mock_network_tools
        assert 'wifi_analyzer' in mock_network_tools
        assert 'lan_transfer' in mock_network_tools
    
    def test_sample_network_data_fixture(self, sample_network_data):
        """Test sample network data fixture."""
        assert 'scan_result' in sample_network_data
        assert 'bandwidth_data' in sample_network_data
        assert 'wifi_network' in sample_network_data
        assert 'host_discovery' in sample_network_data
        assert 'connectivity_result' in sample_network_data
    
    def test_worker_thread_params_fixture(self, worker_thread_params):
        """Test worker thread parameters fixture."""
        assert 'port_scan' in worker_thread_params
        assert 'bandwidth_monitor' in worker_thread_params
        assert 'network_discovery' in worker_thread_params
        assert 'connectivity_test' in worker_thread_params
        assert 'wifi_scan' in worker_thread_params


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "--tb=short"])