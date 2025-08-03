#!/usr/bin/env python3
"""
Simple Checksum GUI for Richard's File Utilities
"""

import sys
import os
import hashlib
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QProgressBar,
    QApplication, QMessageBox, QGroupBox, QFileDialog
)


class ChecksumGUI(QMainWindow):
    """Simple Checksum Calculator GUI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Checksum Calculator - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("File Checksum Calculator")
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
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        select_button = QPushButton("Select File")
        select_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_button)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Calculate button
        calc_button = QPushButton("Calculate MD5 Checksum")
        calc_button.clicked.connect(self.calculate_checksum)
        layout.addWidget(calc_button)
        
        # Results
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        self.selected_file = None
    
    def select_file(self):
        """Select a file for checksum calculation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
    
    def calculate_checksum(self):
        """Calculate MD5 checksum."""
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
        
        try:
            md5_hash = hashlib.md5()
            with open(self.selected_file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            
            checksum = md5_hash.hexdigest()
            result = f"MD5: {checksum}"
            self.results_list.addItem(result)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate checksum: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = ChecksumGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
