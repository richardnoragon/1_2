from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import show_error_dialog, show_info_dialog, get_existing_directory
import sys
import os

from core.error_handler import error_handler



class EmptyFolderLogic(QObject):
    """Handles the logic for finding and deleting empty folders."""
    progress_updated = pyqtSignal(str)  # Status message updates
    folders_found = pyqtSignal(list)    # List of found empty folders
    deletion_update = pyqtSignal(str, bool)  # Path and success status
    error_occurred = pyqtSignal(str)    # Error messages
    finished = pyqtSignal(bool)         # True=find operation, False=delete operation

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._base_path = None

    def stop(self):
        self.progress_updated.emit("Stopping operation...")
        self._is_running = False

    def find_empty_folders(self, start_path):
        """Starts the process of finding empty folders recursively."""
        if not os.path.isdir(start_path):
            msg = f"Error: Path is not a valid directory: {start_path}"
            self.error_occurred.emit(msg)
            self.finished.emit(True)
            return

        self._is_running = True
        self._base_path = start_path
        empty_folders = []
        folders_to_check = []

        self.progress_updated.emit(f"Scanning directory: {start_path}...")

        try:
            # First pass: Collect directory paths using topdown=True
            for root, dirs, files in os.walk(start_path, topdown=True):
                if not self._is_running:
                    break

                # Add full paths of directories
                for d in dirs:
                    if not self._is_running:
                        break
                    dir_path = os.path.join(root, d)
                    folders_to_check.append(dir_path)

                    if len(folders_to_check) % 100 == 0:
                        msg = (f"Scanning... Found "
                              f"{len(folders_to_check)} potential folders.")
                        self.progress_updated.emit(msg)

                if not self._is_running:
                    break

                if root == start_path:
                    folders_to_check.append(root)

            if not self._is_running:
                self.progress_updated.emit("Scan cancelled.")
                self.finished.emit(True)
                return

            # Second pass: Check collected directories
            checked_count = 0
            total_to_check = len(folders_to_check)
            folders_to_check.sort(key=len, reverse=True)

            for folder_path in folders_to_check:
                if not self._is_running:
                    break
                checked_count += 1
                if checked_count % 50 == 0:
                    basename = os.path.basename(folder_path)
                    msg = (f"Checking folder {checked_count}/{total_to_check}: "
                          f"{basename}")
                    self.progress_updated.emit(msg)
                try:
                    # Check if directory exists and is empty
                    if (os.path.isdir(folder_path) and
                        not os.listdir(folder_path)):
                        empty_folders.append(folder_path)
                except PermissionError:
                    msg = f"Skipping (permission denied): {folder_path}"
                    self.progress_updated.emit(msg)
                except FileNotFoundError:
                    msg = f"Skipping (not found): {folder_path}"
                    self.progress_updated.emit(msg)
                except Exception as e:
                    basename = os.path.basename(folder_path)
                    msg = f"Skipping (error checking {basename}): {e}"
                    self.progress_updated.emit(msg)

            if self._is_running:
                self.folders_found.emit(empty_folders)
                msg = (f"Scan complete. Found "
                      f"{len(empty_folders)} empty folders.")
                self.progress_updated.emit(msg)

        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(f"An error occurred during scan: {e}")
        finally:
            if self._is_running:
                self._is_running = False
                self.finished.emit(True)

    def delete_folders(self, folder_paths):
        """Attempts to delete the provided list of folder paths."""
        if not folder_paths:
            self.progress_updated.emit("No folders selected for deletion.")
            self.finished.emit(False)
            return

        self._is_running = True
        folders_to_delete = sorted(folder_paths, key=len, reverse=True)
        deleted_count = 0
        failed_count = 0

        msg = f"Starting deletion of {len(folders_to_delete)} folders..."
        self.progress_updated.emit(msg)

        for folder_path in folders_to_delete:
            if not self._is_running:
                break
            try:
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    os.rmdir(folder_path)
                    self.deletion_update.emit(folder_path, True)
                    deleted_count += 1
                else:
                    msg = f"{folder_path} (Not found or not a directory)"
                    self.deletion_update.emit(msg, False)
                    failed_count += 1

            except OSError as e:
                self.deletion_update.emit(
                    f"{folder_path} ({e.strerror})", False
                )
                failed_count += 1
            except Exception as e:
                msg = f"{folder_path} (Unexpected error: {e})"
                self.deletion_update.emit(msg, False)
                failed_count += 1

        if not self._is_running:
            self.progress_updated.emit("Deletion cancelled.")
        else:
            msg = (f"Deletion complete. Deleted: {deleted_count}, "
                  f"Failed: {failed_count}")
            self.progress_updated.emit(msg)

        self._is_running = False
        self.finished.emit(False)


class EmptyFoldersWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        ui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty_folders.ui")
        uic.loadUi(ui_file, self)
        
        # Initialize the logic handler
        self.logic = EmptyFolderLogic()
        
        # Connect signals from logic to UI
        self.logic.progress_updated.connect(self.update_status)
        self.logic.folders_found.connect(self.display_folders)
        self.logic.deletion_update.connect(self.handle_deletion_update)
        self.logic.error_occurred.connect(self.show_error)
        self.logic.finished.connect(self.handle_operation_finished)
        
        # Connect UI elements to slots
        self.browseButton.clicked.connect(self.browse_directory)
        self.scanButton.clicked.connect(self.start_scan)
        self.stopButton.clicked.connect(self.logic.stop)
        self.selectAllButton.clicked.connect(self.select_all)
        self.unselectAllButton.clicked.connect(self.unselect_all)
        self.deleteButton.clicked.connect(self.delete_selected)
        
        # Connect folder list selection changed signal
        self.folderList.itemSelectionChanged.connect(self.update_delete_button)
        
        self.show()
    
    def browse_directory(self):
        directory = get_existing_directory(self, "Select Directory")
        if directory:
            self.pathInput.setText(directory)
    
    def start_scan(self):
        path = self.pathInput.text()
        if not path:
            self.show_error("Please select a directory first")
            return
        
        # Clear previous results
        self.folderList.clear()
        self.deleteButton.setEnabled(False)
        
        # Update UI state
        self.scanButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.statusLabel.setText("Scanning...")
        
        # Start the scan
        self.logic.find_empty_folders(path)
    
    def select_all(self):
        for i in range(self.folderList.count()):
            self.folderList.item(i).setSelected(True)
    
    def unselect_all(self):
        self.folderList.clearSelection()
    
    def delete_selected(self):
        selected_items = self.folderList.selectedItems()
        if not selected_items:
            return
        
        # Confirm deletion
        msg = f'Delete {len(selected_items)} empty folder(s)?'
        reply = QMessageBox.question(
            self, 'Confirm Deletion', msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            folders_to_delete = [item.text() for item in selected_items]
            self.deleteButton.setEnabled(False)
            self.logic.delete_folders(folders_to_delete)
    
    def update_status(self, message):
        self.statusLabel.setText(message)
    
    def display_folders(self, folders):
        self.folderList.clear()
        for folder in folders:
            item = QListWidgetItem(folder)
            self.folderList.addItem(item)
    
    def handle_deletion_update(self, path, success):
        # Find and remove the item from the list if deletion was successful
        if success:
            items = self.folderList.findItems(path, Qt.MatchExactly)
            for item in items:
                self.folderList.takeItem(self.folderList.row(item))
    
    def show_error(self, message):
        show_error_dialog(self, "Error", message)
    
    def handle_operation_finished(self, was_find_operation):
        if was_find_operation:
            self.scanButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.update_delete_button()
        else:
            self.deleteButton.setEnabled(True)
    
    def update_delete_button(self):
        self.deleteButton.setEnabled(len(self.folderList.selectedItems()) > 0)


def main():
    app = QApplication(sys.argv)
    window = EmptyFoldersWindow()  # Keep a reference to the window
    window.show()  # Explicitly show the window
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()