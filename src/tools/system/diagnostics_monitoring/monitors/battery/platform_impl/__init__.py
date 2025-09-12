"""Platform-specific battery monitoring implementations.

This module contains platform-specific implementations for battery monitoring:
- Windows: WMI battery queries, Power Management APIs, battery status monitoring
- macOS: IOKit Power Sources, system_profiler battery info, pmset integration
- Linux: /sys/class/power_supply, ACPI battery information, upower integration
"""

from ...core.platform_detector import get_platform_detector, SupportedPlatform

__all__ = []

# Platform-specific imports based on current platform
_platform_detector = get_platform_detector()

if _platform_detector.is_windows():
    try:
        from .windows_battery import WindowsBatteryMonitor
        __all__.append('WindowsBatteryMonitor')
    except ImportError:
        pass

if _platform_detector.is_macos():
    try:
        from .macos_battery import MacOSBatteryMonitor
        __all__.append('MacOSBatteryMonitor')
    except ImportError:
        pass

if _platform_detector.is_linux():
    try:
        from .linux_battery import LinuxBatteryMonitor
        __all__.append('LinuxBatteryMonitor')
    except ImportError:
        pass


def get_platform_battery_monitor():
    """Get the appropriate platform-specific battery monitor.
    
    Returns:
        Platform-specific battery monitor class or None if not available
    """
    if _platform_detector.is_windows():
        try:
            from .windows_battery import WindowsBatteryMonitor
            return WindowsBatteryMonitor
        except ImportError:
            pass
    
    if _platform_detector.is_macos():
        try:
            from .macos_battery import MacOSBatteryMonitor
            return MacOSBatteryMonitor
        except ImportError:
            pass
    
    if _platform_detector.is_linux():
        try:
            from .linux_battery import LinuxBatteryMonitor
            return LinuxBatteryMonitor
        except ImportError:
            pass
    
    return None