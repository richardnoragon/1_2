"""
Enhanced File Touch Tool with Menu Integration

This enhanced version provides file timestamp modification capabilities with 
standardized menu integration following the File Finder template pattern.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to import StandardWindow, fall back to QMainWindow if not available
STANDARD_WINDOW_AVAILABLE = False
try:
    from src.gui.standard_window import StandardWindow
    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    print("StandardWindow not available, using fallback mode")
    from PyQt5.QtWidgets import QMainWindow as StandardWindow

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox,
        QDateTimeEdit, QGridLayout, QTextEdit, QSplitter,
        QTableWidget, QTableWidgetItem
    )
    from PyQt5.QtCore import QDateTime, Qt
    from PyQt5.QtGui import QFont

    class EnhancedFileTouchGUI(StandardWindow):
        """Enhanced File Touch GUI with menu integration."""
        
        def __init__(self):
            if STANDARD_WINDOW_AVAILABLE:
                super().__init__(
                    title="File Touch - Richard's File Utilities",
                    window_type="utility"
                )
            else:
                super().__init__()
                self.setWindowTitle("File Touch - Richard's File Utilities")
                self.setGeometry(100, 100, 900, 700)
            
            self.selected_files = []
            self.file_info = {}
            
            self.init_ui()
            if STANDARD_WINDOW_AVAILABLE:
                self._setup_menu_callbacks()
                # Ensure menu bar exists
                self.ensure_menu_bar()
        
        def _setup_menu_callbacks(self):
            """Setup tool-specific menu callbacks."""
            if hasattr(self, 'menu_manager'):
                # Register tool-specific callbacks
                self.menu_manager.register_callback('new_touch_session', self.clear_files)
                self.menu_manager.register_callback('help_file_touch', self.show_help)
                
        def show_help(self):
            """Show comprehensive help for File Touch."""
            help_text = """
            <h2>File Touch Tool - Comprehensive Guide</h2>
            
            <h3>🕒 Overview</h3>
            <p>The File Touch tool allows you to modify file timestamps, including 
            access time and modification time, for one or multiple files. This is useful 
            for file organization, backup synchronization, and forensic analysis.</p>
            
            <h3>🚀 Key Features</h3>
            <ul>
                <li><b>Single & Batch Processing</b>: Modify timestamps for individual files or multiple files</li>
                <li><b>Precise Control</b>: Set exact timestamps down to the second</li>
                <li><b>Current Time Setting</b>: Quickly set timestamps to current date/time</li>
                <li><b>Timestamp Reading</b>: Load and display current file timestamps</li>
                <li><b>File Information</b>: View comprehensive file details</li>
                <li><b>Error Handling</b>: Robust error handling for file operations</li>
            </ul>
            
            <h3>📊 Timestamp Types</h3>
            <ul>
                <li><b>Access Time (atime)</b>: Last time the file was accessed or read</li>
                <li><b>Modification Time (mtime)</b>: Last time the file content was modified</li>
                <li><b>Creation Time (ctime)</b>: File creation time (read-only on most systems)</li>
            </ul>
            
            <h3>🔧 Common Use Cases</h3>
            <ul>
                <li><b>File Organization</b>: Organize files by setting consistent timestamps</li>
                <li><b>Backup Synchronization</b>: Ensure proper backup ordering</li>
                <li><b>Forensic Analysis</b>: Analyze and modify file timeline information</li>
                <li><b>Build Systems</b>: Control file timestamps for build processes</li>
                <li><b>Archive Management</b>: Set proper timestamps for archived files</li>
            </ul>
            
            <h3>📋 Step-by-Step Instructions</h3>
            <ol>
                <li><b>File Selection</b>: 
                    <ul>
                        <li>Click "Select Files" to choose individual files</li>
                        <li>Click "Select Folder" to process all files in a directory</li>
                        <li>Enable "Include subdirectories" for recursive processing</li>
                    </ul>
                </li>
                <li><b>Timestamp Configuration</b>:
                    <ul>
                        <li>Use "Load Current" to read existing timestamps</li>
                        <li>Manually set desired timestamps using date/time controls</li>
                        <li>Click "Set to Current Time" for current date/time</li>
                    </ul>
                </li>
                <li><b>Apply Changes</b>:
                    <ul>
                        <li>Review selected files and timestamp settings</li>
                        <li>Click "Apply to Selected" to modify timestamps</li>
                        <li>Monitor progress and results in the status area</li>
                    </ul>
                </li>
            </ol>
            
            <h3>🛠️ Advanced Features</h3>
            <ul>
                <li><b>Batch Operations</b>: Apply same timestamp to multiple files</li>
                <li><b>Selective Processing</b>: Choose which files to process from selection</li>
                <li><b>Progress Monitoring</b>: Real-time progress updates for large operations</li>
                <li><b>Error Reporting</b>: Detailed error messages for failed operations</li>
                <li><b>File Information Display</b>: Comprehensive file details and statistics</li>
            </ul>
            
            <h3>⚠️ Important Considerations</h3>
            <ul>
                <li><b>Permissions</b>: Ensure you have write permissions to modify files</li>
                <li><b>Backup</b>: Consider backing up important files before modification</li>
                <li><b>System Impact</b>: Timestamp changes may affect file synchronization</li>
                <li><b>Forensics</b>: Be aware that timestamp modification leaves traces</li>
                <li><b>Applications</b>: Some applications may behave differently with modified timestamps</li>
            </ul>
            
            <h3>💡 Tips and Best Practices</h3>
            <ul>
                <li><b>Test First</b>: Test timestamp changes on copies before applying to originals</li>
                <li><b>Consistent Format</b>: Use consistent timestamp formats for organized workflows</li>
                <li><b>Document Changes</b>: Keep records of timestamp modifications for auditing</li>
                <li><b>Check Results</b>: Verify timestamp changes using file properties or other tools</li>
                <li><b>Batch Efficiently</b>: Group similar timestamp operations for efficiency</li>
            </ul>
            
            <h3>🔍 Technical Details</h3>
            <ul>
                <li><b>Precision</b>: Timestamps are precise to the second on most systems</li>
                <li><b>Time Zones</b>: All times are displayed in local system timezone</li>
                <li><b>Date Range</b>: Supports dates from 1970 to 2038 (Unix timestamp limits)</li>
                <li><b>File Types</b>: Works with all file types and sizes</li>
                <li><b>Cross-Platform</b>: Compatible with Windows, Linux, and macOS</li>
            </ul>
            
            <h3>🚨 Troubleshooting</h3>
            <ul>
                <li><b>Access Denied</b>: Run as administrator or check file permissions</li>
                <li><b>Invalid Date</b>: Ensure date/time values are within valid ranges</li>
                <li><b>File Locked</b>: Close applications that may have files open</li>
                <li><b>Network Files</b>: Local files process faster than network files</li>
                <li><b>Large Batches</b>: Process very large file sets in smaller chunks</li>
            </ul>
            
            <p><b>Note:</b> File Touch operations require appropriate file system permissions. 
            Some operations may require administrator privileges depending on file ownership and location.</p>
            """
            
            msg_box = QMessageBox()
            msg_box.setWindowTitle("File Touch Tool - Help")
            msg_box.setTextFormat(1)  # Rich text format
            msg_box.setText(help_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.resize(800, 600)
            msg_box.exec_()
            
        def show_preferences(self):
            """Show File Touch preferences."""
            QMessageBox.information(self, "File Touch Preferences", 
                                   "File Touch preferences:\n\n"
                                   "• Default timestamp format\n"
                                   "• Batch processing options\n"
                                   "• Error handling settings\n"
                                   "• Progress notification preferences\n"
                                   "• File type filters\n\n"
                                   "Advanced preferences coming soon!")
                                   
        def refresh_view(self):
            """Refresh the current file information."""
            if self.selected_files:
                self.load_current_timestamps()
                count = len(self.selected_files)
                self.status_label.setText(f"Refreshed - {count} files loaded")
            else:
                self.clear_files()
                
        def clear_files(self):
            """Clear all selected files and reset interface."""
            self.selected_files = []
            self.file_info = {}
            self.files_list.clear()
            self.files_label.setText("No files selected")
            self.load_button.setEnabled(False)
            self.apply_button.setEnabled(False)
            self.status_label.setText("Ready - Select files to begin")
        
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
            
            # Create main splitter
            main_splitter = QSplitter(Qt.Orientation.Horizontal)
            layout.addWidget(main_splitter)
            
            # Left panel - File selection and controls
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # File selection group
            file_group = QGroupBox("File Selection")
            file_layout = QVBoxLayout(file_group)
            
            # Selection buttons
            button_layout = QHBoxLayout()
            
            select_files_button = QPushButton("Select Files")
            select_files_button.clicked.connect(self.select_files)
            select_files_button.setStyleSheet("""
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
            button_layout.addWidget(select_files_button)
            
            select_folder_button = QPushButton("Select Folder")
            select_folder_button.clicked.connect(self.select_folder)
            select_folder_button.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            button_layout.addWidget(select_folder_button)
            
            file_layout.addLayout(button_layout)
            
            self.files_label = QLabel("No files selected")
            self.files_label.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
            file_layout.addWidget(self.files_label)
            
            left_layout.addWidget(file_group)
            
            # Timestamp controls
            timestamp_group = QGroupBox("Timestamp Settings")
            timestamp_layout = QGridLayout(timestamp_group)
            
            # Access time
            timestamp_layout.addWidget(QLabel("Access Time:"), 0, 0)
            self.access_time_edit = QDateTimeEdit()
            self.access_time_edit.setDateTime(QDateTime.currentDateTime())
            self.access_time_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
            timestamp_layout.addWidget(self.access_time_edit, 0, 1)
            
            # Modification time
            timestamp_layout.addWidget(QLabel("Modification Time:"), 1, 0)
            self.mod_time_edit = QDateTimeEdit()
            self.mod_time_edit.setDateTime(QDateTime.currentDateTime())
            self.mod_time_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
            timestamp_layout.addWidget(self.mod_time_edit, 1, 1)
            
            left_layout.addWidget(timestamp_group)
            
            # Control buttons
            control_layout = QHBoxLayout()
            
            self.load_button = QPushButton("Load Current")
            self.load_button.clicked.connect(self.load_current_timestamps)
            self.load_button.setEnabled(False)
            self.load_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            control_layout.addWidget(self.load_button)
            
            current_time_button = QPushButton("Set to Current Time")
            current_time_button.clicked.connect(self.set_current_time)
            control_layout.addWidget(current_time_button)
            
            left_layout.addLayout(control_layout)
            
            # Apply button
            self.apply_button = QPushButton("Apply to Selected Files")
            self.apply_button.clicked.connect(self.apply_timestamps)
            self.apply_button.setEnabled(False)
            self.apply_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            left_layout.addWidget(self.apply_button)
            
            # Status
            self.status_label = QLabel("Ready - Select files to begin")
            self.status_label.setStyleSheet("padding: 10px; color: #666; font-style: italic;")
            left_layout.addWidget(self.status_label)
            
            main_splitter.addWidget(left_panel)
            
            # Right panel - File list and information
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # File list
            files_group = QGroupBox("Selected Files")
            files_group_layout = QVBoxLayout(files_group)
            
            self.files_list = QTableWidget()
            self.files_list.setColumnCount(4)
            self.files_list.setHorizontalHeaderLabels(["Filename", "Size", "Access Time", "Modified Time"])
            self.files_list.setSelectionBehavior(QTableWidget.SelectRows)
            files_group_layout.addWidget(self.files_list)
            
            right_layout.addWidget(files_group)
            
            # Progress and status
            progress_group = QGroupBox("Operation Progress")
            progress_layout = QVBoxLayout(progress_group)
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            progress_layout.addWidget(self.progress_bar)
            
            self.operation_status = QTextEdit()
            self.operation_status.setMaximumHeight(100)
            self.operation_status.setReadOnly(True)
            progress_layout.addWidget(self.operation_status)
            
            right_layout.addWidget(progress_group)
            
            main_splitter.addWidget(right_panel)
            
            # Set splitter proportions
            main_splitter.setSizes([400, 500])
        
        def select_files(self):
            """Select individual files."""
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files to Touch", "", "All Files (*.*)"
            )
            if files:
                self.selected_files = files
                self.update_file_display()
                
        def select_folder(self):
            """Select all files from a folder."""
            folder = QFileDialog.getExistingDirectory(
                self, "Select Folder"
            )
            if folder:
                files = []
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        files.append(file_path)
                
                self.selected_files = files
                self.update_file_display()
                
        def update_file_display(self):
            """Update the file display with selected files."""
            count = len(self.selected_files)
            self.files_label.setText(f"{count} file(s) selected")
            
            # Update table
            self.files_list.setRowCount(count)
            
            for i, file_path in enumerate(self.selected_files):
                filename = os.path.basename(file_path)
                self.files_list.setItem(i, 0, QTableWidgetItem(filename))
                
                try:
                    stat = os.stat(file_path)
                    
                    # File size
                    size = stat.st_size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    
                    self.files_list.setItem(i, 1, QTableWidgetItem(size_str))
                    
                    # Timestamps
                    access_time = datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")
                    mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    
                    self.files_list.setItem(i, 2, QTableWidgetItem(access_time))
                    self.files_list.setItem(i, 3, QTableWidgetItem(mod_time))
                    
                    # Store file info
                    self.file_info[file_path] = {
                        'size': stat.st_size,
                        'atime': stat.st_atime,
                        'mtime': stat.st_mtime,
                        'ctime': stat.st_ctime
                    }
                    
                except Exception as e:
                    self.files_list.setItem(i, 1, QTableWidgetItem("Error"))
                    self.files_list.setItem(i, 2, QTableWidgetItem("Error"))
                    self.files_list.setItem(i, 3, QTableWidgetItem("Error"))
                    self.operation_status.append(f"Error reading {filename}: {e}")
            
            # Resize columns
            self.files_list.resizeColumnsToContents()
            
            # Enable buttons
            self.load_button.setEnabled(True)
            self.apply_button.setEnabled(True)
            self.status_label.setText(f"{count} files selected - Ready to modify timestamps")
            
        def load_current_timestamps(self):
            """Load current timestamps from the first selected file."""
            if not self.selected_files:
                QMessageBox.warning(self, "Warning", "Please select files first.")
                return
                
            try:
                # Use first file as reference
                first_file = self.selected_files[0]
                stat = os.stat(first_file)
                
                # Set access time
                access_time = QDateTime.fromSecsSinceEpoch(int(stat.st_atime))
                self.access_time_edit.setDateTime(access_time)
                
                # Set modification time
                mod_time = QDateTime.fromSecsSinceEpoch(int(stat.st_mtime))
                self.mod_time_edit.setDateTime(mod_time)
                
                self.operation_status.append(f"Loaded timestamps from: {os.path.basename(first_file)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading timestamps: {e}")
                self.operation_status.append(f"Error loading timestamps: {e}")
                
        def set_current_time(self):
            """Set both timestamps to current time."""
            current_time = QDateTime.currentDateTime()
            self.access_time_edit.setDateTime(current_time)
            self.mod_time_edit.setDateTime(current_time)
            self.operation_status.append("Timestamps set to current time")
            
        def apply_timestamps(self):
            """Apply timestamp changes to all selected files."""
            if not self.selected_files:
                QMessageBox.warning(self, "Warning", "Please select files first.")
                return
                
            # Confirmation dialog
            count = len(self.selected_files)
            access_time_str = self.access_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            mod_time_str = self.mod_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            
            reply = QMessageBox.question(
                self, "Confirm Timestamp Changes",
                f"Apply timestamps to {count} file(s)?\n\n"
                f"Access Time: {access_time_str}\n"
                f"Modification Time: {mod_time_str}\n\n"
                "This operation cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(count)
            self.progress_bar.setValue(0)
            
            # Get timestamps
            access_time = self.access_time_edit.dateTime().toSecsSinceEpoch()
            mod_time = self.mod_time_edit.dateTime().toSecsSinceEpoch()
            
            success_count = 0
            error_count = 0
            
            self.operation_status.append(f"\nStarting timestamp update for {count} files...")
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    # Apply timestamps to file
                    os.utime(file_path, (access_time, mod_time))
                    success_count += 1
                    self.operation_status.append(f"✓ Updated: {os.path.basename(file_path)}")
                    
                except Exception as e:
                    error_count += 1
                    self.operation_status.append(f"✗ Error: {os.path.basename(file_path)} - {e}")
                
                # Update progress
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()  # Keep UI responsive
            
            # Hide progress bar
            self.progress_bar.setVisible(False)
            
            # Update file display
            self.update_file_display()
            
            # Show completion message
            self.operation_status.append(f"\nOperation completed: {success_count} successful, {error_count} errors")
            
            if error_count == 0:
                QMessageBox.information(
                    self, "Success",
                    f"Successfully updated timestamps for all {success_count} files!"
                )
            else:
                QMessageBox.warning(
                    self, "Completed with Errors",
                    f"Updated {success_count} files successfully.\n"
                    f"{error_count} files had errors.\n"
                    "Check the status log for details."
                )


    def main():
        """Main function to run the Enhanced File Touch Tool."""
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show the main window
        window = EnhancedFileTouchGUI()
        window.show()
        
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing PyQt5 modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    
    def main():
        print("Enhanced File Touch Tool requires PyQt5 to be installed.")
        print("Please install PyQt5 using: pip install PyQt5")

    if __name__ == "__main__":
        main()
