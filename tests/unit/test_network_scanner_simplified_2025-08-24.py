#!/usr/bin/env python3
"""
Simplified Unit Tests for Network Scanner Module

Test file for network_scanner.py - Created on 2025-08-24
Focused on core functionality testing with minimal GUI interactions.
"""

import os
import socket
import sys
from datetime import datetime
from unittest.mock import Mock, call, patch

import pytest

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    pytest.skip("PyQt5 not available", allow_module_level=True)

from src.tools.network.network_scanner import NetworkScannerGUI


class TestNetworkScannerCore:
    """Test class for core NetworkScannerGUI functionality."""

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
        self.timestamp = datetime.now().isoformat()

    def teardown_method(self):
        """Cleanup method called after each test."""
        if hasattr(self, 'scanner'):
            self.scanner.close()
            del self.scanner

    def test_init_creates_basic_components(self):
        """Test that basic GUI components are created."""
        # Test essential attributes exist
        assert hasattr(self.scanner, 'target_input')
        assert hasattr(self.scanner, 'start_port')
        assert hasattr(self.scanner, 'end_port')
        assert hasattr(self.scanner, 'results_text')

    def test_default_values_set_correctly(self):
        """Test that default values are set correctly."""
        assert self.scanner.target_input.text() == "127.0.0.1"
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1000

    def test_set_common_ports_method(self):
        """Test set_common_ports method."""
        self.scanner.set_common_ports()
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1000

    def test_set_web_ports_method(self):
        """Test set_web_ports method."""
        self.scanner.set_web_ports()
        assert self.scanner.start_port.value() == 80
        assert self.scanner.end_port.value() == 443

    def test_set_all_ports_method(self):
        """Test set_all_ports method."""
        self.scanner.set_all_ports()
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 65535

    def test_empty_target_validation(self):
        """Test validation for empty target."""
        self.scanner.target_input.setText("")
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.scanner.start_scan()
            mock_warning.assert_called_once()

    def test_invalid_port_range_validation(self):
        """Test validation for invalid port range."""
        self.scanner.target_input.setText("127.0.0.1")
        self.scanner.start_port.setValue(100)
        self.scanner.end_port.setValue(50)
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.scanner.start_scan()
            mock_warning.assert_called_once()

    @patch('socket.gethostbyname')
    def test_connectivity_test_success(self, mock_gethostbyname):
        """Test successful connectivity test."""
        mock_gethostbyname.return_value = "127.0.0.1"
        
        self.scanner.test_basic_connectivity("localhost")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "✓ Host localhost is reachable" in text_content

    @patch('socket.gethostbyname')
    def test_connectivity_test_dns_error(self, mock_gethostbyname):
        """Test connectivity test with DNS error."""
        mock_gethostbyname.side_effect = socket.gaierror("DNS failed")
        
        self.scanner.test_basic_connectivity("invalid-host")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "✗ Host invalid-host could not be resolved" in text_content

    @patch('socket.gethostbyname')
    def test_connectivity_test_general_error(self, mock_gethostbyname):
        """Test connectivity test with general error."""
        mock_gethostbyname.side_effect = Exception("Network error")
        
        self.scanner.test_basic_connectivity("test-host")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "✗ Connectivity test failed: Network error" in text_content

    def test_show_preferences_functionality(self):
        """Test show preferences method."""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.scanner.show_preferences()
            mock_info.assert_called_once()

    def test_refresh_view_functionality(self):
        """Test refresh view method."""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            self.scanner.refresh_view()
            mock_info.assert_called_once()

    def test_port_range_validation_edge_cases(self):
        """Test port range validation with edge cases."""
        # Test minimum values
        self.scanner.start_port.setValue(1)
        self.scanner.end_port.setValue(1)
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1
        
        # Test maximum values
        self.scanner.start_port.setValue(65535)
        self.scanner.end_port.setValue(65535)
        assert self.scanner.start_port.value() == 65535
        assert self.scanner.end_port.value() == 65535

    def test_target_input_edge_cases(self):
        """Test target input with various edge cases."""
        test_targets = [
            "192.168.1.1",
            "google.com",
            "localhost",
            "::1"  # IPv6
        ]
        
        for target in test_targets:
            self.scanner.target_input.setText(target)
            assert self.scanner.target_input.text() == target

    def test_checkbox_state_changes(self):
        """Test checkbox state changes."""
        # Test TCP scan checkbox
        original_state = self.scanner.tcp_scan.isChecked()
        self.scanner.tcp_scan.setChecked(not original_state)
        assert self.scanner.tcp_scan.isChecked() != original_state

    def test_scan_configuration_properties(self):
        """Test scan configuration properties."""
        # Setup specific configuration
        self.scanner.target_input.setText("192.168.1.100")
        self.scanner.start_port.setValue(22)
        self.scanner.end_port.setValue(80)
        self.scanner.tcp_scan.setChecked(True)
        self.scanner.udp_scan.setChecked(False)
        
        # Verify configuration
        assert self.scanner.target_input.text() == "192.168.1.100"
        assert self.scanner.start_port.value() == 22
        assert self.scanner.end_port.value() == 80
        assert self.scanner.tcp_scan.isChecked() is True
        assert self.scanner.udp_scan.isChecked() is False

    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_valid_scan_execution(self, mock_info):
        """Test valid scan execution flow."""
        self.scanner.target_input.setText("127.0.0.1")
        
        with patch.object(self.scanner, 'test_basic_connectivity') as mock_test:
            self.scanner.start_scan()
            mock_test.assert_called_once_with("127.0.0.1")
            mock_info.assert_called_once()

    def test_menu_callback_setup(self):
        """Test menu callback setup."""
        # Mock menu_manager
        self.scanner.menu_manager = Mock()
        
        self.scanner._setup_menu_callbacks()
        
        # Verify callbacks were registered
        expected_calls = [
            call('show_preferences', self.scanner.show_preferences),
            call('refresh', self.scanner.refresh_view)
        ]
        self.scanner.menu_manager.register_callback.assert_has_calls(
            expected_calls
        )

    def test_results_text_properties(self):
        """Test results text properties."""
        assert self.scanner.results_text.isReadOnly() is True
        
        # Test initial content
        initial_text = self.scanner.results_text.toPlainText()
        assert "Network scanner ready" in initial_text

    def test_spinbox_ranges_configured(self):
        """Test that spinboxes have correct ranges."""
        assert self.scanner.start_port.minimum() == 1
        assert self.scanner.start_port.maximum() == 65535
        assert self.scanner.end_port.minimum() == 1
        assert self.scanner.end_port.maximum() == 65535


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

    def test_unicode_target_handling(self):
        """Test handling of unicode characters in target."""
        unicode_target = "тест.com"  # Cyrillic
        self.scanner.target_input.setText(unicode_target)
        assert self.scanner.target_input.text() == unicode_target

    def test_long_target_input(self):
        """Test handling of very long target input."""
        long_target = "a" * 500 + ".com"
        self.scanner.target_input.setText(long_target)
        assert self.scanner.target_input.text() == long_target

    def test_whitespace_only_target(self):
        """Test handling of whitespace-only target."""
        self.scanner.target_input.setText("   ")
        
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.scanner.start_scan()
            mock_warning.assert_called_once()

    @patch('socket.gethostbyname')
    def test_timeout_in_connectivity(self, mock_gethostbyname):
        """Test timeout handling in connectivity test."""
        mock_gethostbyname.side_effect = socket.timeout("Timeout")
        
        self.scanner.test_basic_connectivity("slow-host.com")
        
        text_content = self.scanner.results_text.toPlainText()
        assert "Connectivity test failed: Timeout" in text_content

    def test_multiple_preset_operations(self):
        """Test multiple preset operations in sequence."""
        # Test sequence of preset operations
        self.scanner.set_common_ports()
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 1000
        
        self.scanner.set_web_ports()
        assert self.scanner.start_port.value() == 80
        assert self.scanner.end_port.value() == 443
        
        self.scanner.set_all_ports()
        assert self.scanner.start_port.value() == 1
        assert self.scanner.end_port.value() == 65535

    def test_large_port_range_handling(self):
        """Test handling of very large port ranges."""
        self.scanner.target_input.setText("127.0.0.1")
        self.scanner.start_port.setValue(1)
        self.scanner.end_port.setValue(65535)
        
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            with patch.object(self.scanner, 'test_basic_connectivity'):
                self.scanner.start_scan()
                mock_info.assert_called_once()


