"""
Empty Folders Cleaner - UI file-based implementation
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path modification
from gui.common.base_window import BaseWindow  # noqa: E402
from gui.common.dialogs import (  # noqa: E402
    get_existing_directory, show_error_dialog
)


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


class EmptyFoldersWindow(BaseWindow):
    """Empty folders cleaner with UI file-based implementation."""
    
    # UI file path
    _UI_FILE = "empty_folders.ui"
    
    def __init__(self) -> None:
        """Initialize the EmptyFoldersWindow.
        
        Sets up:
        - UI components from .ui file
        - Internal state variables
        - Signal connections
        - Initial UI state
        """
        # Calculate UI file path relative to this file
        ui_file = Path(__file__).parent / self._UI_FILE
        super().__init__(ui_file)
        
        self.current_path: Optional[str] = None
        self.empty_folders: List[str] = []
        self.logic: Optional[EmptyFolderLogic] = None
        self.thread: Optional[QThread] = None
        
        self._connect_signals()
        self._set_initial_state()
        
    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots."""
        # Connect buttons to their handlers
        if hasattr(self, 'browseButton'):
            self.browseButton.clicked.connect(self._select_directory)
        if hasattr(self, 'scanButton'):
            self.scanButton.clicked.connect(self._scan_folders)
        if hasattr(self, 'stopButton'):
            self.stopButton.clicked.connect(self._stop_operation)
        if hasattr(self, 'selectAllButton'):
            self.selectAllButton.clicked.connect(self._select_all_folders)
        if hasattr(self, 'unselectAllButton'):
            self.unselectAllButton.clicked.connect(self._unselect_all_folders)
        if hasattr(self, 'deleteButton'):
            self.deleteButton.clicked.connect(self._delete_selected)
            
    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements."""
        if hasattr(self, 'deleteButton'):
            self.deleteButton.setEnabled(False)
        if hasattr(self, 'stopButton'):
            self.stopButton.setEnabled(False)
        if hasattr(self, 'selectAllButton'):
            self.selectAllButton.setEnabled(False)
        if hasattr(self, 'unselectAllButton'):
            self.unselectAllButton.setEnabled(False)
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText("Ready - Select a directory to begin")
            
    def _select_directory(self) -> None:
        """Select directory to scan."""
        directory = get_existing_directory(self, "Select Directory to Scan")
        if directory:
            self.current_path = str(directory)  # Convert Path to string
            if hasattr(self, 'pathInput'):
                self.pathInput.setText(str(directory))
            if hasattr(self, 'statusLabel'):
                dir_name = os.path.basename(str(directory))
                self.statusLabel.setText(f"Selected: {dir_name}")
            
            # Clear previous results
            if hasattr(self, 'folderList'):
                self.folderList.clear()
            self.empty_folders = []
            self._update_button_states()
            
    def _scan_folders(self) -> None:
        """Scan for empty folders."""
        if not self.current_path:
            show_error_dialog("Please select a directory first", "Error", self)
            return
            
        # Clear previous results
        if hasattr(self, 'folderList'):
            self.folderList.clear()
        self.empty_folders = []
        
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText("Scanning for empty folders...")
        
        # Disable scan button, enable stop button
        if hasattr(self, 'scanButton'):
            self.scanButton.setEnabled(False)
        if hasattr(self, 'stopButton'):
            self.stopButton.setEnabled(True)
        
        # Create and start scan thread
        self.logic = EmptyFolderLogic()
        self.thread = QThread()
        self.logic.moveToThread(self.thread)
        
        # Connect signals
        self.logic.progress_updated.connect(self._update_status)
        self.logic.folders_found.connect(self._display_folders)
        self.logic.error_occurred.connect(self._handle_error)
        self.logic.finished.connect(self._scan_complete)
        self.thread.started.connect(
            lambda: self.logic.find_empty_folders(self.current_path))
        
        self.thread.start()
        
    def _stop_operation(self) -> None:
        """Stop the current operation."""
        if self.logic:
            self.logic.stop()
        if hasattr(self, 'stopButton'):
            self.stopButton.setEnabled(False)
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText("Stopping operation...")
            
    def _update_status(self, message: str) -> None:
        """Update status message."""
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText(message)
        
    def _display_folders(self, folders: List[str]) -> None:
        """Display found empty folders."""
        self.empty_folders = folders
        
        if hasattr(self, 'folderList'):
            self.folderList.clear()
            
            for folder in folders:
                # Show relative path if possible
                if self.current_path:
                    try:
                        display_path = os.path.relpath(
                            folder, self.current_path)
                    except ValueError:
                        display_path = folder
                else:
                    display_path = folder
                    
                item = QListWidgetItem(display_path)
                item.setData(Qt.UserRole, folder)  # Store full path
                self.folderList.addItem(item)
                
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText(f"Found {len(folders)} empty folders")
            
        self._update_button_states()
        
    def _select_all_folders(self) -> None:
        """Select all folders in the list."""
        if hasattr(self, 'folderList'):
            self.folderList.selectAll()
            
    def _unselect_all_folders(self) -> None:
        """Unselect all folders in the list."""
        if hasattr(self, 'folderList'):
            self.folderList.clearSelection()
            
    def _delete_selected(self) -> None:
        """Delete selected empty folders."""
        if not hasattr(self, 'folderList'):
            return
            
        selected_items = self.folderList.selectedItems()
        if not selected_items:
            show_error_dialog("Please select folders to delete", "Error", self)
            return
            
        folders_to_delete: List[str] = [
            item.data(Qt.UserRole) for item in selected_items
        ]
        
        # Confirm deletion
        reply: int = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete {len(folders_to_delete)} empty folders?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText("Deleting folders...")
        
        # Disable buttons during deletion
        if hasattr(self, 'deleteButton'):
            self.deleteButton.setEnabled(False)
        if hasattr(self, 'scanButton'):
            self.scanButton.setEnabled(False)
        if hasattr(self, 'stopButton'):
            self.stopButton.setEnabled(True)
        
        # Create and start delete thread
        self.logic = EmptyFolderLogic()
        self.thread = QThread()
        self.logic.moveToThread(self.thread)
        
        # Connect signals
        self.logic.progress_updated.connect(self._update_status)
        self.logic.deletion_update.connect(self._handle_deletion)
        self.logic.error_occurred.connect(self._handle_error)
        self.logic.finished.connect(self._delete_complete)
        self.thread.started.connect(
            lambda: self.logic.delete_folders(folders_to_delete))
        
        self.thread.start()
        
    def _handle_deletion(self, folder_path: str, success: bool) -> None:
        """Handle deletion results."""
        if not hasattr(self, 'folderList'):
            return
            
        if success:
            # Remove from list
            for i in range(self.folderList.count()):
                item = self.folderList.item(i)
                if item and item.data(Qt.UserRole) == folder_path:
                    self.folderList.takeItem(i)
                    break
                    
    def _scan_complete(self) -> None:
        """Handle scan completion."""
        self._operation_complete()
        
    def _delete_complete(self) -> None:
        """Handle delete completion."""
        self._operation_complete()
        if hasattr(self, 'statusLabel'):
            self.statusLabel.setText("Deletion complete")
        
    def _operation_complete(self) -> None:
        """Handle operation completion - common cleanup."""
        # Re-enable buttons
        if hasattr(self, 'scanButton'):
            self.scanButton.setEnabled(True)
        if hasattr(self, 'stopButton'):
            self.stopButton.setEnabled(False)
            
        self._update_button_states()
        
        # Clean up thread
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
        self.logic = None
        
    def _update_button_states(self) -> None:
        """Update button enabled states based on current state."""
        has_folders = (hasattr(self, 'folderList') and
                       self.folderList.count() > 0)
        
        if hasattr(self, 'deleteButton'):
            self.deleteButton.setEnabled(has_folders)
        if hasattr(self, 'selectAllButton'):
            self.selectAllButton.setEnabled(has_folders)
        if hasattr(self, 'unselectAllButton'):
            self.unselectAllButton.setEnabled(has_folders)
        
    def _handle_error(self, error_message: str) -> None:
        """Handle errors."""
        show_error_dialog(error_message, "Error", self)
        self._operation_complete()


def main() -> None:
    """Main function to run the empty folders cleaner."""
    app: QApplication = QApplication(sys.argv)
    app.setStyle('Fusion')
    window: EmptyFoldersWindow = EmptyFoldersWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()