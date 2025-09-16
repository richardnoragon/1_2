"""
Simple BaseWindow implementation for legacy tools.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt


class BaseWindow(QMainWindow):
    """Simple base window for legacy tools."""
    
    def __init__(self, title="Tool Window"):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
    def setup_ui(self):
        """Override this method to setup the UI."""
        pass
        
    def showEvent(self, event):
        """Called when window is shown."""
        super().showEvent(event)
        self.setup_ui()
