"""
CMSD GUI Module

Modern PyQt5 GUI implementation using StandardWindow architecture.
Migrated from original cmsd.py with enhanced features and consistency.
"""

import os
import sys
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager
from file_utilities_2.core.cmsd_logic import CMSDLogic


class CMSDWindow(StandardWindow):
    """Content Management System Directory window."""
    
    def __init__(self):
        """Initialize CMSD window."""
        super().__init__(
            title="Content Management System Directory",
            icon_path=self._get_cmsd_icon()
        )
        
        # Initialize core logic
        self.cmsd_logic = CMSDLogic()
        
        # Initialize models
        self.left_model = QStandardItemModel()
        self.right_model = QStandardItemModel()
        
        # Setup UI
        self._setup_cmsd_ui()
        self._connect_signals()
        self._apply_cmsd_theme()
        
        # Load initial state
        self._load_initial_directories()
    
    def _get_cmsd_icon(self) -> str:
        """Get CMSD icon path."""
        icon_path = os.path.join(
            os.path.dirname(__file__), '..', 'icons', 'cmsd.png'
        )
        # Fallback to a default icon if specific one doesn't exist
        if not os.path.exists(icon_path):
            return os.path.join(
                os.path.dirname(__file__), 'icons', 'app_icon.png'
            )
        return icon_path
    
    def _setup_cmsd_ui(self) -> None:
        """Setup CMSD-specific UI components."""
        try:
            # Load UI file
            ui_path = os.path.join(os.path.dirname(__file__), 'cmsd.ui')
            uic.loadUi(ui_path, self)
            
            # Setup list views
            if hasattr(self, 'listView'):
                self.listView.setModel(self.left_model)
            if hasattr(self, 'selectView'):
                self.selectView.setModel(self.right_model)
                
        except Exception as e:
            self.show_error_dialog(
                "UI Setup Error", f"Failed to load UI: {e}"
            )
    
    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        # Menu actions
        if hasattr(self, 'actionOpenLeft'):
            self.actionOpenLeft.triggered.connect(self.load_directory_left)
        if hasattr(self, 'actionOpenRight'):
            self.actionOpenRight.triggered.connect(
                self.load_directory_right
            )
        if hasattr(self, 'actionexit'):
            self.actionexit.triggered.connect(self.close)
        
        # Button connections
        if hasattr(self, 'selectButton'):
            self.selectButton.clicked.connect(self._move_files_right)
        if hasattr(self, 'removeButton'):
            self.removeButton.clicked.connect(self._move_files_left)
        if hasattr(self, 'applyButton'):
            self.applyButton.clicked.connect(self._apply_operations)
        if hasattr(self, 'filterButton'):
            self.filterButton.clicked.connect(self._apply_filter)
    
    def _apply_cmsd_theme(self) -> None:
        """Apply CMSD-specific theming."""
        ThemeManager.apply_utility_window_theme(self)
        
        # Additional CMSD-specific styling
        self.setStyleSheet(self.styleSheet() + """
            QListView {
                border: 1px solid #ccc;
                background-color: white;
                selection-background-color: #3498db;
                alternate-background-color: #f5f5f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                margin: 10px 0px;
                padding-top: 5px;
            }
            
            QPushButton {
                min-height: 25px;
                padding: 5px 10px;
            }
            
            QLineEdit {
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 3px;
            }
        """)
    
    def _load_initial_directories(self) -> None:
        """Load initial directories."""
        self.load_directory_left(".")
        self.load_directory_right(".")
    
    def load_directory_left(self, directory: Optional[str] = None) -> None:
        """Load left directory."""
        if directory is None:
            directory = self.get_directory_path("Select Left Directory")
        
        if directory and os.path.isdir(directory):
            self.cmsd_logic.left_directory = directory
            self._update_left_view()
            self.show_status_message(f"Left directory: {directory}")
    
    def load_directory_right(self, directory: Optional[str] = None) -> None:
        """Load right directory."""
        if directory is None:
            directory = self.get_directory_path("Select Right Directory")
        
        if directory and os.path.isdir(directory):
            self.cmsd_logic.right_directory = directory
            self._update_right_view()
            self.show_status_message(f"Right directory: {directory}")
    
    def _update_left_view(self) -> None:
        """Update left directory view."""
        self.left_model.clear()
        files = self.cmsd_logic.get_left_files()
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            item = QStandardItem(file_name)
            item.setData(file_path)
            self.left_model.appendRow(item)
    
    def _update_right_view(self) -> None:
        """Update right directory view."""
        self.right_model.clear()
        files = self.cmsd_logic.get_right_files()
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            item = QStandardItem(file_name)
            item.setData(file_path)
            self.right_model.appendRow(item)
    
    def _update_directory_views(self) -> None:
        """Update both directory views."""
        self._update_left_view()
        self._update_right_view()
    
    def _move_files_right(self) -> None:
        """Move selected files from left to right."""
        if hasattr(self, 'listView'):
            selected_indexes = self.listView.selectedIndexes()
            for index in selected_indexes:
                item = self.left_model.itemFromIndex(index)
                if item:
                    file_path = item.data()
                    if file_path:
                        self.cmsd_logic.add_to_selection(file_path)
            
            # Perform copy operation
            result = self.cmsd_logic.copy_selected_to_right()
            if result.success:
                self.show_status_message(
                    f"Copied {len(result.processed_files)} files"
                )
                self._update_directory_views()
            else:
                error_msg = "\n".join([
                    f"{file}: {error}" 
                    for file, error in result.failed_files
                ])
                self.show_error_dialog("Copy Failed", error_msg)
    
    def _move_files_left(self) -> None:
        """Move selected files from right to left."""
        if hasattr(self, 'selectView'):
            selected_indexes = self.selectView.selectedIndexes()
            for index in selected_indexes:
                item = self.right_model.itemFromIndex(index)
                if item:
                    file_path = item.data()
                    if file_path:
                        self.cmsd_logic.add_to_selection(file_path)
            
            # Perform copy operation
            result = self.cmsd_logic.copy_selected_to_left()
            if result.success:
                self.show_status_message(
                    f"Copied {len(result.processed_files)} files"
                )
                self._update_directory_views()
            else:
                error_msg = "\n".join([
                    f"{file}: {error}" 
                    for file, error in result.failed_files
                ])
                self.show_error_dialog("Copy Failed", error_msg)
    
    def _apply_operations(self) -> None:
        """Apply selected operations to files."""
        # This would implement the rename operations based on radio buttons
        # For now, just show a comparison
        comparison = self.cmsd_logic.compare_directories()
        
        message = f"""Directory Comparison Results:
        
Left only: {len(comparison.only_left)} files
Right only: {len(comparison.only_right)} files
Common: {len(comparison.common)} files
        
Total Left: {comparison.total_left}
Total Right: {comparison.total_right}"""
        
        self.show_info_dialog("Comparison Results", message)
    
    def _apply_filter(self) -> None:
        """Apply filter to directory views."""
        if hasattr(self, 'filterEdit'):
            filter_text = self.filterEdit.text().lower()
            if filter_text:
                # Simple filter implementation
                self.show_status_message(f"Filter applied: {filter_text}")
                # TODO: Implement actual filtering logic
            else:
                self.show_status_message("Filter cleared")
                self._update_directory_views()


def main():
    """Main entry point for standalone execution."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = CMSDWindow()
    window.show()
    
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())