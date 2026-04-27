"""T028 — FontPickerDialog.

Governance:
  N7 — OK handler MUST NOT call parent_window.setFont() directly.
       Font propagation flows exclusively through:
       UAPService.set_font() → set_font_preferences() → ThemeManager.uap_font_changed → StandardWindow._on_uap_font_changed
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFontDatabase,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class FontPickerDialog(QDialog):
    """Pick a font family and size; propagate change via UAPService (N7)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Choose Font")
        self.resize(440, 380)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Font family list
        self.font_list = QListWidget()
        db = QFontDatabase()
        self.font_list.addItems(db.families())
        layout.addWidget(QLabel("Font Family:"))
        layout.addWidget(self.font_list)

        # Size spinner
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.size_spinner = QSpinBox()
        self.size_spinner.setMinimum(6)
        self.size_spinner.setMaximum(32)
        self.size_spinner.setValue(10)
        size_row.addWidget(self.size_spinner)
        size_row.addStretch()
        layout.addLayout(size_row)

        # Live preview
        self.preview_label = QLabel("AaBbCcDdEeFf 0123456789")
        self.preview_label.setObjectName("preview_label")
        layout.addWidget(QLabel("Preview:"))
        layout.addWidget(self.preview_label)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _connect_signals(self) -> None:
        self.font_list.currentTextChanged.connect(self._update_preview)
        self.size_spinner.valueChanged.connect(self._update_preview)

    def _update_preview(self) -> None:
        family = self.font_list.currentItem()
        family_name = family.text() if family else ""
        size = self.size_spinner.value()
        self.preview_label.setFont(QFont(family_name, size))

    def _on_ok(self) -> None:
        """Call UAPService.set_font — do NOT call parent.setFont() directly (N7)."""
        from src.core.preferences.uap.service import UAPService

        item = self.font_list.currentItem()
        family = item.text() if item else "Segoe UI"
        size = self.size_spinner.value()
        UAPService().set_font(family, size)
        self.accept()

    def accept(self) -> None:  # type: ignore[override]
        """Override to allow test doubles to intercept."""
        super().accept()
