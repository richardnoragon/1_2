"""Diagnostics Monitoring System for Richard's File Utilities.

This module provides comprehensive cross-platform system monitoring
capabilities including disk health, performance tracking, filesystem
integrity, and battery monitoring.
"""

from .core.monitor_base import MonitorBase
from .core.platform_detector import PlatformDetector
from .core.data_collector import DataCollector
from .core.alert_manager import AlertManager

__version__ = "1.0.0"
__author__ = "Richard's File Utilities Team"

__all__ = [
    'MonitorBase',
    'PlatformDetector', 
    'DataCollector',
    'AlertManager'
]