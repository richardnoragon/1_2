"""Metrics collection and analysis service for network connectivity tools."""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, deque
import json

from .logging_integration import get_network_logging_manager


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


class MetricUnit(Enum):
    """Metric units."""
    NONE = ""
    BYTES = "bytes"
    SECONDS = "seconds"
    MILLISECONDS = "ms"
    PERCENT = "percent"
    COUNT = "count"
    RATE_PER_SECOND = "per_second"
    MBPS = "mbps"
    PACKETS = "packets"


@dataclass
class MetricValue:
    """Individual metric value."""
    timestamp: datetime
    value: Union[int, float]
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class Metric:
    """Metric definition and storage."""
    name: str
    type: MetricType
    unit: MetricUnit
    description: str
    values: deque
    tags: Dict[str, str] = None
    max_values: int = 1000
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if not isinstance(self.values, deque):
            self.values = deque(maxlen=self.max_values)


@dataclass
class MetricAlert:
    """Metric alert configuration."""
    metric_name: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: Union[int, float]
    duration_seconds: int = 60
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    cooldown_seconds: int = 300


class MetricAggregator:
    """Aggregates metrics over time windows."""
    
    def __init__(self, window_size_seconds: int = 60):
        self.window_size = window_size_seconds
        self.logger = get_network_logging_manager().get_tool_logger(
            'MetricAggregator'
        )
    
    def aggregate_values(self, values: List[MetricValue], 
                        aggregation_type: str = "avg") -> Optional[float]:
        """Aggregate metric values.
        
        Args:
            values: List of metric values
            aggregation_type: Type of aggregation (avg, sum, min, max, count)
            
        Returns:
            Aggregated value or None if no values
        """
        if not values:
            return None
        
        numeric_values = [v.value for v in values if isinstance(v.value, (int, float))]
        
        if not numeric_values:
            return None
        
        try:
            if aggregation_type == "avg":
                return statistics.mean(numeric_values)
            elif aggregation_type == "sum":
                return sum(numeric_values)
            elif aggregation_type == "min":
                return min(numeric_values)
            elif aggregation_type == "max":
                return max(numeric_values)
            elif aggregation_type == "count":
                return len(numeric_values)
            elif aggregation_type == "median":
                return statistics.median(numeric_values)
            elif aggregation_type == "stdev":
                return statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
            else:
                self.logger.warning(f"Unknown aggregation type: {aggregation_type}")
                return statistics.mean(numeric_values)
                
        except Exception as e:
            self.logger.error(f"Error aggregating values: {e}")
            return None
    
    def get_time_window_values(self, metric: Metric, 
                              window_seconds: int = None) -> List[MetricValue]:
        """Get metric values within a time window.
        
        Args:
            metric: Metric to get values from
            window_seconds: Time window in seconds (uses default if None)
            
        Returns:
            List of metric values within the window
        """
        if window_seconds is None:
            window_seconds = self.window_size
        
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        
        return [
            value for value in metric.values
            if value.timestamp >= cutoff_time
        ]


