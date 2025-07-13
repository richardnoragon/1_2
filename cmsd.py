import os
import shutil
import re
import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QListView,
                           QVBoxLayout, QLabel, QPushButton)
from PyQt5 import uic

from gui.common.base_window import BaseWindow
from gui.common.dialogs import get_existing_directory

from core.error_handler import error_handler



class MyGUI(BaseWindow):
    """A class that handles my g u i and inherits from BaseWindow."""
    def __init__(self):
        """init."""
        super(MyGUI, self).__init__()
        uic.loadUi("cmsd.ui", self)
        self.show()

        self.left_directory = "."
        self.right_directory = "."
        self.left_model = QStandardItemModel()
        self.right_model = QStandardItemModel()
        self.selectModel = QStandardItemModel()

        # Set up list views
        self.listView.setModel(self.left_model)
        self.selectView.setModel(self.right_model)
        self.selected = []

        # Connect menu actions
        self.actionOpenLeft.triggered.connect(self.load_directory_left)
        self.actionOpenRight.triggered.connect(self.load_directory_right)
        self.actionexit.triggered.connect(self.close)

    def load_directory_left(self):
        """Load files from selected directory into the left view."""
        directory = get_existing_directory(self, "Select Left Directory")
        if directory:
            self.left_directory = directory
            self.left_model.clear()
            dir_path = str(self.left_directory)
            for file in os.listdir(dir_path):
                full_path = os.path.join(dir_path, file)
                if os.path.isfile(full_path):
                    self.left_model.appendRow(QStandardItem(file))

    def load_directory_right(self):
        """Load files from selected directory into the right view."""
        directory = get_existing_directory(self, "Select Right Directory")
        if directory:
            self.right_directory = directory
            self.right_model.clear()
            dir_path = str(self.right_directory)
            for file in os.listdir(dir_path):
                full_path = os.path.join(dir_path, file)
                if os.path.isfile(full_path):
                    self.right_model.appendRow(QStandardItem(file))

    def close(self) -> bool:
        """close.
        Returns:
            bool: Description of value"""
        return super().close()


def main():
    """main."""
    app = QApplication(sys.argv)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
