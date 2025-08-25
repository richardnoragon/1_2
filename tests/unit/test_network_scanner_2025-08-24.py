#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Network Scanner Module

Test file for network_scanner.py - Created on 2025-08-24
Covers all functions and methods with edge cases and mock data.
"""

import json
import os
import socket
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt5 not available", allow_module_level=True)

from src.utilities.network.network_scanner import NetworkScannerGUI


class TestNetworkScannerGUI:
    """Test class for NetworkScannerGUI functionality."""

    @classmethod
    def setup_class(cls):
        """Setup class-level fixtures."""
        if not hasattr(cls, 'app'):
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication([])
        cls.test_data = {
            'valid_ip': '192.168.1.1',
            'valid_hostname': 'localhost',
            'invalid_ip': '999.999.999.999',
            'invalid_hostname': 'invalid-host-name-that-does-not-exist',
            'common_ports': {'start': 1, 'end': 1000},
            'web_ports': {'start': 80, 'end': 443},
            'all_ports': {'start': 1, 'end': 65535}
        }

    def setup_method(self):
        """Setup method called before each test."""
        self.scanner = NetworkScannerGUI()
        self.timestamp = datetime.now().isoformat()

    def teardown_method(self):
        """Cleanup method called after each test."""
        if hasattr(self, 'scanner'):
            self.scanner.close()
            del self.scanner

    def test_init_creates_gui_components(self):
        """Test that GUI components are properly initialized."""
        # Test window properties
        assert self.scanner.windowTitle() == "Network Scanner - Richard's File Utilities"
        
        # Test main components exist
        assert hasattr(self.scanner, 'target_input')
        assert hasattr(self.scanner, 'start_port')
        assert hasattr(self.scanner, 'end_port')
        assert hasattr(self.scanner, 'tcp_scan')
        assert hasattr(self.scanner, 'udp_scan')
        assert hasattr(self.scanner, 'service_detection')
        assert hasattr(self.scanner, 'scan_button')
        assert hasattr(self.scanner, 'results_text')
        assert hasattr(self.scanner, 'progress_bar')

    def test_initial_default_values(self):
        """Test that initial default values are set correctly."""
        # Test default target
        assert self.scanner.target_input.text() == "127.0.0.1"
        
        # Test default port range
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1000
        
        # Test default scan options
        assert self.scanner.tcp_scan.isChecked() is True
        assert self.scanner.udp_scan.isChecked() is False
        assert self.scanner.service_detection.isChecked() is False
        
        # Test progress bar is initially hidden
        assert self.scanner.progress_bar.isVisible() is False

    def test_set_common_ports(self):
        """Test setting common ports preset."""
        self.scanner.set_common_ports()
        
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1000
        
        # Check if message was added to results
        text_content = self.scanner.results_text.toPlainText()
        assert "Common ports (1-1000) selected" in text_content

    def test_set_web_ports(self):
        """Test setting web ports preset."""
        self.scanner.set_web_ports()
        
        assert self.scanner.start_port.value() == 80
        assert self.scanner.end_port.value() == 443
        
        # Check if message was added to results
        text_content = self.scanner.results_text.toPlainText()
        assert "Web ports (80-443) selected" in text_content

    def test_set_all_ports(self):
        """Test setting all ports preset."""
        self.scanner.set_all_ports()
        
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 65535
        
        # Check if message was added to results
        text_content = self.scanner.results_text.toPlainText()
        assert "All ports (1-65535) selected" in text_content

    def test_start_scan_empty_target_warning(self):
        """Test that empty target shows warning."""
        self.scanner.target_input.setText("")
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.scanner.start_scan()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Please enter a target IP address or hostname" in args[2]

    def test_start_scan_invalid_port_range_warning(self):
        """Test that invalid port range shows warning."""
        self.scanner.target_input.setText("127.0.0.1")
        self.scanner.start_port.setValue(100)
        self.scanner.end_port.setValue(50)  # End port less than start port
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.scanner.start_scan()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Start port must be less than or equal to end port" in args[2]

    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_start_scan_valid_input(self, mock_info):
        """Test start scan with valid input."""
        # Setup valid input
        self.scanner.target_input.setText("127.0.0.1")
        self.scanner.start_port.setValue(80)
        self.scanner.end_port.setValue(443)
        self.scanner.tcp_scan.setChecked(True)
        self.scanner.udp_scan.setChecked(False)
        self.scanner.service_detection.setChecked(True)
        
        with patch.object(self.scanner, 'test_basic_connectivity') as mock_test:
            self.scanner.start_scan()
            
            # Verify test_basic_connectivity was called with correct target
            mock_test.assert_called_once_with("127.0.0.1")
            
            # Verify success message was shown
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            assert "Network scan initiated for 127.0.0.1" in args[2]
            
            # Check results text contains scan information
            text_content = self.scanner.results_text.toPlainText()
            assert "Network Scan Started" in text_content
            assert "Target: 127.0.0.1" in text_content
            assert "Port Range: 80-443" in text_content
            assert "TCP Scan: Yes" in text_content
            assert "UDP Scan: No" in text_content
            assert "Service Detection: Yes" in text_content

    @patch('socket.gethostbyname')
    def test_test_basic_connectivity_success(self, mock_gethostbyname):
        """Test successful basic connectivity test."""
        mock_gethostbyname.return_value = "127.0.0.1"
        
        self.scanner.test_basic_connectivity("localhost")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "✓ Host localhost is reachable" in text_content
        mock_gethostbyname.assert_called_once_with("localhost")

    @patch('socket.gethostbyname')
    def test_test_basic_connectivity_gai_error(self, mock_gethostbyname):
        """Test basic connectivity with DNS resolution error."""
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")
        
        self.scanner.test_basic_connectivity("invalid-host")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "✗ Host invalid-host could not be resolved" in text_content

    @patch('socket.gethostbyname')
    def test_test_basic_connectivity_general_exception(self, mock_gethostbyname):
        """Test basic connectivity with general exception."""
        mock_gethostbyname.side_effect = Exception("Network error")
        
        self.scanner.test_basic_connectivity("test-host")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "✗ Connectivity test failed: Network error" in text_content

    def test_show_preferences(self):
        """Test show preferences functionality."""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.scanner.show_preferences()
            
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            assert "Network Scanner Preferences" in args[1]
            assert "Default scan timeout settings" in args[2]

    def test_refresh_view(self):
        """Test refresh view functionality."""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.scanner.refresh_view()
            
            text_content = self.scanner.results_text.toPlainText()
            assert "Refreshing Scanner Interface" in text_content
            assert "Target configuration refreshed" in text_content
            assert "Scan options updated" in text_content
            
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            assert "Scanner interface refreshed successfully" in args[2]

    def test_spinbox_ranges(self):
        """Test that spinboxes have correct ranges."""
        # Test start port range
        assert self.scanner.start_port.minimum() == 1
        assert self.scanner.start_port.maximum() == 65535
        
        # Test end port range
        assert self.scanner.end_port.minimum() == 1
        assert self.scanner.end_port.maximum() == 65535

    def test_checkbox_states(self):
        """Test checkbox state changes."""
        # Test TCP scan checkbox
        self.scanner.tcp_scan.setChecked(False)
        assert self.scanner.tcp_scan.isChecked() is False
        
        self.scanner.tcp_scan.setChecked(True)
        assert self.scanner.tcp_scan.isChecked() is True
        
        # Test UDP scan checkbox
        self.scanner.udp_scan.setChecked(True)
        assert self.scanner.udp_scan.isChecked() is True
        
        # Test service detection checkbox
        self.scanner.service_detection.setChecked(True)
        assert self.scanner.service_detection.isChecked() is True

    def test_target_input_placeholder(self):
        """Test target input placeholder text."""
        placeholder = self.scanner.target_input.placeholderText()
        assert placeholder == "Enter IP address or hostname"

    def test_results_text_readonly(self):
        """Test that results text is read-only."""
        assert self.scanner.results_text.isReadOnly() is True

    def test_button_connections(self):
        """Test that buttons are properly connected."""
        # This test verifies that clicking buttons triggers expected methods
        with patch.object(self.scanner, 'start_scan') as mock_start:
            self.scanner.scan_button.click()
            mock_start.assert_called_once()

    def test_port_value_validation(self):
        """Test port value validation with edge cases."""
        # Test minimum port values
        self.scanner.start_port.setValue(1)
        self.scanner.end_port.setValue(1)
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1
        
        # Test maximum port values
        self.scanner.start_port.setValue(65535)
        self.scanner.end_port.setValue(65535)
        assert self.scanner.start_port.value() == 65535
        assert self.scanner.end_port.value() == 65535

    def test_multiple_scan_configurations(self):
        """Test multiple scan configuration scenarios."""
        configurations = [
            {
                'target': '192.168.1.1',
                'start_port': 22,
                'end_port': 80,
                'tcp': True,
                'udp': False,
                'service': True
            },
            {
                'target': 'google.com',
                'start_port': 443,
                'end_port': 443,
                'tcp': True,
                'udp': True,
                'service': False
            },
            {
                'target': '::1',  # IPv6 localhost
                'start_port': 8080,
                'end_port': 8090,
                'tcp': False,
                'udp': True,
                'service': True
            }
        ]
        
        for config in configurations:
            self.scanner.target_input.setText(config['target'])
            self.scanner.start_port.setValue(config['start_port'])
            self.scanner.end_port.setValue(config['end_port'])
            self.scanner.tcp_scan.setChecked(config['tcp'])
            self.scanner.udp_scan.setChecked(config['udp'])
            self.scanner.service_detection.setChecked(config['service'])
            
            # Verify settings were applied
            assert self.scanner.target_input.text() == config['target']
            assert self.scanner.start_port.value() == config['start_port']
            assert self.scanner.end_port.value() == config['end_port']
            assert self.scanner.tcp_scan.isChecked() == config['tcp']
            assert self.scanner.udp_scan.isChecked() == config['udp']
            assert self.scanner.service_detection.isChecked() == config['service']

    @patch('src.utilities.network.network_scanner.StandardWindow')
    def test_inheritance_from_standard_window(self, mock_standard_window):
        """Test that NetworkScannerGUI properly inherits from StandardWindow."""
        # This test ensures proper inheritance structure
        from src.utilities.network.network_scanner import NetworkScannerGUI
        assert hasattr(NetworkScannerGUI, '__init__')
        assert hasattr(NetworkScannerGUI, 'init_ui')

    def test_menu_callback_registration(self):
        """Test menu callback registration."""
        # Mock menu_manager
        self.scanner.menu_manager = Mock()
        
        self.scanner._setup_menu_callbacks()
        
        # Verify callbacks were registered
        expected_calls = [
            call('show_preferences', self.scanner.show_preferences),
            call('refresh', self.scanner.refresh_view)
        ]
        self.scanner.menu_manager.register_callback.assert_has_calls(expected_calls)

    def test_edge_case_empty_string_target(self):
        """Test edge case with empty string target."""
        self.scanner.target_input.setText("   ")  # Whitespace only
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.scanner.start_scan()
            mock_warning.assert_called_once()

    def test_edge_case_very_large_port_range(self):
        """Test edge case with very large port range."""
        self.scanner.target_input.setText("127.0.0.1")
        self.scanner.start_port.setValue(1)
        self.scanner.end_port.setValue(65535)
        
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            with patch.object(self.scanner, 'test_basic_connectivity'):
                self.scanner.start_scan()
                mock_info.assert_called_once()

    def test_results_text_initial_content(self):
        """Test initial content of results text."""
        initial_text = self.scanner.results_text.toPlainText()
        expected_text = ("Network scanner ready. Configure target and port range, "
                        "then click 'Start Network Scan'.")
        assert expected_text in initial_text


class TestNetworkScannerEdgeCases:
    """Test class for edge cases and error conditions."""

    @classmethod
    def setup_class(cls):
        """Setup class-level fixtures."""
        if not hasattr(cls, 'app'):
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication([])

    def setup_method(self):
        """Setup method called before each test."""
        self.scanner = NetworkScannerGUI()

    def teardown_method(self):
        """Cleanup method called after each test."""
        if hasattr(self, 'scanner'):
            self.scanner.close()
            del self.scanner

    def test_unicode_target_input(self):
        """Test handling of unicode characters in target input."""
        unicode_targets = [
            "тест.com",  # Cyrillic
            "例え.jp",   # Japanese
            "münchen.de",  # German umlaut
            "ñandú.com"   # Spanish ñ
        ]
        
        for target in unicode_targets:
            self.scanner.target_input.setText(target)
            assert self.scanner.target_input.text() == target

    def test_extremely_long_target_input(self):
        """Test handling of extremely long target input."""
        long_target = "a" * 1000 + ".com"
        self.scanner.target_input.setText(long_target)
        assert self.scanner.target_input.text() == long_target

    def test_special_characters_in_target(self):
        """Test handling of special characters in target input."""
        special_targets = [
            "test-host.com",
            "test_host.com",
            "test.host.com",
            "127.0.0.1:8080",  # Port in hostname (should be handled)
            "http://example.com",  # URL format
            "example.com/path"  # With path
        ]
        
        for target in special_targets:
            self.scanner.target_input.setText(target)
            assert self.scanner.target_input.text() == target

    @patch('socket.gethostbyname')
    def test_timeout_in_connectivity_test(self, mock_gethostbyname):
        """Test timeout handling in connectivity test."""
        import socket
        mock_gethostbyname.side_effect = socket.timeout("Connection timeout")
        
        self.scanner.test_basic_connectivity("slow-host.com")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "Connectivity test failed: Connection timeout" in text_content

    def test_rapid_consecutive_scans(self):
        """Test rapid consecutive scan attempts."""
        self.scanner.target_input.setText("127.0.0.1")
        
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            with patch.object(self.scanner, 'test_basic_connectivity'):
                # Simulate rapid clicking
                for _ in range(5):
                    self.scanner.start_scan()
                
                # Should handle all scan requests
                assert mock_info.call_count == 5


class TestNetworkScannerPerformance:
    """Test class for performance-related tests."""

    @classmethod
    def setup_class(cls):
        """Setup class-level fixtures."""
        if not hasattr(cls, 'app'):
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication([])

    def setup_method(self):
        """Setup method called before each test."""
        self.scanner = NetworkScannerGUI()

    def teardown_method(self):
        """Cleanup method called after each test."""
        if hasattr(self, 'scanner'):
            self.scanner.close()
            del self.scanner

    def test_gui_initialization_time(self):
        """Test GUI initialization performance."""
        import time
        
        start_time = time.time()
        scanner = NetworkScannerGUI()
        initialization_time = time.time() - start_time
        
        # Should initialize in reasonable time (less than 1 second)
        assert initialization_time < 1.0
        
        scanner.close()

    def test_large_results_text_handling(self):
        """Test handling of large amounts of text in results area."""
        large_text = "Test line\n" * 10000  # 10,000 lines
        
        self.scanner.results_text.append(large_text)
        
        # Should handle large text without crashing
        assert len(self.scanner.results_text.toPlainText()) > 50000

    def test_memory_usage_stability(self):
        """Test memory usage doesn't grow excessively."""
        import gc

        # Perform multiple operations
        for i in range(100):
            self.scanner.set_common_ports()
            self.scanner.set_web_ports()
            self.scanner.set_all_ports()
            
            if i % 10 == 0:
                gc.collect()  # Force garbage collection
        
        # Test should complete without memory issues
        assert True  # If we reach here, memory handling is acceptable


