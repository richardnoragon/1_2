"""RFU Main Window with readonly mode enforcement and break-glass indicators.

This module provides the MainWindow class that integrates:
- T062: Readonly mode enforcement
- T063: Break-glass session indicator

The MainWindow wraps the hub utilities and provides a consistent interface
for the GUI application with role-based access control.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QKeyEvent
    from PyQt5.QtWidgets import (
        QAction,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QPushButton,
        QStatusBar,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    PYQT5_AVAILABLE = True
except ImportError:  # pragma: no cover
    PYQT5_AVAILABLE = False
    Qt = object  # type: ignore
    QMainWindow = object  # type: ignore
    QWidget = object  # type: ignore

from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("RFU.MainWindow")

# Role constants
READONLY_ROLE = "readonly"
WRITE_ROLES = {"dev", "admin", "user"}

# Write operations that should be blocked for readonly users
WRITE_OPERATIONS = {
    "save",
    "delete",
    "create",
    "edit",
    "paste",
    "cut",
    "rename",
    "move",
    "copy",  # copy might involve writes
}


if PYQT5_AVAILABLE:

    class ReadonlyBanner(QWidget):
        """Banner widget displayed when user is in readonly mode."""

        def __init__(self, parent: Optional[QWidget] = None) -> None:
            super().__init__(parent)
            self._setup_ui()

        def _setup_ui(self) -> None:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(8, 4, 8, 4)

            icon = QLabel("🔒")
            layout.addWidget(icon)

            message = QLabel(
                "Readonly Mode: You have view-only access. "
                "Write operations are disabled."
            )
            message.setStyleSheet("color: #7f8c8d; font-style: italic;")
            layout.addWidget(message)

            layout.addStretch(1)

            self.setStyleSheet(
                "background-color: #ecf0f1; border-bottom: 1px solid #bdc3c7;"
            )

    class BreakGlassBanner(QWidget):
        """Warning banner displayed during break-glass session."""

        def __init__(self, parent: Optional[QWidget] = None) -> None:
            super().__init__(parent)
            self._setup_ui()

        def _setup_ui(self) -> None:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(8, 4, 8, 4)

            icon = QLabel("⚠️")
            layout.addWidget(icon)

            message = QLabel(
                "Break-Glass Session Active: All actions are being logged. "
                "Use only for emergency recovery."
            )
            message.setStyleSheet("color: #c0392b; font-weight: bold;")
            layout.addWidget(message)

            layout.addStretch(1)

            reminder = QLabel("📝 Actions logged")
            reminder.setStyleSheet("color: #e74c3c;")
            layout.addWidget(reminder)

            self.setStyleSheet(
                "background-color: #fadbd8; border-bottom: 2px solid #e74c3c;"
            )

    class MainWindow(QMainWindow):
        """Main application window with role-based access control.

        Features:
        - T062: Readonly mode enforcement
          - Disables write operation buttons for readonly users
          - Blocks write hotkeys with permission error
          - Shows readonly banner

        - T063: Break-glass session indicator
          - Displays warning banner during break-glass session
          - Shows "Actions logged" reminder
          - Prompts for logout confirmation
        """

        def __init__(
            self,
            *,
            database_path: str | Path,
            session_id: str,
            parent: Optional[QWidget] = None,
        ) -> None:
            super().__init__(parent)
            self.database_path = Path(database_path)
            self.session_id = session_id

            # Session state
            self._role: str = "readonly"
            self._username: str = ""
            self._is_break_glass: bool = False
            self._session_type: str = "normal"

            # UI elements
            self._write_buttons: List[QPushButton] = []
            self._read_buttons: List[QPushButton] = []
            self._write_actions: List[QAction] = []

            # Load session data
            self._load_session()

            # Setup UI
            self._setup_ui()

            # Apply role-based restrictions
            self._apply_role_restrictions()

        def _load_session(self) -> None:
            """Load session data from database."""
            try:
                conn = sqlite3.connect(self.database_path)
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    """
                    SELECT s.session_id, s.username, s.role,
                           COALESCE(s.session_type, 'normal') as session_type
                    FROM sessions s
                    WHERE s.session_id = ?
                    """,
                    (self.session_id,),
                ).fetchone()
                conn.close()

                if row:
                    self._role = row["role"] or "readonly"
                    self._username = row["username"] or ""
                    self._session_type = row["session_type"] or "normal"
                    self._is_break_glass = self._session_type == "break_glass"
            except Exception as exc:
                LOGGER.warning("Failed to load session: %s", exc)
                self._role = "readonly"

        def _setup_ui(self) -> None:
            """Initialize the main window UI."""
            self.setWindowTitle(f"RFU Hub - {self._username}")
            self.setMinimumSize(800, 600)

            # Central widget
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Banners container
            self._banners_container = QWidget()
            banners_layout = QVBoxLayout(self._banners_container)
            banners_layout.setContentsMargins(0, 0, 0, 0)
            banners_layout.setSpacing(0)

            # Readonly banner
            self.readonly_banner = ReadonlyBanner()
            self.readonly_banner.setVisible(False)
            banners_layout.addWidget(self.readonly_banner)

            # Break-glass banner
            self.break_glass_banner = BreakGlassBanner()
            self.break_glass_banner.setVisible(False)
            banners_layout.addWidget(self.break_glass_banner)

            layout.addWidget(self._banners_container)

            # Create toolbar
            self._create_toolbar()

            # Main content area (placeholder)
            content = QWidget()
            content.setStyleSheet("background-color: white;")
            layout.addWidget(content, 1)

            # Create menus
            self._create_menus()

            # Status bar
            self.setStatusBar(QStatusBar())
            self.statusBar().showMessage(
                f"Logged in as {self._username} ({self._role})"
            )

        def _create_toolbar(self) -> None:
            """Create the main toolbar with action buttons."""
            toolbar = QToolBar("Main Toolbar")
            self.addToolBar(toolbar)

            # View button (always enabled)
            self.view_button = QPushButton("View")
            self.view_button.setObjectName("view_button")
            toolbar.addWidget(self.view_button)
            self._read_buttons.append(self.view_button)

            # Refresh button (always enabled)
            self.refresh_button = QPushButton("Refresh")
            self.refresh_button.setObjectName("refresh_button")
            toolbar.addWidget(self.refresh_button)
            self._read_buttons.append(self.refresh_button)

            toolbar.addSeparator()

            # Save button (write operation)
            self.save_button = QPushButton("Save")
            self.save_button.setObjectName("save_button")
            toolbar.addWidget(self.save_button)
            self._write_buttons.append(self.save_button)

            # Create button (write operation)
            self.create_button = QPushButton("New")
            self.create_button.setObjectName("create_button")
            toolbar.addWidget(self.create_button)
            self._write_buttons.append(self.create_button)

            # Edit button (write operation)
            self.edit_button = QPushButton("Edit")
            self.edit_button.setObjectName("edit_button")
            toolbar.addWidget(self.edit_button)
            self._write_buttons.append(self.edit_button)

            # Delete button (write operation)
            self.delete_button = QPushButton("Delete")
            self.delete_button.setObjectName("delete_button")
            toolbar.addWidget(self.delete_button)
            self._write_buttons.append(self.delete_button)

        def _create_menus(self) -> None:
            """Create the menu bar with actions."""
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("File")

            # Save action
            self.action_save = QAction("Save", self)
            self.action_save.setShortcut("Ctrl+S")
            self.action_save.setObjectName("actionSave")
            file_menu.addAction(self.action_save)
            self._write_actions.append(self.action_save)

            # Refresh action
            self.action_refresh = QAction("Refresh", self)
            self.action_refresh.setShortcut("F5")
            self.action_refresh.setObjectName("actionRefresh")
            file_menu.addAction(self.action_refresh)

            file_menu.addSeparator()

            # Exit action
            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Alt+F4")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # Edit menu
            edit_menu = menubar.addMenu("Edit")

            # Cut action
            self.action_cut = QAction("Cut", self)
            self.action_cut.setShortcut("Ctrl+X")
            self.action_cut.setObjectName("actionCut")
            edit_menu.addAction(self.action_cut)
            self._write_actions.append(self.action_cut)

            # Copy action (read operation)
            self.action_copy = QAction("Copy", self)
            self.action_copy.setShortcut("Ctrl+C")
            self.action_copy.setObjectName("actionCopy")
            edit_menu.addAction(self.action_copy)

            # Paste action
            self.action_paste = QAction("Paste", self)
            self.action_paste.setShortcut("Ctrl+V")
            self.action_paste.setObjectName("actionPaste")
            edit_menu.addAction(self.action_paste)
            self._write_actions.append(self.action_paste)

            edit_menu.addSeparator()

            # Delete action
            self.action_delete = QAction("Delete", self)
            self.action_delete.setShortcut("Delete")
            self.action_delete.setObjectName("actionDelete")
            edit_menu.addAction(self.action_delete)
            self._write_actions.append(self.action_delete)

            # View menu
            view_menu = menubar.addMenu("View")

            # Refresh in view menu
            refresh_view = QAction("Refresh", self)
            refresh_view.triggered.connect(lambda: None)  # Placeholder
            view_menu.addAction(refresh_view)

        def _apply_role_restrictions(self) -> None:
            """Apply role-based UI restrictions."""
            is_readonly = self._role == READONLY_ROLE

            # Show readonly banner
            self.readonly_banner.setVisible(is_readonly)

            # Show break-glass banner
            self.break_glass_banner.setVisible(self._is_break_glass)

            # Disable write buttons for readonly
            readonly_tooltip = (
                "This action is disabled because you have readonly access. "
                "Contact an administrator if you need write permissions."
            )

            for button in self._write_buttons:
                button.setEnabled(not is_readonly)
                if is_readonly:
                    button.setToolTip(readonly_tooltip)
                else:
                    button.setToolTip("")

            # Disable write menu actions for readonly
            for action in self._write_actions:
                action.setEnabled(not is_readonly)
                if is_readonly:
                    action.setToolTip(readonly_tooltip)
                else:
                    action.setToolTip("")

        def is_readonly(self) -> bool:
            """Return True if user has readonly role."""
            return self._role == READONLY_ROLE

        def is_break_glass_session(self) -> bool:
            """Return True if this is a break-glass session."""
            return self._is_break_glass

        def get_write_operation_buttons(self) -> List[QPushButton]:
            """Return list of write operation buttons."""
            return self._write_buttons.copy()

        def get_read_operation_buttons(self) -> List[QPushButton]:
            """Return list of read operation buttons."""
            return self._read_buttons.copy()

        def show_permission_error(self, operation: str = "this action") -> None:
            """Show a permission error dialog for blocked operations."""
            QMessageBox.warning(
                self,
                "Permission Denied",
                f"You cannot perform {operation} because you have readonly access.\n\n"
                "Contact an administrator if you need write permissions.",
            )
            LOGGER.warning(
                "Permission denied for %s: user=%s role=%s",
                operation,
                self._username,
                self._role,
            )

        def save_action(self) -> None:
            """Perform save action (placeholder for actual implementation)."""
            if self.is_readonly():
                self.show_permission_error("save")
                return
            LOGGER.info("Save action triggered")

        def delete_action(self) -> None:
            """Perform delete action (placeholder for actual implementation)."""
            if self.is_readonly():
                self.show_permission_error("delete")
                return
            LOGGER.info("Delete action triggered")

        def keyPressEvent(self, event: QKeyEvent) -> None:
            """Handle key press events with readonly blocking."""
            key = event.key()
            modifiers = event.modifiers()

            # Block write hotkeys for readonly users
            if self.is_readonly():
                # Ctrl+S (Save)
                if key == Qt.Key_S and modifiers == Qt.ControlModifier:
                    self.show_permission_error("save")
                    event.accept()
                    return

                # Ctrl+X (Cut)
                if key == Qt.Key_X and modifiers == Qt.ControlModifier:
                    self.show_permission_error("cut")
                    event.accept()
                    return

                # Ctrl+V (Paste)
                if key == Qt.Key_V and modifiers == Qt.ControlModifier:
                    self.show_permission_error("paste")
                    event.accept()
                    return

                # Delete key
                if key == Qt.Key_Delete and modifiers == Qt.NoModifier:
                    self.show_permission_error("delete")
                    event.accept()
                    return

            super().keyPressEvent(event)

        def closeEvent(self, event) -> None:
            """Handle window close with break-glass confirmation."""
            if self._is_break_glass:
                reply = QMessageBox.question(
                    self,
                    "End Break-Glass Session?",
                    "You are in a break-glass emergency session.\n\n"
                    "Closing this window will end your session and trigger "
                    "password rotation.\n\n"
                    "Are you sure you want to close?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.No:
                    event.ignore()
                    return

                LOGGER.warning(
                    "Break-glass session ended by window close: user=%s",
                    self._username,
                )

            event.accept()

else:  # pragma: no cover

    class ReadonlyBanner:  # type: ignore[override]
        """Fallback when PyQt5 is not available."""

        def __init__(self, *_, **__) -> None:
            raise RuntimeError("PyQt5 is required for ReadonlyBanner")

    class BreakGlassBanner:  # type: ignore[override]
        """Fallback when PyQt5 is not available."""

        def __init__(self, *_, **__) -> None:
            raise RuntimeError("PyQt5 is required for BreakGlassBanner")

    class MainWindow:  # type: ignore[override]
        """Fallback when PyQt5 is not available."""

        def __init__(self, *_, **__) -> None:
            raise RuntimeError("PyQt5 is required for MainWindow")


__all__ = [
    "MainWindow",
    "ReadonlyBanner",
    "BreakGlassBanner",
    "READONLY_ROLE",
    "WRITE_ROLES",
    "WRITE_OPERATIONS",
]
