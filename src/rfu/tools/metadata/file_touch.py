#!/usr/bin/env python3
"""
File Touch Tool for Richard's File Utilities

A streamlined file touch utility with essential functionality.
"""

import os
import sys
import json
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog, QGroupBox,
        QDateTimeEdit
    )
    from PyQt5.QtCore import QDateTime
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.rfu.gui.standard_window import StandardWindow
except ImportError:
    try:
        from rfu.gui.standard_window import StandardWindow
    except ImportError:
        # Fallback for standalone execution
        from PyQt5.QtWidgets import QMainWindow, QStatusBar
        
        class StandardWindow(QMainWindow):
            def __init__(self, title="", window_type="utility"):
                super().__init__()
                self.setWindowTitle(title)
                self.central_widget = QWidget()
                self.setCentralWidget(self.central_widget)
                self.main_layout = QVBoxLayout(self.central_widget)
                self.setStatusBar(QStatusBar())
                
            def show_status_message(self, message, timeout=3000):
                status_bar = self.statusBar()
                if status_bar:
                    status_bar.showMessage(message, timeout)
                    
            def show_error_dialog(self, title, message):
                QMessageBox.critical(self, title, message)
                
            def show_info_dialog(self, title, message):
                QMessageBox.information(self, title, message)
                
            def show_warning_dialog(self, title, message):
                QMessageBox.warning(self, title, message)
                
            def get_file_path(self, title="Select File",
                             file_filter="All Files (*)"):
                return QFileDialog.getOpenFileName(
                    self, title, "", file_filter)[0]
                
            def get_save_file_path(self, title="Save File",
                                 file_filter="All Files (*)"):
                return QFileDialog.getSaveFileName(
                    self, title, "", file_filter)[0]
                    
            def get_directory_path(self, title="Select Directory"):
                return QFileDialog.getExistingDirectory(self, title)
                
            def create_header(self, text):
                """Create a standard header label."""
                header = QLabel(text)
                header.setStyleSheet("""
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
                return header


class FileTouchGUI(StandardWindow):
    """Main window for File Touch operations."""
    
    def __init__(self):
        super().__init__(
            title="File Touch - Richard's File Utilities",
            window_type="utility"
        )
        self.current_file = None
        self.file_list = []
        self.init_ui()
        self._setup_menu_callbacks()
        
    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # File menu callbacks
            self.menu_manager.register_callback(
                'new_touch_session', self.new_touch_session)
            self.menu_manager.register_callback(
                'save_file', self.save_touch_settings)
            self.menu_manager.register_callback(
                'open_file', self.load_touch_settings)
            self.menu_manager.register_callback(
                'export_data', self.export_file_list)
            self.menu_manager.register_callback(
                'import_data', self.import_file_list)
            self.menu_manager.register_callback(
                'print_document', self.print_touch_report)
            
            # Edit menu callbacks
            self.menu_manager.register_callback('cut', self.cut_text)
            self.menu_manager.register_callback('copy', self.copy_text)
            self.menu_manager.register_callback('paste', self.paste_text)
            self.menu_manager.register_callback(
                'select_all', self.select_all_files)
            self.menu_manager.register_callback('find', self.find_files)
            
            # View menu callbacks
            self.menu_manager.register_callback('zoom_in', self.zoom_in)
            self.menu_manager.register_callback('zoom_out', self.zoom_out)
            self.menu_manager.register_callback('zoom_reset', self.zoom_reset)
            
            # Tools menu callbacks
            self.menu_manager.register_callback(
                'show_options', self.show_touch_options)
            self.menu_manager.register_callback(
                'timestamp_presets', self.show_timestamp_presets)
            self.menu_manager.register_callback(
                'batch_operations', self.show_batch_operations)
            
            # Help menu callbacks
            self.menu_manager.register_callback('help_touch', self.show_help)
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setGeometry(100, 100, 800, 600)
        
        # Use the main layout from StandardWindow
        layout = self.main_layout
        
        # Add header using StandardWindow method
        header_label = self.create_header("File Touch - Modify File Timestamps")
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
            
    def new_touch_session(self):
        """Start a new file touch session."""
        self.current_file = None
        self.file_list = []
        self.file_label.setText("No file selected")
        self.refresh_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.set_current_time()
        self.show_status_message("New touch session started")
        
    def save_touch_settings(self):
        """Save current touch settings to file."""
        settings = {
            'current_file': self.current_file,
            'file_list': self.file_list,
            'access_time': self.access_time_edit.dateTime().toString(),
            'mod_time': self.mod_time_edit.dateTime().toString(),
            'timestamp': datetime.now().isoformat()
        }
        
        file_path = self.get_save_file_path(
            "Save Touch Settings",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                self.show_info_dialog(
                    "Settings Saved",
                    f"Touch settings saved to {file_path}"
                )
            except Exception as e:
                self.show_error_dialog(
                    "Save Error",
                    f"Failed to save settings: {str(e)}"
                )
                
    def load_touch_settings(self):
        """Load touch settings from file."""
        file_path = self.get_file_path(
            "Load Touch Settings",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                
                self.current_file = settings.get('current_file')
                self.file_list = settings.get('file_list', [])
                
                if self.current_file:
                    self.file_label.setText(
                        f"Selected: {os.path.basename(self.current_file)}")
                    self.refresh_button.setEnabled(True)
                    self.apply_button.setEnabled(True)
                
                # Restore timestamps
                access_time_str = settings.get('access_time')
                mod_time_str = settings.get('mod_time')
                
                if access_time_str:
                    access_time = QDateTime.fromString(access_time_str)
                    self.access_time_edit.setDateTime(access_time)
                    
                if mod_time_str:
                    mod_time = QDateTime.fromString(mod_time_str)
                    self.mod_time_edit.setDateTime(mod_time)
                
                self.show_info_dialog(
                    "Settings Loaded",
                    f"Touch settings loaded from {file_path}"
                )
            except Exception as e:
                self.show_error_dialog(
                    "Load Error",
                    f"Failed to load settings: {str(e)}"
                )
                
    def export_file_list(self):
        """Export list of files to process."""
        self.show_info_dialog(
            "Export File List",
            "File list export functionality will be implemented."
        )
        
    def import_file_list(self):
        """Import list of files to process."""
        self.show_info_dialog(
            "Import File List",
            "File list import functionality will be implemented."
        )
        
    def print_touch_report(self):
        """Print file touch operation report."""
        self.show_info_dialog(
            "Print Report",
            "Touch operation report printing will be implemented."
        )
        
    def cut_text(self):
        """Cut text from focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'cut'):
            focused.cut()
            
    def copy_text(self):
        """Copy text from focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'copy'):
            focused.copy()
            
    def paste_text(self):
        """Paste text to focused widget."""
        focused = QApplication.focusWidget()
        if focused and hasattr(focused, 'paste'):
            focused.paste()
            
    def select_all_files(self):
        """Select all files in the current session."""
        self.show_info_dialog(
            "Select All Files",
            "Select all functionality will be implemented."
        )
        
    def find_files(self):
        """Find files by name or path."""
        self.show_info_dialog(
            "Find Files",
            "File search functionality will be implemented."
        )
        
    def zoom_in(self):
        """Increase interface zoom level."""
        self.show_status_message("Zoom in functionality not applicable")
        
    def zoom_out(self):
        """Decrease interface zoom level."""
        self.show_status_message("Zoom out functionality not applicable")
        
    def zoom_reset(self):
        """Reset interface zoom level."""
        self.show_status_message("Zoom reset functionality not applicable")
        
    def show_touch_options(self):
        """Show file touch options dialog."""
        self.show_info_dialog(
            "File Touch Options",
            "File touch options:\n\n"
            "• Timestamp precision settings\n"
            "• Batch operation preferences\n"
            "• File type filters\n"
            "• Backup options\n\n"
            "Advanced options coming soon!"
        )
        
    def show_timestamp_presets(self):
        """Show timestamp preset options."""
        self.show_info_dialog(
            "Timestamp Presets",
            "Common timestamp presets:\n\n"
            "• Current time\n"
            "• Specific date/time\n"
            "• Copy from another file\n"
            "• Relative adjustments\n\n"
            "Preset functionality will be implemented."
        )
        
    def show_batch_operations(self):
        """Show batch operations dialog."""
        self.show_info_dialog(
            "Batch Operations",
            "Batch file touch operations will be implemented."
        )
        
    def show_help(self):
        """Show help dialog for File Touch tool."""
        help_text = """
        <h2>File Touch - Help</h2>
        
        <h3>Overview:</h3>
        <p>The File Touch tool allows you to modify file timestamps
        (access time and modification time) for individual files or
        batches of files.</p>
        
        <h3>Features:</h3>
        <ul>
        <li><b>Single File Mode:</b> Modify timestamps for one file</li>
        <li><b>Batch Mode:</b> Process multiple files at once</li>
        <li><b>Timestamp Presets:</b> Common time settings</li>
        <li><b>Current Time:</b> Set timestamps to now</li>
        <li><b>Custom Time:</b> Set specific date and time</li>
        </ul>
        
        <h3>Usage:</h3>
        <ol>
        <li>Click "Select File" to choose a file</li>
        <li>Use "Refresh from File" to load current timestamps</li>
        <li>Adjust the access and modification times</li>
        <li>Click "Apply Changes" to update the file</li>
        </ol>
        
        <h3>Timestamp Types:</h3>
        <ul>
        <li><b>Access Time:</b> When the file was last accessed</li>
        <li><b>Modification Time:</b> When the file was last modified</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
        <li><b>Ctrl+O:</b> Select file</li>
        <li><b>Ctrl+S:</b> Save settings</li>
        <li><b>F5:</b> Refresh timestamps</li>
        <li><b>F1:</b> Show this help</li>
        </ul>
        
        <h3>Tips:</h3>
        <ul>
        <li>Use "Set to Current Time" for quick updates</li>
        <li>Save settings to reuse timestamp configurations</li>
        <li>Be careful when modifying system files</li>
        </ul>
        """
        
        QMessageBox.information(self, "File Touch Help", help_text)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = FileTouchGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()