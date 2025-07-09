# Import the os module
import os
import sys

# import qt modules
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic

from gui.common.base_window import BaseWindow
from gui.common.dialogs import get_existing_directory

# create a GUI class, inherits from QMainWindow
# GUI has two menu items, select directory and exit.
# On menu item select directory, a dialog box opens
# to select a directory. The selected directory is
# displayed in select_directory_lineEdit. On menu item
# exit, the GUI closes. The GUI has a button size_analyzer_button
# and a list view size_analyzer_output_ListView. On clicking
# the button size_analyzer_button, the method size_analyzer
# is called. The method size_analyzer returns the selected
# diretory, total number of files, total number of folders,
# total size of selection and average file and folder size
# for the selected directory and displays them in
# size_analyzer_output_ListView


class SizeAnalyzerWindow(BaseWindow):
    """Main window for the Size Analyzer tool."""
    def __init__(self):
        super().__init__()
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct absolute path to the UI file
        ui_file = os.path.join(script_dir, 'size_analyzer.ui')
        # load the GUI with absolute path
        uic.loadUi(ui_file, self)
        self.show()

        self.directory = "."
        self.listModel = QStandardItemModel()
        self.selectModel = QStandardItemModel()

        # self.selectView.setModel(self.selectModel)
        self.selected = []

        self.actionselect.triggered.connect(self.load_directory)
        self.actionexit.triggered.connect(self.close)
        self.size_analyzer_button.clicked.connect(self.size_analyzer)

    def load_directory(self):
        """Load files from selected directory into the view."""
        self.directory = get_existing_directory(self, "Select Directory")
        if self.directory:
            self.listModel.clear()
            dir_path = str(self.directory)
            for file in os.listdir(dir_path):
                full_path = os.path.join(dir_path, file)
                if os.path.isfile(full_path):
                    self.listModel.appendRow(QStandardItem(file))
            self.output_ListView.setModel(self.listModel)

    def size_analyzer(self):
        """Analyze the selected directory and display statistics.
        
        Returns:
            - Total number of files
            - Total number of folders
            - Total size of selection
            - Average file and folder size
        """
        if not self.directory:
            self.output_ListView.setModel(QStandardItemModel())
            self.output_ListView.model().appendRow(
                QStandardItem('Please select a directory first'))
            return

        dir_path = str(self.directory)
        if not os.path.exists(dir_path):
            self.output_ListView.setModel(QStandardItemModel())
            self.output_ListView.model().appendRow(
                QStandardItem('Directory does not exist'))
            return

        # Initialize counters
        total_size = 0
        total_files = 0
        total_folders = 0

        # Count files and folders
        for file in os.listdir(dir_path):
            full_path = os.path.join(dir_path, file)
            if os.path.isdir(full_path):
                total_folders += 1
            else:
                total_files += 1
                total_size += os.path.getsize(full_path)

        # Calculate averages
        # Calculate averages with safe division
        if total_files > 0:
            avg_file_size = total_size / total_files
        else:
            avg_file_size = 0

        if total_folders > 0:
            avg_folder_size = total_size / total_folders
        else:
            avg_folder_size = 0

        # Create output list
        output = [
            f'Directory: {dir_path}',
            f'Total files: {total_files}',
            f'Total folders: {total_folders}',
            f'Total size: {total_size:,} bytes',
            f'Average file size: {avg_file_size:,.2f} bytes',
            f'Average folder size: {avg_folder_size:,.2f} bytes'
        ]

        # Display the results
        self.output_ListView.setModel(QStandardItemModel())
        for item in output:
            self.output_ListView.model().appendRow(QStandardItem(item))

    # close the GUI

    def close(self) -> bool:
        return super().close()


# show GUI
app = QApplication(sys.argv)
window = SizeAnalyzerWindow()
window.show()
sys.exit(app.exec_())
