"""macOS-specific disk health monitoring with IOKit framework."""

import subprocess
import json
import plistlib
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import objc
    from Foundation import NSBundle

    OBJC_AVAILABLE = True

    # Load IOKit framework
    IOKit = NSBundle.bundleWithIdentifier_("com.apple.framework.IOKit")
    if IOKit:
        objc.loadBundleFunctions(
            IOKit,
            globals(),
            [
                ("IOServiceMatching", b"@*"),
                ("IOServiceGetMatchingServices", b"i@*^i"),
                ("IOIteratorNext", b"ii"),
                ("IORegistryEntryCreateCFProperty", b"@i@@i"),
                ("IOObjectRelease", b"vi"),
            ],
        )
        IOKIT_AVAILABLE = True
    else:
        IOKIT_AVAILABLE = False
except ImportError:
    OBJC_AVAILABLE = False
    IOKIT_AVAILABLE = False

from ....core.monitor_base import MonitorBase
from core.error_handler import error_handler


class MacOSDiskMonitor(MonitorBase):
    """macOS-specific disk health monitoring with enhanced capabilities."""

    def __init__(self, update_interval: float = 30.0):
        """Initialize macOS disk monitor.

        Args:
            update_interval: Update interval in seconds
        """
        super().__init__("MacOSDiskHealth", update_interval)

        # macOS-specific components
        self.iokit_enabled = IOKIT_AVAILABLE
        self.objc_enabled = OBJC_AVAILABLE

        # Disk tracking
        self._physical_disks: Dict[str, Dict[str, Any]] = {}
        self._logical_disks: Dict[str, Dict[str, Any]] = {}
        self._disk_performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # macOS system tools
        self._system_tools = {
            "diskutil": "/usr/sbin/diskutil",
            "system_profiler": "/usr/sbin/system_profiler",
            "ioreg": "/usr/sbin/ioreg",
            "smartctl": "/usr/local/bin/smartctl",  # Common Homebrew location
        }

        # Verify tool availability
        self._available_tools = {}
        for tool_name, tool_path in self._system_tools.items():
            if self._check_tool_availability(tool_path):
                self._available_tools[tool_name] = tool_path

        self.logger.info("macOS disk monitor initialized")

    def _check_tool_availability(self, tool_path: str) -> bool:
        """Check if a system tool is available.

        Args:
            tool_path: Path to the tool

        Returns:
            bool: True if tool is available
        """
        try:
            result = subprocess.run(
                [tool_path, "--version"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            return False

    def _initialize_platform_specific(self) -> None:
        """Initialize macOS-specific disk monitoring."""
        try:
            # Check IOKit availability
            if self.iokit_enabled:
                self.logger.info(
                    "IOKit framework available for enhanced disk monitoring"
                )
            else:
                self.logger.warning(
                    "IOKit framework not available - using fallback methods"
                )

            # Check available system tools
            available_tools = list(self._available_tools.keys())
            self.logger.info(
                f"Available macOS tools: {', '.join(available_tools)}"
            )

            if not available_tools:
                self.logger.warning(
                    "No macOS system tools available - limited functionality"
                )

            # Discover disks using macOS-specific methods
            self._discover_macos_disks()

            disk_count = len(self._physical_disks) + len(self._logical_disks)
            self.logger.info(
                f"Initialized macOS disk monitoring for {disk_count} disks"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize macOS disk monitoring: {e}"
            )
            error_handler.handle_error(e, "MacOSDiskMonitor.initialize")
            raise

    def _discover_macos_disks(self) -> None:
        """Discover macOS disks using system tools and IOKit."""
        try:
            self._physical_disks.clear()
            self._logical_disks.clear()

            # Discover physical disks via system_profiler
            if "system_profiler" in self._available_tools:
                self._discover_physical_disks_system_profiler()

            # Discover disks via diskutil
            if "diskutil" in self._available_tools:
                self._discover_disks_diskutil()

            # Enhance with IOKit data if available
            if self.iokit_enabled:
                self._enhance_with_iokit_data()

            # Get additional disk information
            self._enrich_disk_information()

        except Exception as e:
            self.logger.error(f"Error discovering macOS disks: {e}")
            error_handler.handle_error(e, "MacOSDiskMonitor.discover_disks")

    def _discover_physical_disks_system_profiler(self) -> None:
        """Discover physical disks using system_profiler."""
        try:
            result = subprocess.run(
                [
                    self._available_tools["system_profiler"],
                    "SPStorageDataType",
                    "-xml",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.warning(
                    "system_profiler failed to get storage data"
                )
                return

            # Parse XML output
            try:
                plist_data = plistlib.loads(result.stdout.encode())
                storage_data = plist_data[0].get("_items", [])

                for item in storage_data:
                    try:
                        disk_info = self._parse_system_profiler_disk(item)
                        if disk_info:
                            device_id = disk_info.get("device_id")
                            if device_id:
                                self._physical_disks[device_id] = disk_info
                                self.logger.debug(
                                    f"Added physical disk from "
                                    f"system_profiler: {device_id} "
                                    f"({disk_info.get('model', 'Unknown')})"
                                )
                    except Exception as e:
                        self.logger.warning(
                            f"Error parsing system_profiler disk item: {e}"
                        )
                        continue

            except Exception as e:
                self.logger.error(
                    f"Error parsing system_profiler XML output: {e}"
                )

        except Exception as e:
            self.logger.error(
                f"Error discovering physical disks via system_profiler: {e}"
            )

    def _parse_system_profiler_disk(
        self, item: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Parse a disk item from system_profiler output.

        Args:
            item: Disk item from system_profiler

        Returns:
            Dict containing parsed disk information or None
        """
        try:
            # Extract basic information
            disk_info = {
                "device_id": item.get("_name", "Unknown"),
                "model": item.get("_name", "Unknown"),
                "size_bytes": 0,
                "interface_type": item.get(
                    "spstorage_connection_type", "Unknown"
                ),
                "media_type": item.get("spstorage_medium_type", "Unknown"),
                "removable": item.get("spstorage_removable", False),
                "solid_state": item.get("spstorage_solid_state", False),
                "trim_support": item.get("spstorage_trim_support", False),
            }

            # Parse size
            size_str = item.get("spstorage_size", "")
            if size_str:
                disk_info["size_bytes"] = self._parse_size_string(size_str)

            # Get additional attributes
            if "spstorage_physical_drive" in item:
                physical_drive = item["spstorage_physical_drive"]
                disk_info.update(
                    {
                        "manufacturer": physical_drive.get(
                            "spstorage_manufacturer", "Unknown"
                        ),
                        "model": physical_drive.get(
                            "spstorage_model", disk_info["model"]
                        ),
                        "revision": physical_drive.get(
                            "spstorage_revision", "Unknown"
                        ),
                        "serial_number": physical_drive.get(
                            "spstorage_serialnumber", "Unknown"
                        ),
                        "smart_status": physical_drive.get(
                            "spstorage_smart_status", "Unknown"
                        ),
                    }
                )

            # Get volumes information
            volumes = item.get("_items", [])
            if volumes:
                disk_info["volumes"] = []
                for volume in volumes:
                    volume_info = self._parse_volume_info(volume)
                    if volume_info:
                        disk_info["volumes"].append(volume_info)

            return disk_info

        except Exception as e:
            self.logger.error(f"Error parsing system_profiler disk item: {e}")
            return None

    def _parse_volume_info(
        self, volume: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Parse volume information from system_profiler.

        Args:
            volume: Volume item from system_profiler

        Returns:
            Dict containing volume information or None
        """
        try:
            volume_info = {
                "name": volume.get("_name", "Unknown"),
                "mount_point": volume.get("spstorage_mount_point", ""),
                "file_system": volume.get("spstorage_file_system", "Unknown"),
                "size_bytes": 0,
                "available_bytes": 0,
                "used_bytes": 0,
                "writable": volume.get("spstorage_writable", False),
                "ignore_ownership": volume.get(
                    "spstorage_ignore_ownership", False
                ),
            }

            # Parse sizes
            size_str = volume.get("spstorage_size", "")
            if size_str:
                volume_info["size_bytes"] = self._parse_size_string(size_str)

            available_str = volume.get("spstorage_free_space", "")
            if available_str:
                volume_info["available_bytes"] = self._parse_size_string(
                    available_str
                )
                volume_info["used_bytes"] = (
                    volume_info["size_bytes"] - volume_info["available_bytes"]
                )

            # Calculate percentages
            if volume_info["size_bytes"] > 0:
                volume_info["used_percent"] = (
                    volume_info["used_bytes"] / volume_info["size_bytes"]
                ) * 100
                volume_info["free_percent"] = (
                    volume_info["available_bytes"] / volume_info["size_bytes"]
                ) * 100

            return volume_info

        except Exception as e:
            self.logger.error(f"Error parsing volume info: {e}")
            return None

    def _parse_size_string(self, size_str: str) -> int:
        """Parse a size string (e.g., '1 TB', '500 GB') to bytes.

        Args:
            size_str: Size string to parse

        Returns:
            Size in bytes
        """
        try:
            # Remove parentheses and extra whitespace
            size_str = re.sub(r"[(),]", "", size_str).strip()

            # Extract number and unit
            match = re.match(
                r"([\d.,]+)\s*([KMGTPE]?B)", size_str, re.IGNORECASE
            )
            if not match:
                return 0

            number_str, unit = match.groups()
            number = float(number_str.replace(",", ""))

            # Convert to bytes
            unit_multipliers = {
                "B": 1,
                "KB": 1024,
                "MB": 1024**2,
                "GB": 1024**3,
                "TB": 1024**4,
                "PB": 1024**5,
                "EB": 1024**6,
            }

            multiplier = unit_multipliers.get(unit.upper(), 1)
            return int(number * multiplier)

        except Exception as e:
            self.logger.error(f"Error parsing size string '{size_str}': {e}")
            return 0

    def _discover_disks_diskutil(self) -> None:
        """Discover disks using diskutil."""
        try:
            # Get list of all disks
            result = subprocess.run(
                [self._available_tools["diskutil"], "list", "-plist"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.warning("diskutil list failed")
                return

            # Parse plist output
            try:
                plist_data = plistlib.loads(result.stdout.encode())
                all_disks = plist_data.get("AllDisks", [])
                whole_disks = plist_data.get("WholeDisks", [])

                # Process whole disks (physical disks)
                for disk_id in whole_disks:
                    try:
                        disk_info = self._get_diskutil_info(disk_id)
                        if disk_info and disk_info.get("device_id"):
                            # Add to physical disks if not already present
                            device_id = disk_info["device_id"]
                            if device_id not in self._physical_disks:
                                self._physical_disks[device_id] = disk_info
                                self.logger.debug(
                                    f"Added physical disk from diskutil: "
                                    f"{device_id}"
                                )
                    except Exception as e:
                        self.logger.warning(
                            f"Error processing whole disk {disk_id}: {e}"
                        )
                        continue

                # Process all disks for logical volumes
                for disk_id in all_disks:
                    try:
                        # This is a partition/volume
                        if disk_id not in whole_disks:
                            volume_info = self._get_diskutil_info(disk_id)
                            if volume_info and volume_info.get("device_id"):
                                device_id = volume_info["device_id"]
                                self._logical_disks[device_id] = volume_info
                                self.logger.debug(
                                    f"Added logical disk from diskutil: "
                                    f"{device_id}"
                                )
                    except Exception as e:
                        self.logger.warning(
                            f"Error processing disk {disk_id}: {e}"
                        )
                        continue

            except Exception as e:
                self.logger.error(f"Error parsing diskutil plist output: {e}")

        except Exception as e:
            self.logger.error(f"Error discovering disks via diskutil: {e}")

    def _get_diskutil_info(self, disk_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a disk using diskutil.

        Args:
            disk_id: Disk identifier (e.g., 'disk0', 'disk1s1')

        Returns:
            Dict containing disk information or None
        """
        try:
            result = subprocess.run(
                [self._available_tools["diskutil"], "info", "-plist", disk_id],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                return None

            # Parse plist output
            plist_data = plistlib.loads(result.stdout.encode())

            # Extract relevant information
            disk_info = {
                "device_id": disk_id,
                "device_node": plist_data.get("DeviceNode", ""),
                "volume_name": plist_data.get("VolumeName", ""),
                "mount_point": plist_data.get("MountPoint", ""),
                "file_system": plist_data.get("FilesystemType", "Unknown"),
                "size_bytes": plist_data.get("TotalSize", 0),
                "available_bytes": plist_data.get("FreeSpace", 0),
                "used_bytes": 0,
                "block_size": plist_data.get("DeviceBlockSize", 512),
                "whole_disk": plist_data.get("WholeDisk", False),
                "writable": plist_data.get("Writable", False),
                "removable": plist_data.get("RemovableMedia", False),
                "solid_state": plist_data.get("SolidState", False),
                "smart_status": plist_data.get("SMARTStatus", "Unknown"),
                "partition_type": plist_data.get("Content", "Unknown"),
            }

            # Calculate usage
            if (
                disk_info["size_bytes"] > 0
                and disk_info["available_bytes"] > 0
            ):
                disk_info["used_bytes"] = (
                    disk_info["size_bytes"] - disk_info["available_bytes"]
                )
                disk_info["used_percent"] = (
                    disk_info["used_bytes"] / disk_info["size_bytes"]
                ) * 100
                disk_info["free_percent"] = (
                    disk_info["available_bytes"] / disk_info["size_bytes"]
                ) * 100

            # Get parent disk information for partitions
            parent_whole_disk = plist_data.get("ParentWholeDisk", "")
            if parent_whole_disk:
                disk_info["parent_disk"] = parent_whole_disk

            # Get additional attributes
            disk_info.update(
                {
                    "bus_protocol": plist_data.get("BusProtocol", "Unknown"),
                    "device_tree_path": plist_data.get("DeviceTreePath", ""),
                    "io_registry_entry_name": plist_data.get(
                        "IORegistryEntryName", ""
                    ),
                    "media_name": plist_data.get("MediaName", ""),
                    "media_type": plist_data.get("MediaType", "Unknown"),
                }
            )

            return disk_info

        except Exception as e:
            self.logger.error(
                f"Error getting diskutil info for {disk_id}: {e}"
            )
            return None

    def _enhance_with_iokit_data(self) -> None:
        """Enhance disk information with IOKit data."""
        try:
            if not self.iokit_enabled:
                return

            # This would require more complex IOKit integration
            # For now, we'll use ioreg as a fallback
            if "ioreg" in self._available_tools:
                self._enhance_with_ioreg_data()

        except Exception as e:
            self.logger.error(f"Error enhancing with IOKit data: {e}")

    def _enhance_with_ioreg_data(self) -> None:
        """Enhance disk information with ioreg data."""
        try:
            # Get storage controller information
            result = subprocess.run(
                [
                    self._available_tools["ioreg"],
                    "-r",
                    "-c",
                    "IOBlockStorageDriver",
                    "-a",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse ioreg output (this is complex and would need
                # detailed parsing)
                # For now, we'll extract basic information
                self._parse_ioreg_output(result.stdout)

        except Exception as e:
            self.logger.error(f"Error enhancing with ioreg data: {e}")

    def _parse_ioreg_output(self, ioreg_output: str) -> None:
        """Parse ioreg output for additional disk information.

        Args:
            ioreg_output: Raw ioreg output
        """
        try:
            # This is a simplified parser - full implementation would be
            # more complex
            lines = ioreg_output.split("\n")
            current_device = None

            for line in lines:
                line = line.strip()

                # Look for device entries
                if "IOBlockStorageDriver" in line:
                    # Extract device information
                    pass

                # Extract properties
                if "=" in line and current_device:
                    # Parse property lines
                    pass

        except Exception as e:
            self.logger.error(f"Error parsing ioreg output: {e}")

    def _enrich_disk_information(self) -> None:
        """Enrich disk information with additional macOS-specific data."""
        try:
            # Get SMART data for physical disks
            for device_id, disk_info in self._physical_disks.items():
                try:
                    smart_data = self._get_macos_smart_data(device_id)
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

            # Get additional volume information for logical disks
            for device_id, disk_info in self._logical_disks.items():
                try:
                    # Update current space usage
                    self._update_volume_usage(device_id, disk_info)
                except Exception as e:
                    self.logger.warning(
                        f"Error updating volume usage for {device_id}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error enriching disk information: {e}")

    def _get_macos_smart_data(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get SMART data using macOS-specific methods.

        Args:
            device_id: Disk device identifier

        Returns:
            Dict containing SMART data or None if unavailable
        """
        try:
            # Try smartctl first if available
            if "smartctl" in self._available_tools:
                smart_data = self._get_smartctl_data_macos(device_id)
                if smart_data:
                    return smart_data

            # Try diskutil SMART status
            if "diskutil" in self._available_tools:
                return self._get_diskutil_smart_data(device_id)

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting macOS SMART data for {device_id}: {e}"
            )
            return None

    def _get_smartctl_data_macos(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get SMART data using smartctl on macOS.

        Args:
            device_id: Disk device identifier

        Returns:
            Dict containing smartctl SMART data or None if unavailable
        """
        try:
            # Convert device ID to device path
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
                f"Error getting smartctl data on macOS for {device_id}: {e}"
            )
            return None

    def _get_diskutil_smart_data(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get basic SMART data using diskutil.

        Args:
            device_id: Disk device identifier

        Returns:
            Dict containing basic SMART data or None if unavailable
        """
        try:
            result = subprocess.run(
                [
                    self._available_tools["diskutil"],
                    "info",
                    "-plist",
                    device_id,
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode != 0:
                return None

            plist_data = plistlib.loads(result.stdout.encode())
            smart_status = plist_data.get("SMARTStatus", "Unknown")

            if smart_status != "Unknown":
                return {
                    "overall_health": (
                        "passed" if smart_status == "Verified" else "failed"
                    ),
                    "smart_status": smart_status,
                }

            return None

        except Exception as e:
            self.logger.error(
                f"Error getting diskutil SMART data for {device_id}: {e}"
            )
            return None

    def _update_volume_usage(
        self, device_id: str, disk_info: Dict[str, Any]
    ) -> None:
        """Update volume usage information.

        Args:
            device_id: Volume device identifier
            disk_info: Disk information dictionary to update
        """
        try:
            mount_point = disk_info.get("mount_point", "")
            if not mount_point:
                return

            # Use df to get current usage
            result = subprocess.run(
                ["df", "-b", mount_point],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    fields = lines[1].split()
                    if len(fields) >= 4:
                        total_blocks = int(fields[1])
                        used_blocks = int(fields[2])
                        available_blocks = int(fields[3])

                        # Update disk info (df reports in 512-byte blocks)
                        block_size = 512
                        disk_info.update(
                            {
                                "size_bytes": total_blocks * block_size,
                                "used_bytes": used_blocks * block_size,
                                "available_bytes": available_blocks
                                * block_size,
                                "used_percent": (
                                    (used_blocks / total_blocks) * 100
                                    if total_blocks > 0
                                    else 0
                                ),
                                "free_percent": (
                                    (available_blocks / total_blocks) * 100
                                    if total_blocks > 0
                                    else 0
                                ),
                            }
                        )

        except Exception as e:
            self.logger.warning(
                f"Error updating volume usage for {device_id}: {e}"
            )

    def _collect_data(self) -> Dict[str, Any]:
        """Collect macOS-specific disk data.

        Returns:
            Dict containing comprehensive disk monitoring data
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "platform": "macos",
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
            self.logger.error(f"Error collecting macOS disk data: {e}")
            error_handler.handle_error(e, "MacOSDiskMonitor.collect_data")
            return {}

    def _get_system_info(self) -> Dict[str, Any]:
        """Get macOS system information.

        Returns:
            Dict containing system information
        """
        try:
            system_info = {
                "available_tools": list(self._available_tools.keys()),
                "iokit_available": self.iokit_enabled,
                "objc_available": self.objc_enabled,
            }

            # Get macOS version
            try:
                result = subprocess.run(
                    ["sw_vers", "-productVersion"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    system_info["macos_version"] = result.stdout.strip()
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

            # Get SMART data using enhanced macOS methods
            smart_data = self._get_macos_smart_data(device_id)
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

            # Update current space usage
            self._update_volume_usage(device_id, data)

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

            # Check SMART status from diskutil
            smart_status = disk_data.get("smart_status", "").lower()
            if smart_status in ["failing", "failed"]:
                return "critical"
            elif smart_status in ["warning"]:
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

            # Check if volume is writable
            if not disk_data.get("writable", True):
                return "warning"

            return "healthy"

        except Exception as e:
            self.logger.error(f"Error determining logical disk health: {e}")
            return "unknown"

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected macOS disk data.

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

            if data["platform"] != "macos":
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
            self.logger.error(f"Error validating macOS disk data: {e}")
            return False

    def get_macos_disk_details(
        self, device_id: str, disk_type: str = "logical"
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific macOS disk.

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
                f"Error getting macOS disk details for {device_id}: {e}"
            )
            return None

    def refresh_macos_disks(self) -> bool:
        """Refresh the macOS disk information.

        Returns:
            bool: True if refresh was successful
        """
        try:
            self._discover_macos_disks()
            self.logger.info("macOS disk information refreshed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error refreshing macOS disk information: {e}")
            error_handler.handle_error(e, "MacOSDiskMonitor.refresh_disks")
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

    def cleanup(self) -> None:
        """Clean up macOS-specific resources."""
        try:
            # Clear disk caches
            self._physical_disks.clear()
            self._logical_disks.clear()
            self._disk_performance_history.clear()

            # Clear tool references
            self._available_tools.clear()

            self.logger.info("macOS disk monitor cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during macOS disk monitor cleanup: {e}")
