"""
Widget Lifecycle Management for RFU File Explorer

This module provides comprehensive Qt widget lifecycle management to prevent
"wrapped C/C++ object has been deleted" errors and ensure proper memory cleanup.

Author: RFU Development Team
Version: 1.0.0
"""

import logging
import weakref
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Set

try:
    from PyQt5.QtCore import QObject, QTimer, pyqtSignal
    from PyQt5.QtWidgets import QLabel, QLayout, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Mock classes for testing without Qt
    class QObject:
        pass

    class QWidget:
        def deleteLater(self):
            pass

        def setParent(self, parent):
            pass

        def findChildren(self, type_class):
            return []

    class QLabel(QWidget):
        def setText(self, text):
            pass

    class QLayout:
        def removeWidget(self, widget):
            pass

        def removeItem(self, item):
            pass

    class QTimer:
        def stop(self):
            pass

        def start(self, interval):
            pass


class WidgetLifecycleError(Exception):
    """Exception raised when widget lifecycle operations fail."""

    pass


class WidgetState:
    """Track the state of a widget throughout its lifecycle."""

    def __init__(
        self, widget_id: str, widget_ref: "weakref.ref", widget_type: str
    ):
        self.widget_id = widget_id
        self.widget_ref = widget_ref
        self.widget_type = widget_type
        self.created_at = datetime.now()
        self.destroyed_at: Optional[datetime] = None
        self.parent_id: Optional[str] = None
        self.children_ids: Set[str] = set()
        self.is_being_destroyed = False
        self.cleanup_callbacks: list[Callable[[], None]] = []

    def is_valid(self) -> bool:
        """Check if the widget reference is still valid."""
        return self.widget_ref() is not None and not self.is_being_destroyed

    def get_widget(self) -> Optional[QWidget]:
        """Get the widget if it's still valid."""
        if self.is_valid():
            return self.widget_ref()
        return None

    def mark_destroying(self):
        """Mark widget as being destroyed."""
        self.is_being_destroyed = True
        self.destroyed_at = datetime.now()


