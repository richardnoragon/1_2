#!/usr/bin/env python3
"""
Simplified File Finder Tool for Richard's File Utilities

A streamlined file search utility with basic functionality.
"""

import os
import sys
import fnmatch

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel,
        QCheckBox, QGroupBox, QFileDialog, QMessageBox,
        QApplication, QTextEdit
    )
    # PyQt5 core imports available if needed for future enhancements
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class FileFinderGUI(QMainWindow):
    """Simplified File Finder GUI with essential functionality."""
    
    def __init__(self):
        super().__init__()
        self.current_directory = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("File Finder - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header_label = QLabel("File Finder")
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
        
        # Create search controls
        search_group = QGroupBox("Search Parameters")
        search_layout = QGridLayout(search_group)
        
        # Directory selection
        search_layout.addWidget(QLabel("Search Directory:"), 0, 0)
        self.directory_edit = QLineEdit()
        self.directory_edit.setPlaceholderText(
            "Select a directory to search...")
        search_layout.addWidget(self.directory_edit, 0, 1)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        search_layout.addWidget(self.browse_button, 0, 2)
        
        # Search pattern
        search_layout.addWidget(QLabel("File Pattern:"), 1, 0)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("*.txt, *.pdf, image*, etc.")
        self.pattern_edit.setText("*.*")
        search_layout.addWidget(self.pattern_edit, 1, 1)
        
        # Search options
        self.recursive_check = QCheckBox("Search subdirectories")
        self.recursive_check.setChecked(True)
        search_layout.addWidget(self.recursive_check, 1, 2)
        
        # Search button
        self.search_button = QPushButton("Search Files")
        self.search_button.clicked.connect(self.start_search)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_layout.addWidget(self.search_button, 2, 0, 1, 3)
        
        layout.addWidget(search_group)
        
        # Create results area
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results info
        self.results_label = QLabel("No search performed yet")
        results_layout.addWidget(self.results_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_file)
        self.results_list.itemClicked.connect(self.show_file_info)
        results_layout.addWidget(self.results_list)
        
        # File info panel
        info_label = QLabel("File Information:")
        results_layout.addWidget(info_label)
        
        self.file_info_text = QTextEdit()
        self.file_info_text.setMaximumHeight(100)
        self.file_info_text.setReadOnly(True)
        results_layout.addWidget(self.file_info_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_selected_file)
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_file_folder)
        self.open_folder_button.setEnabled(False)
        button_layout.addWidget(self.open_folder_button)
        
        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)
        
        results_layout.addLayout(button_layout)
        layout.addWidget(results_group)
        
    def browse_directory(self):
        """Open directory selection dialog."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Search", self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.directory_edit.setText(directory)
            
    def start_search(self):
        """Start file search."""
        directory = self.directory_edit.text().strip()
        pattern = self.pattern_edit.text().strip()
        
        if not directory:
            QMessageBox.warning(self, "Warning", 
                                "Please select a directory to search.")
            return
            
        if not os.path.exists(directory):
            QMessageBox.warning(self, "Warning", 
                                "Selected directory does not exist.")
            return
            
        if not pattern:
            pattern = "*.*"
            
        # Clear previous results
        self.clear_results()
        self.results_label.setText("Searching...")
        
        # Perform search
        found_files = []
        try:
            if self.recursive_check.isChecked():
                for root, dirs, files in os.walk(directory):
                    for filename in files:
                        if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                            file_path = os.path.join(root, filename)
                            found_files.append(file_path)
            else:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if (os.path.isfile(file_path) and
                            fnmatch.fnmatch(filename.lower(),
                                          pattern.lower())):
                        found_files.append(file_path)
                        
            # Add results to list
            for file_path in sorted(found_files):
                item = QListWidgetItem(file_path)
                self.results_list.addItem(item)
                
            # Update results label
            count = len(found_files)
            if count == 0:
                self.results_label.setText("No files found matching the criteria")
            else:
                self.results_label.setText(f"Found {count} file(s)")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Search failed: {e}")
            self.results_label.setText("Search failed")
            
    def show_file_info(self, item):
        """Show information about the selected file."""
        file_path = item.text()
        
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            elif file_size < 1024 * 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                
            import time
            modified_time = time.ctime(stat.st_mtime)
            
            info_text = f"""File: {os.path.basename(file_path)}
Path: {file_path}
Size: {size_str}
Modified: {modified_time}"""
            
            self.file_info_text.setText(info_text)
            self.open_button.setEnabled(True)
            self.open_folder_button.setEnabled(True)
            
        except Exception as e:
            self.file_info_text.setText(f"Error reading file information: {e}")
            self.open_button.setEnabled(False)
            self.open_folder_button.setEnabled(False)
            
    def open_file(self, item):
        """Open the double-clicked file."""
        file_path = item.text()
        self.open_file_with_system(file_path)
        
    def open_selected_file(self):
        """Open the currently selected file."""
        current_item = self.results_list.currentItem()
        if current_item:
            file_path = current_item.text()
            self.open_file_with_system(file_path)
            
    def open_file_folder(self):
        """Open the folder containing the selected file."""
        current_item = self.results_list.currentItem()
        if current_item:
            file_path = current_item.text()
            folder_path = os.path.dirname(file_path)
            self.open_file_with_system(folder_path)
            
    def open_file_with_system(self, path):
        """Open file or folder with system default application."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")
            
    def clear_results(self):
        """Clear all search results."""
        self.results_list.clear()
        self.file_info_text.clear()
        self.results_label.setText("No search performed yet")
        self.open_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = FileFinderGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
