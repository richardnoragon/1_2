"""
Enhanced Pane Manager with Widget Lifecycle Management

This module provides the enhanced pane manager implementation with proper
Qt widget lifecycle management to prevent deletion errors and memory leaks.

The key improvements:
1. Integration with WidgetLifecycleManager for safe widget operations
2. Proper widget destruction order (children first)
3. Defensive programming against deleted Qt objects
4. Comprehensive error handling and recovery

Author: RFU Development Team
Version: 2.0.0 (Enhanced with Widget Lifecycle Management)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .widget_lifecycle_manager import (
    WidgetLifecycleManager,
    get_widget_lifecycle_manager,
    is_widget_valid,
    register_widget,
    safe_destroy_widget,
    safe_widget_operation,
)

try:
    from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


class EnhancedBasePaneWidget:
    """
    Enhanced base pane widget with lifecycle management.

    This version includes:
    - Widget lifecycle tracking
    - Safe widget operations
    - Proper cleanup procedures
    - Error recovery mechanisms
    """

    def __init__(self, config, parent=None):
        """Initialize enhanced pane widget."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.pane_id}")
        self.lifecycle_manager = get_widget_lifecycle_manager()

        # Widget tracking
        self._widget_ids: Dict[str, str] = (
            {}
        )  # Maps widget name to lifecycle ID
        self._is_active = False
        self._is_modified = False
        self._creation_time = datetime.now()
        self._last_access_time = datetime.now()

        # Widget components
        self._title_widget = None
        self._content_widget = None
        self._title_widget_id = ""
        self._content_widget_id = ""
        self._title_label_id = ""

        # Signals (only available if Qt is available)
        if QT_AVAILABLE:
            self.paneActivated = None
            self.paneDeactivated = None
            self.paneClosed = None
            self.paneModified = None

        self._setup_widgets(parent)

    def _setup_widgets(self, parent):
        """Setup widgets with lifecycle management."""
        try:
            if not QT_AVAILABLE:
                return

            # Create title widget with lifecycle tracking
            self._title_widget = self._create_title_widget()
            if self._title_widget:
                self._title_widget_id = register_widget(
                    self._title_widget, f"TitleWidget_{self.config.pane_id}"
                )
                self._widget_ids["title"] = self._title_widget_id

            # Create content widget with lifecycle tracking
            self._content_widget = self._create_content_widget()
            if self._content_widget:
                self._content_widget_id = register_widget(
                    self._content_widget,
                    f"ContentWidget_{self.config.pane_id}",
                    parent_id=self._title_widget_id,
                )
                self._widget_ids["content"] = self._content_widget_id

            self.logger.debug(f"Setup widgets for pane {self.config.pane_id}")

        except Exception as e:
            self.logger.error(
                f"Failed to setup widgets for pane {self.config.pane_id}: {e}"
            )

    def _create_title_widget(self) -> Optional[QWidget]:
        """Create title widget with safe operations."""
        if not QT_AVAILABLE:
            return None

        try:
            title_widget = QWidget()
            layout = QHBoxLayout(title_widget)
            layout.setContentsMargins(5, 0, 5, 0)

            # Create title label
            title_label = QLabel(self.config.title)
            title_label.setFont(QFont("Arial", 9, QFont.Bold))

            # Register title label for lifecycle management
            self._title_label_id = register_widget(
                title_label, f"TitleLabel_{self.config.pane_id}"
            )
            self._widget_ids["title_label"] = self._title_label_id

            layout.addWidget(title_label)
            layout.addStretch()

            return title_widget

        except Exception as e:
            self.logger.error(f"Failed to create title widget: {e}")
            return None

    def _create_content_widget(self) -> Optional[QWidget]:
        """Create content widget. Override in subclasses."""
        if not QT_AVAILABLE:
            return None

        try:
            content = QLabel("Base Pane Content")
            content.setAlignment(Qt.AlignCenter)
            return content

        except Exception as e:
            self.logger.error(f"Failed to create content widget: {e}")
            return None

    def safe_update_title_display(self):
        """Safely update title display to reflect modified state."""
        try:
            if not QT_AVAILABLE or not self._title_label_id:
                return

            if not is_widget_valid(self._title_label_id):
                self.logger.warning(
                    f"Title label widget is no longer valid for pane {self.config.pane_id}"
                )
                return

            title = self.config.title
            if self._is_modified:
                title += "*"

            # Use safe widget operation to update label
            def update_label(widget):
                if isinstance(widget, QLabel):
                    widget.setText(title)
                    return True
                return False

            success = safe_widget_operation(self._title_label_id, update_label)
            if success:
                self.logger.debug(
                    f"Updated title display for pane {self.config.pane_id}"
                )
            else:
                self.logger.warning(
                    f"Failed to update title display for pane {self.config.pane_id}"
                )

        except Exception as e:
            self.logger.error(
                f"Error updating title display for pane {self.config.pane_id}: {e}"
            )

    def safe_close_pane(self) -> bool:
        """
        Safely close the pane with proper widget cleanup.

        Returns:
            bool: True if pane was closed successfully
        """
        try:
            if not self.config.is_closable:
                return False

            if not self._can_close():
                return False

            # Emit signal before cleanup
            if (
                QT_AVAILABLE
                and hasattr(self, "paneClosed")
                and self.paneClosed
            ):
                self.paneClosed.emit(self.config.pane_id)

            # Perform cleanup
            self._cleanup_widgets()

            # Call subclass cleanup
            self._on_closed()

            self.logger.info(f"Successfully closed pane {self.config.pane_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to close pane {self.config.pane_id}: {e}"
            )
            return False

    def _cleanup_widgets(self):
        """Clean up all widgets associated with this pane."""
        try:
            # Destroy widgets in reverse order (children first)
            widget_destroy_order = ["title_label", "content", "title"]

            for widget_name in widget_destroy_order:
                widget_id = self._widget_ids.get(widget_name)
                if widget_id and is_widget_valid(widget_id):
                    success = safe_destroy_widget(widget_id)
                    if success:
                        self.logger.debug(
                            f"Destroyed {widget_name} widget for pane {self.config.pane_id}"
                        )
                    else:
                        self.logger.warning(
                            f"Failed to destroy {widget_name} widget for pane {self.config.pane_id}"
                        )

            # Clear widget tracking
            self._widget_ids.clear()
            self._title_widget = None
            self._content_widget = None
            self._title_widget_id = ""
            self._content_widget_id = ""
            self._title_label_id = ""

            self.logger.debug(
                f"Widget cleanup completed for pane {self.config.pane_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Error during widget cleanup for pane {self.config.pane_id}: {e}"
            )

    def set_modified(self, modified: bool = True):
        """
        Set pane modified state with safe title update.

        Args:
            modified: Whether pane is modified
        """
        try:
            if self._is_modified != modified:
                self._is_modified = modified

                if (
                    QT_AVAILABLE
                    and hasattr(self, "paneModified")
                    and self.paneModified
                ):
                    self.paneModified.emit(self.config.pane_id)

                self.safe_update_title_display()

        except Exception as e:
            self.logger.error(
                f"Error setting modified state for pane {self.config.pane_id}: {e}"
            )

    def activate(self):
        """Activate the pane safely."""
        try:
            if not self._is_active:
                self._is_active = True
                self._last_access_time = datetime.now()
                self.config.state = getattr(self.config, "PaneState", {}).get(
                    "ACTIVE", "ACTIVE"
                )

                if (
                    QT_AVAILABLE
                    and hasattr(self, "paneActivated")
                    and self.paneActivated
                ):
                    self.paneActivated.emit(self.config.pane_id)

                self._on_activated()

        except Exception as e:
            self.logger.error(
                f"Error activating pane {self.config.pane_id}: {e}"
            )

    def deactivate(self):
        """Deactivate the pane safely."""
        try:
            if self._is_active:
                self._is_active = False
                self.config.state = getattr(self.config, "PaneState", {}).get(
                    "INACTIVE", "INACTIVE"
                )

                if (
                    QT_AVAILABLE
                    and hasattr(self, "paneDeactivated")
                    and self.paneDeactivated
                ):
                    self.paneDeactivated.emit(self.config.pane_id)

                self._on_deactivated()

        except Exception as e:
            self.logger.error(
                f"Error deactivating pane {self.config.pane_id}: {e}"
            )

    def is_valid(self) -> bool:
        """Check if the pane's widgets are still valid."""
        try:
            # Check if critical widgets are still valid
            critical_widgets = ["title", "content"]
            for widget_name in critical_widgets:
                widget_id = self._widget_ids.get(widget_name)
                if widget_id and not is_widget_valid(widget_id):
                    return False
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking pane validity for {self.config.pane_id}: {e}"
            )
            return False

    # Methods to override in subclasses
    def _can_close(self) -> bool:
        """Check if pane can be closed. Override in subclasses."""
        return True

    def _on_activated(self):
        """Called when pane is activated. Override in subclasses."""
        pass

    def _on_deactivated(self):
        """Called when pane is deactivated. Override in subclasses."""
        pass

    def _on_closed(self):
        """Called when pane is closed. Override in subclasses."""
        pass

    @property
    def pane_id(self) -> str:
        """Get pane ID."""
        return self.config.pane_id

    @property
    def is_active(self) -> bool:
        """Check if pane is active."""
        return self._is_active

    @property
    def is_modified(self) -> bool:
        """Check if pane has been modified."""
        return self._is_modified


