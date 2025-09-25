"""Main disk health monitoring class."""

import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...core.monitor_base import MonitorBase, AlertLevel
from ...core.data_collector import get_data_collector
from .smart_analyzer import SmartAnalyzer
from .space_tracker import SpaceTracker
from core.error_handler import error_handler


class DiskMonitor(MonitorBase):
    """Monitors disk health including SMART data and space usage."""

    def __init__(self, update_interval: float = 30.0):
        """Initialize the disk monitor.

        Args:
            update_interval: Update interval in seconds (default 30s for disks)
        """
        super().__init__("DiskHealth", update_interval)

        # Initialize components
        self.smart_analyzer = SmartAnalyzer()
        self.space_tracker = SpaceTracker()
        self.data_collector = get_data_collector()

        # Disk tracking
        self._monitored_disks: List[str] = []
        self._disk_info_cache: Dict[str, Dict[str, Any]] = {}

        # Thresholds (can be configured via alert manager)
        self.space_warning_threshold = 20.0  # 20% free space warning
        self.space_critical_threshold = 10.0  # 10% free space critical
        self.temp_warning_threshold = 50.0  # 50°C temperature warning
        self.temp_critical_threshold = 60.0  # 60°C temperature critical

        self.logger.info("Disk health monitor initialized")

    def _initialize_platform_specific(self) -> None:
        """Initialize platform-specific disk monitoring."""
        try:
            # Discover available disks
            self._discover_disks()

            # Initialize SMART monitoring
            self.smart_analyzer.initialize(self.platform_detector.platform)

            # Initialize space tracking
            self.space_tracker.initialize()

            disk_count = len(self._monitored_disks)
            self.logger.info(
                f"Initialized disk monitoring for {disk_count} disks"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize disk monitoring: {e}")
            error_handler.handle_error(e, "DiskMonitor.initialize")
            raise

    def _discover_disks(self) -> None:
        """Discover available disks for monitoring."""
        try:
            self._monitored_disks.clear()
            self._disk_info_cache.clear()

            # Get disk partitions
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    # Skip special filesystems
                    if self._should_skip_partition(partition):
                        continue

                    # Get basic disk info
                    usage = psutil.disk_usage(partition.mountpoint)

                    disk_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "free_percent": (usage.free / usage.total) * 100,
                        "used_percent": (usage.used / usage.total) * 100,
                    }

                    self._monitored_disks.append(partition.device)
                    self._disk_info_cache[partition.device] = disk_info

                    self.logger.debug(
                        f"Added disk for monitoring: {partition.device} "
                        f"({disk_info['free_percent']:.1f}% free)"
                    )

                except (PermissionError, OSError) as e:
                    self.logger.warning(
                        f"Cannot access partition {partition.device}: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error discovering disks: {e}")
            error_handler.handle_error(e, "DiskMonitor.discover_disks")

    def _should_skip_partition(self, partition) -> bool:
        """Check if a partition should be skipped.

        Args:
            partition: Disk partition info

        Returns:
            bool: True if partition should be skipped
        """
        # Skip based on filesystem type
        skip_fstypes = {
            "tmpfs",
            "devtmpfs",
            "proc",
            "sysfs",
            "devpts",
            "debugfs",
            "securityfs",
            "cgroup",
            "pstore",
            "hugetlbfs",
            "configfs",
            "selinuxfs",
            "systemd-1",
            "mqueue",
            "autofs",
            "rpc_pipefs",
            "nfsd",
        }

        if partition.fstype.lower() in skip_fstypes:
            return True

        # Skip based on mount point
        skip_mountpoints = {"/dev", "/proc", "/sys", "/run", "/boot/efi"}

        if partition.mountpoint in skip_mountpoints:
            return True

        # Skip if mountpoint starts with certain prefixes
        skip_prefixes = ["/dev/", "/proc/", "/sys/", "/run/"]
        for prefix in skip_prefixes:
            if partition.mountpoint.startswith(prefix):
                return True

        return False

    def _collect_data(self) -> Dict[str, Any]:
        """Collect disk health and space data.

        Returns:
            Dict containing disk monitoring data
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "disks": [],
                "summary": {
                    "total_disks": 0,
                    "healthy_disks": 0,
                    "warning_disks": 0,
                    "critical_disks": 0,
                    "total_space_gb": 0,
                    "used_space_gb": 0,
                    "free_space_gb": 0,
                },
            }

            total_space = 0
            used_space = 0
            free_space = 0

            for device in self._monitored_disks:
                try:
                    disk_data = self._collect_disk_data(device)
                    if disk_data:
                        data["disks"].append(disk_data)

                        # Update summary
                        total_space += disk_data.get("total_bytes", 0)
                        used_space += disk_data.get("used_bytes", 0)
                        free_space += disk_data.get("free_bytes", 0)

                        # Count disk health status
                        health_status = disk_data.get(
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
                        f"Error collecting data for {device}: {e}"
                    )
                    continue

            # Update summary totals
            data["summary"]["total_disks"] = len(data["disks"])
            data["summary"]["total_space_gb"] = total_space / (1024**3)
            data["summary"]["used_space_gb"] = used_space / (1024**3)
            data["summary"]["free_space_gb"] = free_space / (1024**3)

            return data

        except Exception as e:
            self.logger.error(f"Error collecting disk data: {e}")
            error_handler.handle_error(e, "DiskMonitor.collect_data")
            return {}

    def _collect_disk_data(self, device: str) -> Optional[Dict[str, Any]]:
        """Collect data for a specific disk.

        Args:
            device: Disk device identifier

        Returns:
            Dict containing disk data or None if error
        """
        try:
            # Get cached basic info
            disk_info = self._disk_info_cache.get(device, {})
            if not disk_info:
                return None

            # Update space usage
            try:
                usage = psutil.disk_usage(disk_info["mountpoint"])
                disk_info.update(
                    {
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "free_percent": (usage.free / usage.total) * 100,
                        "used_percent": (usage.used / usage.total) * 100,
                    }
                )
            except (PermissionError, OSError):
                # Use cached values if current access fails
                pass

            # Get SMART data
            smart_data = self.smart_analyzer.get_smart_data(device)
            if smart_data:
                disk_info["smart"] = smart_data
                disk_info["temperature"] = smart_data.get("temperature")
                disk_info["power_on_hours"] = smart_data.get("power_on_hours")
                disk_info["reallocated_sectors"] = smart_data.get(
                    "reallocated_sectors"
                )

            # Determine health status
            disk_info["health_status"] = self._determine_health_status(
                disk_info
            )

            # Add I/O statistics if available
            io_stats = self.space_tracker.get_io_stats(device)
            if io_stats:
                disk_info["io_stats"] = io_stats

            return disk_info

        except Exception as e:
            self.logger.error(f"Error collecting data for disk {device}: {e}")
            return None

    def _determine_health_status(self, disk_info: Dict[str, Any]) -> str:
        """Determine the health status of a disk.

        Args:
            disk_info: Disk information dictionary

        Returns:
            Health status: 'healthy', 'warning', or 'critical'
        """
        # Check space usage
        free_percent = disk_info.get("free_percent", 100)
        if free_percent <= self.space_critical_threshold:
            return "critical"
        elif free_percent <= self.space_warning_threshold:
            return "warning"

        # Check temperature
        temperature = disk_info.get("temperature")
        if temperature is not None:
            if temperature >= self.temp_critical_threshold:
                return "critical"
            elif temperature >= self.temp_warning_threshold:
                return "warning"

        # Check SMART data
        smart_data = disk_info.get("smart", {})
        if smart_data:
            # Check for critical SMART indicators
            reallocated_sectors = smart_data.get("reallocated_sectors", 0)
            if reallocated_sectors > 100:  # Configurable threshold
                return "critical"
            elif reallocated_sectors > 10:
                return "warning"

            # Check overall SMART health
            smart_health = smart_data.get("overall_health", "unknown")
            if smart_health.lower() in ["failed", "failing"]:
                return "critical"
            elif smart_health.lower() in ["warning", "degraded"]:
                return "warning"

        return "healthy"

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected disk data.

        Args:
            data: Data to validate

        Returns:
            bool: True if data is valid
        """
        if not isinstance(data, dict):
            return False

        if "disks" not in data or not isinstance(data["disks"], list):
            return False

        if "summary" not in data or not isinstance(data["summary"], dict):
            return False

        # Validate each disk entry
        for disk in data["disks"]:
            if not isinstance(disk, dict):
                return False

            required_fields = ["device", "free_percent", "used_percent"]
            if not all(field in disk for field in required_fields):
                return False

            # Validate percentages
            free_percent = disk.get("free_percent", 0)
            used_percent = disk.get("used_percent", 0)

            if not (0 <= free_percent <= 100) or not (
                0 <= used_percent <= 100
            ):
                return False

        return True

    def _check_alerts(self, data: Dict[str, Any]) -> None:
        """Check for disk-related alert conditions.

        Args:
            data: Current disk monitoring data
        """
        try:
            for disk in data.get("disks", []):
                device = disk.get("device", "unknown")

                # Check space alerts
                free_percent = disk.get("free_percent", 100)
                if free_percent <= self.space_critical_threshold:
                    self._notify_alert_callbacks(
                        f"disk_space_critical_{device}",
                        AlertLevel.CRITICAL,
                        f"Critical: Disk {device} has only "
                        f"{free_percent:.1f}% free space",
                    )
                elif free_percent <= self.space_warning_threshold:
                    self._notify_alert_callbacks(
                        f"disk_space_warning_{device}",
                        AlertLevel.WARNING,
                        f"Warning: Disk {device} has only "
                        f"{free_percent:.1f}% free space",
                    )

                # Check temperature alerts
                temperature = disk.get("temperature")
                if temperature is not None:
                    if temperature >= self.temp_critical_threshold:
                        self._notify_alert_callbacks(
                            f"disk_temp_critical_{device}",
                            AlertLevel.CRITICAL,
                            f"Critical: Disk {device} temperature is "
                            f"{temperature}°C",
                        )
                    elif temperature >= self.temp_warning_threshold:
                        self._notify_alert_callbacks(
                            f"disk_temp_warning_{device}",
                            AlertLevel.WARNING,
                            f"Warning: Disk {device} temperature is "
                            f"{temperature}°C",
                        )

                # Check SMART alerts
                smart_data = disk.get("smart", {})
                if smart_data:
                    overall_health = smart_data.get(
                        "overall_health", ""
                    ).lower()
                    if overall_health in ["failed", "failing"]:
                        self._notify_alert_callbacks(
                            f"disk_smart_critical_{device}",
                            AlertLevel.CRITICAL,
                            f"Critical: Disk {device} SMART status is "
                            f"{overall_health}",
                        )
                    elif overall_health in ["warning", "degraded"]:
                        self._notify_alert_callbacks(
                            f"disk_smart_warning_{device}",
                            AlertLevel.WARNING,
                            f"Warning: Disk {device} SMART status is "
                            f"{overall_health}",
                        )

        except Exception as e:
            self.logger.error(f"Error checking disk alerts: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get the current disk health status.

        Returns:
            Dict containing health status information
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return {
                    "status": "unknown",
                    "message": "No disk data available",
                    "disks": [],
                }

            summary = current_data.get("summary", {})
            disks = current_data.get("disks", [])

            # Determine overall status
            critical_disks = summary.get("critical_disks", 0)
            warning_disks = summary.get("warning_disks", 0)

            if critical_disks > 0:
                overall_status = "critical"
                message = f"{critical_disks} disk(s) in critical state"
            elif warning_disks > 0:
                overall_status = "warning"
                message = f"{warning_disks} disk(s) need attention"
            else:
                overall_status = "healthy"
                message = "All disks are healthy"

            return {
                "status": overall_status,
                "message": message,
                "summary": summary,
                "disks": [
                    {
                        "device": disk.get("device"),
                        "health_status": disk.get("health_status"),
                        "free_percent": disk.get("free_percent"),
                        "temperature": disk.get("temperature"),
                    }
                    for disk in disks
                ],
            }

        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                "status": "error",
                "message": f"Error retrieving disk health: {str(e)}",
                "disks": [],
            }

    def get_disk_details(self, device: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific disk.

        Args:
            device: Disk device identifier

        Returns:
            Detailed disk information or None if not found
        """
        try:
            current_data = self.get_current_data()
            if not current_data:
                return None

            for disk in current_data.get("disks", []):
                if disk.get("device") == device:
                    return disk

            return None

        except Exception as e:
            self.logger.error(f"Error getting disk details for {device}: {e}")
            return None

    def refresh_disk_list(self) -> bool:
        """Refresh the list of monitored disks.

        Returns:
            bool: True if refresh was successful
        """
        try:
            self._discover_disks()
            self.logger.info("Disk list refreshed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error refreshing disk list: {e}")
            error_handler.handle_error(e, "DiskMonitor.refresh_disk_list")
            return False

    def set_thresholds(
        self,
        space_warning: Optional[float] = None,
        space_critical: Optional[float] = None,
        temp_warning: Optional[float] = None,
        temp_critical: Optional[float] = None,
    ) -> None:
        """Set alert thresholds.

        Args:
            space_warning: Warning threshold for free space percentage
            space_critical: Critical threshold for free space percentage
            temp_warning: Warning threshold for temperature (°C)
            temp_critical: Critical threshold for temperature (°C)
        """
        if space_warning is not None:
            self.space_warning_threshold = space_warning
        if space_critical is not None:
            self.space_critical_threshold = space_critical
        if temp_warning is not None:
            self.temp_warning_threshold = temp_warning
        if temp_critical is not None:
            self.temp_critical_threshold = temp_critical

        self.logger.info("Updated disk monitoring thresholds")
