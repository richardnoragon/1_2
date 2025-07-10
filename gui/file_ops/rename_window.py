"""GUI for file renaming operations."""
import sys
from pathlib import Path
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QFileDialog, QMessageBox
)
from PyQt5 import uic

from core.file_ops.renamer import FileRenamer
from core.logging_manager import LogManager

from core.error_handler import error_handler



class RenameWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.logger = LogManager().get_logger('RenameWindow')
        self.setup_ui()
        self.directory = Path(".")
        self.selected_files = []
    
    def setup_ui(self):
        """Initialize the UI components."""
        try:
            # Load UI file
            ui_file = Path(__file__).parent.parent.parent / "rename.ui"
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
            
            # Add error handling for UI loading
            try:
                ui_content = ui_file.read_text(encoding='utf-8')
                if not ui_content:
                    raise ValueError("UI file is empty")
            except Exception as e:
                raise IOError(f"Failed to read UI file: {str(e)}")

            uic.loadUi(str(ui_file), self)
            
            # Initialize models
            self.listModel = QStandardItemModel()
            self.selectModel = QStandardItemModel()
            self.selectView.setModel(self.selectModel)
            
            # Setup metadata format combo box
            self.metadataFormatCombo.addItems([
                "YYYY-MM-DD_HHMMSS",
                "YYYYMMDD_HHMMSS",
                "DD-MM-YYYY_HHMMSS",
                "YYYY-MM-DD",
                "YYYYMMDD"
            ])
            
            # Connect signals
            self.actionSelect.triggered.connect(self.load_directory)
            self.actionexit.triggered.connect(self.close)
            self.filterButton.clicked.connect(self.filter_list)
            self.selectButton.clicked.connect(self.choose_selection)
            self.removeButton.clicked.connect(self.remove_selection)
            self.applyButton.clicked.connect(self.rename_files)
            
            # Initialize radio buttons
            self.addPrefixRadio.setChecked(True)
            
            self.show()
            
        except (IOError, ValueError) as e:
            msg = f"Failed to initialize: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogNone, "Error", msg
            sys.exit(1)

    def load_directory(self):
        """Load files from selected directory."""
        try:
            dir_path = get_existing_directory(
                self, 
                "Select Directory"
            )
            if dir_path:
                self.directory = Path(dir_path)
                self.refresh_file_list()
        except OSError as e:
            msg = f"Failed to load directory: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg
    
    def refresh_file_list(self, filter_text: str = ""):
        """Refresh the file list with optional filtering."""
        try:
            self.listModel.clear()
            filter_text = filter_text.lower()
            
            for file_path in self.directory.iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    if not filter_text or filter_text in filename.lower():
                        self.listModel.appendRow(QStandardItem(filename))
            
            self.listView.setModel(self.listModel)
        except OSError as e:
            msg = f"Failed to refresh file list: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg

    def filter_list(self):
        """Filter the file list based on user input."""
        try:
            filter_text = self.filterEdit.text()
            self.refresh_file_list(filter_text)
        except ValueError as e:
            msg = f"Failed to filter list: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg

    def choose_selection(self):
        """Add selected files to the rename list."""
        try:
            indices = self.listView.selectedIndexes()
            for index in indices:
                item = self.listModel.itemFromIndex(index)
                if item is None:
                    continue
                filename = item.text()
                if filename not in self.selected_files:
                    self.selected_files.append(filename)
                    self.selectModel.appendRow(QStandardItem(filename))
        except ValueError as e:
            msg = f"Failed to add selection: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg

    def remove_selection(self):
        """Remove selected files from the rename list."""
        try:
            indices = self.selectView.selectedIndexes()
            for index in sorted(indices, reverse=True):
                item = self.selectModel.itemFromIndex(index)
                if item is None:
                    continue
                filename = item.text()
                self.selected_files.remove(filename)
                self.selectModel.removeRow(index.row())
        except (ValueError, IndexError) as e:
            msg = f"Failed to remove selection: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg

    def get_rename_mode(self) -> tuple:
        """Get the current rename mode and parameters."""
        try:
            text = self.nameEdit.text()
            mode = None
            date_format = None
            
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
            elif self.radioButton.isChecked():
                mode = "upper"
            elif self.adddateprefixRadio.isChecked():
                mode = "date_prefix"
            elif self.adddatesuffixRadio.isChecked():
                mode = "date_suffix"
            
            return mode, text, date_format
        except (AttributeError, ValueError) as e:
            msg = f"Failed to get rename mode: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg
            return None, None, None

    def rename_files(self):
        """Rename the selected files."""
        try:
            mode, text, date_format = self.get_rename_mode()
            if not mode and not text:
                return
            
            # Create list of file paths
            files = [
                self.directory / filename
                for filename in self.selected_files
            ]
            
            # Attempt to rename all files
            results = FileRenamer.rename_files(
                files, mode, text, date_format
            )
            
            # Check results and show appropriate message
            success_count = sum(1 for result in results if result)
            if success_count == len(results):
                show_info_dialog
                    self,
                    "Success",
                    "All files renamed successfully"
                
            elif success_count == 0:
                show_error_dialog
                    self,
                    "Warning",
                    "Failed to rename any files"
                
            else:
                show_error_dialog
                    self,
                    "Partial Success",
                    f"Renamed {success_count} out of {len(results} files"
                )
            
            # Clear selection and refresh
            self.selected_files.clear()
            self.selectModel.clear()
            self.refresh_file_list()
            
        except (IOError, ValueError) as e:
            msg = f"Failed to rename files: {str(e)}"
            self.logger.error(msg, exc_info=True)
            show_error_dialogself, "Error", msg


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = RenameWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
