"""Diagnostics Monitoring System for Richard's File Utilities.

This module provides comprehensive cross-platform system monitoring
capabilities including disk health, performance tracking, filesystem
integrity, and battery monitoring.
"""

# Import core components
try:
    from .core.monitor_base import MonitorBase
    from .core.platform_detector import PlatformDetector
    from .core.data_collector import DataCollector
    from .core.alert_manager import AlertManager
    CORE_AVAILABLE = True
except ImportError:
    MonitorBase = None
    PlatformDetector = None
    DataCollector = None
    AlertManager = None
    CORE_AVAILABLE = False

# Import GUI components
try:
    from .gui.disk_health_widget import DiskHealthWidget
    from .gui.performance_widget import PerformanceWidget
    from .gui.battery_health_widget import BatteryHealthWidget
    GUI_WIDGETS_AVAILABLE = True
except ImportError:
    DiskHealthWidget = None
    PerformanceWidget = None
    BatteryHealthWidget = None
    GUI_WIDGETS_AVAILABLE = False

# Import the main comprehensive GUI class
try:
    from .system_diagnostics_gui import SystemDiagnosticsGUI
    from .system_diagnostics_gui import create_system_diagnostics_gui
    MAIN_GUI_AVAILABLE = True
except ImportError:
    SystemDiagnosticsGUI = None
    create_system_diagnostics_gui = None
    MAIN_GUI_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "Richard's File Utilities Team"

__all__ = [
    'MonitorBase',
    'PlatformDetector',
    'DataCollector',
    'AlertManager',
    'SystemDiagnosticsGUI',
    'create_system_diagnostics_gui',
    'DiskHealthWidget',
    'PerformanceWidget',
    'BatteryHealthWidget',
    'CORE_AVAILABLE',
    'GUI_WIDGETS_AVAILABLE',
    'MAIN_GUI_AVAILABLE'
]