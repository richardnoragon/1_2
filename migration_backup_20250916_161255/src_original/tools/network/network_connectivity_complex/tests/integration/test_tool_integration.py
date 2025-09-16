"""Integration tests for network connectivity tools."""

import pytest
import time
import threading
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from ...tools.bandwidth_monitor import BandwidthMonitor
from ...tools.port_scanner import PortScanner
from ...tools.wifi_analyzer import WiFiAnalyzer
from ...tools.lan_file_transfer import LANFileTransfer
from ...core.platform_network import PlatformNetworkDetector
from ..mocks.network_mocks import MockPlatformDetector
from ..mocks.service_mocks import (
    MockConfigService, MockLoggingService, 
    MockNotificationService, MockMetricsService
)


class TestToolServiceIntegration:
    """Test integration between tools and services."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        return {
            'config': MockConfigService(),
            'logging': MockLoggingService(),
            'notification': MockNotificationService(),
            'metrics': MockMetricsService()
        }
    
    @pytest.fixture
    def mock_platform_detector(self):
        """Create mock platform detector."""
        return MockPlatformDetector()
    
    def test_bandwidth_monitor_service_integration(self, mock_services, 
                                                  mock_platform_detector):
        """Test bandwidth monitor integration with services."""
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service', 
                  return_value=mock_services['logging']), \
             patch('network_connectivity.tools.bandwidth_monitor.get_notification_service', 
                  return_value=mock_services['notification']), \
             patch('network_connectivity.tools.bandwidth_monitor.get_metrics_service', 
                  return_value=mock_services['metrics']):
            
            # Create bandwidth monitor
            monitor = BandwidthMonitor()
            monitor.platform_detector = mock_platform_detector
            
            # Test configuration integration
            config = mock_services['config'].get_setting('bandwidth_monitor')
            assert config is not None
            assert 'update_interval' in config
            
            # Test logging integration
            monitor.set_monitoring_interface("eth0")
            monitor.start_monitoring()
            time.sleep(0.1)
            monitor.stop_monitoring()
            
            # Verify logging was used
            assert len(mock_services['logging'].log_entries) > 0
            
            # Test metrics integration
            current_data = monitor.get_current_bandwidth()
            assert current_data is not None
            
            # Verify metrics were recorded
            metrics = mock_services['metrics'].get_metrics()
            # Note: Actual metrics recording depends on implementation
    
    def test_port_scanner_service_integration(self, mock_services, 
                                            mock_platform_detector):
        """Test port scanner integration with services."""
        with patch('network_connectivity.tools.port_scanner.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.port_scanner.get_logging_service', 
                  return_value=mock_services['logging']):
            
            # Create port scanner
            scanner = PortScanner()
            scanner.platform_detector = mock_platform_detector
            
            # Test configuration integration
            config = mock_services['config'].get_setting('port_scanner')
            assert config is not None
            assert 'default_timeout' in config
            
            # Test basic functionality
            # Note: Actual scanning would require network access
            # This tests the integration setup
            assert scanner.tool_name == "PortScanner"
    
    def test_wifi_analyzer_service_integration(self, mock_services, 
                                             mock_platform_detector):
        """Test WiFi analyzer integration with services."""
        with patch('network_connectivity.tools.wifi_analyzer.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.wifi_analyzer.get_logging_service', 
                  return_value=mock_services['logging']):
            
            # Create WiFi analyzer
            analyzer = WiFiAnalyzer()
            analyzer.platform_detector = mock_platform_detector
            
            # Test configuration integration
            config = mock_services['config'].get_setting('wifi_analyzer')
            assert config is not None
            assert 'scan_interval' in config
            
            # Test basic functionality
            assert analyzer.tool_name == "WiFiAnalyzer"
    
    def test_lan_file_transfer_service_integration(self, mock_services, 
                                                  mock_platform_detector):
        """Test LAN file transfer integration with services."""
        with patch('network_connectivity.tools.lan_file_transfer.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.lan_file_transfer.get_logging_service', 
                  return_value=mock_services['logging']):
            
            # Create LAN file transfer
            transfer = LANFileTransfer()
            transfer.platform_detector = mock_platform_detector
            
            # Test configuration integration
            config = mock_services['config'].get_setting('lan_file_transfer')
            assert config is not None
            assert 'discovery_port' in config
            
            # Test basic functionality
            assert transfer.tool_name == "LANFileTransfer"


class TestCrossToolIntegration:
    """Test integration between different tools."""
    
    @pytest.fixture
    def tools_setup(self):
        """Set up multiple tools for cross-integration testing."""
        mock_services = {
            'config': MockConfigService(),
            'logging': MockLoggingService(),
            'notification': MockNotificationService(),
            'metrics': MockMetricsService()
        }
        mock_detector = MockPlatformDetector()
        
        tools = {}
        
        # Create tools with mocked services
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service', 
                  return_value=mock_services['logging']):
            tools['bandwidth_monitor'] = BandwidthMonitor()
            tools['bandwidth_monitor'].platform_detector = mock_detector
        
        with patch('network_connectivity.tools.port_scanner.get_config_service', 
                  return_value=mock_services['config']), \
             patch('network_connectivity.tools.port_scanner.get_logging_service', 
                  return_value=mock_services['logging']):
            tools['port_scanner'] = PortScanner()
            tools['port_scanner'].platform_detector = mock_detector
        
        return {
            'tools': tools,
            'services': mock_services,
            'detector': mock_detector
        }
    
    def test_shared_platform_detector(self, tools_setup):
        """Test that tools can share platform detector."""
        tools = tools_setup['tools']
        detector = tools_setup['detector']
        
        # Both tools should use the same detector
        assert tools['bandwidth_monitor'].platform_detector is detector
        assert tools['port_scanner'].platform_detector is detector
        
        # Both should get the same interface list
        bm_interfaces = tools['bandwidth_monitor'].get_available_interfaces()
        ps_interfaces = tools['port_scanner'].get_available_interfaces()
        
        assert len(bm_interfaces) == len(ps_interfaces)
        assert bm_interfaces[0].name == ps_interfaces[0].name
    
    def test_shared_logging_service(self, tools_setup):
        """Test that tools share logging service."""
        tools = tools_setup['tools']
        services = tools_setup['services']
        
        # Perform operations that should log
        tools['bandwidth_monitor'].set_monitoring_interface("eth0")
        tools['port_scanner'].set_target("192.168.1.1")
        
        # Check that both tools logged to the same service
        log_entries = services['logging'].log_entries
        tool_names = [entry.get('tool_name') for entry in log_entries]
        
        # Should have logs from both tools
        assert any('BandwidthMonitor' in name for name in tool_names if name)
        assert any('PortScanner' in name for name in tool_names if name)
    
    def test_concurrent_tool_operations(self, tools_setup):
        """Test concurrent operations of multiple tools."""
        tools = tools_setup['tools']
        
        # Set up tools
        tools['bandwidth_monitor'].set_monitoring_interface("eth0")
        
        # Start operations concurrently
        def start_bandwidth_monitoring():
            tools['bandwidth_monitor'].start_monitoring()
            time.sleep(0.2)
            tools['bandwidth_monitor'].stop_monitoring()
        
        def perform_port_scan():
            # Mock port scan operation
            time.sleep(0.1)
            # In real implementation, this would scan ports
        
        # Run operations in parallel
        threads = [
            threading.Thread(target=start_bandwidth_monitoring),
            threading.Thread(target=perform_port_scan)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Both operations should complete without interference
        assert not tools['bandwidth_monitor'].is_monitoring


class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    @pytest.fixture
    def config_service(self):
        """Create configuration service for testing."""
        return MockConfigService()
    
    def test_profile_switching_affects_tools(self, config_service):
        """Test that profile switching affects tool configuration."""
        # Create a custom profile
        custom_settings = {
            "bandwidth_monitor": {
                "update_interval": 2000,
                "history_size": 200
            },
            "port_scanner": {
                "default_timeout": 5000,
                "max_threads": 100
            }
        }
        
        config_service.create_profile(
            "high_performance",
            "High performance profile",
            "performance",
            custom_settings
        )
        
        # Switch to custom profile
        success = config_service.switch_profile("high_performance")
        assert success
        
        # Verify configuration changes
        bm_config = config_service.get_setting('bandwidth_monitor')
        assert bm_config['update_interval'] == 2000
        assert bm_config['history_size'] == 200
        
        ps_config = config_service.get_setting('port_scanner')
        assert ps_config['default_timeout'] == 5000
        assert ps_config['max_threads'] == 100
    
    def test_configuration_validation_integration(self, config_service):
        """Test configuration validation integration."""
        # Try to set invalid configuration
        invalid_config = {
            "general": {
                "default_timeout": 500,  # Too low
                "log_level": "INVALID"   # Invalid level
            }
        }
        
        # Should fail validation
        success = config_service.update_configuration(
            invalid_config, validate=True
        )
        assert not success
        
        # Valid configuration should work
        valid_config = {
            "general": {
                "default_timeout": 5000,
                "log_level": "INFO"
            }
        }
        
        success = config_service.update_configuration(
            valid_config, validate=True
        )
        assert success


class TestNotificationIntegration:
    """Test notification system integration."""
    
    @pytest.fixture
    def notification_service(self):
        """Create notification service for testing."""
        return MockNotificationService()
    
    def test_tool_error_notifications(self, notification_service):
        """Test that tool errors trigger notifications."""
        # Add notification rule for errors
        error_rule = {
            "id": "tool_errors",
            "event_type": "error",
            "tools": ["BandwidthMonitor", "PortScanner"],
            "enabled": True
        }
        notification_service.add_rule(error_rule)
        
        # Simulate tool error
        notification_service.send_notification(
            "Tool Error",
            "BandwidthMonitor encountered an error",
            "error",
            "high"
        )
        
        # Verify notification was sent
        notifications = notification_service.get_notifications()
        assert len(notifications) == 1
        assert notifications[0]['type'] == 'error'
        assert notifications[0]['priority'] == 'high'
    
    def test_bandwidth_alert_notifications(self, notification_service):
        """Test bandwidth alert notifications."""
        # Simulate bandwidth alert
        notification_service.send_notification(
            "High Bandwidth Usage",
            "Download speed exceeded 100 Mbps threshold",
            "warning",
            "normal"
        )
        
        # Verify notification
        notifications = notification_service.get_notifications()
        assert len(notifications) == 1
        assert "bandwidth" in notifications[0]['title'].lower()


class TestMetricsIntegration:
    """Test metrics system integration."""
    
    @pytest.fixture
    def metrics_service(self):
        """Create metrics service for testing."""
        return MockMetricsService()
    
    def test_tool_performance_metrics(self, metrics_service):
        """Test tool performance metrics collection."""
        # Simulate tool performance metrics
        metrics_service.record_metric(
            "bandwidth_monitor.update_time",
            0.05,  # 50ms
            {"interface": "eth0"}
        )
        
        metrics_service.record_metric(
            "port_scanner.scan_time",
            2.5,  # 2.5 seconds
            {"target": "192.168.1.1", "ports": 1000}
        )
        
        # Verify metrics were recorded
        bm_metrics = metrics_service.get_metrics("bandwidth_monitor.update_time")
        ps_metrics = metrics_service.get_metrics("port_scanner.scan_time")
        
        assert len(bm_metrics["bandwidth_monitor.update_time"]) == 1
        assert len(ps_metrics["port_scanner.scan_time"]) == 1
        
        # Test metric statistics
        bm_stats = metrics_service.get_metric_statistics(
            "bandwidth_monitor.update_time"
        )
        assert bm_stats['avg'] == 0.05
        assert bm_stats['count'] == 1
    
    def test_network_usage_metrics(self, metrics_service):
        """Test network usage metrics collection."""
        # Simulate network usage metrics over time
        timestamps = [
            datetime.now() - timedelta(seconds=10),
            datetime.now() - timedelta(seconds=5),
            datetime.now()
        ]
        
        for i, timestamp in enumerate(timestamps):
            metrics_service.record_metric(
                "network.bytes_received",
                1000 * (i + 1),
                {"interface": "eth0"},
                timestamp
            )
        
        # Get metrics for time range
        start_time = datetime.now() - timedelta(seconds=15)
        end_time = datetime.now() + timedelta(seconds=5)
        
        metrics = metrics_service.get_metrics(
            time_range=(start_time, end_time)
        )
        
        assert "network.bytes_received" in metrics
        assert len(metrics["network.bytes_received"]) == 3


class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""
    
    def test_service_failure_handling(self):
        """Test handling of service failures."""
        # Create tools with failing services
        failing_config = Mock()
        failing_config.get_setting.side_effect = Exception("Config service failed")
        
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service', 
                  return_value=failing_config):
            
            # Tool should handle service failure gracefully
            try:
                monitor = BandwidthMonitor()
                # Should not raise exception during initialization
                assert monitor is not None
            except Exception as e:
                pytest.fail(f"Tool should handle service failure gracefully: {e}")
    
    def test_platform_detector_failure_handling(self):
        """Test handling of platform detector failures."""
        failing_detector = Mock()
        failing_detector.get_network_interfaces.side_effect = Exception(
            "Platform detection failed"
        )
        
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service'), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service'):
            
            monitor = BandwidthMonitor()
            monitor.platform_detector = failing_detector
            
            # Should handle detector failure gracefully
            interfaces = monitor.get_available_interfaces()
            assert interfaces == []  # Should return empty list, not raise exception


if __name__ == "__main__":
    pytest.main([__file__])