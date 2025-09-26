"""
Consolidated File Rename GUI - File Utilities 2
===============================================

This module provides a comprehensive file renaming interface that consolidates
the best features from multiple rename implementations into a single, 
standardized GUI following the file_utilities_2 architecture patterns.

Features:
- Comprehensive rename modes (prefix, suffix, case, date, metadata)
- Metadata extraction from images and audio files
- Multiple date format options
- File filtering and batch selection
- Standardized UI with consistent theming
- Enhanced error handling and logging
- PyQt5 compatibility
"""

import sys
from pathlib import Path
from typing import List, Optional

# PyQt5 imports
from PyQt5.QtWidgets import QApplication, QGroupBox, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic

# File Utilities 2 imports
from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager
from core.file_ops.renamer import FileRenamer
from core.logging_manager import LogManager
from core.error_handler import error_handler


class RenameGUI(StandardWindow):
    """
    Consolidated file rename GUI with comprehensive functionality.
    
    This class combines the best features from multiple rename implementations:
    - Rich UI from original rename.py
    - Modern architecture from gui/file_ops/rename_window.py
    - Core business logic from core/file_ops/renamer.py
    - Standardized patterns from file_utilities_2
    
    Features:
    - 9 different rename modes
    - Metadata-based renaming (EXIF, audio tags)
    - 5 date format options
    - File filtering and selection
    - Batch processing
    - Enhanced error handling
    """
    
    # Supported date formats for metadata-based renaming
    DATE_FORMATS = [
        "YYYY-MM-DD_HHMMSS",
        "YYYYMMDD_HHMMSS", 
        "DD-MM-YYYY_HHMMSS",
        "YYYY-MM-DD",
        "YYYYMMDD"
    ]
    
    def __init__(self):
        """Initialize the RenameGUI with consolidated functionality."""
        super().__init__(
            title="File Rename Utility - File Utilities 2",
            icon_path=self._get_rename_icon()
        )
        
        # Initialize logging
        self.logger = LogManager().get_logger('RenameGUI')
        self.logger.info("Initializing consolidated rename GUI")
        
        # Initialize state
        self._current_dir = Path(".")
        self._selected_files = []
        self._file_list_model = QStandardItemModel()
        self._selection_model = QStandardItemModel()
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        
        self.logger.info("Rename GUI initialization completed")
    
    def _get_rename_icon(self) -> str:
        """Get the rename utility icon path."""
        icon_path = Path(__file__).parent / "icons" / "rename.png"
        if icon_path.exists():
            return str(icon_path)
        return str(Path(__file__).parent / "icons" / "app_icon.png")
    
    def _setup_ui(self):
        """Setup the user interface by loading and configuring the UI file."""
        try:
            # Load UI file from the same directory
            ui_file = Path(__file__).parent / "rename.ui"
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
            
            # Validate UI file
            if not ui_file.stat().st_size:
                raise ValueError("UI file is empty")
            
            # Load UI
            uic.loadUi(str(ui_file), self)
            self.logger.info(f"UI loaded successfully from {ui_file}")
            
            # Setup models
            self._setup_models()
            
            # Setup metadata formats
            self._setup_metadata_formats()
            
            # Apply standardized theming
            self._apply_standardized_theming()
            
            # Set initial state
            self._set_initial_state()
            
        except Exception as e:
            error_msg = f"Failed to setup UI: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("UI Setup Error", error_msg)
            sys.exit(1)
    
    def _setup_models(self):
        """Setup data models for file lists."""
        try:
            # Setup file list model
            self.listView.setModel(self._file_list_model)
            
            # Setup selection model  
            self.selectView.setModel(self._selection_model)
            
            self.logger.debug("Data models setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup models: {e}", exc_info=True)
            raise
    
    def _setup_metadata_formats(self):
        """Setup metadata format options in combo box."""
        try:
            self.metadataFormatCombo.clear()
            self.metadataFormatCombo.addItems(self.DATE_FORMATS)
            self.metadataFormatCombo.setCurrentIndex(0)
            
            self.logger.debug("Metadata formats setup completed")
            
        except Exception as e:
            self.logger.error(
                f"Failed to setup metadata formats: {e}", exc_info=True
            )
            raise
    
    def _apply_standardized_theming(self):
        """Apply standardized theming to UI components."""
        try:
            # Apply theme to main components
            ThemeManager.style_primary_button(self.applyButton)
            ThemeManager.style_secondary_button(self.filterButton)
            ThemeManager.style_secondary_button(self.selectButton)
            ThemeManager.style_secondary_button(self.removeButton)
            
            # Style group boxes for rename options
            rename_group = QGroupBox("Rename Options")
            ThemeManager.style_group_box(rename_group)
            
            self.logger.debug("Standardized theming applied")
            
        except Exception as e:
            self.logger.warning(f"Failed to apply theming: {e}")
    
    def _set_initial_state(self):
        """Set initial UI state."""
        try:
            # Set default rename mode
            self.addPrefixRadio.setChecked(True)
            
            # Clear input fields
            self.nameEdit.clear()
            self.filterEdit.clear()
            
            # Update status
            self.show_status_message("Ready - Select directory to begin")
            
            self.logger.debug("Initial state set")
            
        except Exception as e:
            self.logger.error(
                f"Failed to set initial state: {e}", exc_info=True
            )
    
    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        try:
            # Menu actions
            self.actionSelect.triggered.connect(self.load_directory)
            self.actionExit.triggered.connect(self.close)
            
            # Button signals
            self.filterButton.clicked.connect(self.filter_list)
            self.selectButton.clicked.connect(self.choose_selection)
            self.removeButton.clicked.connect(self.remove_selection)
            self.applyButton.clicked.connect(self.rename_files)
            
            self.logger.debug("Signal connections completed")
            
        except Exception as e:
            self.logger.error(f"Failed to connect signals: {e}", exc_info=True)
            raise
    
    @error_handler
    def load_directory(self):
        """Load files from selected directory into the view."""
        try:
            dir_path = self.get_directory_path(
                "Select Directory for Rename Operations"
            )
            if dir_path:
                self._current_dir = Path(dir_path)
                self._update_file_list()
                self.show_status_message(
                    f"Loaded directory: {self._current_dir}"
                )
                self.logger.info(f"Directory loaded: {self._current_dir}")
                
        except Exception as e:
            error_msg = f"Failed to load directory: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("Directory Load Error", error_msg)
    
    def _update_file_list(self):
        """Update the file list view with current directory contents."""
        try:
            self._file_list_model.clear()
            
            if not self._current_dir.exists():
                self.logger.warning(
                    f"Directory does not exist: {self._current_dir}"
                )
                return
            
            files = self._get_files_in_directory()
            for filename in files:
                item = QStandardItem(filename)
                self._file_list_model.appendRow(item)
            
            self.show_status_message(f"Found {len(files)} files")
            self.logger.debug(f"File list updated with {len(files)} files")
            
        except Exception as e:
            error_msg = f"Failed to update file list: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("File List Error", error_msg)
    
    def _get_files_in_directory(self) -> List[str]:
        """Get list of files in the current directory."""
        try:
            if not self._current_dir.exists():
                return []
            
            files = []
            for item in self._current_dir.iterdir():
                if item.is_file():
                    files.append(item.name)
            
            return sorted(files)
            
        except Exception as e:
            self.logger.error(
                f"Failed to get files in directory: {e}", exc_info=True
            )
            return []
    
    @error_handler
    def filter_list(self):
        """Filter file list based on user input."""
        try:
            filter_text = self.filterEdit.text().lower()
            self._file_list_model.clear()
            
            if not self._current_dir.exists():
                return
            
            files = self._get_filtered_files(filter_text)
            for filename in files:
                item = QStandardItem(filename)
                self._file_list_model.appendRow(item)
            
            self.show_status_message(f"Filtered to {len(files)} files")
            self.logger.debug(
                f"Applied filter '{filter_text}', {len(files)} files shown"
            )
            
        except Exception as e:
            error_msg = f"Failed to filter files: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("Filter Error", error_msg)
    
    def _get_filtered_files(self, filter_text: str) -> List[str]:
        """Get list of files matching the filter."""
        try:
            if not self._current_dir.exists():
                return []
            
            files = []
            for item in self._current_dir.iterdir():
                if item.is_file() and filter_text in item.name.lower():
                    files.append(item.name)
            
            return sorted(files)
            
        except Exception as e:
            self.logger.error(
                f"Failed to get filtered files: {e}", exc_info=True
            )
            return []
    
    @error_handler
    def choose_selection(self):
        """Add selected files to the selection list."""
        try:
            indices = self.listView.selectedIndexes()
            added_count = 0
            
            for index in indices:
                item = self._file_list_model.itemFromIndex(index)
                if item:
                    filename = item.text()
                    if filename not in self._selected_files:
                        self._add_to_selection(filename)
                        added_count += 1
            
            if added_count > 0:
                self.show_status_message(
                    f"Added {added_count} files to selection"
                )
                self.logger.debug(f"Added {added_count} files to selection")
            
        except Exception as e:
            error_msg = f"Failed to add selection: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("Selection Error", error_msg)
    
    def _add_to_selection(self, filename: str):
        """Add a file to the selection list."""
        try:
            self._selected_files.append(filename)
            item = QStandardItem(filename)
            self._selection_model.appendRow(item)
            
        except Exception as e:
            self.logger.error(
                f"Failed to add file to selection: {e}", exc_info=True
            )
    
    @error_handler
    def remove_selection(self):
        """Remove selected files from the selection list."""
        try:
            indices = sorted(
                self.selectView.selectedIndexes(),
                key=lambda x: x.row(),
                reverse=True
            )
            
            removed_count = 0
            for index in indices:
                item = self._selection_model.itemFromIndex(index)
                if item:
                    filename = item.text()
                    if filename in self._selected_files:
                        self._selected_files.remove(filename)
                        self._selection_model.removeRow(index.row())
                        removed_count += 1
            
            if removed_count > 0:
                self.show_status_message(
                    f"Removed {removed_count} files from selection"
                )
                self.logger.debug(
                    f"Removed {removed_count} files from selection"
                )
            
        except Exception as e:
            error_msg = f"Failed to remove selection: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("Selection Error", error_msg)
    
    def _get_rename_mode_and_params(self) -> tuple:
        """Get the current rename mode and parameters."""
        try:
            text = self.nameEdit.text()
            mode = None
            date_format = None
            
            # Determine rename mode based on radio button selection
            if self.metadataRadio.isChecked():
                mode = "metadata"
                date_format = self.metadataFormatCombo.currentText()
            elif self.addPrefixRadio.isChecked():
                mode = "prefix"
            elif self.removePrefixRadio.isChecked():
                mode = "remove_prefix"
            elif self.addSuffixRadio.isChecked():
                mode = "suffix"
            elif self.removeSuffixRadio.isChecked():
                mode = "remove_suffix"
            elif self.newNameRadio.isChecked():
                mode = "new_name"
            elif self.lowerCaseRadio.isChecked():
                mode = "lower"
            elif self.radioButton.isChecked():  # Upper case radio
                mode = "upper"
            elif self.adddateprefixRadio.isChecked():
                mode = "date_prefix"
            elif self.adddatesuffixRadio.isChecked():
                mode = "date_suffix"
            
            return mode, text, date_format
            
        except Exception as e:
            self.logger.error(f"Failed to get rename mode: {e}", exc_info=True)
            return None, None, None
    
    @error_handler
    def rename_files(self):
        """Rename selected files based on chosen options and patterns."""
        try:
            # Validate selection
            if not self._selected_files:
                self.show_warning_dialog(
                    "No Selection", "Please select files to rename"
                )
                return
            
            # Get rename parameters
            mode, text, date_format = self._get_rename_mode_and_params()
            
            # Validate parameters
            if not self._validate_rename_params(mode, text):
                return
            
            # Confirm operation
            if not self._confirm_rename_operation():
                return
            
            # Perform rename operation
            self._perform_rename_operation(mode, text, date_format)
            
        except Exception as e:
            error_msg = f"Failed to rename files: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("Rename Error", error_msg)
    
    def _validate_rename_params(self, mode: str, text: str) -> bool:
        """Validate rename parameters."""
        try:
            # Check if mode requires text input
            text_required_modes = [
                "prefix", "remove_prefix", "suffix", "remove_suffix",
                "new_name"
            ]
            
            if mode in text_required_modes and not text.strip():
                self.show_warning_dialog(
                    "Missing Input", 
                    f"Please enter text for {mode} operation"
                )
                return False
            
            # Check for valid mode
            if not mode:
                self.show_warning_dialog(
                    "No Mode Selected",
                    "Please select a rename mode"
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to validate rename params: {e}", exc_info=True
            )
            return False
    
    def _confirm_rename_operation(self) -> bool:
        """Confirm rename operation with user."""
        try:
            reply = QMessageBox.question(
                self,
                "Confirm Rename",
                f"Are you sure you want to rename "
                f"{len(self._selected_files)} files?\n\n"
                "This operation cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            return reply == QMessageBox.Yes
            
        except Exception as e:
            self.logger.error(
                f"Failed to confirm rename operation: {e}", exc_info=True
            )
            return False
    
    def _perform_rename_operation(
        self, mode: str, text: str, date_format: Optional[str]
    ):
        """Perform the actual rename operation."""
        try:
            # Create file paths
            file_paths = [
                self._current_dir / filename 
                for filename in self._selected_files
            ]
            
            # Show progress
            self.show_status_message("Renaming files...")
            
            # Perform rename using core FileRenamer
            results = FileRenamer.rename_files(
                file_paths, mode, text, date_format
            )
            
            # Process results
            success_count = sum(1 for result in results if result)
            total_count = len(results)
            
            # Show results
            self._show_rename_results(success_count, total_count)
            
            # Clear selection and refresh
            self._clear_selection()
            self._update_file_list()
            
            self.logger.info(
                f"Rename operation completed: {success_count}/"
                f"{total_count} successful"
            )
            
        except Exception as e:
            error_msg = f"Failed to perform rename operation: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_dialog("Rename Operation Error", error_msg)
    
    def _show_rename_results(self, success_count: int, total_count: int):
        """Show rename operation results to user."""
        try:
            if success_count == total_count:
                self.show_info_dialog(
                    "Rename Complete",
                    f"Successfully renamed all {total_count} files"
                )
                self.show_status_message(
                    f"Successfully renamed {total_count} files"
                )
            elif success_count == 0:
                self.show_error_dialog(
                    "Rename Failed",
                    "Failed to rename any files"
                )
                self.show_status_message("Rename operation failed")
            else:
                self.show_warning_dialog(
                    "Partial Success",
                    f"Renamed {success_count} out of {total_count} files"
                )
                self.show_status_message(
                    f"Renamed {success_count}/{total_count} files"
                )
                
        except Exception as e:
            self.logger.error(
                f"Failed to show rename results: {e}", exc_info=True
            )
    
    def _clear_selection(self):
        """Clear the current selection after renaming."""
        try:
            self._selected_files.clear()
            self._selection_model.clear()
            self.logger.debug("Selection cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear selection: {e}", exc_info=True)
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            self.logger.info("Rename GUI closing")
            super().closeEvent(event)
            
        except Exception as e:
            self.logger.error(f"Error during close: {e}", exc_info=True)
            event.accept()


def main():
    """Application entry point for standalone execution."""
    try:
        app = QApplication(sys.argv)
        
        # Create and show window
        window = RenameGUI()
        window.show()
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Failed to start Rename GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()