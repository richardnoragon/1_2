"""
Safe StandardWindow Implementation - Dependency-Free Fallback

This module provides a safe, dependency-free StandardWindow implementation
that can be used when the full theme system is not available.
"""

import os
import sys

from PyQt5.QtCore import Qt
from src.gui.themes import token
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class SafeStandardWindow(QMainWindow):
    """Safe StandardWindow implementation without external dependencies."""

    def __init__(
        self,
        title="Richard's File Utilities",
        window_type="utility",
        parent=None,
    ):
        super().__init__(parent)
        self.title = title
        self.window_type = window_type

        self._setup_window()
        self._create_central_widget()
        self._create_menu_bar()
        self._create_status_bar()
        self._apply_basic_styling()

    def _setup_window(self):
        """Setup basic window properties."""
        self.setWindowTitle(self.title)

        # Set reasonable default size
        min_width = 600
        min_height = 500
        self.setMinimumSize(min_width, min_height)
        self.resize(min_width + 200, min_height + 150)

    def _create_central_widget(self):
        """Create central widget with standard layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        self.central_widget.setLayout(self.main_layout)

    def _create_menu_bar(self):
        """Create basic menu bar."""
        try:
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("&File")

            # Exit action
            exit_action = QAction("E&xit", self)
            exit_action.setShortcut(QKeySequence("Ctrl+Q"))
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # Help menu
            help_menu = menubar.addMenu("&Help")

            about_action = QAction("&About", self)
            about_action.triggered.connect(self._show_about)
            help_menu.addAction(about_action)

        except Exception as e:
            print(f"Error creating menu bar: {e}")

    def _create_status_bar(self):
        """Create standard status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _apply_basic_styling(self):
        """Apply basic styling without external dependencies."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: {token('window_background')};
                color: {token('text_primary')};
            }
            QPushButton {
                background-color: {token('accent')};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: {token('button_primary_hover')};
            }
            QPushButton:pressed {
                background-color: {token('button_primary_pressed')};
            }
            QPushButton:disabled {
                background-color: {token('text_disabled')};
            }
            QLabel {
                color: {token('text_primary')};
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid {token('secondary')};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )

    def ensure_menu_bar(self):
        """Ensure menu bar exists - safe fallback method."""
        if not self.menuBar() or not self.menuBar().actions():
            self._create_menu_bar()

    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        return header

    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return button

    def create_group_box(self, title):
        """Create a standard group box."""
        return QGroupBox(title)

    def create_progress_bar(self):
        """Create a standard progress bar."""
        progress = QProgressBar()
        progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid {token('text_disabled')};
                border-radius: 4px;
                text-align: center;
                background-color: {token('dialog_background')};
            }
            QProgressBar::chunk {
                background-color: {token('accent')};
                border-radius: 3px;
            }
        """
        )
        return progress

    def show_status_message(self, message, timeout=3000):
        """Show status message with optional timeout."""
        self.status_bar.showMessage(message, timeout)

    def show_error_dialog(self, title, message):
        """Show error dialog."""
        QMessageBox.critical(self, title, message)

    def show_info_dialog(self, title, message):
        """Show info dialog."""
        QMessageBox.information(self, title, message)

    def show_warning_dialog(self, title, message):
        """Show warning dialog."""
        QMessageBox.warning(self, title, message)

    def get_file_path(self, title="Select File", file_filter="All Files (*)"):
        """Show file selection dialog."""
        return QFileDialog.getOpenFileName(self, title, "", file_filter)[0]

    def get_directory_path(self, title="Select Directory"):
        """Show directory selection dialog."""
        return QFileDialog.getExistingDirectory(self, title)

    def get_save_file_path(
        self, title="Save File", file_filter="All Files (*)"
    ):
        """Show save file dialog."""
        return QFileDialog.getSaveFileName(self, title, "", file_filter)[0]

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            f"{self.title}\n\n"
            "Part of Richard's File Utilities\n"
            "© 2025 Richard Noragon",
        )

    # Safe fallback methods for menu integration
    def show_preferences(self):
        """Show preferences dialog - safe fallback."""
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog not implemented for this tool.",
        )

    def show_options(self):
        """Show options dialog - safe fallback."""
        QMessageBox.information(
            self, "Options", "Options dialog not implemented for this tool."
        )

    def refresh_view(self):
        """Refresh the current view - safe fallback."""
        if hasattr(self, "statusBar"):
            self.statusBar().showMessage("Refreshed", 2000)
