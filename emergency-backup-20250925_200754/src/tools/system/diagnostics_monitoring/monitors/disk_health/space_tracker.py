"""Disk space tracking and I/O statistics monitoring."""

import logging
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from core.error_handler import error_handler


class SpaceTracker:
    """Tracks disk space usage and I/O statistics."""

    def __init__(self):
        """Initialize the space tracker."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.SpaceTracker"
        )

        # I/O statistics tracking
        self._io_stats_cache: Dict[str, Dict[str, Any]] = {}
        self._last_io_update = datetime.now()
        self._io_update_interval = timedelta(seconds=5)

        # Space usage history
        self._space_history: Dict[str, List[Dict[str, Any]]] = {}
        self._max_history_points = 100

        self.logger.info("Space tracker initialized")

    def initialize(self) -> bool:
        """Initialize space tracking.

        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize I/O statistics
            self._update_io_stats()

            self.logger.info("Space tracking initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize space tracking: {e}")
            error_handler.handle_error(e, "SpaceTracker.initialize")
            return False

    def get_space_usage(self, mountpoint: str) -> Optional[Dict[str, Any]]:
        """Get space usage for a mountpoint.

        Args:
            mountpoint: Mount point path

        Returns:
            Dict containing space usage information or None if error
        """
        try:
            usage = psutil.disk_usage(mountpoint)

            space_info = {
                "mountpoint": mountpoint,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "total_gb": usage.total / (1024**3),
                "used_gb": usage.used / (1024**3),
                "free_gb": usage.free / (1024**3),
                "used_percent": (usage.used / usage.total) * 100,
                "free_percent": (usage.free / usage.total) * 100,
                "timestamp": datetime.now().isoformat(),
            }

            # Store in history
            self._store_space_history(mountpoint, space_info)

            return space_info

        except (PermissionError, OSError, FileNotFoundError) as e:
            self.logger.warning(f"Cannot access mountpoint {mountpoint}: {e}")
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting space usage for {mountpoint}: {e}"
            )
            return None

    def get_io_stats(self, device: str) -> Optional[Dict[str, Any]]:
        """Get I/O statistics for a device.

        Args:
            device: Device identifier

        Returns:
            Dict containing I/O statistics or None if unavailable
        """
        try:
            # Update I/O stats if needed
            if self._should_update_io_stats():
                self._update_io_stats()

            # Find device in cache
            device_key = self._normalize_device_name(device)
            if device_key in self._io_stats_cache:
                return self._io_stats_cache[device_key].copy()

            # Try alternative device names
            for cached_device in self._io_stats_cache:
                if (
                    device in cached_device
                    or cached_device in device
                    or self._devices_match(device, cached_device)
                ):
                    return self._io_stats_cache[cached_device].copy()

            return None

        except Exception as e:
            self.logger.error(f"Error getting I/O stats for {device}: {e}")
            return None

    def _should_update_io_stats(self) -> bool:
        """Check if I/O stats should be updated.

        Returns:
            bool: True if update is needed
        """
        time_diff = datetime.now() - self._last_io_update
        return time_diff > self._io_update_interval

    def _update_io_stats(self) -> None:
        """Update I/O statistics for all devices."""
        try:
            current_time = datetime.now()

            # Get current I/O counters
            disk_io = psutil.disk_io_counters(perdisk=True)

            for device, counters in disk_io.items():
                device_key = self._normalize_device_name(device)

                # Calculate rates if we have previous data
                previous_data = self._io_stats_cache.get(device_key)

                io_data = {
                    "device": device,
                    "read_count": counters.read_count,
                    "write_count": counters.write_count,
                    "read_bytes": counters.read_bytes,
                    "write_bytes": counters.write_bytes,
                    "read_time": counters.read_time,
                    "write_time": counters.write_time,
                    "timestamp": current_time.isoformat(),
                }

                # Calculate rates
                if previous_data:
                    time_delta = (
                        current_time
                        - datetime.fromisoformat(previous_data["timestamp"])
                    ).total_seconds()

                    if time_delta > 0:
                        io_data.update(
                            {
                                "read_rate_bytes_per_sec": (
                                    (
                                        counters.read_bytes
                                        - previous_data["read_bytes"]
                                    )
                                    / time_delta
                                ),
                                "write_rate_bytes_per_sec": (
                                    (
                                        counters.write_bytes
                                        - previous_data["write_bytes"]
                                    )
                                    / time_delta
                                ),
                                "read_rate_ops_per_sec": (
                                    (
                                        counters.read_count
                                        - previous_data["read_count"]
                                    )
                                    / time_delta
                                ),
                                "write_rate_ops_per_sec": (
                                    (
                                        counters.write_count
                                        - previous_data["write_count"]
                                    )
                                    / time_delta
                                ),
                            }
                        )
                else:
                    # First measurement - no rates available
                    io_data.update(
                        {
                            "read_rate_bytes_per_sec": 0,
                            "write_rate_bytes_per_sec": 0,
                            "read_rate_ops_per_sec": 0,
                            "write_rate_ops_per_sec": 0,
                        }
                    )

                self._io_stats_cache[device_key] = io_data

            self._last_io_update = current_time

        except Exception as e:
            self.logger.error(f"Error updating I/O statistics: {e}")

    def _normalize_device_name(self, device: str) -> str:
        """Normalize device name for consistent lookup.

        Args:
            device: Device name

        Returns:
            Normalized device name
        """
        # Remove common prefixes and suffixes
        normalized = device.replace("/dev/", "").replace("\\", "/")

        # Handle Windows drive letters
        if ":" in normalized and len(normalized) <= 3:
            normalized = normalized.replace(":", "")

        return normalized.lower()

    def _devices_match(self, device1: str, device2: str) -> bool:
        """Check if two device identifiers refer to the same device.

        Args:
            device1: First device identifier
            device2: Second device identifier

        Returns:
            bool: True if devices match
        """
        norm1 = self._normalize_device_name(device1)
        norm2 = self._normalize_device_name(device2)

        # Direct match
        if norm1 == norm2:
            return True

        # Check if one is a substring of the other
        if norm1 in norm2 or norm2 in norm1:
            return True

        # Check for common patterns
        # e.g., sda vs sda1, nvme0n1 vs nvme0n1p1
        if (norm1.startswith(norm2) and norm1[len(norm2) :].isdigit()) or (
            norm2.startswith(norm1) and norm2[len(norm1) :].isdigit()
        ):
            return True

        return False

    def _store_space_history(
        self, mountpoint: str, space_info: Dict[str, Any]
    ) -> None:
        """Store space usage in history.

        Args:
            mountpoint: Mount point
            space_info: Space usage information
        """
        try:
            if mountpoint not in self._space_history:
                self._space_history[mountpoint] = []

            # Add current data point
            history_point = {
                "timestamp": space_info["timestamp"],
                "used_percent": space_info["used_percent"],
                "free_percent": space_info["free_percent"],
                "used_gb": space_info["used_gb"],
                "free_gb": space_info["free_gb"],
            }

            self._space_history[mountpoint].append(history_point)

            # Limit history size
            history_len = len(self._space_history[mountpoint])
            if history_len > self._max_history_points:
                self._space_history[mountpoint] = self._space_history[
                    mountpoint
                ][-self._max_history_points :]

        except Exception as e:
            self.logger.error(f"Error storing space history: {e}")

    def get_space_history(
        self, mountpoint: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get space usage history for a mountpoint.

        Args:
            mountpoint: Mount point
            hours: Number of hours of history to return

        Returns:
            List of historical space usage data
        """
        try:
            if mountpoint not in self._space_history:
                return []

            # Filter by time range
            cutoff_time = datetime.now() - timedelta(hours=hours)

            filtered_history = []
            for point in self._space_history[mountpoint]:
                point_time = datetime.fromisoformat(point["timestamp"])
                if point_time >= cutoff_time:
                    filtered_history.append(point)

            return filtered_history

        except Exception as e:
            self.logger.error(f"Error getting space history: {e}")
            return []

    def get_space_trend(
        self, mountpoint: str, hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze space usage trend.

        Args:
            mountpoint: Mount point
            hours: Number of hours to analyze

        Returns:
            Dict containing trend analysis
        """
        try:
            history = self.get_space_history(mountpoint, hours)

            if len(history) < 2:
                return {
                    "trend": "insufficient_data",
                    "rate_gb_per_hour": 0,
                    "rate_percent_per_hour": 0,
                    "data_points": len(history),
                }

            # Calculate trend
            first_point = history[0]
            last_point = history[-1]

            first_time = datetime.fromisoformat(first_point["timestamp"])
            last_time = datetime.fromisoformat(last_point["timestamp"])

            time_diff_hours = (last_time - first_time).total_seconds() / 3600

            if time_diff_hours <= 0:
                return {
                    "trend": "no_change",
                    "rate_gb_per_hour": 0,
                    "rate_percent_per_hour": 0,
                    "data_points": len(history),
                }

            # Calculate rates
            used_gb_change = last_point["used_gb"] - first_point["used_gb"]
            used_percent_change = (
                last_point["used_percent"] - first_point["used_percent"]
            )

            rate_gb_per_hour = used_gb_change / time_diff_hours
            rate_percent_per_hour = used_percent_change / time_diff_hours

            # Determine trend direction
            if abs(rate_percent_per_hour) < 0.01:  # Less than 0.01% per hour
                trend = "stable"
            elif rate_percent_per_hour > 0:
                trend = "increasing"
            else:
                trend = "decreasing"

            return {
                "trend": trend,
                "rate_gb_per_hour": rate_gb_per_hour,
                "rate_percent_per_hour": rate_percent_per_hour,
                "data_points": len(history),
                "time_span_hours": time_diff_hours,
                "total_change_gb": used_gb_change,
                "total_change_percent": used_percent_change,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing space trend: {e}")
            return {
                "trend": "error",
                "rate_gb_per_hour": 0,
                "rate_percent_per_hour": 0,
                "data_points": 0,
            }

    def predict_full_time(
        self, mountpoint: str, hours: int = 24
    ) -> Optional[datetime]:
        """Predict when a disk will be full based on current trend.

        Args:
            mountpoint: Mount point
            hours: Number of hours of history to use for prediction

        Returns:
            Predicted time when disk will be full, or None if not applicable
        """
        try:
            trend = self.get_space_trend(mountpoint, hours)

            if (
                trend["trend"] != "increasing"
                or trend["rate_percent_per_hour"] <= 0
            ):
                return None

            # Get current space usage
            current_usage = self.get_space_usage(mountpoint)
            if not current_usage:
                return None

            current_free_percent = current_usage["free_percent"]
            rate_per_hour = trend["rate_percent_per_hour"]

            # Calculate hours until full
            hours_until_full = current_free_percent / rate_per_hour

            # Don't predict beyond reasonable timeframes
            if hours_until_full > 8760:  # More than 1 year
                return None

            predicted_time = datetime.now() + timedelta(hours=hours_until_full)
            return predicted_time

        except Exception as e:
            self.logger.error(f"Error predicting full time: {e}")
            return None

    def get_all_mountpoints(self) -> List[str]:
        """Get all available mountpoints.

        Returns:
            List of mountpoint paths
        """
        try:
            mountpoints = []
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    # Test if mountpoint is accessible
                    psutil.disk_usage(partition.mountpoint)
                    mountpoints.append(partition.mountpoint)
                except (PermissionError, OSError):
                    continue

            return mountpoints

        except Exception as e:
            self.logger.error(f"Error getting mountpoints: {e}")
            return []

    def get_io_summary(self) -> Dict[str, Any]:
        """Get I/O summary for all devices.

        Returns:
            Dict containing I/O summary
        """
        try:
            if self._should_update_io_stats():
                self._update_io_stats()

            total_read_bytes = 0
            total_write_bytes = 0
            total_read_ops = 0
            total_write_ops = 0
            total_read_rate = 0
            total_write_rate = 0
            device_count = 0

            for device_data in self._io_stats_cache.values():
                total_read_bytes += device_data.get("read_bytes", 0)
                total_write_bytes += device_data.get("write_bytes", 0)
                total_read_ops += device_data.get("read_count", 0)
                total_write_ops += device_data.get("write_count", 0)
                total_read_rate += device_data.get(
                    "read_rate_bytes_per_sec", 0
                )
                total_write_rate += device_data.get(
                    "write_rate_bytes_per_sec", 0
                )
                device_count += 1

            return {
                "device_count": device_count,
                "total_read_bytes": total_read_bytes,
                "total_write_bytes": total_write_bytes,
                "total_read_gb": total_read_bytes / (1024**3),
                "total_write_gb": total_write_bytes / (1024**3),
                "total_read_ops": total_read_ops,
                "total_write_ops": total_write_ops,
                "total_read_rate_mbps": total_read_rate / (1024**2),
                "total_write_rate_mbps": total_write_rate / (1024**2),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting I/O summary: {e}")
            return {}

    def clear_history(self, mountpoint: Optional[str] = None) -> None:
        """Clear space usage history.

        Args:
            mountpoint: Specific mountpoint to clear, or None for all
        """
        try:
            if mountpoint:
                if mountpoint in self._space_history:
                    del self._space_history[mountpoint]
                    self.logger.info(f"Cleared history for {mountpoint}")
            else:
                self._space_history.clear()
                self.logger.info("Cleared all space usage history")

        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
