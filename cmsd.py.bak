import os
import shutil
import re
import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5 import uic


class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("cmsd.ui", self)
        self.show()

        self.directory = "."
        self.listModel = QStandardItemModel()
        self.selectModel = QStandardItemModel()

        self.selectView.setModel(self.selectModel)
        self.selected = []

        self.actionOpenLeft.triggered.connect(self.load_directory_left)
        self.actionOpenRight.triggered.connect(self.load_directory_right)
        self.actionexit.triggered.connect(self.close)
        # self.filterButton.clicked.connect(self.filter_list)
        # self.selectButton.clicked.connect(self.choose_selection)
        # self.removeButton.clicked.connect(self.remove_selection)
        # self.applyButton.clicked.connect(self.rename_files)

    def load_directory_left(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        for file in os.listdir(self.directory):
            if os.path.isfile(os.path.join(self.directory, file)):
                self.listModel.appendRow(QStandardItem(file))
        self.listView.setModel(self.listModel)

    def load_directory_right(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        for file in os.listdir(self.directory):
            if os.path.isfile(os.path.join(self.directory, file)):
                self.listModel.appendRow(QStandardItem(file))
        self.listView.setModel(self.listModel)

    def close(self) -> bool:
        return super().close()


app = QApplication(sys.argv)
gui = MyGUI()
gui.show()
sys.exit(app.exec_())
