"""Linux-specific disk health monitoring with proc filesystem and sysfs."""

import subprocess
import json
import re
import os
import glob
from typing import Dict, Any, List, Optional
from datetime import datetime

from ....core.monitor_base import MonitorBase
from core.error_handler import error_handler


class LinuxDiskMonitor(MonitorBase):
    """Linux-specific disk health monitoring with enhanced capabilities."""

    def __init__(self, update_interval: float = 30.0):
        """Initialize Linux disk monitor.

        Args:
            update_interval: Update interval in seconds
        """
        super().__init__("LinuxDiskHealth", update_interval)

        # Linux-specific paths
        self.proc_path = "/proc"
        self.sys_path = "/sys"
        self.dev_path = "/dev"

        # Disk tracking
        self._physical_disks: Dict[str, Dict[str, Any]] = {}
        self._logical_disks: Dict[str, Dict[str, Any]] = {}
        self._disk_performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # Linux system tools
        self._system_tools = {
            "lsblk": "/bin/lsblk",
            "smartctl": "/usr/sbin/smartctl",
            "hdparm": "/sbin/hdparm",
            "fdisk": "/sbin/fdisk",
            "df": "/bin/df",
            "lshw": "/usr/bin/lshw",
            "udevadm": "/bin/udevadm",
        }

        # Verify tool availability
        self._available_tools = {}
        for tool_name, tool_path in self._system_tools.items():
            if self._check_tool_availability(tool_path):
                self._available_tools[tool_name] = tool_path

        # Check filesystem availability
        self.proc_available = os.path.exists(self.proc_path)
        self.sys_available = os.path.exists(self.sys_path)

        self.logger.info("Linux disk monitor initialized")

    def _check_tool_availability(self, tool_path: str) -> bool:
        """Check if a system tool is available.

        Args:
            tool_path: Path to the tool

        Returns:
            bool: True if tool is available
        """
        try:
            if os.path.exists(tool_path):
                result = subprocess.run(
                    [tool_path, "--version"], capture_output=True, timeout=5
                )
                return result.returncode == 0
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            return False

    def _initialize_platform_specific(self) -> None:
        """Initialize Linux-specific disk monitoring."""
        try:
            # Check filesystem availability
            if self.proc_available:
                self.logger.info("proc filesystem available")
            else:
                self.logger.warning("proc filesystem not available")

            if self.sys_available:
                self.logger.info("sysfs filesystem available")
            else:
                self.logger.warning("sysfs filesystem not available")

            # Check available system tools
            available_tools = list(self._available_tools.keys())
            self.logger.info(
                f"Available Linux tools: {', '.join(available_tools)}"
            )

            if not available_tools and not (
                self.proc_available or self.sys_available
            ):
                self.logger.warning(
                    "No Linux system tools or filesystems available - "
                    "limited functionality"
                )

            # Discover disks using Linux-specific methods
            self._discover_linux_disks()

            disk_count = len(self._physical_disks) + len(self._logical_disks)
            self.logger.info(
                f"Initialized Linux disk monitoring for {disk_count} disks"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize Linux disk monitoring: {e}"
            )
            error_handler.handle_error(e, "LinuxDiskMonitor.initialize")
            raise

    def _discover_linux_disks(self) -> None:
        """Discover Linux disks using proc, sysfs, and system tools."""
        try:
            self._physical_disks.clear()
            self._logical_disks.clear()

            # Discover disks via lsblk if available
            if "lsblk" in self._available_tools:
                self._discover_disks_lsblk()

            # Discover disks via proc filesystem
            if self.proc_available:
                self._discover_disks_proc()

            # Enhance with sysfs data if available
            if self.sys_available:
                self._enhance_with_sysfs_data()

            # Get additional disk information
            self._enrich_disk_information()

        except Exception as e:
            self.logger.error(f"Error discovering Linux disks: {e}")
            error_handler.handle_error(e, "LinuxDiskMonitor.discover_disks")

    def _discover_disks_lsblk(self) -> None:
        """Discover disks using lsblk."""
        try:
            result = subprocess.run(
                [
                    self._available_tools["lsblk"],
                    "-J",
                    "-o",
                    "NAME,TYPE,SIZE,MOUNTPOINT,FSTYPE,UUID,LABEL,MODEL,"
                    "SERIAL,STATE,OWNER,GROUP,MODE,ALIGNMENT,MIN-IO,OPT-IO,"
                    "PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,RA,WSAME",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.warning("lsblk failed to get disk information")
                return

            # Parse JSON output
            try:
                lsblk_data = json.loads(result.stdout)
                block_devices = lsblk_data.get("blockdevices", [])

                for device in block_devices:
                    try:
                        self._parse_lsblk_device(device)
                    except Exception as e:
                        self.logger.warning(f"Error parsing lsblk device: {e}")
                        continue

            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing lsblk JSON output: {e}")

        except Exception as e:
            self.logger.error(f"Error discovering disks via lsblk: {e}")

    def _parse_lsblk_device(self, device: Dict[str, Any]) -> None:
        """Parse a device from lsblk output.

        Args:
            device: Device information from lsblk
        """
        try:
            device_name = device.get("name", "")
            device_type = device.get("type", "")

            if not device_name:
                return

            # Create device info
            device_info = {
                "device_id": device_name,
                "device_path": f"/dev/{device_name}",
                "type": device_type,
                "size_bytes": self._parse_size_lsblk(device.get("size", "0")),
                "mount_point": device.get("mountpoint", ""),
                "filesystem": device.get("fstype", ""),
                "uuid": device.get("uuid", ""),
                "label": device.get("label", ""),
                "model": device.get("model", ""),
                "serial": device.get("serial", ""),
                "state": device.get("state", ""),
                "owner": device.get("owner", ""),
                "group": device.get("group", ""),
                "mode": device.get("mode", ""),
                "alignment": device.get("alignment", ""),
                "min_io": device.get("min-io", ""),
                "opt_io": device.get("opt-io", ""),
                "physical_sector_size": device.get("phy-sec", ""),
                "logical_sector_size": device.get("log-sec", ""),
                "rotational": device.get("rota", "") == "1",
                "scheduler": device.get("sched", ""),
                "queue_size": device.get("rq-size", ""),
                "read_ahead": device.get("ra", ""),
                "write_same_max": device.get("wsame", ""),
            }

            # Categorize device
            if device_type == "disk":
                self._physical_disks[device_name] = device_info
                self.logger.debug(f"Added physical disk: {device_name}")
            elif device_type in ["part", "lvm", "crypt"]:
                self._logical_disks[device_name] = device_info
                self.logger.debug(f"Added logical disk: {device_name}")

            # Process children (partitions)
            children = device.get("children", [])
            for child in children:
                self._parse_lsblk_device(child)

        except Exception as e:
            self.logger.error(f"Error parsing lsblk device: {e}")

    def _parse_size_lsblk(self, size_str: str) -> int:
        """Parse size string from lsblk to bytes.

        Args:
            size_str: Size string (e.g., '1T', '500G')

        Returns:
            Size in bytes
        """
        try:
            if not size_str or size_str == "null":
                return 0

            # Extract number and unit
            match = re.match(r"([\d.,]+)([KMGTPE]?)", size_str.upper())
            if not match:
                return 0

            number_str, unit = match.groups()
            number = float(number_str.replace(",", ""))

            # Convert to bytes
            unit_multipliers = {
                "": 1,
                "K": 1024,
                "M": 1024**2,
                "G": 1024**3,
                "T": 1024**4,
                "P": 1024**5,
                "E": 1024**6,
            }

            multiplier = unit_multipliers.get(unit, 1)
            return int(number * multiplier)

        except Exception as e:
            self.logger.error(f"Error parsing size string '{size_str}': {e}")
            return 0

    def _discover_disks_proc(self) -> None:
        """Discover disks using proc filesystem."""
        try:
            # Read /proc/partitions
            partitions_file = os.path.join(self.proc_path, "partitions")
            if os.path.exists(partitions_file):
                self._parse_proc_partitions(partitions_file)

            # Read /proc/diskstats
            diskstats_file = os.path.join(self.proc_path, "diskstats")
            if os.path.exists(diskstats_file):
                self._parse_proc_diskstats(diskstats_file)

            # Read /proc/mounts
            mounts_file = os.path.join(self.proc_path, "mounts")
            if os.path.exists(mounts_file):
                self._parse_proc_mounts(mounts_file)

        except Exception as e:
            self.logger.error(f"Error discovering disks via proc: {e}")

    def _parse_proc_partitions(self, partitions_file: str) -> None:
        """Parse /proc/partitions file.

        Args:
            partitions_file: Path to partitions file
        """
        try:
            with open(partitions_file, "r") as f:
                lines = f.readlines()

            for line in lines[2:]:  # Skip header lines
                fields = line.strip().split()
                if len(fields) >= 4:
                    major, minor, blocks, name = fields[:4]

                    try:
                        device_info = {
                            "device_id": name,
                            "device_path": f"/dev/{name}",
                            "major": int(major),
                            "minor": int(minor),
                            "size_bytes": int(blocks) * 1024,  # blocks are 1KB
                            "type": "unknown",
                        }

                        # Determine if it's a physical disk or partition
                        if self._is_physical_disk(name):
                            if name not in self._physical_disks:
                                self._physical_disks[name] = device_info
                        else:
                            if name not in self._logical_disks:
                                self._logical_disks[name] = device_info

                    except ValueError:
                        continue

        except Exception as e:
            self.logger.error(f"Error parsing proc partitions: {e}")

    def _parse_proc_diskstats(self, diskstats_file: str) -> None:
        """Parse /proc/diskstats file for I/O statistics.

        Args:
            diskstats_file: Path to diskstats file
        """
        try:
            with open(diskstats_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                fields = line.strip().split()
                if len(fields) >= 14:
                    device_name = fields[2]

                    # Parse I/O statistics
                    io_stats = {
                        "reads_completed": int(fields[3]),
                        "reads_merged": int(fields[4]),
                        "sectors_read": int(fields[5]),
                        "time_reading_ms": int(fields[6]),
                        "writes_completed": int(fields[7]),
                        "writes_merged": int(fields[8]),
                        "sectors_written": int(fields[9]),
                        "time_writing_ms": int(fields[10]),
                        "ios_in_progress": int(fields[11]),
                        "time_io_ms": int(fields[12]),
                        "weighted_time_io_ms": int(fields[13]),
                    }

                    # Add to existing device info
                    if device_name in self._physical_disks:
                        self._physical_disks[device_name][
                            "io_stats"
                        ] = io_stats
                    elif device_name in self._logical_disks:
                        self._logical_disks[device_name]["io_stats"] = io_stats

        except Exception as e:
            self.logger.error(f"Error parsing proc diskstats: {e}")

    def _parse_proc_mounts(self, mounts_file: str) -> None:
        """Parse /proc/mounts file for mount information.

        Args:
            mounts_file: Path to mounts file
        """
        try:
            with open(mounts_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                fields = line.strip().split()
                if len(fields) >= 6:
                    device, mount_point, filesystem = fields[:3]
                    mount_options = fields[3]

                    # Extract device name
                    if device.startswith("/dev/"):
                        device_name = device.replace("/dev/", "")

                        mount_info = {
                            "mount_point": mount_point,
                            "filesystem": filesystem,
                            "mount_options": mount_options.split(","),
                        }

                        # Add to existing device info
                        if device_name in self._logical_disks:
                            self._logical_disks[device_name].update(mount_info)
                        elif device_name in self._physical_disks:
                            self._physical_disks[device_name].update(
                                mount_info
                            )

        except Exception as e:
            self.logger.error(f"Error parsing proc mounts: {e}")

    def _is_physical_disk(self, device_name: str) -> bool:
        """Determine if a device is a physical disk.

        Args:
            device_name: Device name

        Returns:
            bool: True if it's a physical disk
        """
        # Common patterns for physical disks
        physical_patterns = [
            r"^sd[a-z]$",  # SCSI/SATA disks (sda, sdb, etc.)
            r"^hd[a-z]$",  # IDE disks (hda, hdb, etc.)
            r"^nvme\d+n\d+$",  # NVMe disks (nvme0n1, nvme1n1, etc.)
            r"^mmcblk\d+$",  # MMC/SD cards (mmcblk0, mmcblk1, etc.)
            r"^vd[a-z]$",  # Virtual disks (vda, vdb, etc.)
            r"^xvd[a-z]$",  # Xen virtual disks (xvda, xvdb, etc.)
        ]

        for pattern in physical_patterns:
            if re.match(pattern, device_name):
                return True

        return False

    def _enhance_with_sysfs_data(self) -> None:
        """Enhance disk information with sysfs data."""
        try:
            block_path = os.path.join(self.sys_path, "block")
            if not os.path.exists(block_path):
                return

            for device_name in os.listdir(block_path):
                try:
                    device_path = os.path.join(block_path, device_name)
                    if os.path.isdir(device_path):
                        sysfs_info = self._get_sysfs_device_info(
                            device_name, device_path
                        )

                        # Add to existing device info
                        if device_name in self._physical_disks:
                            self._physical_disks[device_name].update(
                                sysfs_info
                            )
                        elif device_name in self._logical_disks:
                            self._logical_disks[device_name].update(sysfs_info)
                        else:
                            # Create new entry if not found
                            if self._is_physical_disk(device_name):
                                self._physical_disks[device_name] = sysfs_info
                            else:
                                self._logical_disks[device_name] = sysfs_info

                except Exception as e:
                    self.logger.warning(
                        f"Error processing sysfs device {device_name}: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error enhancing with sysfs data: {e}")

    def _get_sysfs_device_info(
        self, device_name: str, device_path: str
    ) -> Dict[str, Any]:
        """Get device information from sysfs.

        Args:
            device_name: Device name
            device_path: Path to device in sysfs

        Returns:
            Dict containing sysfs device information
        """
        try:
            sysfs_info = {
                "device_id": device_name,
                "device_path": f"/dev/{device_name}",
            }

            # Read various sysfs attributes
            sysfs_attributes = {
                "size": "size_sectors",
                "removable": "removable",
                "ro": "read_only",
                "alignment_offset": "alignment_offset",
                "discard_alignment": "discard_alignment",
                "queue/rotational": "rotational",
                "queue/scheduler": "scheduler",
                "queue/nr_requests": "queue_depth",
                "queue/read_ahead_kb": "read_ahead_kb",
                "queue/max_sectors_kb": "max_sectors_kb",
                "queue/physical_block_size": "physical_block_size",
                "queue/logical_block_size": "logical_block_size",
                "queue/minimum_io_size": "minimum_io_size",
                "queue/optimal_io_size": "optimal_io_size",
            }

            for attr_path, attr_name in sysfs_attributes.items():
                try:
                    full_path = os.path.join(device_path, attr_path)
                    if os.path.exists(full_path):
                        with open(full_path, "r") as f:
                            value = f.read().strip()

                        # Convert to appropriate type
                        if attr_name in [
                            "size_sectors",
                            "alignment_offset",
                            "discard_alignment",
                            "queue_depth",
                            "read_ahead_kb",
                            "max_sectors_kb",
                            "physical_block_size",
                            "logical_block_size",
                            "minimum_io_size",
                            "optimal_io_size",
                        ]:
                            try:
                                sysfs_info[attr_name] = int(value)
                            except ValueError:
                                sysfs_info[attr_name] = 0
                        elif attr_name in [
                            "removable",
                            "read_only",
                            "rotational",
                        ]:
                            sysfs_info[attr_name] = value == "1"
                        else:
                            sysfs_info[attr_name] = value

                except Exception:
                    continue

            # Calculate size in bytes from sectors
            if "size_sectors" in sysfs_info:
                logical_block_size = sysfs_info.get("logical_block_size", 512)
                sysfs_info["size_bytes"] = (
                    sysfs_info["size_sectors"] * logical_block_size
                )

            # Get device model and vendor if available
            try:
                device_dir = os.path.join(device_path, "device")
                if os.path.exists(device_dir):
                    model_file = os.path.join(device_dir, "model")
                    vendor_file = os.path.join(device_dir, "vendor")

                    if os.path.exists(model_file):
                        with open(model_file, "r") as f:
                            sysfs_info["model"] = f.read().strip()

                    if os.path.exists(vendor_file):
                        with open(vendor_file, "r") as f:
                            sysfs_info["vendor"] = f.read().strip()
            except Exception:
                pass

            return sysfs_info

        except Exception as e:
            self.logger.error(
                f"Error getting sysfs info for {device_name}: {e}"
            )
            return {"device_id": device_name}

    def _enrich_disk_information(self) -> None:
        """Enrich disk information with additional Linux-specific data."""
        try:
            # Get SMART data for physical disks
            for device_id, disk_info in self._physical_disks.items():
                try:
                    smart_data = self._get_linux_smart_data(device_id)
                    if smart_data:
                        disk_info["smart"] = smart_data
                        disk_info["temperature"] = smart_data.get(
                            "temperature"
                        )
                        disk_info["power_on_hours"] = smart_data.get(
                            "power_on_hours"
                        )
                except Exception as e:
                    self.logger.warning(
                        f"Error getting SMART data for {device_id}: {e}"
                    )

            # Get filesystem usage for mounted logical disks
            for device_id, disk_info in self._logical_disks.items():
                try:
                    if disk_info.get("mount_point"):
                        self._update_filesystem_usage(device_id, disk_info)
                except Exception as e:
                    self.logger.warning(
                        f"Error updating filesystem usage for "
                        f"{device_id}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error enriching disk information: {e}")

    def _get_linux_smart_data(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get SMART data using Linux-specific methods.

        Args:
            device_id: Disk device identifier

        Returns:
            Dict containing SMART data or None if unavailable
        """
        try:
            # Try smartctl first if available
            if "smartctl" in self._available_tools:
                smart_data = self._get_smartctl_data_linux(device_id)
                if smart_data:
                    return smart_data

            # Try hdparm as fallback
            if "hdparm" in self._available_tools:
                return self._get_hdparm_data(device_id)

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting Linux SMART data for {device_id}: {e}"
            )
            return None

    def _get_smartctl_data_linux(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get SMART data using smartctl on Linux.

        Args:
            device_id: Disk device identifier

        Returns:
            Dict containing smartctl SMART data or None if unavailable
        """
        try:
            device_path = f"/dev/{device_id}"

            result = subprocess.run(
                [self._available_tools["smartctl"], "-a", "-j", device_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode in [0, 1, 2, 4] and result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"Invalid JSON from smartctl for {device_id}"
                    )
                    return None

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting smartctl data on Linux for {device_id}: {e}"
            )
            return None

    def _get_hdparm_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get basic disk data using hdparm.

        Args:
            device_id: Disk device identifier

        Returns:
            Dict containing basic disk data or None if unavailable
        """
        try:
            device_path = f"/dev/{device_id}"

            result = subprocess.run(
                [self._available_tools["hdparm"], "-I", device_path],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0 and result.stdout:
                return self._parse_hdparm_output(result.stdout)

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting hdparm data for {device_id}: {e}"
            )
            return None

    def _parse_hdparm_output(self, hdparm_output: str) -> Dict[str, Any]:
        """Parse hdparm output for disk information.

        Args:
            hdparm_output: Raw hdparm output

        Returns:
            Dict containing parsed disk information
        """
        try:
            hdparm_data = {}
            lines = hdparm_output.split("\n")

            for line in lines:
                line = line.strip()

                # Parse model information
                if "Model Number:" in line:
                    hdparm_data["model"] = line.split(":", 1)[1].strip()
                elif "Serial Number:" in line:
                    hdparm_data["serial_number"] = line.split(":", 1)[
                        1
                    ].strip()
                elif "Firmware Revision:" in line:
                    hdparm_data["firmware_revision"] = line.split(":", 1)[
                        1
                    ].strip()

                # Parse capacity
                elif "device size with M = 1000*1000:" in line:
                    # Extract size information
                    match = re.search(r"(\d+) bytes", line)
                    if match:
                        hdparm_data["size_bytes"] = int(match.group(1))

                # Parse features
                elif "SMART feature set" in line:
                    if "Enabled" in line:
                        hdparm_data["smart_enabled"] = True
                    elif "Disabled" in line:
                        hdparm_data["smart_enabled"] = False

            return hdparm_data

        except Exception as e:
            self.logger.error(f"Error parsing hdparm output: {e}")
            return {}

    def _update_filesystem_usage(
        self, device_id: str, disk_info: Dict[str, Any]
    ) -> None:
        """Update filesystem usage information.

        Args:
            device_id: Device identifier
            disk_info: Disk information dictionary to update
        """
        try:
            mount_point = disk_info.get("mount_point", "")
            if not mount_point:
                return

            # Use df to get current usage
            if "df" in self._available_tools:
                result = subprocess.run(
                    [self._available_tools["df"], "-B1", mount_point],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) >= 2:
                        fields = lines[1].split()
                        if len(fields) >= 4:
                            total_bytes = int(fields[1])
                            used_bytes = int(fields[2])
                            available_bytes = int(fields[3])

                            disk_info.update(
                                {
                                    "size_bytes": total_bytes,
                                    "used_bytes": used_bytes,
                                    "available_bytes": available_bytes,
                                    "used_percent": (
                                        (used_bytes / total_bytes) * 100
                                        if total_bytes > 0
                                        else 0
                                    ),
                                    "free_percent": (
                                        (available_bytes / total_bytes) * 100
                                        if total_bytes > 0
                                        else 0
                                    ),
                                }
                            )

        except Exception as e:
            self.logger.warning(
                f"Error updating filesystem usage for {device_id}: {e}"
            )

    def _collect_data(self) -> Dict[str, Any]:
        """Collect Linux-specific disk data.

        Returns:
            Dict containing comprehensive disk monitoring data
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "platform": "linux",
                "physical_disks": [],
                "logical_disks": [],
                "system_info": self._get_system_info(),
                "summary": {
                    "total_physical_disks": 0,
                    "total_logical_disks": 0,
                    "healthy_disks": 0,
                    "warning_disks": 0,
                    "critical_disks": 0,
                    "total_capacity_gb": 0,
                    "total_used_gb": 0,
                    "total_free_gb": 0,
                },
            }

            # Collect physical disk data
            for device_id, disk_info in self._physical_disks.items():
                try:
                    physical_data = self._collect_physical_disk_data(
                        device_id, disk_info
                    )
                    if physical_data:
                        data["physical_disks"].append(physical_data)
                except Exception as e:
                    self.logger.error(
                        f"Error collecting data for physical disk "
                        f"{device_id}: {e}"
                    )
                    continue

            # Collect logical disk data
            total_capacity = 0
            total_used = 0
            total_free = 0

            for device_id, disk_info in self._logical_disks.items():
                try:
                    logical_data = self._collect_logical_disk_data(
                        device_id, disk_info
                    )
                    if logical_data:
                        data["logical_disks"].append(logical_data)

                        # Update summary
                        total_capacity += logical_data.get("size_bytes", 0)
                        total_used += logical_data.get("used_bytes", 0)
                        total_free += logical_data.get("available_bytes", 0)

                        # Count health status
                        health_status = logical_data.get(
                            "health_status", "unknown"
                        )
                        if health_status == "healthy":
                            data["summary"]["healthy_disks"] += 1
                        elif health_status == "warning":
                            data["summary"]["warning_disks"] += 1
                        elif health_status == "critical":
                            data["summary"]["critical_disks"] += 1

                except Exception as e:
                    self.logger.error(
                        f"Error collecting data for logical disk "
                        f"{device_id}: {e}"
                    )
                    continue

            # Update summary
            data["summary"]["total_physical_disks"] = len(
                data["physical_disks"]
            )
            data["summary"]["total_logical_disks"] = len(data["logical_disks"])
            data["summary"]["total_capacity_gb"] = total_capacity / (1024**3)
            data["summary"]["total_used_gb"] = total_used / (1024**3)
            data["summary"]["total_free_gb"] = total_free / (1024**3)

            return data

        except Exception as e:
            self.logger.error(f"Error collecting Linux disk data: {e}")
            error_handler.handle_error(e, "LinuxDiskMonitor.collect_data")
            return {}

    def _get_system_info(self) -> Dict[str, Any]:
        """Get Linux system information.

        Returns:
            Dict containing system information
        """
        try:
            system_info = {
                "available_tools": list(self._available_tools.keys()),
                "proc_available": self.proc_available,
                "sys_available": self.sys_available,
            }

            # Get kernel version
            try:
                with open("/proc/version", "r") as f:
                    system_info["kernel_version"] = f.read().strip()
            except Exception:
                pass

            # Get distribution information
            try:
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                system_info["distribution"] = (
                                    line.split("=", 1)[1].strip().strip('"')
                                )
                                break
            except Exception:
                pass

            return system_info

        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}

    def _collect_physical_disk_data(
        self, device_id: str, disk_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Collect data for a specific physical disk.

        Args:
            device_id: Physical disk device ID
            disk_info: Cached disk information

        Returns:
            Dict containing physical disk data or None if error
        """
        try:
            # Start with cached info
            data = disk_info.copy()
            data["device_id"] = device_id
            data["disk_type"] = "physical"

            # Get SMART data using enhanced Linux methods
            smart_data = self._get_linux_smart_data(device_id)
            if smart_data:
                data["smart"] = smart_data
                data["temperature"] = smart_data.get("temperature")
                data["power_on_hours"] = smart_data.get("power_on_hours")
                data["health_status"] = smart_data.get(
                    "overall_health", "unknown"
                )

            # Determine overall health status
            data["health_status"] = self._determine_physical_disk_health(data)

            return data

        except Exception as e:
            self.logger.error(
                f"Error collecting physical disk data for {device_id}: {e}"
            )
            return None

    def _collect_logical_disk_data(
        self, device_id: str, disk_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Collect data for a specific logical disk.

        Args:
            device_id: Logical disk device ID
            disk_info: Cached disk information

        Returns:
            Dict containing logical disk data or None if error
        """
        try:
            # Start with cached info
            data = disk_info.copy()
            data["device_id"] = device_id
            data["disk_type"] = "logical"

            # Update current filesystem usage
            if data.get("mount_point"):
                self._update_filesystem_usage(device_id, data)

            # Determine health status
            data["health_status"] = self._determine_logical_disk_health(data)

            return data

        except Exception as e:
            self.logger.error(
                f"Error collecting logical disk data for {device_id}: {e}"
            )
            return None

    def _determine_physical_disk_health(
        self, disk_data: Dict[str, Any]
    ) -> str:
        """Determine the health status of a physical disk.

        Args:
            disk_data: Physical disk data

        Returns:
            Health status: 'healthy', 'warning', or 'critical'
        """
        try:
            # Check SMART data
            smart_data = disk_data.get("smart", {})
            if smart_data:
                # Check overall health
                overall_health = smart_data.get("overall_health", "").lower()
                if overall_health in ["failed", "failing"]:
                    return "critical"
                elif overall_health in ["warning", "degraded"]:
                    return "warning"

                # Check temperature
                temperature = smart_data.get("temperature")
                if temperature is not None:
                    if temperature >= 60:
                        return "critical"
                    elif temperature >= 50:
                        return "warning"

            # Check if SMART is enabled
            if disk_data.get("smart_enabled") is False:
                return "warning"

            return "healthy"

        except Exception as e:
            self.logger.error(f"Error determining physical disk health: {e}")
            return "unknown"

    def _determine_logical_disk_health(self, disk_data: Dict[str, Any]) -> str:
        """Determine the health status of a logical disk.

        Args:
            disk_data: Logical disk data

        Returns:
            Health status: 'healthy', 'warning', or 'critical'
        """
        try:
            # Check space usage
            free_percent = disk_data.get("free_percent", 100)
            if free_percent <= 5:  # Critical threshold
                return "critical"
            elif free_percent <= 15:  # Warning threshold
                return "warning"

            # Check if filesystem is read-only
            if disk_data.get("read_only", False):
                return "warning"

            # Check mount options for errors
            mount_options = disk_data.get("mount_options", [])
            if "ro" in mount_options:
                return "warning"

            return "healthy"

        except Exception as e:
            self.logger.error(f"Error determining logical disk health: {e}")
            return "unknown"

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected Linux disk data.

        Args:
            data: Data to validate

        Returns:
            bool: True if data is valid
        """
        try:
            if not isinstance(data, dict):
                return False

            required_fields = [
                "timestamp",
                "platform",
                "physical_disks",
                "logical_disks",
                "summary",
            ]
            if not all(field in data for field in required_fields):
                return False

            if data["platform"] != "linux":
                return False

            # Validate disk arrays
            if not isinstance(data["physical_disks"], list) or not isinstance(
                data["logical_disks"], list
            ):
                return False

            # Validate summary
            summary = data["summary"]
            if not isinstance(summary, dict):
                return False

            required_summary_fields = [
                "total_physical_disks",
                "total_logical_disks",
                "healthy_disks",
                "warning_disks",
                "critical_disks",
            ]
            if not all(field in summary for field in required_summary_fields):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating Linux disk data: {e}")
            return False

    def get_linux_disk_details(
        self, device_id: str, disk_type: str = "logical"
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific Linux disk.

        Args:
            device_id: Disk device identifier
            disk_type: Type of disk ('logical' or 'physical')

        Returns:
            Detailed disk information or None if not found
        """
        try:
            if disk_type == "logical":
                return self._logical_disks.get(device_id)
            elif disk_type == "physical":
                return self._physical_disks.get(device_id)
            else:
                return None

        except Exception as e:
            self.logger.error(
                f"Error getting Linux disk details for {device_id}: {e}"
            )
            return None

    def refresh_linux_disks(self) -> bool:
        """Refresh the Linux disk information.

        Returns:
            bool: True if refresh was successful
        """
        try:
            self._discover_linux_disks()
            self.logger.info("Linux disk information refreshed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error refreshing Linux disk information: {e}")
            error_handler.handle_error(e, "LinuxDiskMonitor.refresh_disks")
            return False

    def get_disk_performance_history(
        self, device_id: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get performance history for a specific disk.

        Args:
            device_id: Disk device identifier
            hours: Number of hours of history to retrieve

        Returns:
            List of performance data points
        """
        try:
            history = self._disk_performance_history.get(device_id, [])

            # Filter by time range
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            filtered_history = [
                entry
                for entry in history
                if datetime.fromisoformat(
                    entry.get("timestamp", "")
                ).timestamp()
                > cutoff_time
            ]

            return filtered_history

        except Exception as e:
            self.logger.error(
                f"Error getting disk performance history for {device_id}: {e}"
            )
            return []

    def get_proc_diskstats(self) -> Dict[str, Dict[str, Any]]:
        """Get current disk statistics from /proc/diskstats.

        Returns:
            Dict containing disk statistics
        """
        try:
            diskstats = {}
            diskstats_file = os.path.join(self.proc_path, "diskstats")

            if os.path.exists(diskstats_file):
                with open(diskstats_file, "r") as f:
                    lines = f.readlines()

                for line in lines:
                    fields = line.strip().split()
                    if len(fields) >= 14:
                        device_name = fields[2]

                        diskstats[device_name] = {
                            "major": int(fields[0]),
                            "minor": int(fields[1]),
                            "reads_completed": int(fields[3]),
                            "reads_merged": int(fields[4]),
                            "sectors_read": int(fields[5]),
                            "time_reading_ms": int(fields[6]),
                            "writes_completed": int(fields[7]),
                            "writes_merged": int(fields[8]),
                            "sectors_written": int(fields[9]),
                            "time_writing_ms": int(fields[10]),
                            "ios_in_progress": int(fields[11]),
                            "time_io_ms": int(fields[12]),
                            "weighted_time_io_ms": int(fields[13]),
                        }

            return diskstats

        except Exception as e:
            self.logger.error(f"Error getting proc diskstats: {e}")
            return {}

    def cleanup(self) -> None:
        """Clean up Linux-specific resources."""
        try:
            # Clear disk caches
            self._physical_disks.clear()
            self._logical_disks.clear()
            self._disk_performance_history.clear()

            # Clear tool references
            self._available_tools.clear()

            self.logger.info("Linux disk monitor cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during Linux disk monitor cleanup: {e}")
