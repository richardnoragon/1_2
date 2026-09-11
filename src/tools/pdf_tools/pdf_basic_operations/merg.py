import os
import pikepdf
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from log_config import setup_logger

from src.gui.components.loading_indicator import LoadingIndicator

# Set up logger
logger = setup_logger(__name__)


def merge_pdfs(input_files: list, output_file: str) -> bool:
    """Merge multiple PDF files into one"""
    try:
        logger.info("Starting PDF merge operation")
        logger.debug("Input files: %s", input_files)
        logger.debug("Output file: %s", output_file)

        if not input_files:
            logger.error("No input files provided")
            QMessageBox.critical(None, "Error", "No input files provided")
            return False

        logger.info(
            "Starting merge of %d files into: %s",
            len(input_files),
            output_file,
        )
        pdf = pikepdf.Pdf.new()

        # Process each input file
        for input_file in input_files:
            try:
                logger.debug("Processing file: %s", input_file)
                src = pikepdf.Pdf.open(input_file)
                pdf.pages.extend(src.pages)
                logger.debug("Successfully added pages from: %s", input_file)
            except FileNotFoundError:
                logger.error("File not found: %s", input_file)
                QMessageBox.critical(
                    None, "Error", f"File not found: {input_file}"
                )
                return False
            except pikepdf.PdfError as e:
                logger.error("Error processing PDF %s: %s", input_file, str(e))
                QMessageBox.critical(
                    None,
                    "Error",
                    f"Error processing PDF {input_file}: {str(e)}",
                )
                return False
            except Exception as e:
                logger.error(
                    "Error processing file %s: %s", input_file, str(e)
                )
                QMessageBox.critical(
                    None,
                    "Error",
                    f"Error processing file %s: %s",
                    input_file,
                    str(e),
                )
                return False

        # Save merged PDF
        try:
            pdf.save(output_file)
            logger.info("Successfully merged files into: %s", output_file)
            return True
        except PermissionError:
            logger.error(
                "Permission denied when saving output file: %s", output_file
            )
            QMessageBox.critical(
                None,
                "Error",
                f"Permission denied when saving output file: %s",
                output_file,
            )
        except Exception as e:
            logger.error("Error saving merged file: %s", str(e))
            QMessageBox.critical(
                None, "Error", f"Error saving merged file: %s", str(e)
            )
        return False

    except Exception as e:
        logger.error(
            "Unexpected error during merge operation: %s",
            str(e),
            exc_info=True,
        )
        QMessageBox.critical(
            None,
            "Error",
            f"Unexpected error during merge operation: %s",
            str(e),
        )
        return False


