"""Admin panel guard helpers shared between GUI flows and tests."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import (
        QAction,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QMenu,
        QMessageBox,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    PYQT5_AVAILABLE = True
except ImportError:  # pragma: no cover
    PYQT5_AVAILABLE = False
    Qt = object  # type: ignore
    QWidget = object  # type: ignore

from src.core.auth.endpoints.admin_users_controller import AdminUsersController
from src.core.auth.policies import InputValidator
from src.core.auth.repositories.always_available_account_repository import (
    AlwaysAvailableAccountRepository,
)
from src.core.auth.repositories.break_glass_usage_log_repository import (
    BreakGlassUsageLogRepository,
)
from src.log_manager import get_log_manager

LOGGER = get_log_manager().get_logger("RFU.AdminPanel")

# Icon constants for protected accounts
LOCK_ICON = "🔒"
EMERGENCY_ICON = "🚨"

# Roles that can access lockout prevention features
DEV_ROLES = {"dev"}
ADMIN_ROLES = {"dev", "admin"}


def _extract_session_mapping(
    session: Mapping[str, Any] | Dict[str, Any],
) -> Mapping[str, Any]:
    if isinstance(session, dict):
        return session
    return dict(session)


def _extract_role(session: Mapping[str, Any]) -> str | None:
    role = session.get("role")
    if not role and isinstance(session.get("session"), Mapping):
        nested = session["session"]
        role = nested.get("role")  # type: ignore[index]
    return str(role).lower() if role else None


def _extract_username(session: Mapping[str, Any]) -> str | None:
    username = session.get("username")
    if not username and isinstance(session.get("session"), Mapping):
        nested = session["session"]
        username = nested.get("username")  # type: ignore[index]
    return str(username) if username else None


def guard_admin_panel_access(
    *,
    session: Mapping[str, Any] | Dict[str, Any],
) -> None:
    """Raise when the provided session does not represent an admin user."""

    mapping = _extract_session_mapping(session)
    role = _extract_role(mapping)
    if role in ADMIN_ROLES:
        return
    username = _extract_username(mapping) or "unknown"
    LOGGER.warning(
        "Admin panel access denied for user %s with role=%s",
        username,
        role or "missing",
    )
    raise PermissionError("Administrator role required to open the admin panel")


def guard_dev_only_access(
    *,
    session: Mapping[str, Any] | Dict[str, Any],
    feature: str = "lockout prevention",
) -> None:
    """Raise when session is not dev role (for security features)."""

    mapping = _extract_session_mapping(session)
    role = _extract_role(mapping)
    if role in DEV_ROLES:
        return
    username = _extract_username(mapping) or "unknown"
    LOGGER.warning(
        "%s feature access denied for user %s with role=%s",
        feature,
        username,
        role or "missing",
    )
    raise PermissionError(f"Developer role required to access {feature} features")


@dataclass(frozen=True)
class ResetSecretEnvelope:
    """Container describing the outcome of a reset request."""

    temporary_password: Optional[str]
    delivery: str
    justification: str
    revealed: bool


@dataclass
class AdminPanelActions:
    """High-level helpers that back the GUI admin management panel."""

    controller: AdminUsersController
    database_path: Path
    session_username: str | None = None
    validator: InputValidator = field(default_factory=InputValidator)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def list_pending_users(self, limit: int = 25) -> list[Dict[str, Any]]:
        return self.controller.workflow.list_pending_users(limit=limit)

    def recent_audit_entries(self, limit: int = 50) -> list[Dict[str, Any]]:
        return self.controller.workflow.export_audit_entries(limit=limit)

    def approve_pending_user(
        self,
        *,
        username: str,
        role: str = "standard",
        template: str = "default",
    ) -> Dict[str, Any]:
        sanitized = self.validator.validate_username(username)
        payload = {
            "username": sanitized,
            "approve": True,
            "role": role,
            "preferences_template": template,
            "token_role": "admin",
            "token_username": self.session_username,
        }
        result = self.controller.post_user(payload)
        LOGGER.info("Admin panel approved %s (role=%s)", sanitized, role)
        return result

    def reset_user_password(
        self,
        *,
        username: str,
        delivery: str = "console",
        justification: str,
        reveal_secret: bool = False,
    ) -> ResetSecretEnvelope:
        sanitized = self.validator.validate_username(username)
        justification_value = (justification or "").strip()
        if not justification_value:
            raise ValueError("justification is required")

        payload = self.controller.patch_user(
            {
                "action": "reset_password",
                "username": sanitized,
                "dispatcher_channel": delivery,
                "reason": justification_value,
                "token_role": "admin",
                "token_username": self.session_username,
            }
        )
        temporary_password = payload.get("temporary_password")
        return ResetSecretEnvelope(
            temporary_password=temporary_password if reveal_secret else None,
            delivery=delivery,
            justification=justification_value,
            revealed=reveal_secret,
        )

    def unblock_user(
        self,
        *,
        username: str,
        justification: str,
    ) -> Dict[str, Any]:
        sanitized = self.validator.validate_username(username)
        justification_value = (justification or "").strip()
        if not justification_value:
            raise ValueError("justification is required")
        payload = self.controller.patch_user(
            {
                "action": "unblock",
                "username": sanitized,
                "reason": justification_value,
                "token_role": "admin",
                "token_username": self.session_username,
            }
        )
        LOGGER.info("Admin panel unblocked %s", sanitized)
        return payload

    def share_preferences_state(self, username: str) -> Dict[str, Any]:
        sanitized = self.validator.validate_username(username)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT username,
                       share_preferences,
                       preferences_id
                FROM user_accounts
                WHERE username = ?
                LIMIT 1
                """,
                (sanitized,),
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"User {sanitized!r} does not exist for preference view"
                )
            return {
                "username": row["username"],
                "share_preferences": bool(row["share_preferences"]),
                "preferences_id": row["preferences_id"],
            }

    # ------------------------------------------------------------------
    # Lockout prevention features (dev role only)
    # ------------------------------------------------------------------

    def get_break_glass_history(
        self,
        *,
        limit: int = 50,
        hours: int = 168,  # 7 days default
    ) -> List[Dict[str, Any]]:
        """Get break-glass usage history (dev role only).

        Args:
            limit: Maximum number of records to return
            hours: Look back window in hours (default 7 days)

        Returns:
            List of break-glass usage records
        """
        with self._connect() as conn:
            repo = BreakGlassUsageLogRepository(db_connection=conn)
            logs = repo.get_recent_sessions(hours=hours, limit=limit)
            return [
                {
                    "session_id": log.session_id,
                    "username": log.username,
                    "justification": log.justification,
                    "started_at": (
                        log.started_at.isoformat() if log.started_at else None
                    ),
                    "ended_at": (log.ended_at.isoformat() if log.ended_at else None),
                    "is_active": log.is_active,
                    "action_count": log.action_count,
                }
                for log in logs
            ]

    def get_always_available_status(self) -> List[Dict[str, Any]]:
        """Get always-available account status (dev role only).

        Returns:
            List of always-available account status records
        """
        with self._connect() as conn:
            repo = AlwaysAvailableAccountRepository(db_connection=conn)
            configs = repo.get_all()

            # Also get account info from user_accounts
            result = []
            for config in configs:
                account_row = conn.execute(
                    """
                    SELECT username, role, is_blocked, is_always_available,
                           is_break_glass, login_attempts
                    FROM user_accounts
                    WHERE username = ?
                    """,
                    (config.username,),
                ).fetchone()

                status = {
                    "username": config.username,
                    "cooldown_minutes": config.cooldown_duration_minutes,
                    "auto_unblock_enabled": config.auto_unblock_enabled,
                    "last_cooldown_started_at": (
                        config.last_cooldown_started_at.isoformat()
                        if config.last_cooldown_started_at
                        else None
                    ),
                    "cooldown_count": config.cooldown_count,
                    "in_cooldown": config.is_in_cooldown(datetime.now()),
                }

                if account_row:
                    status["role"] = account_row["role"]
                    status["is_blocked"] = bool(account_row["is_blocked"])
                    status["is_always_available"] = bool(
                        account_row["is_always_available"]
                    )
                    status["is_break_glass"] = bool(account_row["is_break_glass"])
                    status["login_attempts"] = account_row["login_attempts"]

                result.append(status)

            return result

    def get_protected_accounts_summary(self) -> Dict[str, Any]:
        """Get summary of all protected accounts (dev role only).

        Returns:
            Dictionary with always-available and break-glass account lists
        """
        with self._connect() as conn:
            always_available = conn.execute(
                """
                SELECT username, role, is_blocked, login_attempts
                FROM user_accounts
                WHERE is_always_available = 1
                ORDER BY username
                """
            ).fetchall()

            break_glass = conn.execute(
                """
                SELECT username, role, is_blocked, login_attempts
                FROM user_accounts
                WHERE is_break_glass = 1
                ORDER BY username
                """
            ).fetchall()

            return {
                "always_available": [
                    {
                        "username": row["username"],
                        "role": row["role"],
                        "is_blocked": bool(row["is_blocked"]),
                        "login_attempts": row["login_attempts"],
                    }
                    for row in always_available
                ],
                "break_glass": [
                    {
                        "username": row["username"],
                        "role": row["role"],
                        "is_blocked": bool(row["is_blocked"]),
                        "login_attempts": row["login_attempts"],
                    }
                    for row in break_glass
                ],
                "total_always_available": len(always_available),
                "total_break_glass": len(break_glass),
            }


