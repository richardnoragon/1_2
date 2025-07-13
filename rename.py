"""File renaming tool supporting patterns and metadata-based renaming."""

import os
import shutil
import sys
import time
from datetime import datetime
from typing import Optional

# Third-party imports
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen._file import File as MutagenFile
from PyQt5 import uic
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication

# Local imports
from gui.common.base_window import BaseWindow
from gui.common.dialogs import get_existing_directory, show_error_dialog

from core.error_handler import error_handler



class FileRenamerWindow(BaseWindow):
    """Main window for batch file renaming operations.
    
    This class provides a GUI for batch renaming files using various patterns
    and metadata extraction capabilities.
    
    Features:
    - Directory browsing and file filtering
    - Multiple file selection and batch processing
    - Pattern-based renaming (prefix, suffix, replacement)
    - Metadata-based renaming (from image/audio files)
    - Date-based renaming (file dates or metadata dates)
    - Case conversion (upper/lower)
    
    Attributes:
        _current_dir (str): Current working directory path
        _file_list_model (QStandardItemModel): Model for main file list
        _selection_model (QStandardItemModel): Model for selected files
        _selected_files (list[str]): List of selected filenames
    """
    
    # Supported date formats for metadata-based renaming
    DATE_FORMATS = [
        "YYYY-MM-DD_HHMMSS",
        "YYYYMMDD_HHMMSS",
        "DD-MM-YYYY_HHMMSS",
        "YYYY-MM-DD",
        "YYYYMMDD"
    ]
    
    # Supported image extensions
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
    
    # Supported audio extensions
    AUDIO_EXTENSIONS = ('.mp3', '.flac', '.m4a', '.wav')
    

    def __init__(self) -> None:
        """Initialize the FileRenamerWindow.
        
        Sets up:
        - UI components and layout
        - Data models
        - Signal connections
        """
        super().__init__()
        self._setup_ui()
        self._init_models()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize and load the UI file.
        
        This method handles:
        1. Loading the UI definition file
        2. Setting up data models
        3. Configuring metadata formats
        4. Connecting UI signals to handlers
        
        Raises:
            FileNotFoundError: If UI file is not found
            ValueError: If UI file is empty
            Exception: For any other initialization errors
        """
        try:
            self._load_ui_file()
            self._init_models()
            self._setup_metadata_formats()
            self._connect_signals()
            self.show()
            
        except (FileNotFoundError, ValueError) as e:
            self._handle_ui_error(str(e), "UI Error")
        except Exception as e:
            self._handle_ui_error(f"Failed to initialize UI: {e}", "Error")
    
    def _load_ui_file(self) -> None:
        """Load and validate the UI definition file.
        
        Raises:
            FileNotFoundError: If UI file is not found
            ValueError: If UI file is empty
        """
        ui_file = self._get_ui_file_path()
        
        if not os.path.exists(ui_file):
            raise FileNotFoundError(f"UI file not found: {ui_file}")
        
        if not os.path.getsize(ui_file):
            raise ValueError("UI file is empty")
            
        uic.loadUi(ui_file, self)
    
    def _get_ui_file_path(self) -> str:
        """Get the absolute path to the UI file.
        
        Returns:
            str: Absolute path to rename.ui
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "rename.ui")
    
    def _init_models(self) -> None:
        """Initialize data models and internal state.
        
        Sets up:
        - File list model
        - Selection model
        - Selected files list
        - Current directory
        """
        self._current_dir = "."
        self._file_list_model = QStandardItemModel()
        self._selection_model = QStandardItemModel()
        self._selected_files = []
        
        self.selectView.setModel(self._selection_model)
            
    def _setup_metadata_formats(self) -> None:
        """Setup metadata format options in combo box.
        
        Configures:
        - Available date/time formats
        - Default rename mode
        """
        self.metadataFormatCombo.addItems(self.DATE_FORMATS)
        self.addPrefixRadio.setChecked(True)
    
    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers.
        
        Connects:
        - Menu actions
        - Filter button
        - Selection buttons
        - Apply button
        """
        self.actionSelect.triggered.connect(self.load_directory)
        self.actionExit.triggered.connect(self.close)
        self.filterButton.clicked.connect(self.filter_list)
        self.selectButton.clicked.connect(self.choose_selection)
        self.removeButton.clicked.connect(self.remove_selection)
        self.applyButton.clicked.connect(self.rename_files)
    
    def _handle_ui_error(self, message: str, title: str) -> None:
        """Handle UI initialization errors.
        
        Args:
            message: Error message to display
            title: Dialog title
        """
        show_error_dialog(message, title, self)
        sys.exit(1)

    def load_directory(self) -> None:
        """Load files from selected directory into the view."""
        dir_path = get_existing_directory(self, "Select Directory")
        if dir_path:
            self._current_dir = dir_path
            self._update_file_list()
    
    def _update_file_list(self) -> None:
        """Update the file list view with current directory contents.
        
        Filters out directories and only shows files.
        """
        self._file_list_model.clear()
        if not self._current_dir:
            return
            
        files = self._get_files_in_directory()
        for filename in files:
            self._file_list_model.appendRow(QStandardItem(filename))
        self.listView.setModel(self._file_list_model)
        
    def _get_files_in_directory(self) -> list[str]:
        """Get list of files in the current directory.
        
        Returns:
            list[str]: List of filenames (excluding directories)
        """
        if not self._current_dir:
            return []
            
        return [
            filename for filename in os.listdir(self._current_dir)
            if os.path.isfile(os.path.join(self._current_dir, filename))
        ]

    def filter_list(self) -> None:
        """Filter file list based on user input.
        
        Updates the file list to only show files matching the filter text.
        Filter is case-insensitive.
        """
        filter_text = self.filterEdit.text().lower()
        self._file_list_model.clear()
        
        if not self._current_dir:
            return
            
        files = self._get_filtered_files(filter_text)
        for filename in files:
            self._file_list_model.appendRow(QStandardItem(filename))
            
    def _get_filtered_files(self, filter_text: str) -> list[str]:
        """Get list of files matching the filter.
        
        Args:
            filter_text: Text to filter filenames by (case-insensitive)
            
        Returns:
            list[str]: List of matching filenames
        """
        if not self._current_dir:
            return []
            
        return [
            filename for filename in os.listdir(self._current_dir)
            if (os.path.isfile(os.path.join(self._current_dir, filename)) and
                filter_text in filename.lower())
        ]

    def choose_selection(self) -> None:
        """Add selected files to the selection list.
        
        Adds files from the main list to the selection list,
        avoiding duplicates.
        """
        for index in self.listView.selectedIndexes():
            item = self._file_list_model.itemFromIndex(index)
            if item and item.text() not in self._selected_files:
                self._add_to_selection(item.text())

    def _add_to_selection(self, filename: str) -> None:
        """Add a file to the selection list.
        
        Args:
            filename: Name of file to add to selection
        """
        self._selected_files.append(filename)
        self._selection_model.appendRow(QStandardItem(filename))

    def remove_selection(self) -> None:
        """Remove selected files from the selection list.
        
        Removes files from both the selection model and tracking list.
        Processes indices in reverse order to maintain correct indices.
        """
        indices = sorted(
            self.selectView.selectedIndexes(),
            key=lambda x: x.row(),
            reverse=True
        )
        
        for index in indices:
            self._remove_from_selection(index)
            
    def _remove_from_selection(self, index: 'QModelIndex') -> None:
        """Remove a file from the selection list by index.
        
        Args:
            index: Index of the item to remove
        """
        item = self._selection_model.itemFromIndex(index)
        if item:
            self._selected_files.remove(item.text())
            self._selection_model.removeRow(index.row())

    def _get_metadata_date(self, filepath: str) -> datetime:
        """Extract date from file metadata based on file type.
        
        Args:
            filepath: Path to the file to extract date from
            
        Returns:
            datetime: Extracted date or file modification time as fallback
        """
        try:
            if self._is_image_file(filepath):
                return self._get_image_date(filepath)
            elif self._is_audio_file(filepath):
                return self._get_audio_date(filepath)
            
            return self._get_file_mtime(filepath)
        except Exception:
            return self._get_file_mtime(filepath)
            
    def _is_image_file(self, filepath: str) -> bool:
        """Check if file is an image based on extension.
        
        Args:
            filepath: Path to the file to check
            
        Returns:
            bool: True if file has an image extension
        """
        return filepath.lower().endswith(self.IMAGE_EXTENSIONS)
        
    def _is_audio_file(self, filepath: str) -> bool:
        """Check if file is an audio file based on extension.
        
        Args:
            filepath: Path to the file to check
            
        Returns:
            bool: True if file has an audio extension
        """
        return filepath.lower().endswith(self.AUDIO_EXTENSIONS)
        
    def _get_image_date(self, filepath: str) -> datetime:
        """Extract date from image metadata."""
        with Image.open(filepath) as img:
            exif = img.getexif()
            if not exif:
                return self._get_file_mtime(filepath)
                
            for tag_id in exif:
                tag = TAGS.get(tag_id, tag_id)
                if tag in ('DateTimeOriginal', 'DateTime'):
                    date_str = exif[tag_id]
                    return datetime.strptime(
                        date_str, '%Y:%m:%d %H:%M:%S'
                    )
                    
        return self._get_file_mtime(filepath)
        
    def _get_audio_date(self, filepath: str) -> datetime:
        """Extract date from audio file metadata."""
        audio = MutagenFile(filepath)
        if not audio or not hasattr(audio, 'tags'):
            return self._get_file_mtime(filepath)
            
        for tag in ('date', 'TDRC', 'year'):
            if tag not in audio.tags:
                continue
                
            date_str = str(audio.tags[tag][0])
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y')
                except ValueError:
                    continue
                    
        return self._get_file_mtime(filepath)
        
    def _get_file_mtime(self, filepath: str) -> datetime:
        """Get file modification time as datetime."""
        return datetime.fromtimestamp(os.path.getmtime(filepath))

    # Format map for converting display formats to strftime formats
    _DATE_FORMAT_MAP = {
        "YYYY-MM-DD_HHMMSS": "%Y-%m-%d_%H%M%S",
        "YYYYMMDD_HHMMSS": "%Y%m%d_%H%M%S",
        "DD-MM-YYYY_HHMMSS": "%d-%m-%Y_%H%M%S",
        "YYYY-MM-DD": "%Y-%m-%d",
        "YYYYMMDD": "%Y%m%d"
    }
    
    def _format_date(self, date: datetime, format_str: str) -> str:
        """Format date according to selected format.
        
        Args:
            date: Date to format
            format_str: Format string from DATE_FORMATS
            
        Returns:
            str: Formatted date string using the corresponding strftime format
        """
        default_format = "%Y-%m-%d_%H%M%S"
        strftime_format = self._DATE_FORMAT_MAP.get(format_str, default_format)
        return date.strftime(strftime_format)

    def rename_files(self) -> None:
        """Rename selected files based on chosen options and patterns.
        
        This method handles all renaming operations including:
        - Prefix/suffix addition and removal
        - Case changes
        - Complete name replacement
        - Date-based renaming
        - Metadata-based renaming
        """
        new_text = self.nameEdit.text()
        if not self._should_perform_rename(new_text):
            return

        for filename in self._selected_files:
            if not self._current_dir or not filename:
                continue
                
            old_path = os.path.join(self._current_dir, filename)
            name, ext = os.path.splitext(filename)
            new_name = self._generate_new_name(name, new_text, old_path)
            
            if new_name:
                self._perform_file_rename(old_path, new_name + ext)

        self._clear_selection()
        self._update_file_list()

    def _should_perform_rename(self, new_text: str) -> bool:
        """Check if renaming operation should proceed.
        
        Args:
            new_text: New text to be used in renaming
            
        Returns:
            bool: True if renaming should proceed
        """
        return bool(new_text or any([
            self.lowerCaseRadio.isChecked(),
            self.radioButton.isChecked(),
            self.metadataRadio.isChecked()
        ]))

    def _generate_new_name(
        self,
        name: str,
        new_text: str,
        file_path: str
    ) -> Optional[str]:
        """Generate new filename based on selected options.
        
        Args:
            name: Original filename without extension
            new_text: New text to be used in renaming
            file_path: Full path to the file
            
        Returns:
            Optional[str]: New filename or None if unchanged
        """
        if self.metadataRadio.isChecked():
            return self._format_date(
                self._get_metadata_date(file_path),
                self.metadataFormatCombo.currentText()
            )
            
        elif self.addPrefixRadio.isChecked():
            return f"{new_text}{name}"
            
        elif self.removePrefixRadio.isChecked() and name.startswith(new_text):
            return name[len(new_text):]
            
        elif self.addSuffixRadio.isChecked():
            return f"{name}{new_text}"
            
        elif self.removeSuffixRadio.isChecked() and name.endswith(new_text):
            return name[:-len(new_text)]
            
        elif self.newNameRadio.isChecked():
            return new_text
            
        elif self.lowerCaseRadio.isChecked():
            return name.lower()
            
        elif self.radioButton.isChecked():
            return name.upper()
            
        elif self.adddateprefixRadio.isChecked():
            return f"{self._get_formatted_mtime(file_path)}_{name}"
            
        elif self.adddatesuffixRadio.isChecked():
            return f"{name}_{self._get_formatted_mtime(file_path)}"
            
        return None

    def _get_formatted_mtime(self, file_path: str) -> str:
        """Get formatted modification time of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Formatted date string (YYYYMMDD)
        """
        mtime = os.path.getmtime(file_path)
        return time.strftime('%Y%m%d', time.localtime(mtime))

    def _perform_file_rename(self, old_path: str, new_filename: str) -> None:
        """Perform the actual file rename operation.
        
        Args:
            old_path: Current path of the file
            new_filename: New filename (including extension)
        """
        if not self._current_dir:
            return
            
        new_path = os.path.join(self._current_dir, new_filename)
        if old_path != new_path and os.path.isfile(old_path):
            shutil.move(old_path, new_path)

    def _clear_selection(self) -> None:
        """Clear the current selection after renaming."""
        self._selected_files.clear()
        self._selection_model.clear()


def main():
    """main."""
    app = QApplication(sys.argv)
    window = FileRenamerWindow()
    window.show()
    sys.exit(app.exec_())


# Make sure main() is only called when the script is run directly
if __name__ == "__main__":
    main()
