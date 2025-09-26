"""Linux-specific filesystem implementation with ext2/3/4 and fsck support."""

import os
import subprocess
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from ....core.platform_detector import get_platform_detector
from src.core.error_handler import error_handler


class LinuxFilesystemImpl:
    """Linux filesystem implementation.

    Provides Linux-specific filesystem operations including:
    - ext2/3/4 filesystem analysis
    - fsck integration and automation
    - Multiple filesystem support (btrfs, xfs, etc.)
    - LVM and device mapper support
    - System integrity checking
    - Package manager integration
    """

    def __init__(self):
        """Initialize Linux filesystem implementation."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.LinuxFilesystem"
        )
        self.platform_detector = get_platform_detector()

        # Linux-specific tools
        self.tools = {
            "fsck": "/sbin/fsck",
            "e2fsck": "/sbin/e2fsck",
            "fsck.ext2": "/sbin/fsck.ext2",
            "fsck.ext3": "/sbin/fsck.ext3",
            "fsck.ext4": "/sbin/fsck.ext4",
            "fsck.xfs": "/sbin/fsck.xfs",
            "fsck.btrfs": "/sbin/fsck.btrfs",
            "tune2fs": "/sbin/tune2fs",
            "dumpe2fs": "/sbin/dumpe2fs",
            "lsblk": "/bin/lsblk",
            "blkid": "/sbin/blkid",
            "mount": "/bin/mount",
            "df": "/bin/df",
            "findmnt": "/bin/findmnt",
            "lvm": "/sbin/lvm",
            "dmsetup": "/sbin/dmsetup",
        }

        # Check tool availability
        self._check_tool_availability()

        # Supported filesystems
        self.supported_filesystems = {
            "ext2": {
                "name": "Second Extended Filesystem",
                "features": ["sparse_super", "large_file"],
                "fsck_tool": "fsck.ext2",
                "info_tool": "dumpe2fs",
            },
            "ext3": {
                "name": "Third Extended Filesystem",
                "features": ["has_journal", "sparse_super", "large_file"],
                "fsck_tool": "fsck.ext3",
                "info_tool": "dumpe2fs",
            },
            "ext4": {
                "name": "Fourth Extended Filesystem",
                "features": ["extents", "flex_bg", "huge_file", "dir_nlink"],
                "fsck_tool": "fsck.ext4",
                "info_tool": "dumpe2fs",
            },
            "xfs": {
                "name": "XFS Filesystem",
                "features": ["journaling", "online_resize", "quotas"],
                "fsck_tool": "fsck.xfs",
                "info_tool": "xfs_info",
            },
            "btrfs": {
                "name": "B-tree Filesystem",
                "features": ["snapshots", "compression", "checksums", "raid"],
                "fsck_tool": "fsck.btrfs",
                "info_tool": "btrfs",
            },
        }

    def _check_tool_availability(self) -> None:
        """Check availability of Linux filesystem tools."""
        for tool_name, tool_path in self.tools.items():
            if not os.path.exists(tool_path):
                # Try to find in PATH
                try:
                    result = subprocess.run(
                        ["which", tool_name],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        self.tools[tool_name] = result.stdout.strip()
                    else:
                        self.logger.warning(f"Tool not found: {tool_name}")
                        self.tools[tool_name] = None
                except Exception:
                    self.logger.warning(f"Tool not found: {tool_name}")
                    self.tools[tool_name] = None

    def get_filesystem_info(self) -> Dict[str, Any]:
        """Get comprehensive Linux filesystem information.

        Returns:
            Dict containing filesystem information
        """
        try:
            info = {
                "platform": "linux",
                "timestamp": datetime.now().isoformat(),
                "filesystems": [],
                "block_devices": [],
                "mount_points": [],
                "lvm_info": {},
                "system_info": {},
                "supported_filesystems": self.supported_filesystems.copy(),
                "tools_available": {
                    k: v is not None for k, v in self.tools.items()
                },
            }

            # Get filesystem information
            info["filesystems"] = self._get_filesystem_info()

            # Get block device information
            info["block_devices"] = self._get_block_devices()

            # Get mount point information
            info["mount_points"] = self._get_mount_points()

            # Get LVM information
            info["lvm_info"] = self._get_lvm_info()

            # Get system filesystem information
            info["system_info"] = self._get_system_filesystem_info()

            return info

        except Exception as e:
            self.logger.error(f"Error getting filesystem info: {e}")
            error_handler.handle_error(
                e, "LinuxFilesystemImpl.get_filesystem_info"
            )
            return {"error": str(e), "platform": "linux"}

    def _get_filesystem_info(self) -> List[Dict[str, Any]]:
        """Get information about all filesystems.

        Returns:
            List of filesystem information dictionaries
        """
        filesystems = []

        try:
            if not self.tools["findmnt"]:
                return []

            # Get mounted filesystems
            result = subprocess.run(
                [self.tools["findmnt"], "-J"],  # JSON output
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json

                try:
                    mount_data = json.loads(result.stdout)

                    for filesystem in mount_data.get("filesystems", []):
                        fs_info = self._process_filesystem_entry(filesystem)
                        if fs_info:
                            filesystems.append(fs_info)

                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing findmnt JSON: {e}")

            return filesystems

        except Exception as e:
            self.logger.error(f"Error getting filesystem info: {e}")
            return []

    def _process_filesystem_entry(
        self, fs_entry: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process a filesystem entry from findmnt.

        Args:
            fs_entry: Filesystem entry from findmnt

        Returns:
            Processed filesystem information or None
        """
        try:
            source = fs_entry.get("source", "")
            target = fs_entry.get("target", "")
            fstype = fs_entry.get("fstype", "")
            options = fs_entry.get("options", "")

            # Skip virtual filesystems for basic analysis
            virtual_fs = ["proc", "sysfs", "devtmpfs", "tmpfs", "devpts"]
            if fstype in virtual_fs:
                return None

            fs_info = {
                "source": source,
                "target": target,
                "fstype": fstype,
                "options": options.split(",") if options else [],
                "size": 0,
                "used": 0,
                "available": 0,
                "use_percent": 0,
                "health_status": "unknown",
                "filesystem_info": {},
            }

            # Get space usage
            space_info = self._get_filesystem_space_usage(target)
            fs_info.update(space_info)

            # Get filesystem-specific information
            if fstype in self.supported_filesystems:
                detailed_info = self._get_filesystem_detailed_info(
                    source, fstype
                )
                fs_info["filesystem_info"] = detailed_info

            # Check filesystem health
            fs_info["health_status"] = self._check_filesystem_health(
                source, fstype
            )

            return fs_info

        except Exception as e:
            self.logger.error(f"Error processing filesystem entry: {e}")
            return None

    def _get_filesystem_space_usage(self, mount_point: str) -> Dict[str, Any]:
        """Get space usage for a filesystem.

        Args:
            mount_point: Mount point to check

        Returns:
            Space usage information
        """
        space_info = {"size": 0, "used": 0, "available": 0, "use_percent": 0}

        try:
            if self.tools["df"]:
                result = subprocess.run(
                    [self.tools["df"], "-B1", mount_point],  # 1-byte blocks
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) >= 2:
                        # Parse df output
                        fields = lines[1].split()
                        if len(fields) >= 6:
                            size = int(fields[1])
                            used = int(fields[2])
                            available = int(fields[3])
                            use_percent = int(fields[4].rstrip("%"))

                            space_info.update(
                                {
                                    "size": size,
                                    "used": used,
                                    "available": available,
                                    "use_percent": use_percent,
                                }
                            )

            return space_info

        except Exception as e:
            self.logger.error(
                f"Error getting space usage for {mount_point}: {e}"
            )
            return space_info

    def _get_filesystem_detailed_info(
        self, device: str, fstype: str
    ) -> Dict[str, Any]:
        """Get detailed filesystem information.

        Args:
            device: Device path
            fstype: Filesystem type

        Returns:
            Detailed filesystem information
        """
        detailed_info = {}

        try:
            if fstype in ["ext2", "ext3", "ext4"]:
                detailed_info = self._get_ext_filesystem_info(device)
            elif fstype == "xfs":
                detailed_info = self._get_xfs_filesystem_info(device)
            elif fstype == "btrfs":
                detailed_info = self._get_btrfs_filesystem_info(device)

            return detailed_info

        except Exception as e:
            self.logger.error(f"Error getting detailed info for {device}: {e}")
            return {}

    def _get_ext_filesystem_info(self, device: str) -> Dict[str, Any]:
        """Get ext2/3/4 filesystem information.

        Args:
            device: Device path

        Returns:
            ext filesystem information
        """
        ext_info = {
            "block_size": 0,
            "block_count": 0,
            "free_blocks": 0,
            "inode_count": 0,
            "free_inodes": 0,
            "features": [],
            "last_check": "",
            "check_interval": 0,
            "mount_count": 0,
            "max_mount_count": 0,
        }

        try:
            if self.tools["dumpe2fs"]:
                result = subprocess.run(
                    [self.tools["dumpe2fs"], "-h", device],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    output = result.stdout

                    # Parse dumpe2fs output
                    patterns = {
                        "block_size": r"Block size:\s*(\d+)",
                        "block_count": r"Block count:\s*(\d+)",
                        "free_blocks": r"Free blocks:\s*(\d+)",
                        "inode_count": r"Inode count:\s*(\d+)",
                        "free_inodes": r"Free inodes:\s*(\d+)",
                        "mount_count": r"Mount count:\s*(\d+)",
                        "max_mount_count": r"Maximum mount count:\s*(\d+)",
                        "check_interval": r"Check interval:\s*(\d+)",
                        "last_check": r"Last checked:\s*(.+)",
                    }

                    for key, pattern in patterns.items():
                        match = re.search(pattern, output)
                        if match:
                            value = match.group(1).strip()
                            if key in ["last_check"]:
                                ext_info[key] = value
                            else:
                                ext_info[key] = int(value)

                    # Parse filesystem features
                    features_match = re.search(
                        r"Filesystem features:\s*(.+)", output
                    )
                    if features_match:
                        features = features_match.group(1).strip().split()
                        ext_info["features"] = features

            return ext_info

        except Exception as e:
            self.logger.error(
                f"Error getting ext filesystem info for {device}: {e}"
            )
            return ext_info

    def _get_xfs_filesystem_info(self, device: str) -> Dict[str, Any]:
        """Get XFS filesystem information.

        Args:
            device: Device path

        Returns:
            XFS filesystem information
        """
        xfs_info = {
            "block_size": 0,
            "data_blocks": 0,
            "free_blocks": 0,
            "inode_size": 0,
            "agcount": 0,
            "version": "",
        }

        try:
            # XFS info requires the filesystem to be mounted
            # We'll use xfs_db for unmounted filesystems
            result = subprocess.run(
                ["xfs_info", device],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                output = result.stdout

                # Parse xfs_info output
                patterns = {
                    "block_size": r"bsize=(\d+)",
                    "data_blocks": r"dblocks=(\d+)",
                    "inode_size": r"isize=(\d+)",
                    "agcount": r"agcount=(\d+)",
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, output)
                    if match:
                        xfs_info[key] = int(match.group(1))

            return xfs_info

        except Exception as e:
            self.logger.error(
                f"Error getting XFS filesystem info for {device}: {e}"
            )
            return xfs_info

    def _get_btrfs_filesystem_info(self, device: str) -> Dict[str, Any]:
        """Get Btrfs filesystem information.

        Args:
            device: Device path

        Returns:
            Btrfs filesystem information
        """
        btrfs_info = {
            "uuid": "",
            "total_devices": 0,
            "node_size": 0,
            "sector_size": 0,
            "data_profile": "",
            "metadata_profile": "",
            "features": [],
        }

        try:
            result = subprocess.run(
                ["btrfs", "filesystem", "show", device],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                output = result.stdout

                # Parse btrfs output
                uuid_match = re.search(r"uuid: ([a-f0-9-]+)", output)
                if uuid_match:
                    btrfs_info["uuid"] = uuid_match.group(1)

                devices_match = re.search(r"Total devices (\d+)", output)
                if devices_match:
                    btrfs_info["total_devices"] = int(devices_match.group(1))

            return btrfs_info

        except Exception as e:
            self.logger.error(
                f"Error getting Btrfs filesystem info for {device}: {e}"
            )
            return btrfs_info

    def _check_filesystem_health(self, device: str, fstype: str) -> str:
        """Check filesystem health status.

        Args:
            device: Device path
            fstype: Filesystem type

        Returns:
            Health status string
        """
        try:
            # Use appropriate fsck tool
            fsck_tool = self.supported_filesystems.get(fstype, {}).get(
                "fsck_tool"
            )
            if not fsck_tool or not self.tools.get(fsck_tool):
                return "unknown"

            # Run fsck in read-only mode
            result = subprocess.run(
                [self.tools[fsck_tool], "-n", device],  # -n = no changes
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            if result.returncode == 0:
                return "healthy"
            elif result.returncode == 1:
                return "errors_corrected"
            elif result.returncode == 2:
                return "errors_found"
            elif result.returncode == 4:
                return "errors_uncorrected"
            else:
                return "check_failed"

        except subprocess.TimeoutExpired:
            return "check_timeout"
        except Exception as e:
            self.logger.error(
                f"Error checking filesystem health for {device}: {e}"
            )
            return "unknown"

    def _get_block_devices(self) -> List[Dict[str, Any]]:
        """Get block device information.

        Returns:
            List of block device information
        """
        devices = []

        try:
            if not self.tools["lsblk"]:
                return []

            result = subprocess.run(
                [
                    self.tools["lsblk"],
                    "-J",
                    "-o",
                    "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,UUID",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json

                try:
                    lsblk_data = json.loads(result.stdout)

                    for device in lsblk_data.get("blockdevices", []):
                        device_info = self._process_block_device(device)
                        if device_info:
                            devices.append(device_info)

                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing lsblk JSON: {e}")

            return devices

        except Exception as e:
            self.logger.error(f"Error getting block devices: {e}")
            return []

    def _process_block_device(
        self, device: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process a block device entry.

        Args:
            device: Device entry from lsblk

        Returns:
            Processed device information or None
        """
        try:
            device_info = {
                "name": device.get("name", ""),
                "size": device.get("size", ""),
                "type": device.get("type", ""),
                "mountpoint": device.get("mountpoint", ""),
                "fstype": device.get("fstype", ""),
                "uuid": device.get("uuid", ""),
                "children": [],
            }

            # Process child devices (partitions)
            for child in device.get("children", []):
                child_info = self._process_block_device(child)
                if child_info:
                    device_info["children"].append(child_info)

            return device_info

        except Exception as e:
            self.logger.error(f"Error processing block device: {e}")
            return None

    def _get_mount_points(self) -> List[Dict[str, Any]]:
        """Get mount point information.

        Returns:
            List of mount point information
        """
        mount_points = []

        try:
            if self.tools["mount"]:
                result = subprocess.run(
                    [self.tools["mount"]],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if " on " in line and " type " in line:
                            parts = line.split(" on ")
                            if len(parts) >= 2:
                                device = parts[0]
                                rest = parts[1].split(" type ")
                                if len(rest) >= 2:
                                    mount_point = rest[0]
                                    fs_and_options = rest[1].split(" (")
                                    fstype = fs_and_options[0]
                                    options = (
                                        fs_and_options[1].rstrip(")")
                                        if len(fs_and_options) > 1
                                        else ""
                                    )

                                    mount_points.append(
                                        {
                                            "device": device,
                                            "mount_point": mount_point,
                                            "fstype": fstype,
                                            "options": (
                                                options.split(",")
                                                if options
                                                else []
                                            ),
                                        }
                                    )

            return mount_points

        except Exception as e:
            self.logger.error(f"Error getting mount points: {e}")
            return []

    def _get_lvm_info(self) -> Dict[str, Any]:
        """Get LVM information.

        Returns:
            LVM information dictionary
        """
        lvm_info = {
            "volume_groups": [],
            "logical_volumes": [],
            "physical_volumes": [],
        }

        try:
            if not self.tools["lvm"]:
                return lvm_info

            # Get volume groups
            result = subprocess.run(
                [self.tools["lvm"], "vgs", "--reportformat", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json

                try:
                    vgs_data = json.loads(result.stdout)
                    lvm_info["volume_groups"] = vgs_data.get("report", [{}])[
                        0
                    ].get("vg", [])
                except json.JSONDecodeError:
                    pass

            # Get logical volumes
            result = subprocess.run(
                [self.tools["lvm"], "lvs", "--reportformat", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json

                try:
                    lvs_data = json.loads(result.stdout)
                    lvm_info["logical_volumes"] = lvs_data.get("report", [{}])[
                        0
                    ].get("lv", [])
                except json.JSONDecodeError:
                    pass

            # Get physical volumes
            result = subprocess.run(
                [self.tools["lvm"], "pvs", "--reportformat", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json

                try:
                    pvs_data = json.loads(result.stdout)
                    lvm_info["physical_volumes"] = pvs_data.get(
                        "report", [{}]
                    )[0].get("pv", [])
                except json.JSONDecodeError:
                    pass

            return lvm_info

        except Exception as e:
            self.logger.error(f"Error getting LVM info: {e}")
            return lvm_info

    def _get_system_filesystem_info(self) -> Dict[str, Any]:
        """Get system-wide filesystem information.

        Returns:
            System filesystem information
        """
        system_info = {
            "kernel_version": "Unknown",
            "distribution": "Unknown",
            "root_filesystem": "Unknown",
            "boot_filesystem": "Unknown",
            "supported_filesystems": [],
        }

        try:
            # Get kernel version
            result = subprocess.run(
                ["uname", "-r"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                system_info["kernel_version"] = result.stdout.strip()

            # Get distribution info
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            system_info["distribution"] = line.split("=")[
                                1
                            ].strip('"')
                            break

            # Get root filesystem
            result = subprocess.run(
                [self.tools["df"], "/"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    system_info["root_filesystem"] = lines[1].split()[0]

            # Get supported filesystems
            if os.path.exists("/proc/filesystems"):
                with open("/proc/filesystems", "r") as f:
                    for line in f:
                        if not line.startswith("nodev"):
                            fs = line.strip()
                            if fs:
                                system_info["supported_filesystems"].append(fs)

            return system_info

        except Exception as e:
            self.logger.error(f"Error getting system filesystem info: {e}")
            return system_info

    def run_fsck(
        self,
        device: str,
        fstype: str,
        fix_errors: bool = False,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Run fsck on a specified device.

        Args:
            device: Device path to check
            fstype: Filesystem type
            fix_errors: Whether to fix errors
            force: Force check even if clean

        Returns:
            fsck results dictionary
        """
        try:
            # Get appropriate fsck tool
            fsck_tool = self.supported_filesystems.get(fstype, {}).get(
                "fsck_tool"
            )
            if not fsck_tool or not self.tools.get(fsck_tool):
                return {
                    "success": False,
                    "error": f"No fsck tool available for {fstype}",
                }

            # Build command
            cmd = [self.tools[fsck_tool]]

            if fix_errors:
                cmd.append("-y")  # Answer yes to all questions
            else:
                cmd.append("-n")  # No modifications

            if force:
                cmd.append("-f")  # Force check

            cmd.append(device)

            # Run fsck
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
            )

            return {
                "success": result.returncode
                in [0, 1],  # 0=clean, 1=errors corrected
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
        self, filesystem_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get Linux-specific repair recommendations.

        Args:
            filesystem_info: Filesystem information from analysis

        Returns:
            List of repair recommendations
        """
        recommendations = []

        try:
            source = filesystem_info.get("source", "")
            fstype = filesystem_info.get("fstype", "")
            health_status = filesystem_info.get("health_status", "unknown")
            target = filesystem_info.get("target", "")

            # Basic health recommendations
            if health_status == "errors_found":
                fsck_tool = self.supported_filesystems.get(fstype, {}).get(
                    "fsck_tool"
                )
                if fsck_tool:
                    recommendations.append(
                        {
                            "priority": "high",
                            "action": "run_fsck_repair",
                            "description": f"Run {fsck_tool} to fix errors on {source}",
                            "command": f"{fsck_tool} -y {source}",
                            "requires_admin": True,
                            "requires_unmount": target != "/",
                        }
                    )

            elif health_status == "errors_uncorrected":
                recommendations.append(
                    {
                        "priority": "critical",
                        "action": "emergency_repair",
                        "description": f"Critical errors on {source} - manual intervention needed",
                        "command": f"fsck -f {source}",
                        "requires_admin": True,
                        "requires_unmount": True,
                    }
                )

            # Filesystem-specific recommendations
            if fstype in ["ext2", "ext3", "ext4"]:
                fs_info = filesystem_info.get("filesystem_info", {})
                mount_count = fs_info.get("mount_count", 0)
                max_mount_count = fs_info.get("max_mount_count", 0)

                if (
                    max_mount_count > 0
                    and mount_count >= max_mount_count * 0.9
                ):
                    new_max = max_mount_count + 10
                    recommendations.append(
                        {
                            "priority": "medium",
                            "action": "schedule_fsck",
                            "description": f"Approaching max mount count ({mount_count}/{max_mount_count})",
                            "command": f"tune2fs -c {new_max} {source}",
                            "requires_admin": True,
                            "requires_unmount": False,
                        }
                    )

            # Space usage recommendations
            use_percent = filesystem_info.get("use_percent", 0)
            if use_percent > 90:
                recommendations.append(
                    {
                        "priority": "high",
                        "action": "free_space",
                        "description": f"Filesystem {target} is {use_percent}% full",
                        "command": f"df -h {target}",
                        "requires_admin": False,
                        "requires_unmount": False,
                    }
                )

            # LVM recommendations
            if "/dev/mapper/" in source:
                recommendations.append(
                    {
                        "priority": "low",
                        "action": "check_lvm",
                        "description": "Check LVM volume group health",
                        "command": "vgck",
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
            "filesystem_repair",
            "lvm_operations",
            "tune2fs_operations",
            "mount_operations",
        }

        return operation in admin_operations

    def get_supported_operations(self) -> List[str]:
        """Get list of supported filesystem operations.

        Returns:
            List of supported operation names
        """
        operations = ["filesystem_scan", "health_check", "space_analysis"]

        if self.tools["fsck"]:
            operations.append("fsck_check")

        if self.tools["e2fsck"]:
            operations.extend(["ext_check", "ext_repair"])

        if self.tools["tune2fs"]:
            operations.append("ext_tuning")

        if self.tools["lvm"]:
            operations.extend(["lvm_check", "lvm_management"])

        if self.tools["btrfs"]:
            operations.extend(["btrfs_check", "btrfs_scrub"])

        return operations