class MergeUI(QMainWindow):
    def __init__(self):
        try:
            super(MergeUI, self).__init__()
            logger.info("Initializing Merge UI")

            # Load UI file
            uic.loadUi("merg.ui", self)
            logger.debug("UI file loaded successfully")

            # Initialize file list
            self.files = []

            # Add progress bar
            self.progressBar = LoadingIndicator(parent=self, message="Working...")
            self.statusBar().addPermanentWidget(self.progressBar)
            self.progressBar.hide()

            # Connect signals
            self.addButton.clicked.connect(self.add_files)
            self.removeButton.clicked.connect(self.remove_file)
            self.mergeButton.clicked.connect(self.merge_files)
            self.clearButton.clicked.connect(self.clear_files)
            self.actionExit.triggered.connect(self.close)
            self.upButton.clicked.connect(self.move_up)
            self.downButton.clicked.connect(self.move_down)

            # Initially disable buttons that need files
            self.update_button_states()

            logger.info("Merge UI initialized successfully")
            self.show()

        except Exception as e:
            logger.error("Failed to initialize UI: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Failed to initialize UI: {str(e)}"
            )
            self.close()

    def update_button_states(self):
        """Update enabled/disabled state of buttons based on selection"""
        has_files = len(self.files) > 0
        has_selection = self.fileList.currentRow() >= 0

        self.mergeButton.setEnabled(has_files)
        self.clearButton.setEnabled(has_files)
        self.removeButton.setEnabled(has_selection)
        self.upButton.setEnabled(
            has_selection and self.fileList.currentRow() > 0
        )
        self.downButton.setEnabled(
            has_selection and self.fileList.currentRow() < len(self.files) - 1
        )

        logger.debug(
            "Updated button states: has_files=%s, has_selection=%s",
            has_files,
            has_selection,
        )

    def add_files(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select PDF Files", "", "PDF Files (*.pdf)"
            )

            if files:
                logger.info("Adding %d files", len(files))
                self.files.extend(files)
                self.fileList.clear()
                self.fileList.addItems(
                    [os.path.basename(f) for f in self.files]
                )
                self.update_button_states()
                logger.debug("Files added successfully")

        except Exception as e:
            logger.error("Error adding files: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error adding files: %s", str(e)
            )

    def remove_file(self):
        try:
            current = self.fileList.currentRow()
            if current >= 0:
                logger.debug("Removing file at index %d", current)
                del self.files[current]
                self.fileList.takeItem(current)
                self.update_button_states()
                logger.info("Removed file at index %d", current)
        except Exception as e:
            logger.error("Error removing file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error removing file: %s", str(e)
            )

    def clear_files(self):
        try:
            logger.debug("Clearing file list")
            self.files.clear()
            self.fileList.clear()
            self.update_button_states()
            logger.info("Cleared file list")
        except Exception as e:
            logger.error("Error clearing files: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error clearing files: %s", str(e)
            )

    def move_up(self):
        try:
            current = self.fileList.currentRow()
            if current > 0:
                logger.debug("Moving file up from index %d", current)
                self.files[current], self.files[current - 1] = (
                    self.files[current - 1],
                    self.files[current],
                )
                item = self.fileList.takeItem(current)
                self.fileList.insertItem(current - 1, item)
                self.fileList.setCurrentRow(current - 1)
                self.update_button_states()
                logger.info("Moved file up from index %d", current)
        except Exception as e:
            logger.error("Error moving file up: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error moving file up: %s", str(e)
            )

    def move_down(self):
        try:
            current = self.fileList.currentRow()
            if current < len(self.files) - 1:
                logger.debug("Moving file down from index %d", current)
                self.files[current], self.files[current + 1] = (
                    self.files[current + 1],
                    self.files[current],
                )
                item = self.fileList.takeItem(current)
                self.fileList.insertItem(current + 1, item)
                self.fileList.setCurrentRow(current + 1)
                self.update_button_states()
                logger.info("Moved file down from index %d", current)
        except Exception as e:
            logger.error("Error moving file down: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error moving file down: %s", str(e)
            )

    def merge_files(self):
        try:
            if not self.files:
                logger.warning("No files to merge")
                QMessageBox.warning(
                    self, "Warning", "Please add files to merge first!"
                )
                return

            output_file, _ = QFileDialog.getSaveFileName(
                self, "Save Merged PDF", "", "PDF Files (*.pdf)"
            )

            if output_file:
                self.progressBar.show()
                self.progressBar.setValue(0)
                self.statusBar().showMessage("Preparing to merge PDFs...")
                QtWidgets.QApplication.processEvents()

                logger.info("Starting merge operation to: %s", output_file)

                total_files = len(self.files)
                for i, file in enumerate(self.files, 1):
                    progress = int(
                        (i / total_files) * 90
                    )  # Leave 10% for final operations
                    self.progressBar.setValue(progress)
                    self.statusBar().showMessage(
                        f"Processing file {i} of {total_files}..."
                    )
                    QtWidgets.QApplication.processEvents()

                self.progressBar.setValue(95)
                self.statusBar().showMessage("Finalizing merge...")
                QtWidgets.QApplication.processEvents()

                if merge_pdfs(self.files, output_file):
                    self.progressBar.setValue(100)
                    logger.info("Merge completed successfully")
                    QMessageBox.information(
                        self, "Success", "PDFs merged successfully!"
                    )
                    self.statusBar().showMessage("Merge complete", 3000)
                else:
                    logger.warning("Merge operation failed")
                    QMessageBox.warning(
                        self, "Warning", "Failed to merge PDFs!"
                    )
                    self.statusBar().showMessage("Merge failed", 3000)

                self.progressBar.hide()

        except Exception as e:
            logger.error(
                "Error during merge operation: %s", str(e), exc_info=True
            )
            QMessageBox.critical(
                self, "Error", f"Error during merge operation: %s", str(e)
            )
            self.statusBar().showMessage("Error during merge", 3000)
            self.progressBar.hide()


def main():
    try:
        logger.info("Starting Merge PDF application")
        app = QApplication(sys.argv)
        window = MergeUI()
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
