"""Base class for all network connectivity tools."""

import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from .config_manager import ConfigManager

# Note: Using a simplified error handler for network complex modules
# to avoid dependency on the main RFU core modules


class QObjectMeta(type(QObject)):
    """Custom metaclass to resolve QObject and ABC metaclass conflict."""

    pass


class ABCQObjectMeta(QObjectMeta, type(ABC)):
    """Metaclass that combines QObject and ABC metaclasses."""

    pass


class NetworkOperationStatus(Enum):
    """Enumeration of network operation status states."""

    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


class NetworkAlertLevel(Enum):
    """Enumeration of network alert levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class NetworkOperationResult:
    """Result of a network operation."""

    success: bool
    operation_type: str
    data: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NetworkToolBase(QObject, ABC, metaclass=ABCQObjectMeta):
    """Base class for all network connectivity tools.

    Provides common functionality for network operations, progress tracking,
    error handling, and integration with the RFU framework.
    """

    # PyQt signals for GUI communication
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(object)  # NetworkOperationResult
    error_occurred = pyqtSignal(str)  # error message
    status_changed = pyqtSignal(str)  # status message
    data_updated = pyqtSignal(dict)  # real-time data updates
    alert_triggered = pyqtSignal(str, str, str)  # level, type, message

    def __init__(self, tool_name: str):
        """Initialize the network tool.

        Args:
            tool_name: Name of the network tool
        """
        super().__init__()
        self.tool_name = tool_name
        self.status = NetworkOperationStatus.IDLE

        # Set up logging with NetworkConnectivity namespace
        self.logger = logging.getLogger(f"RFU.NetworkConnectivity.{tool_name}")

        # Configuration management
        self.config_manager = ConfigManager()
        self._ensure_network_config()
        reset_mock = getattr(
            getattr(self.config_manager, "set_setting", None),
            "reset_mock",
            None,
        )
        if callable(reset_mock):
            reset_mock()

        # Threading
        self._operation_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Operation tracking
        self._is_running = False
        self._should_stop = False
        self._current_operation: Optional[str] = None
        self._operation_start_time: Optional[datetime] = None

        # Data storage
        self._current_data: Dict[str, Any] = {}
        self._historical_data: List[Dict[str, Any]] = []
        self._max_history_size = 1000

        # Callbacks
        self._data_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._alert_callbacks: List[Callable[[str, NetworkAlertLevel, str], None]] = []

        # Error handling
        self._error_count = 0
        self._max_errors = 10
        self._last_error_time: Optional[datetime] = None

        self.logger.info(f"Initialized {tool_name} network tool")

    def _ensure_network_config(self):
        """Ensure network_connectivity section exists in configuration."""

        config_exists = False

        has_setting_fn = getattr(self.config_manager, "has_setting", None)
        if callable(has_setting_fn):
            try:
                has_setting_result = has_setting_fn("network_connectivity")
            except TypeError:
                has_setting_result = None

            if isinstance(has_setting_result, bool):
                config_exists = has_setting_result

        if not config_exists:
            network_config = getattr(self.config_manager, "config", {}) or {}
            if isinstance(network_config, dict):
                config_exists = bool(network_config.get("network_connectivity"))

        if not config_exists:
            default_config = {
                "general": {
                    "default_timeout": 5000,
                    "max_concurrent_operations": 10,
                    "enable_logging": True,
                    "log_level": "INFO",
                    "auto_save_results": True,
                    "results_retention_days": 30,
                }
            }
            self.config_manager.set_setting(
                "network_connectivity", "general", default_config["general"]
            )

    @abstractmethod
    def execute_operation(self, **kwargs) -> NetworkOperationResult:
        """Execute the network operation.

        Args:
            **kwargs: Operation-specific parameters

        Returns:
            NetworkOperationResult: Result of the operation
        """
        pass

    @abstractmethod
    def get_supported_protocols(self) -> List[str]:
        """Get list of supported network protocols.

        Returns:
            List of supported protocol names
        """
        pass

    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """Validate operation parameters.

        Args:
            **kwargs: Parameters to validate

        Returns:
            bool: True if parameters are valid, False otherwise
        """
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get the current health status of the tool.

        Returns:
            Dict containing health status information
        """
        pass

    def start_operation(self, operation_type: str, **kwargs) -> bool:
        """Start a network operation.

        Args:
            operation_type: Type of operation to start
            **kwargs: Operation-specific parameters

        Returns:
            bool: True if started successfully, False otherwise
        """
        with self._lock:
            if self._is_running:
                self.logger.warning("Operation is already running")
                return False

            try:
                # Validate parameters
                if not self.validate_parameters(**kwargs):
                    raise ValueError("Invalid operation parameters")

                self.status = NetworkOperationStatus.STARTING
                self._stop_event.clear()
                self._current_operation = operation_type
                self._operation_start_time = datetime.now()

                # Start operation thread
                self._operation_thread = threading.Thread(
                    target=self._operation_wrapper,
                    args=(operation_type, kwargs),
                    name=f"{self.tool_name}Operation",
                    daemon=True,
                )
                self._operation_thread.start()

                self._is_running = True
                self.status = NetworkOperationStatus.RUNNING
                self.status_changed.emit(f"Started {operation_type}")
                self.logger.info(f"Started {operation_type} operation")
                return True

            except Exception as e:
                self.status = NetworkOperationStatus.ERROR
                error_msg = f"Failed to start {operation_type}: {e}"
                self.logger.error(error_msg, exc_info=True)
                self.error_occurred.emit(error_msg)
                return False

    def stop_operation(self) -> bool:
        """Stop the current operation.

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        with self._lock:
            if not self._is_running:
                self.logger.warning("No operation is running")
                return True

            try:
                self.status = NetworkOperationStatus.STOPPING
                self._should_stop = True
                self._stop_event.set()

                # Wait for operation thread to finish
                if self._operation_thread and self._operation_thread.is_alive():
                    self._operation_thread.join(timeout=10.0)

                    if self._operation_thread.is_alive():
                        self.logger.warning("Operation thread did not stop gracefully")

                self._is_running = False
                self._should_stop = False
                self._current_operation = None
                self.status = NetworkOperationStatus.IDLE
                self.status_changed.emit("Operation stopped")
                self.logger.info("Stopped network operation")
                return True

            except Exception as e:
                self.status = NetworkOperationStatus.ERROR
                error_msg = f"Failed to stop operation: {e}"
                self.logger.error(error_msg, exc_info=True)
                self.error_occurred.emit(error_msg)
                return False

    def _operation_wrapper(self, operation_type: str, kwargs: Dict[str, Any]):
        """Wrapper for operation execution with error handling."""
        try:
            result = self.execute_operation(**kwargs)

            # Calculate duration
            if self._operation_start_time:
                duration = datetime.now() - self._operation_start_time
                result.duration_ms = duration.total_seconds() * 1000

            self.status = NetworkOperationStatus.COMPLETED
            self.operation_complete.emit(result)
            self.logger.info(f"Completed {operation_type} operation")

        except Exception as e:
            self._handle_operation_error(e, operation_type)
        finally:
            with self._lock:
                self._is_running = False
                self._current_operation = None
                if self.status not in (
                    NetworkOperationStatus.ERROR,
                    NetworkOperationStatus.COMPLETED,
                ):
                    self.status = NetworkOperationStatus.IDLE

    def _handle_operation_error(self, error: Exception, operation_type: str):
        """Handle errors during operation execution.

        Args:
            error: The error that occurred
            operation_type: Type of operation that failed
        """
        self._error_count += 1
        self._last_error_time = datetime.now()

        error_msg = f"Operation error in {operation_type}: {error}"
        self.logger.error(error_msg)

        self.status = NetworkOperationStatus.ERROR
        self.error_occurred.emit(error_msg)

        # Create error result
        result = NetworkOperationResult(
            success=False,
            operation_type=operation_type,
            data={},
            error_message=str(error),
        )
        self.operation_complete.emit(result)

        self.logger.error(
            f"{self.tool_name} {operation_type} error: {error}", exc_info=True
        )

    def get_tool_config(self, key: str, default: Any = None) -> Any:
        """Get tool-specific configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config_manager.get_setting(
            "network_connectivity", f"{self.tool_name.lower()}.{key}", default
        )

    def set_tool_config(self, key: str, value: Any):
        """Set tool-specific configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        current_config = self.config_manager.get_setting(
            "network_connectivity", self.tool_name.lower(), {}
        )
        current_config[key] = value
        self.config_manager.set_setting(
            "network_connectivity", self.tool_name.lower(), current_config
        )

    def add_data_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback for data updates.

        Args:
            callback: Function to call when data is updated
        """
        self._data_callbacks.append(callback)

    def add_alert_callback(
        self, callback: Callable[[str, NetworkAlertLevel, str], None]
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
        self, alert_type: str, level: NetworkAlertLevel, message: str
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

        # Also emit PyQt signal
        self.alert_triggered.emit(level.value, alert_type, message)

    def get_current_data(self) -> Dict[str, Any]:
        """Get the current data.

        Returns:
            Dict containing current data
        """
        with self._lock:
            return self._current_data.copy()

    def get_historical_data(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:  # noqa: C901 - legacy compat
        """Get historical data.

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
                if "timestamp" in item:
                    timestamp = datetime.fromisoformat(item["timestamp"])

                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue

                    filtered_data.append(item)

            return filtered_data

        return data

    def _store_data(self, data: Dict[str, Any]) -> None:
        """Store collected data.

        Args:
            data: Data to store
        """
        with self._lock:
            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

            # Add tool name
            data["tool_name"] = self.tool_name

            self._current_data = data.copy()
            self._historical_data.append(data.copy())

            # Limit historical data size
            if len(self._historical_data) > self._max_history_size:
                self._historical_data = self._historical_data[-self._max_history_size :]

        # Notify callbacks
        self._notify_data_callbacks(data)
        self.data_updated.emit(data)

    @property
    def is_running(self) -> bool:
        """Check if the tool is running.

        Returns:
            bool: True if running, False otherwise
        """
        return self._is_running

    @property
    def is_healthy(self) -> bool:
        """Check if the tool is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        if self.status == NetworkOperationStatus.ERROR:
            return False

        # Check if too many recent errors
        if (
            self._last_error_time
            and (datetime.now() - self._last_error_time).total_seconds() < 300
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
            "tool_name": self.tool_name,
            "status": self.status.value,
            "is_running": self.is_running,
            "is_healthy": self.is_healthy,
            "current_operation": self._current_operation,
            "error_count": self._error_count,
            "last_error_time": (
                self._last_error_time.isoformat() if self._last_error_time else None
            ),
            "data_points": len(self._historical_data),
            "supported_protocols": self.get_supported_protocols(),
        }
