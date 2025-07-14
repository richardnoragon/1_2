"""Content Management System Directory tool.

This module provides functionality for managing and comparing directories
with file selection and organization capabilities.
"""

import os
import sys
import shutil
from typing import List, Optional

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic

from gui.common.base_window import BaseWindow
from gui.common.dialogs import get_existing_directory


class CMSDWindow(BaseWindow):
    """Content Management System Directory window for file management.
    
    This window provides a graphical interface for managing and comparing
    directories with file selection and organization capabilities.
    
    Features:
    - Dual directory views for comparison
    - File selection and management
    - Directory navigation
    - File operations between directories
    
    Attributes:
        left_directory: Path to the left directory
        right_directory: Path to the right directory
        left_model: Model for left file list
        right_model: Model for right file list
        selected: List of selected files
    """
    # Default paths
    _ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
    _ICON_NAME = "cmsd.png"
    _UI_FILE = "cmsd.ui"

    def __init__(self) -> None:
        """Initialize the CMSDWindow.
        
        Sets up:
        - UI components and layout
        - Data models and internal state
        - Signal connections
        - Initial directory paths
        """
        super().__init__()
        self._setup_ui()
        self._init_models()
        self._connect_signals()
        self._set_initial_state()
        self.show()

    def _setup_ui(self) -> None:
        """Initialize and load the UI file."""
        try:
            ui_path = os.path.dirname(__file__)
            ui_file: str = os.path.join(ui_path, self._UI_FILE)
            uic.loadUi(ui_file, self)
        except Exception as e:
            print(f"Error loading UI: {e}")

    def _init_models(self) -> None:
        """Initialize data models and internal state."""
        self.left_directory: str = "."
        self.right_directory: str = "."
        self.left_model: QStandardItemModel = QStandardItemModel()
        self.right_model: QStandardItemModel = QStandardItemModel()
        self.selected: List[str] = []

        # Set up list views
        if hasattr(self, 'listView'):
            self.listView.setModel(self.left_model)
        if hasattr(self, 'selectView'):
            self.selectView.setModel(self.right_model)

    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots."""
        # Connect menu actions
        if hasattr(self, 'actionOpenLeft'):
            self.actionOpenLeft.triggered.connect(self.load_directory_left)
        if hasattr(self, 'actionOpenRight'):
            self.actionOpenRight.triggered.connect(self.load_directory_right)
        if hasattr(self, 'actionexit'):
            self.actionexit.triggered.connect(self.close)

    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements."""
        self._load_initial_directories()

    def _load_initial_directories(self) -> None:
        """Load initial directories into the views."""
        self.load_directory_left(self.left_directory)
        self.load_directory_right(self.right_directory)

    def load_directory_left(self, directory: Optional[str] = None) -> None:
        """Load files from selected directory into the left view.
        
        Args:
            directory: Directory path to load (uses dialog if None)
        """
        if directory is None or not os.path.isdir(directory):
            directory = get_existing_directory(self, "Select Left Directory")
        
        if directory and os.path.isdir(directory):
            self.left_directory = directory
            self.left_model.clear()
            
            try:
                files: List[str] = sorted(os.listdir(directory))
                for file in files:
                    full_path: str = os.path.join(directory, file)
                    if os.path.isfile(full_path):
                        item: QStandardItem = QStandardItem(file)
                        item.setData(full_path)  # Store full path
                        self.left_model.appendRow(item)
            except OSError as e:
                print(f"Error loading left directory: {e}")

    def load_directory_right(self, directory: Optional[str] = None) -> None:
        """Load files from selected directory into the right view.
        
        Args:
            directory: Directory path to load (uses dialog if None)
        """
        if directory is None or not os.path.isdir(directory):
            directory = get_existing_directory(self, "Select Right Directory")
        
        if directory and os.path.isdir(directory):
            self.right_directory = directory
            self.right_model.clear()
            
            try:
                files: List[str] = sorted(os.listdir(directory))
                for file in files:
                    full_path: str = os.path.join(directory, file)
                    if os.path.isfile(full_path):
                        item: QStandardItem = QStandardItem(file)
                        item.setData(full_path)  # Store full path
                        self.right_model.appendRow(item)
            except OSError as e:
                print(f"Error loading right directory: {e}")

    def get_selected_files(self) -> List[str]:
        """Get list of currently selected files.
        
        Returns:
            List of selected file paths
        """
        return self.selected.copy()

    def add_to_selection(self, file_path: str) -> None:
        """Add a file to the selection list.
        
        Args:
            file_path: Path to the file to add
        """
        if file_path not in self.selected:
            self.selected.append(file_path)

    def remove_from_selection(self, file_path: str) -> None:
        """Remove a file from the selection list.
        
        Args:
            file_path: Path to the file to remove
        """
        if file_path in self.selected:
            self.selected.remove(file_path)

    def clear_selection(self) -> None:
        """Clear all selected files."""
        self.selected.clear()

    def get_left_files(self) -> List[str]:
        """Get list of files in the left directory.
        
        Returns:
            List of file paths in left directory
        """
        files: List[str] = []
        if os.path.isdir(self.left_directory):
            try:
                for file in os.listdir(self.left_directory):
                    full_path: str = os.path.join(self.left_directory, file)
                    if os.path.isfile(full_path):
                        files.append(full_path)
            except OSError:
                pass
        return sorted(files)

    def get_right_files(self) -> List[str]:
        """Get list of files in the right directory.
        
        Returns:
            List of file paths in right directory
        """
        files: List[str] = []
        if os.path.isdir(self.right_directory):
            try:
                for file in os.listdir(self.right_directory):
                    full_path: str = os.path.join(self.right_directory, file)
                    if os.path.isfile(full_path):
                        files.append(full_path)
            except OSError:
                pass
        return sorted(files)

    def compare_directories(self) -> None:
        """Compare the contents of both directories."""
        left_files: set[str] = set(self.get_left_files())
        right_files: set[str] = set(self.get_right_files())
        
        # Find differences
        only_left: List[str] = sorted(left_files - right_files)
        only_right: List[str] = sorted(right_files - left_files)
        common: List[str] = sorted(left_files & right_files)
        
        # You could update UI to show these differences
        print(f"Files only in left: {len(only_left)}")
        print(f"Files only in right: {len(only_right)}")
        print(f"Common files: {len(common)}")

    def copy_selected_to_right(self) -> None:
        """Copy selected files from left to right directory."""
        if not self.selected:
            return
            
        for file_path in self.selected:
            if os.path.isfile(file_path):
                try:
                    file_name: str = os.path.basename(file_path)
                    dest_path: str = os.path.join(
                        self.right_directory, file_name
                    )
                    shutil.copy2(file_path, dest_path)
                except OSError as e:
                    print(f"Error copying {file_path}: {e}")
        
        # Refresh right directory view
        self.load_directory_right(self.right_directory)
        self.clear_selection()

    def copy_selected_to_left(self) -> None:
        """Copy selected files from right to left directory."""
        if not self.selected:
            return
            
        for file_path in self.selected:
            if os.path.isfile(file_path):
                try:
                    file_name: str = os.path.basename(file_path)
                    dest_path: str = os.path.join(
                        self.left_directory, file_name
                    )
                    shutil.copy2(file_path, dest_path)
                except OSError as e:
                    print(f"Error copying {file_path}: {e}")
        
        # Refresh left directory view
        self.load_directory_left(self.left_directory)
        self.clear_selection()

    def delete_selected_files(self) -> None:
        """Delete selected files from their respective directories."""
        if not self.selected:
            return
            
        for file_path in self.selected:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
        
        # Refresh both directory views
        self.load_directory_left(self.left_directory)
        self.load_directory_right(self.right_directory)
        self.clear_selection()

    def close(self) -> bool:
        """Close the application window.
        
        Returns:
            bool: True if window was closed successfully
        """
        return super().close()


def main() -> None:
    """Main entry point for the CMSD application."""
    app: QApplication = QApplication(sys.argv)
    app.setStyle('Fusion')
    CMSDWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
