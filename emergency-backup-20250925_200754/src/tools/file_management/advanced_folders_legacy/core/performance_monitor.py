"""
Advanced Folders - Performance Monitoring System

Enterprise monitoring with metrics collection, performance benchmarks,
and automated optimization recommendations for the Advanced Folders system.

Features:
- Real-time performance metrics collection
- System resource monitoring (CPU, memory, disk I/O)
- Operation-specific performance tracking
- Automated performance analysis and optimization recommendations
- Historical performance data storage
- Performance alerts and thresholds
- Benchmarking and comparison capabilities
- Export and reporting functionality

Author: RFU Development Team
Version: 1.0.0
"""

import json
import logging
import platform
import sqlite3
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil


class PerformanceMetricType(Enum):
    """Types of performance metrics."""

    SYSTEM_CPU = "system_cpu"
    SYSTEM_MEMORY = "system_memory"
    SYSTEM_DISK_IO = "system_disk_io"
    SEARCH_OPERATION = "search_operation"
    SCAN_OPERATION = "scan_operation"
    CACHE_OPERATION = "cache_operation"
    METADATA_EXTRACTION = "metadata_extraction"
    DATABASE_QUERY = "database_query"


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Represents a single performance metric measurement."""

    timestamp: datetime
    metric_type: PerformanceMetricType
    operation_name: str
    duration_ms: float
    resource_usage: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type.value,
            "operation_name": self.operation_name,
            "duration_ms": self.duration_ms,
            "resource_usage": self.resource_usage,
            "metadata": self.metadata,
        }


@dataclass
class PerformanceAlert:
    """Represents a performance alert."""

    timestamp: datetime
    level: AlertLevel
    metric_type: PerformanceMetricType
    message: str
    threshold_value: float
    actual_value: float
    operation_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "metric_type": self.metric_type.value,
            "message": self.message,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "operation_name": self.operation_name,
        }


@dataclass
class PerformanceSummary:
    """Summary of performance metrics over a time period."""

    start_time: datetime
    end_time: datetime
    total_operations: int
    average_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    operations_per_second: float
    error_rate: float
    resource_usage_avg: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_operations": self.total_operations,
            "average_duration_ms": self.average_duration_ms,
            "min_duration_ms": self.min_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "p95_duration_ms": self.p95_duration_ms,
            "p99_duration_ms": self.p99_duration_ms,
            "operations_per_second": self.operations_per_second,
            "error_rate": self.error_rate,
            "resource_usage_avg": self.resource_usage_avg,
        }


@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation."""

    category: str
    severity: AlertLevel
    title: str
    description: str
    impact_estimate: str
    implementation_effort: str
    action_items: List[str] = field(default_factory=list)
    metrics_evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "impact_estimate": self.impact_estimate,
            "implementation_effort": self.implementation_effort,
            "action_items": self.action_items,
            "metrics_evidence": self.metrics_evidence,
        }


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(
        self,
        monitor: "PerformanceMonitor",
        operation_name: str,
        metric_type: PerformanceMetricType,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize performance timer."""
        self.monitor = monitor
        self.operation_name = operation_name
        self.metric_type = metric_type
        self.metadata = metadata or {}
        self.start_time = None
        self.start_resources = None

    def __enter__(self):
        """Start timing operation."""
        self.start_time = time.time()
        self.start_resources = self.monitor._capture_resource_snapshot()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing operation and record metric."""
        if self.start_time is not None:
            duration_ms = (time.time() - self.start_time) * 1000
            end_resources = self.monitor._capture_resource_snapshot()

            # Calculate resource usage delta
            resource_usage = {}
            if self.start_resources and end_resources:
                for key in self.start_resources:
                    if key in end_resources:
                        resource_usage[f"delta_{key}"] = (
                            end_resources[key] - self.start_resources[key]
                        )

            # Add error information if exception occurred
            if exc_type is not None:
                self.metadata["error"] = True
                self.metadata["error_type"] = exc_type.__name__
                self.metadata["error_message"] = str(exc_val)

            # Record the metric
            self.monitor.record_metric(
                metric_type=self.metric_type,
                operation_name=self.operation_name,
                duration_ms=duration_ms,
                resource_usage=resource_usage,
                metadata=self.metadata,
            )


class PerformanceMonitor:
    """
    Main performance monitoring system.

    Collects metrics, monitors system resources, generates alerts,
    and provides optimization recommendations.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        max_memory_metrics: int = 10000,
        alert_thresholds: Optional[Dict[str, float]] = None,
        enable_system_monitoring: bool = True,
        monitoring_interval_seconds: float = 5.0,
    ):
        """
        Initialize performance monitor.


        Args:
            db_path: Path to performance database
            max_memory_metrics: Maximum metrics to keep in memory
            alert_thresholds: Custom alert thresholds
            enable_system_monitoring: Enable system resource monitoring
            monitoring_interval_seconds: System monitoring interval
        """
        self.db_path = db_path
        self.max_memory_metrics = max_memory_metrics
        self.enable_system_monitoring = enable_system_monitoring
        self.monitoring_interval = monitoring_interval_seconds

        # In-memory metrics storage
        self.metrics_buffer: deque = deque(maxlen=max_memory_metrics)
        self.alerts_buffer: deque = deque(maxlen=1000)

        # Metrics by type for quick access
        self.metrics_by_type: Dict[PerformanceMetricType, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )

        # Alert thresholds
        self.alert_thresholds = (
            alert_thresholds or self._get_default_thresholds()
        )

        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._shutdown_event = threading.Event()

        # Initialize database
        if self.db_path:
            self._init_database()

        # Logging
        self.logger = logging.getLogger(__name__)

        # System information
        self.system_info = self._get_system_info()

        # Start monitoring if enabled
        if self.enable_system_monitoring:
            self.start_monitoring()

    def record_metric(
        self,
        metric_type: PerformanceMetricType,
        operation_name: str,
        duration_ms: float,
        resource_usage: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a performance metric.


        Args:
            metric_type: Type of metric
            operation_name: Name of operation
            duration_ms: Duration in milliseconds
            resource_usage: Resource usage data
            metadata: Additional metadata
        """
        timestamp = datetime.now()

        metric = PerformanceMetric(
            timestamp=timestamp,
            metric_type=metric_type,
            operation_name=operation_name,
            duration_ms=duration_ms,
            resource_usage=resource_usage or {},
            metadata=metadata or {},
        )

        with self._lock:
            # Add to buffers
            self.metrics_buffer.append(metric)
            self.metrics_by_type[metric_type].append(metric)

            # Check for alerts
            self._check_alerts(metric)

            # Persist to database if available
            if self.db_path:
                self._persist_metric(metric)

    def get_timer(
        self,
        operation_name: str,
        metric_type: PerformanceMetricType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PerformanceTimer:
        """
        Get a performance timer context manager.


        Args:
            operation_name: Name of operation to time
            metric_type: Type of metric
            metadata: Additional metadata

        Returns:
            PerformanceTimer context manager
        """
        return PerformanceTimer(self, operation_name, metric_type, metadata)

    def get_metrics_summary(
        self,
        metric_type: Optional[PerformanceMetricType] = None,
        time_window_minutes: int = 60,
        operation_name: Optional[str] = None,
    ) -> PerformanceSummary:
        """
        Get performance summary for specified criteria.


        Args:
            metric_type: Filter by metric type
            time_window_minutes: Time window in minutes
            operation_name: Filter by operation name

        Returns:
            PerformanceSummary object
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_window_minutes)

        # Filter metrics
        filtered_metrics = []

        with self._lock:
            for metric in self.metrics_buffer:
                if metric.timestamp < start_time:
                    continue

                if metric_type and metric.metric_type != metric_type:
                    continue

                if operation_name and metric.operation_name != operation_name:
                    continue

                filtered_metrics.append(metric)

        if not filtered_metrics:
            return PerformanceSummary(
                start_time=start_time,
                end_time=end_time,
                total_operations=0,
                average_duration_ms=0,
                min_duration_ms=0,
                max_duration_ms=0,
                p95_duration_ms=0,
                p99_duration_ms=0,
                operations_per_second=0,
                error_rate=0,
            )

        # Calculate statistics
        durations = [m.duration_ms for m in filtered_metrics]
        durations.sort()

        total_operations = len(filtered_metrics)
        average_duration = sum(durations) / total_operations
        min_duration = min(durations)
        max_duration = max(durations)

        # Calculate percentiles
        p95_index = int(0.95 * len(durations))
        p99_index = int(0.99 * len(durations))
        p95_duration = (
            durations[p95_index]
            if p95_index < len(durations)
            else max_duration
        )
        p99_duration = (
            durations[p99_index]
            if p99_index < len(durations)
            else max_duration
        )

        # Calculate operations per second
        time_span_seconds = (end_time - start_time).total_seconds()
        ops_per_second = (
            total_operations / time_span_seconds
            if time_span_seconds > 0
            else 0
        )

        # Calculate error rate
        error_count = sum(
            1 for m in filtered_metrics if m.metadata.get("error", False)
        )
        error_rate = (
            (error_count / total_operations) * 100
            if total_operations > 0
            else 0
        )

        # Calculate average resource usage
        resource_usage_avg = {}
        if filtered_metrics:
            resource_keys = set()
            for metric in filtered_metrics:
                resource_keys.update(metric.resource_usage.keys())

            for key in resource_keys:
                values = [
                    m.resource_usage.get(key, 0)
                    for m in filtered_metrics
                    if key in m.resource_usage
                ]
                if values:
                    resource_usage_avg[key] = sum(values) / len(values)

        return PerformanceSummary(
            start_time=start_time,
            end_time=end_time,
            total_operations=total_operations,
            average_duration_ms=average_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            p95_duration_ms=p95_duration,
            p99_duration_ms=p99_duration,
            operations_per_second=ops_per_second,
            error_rate=error_rate,
            resource_usage_avg=resource_usage_avg,
        )

    def get_recent_alerts(self, limit: int = 50) -> List[PerformanceAlert]:
        """Get recent performance alerts."""
        with self._lock:
            return list(self.alerts_buffer)[-limit:]

    def get_optimization_recommendations(
        self,
    ) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations based on collected metrics.

        Returns:
            List of OptimizationRecommendation objects
        """
        recommendations = []

        # Analyze recent performance data
        summary = self.get_metrics_summary(time_window_minutes=60)

        # High latency recommendations
        if summary.average_duration_ms > 1000:  # More than 1 second average
            recommendations.append(
                OptimizationRecommendation(
                    category="Performance",
                    severity=AlertLevel.WARNING,
                    title="High Average Operation Latency",
                    description=(
                        f"Average operation duration is "
                        f"{summary.average_duration_ms:.1f}ms, "
                        "which may impact user experience."
                    ),
                    impact_estimate="20-50% latency reduction",
                    implementation_effort="Medium",
                    action_items=[
                        "Review database query optimization",
                        "Implement result caching",
                        "Consider operation parallelization",
                        "Profile hot code paths",
                    ],
                    metrics_evidence=[
                        f"Average duration: {summary.average_duration_ms:.1f}ms",
                        f"P95 duration: {summary.p95_duration_ms:.1f}ms",
                    ],
                )
            )

        # High error rate recommendations
        if summary.error_rate > 5:  # More than 5% error rate
            recommendations.append(
                OptimizationRecommendation(
                    category="Reliability",
                    severity=AlertLevel.CRITICAL,
                    title="High Error Rate Detected",
                    description=(
                        f"Error rate is {summary.error_rate:.1f}%, indicating "
                        "potential reliability issues."
                    ),
                    impact_estimate="Improved system stability",
                    implementation_effort="High",
                    action_items=[
                        "Investigate error patterns",
                        "Improve error handling",
                        "Add retry mechanisms",
                        "Review input validation",
                    ],
                    metrics_evidence=[
                        f"Error rate: {summary.error_rate:.1f}%",
                        f"Total operations: {summary.total_operations}",
                    ],
                )
            )

        # Memory usage recommendations
        system_metrics = self.get_current_system_metrics()
        if system_metrics.get("memory_percent", 0) > 80:
            recommendations.append(
                OptimizationRecommendation(
                    category="Resource Usage",
                    severity=AlertLevel.WARNING,
                    title="High Memory Usage",
                    description=(
                        f"System memory usage is {system_metrics['memory_percent']:.1f}%, "
                        "which may affect performance."
                    ),
                    impact_estimate="Reduced memory pressure",
                    implementation_effort="Medium",
                    action_items=[
                        "Review memory caching strategies",
                        "Implement memory cleanup routines",
                        "Consider memory usage limits",
                        "Optimize data structures",
                    ],
                    metrics_evidence=[
                        f"Memory usage: {system_metrics['memory_percent']:.1f}%"
                    ],
                )
            )

        # Cache efficiency recommendations
        cache_summary = self.get_metrics_summary(
            metric_type=PerformanceMetricType.CACHE_OPERATION
        )

        if cache_summary.total_operations > 100:
            # Analyze cache hit rates from metadata
            cache_hits = 0
            cache_total = 0

            for metric in self.metrics_by_type[
                PerformanceMetricType.CACHE_OPERATION
            ]:
                if "cache_hit" in metric.metadata:
                    cache_total += 1
                    if metric.metadata["cache_hit"]:
                        cache_hits += 1

            if cache_total > 0:
                hit_rate = (cache_hits / cache_total) * 100
                if hit_rate < 50:  # Less than 50% hit rate
                    recommendations.append(
                        OptimizationRecommendation(
                            category="Caching",
                            severity=AlertLevel.WARNING,
                            title="Low Cache Hit Rate",
                            description=(
                                f"Cache hit rate is {hit_rate:.1f}%, indicating "
                                "inefficient caching strategy."
                            ),
                            impact_estimate="30-60% performance improvement",
                            implementation_effort="Medium",
                            action_items=[
                                "Review cache eviction policies",
                                "Increase cache size if memory allows",
                                "Improve cache key strategies",
                                "Implement cache warming",
                            ],
                            metrics_evidence=[
                                f"Cache hit rate: {hit_rate:.1f}%",
                                f"Cache operations: {cache_total}",
                            ],
                        )
                    )

        return recommendations

    def get_current_system_metrics(self) -> Dict[str, float]:
        """Get current system resource metrics."""
        return self._capture_resource_snapshot()

    def export_metrics(
        self,
        output_path: str,
        format_type: str = "json",
        time_window_hours: int = 24,
    ) -> None:
        """
        Export metrics data to file.


        Args:
            output_path: Output file path
            format_type: Export format (json, csv)
            time_window_hours: Time window in hours
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)

        # Collect metrics
        export_data = {
            "export_timestamp": end_time.isoformat(),
            "time_window_hours": time_window_hours,
            "system_info": self.system_info,
            "metrics": [],
            "alerts": [],
            "summaries": {},
        }

        with self._lock:
            # Export metrics
            for metric in self.metrics_buffer:
                if metric.timestamp >= start_time:
                    export_data["metrics"].append(metric.to_dict())

            # Export alerts
            for alert in self.alerts_buffer:
                if alert.timestamp >= start_time:
                    export_data["alerts"].append(alert.to_dict())

        # Generate summaries by metric type
        for metric_type in PerformanceMetricType:
            summary = self.get_metrics_summary(
                metric_type=metric_type,
                time_window_minutes=time_window_hours * 60,
            )
            export_data["summaries"][metric_type.value] = summary.to_dict()

        # Write to file
        if format_type.lower() == "json":
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def start_monitoring(self) -> None:
        """Start background system monitoring."""
        if (
            self._monitoring_thread is None
            or not self._monitoring_thread.is_alive()
        ):
            self._shutdown_event.clear()
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_worker, daemon=True
            )
            self._monitoring_thread.start()
            self.logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop background system monitoring."""
        self._shutdown_event.set()
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5.0)
        self.logger.info("Performance monitoring stopped")

    def _monitoring_worker(self) -> None:
        """Background worker for system monitoring."""
        while not self._shutdown_event.is_set():
            try:
                # Capture system metrics
                system_metrics = self._capture_resource_snapshot()

                # Record system metrics
                self.record_metric(
                    metric_type=PerformanceMetricType.SYSTEM_CPU,
                    operation_name="system_monitoring",
                    duration_ms=0,  # Instantaneous reading
                    resource_usage=system_metrics,
                    metadata={"monitoring_type": "system"},
                )

                # Sleep until next monitoring interval
                self._shutdown_event.wait(timeout=self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring worker: {str(e)}")
                self._shutdown_event.wait(timeout=self.monitoring_interval)

    def _capture_resource_snapshot(self) -> Dict[str, float]:
        """Capture current system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk I/O
            disk_io = psutil.disk_io_counters()

            # Network I/O
            net_io = psutil.net_io_counters()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "disk_read_mb": (
                    disk_io.read_bytes / (1024**2) if disk_io else 0
                ),
                "disk_write_mb": (
                    disk_io.write_bytes / (1024**2) if disk_io else 0
                ),
                "network_sent_mb": (
                    net_io.bytes_sent / (1024**2) if net_io else 0
                ),
                "network_recv_mb": (
                    net_io.bytes_recv / (1024**2) if net_io else 0
                ),
                "timestamp": time.time(),
            }
        except Exception as e:
            self.logger.warning(f"Error capturing resource snapshot: {str(e)}")
            return {"timestamp": time.time()}

    def _check_alerts(self, metric: PerformanceMetric) -> None:
        """Check if metric triggers any alerts."""
        # Check duration thresholds
        duration_threshold = self.alert_thresholds.get(
            f"{metric.metric_type.value}_duration_ms"
        )

        if duration_threshold and metric.duration_ms > duration_threshold:
            alert = PerformanceAlert(
                timestamp=metric.timestamp,
                level=AlertLevel.WARNING,
                metric_type=metric.metric_type,
                message=(
                    f"Operation '{metric.operation_name}' exceeded duration threshold: "
                    f"{metric.duration_ms:.1f}ms > {duration_threshold}ms"
                ),
                threshold_value=duration_threshold,
                actual_value=metric.duration_ms,
                operation_name=metric.operation_name,
            )
            self.alerts_buffer.append(alert)

        # Check resource usage thresholds
        for resource, value in metric.resource_usage.items():
            threshold_key = f"{resource}_threshold"
            threshold = self.alert_thresholds.get(threshold_key)

            if threshold and value > threshold:
                alert = PerformanceAlert(
                    timestamp=metric.timestamp,
                    level=AlertLevel.WARNING,
                    metric_type=metric.metric_type,
                    message=(
                        f"Resource '{resource}' exceeded threshold: "
                        f"{value:.1f} > {threshold}"
                    ),
                    threshold_value=threshold,
                    actual_value=value,
                    operation_name=metric.operation_name,
                )
                self.alerts_buffer.append(alert)

    def _get_default_thresholds(self) -> Dict[str, float]:
        """Get default alert thresholds."""
        return {
            # Duration thresholds (milliseconds)
            f"{PerformanceMetricType.SEARCH_OPERATION.value}_duration_ms": 5000,
            f"{PerformanceMetricType.SCAN_OPERATION.value}_duration_ms": 10000,
            f"{PerformanceMetricType.METADATA_EXTRACTION.value}_duration_ms": 2000,
            f"{PerformanceMetricType.DATABASE_QUERY.value}_duration_ms": 1000,
            # Resource thresholds
            "cpu_percent_threshold": 90,
            "memory_percent_threshold": 85,
            "disk_read_mb_threshold": 100,
            "disk_write_mb_threshold": 100,
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            return {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "boot_time": datetime.fromtimestamp(
                    psutil.boot_time()
                ).isoformat(),
            }
        except Exception:
            return {"platform": "unknown"}

    def _persist_metric(self, metric: PerformanceMetric) -> None:
        """Persist metric to database."""
        if not self.db_path:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_metrics
                    (timestamp, metric_type, operation_name, duration_ms,
                     resource_usage_json, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        metric.timestamp.isoformat(),
                        metric.metric_type.value,
                        metric.operation_name,
                        metric.duration_ms,
                        json.dumps(metric.resource_usage, default=str),
                        json.dumps(metric.metadata, default=str),
                    ),
                )
        except Exception as e:
            self.logger.warning(f"Error persisting metric: {str(e)}")

    def _init_database(self) -> None:
        """Initialize performance database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        operation_name TEXT NOT NULL,
                        duration_ms REAL NOT NULL,
                        resource_usage_json TEXT,
                        metadata_json TEXT,
                        created_time TEXT DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE INDEX IF NOT EXISTS idx_perf_timestamp
                        ON performance_metrics(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_perf_metric_type
                        ON performance_metrics(metric_type);
                    CREATE INDEX IF NOT EXISTS idx_perf_operation
                        ON performance_metrics(operation_name);

                    CREATE TABLE IF NOT EXISTS performance_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        message TEXT NOT NULL,
                        threshold_value REAL NOT NULL,
                        actual_value REAL NOT NULL,
                        operation_name TEXT,
                        created_time TEXT DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE INDEX IF NOT EXISTS idx_alert_timestamp
                        ON performance_alerts(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_alert_level
                        ON performance_alerts(level);
                    """
                )
        except Exception as e:
            self.logger.error(
                f"Error initializing performance database: {str(e)}"
            )


# Factory and utility functions


def create_performance_monitor(
    enable_persistence: bool = True, db_path: Optional[str] = None, **kwargs
) -> PerformanceMonitor:
    """
    Create a configured performance monitor.


    Args:
        enable_persistence: Enable database persistence
        db_path: Custom database path
        **kwargs: Additional monitor configuration

    Returns:
        Configured PerformanceMonitor
    """
    if enable_persistence and not db_path:
        db_path = "performance_metrics.db"
    elif not enable_persistence:
        db_path = None

    return PerformanceMonitor(db_path=db_path, **kwargs)


def benchmark_operation(
    monitor: PerformanceMonitor,
    operation: Callable,
    operation_name: str,
    metric_type: PerformanceMetricType,
    iterations: int = 1,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[float]:
    """
    Benchmark an operation multiple times.


    Args:
        monitor: Performance monitor instance
        operation: Function to benchmark
        operation_name: Name for the operation
        metric_type: Type of metric
        iterations: Number of iterations
        metadata: Additional metadata

    Returns:
        List of duration measurements in milliseconds
    """
    durations = []

    for i in range(iterations):
        iter_metadata = (metadata or {}).copy()
        iter_metadata["iteration"] = i + 1
        iter_metadata["total_iterations"] = iterations

        with monitor.get_timer(operation_name, metric_type, iter_metadata):
            operation()

        # Get the last recorded metric duration
        if monitor.metrics_buffer:
            durations.append(monitor.metrics_buffer[-1].duration_ms)

    return durations
