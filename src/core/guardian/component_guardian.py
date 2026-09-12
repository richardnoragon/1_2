#!/usr/bin/env python3
from __future__ import annotations

"""
Enterprise GUI Component Guardian Framework

Comprehensive protection against GUI component degradation during development
iterations, preventing widget malfunction and ensuring stable interface
behavior under all conditions.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

import functools
import logging
import weakref
from contextlib import contextmanager
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

try:
    from PyQt5.QtCore import QObject, QTimer, pyqtSignal
    from PyQt5.QtWidgets import QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    class MockQObject:
        """Mock QObject for testing without Qt."""

        pass

    class MockQWidget:
        """Mock QWidget for testing without Qt."""

        def deleteLater(self):
            """Mock deleteLater method."""
            pass

        def setParent(self, parent):
            """Mock setParent method."""
            pass

    def mock_pyqt_signal(*args):
        """Mock pyqtSignal for testing without Qt."""

        def dummy_signal(*signal_args):
            pass

        return dummy_signal

    QObject = MockQObject
    QWidget = MockQWidget
    pyqtSignal = mock_pyqt_signal


class ComponentState(Enum):
    """Enumeration of component states."""

    INITIALIZING = auto()
    ACTIVE = auto()
    DEGRADED = auto()
    RECOVERING = auto()
    FAILED = auto()
    DESTROYED = auto()


class ComponentError(Exception):
    """Base exception for component errors."""

    def __init__(self, component_id: str, error_type: str, message: str):
        """Initialize component error."""
        self.component_id = component_id
        self.error_type = error_type
        self.timestamp = datetime.now()
        error_msg = f"[{component_id}] {error_type}: {message}"
        super().__init__(error_msg)


class ComponentDegradationError(ComponentError):
    """Raised when component degrades during operation."""

    pass


class ComponentRecoveryError(ComponentError):
    """Raised when component recovery fails."""

    pass


class ComponentInfo:
    """Track component information and health status."""

    def __init__(
        self, component_id: str, component_type: str, widget_ref: "weakref.ref[QWidget]"
    ):
        """Initialize component info."""
        self.component_id = component_id
        self.component_type = component_type
        self.widget_ref = widget_ref
        self.state = ComponentState.INITIALIZING
        self.created_at = datetime.now()
        self.last_health_check = datetime.now()
        self.error_count = 0
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        self.health_check_interval = timedelta(seconds=5)
        self.error_history: List[ComponentError] = []
        self.recovery_callbacks: List[Callable[[], bool]] = []
        self.destruction_callbacks: List[Callable[[], None]] = []

    def is_healthy(self) -> bool:
        """Check if component is in healthy state."""
        healthy_states = [ComponentState.ACTIVE, ComponentState.RECOVERING]
        return self.state in healthy_states

    def is_recoverable(self) -> bool:
        """Check if component can be recovered."""
        attempts_ok = self.recovery_attempts < self.max_recovery_attempts
        not_destroyed = self.state != ComponentState.DESTROYED
        return attempts_ok and not_destroyed

    def get_widget(self) -> Optional[QWidget]:
        """Get widget reference if still valid."""
        try:
            widget = self.widget_ref()
            if widget is not None:
                # Test widget validity by accessing a basic property
                _ = widget.isVisible()
                return widget
            return None
        except (RuntimeError, TypeError):
            return None

    def record_error(self, error: ComponentError):
        """Record an error for this component."""
        self.error_count += 1
        self.error_history.append(error)
        # Keep only last 10 errors
        if len(self.error_history) > 10:
            self.error_history.pop(0)


class ComponentGuardian(QObject if QT_AVAILABLE else object):
    """
    Enterprise-grade GUI component guardian providing comprehensive
    protection against widget degradation and automatic recovery.
    """

    # Signals
    componentFailed = pyqtSignal(str, str) if QT_AVAILABLE else None
    componentRecovered = pyqtSignal(str) if QT_AVAILABLE else None
    componentDestroyed = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self):
        """Initialize component guardian."""
        if QT_AVAILABLE:
            super().__init__()

        self.logger = logging.getLogger("RFU.ComponentGuardian")
        self._components: Dict[str, ComponentInfo] = {}
        self._component_counter = 0
        self._health_check_timer = QTimer() if QT_AVAILABLE else None
        self._recovery_queue: List[str] = []
        self._destruction_queue: List[str] = []

        # Configuration
        self.auto_recovery_enabled = True
        self.health_monitoring_enabled = True
        self.error_reporting_enabled = True

        self._setup_health_monitoring()

    def _setup_health_monitoring(self):
        """Setup automated health monitoring."""
        if not QT_AVAILABLE or not self._health_check_timer:
            return

        self._health_check_timer.timeout.connect(self._perform_health_checks)
        if self.health_monitoring_enabled:
            # Check every 5 seconds
            self._health_check_timer.start(5000)

    def register_component(
        self,
        widget: QWidget,
        component_type: Optional[str] = None,
        recovery_callback: Optional[Callable[[], bool]] = None,
    ) -> str:
        """
        Register a component for guardian protection.

        Args:
            widget: Widget to protect
            component_type: Type description for monitoring
            recovery_callback: Function to call for recovery

        Returns:
            str: Component ID for future reference
        """
        if not QT_AVAILABLE or widget is None:
            return ""

        try:
            self._component_counter += 1
            comp_id = f"comp_{self._component_counter}_{id(widget)}"

            # Create weak reference to prevent circular references
            widget_ref = weakref.ref(
                widget, self._component_destroyed_callback(comp_id)
            )

            # Determine component type
            if component_type is None:
                component_type = widget.__class__.__name__

            # Create component info
            info = ComponentInfo(comp_id, component_type, widget_ref)
            info.state = ComponentState.ACTIVE

            # Add recovery callback if provided
            if recovery_callback is not None:
                info.recovery_callbacks.append(recovery_callback)

            # Register component
            self._components[comp_id] = info

            self.logger.info(f"Registered component {comp_id} ({component_type})")
            return comp_id

        except Exception as e:
            self.logger.error(f"Failed to register component: {e}")
            return ""

    def _component_destroyed_callback(self, component_id: str):
        """Create callback for when component is destroyed."""

        def callback(widget_ref):
            if component_id in self._components:
                info = self._components[component_id]
                info.state = ComponentState.DESTROYED

                # Execute destruction callbacks
                for callback_func in info.destruction_callbacks:
                    try:
                        callback_func()
                    except Exception as e:
                        msg = f"Destruction callback failed for " f"{component_id}: {e}"
                        self.logger.warning(msg)

                # Emit signal
                if self.componentDestroyed:
                    self.componentDestroyed.emit(component_id)

                # Clean up after delay
                if QT_AVAILABLE:
                    cleanup_func = lambda: self._cleanup_destroyed_component(
                        component_id
                    )
                    QTimer.singleShot(1000, cleanup_func)

                self.logger.debug(f"Component {component_id} destroyed")

        return callback

    def _cleanup_destroyed_component(self, component_id: str):
        """Clean up destroyed component from registry."""
        if component_id in self._components:
            del self._components[component_id]

    @contextmanager
    def protect_operation(self, component_id: str, operation_name: str = "operation"):
        """
        Context manager for protected GUI operations.

        Args:
            component_id: Component to protect
            operation_name: Name of operation for logging
        """
        if component_id not in self._components:
            yield
            return

        info = self._components[component_id]

        try:
            # Validate component before operation
            if not self._validate_component(info):
                raise ComponentDegradationError(
                    component_id,
                    "PRE_OPERATION_CHECK",
                    f"Component invalid before {operation_name}",
                )

            yield

            # Validate component after operation
            if not self._validate_component(info):
                raise ComponentDegradationError(
                    component_id,
                    "POST_OPERATION_CHECK",
                    f"Component degraded during {operation_name}",
                )

        except ComponentDegradationError:
            self._handle_component_degradation(info, operation_name)
            raise
        except Exception as e:
            self._handle_component_error(info, operation_name, e)
            raise

    def safe_operation(
        self,
        component_id: str,
        operation: Callable[[QWidget], Any],
        fallback_value: Any = None,
    ) -> Any:
        """
        Perform safe operation on component with automatic error handling.

        Args:
            component_id: Component ID
            operation: Operation to perform
            fallback_value: Value to return on error

        Returns:
            Any: Operation result or fallback value
        """
        if component_id not in self._components:
            self.logger.warning(f"Component {component_id} not registered")
            return fallback_value

        info = self._components[component_id]

        try:
            with self.protect_operation(component_id, operation.__name__):
                widget = info.get_widget()
                if widget is None:
                    self.logger.warning(f"Component {component_id} widget is None")
                    return fallback_value

                return operation(widget)

        except Exception as e:
            msg = f"Safe operation failed for {component_id}: {e}"
            self.logger.error(msg)
            return fallback_value

    def _validate_component(self, info: ComponentInfo) -> bool:
        """Validate component health and functionality."""
        try:
            widget = info.get_widget()
            if widget is None:
                return False

            # Test widget validity by accessing basic properties
            try:
                _ = widget.isVisible()
                _ = widget.parent()
                _ = widget.geometry()
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    return False
                raise

            info.last_health_check = datetime.now()
            return True

        except Exception as e:
            msg = f"Component validation failed for {info.component_id}: {e}"
            self.logger.warning(msg)
            return False

    def _handle_component_degradation(self, info: ComponentInfo, operation_name: str):
        """Handle component degradation with recovery attempts."""
        try:
            error = ComponentDegradationError(
                info.component_id,
                "DEGRADATION",
                f"Component degraded during {operation_name}",
            )
            info.record_error(error)
            info.state = ComponentState.DEGRADED

            msg = f"Component {info.component_id} degraded during " f"{operation_name}"
            self.logger.warning(msg)

            # Attempt recovery if enabled and possible
            if self.auto_recovery_enabled and info.is_recoverable():
                self._attempt_component_recovery(info)
            else:
                info.state = ComponentState.FAILED
                if self.componentFailed:
                    self.componentFailed.emit(info.component_id, "DEGRADATION")

        except Exception as e:
            self.logger.error(f"Error handling component degradation: {e}")

    def _handle_component_error(
        self, info: ComponentInfo, operation_name: str, error: Exception
    ):
        """Handle component errors with comprehensive logging."""
        try:
            comp_error = ComponentError(
                info.component_id,
                "OPERATION_ERROR",
                f"Error during {operation_name}: {str(error)}",
            )
            info.record_error(comp_error)

            msg = (
                f"Component {info.component_id} error in " f"{operation_name}: {error}"
            )
            self.logger.error(msg)

            # Check if this is a critical error requiring recovery
            if self._is_critical_error(error):
                info.state = ComponentState.DEGRADED
                if self.auto_recovery_enabled and info.is_recoverable():
                    self._attempt_component_recovery(info)

        except Exception as e:
            self.logger.error(f"Error handling component error: {e}")

    def _is_critical_error(self, error: Exception) -> bool:
        """Determine if error is critical requiring recovery."""
        critical_patterns = [
            "wrapped C/C++ object",
            "QWidget: Must construct a QApplication",
            "QObject: Cannot create children",
            "underlying C/C++ object has been deleted",
        ]

        error_str = str(error)
        return any(pattern in error_str for pattern in critical_patterns)

    def _attempt_component_recovery(self, info: ComponentInfo):
        """Attempt to recover a degraded component."""
        try:
            info.state = ComponentState.RECOVERING
            info.recovery_attempts += 1

            msg = (
                f"Attempting recovery for component {info.component_id} "
                f"(attempt {info.recovery_attempts})"
            )
            self.logger.info(msg)

            # Try recovery callbacks
            recovery_success = False
            for callback in info.recovery_callbacks:
                try:
                    if callback():
                        recovery_success = True
                        break
                except Exception as e:
                    msg = f"Recovery callback failed for " f"{info.component_id}: {e}"
                    self.logger.warning(msg)

            if recovery_success:
                info.state = ComponentState.ACTIVE
                # Reset error count on successful recovery
                info.error_count = 0
                if self.componentRecovered:
                    self.componentRecovered.emit(info.component_id)
                msg = f"Component {info.component_id} recovered successfully"
                self.logger.info(msg)
            else:
                # Recovery failed
                max_attempts = info.max_recovery_attempts
                if info.recovery_attempts >= max_attempts:
                    info.state = ComponentState.FAILED
                    if self.componentFailed:
                        self.componentFailed.emit(info.component_id, "RECOVERY_FAILED")
                    msg = (
                        f"Component {info.component_id} recovery " f"failed permanently"
                    )
                    self.logger.error(msg)
                else:
                    # Schedule retry
                    self._schedule_recovery_retry(info)

        except Exception as e:
            self.logger.error(f"Error during component recovery: {e}")
            info.state = ComponentState.FAILED

    def _schedule_recovery_retry(self, info: ComponentInfo):
        """Schedule recovery retry with exponential backoff."""
        if not QT_AVAILABLE:
            return

        # Max 30 seconds delay
        base_delay = 1000 * (2**info.recovery_attempts)
        retry_delay = min(base_delay, 30000)

        recovery_func = lambda: self._attempt_component_recovery(info)
        QTimer.singleShot(retry_delay, recovery_func)

        msg = f"Scheduled recovery retry for {info.component_id} " f"in {retry_delay}ms"
        self.logger.info(msg)

    def _perform_health_checks(self):
        """Perform periodic health checks on all components."""
        try:
            current_time = datetime.now()
            components_to_check = []

            for component_id, info in self._components.items():
                time_since_check = current_time - info.last_health_check
                interval_passed = time_since_check >= info.health_check_interval
                if info.is_healthy() and interval_passed:
                    components_to_check.append(info)

            for info in components_to_check:
                try:
                    if not self._validate_component(info):
                        msg = f"Health check failed for {info.component_id}"
                        self.logger.warning(msg)
                        info.state = ComponentState.DEGRADED
                        if self.auto_recovery_enabled and info.is_recoverable():
                            self._attempt_component_recovery(info)
                except Exception as e:
                    msg = f"Health check error for {info.component_id}: {e}"
                    self.logger.error(msg)

        except Exception as e:
            self.logger.error(f"Error during health checks: {e}")

    def add_recovery_callback(
        self, component_id: str, callback: Callable[[], bool]
    ) -> bool:
        """
        Add recovery callback for a component.

        Args:
            component_id: Component ID
            callback: Recovery function that returns True if successful

        Returns:
            bool: True if callback was added
        """
        try:
            if component_id in self._components:
                callbacks = self._components[component_id].recovery_callbacks
                callbacks.append(callback)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to add recovery callback: {e}")
            return False

    def add_destruction_callback(
        self, component_id: str, callback: Callable[[], None]
    ) -> bool:
        """
        Add destruction callback for a component.

        Args:
            component_id: Component ID
            callback: Cleanup function to call on destruction

        Returns:
            bool: True if callback was added
        """
        try:
            if component_id in self._components:
                callbacks = self._components[component_id].destruction_callbacks
                callbacks.append(callback)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to add destruction callback: {e}")
            return False

    def force_component_recovery(self, component_id: str) -> bool:
        """
        Force recovery attempt for a specific component.

        Args:
            component_id: Component to recover

        Returns:
            bool: True if recovery was attempted
        """
        try:
            if component_id not in self._components:
                return False

            info = self._components[component_id]
            if info.is_recoverable():
                self._attempt_component_recovery(info)
                return True
            return False

        except Exception as e:
            msg = f"Failed to force recovery for {component_id}: {e}"
            self.logger.error(msg)
            return False

    def get_component_status(self, component_id: str) -> Dict[str, Any]:
        """
        Get comprehensive status information for a component.

        Args:
            component_id: Component ID

        Returns:
            Dict: Status information
        """
        if component_id not in self._components:
            return {"error": "Component not found"}

        info = self._components[component_id]
        widget = info.get_widget()

        return {
            "component_id": component_id,
            "component_type": info.component_type,
            "state": info.state.name,
            "is_healthy": info.is_healthy(),
            "is_recoverable": info.is_recoverable(),
            "widget_valid": widget is not None,
            "error_count": info.error_count,
            "recovery_attempts": info.recovery_attempts,
            "created_at": info.created_at.isoformat(),
            "last_health_check": info.last_health_check.isoformat(),
            "recent_errors": [
                {
                    "type": err.error_type,
                    "message": str(err),
                    "timestamp": err.timestamp.isoformat(),
                }
                for err in info.error_history[-3:]  # Last 3 errors
            ],
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        total_components = len(self._components)
        healthy_count = sum(
            1 for info in self._components.values() if info.is_healthy()
        )
        failed_count = sum(
            1
            for info in self._components.values()
            if info.state == ComponentState.FAILED
        )
        recovering_count = sum(
            1
            for info in self._components.values()
            if info.state == ComponentState.RECOVERING
        )

        degraded_count = total_components - healthy_count - failed_count

        return {
            "total_components": total_components,
            "healthy_components": healthy_count,
            "failed_components": failed_count,
            "recovering_components": recovering_count,
            "degraded_components": degraded_count,
            "auto_recovery_enabled": self.auto_recovery_enabled,
            "health_monitoring_enabled": self.health_monitoring_enabled,
            "recovery_queue_size": len(self._recovery_queue),
            "destruction_queue_size": len(self._destruction_queue),
        }

    def enable_auto_recovery(self, enabled: bool = True):
        """Enable or disable automatic component recovery."""
        self.auto_recovery_enabled = enabled
        status = "enabled" if enabled else "disabled"
        self.logger.info(f"Auto recovery {status}")

    def enable_health_monitoring(self, enabled: bool = True):
        """Enable or disable health monitoring."""
        self.health_monitoring_enabled = enabled

        if QT_AVAILABLE and self._health_check_timer:
            if enabled:
                self._health_check_timer.start(5000)
            else:
                self._health_check_timer.stop()

        status = "enabled" if enabled else "disabled"
        self.logger.info(f"Health monitoring {status}")

    def emergency_recovery_all(self):
        """Perform emergency recovery for all degraded components."""
        try:
            degraded_states = [ComponentState.DEGRADED, ComponentState.FAILED]
            degraded_components = [
                info
                for info in self._components.values()
                if info.state in degraded_states and info.is_recoverable()
            ]

            if not degraded_components:
                self.logger.info("No components require emergency recovery")
                return

            comp_count = len(degraded_components)
            msg = f"Performing emergency recovery for {comp_count} components"
            self.logger.warning(msg)

            for info in degraded_components:
                try:
                    self._attempt_component_recovery(info)
                except Exception as e:
                    msg = f"Emergency recovery failed for " f"{info.component_id}: {e}"
                    self.logger.error(msg)

        except Exception as e:
            self.logger.error(f"Error during emergency recovery: {e}")

    def cleanup_all_components(self):
        """Clean up all registered components."""
        try:
            if self._health_check_timer:
                self._health_check_timer.stop()

            component_ids = list(self._components.keys())
            for component_id in component_ids:
                try:
                    info = self._components[component_id]
                    widget = info.get_widget()
                    if widget:
                        widget.deleteLater()
                except Exception as e:
                    msg = f"Error cleaning up component {component_id}: {e}"
                    self.logger.warning(msg)

            self._components.clear()
            self.logger.info("All components cleaned up")

        except Exception as e:
            self.logger.error(f"Error during component cleanup: {e}")


def gui_protected(recovery_callback: Optional[Callable[[], bool]] = None):
    """
    Decorator for protecting GUI component methods against degradation.

    Args:
        recovery_callback: Optional recovery function
    """

    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            # Get component guardian
            guardian = get_component_guardian()

            # Register component if not already registered
            component_id = getattr(self, "_guardian_component_id", None)
            if not component_id and hasattr(self, "__class__"):
                if QT_AVAILABLE and isinstance(self, QWidget):
                    component_id = guardian.register_component(
                        self, self.__class__.__name__, recovery_callback
                    )
                    self._guardian_component_id = component_id

            if component_id:
                try:
                    with guardian.protect_operation(component_id, method.__name__):
                        return method(self, *args, **kwargs)
                except Exception as e:
                    logger = logging.getLogger("RFU.ComponentGuardian")
                    msg = f"Protected method {method.__name__} failed: {e}"
                    logger.error(msg)
                    raise
            else:
                # No component protection available, execute normally
                return method(self, *args, **kwargs)

        return wrapper

    return decorator


def safe_gui_operation(operation: Callable[[], Any], fallback_value: Any = None) -> Any:
    """
    Execute GUI operation with protection against Qt object lifecycle issues.

    Args:
        operation: Operation to execute
        fallback_value: Value to return on error

    Returns:
        Any: Operation result or fallback value
    """
    try:
        return operation()
    except RuntimeError as e:
        if "wrapped C/C++ object" in str(e):
            logger = logging.getLogger("RFU.ComponentGuardian")
            logger.warning(f"Qt object deleted during operation: {e}")
            return fallback_value
        raise
    except Exception as e:
        logger = logging.getLogger("RFU.ComponentGuardian")
        logger.error(f"GUI operation failed: {e}")
        return fallback_value


# Global instance
_global_component_guardian: Optional["ComponentGuardian"] = None


def get_component_guardian() -> ComponentGuardian:
    """Get global component guardian instance."""
    global _global_component_guardian
    if _global_component_guardian is None:
        _global_component_guardian = ComponentGuardian()
    return _global_component_guardian


def register_gui_component(
    widget: QWidget,
    component_type: Optional[str] = None,
    recovery_callback: Optional[Callable[[], bool]] = None,
    **kwargs: Any,
) -> str:
    """Convenience function for component registration.

    Compatibility shim: older call sites pass ``tool_id`` while newer code uses
    ``component_type``. Both are accepted here and normalized to the guardian
    contract.
    """
    if component_type is None:
        component_type = kwargs.get("tool_id")
    if recovery_callback is None:
        recovery_callback = kwargs.get("recovery_callback")
    return get_component_guardian().register_component(
        widget, component_type, recovery_callback
    )


def protected_gui_operation(
    component_id: str, operation: Callable[[QWidget], Any], fallback_value: Any = None
) -> Any:
    """Convenience function for protected GUI operations."""
    return get_component_guardian().safe_operation(
        component_id, operation, fallback_value
    )
