"""Data collection framework for diagnostics monitoring."""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .platform_detector import get_platform_detector
from core.error_handler import error_handler


class DataType(Enum):
    """Enumeration of data types."""

    DISK_HEALTH = "disk_health"
    PERFORMANCE = "performance"
    FILESYSTEM = "filesystem"
    BATTERY = "battery"


@dataclass
class DataPoint:
    """Represents a single data point."""

    timestamp: datetime
    data_type: DataType
    monitor_name: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class DataCollector:
    """Handles data collection, validation, and processing."""

    def __init__(self):
        """Initialize the data collector."""
        self.logger = logging.getLogger(
            "RFU.DiagnosticsMonitoring.DataCollector"
        )
        self.platform_detector = get_platform_detector()

        # Data storage
        self._data_points: List[DataPoint] = []
        self._max_data_points = 10000
        self._lock = threading.Lock()

        # Data processors
        self._processors: Dict[DataType, List[Callable]] = {
            DataType.DISK_HEALTH: [],
            DataType.PERFORMANCE: [],
            DataType.FILESYSTEM: [],
            DataType.BATTERY: [],
        }

        # Validation rules
        self._validation_rules: Dict[DataType, List[Callable]] = {
            DataType.DISK_HEALTH: [],
            DataType.PERFORMANCE: [],
            DataType.FILESYSTEM: [],
            DataType.BATTERY: [],
        }

        self.logger.info("Data collector initialized")

    def add_data_point(
        self,
        data_type: DataType,
        monitor_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add a new data point.

        Args:
            data_type: Type of data
            monitor_name: Name of the monitor
            data: The data to store
            metadata: Optional metadata

        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            # Validate data
            if not self._validate_data(data_type, data):
                self.logger.warning(
                    f"Invalid data from {monitor_name}, skipping"
                )
                return False

            # Process data
            processed_data = self._process_data(data_type, data)

            # Create data point
            data_point = DataPoint(
                timestamp=datetime.now(),
                data_type=data_type,
                monitor_name=monitor_name,
                data=processed_data,
                metadata=metadata,
            )

            # Store data point
            with self._lock:
                self._data_points.append(data_point)

                # Limit data points
                if len(self._data_points) > self._max_data_points:
                    self._data_points = self._data_points[
                        -self._max_data_points :
                    ]

            self.logger.debug(
                f"Added data point from {monitor_name} ({data_type.value})"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error adding data point: {e}")
            error_handler.handle_error(e, "DataCollector.add_data_point")
            return False

    def get_data_points(
        self,
        data_type: Optional[DataType] = None,
        monitor_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[DataPoint]:
        """Get data points with optional filtering.

        Args:
            data_type: Filter by data type
            monitor_name: Filter by monitor name
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Limit number of results

        Returns:
            List of matching data points
        """
        with self._lock:
            data_points = self._data_points.copy()

        # Apply filters
        filtered_points = []
        for point in data_points:
            # Filter by data type
            if data_type and point.data_type != data_type:
                continue

            # Filter by monitor name
            if monitor_name and point.monitor_name != monitor_name:
                continue

            # Filter by time range
            if start_time and point.timestamp < start_time:
                continue
            if end_time and point.timestamp > end_time:
                continue

            filtered_points.append(point)

        # Apply limit
        if limit:
            filtered_points = filtered_points[-limit:]

        return filtered_points

    def get_latest_data(
        self,
        data_type: Optional[DataType] = None,
        monitor_name: Optional[str] = None,
    ) -> Optional[DataPoint]:
        """Get the latest data point.

        Args:
            data_type: Filter by data type
            monitor_name: Filter by monitor name

        Returns:
            Latest matching data point or None
        """
        points = self.get_data_points(
            data_type=data_type, monitor_name=monitor_name, limit=1
        )
        return points[0] if points else None

    def get_data_summary(
        self, data_type: DataType, time_range: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Get a summary of data for the specified time range.

        Args:
            data_type: Type of data to summarize
            time_range: Time range for summary

        Returns:
            Dict containing data summary
        """
        end_time = datetime.now()
        start_time = end_time - time_range

        points = self.get_data_points(
            data_type=data_type, start_time=start_time, end_time=end_time
        )

        if not points:
            return {
                "data_type": data_type.value,
                "time_range": str(time_range),
                "point_count": 0,
                "monitors": [],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }

        # Analyze data
        monitors = list(set(point.monitor_name for point in points))

        summary = {
            "data_type": data_type.value,
            "time_range": str(time_range),
            "point_count": len(points),
            "monitors": monitors,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "first_point": points[0].timestamp.isoformat(),
            "last_point": points[-1].timestamp.isoformat(),
        }

        # Add type-specific analysis
        if data_type == DataType.PERFORMANCE:
            summary.update(self._analyze_performance_data(points))
        elif data_type == DataType.DISK_HEALTH:
            summary.update(self._analyze_disk_data(points))
        elif data_type == DataType.BATTERY:
            summary.update(self._analyze_battery_data(points))
        elif data_type == DataType.FILESYSTEM:
            summary.update(self._analyze_filesystem_data(points))

        return summary

    def _validate_data(
        self, data_type: DataType, data: Dict[str, Any]
    ) -> bool:
        """Validate data using registered validation rules.

        Args:
            data_type: Type of data
            data: Data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation
        if not isinstance(data, dict):
            return False

        if not data:
            return False

        # Apply type-specific validation rules
        for validator in self._validation_rules.get(data_type, []):
            try:
                if not validator(data):
                    return False
            except Exception as e:
                self.logger.error(f"Validation error: {e}")
                return False

        return True

    def _process_data(
        self, data_type: DataType, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process data using registered processors.

        Args:
            data_type: Type of data
            data: Data to process

        Returns:
            Processed data
        """
        processed_data = data.copy()

        # Apply processors
        for processor in self._processors.get(data_type, []):
            try:
                processed_data = processor(processed_data)
            except Exception as e:
                self.logger.error(f"Processing error: {e}")

        return processed_data

    def add_processor(
        self,
        data_type: DataType,
        processor: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Add a data processor.

        Args:
            data_type: Type of data to process
            processor: Processing function
        """
        self._processors[data_type].append(processor)
        self.logger.debug(f"Added processor for {data_type.value}")

    def add_validator(
        self, data_type: DataType, validator: Callable[[Dict[str, Any]], bool]
    ) -> None:
        """Add a data validator.

        Args:
            data_type: Type of data to validate
            validator: Validation function
        """
        self._validation_rules[data_type].append(validator)
        self.logger.debug(f"Added validator for {data_type.value}")

    def _analyze_performance_data(
        self, points: List[DataPoint]
    ) -> Dict[str, Any]:
        """Analyze performance data points.

        Args:
            points: Performance data points

        Returns:
            Analysis results
        """
        if not points:
            return {}

        cpu_values = []
        memory_values = []

        for point in points:
            data = point.data
            if "cpu_percent" in data:
                cpu_values.append(data["cpu_percent"])
            if "memory_percent" in data:
                memory_values.append(data["memory_percent"])

        analysis = {}

        if cpu_values:
            analysis["cpu_analysis"] = {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": sum(cpu_values) / len(cpu_values),
                "samples": len(cpu_values),
            }

        if memory_values:
            analysis["memory_analysis"] = {
                "min": min(memory_values),
                "max": max(memory_values),
                "avg": sum(memory_values) / len(memory_values),
                "samples": len(memory_values),
            }

        return analysis

    def _analyze_disk_data(self, points: List[DataPoint]) -> Dict[str, Any]:
        """Analyze disk health data points.

        Args:
            points: Disk health data points

        Returns:
            Analysis results
        """
        if not points:
            return {}

        # Extract disk information
        disks = set()
        space_data = {}

        for point in points:
            data = point.data
            if "disks" in data:
                for disk_info in data["disks"]:
                    disk_id = disk_info.get("device", "unknown")
                    disks.add(disk_id)

                    if disk_id not in space_data:
                        space_data[disk_id] = []

                    if "free_space_percent" in disk_info:
                        space_data[disk_id].append(
                            disk_info["free_space_percent"]
                        )

        analysis = {"disk_count": len(disks), "monitored_disks": list(disks)}

        # Analyze space usage trends
        for disk_id, values in space_data.items():
            if values:
                analysis[f"{disk_id}_space"] = {
                    "min_free": min(values),
                    "max_free": max(values),
                    "avg_free": sum(values) / len(values),
                    "samples": len(values),
                }

        return analysis

    def _analyze_battery_data(self, points: List[DataPoint]) -> Dict[str, Any]:
        """Analyze battery data points.

        Args:
            points: Battery data points

        Returns:
            Analysis results
        """
        if not points:
            return {}

        charge_levels = []
        health_values = []

        for point in points:
            data = point.data
            if "charge_percent" in data:
                charge_levels.append(data["charge_percent"])
            if "health_percent" in data:
                health_values.append(data["health_percent"])

        analysis = {}

        if charge_levels:
            analysis["charge_analysis"] = {
                "min": min(charge_levels),
                "max": max(charge_levels),
                "avg": sum(charge_levels) / len(charge_levels),
                "samples": len(charge_levels),
            }

        if health_values:
            analysis["health_analysis"] = {
                "min": min(health_values),
                "max": max(health_values),
                "avg": sum(health_values) / len(health_values),
                "samples": len(health_values),
            }

        return analysis

    def _analyze_filesystem_data(
        self, points: List[DataPoint]
    ) -> Dict[str, Any]:
        """Analyze filesystem data points.

        Args:
            points: Filesystem data points

        Returns:
            Analysis results
        """
        if not points:
            return {}

        scan_results = []
        error_counts = []

        for point in points:
            data = point.data
            if "scan_result" in data:
                scan_results.append(data["scan_result"])
            if "error_count" in data:
                error_counts.append(data["error_count"])

        analysis = {
            "scan_count": len(scan_results),
            "scans_with_errors": sum(1 for count in error_counts if count > 0),
        }

        if error_counts:
            analysis["error_analysis"] = {
                "total_errors": sum(error_counts),
                "max_errors": max(error_counts),
                "avg_errors": sum(error_counts) / len(error_counts),
            }

        return analysis

    def clear_old_data(self, older_than: timedelta = timedelta(days=7)) -> int:
        """Clear old data points.

        Args:
            older_than: Remove data older than this

        Returns:
            Number of data points removed
        """
        cutoff_time = datetime.now() - older_than

        with self._lock:
            original_count = len(self._data_points)
            self._data_points = [
                point
                for point in self._data_points
                if point.timestamp >= cutoff_time
            ]
            removed_count = original_count - len(self._data_points)

        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} old data points")

        return removed_count

    def get_statistics(self) -> Dict[str, Any]:
        """Get data collector statistics.

        Returns:
            Dict containing statistics
        """
        with self._lock:
            total_points = len(self._data_points)

            # Count by type
            type_counts = {}
            monitor_counts = {}

            for point in self._data_points:
                data_type = point.data_type.value
                monitor_name = point.monitor_name

                type_counts[data_type] = type_counts.get(data_type, 0) + 1
                monitor_counts[monitor_name] = (
                    monitor_counts.get(monitor_name, 0) + 1
                )

        oldest_point = None
        newest_point = None

        if self._data_points:
            oldest_point = min(
                point.timestamp for point in self._data_points
            ).isoformat()
            newest_point = max(
                point.timestamp for point in self._data_points
            ).isoformat()

        return {
            "total_data_points": total_points,
            "max_data_points": self._max_data_points,
            "data_types": type_counts,
            "monitors": monitor_counts,
            "oldest_point": oldest_point,
            "newest_point": newest_point,
            "platform": self.platform_detector.platform.value,
        }


# Global data collector instance
_data_collector: Optional[DataCollector] = None


def get_data_collector() -> DataCollector:
    """Get the global data collector instance.

    Returns:
        DataCollector: The data collector instance
    """
    global _data_collector
    if _data_collector is None:
        _data_collector = DataCollector()
    return _data_collector