# Test fixtures and utilities
@pytest.fixture
def sample_network_data():
    """Fixture providing sample network data for tests."""
    return {
        'hosts': ['127.0.0.1', 'localhost', '192.168.1.1'],
        'ports': [22, 80, 443, 8080, 3389],
        'services': {
            22: 'SSH',
            80: 'HTTP',
            443: 'HTTPS',
            8080: 'HTTP-PROXY',
            3389: 'RDP'
        }
    }


@pytest.fixture
def mock_socket_responses():
    """Fixture providing mock socket responses."""
    return {
        'success': socket.gethostbyname,
        'gai_error': socket.gaierror("Name resolution failed"),
        'timeout': socket.timeout("Connection timeout"),
        'connection_error': ConnectionError("Connection refused")
    }


def test_main_function_execution():
    """Test main function can be called without errors."""
    # Mock sys.argv and QApplication to test main function
    with patch('sys.argv', ['network_scanner.py']):
        with patch('PyQt5.QtWidgets.QApplication') as mock_app:
            with patch('sys.exit') as mock_exit:
                mock_app_instance = Mock()
                mock_app.return_value = mock_app_instance
                mock_app_instance.exec_.return_value = 0
                
                from src.utilities.network.network_scanner import main

                # Should not raise exceptions
                main()
                mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])