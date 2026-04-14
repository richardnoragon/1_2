#!/usr/bin/env python3
"""
PDF Functional Integration - Connects operation engine with enhanced PDF tools widget
Replaces placeholder implementations with functional PDF operations
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from src.gui.themes import token
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QProgressDialog,
)

# Import our PDF operation components
try:
    # Import PDF extraction components
    from pdf_extraction_engine import (
        ExtractionResult,
        ExtractionType,
        PDFExtractionEngine,
    )
    from pdf_extraction_parameter_dialogs import (
        PDFImageExtractionDialog,
        PDFLinkExtractionDialog,
        PDFMetadataExtractionDialog,
        PDFTableExtractionDialog,
        PDFTextExtractionDialog,
    )
    from pdf_operation_engine import (
        OperationResult,
        OperationType,
        PDFFileManager,
        PDFOperationEngine,
        PDFValidator,
    )
    from pdf_parameter_dialogs import (
        PDFMergeDialog,
        PDFSignDialog,
        PDFSplitDialog,
    )

    # Import PDF security components
    from pdf_security_engine import (
        DigitalSignature,
        PDFSecurityEngine,
        SecurityOperation,
        SecurityResult,
        SecuritySettings,
    )
    from pdf_security_parameter_dialogs import (
        PDFDecryptionDialog,
        PDFDigitalSignatureDialog,
        PDFEncryptionDialog,
        PDFSecurityInfoDialog,
    )

    PDF_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import PDF components: {e}")
    PDF_COMPONENTS_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class PDFOperationThread(QThread):
    """Thread for executing PDF operations without blocking UI"""

    progress_updated = pyqtSignal(float, str)  # percentage, message
    operation_completed = pyqtSignal(object)  # OperationResult
    operation_failed = pyqtSignal(str)  # error message

    def __init__(self, operation_func, *args, **kwargs):
        super().__init__()
        self.operation_func = operation_func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        """Execute the PDF operation in background thread"""
        try:
            # Add progress callback to kwargs
            self.kwargs["progress_callback"] = self.progress_callback

            # Execute the operation
            self.result = self.operation_func(*self.args, **self.kwargs)

            # Emit completion signal
            self.operation_completed.emit(self.result)

        except Exception as e:
            logger.error(f"PDF operation failed in thread: {e}", exc_info=True)
            self.operation_failed.emit(str(e))

    def progress_callback(self, percentage: float, message: str):
        """Progress callback for operation updates"""
        self.progress_updated.emit(percentage, message)


class PDFProgressDialog(QProgressDialog):
    """Enhanced progress dialog for PDF operations"""

    def __init__(self, operation_name: str, parent=None):
        super().__init__(parent)
        self.operation_name = operation_name
        self.setWindowTitle(f"PDF Operation - {operation_name}")
        self.setLabelText("Initializing...")
        self.setRange(0, 100)
        self.setValue(0)
        self.setModal(True)
        self.setAutoClose(False)
        self.setAutoReset(False)

        # Style the progress dialog
        self.setStyleSheet(
            """
            QProgressDialog {
                background-color: {token('window_background')};
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QProgressBar {
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                text-align: center;
                background-color: {token('dialog_background')};
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: {token('button_primary')};
                border-radius: 3px;
            }
        """
        )

    def update_progress(self, percentage: float, message: str):
        """Update progress with percentage and message"""
        self.setValue(int(percentage))
        self.setLabelText(f"{self.operation_name}: {message}")
        QApplication.processEvents()  # Keep UI responsive


class PDFFunctionalIntegration:
    """
    Integration class that provides functional PDF operations
    to replace placeholder implementations in the enhanced PDF tools widget
    """

    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.pdf_engine = PDFOperationEngine()
        self.pdf_extraction_engine = PDFExtractionEngine()
        self.pdf_security_engine = PDFSecurityEngine()
        self.current_operation_thread = None
        self.progress_dialog = None

        # Set up logger
        self.logger = logging.getLogger(f"{__name__}.PDFFunctionalIntegration")

    def merge_pdfs_functional(self):
        """Functional PDF merge implementation"""
        try:
            self.logger.info("Starting functional PDF merge operation")

            # Show merge parameter dialog
            merge_dialog = PDFMergeDialog(self.parent_widget)
            if merge_dialog.exec_() != merge_dialog.Accepted:
                self.logger.info("PDF merge cancelled by user")
                return

            # Get parameters from dialog
            input_files = merge_dialog.get_input_files()
            output_file = merge_dialog.get_output_file()
            options = merge_dialog.get_merge_options()

            if not input_files or not output_file:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input files and output location.",
                )
                return

            # Validate input files
            self.logger.info(f"Validating {len(input_files)} input files")
            validation_results = PDFValidator.validate_multiple_files(
                input_files
            )
            invalid_files = [
                f for f, v in validation_results.items() if not v["valid_pdf"]
            ]

            if invalid_files:
                error_msg = "Invalid PDF files found:\n" + "\n".join(
                    [
                        f"• {os.path.basename(f)}: {validation_results[f].get('error', 'Unknown error')}"
                        for f in invalid_files
                    ]
                )
                QMessageBox.critical(
                    self.parent_widget, "Invalid PDF Files", error_msg
                )
                return

            # Start merge operation in background thread
            self.start_pdf_operation(
                "Merge PDFs",
                self.pdf_engine.merge_pdfs,
                input_files,
                output_file,
                options,
            )

        except Exception as e:
            self.logger.error(f"Error in merge operation: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Merge Error",
                f"Failed to start merge operation: {str(e)}",
            )

    def split_pdf_functional(self):
        """Functional PDF split implementation"""
        try:
            self.logger.info("Starting functional PDF split operation")

            # Show split parameter dialog
            split_dialog = PDFSplitDialog(self.parent_widget)
            if split_dialog.exec_() != split_dialog.Accepted:
                self.logger.info("PDF split cancelled by user")
                return

            # Get parameters from dialog
            input_file = split_dialog.get_input_file()
            output_dir = split_dialog.get_output_directory()
            options = split_dialog.get_split_options()

            if not input_file or not output_dir:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file and output directory.",
                )
                return

            # Validate input file
            self.logger.info(f"Validating input file: {input_file}")
            validation = PDFValidator.validate_pdf_file(input_file)
            if not validation["valid_pdf"]:
                QMessageBox.critical(
                    self.parent_widget,
                    "Invalid PDF File",
                    f"Invalid PDF file: {validation.get('error', 'Unknown error')}",
                )
                return

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Start split operation in background thread
            self.start_pdf_operation(
                "Split PDF",
                self.pdf_engine.split_pdf,
                input_file,
                output_dir,
                options,
            )

        except Exception as e:
            self.logger.error(f"Error in split operation: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Split Error",
                f"Failed to start split operation: {str(e)}",
            )

    def sign_pdf_functional(self):
        """Functional PDF sign implementation"""
        try:
            self.logger.info("Starting functional PDF sign operation")

            # Show sign parameter dialog
            sign_dialog = PDFSignDialog(self.parent_widget)
            if sign_dialog.exec_() != sign_dialog.Accepted:
                self.logger.info("PDF sign cancelled by user")
                return

            # Get parameters from dialog
            input_file = sign_dialog.get_input_file()
            signature_file = sign_dialog.get_signature_file()
            output_file = sign_dialog.get_output_file()
            options = sign_dialog.get_sign_options()

            if not input_file or not signature_file or not output_file:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file, signature image, and output location.",
                )
                return

            # Validate input files
            self.logger.info(f"Validating input files")
            pdf_validation = PDFValidator.validate_pdf_file(input_file)
            if not pdf_validation["valid_pdf"]:
                QMessageBox.critical(
                    self.parent_widget,
                    "Invalid PDF File",
                    f"Invalid PDF file: {pdf_validation.get('error', 'Unknown error')}",
                )
                return

            if not os.path.exists(signature_file):
                QMessageBox.critical(
                    self.parent_widget,
                    "Signature File Not Found",
                    f"Signature file not found: {signature_file}",
                )
                return

            # Start sign operation in background thread
            self.start_pdf_operation(
                "Sign PDF",
                self.pdf_engine.sign_pdf,
                input_file,
                signature_file,
                output_file,
                options,
            )

        except Exception as e:
            self.logger.error(f"Error in sign operation: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Sign Error",
                f"Failed to start sign operation: {str(e)}",
            )

    def extract_text_functional(self):
        """Functional PDF text extraction implementation"""
        try:
            self.logger.info("Starting functional PDF text extraction")

            # Show text extraction parameter dialog
            extraction_dialog = PDFTextExtractionDialog(self.parent_widget)
            if extraction_dialog.exec_() != extraction_dialog.Accepted:
                self.logger.info("PDF text extraction cancelled by user")
                return

            # Get parameters from dialog
            input_file = extraction_dialog.get_input_file()
            output_path = extraction_dialog.get_output_location()
            options = extraction_dialog.get_extraction_options()

            if not input_file or not output_path:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file and output location.",
                )
                return

            # Start extraction operation in background thread
            self.start_pdf_operation(
                "Extract Text",
                self.pdf_extraction_engine.extract_text,
                input_file,
                output_path,
                options,
            )

        except Exception as e:
            self.logger.error(
                f"Error in text extraction operation: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Text Extraction Error",
                f"Failed to start text extraction: {str(e)}",
            )

    def extract_images_functional(self):
        """Functional PDF image extraction implementation"""
        try:
            self.logger.info("Starting functional PDF image extraction")

            # Show image extraction parameter dialog
            extraction_dialog = PDFImageExtractionDialog(self.parent_widget)
            if extraction_dialog.exec_() != extraction_dialog.Accepted:
                self.logger.info("PDF image extraction cancelled by user")
                return

            # Get parameters from dialog
            input_file = extraction_dialog.get_input_file()
            output_dir = extraction_dialog.get_output_location()
            options = extraction_dialog.get_extraction_options()

            if not input_file or not output_dir:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file and output directory.",
                )
                return

            # Start extraction operation in background thread
            self.start_pdf_operation(
                "Extract Images",
                self.pdf_extraction_engine.extract_images,
                input_file,
                output_dir,
                options,
            )

        except Exception as e:
            self.logger.error(
                f"Error in image extraction operation: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Image Extraction Error",
                f"Failed to start image extraction: {str(e)}",
            )

    def extract_metadata_functional(self):
        """Functional PDF metadata extraction implementation"""
        try:
            self.logger.info("Starting functional PDF metadata extraction")

            # Show metadata extraction parameter dialog
            extraction_dialog = PDFMetadataExtractionDialog(self.parent_widget)
            if extraction_dialog.exec_() != extraction_dialog.Accepted:
                self.logger.info("PDF metadata extraction cancelled by user")
                return

            # Get parameters from dialog
            input_file = extraction_dialog.get_input_file()
            output_path = extraction_dialog.get_output_location()
            options = extraction_dialog.get_extraction_options()

            if not input_file or not output_path:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file and output location.",
                )
                return

            # Start extraction operation in background thread
            self.start_pdf_operation(
                "Extract Metadata",
                self.pdf_extraction_engine.extract_metadata,
                input_file,
                output_path,
                options,
            )

        except Exception as e:
            self.logger.error(
                f"Error in metadata extraction operation: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Metadata Extraction Error",
                f"Failed to start metadata extraction: {str(e)}",
            )

    def extract_tables_functional(self):
        """Functional PDF table extraction implementation"""
        try:
            self.logger.info("Starting functional PDF table extraction")

            # Show table extraction parameter dialog
            extraction_dialog = PDFTableExtractionDialog(self.parent_widget)
            if extraction_dialog.exec_() != extraction_dialog.Accepted:
                self.logger.info("PDF table extraction cancelled by user")
                return

            # Get parameters from dialog
            input_file = extraction_dialog.get_input_file()
            output_dir = extraction_dialog.get_output_location()
            options = extraction_dialog.get_extraction_options()

            if not input_file or not output_dir:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file and output directory.",
                )
                return

            # Start extraction operation in background thread
            self.start_pdf_operation(
                "Extract Tables",
                self.pdf_extraction_engine.extract_tables,
                input_file,
                output_dir,
                options,
            )

        except Exception as e:
            self.logger.error(
                f"Error in table extraction operation: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Table Extraction Error",
                f"Failed to start table extraction: {str(e)}",
            )

    def extract_links_functional(self):
        """Functional PDF link extraction implementation"""
        try:
            self.logger.info("Starting functional PDF link extraction")

            # Show link extraction parameter dialog
            extraction_dialog = PDFLinkExtractionDialog(self.parent_widget)
            if extraction_dialog.exec_() != extraction_dialog.Accepted:
                self.logger.info("PDF link extraction cancelled by user")
                return

            # Get parameters from dialog
            input_file = extraction_dialog.get_input_file()
            output_path = extraction_dialog.get_output_location()
            options = extraction_dialog.get_extraction_options()

            if not input_file or not output_path:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Parameters",
                    "Please select input file and output location.",
                )
                return

            # Start extraction operation in background thread
            self.start_pdf_operation(
                "Extract Links",
                self.pdf_extraction_engine.extract_links,
                input_file,
                output_path,
                options,
            )

        except Exception as e:
            self.logger.error(
                f"Error in link extraction operation: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Link Extraction Error",
                f"Failed to start link extraction: {str(e)}",
            )

    def start_pdf_operation(
        self, operation_name: str, operation_func, *args, **kwargs
    ):
        """Start a PDF operation in background thread with progress dialog"""
        try:
            # Create and show progress dialog
            self.progress_dialog = PDFProgressDialog(
                operation_name, self.parent_widget
            )
            self.progress_dialog.show()

            # Create and start operation thread
            self.current_operation_thread = PDFOperationThread(
                operation_func, *args, **kwargs
            )

            # Connect signals
            self.current_operation_thread.progress_updated.connect(
                self.progress_dialog.update_progress
            )
            self.current_operation_thread.operation_completed.connect(
                self.on_operation_completed
            )
            self.current_operation_thread.operation_failed.connect(
                self.on_operation_failed
            )

            # Connect progress dialog cancel to thread termination
            self.progress_dialog.canceled.connect(self.cancel_operation)

            # Start the operation
            self.current_operation_thread.start()

            self.logger.info(
                f"Started {operation_name} operation in background thread"
            )

        except Exception as e:
            self.logger.error(f"Error starting operation: {e}", exc_info=True)
            if self.progress_dialog:
                self.progress_dialog.close()
            QMessageBox.critical(
                self.parent_widget,
                "Operation Error",
                f"Failed to start operation: {str(e)}",
            )

    def on_operation_completed(self, result: OperationResult):
        """Handle operation completion"""
        try:
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None

            # Clean up thread
            if self.current_operation_thread:
                self.current_operation_thread.quit()
                self.current_operation_thread.wait()
                self.current_operation_thread = None

            if result.success:
                self.show_operation_success(result)
            else:
                self.show_operation_error(result)

        except Exception as e:
            self.logger.error(
                f"Error handling operation completion: {e}", exc_info=True
            )

    def on_operation_failed(self, error_message: str):
        """Handle operation failure"""
        try:
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None

            # Clean up thread
            if self.current_operation_thread:
                self.current_operation_thread.quit()
                self.current_operation_thread.wait()
                self.current_operation_thread = None

            # Show error message
            QMessageBox.critical(
                self.parent_widget,
                "Operation Failed",
                f"PDF operation failed:\n\n{error_message}",
            )

        except Exception as e:
            self.logger.error(
                f"Error handling operation failure: {e}", exc_info=True
            )

    def cancel_operation(self):
        """Cancel the current operation"""
        try:
            if (
                self.current_operation_thread
                and self.current_operation_thread.isRunning()
            ):
                self.logger.info("Cancelling PDF operation")
                self.current_operation_thread.terminate()
                self.current_operation_thread.wait(
                    3000
                )  # Wait up to 3 seconds

                if self.current_operation_thread.isRunning():
                    self.current_operation_thread.kill()

                self.current_operation_thread = None

            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None

        except Exception as e:
            self.logger.error(
                f"Error cancelling operation: {e}", exc_info=True
            )

    def show_operation_success(self, result: OperationResult):
        """Show success message with operation details"""
        try:
            operation_name = result.operation_type.value.title()

            # Build success message
            message = f"{operation_name} operation completed successfully!\n\n"

            if result.processing_time:
                message += (
                    f"Processing time: {result.processing_time:.2f} seconds\n"
                )

            if result.output_files:
                message += f"Output files ({len(result.output_files)}):\n"
                for output_file in result.output_files:
                    message += f"• {os.path.basename(output_file)}\n"

            if result.details:
                if "total_pages" in result.details:
                    message += (
                        f"Total pages: {result.details['total_pages']}\n"
                    )
                if "files_created" in result.details:
                    message += (
                        f"Files created: {result.details['files_created']}\n"
                    )
                if "pages_signed" in result.details:
                    message += (
                        f"Pages signed: {result.details['pages_signed']}\n"
                    )

            # Show success dialog
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setWindowTitle("Operation Successful")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(message.strip())

            # Add "Open Output" button if there are output files
            if result.output_files:
                open_button = msg_box.addButton(
                    "Open Output Folder", QMessageBox.ActionRole
                )
                msg_box.addButton(QMessageBox.Ok)

                msg_box.exec_()

                # Handle "Open Output" button click
                if msg_box.clickedButton() == open_button:
                    self.open_output_folder(result.output_files[0])
            else:
                msg_box.exec_()

            self.logger.info(
                f"{operation_name} operation completed successfully"
            )

        except Exception as e:
            self.logger.error(
                f"Error showing success message: {e}", exc_info=True
            )

    def show_operation_error(self, result: OperationResult):
        """Show error message with details"""
        try:
            operation_name = result.operation_type.value.title()

            message = f"{operation_name} operation failed.\n\n"
            if result.error_message:
                message += f"Error: {result.error_message}\n\n"

            message += "Please check the following:\n"
            message += "• Input files are valid PDF files\n"
            message += "• Output location is writable\n"
            message += "• Files are not open in other applications\n"
            message += "• Sufficient disk space is available"

            QMessageBox.critical(
                self.parent_widget, "Operation Failed", message
            )

            self.logger.error(
                f"{operation_name} operation failed: {result.error_message}"
            )

        except Exception as e:
            self.logger.error(
                f"Error showing error message: {e}", exc_info=True
            )

    def open_output_folder(self, file_path: str):
        """Open the output folder containing the result file"""
        try:
            import platform
            import subprocess

            folder_path = os.path.dirname(file_path)

            if platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])

            self.logger.info(f"Opened output folder: {folder_path}")

        except Exception as e:
            self.logger.warning(f"Could not open output folder: {e}")

    # Security operations - Phase 2.3
    def encrypt_pdf_functional(self):
        """Functional PDF encryption implementation"""
        try:
            self.logger.info("Starting functional PDF encryption operation")

            # Show encryption parameter dialog
            encryption_dialog = PDFEncryptionDialog(self.parent_widget)
            if encryption_dialog.exec_() != encryption_dialog.Accepted:
                self.logger.info("PDF encryption cancelled by user")
                return

            # Get encryption settings
            settings = encryption_dialog.get_security_settings()

            # Get input and output files
            from PyQt5.QtWidgets import QFileDialog

            input_file, _ = QFileDialog.getOpenFileName(
                self.parent_widget,
                "Select PDF to Encrypt",
                "",
                "PDF files (*.pdf)",
            )

            if not input_file:
                self.logger.info("No input file selected for encryption")
                return

            # Get output file
            output_file, _ = QFileDialog.getSaveFileName(
                self.parent_widget,
                "Save Encrypted PDF",
                input_file.replace(".pdf", "_encrypted.pdf"),
                "PDF files (*.pdf)",
            )

            if not output_file:
                self.logger.info("No output file selected for encryption")
                return

            # Show progress dialog
            progress = PDFProgressDialog("Encrypting PDF", self.parent_widget)
            progress.update_progress(0, "Preparing encryption...")
            progress.show()

            # Perform encryption
            result = self.pdf_security_engine.encrypt_pdf(
                input_file, output_file, settings
            )

            progress.close()

            if result.success:
                self.show_security_success(result)
            else:
                self.show_security_error(result)

        except Exception as e:
            self.logger.error(f"PDF encryption failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Encryption Error",
                f"Failed to encrypt PDF: {str(e)}",
            )

    def decrypt_pdf_functional(self):
        """Functional PDF decryption implementation"""
        try:
            self.logger.info("Starting functional PDF decryption operation")

            # Get input and output files first
            from PyQt5.QtWidgets import QFileDialog

            input_file, _ = QFileDialog.getOpenFileName(
                self.parent_widget,
                "Select PDF to Decrypt",
                "",
                "PDF files (*.pdf)",
            )

            if not input_file:
                self.logger.info("No input file selected for decryption")
                return

            # Show decryption parameter dialog
            decryption_dialog = PDFDecryptionDialog(self.parent_widget)
            if decryption_dialog.exec_() != decryption_dialog.Accepted:
                self.logger.info("PDF decryption cancelled by user")
                return

            # Get password
            password = decryption_dialog.get_password()

            # Get output file
            output_file, _ = QFileDialog.getSaveFileName(
                self.parent_widget,
                "Save Decrypted PDF",
                input_file.replace(".pdf", "_decrypted.pdf"),
                "PDF files (*.pdf)",
            )

            if not output_file:
                self.logger.info("No output file selected for decryption")
                return

            # Show progress dialog
            progress = PDFProgressDialog("Decrypting PDF", self.parent_widget)
            progress.update_progress(0, "Removing encryption...")
            progress.show()

            # Perform decryption
            result = self.pdf_security_engine.decrypt_pdf(
                input_file, output_file, password
            )

            progress.close()

            if result.success:
                self.show_security_success(result)
            else:
                self.show_security_error(result)

        except Exception as e:
            self.logger.error(f"PDF decryption failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Decryption Error",
                f"Failed to decrypt PDF: {str(e)}",
            )

    def sign_digital_pdf_functional(self):
        """Functional PDF digital signing implementation"""
        try:
            self.logger.info("Starting functional PDF signing operation")

            # Show signature parameter dialog
            signature_dialog = PDFDigitalSignatureDialog(self.parent_widget)
            if signature_dialog.exec_() != signature_dialog.Accepted:
                self.logger.info("PDF signing cancelled by user")
                return

            # Get signature configuration
            signature_config = signature_dialog.get_signature_config()

            # Get input and output files
            from PyQt5.QtWidgets import QFileDialog

            input_file, _ = QFileDialog.getOpenFileName(
                self.parent_widget,
                "Select PDF to Sign",
                "",
                "PDF files (*.pdf)",
            )

            if not input_file:
                self.logger.info("No input file selected for signing")
                return

            # Get output file
            output_file, _ = QFileDialog.getSaveFileName(
                self.parent_widget,
                "Save Signed PDF",
                input_file.replace(".pdf", "_signed.pdf"),
                "PDF files (*.pdf)",
            )

            if not output_file:
                self.logger.info("No output file selected for signing")
                return

            # Show progress dialog
            progress = PDFProgressDialog("Signing PDF", self.parent_widget)
            progress.update_progress(0, "Adding digital signature...")
            progress.show()

            # Perform signing
            result = self.pdf_security_engine.sign_pdf(
                input_file, output_file, signature_config
            )

            progress.close()

            if result.success:
                self.show_security_success(result)
            else:
                self.show_security_error(result)

        except Exception as e:
            self.logger.error(f"PDF signing failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Signing Error",
                f"Failed to sign PDF: {str(e)}",
            )

    def get_security_info_functional(self):
        """Get and display PDF security information"""
        try:
            self.logger.info("Getting PDF security information")

            # Get input file
            from PyQt5.QtWidgets import QFileDialog

            input_file, _ = QFileDialog.getOpenFileName(
                self.parent_widget,
                "Select PDF to Analyze",
                "",
                "PDF files (*.pdf)",
            )

            if not input_file:
                self.logger.info(
                    "No input file selected for security analysis"
                )
                return

            # Get security information
            result = self.pdf_security_engine.get_security_info(input_file)

            if result.success:
                # Show security info dialog
                PDFSecurityInfoDialog(
                    self.parent_widget, result.security_info
                ).exec_()
            else:
                QMessageBox.critical(
                    self.parent_widget,
                    "Security Analysis Error",
                    f"Failed to analyze PDF security: {result.message}",
                )

        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Analysis Error",
                f"Failed to analyze PDF security: {str(e)}",
            )

    def show_security_success(self, result):
        """Show security operation success message"""
        try:
            operation_name = result.operation.value.replace("_", " ").title()

            message = f"{operation_name} completed successfully!\n\n"
            message += f"Details: {result.message}\n"

            if result.output_path:
                message += f"Output: {os.path.basename(result.output_path)}\n"

            if result.signature_info:
                message += f"\nSignature Information:\n"
                for key, value in result.signature_info.items():
                    message += f"• {key.title()}: {value}\n"

            QMessageBox.information(
                self.parent_widget, f"{operation_name} Complete", message
            )

            # Open output folder if available
            if result.output_path and os.path.exists(result.output_path):
                self.open_output_folder(os.path.dirname(result.output_path))

        except Exception as e:
            self.logger.error(f"Error showing security success: {e}")

    def show_security_error(self, result):
        """Show security operation error message"""
        try:
            operation_name = result.operation.value.replace("_", " ").title()

            message = f"{operation_name} failed!\n\n"
            message += f"Error: {result.message}\n"

            if result.errors:
                message += f"\nDetailed Errors:\n"
                for error in result.errors:
                    message += f"• {error}\n"

            if result.warnings:
                message += f"\nWarnings:\n"
                for warning in result.warnings:
                    message += f"• {warning}\n"

            QMessageBox.critical(
                self.parent_widget, f"{operation_name} Failed", message
            )

        except Exception as e:
            self.logger.error(f"Error showing security error: {e}")

    # Enhancement operations - Phase 2.4
    def add_watermark_functional(self):
        """Functional PDF watermark implementation"""
        try:
            self.logger.info("Starting functional PDF watermark operation")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                from PyQt5.QtWidgets import QFileDialog

                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF for Watermark",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                self.logger.info("No input file selected for watermark")
                return

            # Get watermark parameters
            from PyQt5.QtCore import Qt
            from PyQt5.QtWidgets import (
                QDialog,
                QDialogButtonBox,
                QHBoxLayout,
                QInputDialog,
                QLabel,
                QLineEdit,
                QPushButton,
                QSlider,
                QVBoxLayout,
            )

            # Create watermark parameter dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("Add Watermark")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # Watermark text
            layout.addWidget(QLabel("Watermark Text:"))
            text_edit = QLineEdit()
            text_edit.setText("CONFIDENTIAL")
            layout.addWidget(text_edit)

            # Opacity
            layout.addWidget(QLabel("Opacity (0-100%):"))
            opacity_layout = QHBoxLayout()
            opacity_slider = QSlider()
            opacity_slider.setOrientation(Qt.Horizontal)
            opacity_slider.setRange(0, 100)
            opacity_slider.setValue(50)
            opacity_label = QLabel("50%")
            opacity_slider.valueChanged.connect(
                lambda v: opacity_label.setText(f"{v}%")
            )
            opacity_layout.addWidget(opacity_slider)
            opacity_layout.addWidget(opacity_label)
            layout.addLayout(opacity_layout)

            # Pages
            layout.addWidget(
                QLabel("Pages (comma-separated, leave empty for all):")
            )
            pages_edit = QLineEdit()
            layout.addWidget(pages_edit)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() != QDialog.Accepted:
                self.logger.info("Watermark operation cancelled by user")
                return

            # Get parameters
            watermark_text = text_edit.text()
            opacity = opacity_slider.value() / 100.0

            # Parse pages
            pages = None
            if pages_edit.text().strip():
                try:
                    pages = tuple(
                        int(p.strip()) - 1
                        for p in pages_edit.text().split(",")
                    )
                except ValueError:
                    QMessageBox.warning(
                        self.parent_widget,
                        "Invalid Pages",
                        "Invalid page format. Use comma-separated numbers.",
                    )
                    return

            # Show progress
            progress = PDFProgressDialog(
                "Adding Watermark", self.parent_widget
            )
            progress.update_progress(0, "Preparing watermark...")
            progress.show()

            # Import and use the watermark function
            try:
                import os
                import sys

                sys.path.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "src",
                        "utilities",
                        "pdf_tools",
                        "pdf_enhancements",
                    )
                )

                from watermark import add_watermark

                progress.update_progress(50, "Applying watermark...")

                # Apply watermark
                success = add_watermark(
                    input_file=input_file,
                    watermark_text=watermark_text,
                    pages=pages,
                    opacity=opacity,
                )
            except ImportError:
                # Fallback implementation using PyMuPDF directly
                progress.update_progress(
                    50, "Applying watermark (fallback)..."
                )
                success = self._add_watermark_fallback(
                    input_file, watermark_text, pages, opacity
                )

            progress.close()

            if success:
                output_file = (
                    os.path.splitext(input_file)[0] + "_watermarked.pdf"
                )
                QMessageBox.information(
                    self.parent_widget,
                    "Watermark Complete",
                    f"Watermark applied successfully!\nOutput: {output_file}",
                )
                # Open output folder
                import platform
                import subprocess

                folder_path = os.path.dirname(output_file)
                if platform.system() == "Windows":
                    subprocess.run(["explorer", folder_path])
            else:
                QMessageBox.critical(
                    self.parent_widget,
                    "Watermark Failed",
                    "Failed to apply watermark to PDF.",
                )

        except Exception as e:
            self.logger.error(f"PDF watermark failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Watermark Error",
                f"Failed to add watermark: {str(e)}",
            )

    def perform_ocr_functional(self):
        """Functional PDF OCR implementation"""
        try:
            self.logger.info("Starting functional PDF OCR operation")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                from PyQt5.QtWidgets import QFileDialog

                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF for OCR",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                self.logger.info("No input file selected for OCR")
                return

            # Get OCR parameters
            from PyQt5.QtWidgets import (
                QCheckBox,
                QComboBox,
                QDialog,
                QDialogButtonBox,
                QLabel,
                QLineEdit,
                QVBoxLayout,
            )

            # Create OCR parameter dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("OCR Processing")
            dialog.setModal(True)
            dialog.resize(400, 350)

            layout = QVBoxLayout(dialog)

            # Search text (optional)
            layout.addWidget(QLabel("Search Text (optional):"))
            search_edit = QLineEdit()
            search_edit.setPlaceholderText(
                "Enter text to search and highlight..."
            )
            layout.addWidget(search_edit)

            # Action type
            layout.addWidget(QLabel("Action for found text:"))
            action_combo = QComboBox()
            action_combo.addItems(["Highlight", "Redact"])
            layout.addWidget(action_combo)

            # Pages
            layout.addWidget(
                QLabel("Pages (comma-separated, leave empty for all):")
            )
            pages_edit = QLineEdit()
            layout.addWidget(pages_edit)

            # Generate output
            generate_output_check = QCheckBox("Generate text output file")
            generate_output_check.setChecked(True)
            layout.addWidget(generate_output_check)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() != QDialog.Accepted:
                self.logger.info("OCR operation cancelled by user")
                return

            # Get parameters
            search_text = (
                search_edit.text() if search_edit.text().strip() else None
            )
            action = action_combo.currentText()
            generate_output = generate_output_check.isChecked()

            # Parse pages
            pages = None
            if pages_edit.text().strip():
                try:
                    pages = tuple(
                        int(p.strip()) for p in pages_edit.text().split(",")
                    )
                except ValueError:
                    QMessageBox.warning(
                        self.parent_widget,
                        "Invalid Pages",
                        "Invalid page format. Use comma-separated numbers.",
                    )
                    return

            # Show progress
            progress = PDFProgressDialog("OCR Processing", self.parent_widget)
            progress.update_progress(0, "Initializing OCR...")
            progress.show()

            # Import and use the OCR function
            try:
                import os
                import sys

                sys.path.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "src",
                        "utilities",
                        "pdf_tools",
                        "pdf_enhancements",
                    )
                )

                from ocr import ocr_file

                progress.update_progress(20, "Processing document...")

                # Generate output file if needed
                output_file = None
                if search_text or generate_output:
                    output_file = os.path.splitext(input_file)[0] + "_ocr.pdf"

                # Perform OCR
                success = ocr_file(
                    input_file=input_file,
                    output_file=output_file,
                    search_str=search_text,
                    pages=pages,
                    highlight_readable_text=False,
                    action=action,
                    show_comparison=False,
                    generate_output=generate_output,
                )
            except ImportError:
                # Fallback implementation
                progress.update_progress(
                    20, "Processing document (fallback)..."
                )
                success = self._perform_ocr_fallback(
                    input_file, search_text, action, pages, generate_output
                )

            progress.close()

            if success is not False:  # ocr_file returns None on success
                message = "OCR processing completed successfully!"
                if output_file and os.path.exists(output_file):
                    message += f"\nOutput: {output_file}"
                if generate_output:
                    content_file = os.path.splitext(input_file)[0] + ".csv"
                    if os.path.exists(content_file):
                        message += f"\nText content: {content_file}"

                QMessageBox.information(
                    self.parent_widget, "OCR Complete", message
                )

                # Open output folder
                if output_file:
                    import platform
                    import subprocess

                    folder_path = os.path.dirname(output_file)
                    if platform.system() == "Windows":
                        subprocess.run(["explorer", folder_path])
            else:
                QMessageBox.critical(
                    self.parent_widget,
                    "OCR Failed",
                    "Failed to process PDF with OCR.",
                )

        except Exception as e:
            self.logger.error(f"PDF OCR failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "OCR Error",
                f"Failed to perform OCR: {str(e)}",
            )

    def highlight_content_functional(self):
        """Functional PDF content highlighting implementation"""
        try:
            self.logger.info("Starting functional PDF highlighting operation")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                from PyQt5.QtWidgets import QFileDialog

                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF for Highlighting",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                self.logger.info("No input file selected for highlighting")
                return

            # Get highlighting parameters
            from PyQt5.QtCore import Qt
            from PyQt5.QtWidgets import (
                QComboBox,
                QDialog,
                QDialogButtonBox,
                QHBoxLayout,
                QLabel,
                QLineEdit,
                QSlider,
                QVBoxLayout,
            )

            # Create highlighting parameter dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("Highlight Content")
            dialog.setModal(True)
            dialog.resize(400, 400)

            layout = QVBoxLayout(dialog)

            # Search text
            layout.addWidget(QLabel("Search Text:"))
            search_edit = QLineEdit()
            search_edit.setPlaceholderText(
                "Enter text to search and highlight..."
            )
            layout.addWidget(search_edit)

            # Action type
            layout.addWidget(QLabel("Action:"))
            action_combo = QComboBox()
            action_combo.addItems(
                [
                    "Highlight",
                    "Underline",
                    "Strikeout",
                    "Squiggly",
                    "Frame",
                    "Redact",
                    "Remove",
                ]
            )
            layout.addWidget(action_combo)

            # Color selection
            layout.addWidget(QLabel("Color:"))
            color_combo = QComboBox()
            color_combo.addItems(["Yellow", "Red", "Green", "Blue", "Purple"])
            layout.addWidget(color_combo)

            # Opacity
            layout.addWidget(QLabel("Opacity (0-100%):"))
            opacity_layout = QHBoxLayout()
            opacity_slider = QSlider()
            opacity_slider.setOrientation(Qt.Horizontal)
            opacity_slider.setRange(0, 100)
            opacity_slider.setValue(80)
            opacity_label = QLabel("80%")
            opacity_slider.valueChanged.connect(
                lambda v: opacity_label.setText(f"{v}%")
            )
            opacity_layout.addWidget(opacity_slider)
            opacity_layout.addWidget(opacity_label)
            layout.addLayout(opacity_layout)

            # Pages
            layout.addWidget(
                QLabel("Pages (comma-separated, leave empty for all):")
            )
            pages_edit = QLineEdit()
            layout.addWidget(pages_edit)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Enable/disable controls based on action
            def on_action_changed():
                action = action_combo.currentText()
                color_enabled = action not in ["Redact", "Remove"]
                color_combo.setEnabled(color_enabled)
                opacity_slider.setEnabled(color_enabled)
                search_enabled = action != "Remove"
                search_edit.setEnabled(search_enabled)

            action_combo.currentTextChanged.connect(on_action_changed)
            on_action_changed()

            if dialog.exec_() != QDialog.Accepted:
                self.logger.info("Highlighting operation cancelled by user")
                return

            # Get parameters
            search_text = (
                search_edit.text() if search_edit.text().strip() else None
            )
            action = action_combo.currentText()
            color = color_combo.currentText().lower()
            opacity = opacity_slider.value() / 100.0

            if action != "Remove" and not search_text:
                QMessageBox.warning(
                    self.parent_widget,
                    "Missing Search Text",
                    "Please enter search text for highlighting.",
                )
                return

            # Parse pages
            pages = None
            if pages_edit.text().strip():
                try:
                    pages = tuple(
                        str(int(p.strip()))
                        for p in pages_edit.text().split(",")
                    )
                except ValueError:
                    QMessageBox.warning(
                        self.parent_widget,
                        "Invalid Pages",
                        "Invalid page format. Use comma-separated numbers.",
                    )
                    return

            # Show progress
            progress = PDFProgressDialog(
                "Highlighting Content", self.parent_widget
            )
            progress.update_progress(0, "Preparing highlighting...")
            progress.show()

            # Import and use the highlight function
            try:
                import os
                import sys

                sys.path.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "src",
                        "utilities",
                        "pdf_tools",
                        "pdf_enhancements",
                    )
                )

                from highlight import process_data, remove_highlght

                progress.update_progress(30, "Processing document...")

                # Generate output file
                output_file = (
                    os.path.splitext(input_file)[0] + "_highlighted.pdf"
                )

                # Perform highlighting
                if action == "Remove":
                    success = remove_highlght(
                        input_file=input_file,
                        output_file=output_file,
                        pages=pages,
                    )
                else:
                    success = process_data(
                        input_file=input_file,
                        output_file=output_file,
                        search_str=search_text,
                        pages=pages,
                        action=action,
                        color=color,
                        opacity=opacity,
                    )
            except ImportError:
                # Fallback implementation
                progress.update_progress(
                    30, "Processing document (fallback)..."
                )
                output_file = (
                    os.path.splitext(input_file)[0] + "_highlighted.pdf"
                )
                success = self._highlight_content_fallback(
                    input_file, search_text, action, color, opacity, pages
                )

            progress.close()

            if success:
                QMessageBox.information(
                    self.parent_widget,
                    "Highlighting Complete",
                    f"Content highlighting completed successfully!\n"
                    f"Output: {output_file}",
                )

                # Open output folder
                import platform
                import subprocess

                folder_path = os.path.dirname(output_file)
                if platform.system() == "Windows":
                    subprocess.run(["explorer", folder_path])
            else:
                QMessageBox.critical(
                    self.parent_widget,
                    "Highlighting Failed",
                    "Failed to highlight content in PDF.",
                )

        except Exception as e:
            self.logger.error(f"PDF highlighting failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Highlighting Error",
                f"Failed to highlight content: {str(e)}",
            )

    # Conversion operations - Phase 2.5
    def convert_to_docx_functional(self):
        """Functional PDF to DOCX conversion implementation"""
        try:
            self.logger.info("Starting functional PDF to DOCX conversion")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF to Convert",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                return

            # Get conversion parameters
            from PyQt5.QtWidgets import (
                QCheckBox,
                QDialog,
                QDialogButtonBox,
                QLabel,
                QLineEdit,
                QVBoxLayout,
            )

            # Create conversion parameter dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("Convert to DOCX")
            dialog.setModal(True)
            dialog.resize(400, 250)

            layout = QVBoxLayout(dialog)

            # Output file
            layout.addWidget(QLabel("Output DOCX File:"))
            output_edit = QLineEdit()
            output_edit.setText(os.path.splitext(input_file)[0] + ".docx")
            layout.addWidget(output_edit)

            # Pages
            layout.addWidget(
                QLabel("Pages (comma-separated, leave empty for all):")
            )
            pages_edit = QLineEdit()
            layout.addWidget(pages_edit)

            # Create output folder option
            create_folder_check = QCheckBox(
                "Create output folder for converted files"
            )
            layout.addWidget(create_folder_check)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() != QDialog.Accepted:
                return

            # Get parameters
            output_file = output_edit.text()
            create_folder = create_folder_check.isChecked()

            # Parse pages
            pages = None
            if pages_edit.text().strip():
                try:
                    pages = tuple(
                        int(p.strip()) for p in pages_edit.text().split(",")
                    )
                except ValueError:
                    QMessageBox.warning(
                        self.parent_widget,
                        "Invalid Pages",
                        "Invalid page format. Use comma-separated numbers.",
                    )
                    return

            # Show progress
            progress = PDFProgressDialog(
                "Converting to DOCX", self.parent_widget
            )
            progress.update_progress(0, "Preparing conversion...")
            progress.show()

            # Import and use the conversion function
            try:
                sys.path.insert(
                    0, r"C:\Users\HP1\1_2\src\tools\pdf_tools\pdf_conversion"
                )
                from convert_to_docx import convert_pdf2docx, create_folder

                success = convert_pdf2docx(input_file, output_file, pages)

                if create_folder and success:
                    folder_name = "converted_docx"
                    create_folder(folder_name)

                progress.close()

                if success:
                    QMessageBox.information(
                        self.parent_widget,
                        "Conversion Complete",
                        f"PDF successfully converted to DOCX:\n{output_file}",
                    )
                    # Open output folder
                    if os.path.exists(output_file):
                        self.open_output_folder(output_file)
                else:
                    QMessageBox.critical(
                        self.parent_widget,
                        "Conversion Failed",
                        "Failed to convert PDF to DOCX.",
                    )

            except ImportError:
                progress.close()
                success = self._convert_to_docx_fallback(
                    input_file, output_file, pages
                )

                if success:
                    QMessageBox.information(
                        self.parent_widget,
                        "Conversion Complete",
                        f"PDF successfully converted to DOCX:\n{output_file}",
                    )
                else:
                    QMessageBox.critical(
                        self.parent_widget,
                        "Conversion Failed",
                        "Failed to convert PDF to DOCX. Missing dependencies.",
                    )

        except Exception as e:
            self.logger.error(
                f"PDF to DOCX conversion failed: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Conversion Error",
                f"Failed to convert to DOCX: {str(e)}",
            )

    def convert_to_image_functional(self):
        """Functional PDF to Image conversion implementation"""
        try:
            self.logger.info("Starting functional PDF to Image conversion")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF to Convert",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                return

            # Get conversion parameters
            from PyQt5.QtWidgets import (
                QComboBox,
                QDialog,
                QDialogButtonBox,
                QLabel,
                QLineEdit,
                QVBoxLayout,
            )

            # Create conversion parameter dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("Convert to Images")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # Output directory
            layout.addWidget(QLabel("Output Directory:"))
            output_edit = QLineEdit()
            output_edit.setText("converted_images")
            layout.addWidget(output_edit)

            # Image format
            layout.addWidget(QLabel("Image Format:"))
            format_combo = QComboBox()
            format_combo.addItems(["PNG", "JPEG", "BMP", "TIFF"])
            layout.addWidget(format_combo)

            # Pages
            layout.addWidget(
                QLabel("Pages (comma-separated, leave empty for all):")
            )
            pages_edit = QLineEdit()
            layout.addWidget(pages_edit)

            # Quality/DPI
            layout.addWidget(QLabel("DPI (Image Quality):"))
            dpi_combo = QComboBox()
            dpi_combo.addItems(["150", "300", "600", "1200"])
            dpi_combo.setCurrentText("300")
            layout.addWidget(dpi_combo)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() != QDialog.Accepted:
                return

            # Get parameters
            output_dir = output_edit.text()
            image_format = format_combo.currentText().lower()
            dpi = int(dpi_combo.currentText())

            # Parse pages
            pages = None
            if pages_edit.text().strip():
                try:
                    pages = tuple(
                        int(p.strip()) - 1
                        for p in pages_edit.text().split(",")
                    )
                except ValueError:
                    QMessageBox.warning(
                        self.parent_widget,
                        "Invalid Pages",
                        "Invalid page format. Use comma-separated numbers.",
                    )
                    return

            # Show progress
            progress = PDFProgressDialog(
                "Converting to Images", self.parent_widget
            )
            progress.update_progress(0, "Preparing conversion...")
            progress.show()

            # Import and use the conversion function
            try:
                sys.path.insert(
                    0, r"C:\Users\HP1\1_2\src\tools\pdf_tools\pdf_conversion"
                )
                from convert_to_image import convert_pdf2img

                # Create output directory
                os.makedirs(output_dir, exist_ok=True)

                output_files = convert_pdf2img(input_file, pages)

                progress.close()

                if output_files:
                    QMessageBox.information(
                        self.parent_widget,
                        "Conversion Complete",
                        f"PDF successfully converted to {len(output_files)} images in:\n{output_dir}",
                    )
                    # Open output folder
                    if os.path.exists(output_dir):
                        self.open_output_folder(output_dir)
                else:
                    QMessageBox.critical(
                        self.parent_widget,
                        "Conversion Failed",
                        "Failed to convert PDF to images.",
                    )

            except ImportError:
                progress.close()
                success = self._convert_to_image_fallback(
                    input_file, output_dir, pages, image_format, dpi
                )

                if success:
                    QMessageBox.information(
                        self.parent_widget,
                        "Conversion Complete",
                        f"PDF successfully converted to images in:\n{output_dir}",
                    )
                else:
                    QMessageBox.critical(
                        self.parent_widget,
                        "Conversion Failed",
                        "Failed to convert PDF to images.",
                    )

        except Exception as e:
            self.logger.error(
                f"PDF to Image conversion failed: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Conversion Error",
                f"Failed to convert to images: {str(e)}",
            )

    def convert_html_to_pdf_functional(self):
        """Functional HTML to PDF conversion implementation"""
        try:
            self.logger.info("Starting functional HTML to PDF conversion")

            # Get conversion parameters
            from PyQt5.QtWidgets import (
                QComboBox,
                QDialog,
                QDialogButtonBox,
                QHBoxLayout,
                QLabel,
                QLineEdit,
                QPushButton,
                QTabWidget,
                QTextEdit,
                QVBoxLayout,
                QWidget,
            )

            # Create conversion parameter dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("Convert HTML to PDF")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # Create tabs for different input methods
            tab_widget = QTabWidget()
            layout.addWidget(tab_widget)

            # URL Tab
            url_tab = QWidget()
            url_layout = QVBoxLayout(url_tab)
            url_layout.addWidget(QLabel("Website URL:"))
            url_edit = QLineEdit()
            url_edit.setPlaceholderText("https://example.com")
            url_layout.addWidget(url_edit)
            tab_widget.addTab(url_tab, "From URL")

            # File Tab
            file_tab = QWidget()
            file_layout = QVBoxLayout(file_tab)
            file_layout.addWidget(QLabel("HTML File:"))
            file_input_layout = QHBoxLayout()
            file_edit = QLineEdit()
            browse_btn = QPushButton("Browse")

            def browse_html_file():
                filename, _ = QFileDialog.getOpenFileName(
                    dialog,
                    "Select HTML File",
                    "",
                    "HTML files (*.html *.htm);;All files (*.*)",
                )
                if filename:
                    file_edit.setText(filename)

            browse_btn.clicked.connect(browse_html_file)
            file_input_layout.addWidget(file_edit)
            file_input_layout.addWidget(browse_btn)
            file_layout.addLayout(file_input_layout)
            tab_widget.addTab(file_tab, "From File")

            # HTML Content Tab
            html_tab = QWidget()
            html_layout = QVBoxLayout(html_tab)
            html_layout.addWidget(QLabel("HTML Content:"))
            html_edit = QTextEdit()
            html_edit.setPlaceholderText("Enter HTML content here...")
            html_layout.addWidget(html_edit)
            tab_widget.addTab(html_tab, "HTML Code")

            # Output file
            layout.addWidget(QLabel("Output PDF File:"))
            output_input_layout = QHBoxLayout()
            output_edit = QLineEdit()
            output_edit.setText("output.pdf")
            output_browse_btn = QPushButton("Browse")

            def browse_output_file():
                filename, _ = QFileDialog.getSaveFileName(
                    dialog,
                    "Save PDF File",
                    "",
                    "PDF files (*.pdf);;All files (*.*)",
                )
                if filename:
                    output_edit.setText(filename)

            output_browse_btn.clicked.connect(browse_output_file)
            output_input_layout.addWidget(output_edit)
            output_input_layout.addWidget(output_browse_btn)
            layout.addLayout(output_input_layout)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() != QDialog.Accepted:
                return

            # Get parameters based on selected tab
            current_tab = tab_widget.currentIndex()
            output_file = output_edit.text()

            if not output_file:
                QMessageBox.warning(
                    self.parent_widget,
                    "Invalid Output",
                    "Please specify output PDF file.",
                )
                return

            # Show progress
            progress = PDFProgressDialog(
                "Converting HTML to PDF", self.parent_widget
            )
            progress.update_progress(0, "Preparing conversion...")
            progress.show()

            # Import and use the conversion function
            try:
                sys.path.insert(
                    0, r"C:\Users\HP1\1_2\src\tools\pdf_tools\pdf_conversion"
                )
                import pdfkit

                success = False

                if current_tab == 0:  # URL
                    url = url_edit.text()
                    if not url:
                        progress.close()
                        QMessageBox.warning(
                            self.parent_widget,
                            "Invalid URL",
                            "Please enter a valid URL.",
                        )
                        return
                    progress.update_progress(50, "Converting URL to PDF...")
                    pdfkit.from_url(url, output_file)
                    success = True

                elif current_tab == 1:  # File
                    input_file = file_edit.text()
                    if not input_file or not os.path.exists(input_file):
                        progress.close()
                        QMessageBox.warning(
                            self.parent_widget,
                            "Invalid File",
                            "Please select a valid HTML file.",
                        )
                        return
                    progress.update_progress(
                        50, "Converting HTML file to PDF..."
                    )
                    pdfkit.from_file(input_file, output_file)
                    success = True

                elif current_tab == 2:  # HTML Content
                    html_content = html_edit.toPlainText()
                    if not html_content.strip():
                        progress.close()
                        QMessageBox.warning(
                            self.parent_widget,
                            "Invalid Content",
                            "Please enter HTML content.",
                        )
                        return
                    progress.update_progress(
                        50, "Converting HTML content to PDF..."
                    )
                    pdfkit.from_string(html_content, output_file)
                    success = True

                progress.close()

                if success and os.path.exists(output_file):
                    QMessageBox.information(
                        self.parent_widget,
                        "Conversion Complete",
                        f"HTML successfully converted to PDF:\n{output_file}",
                    )
                    # Open output folder
                    self.open_output_folder(output_file)
                else:
                    QMessageBox.critical(
                        self.parent_widget,
                        "Conversion Failed",
                        "Failed to convert HTML to PDF.",
                    )

            except ImportError:
                progress.close()
                QMessageBox.critical(
                    self.parent_widget,
                    "Missing Dependencies",
                    "HTML to PDF conversion requires pdfkit and wkhtmltopdf.\n\n"
                    "Please install:\n"
                    "- pip install pdfkit\n"
                    "- Download and install wkhtmltopdf",
                )
            except Exception as conv_error:
                progress.close()
                QMessageBox.critical(
                    self.parent_widget,
                    "Conversion Error",
                    f"Failed to convert HTML to PDF:\n{str(conv_error)}",
                )

        except Exception as e:
            self.logger.error(
                f"HTML to PDF conversion failed: {e}", exc_info=True
            )
            QMessageBox.critical(
                self.parent_widget,
                "Conversion Error",
                f"Failed to convert HTML to PDF: {str(e)}",
            )

    # View and Analysis operations - Phase 2.6
    def view_pdf_functional(self):
        """Functional PDF viewer implementation"""
        try:
            self.logger.info("Starting functional PDF viewer")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF to View",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                return

            # Show PDF viewer
            try:
                sys.path.insert(
                    0,
                    r"C:\Users\HP1\1_2\src\tools\pdf_tools\pdf_view_analysis",
                )

                # Add missing import fix for the view module
                import builtins

                original_import = builtins.__import__

                def patched_import(name, *args, **kwargs):
                    if name == "QtWidgets" and "view" in str(
                        kwargs.get("fromlist", [])
                    ):
                        from PyQt5 import QtWidgets

                        return QtWidgets
                    return original_import(name, *args, **kwargs)

                builtins.__import__ = patched_import

                try:
                    from view import PDFViewer
                finally:
                    builtins.__import__ = original_import

                # Create and configure viewer
                self.pdf_viewer_window = PDFViewer()

                # Open the selected file automatically
                if (
                    hasattr(self.pdf_viewer_window, "doc")
                    and self.pdf_viewer_window.doc
                ):
                    self.pdf_viewer_window.doc.close()

                import fitz

                self.pdf_viewer_window.doc = fitz.open(input_file)
                self.pdf_viewer_window.total_pages = len(
                    self.pdf_viewer_window.doc
                )
                self.pdf_viewer_window.current_page = 0

                if self.pdf_viewer_window.total_pages > 0:
                    self.pdf_viewer_window.show_page()
                    self.pdf_viewer_window.previousButton.setEnabled(True)
                    self.pdf_viewer_window.nextButton.setEnabled(True)
                    self.pdf_viewer_window.statusBar().showMessage(
                        f"Loaded {os.path.basename(input_file)}", 3000
                    )

                # Show the viewer window
                self.pdf_viewer_window.show()
                self.pdf_viewer_window.raise_()
                self.pdf_viewer_window.activateWindow()

                self.logger.info(f"PDF viewer opened for: {input_file}")

            except ImportError:
                # Fallback viewer implementation
                self._view_pdf_fallback(input_file)
            except Exception as viewer_error:
                self.logger.error(
                    f"PDF viewer error: {viewer_error}", exc_info=True
                )
                QMessageBox.critical(
                    self.parent_widget,
                    "Viewer Error",
                    f"Failed to open PDF viewer:\n{str(viewer_error)}",
                )

        except Exception as e:
            self.logger.error(f"PDF viewer failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Viewer Error",
                f"Failed to open PDF viewer: {str(e)}",
            )

    def analyze_pdf_functional(self):
        """Functional PDF analysis implementation"""
        try:
            self.logger.info("Starting functional PDF analysis")

            # Get current file or ask for input file
            input_file = self.parent_widget.state_manager.get_current_file()
            if not input_file:
                input_file, _ = QFileDialog.getOpenFileName(
                    self.parent_widget,
                    "Select PDF to Analyze",
                    "",
                    "PDF files (*.pdf)",
                )

            if not input_file:
                return

            # Show analysis options dialog
            from PyQt5.QtWidgets import (
                QCheckBox,
                QDialog,
                QDialogButtonBox,
                QHBoxLayout,
                QLabel,
                QPushButton,
                QTabWidget,
                QTextEdit,
                QVBoxLayout,
                QWidget,
            )

            # Create analysis dialog
            dialog = QDialog(self.parent_widget)
            dialog.setWindowTitle("PDF Analysis Options")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # Analysis options
            layout.addWidget(QLabel("Select analysis operations:"))

            metadata_check = QCheckBox(
                "Extract metadata (author, title, creation date)"
            )
            metadata_check.setChecked(True)
            layout.addWidget(metadata_check)

            text_check = QCheckBox("Extract and analyze text content")
            text_check.setChecked(True)
            layout.addWidget(text_check)

            structure_check = QCheckBox("Analyze document structure")
            structure_check.setChecked(True)
            layout.addWidget(structure_check)

            images_check = QCheckBox("Count and analyze images")
            images_check.setChecked(False)
            layout.addWidget(images_check)

            # Results display option
            viewer_check = QCheckBox("Open in interactive PDF miner")
            viewer_check.setChecked(True)
            layout.addWidget(viewer_check)

            # Buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() != QDialog.Accepted:
                return

            # Get selected options
            extract_metadata = metadata_check.isChecked()
            extract_text = text_check.isChecked()
            analyze_structure = structure_check.isChecked()
            analyze_images = images_check.isChecked()
            open_miner = viewer_check.isChecked()

            # Show progress
            progress = PDFProgressDialog("Analyzing PDF", self.parent_widget)
            progress.update_progress(0, "Starting analysis...")
            progress.show()

            # Perform analysis
            try:
                sys.path.insert(
                    0,
                    r"C:\Users\HP1\1_2\src\tools\pdf_tools\pdf_view_analysis",
                )
                import fitz
                from miner import PDFMiner

                # Create PDF miner instance
                pdf_miner = PDFMiner(input_file)

                analysis_results = {}

                # Extract metadata
                if extract_metadata:
                    progress.update_progress(20, "Extracting metadata...")
                    metadata, num_pages = pdf_miner.get_metadata()
                    analysis_results["metadata"] = metadata
                    analysis_results["page_count"] = num_pages

                # Extract and analyze text
                if extract_text:
                    progress.update_progress(40, "Analyzing text content...")
                    doc = fitz.open(input_file)
                    total_text = ""
                    page_texts = []

                    for page_num in range(len(doc)):
                        page_text = pdf_miner.get_text(page_num)
                        page_texts.append(page_text)
                        total_text += page_text + " "

                    analysis_results["total_text_length"] = len(total_text)
                    analysis_results["word_count"] = len(total_text.split())
                    analysis_results["page_texts"] = page_texts
                    doc.close()

                # Analyze structure
                if analyze_structure:
                    progress.update_progress(
                        60, "Analyzing document structure..."
                    )
                    doc = fitz.open(input_file)
                    analysis_results["page_dimensions"] = []
                    analysis_results["total_size"] = os.path.getsize(
                        input_file
                    )

                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        analysis_results["page_dimensions"].append(
                            {
                                "page": page_num + 1,
                                "width": page.rect.width,
                                "height": page.rect.height,
                            }
                        )
                    doc.close()

                # Analyze images
                if analyze_images:
                    progress.update_progress(80, "Analyzing images...")
                    doc = fitz.open(input_file)
                    image_count = 0

                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        image_list = page.get_images()
                        image_count += len(image_list)

                    analysis_results["image_count"] = image_count
                    doc.close()

                progress.close()

                # Show results
                if open_miner:
                    # Open interactive miner
                    from miner import MainWindow

                    self.pdf_miner_window = MainWindow()
                    self.pdf_miner_window.pdf_miner = pdf_miner
                    self.pdf_miner_window.show()
                    self.pdf_miner_window.show_page(0)
                    self.pdf_miner_window.raise_()
                    self.pdf_miner_window.activateWindow()
                else:
                    # Show analysis results in dialog
                    self._show_analysis_results(analysis_results, input_file)

                self.logger.info(f"PDF analysis completed for: {input_file}")

            except ImportError:
                progress.close()
                # Fallback analysis implementation
                self._analyze_pdf_fallback(
                    input_file,
                    extract_metadata,
                    extract_text,
                    analyze_structure,
                    analyze_images,
                )
            except Exception as analysis_error:
                progress.close()
                self.logger.error(
                    f"PDF analysis error: {analysis_error}", exc_info=True
                )
                QMessageBox.critical(
                    self.parent_widget,
                    "Analysis Error",
                    f"Failed to analyze PDF:\n{str(analysis_error)}",
                )

        except Exception as e:
            self.logger.error(f"PDF analysis failed: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent_widget,
                "Analysis Error",
                f"Failed to analyze PDF: {str(e)}",
            )

    def cleanup(self):
        """Clean up resources"""
        try:
            # Cancel any running operation
            self.cancel_operation()

            # Clean up PDF engines
            if self.pdf_engine:
                self.pdf_engine.cleanup()
            if (
                hasattr(self, "pdf_security_engine")
                and self.pdf_security_engine
            ):
                # Security engine cleanup if needed
                pass

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}", exc_info=True)

    def _add_watermark_fallback(
        self, input_file, watermark_text, pages=None, opacity=0.5
    ):
        """Fallback watermark implementation using PyMuPDF directly"""
        try:
            import fitz

            # Open the PDF
            pdf = fitz.open(input_file)

            # Get pages to process
            if pages:
                page_list = pages
            else:
                page_list = range(len(pdf))

            for page_num in page_list:
                if page_num >= len(pdf):
                    continue

                page = pdf[page_num]

                # Calculate text position (center of page)
                rect = page.rect
                text_width = fitz.get_text_length(
                    watermark_text, fontname="helv"
                )
                x = (rect.width - text_width) / 2
                y = rect.height / 2

                # Add watermark text
                page.insert_text(
                    (x, y),
                    watermark_text,
                    fontsize=36,
                    fontname="helv",
                    rotate=45,
                    opacity=opacity,
                )

            # Save the output file
            output_file = os.path.splitext(input_file)[0] + "_watermarked.pdf"
            pdf.save(output_file)
            pdf.close()

            return True

        except Exception as e:
            self.logger.error(f"Fallback watermark failed: {e}")
            return False

    def _perform_ocr_fallback(
        self,
        input_file,
        search_text=None,
        action="Highlight",
        pages=None,
        generate_output=True,
    ):
        """Fallback OCR implementation with basic functionality"""
        try:
            # Create a simple message about OCR functionality
            QMessageBox.information(
                self.parent_widget,
                "OCR Information",
                "OCR functionality requires additional dependencies.\n\n"
                "To enable full OCR features, install:\n"
                "- pytesseract\n"
                "- opencv-python\n"
                "- Tesseract OCR engine\n\n"
                "For now, basic text extraction will be performed.",
            )

            # Perform basic text extraction instead
            import fitz

            pdf = fitz.open(input_file)
            text_content = []

            page_range = pages if pages else range(len(pdf))

            for page_num in page_range:
                if page_num < len(pdf):
                    page = pdf[page_num]
                    text = page.get_text()
                    if text.strip():
                        text_content.append(
                            f"=== Page {page_num + 1} ===\n{text}\n"
                        )

            pdf.close()

            # Save text content
            if generate_output:
                output_file = (
                    os.path.splitext(input_file)[0] + "_text_extract.txt"
                )
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(text_content))

            return True

        except Exception as e:
            self.logger.error(f"Fallback OCR failed: {e}")
            return False

    def _highlight_content_fallback(
        self,
        input_file,
        search_text,
        action="Highlight",
        color="yellow",
        opacity=0.8,
        pages=None,
    ):
        """Fallback highlighting implementation using PyMuPDF"""
        try:
            import fitz

            # Open the PDF
            pdf = fitz.open(input_file)
            total_matches = 0

            # Define colors
            color_map = {
                "yellow": (1, 1, 0),
                "red": (1, 0, 0),
                "green": (0, 1, 0),
                "blue": (0, 0, 1),
                "purple": (0.7, 0, 0.7),
            }

            fill_color = color_map.get(color, (1, 1, 0))

            # Process pages
            page_range = pages if pages else range(len(pdf))

            for page_num in page_range:
                if page_num < len(pdf):
                    page = pdf[page_num]

                    # Search for text
                    text_instances = page.search_for(search_text)

                    for inst in text_instances:
                        total_matches += 1

                        if action == "Highlight":
                            highlight = page.add_highlight_annot(inst)
                            highlight.set_opacity(opacity)
                            highlight.set_colors(stroke=None, fill=fill_color)
                            highlight.update()
                        elif action == "Underline":
                            highlight = page.add_underline_annot(inst)
                            highlight.set_opacity(opacity)
                            highlight.set_colors(stroke=fill_color)
                            highlight.update()
                        elif action == "Strikeout":
                            highlight = page.add_strikeout_annot(inst)
                            highlight.set_opacity(opacity)
                            highlight.set_colors(stroke=fill_color)
                            highlight.update()
                        elif action == "Redact":
                            page.add_redact_annot(
                                inst, text=" ", fill=(0, 0, 0)
                            )

                    # Apply redactions if needed
                    if action == "Redact":
                        page.apply_redactions()

            # Save output
            output_file = os.path.splitext(input_file)[0] + "_highlighted.pdf"
            pdf.save(output_file)
            pdf.close()

            return True

        except Exception as e:
            self.logger.error(f"Fallback highlighting failed: {e}")
            return False

    def _convert_to_docx_fallback(self, input_file, output_file, pages=None):
        """Fallback DOCX conversion implementation"""
        try:
            QMessageBox.information(
                self.parent_widget,
                "Conversion Information",
                "DOCX conversion functionality requires additional dependencies.\n\n"
                "To enable DOCX conversion, install:\n"
                "- pip install pdf2docx\n\n"
                "For now, a basic text extraction will be performed.",
            )

            # Perform basic text extraction instead
            import fitz

            pdf = fitz.open(input_file)
            text_content = []

            page_range = pages if pages else range(len(pdf))

            for page_num in page_range:
                if page_num < len(pdf):
                    page = pdf[page_num]
                    text_content.append(f"=== Page {page_num + 1} ===\n")
                    text_content.append(page.get_text())
                    text_content.append("\n\n")

            pdf.close()

            # Save as text file with .docx extension
            text_output = os.path.splitext(output_file)[0] + "_text.txt"
            with open(text_output, "w", encoding="utf-8") as f:
                f.writelines(text_content)

            return True

        except Exception as e:
            self.logger.error(f"Fallback DOCX conversion failed: {e}")
            return False

    def _convert_to_image_fallback(
        self, input_file, output_dir, pages=None, image_format="png", dpi=300
    ):
        """Fallback image conversion implementation using PyMuPDF"""
        try:
            import fitz

            # Open the PDF
            pdf = fitz.open(input_file)
            output_files = []

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Process pages
            page_range = pages if pages else range(len(pdf))

            for page_num in page_range:
                if page_num < len(pdf):
                    page = pdf[page_num]

                    # Create pixmap with specified DPI
                    zoom = dpi / 72  # 72 is the default DPI
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)

                    # Save image
                    output_file = os.path.join(
                        output_dir, f"page_{page_num + 1}.{image_format}"
                    )
                    pix.save(output_file)
                    output_files.append(output_file)

            pdf.close()
            return True

        except Exception as e:
            self.logger.error(f"Fallback image conversion failed: {e}")
            return False

    def _view_pdf_fallback(self, input_file):
        """Fallback PDF viewer implementation using basic display"""
        try:
            import fitz
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtWidgets import (
                QDialog,
                QGraphicsScene,
                QGraphicsView,
                QHBoxLayout,
                QLabel,
                QPushButton,
                QScrollArea,
                QVBoxLayout,
            )

            # Create simple viewer dialog
            viewer_dialog = QDialog(self.parent_widget)
            viewer_dialog.setWindowTitle(
                f"PDF Viewer - {os.path.basename(input_file)}"
            )
            viewer_dialog.resize(800, 600)

            layout = QVBoxLayout(viewer_dialog)

            # Navigation controls
            nav_layout = QHBoxLayout()
            prev_btn = QPushButton("Previous")
            next_btn = QPushButton("Next")
            page_label = QLabel("Page 1 of 1")

            nav_layout.addWidget(prev_btn)
            nav_layout.addWidget(page_label)
            nav_layout.addWidget(next_btn)
            layout.addLayout(nav_layout)

            # PDF display area
            graphics_view = QGraphicsView()
            scene = QGraphicsScene()
            graphics_view.setScene(scene)
            layout.addWidget(graphics_view)

            # Open PDF and display first page
            doc = fitz.open(input_file)
            current_page = 0
            total_pages = len(doc)

            def show_page():
                nonlocal current_page
                if 0 <= current_page < total_pages:
                    page = doc[current_page]
                    pix = page.get_pixmap()

                    # Convert to QPixmap
                    from PyQt5.QtGui import QImage

                    fmt = (
                        QImage.Format_RGBA8888
                        if pix.alpha
                        else QImage.Format_RGB888
                    )
                    img = QImage(
                        pix.samples, pix.width, pix.height, pix.stride, fmt
                    )
                    pixmap = QPixmap.fromImage(img)

                    scene.clear()
                    scene.addPixmap(pixmap)
                    graphics_view.fitInView(
                        scene.itemsBoundingRect(), Qt.KeepAspectRatio
                    )

                    page_label.setText(
                        f"Page {current_page + 1} of {total_pages}"
                    )
                    prev_btn.setEnabled(current_page > 0)
                    next_btn.setEnabled(current_page < total_pages - 1)

            def prev_page():
                nonlocal current_page
                if current_page > 0:
                    current_page -= 1
                    show_page()

            def next_page():
                nonlocal current_page
                if current_page < total_pages - 1:
                    current_page += 1
                    show_page()

            prev_btn.clicked.connect(prev_page)
            next_btn.clicked.connect(next_page)

            # Show first page
            show_page()

            # Show viewer
            viewer_dialog.exec_()
            doc.close()

            return True

        except Exception as e:
            self.logger.error(f"Fallback PDF viewer failed: {e}")
            QMessageBox.critical(
                self.parent_widget,
                "Viewer Error",
                f"Failed to open PDF viewer:\n{str(e)}",
            )
            return False

    def _analyze_pdf_fallback(
        self,
        input_file,
        extract_metadata=True,
        extract_text=True,
        analyze_structure=True,
        analyze_images=False,
    ):
        """Fallback PDF analysis implementation using PyMuPDF"""
        try:
            import fitz

            # Open PDF
            doc = fitz.open(input_file)
            analysis_results = {}

            # Extract metadata
            if extract_metadata:
                metadata = doc.metadata
                analysis_results["metadata"] = metadata
                analysis_results["page_count"] = len(doc)

            # Extract text
            if extract_text:
                total_text = ""
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    total_text += page.get_text() + " "

                analysis_results["total_text_length"] = len(total_text)
                analysis_results["word_count"] = len(total_text.split())

            # Analyze structure
            if analyze_structure:
                analysis_results["page_dimensions"] = []
                analysis_results["total_size"] = os.path.getsize(input_file)

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    analysis_results["page_dimensions"].append(
                        {
                            "page": page_num + 1,
                            "width": page.rect.width,
                            "height": page.rect.height,
                        }
                    )

            # Analyze images
            if analyze_images:
                image_count = 0
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    image_list = page.get_images()
                    image_count += len(image_list)
                analysis_results["image_count"] = image_count

            doc.close()

            # Show results
            self._show_analysis_results(analysis_results, input_file)

            return True

        except Exception as e:
            self.logger.error(f"Fallback PDF analysis failed: {e}")
            QMessageBox.critical(
                self.parent_widget,
                "Analysis Error",
                f"Failed to analyze PDF:\n{str(e)}",
            )
            return False

    def _show_analysis_results(self, results, input_file):
        """Show analysis results in a dialog"""
        try:
            from PyQt5.QtWidgets import (
                QDialog,
                QPushButton,
                QTextEdit,
                QVBoxLayout,
            )

            # Create results dialog
            results_dialog = QDialog(self.parent_widget)
            results_dialog.setWindowTitle(
                f"PDF Analysis Results - {os.path.basename(input_file)}"
            )
            results_dialog.resize(600, 500)

            layout = QVBoxLayout(results_dialog)

            # Results text area
            results_text = QTextEdit()
            results_text.setReadOnly(True)

            # Format results
            result_str = (
                f"PDF Analysis Results for: {os.path.basename(input_file)}\n"
            )
            result_str += "=" * 60 + "\n\n"

            if "metadata" in results:
                result_str += "METADATA:\n"
                metadata = results["metadata"]
                for key, value in metadata.items():
                    if value:
                        result_str += f"  {key}: {value}\n"
                result_str += "\n"

            if "page_count" in results:
                result_str += f"DOCUMENT STRUCTURE:\n"
                result_str += f"  Total Pages: {results['page_count']}\n"

            if "total_size" in results:
                size_mb = results["total_size"] / (1024 * 1024)
                result_str += f"  File Size: {size_mb:.2f} MB\n"

            if "page_dimensions" in results:
                result_str += f"  Page Dimensions:\n"
                for dim in results["page_dimensions"][
                    :5
                ]:  # Show first 5 pages
                    result_str += f"    Page {dim['page']}: {dim['width']:.1f} x {dim['height']:.1f} pts\n"
                if len(results["page_dimensions"]) > 5:
                    result_str += f"    ... and {len(results['page_dimensions']) - 5} more pages\n"
                result_str += "\n"

            if "total_text_length" in results:
                result_str += f"TEXT ANALYSIS:\n"
                result_str += (
                    f"  Total Characters: {results['total_text_length']:,}\n"
                )
                result_str += f"  Total Words: {results['word_count']:,}\n"
                avg_words_per_page = results["word_count"] / results.get(
                    "page_count", 1
                )
                result_str += (
                    f"  Average Words per Page: {avg_words_per_page:.1f}\n\n"
                )

            if "image_count" in results:
                result_str += f"IMAGE ANALYSIS:\n"
                result_str += f"  Total Images: {results['image_count']}\n\n"

            results_text.setPlainText(result_str)
            layout.addWidget(results_text)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(results_dialog.close)
            layout.addWidget(close_btn)

            # Show dialog
            results_dialog.exec_()

        except Exception as e:
            self.logger.error(f"Error showing analysis results: {e}")
            QMessageBox.information(
                self.parent_widget,
                "Analysis Complete",
                f"PDF analysis completed for: {os.path.basename(input_file)}",
            )


def integrate_functional_pdf_operations(enhanced_pdf_widget):
    """
    Integrate functional PDF operations into the enhanced PDF tools widget
    Replaces placeholder implementations with actual functionality
    """
    try:
        if not PDF_COMPONENTS_AVAILABLE:
            logger.warning(
                "PDF components not available - using basic implementations"
            )
            return False

        logger.info("Integrating functional PDF operations")

        # Create functional integration instance
        integration = PDFFunctionalIntegration(enhanced_pdf_widget)

        # Replace placeholder implementations with functional ones
        enhanced_pdf_widget._merge_pdfs_impl = (
            integration.merge_pdfs_functional
        )
        enhanced_pdf_widget._split_pdf_impl = integration.split_pdf_functional
        enhanced_pdf_widget._sign_pdf_impl = integration.sign_pdf_functional

        # Replace extraction placeholder implementations
        enhanced_pdf_widget._extract_text_impl = (
            integration.extract_text_functional
        )
        enhanced_pdf_widget._extract_images_impl = (
            integration.extract_images_functional
        )
        enhanced_pdf_widget._extract_metadata_impl = (
            integration.extract_metadata_functional
        )
        enhanced_pdf_widget._extract_tables_impl = (
            integration.extract_tables_functional
        )
        enhanced_pdf_widget._extract_links_impl = (
            integration.extract_links_functional
        )

        # Replace security placeholder implementations (Phase 2.3)
        enhanced_pdf_widget._encrypt_pdf_impl = (
            integration.encrypt_pdf_functional
        )
        enhanced_pdf_widget._decrypt_pdf_impl = (
            integration.decrypt_pdf_functional
        )
        enhanced_pdf_widget._sign_digital_pdf_impl = (
            integration.sign_digital_pdf_functional
        )
        enhanced_pdf_widget._get_security_info_impl = (
            integration.get_security_info_functional
        )

        # Replace enhancement placeholder implementations (Phase 2.4)
        enhanced_pdf_widget._add_watermark_impl = (
            integration.add_watermark_functional
        )
        enhanced_pdf_widget._perform_ocr_impl = (
            integration.perform_ocr_functional
        )
        enhanced_pdf_widget._highlight_content_impl = (
            integration.highlight_content_functional
        )

        # Replace conversion placeholder implementations (Phase 2.5)
        enhanced_pdf_widget._convert_to_docx_impl = (
            integration.convert_to_docx_functional
        )
        enhanced_pdf_widget._convert_to_image_impl = (
            integration.convert_to_image_functional
        )
        enhanced_pdf_widget._convert_html_to_pdf_impl = (
            integration.convert_html_to_pdf_functional
        )

        # Replace view and analysis placeholder implementations (Phase 2.6)
        enhanced_pdf_widget._view_pdf_impl = integration.view_pdf_functional
        enhanced_pdf_widget._analyze_pdf_impl = (
            integration.analyze_pdf_functional
        )

        # Store integration instance for cleanup
        enhanced_pdf_widget._pdf_integration = integration

        # Override the cleanup method to include integration cleanup
        original_cleanup = getattr(enhanced_pdf_widget, "cleanup", None)

        def enhanced_cleanup():
            try:
                integration.cleanup()
                if original_cleanup:
                    original_cleanup()
            except Exception as e:
                logger.error(f"Error during enhanced cleanup: {e}")

        enhanced_pdf_widget.cleanup = enhanced_cleanup

        logger.info("Functional PDF operations integrated successfully")
        return True

    except Exception as e:
        logger.error(
            f"Failed to integrate functional PDF operations: {e}",
            exc_info=True,
        )
        return False


if __name__ == "__main__":
    # Test the integration
    import sys

    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    class TestWidget(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)

            merge_btn = QPushButton("Test Merge")
            split_btn = QPushButton("Test Split")
            sign_btn = QPushButton("Test Sign")

            layout.addWidget(merge_btn)
            layout.addWidget(split_btn)
            layout.addWidget(sign_btn)

            # Create integration
            self.integration = PDFFunctionalIntegration(self)

            # Connect buttons
            merge_btn.clicked.connect(self.integration.merge_pdfs_functional)
            split_btn.clicked.connect(self.integration.split_pdf_functional)
            sign_btn.clicked.connect(self.integration.sign_pdf_functional)

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("PDF Functional Integration Test")
    window.setCentralWidget(TestWidget())
    window.show()

    sys.exit(app.exec_())
