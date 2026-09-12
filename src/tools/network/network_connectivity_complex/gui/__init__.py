"""Network Connectivity GUI Components.

This module provides comprehensive GUI components for all network connectivity tools,
including bandwidth monitoring, port scanning, Wi-Fi analysis, and LAN file transfer.

The GUI components follow the established RFU patterns and integrate seamlessly with
the existing theme system and base classes.
"""

from .hub import NetworkConnectivityHub
from .widgets.bandwidth_monitor_widget import BandwidthMonitorWidget

# Import additional widgets only if they exist; others can be added when implemented
try:
    from .widgets.port_scanner_widget import PortScannerWidget
except ImportError:
    PortScannerWidget = None

try:
    from .widgets.wifi_analyzer_widget import WiFiAnalyzerWidget
except ImportError:
    WiFiAnalyzerWidget = None

try:
    from .widgets.lan_file_transfer_widget import LANFileTransferWidget
except ImportError:
    LANFileTransferWidget = None

__all__ = [
    "NetworkConnectivityHub",
    "BandwidthMonitorWidget",
]