@dataclass(frozen=True)
class AdminPanelContext:
    session_username: str | None
    deeplink_target: str | None
    controller: AdminUsersController
    actions: AdminPanelActions


def open_admin_panel(
    *,
    session: Mapping[str, Any] | Dict[str, Any],
    database_path: str | Path,
    deeplink_target: str | None = None,
) -> AdminPanelContext:
    """Return a launch context with helpers after enforcing admin gate."""

    guard_admin_panel_access(session=session)
    controller = AdminUsersController(db_path=database_path)
    username = _extract_username(_extract_session_mapping(session))
    LOGGER.info(
        "Admin panel opened by %s (deeplink=%s)",
        username or "unknown",
        deeplink_target,
    )
    actions = AdminPanelActions(
        controller=controller,
        database_path=Path(database_path),
        session_username=username,
    )
    return AdminPanelContext(
        session_username=username,
        deeplink_target=deeplink_target,
        controller=controller,
        actions=actions,
    )


# ---------------------------------------------------------------------------
# GUI Models and Widgets for T061 Protected Account Indicators
# ---------------------------------------------------------------------------


@dataclass
class AdminPanelUserModel:
    """Model representing a user row in the admin panel.

    Includes protection indicator fields for always-available and break-glass.
    """

    username: str
    role: str
    account_status: str
    is_always_available: bool = False
    is_break_glass: bool = False
    is_blocked: bool = False
    login_attempts: int = 0

    @property
    def is_protected(self) -> bool:
        """Return True if account is protected (always-available or break-glass)."""
        return self.is_always_available or self.is_break_glass

    @property
    def protection_type(self) -> Optional[str]:
        """Return protection type label or None."""
        if self.is_always_available:
            return "Always Available"
        if self.is_break_glass:
            return "Break Glass"
        return None

    @property
    def protection_icon(self) -> str:
        """Return icon for protection type."""
        if self.is_always_available:
            return LOCK_ICON
        if self.is_break_glass:
            return EMERGENCY_ICON
        return ""


