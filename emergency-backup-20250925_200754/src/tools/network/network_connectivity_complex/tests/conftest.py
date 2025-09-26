"""Pytest configuration and shared fixtures for network connectivity tests."""

import pytest
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import network connectivity components
from ..core.network_base import NetworkToolBase
from ..core.platform_network import (
    PlatformNetworkDetector,
    NetworkInterface,
    NetworkStats,
)
from ..core.connection_manager import ConnectionManager, ConnectionState
from ..core.security_validator import SecurityValidator
from ..core.performance_analyzer import PerformanceAnalyzer
from ..core.config_service import ConfigurationService
from ..core.logging_service import LoggingService
from ..core.notification_service import NotificationService
from ..core.metrics_service import MetricsService
from ..tools.bandwidth_monitor import BandwidthMonitor
from ..tools.port_scanner import PortScanner
from ..tools.wifi_analyzer import WiFiAnalyzer
from ..tools.lan_file_transfer import LANFileTransfer


# Test Configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "timeout": 5.0,
        "max_retries": 3,
        "test_data_dir": "test_data",
        "mock_network_interfaces": True,
        "enable_performance_tests": True,
        "enable_stress_tests": False,  # Disabled by default
        "test_network_range": "192.168.1.0/24",
        "test_ports": [22, 80, 443, 8080],
        "test_file_sizes": [1024, 10240, 102400],  # 1KB, 10KB, 100KB
    }


# Temporary Directory Fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_data_dir(temp_dir):
    """Create test data directory with sample files."""
    data_dir = temp_dir / "test_data"
    data_dir.mkdir()

    # Create sample test files
    (data_dir / "small_file.txt").write_text("Small test file content")
    (data_dir / "medium_file.txt").write_text("Medium test file content" * 100)
    (data_dir / "large_file.txt").write_text("Large test file content" * 1000)

    return data_dir


# Mock Network Interface Fixtures
@pytest.fixture
def mock_network_interface():
    """Create a mock network interface."""
    return NetworkInterface(
        name="eth0",
        display_name="Ethernet",
        description="Mock Ethernet Interface",
        mac_address="00:11:22:33:44:55",
        ip_addresses=["192.168.1.100"],
        is_up=True,
        is_wireless=False,
        speed_mbps=1000,
        mtu=1500,
    )


@pytest.fixture
def mock_wireless_interface():
    """Create a mock wireless interface."""
    return NetworkInterface(
        name="wlan0",
        display_name="Wi-Fi",
        description="Mock Wireless Interface",
        mac_address="AA:BB:CC:DD:EE:FF",
        ip_addresses=["192.168.1.101"],
        is_up=True,
        is_wireless=True,
        speed_mbps=150,
        mtu=1500,
    )


@pytest.fixture
def mock_network_stats():
    """Create mock network statistics."""
    return NetworkStats(
        interface_name="eth0",
        bytes_sent=1024000,
        bytes_received=2048000,
        packets_sent=1000,
        packets_received=2000,
        errors_in=0,
        errors_out=0,
        drops_in=0,
        drops_out=0,
        timestamp=datetime.now(),
    )


@pytest.fixture
def mock_platform_detector(
    mock_network_interface, mock_wireless_interface, mock_network_stats
):
    """Create a mock platform network detector."""
    detector = Mock(spec=PlatformNetworkDetector)
    detector.get_network_interfaces.return_value = [
        mock_network_interface,
        mock_wireless_interface,
    ]
    detector.get_interface_stats.return_value = mock_network_stats
    detector.is_interface_wireless.side_effect = lambda name: name == "wlan0"
    detector.get_default_gateway.return_value = "192.168.1.1"
    detector.get_dns_servers.return_value = ["8.8.8.8", "8.8.4.4"]
    return detector


# Service Fixtures
@pytest.fixture
def mock_config_service():
    """Create a mock configuration service."""
    service = Mock(spec=ConfigurationService)
    service.get_configuration.return_value = {
        "general": {
            "default_timeout": 5000,
            "max_concurrent_operations": 10,
            "enable_logging": True,
            "log_level": "INFO",
        },
        "bandwidth_monitor": {
            "update_interval": 1000,
            "history_size": 100,
            "enable_alerts": True,
        },
        "port_scanner": {
            "default_timeout": 3000,
            "max_threads": 50,
            "scan_techniques": ["tcp_connect", "tcp_syn"],
        },
        "wifi_analyzer": {
            "scan_interval": 5000,
            "channel_bands": ["2.4GHz", "5GHz"],
            "enable_security_analysis": True,
        },
        "lan_file_transfer": {
            "discovery_port": 8888,
            "transfer_port_range": [9000, 9100],
            "encryption_enabled": True,
            "authentication_required": True,
        },
    }
    service.get_setting.side_effect = (
        lambda key, default=None: service.get_configuration().get(key, default)
    )
    return service


