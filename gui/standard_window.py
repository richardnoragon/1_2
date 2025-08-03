"""
Simplified standard window for privacy tools compatibility.

This provides a basic StandardWindow class that can be imported by privacy tools
without complex dependencies.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QStatusBar, QGroupBox, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StandardWindow(QMainWindow):
    """Simplified standard window for privacy tools."""
    
    def __init__(self, title="RFU Utility"):
        """Initialize the standard window."""
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(600, 500)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Apply basic styling
        self._apply_basic_styling()
    
    def _apply_basic_styling(self):
        """Apply basic styling to the window."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #f5f5f5;
            }
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
    
    def create_header(self, text: str) -> QLabel:
        """Create a header label."""
        header = QLabel(text)
        header.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        header.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        return header
    
    def create_group_box(self, title: str) -> QGroupBox:
        """Create a styled group box."""
        group_box = QGroupBox(title)
        return group_box
    
    def create_button(self, text: str, callback=None, primary: bool = False) -> QPushButton:
        """Create a styled button."""
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        
        if primary:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-height: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
        
        return button
    
    def create_progress_bar(self) -> QProgressBar:
        """Create a styled progress bar."""
        progress = QProgressBar()
        progress.setVisible(False)
        return progress
    
    def show_status_message(self, message: str, timeout: int = 0):
        """Show a status message."""
        self.status_bar.showMessage(message, timeout)
    
    def show_error_dialog(self, title: str, message: str):
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)
    
    def show_warning_dialog(self, title: str, message: str):
        """Show a warning dialog."""
        QMessageBox.warning(self, title, message)
    
    def show_info_dialog(self, title: str, message: str):
        """Show an info dialog."""
        QMessageBox.information(self, title, message)


class StandardDialog(StandardWindow):
    """Simplified standard dialog."""
    
    def __init__(self, title="RFU Dialog"):
        """Initialize the standard dialog."""
        super().__init__(title)
        self.setMinimumSize(400, 300)
        # Remove status bar for dialogs
        self.setStatusBar(None)