"""
Standardized base window class for all GUI utilities.
Provides consistent styling, layout, and behavior across all windows.
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGroupBox, QProgressBar, QMessageBox,
                             QFileDialog, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from file_utilities_2.gui.themes import ThemeManager, Colors, Fonts, Spacing, Dimensions


class StandardWindow(QMainWindow):
    """Standardized main window for utilities."""
    
    def __init__(self, title="Richard's File Utilities", icon_path=None):
        super().__init__()
        self.title = title
        self.icon_path = icon_path or self._get_default_icon()
        
        self._setup_window()
        self._create_central_widget()
        self._create_status_bar()
        self._apply_theme()
    
    def _setup_window(self):
        """Setup basic window properties."""
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))
        self.setMinimumSize(Dimensions.UTILITY_WINDOW_MIN_WIDTH, 
                           Dimensions.UTILITY_WINDOW_MIN_HEIGHT)
        self.resize(Dimensions.UTILITY_WINDOW_MIN_WIDTH + 200, 
                   Dimensions.UTILITY_WINDOW_MIN_HEIGHT + 150)
    
    def _create_central_widget(self):
        """Create central widget with standard layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = ThemeManager.create_standard_layout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
    
    def _create_status_bar(self):
        """Create standard status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _apply_theme(self):
        """Apply standard theme to the window."""
        ThemeManager.apply_utility_window_theme(self)
    
    def _get_default_icon(self):
        """Get default application icon."""
        return os.path.join(os.path.dirname(__file__), '..', 'icons', 'app_icon.png')
    
    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        ThemeManager.style_label(header, is_header=True)
        header.setAlignment(Qt.AlignCenter)
        return header
    
    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if primary:
            ThemeManager.style_primary_button(button)
        else:
            ThemeManager.style_secondary_button(button)
        
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    def create_group_box(self, title):
        """Create a standard group box."""
        group_box = QGroupBox(title)
        ThemeManager.style_group_box(group_box)
        return group_box
    
    def create_progress_bar(self):
        """Create a standard progress bar."""
        progress = QProgressBar()
        ThemeManager.style_progress_bar(progress)
        return progress
    
    def show_status_message(self, message, timeout=3000):
        """Show status message with optional timeout."""
        self.status_bar.showMessage(message, timeout)
    
    def show_error_dialog(self, title, message):
        """Show error dialog with standard styling."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def show_info_dialog(self, title, message):
        """Show info dialog with standard styling."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def show_warning_dialog(self, title, message):
        """Show warning dialog with standard styling."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def get_file_path(self, title="Select File", file_filter="All Files (*)"):
        """Show file selection dialog with standard styling."""
        return QFileDialog.getOpenFileName(self, title, "", file_filter)[0]
    
    def get_directory_path(self, title="Select Directory"):
        """Show directory selection dialog with standard styling."""
        return QFileDialog.getExistingDirectory(self, title)
    
    def get_save_file_path(self, title="Save File", file_filter="All Files (*)"):
        """Show save file dialog with standard styling."""
        return QFileDialog.getSaveFileName(self, title, "", file_filter)[0]


class StandardDialog(QDialog):
    """Standardized dialog for utilities."""
    
    def __init__(self, title="Dialog", parent=None):
        super().__init__(parent)
        self.title = title
        
        self._setup_dialog()
        self._create_layout()
        self._apply_theme()
    
    def _setup_dialog(self):
        """Setup basic dialog properties."""
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.setMinimumSize(Dimensions.DIALOG_WIDTH, Dimensions.DIALOG_HEIGHT)
    
    def _create_layout(self):
        """Create standard dialog layout."""
        self.main_layout = ThemeManager.create_standard_layout(self)
        self.setLayout(self.main_layout)
    
    def _apply_theme(self):
        """Apply standard theme to the dialog."""
        ThemeManager.apply_utility_window_theme(self)
    
    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        ThemeManager.style_label(header, is_header=True)
        header.setAlignment(Qt.AlignCenter)
        return header
    
    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if primary:
            ThemeManager.style_primary_button(button)
        else:
            ThemeManager.style_secondary_button(button)
        
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    def create_group_box(self, title):
        """Create a standard group box."""
        group_box = QGroupBox(title)
        ThemeManager.style_group_box(group_box)
        return group_box
    
    def show_error_dialog(self, title, message):
        """Show error dialog."""
        QMessageBox.critical(self, title, message)
    
    def show_info_dialog(self, title, message):
        """Show info dialog."""
        QMessageBox.information(self, title, message)


class StandardUtilityWidget(QWidget):
    """Standardized widget for embedding in other windows."""
    
    def __init__(self, title="Utility", parent=None):
        super().__init__(parent)
        self.title = title
        
        self._create_layout()
        self._apply_theme()
    
    def _create_layout(self):
        """Create standard widget layout."""
        self.main_layout = ThemeManager.create_standard_layout(self)
        self.setLayout(self.main_layout)
    
    def _apply_theme(self):
        """Apply standard theme to the widget."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.WINDOW_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
    
    def create_header(self, text):
        """Create a standard header label."""
        header = QLabel(text)
        ThemeManager.style_label(header, is_header=True)
        header.setAlignment(Qt.AlignCenter)
        return header
    
    def create_button(self, text, callback=None, primary=True):
        """Create a standard button."""
        button = QPushButton(text)
        if primary:
            ThemeManager.style_primary_button(button)
        else:
            ThemeManager.style_secondary_button(button)
        
        if callback:
            button.clicked.connect(callback)
        
        return button