@pytest.fixture
def mock_logging_service():
    """Create a mock logging service."""
    service = Mock(spec=LoggingService)
    service.log_structured = Mock()
    service.get_logger.return_value = Mock()
    return service


@pytest.fixture
def mock_notification_service():
    """Create a mock notification service."""
    service = Mock(spec=NotificationService)
    service.send_notification = Mock()
    service.add_rule = Mock()
    return service


@pytest.fixture
def mock_metrics_service():
    """Create a mock metrics service."""
    service = Mock(spec=MetricsService)
    service.record_metric = Mock()
    service.get_metrics = Mock(return_value={})
    return service


# Tool Fixtures
@pytest.fixture
def bandwidth_monitor(
    mock_platform_detector, mock_config_service, mock_logging_service
):
    """Create a bandwidth monitor instance for testing."""
    with (
        patch(
            "network_connectivity.tools.bandwidth_monitor.get_config_service",
            return_value=mock_config_service,
        ),
        patch(
            "network_connectivity.tools.bandwidth_monitor.get_logging_service",
            return_value=mock_logging_service,
        ),
    ):
        monitor = BandwidthMonitor()
        monitor.platform_detector = mock_platform_detector
        return monitor


@pytest.fixture
def port_scanner(
    mock_platform_detector, mock_config_service, mock_logging_service
):
    """Create a port scanner instance for testing."""
    with (
        patch(
            "network_connectivity.tools.port_scanner.get_config_service",
            return_value=mock_config_service,
        ),
        patch(
            "network_connectivity.tools.port_scanner.get_logging_service",
            return_value=mock_logging_service,
        ),
    ):
        scanner = PortScanner()
        scanner.platform_detector = mock_platform_detector
        return scanner


@pytest.fixture
def wifi_analyzer(
    mock_platform_detector, mock_config_service, mock_logging_service
):
    """Create a WiFi analyzer instance for testing."""
    with (
        patch(
            "network_connectivity.tools.wifi_analyzer.get_config_service",
            return_value=mock_config_service,
        ),
        patch(
            "network_connectivity.tools.wifi_analyzer.get_logging_service",
            return_value=mock_logging_service,
        ),
    ):
        analyzer = WiFiAnalyzer()
        analyzer.platform_detector = mock_platform_detector
        return analyzer


@pytest.fixture
def lan_file_transfer(
    mock_platform_detector, mock_config_service, mock_logging_service
):
    """Create a LAN file transfer instance for testing."""
    with (
        patch(
            "network_connectivity.tools.lan_file_transfer.get_config_service",
            return_value=mock_config_service,
        ),
        patch(
            "network_connectivity.tools.lan_file_transfer.get_logging_service",
            return_value=mock_logging_service,
        ),
    ):
        transfer = LANFileTransfer()
        transfer.platform_detector = mock_platform_detector
        return transfer


# Core Component Fixtures
@pytest.fixture
def connection_manager(mock_platform_detector):
    """Create a connection manager instance for testing."""
    manager = ConnectionManager()
    manager.platform_detector = mock_platform_detector
    return manager


@pytest.fixture
def security_validator():
    """Create a security validator instance for testing."""
    return SecurityValidator()


@pytest.fixture
def performance_analyzer():
    """Create a performance analyzer instance for testing."""
    return PerformanceAnalyzer()


# GUI Test Fixtures
@pytest.fixture
def qt_app():
    """Create QApplication for GUI tests."""
    try:
        from PyQt6.QtWidgets import QApplication
        import sys

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        yield app

        # Clean up
        app.processEvents()

    except ImportError:
        pytest.skip("PyQt6 not available for GUI tests")


@pytest.fixture
def mock_qt_widget():
    """Create a mock Qt widget for testing."""
    try:
        from PyQt6.QtWidgets import QWidget
        from unittest.mock import Mock

        widget = Mock(spec=QWidget)
        widget.show = Mock()
        widget.hide = Mock()
        widget.close = Mock()
        widget.update = Mock()

        return widget

    except ImportError:
        pytest.skip("PyQt6 not available for GUI tests")


# Network Test Data Fixtures
@pytest.fixture
def sample_scan_results():
    """Sample port scan results for testing."""
    return {
        "192.168.1.1": {
            "22": {
                "state": "open",
                "service": "ssh",
                "version": "OpenSSH 8.0",
            },
            "80": {
                "state": "open",
                "service": "http",
                "version": "Apache 2.4",
            },
            "443": {
                "state": "open",
                "service": "https",
                "version": "Apache 2.4",
            },
        },
        "192.168.1.100": {
            "22": {"state": "closed"},
            "80": {"state": "filtered"},
            "443": {
                "state": "open",
                "service": "https",
                "version": "nginx 1.18",
            },
        },
    }


