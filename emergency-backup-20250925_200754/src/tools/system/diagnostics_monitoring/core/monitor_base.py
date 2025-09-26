"""Base class for all monitoring tools in the diagnostics system."""

import logging
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

from .platform_detector import get_platform_detector
from core.error_handler import error_handler


class MonitorStatus(Enum):
    """Enumeration of monitor status states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class AlertLevel(Enum):
    """Enumeration of alert levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitorBase(ABC):
    """Base class for all system monitoring tools.

    Provides common functionality for data collection, alerting,
    and integration with the RFU framework.
    """

    def __init__(self, monitor_name: str, update_interval: float = 5.0):
        """Initialize the monitor.

        Args:
            monitor_name: Name of the monitor
            update_interval: Update interval in seconds
        """
        self.monitor_name = monitor_name
        self.update_interval = update_interval
        self.status = MonitorStatus.STOPPED

        # Set up logging
        self.logger = logging.getLogger(
            f"RFU.DiagnosticsMonitoring.{monitor_name}"
        )

        # Platform detection
        self.platform_detector = get_platform_detector()

        # Threading
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Data storage
        self._current_data: Dict[str, Any] = {}
        self._historical_data: List[Dict[str, Any]] = []
        self._max_history_size = 1000

        # Callbacks
        self._data_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._alert_callbacks: List[Callable[[str, AlertLevel, str], None]] = (
            []
        )

        # Error handling
        self._error_count = 0
        self._max_errors = 10
        self._last_error_time: Optional[datetime] = None

        self.logger.info(f"Initialized {monitor_name} monitor")

    @abstractmethod
    def _collect_data(self) -> Dict[str, Any]:
        """Collect monitoring data.

        This method must be implemented by subclasses to collect
        platform-specific monitoring data.

        Returns:
            Dict containing collected monitoring data

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _collect_data")

    @abstractmethod
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate collected data.

        Args:
            data: Data to validate

        Returns:
            bool: True if data is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement _validate_data")

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get the current health status.

        Returns:
            Dict containing health status information
        """
        raise NotImplementedError(
            "Subclasses must implement get_health_status"
        )

    def start_monitoring(self) -> bool:
        """Start the monitoring process.

        Returns:
            bool: True if started successfully, False otherwise
        """
        with self._lock:
            if self.status == MonitorStatus.RUNNING:
                self.logger.warning("Monitor is already running")
                return True

            if self.status == MonitorStatus.STARTING:
                self.logger.warning("Monitor is already starting")
                return False

            try:
                self.status = MonitorStatus.STARTING
                self._stop_event.clear()

                # Check platform support
                if not self.platform_detector.is_supported():
                    raise RuntimeError("Platform not supported")

                # Initialize platform-specific components
                self._initialize_platform_specific()

                # Start monitoring thread
                self._monitor_thread = threading.Thread(
                    target=self._monitor_loop,
                    name=f"{self.monitor_name}Monitor",
                    daemon=True,
                )
                self._monitor_thread.start()

                self.status = MonitorStatus.RUNNING
                self.logger.info(f"Started {self.monitor_name} monitoring")
                return True

            except Exception as e:
                self.status = MonitorStatus.ERROR
                self.logger.error(f"Failed to start monitoring: {e}")
                error_handler.handle_error(e, f"{self.monitor_name} start")
                return False

    def stop_monitoring(self) -> bool:
        """Stop the monitoring process.

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        with self._lock:
            if self.status == MonitorStatus.STOPPED:
                self.logger.warning("Monitor is already stopped")
                return True

            try:
                self.status = MonitorStatus.STOPPING
                self._stop_event.set()

                # Wait for monitor thread to finish
                if self._monitor_thread and self._monitor_thread.is_alive():
                    self._monitor_thread.join(timeout=10.0)

                    if self._monitor_thread.is_alive():
                        self.logger.warning(
                            "Monitor thread did not stop gracefully"
                        )

                self._cleanup_platform_specific()
                self.status = MonitorStatus.STOPPED
                self.logger.info(f"Stopped {self.monitor_name} monitoring")
                return True

            except Exception as e:
                self.status = MonitorStatus.ERROR
                self.logger.error(f"Failed to stop monitoring: {e}")
                error_handler.handle_error(e, f"{self.monitor_name} stop")
                return False

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        self.logger.debug("Starting monitor loop")

        while not self._stop_event.is_set():
            try:
                # Collect data
                data = self._collect_data()

                # Validate data
                if not self._validate_data(data):
                    self.logger.warning("Invalid data collected, skipping")
                    continue

                # Add timestamp
                data["timestamp"] = datetime.now().isoformat()
                data["monitor_name"] = self.monitor_name

                # Store data
                self._store_data(data)

                # Check for alerts
                self._check_alerts(data)

                # Notify callbacks
                self._notify_data_callbacks(data)

                # Reset error count on successful collection
                self._error_count = 0

            except Exception as e:
                self._handle_monitoring_error(e)

            # Wait for next update
            self._stop_event.wait(self.update_interval)

        self.logger.debug("Monitor loop stopped")

    def _store_data(self, data: Dict[str, Any]) -> None:
        """Store collected data.

        Args:
            data: Data to store
        """
        with self._lock:
            self._current_data = data.copy()
            self._historical_data.append(data.copy())

            # Limit historical data size
            if len(self._historical_data) > self._max_history_size:
                self._historical_data = self._historical_data[
                    -self._max_history_size :
                ]

    def _check_alerts(self, data: Dict[str, Any]) -> None:
        """Check for alert conditions.

        Args:
            data: Current monitoring data
        """
        # This is a basic implementation - subclasses should override
        # for specific alert logic
        pass

    def _handle_monitoring_error(self, error: Exception) -> None:
        """Handle errors during monitoring.

        Args:
            error: The error that occurred
        """
        self._error_count += 1
        self._last_error_time = datetime.now()

        error_msg = (
            f"Monitoring error ({self._error_count}/"
            f"{self._max_errors}): {error}"
        )
        self.logger.error(error_msg)

        # Stop monitoring if too many errors
        if self._error_count >= self._max_errors:
            self.logger.critical("Too many errors, stopping monitoring")
            self.status = MonitorStatus.ERROR
            self._stop_event.set()

        error_handler.handle_error(error, f"{self.monitor_name} monitoring")

    def _initialize_platform_specific(self) -> None:
        """Initialize platform-specific components.

        Override in subclasses for platform-specific initialization.
        """
        pass

    def _cleanup_platform_specific(self) -> None:
        """Cleanup platform-specific components.

        Override in subclasses for platform-specific cleanup.
        """
        pass

    def get_current_data(self) -> Dict[str, Any]:
        """Get the current monitoring data.

        Returns:
            Dict containing current data
        """
        with self._lock:
            return self._current_data.copy()

    def get_historical_data(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get historical monitoring data.

        Args:
            start_time: Start time for data range
            end_time: End time for data range

        Returns:
            List of historical data points
        """
        with self._lock:
            data = self._historical_data.copy()

        if start_time or end_time:
            filtered_data = []
            for item in data:
                timestamp = datetime.fromisoformat(item["timestamp"])

                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue

                filtered_data.append(item)

            return filtered_data

        return data

    def add_data_callback(
        self, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Add a callback for data updates.

        Args:
            callback: Function to call when data is updated
        """
        self._data_callbacks.append(callback)

    def add_alert_callback(
        self, callback: Callable[[str, AlertLevel, str], None]
    ) -> None:
        """Add a callback for alerts.

        Args:
            callback: Function to call when alerts are generated
        """
        self._alert_callbacks.append(callback)

    def _notify_data_callbacks(self, data: Dict[str, Any]) -> None:
        """Notify all data callbacks.

        Args:
            data: Data to send to callbacks
        """
        for callback in self._data_callbacks:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in data callback: {e}")

    def _notify_alert_callbacks(
        self, alert_type: str, level: AlertLevel, message: str
    ) -> None:
        """Notify all alert callbacks.

        Args:
            alert_type: Type of alert
            level: Alert level
            message: Alert message
        """
        for callback in self._alert_callbacks:
            try:
                callback(alert_type, level, message)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")

    @property
    def is_running(self) -> bool:
        """Check if the monitor is running.

        Returns:
            bool: True if running, False otherwise
        """
        return self.status == MonitorStatus.RUNNING

    @property
    def is_healthy(self) -> bool:
        """Check if the monitor is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        if self.status == MonitorStatus.ERROR:
            return False

        # Check if too many recent errors
        if (
            self._last_error_time
            and datetime.now() - self._last_error_time < timedelta(minutes=5)
            and self._error_count > 3
        ):
            return False

        return True

    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information.

        Returns:
            Dict containing status information
        """
        return {
            "monitor_name": self.monitor_name,
            "status": self.status.value,
            "is_running": self.is_running,
            "is_healthy": self.is_healthy,
            "update_interval": self.update_interval,
            "error_count": self._error_count,
            "last_error_time": (
                self._last_error_time.isoformat()
                if self._last_error_time
                else None
            ),
            "data_points": len(self._historical_data),
            "platform": self.platform_detector.platform.value,
        }
