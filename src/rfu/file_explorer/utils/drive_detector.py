"""
Cross-Platform Drive Detection System for RFU Multi-Pane File Explorer
Enterprise-Grade Drive Management with Real-Time Monitoring

This module provides comprehensive drive detection and monitoring:

- Cross-platform drive enumeration (Windows/macOS/Linux)
- Real-time mount point monitoring and notifications
- Network drive detection and availability checking
- USB/removable media detection with hot-plug support
- Drive capacity and space monitoring
- Mount/unmount event handling
- Performance optimization for drive queries
- Accessibility support for drive information

Drive Detection Features:
- Windows: Drive letters, UNC paths, network shares
- macOS: Volume mounts, external drives, network volumes  
- Linux: Mount points, file systems, device detection
- Real-time monitoring of drive changes
- Drive type classification (local, network, removable, optical)
- Capacity and free space tracking
- Mount state validation and error handling

Author: RFU Development Team
Created: 2025-01-12
Version: 1.0.0 (Phase 1 Foundation)
"""

import logging
import platform
import shutil
import sys
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import psutil
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

# Platform-specific imports
if sys.platform == 'win32':
    import win32api
    import win32file
    import wmi
elif sys.platform == 'darwin':
    import plistlib
    import subprocess
elif sys.platform.startswith('linux'):
    import subprocess


class DriveType(Enum):
    """Drive type classification."""
    UNKNOWN = "unknown"
    LOCAL = "local"
    REMOVABLE = "removable"
    NETWORK = "network"
    OPTICAL = "optical"
    RAM = "ram"
    VIRTUAL = "virtual"


class DriveStatus(Enum):
    """Drive status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MOUNTING = "mounting"
    UNMOUNTING = "unmounting"
    ERROR = "error"


class DriveInfo:
    """
    Comprehensive drive information container.
    
    Stores all relevant information about a detected drive
    including capacity, type, mount point, and status.
    """
    
    def __init__(self, mount_point: str):
        """
        Initialize drive information.
        
        Args:
            mount_point: Drive mount point or path
        """
        self.mount_point = mount_point
        self.label = ""
        self.file_system = ""
        self.drive_type = DriveType.UNKNOWN
        self.status = DriveStatus.AVAILABLE
        
        # Capacity information
        self.total_size = 0
        self.free_size = 0
        self.used_size = 0
        
        # Device information
        self.device_name = ""
        self.device_id = ""
        self.vendor = ""
        self.model = ""
        
        # Network information (for network drives)
        self.network_path = ""
        self.server_name = ""
        
        # State information
        self.is_ready = False
        self.is_removable = False
        self.is_network = False
        self.is_mounted = True
        
        # Timestamps
        self.detected_at = datetime.now()
        self.last_accessed = None
        self.last_updated = datetime.now()
    
    def update_capacity(self):
        """Update drive capacity information."""
        try:
            if self.status == DriveStatus.AVAILABLE and Path(self.mount_point).exists():
                usage = shutil.disk_usage(self.mount_point)
                self.total_size = usage.total
                self.free_size = usage.free
                self.used_size = usage.total - usage.free
                self.last_updated = datetime.now()
                self.is_ready = True
        except (OSError, PermissionError):
            self.is_ready = False
    
    def get_capacity_info(self) -> Dict[str, Any]:
        """
        Get formatted capacity information.
        
        Returns:
            Dict: Capacity information with human-readable sizes
        """
        def format_size(size_bytes: int) -> str:
            """Format bytes to human-readable string."""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} PB"
        
        if self.total_size > 0:
            usage_percent = (self.used_size / self.total_size) * 100
        else:
            usage_percent = 0
        
        return {
            'total': format_size(self.total_size),
            'free': format_size(self.free_size),
            'used': format_size(self.used_size),
            'total_bytes': self.total_size,
            'free_bytes': self.free_size,
            'used_bytes': self.used_size,
            'usage_percent': usage_percent
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert drive info to dictionary.
        
        Returns:
            Dict: Drive information
        """
        return {
            'mount_point': self.mount_point,
            'label': self.label,
            'file_system': self.file_system,
            'drive_type': self.drive_type.value,
            'status': self.status.value,
            'device_name': self.device_name,
            'device_id': self.device_id,
            'vendor': self.vendor,
            'model': self.model,
            'network_path': self.network_path,
            'server_name': self.server_name,
            'is_ready': self.is_ready,
            'is_removable': self.is_removable,
            'is_network': self.is_network,
            'is_mounted': self.is_mounted,
            'capacity': self.get_capacity_info(),
            'detected_at': self.detected_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'last_updated': self.last_updated.isoformat()
        }
    
    def __str__(self) -> str:
        return f"DriveInfo({self.mount_point}, {self.label}, {self.drive_type.value})"
    
    def __repr__(self) -> str:
        return f"DriveInfo(mount_point='{self.mount_point}', label='{self.label}')"