@pytest.fixture
def sample_wifi_networks():
    """Sample WiFi networks for testing."""
    return [
        {
            "ssid": "TestNetwork1",
            "bssid": "00:11:22:33:44:55",
            "channel": 6,
            "frequency": 2437,
            "signal_strength": -45,
            "security": ["WPA2-PSK"],
            "encryption": "AES",
        },
        {
            "ssid": "TestNetwork2",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "channel": 36,
            "frequency": 5180,
            "signal_strength": -60,
            "security": ["WPA3-SAE"],
            "encryption": "AES",
        },
    ]


@pytest.fixture
def sample_bandwidth_data():
    """Sample bandwidth monitoring data for testing."""
    base_time = datetime.now()
    return [
        {
            "timestamp": base_time - timedelta(seconds=10),
            "bytes_sent": 1000,
            "bytes_received": 2000,
            "upload_speed": 100,
            "download_speed": 200,
        },
        {
            "timestamp": base_time - timedelta(seconds=5),
            "bytes_sent": 1500,
            "bytes_received": 3000,
            "upload_speed": 100,
            "download_speed": 200,
        },
        {
            "timestamp": base_time,
            "bytes_sent": 2000,
            "bytes_received": 4000,
            "upload_speed": 100,
            "download_speed": 200,
        },
    ]


# Performance Test Fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance tests."""
    return {
        "max_execution_time": 10.0,  # seconds
        "max_memory_usage": 100,  # MB
        "max_cpu_usage": 80,  # percentage
        "iterations": 100,
        "concurrent_operations": 10,
    }


@pytest.fixture
def stress_test_config():
    """Configuration for stress tests."""
    return {
        "duration": 60,  # seconds
        "max_connections": 1000,
        "request_rate": 100,  # requests per second
        "memory_limit": 500,  # MB
        "cpu_limit": 90,  # percentage
    }


# Error Simulation Fixtures
@pytest.fixture
def network_error_simulator():
    """Simulate various network errors for testing."""

    class NetworkErrorSimulator:
        def __init__(self):
            self.error_types = [
                "connection_timeout",
                "connection_refused",
                "host_unreachable",
                "network_unreachable",
                "dns_resolution_failed",
                "ssl_handshake_failed",
            ]

        def simulate_error(self, error_type: str):
            """Simulate a specific network error."""
            if error_type == "connection_timeout":
                raise TimeoutError("Connection timed out")
            elif error_type == "connection_refused":
                raise ConnectionRefusedError("Connection refused")
            elif error_type == "host_unreachable":
                raise OSError("Host unreachable")
            elif error_type == "network_unreachable":
                raise OSError("Network unreachable")
            elif error_type == "dns_resolution_failed":
                raise OSError("DNS resolution failed")
            elif error_type == "ssl_handshake_failed":
                raise OSError("SSL handshake failed")
            else:
                raise ValueError(f"Unknown error type: {error_type}")

    return NetworkErrorSimulator()


# Test Markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line("markers", "gui: mark test as a GUI test")
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line("markers", "stress: mark test as a stress test")
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "windows: mark test as Windows-specific"
    )
    config.addinivalue_line("markers", "macos: mark test as macOS-specific")
    config.addinivalue_line("markers", "linux: mark test as Linux-specific")


# Test Collection Hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "gui" in str(item.fspath):
            item.add_marker(pytest.mark.gui)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # Add slow marker for tests that might take longer
        if any(
            keyword in item.name.lower()
            for keyword in ["stress", "performance", "large"]
        ):
            item.add_marker(pytest.mark.slow)


# Cleanup Fixtures
@pytest.fixture(autouse=True)
def cleanup_threads():
    """Ensure all threads are cleaned up after tests."""
    initial_thread_count = threading.active_count()

    yield

    # Wait for threads to finish
    timeout = 5.0
    start_time = time.time()

    while (
        threading.active_count() > initial_thread_count
        and time.time() - start_time < timeout
    ):
        time.sleep(0.1)

    # Log warning if threads didn't clean up
    if threading.active_count() > initial_thread_count:
        print(
            f"Warning: {threading.active_count() - initial_thread_count} threads still active after test"
        )


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Reset any singleton instances that might interfere with tests
    yield

    # Clean up any cached instances
    # This would be implemented based on the actual singleton patterns used
