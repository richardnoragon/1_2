# Import the os module
import os
import sys
import datetime
from typing import Optional, List

# Import QT modules
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import show_error_dialog, show_info_dialog, get_existing_directory

# Import Crypt modules
from cryptography.fernet import Fernet


class EnAndDecryptGUI(BaseWindow):
    """A class that handles encryption/decryption GUI."""
    
    ENCRYPTED_EXTENSION: str = '.encrypted'
    KEY_EXTENSION: str = '.key'
    
    def __init__(self) -> None:
        """Initialize the encryption/decryption GUI."""
        super().__init__()
        # load the GUI
        uic.loadUi('en_and_decrypt.ui', self)
        self.show()

        self.directory: str = "."
        self.listModel: QStandardItemModel = QStandardItemModel()
        self.selectModel: QStandardItemModel = QStandardItemModel()
        self.current_key: Optional[bytes] = None

        # Connect signals
        self.actionselectfile.triggered.connect(self.load_file)
        self.actionselectfolder.triggered.connect(self.load_directory)
        self.actionexit.triggered.connect(self.close)
        self.decrypt_PushButton.clicked.connect(self.decrypt_file)
        self.encrypt_PushButton.clicked.connect(self.encrypt_file)
        self.generate_key_PushButton.clicked.connect(self.generate_key)
        self.load_key_PushButton.clicked.connect(self.load_key)

        # Setup UI
        self.select_ListView.setModel(self.listModel)
        # The same ListView is used for both file list and messages
        # We'll use it for messages in add_message method

    def load_file(self) -> None:
        """Load a single file for encryption/decryption."""
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.directory = file_path
            self.listModel.clear()
            self.listModel.appendRow(
                QStandardItem(os.path.basename(file_path))
            )
            self.add_message(f"File loaded: {os.path.basename(file_path)}")

    def load_directory(self) -> None:
        """Load a directory for batch operations."""
        directory = get_existing_directory(self, "Select Directory")
        if directory:
            self.directory = str(directory)
            self.listModel.clear()
            
            files: List[str] = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if not filename.endswith(self.ENCRYPTED_EXTENSION):
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(
                            file_path, directory
                        )
                        files.append(relative_path)
            
            for file_path in sorted(files):
                self.listModel.appendRow(QStandardItem(file_path))
            
            self.add_message(f"Directory loaded: {len(files)} files found")

    def generate_key(self) -> None:
        """Generate a new encryption key."""
        try:
            key: bytes = Fernet.generate_key()
            
            # Save key to file
            timestamp: str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            key_filename: str = f"key_{timestamp}{self.KEY_EXTENSION}"
            key_path: str
            key_path, _ = QFileDialog.getSaveFileName(
                self, "Save Key", key_filename, "Key Files (*.key)"
            )
            
            if key_path:
                with open(key_path, 'wb') as key_file:
                    key_file.write(key)
                
                self.current_key = key
                msg = f"Key generated and saved: {os.path.basename(key_path)}"
                self.add_message(msg)
            else:
                self.current_key = key
                self.add_message("Key generated (not saved to file)")
                
        except Exception as e:
            error_msg: str = f"Failed to generate key: {str(e)}"
            show_error_dialog(self, "Error", error_msg)

    def load_key(self) -> None:
        """Load an existing encryption key."""
        try:
            key_path: str
            key_path, _ = QFileDialog.getOpenFileName(
                self, "Load Key", "", "Key Files (*.key)"
            )
            
            if key_path:
                with open(key_path, 'rb') as key_file:
                    self.current_key = key_file.read()
                
                self.add_message(f"Key loaded: {os.path.basename(key_path)}")
            else:
                self.add_message("No key selected")
                
        except Exception as e:
            error_msg: str = f"Failed to load key: {str(e)}"
            show_error_dialog(self, "Error", error_msg)

    def encrypt_file(self) -> None:
        """Encrypt the selected file(s)."""
        if not self.current_key:
            error_msg: str = "Please generate or load a key first"
            show_error_dialog(self, "Error", error_msg)
            return

        try:
            fernet: Fernet = Fernet(self.current_key)
            
            if os.path.isfile(self.directory):
                # Single file
                self._encrypt_single_file(self.directory, fernet)
            else:
                # Directory - encrypt all files
                self._encrypt_directory(self.directory, fernet)
                
        except Exception as e:
            error_msg: str = f"Encryption failed: {str(e)}"
            show_error_dialog(self, "Error", error_msg)

    def decrypt_file(self) -> None:
        """Decrypt the selected file(s)."""
        if not self.current_key:
            error_msg: str = "Please generate or load a key first"
            show_error_dialog(self, "Error", error_msg)
            return

        try:
            fernet: Fernet = Fernet(self.current_key)
            
            if os.path.isfile(self.directory):
                # Single file
                self._decrypt_single_file(self.directory, fernet)
            else:
                # Directory - decrypt all .encrypted files
                self._decrypt_directory(self.directory, fernet)
                
        except Exception as e:
            error_msg: str = f"Decryption failed: {str(e)}"
            show_error_dialog(self, "Error", error_msg)

    def _encrypt_single_file(self, file_path: str, fernet: Fernet) -> None:
        """Encrypt a single file."""
        if file_path.endswith(self.ENCRYPTED_EXTENSION):
            self.add_message("File already encrypted")
            return

        encrypted_path: str = file_path + self.ENCRYPTED_EXTENSION
        
        with open(file_path, 'rb') as infile:
            with open(encrypted_path, 'wb') as outfile:
                data: bytes = infile.read()
                encrypted_data: bytes = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        self.add_message(f"File encrypted: {os.path.basename(file_path)}")

    def _decrypt_single_file(self, file_path: str, fernet: Fernet) -> None:
        """Decrypt a single file."""
        if not file_path.endswith(self.ENCRYPTED_EXTENSION):
            self.add_message("File is not encrypted")
            return

        decrypted_path: str = file_path.replace(self.ENCRYPTED_EXTENSION, '')
        
        with open(file_path, 'rb') as infile:
            with open(decrypted_path, 'wb') as outfile:
                encrypted_data: bytes = infile.read()
                decrypted_data: bytes = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        self.add_message(f"File decrypted: {os.path.basename(file_path)}")

    def _encrypt_directory(self, directory: str, fernet: Fernet) -> None:
        """Encrypt all files in a directory."""
        encrypted_count: int = 0
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if not filename.endswith(self.ENCRYPTED_EXTENSION):
                    file_path: str = os.path.join(root, filename)
                    try:
                        self._encrypt_single_file(file_path, fernet)
                        encrypted_count += 1
                    except Exception as e:
                        msg: str = f"Failed to encrypt {filename}: {str(e)}"
                        self.add_message(msg)
        
        msg: str = f"Directory encryption complete: {encrypted_count} files"
        self.add_message(msg)

    def _decrypt_directory(self, directory: str, fernet: Fernet) -> None:
        """Decrypt all .encrypted files in a directory."""
        decrypted_count: int = 0
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(self.ENCRYPTED_EXTENSION):
                    file_path: str = os.path.join(root, filename)
                    try:
                        self._decrypt_single_file(file_path, fernet)
                        decrypted_count += 1
                    except Exception as e:
                        msg: str = f"Failed to decrypt {filename}: {str(e)}"
                        self.add_message(msg)
        
        msg: str = f"Directory decryption complete: {decrypted_count} files"
        self.add_message(msg)

    def add_message(self, message: str) -> None:
        """Add a message to the message list."""
        self.selectModel.appendRow(QStandardItem(message))


def main() -> None:
    """Main function to run the encryption/decryption GUI."""
    app: QApplication = QApplication(sys.argv)
    _: EnAndDecryptGUI = EnAndDecryptGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
