"""
src/gui/components/buttons.py — Shared button components (P1-C08).

Spec §5.2: PrimaryButton, SecondaryButton, DestructiveButton.
All colors resolved via token(); all fonts via Typography.
"""

import logging

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QWidget

from src.rfu import font_tokens
from src.gui.themes import Typography, token

_log = logging.getLogger("RFU.components.buttons")


class PrimaryButton(QPushButton):
    """Primary action button (spec §5.2).

    At most one PrimaryButton should appear per view.  In debug mode
    (``__debug__`` is True) a warning is logged if a second instance is
    shown in the same parent widget.
    """

    def __init__(self, text: str = "", parent=None):
        if isinstance(text, QWidget) and parent is None:
            parent, text = text, ""
        super().__init__(text, parent)
        font_tokens.bind(self, "font.body")
        self.setAccessibleName(text or "Primary action")
        self.setMinimumSize(120, 44)
        self._apply_style()

    def _apply_style(self):
        bg = token("button_primary")
        hover = token("button_primary_hover")
        pressed = token("button_primary_pressed")
        text_color = token("window_background")
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{
                background-color: {token("text_disabled")};
            }}
            """
        )

    def showEvent(self, event):
        super().showEvent(event)
        if __debug__ and self.parent() is not None:
            siblings = [
                w
                for w in self.parent().findChildren(PrimaryButton)
                if w is not self and w.isVisible()
            ]
            if siblings:
                _log.warning(
                    "Multiple PrimaryButtons visible in the same parent — "
                    "spec §5.2 allows at most one primary action per view."
                )


class SecondaryButton(QPushButton):
    """Visually de-emphasized secondary action (spec §5.2)."""

    def __init__(self, text: str = "", parent=None):
        if isinstance(text, QWidget) and parent is None:
            parent, text = text, ""
        super().__init__(text, parent)
        font_tokens.bind(self, "font.body")
        self.setAccessibleName(text or "Secondary action")
        self.setMinimumSize(120, 44)
        self._apply_style()

    def _apply_style(self):
        bg = token("button_secondary")
        hover = token("button_secondary_hover")
        pressed = token("button_secondary_pressed")
        fg = token("text_primary")
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {token("text_secondary")};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{
                background-color: {token("text_disabled")};
            }}
            """
        )


class DestructiveButton(PrimaryButton):
    """Destructive action button.

    The ``clicked`` signal is intercepted; the button emits
    ``action_confirmed`` only after the caller connects a confirmation
    callback via ``set_confirmation_callback(fn)``. If no callback is
    set, the click is silently suppressed.
    """

    action_confirmed = pyqtSignal()

    def __init__(self, text: str = "", parent=None):
        if isinstance(text, QWidget) and parent is None:
            parent, text = text, ""
        super().__init__(text, parent)
        self._confirm_callback = None
        self.setAccessibleName(text or "Destructive action")
        self._apply_destructive_style()
        # Disconnect parent class click → route through confirmation
        if self.receivers(self.clicked):
            self.clicked.disconnect()

    def _apply_destructive_style(self):
        bg = token("semantic_error")
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {token("text_on_primary")};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {token("semantic_error")};
                opacity: 0.85;
            }}
            QPushButton:disabled {{
                background-color: {token("text_disabled")};
            }}
            """
        )

    def set_confirmation_callback(self, fn):
        """Register a callable that must return True to allow the action."""
        self._confirm_callback = fn
        self.clicked.connect(self._on_click)

    def _on_click(self):
        if self._confirm_callback and self._confirm_callback():
            self.action_confirmed.emit()
