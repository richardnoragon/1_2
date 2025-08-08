#!/usr/bin/env python3
"""
Split/Join Files Tool for Richard's File Utilities

A streamlined split/join files utility with essential functionality.
"""

import os
import sys

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow
    StandardWindow = QMainWindow


class FileSplitJoinGUI(StandardWindow):
    """Main window for Split/Join Files operations."""
    
    def __init__(self):
        super().__init__(
            title="Split/Join Files - Richard's File Utilities",
            window_type="utility"
        )
        self.init_ui()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_split_join', 
                                               self.clear_operations)
            self.menu_manager.register_callback('help_split_join', 
                                               self.show_help)
            
    def clear_operations(self):
        """Clear all operations for a new split/join task."""
        # Clear any file lists or progress indicators
        pass
        
    def show_help(self):
        """Show help dialog for Split/Join Files tool."""
        help_text = """
        <h2>Split/Join Files - Help</h2>
        
        <h3>File Splitting:</h3>
        <ul>
        <li><b>Source File:</b> Select the large file you want to split</li>
        <li><b>Split Size:</b> Choose the size for each split part</li>
        <li><b>Output Directory:</b> Where to save the split files</li>
        </ul>
        
        <h3>File Joining:</h3>
        <ul>
        <li><b>First Part:</b> Select the first part of split files (.001)</li>
        <li><b>Auto-detect:</b> Tool will find all related parts</li>
        <li><b>Output File:</b> Choose name for the joined file</li>
        </ul>
        
        <h3>Features:</h3>
        <ul>
        <li>Progress tracking for large files</li>
        <li>Integrity checking with checksums</li>
        <li>Support for various split sizes</li>
        <li>Automatic part numbering</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear operations</li>
        </ul>
        """
        
        QMessageBox.information(self, "Split/Join Files Help", help_text)
        
    def show_preferences(self):
        """Show Split/Join Files preferences."""
        QMessageBox.information(self, "Split/Join Files Preferences", 
                               "Split/Join Files preferences:\n\n"
                               "• Default split sizes\n"
                               "• Output naming patterns\n"
                               "• Checksum verification settings\n"
                               "• Progress display options\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh/clear the current operations."""
        self.clear_operations()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Add header
        header_label = QLabel("Split/Join Files")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Add file selection area
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        
        select_button = QPushButton("Select Files")
        select_button.clicked.connect(self.select_files)
        file_layout.addWidget(select_button)
        
        layout.addWidget(file_group)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        content_label = QLabel("Tool functionality will be implemented here.")
        content_label.setStyleSheet("padding: 20px; color: #666;")
        layout.addWidget(content_label)
        
        # Add action button
        action_button = QPushButton("Execute Action")
        action_button.clicked.connect(self.execute_action)
        action_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(action_button)
        
    def select_files(self):
        """Select files for processing."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "", "All Files (*)"
        )
        for file_path in files:
            self.file_list.addItem(file_path)
            
    def execute_action(self):
        """Main action method for this tool."""
        QMessageBox.information(
            self, 
            "Split/Join Files", 
            "Tool functionality is ready for implementation."
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = FileSplitJoinGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
