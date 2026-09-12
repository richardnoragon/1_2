import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pdfplumber
from log_config import setup_logger

from src.gui.components.loading_indicator import LoadingIndicator

# Set up logger
logger = setup_logger(__name__)


def _parse_page_selection(
    pages: str | tuple[int, ...] | list[int] | None,
    total_pages: int,
) -> list[int] | None:
    if pages is None or pages == "":
        return list(range(total_pages))

    if isinstance(pages, (tuple, list)):
        return [int(page) for page in pages]

    try:
        page_list = []
        for part in pages.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                page_list.extend(range(start - 1, end))
            else:
                page_list.append(int(part) - 1)
        return page_list
    except ValueError:
        logger.error("Invalid page range format: %s", pages)
        QMessageBox.critical(None, "Error", "Invalid page range format")
        return None


def _extract_pages_text(pdf, page_list: list[int]) -> str:
    text_parts = []
    for page_index in page_list:
        try:
            if 0 <= page_index < len(pdf.pages):
                page_text = pdf.pages[page_index].extract_text()
                if page_text:
                    text_parts.append(
                        f"\n=== Page {page_index + 1} ===\n{page_text}\n"
                    )
                logger.debug("Extracted text from page %d", page_index + 1)
            else:
                logger.warning("Page %d out of range", page_index + 1)
        except Exception as e:
            logger.error(
                "Error extracting text from page %d: %s",
                page_index + 1,
                str(e),
            )
            QMessageBox.warning(
                None,
                "Warning",
                f"Error extracting text from page {page_index + 1}: {str(e)}",
            )
    return "".join(text_parts)


def _save_text(output_file: str, text: str) -> bool:
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info("Text saved to file: %s", output_file)
        return True
    except Exception as e:
        logger.error("Error saving text to file: %s", str(e))
        QMessageBox.critical(None, "Error", f"Error saving text to file: {str(e)}")
        return False


def extract_text_from_pdf(
    input_file: str, output_file: str = None, pages: str | tuple[int, ...] | list[int] | None = None
) -> str | bool:
    """Extract text from a PDF file"""
    try:
        logger.info("Starting text extraction from: %s", input_file)

        if not os.path.exists(input_file):
            logger.error("Input file not found: %s", input_file)
            QMessageBox.critical(None, "Error", f"Input file not found: {input_file}")
            return False

        try:
            with pdfplumber.open(input_file) as pdf:
                logger.debug(
                    "PDF opened successfully, pages: %d", len(pdf.pages)
                )

                page_list = _parse_page_selection(pages, len(pdf.pages))
                if page_list is None:
                    return False

                logger.debug("Processing pages: %s", page_list)
                text = _extract_pages_text(pdf, page_list)

                if output_file:
                    return _save_text(output_file, text)

                return text

        except Exception as e:
            logger.error("Error opening PDF: %s", str(e))
            QMessageBox.critical(None, "Error", f"Error opening PDF: {str(e)}")
            return False

    except Exception as e:
        logger.error(
            "Unexpected error during text extraction: %s",
            str(e),
            exc_info=True,
        )
        QMessageBox.critical(None, "Error", f"Unexpected error during text extraction: {str(e)}")
        return False


