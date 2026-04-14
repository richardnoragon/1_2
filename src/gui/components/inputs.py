"""
src/gui/components/inputs.py — Shared text input component (P1-C09).

Spec §5.3: persistent label, inline validation, error state via token.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

from src.gui.themes import Typography, token


class TextInput(QWidget):
    """Labeled text input with persistent label and inline validation (spec §5.3).

    Args:
        label:       Visible, persistent label text (never placeholder-only).
        placeholder: Optional hint shown inside the field when empty.
        parent:      Parent widget.
        accessible_name:        Passed to setAccessibleName(); defaults to label.
        accessible_description: Passed to setAccessibleDescription().
    """

    validation_changed = pyqtSignal(bool)
    textChanged = pyqtSignal(str)  # proxy for _field.textChanged (spec §5.3)

    def __init__(
        self,
        label: str,
        placeholder: str = "",
        parent=None,
        accessible_name: str = "",
        accessible_description: str = "",
    ):
        super().__init__(parent)
        self._validator = None
        self._valid = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._label = QLabel(label, self)
        self._label.setFont(Typography.caption())
        layout.addWidget(self._label)

        self._field = QLineEdit(self)
        self._field.setFont(Typography.body())
        self._field.setMinimumHeight(44)
        if placeholder:
            self._field.setPlaceholderText(placeholder)
        layout.addWidget(self._field)

        self._error_label = QLabel("", self)
        self._error_label.setFont(Typography.caption())
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        self.setAccessibleName(accessible_name or label)
        if accessible_description:
            self.setAccessibleDescription(accessible_description)

        self._field.textChanged.connect(self._on_text_changed)
        self._field.textChanged.connect(self.textChanged)
        self._apply_default_style()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def text(self) -> str:
        return self._field.text()

    def setText(self, text: str):
        self._field.setText(text)

    def clear(self):
        self._field.clear()

    def setReadOnly(self, read_only: bool):
        self._field.setReadOnly(read_only)

    def set_validator(self, fn):
        """Set a callable ``fn(text: str) -> (bool, str)`` for inline validation.

        Returns (is_valid, error_message).
        """
        self._validator = fn

    def is_valid(self) -> bool:
        return self._valid

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_text_changed(self, text: str):
        if self._validator is None:
            return
        valid, msg = self._validator(text)
        if valid != self._valid:
            self._valid = valid
            self.validation_changed.emit(valid)
        self._set_error_state(not valid, msg)

    def _set_error_state(self, has_error: bool, message: str = ""):
        error_color = token("semantic_error")
        normal_color = token("text_secondary")
        border_color = error_color if has_error else token("button_secondary")
        self._field.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px 8px;
                color: {token("text_primary")};
                background-color: {token("window_background")};
            }}
            """
        )
        self._error_label.setText(message)
        self._error_label.setStyleSheet(f"color: {error_color};")
        self._error_label.setVisible(has_error and bool(message))

    def _apply_default_style(self):
        self._set_error_state(False)
        self._label.setStyleSheet(f"color: {token('text_secondary')};")
