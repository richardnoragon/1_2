# Import Libraries
from PyQt5 import QtWidgets

from PyPDF2 import PdfReader, PdfWriter
import os
import argparse
import getpass
from io import BytesIO
import pyAesCrypt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic
import sys
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Size of chunck
BUFFER_SIZE = 64 * 1024


def is_encrypted(input_file: str) -> bool:
    """Checks if the inputted file is encrypted using PyPDF2 library"""
    try:
        with open(input_file, "rb") as f:
            pdf = PdfReader(f)
            is_enc = pdf.is_encrypted
            logger.debug(
                "Checked encryption status of %s: %s", input_file, is_enc
            )
            return is_enc
    except FileNotFoundError:
        logger.error("File not found: %s", input_file)
        QMessageBox.critical(None, "Error", f"File not found: {input_file}")
    except PermissionError:
        logger.error("Permission denied when accessing the file")
        QMessageBox.critical(
            None, "Error", "Permission denied when accessing the file"
        )
    except Exception as e:
        logger.error(
            "Error checking encryption status: %s", str(e), exc_info=True
        )
        QMessageBox.critical(
            None, "Error", f"Error checking encryption status: {str(e)}"
        )
    return False


def encrypt_pdf(input_file: str, password: str):
    """Encrypts a PDF file"""
    try:
        logger.info("Starting encryption of file: %s", input_file)
        reader = PdfReader(input_file)
        writer = PdfWriter()

        # Add all pages to the writer
        for page in reader.pages:
            writer.add_page(page)

        logger.debug("Added %d pages to writer", len(writer.pages))

        # Add a password to the PDF
        writer.encrypt(password)
        logger.debug("PDF encrypted with password")

        # Save the new PDF to a file
        output_file = input_file.replace(".pdf", "_encrypted.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)

        logger.info("File encrypted successfully: %s", output_file)
        return output_file

    except FileNotFoundError:
        logger.error("File not found: %s", input_file)
        QMessageBox.critical(None, "Error", f"File not found: %s", input_file)
    except PermissionError:
        logger.error("Permission denied when accessing the file")
        QMessageBox.critical(
            None, "Error", "Permission denied when accessing the file"
        )
    except Exception as e:
        logger.error("Error during PDF encryption: %s", str(e), exc_info=True)
        QMessageBox.critical(
            None, "Error", f"Error during PDF encryption: %s", str(e)
        )
    return None


def decrypt_pdf(input_file: str, password: str):
    """Decrypts a PDF file"""
    try:
        logger.info("Starting decryption of file: %s", input_file)
        reader = PdfReader(input_file)
        writer = PdfWriter()

        if not reader.is_encrypted:
            logger.warning("The PDF is not encrypted: %s", input_file)
            QMessageBox.warning(None, "Warning", "The PDF is not encrypted")
            return None

        try:
            reader.decrypt(password)
            logger.debug("PDF decrypted successfully with provided password")
        except Exception:
            logger.error("Incorrect password provided")
            QMessageBox.critical(None, "Error", "Incorrect password")
            return None

        # Add all pages to the writer
        for page in reader.pages:
            writer.add_page(page)

        logger.debug("Added %d pages to writer", len(writer.pages))

        # Save the new PDF to a file
        output_file = input_file.replace(".pdf", "_decrypted.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)

        logger.info("File decrypted successfully: %s", output_file)
        return output_file

    except FileNotFoundError:
        logger.error("File not found: %s", input_file)
        QMessageBox.critical(None, "Error", f"File not found: %s", input_file)
    except PermissionError:
        logger.error("Permission denied when accessing the file")
        QMessageBox.critical(
            None, "Error", "Permission denied when accessing the file"
        )
    except Exception as e:
        logger.error("Error during PDF decryption: %s", str(e), exc_info=True)
        QMessageBox.critical(
            None, "Error", f"Error during PDF decryption: %s", str(e)
        )
    return None


def cipher_stream(inp_buffer: BytesIO, password: str):
    """Ciphers an input memory buffer and returns a ciphered output memory buffer"""
    try:
        logger.debug("Starting stream encryption")
        out_buffer = BytesIO()
        pyAesCrypt.encryptStream(inp_buffer, out_buffer, password, BUFFER_SIZE)
        logger.debug("Stream encryption completed successfully")
        return out_buffer
    except Exception as e:
        logger.error(
            "Error during stream encryption: %s", str(e), exc_info=True
        )
        QMessageBox.critical(
            None, "Error", f"Error during stream encryption: %s", str(e)
        )
        return None


def decipher_file(input_file: str, output_file: str, password: str):
    """Deciphers a file"""
    try:
        logger.info(
            "Starting file decryption: %s -> %s", input_file, output_file
        )
        pyAesCrypt.decryptFile(input_file, output_file, password, BUFFER_SIZE)
        logger.info("File decryption completed successfully")
        return True
    except ValueError as e:
        logger.error("Incorrect password or corrupted file")
        QMessageBox.critical(
            None, "Error", "Incorrect password or corrupted file"
        )
    except Exception as e:
        logger.error("Error during file decryption: %s", str(e), exc_info=True)
        QMessageBox.critical(
            None, "Error", f"Error during file decryption: %s", str(e)
        )
    return False


def encrypt_decrypt_file(**kwargs):
    """Encrypts or decrypts a file"""
    try:
        input_file = kwargs.get("input_file")
        password = kwargs.get("password")
        action = kwargs.get("action", "encrypt")
        level = kwargs.get("level", 1)

        if not input_file or not os.path.exists(input_file):
            logger.error("Input file does not exist: %s", input_file)
            QMessageBox.critical(
                None, "Error", f"Input file does not exist: %s", input_file
            )
            return False

        if not password:
            logger.error("Password is required")
            QMessageBox.critical(None, "Error", "Password is required")
            return False

        logger.info(
            "Processing file %s with action=%s, level=%d",
            input_file,
            action,
            level,
        )

        if action == "encrypt":
            if level == 1:
                output_file = encrypt_pdf(input_file, password)
                return output_file is not None
            else:
                # Level 2: Encrypt PDF + AES
                pdf_output = encrypt_pdf(input_file, password)
                if pdf_output:
                    try:
                        logger.debug("Starting level 2 encryption")
                        with open(pdf_output, "rb") as f:
                            inp_buffer = BytesIO(f.read())
                        out_buffer = cipher_stream(inp_buffer, password)
                        if out_buffer:
                            final_output = input_file.replace(
                                ".pdf", "_encrypted_l2.pdf"
                            )
                            with open(final_output, "wb") as f:
                                f.write(out_buffer.getvalue())
                            os.remove(pdf_output)  # Remove intermediate file
                            logger.info(
                                "Level 2 encryption completed successfully"
                            )
                            return True
                    except Exception as e:
                        logger.error(
                            "Error during level 2 encryption: %s",
                            str(e),
                            exc_info=True,
                        )
                        QMessageBox.critical(
                            None,
                            "Error",
                            f"Error during level 2 encryption: %s",
                            str(e),
                        )
                return False
        else:  # decrypt
            if level == 1:
                output_file = decrypt_pdf(input_file, password)
                return output_file is not None
            else:
                # Level 2: Decrypt AES + PDF
                try:
                    logger.debug("Starting level 2 decryption")
                    temp_file = input_file.replace(".pdf", "_temp.pdf")
                    if decipher_file(input_file, temp_file, password):
                        decrypted = decrypt_pdf(temp_file, password)
                        os.remove(temp_file)  # Clean up temp file
                        logger.info(
                            "Level 2 decryption completed successfully"
                        )
                        return decrypted is not None
                    return False
                except Exception as e:
                    logger.error(
                        "Error during level 2 decryption: %s",
                        str(e),
                        exc_info=True,
                    )
                    QMessageBox.critical(
                        None,
                        "Error",
                        f"Error during level 2 decryption: %s",
                        str(e),
                    )
                    return False
    except Exception as e:
        logger.error(
            "Unexpected error during operation: %s", str(e), exc_info=True
        )
        QMessageBox.critical(
            None, "Error", f"Unexpected error during operation: %s", str(e)
        )
        return False


class Password(argparse.Action):
    """
    Hides the password entry
    """

    def __call__(self, parser, namespace, values, option_string):
        if values is None:
            values = getpass.getpass()
        setattr(namespace, self.dest, values)


def is_valid_path(path):
    """Validates the path inputted and checks whether it is a file path or a folder path"""
    if not path:
        raise ValueError(f"Invalid Path")
    if os.path.isfile(path):
        return path
    elif os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid Path %s", path)


def parse_args():
    """Get user command line parameters"""
    parser = argparse.ArgumentParser(description="These options are available")
    parser.add_argument(
        "file", help="Input PDF file you want to encrypt", type=is_valid_path
    )
    # parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path,
    #                     required=True, help="Enter the path of the file or the folder to process")
    parser.add_argument(
        "-a",
        "--action",
        dest="action",
        choices=["encrypt", "decrypt"],
        type=str,
        default="encrypt",
        help="Choose whether to encrypt or to decrypt",
    )
    parser.add_argument(
        "-l",
        "--level",
        dest="level",
        choices=[1, 2],
        type=int,
        default=1,
        help="Choose which protection level to apply",
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        action=Password,
        nargs="?",
        type=str,
        required=True,
        help="Enter a valid password",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        dest="output_file",
        type=str,
        help="Enter a valid output file",
    )
    args = vars(parser.parse_args())
    # To Display Command Arguments Except Password
    print(
        "## Command Arguments #################################################"
    )
    print(
        "\n".join(
            "{}:{}".format(i, j) for i, j in args.items() if i != "password"
        )
    )
    print(
        "######################################################################"
    )
    return args


class EncryptUI(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            logger.info("Initializing Encrypt UI")
            uic.loadUi("encrypt.ui", self)

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.encryptButton.clicked.connect(self.handle_encrypt)
            self.decryptButton.clicked.connect(self.handle_decrypt)
            self.actionExit.triggered.connect(self.close)

            logger.debug("UI signals connected successfully")
        except Exception as e:
            logger.error("Failed to initialize UI: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Failed to initialize UI: %s", str(e)
            )
            self.close()

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select PDF file", "", "PDF Files (*.pdf)"
            )
            if filename:
                logger.info("Selected file: %s", filename)
                self.inputFileEdit.setText(filename)
                # Check if file is already encrypted
                if is_encrypted(filename):
                    logger.debug("File is encrypted")
                    self.encryptButton.setEnabled(False)
                    self.decryptButton.setEnabled(True)
                    self.statusBar().showMessage("File is encrypted")
                else:
                    logger.debug("File is not encrypted")
                    self.encryptButton.setEnabled(True)
                    self.decryptButton.setEnabled(False)
                    self.statusBar().showMessage("File is not encrypted")
        except Exception as e:
            logger.error("Error browsing file: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Error browsing file: %s", str(e)
            )

    def handle_encrypt(self):
        try:
            input_file = self.inputFileEdit.text()
            if not input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Error", "Please select a PDF file first!"
                )
                return

            password = self.passwordEdit.text()
            if not password:
                logger.warning("No password entered")
                QMessageBox.warning(self, "Error", "Please enter a password!")
                return

            level = self.protectionLevel.currentIndex() + 1
            logger.info("Starting encryption with level %d", level)

            self.statusBar().showMessage("Encrypting PDF...")
            QtWidgets.QApplication.processEvents()

            if encrypt_decrypt_file(
                input_file=input_file,
                password=password,
                action="encrypt",
                level=level,
            ):
                logger.info("File encrypted successfully")
                QMessageBox.information(
                    self, "Success", "File encrypted successfully!"
                )
                self.statusBar().showMessage("Encryption complete", 3000)
            else:
                logger.warning("Encryption failed")
                self.statusBar().showMessage("Encryption failed", 3000)
        except Exception as e:
            logger.error("Error during encryption: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Error during encryption: %s", str(e)
            )
            self.statusBar().showMessage("Error during encryption", 3000)

    def handle_decrypt(self):
        try:
            input_file = self.inputFileEdit.text()
            if not input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Error", "Please select a PDF file first!"
                )
                return

            password = self.passwordEdit.text()
            if not password:
                logger.warning("No password entered")
                QMessageBox.warning(self, "Error", "Please enter a password!")
                return

            level = self.protectionLevel.currentIndex() + 1
            logger.info("Starting decryption with level %d", level)

            self.statusBar().showMessage("Decrypting PDF...")
            QtWidgets.QApplication.processEvents()

            if encrypt_decrypt_file(
                input_file=input_file,
                password=password,
                action="decrypt",
                level=level,
            ):
                logger.info("File decrypted successfully")
                QMessageBox.information(
                    self, "Success", "File decrypted successfully!"
                )
                self.statusBar().showMessage("Decryption complete", 3000)
            else:
                logger.warning("Decryption failed")
                self.statusBar().showMessage("Decryption failed", 3000)
        except Exception as e:
            logger.error("Error during decryption: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Error during decryption: %s", str(e)
            )
            self.statusBar().showMessage("Error during decryption", 3000)


def main():
    try:
        logger.info("Starting Encrypt PDF application")
        app = QApplication(sys.argv)
        window = EncryptUI()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(
            "Application failed to start: %s", str(e), exc_info=True
        )
        QMessageBox.critical(
            None, "Fatal Error", f"Application failed to start: %s", str(e)
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
