"""
Empty Folders Cleaner - Standardized GUI utility
"""

import os
import sys
import time
import fnmatch
from typing import List, Optional
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

from gui.standard_window import StandardWindow
from gui.themes import ThemeManager


class EmptyFolderLogic(QObject):
    """Handles the logic for finding and deleting empty folders."""
    
    progress_updated = pyqtSignal(str)
    folders_found = pyqtSignal(list)
    deletion_update = pyqtSignal(str, bool)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._is_running = False
        self._base_path = None

    def stop(self) -> None:
        """Stop the operation."""
        self._is_running = False
        self.progress_updated.emit("Stopping operation...")

    def find_empty_folders(self, start_path: str) -> None:
        """Find empty folders recursively."""
        self._is_running = True
        self._base_path = start_path
        empty_folders = []
        
        try:
            for root, dirs, files in os.walk(start_path):
                if not self._is_running:
                    break
                    
                # Check if directory is empty
                try:
                    dir_contents = os.listdir(root)
                    if not dir_contents:  # Empty directory
                        empty_folders.append(root)
                        folder_name = os.path.basename(root)
                        self.progress_updated.emit(f"Found: {folder_name}")
                except (OSError, PermissionError):
                    continue
                    
            if self._is_running:
                self.folders_found.emit(empty_folders)
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit(True)

    def delete_folders(self, folders: List[str]) -> None:
        """Delete the specified empty folders."""
        self._is_running = True
        
        for folder in folders:
            if not self._is_running:
                break
                
            try:
                os.rmdir(folder)
                self.deletion_update.emit(folder, True)
                folder_name = os.path.basename(folder)
                self.progress_updated.emit(f"Deleted: {folder_name}")
            except Exception as e:
                self.deletion_update.emit(folder, False)
                msg = f"Failed to delete {folder}: {str(e)}"
                self.error_occurred.emit(msg)
                
        self.finished.emit(False)


class EmptyFoldersGUI(StandardWindow):
    """Empty folders cleaner with standardized styling."""
    
    def __init__(self) -> None:
        super().__init__("Empty Folders Cleaner")
        self.current_path: Optional[str] = None
        self.empty_folders: List[str] = []
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Setup the user interface with standardized styling."""
        # Create header
        header = self.create_header("Empty Folders Cleaner")
        self.main_layout.addWidget(header)
        
        # Create directory selection group
        dir_group = self.create_group_box("Directory Selection")
        dir_layout = QVBoxLayout()
        
        # Path display
        self.path_label = QLabel("No directory selected")
        ThemeManager.style_label(self.path_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        select_btn = self.create_button("Select Directory",
                                        self.select_directory)
        scan_btn = self.create_button("Scan for Empty Folders",
                                      self.scan_folders)
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(scan_btn)
        
        dir_layout.addWidget(self.path_label)
        dir_layout.addLayout(button_layout)
        dir_group.setLayout(dir_layout)
        self.main_layout.addWidget(dir_group)
        
        # Create results group
        results_group = self.create_group_box("Empty Folders Found")
        results_layout = QVBoxLayout()
        
        # List widget for folders
        self.folders_list = QListWidget()
        self.folders_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ECF0F1;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)
        
        # Buttons
        btn_layout = QHBoxLayout()
        select_all_btn = self.create_button("Select All",
                                            self.select_all_folders,
                                            primary=False)
        delete_btn = self.create_button("Delete Selected",
                                        self.delete_selected)
        
        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(delete_btn)
        
        results_layout.addWidget(self.folders_list)
        results_layout.addLayout(btn_layout)
        results_group.setLayout(results_layout)
        self.main_layout.addWidget(results_group)
        
        # Create progress group
        progress_group = self.create_group_box("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = self.create_progress_bar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("Ready")
        ThemeManager.style_label(self.status_label)
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)
        
    def select_directory(self) -> None:
        """Select directory to scan."""
        directory: Optional[str] = self.get_directory_path(
            "Select Directory to Scan")
        if directory:
            self.current_path = directory
            self.path_label.setText(os.path.basename(directory))
            self.show_status_message(f"Selected: {directory}")
            
    def scan_folders(self) -> None:
        """Scan for empty folders."""
        if not self.current_path:
            self.show_error_dialog("Error", "Please select a directory first")
            return
            
        self.folders_list.clear()
        self.empty_folders = []
        
        self.progress_bar.setVisible(True)
        self.status_label.setText("Scanning for empty folders...")
        
        # Create and start scan thread
        self.logic = EmptyFolderLogic()
        self.thread = QThread()
        self.logic.moveToThread(self.thread)
        
        # Connect signals
        self.logic.progress_updated.connect(self.update_status)
        self.logic.folders_found.connect(self.display_folders)
        self.logic.error_occurred.connect(self.handle_error)
        self.logic.finished.connect(self.scan_complete)
        self.thread.started.connect(
            lambda: self.logic.find_empty_folders(self.current_path))
        
        self.thread.start()
        
    def update_status(self, message: str) -> None:
        """Update status message."""
        self.status_label.setText(message)
        self.show_status_message(message)
        
    def display_folders(self, folders: List[str]) -> None:
        """Display found empty folders."""
        self.empty_folders = folders
        self.folders_list.clear()
        
        for folder in folders:
            item = QListWidgetItem(os.path.relpath(folder, self.current_path))
            item.setData(Qt.UserRole, folder)
            self.folders_list.addItem(item)
            
        self.status_label.setText(f"Found {len(folders)} empty folders")
        
    def select_all_folders(self) -> None:
        """Select all folders in the list."""
        for i in range(self.folders_list.count()):
            self.folders_list.item(i).setSelected(True)
            
    def delete_selected(self) -> None:
        """Delete selected empty folders."""
        selected_items = self.folders_list.selectedItems()
        if not selected_items:
            self.show_error_dialog("Error", "Please select folders to delete")
            return
            
        folders_to_delete: List[str] = [item.data(Qt.UserRole)
                                        for item in selected_items]
        
        # Confirm deletion
        reply: int = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete {len(folders_to_delete)} empty folders?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        self.progress_bar.setVisible(True)
        self.status_label.setText("Deleting folders...")
        
        # Create and start delete thread
        self.logic = EmptyFolderLogic()
        self.thread = QThread()
        self.logic.moveToThread(self.thread)
        
        # Connect signals
        self.logic.progress_updated.connect(self.update_status)
        self.logic.deletion_update.connect(self.handle_deletion)
        self.logic.error_occurred.connect(self.handle_error)
        self.logic.finished.connect(self.delete_complete)
        self.thread.started.connect(
            lambda: self.logic.delete_folders(folders_to_delete))
        
        self.thread.start()
        
    def handle_deletion(self, folder_path: str, success: bool) -> None:
        """Handle deletion results."""
        if success:
            # Remove from list
            for i in range(self.folders_list.count()):
                item = self.folders_list.item(i)
                if item.data(Qt.UserRole) == folder_path:
                    self.folders_list.takeItem(i)
                    break
                    
    def scan_complete(self) -> None:
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        
    def delete_complete(self) -> None:
        """Handle delete completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Deletion complete")
        
    def handle_error(self, error_message: str) -> None:
        """Handle errors."""
        self.progress_bar.setVisible(False)
        self.show_error_dialog("Error", error_message)


def main() -> None:
    """Main function to run the empty folders cleaner."""
    app: QApplication = QApplication(sys.argv)
    window: EmptyFoldersGUI = EmptyFoldersGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()