import os
import shutil
import sys
import time
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen._file import File as MutagenFile
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import (
    show_error_dialog,
    show_info_dialog,
    get_existing_directory
)


class MyGUI(BaseWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        try:
            # Use absolute path to UI file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ui_file = os.path.join(current_dir, "rename.ui")
            if not os.path.exists(ui_file):
                raise FileNotFoundError(f"UI file not found: {ui_file}")
            
            # Add error handling for UI loading
            try:
                with open(ui_file, 'r', encoding='utf-8') as f:
                    ui_content = f.read()
                    if not ui_content:
                        raise ValueError("UI file is empty")
            except Exception as e:
                raise Exception(f"Failed to read UI file: {str(e)}")

            uic.loadUi(ui_file, self)
            self.show()
            
            self.directory = "."
            self.listModel = QStandardItemModel()
            self.selectModel = QStandardItemModel()
            
            self.selectView.setModel(self.selectModel)
            self.selected = []
            
            # Setup metadata format combo box
            self.metadataFormatCombo.addItems([
                "YYYY-MM-DD_HHMMSS",
                "YYYYMMDD_HHMMSS",
                "DD-MM-YYYY_HHMMSS",
                "YYYY-MM-DD",
                "YYYYMMDD"
            ])
            
            self.actionSelect.triggered.connect(self.load_directory)
            self.actionexit.triggered.connect(self.close)
            self.filterButton.clicked.connect(self.filter_list)
            self.selectButton.clicked.connect(self.choose_selection)
            self.removeButton.clicked.connect(self.remove_selection)
            self.applyButton.clicked.connect(self.rename_files)
            
            # Initialize radio buttons
            self.addPrefixRadio.setChecked(True)
        except Exception as e:
            error_msg = f"Failed to initialize: {str(e)}"
            show_error_dialog(
                error_msg,
                title="Error",
                parent=None
            )
            sys.exit(1)

    def load_directory(self):
        self.directory = get_existing_directory(
            self, "Select Directory"
        )
        for file in os.listdir(self.directory):
            if (os.path.isfile(os.path.join(self.directory, file))):
                self.listModel.appendRow(QStandardItem(file))
        self.listView.setModel(self.listModel)

    def close(self) -> bool:
        return super().close()

    def filter_list(self):
        filter_text = self.filterEdit.text().lower()
        self.listModel.clear()
        for file in os.listdir(self.directory):
            if (os.path.isfile(os.path.join(self.directory, file)) and 
                filter_text in file.lower()):
                self.listModel.appendRow(QStandardItem(file))

    def choose_selection(self):
        indices = self.listView.selectedIndexes()
        for index in indices:
            item = self.listModel.itemFromIndex(index)
            if item and item.text() not in self.selected:
                self.selected.append(item.text())
                self.selectModel.appendRow(QStandardItem(item.text()))

    def remove_selection(self):
        indices = self.selectView.selectedIndexes()
        for index in sorted(indices, reverse=True):
            item = self.selectModel.itemFromIndex(index)
            if item:
                self.selected.remove(item.text())
                self.selectModel.removeRow(index.row())

    def get_file_metadata_date(self, filepath):
        """Extract date from file metadata based on file type."""
        try:
            # Image files (JPEG, PNG, etc.)
            if filepath.lower().endswith(
                ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
            ):
                with Image.open(filepath) as img:
                    exif = img.getexif()
                    if exif:
                        for tag_id in exif:
                            tag = TAGS.get(tag_id, tag_id)
                            if tag in ('DateTimeOriginal', 'DateTime'):
                                date_str = exif[tag_id]
                                return datetime.strptime(
                                    date_str, '%Y:%m:%d %H:%M:%S'
                                )
            
            # Audio files (MP3, FLAC, etc.)
            elif filepath.lower().endswith(('.mp3', '.flac', '.m4a', '.wav')):
                audio = MutagenFile(filepath)
                if audio:
                    if hasattr(audio, 'tags'):
                        # Try common metadata date tags
                        for tag in ('date', 'TDRC', 'year'):
                            if tag in audio.tags:
                                date_str = str(audio.tags[tag][0])
                                try:
                                    return datetime.strptime(
                                        date_str, '%Y-%m-%d'
                                    )
                                except ValueError:
                                    try:
                                        return datetime.strptime(
                                            date_str, '%Y'
                                        )
                                    except ValueError:
                                        continue

            # Fallback to file modification time
            return datetime.fromtimestamp(os.path.getmtime(filepath))
        except Exception:
            return datetime.fromtimestamp(os.path.getmtime(filepath))

    def format_date(self, date, format_str):
        """Format date according to selected format."""
        if format_str == "YYYY-MM-DD_HHMMSS":
            return date.strftime("%Y-%m-%d_%H%M%S")
        elif format_str == "YYYYMMDD_HHMMSS":
            return date.strftime("%Y%m%d_%H%M%S")
        elif format_str == "DD-MM-YYYY_HHMMSS":
            return date.strftime("%d-%m-%Y_%H%M%S")
        elif format_str == "YYYY-MM-DD":
            return date.strftime("%Y-%m-%d")
        elif format_str == "YYYYMMDD":
            return date.strftime("%Y%m%d")
        return date.strftime("%Y-%m-%d_%H%M%S")

    def rename_files(self):
        new_text = self.nameEdit.text()
        if not new_text and not any([
            self.lowerCaseRadio.isChecked(),
            self.radioButton.isChecked(),
            self.metadataRadio.isChecked()
        ]):
            return

        for filename in self.selected:
            if not self.directory or not filename:
                continue
                
            old_path = str(os.path.join(str(self.directory), filename))
            name, ext = os.path.splitext(filename)
            new_name = name

            if self.metadataRadio.isChecked():
                date = self.get_file_metadata_date(old_path)
                format_str = self.metadataFormatCombo.currentText()
                new_name = self.format_date(date, format_str)
            elif self.addPrefixRadio.isChecked():
                new_name = f"{new_text}{name}"
            elif (self.removePrefixRadio.isChecked() and
                    name.startswith(new_text)):
                new_name = name[len(new_text):]
            elif self.addSuffixRadio.isChecked():
                new_name = f"{name}{new_text}"
            elif (self.removeSuffixRadio.isChecked() and
                    name.endswith(new_text)):
                new_name = name[:-len(new_text)]
            elif self.newNameRadio.isChecked():
                new_name = new_text
            elif self.lowerCaseRadio.isChecked():
                new_name = name.lower()
            elif self.radioButton.isChecked():
                new_name = name.upper()
            elif self.adddateprefixRadio.isChecked():
                date = os.path.getmtime(old_path)
                date_str = time.strftime('%Y%m%d', time.localtime(date))
                new_name = f"{date_str}_{name}"
            elif self.adddatesuffixRadio.isChecked():
                date = os.path.getmtime(old_path)
                date_str = time.strftime('%Y%m%d', time.localtime(date))
                new_name = f"{name}_{date_str}"

            new_path = str(os.path.join(str(self.directory), new_name + ext))
            if old_path != new_path and os.path.isfile(old_path):
                shutil.move(old_path, new_path)

        # Clear selection after renaming
        self.selected.clear()
        self.selectModel.clear()
        self.load_directory()  # Refresh the file list


def main():
    app = QApplication(sys.argv)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())


# Make sure main() is only called when the script is run directly
if __name__ == "__main__":
    main()
