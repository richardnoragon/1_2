# Import the os module
import os
import sys
# import qt modules
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5 import uic

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


class MyGUI(QMainWindow):
    # initialize the GUI
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
        self.directory = QFileDialog.getExistingDirectory(
            self, "Select Directory")
        for file in os.listdir(self.directory):
            if os.path.isfile(os.path.join(self.directory, file)):
                self.listModel.appendRow(QStandardItem(file))
        self.output_ListView.setModel(self.listModel)

    # method size_analyzer, returns the selected diretory,
    # total number of files, total number of folders,
    # total size of selection and average file and folder size
    # for the selected directory and displays them in
    # size_analyzer_output_ListView

    def size_analyzer(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # get the list of files and folders in the directory
            files = os.listdir(directory)
            # initialize the variables
            total_size = 0
            total_files = 0
            total_folders = 0
            # iterate through the list of files and folders
            for file in files:
                # get the full path of the file
                file_path = os.path.join(directory, file)
                # check if the file is a directory
                if os.path.isdir(file_path):
                    # increment the total folders
                    total_folders += 1
                else:
                    # increment the total files
                    total_files += 1
                    # get the size of the file
                    file_size = os.path.getsize(file_path)
                    # increment the total size
                    total_size += file_size
            # calculate the average file size
            average_file_size = total_size / total_files
            # calculate the average folder size
            average_folder_size = total_size / total_folders
            # create a list of strings to display in the GUI
            output = [f'Directory: {directory}', f'Total files: {total_files}', f'Total folders: {total_folders}',
                      f'Total size: {total_size}', f'Average file size: {average_file_size}',
                      f'Average folder size: {average_folder_size}']
            # display the list in the GUI
            self.output_ListView.setModel(QStandardItemModel())
            for item in output:
                self.output_ListView.model().appendRow(QStandardItem(item))
        else:
            # display an error message
            self.output_ListView.setModel(QStandardItemModel())
            self.output_ListView.model().appendRow(
                QStandardItem('Directory does not exist'))

    # close the GUI

    def close(self) -> bool:
        return super().close()


# show GUI
app = QApplication(sys.argv)
gui = MyGUI()
gui.show()
sys.exit(app.exec_())