class TestNetworkScannerFunctionality:
    """Test class for specific functionality testing."""

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

    def test_scan_options_configuration(self):
        """Test scan options configuration."""
        configurations = [
            {'tcp': True, 'udp': False, 'service': True},
            {'tcp': False, 'udp': True, 'service': False},
            {'tcp': True, 'udp': True, 'service': True}
        ]
        
        for config in configurations:
            self.scanner.tcp_scan.setChecked(config['tcp'])
            self.scanner.udp_scan.setChecked(config['udp'])
            self.scanner.service_detection.setChecked(config['service'])
            
            assert self.scanner.tcp_scan.isChecked() == config['tcp']
            assert self.scanner.udp_scan.isChecked() == config['udp']
            assert (self.scanner.service_detection.isChecked() == 
                   config['service'])

    def test_target_placeholder_text(self):
        """Test target input placeholder text."""
        placeholder = self.scanner.target_input.placeholderText()
        assert placeholder == "Enter IP address or hostname"

    def test_progress_bar_initial_state(self):
        """Test progress bar initial state."""
        assert self.scanner.progress_bar.isVisible() is False

    def test_window_title_configuration(self):
        """Test window title is set correctly."""
        title = self.scanner.windowTitle()
        expected = "Network Scanner - Richard's File Utilities"
        assert title == expected

    def test_results_text_content_updates(self):
        """Test that results text content updates correctly."""
        initial_length = len(self.scanner.results_text.toPlainText())
        
        # Trigger an operation that adds text
        self.scanner.set_common_ports()
        
        updated_length = len(self.scanner.results_text.toPlainText())
        assert updated_length > initial_length


# Test fixtures for comprehensive testing
@pytest.fixture
def sample_scan_data():
    """Fixture providing sample scan data."""
    return {
        'targets': ['127.0.0.1', 'localhost', '192.168.1.1'],
        'port_ranges': [
            {'start': 22, 'end': 80},
            {'start': 443, 'end': 443},
            {'start': 8080, 'end': 8090}
        ],
        'scan_types': ['tcp', 'udp', 'service']
    }


@pytest.fixture
def mock_network_responses():
    """Fixture providing mock network responses."""
    return {
        'success_response': "127.0.0.1",
        'dns_error': socket.gaierror("Name resolution failed"),
        'timeout_error': socket.timeout("Connection timeout"),
        'general_error': Exception("Network unreachable")
    }


def test_main_function_import():
    """Test that main function can be imported."""
    from src.tools.network.network_scanner import main
    assert callable(main)


def test_network_scanner_class_import():
    """Test that NetworkScannerGUI class can be imported."""
    from src.tools.network.network_scanner import NetworkScannerGUI
    assert NetworkScannerGUI is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])