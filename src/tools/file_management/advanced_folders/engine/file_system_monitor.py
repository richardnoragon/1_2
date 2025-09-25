"""File System Monitoring and Watching Implementation.

Enterprise-grade file system monitoring with efficient event handling,
debouncing, and intelligent index updates for real-time file tracking.

Features:
- Real-time file system event monitoring
- Intelligent event debouncing and filtering
- Batch processing of file system changes
- Thread-safe operations with event queuing
- Configurable monitoring depth and filters
- Integration with search index updates
"""

import logging
import os
import queue
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock, Timer
from typing import Any, Callable, Dict, List, Optional, Set

from PyQt5.QtCore import QObject, QThread, pyqtSignal

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None


class FileChangeType(Enum):
    """Types of file system changes."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileSystemMonitorConfig:
    """Configuration for file system monitoring."""

    # Monitoring behavior
    enable_recursive_monitoring: bool = True
    monitor_file_changes: bool = True
    monitor_directory_changes: bool = True

    # Performance tuning
    debounce_delay_seconds: float = 0.5
    batch_processing_interval: float = 2.0
    max_events_per_batch: int = 1000

    # Filtering
    ignore_patterns: List[str] = field(
        default_factory=lambda: [
            "*.tmp",
            "*.temp",
            "*.log",
            "*~",
            ".DS_Store",
            "Thumbs.db",
        ]
    )
    ignore_directories: List[str] = field(
        default_factory=lambda: [
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            ".vscode",
        ]
    )

    # Resource limits
    max_monitored_paths: int = 100
    max_queue_size: int = 10000

    # Error handling
    retry_failed_paths: bool = True
    max_retries: int = 3
    retry_delay_seconds: float = 5.0


@dataclass
class FileChangeEvent:
    """Represents a file system change event."""

    event_id: str
    change_type: FileChangeType
    file_path: str
    old_path: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    file_size: Optional[int] = None
    is_directory: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"event_{int(self.timestamp * 1000000)}"


@dataclass
class MonitoringStats:
    """Statistics for file system monitoring."""

    total_events_processed: int = 0
    events_by_type: Dict[str, int] = field(
        default_factory=lambda: {
            "created": 0,
            "modified": 0,
            "deleted": 0,
            "moved": 0,
        }
    )
    monitored_paths_count: int = 0
    active_watchers: int = 0
    debounced_events: int = 0
    batch_processed_events: int = 0
    errors_count: int = 0
    last_activity: Optional[float] = None

    def update_event_processed(self, change_type: FileChangeType):
        """Update statistics when an event is processed."""
        self.total_events_processed += 1
        self.events_by_type[change_type.value] += 1
        self.last_activity = time.time()


class FileSystemEventProcessor(FileSystemEventHandler):
    """Handles file system events from watchdog."""

    def __init__(self, monitor_manager, config: FileSystemMonitorConfig):
        """Initialize event processor.

        Args:
            monitor_manager: Parent monitoring manager
            config: Monitor configuration
        """
        super().__init__()
        self.monitor_manager = monitor_manager
        self.config = config
        self.logger = logging.getLogger("FileSystemMonitor.EventProcessor")

    def on_created(self, event):
        """Handle file/directory creation events."""
        if self._should_process_event(event):
            change_event = self._create_change_event(
                event, FileChangeType.CREATED
            )
            self.monitor_manager.queue_event(change_event)

    def on_modified(self, event):
        """Handle file/directory modification events."""
        if self._should_process_event(event):
            change_event = self._create_change_event(
                event, FileChangeType.MODIFIED
            )
            self.monitor_manager.queue_event(change_event)

    def on_deleted(self, event):
        """Handle file/directory deletion events."""
        if self._should_process_event(event):
            change_event = self._create_change_event(
                event, FileChangeType.DELETED
            )
            self.monitor_manager.queue_event(change_event)

    def on_moved(self, event):
        """Handle file/directory move events."""
        if self._should_process_event(event):
            change_event = self._create_change_event(
                event, FileChangeType.MOVED
            )
            change_event.old_path = event.src_path
            self.monitor_manager.queue_event(change_event)

    def _should_process_event(self, event) -> bool:
        """Check if event should be processed.

        Args:
            event: File system event

        Returns:
            True if event should be processed
        """
        # Check if file monitoring is enabled
        if event.is_directory and not self.config.monitor_directory_changes:
            return False
        if not event.is_directory and not self.config.monitor_file_changes:
            return False

        # Check ignore patterns
        path = Path(event.src_path)

        # Check ignore patterns
        for pattern in self.config.ignore_patterns:
            if path.match(pattern):
                return False

        # Check ignore directories
        for ignore_dir in self.config.ignore_directories:
            if ignore_dir in path.parts:
                return False

        return True

    def _create_change_event(
        self, fs_event, change_type: FileChangeType
    ) -> FileChangeEvent:
        """Create FileChangeEvent from file system event.

        Args:
            fs_event: Original file system event
            change_type: Type of change

        Returns:
            FileChangeEvent instance
        """
        file_path = fs_event.src_path
        file_size = None

        # Get file size if file exists and is not a directory
        if not fs_event.is_directory and os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path)
            except OSError:
                pass

        return FileChangeEvent(
            event_id=f"event_{int(time.time() * 1000000)}",
            change_type=change_type,
            file_path=file_path,
            file_size=file_size,
            is_directory=fs_event.is_directory,
            metadata={
                "src_path": getattr(fs_event, "src_path", None),
                "dest_path": getattr(fs_event, "dest_path", None),
                "event_type": str(type(fs_event).__name__),
            },
        )


class EventDebouncer:
    """Debounces file system events to reduce noise."""

    def __init__(self, delay_seconds: float, callback: Callable):
        """Initialize debouncer.

        Args:
            delay_seconds: Debounce delay
            callback: Function to call with debounced events
        """
        self.delay_seconds = delay_seconds
        self.callback = callback
        self.pending_events: Dict[str, FileChangeEvent] = {}
        self.timers: Dict[str, Timer] = {}
        self.lock = Lock()
        self.logger = logging.getLogger("FileSystemMonitor.Debouncer")

    def add_event(self, event: FileChangeEvent):
        """Add event to debounce queue.

        Args:
            event: File change event
        """
        with self.lock:
            # Use file path as key for debouncing
            key = event.file_path

            # Cancel existing timer for this path
            if key in self.timers:
                self.timers[key].cancel()

            # Store/update the event
            self.pending_events[key] = event

            # Create new timer
            timer = Timer(self.delay_seconds, self._timer_callback, args=[key])
            self.timers[key] = timer
            timer.start()

    def _timer_callback(self, key: str):
        """Timer callback to process debounced event.

        Args:
            key: Event key (file path)
        """
        with self.lock:
            if key in self.pending_events:
                event = self.pending_events.pop(key)
                self.timers.pop(key, None)

                # Call the callback with the debounced event
                try:
                    self.callback(event)
                except Exception as e:
                    self.logger.error(f"Error in debounce callback: {e}")

    def flush_all(self):
        """Flush all pending events immediately."""
        with self.lock:
            # Cancel all timers
            for timer in self.timers.values():
                timer.cancel()

            # Process all pending events
            for event in self.pending_events.values():
                try:
                    self.callback(event)
                except Exception as e:
                    self.logger.error(f"Error in flush callback: {e}")

            # Clear state
            self.pending_events.clear()
            self.timers.clear()


class BatchProcessor(QThread):
    """Processes file system events in batches for efficiency."""

    events_processed = pyqtSignal(list)  # List of FileChangeEvent
    processing_error = pyqtSignal(str)  # Error message

    def __init__(self, config: FileSystemMonitorConfig, parent=None):
        """Initialize batch processor.

        Args:
            config: Monitor configuration
            parent: Parent QObject
        """
        super().__init__(parent)

        self.config = config
        self.logger = logging.getLogger("FileSystemMonitor.BatchProcessor")

        # Event queue and processing
        self.event_queue = queue.Queue(maxsize=config.max_queue_size)
        self.is_running = False
        self.stop_requested = False

    def add_event(self, event: FileChangeEvent):
        """Add event to processing queue.

        Args:
            event: File change event
        """
        try:
            self.event_queue.put(event, timeout=1.0)
        except queue.Full:
            self.logger.warning("Event queue full, dropping event")

    def run(self):
        """Main batch processing loop."""
        self.is_running = True
        self.logger.info("Batch processor started")

        while not self.stop_requested:
            try:
                batch = self._collect_batch()
                if batch:
                    self._process_batch(batch)

            except Exception as e:
                self.logger.error(f"Batch processing error: {e}")
                self.processing_error.emit(str(e))

        self.is_running = False
        self.logger.info("Batch processor stopped")

    def _collect_batch(self) -> List[FileChangeEvent]:
        """Collect a batch of events for processing.

        Returns:
            List of events to process
        """
        batch = []
        batch_timeout = self.config.batch_processing_interval
        start_time = time.time()

        while (
            len(batch) < self.config.max_events_per_batch
            and time.time() - start_time < batch_timeout
            and not self.stop_requested
        ):

            try:
                # Use shorter timeout to allow periodic stop checks
                event = self.event_queue.get(timeout=0.1)
                batch.append(event)
                self.event_queue.task_done()

            except queue.Empty:
                # No events available, continue waiting
                continue

        return batch

    def _process_batch(self, batch: List[FileChangeEvent]):
        """Process a batch of events.

        Args:
            batch: List of events to process
        """
        if not batch:
            return

        self.logger.debug(f"Processing batch of {len(batch)} events")

        try:
            # Group events by type for optimization
            events_by_type = defaultdict(list)
            for event in batch:
                events_by_type[event.change_type].append(event)

            # Emit processed events
            self.events_processed.emit(batch)

        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
            self.processing_error.emit(str(e))

    def stop_processing(self):
        """Stop the batch processor."""
        self.stop_requested = True
        if self.isRunning():
            self.wait(5000)  # Wait up to 5 seconds


class FileSystemMonitor(QObject):
    """Main file system monitoring manager.

    Coordinates file system watching, event processing, and notifications.
    """

    # Signals for external communication
    files_changed = pyqtSignal(list)  # List of FileChangeEvent
    monitoring_started = pyqtSignal(str)  # path
    monitoring_stopped = pyqtSignal(str)  # path
    monitoring_error = pyqtSignal(str, str)  # path, error
    stats_updated = pyqtSignal(object)  # MonitoringStats

    def __init__(
        self, config: Optional[FileSystemMonitorConfig] = None, parent=None
    ):
        """Initialize file system monitor.

        Args:
            config: Monitor configuration
            parent: Parent QObject
        """
        super().__init__(parent)

        self.config = config or FileSystemMonitorConfig()
        self.logger = logging.getLogger("FileSystemMonitor")

        # Check if watchdog is available
        if not WATCHDOG_AVAILABLE:
            self.logger.error(
                "Watchdog library not available for file monitoring"
            )
            raise ImportError(
                "Watchdog library required for file system monitoring"
            )

        # Monitoring state
        self.is_monitoring = False
        self.monitored_paths: Set[str] = set()
        self.observers: Dict[str, Observer] = {}
        self.event_handlers: Dict[str, FileSystemEventProcessor] = {}

        # Event processing
        self.debouncer = EventDebouncer(
            self.config.debounce_delay_seconds, self._handle_debounced_event
        )
        self.batch_processor = BatchProcessor(self.config, self)

        # Statistics
        self.stats = MonitoringStats()
        self.stats_lock = Lock()

        # Connect signals
        self.batch_processor.events_processed.connect(
            self._handle_batch_processed
        )
        self.batch_processor.processing_error.connect(
            self._handle_processing_error
        )

        self.logger.info("File system monitor initialized")

    def start_monitoring(self, paths: List[str]) -> bool:
        """Start monitoring specified paths.

        Args:
            paths: List of directory paths to monitor

        Returns:
            True if monitoring started successfully
        """
        if self.is_monitoring:
            self.logger.warning("Monitoring already active")
            return False

        if len(paths) > self.config.max_monitored_paths:
            self.logger.error(
                f"Too many paths to monitor: {len(paths)} > "
                f"{self.config.max_monitored_paths}"
            )
            return False

        self.logger.info(f"Starting monitoring for {len(paths)} paths")

        try:
            # Start batch processor
            self.batch_processor.start()

            # Start monitoring each path
            for path in paths:
                if self._start_path_monitoring(path):
                    self.monitored_paths.add(path)
                    self.monitoring_started.emit(path)

            self.is_monitoring = True
            self._update_stats()

            self.logger.info(
                f"Started monitoring {len(self.monitored_paths)} paths"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            self.stop_monitoring()
            return False

    def stop_monitoring(self):
        """Stop all file system monitoring."""
        if not self.is_monitoring:
            return

        self.logger.info("Stopping file system monitoring")

        # Stop all observers
        for path, observer in self.observers.items():
            try:
                observer.stop()
                observer.join(timeout=2.0)
                self.monitoring_stopped.emit(path)
            except Exception as e:
                self.logger.error(f"Error stopping observer for {path}: {e}")

        # Clear state
        self.observers.clear()
        self.event_handlers.clear()
        self.monitored_paths.clear()

        # Stop batch processor
        if self.batch_processor.isRunning():
            self.batch_processor.stop_processing()

        # Flush any pending debounced events
        self.debouncer.flush_all()

        self.is_monitoring = False
        self._update_stats()

        self.logger.info("File system monitoring stopped")

    def add_monitored_path(self, path: str) -> bool:
        """Add a new path to monitoring.

        Args:
            path: Directory path to monitor

        Returns:
            True if path was added successfully
        """
        if not self.is_monitoring:
            self.logger.error("Monitoring not active")
            return False

        if path in self.monitored_paths:
            self.logger.warning(f"Path already monitored: {path}")
            return True

        if len(self.monitored_paths) >= self.config.max_monitored_paths:
            self.logger.error("Maximum monitored paths reached")
            return False

        if self._start_path_monitoring(path):
            self.monitored_paths.add(path)
            self.monitoring_started.emit(path)
            self._update_stats()
            return True

        return False

    def remove_monitored_path(self, path: str) -> bool:
        """Remove a path from monitoring.

        Args:
            path: Directory path to stop monitoring

        Returns:
            True if path was removed successfully
        """
        if path not in self.monitored_paths:
            return False

        try:
            # Stop observer for this path
            if path in self.observers:
                observer = self.observers.pop(path)
                observer.stop()
                observer.join(timeout=2.0)

            # Remove handler
            if path in self.event_handlers:
                del self.event_handlers[path]

            # Remove from monitored paths
            self.monitored_paths.discard(path)
            self.monitoring_stopped.emit(path)
            self._update_stats()

            self.logger.info(f"Stopped monitoring path: {path}")
            return True

        except Exception as e:
            self.logger.error(f"Error removing monitored path {path}: {e}")
            return False

    def get_monitored_paths(self) -> List[str]:
        """Get list of currently monitored paths.

        Returns:
            List of monitored directory paths
        """
        return list(self.monitored_paths)

    def get_monitoring_stats(self) -> MonitoringStats:
        """Get current monitoring statistics.

        Returns:
            Current monitoring statistics
        """
        with self.stats_lock:
            return self.stats

    def queue_event(self, event: FileChangeEvent):
        """Queue a file system event for processing.

        Args:
            event: File change event
        """
        # Add to debouncer first
        self.debouncer.add_event(event)

    def _start_path_monitoring(self, path: str) -> bool:
        """Start monitoring a specific path.

        Args:
            path: Directory path to monitor

        Returns:
            True if monitoring started successfully
        """
        try:
            # Validate path
            path_obj = Path(path)
            if not path_obj.exists():
                self.logger.error(f"Path does not exist: {path}")
                return False

            if not path_obj.is_dir():
                self.logger.error(f"Path is not a directory: {path}")
                return False

            # Create event handler
            event_handler = FileSystemEventProcessor(self, self.config)
            self.event_handlers[path] = event_handler

            # Create and start observer
            observer = Observer()
            observer.schedule(
                event_handler,
                path,
                recursive=self.config.enable_recursive_monitoring,
            )
            observer.start()

            self.observers[path] = observer

            self.logger.debug(f"Started monitoring path: {path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start monitoring {path}: {e}")
            self.monitoring_error.emit(path, str(e))
            return False

    def _handle_debounced_event(self, event: FileChangeEvent):
        """Handle debounced file system event.

        Args:
            event: Debounced file change event
        """
        # Add to batch processor
        self.batch_processor.add_event(event)

        # Update stats
        with self.stats_lock:
            self.stats.debounced_events += 1

    def _handle_batch_processed(self, events: List[FileChangeEvent]):
        """Handle batch of processed events.

        Args:
            events: List of processed events
        """
        # Update statistics
        with self.stats_lock:
            self.stats.batch_processed_events += len(events)
            for event in events:
                self.stats.update_event_processed(event.change_type)

        # Emit processed events
        self.files_changed.emit(events)

        # Update statistics signal
        self.stats_updated.emit(self.stats)

        self.logger.debug(
            f"Processed batch of {len(events)} file system events"
        )

    def _handle_processing_error(self, error_message: str):
        """Handle batch processing error.

        Args:
            error_message: Error description
        """
        with self.stats_lock:
            self.stats.errors_count += 1

        self.logger.error(f"Event processing error: {error_message}")

    def _update_stats(self):
        """Update monitoring statistics."""
        with self.stats_lock:
            self.stats.monitored_paths_count = len(self.monitored_paths)
            self.stats.active_watchers = len(self.observers)

        self.stats_updated.emit(self.stats)

    def __del__(self):
        """Cleanup when monitor is destroyed."""
        if hasattr(self, "is_monitoring") and self.is_monitoring:
            self.stop_monitoring()
