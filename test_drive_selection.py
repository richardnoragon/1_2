"""
Drive Selection File Browser Test

A standalone test application demonstrating the enhanced file browser
with cross-platform drive selection functionality.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout,
                             QWidget)

from src.file_explorer.enhanced_file_browser import EnhancedFileBrowser


class DriveSelectionTestWindow(QMainWindow):
    """Test window for drive selection file browser."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Drive Selection File Browser - Test Interface")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Enhanced File Browser with Drive Selection")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
        """)
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel("""
<b>Features:</b><br>
• <b>Drive Selection:</b> Dropdown menu showing all available system drives<br>
• <b>Cross-Platform:</b> Windows drives (C:, D:, etc.) and Unix mount points (/home, /media, etc.)<br>
• <b>Navigation Bar:</b> Drive dropdown + current path display + navigation buttons<br>
• <b>File Listing:</b> Detailed view with file sizes, types, and modification dates<br>
• <b>Directory Navigation:</b> Double-click folders to navigate, use ↑ button to go up<br>
• <b>File Operations:</b> Double-click files to open with default application<br><br>

<b>Usage:</b><br>
1. Select a drive from the dropdown to browse different storage devices<br>
2. Navigate through directories using the file list or navigation buttons<br>
3. The path display shows your current location within the selected drive<br>
4. Use the refresh button (⟲) to update the current directory listing
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            font-size: 12px;
            color: #34495e;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
        """)
        layout.addWidget(instructions)
        
        # Enhanced file browser
        self.file_browser = EnhancedFileBrowser()
        
        # Connect signals for status updates
        self.file_browser.pathChanged.connect(self.on_path_changed)
        self.file_browser.fileActivated.connect(self.on_file_activated)
        self.file_browser.directoryChanged.connect(self.on_directory_changed)
        
        layout.addWidget(self.file_browser, 1)
        
        # Status display
        self.status_label = QLabel("Ready - Select a drive to begin browsing")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #495057;
            background-color: #e9ecef;
            border: 1px solid #ced4da;
            padding: 5px 10px;
            border-radius: 3px;
        """)
        layout.addWidget(self.status_label)
    
    def on_path_changed(self, path):
        """Handle path change events."""
        self.status_label.setText(f"Current location: {path}")
    
    def on_file_activated(self, file_path):
        """Handle file activation events."""
        file_name = Path(file_path).name
        self.status_label.setText(f"Opened file: {file_name}")
    
    def on_directory_changed(self, directory):
        """Handle directory change events."""
        self.status_label.setText(f"Browsing directory: {directory}")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Drive Selection File Browser Test")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("RFU")
    
    # Create and show main window
    window = DriveSelectionTestWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()