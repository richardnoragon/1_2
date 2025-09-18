"""Base window class for consistent GUI behavior across the application."""
from typing import Union
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QStatusBar, QProgressBar,
        QMenu, QAction, QMenuBar
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5 import uic
    PYQT5_AVAILABLE = True
except ImportError:
    # Fallback for when PyQt5 is not available
    PYQT5_AVAILABLE = False
    QMainWindow = object
    QWidget = object
    QStatusBar = object
    QProgressBar = object
    QMenu = object
    QAction = object
    QMenuBar = object
    Qt = None
    QSize = None
    uic = None

from ...core.error_handler import error_handler


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
        self.setup_menus()
        self._connect_signals()
        
    def _load_ui(self):
        """Load the UI file if provided."""
        if self._ui_file:
            try:
                uic.loadUi(self._ui_file, self)
            except Exception as e:
                error_handler.handle_error(
                    e, 
                    f"loading UI file {self._ui_file}",
                    f"Failed to load UI file: {e}"
                )
                
    def setup_window_properties(self):
        """Set up common window properties."""
        # Center the window on screen
        self.center_on_screen()
        # Set window flags for consistent behavior
        self.setWindowFlags(
            Qt.Window |  # type: ignore
            Qt.WindowCloseButtonHint |  # type: ignore
            Qt.WindowMinimizeButtonHint |  # type: ignore
            Qt.WindowMaximizeButtonHint  # type: ignore
        )

    def setup_menus(self):
        """Set up the application menus."""
        # Create menu bar if it doesn't exist
        if not self.menuBar():
            self.setMenuBar(QMenuBar())

        # Find or create View menu
        view_menu = None
        for action in self.menuBar().actions():
            if action.text() == "View":
                view_menu = action.menu()
                break

        if not view_menu:
            view_menu = QMenu("View", self)
            self.menuBar().addMenu(view_menu)

        # Add appearance settings action
        appearance_action = QAction("Appearance Settings...", self)
        appearance_action.triggered.connect(self.show_appearance_settings)
        appearance_action.setStatusTip("Configure application appearance")
        view_menu.addAction(appearance_action)
        
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
        """Enable or disable all UI elements in the window.
        
        Args:
            enabled: Whether to enable (True) or disable (False) the UI
        """
        for widget in self.findChildren(QWidget):
            widget.setEnabled(enabled)
            
    def show_appearance_settings(self) -> None:
        """Show the appearance settings dialog."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Appearance Settings",
                "Appearance settings will be available in a future update."
            )
        except Exception as e:
            error_handler.handle_error(
                e,
                "showing appearance settings",
                "Failed to show appearance settings dialog"
            )