class EnhancedPaneManager:
    """
    Enhanced pane manager with comprehensive widget lifecycle management.

    Features:
    - Safe widget operations with validation
    - Proper cleanup order for widget destruction
    - Error recovery and defensive programming
    - Memory leak prevention
    - Comprehensive logging and monitoring
    """

    def __init__(self):
        """Initialize enhanced pane manager."""
        self.logger = logging.getLogger(__name__)
        self.lifecycle_manager = get_widget_lifecycle_manager()

        # Pane management
        self._panes: Dict[str, EnhancedBasePaneWidget] = {}
        self._pane_order: List[str] = []
        self._active_pane_id: Optional[str] = None

        # State management
        self._state_dirty = False
        self._auto_save_timer = None

        # Statistics
        self.stats = {
            "panes_created": 0,
            "panes_destroyed": 0,
            "operations_performed": 0,
            "errors_encountered": 0,
        }

        self.logger.info("Enhanced pane manager initialized")

    def create_pane(self, config, parent=None) -> str:
        """
        Create a new pane with enhanced lifecycle management.

        Args:
            config: Pane configuration
            parent: Parent widget

        Returns:
            str: Pane ID if successful, empty string if failed
        """
        try:
            # Create enhanced pane widget
            pane = EnhancedBasePaneWidget(config, parent)

            # Validate pane creation
            if not pane.is_valid():
                self.logger.error(
                    f"Failed to create valid pane widgets for {config.pane_id}"
                )
                return ""

            # Add to management
            self._panes[config.pane_id] = pane
            self._pane_order.append(config.pane_id)

            # Update statistics
            self.stats["panes_created"] += 1
            self._state_dirty = True

            self.logger.info(f"Created pane: {config.pane_id}")
            return config.pane_id

        except Exception as e:
            self.stats["errors_encountered"] += 1
            self.logger.error(f"Failed to create pane: {e}")
            return ""

    def remove_pane(self, pane_id: str) -> bool:
        """
        Safely remove pane with proper widget cleanup.

        Args:
            pane_id: ID of pane to remove

        Returns:
            bool: True if pane was removed successfully
        """
        try:
            if pane_id not in self._panes:
                self.logger.warning(f"Pane {pane_id} not found for removal")
                return False

            pane = self._panes[pane_id]

            # Validate pane before removal
            if not pane.is_valid():
                self.logger.warning(
                    f"Pane {pane_id} is already invalid, forcing removal"
                )
            else:
                # Try to close pane normally
                if not pane.safe_close_pane():
                    self.logger.warning(
                        f"Pane {pane_id} could not be closed normally, forcing removal"
                    )

            # Remove from management
            del self._panes[pane_id]
            if pane_id in self._pane_order:
                self._pane_order.remove(pane_id)

            # Update active pane if necessary
            if self._active_pane_id == pane_id:
                self._active_pane_id = None
                if self._pane_order:
                    self.activate_pane(self._pane_order[-1])

            # Update statistics
            self.stats["panes_destroyed"] += 1
            self.stats["operations_performed"] += 1
            self._state_dirty = True

            self.logger.info(f"Removed pane: {pane_id}")
            return True

        except Exception as e:
            self.stats["errors_encountered"] += 1
            self.logger.error(f"Failed to remove pane {pane_id}: {e}")
            return False

    def activate_pane(self, pane_id: str) -> bool:
        """
        Safely activate a pane.

        Args:
            pane_id: ID of pane to activate

        Returns:
            bool: True if pane was activated successfully
        """
        try:
            if pane_id not in self._panes:
                self.logger.warning(f"Pane {pane_id} not found for activation")
                return False

            pane = self._panes[pane_id]

            # Validate pane before activation
            if not pane.is_valid():
                self.logger.error(f"Cannot activate invalid pane {pane_id}")
                return False

            # Deactivate current active pane
            if self._active_pane_id and self._active_pane_id != pane_id:
                current_pane = self._panes.get(self._active_pane_id)
                if current_pane and current_pane.is_valid():
                    current_pane.deactivate()

            # Activate new pane
            pane.activate()
            self._active_pane_id = pane_id

            # Update pane order (move to end)
            if pane_id in self._pane_order:
                self._pane_order.remove(pane_id)
            self._pane_order.append(pane_id)

            self.stats["operations_performed"] += 1
            self._state_dirty = True

            self.logger.info(f"Activated pane: {pane_id}")
            return True

        except Exception as e:
            self.stats["errors_encountered"] += 1
            self.logger.error(f"Failed to activate pane {pane_id}: {e}")
            return False

    def get_pane(self, pane_id: str) -> Optional[EnhancedBasePaneWidget]:
        """
        Get pane by ID with validation.

        Args:
            pane_id: Pane ID

        Returns:
            Optional[EnhancedBasePaneWidget]: Pane widget or None
        """
        try:
            pane = self._panes.get(pane_id)
            if pane and not pane.is_valid():
                self.logger.warning(
                    f"Pane {pane_id} is invalid, removing from management"
                )
                self.remove_pane(pane_id)
                return None
            return pane

        except Exception as e:
            self.logger.error(f"Error getting pane {pane_id}: {e}")
            return None

    def cleanup(self):
        """Clean up all resources with proper widget destruction."""
        try:
            # Save state if dirty
            if self._state_dirty:
                # Would normally save state here
                pass

            # Stop auto-save timer
            if self._auto_save_timer:
                self._auto_save_timer.stop()

            # Close all panes in reverse order
            pane_ids = list(self._panes.keys())
            for pane_id in reversed(pane_ids):
                self.remove_pane(pane_id)

            # Final cleanup
            self._panes.clear()
            self._pane_order.clear()
            self._active_pane_id = None

            self.logger.info("Enhanced pane manager cleanup completed")

        except Exception as e:
            self.stats["errors_encountered"] += 1
            self.logger.error(f"Error during cleanup: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get pane manager statistics."""
        return {
            **self.stats,
            "active_panes": len(self._panes),
            "active_pane_id": self._active_pane_id,
            "widget_stats": self.lifecycle_manager.get_statistics(),
        }

    def validate_all_panes(self) -> Dict[str, bool]:
        """
        Validate all panes and return status.

        Returns:
            Dict[str, bool]: Pane ID to validity mapping
        """
        validation_results = {}

        try:
            for pane_id, pane in self._panes.items():
                validation_results[pane_id] = pane.is_valid()

            invalid_count = sum(
                1 for valid in validation_results.values() if not valid
            )
            if invalid_count > 0:
                self.logger.warning(
                    f"Found {invalid_count} invalid panes during validation"
                )

        except Exception as e:
            self.logger.error(f"Error during pane validation: {e}")

        return validation_results


# For testing and development
if __name__ == "__main__":
    import sys

    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Enhanced pane manager test starting")

    try:
        # Create test configuration
        class TestConfig:
            def __init__(self, pane_id):
                self.pane_id = pane_id
                self.title = f"Test Pane {pane_id}"
                self.is_closable = True
                self.state = "ACTIVE"

        # Create enhanced pane manager
        manager = EnhancedPaneManager()

        # Create test panes
        for i in range(3):
            config = TestConfig(f"test_pane_{i}")
            pane_id = manager.create_pane(config)
            if pane_id:
                logger.info(f"Created test pane: {pane_id}")
            else:
                logger.error(f"Failed to create test pane {i}")

        # Test activation
        manager.activate_pane("test_pane_1")

        # Validate all panes
        validation_results = manager.validate_all_panes()
        logger.info(f"Validation results: {validation_results}")

        # Get statistics
        stats = manager.get_statistics()
        logger.info(f"Statistics: {stats}")

        # Cleanup
        manager.cleanup()

        logger.info("Enhanced pane manager test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
