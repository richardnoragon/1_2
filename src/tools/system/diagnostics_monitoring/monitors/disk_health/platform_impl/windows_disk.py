"""Windows-specific disk health monitoring with WMI and Performance Counters."""

import logging
import subprocess
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time

try:
    import wmi

    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    wmi = None

try:
    import win32pdh
    import win32pdhutil
    import win32api
    import win32file

    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    win32pdh = None
    win32pdhutil = None
    win32api = None
    win32file = None

from ....core.monitor_base import MonitorBase
from core.error_handler import error_handler


class WindowsDiskMonitor(MonitorBase):
    """Windows-specific disk health monitoring with enhanced capabilities."""

    def __init__(self, update_interval: float = 30.0):
        """Initialize Windows disk monitor.

        Args:
            update_interval: Update interval in seconds
        """
        super().__init__("WindowsDiskHealth", update_interval)

        # Windows-specific components
        self.wmi_connection = None
        self.performance_counters = {}
        self.disk_performance_data = {}

        # Capabilities flags
        self.wmi_enabled = WMI_AVAILABLE
        self.perfcounter_enabled = PYWIN32_AVAILABLE

        # Disk tracking
        self._physical_disks: Dict[str, Dict[str, Any]] = {}
        self._logical_disks: Dict[str, Dict[str, Any]] = {}
        self._disk_performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # Performance counter paths
        self._counter_paths = {
            "disk_reads_sec": r"\PhysicalDisk(*)\Disk Reads/sec",
            "disk_writes_sec": r"\PhysicalDisk(*)\Disk Writes/sec",
            "disk_read_bytes_sec": r"\PhysicalDisk(*)\Disk Read Bytes/sec",
            "disk_write_bytes_sec": r"\PhysicalDisk(*)\Disk Write Bytes/sec",
            "avg_disk_queue_length": r"\PhysicalDisk(*)\Avg. Disk Queue Length",
            "avg_disk_read_time": r"\PhysicalDisk(*)\Avg. Disk sec/Read",
            "avg_disk_write_time": r"\PhysicalDisk(*)\Avg. Disk sec/Write",
            "disk_idle_time": r"\PhysicalDisk(*)\% Idle Time",
        }

        self.logger.info("Windows disk monitor initialized")

    def _initialize_platform_specific(self) -> None:
        """Initialize Windows-specific disk monitoring."""
        try:
            # Initialize WMI connection
            if self.wmi_enabled:
                self._initialize_wmi()
            else:
                self.logger.warning(
                    "WMI not available - limited functionality"
                )

            # Initialize Performance Counters
            if self.perfcounter_enabled:
                self._initialize_performance_counters()
            else:
                self.logger.warning(
                    "Performance Counters not available - limited metrics"
                )

            # Discover disks using Windows-specific methods
            self._discover_windows_disks()

            disk_count = len(self._physical_disks) + len(self._logical_disks)
            self.logger.info(
                f"Initialized Windows disk monitoring for {disk_count} disks"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize Windows disk monitoring: {e}"
            )
            error_handler.handle_error(e, "WindowsDiskMonitor.initialize")
            raise

    def _initialize_wmi(self) -> None:
        """Initialize WMI connection for Windows disk monitoring."""
        try:
            if not WMI_AVAILABLE:
                return

            self.wmi_connection = wmi.WMI()
            self.logger.info("WMI connection established")

            # Test WMI functionality
            disks = self.wmi_connection.Win32_DiskDrive()
            self.logger.debug(f"WMI found {len(disks)} physical disks")

        except Exception as e:
            self.logger.error(f"Failed to initialize WMI: {e}")
            self.wmi_enabled = False
            self.wmi_connection = None

    def _initialize_performance_counters(self) -> None:
        """Initialize Windows Performance Counters."""
        try:
            if not PYWIN32_AVAILABLE:
                return

            # Initialize performance counter queries
            for counter_name, counter_path in self._counter_paths.items():
                try:
                    # Create counter query
                    query = win32pdh.OpenQuery()
                    counter = win32pdh.AddCounter(query, counter_path)

                    self.performance_counters[counter_name] = {
                        "query": query,
                        "counter": counter,
                        "path": counter_path,
                    }

                    self.logger.debug(f"Initialized counter: {counter_name}")

                except Exception as e:
                    self.logger.warning(
                        f"Failed to initialize counter {counter_name}: {e}"
                    )
                    continue

            self.logger.info(
                f"Initialized {len(self.performance_counters)} performance counters"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to initialize performance counters: {e}"
            )
            self.perfcounter_enabled = False

    def _discover_windows_disks(self) -> None:
        """Discover Windows disks using WMI and system APIs."""
        try:
            self._physical_disks.clear()
            self._logical_disks.clear()

            # Discover physical disks via WMI
            if self.wmi_enabled and self.wmi_connection:
                self._discover_physical_disks_wmi()

            # Discover logical disks
            self._discover_logical_disks()

            # Get additional disk information
            self._enrich_disk_information()

        except Exception as e:
            self.logger.error(f"Error discovering Windows disks: {e}")
            error_handler.handle_error(e, "WindowsDiskMonitor.discover_disks")

    def _discover_physical_disks_wmi(self) -> None:
        """Discover physical disks using WMI."""
        try:
            if not self.wmi_connection:
                return

            # Get physical disk drives
            for disk in self.wmi_connection.Win32_DiskDrive():
                try:
                    disk_info = {
                        "device_id": disk.DeviceID,
                        "model": disk.Model or "Unknown",
                        "serial_number": disk.SerialNumber or "Unknown",
                        "size_bytes": int(disk.Size) if disk.Size else 0,
                        "interface_type": disk.InterfaceType or "Unknown",
                        "media_type": disk.MediaType or "Unknown",
                        "status": disk.Status or "Unknown",
                        "manufacturer": disk.Manufacturer or "Unknown",
                        "firmware_revision": disk.FirmwareRevision
                        or "Unknown",
                        "partitions": disk.Partitions or 0,
                        "bytes_per_sector": disk.BytesPerSector or 512,
                        "sectors_per_track": disk.SectorsPerTrack or 0,
                        "tracks_per_cylinder": disk.TracksPerCylinder or 0,
                        "total_cylinders": disk.TotalCylinders or 0,
                        "total_heads": disk.TotalHeads or 0,
                        "total_sectors": disk.TotalSectors or 0,
                        "total_tracks": disk.TotalTracks or 0,
                    }

                    self._physical_disks[disk.DeviceID] = disk_info

                    self.logger.debug(
                        f"Added physical disk: {disk.DeviceID} "
                        f"({disk.Model}, {disk_info['size_bytes'] / (1024**3):.1f} GB)"
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Error processing physical disk {disk.DeviceID}: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error discovering physical disks via WMI: {e}")

    def _discover_logical_disks(self) -> None:
        """Discover logical disks and volumes."""
        try:
            if self.wmi_enabled and self.wmi_connection:
                # Use WMI for logical disks
                for disk in self.wmi_connection.Win32_LogicalDisk():
                    try:
                        if disk.DriveType == 3:  # Local disk
                            disk_info = {
                                "device_id": disk.DeviceID,
                                "volume_name": disk.VolumeName or "",
                                "file_system": disk.FileSystem or "Unknown",
                                "size_bytes": (
                                    int(disk.Size) if disk.Size else 0
                                ),
                                "free_bytes": (
                                    int(disk.FreeSpace)
                                    if disk.FreeSpace
                                    else 0
                                ),
                                "drive_type": disk.DriveType,
                                "media_type": disk.MediaType or "Unknown",
                                "volume_serial_number": disk.VolumeSerialNumber
                                or "",
                                "compressed": disk.Compressed or False,
                                "supports_disk_quotas": disk.SupportsDiskQuotas
                                or False,
                            }

                            # Calculate usage percentages
                            if disk_info["size_bytes"] > 0:
                                used_bytes = (
                                    disk_info["size_bytes"]
                                    - disk_info["free_bytes"]
                                )
                                disk_info["used_bytes"] = used_bytes
                                disk_info["used_percent"] = (
                                    used_bytes / disk_info["size_bytes"]
                                ) * 100
                                disk_info["free_percent"] = (
                                    disk_info["free_bytes"]
                                    / disk_info["size_bytes"]
                                ) * 100
                            else:
                                disk_info["used_bytes"] = 0
                                disk_info["used_percent"] = 0
                                disk_info["free_percent"] = 0

                            self._logical_disks[disk.DeviceID] = disk_info

                            self.logger.debug(
                                f"Added logical disk: {disk.DeviceID} "
                                f"({disk_info['free_percent']:.1f}% free)"
                            )

                    except Exception as e:
                        self.logger.warning(
                            f"Error processing logical disk {disk.DeviceID}: {e}"
                        )
                        continue
            else:
                # Fallback to basic drive enumeration
                self._discover_logical_disks_fallback()

        except Exception as e:
            self.logger.error(f"Error discovering logical disks: {e}")

    def _discover_logical_disks_fallback(self) -> None:
        """Fallback method for discovering logical disks without WMI."""
        try:
            if not PYWIN32_AVAILABLE:
                return

            # Get all drive letters
            drives = win32api.GetLogicalDriveStrings()
            drive_list = drives.split("\000")[:-1]

            for drive in drive_list:
                try:
                    drive_type = win32file.GetDriveType(drive)
                    if drive_type == win32file.DRIVE_FIXED:  # Fixed disk
                        # Get disk usage
                        free_bytes, total_bytes = win32api.GetDiskFreeSpace(
                            drive
                        )[:2]
                        used_bytes = total_bytes - free_bytes

                        disk_info = {
                            "device_id": drive.rstrip("\\"),
                            "volume_name": "",
                            "file_system": "Unknown",
                            "size_bytes": total_bytes,
                            "free_bytes": free_bytes,
                            "used_bytes": used_bytes,
                            "drive_type": drive_type,
                            "used_percent": (
                                (used_bytes / total_bytes) * 100
                                if total_bytes > 0
                                else 0
                            ),
                            "free_percent": (
                                (free_bytes / total_bytes) * 100
                                if total_bytes > 0
                                else 0
                            ),
                        }

                        self._logical_disks[drive.rstrip("\\")] = disk_info

                except Exception as e:
                    self.logger.warning(f"Error processing drive {drive}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in fallback logical disk discovery: {e}")

    def _enrich_disk_information(self) -> None:
        """Enrich disk information with additional Windows-specific data."""
        try:
            if not self.wmi_enabled or not self.wmi_connection:
                return

            # Get disk partition information
            for partition in self.wmi_connection.Win32_DiskPartition():
                try:
                    disk_index = partition.DiskIndex
                    device_id = f"\\\\.\\PHYSICALDRIVE{disk_index}"

                    if device_id in self._physical_disks:
                        if (
                            "partitions_info"
                            not in self._physical_disks[device_id]
                        ):
                            self._physical_disks[device_id][
                                "partitions_info"
                            ] = []

                        partition_info = {
                            "index": partition.Index,
                            "size_bytes": (
                                int(partition.Size) if partition.Size else 0
                            ),
                            "starting_offset": (
                                int(partition.StartingOffset)
                                if partition.StartingOffset
                                else 0
                            ),
                            "type": partition.Type or "Unknown",
                            "bootable": partition.Bootable or False,
                            "primary_partition": partition.PrimaryPartition
                            or False,
                        }

                        self._physical_disks[device_id][
                            "partitions_info"
                        ].append(partition_info)

                except Exception as e:
                    self.logger.warning(f"Error processing partition: {e}")
                    continue

            # Get disk performance objects
            for (
                perf_disk
            ) in self.wmi_connection.Win32_PerfRawData_PerfDisk_PhysicalDisk():
                try:
                    if perf_disk.Name and perf_disk.Name != "_Total":
                        disk_name = perf_disk.Name

                        # Find matching physical disk
                        for (
                            device_id,
                            disk_info,
                        ) in self._physical_disks.items():
                            if (
                                disk_name in device_id
                                or str(disk_info.get("index", "")) in disk_name
                            ):
                                disk_info["performance_object"] = (
                                    perf_disk.Name
                                )
                                break

                except Exception as e:
                    self.logger.warning(
                        f"Error processing performance disk: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error enriching disk information: {e}")

    def _collect_data(self) -> Dict[str, Any]:
        """Collect Windows-specific disk data.

        Returns:
            Dict containing comprehensive disk monitoring data
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "platform": "windows",
                "physical_disks": [],
                "logical_disks": [],
                "performance_metrics": {},
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
                        f"Error collecting data for physical disk {device_id}: {e}"
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
                        total_free += logical_data.get("free_bytes", 0)

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
                        f"Error collecting data for logical disk {device_id}: {e}"
                    )
                    continue

            # Collect performance metrics
            if self.perfcounter_enabled:
                data["performance_metrics"] = (
                    self._collect_performance_metrics()
                )

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
            self.logger.error(f"Error collecting Windows disk data: {e}")
            error_handler.handle_error(e, "WindowsDiskMonitor.collect_data")
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

            # Get SMART data using enhanced Windows methods
            smart_data = self._get_windows_smart_data(device_id)
            if smart_data:
                data["smart"] = smart_data
                data["temperature"] = smart_data.get("temperature")
                data["power_on_hours"] = smart_data.get("power_on_hours")
                data["health_status"] = smart_data.get(
                    "overall_health", "unknown"
                )

            # Get additional WMI data if available
            if self.wmi_enabled and self.wmi_connection:
                wmi_data = self._get_wmi_disk_data(device_id)
                if wmi_data:
                    data.update(wmi_data)

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
            if self.wmi_enabled and self.wmi_connection:
                try:
                    for disk in self.wmi_connection.Win32_LogicalDisk():
                        if disk.DeviceID == device_id:
                            if disk.Size and disk.FreeSpace:
                                size_bytes = int(disk.Size)
                                free_bytes = int(disk.FreeSpace)
                                used_bytes = size_bytes - free_bytes

                                data.update(
                                    {
                                        "size_bytes": size_bytes,
                                        "free_bytes": free_bytes,
                                        "used_bytes": used_bytes,
                                        "used_percent": (
                                            used_bytes / size_bytes
                                        )
                                        * 100,
                                        "free_percent": (
                                            free_bytes / size_bytes
                                        )
                                        * 100,
                                    }
                                )
                            break
                except Exception as e:
                    self.logger.warning(
                        f"Error updating space usage for {device_id}: {e}"
                    )

            # Get volume-specific information
            volume_info = self._get_volume_information(device_id)
            if volume_info:
                data.update(volume_info)

            # Determine health status
            data["health_status"] = self._determine_logical_disk_health(data)

            return data

        except Exception as e:
            self.logger.error(
                f"Error collecting logical disk data for {device_id}: {e}"
            )
            return None

    def _get_windows_smart_data(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get SMART data using Windows-specific methods.

        Args:
            device_id: Physical disk device ID

        Returns:
            Dict containing SMART data or None if unavailable
        """
        try:
            # Try WMI SMART data first
            if self.wmi_enabled and self.wmi_connection:
                smart_data = self._get_wmi_smart_data(device_id)
                if smart_data:
                    return smart_data

            # Fallback to smartctl if available
            return self._get_smartctl_data_windows(device_id)

        except Exception as e:
            self.logger.error(
                f"Error getting Windows SMART data for {device_id}: {e}"
            )
            return None

    def _get_wmi_smart_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get SMART data via WMI.

        Args:
            device_id: Physical disk device ID

        Returns:
            Dict containing WMI SMART data or None if unavailable
        """
        try:
            if not self.wmi_connection:
                return None

            # Extract disk index from device ID
            disk_index = None
            if "PHYSICALDRIVE" in device_id:
                disk_index = device_id.split("PHYSICALDRIVE")[-1]

            if disk_index is None:
                return None

            # Get SMART data from WMI
            smart_data = {}

            # Try MSStorageDriver_FailurePredictStatus
            try:
                for (
                    item
                ) in (
                    self.wmi_connection.MSStorageDriver_FailurePredictStatus()
                ):
                    if str(item.InstanceName).endswith(f"_{disk_index}"):
                        smart_data["prediction_failure"] = item.PredictFailure
                        smart_data["overall_health"] = (
                            "failed" if item.PredictFailure else "passed"
                        )
                        break
            except Exception:
                pass

            # Try MSStorageDriver_FailurePredictData
            try:
                for (
                    item
                ) in self.wmi_connection.MSStorageDriver_FailurePredictData():
                    if str(item.InstanceName).endswith(f"_{disk_index}"):
                        if item.VendorSpecific:
                            # Parse vendor-specific SMART data
                            vendor_data = self._parse_vendor_smart_data(
                                item.VendorSpecific
                            )
                            smart_data.update(vendor_data)
                        break
            except Exception:
                pass

            # Try MSStorageDriver_FailurePredictThresholds
            try:
                for (
                    item
                ) in (
                    self.wmi_connection.MSStorageDriver_FailurePredictThresholds()
                ):
                    if str(item.InstanceName).endswith(f"_{disk_index}"):
                        if item.VendorSpecific:
                            # Parse threshold data
                            threshold_data = self._parse_threshold_data(
                                item.VendorSpecific
                            )
                            smart_data["thresholds"] = threshold_data
                        break
            except Exception:
                pass

            return smart_data if smart_data else None

        except Exception as e:
            self.logger.error(f"Error getting WMI SMART data: {e}")
            return None

    def _parse_vendor_smart_data(self, vendor_data: bytes) -> Dict[str, Any]:
        """Parse vendor-specific SMART data.

        Args:
            vendor_data: Raw vendor-specific data

        Returns:
            Dict containing parsed SMART attributes
        """
        try:
            parsed_data = {}

            # SMART data is typically 512 bytes with attribute entries
            if len(vendor_data) >= 512:
                # Skip header (first 2 bytes) and parse attributes
                for i in range(2, 362, 12):  # Each attribute is 12 bytes
                    if i + 12 <= len(vendor_data):
                        attr_id = vendor_data[i]
                        if attr_id == 0:
                            continue

                        # Parse attribute structure
                        flags = vendor_data[i + 1]
                        current_value = vendor_data[i + 3]
                        worst_value = vendor_data[i + 4]
                        raw_value = int.from_bytes(
                            vendor_data[i + 5 : i + 11], "little"
                        )

                        # Map common SMART attributes
                        attr_name = self._get_smart_attribute_name(attr_id)

                        parsed_data[attr_name] = {
                            "id": attr_id,
                            "flags": flags,
                            "current_value": current_value,
                            "worst_value": worst_value,
                            "raw_value": raw_value,
                        }

                        # Extract key metrics
                        if attr_id == 194:  # Temperature
                            parsed_data["temperature"] = raw_value & 0xFF
                        elif attr_id == 9:  # Power on hours
                            parsed_data["power_on_hours"] = raw_value
                        elif attr_id == 5:  # Reallocated sectors
                            parsed_data["reallocated_sectors"] = raw_value

            return parsed_data

        except Exception as e:
            self.logger.error(f"Error parsing vendor SMART data: {e}")
            return {}

    def _get_smart_attribute_name(self, attr_id: int) -> str:
        """Get SMART attribute name by ID.

        Args:
            attr_id: SMART attribute ID

        Returns:
            str: Attribute name
        """
        smart_attributes = {
            1: "raw_read_error_rate",
            3: "spin_up_time",
            4: "start_stop_count",
            5: "reallocated_sectors",
            7: "seek_error_rate",
            9: "power_on_hours",
            10: "spin_retry_count",
            12: "power_cycle_count",
            184: "end_to_end_error",
            187: "reported_uncorrectable_errors",
            188: "command_timeout",
            190: "airflow_temperature",
            194: "temperature",
            195: "hardware_ecc_recovered",
            196: "reallocation_event_count",
            197: "current_pending_sectors",
            198: "offline_uncorrectable",
            199: "udma_crc_error_count",
        }

        return smart_attributes.get(attr_id, f"attribute_{attr_id}")

    def _parse_threshold_data(self, threshold_data: bytes) -> Dict[str, Any]:
        """Parse SMART threshold data.

        Args:
            threshold_data: Raw threshold data

        Returns:
            Dict containing threshold information
        """
        try:
            thresholds = {}

            # Parse threshold entries (similar to vendor data structure)
            for i in range(2, 362, 12):
                if i + 12 <= len(threshold_data):
                    attr_id = threshold_data[i]
                    if attr_id == 0:
                        continue

                    threshold_value = threshold_data[i + 1]
                    attr_name = self._get_smart_attribute_name(attr_id)

                    thresholds[attr_name] = {
                        "id": attr_id,
                        "threshold": threshold_value,
                    }

            return thresholds

        except Exception as e:
            self.logger.error(f"Error parsing threshold data: {e}")
            return {}

    def _get_smartctl_data_windows(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get SMART data using smartctl on Windows.

        Args:
            device_id: Physical disk device ID

        Returns:
            Dict containing smartctl SMART data or None if unavailable
        """
        try:
            # Convert device ID to smartctl format
            if "PHYSICALDRIVE" in device_id:
                disk_index = device_id.split("PHYSICALDRIVE")[-1]
                smartctl_device = f"/dev/pd{disk_index}"
            else:
                return None

            # Try to run smartctl
            smartctl_paths = [
                r"C:\Program Files\smartmontools\bin\smartctl.exe",
                r"C:\Program Files (x86)\smartmontools\bin\smartctl.exe",
                "smartctl.exe",
            ]

            for smartctl_path in smartctl_paths:
                try:
                    result = subprocess.run(
                        [smartctl_path, "-a", "-j", smartctl_device],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode in [0, 1, 2, 4] and result.stdout:
                        return json.loads(result.stdout)

                except (
                    subprocess.TimeoutExpired,
                    json.JSONDecodeError,
                    FileNotFoundError,
                ):
                    continue

            return None

        except Exception as e:
            self.logger.error(f"Error getting smartctl data on Windows: {e}")
            return None

    def _get_wmi_disk_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get additional disk data via WMI.

        Args:
            device_id: Physical disk device ID

        Returns:
            Dict containing additional WMI disk data or None if unavailable
        """
        try:
            if not self.wmi_connection:
                return None

            # Get disk drive information
            for disk in self.wmi_connection.Win32_DiskDrive():
                if disk.DeviceID == device_id:
                    return {
                        "availability": disk.Availability,
                        "capabilities": disk.Capabilities,
                        "capability_descriptions": disk.CapabilityDescriptions,
                        "compression_method": disk.CompressionMethod,
                        "config_manager_error_code": disk.ConfigManagerErrorCode,
                        "config_manager_user_config": disk.ConfigManagerUserConfig,
                        "default_block_size": disk.DefaultBlockSize,
                        "error_cleared": disk.ErrorCleared,
                        "error_description": disk.ErrorDescription,
                        "error_methodology": disk.ErrorMethodology,
                        "last_error_code": disk.LastErrorCode,
                        "max_block_size": disk.MaxBlockSize,
                        "max_media_size": disk.MaxMediaSize,
                        "min_block_size": disk.MinBlockSize,
                        "needs_cleaning": disk.NeedsCleaning,
                        "number_of_media_supported": disk.NumberOfMediaSupported,
                        "pnp_device_id": disk.PNPDeviceID,
                        "power_management_capabilities": disk.PowerManagementCapabilities,
                        "power_management_supported": disk.PowerManagementSupported,
                        "scsi_bus": disk.SCSIBus,
                        "scsi_logical_unit": disk.SCSILogicalUnit,
                        "scsi_port": disk.SCSIPort,
                        "scsi_target_id": disk.SCSITargetId,
                        "signature": disk.Signature,
                        "status_info": disk.StatusInfo,
                    }

            return None

        except Exception as e:
            self.logger.error(f"Error getting WMI disk data: {e}")
            return None

    def _get_volume_information(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get volume-specific information.

        Args:
            device_id: Logical disk device ID

        Returns:
            Dict containing volume information or None if unavailable
        """
        try:
            volume_info = {}

            if PYWIN32_AVAILABLE:
                try:
                    # Get volume information using Windows API
                    (
                        volume_name,
                        volume_serial,
                        max_component_length,
                        file_system_flags,
                        file_system_name,
                    ) = win32api.GetVolumeInformation(device_id + "\\")

                    volume_info.update(
                        {
                            "volume_name": volume_name,
                            "volume_serial_number": volume_serial,
                            "max_component_length": max_component_length,
                            "file_system_flags": file_system_flags,
                            "file_system_name": file_system_name,
                        }
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Error getting volume info for {device_id}: {e}"
                    )

            # Get additional WMI volume information
            if self.wmi_enabled and self.wmi_connection:
                try:
                    for volume in self.wmi_connection.Win32_Volume():
                        if volume.DriveLetter == device_id:
                            volume_info.update(
                                {
                                    "block_size": volume.BlockSize,
                                    "capacity": volume.Capacity,
                                    "compressed": volume.Compressed,
                                    "dirty_bit_set": volume.DirtyBitSet,
                                    "file_system": volume.FileSystem,
                                    "free_space": volume.FreeSpace,
                                    "indexing_enabled": volume.IndexingEnabled,
                                    "label": volume.Label,
                                    "maximum_file_name_length": volume.MaximumFileNameLength,
                                    "page_file_present": volume.PageFilePresent,
                                    "quotas_enabled": volume.QuotasEnabled,
                                    "quotas_incomplete": volume.QuotasIncomplete,
                                    "quotas_rebuilding": volume.QuotasRebuilding,
                                    "serial_number": volume.SerialNumber,
                                    "supports_disk_quotas": volume.SupportsDiskQuotas,
                                    "supports_file_based_compression": volume.SupportsFileBasedCompression,
                                }
                            )
                            break

                except Exception as e:
                    self.logger.warning(
                        f"Error getting WMI volume info for {device_id}: {e}"
                    )

            return volume_info if volume_info else None

        except Exception as e:
            self.logger.error(
                f"Error getting volume information for {device_id}: {e}"
            )
            return None

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect Windows Performance Counter metrics.

        Returns:
            Dict containing performance metrics
        """
        try:
            if not self.perfcounter_enabled or not self.performance_counters:
                return {}

            metrics = {}

            for (
                counter_name,
                counter_info,
            ) in self.performance_counters.items():
                try:
                    query = counter_info["query"]
                    counter = counter_info["counter"]

                    # Collect counter data
                    win32pdh.CollectQueryData(query)
                    time.sleep(0.1)  # Small delay for accurate measurement
                    win32pdh.CollectQueryData(query)

                    # Get counter value
                    counter_type, counter_value = (
                        win32pdh.GetFormattedCounterValue(
                            counter, win32pdh.PDH_FMT_DOUBLE
                        )
                    )

                    metrics[counter_name] = {
                        "value": counter_value,
                        "type": counter_type,
                        "timestamp": datetime.now().isoformat(),
                    }

                except Exception as e:
                    self.logger.warning(
                        f"Error collecting counter {counter_name}: {e}"
                    )
                    continue

            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
            return {}

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
                # Check prediction failure
                if smart_data.get("prediction_failure"):
                    return "critical"

                # Check overall health
                overall_health = smart_data.get("overall_health", "").lower()
                if overall_health in ["failed", "failing"]:
                    return "critical"
                elif overall_health in ["warning", "degraded"]:
                    return "warning"

                # Check specific attributes
                reallocated_sectors = smart_data.get("reallocated_sectors", 0)
                if reallocated_sectors > 100:
                    return "critical"
                elif reallocated_sectors > 10:
                    return "warning"

                # Check temperature
                temperature = smart_data.get("temperature")
                if temperature is not None:
                    if temperature >= 60:
                        return "critical"
                    elif temperature >= 50:
                        return "warning"

            # Check WMI status
            status = disk_data.get("status", "").lower()
            if status in ["error", "degraded", "failed"]:
                return "critical"
            elif status in ["warning", "stressed"]:
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

            # Check for dirty bit
            if disk_data.get("dirty_bit_set"):
                return "warning"

            # Check file system errors
            if disk_data.get("error_description"):
                return "warning"

            return "healthy"

        except Exception as e:
            self.logger.error(f"Error determining logical disk health: {e}")
            return "unknown"

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected Windows disk data.

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

            if data["platform"] != "windows":
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
            self.logger.error(f"Error validating Windows disk data: {e}")
            return False

    def get_windows_disk_details(
        self, device_id: str, disk_type: str = "logical"
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific Windows disk.

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
                f"Error getting Windows disk details for {device_id}: {e}"
            )
            return None

    def refresh_windows_disks(self) -> bool:
        """Refresh the Windows disk information.

        Returns:
            bool: True if refresh was successful
        """
        try:
            self._discover_windows_disks()
            self.logger.info("Windows disk information refreshed successfully")
            return True

        except Exception as e:
            self.logger.error(
                f"Error refreshing Windows disk information: {e}"
            )
            error_handler.handle_error(e, "WindowsDiskMonitor.refresh_disks")
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
        """Clean up Windows-specific resources."""
        try:
            # Close performance counter queries
            if self.performance_counters:
                for counter_info in self.performance_counters.values():
                    try:
                        if "query" in counter_info:
                            win32pdh.CloseQuery(counter_info["query"])
                    except Exception as e:
                        self.logger.warning(
                            f"Error closing performance counter: {e}"
                        )

                self.performance_counters.clear()

            # Clean up WMI connection
            if self.wmi_connection:
                try:
                    # WMI connections are automatically cleaned up by Python
                    self.wmi_connection = None
                except Exception as e:
                    self.logger.warning(
                        f"Error cleaning up WMI connection: {e}"
                    )

            self.logger.info("Windows disk monitor cleanup completed")

        except Exception as e:
            self.logger.error(
                f"Error during Windows disk monitor cleanup: {e}"
            )
