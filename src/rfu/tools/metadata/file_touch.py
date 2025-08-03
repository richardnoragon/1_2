#!/usr/bin/env python3
"""
File Touch Tool for Richard's File Utilities

A streamlined file touch utility with essential functionality.
"""

import os
import sys

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox,
        QDateTimeEdit
    )
    from PyQt5.QtCore import QDateTime
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class FileTouchGUI(QMainWindow):
    """Main window for File Touch operations."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("File Touch - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("File Touch - Modify File Timestamps")
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
        
        # Add file selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_button)
        
        layout.addWidget(file_group)
        
        # Add timestamp controls
        timestamp_group = QGroupBox("File Timestamps")
        timestamp_layout = QVBoxLayout(timestamp_group)
        
        # Access time
        access_layout = QHBoxLayout()
        access_layout.addWidget(QLabel("Access Time:"))
        self.access_time_edit = QDateTimeEdit()
        self.access_time_edit.setDateTime(QDateTime.currentDateTime())
        access_layout.addWidget(self.access_time_edit)
        timestamp_layout.addLayout(access_layout)
        
        # Modification time
        mod_layout = QHBoxLayout()
        mod_layout.addWidget(QLabel("Modification Time:"))
        self.mod_time_edit = QDateTimeEdit()
        self.mod_time_edit.setDateTime(QDateTime.currentDateTime())
        mod_layout.addWidget(self.mod_time_edit)
        timestamp_layout.addLayout(mod_layout)
        
        layout.addWidget(timestamp_group)
        
        # Add action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh from File")
        self.refresh_button.clicked.connect(self.refresh_timestamps)
        self.refresh_button.setEnabled(False)
        button_layout.addWidget(self.refresh_button)
        
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_timestamps)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        self.current_time_button = QPushButton("Set to Current Time")
        self.current_time_button.clicked.connect(self.set_current_time)
        button_layout.addWidget(self.current_time_button)
        
        layout.addLayout(button_layout)
        
        # Add status label
        self.status_label = QLabel("Ready - Select a file to begin")
        self.status_label.setStyleSheet("padding: 10px; color: #666;")
        layout.addWidget(self.status_label)
        
    def select_file(self):
        """Select a file to modify timestamps."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Touch", "", "All Files (*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.refresh_button.setEnabled(True)
            self.apply_button.setEnabled(True)
            self.status_label.setText("File selected - Use 'Refresh' to load current timestamps")
            
            # Automatically refresh timestamps
            self.refresh_timestamps()
            
    def refresh_timestamps(self):
        """Load current timestamps from the selected file."""
        if not self.current_file or not os.path.exists(self.current_file):
            QMessageBox.warning(self, "Warning", "Please select a valid file first.")
            return
            
        try:
            stat = os.stat(self.current_file)
            
            # Set access time
            access_time = QDateTime.fromSecsSinceEpoch(int(stat.st_atime))
            self.access_time_edit.setDateTime(access_time)
            
            # Set modification time
            mod_time = QDateTime.fromSecsSinceEpoch(int(stat.st_mtime))
            self.mod_time_edit.setDateTime(mod_time)
            
            self.status_label.setText("Timestamps loaded from file")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading file timestamps: {str(e)}")
            self.status_label.setText("Error loading timestamps")
            
    def set_current_time(self):
        """Set both timestamps to current time."""
        current_time = QDateTime.currentDateTime()
        self.access_time_edit.setDateTime(current_time)
        self.mod_time_edit.setDateTime(current_time)
        self.status_label.setText("Timestamps set to current time")
        
    def apply_timestamps(self):
        """Apply the timestamp changes to the file."""
        if not self.current_file or not os.path.exists(self.current_file):
            QMessageBox.warning(self, "Warning", "Please select a valid file first.")
            return
            
        try:
            # Get timestamps from GUI
            access_time = self.access_time_edit.dateTime().toSecsSinceEpoch()
            mod_time = self.mod_time_edit.dateTime().toSecsSinceEpoch()
            
            # Apply timestamps to file
            os.utime(self.current_file, (access_time, mod_time))
            
            self.status_label.setText("Timestamps applied successfully")
            QMessageBox.information(
                self, "Success",
                "File timestamps have been updated successfully!"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying timestamps: {str(e)}")
            self.status_label.setText("Error applying timestamps")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = FileTouchGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()