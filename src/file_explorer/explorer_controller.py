#!/usr/bin/env python3
"""
Multi-Pane Explorer Controller - Clean Architecture Implementation

This module provides the main controller for the multi-pane file explorer,
implementing proper separation of concerns and enterprise-grade error handling.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import QObject, Qt, pyqtSignal
    from PyQt5.QtWidgets import QMainWindow, QSplitter, QTabWidget, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QMainWindow = object
    QObject = object


class ExplorerController(QObject if QT_AVAILABLE else object):
    """
    Central controller for multi-pane file explorer.

    Responsibilities:
    - Coordinate between UI components
    - Manage pane lifecycle
    - Handle inter-pane communication
    - Provide unified interface for external integrations
    """

    # Signals
    paneAdded = pyqtSignal(str) if QT_AVAILABLE else None
    paneRemoved = pyqtSignal(str) if QT_AVAILABLE else None
    activePaneChanged = pyqtSignal(str) if QT_AVAILABLE else None
    pathChanged = pyqtSignal(str, str) if QT_AVAILABLE else None
    fileSelected = pyqtSignal(str) if QT_AVAILABLE else None

    def __init__(self, main_window: Optional[QMainWindow] = None):
        """Initialize explorer controller."""
        if QT_AVAILABLE:
            super().__init__()

        self.logger = logging.getLogger("RFU.ExplorerController")
        self.main_window = main_window

        # Component managers
        self._pane_manager = None
        self._layout_manager = None
        self._tool_integration = None

        # State management
        self.active_pane_id = ""
        self.pane_count = 2
        self.layout_mode = "horizontal"
        self.is_initialized = False

        # Center pane management (T042)
        self.center_panes = {}  # pane_id -> pane widget
        self.pane_states = {}  # pane_id -> state dict
        self.right_pane_widget = None  # Reference to right pane

        # Preference service (T043)
        self._preference_service = None
        self._config_dir = None

        # Initialize components
        self._initialize_managers()
        self._initialize_preferences()

    def _initialize_managers(self):
        """Initialize component managers."""
        try:
            from .integration.tool_integration import ToolIntegration
            from .managers.layout_manager import LayoutManager
            from .managers.pane_manager import PaneManager

            self._pane_manager = PaneManager(self)
            self._layout_manager = LayoutManager(self)
            self._tool_integration = ToolIntegration(self)

            # Connect signals
            if self._pane_manager and hasattr(self._pane_manager, "paneAdded"):
                self._pane_manager.paneAdded.connect(self._on_pane_added)
                self._pane_manager.paneRemoved.connect(self._on_pane_removed)

            self.logger.info("Component managers initialized successfully")

        except ImportError as e:
            self.logger.warning(f"Some managers not available: {e}")
            self._initialize_fallback_managers()
        except Exception as e:
            self.logger.error(f"Error initializing managers: {e}")
            self._initialize_fallback_managers()

    def _initialize_fallback_managers(self):
        """Initialize fallback managers when full versions not available."""
        try:
            from .fallback.simple_managers import (
                SimpleLayoutManager,
                SimplePaneManager,
                SimpleToolIntegration,
            )

            self._pane_manager = SimplePaneManager(self)
            self._layout_manager = SimpleLayoutManager(self)
            self._tool_integration = SimpleToolIntegration(self)

            self.logger.info("Fallback managers initialized")

        except ImportError:
            self.logger.error("No managers available - creating minimal fallbacks")
            self._create_minimal_managers()

    def _create_minimal_managers(self):
        """Create minimal manager implementations."""

        class MinimalManager:
            def __init__(self, controller):
                self.controller = controller
                self.logger = logging.getLogger("RFU.MinimalManager")

        self._pane_manager = MinimalManager(self)
        self._layout_manager = MinimalManager(self)
        self._tool_integration = MinimalManager(self)

    def _initialize_preferences(self, config_dir: Optional[Path] = None):
        """
        Initialize preference service and load user preferences (T043).

        Args:
            config_dir: Optional config directory for testing
        """
        try:
            from src.file_explorer.services.preference_service import (
                PreferenceService,
            )

            self._config_dir = config_dir
            self._preference_service = PreferenceService(config_dir=config_dir)

            # Load preferences
            prefs = self._preference_service.load_preferences()

            # Apply loaded preferences to state
            if prefs.pane_config:
                self.pane_count = prefs.pane_config.pane_count
                layout_type = prefs.pane_config.layout_type
                self.layout_mode = (
                    "horizontal"
                    if str(layout_type).lower() == "horizontal"
                    else "vertical"
                )

            self.logger.info(
                f"Preferences loaded: {self.pane_count} panes, "
                f"{self.layout_mode} layout"
            )

        except ImportError as e:
            self.logger.warning(f"PreferenceService not available: {e}")
            self._preference_service = None
        except Exception as e:
            self.logger.error(f"Error initializing preferences: {e}")
            self._preference_service = None

    def _save_preferences(self):
        """Save current state to preferences (T043)."""
        try:
            if not self._preference_service:
                return

            prefs = self._preference_service.load_preferences()

            # Update pane configuration
            from src.file_explorer.models.pane_configuration import (
                LayoutType,
                PaneConfiguration,
            )

            layout_type = (
                LayoutType.HORIZONTAL
                if self.layout_mode == "horizontal"
                else LayoutType.VERTICAL
            )
            prefs.pane_config = PaneConfiguration(self.pane_count, layout_type, {})

            # Save updated preferences
            self._preference_service.save_preferences(prefs)

            self.logger.debug("Preferences saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")

    def initialize_ui(self, container_widget: QWidget) -> bool:
        """
        Initialize the UI components in the provided container.

        Args:
            container_widget: Widget to contain the explorer interface

        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing multi-pane explorer UI")

            if not container_widget:
                self.logger.error("No container widget provided")
                return False

            # Setup main layout
            success = self._setup_main_layout(container_widget)
            if not success:
                return False

            # Initialize panes
            success = self._initialize_default_panes()
            if not success:
                return False

            # Setup tool integration
            self._setup_tool_integration()

            self.is_initialized = True
            self.logger.info("Multi-pane explorer UI initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
            return False

    def _setup_main_layout(self, container: QWidget) -> bool:
        """Setup main layout structure."""
        try:
            if self._layout_manager and hasattr(self._layout_manager, "setup"):
                return self._layout_manager.setup(container)
            else:
                # Fallback layout setup
                return self._setup_fallback_layout(container)
        except Exception as e:
            self.logger.error(f"Error setting up main layout: {e}")
            return False

    def _setup_fallback_layout(self, container: QWidget) -> bool:
        """Setup fallback layout when manager not available."""
        try:
            from PyQt5.QtWidgets import QHBoxLayout

            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Create simple splitter
            splitter = QSplitter(Qt.Horizontal)
            layout.addWidget(splitter)

            # Store reference
            container._main_splitter = splitter

            self.logger.info("Fallback layout setup completed")
            return True

        except Exception as e:
            self.logger.error(f"Error setting up fallback layout: {e}")
            return False

    def _initialize_default_panes(self) -> bool:
        """Initialize default pane configuration."""
        try:
            if self._pane_manager and hasattr(self._pane_manager, "create_panes"):
                return self._pane_manager.create_panes(self.pane_count)
            else:
                # Fallback pane creation
                return self._create_fallback_panes()
        except Exception as e:
            self.logger.error(f"Error initializing panes: {e}")
            return False

    def _create_fallback_panes(self) -> bool:
        """Create fallback panes when manager not available."""
        try:
            # Simple implementation for fallback
            self.logger.info("Creating fallback panes")
            return True
        except Exception as e:
            self.logger.error(f"Error creating fallback panes: {e}")
            return False

    def _setup_tool_integration(self):
        """Setup tool integration."""
        try:
            if self._tool_integration and hasattr(self._tool_integration, "setup"):
                self._tool_integration.setup()
            else:
                self.logger.info("Tool integration not available")
        except Exception as e:
            self.logger.error(f"Error setting up tool integration: {e}")

    def set_pane_count(self, count: int) -> bool:
        """
        Set number of active panes.

        Args:
            count: Number of panes (1-4)

        Returns:
            bool: True if successful
        """
        try:
            if not 1 <= count <= 4:
                self.logger.warning(f"Invalid pane count: {count}")
                return False

            old_count = self.pane_count
            self.pane_count = count

            if self._pane_manager and hasattr(self._pane_manager, "set_count"):
                success = self._pane_manager.set_count(count)
                if success:
                    self.logger.info(f"Pane count changed from {old_count} to {count}")
                    self._save_preferences()  # T043: Persist change
                return success
            else:
                self.logger.info(f"Pane count set to {count} (manager fallback)")
                self._save_preferences()  # T043: Persist change
                return True

        except Exception as e:
            self.logger.error(f"Error setting pane count: {e}")
            return False

    def set_layout_mode(self, mode: str) -> bool:
        """
        Set layout mode for panes.

        Args:
            mode: Layout mode ('horizontal', 'vertical', 'grid')

        Returns:
            bool: True if successful
        """
        try:
            valid_modes = ["horizontal", "vertical", "grid", "single"]
            if mode not in valid_modes:
                self.logger.warning(f"Invalid layout mode: {mode}")
                return False

            old_mode = self.layout_mode
            self.layout_mode = mode

            if self._layout_manager and hasattr(self._layout_manager, "set_mode"):
                success = self._layout_manager.set_mode(mode)
                if success:
                    msg = f"Layout mode changed from {old_mode} to {mode}"
                    self.logger.info(msg)
                    self._save_preferences()  # T043: Persist change
                return success
            else:
                self.logger.info(f"Layout mode set to {mode} (manager fallback)")
                self._save_preferences()  # T043: Persist change
                return True

        except Exception as e:
            self.logger.error(f"Error setting layout mode: {e}")
            return False

    def navigate_active_pane(self, path: str) -> bool:
        """
        Navigate active pane to specified path.

        Args:
            path: Path to navigate to

        Returns:
            bool: True if successful
        """
        try:
            if not Path(path).exists():
                self.logger.warning(f"Path does not exist: {path}")
                return False

            if self._pane_manager and hasattr(self._pane_manager, "navigate"):
                success = self._pane_manager.navigate(self.active_pane_id, path)
                if success and self.pathChanged:
                    self.pathChanged.emit(self.active_pane_id, path)
                return success
            else:
                self.logger.info(f"Navigation to {path} (manager fallback)")
                return True

        except Exception as e:
            self.logger.error(f"Error navigating to {path}: {e}")
            return False

    def navigate_with_fallback(self, pane_id: str, path: Path) -> bool:
        """
        Navigate to path with fallback to system root if unavailable (T045).

        Args:
            pane_id: Pane identifier
            path: Path to navigate to

        Returns:
            bool: True if navigation successful (possibly to fallback)
        """
        try:
            # Check if path is available
            if self._is_path_available(path):
                # Path available, navigate normally
                if self._pane_manager and hasattr(self._pane_manager, "navigate"):
                    success = self._pane_manager.navigate(pane_id, str(path))
                    if success and self.pathChanged:
                        self.pathChanged.emit(pane_id, str(path))
                    return success
                return True

            # Path unavailable, show notification and fall back
            self._show_unavailable_notification(path)
            fallback_path = self._get_system_root()

            if self._pane_manager and hasattr(self._pane_manager, "navigate"):
                success = self._pane_manager.navigate(pane_id, str(fallback_path))
                if success and self.pathChanged:
                    self.pathChanged.emit(pane_id, str(fallback_path))
                return success

            return True

        except Exception as e:
            self.logger.error(f"Error in navigate_with_fallback: {e}")
            return False

    def _is_path_available(self, path: Path) -> bool:
        """
        Check if path is currently accessible (T045).

        Args:
            path: Path to check

        Returns:
            bool: True if accessible
        """
        try:
            # Try to import StorageDeviceService
            from src.file_explorer.services.storage_device_service import (
                StorageDeviceService,
            )

            storage_service = StorageDeviceService()
            return storage_service.is_available(path)

        except ImportError:
            # Fallback: basic existence check
            try:
                return path.exists()
            except (OSError, PermissionError):
                return False
        except Exception as e:
            self.logger.error(f"Error checking path availability: {e}")
            return False

    def _show_unavailable_notification(self, path: Path):
        """
        Show notification that path is unavailable (T045).

        Args:
            path: Unavailable path
        """
        try:
            from src.file_explorer.services.notification_service import (
                NotificationService,
            )

            notification_service = NotificationService()
            message = f"Location unavailable: {path}\n" f"Falling back to system root."
            notification_service.show_warning(message)

        except ImportError:
            self.logger.warning(
                f"NotificationService unavailable. Path {path} not accessible."
            )
        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")

    def _get_system_root(self) -> Path:
        """
        Get system root directory (cross-platform) (T045).

        Returns:
            Path: System root (C:\\ on Windows, / on Unix)
        """
        import sys

        if sys.platform == "win32":
            return Path("C:\\")
        else:
            return Path("/")

    def launch_tool(self, tool_name: str, **kwargs) -> bool:
        """
        Launch integrated tool.

        Args:
            tool_name: Name of tool to launch
            **kwargs: Additional parameters for tool

        Returns:
            bool: True if successful
        """
        try:
            if self._tool_integration and hasattr(self._tool_integration, "launch"):
                return self._tool_integration.launch(tool_name, **kwargs)
            else:
                self.logger.warning(f"Tool integration not available for {tool_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error launching tool {tool_name}: {e}")
            return False

    def get_active_pane_path(self) -> Optional[str]:
        """Get current path of active pane."""
        try:
            if self._pane_manager and hasattr(self._pane_manager, "get_path"):
                return self._pane_manager.get_path(self.active_pane_id)
            return None
        except Exception as e:
            self.logger.error(f"Error getting active pane path: {e}")
            return None

    def get_selected_files(self, pane_id: Optional[str] = None) -> List[str]:
        """Get list of selected files from specified or active pane."""
        try:
            target_pane = pane_id or self.active_pane_id
            if self._pane_manager and hasattr(self._pane_manager, "get_selected"):
                return self._pane_manager.get_selected(target_pane)
            return []
        except Exception as e:
            self.logger.error(f"Error getting selected files: {e}")
            return []

    def refresh_active_pane(self) -> bool:
        """Refresh the active pane."""
        try:
            if self._pane_manager and hasattr(self._pane_manager, "refresh"):
                return self._pane_manager.refresh(self.active_pane_id)
            return True
        except Exception as e:
            self.logger.error(f"Error refreshing active pane: {e}")
            return False

    def _on_pane_added(self, pane_id: str):
        """Handle pane addition."""
        try:
            self.logger.info(f"Pane added: {pane_id}")
            if self.paneAdded:
                self.paneAdded.emit(pane_id)
        except Exception as e:
            self.logger.error(f"Error handling pane addition: {e}")

    def _on_pane_removed(self, pane_id: str):
        """Handle pane removal."""
        try:
            self.logger.info(f"Pane removed: {pane_id}")
            if self.paneRemoved:
                self.paneRemoved.emit(pane_id)

            # Update active pane if necessary
            if self.active_pane_id == pane_id:
                self._select_new_active_pane()
        except Exception as e:
            self.logger.error(f"Error handling pane removal: {e}")

    def _select_new_active_pane(self):
        """Select new active pane when current one is removed."""
        try:
            if self._pane_manager and hasattr(self._pane_manager, "get_pane_ids"):
                pane_ids = self._pane_manager.get_pane_ids()
                if pane_ids:
                    self.active_pane_id = pane_ids[0]
                    if self.activePaneChanged:
                        self.activePaneChanged.emit(self.active_pane_id)
                else:
                    self.active_pane_id = ""
        except Exception as e:
            self.logger.error(f"Error selecting new active pane: {e}")

    def register_center_pane(self, pane_id: str, pane_widget):
        """Register a center pane widget for management (T042)."""
        try:
            self.center_panes[pane_id] = pane_widget
            self.pane_states[pane_id] = {
                "current_path": None,
                "selected_files": [],
                "history": [],
            }

            # Connect selection signals
            if hasattr(pane_widget, "fileSelected"):
                pane_widget.fileSelected.connect(self._on_file_selected)

            self.logger.info(f"Registered center pane: {pane_id}")

        except Exception as e:
            self.logger.error(f"Error registering center pane: {e}")

    def unregister_center_pane(self, pane_id: str):
        """Unregister a center pane widget (T042)."""
        try:
            if pane_id in self.center_panes:
                del self.center_panes[pane_id]
            if pane_id in self.pane_states:
                del self.pane_states[pane_id]

            self.logger.info(f"Unregistered center pane: {pane_id}")

        except Exception as e:
            self.logger.error(f"Error unregistering center pane: {e}")

    def set_right_pane(self, right_pane_widget):
        """Set reference to right pane for selection coordination (T042)."""
        try:
            self.right_pane_widget = right_pane_widget
            self.logger.info("Right pane reference set")
        except Exception as e:
            self.logger.error(f"Error setting right pane: {e}")

    def _on_file_selected(self, file_path: str):
        """Handle file selection from center panes (T042)."""
        try:
            # Emit signal for external listeners
            if self.fileSelected:
                self.fileSelected.emit(file_path)

            # Update right pane
            if self.right_pane_widget:
                if hasattr(self.right_pane_widget, "on_file_selected"):
                    self.right_pane_widget.on_file_selected(file_path)

            self.logger.debug(f"File selected: {file_path}")

        except Exception as e:
            self.logger.error(f"Error handling file selection: {e}")

    def get_center_pane_count(self) -> int:
        """Get number of registered center panes (T042)."""
        return len(self.center_panes)

    def get_pane_state(self, pane_id: str) -> Optional[Dict[str, Any]]:
        """Get state for specific pane (T042)."""
        return self.pane_states.get(pane_id)

    def update_pane_state(self, pane_id: str, state_key: str, state_value: Any):
        """Update specific state value for pane (T042)."""
        try:
            if pane_id in self.pane_states:
                self.pane_states[pane_id][state_key] = state_value
        except Exception as e:
            self.logger.error(f"Error updating pane state: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive controller status."""
        try:
            status = {
                "is_initialized": self.is_initialized,
                "active_pane_id": self.active_pane_id,
                "pane_count": self.pane_count,
                "layout_mode": self.layout_mode,
                "managers_available": {
                    "pane_manager": self._pane_manager is not None,
                    "layout_manager": self._layout_manager is not None,
                    "tool_integration": self._tool_integration is not None,
                },
            }

            # Add manager-specific status if available
            if self._pane_manager and hasattr(self._pane_manager, "get_status"):
                status["pane_manager_status"] = self._pane_manager.get_status()

            if self._layout_manager and hasattr(self._layout_manager, "get_status"):
                status["layout_manager_status"] = self._layout_manager.get_status()

            return status

        except Exception as e:
            self.logger.error(f"Error getting controller status: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """Clean up controller and all managed resources."""
        try:
            self.logger.info("Cleaning up explorer controller")

            # Cleanup managers in reverse order
            managers = [
                ("tool_integration", self._tool_integration),
                ("layout_manager", self._layout_manager),
                ("pane_manager", self._pane_manager),
            ]

            for name, manager in managers:
                if manager and hasattr(manager, "cleanup"):
                    try:
                        manager.cleanup()
                        self.logger.debug(f"Cleaned up {name}")
                    except Exception as e:
                        self.logger.warning(f"Error cleaning up {name}: {e}")

            # Reset state
            self.is_initialized = False
            self.active_pane_id = ""

            self.logger.info("Explorer controller cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class ExplorerMainWindow(QMainWindow if QT_AVAILABLE else object):
    """
    Main window for multi-pane explorer with clean architecture.

    This replaces the monolithic implementation with a properly
    structured, maintainable design following enterprise standards.
    """

    def __init__(self):
        """Initialize explorer main window."""
        if QT_AVAILABLE:
            super().__init__()

        self.logger = logging.getLogger("RFU.ExplorerMainWindow")

        # Initialize component guardian protection
        from ..gui.component_guardian import get_component_guardian

        self.component_guardian = get_component_guardian()

        # Core controller
        self.controller = ExplorerController(self)

        # UI components
        self.central_widget = None
        self.main_splitter = None
        self.left_panel = None
        self.right_panel = None

        # Component IDs for guardian tracking
        self._component_ids: Dict[str, str] = {}

        # Setup window
        self._setup_window()
        self._setup_ui()
        self._setup_menus()

        self.logger.info("Explorer main window initialized")

    def _setup_window(self):
        """Setup window properties."""
        if not QT_AVAILABLE:
            return

        try:
            self.setWindowTitle("RFU Multi-Pane File Explorer")
            self.setMinimumSize(800, 600)
            self.resize(1200, 800)

            # Set window icon if available
            icon_path = Path("assets/images/rfu_explorer.png")
            if icon_path.exists():
                from PyQt5.QtGui import QIcon

                self.setWindowIcon(QIcon(str(icon_path)))

        except Exception as e:
            self.logger.warning(f"Error setting up window properties: {e}")

    def _setup_ui(self):
        """Setup user interface components."""
        try:
            # Create central widget
            self.central_widget = QWidget()
            if QT_AVAILABLE:
                self.setCentralWidget(self.central_widget)

            # Register with component guardian
            if self.central_widget:
                comp_id = self.component_guardian.register_component(
                    self.central_widget, "CentralWidget", self._recover_central_widget
                )
                self._component_ids["central_widget"] = comp_id

            # Initialize controller UI
            success = self.controller.initialize_ui(self.central_widget)
            if not success:
                self.logger.error("Controller UI initialization failed")
                self._setup_emergency_ui()

        except Exception as e:
            self.logger.error(f"Error setting up UI: {e}")
            self._setup_emergency_ui()

    def _setup_emergency_ui(self):
        """Setup emergency UI when normal initialization fails."""
        try:
            from PyQt5.QtWidgets import QLabel, QVBoxLayout

            emergency_widget = QWidget()
            layout = QVBoxLayout(emergency_widget)

            error_label = QLabel("Explorer initialization failed - Emergency mode")
            error_label.setStyleSheet("color: red; font-weight: bold; padding: 20px;")
            layout.addWidget(error_label)

            if QT_AVAILABLE:
                self.setCentralWidget(emergency_widget)

            self.logger.warning("Emergency UI activated")

        except Exception as e:
            self.logger.critical(f"Emergency UI setup failed: {e}")

    def _setup_menus(self):
        """Setup application menus."""
        if not QT_AVAILABLE:
            return

        try:
            from PyQt5.QtWidgets import QAction

            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("&File")

            # Add basic actions
            refresh_action = QAction("&Refresh", self)
            refresh_action.setShortcut("F5")
            refresh_action.triggered.connect(self.controller.refresh_active_pane)
            file_menu.addAction(refresh_action)

            exit_action = QAction("E&xit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # View menu
            view_menu = menubar.addMenu("&View")

            # Pane count submenu
            pane_menu = view_menu.addMenu("&Panes")
            for i in range(1, 5):
                action = QAction(f"{i} Pane{'s' if i > 1 else ''}", self)
                action.triggered.connect(
                    lambda checked, count=i: self.controller.set_pane_count(count)
                )
                pane_menu.addAction(action)

            # Help menu
            help_menu = menubar.addMenu("&Help")
            about_action = QAction("&About", self)
            about_action.triggered.connect(self._show_about)
            help_menu.addAction(about_action)

        except Exception as e:
            self.logger.error(f"Error setting up menus: {e}")

    def _show_about(self):
        """Show about dialog."""
        try:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.about(
                self,
                "About RFU Multi-Pane Explorer",
                "RFU Multi-Pane File Explorer v2.0\n\n"
                "Enterprise-grade file management interface\n"
                "with comprehensive error handling and recovery.\n\n"
                "© 2025 Richard's File Utilities",
            )
        except Exception as e:
            self.logger.error(f"Error showing about dialog: {e}")

    def _recover_central_widget(self) -> bool:
        """Recovery callback for central widget."""
        try:
            self.logger.info("Attempting central widget recovery")

            # Recreate central widget
            if QT_AVAILABLE:
                self.central_widget = QWidget()
                self.setCentralWidget(self.central_widget)

                # Re-register with guardian
                comp_id = self.component_guardian.register_component(
                    self.central_widget, "CentralWidget", self._recover_central_widget
                )
                self._component_ids["central_widget"] = comp_id

                # Reinitialize controller UI
                return self.controller.initialize_ui(self.central_widget)

            return True

        except Exception as e:
            self.logger.error(f"Central widget recovery failed: {e}")
            return False

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            self.logger.info("Explorer window closing")

            # Cleanup controller
            self.controller.cleanup()

            # Cleanup component guardian
            self.component_guardian.cleanup_all_components()

            if QT_AVAILABLE:
                event.accept()

        except Exception as e:
            self.logger.error(f"Error during close event: {e}")
            if QT_AVAILABLE:
                event.accept()  # Close anyway
