"""Unit tests for BandwidthMonitor tool."""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from ...tools.bandwidth_monitor import (
    BandwidthMonitor, BandwidthData, AlertRule, AlertType,
    MonitoringMode, DataExportFormat
)
from ...core.platform_network import NetworkInterface, NetworkStats


class TestBandwidthData:
    """Test BandwidthData data class."""
    
    def test_bandwidth_data_creation(self):
        """Test BandwidthData creation."""
        timestamp = datetime.now()
        data = BandwidthData(
            timestamp=timestamp,
            interface_name="eth0",
            bytes_sent=1024000,
            bytes_received=2048000,
            upload_speed=100.5,
            download_speed=200.8,
            total_bytes_sent=10240000,
            total_bytes_received=20480000
        )
        
        assert data.timestamp == timestamp
        assert data.interface_name == "eth0"
        assert data.bytes_sent == 1024000
        assert data.bytes_received == 2048000
        assert data.upload_speed == 100.5
        assert data.download_speed == 200.8
        assert data.total_bytes_sent == 10240000
        assert data.total_bytes_received == 20480000
    
    def test_bandwidth_data_defaults(self):
        """Test BandwidthData with default values."""
        data = BandwidthData(
            timestamp=datetime.now(),
            interface_name="lo"
        )
        
        assert data.interface_name == "lo"
        assert data.bytes_sent == 0
        assert data.bytes_received == 0
        assert data.upload_speed == 0.0
        assert data.download_speed == 0.0
        assert data.total_bytes_sent == 0
        assert data.total_bytes_received == 0


class TestAlertRule:
    """Test AlertRule data class."""
    
    def test_alert_rule_creation(self):
        """Test AlertRule creation."""
        rule = AlertRule(
            name="High Download Speed",
            alert_type=AlertType.DOWNLOAD_SPEED,
            threshold=100.0,
            duration=30,
            enabled=True
        )
        
        assert rule.name == "High Download Speed"
        assert rule.alert_type == AlertType.DOWNLOAD_SPEED
        assert rule.threshold == 100.0
        assert rule.duration == 30
        assert rule.enabled is True
    
    def test_alert_rule_defaults(self):
        """Test AlertRule with default values."""
        rule = AlertRule(
            name="Test Rule",
            alert_type=AlertType.UPLOAD_SPEED,
            threshold=50.0
        )
        
        assert rule.name == "Test Rule"
        assert rule.alert_type == AlertType.UPLOAD_SPEED
        assert rule.threshold == 50.0
        assert rule.duration == 60  # Default
        assert rule.enabled is True  # Default


