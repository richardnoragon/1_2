"""Network Connectivity Module for Richard's File Utilities.

This module provides comprehensive network connectivity tools including
bandwidth monitoring, connectivity testing, port scanning, and network
diagnostics.
"""

from .core.network_base import NetworkToolBase
from .core.connection_manager import ConnectionManager
from .core.platform_network import PlatformNetworkDetector
from .core.security_validator import SecurityValidator
from .tools.bandwidth_monitor import BandwidthMonitor
from .tools.port_scanner import PortScanner
from .tools.wifi_analyzer import WiFiAnalyzer

__version__ = "1.0.0"
__author__ = "Richard's File Utilities Team"

__all__ = [
    'NetworkToolBase',
    'ConnectionManager',
    'PlatformNetworkDetector',
    'SecurityValidator',
    'BandwidthMonitor',
    'PortScanner',
    'WiFiAnalyzer'
]