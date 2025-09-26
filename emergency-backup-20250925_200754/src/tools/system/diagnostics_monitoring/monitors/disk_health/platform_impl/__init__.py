"""Platform-specific disk health monitoring implementations."""

import logging

from ....core.platform_detector import get_platform_detector


def get_platform_disk_monitor():
    """Get the platform-specific disk monitor implementation.

    Returns:
        Platform-specific disk monitor class or None if not available
    """
    logger = logging.getLogger("RFU.DiagnosticsMonitoring.PlatformImpl")
    platform_detector = get_platform_detector()

    try:
        if platform_detector.is_windows():
            from .windows_disk import WindowsDiskMonitor

            return WindowsDiskMonitor
        elif platform_detector.is_macos():
            # TODO: Implement macOS-specific monitor
            logger.info("macOS-specific disk monitor not yet implemented")
            return None
        elif platform_detector.is_linux():
            # TODO: Implement Linux-specific monitor
            logger.info("Linux-specific disk monitor not yet implemented")
            return None
        else:
            logger.warning(
                "Unsupported platform for platform-specific monitoring"
            )
            return None

    except ImportError as e:
        logger.warning(f"Platform-specific disk monitor not available: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading platform-specific disk monitor: {e}")
        return None


__all__ = ["get_platform_disk_monitor"]