class TestBandwidthMonitor:
    """Test BandwidthMonitor functionality."""
    
    @pytest.fixture
    def mock_platform_detector(self):
        """Create a mock platform detector."""
        detector = Mock()
        
        # Mock network interface
        interface = NetworkInterface(
            name="eth0",
            display_name="Ethernet",
            description="Test Ethernet Interface",
            mac_address="00:11:22:33:44:55",
            ip_addresses=["192.168.1.100"],
            is_up=True,
            is_wireless=False,
            speed_mbps=1000,
            mtu=1500
        )
        
        detector.get_network_interfaces.return_value = [interface]
        detector.get_interface_stats.return_value = NetworkStats(
            interface_name="eth0",
            bytes_sent=1024000,
            bytes_received=2048000,
            packets_sent=1000,
            packets_received=2000,
            timestamp=datetime.now()
        )
        
        return detector
    
    @pytest.fixture
    def bandwidth_monitor(self, mock_platform_detector):
        """Create a bandwidth monitor instance."""
        with patch('network_connectivity.tools.bandwidth_monitor.get_config_service'), \
             patch('network_connectivity.tools.bandwidth_monitor.get_logging_service'), \
             patch('network_connectivity.tools.bandwidth_monitor.get_notification_service'), \
             patch('network_connectivity.tools.bandwidth_monitor.get_metrics_service'):
            
            monitor = BandwidthMonitor()
            monitor.platform_detector = mock_platform_detector
            return monitor
    
    def test_initialization(self, bandwidth_monitor):
        """Test bandwidth monitor initialization."""
        assert bandwidth_monitor.tool_name == "BandwidthMonitor"
        assert bandwidth_monitor.monitoring_mode == MonitoringMode.INTERFACE
        assert bandwidth_monitor.selected_interface == ""
        assert bandwidth_monitor.update_interval == 1000  # Default
        assert bandwidth_monitor.history_size == 100  # Default
        assert len(bandwidth_monitor.bandwidth_history) == 0
        assert len(bandwidth_monitor.alert_rules) == 0
        assert not bandwidth_monitor.is_monitoring
    
    def test_get_available_interfaces(self, bandwidth_monitor):
        """Test getting available network interfaces."""
        interfaces = bandwidth_monitor.get_available_interfaces()
        
        assert len(interfaces) == 1
        assert interfaces[0].name == "eth0"
        assert interfaces[0].display_name == "Ethernet"
    
    def test_set_monitoring_interface(self, bandwidth_monitor):
        """Test setting monitoring interface."""
        # Test valid interface
        success = bandwidth_monitor.set_monitoring_interface("eth0")
        assert success is True
        assert bandwidth_monitor.selected_interface == "eth0"
        
        # Test invalid interface
        success = bandwidth_monitor.set_monitoring_interface("invalid")
        assert success is False
        assert bandwidth_monitor.selected_interface == "eth0"  # Unchanged
    
    def test_set_monitoring_mode(self, bandwidth_monitor):
        """Test setting monitoring mode."""
        # Test valid mode
        bandwidth_monitor.set_monitoring_mode(MonitoringMode.ALL_INTERFACES)
        assert bandwidth_monitor.monitoring_mode == MonitoringMode.ALL_INTERFACES
        
        # Test invalid mode
        with pytest.raises(ValueError):
            bandwidth_monitor.set_monitoring_mode("INVALID_MODE")
    
    def test_start_monitoring(self, bandwidth_monitor):
        """Test starting bandwidth monitoring."""
        # Set interface first
        bandwidth_monitor.set_monitoring_interface("eth0")
        
        # Start monitoring
        success = bandwidth_monitor.start_monitoring()
        assert success is True
        assert bandwidth_monitor.is_monitoring is True
        
        # Wait a bit for monitoring to collect data
        time.sleep(0.2)
        
        # Stop monitoring
        bandwidth_monitor.stop_monitoring()
        assert bandwidth_monitor.is_monitoring is False
    
    def test_start_monitoring_without_interface(self, bandwidth_monitor):
        """Test starting monitoring without selecting interface."""
        # Try to start without setting interface
        success = bandwidth_monitor.start_monitoring()
        assert success is False
        assert bandwidth_monitor.is_monitoring is False
    
    def test_stop_monitoring(self, bandwidth_monitor):
        """Test stopping bandwidth monitoring."""
        # Start monitoring first
        bandwidth_monitor.set_monitoring_interface("eth0")
        bandwidth_monitor.start_monitoring()
        
        # Stop monitoring
        bandwidth_monitor.stop_monitoring()
        assert bandwidth_monitor.is_monitoring is False
    
    def test_get_current_bandwidth(self, bandwidth_monitor):
        """Test getting current bandwidth data."""
        bandwidth_monitor.set_monitoring_interface("eth0")
        
        # Get current bandwidth
        data = bandwidth_monitor.get_current_bandwidth()
        
        assert data is not None
        assert data.interface_name == "eth0"
        assert isinstance(data.timestamp, datetime)
        assert isinstance(data.bytes_sent, int)
        assert isinstance(data.bytes_received, int)
    
    def test_get_bandwidth_history(self, bandwidth_monitor):
        """Test getting bandwidth history."""
        bandwidth_monitor.set_monitoring_interface("eth0")
        
        # Add some test data to history
        test_data = BandwidthData(
            timestamp=datetime.now(),
            interface_name="eth0",
            bytes_sent=1024,
            bytes_received=2048,
            upload_speed=10.0,
            download_speed=20.0
        )
        bandwidth_monitor.bandwidth_history.append(test_data)
        
        # Get history
        history = bandwidth_monitor.get_bandwidth_history()
        assert len(history) == 1
        assert history[0].interface_name == "eth0"
        
        # Get history with time range
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now() + timedelta(hours=1)
        history = bandwidth_monitor.get_bandwidth_history(start_time, end_time)
        assert len(history) == 1
    
    def test_clear_history(self, bandwidth_monitor):
        """Test clearing bandwidth history."""
        # Add test data
        test_data = BandwidthData(
            timestamp=datetime.now(),
            interface_name="eth0"
        )
        bandwidth_monitor.bandwidth_history.append(test_data)
        
        # Clear history
        bandwidth_monitor.clear_history()
        assert len(bandwidth_monitor.bandwidth_history) == 0
    
    def test_add_alert_rule(self, bandwidth_monitor):
        """Test adding alert rules."""
        rule = AlertRule(
            name="High Download",
            alert_type=AlertType.DOWNLOAD_SPEED,
            threshold=100.0
        )
        
        # Add rule
        bandwidth_monitor.add_alert_rule(rule)
        assert len(bandwidth_monitor.alert_rules) == 1
        assert bandwidth_monitor.alert_rules[0].name == "High Download"
    
    def test_remove_alert_rule(self, bandwidth_monitor):
        """Test removing alert rules."""
        rule = AlertRule(
            name="Test Rule",
            alert_type=AlertType.UPLOAD_SPEED,
            threshold=50.0
        )
        
        # Add and remove rule
        bandwidth_monitor.add_alert_rule(rule)
        success = bandwidth_monitor.remove_alert_rule("Test Rule")
        assert success is True
        assert len(bandwidth_monitor.alert_rules) == 0
        
        # Try to remove non-existent rule
        success = bandwidth_monitor.remove_alert_rule("Non-existent")
        assert success is False
    
    def test_update_alert_rule(self, bandwidth_monitor):
        """Test updating alert rules."""
        rule = AlertRule(
            name="Test Rule",
            alert_type=AlertType.UPLOAD_SPEED,
            threshold=50.0
        )
        
        # Add rule
        bandwidth_monitor.add_alert_rule(rule)
        
        # Update rule
        success = bandwidth_monitor.update_alert_rule(
            "Test Rule",
            threshold=75.0,
            enabled=False
        )
        assert success is True
        
        updated_rule = bandwidth_monitor.alert_rules[0]
        assert updated_rule.threshold == 75.0
        assert updated_rule.enabled is False
    
    def test_check_alerts(self, bandwidth_monitor):
        """Test alert checking."""
        # Add alert rule
        rule = AlertRule(
            name="High Download",
            alert_type=AlertType.DOWNLOAD_SPEED,
            threshold=50.0,
            duration=1  # 1 second for testing
        )
        bandwidth_monitor.add_alert_rule(rule)
        
        # Create test data that triggers alert
        test_data = BandwidthData(
            timestamp=datetime.now(),
            interface_name="eth0",
            download_speed=100.0  # Above threshold
        )
        
        # Check alerts
        triggered_alerts = bandwidth_monitor._check_alerts(test_data)
        
        # Should trigger alert
        assert len(triggered_alerts) == 1
        assert triggered_alerts[0].name == "High Download"
    
    def test_export_data_csv(self, bandwidth_monitor, tmp_path):
        """Test exporting data to CSV."""
        # Add test data
        test_data = BandwidthData(
            timestamp=datetime.now(),
            interface_name="eth0",
            bytes_sent=1024,
            bytes_received=2048,
            upload_speed=10.0,
            download_speed=20.0
        )
        bandwidth_monitor.bandwidth_history.append(test_data)
        
        # Export to CSV
        export_file = tmp_path / "bandwidth_data.csv"
        success = bandwidth_monitor.export_data(
            str(export_file),
            DataExportFormat.CSV
        )
        
        assert success is True
        assert export_file.exists()
        
        # Check file content
        content = export_file.read_text()
        assert "timestamp" in content
        assert "interface_name" in content
        assert "eth0" in content
    
    def test_export_data_json(self, bandwidth_monitor, tmp_path):
        """Test exporting data to JSON."""
        # Add test data
        test_data = BandwidthData(
            timestamp=datetime.now(),
            interface_name="eth0",
            bytes_sent=1024,
            bytes_received=2048
        )
        bandwidth_monitor.bandwidth_history.append(test_data)
        
        # Export to JSON
        export_file = tmp_path / "bandwidth_data.json"
        success = bandwidth_monitor.export_data(
            str(export_file),
            DataExportFormat.JSON
        )
        
        assert success is True
        assert export_file.exists()
        
        # Check file content
        content = export_file.read_text()
        assert '"interface_name": "eth0"' in content
    
    def test_import_data(self, bandwidth_monitor, tmp_path):
        """Test importing bandwidth data."""
        # Create test JSON file
        import json
        test_data = [{
            "timestamp": datetime.now().isoformat(),
            "interface_name": "eth0",
            "bytes_sent": 1024,
            "bytes_received": 2048,
            "upload_speed": 10.0,
            "download_speed": 20.0,
            "total_bytes_sent": 10240,
            "total_bytes_received": 20480
        }]
        
        import_file = tmp_path / "import_data.json"
        import_file.write_text(json.dumps(test_data))
        
        # Import data
        success = bandwidth_monitor.import_data(str(import_file))
        assert success is True
        assert len(bandwidth_monitor.bandwidth_history) == 1
        assert bandwidth_monitor.bandwidth_history[0].interface_name == "eth0"
    
    def test_get_statistics(self, bandwidth_monitor):
        """Test getting bandwidth statistics."""
        # Add test data
        timestamps = [
            datetime.now() - timedelta(seconds=10),
            datetime.now() - timedelta(seconds=5),
            datetime.now()
        ]
        
        for i, timestamp in enumerate(timestamps):
            data = BandwidthData(
                timestamp=timestamp,
                interface_name="eth0",
                upload_speed=10.0 + i,
                download_speed=20.0 + i * 2
            )
            bandwidth_monitor.bandwidth_history.append(data)
        
        # Get statistics
        stats = bandwidth_monitor.get_statistics()
        
        assert "total_data_points" in stats
        assert "average_upload_speed" in stats
        assert "average_download_speed" in stats
        assert "max_upload_speed" in stats
        assert "max_download_speed" in stats
        assert "min_upload_speed" in stats
        assert "min_download_speed" in stats
        
        assert stats["total_data_points"] == 3
        assert stats["max_upload_speed"] == 12.0
        assert stats["max_download_speed"] == 24.0
    
    def test_monitoring_thread_safety(self, bandwidth_monitor):
        """Test thread safety of monitoring operations."""
        bandwidth_monitor.set_monitoring_interface("eth0")
        
        # Start monitoring in background
        bandwidth_monitor.start_monitoring()
        
        # Perform operations from multiple threads
        def worker():
            for _ in range(10):
                bandwidth_monitor.get_current_bandwidth()
                time.sleep(0.01)
        
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # Stop monitoring
        bandwidth_monitor.stop_monitoring()
        
        # Should not have any errors
        assert True  # If we get here, no exceptions were raised
    
    def test_error_handling(self, bandwidth_monitor):
        """Test error handling in bandwidth monitoring."""
        # Test with invalid interface
        bandwidth_monitor.platform_detector.get_interface_stats.return_value = None
        
        data = bandwidth_monitor.get_current_bandwidth()
        assert data is None
        
        # Test export with invalid path
        success = bandwidth_monitor.export_data(
            "/invalid/path/file.csv",
            DataExportFormat.CSV
        )
        assert success is False
        
        # Test import with invalid file
        success = bandwidth_monitor.import_data("/non/existent/file.json")
        assert success is False


