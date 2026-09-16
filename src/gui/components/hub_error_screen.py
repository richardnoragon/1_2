"""
src/gui/components/hub_error_screen.py — Hub error screen (P1-C14).

Spec §8.2: user-friendly, accessible error display.  Error code is logged
internally but NEVER shown to the user.
"""

import logging

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.rfu import font_tokens
from src.gui.themes import Typography, token
from src.core.error_codes import resolve_error

_log = logging.getLogger("RFU.components.hub_error_screen")


class HubErrorScreen(QWidget):
    """Non-technical error display shown when a tool encounters a fatal error (spec §8.2, P1-C14).

    Args:
        tool_name:  Human-readable tool name shown in the heading.
        error_code: Internal error code — logged, NOT displayed.
        parent:     Parent widget.

    Signals:
        retry_requested:   Emitted when the user clicks Retry.
        go_home_requested: Emitted when the user clicks Go to Hub.
    """

    retry_requested = pyqtSignal()
    go_home_requested = pyqtSignal()

    def __init__(self, tool_name: str, error_code: str, parent=None):
        super().__init__(parent)
        self._tool_name = tool_name
        self._error_code = error_code

        _log.error(
            "HubErrorScreen shown for tool=%r error_code=%r",
            tool_name,
            error_code,
        )

        self._build_ui()

        self.setAccessibleName("Error")
        self.setAccessibleDescription(
            f"An error occurred in {tool_name}. Use the buttons below to retry or return to Hub."
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_message(self, user_message: str):
        """Update the user-facing message text."""
        self._message_label.setText(user_message)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("⚠", self)
        font_tokens.bind(icon_label, "font.toolHeader")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {token('semantic_warning')};")
        layout.addWidget(icon_label)

        heading = QLabel(f"Something went wrong in {self._tool_name}", self)
        font_tokens.bind(heading, "font.title")
        heading.setAlignment(Qt.AlignCenter)
        heading.setWordWrap(True)
        heading.setStyleSheet(f"color: {token('text_primary')};")
        layout.addWidget(heading)

        self._message_label = QLabel(
            resolve_error(self._error_code).message,
            self,
        )
        font_tokens.bind(self._message_label, "font.body")
        self._message_label.setAlignment(Qt.AlignCenter)
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet(f"color: {token('text_secondary')};")
        layout.addWidget(self._message_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self._retry_btn = QPushButton("Retry", self)
        font_tokens.bind(self._retry_btn, "font.body")
        self._retry_btn.setMinimumSize(120, 44)
        self._retry_btn.setAccessibleName("Retry")
        self._retry_btn.clicked.connect(self.retry_requested)
        bg = token("button_primary")
        fg = token("window_background")
        self._retry_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            """
        )
        btn_row.addWidget(self._retry_btn)

        self._home_btn = QPushButton("Go to Hub", self)
        font_tokens.bind(self._home_btn, "font.body")
        self._home_btn.setMinimumSize(120, 44)
        self._home_btn.setAccessibleName("Go to Hub")
        self._home_btn.clicked.connect(self.go_home_requested)
        sec_bg = token("button_secondary")
        sec_fg = token("text_primary")
        self._home_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {sec_bg};
                color: {sec_fg};
                border: 1px solid {token("text_secondary")};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            """
        )
        btn_row.addWidget(self._home_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        self.setStyleSheet(
            f"QWidget {{ background-color: {token('window_background')}; }}"
        )
