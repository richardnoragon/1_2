#!/usr/bin/env python3
"""
Empty Folders Tool for Richard's File Utilities

A streamlined empty folders utility with essential functionality.
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


class EmptyFoldersGUI(QMainWindow):
    """Main window for Empty Folders operations."""
    
    def __init__(self):
        super().__init__()
        self.empty_folders = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Empty Folders - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("Empty Folders Finder")
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
        
        # Add directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QVBoxLayout(dir_group)
        
        self.path_label = QLabel("No directory selected")
        dir_layout.addWidget(self.path_label)
        
        select_dir_button = QPushButton("Select Directory")
        select_dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(select_dir_button)
        
        layout.addWidget(dir_group)
        
        # Add scan controls
        scan_group = QGroupBox("Scan Controls")
        scan_layout = QHBoxLayout(scan_group)
        
        self.scan_button = QPushButton("Scan for Empty Folders")
        self.scan_button.clicked.connect(self.scan_folders)
        self.scan_button.setEnabled(False)
        scan_layout.addWidget(self.scan_button)
        
        layout.addWidget(scan_group)
        
        # Add results area
        results_group = QGroupBox("Empty Folders Found")
        results_layout = QVBoxLayout(results_group)
        
        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)
        
        # Add action buttons
        action_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        self.select_all_button.setEnabled(False)
        action_layout.addWidget(self.select_all_button)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        action_layout.addWidget(self.delete_button)
        
        results_layout.addLayout(action_layout)
        layout.addWidget(results_group)
        
        # Add status label
        self.status_label = QLabel("Ready - Select a directory to begin")
        self.status_label.setStyleSheet("padding: 10px; color: #666;")
        layout.addWidget(self.status_label)
        
    def select_directory(self):
        """Select directory to scan for empty folders."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Scan", ""
        )
        if directory:
            self.selected_directory = directory
            self.path_label.setText(f"Selected: {directory}")
            self.scan_button.setEnabled(True)
            self.status_label.setText("Directory selected - Click 'Scan' to find empty folders")
            
            # Clear previous results
            self.results_list.clear()
            self.empty_folders = []
            self.update_button_states()
            
    def scan_folders(self):
        """Scan for empty folders in the selected directory."""
        if not hasattr(self, 'selected_directory'):
            QMessageBox.warning(self, "Warning", "Please select a directory first.")
            return
            
        self.status_label.setText("Scanning for empty folders...")
        self.scan_button.setEnabled(False)
        self.results_list.clear()
        self.empty_folders = []
        
        try:
            # Find empty folders
            for root, dirs, files in os.walk(self.selected_directory):
                # Check if directory is empty (no files and no subdirectories)
                try:
                    if not files and not dirs:
                        self.empty_folders.append(root)
                except (OSError, PermissionError):
                    continue
                    
            # Display results
            if self.empty_folders:
                for folder in self.empty_folders:
                    # Show relative path for better readability
                    try:
                        rel_path = os.path.relpath(folder, self.selected_directory)
                        if rel_path == '.':
                            display_path = os.path.basename(self.selected_directory) + " (root)"
                        else:
                            display_path = rel_path
                    except ValueError:
                        display_path = folder
                        
                    self.results_list.addItem(display_path)
                    
                self.status_label.setText(f"Found {len(self.empty_folders)} empty folders")
            else:
                self.status_label.setText("No empty folders found")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error scanning directory: {str(e)}")
            self.status_label.setText("Error occurred during scan")
            
        finally:
            self.scan_button.setEnabled(True)
            self.update_button_states()
            
    def select_all(self):
        """Select all items in the results list."""
        self.results_list.selectAll()
        
    def delete_selected(self):
        """Delete selected empty folders."""
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select folders to delete.")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete {len(selected_items)} empty folders?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # Delete selected folders
        deleted_count = 0
        failed_count = 0
        
        for item in selected_items:
            item_index = self.results_list.row(item)
            if item_index < len(self.empty_folders):
                folder_path = self.empty_folders[item_index]
                try:
                    os.rmdir(folder_path)
                    deleted_count += 1
                    # Remove from list
                    self.results_list.takeItem(self.results_list.row(item))
                    self.empty_folders.remove(folder_path)
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to delete {folder_path}: {e}")
                    
        # Show results
        if failed_count == 0:
            self.status_label.setText(f"Successfully deleted {deleted_count} empty folders")
        else:
            self.status_label.setText(f"Deleted {deleted_count} folders, {failed_count} failed")
            
        self.update_button_states()
        
    def update_button_states(self):
        """Update button states based on current conditions."""
        has_results = self.results_list.count() > 0
        self.select_all_button.setEnabled(has_results)
        self.delete_button.setEnabled(has_results)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = EmptyFoldersGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()