class TestBandwidthMonitorIntegration:
    """Integration tests for BandwidthMonitor."""
    
    def test_signal_emission(self, bandwidth_monitor):
        """Test signal emission during monitoring."""
        # Track signal emissions
        data_updated_signals = []
        status_changed_signals = []
        
        def on_data_updated(data):
            data_updated_signals.append(data)
        
        def on_status_changed(status):
            status_changed_signals.append(status)
        
        # Connect signals
        bandwidth_monitor.data_updated.connect(on_data_updated)
        bandwidth_monitor.status_changed.connect(on_status_changed)
        
        # Start monitoring
        bandwidth_monitor.set_monitoring_interface("eth0")
        bandwidth_monitor.start_monitoring()
        
        # Wait for some data
        time.sleep(0.2)
        
        # Stop monitoring
        bandwidth_monitor.stop_monitoring()
        
        # Verify signals were emitted
        assert len(status_changed_signals) >= 2  # At least start and stop
        # Data signals depend on timing, so we don't assert specific counts
    
    def test_configuration_integration(self, bandwidth_monitor):
        """Test integration with configuration service."""
        # Test that configuration is properly loaded
        assert bandwidth_monitor.update_interval > 0
        assert bandwidth_monitor.history_size > 0
        
        # Test configuration updates
        bandwidth_monitor.set_update_interval(2000)
        assert bandwidth_monitor.update_interval == 2000
        
        bandwidth_monitor.set_history_size(200)
        assert bandwidth_monitor.history_size == 200


if __name__ == "__main__":
    pytest.main([__file__])