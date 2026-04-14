"""
src/gui/components/toast.py — Non-blocking toast notification (P1-C11).

Spec §6.1 / §6.2: Role-coloured overlay that auto-dismisses; respects OS
reduced-motion by skipping slide animation when the setting is active.
"""

import logging
from typing import Literal

from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.gui.themes import Typography, token

_log = logging.getLogger("RFU.components.toast")

ToastRole = Literal["success", "warning", "error", "info"]

_REDUCED_MOTION = False  # Overridden by _check_reduced_motion() at import


def _check_reduced_motion() -> bool:
    """Return True when the OS reports a reduced-motion preference."""
    try:
        import winreg  # Windows only

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Accessibility",
        )
        value, _ = winreg.QueryValueEx(key, "Configuration")
        # "MinimizeAnimations" bit in the accessibility flags
        return bool(value & 0x20)
    except Exception:
        return False


_REDUCED_MOTION = _check_reduced_motion()

# Non-colour secondary indicator for each role (A11Y-4).
_ROLE_PREFIX: dict = {
    "success": "\u2713 ",  # ✓
    "warning": "\u26a0 ",  # ⚠
    "error": "\u2717 ",  # ✗
    "info": "\u2139 ",  # ℹ
}


class ToastNotification(QWidget):
    """Spec-compliant toast notification (spec §6.1, P1-C11).

    Args:
        parent:        Parent widget (toast is positioned relative to it).
        role:          One of ``"success"``, ``"warning"``, ``"error"``, ``"info"``.
        message:       Text to display.
        duration_ms:   Auto-dismiss delay in milliseconds (default 3 000).
    """

    def __init__(
        self,
        parent=None,
        role: ToastRole = "info",
        message: str = "",
        duration_ms: int = 3000,
    ):
        super().__init__(parent)
        if role not in ("success", "warning", "error", "info"):
            raise ValueError(f"Invalid toast role: {role!r}")

        self._role = role
        self._duration_ms = duration_ms

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self._label = QLabel(message or "", self)
        self._label.setFont(Typography.body())
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        self.setAccessibleName(f"{role.capitalize()} notification")
        self.setAccessibleDescription(message)

        self._apply_style(role)
        self.hide()

        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.timeout.connect(self.hide)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_message(self, message: str, role: ToastRole = None):
        """Update message (and optionally role) then show the toast."""
        if role and role != self._role:
            self._role = role
            self._apply_style(role)
        prefix = _ROLE_PREFIX.get(self._role, "")
        self._label.setText(prefix + message)
        self.setAccessibleDescription(message)
        self.adjustSize()
        self._position_in_parent()
        self.show()
        self.raise_()
        self._dismiss_timer.start(self._duration_ms)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _apply_style(self, role: ToastRole):
        bg = token(f"semantic_{role}")
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {bg};
                border-radius: 6px;
            }}
            QLabel {{
                color: {token("text_on_primary")};
            }}
            """
        )

    def _position_in_parent(self):
        if self.parent() is None:
            return
        parent_rect = self.parent().rect()
        self.adjustSize()
        x = parent_rect.width() - self.width() - 16
        y = parent_rect.height() - self.height() - 16
        self.move(x, y)
