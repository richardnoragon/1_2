import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import fitz  # PyMuPDF
from PIL import Image
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)


def convert_pdf2img(input_file: str, pages: tuple = None) -> list:
    """Convert PDF to images"""
    try:
        logger.info("Starting PDF to image conversion: %s", input_file)
        logger.debug("Pages to convert: %s", pages if pages else "all")

        # Check if input file exists
        if not os.path.exists(input_file):
            logger.error("Input file not found: %s", input_file)
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Create output directory if it doesn't exist
        output_dir = "converted_images"
        if not os.path.exists(output_dir):
            logger.info("Creating output directory: %s", output_dir)
            os.makedirs(output_dir)

        # Open PDF file
        pdf_file = fitz.open(input_file)
        output_files = []

        # Get pages to process
        if pages:
            page_list = list(pages)
        else:
            page_list = range(len(pdf_file))

        logger.info("Converting %d pages", len(page_list))

        # Iterate through pages
        for page_num in page_list:
            try:
                if page_num >= len(pdf_file):
                    logger.warning(
                        "Page %d out of range, skipping", page_num + 1
                    )
                    continue

                page = pdf_file[page_num]

                # Get page pixmap
                pix = page.get_pixmap()

                # Convert to PIL Image
                img = Image.frombytes(
                    "RGB", [pix.width, pix.height], pix.samples
                )

                # Save image
                output_file = os.path.join(
                    output_dir, f"page_{page_num + 1}.png"
                )
                img.save(output_file)
                output_files.append(output_file)
                logger.debug(
                    "Converted page %d to %s", page_num + 1, output_file
                )

            except Exception as e:
                logger.error(
                    "Error converting page %d: %s", page_num + 1, str(e)
                )
                continue

        pdf_file.close()
        logger.info(
            "Conversion completed. Created %d images", len(output_files)
        )
        return output_files

    except Exception as e:
        logger.error("Error in PDF to image conversion: %s", str(e))
        raise


class ConvertToImageUI(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(ConvertToImageUI, self).__init__()
            uic.loadUi("convert_to_image.ui", self)

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.convertButton.clicked.connect(self.convert_file)
            self.actionExit.triggered.connect(self.close)

            logger.info("PDF to Image converter initialized")
            self.show()
        except Exception as e:
            logger.error(
                "Failed to initialize PDF to Image converter: %s", str(e)
            )
            raise

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )
            if filename:
                logger.info("Selected input file: %s", filename)
                self.inputFileEdit.setText(filename)
        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error selecting file: {str(e)}"
            )

    def convert_file(self):
        try:
            input_file = self.inputFileEdit.text()
            if not input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Error", "Please select a PDF file first!"
                )
                return

            pages_text = self.pagesEdit.text()
            pages = None
            if pages_text:
                try:
                    pages = tuple(
                        int(p.strip()) - 1 for p in pages_text.split(",")
                    )
                    logger.info("Converting specific pages: %s", pages)
                except ValueError:
                    logger.error("Invalid page numbers format: %s", pages_text)
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Invalid page numbers! Use comma-separated numbers.",
                    )
                    return

            try:
                output_files = convert_pdf2img(input_file, pages)
                success_msg = (
                    "Conversion completed successfully!\n\n"
                    + "\n".join(f"Created: {f}" for f in output_files)
                )
                logger.info("Conversion successful")
                self.outputText.setText(success_msg)
            except Exception as e:
                logger.error("Error during conversion: %s", str(e))
                QMessageBox.critical(
                    self, "Error", f"Error during conversion: {str(e)}"
                )

        except Exception as e:
            logger.error("Error in convert operation: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error in convert operation: {str(e)}"
            )


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = ConvertToImageUI()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