class MetricCollector:
    """Collects metrics from various sources."""
    
    def __init__(self, name: str, collection_interval: int = 30):
        self.name = name
        self.collection_interval = collection_interval
        self.logger = get_network_logging_manager().get_tool_logger(
            f'MetricCollector.{name}'
        )
        
        self._is_active = False
        self._collection_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._metrics_service: Optional['MetricsService'] = None
        
        # Collection functions
        self._collection_functions: List[Callable[[], Dict[str, Any]]] = []
    
    def add_collection_function(self, func: Callable[[], Dict[str, Any]]):
        """Add a function that collects metrics.
        
        Args:
            func: Function that returns a dict of metric_name -> value
        """
        self._collection_functions.append(func)
    
    def start(self, metrics_service: 'MetricsService'):
        """Start the metric collector.
        
        Args:
            metrics_service: Metrics service instance
        """
        if self._is_active:
            return
        
        self._metrics_service = metrics_service
        self._is_active = True
        self._stop_event.clear()
        
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            name=f"MetricCollector-{self.name}",
            daemon=True
        )
        self._collection_thread.start()
        
        self.logger.info(f"Started metric collector: {self.name}")
    
    def stop(self):
        """Stop the metric collector."""
        if not self._is_active:
            return
        
        self._is_active = False
        self._stop_event.set()
        
        if self._collection_thread and self._collection_thread.is_alive():
            self._collection_thread.join(timeout=5.0)
        
        self.logger.info(f"Stopped metric collector: {self.name}")
    
    def _collection_loop(self):
        """Main collection loop."""
        while self._is_active and not self._stop_event.is_set():
            try:
                # Collect metrics from all functions
                for func in self._collection_functions:
                    try:
                        metrics = func()
                        if metrics and self._metrics_service:
                            for metric_name, value in metrics.items():
                                self._metrics_service.record_value(
                                    metric_name, value, 
                                    tags={'collector': self.name}
                                )
                    except Exception as e:
                        self.logger.error(f"Error in collection function: {e}")
                
                # Wait for next collection interval
                self._stop_event.wait(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")


class SystemMetricsCollector(MetricCollector):
    """Collector for system-level metrics."""
    
    def __init__(self):
        super().__init__("System", collection_interval=30)
        self.add_collection_function(self._collect_system_metrics)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            return {
                'system.cpu.percent': cpu_percent,
                'system.memory.percent': memory_percent,
                'system.memory.used_mb': memory_used_mb,
                'system.disk.percent': disk_percent,
                'system.network.bytes_sent': net_io.bytes_sent,
                'system.network.bytes_recv': net_io.bytes_recv,
                'system.network.packets_sent': net_io.packets_sent,
                'system.network.packets_recv': net_io.packets_recv
            }
            
        except ImportError:
            self.logger.warning("psutil not available for system metrics")
            return {}
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}


class NetworkToolMetricsCollector(MetricCollector):
    """Collector for network tool-specific metrics."""
    
    def __init__(self, tool_name: str):
        super().__init__(f"NetworkTool.{tool_name}", collection_interval=15)
        self.tool_name = tool_name
        self._tool_instance = None
    
    def set_tool_instance(self, tool_instance):
        """Set the tool instance to collect metrics from.
        
        Args:
            tool_instance: Network tool instance
        """
        self._tool_instance = tool_instance
        self.add_collection_function(self._collect_tool_metrics)
    
    def _collect_tool_metrics(self) -> Dict[str, Any]:
        """Collect tool-specific metrics."""
        if not self._tool_instance:
            return {}
        
        try:
            metrics = {}
            
            # Basic tool metrics
            if hasattr(self._tool_instance, 'is_running'):
                metrics[f'{self.tool_name}.is_running'] = int(self._tool_instance.is_running)
            
            if hasattr(self._tool_instance, 'is_healthy'):
                metrics[f'{self.tool_name}.is_healthy'] = int(self._tool_instance.is_healthy)
            
            if hasattr(self._tool_instance, '_error_count'):
                metrics[f'{self.tool_name}.error_count'] = self._tool_instance._error_count
            
            # Tool-specific metrics
            if hasattr(self._tool_instance, 'get_current_data'):
                current_data = self._tool_instance.get_current_data()
                for key, value in current_data.items():
                    if isinstance(value, (int, float)):
                        metrics[f'{self.tool_name}.{key}'] = value
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting tool metrics: {e}")
            return {}


