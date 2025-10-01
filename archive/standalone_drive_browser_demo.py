"""
Standalone Drive Selection File Browser Demo

Direct test of the enhanced file browser without dependencies on corrupted modules.
"""

import logging
import os
import platform
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
                             QLabel, QMainWindow, QMessageBox, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                             QWidget)


class DriveDetector:
    """Cross-platform drive detection utility."""
    
    @staticmethod
    def get_available_drives() -> List[Dict[str, str]]:
        """Get list of available drives on the system."""
        drives = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows drive detection
                for letter in string.ascii_uppercase:
                    drive_path = f"{letter}:\\"
                    if os.path.exists(drive_path):
                        try:
                            # Get free space info
                            free_space = ""
                            try:
                                import shutil
                                total, used, free = shutil.disk_usage(drive_path)
                                free_gb = free / (1024**3)
                                free_space = f" ({free_gb:.1f} GB free)"
                            except:
                                pass
                            
                            drives.append({
                                'label': f"{letter}: Drive{free_space}",
                                'path': drive_path
                            })
                        except:
                            continue
            else:
                # Unix-like systems (Linux, macOS)
                # Add root filesystem
                drives.append({'label': "/ (Root)", 'path': "/"})                
                # Add common mount points
                mount_points = ["/home", "/media", "/mnt", "/Volumes"]
                for mount_point in mount_points:
                    if os.path.exists(mount_point):
                        drives.append({
                            'label': f"{mount_point}",
                            'path': mount_point
                        })
                
                # Parse /proc/mounts for additional mount points
                try:
                    with open('/proc/mounts', 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                mount_point = parts[1]
                                if (mount_point.startswith('/media/') or 
                                    mount_point.startswith('/mnt/') or
                                    mount_point.startswith('/Volumes/')):
                                    if mount_point not in [d['path'] for d in drives]:
                                        drives.append({
                                            'label': os.path.basename(mount_point) or mount_point,
                                            'path': mount_point
                                        })
                except (OSError, IOError):
                    pass
        
        except Exception as e:
            print(f"Error detecting drives: {e}")
            # Fallback to home directory
            drives = [{'label': "Home", 'path': str(Path.home())}]
        
        # Always ensure home directory is available
        home_path = str(Path.home())
        if not any(d['path'] == home_path for d in drives):
            drives.insert(0, {'label': "Home", 'path': home_path})
        
        return drives


class StandaloneDriveFileBrowser(QWidget):
    """
    Standalone file browser with drive selection functionality.
    """
    
    # Signals
    pathChanged = pyqtSignal(str)
    fileActivated = pyqtSignal(str)
    directoryChanged = pyqtSignal(str)
    
    def __init__(self, initial_path=None, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger('StandaloneDriveFileBrowser')
        self.current_path = Path(initial_path) if initial_path else Path.home()
        
        self.setup_ui()
        self.navigate_to_path(self.current_path)
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Create navigation bar
        self.nav_bar = self.create_navigation_bar()
        layout.addWidget(self.nav_bar)
        
        # Create file list
        self.file_list = self.create_file_list()
        layout.addWidget(self.file_list, 1)
        
        # Status label
        self.status_label = QLabel("Drive selection file browser ready")
        self.status_label.setStyleSheet("font-size: 10px; color: #666; padding: 3px;")
        layout.addWidget(self.status_label)
    
    def create_navigation_bar(self) -> QWidget:
        """Create navigation bar with drive selection and path display."""
        nav_widget = QFrame()
        nav_widget.setStyleSheet("""
            background-color: #f0f0f0; 
            border: 1px solid #ccc; 
            padding: 3px;
        """)
        
        layout = QHBoxLayout(nav_widget)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # Drive selection dropdown
        drive_label = QLabel("Drive:")
        drive_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(drive_label)
        
        self.drive_combo = QComboBox()
        self.drive_combo.setMinimumWidth(140)
        self.drive_combo.setToolTip("Select drive to browse")
        
        # Populate available drives
        self.refresh_drives()
        
        self.drive_combo.currentTextChanged.connect(self.on_drive_changed)
        layout.addWidget(self.drive_combo)
        
        # Path display
        path_label = QLabel("Path:")
        path_label.setStyleSheet("font-weight: bold; margin-left: 10px;")
        layout.addWidget(path_label)
        
        self.path_display = QLabel(str(self.current_path))
        self.path_display.setStyleSheet("""
            font-family: monospace; 
            background-color: white; 
            padding: 4px; 
            border: 1px solid #999;
            border-radius: 2px;
        """)
        self.path_display.setMinimumWidth(250)
        layout.addWidget(self.path_display, 1)
        
        # Navigation buttons
        up_btn = QPushButton("↑")
        up_btn.setMaximumWidth(30)
        up_btn.setToolTip("Go up one directory")
        up_btn.clicked.connect(self.navigate_up)
        layout.addWidget(up_btn)
        
        refresh_btn = QPushButton("⟲")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.setToolTip("Refresh current directory")
        refresh_btn.clicked.connect(self.refresh_current_directory)
        layout.addWidget(refresh_btn)
        
        return nav_widget
    
    def create_file_list(self) -> QTreeWidget:
        """Create file list widget with enhanced display."""
        file_list = QTreeWidget()
        file_list.setHeaderLabels(["Name", "Size", "Type", "Modified"])
        file_list.setAlternatingRowColors(True)
        file_list.setSortingEnabled(True)
        
        # Configure column widths
        file_list.setColumnWidth(0, 220)  # Name
        file_list.setColumnWidth(1, 90)   # Size
        file_list.setColumnWidth(2, 90)   # Type
        file_list.setColumnWidth(3, 130)  # Modified
        
        # Connect double-click for navigation
        file_list.itemDoubleClicked.connect(self.on_file_item_activated)
        
        return file_list
    
    def refresh_drives(self):
        """Refresh the drive dropdown with available drives."""
        self.drive_combo.clear()
        drives = DriveDetector.get_available_drives()
        
        for drive in drives:
            self.drive_combo.addItem(drive['label'], drive['path'])
        
        # Set current drive based on current path
        current_drive = self.get_drive_from_path(self.current_path)
        index = self.drive_combo.findData(current_drive)
        if index >= 0:
            self.drive_combo.setCurrentIndex(index)
    
    def get_drive_from_path(self, path: Path) -> str:
        """Extract drive/mount point from a given path."""
        try:
            if platform.system() == "Windows":
                return str(path.anchor)  # Returns "C:\\" etc.
            else:
                # For Unix-like systems, find the mount point
                path_str = str(path.resolve())
                drives = DriveDetector.get_available_drives()
                
                # Find the longest matching mount point
                best_match = "/"
                for drive in drives:
                    if path_str.startswith(drive['path']) and len(drive['path']) > len(best_match):
                        best_match = drive['path']
                return best_match
        except Exception as e:
            print(f"Error getting drive from path: {e}")
            return str(Path.home())
    
    def on_drive_changed(self):
        """Handle drive selection change."""
        try:
            selected_path = self.drive_combo.currentData()
            if selected_path:
                new_path = Path(selected_path)
                self.navigate_to_path(new_path)
        except Exception as e:
            print(f"Error changing drive: {e}")
    
    def navigate_to_path(self, path: Path):
        """Navigate to specified path."""
        try:
            if path.exists():
                self.current_path = path
                
                # Update path display
                self.path_display.setText(str(path))
                
                # Update drive selection if needed
                current_drive = self.get_drive_from_path(path)
                index = self.drive_combo.findData(current_drive)
                if index >= 0 and index != self.drive_combo.currentIndex():
                    self.drive_combo.setCurrentIndex(index)
                
                # Update file list
                self.populate_file_list()
                
                # Emit signals
                self.pathChanged.emit(str(path))
                if path.is_dir():
                    self.directoryChanged.emit(str(path))
                
            else:
                QMessageBox.warning(self, "Navigation Error", f"Path does not exist: {path}")
        except Exception as e:
            print(f"Error navigating to path: {e}")
            QMessageBox.warning(self, "Navigation Error", f"Error navigating to {path}: {e}")
    
    def navigate_up(self):
        """Navigate up one directory level."""
        try:
            parent_path = self.current_path.parent
            
            if parent_path != self.current_path:  # Not at root
                self.navigate_to_path(parent_path)
            else:
                self.status_label.setText("Already at root directory")
        except Exception as e:
            print(f"Error navigating up: {e}")
    
    def refresh_current_directory(self):
        """Refresh the current directory."""
        try:
            self.navigate_to_path(self.current_path)
        except Exception as e:
            print(f"Error refreshing directory: {e}")
    
    def on_file_item_activated(self, item):
        """Handle file/directory activation in file list."""
        try:
            if item and item.parent() is None:  # Top-level item
                file_name = item.text(0)
                file_path = self.current_path / file_name
                
                if file_path.is_dir():
                    # Navigate into directory
                    self.navigate_to_path(file_path)
                elif file_path.is_file():
                    # Emit file activation signal
                    self.fileActivated.emit(str(file_path))
                    self.open_file_with_default_app(file_path)
        except Exception as e:
            print(f"Error activating file item: {e}")
    
    def open_file_with_default_app(self, file_path: Path):
        """Open file with default application."""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(str(file_path))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path)])
            
            self.status_label.setText(f"Opened: {file_path.name}")
                
        except Exception as e:
            print(f"Could not open file {file_path}: {e}")
            QMessageBox.warning(
                self,
                "File Open Error",
                f"Could not open file:\n{file_path}\n\nError: {e}"
            )
    
    def populate_file_list(self):
        """Populate file list with directory contents."""
        try:
            self.file_list.clear()
            
            if not self.current_path.exists():
                error_item = QTreeWidgetItem(["Path does not exist", "", "", ""])
                self.file_list.addTopLevelItem(error_item)
                return
            
            if not self.current_path.is_dir():
                error_item = QTreeWidgetItem(["Not a directory", "", "", ""])
                self.file_list.addTopLevelItem(error_item)
                return
            
            # Add items
            items = []
            try:
                for item in self.current_path.iterdir():
                    try:
                        # Get item statistics
                        stat = item.stat()
                        size_str = ""
                        if item.is_file():
                            size = stat.st_size
                            if size > 1024**3:  # GB
                                size_str = f"{size / (1024**3):.1f} GB"
                            elif size > 1024**2:  # MB
                                size_str = f"{size / (1024**2):.1f} MB"
                            elif size > 1024:  # KB
                                size_str = f"{size / 1024:.1f} KB"
                            else:
                                size_str = f"{size} B"
                        
                        type_str = "Directory" if item.is_dir() else "File"
                        modified_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                        
                        tree_item = QTreeWidgetItem([
                            item.name,
                            size_str,
                            type_str,
                            modified_str
                        ])
                        
                        # Set styling for directories
                        if item.is_dir():
                            tree_item.setBackground(0, Qt.GlobalColor.lightGray)
                        
                        items.append((item.is_dir(), item.name.lower(), tree_item))
                        
                    except (OSError, PermissionError) as e:
                        # Handle files we can't access
                        error_item = QTreeWidgetItem([
                            item.name,
                            "",
                            "Access Denied",
                            f"Error: {e}"
                        ])
                        items.append((False, item.name.lower(), error_item))
                
                # Sort items: directories first, then by name
                items.sort(key=lambda x: (not x[0], x[1]))
                
                # Add to tree widget
                for _, _, tree_item in items:
                    self.file_list.addTopLevelItem(tree_item)
                    
            except PermissionError:
                error_item = QTreeWidgetItem(["Permission denied", "", "", ""])
                self.file_list.addTopLevelItem(error_item)
            except Exception as e:
                error_item = QTreeWidgetItem([f"Error: {e}", "", "", ""])
                self.file_list.addTopLevelItem(error_item)
                
            # Update status
            file_count = len([item for item in items if not item[0]])  # Files only
            dir_count = len([item for item in items if item[0]])       # Directories only
            self.status_label.setText(f"{dir_count} directories, {file_count} files")
                
        except Exception as e:
            print(f"Error populating file list: {e}")
            error_item = QTreeWidgetItem([f"Failed to load: {e}", "", "", ""])
            self.file_list.clear()
            self.file_list.addTopLevelItem(error_item)


