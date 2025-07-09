# Import the os module
import os
import shutil
import sys
import datetime

# Import QT modules
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import show_error_dialog, show_info_dialog, get_existing_directory

# Import Crypt modules
import pyAesCrypt
from cryptography.fernet import Fernet

# Create a GUI class, inherits from QMainWindow.
# The menu has three options, SelectFile, SelectFolder and
# Exit. If the menu item SelectFile is selected, a system dialog where
# a file can be selected. When the file is selected,
# method check_encrytion will be called. If the file
# is encrypted, method check_encrytion will display
# message, "File already encrypted" in message_ListView. If the
# file is not encrypted, the message "File loaded" will be
# displayed in message_ListView. If the menu item SelectFolder is selected, a system dialog where
# a folder can be selected. When the folder is selected,
# method check_encrytion will be called. If the file
# is encrypted, method check_encrytion will display
# message, "Folder already encrypted" in message_ListView. If the
# folder is not encrypted, the message "Folder(s) loaded" will be
# displayed in message_ListView.


class en_and_decryptGUI(BaseWindow):
    # initialize the GUI
    def __init__(self):
        super().__init__()
        # load the GUI
        uic.loadUi('en_and_decrypt'
        '.ui', self)
        self.show()

        self.directory = "."
        self.listModel = QStandardItemModel()
        self.selectModel = QStandardItemModel()

        self.actionselectfile.triggered.connect(self.load_directory)
        self.actionselectfolder.triggered.connect(self.load_directory)
        self.actionexit.triggered.connect(self.close)
        self.decrypt_PushButton.clicked.connect(self.decrypt_file)
        self.encrypt_PushButton.clicked.connect(self.encrypt_file)
        self.generate_key_PushButton.clicked.connect(self.generate_key)
        self.load_key_PushButton.clicked.connect(self.load_key)
        # self.decrypt_folder_PushButton.clicked.connect(self.decrypt_folder)
        # self.encrypt_folder_PushButton.clicked.connect(self.encrypt_folder)

    def load_directory(self):
        self.directory = get_existing_directory(
            self, "Select Directory")
        for file in os.listdir(self.directory):
            if os.path.isfile(os.path.join(self.directory, file)):
                self.listModel.appendRow(QStandardItem(file))
        self.output_ListView.setModel(self.listModel)

    # Method generate_key, generates a random 12 character string to which the
    # current date and time will be appended. This will then be used as the key        # and will be stored in a file named with the date and time with
    # the suffix .key. Upon completion the message "Key generated" will
    # be displayed in message_ListView.

    def generate_key(self):
        # generate a random 12 character string
        key = Fernet.generate_key()
        # append current date and time to key
        key = key + str(datetime.datetime.now())
        # create a file with the suffix .key
        key_file = open(key + ".key", "wb")
        # write key to file
        key_file.write(key)
        # close file
        key_file.close()
        # display message in message_ListView
        self.message_ListView.append("Key generated")

    # Method check_encryption will be called when
    # the encrypt_PushButton is pressed. After the encrypt_PushButton has been
    # pushed, another dialog will be opened in which
    # the key_file can be searched for and selected, then
    # the method load_key will be called. Upon completion
    # the message "File successfully encrypted" will be displayed in
    # message_ListView.

    def check_encryption(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # check if the directory is encrypted
            if os.path.isfile(os.path.join(directory, "encrypted")):
                # display message in message_ListView
                self.message_ListView.append("Folder already encrypted")
            else:
                # display message in message_ListView
                self.message_ListView.append("Folder(s) loaded")
        else:
            # display message in message_ListView
            self.message_ListView.append("Folder(s) not loaded")

    # Method load_key opens a system dialog in which
    # files with the suffix .key. Upon completion the
    # message "Key loaded" will be displayed in the
    # message_ListView

    # Method encrypt_file will encrypt the selected file
    # when the encrypt_PushButton is pressed,
    # using the selected key. Upon completion the message
    # "File successfully encrypted" will be displayed in
    # the message_ListView.

    # Method decrypt_file will be called when
    # the decrypt_PushButton is pressed. After the decrypt_PushButton has been
    # pushed, another dialog will be opened in which
    # the key_file can be searched for and selected, then
    # the method load_key will be called. Upon completion
    # the message "File successfully decrypted" in
    # message_ListView.

    # Method encrypt_folder will encrypt the folder
    # using the selected key. If reursive_CheckBox
    # is triggered, the selected folder and recursive folders
    # will be encrpted. Upon completion of operation,
    # "Folder encrypted successfully." will be displayed in
    # message_ListView

    # Method decrypt_folder will be called when
    # the decrypt_PushButton is pressed. After the decrypt_PushButton has been
    # pushed, another dialog will be opened in which
    # the key_file can be searched for and selected, then
    # the method load_key will be called. Upon completion of operation,
    # "Folder decrypted successfully." will be displayed in
    # message_ListView

    # Method load_key opens a system dialog in which
    # files with the suffix .key. Upon completion the
    # message "Key loaded" will be displayed in the
    # message_ListView

    def load_key(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # check if the directory is encrypted
            if os.path.isfile(os.path.join(directory, "encrypted")):
                # display message in message_ListView
                self.message_ListView.append("Folder already encrypted")
            else:
                # display message in message_ListView
                self.message_ListView.append("Folder(s) loaded")

    # Method encrypt_file will encrypt the selected file
    # when the encrypt_PushButton is pressed,
    # using the selected key. Upon completion the message
    # "File successfully encrypted" will be displayed in
    # the message_ListView.

    def encrypt_file(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # check if the directory is encrypted
            if os.path.isfile(os.path.join(directory, "encrypted")):
                # display message in message_ListView
                self.message_ListView.append("Folder already encrypted")
            else:
                # display message in message_ListView
                self.message_ListView.append("Folder(s) loaded")

    # Method decrypt_file will be called when
    # the decrypt_PushButton is pressed. After the decrypt_PushButton has been
    # pushed, another dialog will be opened in which
    # the key_file can be searched for and selected, then
    # the method load_key will be called. Upon completion
    # the message "File successfully decrypted" in
    # message_ListView.

    def decrypt_file(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # check if the directory is encrypted
            if os.path.isfile(os.path.join(directory, "encrypted")):
                # display message in message_ListView
                self.message_ListView.append("Folder already encrypted")
            else:
                # display message in message_ListView
                self.message_ListView.append("Folder(s) loaded")

    # Method encrypt_folder will encrypt the folder
    # using the selected key. If reursive_CheckBox
    # is triggered, the selected folder and recursive folders
    # will be encrpted. Upon completion of operation,
    # "Folder encrypted successfully." will be displayed in
    # message_ListView

    def encrypt_folder(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # check if the directory is encrypted
            if os.path.isfile(os.path.join(directory, "encrypted")):
                # display message in message_ListView
                self.message_ListView.append("Folder already encrypted")
            else:
                # display message in message_ListView
                self.message_ListView.append("Folder(s) loaded")

    # Method decrypt_folder will be called when
    # the decrypt_PushButton is pressed. After the decrypt_PushButton has been
    # pushed, another dialog will be opened in which
    # the key_file can be searched for and selected, then
    # the method load_key will be called. Upon completion of operation,
    # "Folder decrypted successfully." will be displayed in
    # message_ListView

    def decrypt_folder(self):
        # get the selected directory
        directory = self.directory
        # check if the directory exists
        if os.path.exists(directory):
            # check if the directory is encrypted

            if os.path.isfile(os.path.join(directory, "encrypted")):
                # display message in message_ListView
                self.message_ListView.append("Folder already encrypted")

            else:
                # display message in message_ListView
                self.message_ListView.append("Folder(s) loaded")


def main():
    app = QApplication([])
    window = en_and_decryptGUI()
    app.exec_()


if __name__ == "__main__":
    main()