class ExtractTextUI(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(ExtractTextUI, self).__init__()
            logger.info("Initializing Extract Text UI")

            # Load UI
            uic.loadUi("extract_text.ui", self)
            logger.debug("UI file loaded successfully")

            # Add progress bar
            self.progressBar = LoadingIndicator(parent=self, message="Working...")
            self.statusBar().addPermanentWidget(self.progressBar)
            self.progressBar.hide()

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.extractButton.clicked.connect(self.extract_text)
            self.saveButton.clicked.connect(self.save_text)
            self.actionExit.triggered.connect(self.close)

            # Initialize state
            self.current_file = None
            self.extractButton.setEnabled(False)
            self.saveButton.setEnabled(False)

            logger.debug("UI signals connected successfully")
            self.show()

        except Exception as e:
            logger.error("Failed to initialize UI: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Failed to initialize UI: {str(e)}"
            )
            self.close()

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )

            if filename:
                logger.info("Selected input file: %s", filename)
                self.current_file = filename
                self.inputFileEdit.setText(filename)
                self.extractButton.setEnabled(True)
                self.outputText.clear()

        except Exception as e:
            logger.error("Error browsing file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error browsing file: {str(e)}"
            )

    def extract_text(self):
        try:
            if not self.current_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Warning", "Please select a PDF file first!"
                )
                return

            # Get page range if specified
            pages = None
            if self.pagesEdit.text():
                try:
                    pages = tuple(
                        int(p.strip()) - 1
                        for p in self.pagesEdit.text().split(",")
                    )
                    logger.info("Extracting from specific pages: %s", pages)
                except ValueError:
                    logger.error(
                        "Invalid page numbers format: %s",
                        self.pagesEdit.text(),
                    )
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Invalid page numbers! Use comma-separated numbers.",
                    )
                    return

            self.progressBar.start()
            self.progressBar.set_progress(0)
            self.outputText.clear()
            self.statusBar().showMessage("Loading document...")
            QtWidgets.QApplication.processEvents()

            try:
                # Initialize document
                self.progressBar.set_progress(20)
                self.statusBar().showMessage("Analyzing document...")
                QtWidgets.QApplication.processEvents()

                # Extract text
                self.progressBar.set_progress(40)
                self.statusBar().showMessage("Extracting text...")
                QtWidgets.QApplication.processEvents()

                result = extract_text_from_pdf(self.current_file, pages=pages)

                if isinstance(result, str):
                    self.progressBar.set_progress(100)
                    logger.info("Text extracted successfully")
                    self.outputText.setPlainText(result)
                    self.saveButton.setEnabled(True)
                    self.statusBar().showMessage(
                        "Text extraction complete", 3000
                    )
                else:
                    logger.warning("Text extraction failed")
                    QMessageBox.warning(
                        self, "Warning", "Failed to extract text!"
                    )
                    self.statusBar().showMessage(
                        "Text extraction failed", 3000
                    )

            except Exception as e:
                logger.error(
                    "Error during text extraction: %s", str(e), exc_info=True
                )
                QMessageBox.critical(
                    self, "Error", f"Error during text extraction: {str(e)}"
                )
                self.statusBar().showMessage("Error during extraction", 3000)

        except Exception as e:
            logger.error(
                "Error in extract operation: %s", str(e), exc_info=True
            )
            QMessageBox.critical(
                self, "Error", f"Error in extract operation: {str(e)}"
            )
            self.statusBar().showMessage("Error occurred", 3000)

        finally:
            self.progressBar.stop()

    def save_text(self):
        try:
            if not self.outputText.toPlainText():
                logger.warning("No text to save")
                QMessageBox.warning(self, "Warning", "No text to save!")
                return

            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Text File", "", "Text Files (*.txt)"
            )

            if filename:
                self.progressBar.start()
                self.progressBar.set_progress(0)
                self.statusBar().showMessage("Saving text...")
                QtWidgets.QApplication.processEvents()

                try:
                    logger.info("Saving text to: %s", filename)
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.outputText.toPlainText())

                    self.progressBar.set_progress(100)
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Text saved successfully!\nSaved to: {filename}",
                    )
                    self.statusBar().showMessage("Save complete", 3000)

                except Exception as e:
                    logger.error("Error saving text: %s", str(e))
                    QMessageBox.critical(
                        self, "Error", f"Error saving text: {str(e)}"
                    )
                    self.statusBar().showMessage("Error saving text", 3000)

        except Exception as e:
            logger.error("Error in save operation: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error in save operation: {str(e)}"
            )
            self.statusBar().showMessage("Error occurred", 3000)

        finally:
            self.progressBar.stop()


def main():
    try:
        logger.info("Starting Extract Text application")
        app = QtWidgets.QApplication(sys.argv)
        ExtractTextUI()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(
            "Application failed to start: %s", str(e), exc_info=True
        )
        QMessageBox.critical(
            None, "Fatal Error", f"Application failed to start: {str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
