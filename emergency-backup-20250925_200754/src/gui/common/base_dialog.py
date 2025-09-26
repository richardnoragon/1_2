"""Base dialog class for consistent behavior across the application."""

from typing import Optional, Union
from pathlib import Path
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5 import uic

from core.error_handler import error_handler


class BaseDialog(QDialog):
    """Base class for all dialogs in the application.

    Provides common functionality:
    - UI file loading
    - Dialog positioning and sizing
    - Dialog state management
    """

    def __init__(self, ui_file: Union[str, Path, None] = None, parent=None):
        """Initialize the dialog.

        Args:
            ui_file: Path to the .ui file for this dialog
            parent: Parent widget
        """
        super().__init__(parent)
        self._ui_file = Path(ui_file) if ui_file else None
        self._load_ui()
        self.setup_dialog_properties()
        self._connect_signals()

    def _load_ui(self):
        """Load the UI file if provided."""
        if self._ui_file:
            try:
                uic.loadUi(self._ui_file, self)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load UI file {self._ui_file}: {e}"
                )

    def setup_dialog_properties(self):
        """Set up common dialog properties."""
        # Center the dialog on screen
        self.center_on_screen()
        # Set dialog flags for consistent behavior
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )

    def _connect_signals(self):
        """Connect any common signals. Override in subclasses."""
        pass

    def center_on_screen(self):
        """Center the dialog on the screen."""
        frame_geometry = self.frameGeometry()
        screen = self.screen()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def set_dialog_size(self, width: int, height: int):
        """Set the dialog size.

        Args:
            width: Dialog width in pixels
            height: Dialog height in pixels
        """
        self.setFixedSize(QSize(width, height))

    def save_dialog_state(self):
        """Save dialog state for restoration.

        Override in subclasses to save additional state.
        """
        self._saved_geometry = self.saveGeometry()

    def restore_dialog_state(self):
        """Restore saved dialog state.

        Override in subclasses to restore additional state.
        """
        if hasattr(self, "_saved_geometry"):
            self.restoreGeometry(self._saved_geometry)

    def enable_ui(self, enabled: bool = True):
        """Enable or disable the entire UI.

        Args:
            enabled: True to enable, False to disable
        """
        self.setEnabled(enabled)
