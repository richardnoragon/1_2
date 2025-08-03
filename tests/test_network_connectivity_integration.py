"""Integration tests for network connectivity tools with main RFU application."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestNetworkConnectivityIntegration:
    """Test network connectivity integration with main application."""
    
    def test_network_config_manager_import(self):
        """Test that network configuration manager can be imported."""
        try:
            from network_connectivity.config import get_network_config_manager
            config_manager = get_network_config_manager()
            assert config_manager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import network config manager: {e}")
    
    def test_network_logging_manager_import(self):
        """Test that network logging manager can be imported."""
        try:
            from network_connectivity.core import get_network_logging_manager
            logging_manager = get_network_logging_manager()
            assert logging_manager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import network logging manager: {e}")
    
    def test_network_hub_import(self):
        """Test that network connectivity hub can be imported."""
        try:
            from network_connectivity.gui.hub import NetworkConnectivityHub
            assert NetworkConnectivityHub is not None
        except ImportError as e:
            pytest.fail(f"Failed to import network connectivity hub: {e}")
    
    def test_network_tools_import(self):
        """Test that network tools can be imported."""
        try:
            from network_connectivity.tools import (
                BandwidthMonitor, PortScanner, WiFiAnalyzer, LANFileTransfer
            )
            assert BandwidthMonitor is not None
            assert PortScanner is not None
            assert WiFiAnalyzer is not None
            assert LANFileTransfer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import network tools: {e}")
    
    @patch('network_connectivity.config.config_integration.ConfigManager')
    def test_network_config_integration(self, mock_config_manager):
        """Test network configuration integration."""
        # Mock the config manager
        mock_instance = Mock()
        mock_config_manager.return_value = mock_instance
        mock_instance.config = {}
        mock_instance.get_setting.return_value = {}
        mock_instance.set_setting.return_value = None
        mock_instance.save_config.return_value = None
        
        try:
            from network_connectivity.config import get_network_config_manager
            config_manager = get_network_config_manager()
            
            # Test getting tool config
            config = config_manager.get_tool_config('bandwidth_monitor')
            assert config is not None
            
            # Test setting tool config
            result = config_manager.set_tool_config('bandwidth_monitor', 'test_key', 'test_value')
            assert isinstance(result, bool)
            
        except Exception as e:
            pytest.fail(f"Network config integration test failed: {e}")
    
    @patch('network_connectivity.core.logging_integration.LogManager')
    def test_network_logging_integration(self, mock_log_manager):
        """Test network logging integration."""
        # Mock the log manager
        mock_instance = Mock()
        mock_log_manager.return_value = mock_instance
        mock_logger = Mock()
        mock_instance.get_logger.return_value = mock_logger
        
        try:
            from network_connectivity.core import get_network_logging_manager
            logging_manager = get_network_logging_manager()
            
            # Test getting tool logger
            logger = logging_manager.get_tool_logger('BandwidthMonitor')
            assert logger is not None
            
            # Test logging operations
            logging_manager.log_network_operation(
                'BandwidthMonitor', 
                'test_operation',
                details={'test': 'value'}
            )
            
            # Test logging alerts
            logging_manager.log_network_alert(
                'BandwidthMonitor',
                'test_alert',
                'Test alert message'
            )
            
        except Exception as e:
            pytest.fail(f"Network logging integration test failed: {e}")
    
    def test_main_app_network_integration(self):
        """Test that main application can integrate with network tools."""
        try:
            # Test that main app can import network components
            from network_connectivity.config import get_network_config_manager
            from network_connectivity.core import get_network_logging_manager
            
            # Test initialization
            config_manager = get_network_config_manager()
            logging_manager = get_network_logging_manager()
            
            assert config_manager is not None
            assert logging_manager is not None
            
        except Exception as e:
            pytest.fail(f"Main app network integration test failed: {e}")
    
    def test_configuration_schema_integration(self):
        """Test that network configuration schema integrates properly."""
        try:
            from network_connectivity.config import get_default_config, validate_config
            
            # Get default configuration
            default_config = get_default_config()
            assert 'network_connectivity' in default_config
            
            # Validate configuration
            errors = validate_config(default_config)
            assert isinstance(errors, list)
            
        except Exception as e:
            pytest.fail(f"Configuration schema integration test failed: {e}")
    
    @patch('PyQt5.QtWidgets.QApplication')
    def test_gui_integration(self, mock_qapp):
        """Test that GUI components integrate properly."""
        try:
            # Mock QApplication
            mock_app = Mock()
            mock_qapp.return_value = mock_app
            
            # Test that GUI components can be imported
            from network_connectivity.gui.hub import NetworkConnectivityHub
            
            # Test that hub can be instantiated (with mocked Qt)
            with patch('network_connectivity.gui.hub.StandardWindow'):
                hub = NetworkConnectivityHub()
                assert hub is not None
                
        except Exception as e:
            pytest.fail(f"GUI integration test failed: {e}")
    
    def test_error_handling_integration(self):
        """Test that error handling integrates properly."""
        try:
            from network_connectivity.core.network_base import NetworkToolBase
            from core.error_handler import get_error_handler
            
            # Test that error handler can be accessed
            error_handler = get_error_handler()
            assert error_handler is not None
            
        except Exception as e:
            pytest.fail(f"Error handling integration test failed: {e}")
    
    def test_cross_platform_compatibility(self):
        """Test basic cross-platform compatibility."""
        try:
            from network_connectivity.core.platform_network import PlatformNetworkDetector
            
            # Test platform detection
            detector = PlatformNetworkDetector()
            assert detector is not None
            
            # Test that platform is supported
            is_supported = detector.is_supported()
            assert isinstance(is_supported, bool)
            
        except Exception as e:
            pytest.fail(f"Cross-platform compatibility test failed: {e}")


class TestNetworkConnectivityFunctionality:
    """Test basic functionality of network connectivity tools."""
    
    @patch('network_connectivity.core.platform_network.psutil')
    def test_bandwidth_monitor_basic_functionality(self, mock_psutil):
        """Test basic bandwidth monitor functionality."""
        # Mock psutil
        mock_psutil.net_if_addrs.return_value = {'eth0': []}
        mock_psutil.net_if_stats.return_value = {'eth0': Mock()}
        mock_psutil.net_io_counters.return_value = {'eth0': Mock()}
        
        try:
            from network_connectivity.tools import BandwidthMonitor
            
            monitor = BandwidthMonitor()
            assert monitor is not None
            
            # Test health status
            health = monitor.get_health_status()
            assert isinstance(health, dict)
            
        except Exception as e:
            pytest.fail(f"Bandwidth monitor functionality test failed: {e}")
    
    def test_port_scanner_basic_functionality(self):
        """Test basic port scanner functionality."""
        try:
            from network_connectivity.tools import PortScanner
            
            scanner = PortScanner()
            assert scanner is not None
            
            # Test parameter validation
            valid = scanner.validate_parameters(
                operation_type='scan_ports',
                target='127.0.0.1',
                ports=[80, 443]
            )
            assert isinstance(valid, bool)
            
        except Exception as e:
            pytest.fail(f"Port scanner functionality test failed: {e}")
    
    def test_wifi_analyzer_basic_functionality(self):
        """Test basic Wi-Fi analyzer functionality."""
        try:
            from network_connectivity.tools import WiFiAnalyzer
            
            analyzer = WiFiAnalyzer()
            assert analyzer is not None
            
            # Test health status
            health = analyzer.get_health_status()
            assert isinstance(health, dict)
            
        except Exception as e:
            pytest.fail(f"Wi-Fi analyzer functionality test failed: {e}")
    
    def test_lan_file_transfer_basic_functionality(self):
        """Test basic LAN file transfer functionality."""
        try:
            from network_connectivity.tools import LANFileTransfer
            
            transfer = LANFileTransfer()
            assert transfer is not None
            
            # Test health status
            health = transfer.get_health_status()
            assert isinstance(health, dict)
            
        except Exception as e:
            pytest.fail(f"LAN file transfer functionality test failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])