class WidgetLifecycleManager:
    """
    Comprehensive widget lifecycle management system.

    Features:
    - Automatic widget registration and tracking
    - Parent-child relationship management
    - Safe widget destruction with proper cleanup order
    - Memory leak prevention
    - Defensive programming against deleted objects
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._widgets: Dict[str, WidgetState] = {}
        self._widget_counter = 0
        self._destruction_queue: list[str] = []
        self._cleanup_timer = QTimer() if QT_AVAILABLE else None
        self._setup_cleanup_timer()

    def _setup_cleanup_timer(self):
        """Setup periodic cleanup timer."""
        if QT_AVAILABLE and self._cleanup_timer:
            self._cleanup_timer.timeout.connect(self._periodic_cleanup)
            self._cleanup_timer.start(5000)  # Cleanup every 5 seconds

    def register_widget(
        self, widget: QWidget, widget_type: str = None, parent_id: str = None
    ) -> str:
        """
        Register a widget for lifecycle management.

        Args:
            widget: Widget to register
            widget_type: Type description for logging
            parent_id: ID of parent widget if any

        Returns:
            str: Unique widget ID
        """
        if not QT_AVAILABLE or widget is None:
            return ""

        try:
            self._widget_counter += 1
            widget_id = f"widget_{self._widget_counter}_{id(widget)}"

            # Create weak reference to avoid circular references
            widget_ref = weakref.ref(
                widget, self._widget_destroyed_callback(widget_id)
            )

            # Determine widget type
            if widget_type is None:
                widget_type = widget.__class__.__name__

            # Create widget state
            state = WidgetState(widget_id, widget_ref, widget_type)
            state.parent_id = parent_id

            # Register widget
            self._widgets[widget_id] = state

            # Update parent-child relationships
            if parent_id and parent_id in self._widgets:
                self._widgets[parent_id].children_ids.add(widget_id)

            self.logger.debug(f"Registered widget {widget_id} ({widget_type})")
            return widget_id

        except Exception as e:
            self.logger.error(f"Failed to register widget: {e}")
            return ""

    def _widget_destroyed_callback(self, widget_id: str):
        """Create callback for when widget is destroyed."""

        def callback(widget_ref):
            if widget_id in self._widgets:
                self._widgets[widget_id].mark_destroying()
                self.logger.debug(f"Widget {widget_id} was destroyed")

        return callback

    def unregister_widget(self, widget_id: str) -> bool:
        """
        Unregister a widget from lifecycle management.

        Args:
            widget_id: Widget ID to unregister

        Returns:
            bool: True if successfully unregistered
        """
        try:
            if widget_id not in self._widgets:
                return False

            state = self._widgets[widget_id]

            # Remove from parent's children
            if state.parent_id and state.parent_id in self._widgets:
                self._widgets[state.parent_id].children_ids.discard(widget_id)

            # Execute cleanup callbacks
            for callback in state.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.warning(
                        f"Cleanup callback failed for {widget_id}: {e}"
                    )

            # Remove from tracking
            del self._widgets[widget_id]

            self.logger.debug(f"Unregistered widget {widget_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister widget {widget_id}: {e}")
            return False

    def safe_destroy_widget(self, widget_id: str) -> bool:
        """
        Safely destroy a widget with proper cleanup order.

        Args:
            widget_id: Widget ID to destroy

        Returns:
            bool: True if successfully destroyed
        """
        try:
            if widget_id not in self._widgets:
                return False

            state = self._widgets[widget_id]

            if state.is_being_destroyed:
                return True  # Already being destroyed

            # Mark as being destroyed
            state.mark_destroying()

            # Destroy children first (bottom-up approach)
            for child_id in list(state.children_ids):
                self.safe_destroy_widget(child_id)

            # Get widget reference
            widget = state.get_widget()
            if widget is not None:
                try:
                    # Disconnect from parent if it exists
                    widget.setParent(None)

                    # Schedule for deletion
                    widget.deleteLater()

                    self.logger.debug(
                        f"Scheduled widget {widget_id} for deletion"
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Error during widget destruction {widget_id}: {e}"
                    )

            # Unregister the widget
            self.unregister_widget(widget_id)

            return True

        except Exception as e:
            self.logger.error(f"Failed to destroy widget {widget_id}: {e}")
            return False

    def safe_widget_operation(
        self, widget_id: str, operation: Callable[[QWidget], Any]
    ) -> Any:
        """
        Safely perform an operation on a widget with validation.

        Args:
            widget_id: Widget ID
            operation: Operation to perform on the widget

        Returns:
            Any: Result of operation or None if failed
        """
        try:
            if widget_id not in self._widgets:
                self.logger.warning(
                    f"Widget {widget_id} not found in lifecycle manager"
                )
                return None

            state = self._widgets[widget_id]
            widget = state.get_widget()

            if widget is None:
                self.logger.warning(f"Widget {widget_id} is no longer valid")
                return None

            if state.is_being_destroyed:
                self.logger.warning(
                    f"Widget {widget_id} is being destroyed, skipping operation"
                )
                return None

            return operation(widget)

        except Exception as e:
            self.logger.error(
                f"Safe widget operation failed for {widget_id}: {e}"
            )
            return None

    def safe_update_label(self, widget_id: str, text: str) -> bool:
        """
        Safely update a QLabel's text.

        Args:
            widget_id: Widget ID of the label
            text: New text to set

        Returns:
            bool: True if successfully updated
        """

        def update_operation(widget):
            if isinstance(widget, QLabel):
                widget.setText(text)
                return True
            return False

        result = self.safe_widget_operation(widget_id, update_operation)
        return result is True

    def safe_find_children(self, widget_id: str, child_type: type) -> list:
        """
        Safely find children of a widget.

        Args:
            widget_id: Parent widget ID
            child_type: Type of children to find

        Returns:
            list: List of child widgets
        """

        def find_operation(widget):
            return widget.findChildren(child_type)

        result = self.safe_widget_operation(widget_id, find_operation)
        return result if result is not None else []

    def add_cleanup_callback(
        self, widget_id: str, callback: Callable[[], None]
    ) -> bool:
        """
        Add a cleanup callback for a widget.

        Args:
            widget_id: Widget ID
            callback: Callback to execute during cleanup

        Returns:
            bool: True if callback was added
        """
        try:
            if widget_id in self._widgets:
                self._widgets[widget_id].cleanup_callbacks.append(callback)
                return True
            return False
        except Exception as e:
            self.logger.error(
                f"Failed to add cleanup callback for {widget_id}: {e}"
            )
            return False

    def is_widget_valid(self, widget_id: str) -> bool:
        """
        Check if a widget is still valid.

        Args:
            widget_id: Widget ID to check

        Returns:
            bool: True if widget is valid
        """
        if widget_id not in self._widgets:
            return False
        return self._widgets[widget_id].is_valid()

    def get_widget_info(self, widget_id: str) -> Dict[str, Any]:
        """
        Get information about a widget.

        Args:
            widget_id: Widget ID

        Returns:
            Dict: Widget information
        """
        if widget_id not in self._widgets:
            return {}

        state = self._widgets[widget_id]
        return {
            "widget_id": widget_id,
            "widget_type": state.widget_type,
            "created_at": state.created_at.isoformat(),
            "destroyed_at": (
                state.destroyed_at.isoformat() if state.destroyed_at else None
            ),
            "is_valid": state.is_valid(),
            "is_being_destroyed": state.is_being_destroyed,
            "parent_id": state.parent_id,
            "children_count": len(state.children_ids),
        }

    def _periodic_cleanup(self):
        """Perform periodic cleanup of invalid widgets."""
        try:
            invalid_widgets = []

            for widget_id, state in self._widgets.items():
                if not state.is_valid():
                    invalid_widgets.append(widget_id)

            for widget_id in invalid_widgets:
                self.unregister_widget(widget_id)

            if invalid_widgets:
                self.logger.debug(
                    f"Cleaned up {len(invalid_widgets)} invalid widgets"
                )

        except Exception as e:
            self.logger.error(f"Error during periodic cleanup: {e}")

    def cleanup_all(self):
        """Clean up all registered widgets."""
        try:
            # Stop cleanup timer
            if self._cleanup_timer:
                self._cleanup_timer.stop()

            # Destroy all widgets in reverse order (children first)
            widget_ids = list(self._widgets.keys())
            for widget_id in reversed(widget_ids):
                self.safe_destroy_widget(widget_id)

            self._widgets.clear()
            self.logger.info("All widgets cleaned up")

        except Exception as e:
            self.logger.error(f"Error during cleanup all: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get widget lifecycle statistics.

        Returns:
            Dict: Statistics information
        """
        valid_widgets = sum(
            1 for state in self._widgets.values() if state.is_valid()
        )
        invalid_widgets = len(self._widgets) - valid_widgets

        return {
            "total_widgets": len(self._widgets),
            "valid_widgets": valid_widgets,
            "invalid_widgets": invalid_widgets,
            "widgets_being_destroyed": sum(
                1
                for state in self._widgets.values()
                if state.is_being_destroyed
            ),
        }


# Global instance for application-wide use
_global_lifecycle_manager: Optional[WidgetLifecycleManager] = None


def get_widget_lifecycle_manager() -> WidgetLifecycleManager:
    """Get the global widget lifecycle manager instance."""
    global _global_lifecycle_manager
    if _global_lifecycle_manager is None:
        _global_lifecycle_manager = WidgetLifecycleManager()
    return _global_lifecycle_manager


def safe_widget_operation(
    widget_id: str, operation: Callable[[QWidget], Any]
) -> Any:
    """Convenience function for safe widget operations."""
    return get_widget_lifecycle_manager().safe_widget_operation(
        widget_id, operation
    )


def register_widget(
    widget: QWidget, widget_type: str = None, parent_id: str = None
) -> str:
    """Convenience function for widget registration."""
    return get_widget_lifecycle_manager().register_widget(
        widget, widget_type, parent_id
    )


def safe_destroy_widget(widget_id: str) -> bool:
    """Convenience function for safe widget destruction."""
    return get_widget_lifecycle_manager().safe_destroy_widget(widget_id)


def is_widget_valid(widget_id: str) -> bool:
    """Convenience function for widget validation."""
    return get_widget_lifecycle_manager().is_widget_valid(widget_id)
