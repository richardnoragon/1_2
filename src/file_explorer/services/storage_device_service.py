"""
StorageDeviceService: Discover available storage devices (cross-platform).

This service provides platform-specific drive discovery for Windows, macOS, and Linux.
"""

import logging
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class StorageDevice:
    """Represents a storage device/drive."""

    path: Path
    label: str
    free_space: int  # bytes
    total_space: int  # bytes
    is_system: bool = False

    @property
    def used_space(self) -> int:
        """Calculate used space."""
        return self.total_space - self.free_space

    @property
    def usage_percent(self) -> float:
        """Calculate usage percentage."""
        if self.total_space == 0:
            return 0.0
        return (self.used_space / self.total_space) * 100


class StorageDeviceService:
    """Service for discovering available storage devices."""

    def __init__(self):
        """Initialize the storage device service."""
        self.logger = logging.getLogger("RFU.FileExplorer.StorageDeviceService")
        self.platform = platform.system()
        self.logger.info(f"StorageDeviceService initialized for {self.platform}")

    def get_available_drives(self) -> List[StorageDevice]:
        """
        Retrieve all available storage devices.

        Returns:
            List[StorageDevice]: Available drives/mount points
        """
        try:
            if self.platform == "Windows":
                return self._get_windows_drives()
            elif self.platform == "Darwin":  # macOS
                return self._get_macos_drives()
            elif self.platform == "Linux":
                return self._get_linux_drives()
            else:
                self.logger.warning(f"Unsupported platform: {self.platform}")
                return []

        except Exception as e:
            self.logger.error(f"Error getting available drives: {e}")
            return []

    def is_available(self, path: Path) -> bool:
        """
        Check if a path is currently accessible.

        Args:
            path: Path to check

        Returns:
            bool: True if accessible, False otherwise
        """
        try:
            return path.exists()
        except (OSError, PermissionError):
            return False

    def _get_windows_drives(self) -> List[StorageDevice]:
        """
        Get available drives on Windows.

        Returns:
            List[StorageDevice]: Windows drive letters
        """
        import string

        drives = []

        # Check all drive letters A-Z
        for letter in string.ascii_uppercase:
            drive_path = Path(f"{letter}:\\")

            if not drive_path.exists():
                continue

            try:
                # Get drive info using os.statvfs or ctypes
                import ctypes

                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(drive_path)),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes),
                )

                # Get volume label
                try:
                    volume_name_buffer = ctypes.create_unicode_buffer(1024)
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        ctypes.c_wchar_p(str(drive_path)),
                        volume_name_buffer,
                        ctypes.sizeof(volume_name_buffer),
                        None,
                        None,
                        None,
                        None,
                        0,
                    )
                    label = volume_name_buffer.value or f"Drive {letter}"
                except Exception:
                    label = f"Drive {letter}"

                # Check if system drive (typically C:)
                is_system = letter == "C"

                device = StorageDevice(
                    path=drive_path,
                    label=label,
                    free_space=free_bytes.value,
                    total_space=total_bytes.value,
                    is_system=is_system,
                )
                drives.append(device)

            except Exception as e:
                self.logger.debug(f"Error reading drive {letter}: {e}")
                continue

        # Sort with system drive first
        drives.sort(key=lambda d: (not d.is_system, d.path))

        return drives

    def _get_macos_drives(self) -> List[StorageDevice]:
        """
        Get available drives on macOS.

        Returns:
            List[StorageDevice]: macOS volumes
        """
        import os

        drives = []
        volumes_path = Path("/Volumes")

        if not volumes_path.exists():
            return drives

        try:
            # System root
            root_path = Path("/")
            if root_path.exists():
                stat_info = os.statvfs(root_path)
                drives.append(
                    StorageDevice(
                        path=root_path,
                        label="Macintosh HD",
                        free_space=stat_info.f_bavail * stat_info.f_frsize,
                        total_space=stat_info.f_blocks * stat_info.f_frsize,
                        is_system=True,
                    )
                )

            # Other volumes
            for volume in volumes_path.iterdir():
                if not volume.is_dir():
                    continue

                try:
                    stat_info = os.statvfs(volume)
                    drives.append(
                        StorageDevice(
                            path=volume,
                            label=volume.name,
                            free_space=stat_info.f_bavail * stat_info.f_frsize,
                            total_space=stat_info.f_blocks * stat_info.f_frsize,
                            is_system=False,
                        )
                    )
                except Exception as e:
                    self.logger.debug(f"Error reading volume {volume}: {e}")

        except Exception as e:
            self.logger.error(f"Error getting macOS drives: {e}")

        return drives

    def _get_linux_drives(self) -> List[StorageDevice]:
        """
        Get available drives on Linux.

        Returns:
            List[StorageDevice]: Linux mount points
        """
        import os

        drives = []

        try:
            # Parse /proc/mounts or /etc/mtab
            mounts_file = Path("/proc/mounts")
            if not mounts_file.exists():
                mounts_file = Path("/etc/mtab")

            if not mounts_file.exists():
                return drives

            with open(mounts_file, "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 2:
                        continue

                    device = parts[0]
                    mount_point = Path(parts[1])

                    # Filter out virtual filesystems
                    if device.startswith(
                        ("/dev/loop", "/dev/ram", "tmpfs", "devtmpfs")
                    ):
                        continue

                    if not mount_point.exists():
                        continue

                    try:
                        stat_info = os.statvfs(mount_point)

                        # Determine label
                        label = mount_point.name or str(mount_point)
                        if mount_point == Path("/"):
                            label = "Root"
                            is_system = True
                        else:
                            is_system = False

                        drives.append(
                            StorageDevice(
                                path=mount_point,
                                label=label,
                                free_space=stat_info.f_bavail * stat_info.f_frsize,
                                total_space=stat_info.f_blocks * stat_info.f_frsize,
                                is_system=is_system,
                            )
                        )

                    except Exception as e:
                        self.logger.debug(f"Error reading mount {mount_point}: {e}")

        except Exception as e:
            self.logger.error(f"Error getting Linux drives: {e}")

        # Sort with system drive first
        drives.sort(key=lambda d: (not d.is_system, d.path))

        return drives


# Singleton instance
_storage_device_service: Optional[StorageDeviceService] = None


def get_storage_device_service() -> StorageDeviceService:
    """
    Get the singleton storage device service instance.

    Returns:
        StorageDeviceService: The storage device service instance
    """
    global _storage_device_service
    if _storage_device_service is None:
        _storage_device_service = StorageDeviceService()
    return _storage_device_service
