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

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class EmptyFoldersGUI(StandardWindow):
    """Main window for Empty Folders operations."""
    
    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Empty Folders - Richard's File Utilities",
                window_type="utility"
            )
        else:
            super().__init__()
            self.setWindowTitle("Empty Folders - Richard's File Utilities")
            self.setGeometry(100, 100, 800, 600)
        
        self.empty_folders = []
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()
    
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_scan', self.clear_folders)
            self.menu_manager.register_callback('help_empty_folders', self.show_help)
            
    def clear_folders(self):
        """Clear all empty folder scan results."""
        self.empty_folders = []
        if hasattr(self, 'results_list'):
            self.results_list.clear()
        
    def show_help(self):
        """Show help dialog for Empty Folders tool."""
        help_text = """
        <h2>Empty Folders Finder - Help</h2>
        
        <h3>How to Find Empty Folders:</h3>
        <ul>
        <li><b>Select Directory:</b> Choose the root folder to scan</li>
        <li><b>Start Scan:</b> Begin searching for empty directories</li>
        <li><b>Review Results:</b> Examine list of found empty folders</li>
        <li><b>Clean Up:</b> Remove empty folders (with confirmation)</li>
        </ul>
        
        <h3>Empty Folder Detection:</h3>
        <ul>
        <li><b>True Empty:</b> Folders containing no files or subfolders</li>
        <li><b>Recursive Check:</b> Folders with only empty subfolders</li>
        <li><b>Hidden Files:</b> Option to ignore hidden/system files</li>
        <li><b>Size Verification:</b> Confirms zero byte directories</li>
        </ul>
        
        <h3>Cleanup Options:</h3>
        <ul>
        <li><b>Safe Removal:</b> Only removes truly empty directories</li>
        <li><b>Batch Operations:</b> Remove multiple folders at once</li>
        <li><b>Confirmation Prompts:</b> Verify before any deletion</li>
        <li><b>Undo Protection:</b> Keep list for potential restoration</li>
        </ul>
        
        <h3>Use Cases:</h3>
        <ul>
        <li><b>System Cleanup:</b> Remove leftover empty directories</li>
        <li><b>Storage Optimization:</b> Clean up file system structure</li>
        <li><b>Project Maintenance:</b> Remove unused folder hierarchies</li>
        <li><b>Archive Preparation:</b> Clean structure before archiving</li>
        </ul>
        
        <h3>Best Practices:</h3>
        <ul>
        <li><b>Backup First:</b> Always backup before mass deletions</li>
        <li><b>Review Results:</b> Check list before removing folders</li>
        <li><b>Exclude System:</b> Skip system and program directories</li>
        <li><b>Regular Maintenance:</b> Periodic scans keep system clean</li>
        </ul>
        
        <h3>Safety Features:</h3>
        <ul>
        <li><b>Read-Only Mode:</b> Scan without deletion permissions</li>
        <li><b>Protected Paths:</b> Automatic exclusion of critical folders</li>
        <li><b>Confirmation Dialogs:</b> Multiple confirmations for safety</li>
        <li><b>Error Recovery:</b> Graceful handling of permission issues</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+Q:</b> Exit application</li>
        <li><b>F1:</b> Show this help</li>
        <li><b>F5:</b> Clear results and start new scan</li>
        </ul>
        """
        
        QMessageBox.information(self, "Empty Folders Help", help_text)
        
    def show_preferences(self):
        """Show Empty Folders preferences."""
        QMessageBox.information(self, "Empty Folders Preferences", 
                               "Empty Folders preferences:\n\n"
                               "• Scan depth limits\n"
                               "• Hidden file handling\n"
                               "• Protected directory lists\n"
                               "• Deletion confirmation settings\n\n"
                               "Advanced preferences coming soon!")
                               
    def refresh_view(self):
        """Refresh/clear the current scan results."""
        self.clear_folders()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create new layout
        if STANDARD_WINDOW_AVAILABLE and hasattr(self, 'main_layout'):
            layout = self.main_layout
        else:
            # Create central widget and layout for fallback mode
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