class MetricsService:
    """Metrics collection and analysis service."""
    
    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            'MetricsService'
        )
        
        # Threading
        self._lock = threading.RLock()
        
        # Metrics storage
        self._metrics: Dict[str, Metric] = {}
        
        # Aggregation and analysis
        self._aggregator = MetricAggregator()
        
        # Collectors
        self._collectors: Dict[str, MetricCollector] = {}
        
        # Alerts
        self._alerts: Dict[str, MetricAlert] = {}
        
        # Configuration
        self._config = {
            'default_max_values': 1000,
            'cleanup_interval_seconds': 300,
            'alert_check_interval_seconds': 30,
            'enable_system_metrics': True,
            'enable_tool_metrics': True
        }
        
        # Statistics
        self._stats = {
            'total_metrics': 0,
            'total_values_recorded': 0,
            'alerts_triggered': 0
        }
        
        # Background threads
        self._cleanup_thread: Optional[threading.Thread] = None
        self._alert_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the metrics service."""
        try:
            # Create default collectors
            if self._config['enable_system_metrics']:
                self._collectors['system'] = SystemMetricsCollector()
            
            # Start background threads
            self._start_background_threads()
            
            # Start collectors
            for collector in self._collectors.values():
                collector.start(self)
            
            self.logger.info("Metrics service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics service: {e}")
            raise
    
    def _start_background_threads(self):
        """Start background processing threads."""
        self._stop_event.clear()
        
        # Cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            name="MetricsCleanup",
            daemon=True
        )
        self._cleanup_thread.start()
        
        # Alert checking thread
        self._alert_thread = threading.Thread(
            target=self._alert_loop,
            name="MetricsAlerts",
            daemon=True
        )
        self._alert_thread.start()
    
    def _cleanup_loop(self):
        """Background cleanup loop."""
        while not self._stop_event.is_set():
            try:
                self._cleanup_old_values()
                self._stop_event.wait(self._config['cleanup_interval_seconds'])
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def _alert_loop(self):
        """Background alert checking loop."""
        while not self._stop_event.is_set():
            try:
                self._check_alerts()
                self._stop_event.wait(self._config['alert_check_interval_seconds'])
            except Exception as e:
                self.logger.error(f"Error in alert loop: {e}")
    
    def create_metric(self, name: str, metric_type: MetricType, 
                     unit: MetricUnit = MetricUnit.NONE,
                     description: str = "", tags: Dict[str, str] = None,
                     max_values: int = None) -> bool:
        """Create a new metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            unit: Metric unit
            description: Metric description
            tags: Metric tags
            max_values: Maximum number of values to store
            
        Returns:
            True if created successfully
        """
        with self._lock:
            try:
                if name in self._metrics:
                    self.logger.warning(f"Metric already exists: {name}")
                    return False
                
                if max_values is None:
                    max_values = self._config['default_max_values']
                
                metric = Metric(
                    name=name,
                    type=metric_type,
                    unit=unit,
                    description=description,
                    values=deque(maxlen=max_values),
                    tags=tags or {},
                    max_values=max_values
                )
                
                self._metrics[name] = metric
                self._stats['total_metrics'] += 1
                
                self.logger.debug(f"Created metric: {name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to create metric {name}: {e}")
                return False
    
    def record_value(self, metric_name: str, value: Union[int, float],
                    tags: Dict[str, str] = None, timestamp: datetime = None) -> bool:
        """Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Additional tags for this value
            timestamp: Timestamp (current time if None)
            
        Returns:
            True if recorded successfully
        """
        with self._lock:
            try:
                # Auto-create metric if it doesn't exist
                if metric_name not in self._metrics:
                    # Infer metric type from value
                    if isinstance(value, int):
                        metric_type = MetricType.COUNTER
                    else:
                        metric_type = MetricType.GAUGE
                    
                    self.create_metric(metric_name, metric_type)
                
                metric = self._metrics[metric_name]
                
                if timestamp is None:
                    timestamp = datetime.now()
                
                metric_value = MetricValue(
                    timestamp=timestamp,
                    value=value,
                    tags=tags or {}
                )
                
                metric.values.append(metric_value)
                self._stats['total_values_recorded'] += 1
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to record value for {metric_name}: {e}")
                return False
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name.
        
        Args:
            name: Metric name
            
        Returns:
            Metric instance or None if not found
        """
        with self._lock:
            return self._metrics.get(name)
    
    def get_metric_value(self, name: str, aggregation: str = "latest") -> Optional[float]:
        """Get aggregated metric value.
        
        Args:
            name: Metric name
            aggregation: Aggregation type (latest, avg, sum, min, max, count)
            
        Returns:
            Aggregated value or None if not found
        """
        with self._lock:
            metric = self._metrics.get(name)
            if not metric or not metric.values:
                return None
            
            if aggregation == "latest":
                return metric.values[-1].value
            else:
                return self._aggregator.aggregate_values(
                    list(metric.values), aggregation
                )
    
    def get_metric_values(self, name: str, window_seconds: int = 3600) -> List[MetricValue]:
        """Get metric values within a time window.
        
        Args:
            name: Metric name
            window_seconds: Time window in seconds
            
        Returns:
            List of metric values
        """
        with self._lock:
            metric = self._metrics.get(name)
            if not metric:
                return []
            
            return self._aggregator.get_time_window_values(metric, window_seconds)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        with self._lock:
            summary = {}
            
            for name, metric in self._metrics.items():
                if metric.values:
                    latest_value = metric.values[-1].value
                    values_1h = self._aggregator.get_time_window_values(metric, 3600)
                    
                    summary[name] = {
                        'type': metric.type.value,
                        'unit': metric.unit.value,
                        'description': metric.description,
                        'latest_value': latest_value,
                        'total_values': len(metric.values),
                        'values_last_hour': len(values_1h),
                        'avg_last_hour': self._aggregator.aggregate_values(values_1h, "avg"),
                        'min_last_hour': self._aggregator.aggregate_values(values_1h, "min"),
                        'max_last_hour': self._aggregator.aggregate_values(values_1h, "max")
                    }
            
            return summary
    
    def add_tool_collector(self, tool_name: str, tool_instance) -> bool:
        """Add a collector for a network tool.
        
        Args:
            tool_name: Name of the tool
            tool_instance: Tool instance
            
        Returns:
            True if added successfully
        """
        try:
            collector = NetworkToolMetricsCollector(tool_name)
            collector.set_tool_instance(tool_instance)
            
            self._collectors[f"tool_{tool_name}"] = collector
            collector.start(self)
            
            self.logger.info(f"Added tool collector for: {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add tool collector for {tool_name}: {e}")
            return False
    
    def add_alert(self, metric_name: str, condition: str, 
                 threshold: Union[int, float], duration_seconds: int = 60,
                 cooldown_seconds: int = 300) -> bool:
        """Add a metric alert.
        
        Args:
            metric_name: Name of the metric to monitor
            condition: Alert condition (gt, lt, eq, gte, lte)
            threshold: Alert threshold value
            duration_seconds: Duration threshold must be exceeded
            cooldown_seconds: Cooldown period between alerts
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                alert_name = f"{metric_name}_{condition}_{threshold}"
                
                alert = MetricAlert(
                    metric_name=metric_name,
                    condition=condition,
                    threshold=threshold,
                    duration_seconds=duration_seconds,
                    cooldown_seconds=cooldown_seconds
                )
                
                self._alerts[alert_name] = alert
                
                self.logger.info(f"Added metric alert: {alert_name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to add alert: {e}")
                return False
    
    def _check_alerts(self):
        """Check all metric alerts."""
        with self._lock:
            for alert_name, alert in self._alerts.items():
                if not alert.enabled:
                    continue
                
                try:
                    # Check cooldown
                    if (alert.last_triggered and
                        (datetime.now() - alert.last_triggered).total_seconds() < 
                        alert.cooldown_seconds):
                        continue
                    
                    # Get metric values for duration window
                    values = self.get_metric_values(
                        alert.metric_name, alert.duration_seconds
                    )
                    
                    if not values:
                        continue
                    
                    # Check if condition is met for the duration
                    condition_met = True
                    for value in values:
                        if not self._evaluate_condition(
                            value.value, alert.condition, alert.threshold
                        ):
                            condition_met = False
                            break
                    
                    if condition_met:
                        self._trigger_alert(alert_name, alert, values[-1].value)
                        
                except Exception as e:
                    self.logger.error(f"Error checking alert {alert_name}: {e}")
    
    def _evaluate_condition(self, value: Union[int, float], 
                           condition: str, threshold: Union[int, float]) -> bool:
        """Evaluate alert condition.
        
        Args:
            value: Current value
            condition: Condition type
            threshold: Threshold value
            
        Returns:
            True if condition is met
        """
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return value == threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lte":
            return value <= threshold
        else:
            return False
    
    def _trigger_alert(self, alert_name: str, alert: MetricAlert, current_value: Union[int, float]):
        """Trigger a metric alert.
        
        Args:
            alert_name: Name of the alert
            alert: Alert configuration
            current_value: Current metric value
        """
        alert.last_triggered = datetime.now()
        self._stats['alerts_triggered'] += 1
        
        # Send notification (if notification service is available)
        try:
            from .notification_service import get_notification_service, NotificationType
            
            notification_service = get_notification_service()
            notification_service.send_notification(
                type=NotificationType.WARNING,
                title="Metric Alert",
                message=f"Alert triggered: {alert.metric_name} {alert.condition} {alert.threshold} (current: {current_value})",
                source="MetricsService",
                data={
                    'alert_name': alert_name,
                    'metric_name': alert.metric_name,
                    'condition': alert.condition,
                    'threshold': alert.threshold,
                    'current_value': current_value
                }
            )
            
        except ImportError:
            self.logger.warning("Notification service not available for metric alerts")
        except Exception as e:
            self.logger.error(f"Failed to send metric alert notification: {e}")
        
        self.logger.warning(
            f"Metric alert triggered: {alert_name} - "
            f"{alert.metric_name} = {current_value} ({alert.condition} {alert.threshold})"
        )
    
    def _cleanup_old_values(self):
        """Clean up old metric values."""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for metric in self._metrics.values():
                # Remove values older than 24 hours
                while (metric.values and 
                       metric.values[0].timestamp < cutoff_time):
                    metric.values.popleft()
    
    def export_metrics(self, file_path: str, format_type: str = "json",
                      window_seconds: int = 3600) -> bool:
        """Export metrics to file.
        
        Args:
            file_path: Export file path
            format_type: Export format (json, csv)
            window_seconds: Time window for export
            
        Returns:
            True if exported successfully
        """
        try:
            export_data = {}
            
            with self._lock:
                for name, metric in self._metrics.items():
                    values = self._aggregator.get_time_window_values(
                        metric, window_seconds
                    )
                    
                    if format_type == "json":
                        export_data[name] = {
                            'type': metric.type.value,
                            'unit': metric.unit.value,
                            'description': metric.description,
                            'tags': metric.tags,
                            'values': [
                                {
                                    'timestamp': v.timestamp.isoformat(),
                                    'value': v.value,
                                    'tags': v.tags
                                }
                                for v in values
                            ]
                        }
            
            # Write export file
            if format_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif format_type == "csv":
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['metric_name', 'timestamp', 'value', 'tags'])
                    
                    for name, metric in self._metrics.items():
                        values = self._aggregator.get_time_window_values(
                            metric, window_seconds
                        )
                        for value in values:
                            writer.writerow([
                                name,
                                value.timestamp.isoformat(),
                                value.value,
                                json.dumps(value.tags)
                            ])
            
            self.logger.info(f"Exported metrics to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get metrics service statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            return {
                'total_metrics': len(self._metrics),
                'total_values_recorded': self._stats['total_values_recorded'],
                'alerts_configured': len(self._alerts),
                'alerts_triggered': self._stats['alerts_triggered'],
                'active_collectors': len(self._collectors),
                'memory_usage_values': sum(len(m.values) for m in self._metrics.values())
            }
    
    def shutdown(self):
        """Shutdown the metrics service."""
        with self._lock:
            # Stop background threads
            self._stop_event.set()
            
            if self._cleanup_thread and self._cleanup_thread.is_alive():
                self._cleanup_thread.join(timeout=5.0)
            
            if self._alert_thread and self._alert_thread.is_alive():
                self._alert_thread.join(timeout=5.0)
            
            # Stop collectors
            for collector in self._collectors.values():
                try:
                    collector.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping collector: {e}")
            
            self.logger.info("Metrics service shutdown complete")


# Global instance for easy access
_metrics_service = None


def get_metrics_service() -> MetricsService:
    """Get global metrics service instance.
    
    Returns:
        MetricsService instance
    """
    global _metrics_service
    
    if _metrics_service is None:
        _metrics_service = MetricsService()
    
    return _metrics_service


# Convenience functions for recording metrics
def record_counter(name: str, value: int = 1, **kwargs):
    """Record a counter metric."""
    service = get_metrics_service()
    if name not in service._metrics:
        service.create_metric(name, MetricType.COUNTER, MetricUnit.COUNT)
    service.record_value(name, value, **kwargs)


def record_gauge(name: str, value: Union[int, float], **kwargs):
    """Record a gauge metric."""
    service = get_metrics_service()
    if name not in service._metrics:
        service.create_metric(name, MetricType.GAUGE)
    service.record_value(name, value, **kwargs)


def record_timer(name: str, duration_ms: float, **kwargs):
    """Record a timer metric."""
    service = get_metrics_service()
    if name not in service._metrics:
        service.create_metric(name, MetricType.TIMER, MetricUnit.MILLISECONDS)
    service.record_value(name, duration_ms, **kwargs)


def record_rate(name: str, rate: float, **kwargs):
    """Record a rate metric."""
    service = get_metrics_service()
    if name not in service._metrics:
        service.create_metric(name, MetricType.RATE, MetricUnit.RATE_PER_SECOND)
    service.record_value(name, rate, **kwargs)