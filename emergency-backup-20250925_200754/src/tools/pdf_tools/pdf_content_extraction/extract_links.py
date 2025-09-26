import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import QtWidgets, uic
import pikepdf
import os
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)


class ExtractLinksUI(QMainWindow):
    def __init__(self):
        try:
            super(ExtractLinksUI, self).__init__()
            uic.loadUi("extract_links.ui", self)

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.extractButton.clicked.connect(self.extract_links)
            self.actionExit.triggered.connect(self.close)

            logger.info("Link extractor initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize link extractor: %s", str(e))
            raise

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select PDF file", "", "PDF Files (*.pdf)"
            )
            if filename:
                logger.info("Selected input file: %s", filename)
                self.inputFileEdit.setText(filename)
        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error selecting file: {str(e)}"
            )

    def extract_links(self):
        try:
            input_file = self.inputFileEdit.text()
            if not input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Error", "Please select a PDF file first!"
                )
                return

            try:
                # Create urls directory if it doesn't exist
                if not os.path.exists("urls"):
                    logger.info("Creating urls directory")
                    os.makedirs("urls")

                logger.info("Opening PDF file: %s", input_file)
                pdf_file = pikepdf.Pdf.open(input_file)
                urls = []

                # Extract URLs
                logger.info("Starting URL extraction")
                for page_num, page in enumerate(pdf_file.pages):
                    logger.debug("Processing page %d", page_num + 1)
                    for annots in page.get("/Annots", []):
                        if isinstance(annots, pikepdf.Array):
                            continue
                        uri = annots.get("/A", {}).get("/URI")
                        if uri is not None:
                            urls.append(str(uri))
                            logger.debug("Found URL: %s", uri)
                            self.outputText.append(f"[+] URL Found: {uri}")

                # Save URLs to file
                output_filename = os.path.join(
                    "urls", os.path.basename(input_file) + ".txt"
                )
                logger.info("Saving URLs to: %s", output_filename)
                with open(output_filename, "w") as f:
                    for url in urls:
                        f.write(url + "\n")

                # Move PDF file if requested
                try:
                    dest_path = os.path.join(
                        "urls", os.path.basename(input_file)
                    )
                    logger.info("Moving PDF file to: %s", dest_path)
                    os.rename(input_file, dest_path)
                except Exception as e:
                    logger.warning("Could not move PDF file: %s", str(e))

                self.outputText.append(
                    f"\n[*] Total URLs extracted: {len(urls)}"
                )
                logger.info("Extraction completed. Found %d URLs", len(urls))
                pdf_file.close()

            except Exception as e:
                logger.error("Error during extraction: %s", str(e))
                QMessageBox.critical(
                    self, "Error", f"An error occurred: {str(e)}"
                )

        except Exception as e:
            logger.error("Error in extract operation: %s", str(e))
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


def main():
    try:
        app = QApplication(sys.argv)
        window = ExtractLinksUI()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
