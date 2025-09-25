"""Mock objects and test fixtures for network connectivity tests."""

from .network_mocks import (
    MockNetworkInterface,
    MockNetworkStats,
    MockPlatformDetector,
    MockNetworkData,
    MockDeviceDiscovery,
)

from .service_mocks import (
    MockConfigService,
    MockLoggingService,
    MockNotificationService,
    MockMetricsService,
)

from .tool_mocks import (
    MockBandwidthMonitor,
    MockPortScanner,
    MockWiFiAnalyzer,
    MockLANFileTransfer,
)

__all__ = [
    "MockNetworkInterface",
    "MockNetworkStats",
    "MockPlatformDetector",
    "MockNetworkData",
    "MockDeviceDiscovery",
    "MockConfigService",
    "MockLoggingService",
    "MockNotificationService",
    "MockMetricsService",
    "MockBandwidthMonitor",
    "MockPortScanner",
    "MockWiFiAnalyzer",
    "MockLANFileTransfer",
]
