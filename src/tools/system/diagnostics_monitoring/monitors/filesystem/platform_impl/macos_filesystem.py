"""macOS-specific filesystem implementation with HFS+/APFS and fsck support."""

import os
import subprocess
import logging
import re
import plistlib
from datetime import datetime
from typing import Dict, Any, List, Optional

from ....core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class MacOSFilesystemImpl:
    """macOS filesystem implementation.

    Provides macOS-specific filesystem operations including:
    - HFS+ and APFS filesystem analysis
    - fsck integration and automation
    - Disk Utility integration
    - Volume and container analysis
    - System integrity checking
    - Time Machine integration
    """

    def __init__(self):
        """Initialize macOS filesystem implementation."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.MacOSFilesystem"
        )
        self.platform_detector = get_platform_detector()

        # macOS-specific tools
        self.tools = {
            "diskutil": "/usr/sbin/diskutil",
            "fsck": "/sbin/fsck",
            "fsck_hfs": "/sbin/fsck_hfs",
            "fsck_apfs": "/usr/sbin/fsck_apfs",
            "system_profiler": "/usr/sbin/system_profiler",
            "tmutil": "/usr/bin/tmutil",
            "ioreg": "/usr/sbin/ioreg",
            "mount": "/sbin/mount",
            "df": "/bin/df",
        }

        # Check tool availability
        self._check_tool_availability()

        # Supported filesystems
        self.supported_filesystems = {
            "apfs": {
                "name": "Apple File System",
                "features": [
                    "snapshots",
                    "clones",
                    "encryption",
                    "compression",
                ],
                "fsck_tool": "fsck_apfs",
            },
            "hfs": {
                "name": "Hierarchical File System Plus",
                "features": ["journaling", "case_sensitivity", "compression"],
                "fsck_tool": "fsck_hfs",
            },
            "msdos": {
                "name": "MS-DOS FAT",
                "features": [],
                "fsck_tool": "fsck_msdos",
            },
            "exfat": {
                "name": "Extended FAT",
                "features": [],
                "fsck_tool": "fsck_exfat",
            },
        }

    def _check_tool_availability(self) -> None:
        """Check availability of macOS filesystem tools."""
        for tool_name, tool_path in self.tools.items():
            if not os.path.exists(tool_path):
                self.logger.warning(
                    f"Tool not found: {tool_name} at {tool_path}"
                )
                self.tools[tool_name] = None
            else:
                try:
                    # Test tool execution
                    result = subprocess.run(
                        [tool_path], capture_output=True, text=True, timeout=5
                    )
                    # Most tools return non-zero when run without args, that's OK
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    self.logger.warning(f"Tool not executable: {tool_name}")
                    self.tools[tool_name] = None
                except Exception as e:
                    self.logger.error(f"Error testing tool {tool_name}: {e}")
                    self.tools[tool_name] = None

    def get_filesystem_info(self) -> Dict[str, Any]:
        """Get comprehensive macOS filesystem information.

        Returns:
            Dict containing filesystem information
        """
        try:
            info = {
                "platform": "macos",
                "timestamp": datetime.now().isoformat(),
                "volumes": [],
                "containers": [],
                "system_info": {},
                "supported_filesystems": self.supported_filesystems.copy(),
                "tools_available": {
                    k: v is not None for k, v in self.tools.items()
                },
            }

            # Get volume information
            info["volumes"] = self._get_volume_info()

            # Get APFS container information
            info["containers"] = self._get_apfs_containers()

            # Get system filesystem information
            info["system_info"] = self._get_system_filesystem_info()

            return info

        except Exception as e:
            self.logger.error(f"Error getting filesystem info: {e}")
            error_handler.handle_error(
                e, "MacOSFilesystemImpl.get_filesystem_info"
            )
            return {"error": str(e), "platform": "macos"}

    def _get_volume_info(self) -> List[Dict[str, Any]]:
        """Get information about all mounted volumes.

        Returns:
            List of volume information dictionaries
        """
        volumes = []

        try:
            if not self.tools["diskutil"]:
                return []

            # Get list of all volumes
            result = subprocess.run(
                [self.tools["diskutil"], "list", "-plist"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                try:
                    plist_data = plistlib.loads(result.stdout.encode())

                    # Process each disk
                    for disk in plist_data.get("AllDisksAndPartitions", []):
                        volumes.extend(self._process_disk_partitions(disk))

                except Exception as e:
                    self.logger.error(f"Error parsing diskutil plist: {e}")

            return volumes

        except Exception as e:
            self.logger.error(f"Error getting volume info: {e}")
            return []

    def _process_disk_partitions(
        self, disk: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process partitions from a disk entry.

        Args:
            disk: Disk information from diskutil

        Returns:
            List of volume information
        """
        volumes = []

        try:
            # Process partitions
            for partition in disk.get("Partitions", []):
                volume_info = self._get_single_volume_info(partition)
                if volume_info:
                    volumes.append(volume_info)

            # Process APFS containers
            for container in disk.get("APFSContainers", []):
                for volume in container.get("Volumes", []):
                    volume_info = self._get_single_volume_info(volume)
                    if volume_info:
                        volumes.append(volume_info)

            return volumes

        except Exception as e:
            self.logger.error(f"Error processing disk partitions: {e}")
            return []

    def _get_single_volume_info(
        self, volume_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get information for a single volume.

        Args:
            volume_data: Volume data from diskutil

        Returns:
            Volume information dictionary or None
        """
        try:
            device_id = volume_data.get("DeviceIdentifier", "")
            if not device_id:
                return None

            volume_info = {
                "device_id": device_id,
                "volume_name": volume_data.get("VolumeName", "Unnamed"),
                "mount_point": volume_data.get("MountPoint", ""),
                "filesystem": volume_data.get("Content", "Unknown"),
                "size": volume_data.get("Size", 0),
                "free_space": 0,
                "used_space": 0,
                "is_mounted": "MountPoint" in volume_data,
                "is_bootable": volume_data.get("Bootable", False),
                "is_system": volume_data.get("SystemVolume", False),
                "encryption_status": "unknown",
                "health_status": "unknown",
                "filesystem_info": {},
            }

            # Get detailed volume information
            if self.tools["diskutil"]:
                detailed_info = self._get_detailed_volume_info(device_id)
                volume_info.update(detailed_info)

            # Get space usage if mounted
            if volume_info["is_mounted"] and volume_info["mount_point"]:
                space_info = self._get_volume_space_usage(
                    volume_info["mount_point"]
                )
                volume_info.update(space_info)

            # Get filesystem-specific information
            filesystem = volume_info["filesystem"].lower()
            if filesystem in self.supported_filesystems:
                fs_info = self._get_filesystem_specific_info(
                    device_id, filesystem
                )
                volume_info["filesystem_info"] = fs_info

            return volume_info

        except Exception as e:
            self.logger.error(f"Error getting single volume info: {e}")
            return None

    def _get_detailed_volume_info(self, device_id: str) -> Dict[str, Any]:
        """Get detailed information for a volume.

        Args:
            device_id: Device identifier

        Returns:
            Detailed volume information
        """
        detailed_info = {}

        try:
            result = subprocess.run(
                [self.tools["diskutil"], "info", "-plist", device_id],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                plist_data = plistlib.loads(result.stdout.encode())

                detailed_info.update(
                    {
                        "volume_uuid": plist_data.get("VolumeUUID", ""),
                        "disk_uuid": plist_data.get("DiskUUID", ""),
                        "partition_type": plist_data.get("PartitionType", ""),
                        "is_case_sensitive": plist_data.get(
                            "CaseSensitive", False
                        ),
                        "is_journaled": plist_data.get("Journaled", False),
                        "is_encrypted": plist_data.get("Encrypted", False),
                        "encryption_status": self._get_encryption_status(
                            plist_data
                        ),
                        "owners_enabled": plist_data.get(
                            "OwnersEnabled", False
                        ),
                        "permissions_enabled": plist_data.get(
                            "PermissionsEnabled", False
                        ),
                    }
                )

            return detailed_info

        except Exception as e:
            self.logger.error(
                f"Error getting detailed volume info for {device_id}: {e}"
            )
            return {}

    def _get_encryption_status(self, plist_data: Dict[str, Any]) -> str:
        """Get encryption status from diskutil plist data.

        Args:
            plist_data: Plist data from diskutil

        Returns:
            Encryption status string
        """
        if plist_data.get("Encrypted", False):
            if plist_data.get("EncryptionType") == "AES-XTS":
                return "encrypted_aes"
            else:
                return "encrypted"
        elif plist_data.get("FileVault", False):
            return "filevault"
        else:
            return "unencrypted"

    def _get_volume_space_usage(self, mount_point: str) -> Dict[str, Any]:
        """Get space usage for a mounted volume.

        Args:
            mount_point: Volume mount point

        Returns:
            Space usage information
        """
        space_info = {
            "free_space": 0,
            "used_space": 0,
            "total_space": 0,
            "free_percent": 0.0,
        }

        try:
            if self.tools["df"]:
                result = subprocess.run(
                    [self.tools["df"], "-k", mount_point],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) >= 2:
                        # Parse df output (1K blocks)
                        fields = lines[1].split()
                        if len(fields) >= 4:
                            total_kb = int(fields[1])
                            used_kb = int(fields[2])
                            free_kb = int(fields[3])

                            space_info.update(
                                {
                                    "total_space": total_kb * 1024,
                                    "used_space": used_kb * 1024,
                                    "free_space": free_kb * 1024,
                                    "free_percent": (
                                        (free_kb / total_kb * 100)
                                        if total_kb > 0
                                        else 0
                                    ),
                                }
                            )

            return space_info

        except Exception as e:
            self.logger.error(
                f"Error getting space usage for {mount_point}: {e}"
            )
            return space_info

    def _get_filesystem_specific_info(
        self, device_id: str, filesystem: str
    ) -> Dict[str, Any]:
        """Get filesystem-specific information.

        Args:
            device_id: Device identifier
            filesystem: Filesystem type

        Returns:
            Filesystem-specific information
        """
        fs_info = {}

        try:
            if filesystem == "apfs":
                fs_info = self._get_apfs_info(device_id)
            elif filesystem in ["hfs", "hfs+"]:
                fs_info = self._get_hfs_info(device_id)

            return fs_info

        except Exception as e:
            self.logger.error(
                f"Error getting {filesystem} info for {device_id}: {e}"
            )
            return {}

    def _get_apfs_info(self, device_id: str) -> Dict[str, Any]:
        """Get APFS-specific information.

        Args:
            device_id: Device identifier

        Returns:
            APFS information dictionary
        """
        apfs_info = {
            "container_uuid": "",
            "volume_group": "",
            "snapshots": [],
            "clones": [],
            "space_sharing": False,
            "case_sensitive": False,
            "encrypted": False,
        }

        try:
            if self.tools["diskutil"]:
                # Get APFS container info
                result = subprocess.run(
                    [self.tools["diskutil"], "apfs", "list", "-plist"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    plist_data = plistlib.loads(result.stdout.encode())

                    # Find our volume in the containers
                    for container in plist_data.get("Containers", []):
                        for volume in container.get("Volumes", []):
                            if volume.get("DeviceIdentifier") == device_id:
                                apfs_info.update(
                                    {
                                        "container_uuid": container.get(
                                            "ContainerUUID", ""
                                        ),
                                        "volume_group": volume.get(
                                            "VolumeGroupUUID", ""
                                        ),
                                        "case_sensitive": volume.get(
                                            "CaseSensitive", False
                                        ),
                                        "encrypted": volume.get(
                                            "Encrypted", False
                                        ),
                                        "space_sharing": container.get(
                                            "CapacityInUse", 0
                                        )
                                        > 0,
                                    }
                                )
                                break

                # Get snapshots
                apfs_info["snapshots"] = self._get_apfs_snapshots(device_id)

            return apfs_info

        except Exception as e:
            self.logger.error(f"Error getting APFS info for {device_id}: {e}")
            return apfs_info

    def _get_apfs_snapshots(self, device_id: str) -> List[Dict[str, Any]]:
        """Get APFS snapshots for a volume.

        Args:
            device_id: Device identifier

        Returns:
            List of snapshot information
        """
        snapshots = []

        try:
            if self.tools["diskutil"]:
                result = subprocess.run(
                    [
                        self.tools["diskutil"],
                        "apfs",
                        "listSnapshots",
                        device_id,
                        "-plist",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    plist_data = plistlib.loads(result.stdout.encode())

                    for snapshot in plist_data.get("Snapshots", []):
                        snapshots.append(
                            {
                                "name": snapshot.get("SnapshotName", ""),
                                "uuid": snapshot.get("SnapshotUUID", ""),
                                "creation_date": snapshot.get(
                                    "CreationDate", ""
                                ),
                                "sealed": snapshot.get("Sealed", False),
                            }
                        )

            return snapshots

        except Exception as e:
            self.logger.error(
                f"Error getting APFS snapshots for {device_id}: {e}"
            )
            return []

    def _get_hfs_info(self, device_id: str) -> Dict[str, Any]:
        """Get HFS+-specific information.

        Args:
            device_id: Device identifier

        Returns:
            HFS+ information dictionary
        """
        hfs_info = {
            "journaled": False,
            "case_sensitive": False,
            "compression_enabled": False,
            "block_size": 0,
            "total_blocks": 0,
            "free_blocks": 0,
        }

        try:
            if self.tools["diskutil"]:
                result = subprocess.run(
                    [self.tools["diskutil"], "info", "-plist", device_id],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    plist_data = plistlib.loads(result.stdout.encode())

                    hfs_info.update(
                        {
                            "journaled": plist_data.get("Journaled", False),
                            "case_sensitive": plist_data.get(
                                "CaseSensitive", False
                            ),
                            "block_size": plist_data.get("DeviceBlockSize", 0),
                            "total_blocks": plist_data.get("TotalSize", 0)
                            // plist_data.get("DeviceBlockSize", 1),
                            "free_blocks": plist_data.get("FreeSpace", 0)
                            // plist_data.get("DeviceBlockSize", 1),
                        }
                    )

            return hfs_info

        except Exception as e:
            self.logger.error(f"Error getting HFS+ info for {device_id}: {e}")
            return hfs_info

    def _get_apfs_containers(self) -> List[Dict[str, Any]]:
        """Get APFS container information.

        Returns:
            List of APFS container information
        """
        containers = []

        try:
            if not self.tools["diskutil"]:
                return []

            result = subprocess.run(
                [self.tools["diskutil"], "apfs", "list", "-plist"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                plist_data = plistlib.loads(result.stdout.encode())

                for container in plist_data.get("Containers", []):
                    container_info = {
                        "container_uuid": container.get("ContainerUUID", ""),
                        "physical_stores": container.get("PhysicalStores", []),
                        "capacity_ceiling": container.get(
                            "CapacityCeiling", 0
                        ),
                        "capacity_free": container.get("CapacityFree", 0),
                        "capacity_in_use": container.get("CapacityInUse", 0),
                        "volume_count": len(container.get("Volumes", [])),
                        "volumes": [],
                    }

                    # Add volume summaries
                    for volume in container.get("Volumes", []):
                        container_info["volumes"].append(
                            {
                                "device_id": volume.get(
                                    "DeviceIdentifier", ""
                                ),
                                "name": volume.get("VolumeName", ""),
                                "role": volume.get("VolumeRole", ""),
                                "size": volume.get("Size", 0),
                            }
                        )

                    containers.append(container_info)

            return containers

        except Exception as e:
            self.logger.error(f"Error getting APFS containers: {e}")
            return []

    def _get_system_filesystem_info(self) -> Dict[str, Any]:
        """Get system-wide filesystem information.

        Returns:
            System filesystem information
        """
        system_info = {
            "macos_version": "Unknown",
            "kernel_version": "Unknown",
            "boot_volume": "Unknown",
            "system_volume": "Unknown",
            "time_machine_status": "unknown",
            "sip_status": "unknown",
        }

        try:
            # Get macOS version
            system_info["macos_version"] = self._get_macos_version()

            # Get kernel version
            system_info["kernel_version"] = self._get_kernel_version()

            # Get boot and system volumes
            boot_info = self._get_boot_volume_info()
            system_info.update(boot_info)

            # Get Time Machine status
            system_info["time_machine_status"] = (
                self._get_time_machine_status()
            )

            # Get SIP status
            system_info["sip_status"] = self._get_sip_status()

            return system_info

        except Exception as e:
            self.logger.error(f"Error getting system filesystem info: {e}")
            return system_info

    def _get_macos_version(self) -> str:
        """Get macOS version information.

        Returns:
            macOS version string
        """
        try:
            if self.tools["system_profiler"]:
                result = subprocess.run(
                    [
                        self.tools["system_profiler"],
                        "SPSoftwareDataType",
                        "-xml",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    plist_data = plistlib.loads(result.stdout.encode())

                    for item in plist_data:
                        items = item.get("_items", [])
                        if items:
                            software_info = items[0]
                            version = software_info.get(
                                "system_version", "Unknown"
                            )
                            build = software_info.get("os_version", "")
                            return f"{version} ({build})" if build else version

            return "Unknown"

        except Exception as e:
            self.logger.error(f"Error getting macOS version: {e}")
            return "Unknown"

    def _get_kernel_version(self) -> str:
        """Get kernel version.

        Returns:
            Kernel version string
        """
        try:
            result = subprocess.run(
                ["uname", "-r"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                return result.stdout.strip()

            return "Unknown"

        except Exception as e:
            self.logger.error(f"Error getting kernel version: {e}")
            return "Unknown"

    def _get_boot_volume_info(self) -> Dict[str, str]:
        """Get boot and system volume information.

        Returns:
            Boot volume information
        """
        boot_info = {"boot_volume": "Unknown", "system_volume": "Unknown"}

        try:
            # Get boot volume
            result = subprocess.run(
                ["bless", "--info", "--getboot"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                boot_info["boot_volume"] = result.stdout.strip()

            # Get system volume (usually /)
            if self.tools["df"]:
                result = subprocess.run(
                    [self.tools["df"], "/"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) >= 2:
                        boot_info["system_volume"] = lines[1].split()[0]

            return boot_info

        except Exception as e:
            self.logger.error(f"Error getting boot volume info: {e}")
            return boot_info

    def _get_time_machine_status(self) -> str:
        """Get Time Machine backup status.

        Returns:
            Time Machine status string
        """
        try:
            if self.tools["tmutil"]:
                result = subprocess.run(
                    [self.tools["tmutil"], "status"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    if "Running = 1" in result.stdout:
                        return "running"
                    elif "Running = 0" in result.stdout:
                        return "idle"
                    else:
                        return "unknown"
                else:
                    return "disabled"

            return "unknown"

        except Exception as e:
            self.logger.error(f"Error getting Time Machine status: {e}")
            return "unknown"

    def _get_sip_status(self) -> str:
        """Get System Integrity Protection status.

        Returns:
            SIP status string
        """
        try:
            result = subprocess.run(
                ["csrutil", "status"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                if "enabled" in output:
                    return "enabled"
                elif "disabled" in output:
                    return "disabled"
                else:
                    return "unknown"

            return "unknown"

        except Exception as e:
            self.logger.error(f"Error getting SIP status: {e}")
            return "unknown"

    def run_fsck(
        self,
        device_id: str,
        filesystem: str,
        fix_errors: bool = False,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Run fsck on a specified volume.

        Args:
            device_id: Device identifier to check
            filesystem: Filesystem type
            fix_errors: Whether to fix errors
            force: Force check even if clean

        Returns:
            fsck results dictionary
        """
        try:
            # Determine appropriate fsck tool
            fsck_tool = None
            if filesystem.lower() == "apfs" and self.tools["fsck_apfs"]:
                fsck_tool = self.tools["fsck_apfs"]
            elif (
                filesystem.lower() in ["hfs", "hfs+"]
                and self.tools["fsck_hfs"]
            ):
                fsck_tool = self.tools["fsck_hfs"]
            elif self.tools["fsck"]:
                fsck_tool = self.tools["fsck"]

            if not fsck_tool:
                return {
                    "success": False,
                    "error": f"No fsck tool available for {filesystem}",
                }

            # Build command
            cmd = [fsck_tool]

            if fix_errors:
                cmd.append("-y")  # Answer yes to all questions
            else:
                cmd.append("-n")  # No modifications

            if force:
                cmd.append("-f")  # Force check

            cmd.append(f"/dev/{device_id}")

            # Run fsck
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "timestamp": datetime.now().isoformat(),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "fsck timed out",
                "timeout": True,
            }
        except Exception as e:
            self.logger.error(f"Error running fsck: {e}")
            return {"success": False, "error": str(e)}

    def get_repair_recommendations(
        self, volume_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get macOS-specific repair recommendations.

        Args:
            volume_info: Volume information from analysis

        Returns:
            List of repair recommendations
        """
        recommendations = []

        try:
            device_id = volume_info.get("device_id", "")
            filesystem = volume_info.get("filesystem", "").lower()
            health_status = volume_info.get("health_status", "unknown")
            is_system = volume_info.get("is_system", False)

            # Basic health recommendations
            if health_status == "errors_found":
                if filesystem == "apfs":
                    recommendations.append(
                        {
                            "priority": "high",
                            "action": "run_fsck_apfs",
                            "description": f"Run fsck_apfs on {device_id}",
                            "command": f"fsck_apfs -y /dev/{device_id}",
                            "requires_admin": True,
                            "requires_unmount": not is_system,
                        }
                    )
                elif filesystem in ["hfs", "hfs+"]:
                    recommendations.append(
                        {
                            "priority": "high",
                            "action": "run_fsck_hfs",
                            "description": f"Run fsck_hfs on {device_id}",
                            "command": f"fsck_hfs -y /dev/{device_id}",
                            "requires_admin": True,
                            "requires_unmount": not is_system,
                        }
                    )

            # Disk Utility recommendations
            recommendations.append(
                {
                    "priority": "medium",
                    "action": "run_disk_utility",
                    "description": "Run First Aid in Disk Utility",
                    "command": f"diskutil verifyVolume {device_id}",
                    "requires_admin": False,
                    "requires_unmount": False,
                }
            )

            # System volume specific recommendations
            if is_system:
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "boot_recovery",
                        "description": "Boot from Recovery mode for system volume repair",
                        "command": "Restart and hold Cmd+R",
                        "requires_admin": True,
                        "requires_unmount": False,
                    }
                )

            # APFS-specific recommendations
            if filesystem == "apfs":
                fs_info = volume_info.get("filesystem_info", {})
                snapshots = fs_info.get("snapshots", [])

                if len(snapshots) > 10:
                    recommendations.append(
                        {
                            "priority": "low",
                            "action": "cleanup_snapshots",
                            "description": f"Consider cleaning up {len(snapshots)} APFS snapshots",
                            "command": f"tmutil deletelocalsnapshots /",
                            "requires_admin": True,
                            "requires_unmount": False,
                        }
                    )

            # Time Machine recommendations
            tm_status = volume_info.get("time_machine_status", "unknown")
            if tm_status == "disabled" and is_system:
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": "enable_time_machine",
                        "description": "Enable Time Machine for system backup",
                        "command": "System Preferences > Time Machine",
                        "requires_admin": True,
                        "requires_unmount": False,
                    }
                )

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating repair recommendations: {e}")
            return []

    def is_admin_required(self, operation: str) -> bool:
        """Check if operation requires administrator privileges.

        Args:
            operation: Operation to check

        Returns:
            True if admin privileges required
        """
        admin_operations = {
            "fsck_repair",
            "disk_utility_repair",
            "system_repair",
            "snapshot_management",
            "time_machine_config",
        }

        return operation in admin_operations

    def get_supported_operations(self) -> List[str]:
        """Get list of supported filesystem operations.

        Returns:
            List of supported operation names
        """
        operations = ["volume_scan", "health_check", "disk_utility_verify"]

        if self.tools["fsck_apfs"]:
            operations.extend(["apfs_check", "apfs_repair"])

        if self.tools["fsck_hfs"]:
            operations.extend(["hfs_check", "hfs_repair"])

        if self.tools["diskutil"]:
            operations.extend(["diskutil_verify", "diskutil_repair"])

        if self.tools["tmutil"]:
            operations.append("time_machine_management")

        return operations