@dataclass
class AdminPanelUserRow:
    """Row view data for the admin panel table."""

    model: AdminPanelUserModel

    @property
    def has_lock_icon(self) -> bool:
        """Return True if row should show lock icon."""
        return self.model.is_protected

    @property
    def protection_icon(self) -> str:
        """Return protection icon for the row."""
        return self.model.protection_icon

    @property
    def protection_type(self) -> Optional[str]:
        """Return protection type label."""
        return self.model.protection_type


if PYQT5_AVAILABLE:

    class AdminPanelWidget(QWidget):
        """PyQt5 widget for the admin panel with protected account indicators.

        Features (T061):
        - Protected Accounts section (dev role only)
        - Lock icon for always-available accounts
        - Emergency icon for break-glass accounts
        - Disabled delete/disable buttons for protected accounts
        - Break-Glass Usage Log viewer for dev role
        """

        def __init__(
            self,
            *,
            database_path: str | Path,
            session_role: str = "admin",
            parent: Optional[QWidget] = None,
        ) -> None:
            super().__init__(parent)
            self.database_path = Path(database_path)
            self.session_role = session_role.lower()
            self._users: Dict[str, AdminPanelUserRow] = {}
            self._selected_user: Optional[str] = None

            self._setup_ui()

        def _setup_ui(self) -> None:
            """Initialize the admin panel UI."""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(12)

            # Title
            title = QLabel("User Administration")
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(title)

            # User table
            self.user_table = QTableWidget()
            self.user_table.setColumnCount(5)
            self.user_table.setHorizontalHeaderLabels(
                ["", "Username", "Role", "Status", "Protection"]
            )
            self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.user_table.setSelectionBehavior(
                QTableWidget.SelectRows  # type: ignore
            )
            self.user_table.setSelectionMode(
                QTableWidget.SingleSelection  # type: ignore
            )
            self.user_table.itemSelectionChanged.connect(self._on_selection_changed)
            layout.addWidget(self.user_table)

            # Action buttons
            button_layout = QHBoxLayout()

            self.delete_button = QPushButton("Delete User")
            self.delete_button.setEnabled(False)
            self.delete_button.clicked.connect(self._on_delete_clicked)
            button_layout.addWidget(self.delete_button)

            self.disable_button = QPushButton("Disable User")
            self.disable_button.setEnabled(False)
            self.disable_button.clicked.connect(self._on_disable_clicked)
            button_layout.addWidget(self.disable_button)

            button_layout.addStretch(1)
            layout.addLayout(button_layout)

            # Protected Accounts section (dev role only)
            if self.session_role == "dev":
                self._add_protected_accounts_section(layout)

        def _add_protected_accounts_section(self, layout: QVBoxLayout) -> None:
            """Add protected accounts section for dev users."""
            section_label = QLabel("Protected Accounts")
            section_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; margin-top: 12px;"
            )
            layout.addWidget(section_label)

            # Break-Glass Usage Log button
            self.break_glass_log_button = QPushButton(
                f"{EMERGENCY_ICON} View Break-Glass Usage Log"
            )
            self.break_glass_log_button.clicked.connect(self._on_view_break_glass_log)
            layout.addWidget(self.break_glass_log_button)

        def load_users(self) -> None:
            """Load users from database into the table."""
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(
                    """
                    SELECT username, role, account_status, is_blocked,
                           login_attempts, is_always_available, is_break_glass
                    FROM user_accounts
                    ORDER BY username
                    """
                ).fetchall()

                self._users.clear()
                self.user_table.setRowCount(len(rows))

                for i, row in enumerate(rows):
                    model = AdminPanelUserModel(
                        username=row["username"],
                        role=row["role"],
                        account_status=row["account_status"],
                        is_always_available=bool(row["is_always_available"]),
                        is_break_glass=bool(row["is_break_glass"]),
                        is_blocked=bool(row["is_blocked"]),
                        login_attempts=row["login_attempts"] or 0,
                    )
                    user_row = AdminPanelUserRow(model=model)
                    self._users[model.username] = user_row

                    # Icon column
                    icon_item = QTableWidgetItem(user_row.protection_icon)
                    icon_item.setTextAlignment(Qt.AlignCenter)
                    self.user_table.setItem(i, 0, icon_item)

                    # Username
                    self.user_table.setItem(i, 1, QTableWidgetItem(model.username))

                    # Role
                    self.user_table.setItem(i, 2, QTableWidgetItem(model.role))

                    # Status
                    status = model.account_status
                    if model.is_blocked:
                        status = "blocked"
                    self.user_table.setItem(i, 3, QTableWidgetItem(status))

                    # Protection type
                    protection = user_row.protection_type or ""
                    self.user_table.setItem(i, 4, QTableWidgetItem(protection))

            finally:
                conn.close()

        def get_user_row(self, username: str) -> Optional[AdminPanelUserRow]:
            """Get user row data by username."""
            return self._users.get(username)

        def select_user(self, username: str) -> None:
            """Select a user in the table."""
            for i in range(self.user_table.rowCount()):
                item = self.user_table.item(i, 1)
                if item and item.text() == username:
                    self.user_table.selectRow(i)
                    self._selected_user = username
                    self._update_button_states()
                    break

        def _on_selection_changed(self) -> None:
            """Handle table selection change."""
            selected = self.user_table.selectedItems()
            if selected:
                row = selected[0].row()
                username_item = self.user_table.item(row, 1)
                if username_item:
                    self._selected_user = username_item.text()
                    self._update_button_states()
            else:
                self._selected_user = None
                self._update_button_states()

        def _update_button_states(self) -> None:
            """Update delete/disable button states based on selection."""
            if not self._selected_user:
                self.delete_button.setEnabled(False)
                self.disable_button.setEnabled(False)
                self.delete_button.setToolTip("")
                self.disable_button.setToolTip("")
                return

            user_row = self._users.get(self._selected_user)
            if not user_row:
                self.delete_button.setEnabled(False)
                self.disable_button.setEnabled(False)
                return

            if user_row.model.is_protected:
                # Disable buttons for protected accounts
                self.delete_button.setEnabled(False)
                self.disable_button.setEnabled(False)
                protection = user_row.protection_type or "protected"
                tooltip = (
                    f"Cannot modify {protection} account - "
                    "this account is protected from deletion/disabling"
                )
                self.delete_button.setToolTip(tooltip)
                self.disable_button.setToolTip(tooltip)
            else:
                # Enable buttons for regular accounts
                self.delete_button.setEnabled(True)
                self.disable_button.setEnabled(True)
                self.delete_button.setToolTip("Delete selected user")
                self.disable_button.setToolTip("Disable selected user")

        def _on_delete_clicked(self) -> None:
            """Handle delete button click."""
            if not self._selected_user:
                return
            user_row = self._users.get(self._selected_user)
            if user_row and user_row.model.is_protected:
                QMessageBox.warning(
                    self,
                    "Protected Account",
                    f"Cannot delete {user_row.protection_type} account "
                    f"'{self._selected_user}'.",
                )
                return
            # Actual delete logic would go here
            LOGGER.info("Delete requested for user: %s", self._selected_user)

        def _on_disable_clicked(self) -> None:
            """Handle disable button click."""
            if not self._selected_user:
                return
            user_row = self._users.get(self._selected_user)
            if user_row and user_row.model.is_protected:
                QMessageBox.warning(
                    self,
                    "Protected Account",
                    f"Cannot disable {user_row.protection_type} account "
                    f"'{self._selected_user}'.",
                )
                return
            # Actual disable logic would go here
            LOGGER.info("Disable requested for user: %s", self._selected_user)

        def _on_view_break_glass_log(self) -> None:
            """Open break-glass usage log viewer."""
            LOGGER.info("Break-glass usage log viewer requested")
            # Would open a dialog showing break-glass history

        def create_context_menu(self, username: str) -> QMenu:
            """Create context menu for a user row."""
            menu = QMenu(self)
            user_row = self._users.get(username)

            # Delete action
            delete_action = QAction("Delete", menu)
            if user_row and user_row.model.is_protected:
                delete_action.setEnabled(False)
                delete_action.setToolTip(
                    f"Cannot delete {user_row.protection_type} account"
                )
            menu.addAction(delete_action)

            # View Protection Info action
            if user_row and user_row.model.is_protected:
                info_action = QAction("View Protection Info", menu)
                info_action.setEnabled(True)
                menu.addAction(info_action)

            return menu

else:  # pragma: no cover

    class AdminPanelWidget:  # type: ignore[override]
        """Fallback when PyQt5 is not available."""

        def __init__(self, *_, **__) -> None:
            raise RuntimeError("PyQt5 is required for AdminPanelWidget")


__all__ = [
    "AdminPanelActions",
    "AdminPanelContext",
    "AdminPanelUserModel",
    "AdminPanelUserRow",
    "AdminPanelWidget",
    "ResetSecretEnvelope",
    "guard_admin_panel_access",
    "guard_dev_only_access",
    "open_admin_panel",
    "ADMIN_ROLES",
    "DEV_ROLES",
    "LOCK_ICON",
    "EMERGENCY_ICON",
]
