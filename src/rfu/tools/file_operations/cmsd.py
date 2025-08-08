#!/usr/bin/env python3
"""
Copy/Move/Sync/Delete Tool for Richard's File Utilities

A streamlined copy/move/sync/delete utility with essential functionality.
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


class CopyMoveSyncDeleteWindow(StandardWindow):
    """Main window for Copy/Move/Sync/Delete operations."""
    
    def __init__(self):
        super().__init__(
            title="Copy/Move/Sync/Delete - Richard's File Utilities",
            window_type="utility"
        )
        self.init_ui()
        self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_operation', 
                                               self.clear_operations)
            self.menu_manager.register_callback('help_cmsd', self.show_help)
            
    def clear_operations(self):
        """Clear all operations for a new task."""
        # Clear any file lists or operation progress
        pass
        
    def show_help(self):
        """Show help dialog for Copy/Move/Sync/Delete tool."""
        help_text = """
        <h2>Copy/Move/Sync/Delete - Help</h2>
        
        <h3>Copy Operations:</h3>
        <ul>
        <li><b>Source:</b> Select files or folders to copy</li>
        <li><b>Destination:</b> Choose where to copy files</li>
        <li><b>Options:</b> Preserve attributes, overwrite settings</li>
        </ul>
        
        <h3>Move Operations:</h3>
        <ul>
        <li><b>Source:</b> Select files or folders to move</li>
        <li><b>Destination:</b> Choose new location</li>
        <li><b>Safety:</b> Confirmation for destructive operations</li>
        </ul>
        
        <h3>Sync Operations:</h3>
        <ul>
        <li><b>Two Directories:</b> Keep directories synchronized</li>
        <li><b>Sync Mode:</b> One-way or two-way synchronization</li>
        <li><b>Filters:</b> Include/exclude patterns</li>
        </ul>
        
        <h3>Delete Operations:</h3>
        <ul>
        <li><b>Secure Delete:</b> Overwrite data before deletion</li>
        <li><b>Recycle Bin:</b> Move to trash instead of permanent delete</li>
        <li><b>Confirmation:</b> Safety prompts for all deletions</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear operations</li>
        </ul>
        """
        
        QMessageBox.information(self, "Copy/Move/Sync/Delete Help", help_text)
        
    def show_preferences(self):
        """Show Copy/Move/Sync/Delete preferences."""
        QMessageBox.information(self, "Copy/Move/Sync/Delete Preferences", 
                               "Copy/Move/Sync/Delete preferences:\n\n"
                               "• Default operation modes\n"
                               "• File conflict resolution\n"
                               "• Security delete settings\n"
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
        header_label = QLabel("Copy/Move/Sync/Delete")
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
            "Copy/Move/Sync/Delete", 
            "Tool functionality is ready for implementation."
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = CopyMoveSyncDeleteWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
