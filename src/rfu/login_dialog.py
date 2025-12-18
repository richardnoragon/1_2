"""Modal login dialog for authenticating hub sessions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QDialog,
        QDialogButtonBox,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    PYQT5_AVAILABLE = True
except ImportError:  # pragma: no cover - GUI fallback
    PYQT5_AVAILABLE = False
    Qt = object  # type: ignore
    QDialog = object  # type: ignore
    QWidget = object  # type: ignore

from src.identity import (
    BreakGlassJustificationRequired,
    login_with_preferences,
    submit_registration_request,
)

_LOGGER = logging.getLogger("RFU.LoginDialog")


if PYQT5_AVAILABLE:

    class BreakGlassJustificationDialog(QDialog):
        """Modal dialog to collect justification for break-glass access."""

        MIN_JUSTIFICATION_LENGTH = 10

        def __init__(
            self,
            *,
            username: str,
            parent: Optional[QWidget] = None,
        ) -> None:
            super().__init__(parent)
            self.setWindowTitle("Break-Glass Access - Justification Required")
            self.setModal(True)
            self.setMinimumWidth(480)
            self._username = username
            self.justification: Optional[str] = None
            self._build_ui()

        def _build_ui(self) -> None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(12)

            # Warning header
            warning = QLabel("⚠️ Break-Glass Emergency Access")
            warning.setAlignment(Qt.AlignHCenter)
            warning.setStyleSheet("font-size: 16px; font-weight: bold; color: #c0392b;")
            layout.addWidget(warning)

            # Explanation
            explanation = QLabel(
                f"Account '{self._username}' is a break-glass emergency "
                "account. These credentials should only be used when normal "
                "access is unavailable.\n\n"
                "You must provide a justification for this emergency access. "
                "All break-glass logins are logged and audited."
            )
            explanation.setWordWrap(True)
            layout.addWidget(explanation)

            # Justification input
            justification_label = QLabel(
                f"Justification (minimum {self.MIN_JUSTIFICATION_LENGTH} "
                "characters):"
            )
            layout.addWidget(justification_label)

            self.justification_input = QPlainTextEdit()
            self.justification_input.setPlaceholderText(
                "Describe why you need emergency access..."
            )
            self.justification_input.setMaximumHeight(100)
            layout.addWidget(self.justification_input)

            # Character count feedback
            self.char_count_label = QLabel(
                f"0/{self.MIN_JUSTIFICATION_LENGTH} characters"
            )
            self.char_count_label.setStyleSheet("color: #e74c3c;")
            layout.addWidget(self.char_count_label)

            self.justification_input.textChanged.connect(self._update_char_count)

            # Error label
            self.error_label = QLabel("")
            self.error_label.setWordWrap(True)
            self.error_label.setStyleSheet("color: #e74c3c;")
            layout.addWidget(self.error_label)

            # Buttons
            button_row = QHBoxLayout()
            button_row.addStretch(1)

            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(self.reject)
            button_row.addWidget(cancel_button)

            self.submit_button = QPushButton("Submit & Continue Login")
            self.submit_button.setDefault(True)
            self.submit_button.clicked.connect(self._submit)
            button_row.addWidget(self.submit_button)

            layout.addLayout(button_row)

        def _update_char_count(self) -> None:
            text = self.justification_input.toPlainText().strip()
            count = len(text)
            self.char_count_label.setText(
                f"{count}/{self.MIN_JUSTIFICATION_LENGTH} characters"
            )
            if count >= self.MIN_JUSTIFICATION_LENGTH:
                self.char_count_label.setStyleSheet("color: #27ae60;")
            else:
                self.char_count_label.setStyleSheet("color: #e74c3c;")

        def _submit(self) -> None:
            text = self.justification_input.toPlainText().strip()
            if len(text) < self.MIN_JUSTIFICATION_LENGTH:
                self.error_label.setText(
                    f"Justification must be at least "
                    f"{self.MIN_JUSTIFICATION_LENGTH} characters."
                )
                return
            self.justification = text
            self.accept()

    class HubLoginDialog(QDialog):
        """Simple username/password dialog that runs GUI login helpers."""

        def __init__(
            self,
            *,
            database_path: str | Path,
            parent: Optional[QWidget] = None,
            initial_username: str = "",
        ) -> None:
            super().__init__(parent)
            self.setWindowTitle("Sign in to Richard's File Utilities")
            self.setModal(True)
            self.database_path = Path(database_path)
            self.login_result: Optional[Dict[str, Any]] = None
            self._busy = False
            self._registration_busy = False

            self._build_ui(initial_username)

        # ------------------------------------------------------------------
        # UI assembly
        # ------------------------------------------------------------------
        def _build_ui(self, initial_username: str) -> None:
            self.setMinimumWidth(420)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(12)

            title = QLabel("Authenticate to continue")
            title.setAlignment(Qt.AlignHCenter)
            title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(title)

            subtitle = QLabel("Enter your RFU hub credentials. All logins are audited.")
            subtitle.setWordWrap(True)
            layout.addWidget(subtitle)

            form = QGridLayout()
            form.setVerticalSpacing(10)
            form.setHorizontalSpacing(12)

            username_label = QLabel("Username")
            self.username_input = QLineEdit()
            self.username_input.setText(initial_username)
            self.username_input.setPlaceholderText("e.g. admin-ops")
            self.username_input.setMaxLength(64)
            form.addWidget(username_label, 0, 0)
            form.addWidget(self.username_input, 0, 1)

            password_label = QLabel("Password")
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText("Your account password")
            self.password_input.returnPressed.connect(self._attempt_login)
            form.addWidget(password_label, 1, 0)
            form.addWidget(self.password_input, 1, 1)

            layout.addLayout(form)

            self.feedback_label = QLabel("")
            self.feedback_label.setWordWrap(True)
            self.feedback_label.setStyleSheet("color: #e74c3c;")
            layout.addWidget(self.feedback_label)

            button_row = QHBoxLayout()
            button_row.addStretch(1)

            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(self.reject)
            button_row.addWidget(cancel_button)

            self.login_button = QPushButton("Sign In")
            self.login_button.setDefault(True)
            self.login_button.clicked.connect(self._attempt_login)
            button_row.addWidget(self.login_button)

            layout.addLayout(button_row)

            self.username_input.setFocus()

            divider = QFrame()
            divider.setFrameShape(QFrame.HLine)
            divider.setFrameShadow(QFrame.Sunken)
            layout.addWidget(divider)

            registration_panel = self._create_registration_panel()
            layout.addWidget(registration_panel)

        # ------------------------------------------------------------------
        # Behaviour
        # ------------------------------------------------------------------
        def _set_busy(self, busy: bool) -> None:
            self._busy = busy
            self.login_button.setEnabled(not busy)
            self.username_input.setEnabled(not busy)
            self.password_input.setEnabled(not busy)

        def _display_error(self, message: str) -> None:
            self.feedback_label.setText(message)

        def _attempt_login(self, *, justification: Optional[str] = None) -> None:
            if self._busy:
                return

            username = self.username_input.text().strip()
            password = self.password_input.text()
            if not username or not password:
                self._display_error("Enter both username and password to continue")
                return

            self._display_error("")
            self._set_busy(True)
            try:
                result = login_with_preferences(
                    database_path=self.database_path,
                    username=username,
                    password=password,
                    justification=justification,
                )
            except BreakGlassJustificationRequired:
                self._set_busy(False)
                self._handle_break_glass_justification(username, password)
                return
            except Exception as exc:  # pragma: no cover - GUI event path
                _LOGGER.warning("Login failed: %s", exc)
                self._display_error(str(exc))
                self.password_input.selectAll()
                self.password_input.setFocus()
                result = None
            finally:
                self._set_busy(False)

            if result is None:
                return

            self.login_result = result
            badge = result.get("preference_badge") or {}
            badge_text = badge.get("text") or badge.get("label")
            if badge_text:
                self._display_error(f"Loaded preferences: {badge_text}")
            self.accept()

        def _handle_break_glass_justification(
            self, username: str, password: str
        ) -> None:
            """Show justification dialog and retry login with justification."""
            dialog = BreakGlassJustificationDialog(
                username=username,
                parent=self,
            )
            result = dialog.exec_()
            if result != QDialog.Accepted or not dialog.justification:
                self._display_error("Break-glass login cancelled")
                return

            # Retry login with justification
            self._display_error("")
            self._set_busy(True)
            try:
                login_result = login_with_preferences(
                    database_path=self.database_path,
                    username=username,
                    password=password,
                    justification=dialog.justification,
                )
            except Exception as exc:  # pragma: no cover - GUI path
                _LOGGER.warning("Break-glass login failed: %s", exc)
                self._display_error(str(exc))
                self.password_input.selectAll()
                self.password_input.setFocus()
                return
            finally:
                self._set_busy(False)

            self.login_result = login_result
            _LOGGER.warning(
                "Break-glass login successful: %s (justification: %s...)",
                username,
                dialog.justification[:20],
            )
            self.accept()

        # ------------------------------------------------------------------
        # Registration helpers
        # ------------------------------------------------------------------
        def _create_registration_panel(self) -> QWidget:
            panel = QWidget()
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(0, 12, 0, 0)
            panel_layout.setSpacing(8)

            title = QLabel("Need an account? Request access below.")
            title.setStyleSheet("font-size: 14px; font-weight: bold;")
            panel_layout.addWidget(title)

            subtitle = QLabel(
                "Registrations are queued for administrator approval. "
                "You'll receive confirmation once activated."
            )
            subtitle.setWordWrap(True)
            panel_layout.addWidget(subtitle)

            form = QGridLayout()
            form.setVerticalSpacing(10)
            form.setHorizontalSpacing(12)

            reg_user_label = QLabel("Desired Username")
            self.registration_username_input = QLineEdit()
            self.registration_username_input.setPlaceholderText("e.g. analyst-qa")
            form.addWidget(reg_user_label, 0, 0)
            form.addWidget(self.registration_username_input, 0, 1)

            reg_pass_label = QLabel("Password")
            self.registration_password_input = QLineEdit()
            self.registration_password_input.setEchoMode(QLineEdit.Password)
            form.addWidget(reg_pass_label, 1, 0)
            form.addWidget(self.registration_password_input, 1, 1)

            reg_confirm_label = QLabel("Confirm Password")
            self.registration_confirm_input = QLineEdit()
            self.registration_confirm_input.setEchoMode(QLineEdit.Password)
            form.addWidget(reg_confirm_label, 2, 0)
            form.addWidget(self.registration_confirm_input, 2, 1)

            preference_label = QLabel("Workspace Preference (optional)")
            self.registration_preference_input = QLineEdit()
            self.registration_preference_input.setPlaceholderText("e.g. dual-pane")
            form.addWidget(preference_label, 3, 0)
            form.addWidget(self.registration_preference_input, 3, 1)

            notes_label = QLabel("Approval Notes (optional)")
            self.registration_notes_input = QLineEdit()
            self.registration_notes_input.setPlaceholderText("Why you need access")
            form.addWidget(notes_label, 4, 0)
            form.addWidget(self.registration_notes_input, 4, 1)

            panel_layout.addLayout(form)

            self.registration_feedback_label = QLabel("")
            self.registration_feedback_label.setWordWrap(True)
            self.registration_feedback_label.setStyleSheet("color: #e67e22;")
            panel_layout.addWidget(self.registration_feedback_label)

            button_row = QHBoxLayout()
            button_row.addStretch(1)
            self.register_button = QPushButton("Submit Registration")
            self.register_button.clicked.connect(self._attempt_registration)
            button_row.addWidget(self.register_button)
            panel_layout.addLayout(button_row)

            pending_hint = QLabel(
                "Reminder: pending accounts cannot sign in until an administrator "
                "approves them."
            )
            pending_hint.setWordWrap(True)
            pending_hint.setStyleSheet("color: #7f8c8d;")
            panel_layout.addWidget(pending_hint)

            return panel

        def _set_registration_busy(self, busy: bool) -> None:
            self._registration_busy = busy
            self.register_button.setEnabled(not busy)
            self.registration_username_input.setEnabled(not busy)
            self.registration_password_input.setEnabled(not busy)
            self.registration_confirm_input.setEnabled(not busy)
            self.registration_preference_input.setEnabled(not busy)
            self.registration_notes_input.setEnabled(not busy)

        def _display_registration_feedback(
            self, message: str, *, success: bool = False
        ) -> None:
            if success:
                self.registration_feedback_label.setStyleSheet("color: #27ae60;")
            else:
                self.registration_feedback_label.setStyleSheet("color: #e67e22;")
            self.registration_feedback_label.setText(message)

        def _clear_registration_inputs(self) -> None:
            self.registration_password_input.clear()
            self.registration_confirm_input.clear()
            self.registration_notes_input.clear()
            self.registration_preference_input.clear()

        def _attempt_registration(self) -> None:
            if self._registration_busy:
                return

            username = self.registration_username_input.text().strip()
            password = self.registration_password_input.text()
            confirmation = self.registration_confirm_input.text()
            if not username or not password:
                self._display_registration_feedback(
                    "Enter a username and password to submit a request."
                )
                return
            if password != confirmation:
                self._display_registration_feedback("Passwords do not match.")
                self.registration_confirm_input.selectAll()
                self.registration_confirm_input.setFocus()
                return

            metadata: Dict[str, Any] = {}
            preference = self.registration_preference_input.text().strip()
            notes = self.registration_notes_input.text().strip()
            if preference:
                metadata["preferred_workspace"] = preference
            if notes:
                metadata["notes"] = notes
            metadata_payload = metadata or None

            self._display_registration_feedback("")
            self._set_registration_busy(True)
            try:
                response = submit_registration_request(
                    database_path=self.database_path,
                    username=username,
                    password=password,
                    metadata=metadata_payload,
                    channel="gui",
                )
            except Exception as exc:  # pragma: no cover - GUI path
                message = str(exc)
                if "exists" in message.lower():
                    message = (
                        "That username is already pending or active. "
                        "Choose a different username and try again."
                    )
                self._display_registration_feedback(message)
                _LOGGER.warning("Registration attempt failed: %s", exc)
                return
            finally:
                self._set_registration_busy(False)

            pending_message = response.get("message") or (
                "Registration submitted. Your account is pending administrator approval."
            )
            self._display_registration_feedback(pending_message, success=True)
            sanitized_username = response.get("username") or username
            self.registration_username_input.setText(sanitized_username)
            if not self.username_input.text().strip():
                self.username_input.setText(sanitized_username)
            self._clear_registration_inputs()

    def prompt_for_login(
        *,
        database_path: str | Path,
        parent: Optional[QWidget] = None,
        initial_username: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Show the dialog and return the session mapping on success."""

        dialog = HubLoginDialog(
            database_path=database_path,
            parent=parent,
            initial_username=initial_username,
        )
        result = dialog.exec_()
        if result == QDialog.Accepted:
            return dialog.login_result
        return None

else:  # pragma: no cover - fallback definitions

    class HubLoginDialog:  # type: ignore[override]
        def __init__(self, *_, **__) -> None:
            raise RuntimeError("PyQt5 is required for the hub login dialog")

    class BreakGlassJustificationDialog:  # type: ignore[override]
        def __init__(self, *_, **__) -> None:
            raise RuntimeError("PyQt5 is required for the justification dialog")

    def prompt_for_login(*_, **__):  # type: ignore[override]
        raise RuntimeError("PyQt5 is required for the hub login dialog")


__all__ = [
    "HubLoginDialog",
    "BreakGlassJustificationDialog",
    "prompt_for_login",
]
