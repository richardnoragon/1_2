#!/usr/bin/env python3
"""
Synchronize Tool for Richard's File Utilities

A streamlined synchronize utility with essential functionality.
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


class SyncWindow(StandardWindow):
    """Main window for Synchronize operations."""
    
    def __init__(self):
        super().__init__(
            title="Synchronize - Richard's File Utilities",
            window_type="utility"
        )
        self.init_ui()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_sync', self.clear_sync)
            self.menu_manager.register_callback('help_sync', self.show_help)
            
    def clear_sync(self):
        """Clear all sync operations for a new task."""
        # Clear any file lists or sync progress
        pass
        
    def show_help(self):
        """Show help dialog for Synchronize tool."""
        help_text = """
        <h2>Synchronize Tool - Help</h2>
        
        <h3>Directory Synchronization:</h3>
        <ul>
        <li><b>Source Directory:</b> The directory to sync from</li>
        <li><b>Target Directory:</b> The directory to sync to</li>
        <li><b>Sync Mode:</b> Choose one-way or two-way sync</li>
        </ul>
        
        <h3>Sync Options:</h3>
        <ul>
        <li><b>Copy newer files:</b> Only update files that are newer</li>
        <li><b>Delete extra files:</b> Remove files not in source</li>
        <li><b>Skip system files:</b> Ignore hidden/system files</li>
        <li><b>Preserve attributes:</b> Keep file timestamps and permissions</li>
        </ul>
        
        <h3>Features:</h3>
        <ul>
        <li>Real-time progress tracking</li>
        <li>Conflict resolution options</li>
        <li>Detailed sync reports</li>
        <li>Backup before sync option</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear sync operations</li>
        </ul>
        """
        
        QMessageBox.information(self, "Synchronize Help", help_text)
        
    def show_preferences(self):
        """Show Synchronize preferences."""
        QMessageBox.information(self, "Synchronize Preferences", 
                               "Synchronize preferences:\n\n"
                               "• Default sync modes\n"
                               "• File exclusion patterns\n"
                               "• Backup settings\n"
                               "• Conflict resolution rules\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh/clear the current sync operations."""
        self.clear_sync()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout
        
        # Add header
        header_label = QLabel("Synchronize")
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
            "Synchronize", 
            "Tool functionality is ready for implementation."
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = SyncWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
