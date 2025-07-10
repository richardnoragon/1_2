"""Base window class for consistent GUI behavior across the application."""
from typing import Optional, Union
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QWidget, QDialog, QStatusBar, QProgressBar
from PyQt5.QtCore import Qt, QSize
from PyQt5 import uic

from core.error_handler import error_handler



class BaseWindow(QMainWindow):
    """Base class for all main windows in the application.
    
    Provides common functionality:
    - UI file loading
    - Window positioning and sizing
    - Progress and status updates
    - Window state management
    """
    
    def __init__(self, ui_file: Union[str, Path, None] = None):
        """Initialize the window.
        
        Args:
            ui_file: Path to the .ui file for this window
        """
        super().__init__()
        self._ui_file = Path(ui_file) if ui_file else None
        self._load_ui()
        self.setup_window_properties()
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
                
    def setup_window_properties(self):
        """Set up common window properties."""
        # Center the window on screen
        self.center_on_screen()
        # Set window flags for consistent behavior
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )
        
    def _connect_signals(self):
        """Connect any common signals. Override in subclasses."""
        pass
        
    def center_on_screen(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen = self.screen()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def set_window_size(self, width: int, height: int):
        """Set the window size.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.setFixedSize(QSize(width, height))
        
    def set_status_message(self, message: str):
        """Set status bar message.
        
        Args:
            message: Message to display
        """
        if not hasattr(self, 'statusBar'):
            self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(message)
        
    def set_progress(self, value: int, maximum: int = 100):
        """Set progress in status bar.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        if not hasattr(self, '_progress_bar'):
            self._progress_bar = QProgressBar()
            self.statusBar().addPermanentWidget(self._progress_bar)
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.setValue(value)
        
    def save_window_state(self):
        """Save window state for restoration.
        
        Override in subclasses to save additional state.
        """
        self._saved_geometry = self.saveGeometry()
        self._saved_state = self.saveState()
        
    def restore_window_state(self):
        """Restore saved window state.
        
        Override in subclasses to restore additional state.
        """
        if hasattr(self, '_saved_geometry'):
            self.restoreGeometry(self._saved_geometry)
        if hasattr(self, '_saved_state'):
            self.restoreState(self._saved_state)
            
    def enable_ui(self, enabled: bool = True):
        """Enable or disable the entire UI.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.setEnabled(enabled)
        if hasattr(self, 'centralWidget'):
            self.centralWidget().setEnabled(enabled)
