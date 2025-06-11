# import os, sys and pathlib
import os
import sys
import pathlib
import datetime
import docx  # for Word documents
import PyPDF2  # for PDF files
import chardet  # for detecting text file encoding

# Get the directory containing the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# import qt modules
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QHeaderView
)
from PyQt5.QtCore import QDate, Qt, QUrl
from PyQt5 import uic
from log_manager import LogManager

# a class FilePermissionsGUI, inherits from QMainWindow
# FileFinderGUI has one menu item, Exit. when the select_pushbutton is pressed
# a file dialog will be opened and the user can select a directory.
# when officecheckBox is box is selected, pptx, will be searched for
# when the mediacheckBox is selected, avi, mp3, mkv will be searched for
# when the allcheckBox is selected all file types will be searched for
# when the searchpushButton is pressed, the results of the search will be
# displayed in the ListViewBox.
# when the file is seleted from the ListViewBox, the metainformation will
# be displayed in the line boxes and the content will be rendered in ?Box.
# with a double click on the file name, the file will be opened with the
# installed and reqisted program.
# the search will return the results between the dates seleted in from_dateEdit and till_dateEdit.
# furthermore, depending on the created_radioButton, modified_radioButoon or created_modified_radioButton
# the files will be filtered. if no date is selected, then all files will be showen


class FileFinderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # load the GUI's UI definition from the XML file
        uic.loadUi(os.path.join(SCRIPT_DIR, 'file_finder.ui'), self)
        
        self.logger = LogManager().get_logger('FileFinder')
        self.logger.info('Initializing File Finder')
        
        # create a model for the listview
        self.model = QStandardItemModel()
        # set the model for the listview
        self.listView.setModel(self.model)
        
        # create a model for the metadata table
        self.meta_model = QStandardItemModel()
        self.meta_model.setHorizontalHeaderLabels(["Property", "Value"])
        self.meta_info_tableView.setModel(self.meta_model)
        self.meta_info_tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # connect the menu item Exit with the method exit
        self.actionexit.triggered.connect(self.close)
        # connect the select button to open directory dialog
        self.select_pushButton.clicked.connect(self.select_directory)
        # connect the push button search_Pushbutton
        # with the method search
        self.search_pushButton.clicked.connect(self.search)
        # connect double-click on list item to open file
        self.listView.doubleClicked.connect(self.open_file)
        # connect single-click on list item to show metadata
        self.listView.clicked.connect(self.show_metadata)
        
        # Set today as default for till_dateEdit
        today = QDate.currentDate()
        self.till_dateEdit.setDate(today)
        
        # Set 30 days ago as default for from_dateEdit
        thirty_days_ago = today.addDays(-30)
        self.from_dateEdit.setDate(thirty_days_ago)
        
        # Add directory and filetype attributes
        self.directory = ""
        self.filetype = ""
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.directory_lineEdit.setAcceptDrops(True)
        
        # show the GUI
        self.show()
        
    def select_directory(self):
        # Open a dialog to select a directory
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        # Display the selected directory in window title and line edit
        if dir_path:
            self.directory = dir_path
            self.setWindowTitle(f"File Finder - {self.directory}")
            self.directory_lineEdit.setText(self.directory)
            
    # Method to open a file when double-clicked in the listview
    def open_file(self, index):
        try:
            # Get the file name from the model
            file_name = self.model.itemFromIndex(index).text()
            # Create the full path
            file_path = os.path.join(self.directory, file_name)
            # Open the file with the default application
            os.startfile(file_path)
        except Exception as e:
            self.statusbar.showMessage(f"Error opening file: {str(e)}", 5000)
            self.logger.error(f'Error opening file: {str(e)}', exc_info=True)

    # Method to show metadata when a file is selected
    def show_metadata(self, index):
        try:
            # Clear previous metadata
            self.meta_model.removeRows(0, self.meta_model.rowCount())
            
            # Get the file name from the model
            file_name = self.model.itemFromIndex(index).text()
            # Create the full path
            file_path = os.path.join(self.directory, file_name)
            # Get file info
            file_info = pathlib.Path(file_path)
            
            # Add metadata to the table
            self.add_meta_row("Name", file_info.name)
            self.add_meta_row("Size", f"{file_info.stat().st_size:,} bytes")
            self.add_meta_row("Created", datetime.datetime.fromtimestamp(file_info.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S'))
            self.add_meta_row("Modified", datetime.datetime.fromtimestamp(file_info.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'))
            self.add_meta_row("Type", file_info.suffix)
            self.add_meta_row("Path", str(file_info.parent))
            
            # Show success message
            self.statusbar.showMessage(f"Metadata loaded for {file_name}", 3000)
            self.logger.info(f'Metadata loaded for {file_name}')
        except Exception as e:
            self.statusbar.showMessage(f"Error loading metadata: {str(e)}", 5000)
            self.logger.error(f'Error loading metadata: {str(e)}', exc_info=True)
            
    def add_meta_row(self, property_name, value):
        """Helper method to add a row to the metadata table"""
        row = self.meta_model.rowCount()
        self.meta_model.setItem(row, 0, QStandardItem(property_name))
        self.meta_model.setItem(row, 1, QStandardItem(str(value)))

    # Method search, first evalutaes which check boxes has
    # been seleted, then when search_pushButton is selected,
    # the results will be showen in Listview. the metainformation will
    # be displayed in the line boxes and the content will be rendered in ?Box.
    # with a double click on the file name, the file will be opened with the
    # installed and reqisted program.
    def search(self):
        # clear the model
        self.model.clear()
        self.meta_model.removeRows(0, self.meta_model.rowCount())
        
        # Use the directory from select_directory method
        directory = self.directory
        if not directory:
            self.statusbar.showMessage("Please select a directory first", 5000)
            self.logger.warning('No directory selected')
            return
            
        # Get the filetype from user input or use empty string
        filetype = self.filetype if hasattr(self, 'filetype') else ""
        # get the from date from the dateEdit
        from_date = self.from_dateEdit.date().toPyDate()
        # get the till date from the dateEdit
        till_date = self.till_dateEdit.date().toPyDate()
        # get the created_radioButton
        created = self.created_radioButton.isChecked()
        # get the modified_radioButton
        modified = self.modified_radioButton.isChecked()
        # get the created_modified_radioButton
        created_modified = self.created_modified_radioButton.isChecked()
        # get the officecheckBox - fix typo in variable name
        office = self.office_checkBox.isChecked()
        # get the mediacheckBox
        media = self.media_checkBox.isChecked()
        # get the allcheckBox
        all_files = self.all_checkBox.isChecked()
        
        # get the selected files
        self.logger.info(f'Starting search in {directory} with filetype {filetype}')
        files = self.get_files(directory, filetype, from_date, till_date,
                               created, modified, created_modified, office, media, all_files)
                               
        # add the files to the model
        for file in files:
            self.model.appendRow(QStandardItem(file))
            
        # Update status bar with results
        self.statusbar.showMessage(f"Found {len(files)} files", 5000)
        self.logger.info(f'Found {len(files)} files')

    def search_file_content(self, file_path, search_text):
        """Search for text content within a file based on its type"""
        if not search_text:
            return True  # If no search text, include the file
            
        try:
            ext = file_path.suffix.lower()
            if ext in ['.txt', '.py', '.md', '.json', '.xml', '.csv']:
                return self.search_text_file(file_path, search_text)
            elif ext in ['.docx']:
                return self.search_word_document(file_path, search_text)
            elif ext in ['.pdf']:
                return self.search_pdf_document(file_path, search_text)
            return False  # Unsupported file type
        except Exception as e:
            self.statusbar.showMessage(f"Error searching in {file_path.name}: {str(e)}", 5000)
            self.logger.error(f'Error searching in {file_path.name}: {str(e)}', exc_info=True)
            return False

    def search_text_file(self, file_path, search_text):
        """Search within text-based files"""
        try:
            # Detect the file encoding
            with open(file_path, 'rb') as raw_file:
                result = chardet.detect(raw_file.read())
                encoding = result['encoding'] if result['encoding'] else 'utf-8'

            # Read and search the file
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read().lower()
                return search_text.lower() in content
        except Exception:
            return False

    def search_word_document(self, file_path, search_text):
        """Search within Word documents"""
        try:
            doc = docx.Document(file_path)
            text_content = ' '.join([paragraph.text for paragraph in doc.paragraphs])
            return search_text.lower() in text_content.lower()
        except Exception:
            return False

    def search_pdf_document(self, file_path, search_text):
        """Search within PDF documents"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ''
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
                return search_text.lower() in text_content.lower()
        except Exception:
            return False

    # Method get_files, returns a list of files in the directory
    # that match the file type and the date range
    def get_files(
        self, directory, filetype, from_date, till_date, created, 
        modified, created_modified, office, media, all_files
    ):
        files = []
        path = pathlib.Path(directory)
        search_text = self.content_search_lineEdit.text().strip()
        
        # Convert Python date to timestamp for comparison
        from_timestamp = (
            datetime.datetime.combine(from_date, datetime.time.min).timestamp()
        )
        till_timestamp = (
            datetime.datetime.combine(till_date, datetime.time.max).timestamp()
        )
        
        try:
            self.statusbar.showMessage("Searching files...", 0)
            self.logger.info('Searching files...')
            
            for file in path.rglob('*'):
                if file.is_file():
                    if filetype in file.name:
                        if self.in_date_range(
                            file, from_timestamp, till_timestamp,
                            created, modified, created_modified
                        ):
                            ext = file.suffix.lower()
                            is_office = (
                                office and ext in ['.pptx', '.docx', '.xlsx']
                            )
                            is_media = (
                                media and ext in [
                                    '.avi', '.mp3', '.mkv', '.mp4', '.wav', '.mov'
                                ]
                            )
                            
                            if is_office or is_media or all_files:
                                if (search_text and 
                                    not self.search_file_content(file, search_text)):
                                    continue
                                
                                files.append(str(file.relative_to(path)))
            
            files.sort()
            msg = f"Found {len(files)} matching files"
            self.statusbar.showMessage(msg, 5000)
            self.logger.info(msg)
            
        except Exception as e:
            msg = f"Error searching files: {str(e)}"
            self.statusbar.showMessage(msg, 5000)
            self.logger.error(msg, exc_info=True)
            
        return files

    # Method in_date_range, returns True if the file is in the date range
    # otherwise False
    def in_date_range(
        self, file, from_timestamp, till_timestamp,
        created, modified, created_modified
    ):
        try:
            if created:
                return from_timestamp <= file.stat().st_ctime <= till_timestamp
            elif modified:
                return from_timestamp <= file.stat().st_mtime <= till_timestamp
            elif created_modified:
                c_time = file.stat().st_ctime
                m_time = file.stat().st_mtime
                return (
                    (from_timestamp <= c_time <= till_timestamp) or
                    (from_timestamp <= m_time <= till_timestamp)
                )
            else:
                return True
        except Exception:
            return False

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            # Use the first dropped item's path
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.directory = path
                self.directory_lineEdit.setText(path)
                self.setWindowTitle(f"File Finder - {self.directory}")
            else:
                self.statusbar.showMessage("Please drop a folder", 3000)


# show GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = FileFinderGUI()
    gui.show()
    sys.exit(app.exec_())
