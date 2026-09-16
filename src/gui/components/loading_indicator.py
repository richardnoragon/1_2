"""
src/gui/components/loading_indicator.py — Loading indicator widget (P1-C13).

Spec §8.4: hidden on creation; shows only after 300 ms delay; supports
cancellable mode; never blocks the UI thread.
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.rfu import font_tokens
from src.gui.themes import Typography, token


class LoadingIndicator(QWidget):
    """Spec-compliant loading indicator (spec §8.4, P1-C13).

    Stays hidden until ``start()`` is called and 300 ms elapse.
    If ``stop()`` is called within 300 ms the widget never appears.

    Args:
        parent:      Parent widget.
        cancellable: If True, a Cancel button is shown; pressing it emits
                     ``cancelled``.
        message:     Optional status message displayed above the progress bar.
    """

    cancelled = pyqtSignal()

    def __init__(self, parent=None, cancellable: bool = False, message: str = ""):
        super().__init__(parent)
        self._cancellable = cancellable
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.setInterval(300)
        self._show_timer.timeout.connect(self._show_now)

        self._build_ui(message)
        self.hide()

        self.setAccessibleName("Loading")
        self.setAccessibleDescription("Operation in progress")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        """Schedule appearance after 300 ms delay."""
        self._progress_bar.setRange(0, 0)
        self._show_timer.start()

    def stop(self):
        """Cancel the timer and hide immediately."""
        self._show_timer.stop()
        self.hide()

    def set_progress(self, value: int, maximum: int = 100):
        """Update the progress bar."""
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.setValue(value)

    def set_message(self, message: str):
        """Update the status message."""
        self._message_label.setText(message)
        self._message_label.setVisible(bool(message))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_ui(self, message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self._message_label = QLabel(message, self)
        font_tokens.bind(self._message_label, "font.body")
        self._message_label.setAlignment(Qt.AlignCenter)
        self._message_label.setStyleSheet(f"color: {token('text_secondary')};")
        self._message_label.setVisible(bool(message))
        layout.addWidget(self._message_label)

        self._progress_bar = QProgressBar(self)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setMinimumHeight(12)
        self._progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid {token("button_secondary")};
                border-radius: 6px;
                background-color: {token("background")};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {token("accent")};
                border-radius: 5px;
            }}
            """
        )
        layout.addWidget(self._progress_bar)

        if self._cancellable:
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            self._cancel_btn = QPushButton("Cancel", self)
            font_tokens.bind(self._cancel_btn, "font.body")
            self._cancel_btn.setMinimumHeight(44)
            self._cancel_btn.setMinimumWidth(120)
            self._cancel_btn.setAccessibleName("Cancel operation")
            self._cancel_btn.clicked.connect(self._on_cancel)
            btn_row.addWidget(self._cancel_btn)
            layout.addLayout(btn_row)

        self.setStyleSheet(
            f"QWidget {{ background-color: {token('dialog_background')}; border-radius: 6px; }}"
        )

    def _show_now(self):
        self.show()

    def _on_cancel(self):
        self.stop()
        self.cancelled.emit()
