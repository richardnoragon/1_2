#!/usr/bin/env python3
"""
Simple Duplicate Finder GUI for Richard's File Utilities
"""

import sys
import os
import hashlib
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QListWidget,
    QApplication, QMessageBox, QGroupBox, QFileDialog
)


class DuplicateFinderApp(QMainWindow):
    """Simple Duplicate Finder GUI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Duplicate Finder - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("Duplicate File Finder")
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
        
        # Directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QVBoxLayout(dir_group)
        
        select_button = QPushButton("Select Directory")
        select_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(select_button)
        
        self.dir_label = QLabel("No directory selected")
        dir_layout.addWidget(self.dir_label)
        
        layout.addWidget(dir_group)
        
        # Find button
        find_button = QPushButton("Find Duplicates")
        find_button.clicked.connect(self.find_duplicates)
        layout.addWidget(find_button)
        
        # Results
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        self.selected_directory = None
    
    def select_directory(self):
        """Select a directory to scan."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory to Scan"
        )
        if dir_path:
            self.selected_directory = dir_path
            self.dir_label.setText(f"Selected: {dir_path}")
    
    def find_duplicates(self):
        """Find duplicate files in the selected directory."""
        if not self.selected_directory:
            QMessageBox.warning(self, "Warning", "Please select a directory first.")
            return
        
        self.results_list.clear()
        self.results_list.addItem("Scanning for duplicates...")
        QApplication.processEvents()
        
        try:
            file_hashes = {}
            duplicates = []
            
            for root, dirs, files in os.walk(self.selected_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        
                        if file_hash in file_hashes:
                            duplicates.append((file_hashes[file_hash], file_path))
                        else:
                            file_hashes[file_hash] = file_path
                    except Exception:
                        continue
            
            self.results_list.clear()
            if duplicates:
                self.results_list.addItem(f"Found {len(duplicates)} duplicate pairs:")
                for original, duplicate in duplicates:
                    self.results_list.addItem(f"Original: {original}")
                    self.results_list.addItem(f"Duplicate: {duplicate}")
                    self.results_list.addItem("---")
            else:
                self.results_list.addItem("No duplicates found.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan directory: {e}")


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
