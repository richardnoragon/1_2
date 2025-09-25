"""Platform-specific filesystem implementations."""

import logging
from typing import Optional

from ....core.platform_detector import get_platform_detector, SupportedPlatform
from core.error_handler import error_handler


def get_platform_filesystem_impl():
    """Get the appropriate platform-specific filesystem implementation.

    Returns:
        Platform-specific filesystem implementation or None
    """
    platform_detector = get_platform_detector()
    logger = logging.getLogger("RFU.DiagnosticsMonitoring.FilesystemPlatform")

    try:
        if platform_detector.platform == SupportedPlatform.WINDOWS:
            from .windows_filesystem import WindowsFilesystemImpl

            return WindowsFilesystemImpl()
        elif platform_detector.platform == SupportedPlatform.MACOS:
            from .macos_filesystem import MacOSFilesystemImpl

            return MacOSFilesystemImpl()
        elif platform_detector.platform == SupportedPlatform.LINUX:
            from .linux_filesystem import LinuxFilesystemImpl

            return LinuxFilesystemImpl()
        else:
            logger.warning(
                f"Unsupported platform: {platform_detector.platform}"
            )
            return None

    except ImportError as e:
        logger.error(f"Failed to import platform implementation: {e}")
        error_handler.handle_error(e, "get_platform_filesystem_impl")
        return None
    except Exception as e:
        logger.error(f"Error loading platform implementation: {e}")
        error_handler.handle_error(e, "get_platform_filesystem_impl")
        return None


__all__ = ["get_platform_filesystem_impl"]