class WindowsDriveDetector:
    """Windows-specific drive detection implementation."""
    
    def __init__(self):
        """Initialize Windows drive detector."""
        self.logger = logging.getLogger('RFU.FileExplorer.WindowsDriveDetector')
        self.wmi_connection = None
        self._initialize_wmi()
    
    def _initialize_wmi(self):
        """Initialize WMI connection."""
        try:
            self.wmi_connection = wmi.WMI()
        except Exception as e:
            self.logger.warning(f"Failed to initialize WMI: {e}")
    
    def detect_drives(self) -> List[DriveInfo]:
        """
        Detect all available drives on Windows.
        
        Returns:
            List[DriveInfo]: List of detected drives
        """
        drives = []
        
        try:
            # Get drive letters
            drive_letters = win32api.GetLogicalDriveStrings()
            drive_list = drive_letters.split('\x00')[:-1]
            
            for drive_letter in drive_list:
                try:
                    drive_info = self._get_drive_info(drive_letter)
                    if drive_info:
                        drives.append(drive_info)
                except Exception as e:
                    self.logger.warning(f"Failed to get info for drive {drive_letter}: {e}")
            
            # Get network drives
            network_drives = self._get_network_drives()
            drives.extend(network_drives)
            
        except Exception as e:
            self.logger.error(f"Failed to detect Windows drives: {e}")
        
        return drives
    
    def _get_drive_info(self, drive_path: str) -> Optional[DriveInfo]:
        """
        Get detailed information for a Windows drive.
        
        Args:
            drive_path: Drive path (e.g., 'C:\\')
            
        Returns:
            Optional[DriveInfo]: Drive information or None
        """
        try:
            drive_info = DriveInfo(drive_path.rstrip('\\'))
            
            # Get drive type
            drive_type = win32file.GetDriveType(drive_path)
            drive_info.drive_type = self._map_windows_drive_type(drive_type)
            
            # Get volume information
            try:
                volume_info = win32api.GetVolumeInformation(drive_path)
                drive_info.label = volume_info[0] or f"Drive {drive_path[0]}"
                drive_info.file_system = volume_info[4]
            except Exception:
                drive_info.label = f"Drive {drive_path[0]}"
            
            # Update capacity
            drive_info.update_capacity()
            
            # Set drive properties
            drive_info.is_removable = drive_type == win32file.DRIVE_REMOVABLE
            drive_info.is_network = drive_type == win32file.DRIVE_REMOTE
            
            # Get additional WMI information
            self._enhance_with_wmi_info(drive_info)
            
            return drive_info
            
        except Exception as e:
            self.logger.warning(f"Failed to get Windows drive info for {drive_path}: {e}")
            return None
    
    def _map_windows_drive_type(self, drive_type: int) -> DriveType:
        """
        Map Windows drive type to DriveType enum.
        
        Args:
            drive_type: Windows drive type constant
            
        Returns:
            DriveType: Mapped drive type
        """
        mapping = {
            win32file.DRIVE_FIXED: DriveType.LOCAL,
            win32file.DRIVE_REMOVABLE: DriveType.REMOVABLE,
            win32file.DRIVE_REMOTE: DriveType.NETWORK,
            win32file.DRIVE_CDROM: DriveType.OPTICAL,
            win32file.DRIVE_RAMDISK: DriveType.RAM
        }
        return mapping.get(drive_type, DriveType.UNKNOWN)
    
    def _enhance_with_wmi_info(self, drive_info: DriveInfo):
        """
        Enhance drive info with WMI data.
        
        Args:
            drive_info: Drive information to enhance
        """
        if not self.wmi_connection:
            return
        
        try:
            # Query logical disk
            drive_letter = drive_info.mount_point.replace(':', '')
            for disk in self.wmi_connection.Win32_LogicalDisk(DeviceID=f"{drive_letter}:"):
                drive_info.device_id = disk.DeviceID
                if hasattr(disk, 'VolumeName') and disk.VolumeName:
                    drive_info.label = disk.VolumeName
                
                # Get physical disk information
                if hasattr(disk, 'Size') and disk.Size:
                    drive_info.total_size = int(disk.Size)
                if hasattr(disk, 'FreeSpace') and disk.FreeSpace:
                    drive_info.free_size = int(disk.FreeSpace)
                    drive_info.used_size = drive_info.total_size - drive_info.free_size
                
        except Exception as e:
            self.logger.debug(f"Failed to enhance drive info with WMI: {e}")
    
    def _get_network_drives(self) -> List[DriveInfo]:
        """
        Get network drives.
        
        Returns:
            List[DriveInfo]: List of network drives
        """
        network_drives = []
        
        if not self.wmi_connection:
            return network_drives
        
        try:
            for disk in self.wmi_connection.Win32_LogicalDisk(DriveType=4):  # Network drives
                drive_info = DriveInfo(disk.DeviceID)
                drive_info.drive_type = DriveType.NETWORK
                drive_info.is_network = True
                drive_info.label = disk.VolumeName or f"Network Drive {disk.DeviceID}"
                
                if hasattr(disk, 'ProviderName'):
                    drive_info.network_path = disk.ProviderName
                
                drive_info.update_capacity()
                network_drives.append(drive_info)
                
        except Exception as e:
            self.logger.warning(f"Failed to get network drives: {e}")
        
        return network_drives


