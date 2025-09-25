"""Platform-specific performance monitoring implementations.

This module provides platform-specific optimizations and implementations
for performance monitoring on Windows, macOS, and Linux systems.
"""

import logging
from typing import Optional, Any

from ....core.platform_detector import get_platform_detector, SupportedPlatform
from core.error_handler import error_handler


def get_platform_performance_impl() -> Optional[Any]:
    """Get the appropriate platform-specific performance implementation.

    Returns:
        Platform-specific implementation instance or None
    """
    logger = logging.getLogger("RFU.DiagnosticsMonitoring.PlatformPerformance")
    platform_detector = get_platform_detector()

    try:
        if platform_detector.platform == SupportedPlatform.WINDOWS:
            from .windows_perf import WindowsPerformanceImpl

            return WindowsPerformanceImpl()
        elif platform_detector.platform == SupportedPlatform.MACOS:
            from .macos_perf import MacOSPerformanceImpl

            return MacOSPerformanceImpl()
        elif platform_detector.platform == SupportedPlatform.LINUX:
            from .linux_perf import LinuxPerformanceImpl

            return LinuxPerformanceImpl()
        else:
            logger.warning(
                f"No performance implementation for platform: {platform_detector.platform}"
            )
            return None

    except ImportError as e:
        logger.warning(
            f"Platform-specific performance implementation not available: {e}"
        )
        return None
    except Exception as e:
        logger.error(f"Error loading platform performance implementation: {e}")
        error_handler.handle_error(e, "get_platform_performance_impl")
        return None


__all__ = ["get_platform_performance_impl"]
