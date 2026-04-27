"""T029 — DirectoryPickerDialog.

Governance:
  BC-006b, I4 — OK with Apply-to-all calls UAPService.set_directory() ONLY;
                MUST NOT call set_geometry() or save_last_used().
  U4 — relies on last-write-wins semantics; no locking or coordination.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DirectoryPickerDialog(QDialog):
    """Pick a working directory; optionally persist via UAPService (BC-006b)."""

    def __init__(
        self,
        current_directory: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Choose Working Directory")
        self.resize(480, 200)
        self._current_directory = current_directory
        self._selected_path = current_directory
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Current path display (read-only)
        layout.addWidget(QLabel("Current Directory:"))
        self.current_path_label = QLineEdit(self._current_directory)
        self.current_path_label.setReadOnly(True)
        layout.addWidget(self.current_path_label)

        # Browse button row
        browse_row = QHBoxLayout()
        self.browse_button = QPushButton("Browse…")
        browse_row.addWidget(self.browse_button)
        browse_row.addStretch()
        layout.addLayout(browse_row)

        # Apply to all tools checkbox (checked by default)
        self.apply_all_checkbox = QCheckBox("Apply to all tools (update profile)")
        self.apply_all_checkbox.setChecked(True)
        layout.addWidget(self.apply_all_checkbox)

        # Inline error label (hidden until needed)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _connect_signals(self) -> None:
        self.browse_button.clicked.connect(self._browse)

    def _browse(self) -> None:
        """Open a native directory browser. No os.chdir() calls (FR-007)."""
        start = self._selected_path or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Select Directory", start)
        if chosen:
            self._selected_path = chosen
            self.current_path_label.setText(chosen)
            self.error_label.setText("")

    def _try_accept(self) -> None:
        """Validate path and accept; show inline error if invalid."""
        path = self._selected_path
        if path and not Path(path).exists():
            self.error_label.setText(f"Directory does not exist: {path}")
            return  # Do NOT accept()

        self.error_label.setText("")

        if self.apply_all_checkbox.isChecked():
            from src.core.preferences.uap.service import UAPService

            UAPService().set_directory(path)

        self.accept()
