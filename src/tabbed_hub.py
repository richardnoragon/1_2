"""
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import importlib
import time

Richard's File Utilities Hub - Unified Main Application Interface

This module provides the main hub interface that serves as the central
entry point for all file utility tools. This is a consolidated version
that combines the best features from the previous hub implementations.

Features:
- Professional tab-based interface with organized tool categories
- Comprehensive menu system with keyboard shortcuts
- Graceful fallback when dependencies are missing
- Tool registration and status management
- Professional styling and responsive layout
- Error handling and logging integration

Consolidated from:
- simple_hub.py (primary foundation - most functional)
- hub.py (hub integration features)
- rfuhub.py (core functionality and fallback mechanisms)
"""

import importlib
import os
import sys
from collections import deque
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

# Core PyQt5 imports with graceful fallback
try:
    from PyQt5 import QtCore
    from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
    from PyQt5.QtGui import QFont, QIcon
    from PyQt5.QtWidgets import (
        QApplication,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    QtCore = None
    QMainWindow = object
    QWidget = object
    QObject = object
    pyqtSignal = None

# Core application imports with fallback for direct execution
try:
    from .config_manager import get_config_manager
    from .core.error_handler import error_handler
    from .log_manager import get_log_manager
except ImportError:
    # Fallback for direct execution
    try:
        from config_manager import get_config_manager
        from core.error_handler import error_handler
        from log_manager import get_log_manager
    except ImportError:
        # Create minimal fallbacks
        def get_log_manager():
            import logging

            return logging.getLogger(__name__)

        def get_config_manager():
            class MockConfig:
                def get(self, key, default=None):
                    return default

            return MockConfig()

        def error_handler(func):
            return func


# Import constants for string literals with fallback
try:
    from core.constants import (
        ANALYSIS_TOOLS,
        PDF_TOOLS,
        PRIVACY_TOOLS,
        SECTION_MARGIN_STYLE,
        SEGOE_UI_FONT,
        SETTINGS_TOOLS,
        SUBTITLE_STYLE_COLOR,
        TITLE_STYLE_COLOR,
        UTILITIES_TOOLS,
    )
except ImportError:
    # Define fallback constants
    PDF_TOOLS = "PDF Tools"
    SEGOE_UI_FONT = "Segoe UI"
    TITLE_STYLE_COLOR = "#2c3e50"
    SUBTITLE_STYLE_COLOR = "#34495e"
    SECTION_MARGIN_STYLE = "margin: 10px;"
    PRIVACY_TOOLS = "Privacy Tools"
    ANALYSIS_TOOLS = "Analysis Tools"
    UTILITIES_TOOLS = "Utilities Tools"
    SETTINGS_TOOLS = "Settings Tools"

# CSS Color Constants for Professional Styling
PRIMARY_BLUE = "#3498db"
DARK_BLUE = "#2980b9"
DARKER_BLUE = "#1f618d"
LIGHT_BLUE = "#5dade2"
LIGHT_GRAY = "#ecf0f1"
MEDIUM_GRAY = "#bdc3c7"
DARK_GRAY = "#95a5a6"
DARKER_GRAY = "#7f8c8d"
TEXT_DARK = "#2c3e50"
WHITE = "#ffffff"
SUCCESS_GREEN = "#27ae60"
WARNING_ORANGE = "#f39c12"
ERROR_RED = "#e74c3c"

# CSS Style Constants
TITLE_HEADER_STYLE = f"color: {TEXT_DARK}; margin: 10px 0px;"


class UtilityWindow(QMainWindow if PYQT5_AVAILABLE else object):
    """Wrapper class to ensure utilities maintain the main window's menu bar."""

    def __init__(self, parent_hub, utility_widget, title="Utility"):
        if not PYQT5_AVAILABLE:
            return

        super().__init__(parent_hub)
        self.parent_hub = parent_hub
        self.setWindowTitle(f"Richard's File Utilities - {title}")
        self.resize(900, 700)
        self.move(150, 150)
        # Ensure maximize button is enabled
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        # Use the same menu bar as the parent hub
        if hasattr(parent_hub, "menuBar") and parent_hub.menuBar():
            self._clone_menu_bar(parent_hub.menuBar())

        # Set the utility as central widget
        self.setCentralWidget(utility_widget)

        # Create status bar
        status_bar = self.statusBar()
        status_bar.showMessage(f"{title} ready")

        # Connect utility status signals if available
        if hasattr(utility_widget, "status_changed"):
            utility_widget.status_changed.connect(status_bar.showMessage)

    def _clone_menu_bar(self, source_menu_bar):
        """Clone menu bar from source to maintain consistency."""
        try:
            # Use the same menu manager pattern
            if hasattr(self.parent_hub, "menu_manager"):
                from simple_menu_manager import SimpleMenuManager

                self.menu_manager = SimpleMenuManager(self)
                self.menu_manager.create_menubar()
                self._register_delegated_callbacks()
        except Exception as e:
            print(f"Warning: Could not clone menu bar: {e}")

    def _register_delegated_callbacks(self):
        """Register menu callbacks that delegate to parent hub."""
        if not hasattr(self, "menu_manager") or not hasattr(
            self.parent_hub, "menu_manager"
        ):
            return

        # Get all callbacks from parent and delegate them
        parent_callbacks = getattr(self.parent_hub.menu_manager, "callbacks", {})
        for callback_name, callback_func in parent_callbacks.items():
            self.menu_manager.register_callback(callback_name, callback_func)

    def closeEvent(self, event):
        """Handle close event to clean up properly."""
        # Hide instead of closing to preserve the utility
        self.hide()
        if PYQT5_AVAILABLE:
            event.ignore()


if PYQT5_AVAILABLE:

    class _HubValidatorNotifier:
        """Adapter that forwards validator results to the RFU hub UI."""

        def __init__(self, hub: "RFUHub") -> None:
            self._hub = hub
            self._logger = hub.logger

        def push(
            self,
            *,
            level: str,
            message: str,
            workflow: str,
            details: Dict[str, object],
        ) -> None:
            display_message = f"[{workflow}] {message}"
            if level == "critical":
                self._logger.error(
                    "Validator rejection: %s | details=%s",
                    display_message,
                    details,
                )
            elif level == "warning":
                self._logger.warning(
                    "Validator warning: %s | details=%s",
                    display_message,
                    details,
                )
            else:
                self._logger.info("Validator info: %s", display_message)

            self._hub._enqueue_validator_notification(level, display_message, details)


class RFUHub(QMainWindow if PYQT5_AVAILABLE else QObject):
    """
    Richard's File Utilities Hub - Unified Main Application Interface

    This class combines the best features from all previous hub implementations:
    - Professional GUI from simple_hub.py
    - Hub integration features from hub.py
    - Core functionality and fallbacks from rfuhub.py
    """

    # Hub integration signals (from hub.py)
    if PYQT5_AVAILABLE:
        tool_registered = pyqtSignal(str, object)
        tool_unregistered = pyqtSignal(str)
        tool_progress_updated = pyqtSignal(str, int, str)
        tool_status_changed = pyqtSignal(str, str)
        hub_event_broadcast = pyqtSignal(str, str, dict)

    def __init__(self):
        """Initialize the unified RFU Hub."""
        if PYQT5_AVAILABLE:
            super().__init__()

        # Initialize core components
        self.logger = get_log_manager().get_logger("RFUHub")
        self.config = get_config_manager()

        self.logger.info("RFU Hub initializing...")

        self.hub_preferences_adapter = None
        self._init_hub_preferences_adapter()
        self.preference_badge_label = None
        self._preference_badge: Optional[Dict[str, Any]] = None
        self._session_context: Optional[Dict[str, Any]] = None
        self._last_username = ""
        self._login_prompt_shown = not PYQT5_AVAILABLE

        # Hub state management (from hub.py and rfuhub.py)
        self.registered_tools = {}
        self.tool_status = {}
        self.message_queue = []
        self.resource_manager = {
            "cpu": {"available": True, "allocated_to": None},
            "memory": {"available": True, "allocated_to": None},
            "disk": {"available": True, "allocated_to": None},
        }

        self._validator_notification_queue = deque()
        self._validator_notification_lock = Lock()
        self._validator_notifier = None
        self._idle_watchdog_timer = None

        # Multi-Pane Explorer support (Phase 3.5 Integration)
        self.multi_pane_explorer = None
        self.current_hub_mode = None  # Will be set in _setup_gui

        # Check for PyQt5 availability (from rfuhub.py)
        if not PYQT5_AVAILABLE:
            self.logger.warning(
                "PyQt5 not available - GUI functionality will be limited"
            )
            return

        # Initialize GUI components (from simple_hub.py)
        self._setup_gui()
        self._setup_hub_integration()
        self._setup_validator_notifications()
        self._setup_idle_timeout_watchdog()

        self.logger.info("RFU Hub initialized successfully")

    def _init_hub_preferences_adapter(self) -> None:
        """Prepare the hub preference adapter with graceful fallback."""

        try:
            from src.rfu.preferences_adapter import HubPreferencesAdapter

            adapter = HubPreferencesAdapter()
            if adapter.is_available():
                self.logger.debug(
                    "Hub preferences adapter active via PreferenceManager"
                )
            else:
                self.logger.debug(
                    "Hub preferences adapter falling back to legacy service"
                )
            self.hub_preferences_adapter = adapter
        except Exception as exc:  # pragma: no cover - defensive fallback
            self.logger.warning("Unable to initialize hub preferences adapter: %s", exc)
            self.hub_preferences_adapter = None

    def _setup_gui(self):
        """Setup the GUI interface (adapted from simple_hub.py)."""
        if not PYQT5_AVAILABLE:
            return

        # Initialize menu system
        from simple_menu_manager import SimpleMenuManager

        self.menu_manager = SimpleMenuManager(self)
        self.menu_manager.create_menubar()
        self._setup_menu_callbacks()
        self.logger.info("Menu system initialized")

        # Set up the window with proper maximize support
        self.setWindowTitle("Richard's File Utilities - Main Hub")
        self.resize(800, 600)
        self.move(100, 100)
        self.setWindowIcon(self._get_application_icon())
        # Ensure window can be maximized properly
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with title and interface toggle button
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Title with professional styling
        title_label = QLabel("Richard's File Utilities")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {PRIMARY_BLUE};
                margin: 15px 0px;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {WHITE}, stop:1 {LIGHT_GRAY});
                border-radius: 8px;
                border: 1px solid {MEDIUM_GRAY};
            }}
        """
        )
        header_layout.addWidget(title_label, 1)
        header_layout.addStretch(1)

        # Add interface toggle button and preference badge display
        self._create_interface_toggle_button(header_layout)
        self._create_preference_badge_display(header_layout)

        main_layout.addWidget(self.header_widget)

        # Create stacked widget to hold both interfaces
        from PyQt5.QtWidgets import QStackedWidget

        self.interface_stack = QStackedWidget()
        main_layout.addWidget(self.interface_stack)

        # Create tab widget with professional styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {MEDIUM_GRAY};
                background-color: {WHITE};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {LIGHT_GRAY}, stop:1 {MEDIUM_GRAY});
                border: 1px solid {DARK_GRAY};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {WHITE}, stop:1 {LIGHT_GRAY});
                border-bottom-color: {WHITE};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {LIGHT_BLUE}, stop:1 {PRIMARY_BLUE});
                color: white;
            }}
            QPushButton {{
                min-height: 56px;
                padding: 12px 18px;
                font-family: '{SEGOE_UI_FONT}';
                font-size: 12px;
            }}
        """
        )
        main_layout.addWidget(self.tab_widget)

        # Create all tabs (from simple_hub.py)
        self.create_analysis_tab()
        self.create_file_operations_tab()
        self.create_metadata_tab()
        self.create_network_tab()
        self.create_pdf_tools_tab()
        self.create_privacy_tab()
        self.create_security_tab()
        self.create_system_tab()
        self.create_logs_tab()

        # Add tabbed interface to stacked widget
        self.interface_stack.addWidget(self.tab_widget)

        # Create Multi-Pane Explorer interface
        self._create_multi_pane_interface()

        # Load and set initial interface mode
        self._load_and_set_interface_mode()

        # Status bar with professional styling
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(
            f"""
            QStatusBar {{
                background-color: {LIGHT_GRAY};
                border-top: 1px solid {MEDIUM_GRAY};
                padding: 5px;
            }}
        """
        )
        self.status_bar.showMessage("RFU Hub initialized successfully")

        # Apply startup mode that focuses solely on the tab interface
        self._apply_startup_focus_mode()

    def _setup_hub_integration(self):
        """Setup hub integration components (from hub.py)."""
        if not PYQT5_AVAILABLE:
            return

        # Connect internal signals
        if hasattr(self, "tool_registered"):
            self.tool_registered.connect(self._on_tool_registered)
            self.tool_unregistered.connect(self._on_tool_unregistered)
            self.tool_progress_updated.connect(self._on_tool_progress_updated)
            self.tool_status_changed.connect(self._on_tool_status_changed)
            self.hub_event_broadcast.connect(self._on_hub_event_broadcast)

    def _setup_validator_notifications(self) -> None:
        """Register centralized validator notifications with the GUI hub."""
        if not PYQT5_AVAILABLE:
            return

        try:
            from rfu.hub import register_validator_notifier
        except ImportError as exc:
            self.logger.debug("Validator notifier registration skipped: %s", exc)
            return

        self._validator_notifier = _HubValidatorNotifier(self)
        register_validator_notifier(self._validator_notifier)

    def _teardown_validator_notifications(self) -> None:
        """Unregister the validator notifier when the hub closes."""
        try:
            from rfu.hub import unregister_validator_notifier
        except ImportError:
            return

        if self._validator_notifier is not None:
            unregister_validator_notifier(self._validator_notifier)
            self._validator_notifier = None

    def _setup_idle_timeout_watchdog(self) -> None:
        """Configure periodic idle-timeout enforcement for the hub."""

        config_manager = getattr(self, "config", None)
        get_setting = getattr(config_manager, "get_setting", None)
        if get_setting is None:
            return

        enabled = bool(get_setting("identity", "enable_idle_watchdog", False))
        if not enabled:
            return

        database_path = self._get_identity_database_path()
        if not database_path:
            self.logger.warning(
                "Idle timeout watchdog enabled but identity database is missing"
            )
            return

        idle_minutes = int(get_setting("identity", "idle_timeout_minutes", 10))
        interval_seconds = int(get_setting("identity", "watchdog_interval_seconds", 60))

        try:
            from src.rfu import configure_idle_timeout_watcher

            configure_idle_timeout_watcher(
                database_path=database_path,
                idle_minutes=idle_minutes,
            )
        except Exception as exc:
            self.logger.warning(
                "Idle timeout watcher unavailable: %s",
                exc,
            )
            return

        if not PYQT5_AVAILABLE:
            return

        interval_ms = max(5, interval_seconds) * 1000
        self._idle_watchdog_timer = QtCore.QTimer(self)
        self._idle_watchdog_timer.setInterval(interval_ms)
        self._idle_watchdog_timer.timeout.connect(self._execute_idle_watchdog_tick)
        self._idle_watchdog_timer.start()
        self.logger.info(
            "Idle timeout watcher polling every %s seconds (idle=%s minutes)",
            max(5, interval_seconds),
            idle_minutes,
        )

    def _stop_idle_watchdog_timer(self) -> None:
        if self._idle_watchdog_timer is None:
            return
        try:
            self._idle_watchdog_timer.stop()
            self._idle_watchdog_timer.deleteLater()
        finally:
            self._idle_watchdog_timer = None

    def _get_identity_database_path(self) -> Optional[Path]:
        """Return the configured identity database path, if available."""

        config_manager = getattr(self, "config", None)
        get_setting = getattr(config_manager, "get_setting", None)
        raw_value: Optional[str] = None
        if callable(get_setting):
            raw_value = (get_setting("identity", "database_path", "") or "").strip()

        candidates: list[Path] = []
        if raw_value:
            candidates.append(Path(raw_value).expanduser())

        env_path = os.getenv("RFU_IDENTITY_DB_PATH")
        if env_path:
            candidates.append(Path(env_path).expanduser())

        project_root = Path(__file__).resolve().parents[1]
        candidates.append(project_root / "data" / "rfu_identity.sqlite3")

        cwd_candidate = Path.cwd() / "data" / "rfu_identity.sqlite3"
        candidates.append(cwd_candidate)

        normalized_candidates: list[Path] = []
        seen: set[str] = set()
        for candidate in candidates:
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            normalized_candidates.append(candidate)

        for candidate in normalized_candidates:
            if candidate.exists():
                if raw_value and candidate != Path(raw_value).expanduser():
                    self.logger.debug(
                        "Using fallback identity database at %s",
                        candidate,
                    )
                return candidate

        if raw_value:
            self.logger.warning(
                "Configured identity database not found at %s",
                Path(raw_value).expanduser(),
            )
        else:
            self.logger.warning(
                "Identity database not found in default locations: %s",
                ", ".join(str(path) for path in normalized_candidates),
            )
        return None

    def _execute_idle_watchdog_tick(self) -> None:
        try:
            from src.rfu import run_idle_timeout_watcher

            summary = run_idle_timeout_watcher(raise_on_missing_config=False)
        except Exception as exc:
            self.logger.debug("Idle timeout watcher run skipped: %s", exc)
            self._stop_idle_watchdog_timer()
            return

        if not summary:
            return

        revoked = int(summary.get("revoked_sessions", 0) or 0)
        if revoked <= 0:
            return

        self.logger.warning(
            "Idle timeout watcher revoked %s session(s); closing hub",
            revoked,
        )
        if PYQT5_AVAILABLE and hasattr(self, "hub_event_broadcast"):
            self.hub_event_broadcast.emit(
                "idle_watchdog",
                "idle-timeout",
                summary,
            )
        self._update_status_bar("Session expired due to inactivity")
        self.close()

    def _enqueue_validator_notification(
        self,
        level: str,
        message: str,
        details: Dict[str, object],
    ) -> None:
        with self._validator_notification_lock:
            self._validator_notification_queue.append((level, message, details))

        if PYQT5_AVAILABLE:
            QtCore.QMetaObject.invokeMethod(
                self,
                "_process_validator_notifications",
                QtCore.Qt.QueuedConnection,
            )

    @pyqtSlot()
    def _process_validator_notifications(self) -> None:
        pending: List[tuple[str, str, Dict[str, object]]] = []
        with self._validator_notification_lock:
            while self._validator_notification_queue:
                pending.append(self._validator_notification_queue.popleft())

        for level, message, details in pending:
            self._update_status_bar(message)
            if not PYQT5_AVAILABLE:
                continue

            if level == "critical":
                self._show_validator_message_box(
                    QMessageBox.Critical,
                    "File Validation Rejected",
                    message,
                    details,
                )
            elif level == "warning":
                self._show_validator_message_box(
                    QMessageBox.Warning,
                    "File Validation Warning",
                    message,
                    details,
                )

    def _show_validator_message_box(
        self,
        icon: int,
        title: str,
        message: str,
        details: Dict[str, object],
    ) -> None:
        if not PYQT5_AVAILABLE or not self.isVisible():
            return

        lines = [message, ""]
        reason = details.get("reason")
        if reason:
            lines.append(f"Reason: {reason}")

        detected = details.get("detected_type")
        confidence = details.get("confidence")
        if detected:
            confidence_str = confidence or "unknown"
            lines.append(f"Detected type: {detected} (confidence {confidence_str})")

        allowed = details.get("allowed_types")
        if allowed:
            lines.append("Allowed types: " + self._format_allowed_types(allowed))

        text = "\n".join(lines).strip()

        if icon == QMessageBox.Critical:
            QMessageBox.critical(self, title, text)
        elif icon == QMessageBox.Warning:
            QMessageBox.warning(self, title, text)
        else:
            QMessageBox.information(self, title, text)

    def _format_allowed_types(self, allowed: object) -> str:
        if isinstance(allowed, (list, tuple, set)):
            sequence = [str(item) for item in allowed]
        else:
            return str(allowed)

        if len(sequence) > 8:
            preview = ", ".join(sequence[:8])
            return f"{preview}, …"

        return ", ".join(sequence)

    def _load_login_prompt_callable(self):
        """Best-effort import of the login dialog callable."""

        module_candidates = (
            "src.rfu.login_dialog",
            "rfu.login_dialog",
        )
        last_error = None
        for module_name in module_candidates:
            try:
                module = importlib.import_module(module_name)
                prompt = getattr(module, "prompt_for_login", None)
                if callable(prompt):
                    return prompt
            except Exception as exc:  # pragma: no cover - import guard
                last_error = exc
                self.logger.debug(
                    "Login dialog import failed via %s: %s",
                    module_name,
                    exc,
                )

        raise ImportError(
            "Unable to import the login dialog from any known module path"
        ) from last_error

    def _prompt_for_login(self) -> bool:
        """Display the hub login dialog and hydrate the session context."""

        if not PYQT5_AVAILABLE:
            return True

        self.logger.debug(
            "Login prompt requested (last_user=%s, prior_session=%s)",
            self._last_username or "",
            bool(self._session_context),
        )
        self._session_context = None

        database_path = self._get_identity_database_path()
        if database_path is None:
            self.logger.warning(
                "Identity database not configured; continuing without login prompt"
            )
            self._update_preference_badge(
                None,
                fallback_text="Identity database unavailable",
            )
            return True

        try:
            stats = database_path.stat()
            resolved_details = f"size={stats.st_size} bytes"
        except OSError as exc:
            resolved_details = f"stat_error={exc}"
        self.logger.info(
            "Identity database resolved: %s (%s)",
            database_path,
            resolved_details,
        )

        try:
            prompt_for_login = self._load_login_prompt_callable()
        except ImportError as exc:
            self.logger.error("Login dialog unavailable: %s", exc)
            self._update_preference_badge(
                None,
                fallback_text="Login dialog unavailable",
            )
            QMessageBox.critical(
                self,
                "Authentication Unavailable",
                "Unable to load the login dialog component.\n\n"
                "Review the installation and try again.",
            )
            return False

        self.logger.debug(
            "Login dialog callable ready: %s.%s",
            getattr(prompt_for_login, "__module__", "<unknown>"),
            getattr(prompt_for_login, "__name__", "<callable>"),
        )

        start_time = time.perf_counter()
        try:
            result = prompt_for_login(
                database_path=database_path,
                parent=self,
                initial_username=self._last_username,
            )
        except Exception as exc:  # pragma: no cover - GUI path
            self.logger.error("Login dialog crashed: %s", exc, exc_info=True)
            QMessageBox.critical(
                self,
                "Authentication Error",
                f"The sign-in dialog encountered an unexpected error.\n\n{exc}",
            )
            return False
        finally:
            elapsed = time.perf_counter() - start_time
            self.logger.debug("Login dialog duration %.2fs", elapsed)

        if not result:
            self.logger.warning("Login dialog dismissed without authentication")
            return False

        self._session_context = result
        username = str(result.get("username") or "unknown")
        self._last_username = username
        role = result.get("role") or result.get("session", {}).get("role")
        workspace_ready = bool(result.get("workspace_ready"))
        badge = result.get("preference_badge")
        self._update_preference_badge(badge)

        status_parts = [f"Signed in as {username}"]
        if role:
            status_parts.append(f"({role})")
        if not workspace_ready:
            status_parts.append("- preferences fallback applied")
        self._update_status_bar(" ".join(status_parts))
        self.logger.info(
            "Authenticated GUI session for user %s (role=%s, workspace_ready=%s)",
            username,
            role or "unknown",
            workspace_ready,
        )
        return True

    def _create_interface_toggle_button(self, header_layout):
        """Create and configure the interface toggle button."""
        try:
            from src.file_explorer.features.hub_interface_toggle import (
                HubInterfaceToggle,
            )

            adapter = getattr(self, "hub_preferences_adapter", None)
            self.interface_toggle = HubInterfaceToggle(preferences_adapter=adapter)
            self.interface_toggle.mode_changed.connect(self._on_interface_mode_changed)
            header_layout.addWidget(self.interface_toggle)

        except Exception as e:
            self.logger.error(f"Failed to create interface toggle: {e}")

    def _create_preference_badge_display(self, header_layout) -> None:
        """Add a compact badge showing the authenticated preference state."""

        if not PYQT5_AVAILABLE:
            return

        badge = QLabel("Not signed in")
        badge.setObjectName("preferenceBadge")
        badge.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        badge.setMinimumWidth(200)
        badge.setStyleSheet(
            """
            QLabel#preferenceBadge {
                padding: 6px 12px;
                border-radius: 12px;
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: bold;
            }
            """
        )
        header_layout.addWidget(badge)
        self.preference_badge_label = badge
        self._update_preference_badge(None)

    def _update_preference_badge(
        self,
        badge: Optional[Dict[str, Any]],
        *,
        fallback_text: Optional[str] = None,
    ) -> None:
        self._preference_badge = badge
        if not PYQT5_AVAILABLE:
            return

        label = getattr(self, "preference_badge_label", None)
        if label is None:
            return

        if not badge:
            label.setText(fallback_text or "Not signed in")
            label.setToolTip("Sign in to personalize the workspace")
            return

        text = badge.get("text") or badge.get("label")
        label.setText(str(text or fallback_text or "Signed in"))

        tooltip_lines = []
        user = badge.get("user")
        if user:
            tooltip_lines.append(f"User: {user}")
        pref_id = badge.get("preferences_id")
        if pref_id:
            tooltip_lines.append(f"Preferences: {pref_id}")
        layout_hint = badge.get("layout")
        if layout_hint:
            tooltip_lines.append(f"Layout: {layout_hint}")
        favorites = badge.get("favorite_tools")
        if isinstance(favorites, list) and favorites:
            preview = ", ".join(str(item) for item in favorites[:3])
            tooltip_lines.append(f"Favorites: {preview}")
        label.setToolTip("\n".join(tooltip_lines) or "Authenticated session")

    def _create_multi_pane_interface(self):
        """Create the Multi-Pane Explorer interface."""
        try:
            from src.file_explorer.multi_pane_explorer_simple import (
                MultiPaneExplorer,
            )

            self.multi_pane_explorer = MultiPaneExplorer()
            self.interface_stack.addWidget(self.multi_pane_explorer)

            self.logger.info("Multi-Pane Explorer interface created")

        except Exception as e:
            self.logger.error(f"Failed to create multi-pane interface: {e}")
            # Add placeholder
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_label = QLabel("Multi-Pane Explorer unavailable")
            placeholder_layout.addWidget(placeholder_label)
            self.interface_stack.addWidget(placeholder)

    def _load_and_set_interface_mode(self):
        """Load saved interface mode and set initial view."""
        try:
            from src.file_explorer.models.hub_interface_mode import (
                HubInterfaceMode,
            )

            adapter = getattr(self, "hub_preferences_adapter", None)
            if adapter:
                mode = adapter.load_interface_mode(HubInterfaceMode.MULTI_PANE)
            else:
                from src.file_explorer.services.explorer_preferences import (
                    get_explorer_preferences,
                )

                explorer_prefs = get_explorer_preferences()
                prefs = explorer_prefs.load_user_preferences()
                mode = getattr(prefs, "hub_interface_mode", None) or getattr(
                    prefs,
                    "active_hub_mode",
                    HubInterfaceMode.MULTI_PANE,
                )
                if not isinstance(mode, HubInterfaceMode):
                    mode = HubInterfaceMode(mode)

            self.current_hub_mode = mode

            # Set appropriate widget
            if mode == HubInterfaceMode.MULTI_PANE:
                self.interface_stack.setCurrentIndex(1)
            else:
                self.interface_stack.setCurrentIndex(0)

            if getattr(self, "interface_toggle", None):
                self.interface_toggle.set_mode(mode)

            self.logger.info("Interface mode set to: %s", mode.value)

        except Exception as e:
            self.logger.error("Error loading interface mode: %s", e)
            # Default to tabbed
            self.interface_stack.setCurrentIndex(0)

    def _apply_startup_focus_mode(self):
        """Hide non-tab UI so the tabbed interface is the startup focus."""
        if not PYQT5_AVAILABLE:
            return

        menu_bar = self.menuBar()
        if menu_bar:
            menu_bar.setVisible(False)

        if hasattr(self, "status_bar"):
            self.status_bar.setVisible(False)

        if hasattr(self, "header_widget"):
            self.header_widget.setVisible(False)

        if hasattr(self, "interface_toggle") and self.interface_toggle:
            self.interface_toggle.setVisible(False)
            self.interface_toggle.setEnabled(False)

        if hasattr(self, "interface_stack"):
            self.interface_stack.setCurrentIndex(0)

        if hasattr(self, "tab_widget"):
            self.tab_widget.setFocus()
            self.tab_widget.setFocusPolicy(Qt.StrongFocus)

        try:
            from src.file_explorer.models.hub_interface_mode import (
                HubInterfaceMode,
            )

            self.current_hub_mode = HubInterfaceMode.TABBED
        except Exception:
            self.current_hub_mode = "tabbed"

    def _on_interface_mode_changed(self, new_mode):
        """Handle interface mode change from toggle button."""
        try:
            from src.file_explorer.models.hub_interface_mode import (
                HubInterfaceMode,
            )

            self.current_hub_mode = new_mode

            # Switch widget
            if new_mode == HubInterfaceMode.MULTI_PANE:
                self.interface_stack.setCurrentIndex(1)
                self.logger.info("Switched to Multi-Pane Explorer")
            else:
                self.interface_stack.setCurrentIndex(0)
                self.logger.info("Switched to Tabbed Interface")

        except Exception as e:
            self.logger.error(f"Error switching interface mode: {e}")

    def _get_application_icon(self):
        """Get application icon with fallback."""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "app_icon.png")
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        except Exception:
            pass
        return QIcon()  # Return empty icon as fallback

    def show(self):
        """Show the hub interface with graceful fallback."""
        if not PYQT5_AVAILABLE:
            self.logger.error(
                "Cannot show GUI - PyQt5 is not installed. "
                "Please install PyQt5 to use the graphical interface."
            )
            self._show_command_line_interface()
            return

        if not self._login_prompt_shown:
            if not self._prompt_for_login():
                self.logger.warning("Authentication cancelled; shutting down hub")
                app = QApplication.instance()
                if app is not None:
                    app.quit()
                return
            self._login_prompt_shown = True

        try:
            super().show()
            self.logger.info("GUI Hub displayed successfully")
        except Exception as e:
            self.logger.error(f"Failed to show GUI hub: {e}")
            self._show_command_line_interface()

    def _show_command_line_interface(self):
        """Show command line interface when GUI is not available (from rfuhub.py)."""
        print("\n" + "=" * 60)
        print("RICHARD'S FILE UTILITIES - COMMAND LINE MODE")
        print("=" * 60)
        print("PyQt5 is not installed. GUI mode is not available.")
        print("\nTo install PyQt5, run:")
        print("  pip install PyQt5")
        print("\nAvailable tools (command line mode):")
        print("- Configuration management")
        print("- Logging system")
        print("- Error handling")
        print("\nFor full functionality, please install PyQt5.")
        print("=" * 60)

    # Menu callback implementations (from simple_hub.py)
    def _setup_menu_callbacks(self):
        """Setup menu callbacks for the RFU Hub."""
        if not self.menu_manager:
            return

        # File menu callbacks
        self.menu_manager.register_callback("new_project", self.new_project)
        self.menu_manager.register_callback("open_file", self.open_file)
        self.menu_manager.register_callback("save_file", self.save_file)
        self.menu_manager.register_callback("save_as_file", self.save_as_file)
        self.menu_manager.register_callback("export_data", self.export_data)
        self.menu_manager.register_callback("import_data", self.import_data)
        self.menu_manager.register_callback("print_document", self.print_document)
        self.menu_manager.register_callback("show_preferences", self.show_preferences)

        # Edit menu callbacks
        self.menu_manager.register_callback("undo", self.undo)
        self.menu_manager.register_callback("redo", self.redo)
        self.menu_manager.register_callback("cut", self.cut)
        self.menu_manager.register_callback("copy", self.copy)
        self.menu_manager.register_callback("paste", self.paste)
        self.menu_manager.register_callback("select_all", self.select_all)
        self.menu_manager.register_callback("find", self.find)
        self.menu_manager.register_callback("replace", self.replace)

        # View menu callbacks
        self.menu_manager.register_callback("zoom_in", self.zoom_in)
        self.menu_manager.register_callback("zoom_out", self.zoom_out)
        self.menu_manager.register_callback("zoom_reset", self.zoom_reset)
        self.menu_manager.register_callback("refresh", self.refresh)

        # Tools menu callbacks
        self.menu_manager.register_callback("show_options", self.show_options)
        self.menu_manager.register_callback("show_performance", self.show_performance)

        self.logger.info("Menu callbacks registered")

    def _create_styled_tool_button(self, text, tooltip, callback, primary=True):
        """Create a styled tool button with organized layout (from simple_hub.py)."""
        if not PYQT5_AVAILABLE:
            return None

        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setMinimumSize(180, 70)
        button.setMaximumSize(200, 80)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        if primary:
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {PRIMARY_BLUE}, stop:1 {DARK_BLUE});
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {LIGHT_BLUE}, stop:1 {PRIMARY_BLUE});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {DARK_BLUE}, stop:1 {DARKER_BLUE});
                }}
            """
            )
        else:
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {LIGHT_GRAY}, stop:1 {MEDIUM_GRAY});
                    color: {TEXT_DARK};
                    border: 1px solid {DARK_GRAY};
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {WHITE}, stop:1 {LIGHT_GRAY});
                    border: 1px solid {DARKER_GRAY};
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {MEDIUM_GRAY}, stop:1 {DARK_GRAY});
                }}
            """
            )

        return button

    # Hub Integration Methods (from hub.py)
    def register_tool(self, tool_name: str, tool_instance) -> bool:
        """Register a tool with the hub."""
        try:
            if tool_name in self.registered_tools:
                self.registered_tools[tool_name] = tool_instance
            else:
                self.registered_tools[tool_name] = tool_instance
                self.tool_status[tool_name] = {
                    "status": "registered",
                    "last_activity": datetime.now(),
                    "progress": 0,
                    "current_operation": None,
                }

            if PYQT5_AVAILABLE and hasattr(self, "tool_registered"):
                self.tool_registered.emit(tool_name, tool_instance)

            self._update_status_bar(f"Tool registered: {tool_name}")
            self.logger.info(f"Tool registered: {tool_name}")
            return True

        except Exception as e:
            self._update_status_bar(f"Failed to register tool {tool_name}: {e}")
            self.logger.error(f"Failed to register tool {tool_name}: {e}")
            return False

    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the hub."""
        try:
            if tool_name in self.registered_tools:
                del self.registered_tools[tool_name]
                if tool_name in self.tool_status:
                    del self.tool_status[tool_name]

                self._release_tool_resources(tool_name)

                if PYQT5_AVAILABLE and hasattr(self, "tool_unregistered"):
                    self.tool_unregistered.emit(tool_name)

                self._update_status_bar(f"Tool unregistered: {tool_name}")
                self.logger.info(f"Tool unregistered: {tool_name}")
                return True
            return False

        except Exception as e:
            self._update_status_bar(f"Failed to unregister tool {tool_name}: {e}")
            self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False

    def update_tool_progress(self, tool_name: str, percentage: int, message: str = ""):
        """Update tool progress in hub."""
        if tool_name in self.tool_status:
            self.tool_status[tool_name].update(
                {
                    "progress": percentage,
                    "current_operation": message,
                    "last_activity": datetime.now(),
                }
            )

            if PYQT5_AVAILABLE and hasattr(self, "tool_progress_updated"):
                self.tool_progress_updated.emit(tool_name, percentage, message)

            if percentage < 100:
                self._update_status_bar(f"{tool_name}: {message} ({percentage}%)")
            else:
                self._update_status_bar(f"{tool_name}: Completed")

    def _release_tool_resources(self, tool_name: str):
        """Release all resources allocated to a tool."""
        for resource_type, resource_info in self.resource_manager.items():
            if resource_info.get("allocated_to") == tool_name:
                resource_info["available"] = True
                resource_info["allocated_to"] = None
                resource_info.pop("allocated_at", None)

    def _update_status_bar(self, message: str):
        """Update the status bar with a message."""
        if PYQT5_AVAILABLE and hasattr(self, "status_bar"):
            self.status_bar.showMessage(message, 5000)

    # Signal Handlers (from hub.py)
    def _on_tool_registered(self, tool_name: str, tool_instance):
        """Handle tool registration event."""
        pass  # Additional processing if needed

    def _on_tool_unregistered(self, tool_name: str):
        """Handle tool unregistration event."""
        pass  # Additional processing if needed

    def _on_tool_progress_updated(self, tool_name: str, percentage: int, message: str):
        """Handle tool progress update event."""
        pass  # Additional processing if needed

    def _on_tool_status_changed(self, tool_name: str, status: str):
        """Handle tool status change event."""
        pass  # Additional processing if needed

    def _on_hub_event_broadcast(self, sender: str, event_type: str, data: Dict):
        """Handle hub event broadcast."""
        pass  # Additional processing if needed

    # Menu Callback Implementations
    def new_project(self):
        """Create a new project."""
        self._update_status_bar("New Project - Feature coming soon...")
        self.logger.info("New Project requested")

    def open_file(self):
        """Open a file."""
        self._update_status_bar("Open File - Feature coming soon...")
        self.logger.info("Open File requested")

    def save_file(self):
        """Save current work."""
        self._update_status_bar("Save File - Feature coming soon...")
        self.logger.info("Save File requested")

    def save_as_file(self):
        """Save with new name."""
        self._update_status_bar("Save As - Feature coming soon...")
        self.logger.info("Save As requested")

    def export_data(self):
        """Export data."""
        self._update_status_bar("Export Data - Feature coming soon...")
        self.logger.info("Export Data requested")

    def import_data(self):
        """Import data."""
        self._update_status_bar("Import Data - Feature coming soon...")
        self.logger.info("Import Data requested")

    def launch_tool(self, tool_name: str, *args, **kwargs):
        """
        Generic tool launcher interface for enterprise integration testing.

        This method provides a unified interface for launching any tool in the RFU suite.
        It maps tool names to their corresponding open_ methods.

        Args:
            tool_name (str): Name of the tool to launch
            *args: Additional arguments to pass to the tool
            **kwargs: Additional keyword arguments to pass to the tool

        Returns:
            bool: True if tool launched successfully, False otherwise
        """
        try:
            # Normalize tool name to method name
            method_name = (
                f"open_{tool_name.lower().replace(' ', '_').replace('-', '_')}"
            )

            # Check if method exists
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    method(*args, **kwargs)
                    self.logger.info(f"Successfully launched tool: {tool_name}")
                    return True
                else:
                    self.logger.error(f"Tool method {method_name} is not callable")
                    return False
            else:
                # Try alternative naming patterns
                alternative_names = [
                    f"open_{tool_name.lower()}",
                    f"start_{tool_name.lower()}",
                    f"show_{tool_name.lower()}",
                    tool_name.lower().replace(" ", "_"),
                ]

                for alt_name in alternative_names:
                    if hasattr(self, alt_name):
                        method = getattr(self, alt_name)
                        if callable(method):
                            method(*args, **kwargs)
                            self.logger.info(
                                f"Successfully launched tool: {tool_name} via {alt_name}"
                            )
                            return True

                self.logger.error(f"Tool method not found for: {tool_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error launching tool {tool_name}: {str(e)}")
            return False

    def get_available_tools(self):
        """
        Get list of available tools for enterprise testing.

        Returns:
            list: List of available tool names
        """
        import inspect

        tools = []

        # Find all open_ methods
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("open_") and name != "open_file":
                tool_name = name[5:].replace("_", " ").title()
                tools.append(tool_name)

        return sorted(tools)

    def print_document(self):
        """Print current document."""
        self._update_status_bar("Print Document - Feature coming soon...")
        self.logger.info("Print Document requested")

    def show_preferences(self):
        """Display the sharing preferences dialog for the current session."""

        if not PYQT5_AVAILABLE:
            self.logger.info("Preferences view unavailable without PyQt5")
            return

        if not self._session_context:
            self._update_status_bar("Sign in to manage preferences")
            QMessageBox.information(
                self,
                "Preferences",
                "You must sign in before editing preferences.",
            )
            return

        database_path = self._get_identity_database_path()
        if not database_path:
            message = "Identity database is not configured; cannot open preferences."
            self._update_status_bar(message)
            QMessageBox.warning(self, "Preferences", message)
            return

        try:
            from src.rfu.preferences import PreferencesViewDialog

            dialog = PreferencesViewDialog(
                database_path=database_path,
                session=self._session_context,
                parent=self,
            )
        except Exception as exc:
            self.logger.warning("Unable to open preferences dialog: %s", exc)
            QMessageBox.warning(
                self,
                "Preferences",
                f"Preferences dialog unavailable: {exc}",
            )
            return

        self.logger.info("Opening preferences dialog for %s", self._last_username)
        dialog.exec_()
        self._update_status_bar("Preferences dialog closed")

    def show_performance(self, *_, **__):
        """Stub handler for the Performance menu item."""

        self.logger.info("Performance view requested (stub)")
        if not PYQT5_AVAILABLE:
            self._update_status_bar("Performance view unavailable without PyQt5")
            return

        try:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "Performance",
                "Performance view is not yet implemented.",
            )
        except Exception as exc:
            self.logger.debug("Unable to show performance stub dialog: %s", exc)

    def undo(self):
        """Undo last action."""
        self._update_status_bar("Undo - Feature coming soon...")
        self.logger.info("Undo requested")

    def redo(self):
        """Redo last action."""
        self._update_status_bar("Redo - Feature coming soon...")
        self.logger.info("Redo requested")

    def cut(self):
        """Cut to clipboard."""
        self._update_status_bar("Cut - Feature coming soon...")
        self.logger.info("Cut requested")

    def copy(self):
        """Copy to clipboard."""
        self._update_status_bar("Copy - Feature coming soon...")
        self.logger.info("Copy requested")

    def paste(self):
        """Paste from clipboard."""
        self._update_status_bar("Paste - Feature coming soon...")
        self.logger.info("Paste requested")

    def select_all(self):
        """Select all items."""
        self._update_status_bar("Select All - Feature coming soon...")
        self.logger.info("Select All requested")

    def find(self):
        """Find text or items."""
        self._update_status_bar("Find - Feature coming soon...")
        self.logger.info("Find requested")

    def replace(self):
        """Find and replace."""
        self._update_status_bar("Replace - Feature coming soon...")
        self.logger.info("Replace requested")

    def zoom_in(self):
        """Increase zoom level."""
        self._update_status_bar("Zoom In - Feature coming soon...")
        self.logger.info("Zoom In requested")

    def zoom_out(self):
        """Decrease zoom level."""
        self._update_status_bar("Zoom Out - Feature coming soon...")
        self.logger.info("Zoom Out requested")

    def zoom_reset(self):
        """Reset zoom to default."""
        self._update_status_bar("Zoom Reset - Feature coming soon...")
        self.logger.info("Zoom Reset requested")

    def refresh(self):
        """Refresh current view."""
        if hasattr(self, "load_recent_logs"):
            self.load_recent_logs()
        self._update_status_bar("View refreshed")
        self.logger.info("Refresh requested")

    def show_options(self):
        """Show tool options."""
        self._update_status_bar("Options - Feature coming soon...")
        self.logger.info("Options requested")

    def show_documentation(self):
        """Show documentation."""
        self._update_status_bar("Documentation - Feature coming soon...")
        self.logger.info("Documentation requested")

    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        self._update_status_bar("Shortcuts - Feature coming soon...")
        self.logger.info("Shortcuts requested")

    def show_about(self):
        """Show about dialog."""
        self._update_status_bar("RFU Hub - File Processing and Utility Tools")
        self.logger.info("About dialog requested")

    # Tab Creation Methods
    def _create_main_tab(self, tab_widget):
        """Create the main control tab."""
        main_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(main_tab)

        # Welcome section
        welcome_label = QtWidgets.QLabel("<h2>Welcome to RFU Hub</h2>")
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(welcome_label)

        # Description
        desc_label = QtWidgets.QLabel(
            "<p>RFU Hub is your comprehensive file processing and utility toolkit. "
            "Use the tabs above to access various tools and utilities.</p>"
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(desc_label)

        # Quick action buttons
        quick_actions_group = QtWidgets.QGroupBox("Quick Actions")
        quick_layout = QtWidgets.QGridLayout(quick_actions_group)

        # File operations
        file_catalog_btn = QtWidgets.QPushButton("📁 File Catalog")
        file_catalog_btn.setMinimumHeight(40)
        file_catalog_btn.clicked.connect(self.open_file_catalog)
        quick_layout.addWidget(file_catalog_btn, 0, 0)

        # Network tools
        network_btn = QtWidgets.QPushButton("🌐 Network Tools")
        network_btn.setMinimumHeight(40)
        network_btn.clicked.connect(self.open_network_tools)
        quick_layout.addWidget(network_btn, 0, 1)

        # Security tools
        security_btn = QtWidgets.QPushButton("🔒 Security Tools")
        security_btn.setMinimumHeight(40)
        security_btn.clicked.connect(self.open_security_tools)
        quick_layout.addWidget(security_btn, 1, 0)

        # System tools
        system_btn = QtWidgets.QPushButton("⚙️ System Tools")
        system_btn.setMinimumHeight(40)
        system_btn.clicked.connect(self.open_system_tools)
        quick_layout.addWidget(system_btn, 1, 1)

        layout.addWidget(quick_actions_group)
        layout.addStretch()

        return main_tab

    def _create_file_operations_tab(self, tab_widget):
        """Create the file operations tab."""
        file_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(file_tab)

        # File operations group
        file_ops_group = QtWidgets.QGroupBox("File Operations")
        file_ops_layout = QtWidgets.QGridLayout(file_ops_group)

        # File touch tool
        touch_btn = QtWidgets.QPushButton("📝 File Touch")
        touch_btn.setToolTip("Create or update file timestamps")
        touch_btn.clicked.connect(self.open_file_touch)
        file_ops_layout.addWidget(touch_btn, 0, 0)

        # File splitter
        splitter_btn = QtWidgets.QPushButton("✂️ File Splitter")
        splitter_btn.setToolTip("Split large files into smaller chunks")
        splitter_btn.clicked.connect(self.open_file_splitter)
        file_ops_layout.addWidget(splitter_btn, 0, 1)

        # Secure delete
        secure_delete_btn = QtWidgets.QPushButton("🗑️ Secure Delete")
        secure_delete_btn.setToolTip("Securely delete files")
        secure_delete_btn.clicked.connect(self.open_secure_delete)
        file_ops_layout.addWidget(secure_delete_btn, 0, 2)

        # Compression tools
        compress_btn = QtWidgets.QPushButton("📦 Compression")
        compress_btn.setToolTip("Compress and decompress files")
        compress_btn.clicked.connect(self.open_compression_tools)
        file_ops_layout.addWidget(compress_btn, 1, 0)

        # File catalog
        catalog_btn = QtWidgets.QPushButton("📋 File Catalog")
        catalog_btn.setToolTip("Generate detailed file catalogs")
        catalog_btn.clicked.connect(self.open_file_catalog)
        file_ops_layout.addWidget(catalog_btn, 1, 1)

        # Duplicate finder
        duplicate_btn = QtWidgets.QPushButton("🔍 Duplicate Finder")
        duplicate_btn.setToolTip("Find and manage duplicate files")
        duplicate_btn.clicked.connect(self.open_duplicate_finder)
        file_ops_layout.addWidget(duplicate_btn, 1, 2)

        layout.addWidget(file_ops_group)

        # Metadata tools group
        metadata_group = QtWidgets.QGroupBox("Metadata Tools")
        metadata_layout = QtWidgets.QGridLayout(metadata_group)

        # Image metadata
        image_meta_btn = QtWidgets.QPushButton("🖼️ Image Metadata")
        image_meta_btn.setToolTip("Edit image metadata and EXIF data")
        image_meta_btn.clicked.connect(self.open_image_metadata)
        metadata_layout.addWidget(image_meta_btn, 0, 0)

        # Office metadata
        office_meta_btn = QtWidgets.QPushButton("📄 Office Metadata")
        office_meta_btn.setToolTip("Edit office document metadata")
        office_meta_btn.clicked.connect(self.open_office_metadata)
        metadata_layout.addWidget(office_meta_btn, 0, 1)

        # PDF tools
        pdf_btn = QtWidgets.QPushButton("📑 PDF Tools")
        pdf_btn.setToolTip("PDF processing and metadata tools")
        pdf_btn.clicked.connect(self.open_pdf_tools)
        metadata_layout.addWidget(pdf_btn, 0, 2)

        layout.addWidget(metadata_group)
        layout.addStretch()

    def _create_network_tools_tab(self, tab_widget):
        """Create the network tools tab."""
        network_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(network_tab)

        # Network operations group
        network_group = QtWidgets.QGroupBox("Network Operations")
        network_layout = QtWidgets.QGridLayout(network_group)

        # Network transfer
        transfer_btn = QtWidgets.QPushButton("🚀 Network Transfer")
        transfer_btn.setToolTip("Transfer files over network")
        transfer_btn.clicked.connect(self.open_network_transfer)
        network_layout.addWidget(transfer_btn, 0, 0)

        # Network scan
        scan_btn = QtWidgets.QPushButton("🔍 Network Scan")
        scan_btn.setToolTip("Scan network for devices and services")
        scan_btn.clicked.connect(self.open_network_scan)
        network_layout.addWidget(scan_btn, 0, 1)

        # Port scanner
        port_btn = QtWidgets.QPushButton("🔌 Port Scanner")
        port_btn.setToolTip("Scan for open ports on network hosts")
        port_btn.clicked.connect(self.open_port_scanner)
        network_layout.addWidget(port_btn, 0, 2)

        # Network monitor
        monitor_btn = QtWidgets.QPushButton("📊 Network Monitor")
        monitor_btn.setToolTip("Monitor network traffic and connections")
        monitor_btn.clicked.connect(self.open_network_monitor)
        network_layout.addWidget(monitor_btn, 1, 0)

        # Bandwidth test
        bandwidth_btn = QtWidgets.QPushButton("📈 Bandwidth Test")
        bandwidth_btn.setToolTip("Test network bandwidth and latency")
        bandwidth_btn.clicked.connect(self.open_bandwidth_test)
        network_layout.addWidget(bandwidth_btn, 1, 1)

        # Wake on LAN
        wol_btn = QtWidgets.QPushButton("⚡ Wake on LAN")
        wol_btn.setToolTip("Wake up network devices remotely")
        wol_btn.clicked.connect(self.open_wake_on_lan)
        network_layout.addWidget(wol_btn, 1, 2)

        layout.addWidget(network_group)
        layout.addStretch()

        return network_tab

    def _create_security_tools_tab(self, tab_widget):
        """Create the security tools tab."""
        security_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(security_tab)

        # Encryption group
        encryption_group = QtWidgets.QGroupBox("Encryption & Security")
        encryption_layout = QtWidgets.QGridLayout(encryption_group)

        # Encrypt/Decrypt
        encrypt_btn = QtWidgets.QPushButton("🔐 Encrypt/Decrypt")
        encrypt_btn.setToolTip("Encrypt and decrypt files")
        encrypt_btn.clicked.connect(self.open_encrypt_decrypt)
        encryption_layout.addWidget(encrypt_btn, 0, 0)

        # Hash calculator
        hash_btn = QtWidgets.QPushButton("🔢 Hash Calculator")
        hash_btn.setToolTip("Calculate file hashes and checksums")
        hash_btn.clicked.connect(self.open_hash_calculator)
        encryption_layout.addWidget(hash_btn, 0, 1)

        # Password generator
        password_btn = QtWidgets.QPushButton("🎲 Password Generator")
        password_btn.setToolTip("Generate secure passwords")
        password_btn.clicked.connect(self.open_password_generator)
        encryption_layout.addWidget(password_btn, 0, 2)

        # Security preferences
        security_prefs_btn = QtWidgets.QPushButton("⚙️ Security Preferences")
        security_prefs_btn.setToolTip("Configure security settings")
        security_prefs_btn.clicked.connect(self.open_security_preferences)
        encryption_layout.addWidget(security_prefs_btn, 1, 0)

        # Key manager
        key_mgr_btn = QtWidgets.QPushButton("🔑 Key Manager")
        key_mgr_btn.setToolTip("Manage encryption keys")
        key_mgr_btn.clicked.connect(self.open_key_manager)
        encryption_layout.addWidget(key_mgr_btn, 1, 1)

        # Secure notes
        notes_btn = QtWidgets.QPushButton("📝 Secure Notes")
        notes_btn.setToolTip("Create and manage encrypted notes")
        notes_btn.clicked.connect(self.open_secure_notes)
        encryption_layout.addWidget(notes_btn, 1, 2)

        layout.addWidget(encryption_group)
        layout.addStretch()

        return security_tab

    def _create_system_tools_tab(self, tab_widget):
        """Create the system tools tab."""
        system_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(system_tab)

        # System utilities group
        system_group = QtWidgets.QGroupBox("System Utilities")
        system_layout = QtWidgets.QGridLayout(system_group)

        # Clipboard manager
        clipboard_btn = QtWidgets.QPushButton("📋 Clipboard Manager")
        clipboard_btn.setToolTip("Enhanced clipboard management")
        clipboard_btn.clicked.connect(self.open_clipboard_manager)
        system_layout.addWidget(clipboard_btn, 0, 0)

        # System monitor
        monitor_btn = QtWidgets.QPushButton("📊 System Monitor")
        monitor_btn.setToolTip("Monitor system performance")
        monitor_btn.clicked.connect(self.open_system_monitor)
        system_layout.addWidget(monitor_btn, 0, 1)

        # Registry tools
        registry_btn = QtWidgets.QPushButton("🗂️ Registry Tools")
        registry_btn.setToolTip("Windows registry utilities")
        registry_btn.clicked.connect(self.open_registry_tools)
        system_layout.addWidget(registry_btn, 0, 2)

        # Disk tools
        disk_btn = QtWidgets.QPushButton("💾 Disk Tools")
        disk_btn.setToolTip("Disk analysis and cleanup tools")
        disk_btn.clicked.connect(self.open_disk_tools)
        system_layout.addWidget(disk_btn, 1, 0)

        # Process manager
        process_btn = QtWidgets.QPushButton("⚙️ Process Manager")
        process_btn.setToolTip("Advanced process management")
        process_btn.clicked.connect(self.open_process_manager)
        system_layout.addWidget(process_btn, 1, 1)

        # Service manager
        service_btn = QtWidgets.QPushButton("🔧 Service Manager")
        service_btn.setToolTip("Manage Windows services")
        service_btn.clicked.connect(self.open_service_manager)
        system_layout.addWidget(service_btn, 1, 2)

        layout.addWidget(system_group)
        layout.addStretch()

    def _create_logs_tab(self, tab_widget):
        """Create the logs and status tab."""
        logs_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(logs_tab)

        # Controls
        controls_group = QtWidgets.QGroupBox("Log Controls")
        controls_layout = QtWidgets.QHBoxLayout(controls_group)

        refresh_btn = QtWidgets.QPushButton("🔄 Refresh Logs")
        refresh_btn.clicked.connect(self.load_recent_logs)
        controls_layout.addWidget(refresh_btn)

        clear_btn = QtWidgets.QPushButton("🗑️ Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)

        save_btn = QtWidgets.QPushButton("💾 Save Logs")
        save_btn.clicked.connect(self.save_logs)
        controls_layout.addWidget(save_btn)

        controls_layout.addStretch()
        layout.addWidget(controls_group)

        # Log display
        self.log_display = QtWidgets.QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QtGui.QFont("Consolas", 9))
        layout.addWidget(self.log_display)

        return logs_tab

    # Tool Opening Methods
    def open_file_catalog(self):
        """Open file catalog tool."""
        try:
            from ..utilities.file_operations.file_catalog import FileCatalogGUI

            tool = FileCatalogGUI()
            tool.show()
            self._update_status_bar("File Catalog opened")
            self.logger.info("File Catalog tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening File Catalog: {str(e)}")
            self.logger.error(f"Error opening File Catalog: {str(e)}")

    def open_file_touch(self):
        """Open file touch tool."""
        try:
            try:
                from .tools.metadata.file_touch import FileTouchGUI
            except ImportError:
                from tools.metadata.file_touch import FileTouchGUI

            tool = FileTouchGUI()
            tool.show()
            self._update_status_bar("File Touch opened")
            self.logger.info("File Touch tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening File Touch: {str(e)}")
            self.logger.error(f"Error opening File Touch: {str(e)}")

    def open_file_splitter(self):
        """Open file splitter tool."""
        try:
            from ..utilities.file_operations.file_splitter import (
                FileSplitJoinGUI,
            )

            tool = FileSplitJoinGUI()
            tool.show()
            self._update_status_bar("File Splitter opened")
            self.logger.info("File Splitter tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening File Splitter: {str(e)}")
            self.logger.error(f"Error opening File Splitter: {str(e)}")

    def open_secure_delete(self):
        """Open secure delete tool."""
        try:
            try:
                from src.tools.file_operations.secure_delete import SecureDeleteGUI
            except ImportError:
                from tools.file_operations.secure_delete import SecureDeleteGUI

            tool = SecureDeleteGUI()
            tool.show()
            self._update_status_bar("Secure Delete opened")
            self.logger.info("Secure Delete tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Secure Delete: {str(e)}")
            self.logger.error(f"Error opening Secure Delete: {str(e)}")

    def open_compression_tools(self):
        """Open compression tools."""
        try:
            from ..utilities.file_operations.compression import CompressionGUI

            tool = CompressionGUI()
            tool.show()
            self._update_status_bar("Compression Tools opened")
            self.logger.info("Compression Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Compression Tools: {str(e)}")
            self.logger.error(f"Error opening Compression Tools: {str(e)}")

    def open_duplicate_finder(self):
        """Open duplicate finder tool."""
        try:
            from ..utilities.file_operations.duplicate_finder import (
                DuplicateFinderGUI,
            )

            tool = DuplicateFinderGUI()
            tool.show()
            self._update_status_bar("Duplicate Finder opened")
            self.logger.info("Duplicate Finder tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Duplicate Finder: {str(e)}")
            self.logger.error(f"Error opening Duplicate Finder: {str(e)}")

    def open_image_metadata(self):
        """Open image metadata editor."""
        try:
            from ..utilities.metadata.image_metadata import ImageMetadataGUI

            tool = ImageMetadataGUI()
            tool.show()
            self._update_status_bar("Image Metadata Editor opened")
            self.logger.info("Image Metadata Editor opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Image Metadata Editor: {str(e)}")
            self.logger.error(f"Error opening Image Metadata Editor: {str(e)}")

    def open_office_metadata(self):
        """Open office metadata editor."""
        try:
            from ..tools.metadata.office_metadata import OfficeMetadataGUI

            tool = OfficeMetadataGUI()
            tool.show()
            self._update_status_bar("Office Metadata Editor opened")
            self.logger.info("Office Metadata Editor opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Office Metadata Editor: {str(e)}")
            self.logger.error(f"Error opening Office Metadata Editor: {str(e)}")

    def open_pdf_tools(self):
        """Open PDF tools."""
        try:
            from ..tools.pdf_tools.widgets.enhanced_pdf_tools_widget import (
                EnhancedPDFToolsWidget,
            )

            tool = EnhancedPDFToolsWidget()
            tool.show()
            self._update_status_bar("PDF Tools opened")
            self.logger.info("PDF Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening PDF Tools: {str(e)}")
            self.logger.error(f"Error opening PDF Tools: {str(e)}")

    def open_network_transfer(self):
        """Open network transfer tool."""
        try:
            from src.tools.network.transfer.network_transfer import (
                NetworkTransferGUI,
            )

            tool = NetworkTransferGUI()
            tool.show()
            self._update_status_bar("Network Transfer opened")
            self.logger.info("Network Transfer tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Network Transfer: {str(e)}")
            self.logger.error(f"Error opening Network Transfer: {str(e)}")

    def open_network_scan(self):
        """Open network scan tool."""
        try:
            from ..tools.network.scanner.network_scanner import (
                NetworkScannerGUI,
            )

            tool = NetworkScannerGUI()
            tool.show()
            self._update_status_bar("Network Scanner opened")
            self.logger.info("Network Scanner tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Network Scanner: {str(e)}")
            self.logger.error(f"Error opening Network Scanner: {str(e)}")

    def open_network_tools(self):
        """Open general network tools."""
        self.tab_widget.setCurrentIndex(2)  # Switch to network tools tab
        self._update_status_bar("Switched to Network Tools tab")
        self.logger.info("Switched to Network Tools tab")

    def open_security_tools(self):
        """Open general security tools."""
        self.tab_widget.setCurrentIndex(3)  # Switch to security tools tab
        self._update_status_bar("Switched to Security Tools tab")
        self.logger.info("Switched to Security Tools tab")

    def open_system_tools(self):
        """Open general system tools."""
        self.tab_widget.setCurrentIndex(4)  # Switch to system tools tab
        self._update_status_bar("Switched to System Tools tab")

    # Additional tool opening methods for completeness
    def open_port_scanner(self):
        """Open port scanner tool."""
        try:
            from ..utilities.network.port_scanner import PortScannerGUI

            tool = PortScannerGUI()
            tool.show()
            self._update_status_bar("Port Scanner opened")
            self.logger.info("Port Scanner tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Port Scanner: {str(e)}")
            self.logger.error(f"Error opening Port Scanner: {str(e)}")

    def open_network_monitor(self):
        """Open network monitor tool."""
        try:
            from ..utilities.network.network_monitor import NetworkMonitorGUI

            tool = NetworkMonitorGUI()
            tool.show()
            self._update_status_bar("Network Monitor opened")
            self.logger.info("Network Monitor tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Network Monitor: {str(e)}")
            self.logger.error(f"Error opening Network Monitor: {str(e)}")

    def open_bandwidth_test(self):
        """Open bandwidth test tool."""
        try:
            from ..utilities.network.bandwidth_test import BandwidthTestGUI

            tool = BandwidthTestGUI()
            tool.show()
            self._update_status_bar("Bandwidth Test opened")
            self.logger.info("Bandwidth Test tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Bandwidth Test: {str(e)}")
            self.logger.error(f"Error opening Bandwidth Test: {str(e)}")

    def open_wake_on_lan(self):
        """Open Wake on LAN tool."""
        try:
            from ..utilities.network.wake_on_lan import WakeOnLANGUI

            tool = WakeOnLANGUI()
            tool.show()
            self._update_status_bar("Wake on LAN opened")
            self.logger.info("Wake on LAN tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Wake on LAN: {str(e)}")
            self.logger.error(f"Error opening Wake on LAN: {str(e)}")

    def open_encrypt_decrypt(self):
        """Open encrypt/decrypt tool."""
        try:
            from src.tools.security.encryption.en_and_decrypt import (
                EnAndDecryptGUI,
            )

            tool = EnAndDecryptGUI()
            tool.show()
            self._update_status_bar("Encrypt/Decrypt opened")
            self.logger.info("Encrypt/Decrypt tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Encrypt/Decrypt: {str(e)}")
            self.logger.error(f"Error opening Encrypt/Decrypt: {str(e)}")

    def open_hash_calculator(self):
        """Open hash calculator tool."""
        try:
            from ..utilities.security.hash_calculator import HashCalculatorGUI

            tool = HashCalculatorGUI()
            tool.show()
            self._update_status_bar("Hash Calculator opened")
            self.logger.info("Hash Calculator tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Hash Calculator: {str(e)}")
            self.logger.error(f"Error opening Hash Calculator: {str(e)}")

    def open_password_generator(self):
        """Open password generator tool."""
        try:
            from ..utilities.security.password_generator import (
                PasswordGeneratorGUI,
            )

            tool = PasswordGeneratorGUI()
            tool.show()
            self._update_status_bar("Password Generator opened")
            self.logger.info("Password Generator tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Password Generator: {str(e)}")
            self.logger.error(f"Error opening Password Generator: {str(e)}")

    def open_security_preferences(self):
        """Open security preferences tool."""
        try:
            from ..utilities.security.security_preferences import (
                SecurityPreferencesGUI,
            )

            tool = SecurityPreferencesGUI()
            tool.show()
            self._update_status_bar("Security Preferences opened")
            self.logger.info("Security Preferences tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Security Preferences: {str(e)}")
            self.logger.error(f"Error opening Security Preferences: {str(e)}")

    def open_key_manager(self):
        """Open key manager tool."""
        try:
            from ..utilities.security.key_manager import KeyManagerGUI

            tool = KeyManagerGUI()
            tool.show()
            self._update_status_bar("Key Manager opened")
            self.logger.info("Key Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Key Manager: {str(e)}")
            self.logger.error(f"Error opening Key Manager: {str(e)}")

    def open_secure_notes(self):
        """Open secure notes tool."""
        try:
            from ..utilities.security.secure_notes import SecureNotesGUI

            tool = SecureNotesGUI()
            tool.show()
            self._update_status_bar("Secure Notes opened")
            self.logger.info("Secure Notes tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Secure Notes: {str(e)}")
            self.logger.error(f"Error opening Secure Notes: {str(e)}")

    def open_clipboard_manager(self):
        """Open clipboard manager tool."""
        try:
            from ..utilities.system.clipboard_manager import (
                ClipboardManagerGUI,
            )

            tool = ClipboardManagerGUI()
            tool.show()
            self._update_status_bar("Clipboard Manager opened")
            self.logger.info("Clipboard Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Clipboard Manager: {str(e)}")
            self.logger.error(f"Error opening Clipboard Manager: {str(e)}")

    def open_system_monitor(self):
        """Open system monitor tool."""
        try:
            from ..utilities.system.system_monitor import SystemMonitorGUI

            tool = SystemMonitorGUI()
            tool.show()
            self._update_status_bar("System Monitor opened")
            self.logger.info("System Monitor tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening System Monitor: {str(e)}")
            self.logger.error(f"Error opening System Monitor: {str(e)}")

    def open_registry_tools(self):
        """Open registry tools."""
        try:
            from ..utilities.system.registry_tools import RegistryToolsGUI

            tool = RegistryToolsGUI()
            tool.show()
            self._update_status_bar("Registry Tools opened")
            self.logger.info("Registry Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Registry Tools: {str(e)}")
            self.logger.error(f"Error opening Registry Tools: {str(e)}")

    def open_disk_tools(self):
        """Open disk tools."""
        try:
            from ..utilities.system.disk_tools import DiskToolsGUI

            tool = DiskToolsGUI()
            tool.show()
            self._update_status_bar("Disk Tools opened")
            self.logger.info("Disk Tools opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Disk Tools: {str(e)}")
            self.logger.error(f"Error opening Disk Tools: {str(e)}")

    def open_process_manager(self):
        """Open process manager tool."""
        try:
            from ..utilities.system.process_manager import ProcessManagerGUI

            tool = ProcessManagerGUI()
            tool.show()
            self._update_status_bar("Process Manager opened")
            self.logger.info("Process Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Process Manager: {str(e)}")
            self.logger.error(f"Error opening Process Manager: {str(e)}")

    def open_service_manager(self):
        """Open service manager tool."""
        try:
            from ..utilities.system.service_manager import ServiceManagerGUI

            tool = ServiceManagerGUI()
            tool.show()
            self._update_status_bar("Service Manager opened")
            self.logger.info("Service Manager tool opened")
        except Exception as e:
            self._update_status_bar(f"Error opening Service Manager: {str(e)}")
            self.logger.error(f"Error opening Service Manager: {str(e)}")

    def closeEvent(self, event):
        """Ensure validator notifier is released before closing."""
        self._stop_idle_watchdog_timer()
        self._teardown_validator_notifications()
        if PYQT5_AVAILABLE:
            super().closeEvent(event)
        elif event is not None:
            try:
                event.accept()
            except Exception:
                pass

    # Log management methods
    def load_recent_logs(self):
        """Load and display recent log entries."""
        if hasattr(self, "log_display"):
            try:
                # Get recent log entries from the logger
                log_entries = []
                if hasattr(self.logger, "handlers"):
                    for handler in self.logger.handlers:
                        if hasattr(handler, "get_recent_logs"):
                            log_entries.extend(handler.get_recent_logs())

                if log_entries:
                    self.log_display.clear()
                    for entry in log_entries[-100:]:  # Show last 100 entries
                        self.log_display.append(entry)
                else:
                    self.log_display.setText("No recent log entries found.")

                self._update_status_bar("Logs refreshed")
            except Exception as e:
                self.log_display.setText(f"Error loading logs: {str(e)}")
                self.logger.error(f"Error loading logs: {str(e)}")

    def clear_logs(self):
        """Clear the log display."""
        if hasattr(self, "log_display"):
            self.log_display.clear()
            self._update_status_bar("Logs cleared")
            self.logger.info("Log display cleared")

    def save_logs(self):
        """Save current logs to file."""
        if hasattr(self, "log_display"):
            try:
                from PyQt5.QtWidgets import QFileDialog

                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Logs",
                    f"rfu_hub_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "Text Files (*.txt);;All Files (*)",
                )

                if filename:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.log_display.toPlainText())
                    self._update_status_bar(f"Logs saved to {filename}")
                    self.logger.info(f"Logs saved to {filename}")
            except Exception as e:
                self._update_status_bar(f"Error saving logs: {str(e)}")
                self.logger.error(f"Error saving logs: {str(e)}")

    def _update_status_bar(self, message: str):
        """Update the status bar with a message."""
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(message, 5000)  # Show for 5 seconds


def main():
    """Main function to run the RFU Hub."""
    import sys

    # Create QApplication if it doesn't exist
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # Create and show the hub
    hub = RFUHub()
    hub.show()

    # Start the event loop if this is the main application
    if __name__ == "__main__":
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