class DriveSelectionDemoWindow(QMainWindow):
    """Main demo window for drive selection file browser."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Drive Selection File Browser - Demo")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🗂️ Enhanced File Browser with Drive Selection")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: #ecf0f1;
            border: 2px solid #3498db;
            border-radius: 8px;
        """)
        layout.addWidget(title_label)
        
        # Demo info
        demo_info = QLabel("""
<b>🎯 Demonstration Features:</b><br><br>
<b>🎛️ Drive Detection:</b> Automatically detects all available system drives<br>
<b>💾 Windows Support:</b> Shows all drives (C:, D:, E:, etc.) with free space info<br>
<b>🐧 Unix Support:</b> Displays mount points (/home, /media, /mnt, /Volumes)<br>
<b>🗃️ Navigation Bar:</b> Drive dropdown → Path display → Navigation buttons<br>
<b>📋 File Details:</b> Name, size, type, and modification timestamp<br>
<b>🔄 Interactive:</b> Double-click to navigate/open, drag to resize columns<br><br>
<b>⚡ Quick Start:</b> Select any drive from dropdown to explore different storage devices!
        """)
        demo_info.setWordWrap(True)
        demo_info.setStyleSheet("""
            font-size: 13px;
            color: #34495e;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
        """)
        layout.addWidget(demo_info)
        
        # File browser
        self.file_browser = StandaloneDriveFileBrowser()
        
        # Connect signals
        self.file_browser.pathChanged.connect(self.on_path_changed)
        self.file_browser.fileActivated.connect(self.on_file_activated)
        self.file_browser.directoryChanged.connect(self.on_directory_changed)
        
        layout.addWidget(self.file_browser, 1)
        
        # Status display
        self.status_label = QLabel("🚀 Ready - Drive selection file browser loaded successfully!")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #27ae60;
            background-color: #d5f4e6;
            border: 1px solid #27ae60;
            padding: 8px 15px;
            border-radius: 4px;
        """)
        layout.addWidget(self.status_label)
    
    def on_path_changed(self, path):
        """Handle path change events."""
        self.status_label.setText(f"📁 Current location: {path}")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #2980b9;
            background-color: #ebf3fd;
            border: 1px solid #2980b9;
            padding: 8px 15px;
            border-radius: 4px;
        """)
    
    def on_file_activated(self, file_path):
        """Handle file activation events."""
        file_name = Path(file_path).name
        self.status_label.setText(f"🚀 Opened file: {file_name}")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #e67e22;
            background-color: #fef5e7;
            border: 1px solid #e67e22;
            padding: 8px 15px;
            border-radius: 4px;
        """)
    
    def on_directory_changed(self, directory):
        """Handle directory change events."""
        self.status_label.setText(f"🗂️ Browsing directory: {directory}")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #8e44ad;
            background-color: #f4ecf7;
            border: 1px solid #8e44ad;
            padding: 8px 15px;
            border-radius: 4px;
        """)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Drive Selection File Browser Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("RFU")
    
    # Create and show main window
    window = DriveSelectionDemoWindow()
    window.show()
    
    print("🎉 Drive Selection File Browser Demo started successfully!")
    print("📋 Features:")
    print("   • Cross-platform drive detection")
    print("   • Interactive drive selection dropdown")
    print("   • Real-time path display")
    print("   • File and directory navigation")
    print("   • Detailed file information")
    print("🚀 Use the dropdown to select different drives and explore!")
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()