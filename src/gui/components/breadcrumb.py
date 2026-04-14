"""
src/gui/components/breadcrumb.py — Local navigation breadcrumb (P1-C12).

Spec §5.1: local navigation only; MUST NOT reproduce Hub navigation.
Each segment is keyboard-activatable; emits segment_clicked(index).
"""

from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from src.gui.themes import Typography, token


class Breadcrumb(QWidget):
    """Path-segment breadcrumb for local in-tool navigation (spec §5.1).

    Args:
        segments: Initial list of path segment strings.
        parent:   Parent widget.

    Signals:
        segment_clicked(int): Emitted with the 0-based index of the clicked segment.
    """

    segment_clicked = pyqtSignal(int)

    def __init__(self, segments: List[str] = None, parent=None):
        super().__init__(parent)
        self._segments: List[str] = []

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        self._layout.addStretch()

        self.setAccessibleName("Breadcrumb navigation")

        if segments:
            self.set_segments(segments)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_segments(self, segments: List[str]):
        """Replace the current segments with a new list."""
        self._segments = list(segments)
        self._rebuild()

    def append_segment(self, segment: str):
        self._segments.append(segment)
        self._rebuild()

    def pop_segment(self):
        if self._segments:
            self._segments.pop()
            self._rebuild()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rebuild(self):
        # Clear existing widgets (skip the trailing stretch)
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sep_color = token("text_secondary")

        for i, seg in enumerate(self._segments):
            btn = QPushButton(seg, self)
            btn.setFont(Typography.caption())
            btn.setFlat(True)
            btn.setMinimumHeight(44)
            btn.setAccessibleName(f"Navigate to {seg}")
            is_last = i == len(self._segments) - 1
            fg = token("text_primary") if is_last else token("accent")
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {fg};
                    border: none;
                    padding: 2px 4px;
                    text-decoration: {"none" if is_last else "underline"};
                }}
                QPushButton:disabled {{ color: {token("text_disabled")}; }}
                """
            )
            btn.setEnabled(not is_last)
            idx = i  # capture for lambda
            btn.clicked.connect(lambda _, ix=idx: self.segment_clicked.emit(ix))
            self._layout.insertWidget(self._layout.count() - 1, btn)

            if not is_last:
                sep = QLabel("›", self)
                sep.setFont(Typography.caption())
                sep.setStyleSheet(f"color: {sep_color};")
                self._layout.insertWidget(self._layout.count() - 1, sep)