class MacOSDriveDetector:
    """macOS-specific drive detection implementation."""
    
    def __init__(self):
        """Initialize macOS drive detector."""
        self.logger = logging.getLogger('RFU.FileExplorer.MacOSDriveDetector')
    
    def detect_drives(self) -> List[DriveInfo]:
        """
        Detect all available drives on macOS.
        
        Returns:
            List[DriveInfo]: List of detected drives
        """
        drives = []
        
        try:
            # Get mounted volumes
            volumes_path = Path('/Volumes')
            if volumes_path.exists():
                for volume in volumes_path.iterdir():
                    if volume.is_dir() and not volume.name.startswith('.'):
                        drive_info = self._get_volume_info(str(volume))
                        if drive_info:
                            drives.append(drive_info)
            
            # Add root volume
            root_drive = self._get_volume_info('/')
            if root_drive:
                drives.insert(0, root_drive)
            
        except Exception as e:
            self.logger.error(f"Failed to detect macOS drives: {e}")
        
        return drives
    
    def _get_volume_info(self, volume_path: str) -> Optional[DriveInfo]:
        """
        Get detailed information for a macOS volume.
        
        Args:
            volume_path: Volume path
            
        Returns:
            Optional[DriveInfo]: Drive information or None
        """
        try:
            drive_info = DriveInfo(volume_path)
            
            # Get volume name
            volume_name = Path(volume_path).name
            if volume_path == '/':
                drive_info.label = "Macintosh HD"
            else:
                drive_info.label = volume_name
            
            # Get file system information using diskutil
            self._get_diskutil_info(drive_info)
            
            # Update capacity
            drive_info.update_capacity()
            
            return drive_info
            
        except Exception as e:
            self.logger.warning(f"Failed to get macOS volume info for {volume_path}: {e}")
            return None
    
    def _get_diskutil_info(self, drive_info: DriveInfo):
        """
        Get disk information using diskutil.
        
        Args:
            drive_info: Drive information to enhance
        """
        try:
            # Run diskutil info command
            result = subprocess.run(
                ['diskutil', 'info', '-plist', drive_info.mount_point],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse plist output
                plist_data = plistlib.loads(result.stdout.encode())
                
                # Extract information
                if 'VolumeName' in plist_data:
                    drive_info.label = plist_data['VolumeName']
                
                if 'FilesystemType' in plist_data:
                    drive_info.file_system = plist_data['FilesystemType']
                
                if 'DeviceIdentifier' in plist_data:
                    drive_info.device_id = plist_data['DeviceIdentifier']
                
                # Determine drive type
                if plist_data.get('Internal', False):
                    drive_info.drive_type = DriveType.LOCAL
                elif plist_data.get('Protocol') == 'Network':
                    drive_info.drive_type = DriveType.NETWORK
                    drive_info.is_network = True
                elif plist_data.get('Removable', False):
                    drive_info.drive_type = DriveType.REMOVABLE
                    drive_info.is_removable = True
                else:
                    drive_info.drive_type = DriveType.LOCAL
                
        except Exception as e:
            self.logger.debug(f"Failed to get diskutil info: {e}")


class LinuxDriveDetector:
    """Linux-specific drive detection implementation."""
    
    def __init__(self):
        """Initialize Linux drive detector."""
        self.logger = logging.getLogger('RFU.FileExplorer.LinuxDriveDetector')
    
    def detect_drives(self) -> List[DriveInfo]:
        """
        Detect all available drives on Linux.
        
        Returns:
            List[DriveInfo]: List of detected drives
        """
        drives = []
        
        try:
            # Parse /proc/mounts for mounted file systems
            mounts = self._parse_proc_mounts()
            
            for mount_info in mounts:
                drive_info = self._create_drive_info(mount_info)
                if drive_info:
                    drives.append(drive_info)
            
        except Exception as e:
            self.logger.error(f"Failed to detect Linux drives: {e}")
        
        return drives
    
    def _parse_proc_mounts(self) -> List[Dict[str, str]]:
        """
        Parse /proc/mounts file.
        
        Returns:
            List[Dict]: Mount information
        """
        mounts = []
        
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        mount_info = {
                            'device': parts[0],
                            'mount_point': parts[1],
                            'file_system': parts[2],
                            'options': parts[3],
                            'dump': parts[4],
                            'pass': parts[5]
                        }
                        
                        # Filter relevant mount points
                        if self._is_relevant_mount(mount_info):
                            mounts.append(mount_info)
        
        except Exception as e:
            self.logger.warning(f"Failed to parse /proc/mounts: {e}")
        
        return mounts
    
    def _is_relevant_mount(self, mount_info: Dict[str, str]) -> bool:
        """
        Check if mount point is relevant for display.
        
        Args:
            mount_info: Mount information
            
        Returns:
            bool: True if relevant
        """
        mount_point = mount_info['mount_point']
        file_system = mount_info['file_system']
        device = mount_info['device']
        
        # Skip virtual file systems
        virtual_fs = {'proc', 'sysfs', 'devfs', 'tmpfs', 'devpts', 'debugfs'}
        if file_system in virtual_fs:
            return False
        
        # Skip bind mounts and special mounts
        if mount_point.startswith(('/proc', '/sys', '/dev', '/run')):
            return False
        
        # Skip if device is not a real device
        if not device.startswith('/dev/') and not device.startswith('//'):
            return False
        
        return True
    
    def _create_drive_info(self, mount_info: Dict[str, str]) -> Optional[DriveInfo]:
        """
        Create drive info from mount information.
        
        Args:
            mount_info: Mount information
            
        Returns:
            Optional[DriveInfo]: Drive information or None
        """
        try:
            drive_info = DriveInfo(mount_info['mount_point'])
            drive_info.file_system = mount_info['file_system']
            drive_info.device_name = mount_info['device']
            
            # Set label based on mount point
            if mount_info['mount_point'] == '/':
                drive_info.label = "Root"
            else:
                drive_info.label = Path(mount_info['mount_point']).name.title()
            
            # Determine drive type
            self._determine_drive_type(drive_info, mount_info)
            
            # Update capacity
            drive_info.update_capacity()
            
            return drive_info
            
        except Exception as e:
            self.logger.warning(f"Failed to create drive info: {e}")
            return None
    
    def _determine_drive_type(self, drive_info: DriveInfo, mount_info: Dict[str, str]):
        """
        Determine drive type based on mount information.
        
        Args:
            drive_info: Drive information to update
            mount_info: Mount information
        """
        device = mount_info['device']
        mount_point = mount_info['mount_point']
        file_system = mount_info['file_system']
        
        # Network file systems
        if file_system in {'nfs', 'nfs4', 'cifs', 'smb', 'sshfs'}:
            drive_info.drive_type = DriveType.NETWORK
            drive_info.is_network = True
        
        # Network paths
        elif device.startswith('//'):
            drive_info.drive_type = DriveType.NETWORK
            drive_info.is_network = True
            drive_info.network_path = device
        
        # Optical drives
        elif '/cdrom' in mount_point or '/dvd' in mount_point:
            drive_info.drive_type = DriveType.OPTICAL
        
        # Removable media (USB, etc.)
        elif '/media' in mount_point or '/mnt' in mount_point:
            drive_info.drive_type = DriveType.REMOVABLE
            drive_info.is_removable = True
        
        # Local drives
        else:
            drive_info.drive_type = DriveType.LOCAL


class DriveMonitor(QThread):
    """
    Background thread for monitoring drive changes.
    
    Monitors file system for drive mount/unmount events
    and emits signals when changes are detected.
    """
    
    # Signals for drive events
    driveAdded = pyqtSignal(object)  # DriveInfo
    driveRemoved = pyqtSignal(str)   # mount_point
    driveChanged = pyqtSignal(object)  # DriveInfo
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize drive monitor.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger('RFU.FileExplorer.DriveMonitor')
        self.running = False
        self.check_interval = 5.0  # seconds
        self.previous_drives = {}  # mount_point -> DriveInfo
        
        # Platform-specific detector
        if sys.platform == 'win32':
            self.detector = WindowsDriveDetector()
        elif sys.platform == 'darwin':
            self.detector = MacOSDriveDetector()
        else:
            self.detector = LinuxDriveDetector()
    
    def run(self):
        """Main monitoring loop."""
        self.running = True
        self.logger.info("Drive monitoring started")
        
        # Initial detection
        self._update_drives()
        
        while self.running:
            try:
                time.sleep(self.check_interval)
                if self.running:
                    self._update_drives()
                    
            except Exception as e:
                self.logger.error(f"Error in drive monitoring: {e}")
                time.sleep(self.check_interval)
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
        self.logger.info("Drive monitoring stopped")
    
    def _update_drives(self):
        """Update drive list and emit change signals."""
        try:
            current_drives = {}
            detected_drives = self.detector.detect_drives()
            
            for drive in detected_drives:
                current_drives[drive.mount_point] = drive
            
            # Check for new drives
            for mount_point, drive_info in current_drives.items():
                if mount_point not in self.previous_drives:
                    self.driveAdded.emit(drive_info)
                    self.logger.info(f"Drive added: {mount_point}")
                elif self._drive_changed(self.previous_drives[mount_point], drive_info):
                    self.driveChanged.emit(drive_info)
                    self.logger.debug(f"Drive changed: {mount_point}")
            
            # Check for removed drives
            for mount_point in self.previous_drives:
                if mount_point not in current_drives:
                    self.driveRemoved.emit(mount_point)
                    self.logger.info(f"Drive removed: {mount_point}")
            
            self.previous_drives = current_drives
            
        except Exception as e:
            self.logger.error(f"Failed to update drives: {e}")
    
    def _drive_changed(self, old_drive: DriveInfo, new_drive: DriveInfo) -> bool:
        """
        Check if drive information has changed significantly.
        
        Args:
            old_drive: Previous drive information
            new_drive: Current drive information
            
        Returns:
            bool: True if drive changed
        """
        # Check significant changes
        if old_drive.label != new_drive.label:
            return True
        
        if old_drive.is_ready != new_drive.is_ready:
            return True
        
        if old_drive.status != new_drive.status:
            return True
        
        # Check capacity changes (allow some tolerance)
        if abs(old_drive.free_size - new_drive.free_size) > (1024 * 1024 * 100):  # 100MB
            return True
        
        return False


class CrossPlatformDriveDetector(QObject):
    """
    Enterprise-grade cross-platform drive detection system.
    
    Provides unified interface for drive detection across
    Windows, macOS, and Linux with real-time monitoring.
    """
    
    # Signals for drive events
    drivesUpdated = pyqtSignal(list)  # List[DriveInfo]
    driveAdded = pyqtSignal(object)   # DriveInfo
    driveRemoved = pyqtSignal(str)    # mount_point
    driveChanged = pyqtSignal(object) # DriveInfo
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize cross-platform drive detector.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Setup logging
        self.logger = logging.getLogger('RFU.FileExplorer.CrossPlatformDriveDetector')
        
        # Current drives
        self.drives = {}  # mount_point -> DriveInfo
        
        # Platform detection
        self.platform = platform.system()
        self.logger.info(f"Initialized for platform: {self.platform}")
        
        # Platform-specific detector
        if sys.platform == 'win32':
            self.platform_detector = WindowsDriveDetector()
        elif sys.platform == 'darwin':
            self.platform_detector = MacOSDriveDetector()
        else:
            self.platform_detector = LinuxDriveDetector()
        
        # Drive monitoring
        self.monitor = DriveMonitor()
        self.monitor.driveAdded.connect(self._on_drive_added)
        self.monitor.driveRemoved.connect(self._on_drive_removed)
        self.monitor.driveChanged.connect(self._on_drive_changed)
        
        # Refresh timer for capacity updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_drive_info)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Initial detection
        self.refresh_drives()
        
        self.logger.info("Cross-platform drive detector initialized")
    
    def start_monitoring(self):
        """Start real-time drive monitoring."""
        if not self.monitor.isRunning():
            self.monitor.start()
            self.logger.info("Drive monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time drive monitoring."""
        if self.monitor.isRunning():
            self.monitor.stop()
            self.monitor.wait()
            self.logger.info("Drive monitoring stopped")
    
    def refresh_drives(self) -> List[DriveInfo]:
        """
        Refresh drive list.
        
        Returns:
            List[DriveInfo]: Current drives
        """
        try:
            detected_drives = self.platform_detector.detect_drives()
            
            # Update drives dictionary
            self.drives.clear()
            for drive in detected_drives:
                self.drives[drive.mount_point] = drive
            
            # Sort drives for consistent ordering
            sorted_drives = sorted(detected_drives, key=lambda d: d.mount_point)
            
            # Emit signal
            self.drivesUpdated.emit(sorted_drives)
            
            self.logger.debug(f"Refreshed drives: {len(detected_drives)} found")
            return sorted_drives
            
        except Exception as e:
            self.logger.error(f"Failed to refresh drives: {e}")
            return []
    
    def get_drives(self) -> List[DriveInfo]:
        """
        Get current drive list.
        
        Returns:
            List[DriveInfo]: Current drives
        """
        return sorted(list(self.drives.values()), key=lambda d: d.mount_point)
    
    def get_drive(self, mount_point: str) -> Optional[DriveInfo]:
        """
        Get specific drive by mount point.
        
        Args:
            mount_point: Drive mount point
            
        Returns:
            Optional[DriveInfo]: Drive information or None
        """
        return self.drives.get(mount_point)
    
    def get_drives_by_type(self, drive_type: DriveType) -> List[DriveInfo]:
        """
        Get drives filtered by type.
        
        Args:
            drive_type: Drive type to filter by
            
        Returns:
            List[DriveInfo]: Filtered drives
        """
        return [drive for drive in self.drives.values() if drive.drive_type == drive_type]
    
    def get_available_drives(self) -> List[DriveInfo]:
        """
        Get only available (ready) drives.
        
        Returns:
            List[DriveInfo]: Available drives
        """
        return [drive for drive in self.drives.values() if drive.is_ready]
    
    def is_path_on_removable_drive(self, path: str) -> bool:
        """
        Check if path is on a removable drive.
        
        Args:
            path: File system path
            
        Returns:
            bool: True if on removable drive
        """
        try:
            path_obj = Path(path).resolve()
            
            for drive in self.drives.values():
                try:
                    if path_obj.is_relative_to(drive.mount_point):
                        return drive.is_removable
                except ValueError:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Failed to check removable drive for {path}: {e}")
            return False
    
    def is_path_on_network_drive(self, path: str) -> bool:
        """
        Check if path is on a network drive.
        
        Args:
            path: File system path
            
        Returns:
            bool: True if on network drive
        """
        try:
            path_obj = Path(path).resolve()
            
            for drive in self.drives.values():
                try:
                    if path_obj.is_relative_to(drive.mount_point):
                        return drive.is_network
                except ValueError:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Failed to check network drive for {path}: {e}")
            return False
    
    def get_drive_for_path(self, path: str) -> Optional[DriveInfo]:
        """
        Get drive information for a given path.
        
        Args:
            path: File system path
            
        Returns:
            Optional[DriveInfo]: Drive information or None
        """
        try:
            path_obj = Path(path).resolve()
            
            # Find the drive with the longest matching mount point
            best_match = None
            best_match_length = 0
            
            for drive in self.drives.values():
                try:
                    if path_obj.is_relative_to(drive.mount_point):
                        mount_length = len(drive.mount_point)
                        if mount_length > best_match_length:
                            best_match = drive
                            best_match_length = mount_length
                except ValueError:
                    continue
            
            return best_match
            
        except Exception as e:
            self.logger.warning(f"Failed to get drive for path {path}: {e}")
            return None
    
    def _on_drive_added(self, drive_info: DriveInfo):
        """
        Handle drive added event.
        
        Args:
            drive_info: Added drive information
        """
        self.drives[drive_info.mount_point] = drive_info
        self.driveAdded.emit(drive_info)
        self.logger.info(f"Drive added: {drive_info.mount_point}")
    
    def _on_drive_removed(self, mount_point: str):
        """
        Handle drive removed event.
        
        Args:
            mount_point: Removed drive mount point
        """
        if mount_point in self.drives:
            del self.drives[mount_point]
        self.driveRemoved.emit(mount_point)
        self.logger.info(f"Drive removed: {mount_point}")
    
    def _on_drive_changed(self, drive_info: DriveInfo):
        """
        Handle drive changed event.
        
        Args:
            drive_info: Changed drive information
        """
        self.drives[drive_info.mount_point] = drive_info
        self.driveChanged.emit(drive_info)
        self.logger.debug(f"Drive changed: {drive_info.mount_point}")
    
    def _refresh_drive_info(self):
        """Refresh drive information (capacity, etc.)."""
        try:
            for drive in self.drives.values():
                drive.update_capacity()
                
        except Exception as e:
            self.logger.warning(f"Failed to refresh drive info: {e}")
    
    def get_detector_status(self) -> Dict[str, Any]:
        """
        Get detector status information.
        
        Returns:
            Dict: Status information
        """
        return {
            'platform': self.platform,
            'monitoring_active': self.monitor.isRunning(),
            'drive_count': len(self.drives),
            'drives_by_type': {
                drive_type.value: len(self.get_drives_by_type(drive_type))
                for drive_type in DriveType
            },
            'available_drives': len(self.get_available_drives())
        }


# For testing and development
if __name__ == '__main__':
    import sys

    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = QApplication(sys.argv)
    
    # Create drive detector
    detector = CrossPlatformDriveDetector()
    
    # Test drive detection
    def test_drive_detection():
        print(f"Platform: {detector.platform}")
        print(f"Status: {detector.get_detector_status()}")
        
        drives = detector.get_drives()
        print(f"\nDetected {len(drives)} drives:")
        
        for drive in drives:
            print(f"\nDrive: {drive.mount_point}")
            print(f"  Label: {drive.label}")
            print(f"  Type: {drive.drive_type.value}")
            print(f"  File System: {drive.file_system}")
            print(f"  Ready: {drive.is_ready}")
            
            if drive.is_ready:
                capacity = drive.get_capacity_info()
                print(f"  Total: {capacity['total']}")
                print(f"  Free: {capacity['free']}")
                print(f"  Used: {capacity['used']} ({capacity['usage_percent']:.1f}%)")
    
    # Connect signals
    detector.driveAdded.connect(lambda drive: print(f"ADDED: {drive.mount_point}"))
    detector.driveRemoved.connect(lambda mount: print(f"REMOVED: {mount}"))
    detector.driveChanged.connect(lambda drive: print(f"CHANGED: {drive.mount_point}"))
    
    # Start monitoring
    detector.start_monitoring()
    
    # Test after 1 second
    QTimer.singleShot(1000, test_drive_detection)
    
    # Run for 30 seconds then exit
    QTimer.singleShot(30000, app.quit)
    
    sys.exit(app.exec_())