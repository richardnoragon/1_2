"""
src/gui/components/modal.py — Shared modal dialog components (P1-C10).

Spec §5.2: Modal (general), ConfirmationModal (destructive-action confirmation).
"""

from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.rfu import font_tokens
from src.gui.themes import Typography, token


class Modal(QDialog):
    """General-purpose modal dialog (spec §5.2).

    Args:
        title:   Window title and accessible name.
        message: Body text shown to the user.
        buttons: List of button labels.  Accepted automatically mapped to
                 ``QDialogButtonBox.Ok``; the first non-accepted button to
                 ``QDialogButtonBox.Cancel``.
        parent:  Parent widget.
    """

    def __init__(
        self,
        title: str,
        message: str,
        buttons: Optional[List[str]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 16)

        title_label = QLabel(title, self)
        font_tokens.bind(title_label, "font.title")
        title_label.setStyleSheet(f"color: {token('text_primary')};")
        layout.addWidget(title_label)

        msg_label = QLabel(message, self)
        font_tokens.bind(msg_label, "font.body")
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {token('text_secondary')};")
        layout.addWidget(msg_label)

        btn_labels = buttons or ["OK"]
        self._clicked_label: Optional[str] = None
        box = QDialogButtonBox(self)
        for i, label in enumerate(btn_labels):
            role = (
                QDialogButtonBox.AcceptRole if i == 0 else QDialogButtonBox.RejectRole
            )
            btn = box.addButton(label, role)
            font_tokens.bind(btn, "font.body")
            btn.setMinimumHeight(44)
            btn.clicked.connect(
                lambda _checked, _l=label: setattr(self, "_clicked_label", _l)
            )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

        self.setStyleSheet(
            f"QDialog {{ background-color: {token('dialog_background')}; }}"
        )


class ConfirmationModal(Modal):
    """Destructive-action confirmation modal (spec §5.2).

    Opens with the Cancel button focused by default (safe default).

    Args:
        title:        Window title.
        message:      Confirmation prompt shown to user.
        confirm_text: Label for the confirm (destructive) button.
        cancel_text:  Label for the cancel button.
        parent:       Parent widget.
    """

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        parent=None,
    ):
        # Put Cancel first so it's the AcceptRole-adjacent default focus
        super().__init__(title, message, [cancel_text, confirm_text], parent)
        self._remap_buttons(cancel_text, confirm_text)

    def _remap_buttons(self, cancel_text: str, confirm_text: str):
        """Ensure Cancel is focused on open and mapped to reject."""
        from PyQt5.QtWidgets import QDialogButtonBox

        box = self.findChild(QDialogButtonBox)
        for btn in self.findChildren(QPushButton):
            if btn.text() == cancel_text:
                box.removeButton(btn)
                box.addButton(btn, QDialogButtonBox.RejectRole)
                btn.setDefault(True)
                btn.setFocus()
            elif btn.text() == confirm_text:
                box.removeButton(btn)
                box.addButton(btn, QDialogButtonBox.AcceptRole)
                btn.setDefault(False)
                btn.setAutoDefault(False)
                error_color = token("semantic_error")
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {error_color};
                        color: {token("text_on_primary")};
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    }}
                    """
                )
