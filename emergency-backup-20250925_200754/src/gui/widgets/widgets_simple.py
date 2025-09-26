"""
Simple widgets for legacy tools.
"""

from PyQt5.QtWidgets import QWidget, QProgressBar, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


class ProgressWidget(QWidget):
    """Simple progress widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.label = QLabel("Progress:")
        self.progress_bar = QProgressBar()

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

    def set_value(self, value):
        """Set progress value."""
        self.progress_bar.setValue(value)

    def set_text(self, text):
        """Set progress text."""
        self.label.setText(text)
