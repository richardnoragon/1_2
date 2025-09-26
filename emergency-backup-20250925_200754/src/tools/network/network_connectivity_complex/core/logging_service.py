"""Advanced logging service for network connectivity tools."""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import gzip
import csv
from collections import defaultdict, deque

from core.logging_manager import LogManager
from .logging_integration import get_network_logging_manager


class LogLevel(Enum):
    """Enhanced log levels."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    AUDIT = "AUDIT"


class LogFormat(Enum):
    """Log output formats."""

    JSON = "json"
    PLAIN = "plain"
    CSV = "csv"
    XML = "xml"


class LogRotationPolicy(Enum):
    """Log rotation policies."""

    SIZE_BASED = "size_based"
    TIME_BASED = "time_based"
    COMBINED = "combined"


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: datetime
    level: LogLevel
    logger_name: str
    message: str
    tool_name: str
    operation: Optional[str] = None
    context: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    performance_data: Dict[str, Any] = None
    error_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}
        if self.performance_data is None:
            self.performance_data = {}
        if self.error_data is None:
            self.error_data = {}


@dataclass
class LogFilter:
    """Log filtering configuration."""

    min_level: LogLevel = LogLevel.INFO
    max_level: LogLevel = LogLevel.CRITICAL
    tools: List[str] = None
    operations: List[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keywords: List[str] = None
    correlation_ids: List[str] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.operations is None:
            self.operations = []
        if self.keywords is None:
            self.keywords = []
        if self.correlation_ids is None:
            self.correlation_ids = []


class LogCollector:
    """Specialized log collector for different types of network events."""

    def __init__(self, name: str, log_service: "LoggingService"):
        self.name = name
        self.log_service = log_service
        self.logger = get_network_logging_manager().get_tool_logger(
            f"LogCollector.{name}"
        )
        self._is_active = False
        self._collection_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._queue = queue.Queue()

    def start(self):
        """Start the log collector."""
        if self._is_active:
            return

        self._is_active = True
        self._stop_event.clear()
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            name=f"LogCollector-{self.name}",
            daemon=True,
        )
        self._collection_thread.start()
        self.logger.info(f"Started log collector: {self.name}")

    def stop(self):
        """Stop the log collector."""
        if not self._is_active:
            return

        self._is_active = False
        self._stop_event.set()

        if self._collection_thread and self._collection_thread.is_alive():
            self._collection_thread.join(timeout=5.0)

        self.logger.info(f"Stopped log collector: {self.name}")

    def collect(self, log_entry: LogEntry):
        """Collect a log entry."""
        try:
            self._queue.put_nowait(log_entry)
        except queue.Full:
            self.logger.warning(f"Log queue full for collector {self.name}")

    def _collection_loop(self):
        """Main collection loop."""
        while self._is_active and not self._stop_event.is_set():
            try:
                # Process queued log entries
                while not self._queue.empty():
                    try:
                        log_entry = self._queue.get_nowait()
                        self._process_log_entry(log_entry)
                    except queue.Empty:
                        break

                # Sleep briefly to avoid busy waiting
                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")

    def _process_log_entry(self, log_entry: LogEntry):
        """Process a collected log entry."""
        # Override in subclasses for specific processing
        self.log_service._store_log_entry(log_entry)


class PerformanceLogCollector(LogCollector):
    """Collector for performance-related logs."""

    def __init__(self, log_service: "LoggingService"):
        super().__init__("Performance", log_service)
        self._performance_metrics = defaultdict(list)
        self._alert_thresholds = {
            "response_time_ms": 5000,
            "memory_usage_mb": 512,
            "cpu_usage_percent": 80,
        }

    def _process_log_entry(self, log_entry: LogEntry):
        """Process performance log entry."""
        super()._process_log_entry(log_entry)

        if log_entry.performance_data:
            # Store performance metrics
            tool_name = log_entry.tool_name
            for metric, value in log_entry.performance_data.items():
                self._performance_metrics[f"{tool_name}.{metric}"].append(
                    {"timestamp": log_entry.timestamp, "value": value}
                )

                # Check thresholds
                if metric in self._alert_thresholds:
                    threshold = self._alert_thresholds[metric]
                    if value > threshold:
                        self._trigger_performance_alert(
                            tool_name, metric, value, threshold
                        )

    def _trigger_performance_alert(
        self, tool_name: str, metric: str, value: float, threshold: float
    ):
        """Trigger performance alert."""
        alert_entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.WARNING,
            logger_name=f"NetworkConnectivity.{tool_name}",
            message=f"Performance threshold exceeded: {metric}",
            tool_name=tool_name,
            operation="performance_monitoring",
            metadata={
                "alert_type": "performance_threshold",
                "metric": metric,
                "value": value,
                "threshold": threshold,
            },
        )

        self.log_service._store_log_entry(alert_entry)


class SecurityLogCollector(LogCollector):
    """Collector for security-related logs."""

    def __init__(self, log_service: "LoggingService"):
        super().__init__("Security", log_service)
        self._security_events = deque(maxlen=1000)
        self._suspicious_patterns = [
            "failed_authentication",
            "unauthorized_access",
            "suspicious_scan",
            "malformed_request",
        ]

    def _process_log_entry(self, log_entry: LogEntry):
        """Process security log entry."""
        super()._process_log_entry(log_entry)

        # Store security events
        if log_entry.level == LogLevel.SECURITY:
            self._security_events.append(log_entry)

            # Analyze for suspicious patterns
            self._analyze_security_event(log_entry)

    def _analyze_security_event(self, log_entry: LogEntry):
        """Analyze security event for suspicious patterns."""
        message_lower = log_entry.message.lower()

        for pattern in self._suspicious_patterns:
            if pattern in message_lower:
                self._trigger_security_alert(log_entry, pattern)
                break

    def _trigger_security_alert(self, log_entry: LogEntry, pattern: str):
        """Trigger security alert."""
        alert_entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.CRITICAL,
            logger_name=log_entry.logger_name,
            message=f"Security alert: {pattern} detected",
            tool_name=log_entry.tool_name,
            operation="security_monitoring",
            metadata={
                "alert_type": "security_pattern",
                "pattern": pattern,
                "original_message": log_entry.message,
            },
        )

        self.log_service._store_log_entry(alert_entry)


class ErrorLogCollector(LogCollector):
    """Collector for error tracking and correlation."""

    def __init__(self, log_service: "LoggingService"):
        super().__init__("Error", log_service)
        self._error_patterns = defaultdict(list)
        self._correlation_window = timedelta(minutes=5)

    def _process_log_entry(self, log_entry: LogEntry):
        """Process error log entry."""
        super()._process_log_entry(log_entry)

        if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            # Store error for pattern analysis
            error_key = f"{log_entry.tool_name}.{log_entry.operation}"
            self._error_patterns[error_key].append(log_entry)

            # Correlate related errors
            self._correlate_errors(log_entry)

    def _correlate_errors(self, log_entry: LogEntry):
        """Correlate related errors."""
        if not log_entry.correlation_id:
            return

        # Find related errors within time window
        cutoff_time = log_entry.timestamp - self._correlation_window
        related_errors = []

        for errors in self._error_patterns.values():
            for error in errors:
                if (
                    error.correlation_id == log_entry.correlation_id
                    and error.timestamp >= cutoff_time
                ):
                    related_errors.append(error)

        if len(related_errors) > 1:
            self._create_error_correlation(related_errors)

    def _create_error_correlation(self, related_errors: List[LogEntry]):
        """Create error correlation entry."""
        correlation_entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.WARNING,
            logger_name="NetworkConnectivity.ErrorCorrelation",
            message=f"Correlated {len(related_errors)} related errors",
            tool_name="ErrorCorrelation",
            operation="error_correlation",
            metadata={
                "correlation_type": "error_pattern",
                "error_count": len(related_errors),
                "correlation_id": related_errors[0].correlation_id,
                "tools_affected": list(
                    set(e.tool_name for e in related_errors)
                ),
            },
        )

        self.log_service._store_log_entry(correlation_entry)


class LogFormatter:
    """Log formatters for different output formats."""

    @staticmethod
    def format_json(log_entry: LogEntry) -> str:
        """Format log entry as JSON."""
        entry_dict = asdict(log_entry)
        entry_dict["timestamp"] = log_entry.timestamp.isoformat()
        entry_dict["level"] = log_entry.level.value
        return json.dumps(entry_dict, ensure_ascii=False)

    @staticmethod
    def format_plain(log_entry: LogEntry) -> str:
        """Format log entry as plain text."""
        timestamp = log_entry.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level = log_entry.level.value.ljust(8)
        tool = log_entry.tool_name.ljust(15)

        message = f"{timestamp} {level} {tool} {log_entry.message}"

        if log_entry.operation:
            message += f" [op:{log_entry.operation}]"

        if log_entry.correlation_id:
            message += f" [corr:{log_entry.correlation_id[:8]}]"

        return message

    @staticmethod
    def format_csv(log_entry: LogEntry) -> str:
        """Format log entry as CSV."""
        fields = [
            log_entry.timestamp.isoformat(),
            log_entry.level.value,
            log_entry.tool_name,
            log_entry.operation or "",
            log_entry.message.replace('"', '""'),  # Escape quotes
            log_entry.correlation_id or "",
            json.dumps(log_entry.metadata) if log_entry.metadata else "",
        ]

        return ",".join(f'"{field}"' for field in fields)


class LogHandler:
    """Base class for log handlers."""

    def __init__(
        self, name: str, formatter: LogFormatter, log_filter: LogFilter
    ):
        self.name = name
        self.formatter = formatter
        self.log_filter = log_filter
        self.logger = get_network_logging_manager().get_tool_logger(
            f"LogHandler.{name}"
        )

    def should_handle(self, log_entry: LogEntry) -> bool:
        """Check if this handler should process the log entry."""
        # Level filtering
        level_values = {level: i for i, level in enumerate(LogLevel)}
        entry_level_value = level_values[log_entry.level]
        min_level_value = level_values[self.log_filter.min_level]
        max_level_value = level_values[self.log_filter.max_level]

        if not (min_level_value <= entry_level_value <= max_level_value):
            return False

        # Tool filtering
        if (
            self.log_filter.tools
            and log_entry.tool_name not in self.log_filter.tools
        ):
            return False

        # Operation filtering
        if (
            self.log_filter.operations
            and log_entry.operation
            and log_entry.operation not in self.log_filter.operations
        ):
            return False

        # Time filtering
        if (
            self.log_filter.start_time
            and log_entry.timestamp < self.log_filter.start_time
        ):
            return False

        if (
            self.log_filter.end_time
            and log_entry.timestamp > self.log_filter.end_time
        ):
            return False

        # Keyword filtering
        if self.log_filter.keywords:
            message_lower = log_entry.message.lower()
            if not any(
                keyword.lower() in message_lower
                for keyword in self.log_filter.keywords
            ):
                return False

        # Correlation ID filtering
        if (
            self.log_filter.correlation_ids
            and log_entry.correlation_id
            and log_entry.correlation_id not in self.log_filter.correlation_ids
        ):
            return False

        return True

    def handle(self, log_entry: LogEntry):
        """Handle the log entry."""
        if self.should_handle(log_entry):
            self._write_log(log_entry)

    def _write_log(self, log_entry: LogEntry):
        """Write the log entry (override in subclasses)."""
        pass


class FileLogHandler(LogHandler):
    """File-based log handler with rotation."""

    def __init__(
        self,
        name: str,
        file_path: str,
        formatter: LogFormatter,
        log_filter: LogFilter,
        rotation_policy: LogRotationPolicy,
        max_size_mb: int = 100,
        max_files: int = 10,
    ):
        super().__init__(name, formatter, log_filter)
        self.file_path = Path(file_path)
        self.rotation_policy = rotation_policy
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_files = max_files
        self._lock = threading.Lock()

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_log(self, log_entry: LogEntry):
        """Write log entry to file."""
        with self._lock:
            try:
                # Check if rotation is needed
                if self._should_rotate():
                    self._rotate_logs()

                # Format and write log entry
                formatted_entry = self.formatter.format_json(log_entry)

                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(formatted_entry + "\n")

            except Exception as e:
                self.logger.error(f"Failed to write log entry: {e}")

    def _should_rotate(self) -> bool:
        """Check if log rotation is needed."""
        if not self.file_path.exists():
            return False

        if self.rotation_policy in [
            LogRotationPolicy.SIZE_BASED,
            LogRotationPolicy.COMBINED,
        ]:
            if self.file_path.stat().st_size >= self.max_size_bytes:
                return True

        # Add time-based rotation logic here if needed

        return False

    def _rotate_logs(self):
        """Rotate log files."""
        try:
            # Move existing files
            for i in range(self.max_files - 1, 0, -1):
                old_file = self.file_path.with_suffix(f".{i}.gz")
                new_file = self.file_path.with_suffix(f".{i + 1}.gz")

                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)

            # Compress current log file
            if self.file_path.exists():
                compressed_file = self.file_path.with_suffix(".1.gz")
                with open(self.file_path, "rb") as f_in:
                    with gzip.open(compressed_file, "wb") as f_out:
                        f_out.writelines(f_in)

                # Remove original file
                self.file_path.unlink()

            self.logger.info(f"Rotated log files for {self.name}")

        except Exception as e:
            self.logger.error(f"Failed to rotate logs: {e}")


class DatabaseLogHandler(LogHandler):
    """Database-based log handler (placeholder for future implementation)."""

    def __init__(
        self,
        name: str,
        connection_string: str,
        formatter: LogFormatter,
        log_filter: LogFilter,
    ):
        super().__init__(name, formatter, log_filter)
        self.connection_string = connection_string
        # Database implementation would go here

    def _write_log(self, log_entry: LogEntry):
        """Write log entry to database."""
        # Database implementation would go here
        pass


class LoggingService:
    """Advanced logging service for network connectivity tools."""

    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            "LoggingService"
        )

        # Threading
        self._lock = threading.RLock()

        # Log storage
        self._log_entries: deque = deque(maxlen=10000)
        self._log_index: Dict[str, List[LogEntry]] = defaultdict(list)

        # Collectors
        self._collectors: Dict[str, LogCollector] = {}

        # Handlers
        self._handlers: Dict[str, LogHandler] = {}

        # Analytics
        self._analytics_data: Dict[str, Any] = defaultdict(dict)

        # Configuration
        self._config = {
            "max_memory_entries": 10000,
            "enable_analytics": True,
            "enable_correlation": True,
            "correlation_window_minutes": 5,
        }

        # Initialize
        self._initialize()

    def _initialize(self):
        """Initialize the logging service."""
        try:
            # Create default collectors
            self._collectors["performance"] = PerformanceLogCollector(self)
            self._collectors["security"] = SecurityLogCollector(self)
            self._collectors["error"] = ErrorLogCollector(self)

            # Create default handlers
            self._create_default_handlers()

            # Start collectors
            for collector in self._collectors.values():
                collector.start()

            self.logger.info("Logging service initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize logging service: {e}")
            raise

    def _create_default_handlers(self):
        """Create default log handlers."""
        # JSON file handler for all logs
        json_filter = LogFilter(min_level=LogLevel.DEBUG)
        json_formatter = LogFormatter()

        self._handlers["json_file"] = FileLogHandler(
            name="json_file",
            file_path="logs/network_connectivity/all_logs.jsonl",
            formatter=json_formatter,
            log_filter=json_filter,
            rotation_policy=LogRotationPolicy.SIZE_BASED,
            max_size_mb=50,
            max_files=5,
        )

        # Error file handler
        error_filter = LogFilter(min_level=LogLevel.ERROR)

        self._handlers["error_file"] = FileLogHandler(
            name="error_file",
            file_path="logs/network_connectivity/errors.jsonl",
            formatter=json_formatter,
            log_filter=error_filter,
            rotation_policy=LogRotationPolicy.SIZE_BASED,
            max_size_mb=25,
            max_files=10,
        )

        # Security file handler
        security_filter = LogFilter(
            min_level=LogLevel.SECURITY, max_level=LogLevel.SECURITY
        )

        self._handlers["security_file"] = FileLogHandler(
            name="security_file",
            file_path="logs/network_connectivity/security.jsonl",
            formatter=json_formatter,
            log_filter=security_filter,
            rotation_policy=LogRotationPolicy.SIZE_BASED,
            max_size_mb=25,
            max_files=10,
        )

    def log_structured(
        self,
        level: LogLevel,
        tool_name: str,
        message: str,
        operation: str = None,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        correlation_id: str = None,
        session_id: str = None,
        user_id: str = None,
        performance_data: Dict[str, Any] = None,
        error_data: Dict[str, Any] = None,
    ):
        """Log a structured entry.

        Args:
            level: Log level
            tool_name: Name of the tool generating the log
            message: Log message
            operation: Operation being performed
            context: Additional context data
            metadata: Metadata about the log entry
            correlation_id: Correlation ID for related operations
            session_id: Session ID
            user_id: User ID
            performance_data: Performance metrics
            error_data: Error details
        """
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            logger_name=f"NetworkConnectivity.{tool_name}",
            message=message,
            tool_name=tool_name,
            operation=operation,
            context=context or {},
            metadata=metadata or {},
            correlation_id=correlation_id,
            session_id=session_id,
            user_id=user_id,
            performance_data=performance_data or {},
            error_data=error_data or {},
        )

        self._process_log_entry(log_entry)

    def _process_log_entry(self, log_entry: LogEntry):
        """Process a log entry through the logging pipeline."""
        with self._lock:
            # Store in memory
            self._store_log_entry(log_entry)

            # Send to collectors
            for collector in self._collectors.values():
                try:
                    collector.collect(log_entry)
                except Exception as e:
                    self.logger.error(
                        f"Error in collector {collector.name}: {e}"
                    )

            # Send to handlers
            for handler in self._handlers.values():
                try:
                    handler.handle(log_entry)
                except Exception as e:
                    self.logger.error(f"Error in handler {handler.name}: {e}")

            # Update analytics
            if self._config["enable_analytics"]:
                self._update_analytics(log_entry)

    def _store_log_entry(self, log_entry: LogEntry):
        """Store log entry in memory."""
        self._log_entries.append(log_entry)

        # Index by tool name
        self._log_index[log_entry.tool_name].append(log_entry)

        # Index by correlation ID if present
        if log_entry.correlation_id:
            self._log_index[f"corr:{log_entry.correlation_id}"].append(
                log_entry
            )

    def _update_analytics(self, log_entry: LogEntry):
        """Update analytics data."""
        tool_name = log_entry.tool_name
        level = log_entry.level.value

        # Count by tool and level
        if tool_name not in self._analytics_data:
            self._analytics_data[tool_name] = defaultdict(int)

        self._analytics_data[tool_name][f"{level}_count"] += 1
        self._analytics_data[tool_name]["total_count"] += 1

        # Track performance metrics
        if log_entry.performance_data:
            perf_key = f"{tool_name}_performance"
            if perf_key not in self._analytics_data:
                self._analytics_data[perf_key] = defaultdict(list)

            for metric, value in log_entry.performance_data.items():
                self._analytics_data[perf_key][metric].append(
                    {
                        "timestamp": log_entry.timestamp.isoformat(),
                        "value": value,
                    }
                )

    def search_logs(
        self, log_filter: LogFilter, limit: int = 1000
    ) -> List[LogEntry]:
        """Search logs with filtering.

        Args:
            log_filter: Filter criteria
            limit: Maximum number of results

        Returns:
            List of matching log entries
        """
        with self._lock:
            results = []

            for log_entry in reversed(self._log_entries):
                if len(results) >= limit:
                    break

                # Apply filters
                if self._matches_filter(log_entry, log_filter):
                    results.append(log_entry)

            return results

    def _matches_filter(
        self, log_entry: LogEntry, log_filter: LogFilter
    ) -> bool:
        """Check if log entry matches filter criteria."""
        # Level filtering
        level_values = {level: i for i, level in enumerate(LogLevel)}
        entry_level_value = level_values[log_entry.level]
        min_level_value = level_values[log_filter.min_level]
        max_level_value = level_values[log_filter.max_level]

        if not (min_level_value <= entry_level_value <= max_level_value):
            return False

        # Tool filtering
        if log_filter.tools and log_entry.tool_name not in log_filter.tools:
            return False

        # Operation filtering
        if (
            log_filter.operations
            and log_entry.operation
            and log_entry.operation not in log_filter.operations
        ):
            return False

        # Time filtering
        if (
            log_filter.start_time
            and log_entry.timestamp < log_filter.start_time
        ):
            return False

        if log_filter.end_time and log_entry.timestamp > log_filter.end_time:
            return False

        # Keyword filtering
        if log_filter.keywords:
            message_lower = log_entry.message.lower()
            if not any(
                keyword.lower() in message_lower
                for keyword in log_filter.keywords
            ):
                return False

        # Correlation ID filtering
        if (
            log_filter.correlation_ids
            and log_entry.correlation_id
            and log_entry.correlation_id not in log_filter.correlation_ids
        ):
            return False

        return True

    def get_analytics(self, tool_name: str = None) -> Dict[str, Any]:
        """Get analytics data.

        Args:
            tool_name: Specific tool name (all tools if None)

        Returns:
            Analytics data dictionary
        """
        with self._lock:
            if tool_name:
                return dict(self._analytics_data.get(tool_name, {}))
            else:
                return dict(self._analytics_data)

    def export_logs(
        self,
        file_path: str,
        log_filter: LogFilter,
        format_type: LogFormat = LogFormat.JSON,
    ) -> bool:
        """Export logs to file.

        Args:
            file_path: Export file path
            log_filter: Filter criteria
            format_type: Export format

        Returns:
            True if exported successfully
        """
        try:
            logs = self.search_logs(log_filter, limit=100000)

            with open(file_path, "w", encoding="utf-8") as f:
                if format_type == LogFormat.JSON:
                    for log_entry in logs:
                        f.write(LogFormatter.format_json(log_entry) + "\n")

                elif format_type == LogFormat.CSV:
                    # Write CSV header
                    header = [
                        "timestamp",
                        "level",
                        "tool_name",
                        "operation",
                        "message",
                        "correlation_id",
                        "metadata",
                    ]
                    f.write(",".join(f'"{col}"' for col in header) + "\n")

                    # Write data
                    for log_entry in logs:
                        f.write(LogFormatter.format_csv(log_entry) + "\n")

                elif format_type == LogFormat.PLAIN:
                    for log_entry in logs:
                        f.write(LogFormatter.format_plain(log_entry) + "\n")

            self.logger.info(
                f"Exported {len(logs)} log entries to {file_path}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
            return False

    def add_handler(self, name: str, handler: LogHandler):
        """Add a log handler.

        Args:
            name: Handler name
            handler: Log handler instance
        """
        with self._lock:
            self._handlers[name] = handler
            self.logger.info(f"Added log handler: {name}")

    def remove_handler(self, name: str):
        """Remove a log handler.

        Args:
            name: Handler name
        """
        with self._lock:
            if name in self._handlers:
                del self._handlers[name]
                self.logger.info(f"Removed log handler: {name}")

    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics.

        Returns:
            Dictionary with logging statistics
        """
        with self._lock:
            total_entries = len(self._log_entries)

            # Count by level
            level_counts = defaultdict(int)
            tool_counts = defaultdict(int)

            for entry in self._log_entries:
                level_counts[entry.level.value] += 1
                tool_counts[entry.tool_name] += 1

            # Calculate time range
            if self._log_entries:
                oldest = min(entry.timestamp for entry in self._log_entries)
                newest = max(entry.timestamp for entry in self._log_entries)
                time_range = (newest - oldest).total_seconds()
            else:
                oldest = newest = None
                time_range = 0

            return {
                "total_entries": total_entries,
                "level_distribution": dict(level_counts),
                "tool_distribution": dict(tool_counts),
                "time_range_seconds": time_range,
                "oldest_entry": oldest.isoformat() if oldest else None,
                "newest_entry": newest.isoformat() if newest else None,
                "active_collectors": len(self._collectors),
                "active_handlers": len(self._handlers),
                "memory_usage_entries": total_entries,
            }

    def cleanup_old_logs(self, max_age_hours: int = 24):
        """Clean up old log entries from memory.

        Args:
            max_age_hours: Maximum age of logs to keep in hours
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

            # Filter out old entries
            old_count = len(self._log_entries)
            self._log_entries = deque(
                (
                    entry
                    for entry in self._log_entries
                    if entry.timestamp >= cutoff_time
                ),
                maxlen=self._config["max_memory_entries"],
            )

            # Rebuild index
            self._log_index.clear()
            for entry in self._log_entries:
                self._log_index[entry.tool_name].append(entry)
                if entry.correlation_id:
                    self._log_index[f"corr:{entry.correlation_id}"].append(
                        entry
                    )

            removed_count = old_count - len(self._log_entries)
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old log entries")

    def shutdown(self):
        """Shutdown the logging service."""
        with self._lock:
            # Stop all collectors
            for collector in self._collectors.values():
                try:
                    collector.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping collector: {e}")

            self.logger.info("Logging service shutdown complete")


# Global instance for easy access
_logging_service = None


def get_logging_service() -> LoggingService:
    """Get global logging service instance.

    Returns:
        LoggingService instance
    """
    global _logging_service

    if _logging_service is None:
        _logging_service = LoggingService()

    return _logging_service


# Convenience functions for structured logging
def log_info(tool_name: str, message: str, **kwargs):
    """Log info message."""
    get_logging_service().log_structured(
        LogLevel.INFO, tool_name, message, **kwargs
    )


def log_warning(tool_name: str, message: str, **kwargs):
    """Log warning message."""
    get_logging_service().log_structured(
        LogLevel.WARNING, tool_name, message, **kwargs
    )


def log_error(tool_name: str, message: str, **kwargs):
    """Log error message."""
    get_logging_service().log_structured(
        LogLevel.ERROR, tool_name, message, **kwargs
    )


def log_performance(
    tool_name: str, message: str, performance_data: Dict[str, Any], **kwargs
):
    """Log performance message."""
    get_logging_service().log_structured(
        LogLevel.PERFORMANCE,
        tool_name,
        message,
        performance_data=performance_data,
        **kwargs,
    )


def log_security(tool_name: str, message: str, **kwargs):
    """Log security message."""
    get_logging_service().log_structured(
        LogLevel.SECURITY, tool_name, message, **kwargs
    )


def log_audit(tool_name: str, message: str, **kwargs):
    """Log audit message."""
    get_logging_service().log_structured(
        LogLevel.AUDIT, tool_name, message, **kwargs
    )
