import os
import fitz  # PyMuPDF
import io
from PIL import Image
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QFormLayout,
)
from log_config import setup_logger

from src.gui.components.loading_indicator import LoadingIndicator

# Set up logger
logger = setup_logger(__name__)


def extract_images(
    pdf_path: str,
    output_dir: str,
    min_width: int = 100,
    min_height: int = 100,
    format: str = "png",
) -> list:
    """Extract images from PDF file with size filtering"""
    try:
        logger.info("Starting image extraction from: %s", pdf_path)
        logger.debug(
            "Parameters - Min width: %d, Min height: %d, Format: %s",
            min_width,
            min_height,
            format,
        )

        # Check if input file exists
        if not os.path.exists(pdf_path):
            logger.error("Input file not found: %s", pdf_path)
            raise FileNotFoundError(f"Input file not found: {pdf_path}")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            logger.info("Creating output directory: %s", output_dir)
            os.makedirs(output_dir)

        # Open PDF
        pdf_document = fitz.open(pdf_path)
        extracted_images = []
        image_count = 0

        # Iterate through pages
        for page_num in range(len(pdf_document)):
            logger.debug("Processing page %d", page_num + 1)
            page = pdf_document[page_num]

            # Get images from page
            images = page.get_images()

            for img_index, img in enumerate(images, start=1):
                try:
                    # Get image data
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Load as PIL Image for processing
                    image = Image.open(io.BytesIO(image_bytes))

                    # Check image dimensions
                    if image.width >= min_width and image.height >= min_height:
                        image_count += 1
                        # Save image
                        output_path = os.path.join(
                            output_dir,
                            f"image_{page_num + 1}_{img_index}.{format}",
                        )
                        image.save(output_path, format=format.upper())
                        extracted_images.append(output_path)
                        logger.debug("Extracted image: %s", output_path)
                    else:
                        logger.debug(
                            "Skipping image (size too small): %dx%d",
                            image.width,
                            image.height,
                        )

                except Exception as e:
                    logger.error(
                        "Error processing image %d on page %d: %s",
                        img_index,
                        page_num + 1,
                        str(e),
                    )
                    continue

        pdf_document.close()
        logger.info(
            "Extraction completed. Extracted %d images", len(extracted_images)
        )
        return extracted_images

    except Exception as e:
        logger.error("Error in image extraction: %s", str(e))
        raise


class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            uic.loadUi("extract_image_cli.ui", self)

            # Add progress bar
            self.progressBar = LoadingIndicator(parent=self, message="Working...")
            self.statusBar().addPermanentWidget(self.progressBar)
            self.progressBar.hide()

            # Connect signals
            self.browseButton.clicked.connect(self.browse_pdf)
            self.browseOutputButton.clicked.connect(self.browse_output_dir)
            self.extractButton.clicked.connect(self.extract_images)
            self.actionExit.triggered.connect(self.close)

            logger.info("Image extractor initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize image extractor: %s", str(e))
            raise

    def browse_pdf(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )
            if filename:
                logger.info("Selected input file: %s", filename)
                self.pdfFileEdit.setText(filename)
        except Exception as e:
            logger.error("Error browsing for PDF: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error selecting PDF: {str(e)}"
            )

    def browse_output_dir(self):
        try:
            dirname = QFileDialog.getExistingDirectory(
                self, "Select Output Directory"
            )
            if dirname:
                logger.info("Selected output directory: %s", dirname)
                self.outputDirEdit.setText(dirname)
        except Exception as e:
            logger.error("Error selecting output directory: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error selecting directory: {str(e)}"
            )

    def extract_images(self):
        try:
            # Validate inputs
            pdf_file = self.pdfFileEdit.text()
            output_dir = self.outputDirEdit.text()

            if not pdf_file:
                logger.warning("No PDF file selected")
                QMessageBox.warning(
                    self, "Warning", "Please select a PDF file!"
                )
                return

            if not output_dir:
                logger.warning("No output directory selected")
                QMessageBox.warning(
                    self, "Warning", "Please select an output directory!"
                )
                return

            self.progressBar.start()
            self.progressBar.set_progress(0)
            self.statusBar().showMessage("Loading PDF...")
            QtWidgets.QApplication.processEvents()

            try:
                # Open PDF
                self.progressBar.set_progress(10)
                QtWidgets.QApplication.processEvents()

                doc = fitz.open(pdf_file)
                total_pages = doc.page_count

                self.progressBar.set_progress(20)
                self.statusBar().showMessage("Scanning for images...")
                QtWidgets.QApplication.processEvents()

                # Process each page
                images_found = 0
                for page_num in range(total_pages):
                    progress = 20 + int(
                        (page_num / total_pages) * 70
                    )  # 20-90% for page processing
                    self.progressBar.set_progress(progress)
                    self.statusBar().showMessage(
                        f"Processing page {page_num + 1} of {total_pages}..."
                    )
                    QtWidgets.QApplication.processEvents()

                    page = doc[page_num]
                    image_list = page.get_images()

                    for img_idx, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            base_image = doc.extract_image(xref)

                            if base_image:
                                image_bytes = base_image["image"]
                                image_ext = base_image["ext"]
                                image_filename = os.path.join(
                                    output_dir,
                                    f"image_p{page_num + 1}_{img_idx + 1}.{image_ext}",
                                )

                                with open(image_filename, "wb") as image_file:
                                    image_file.write(image_bytes)
                                images_found += 1

                        except Exception as e:
                            logger.error(
                                "Error extracting image %d from page %d: %s",
                                img_idx + 1,
                                page_num + 1,
                                str(e),
                            )
                            continue

                self.progressBar.set_progress(100)
                if images_found > 0:
                    logger.info(
                        "Successfully extracted %d images", images_found
                    )
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Successfully extracted {images_found} images!\nSaved to: {output_dir}",
                    )
                    self.statusBar().showMessage("Extraction complete", 3000)
                else:
                    logger.warning("No images found in document")
                    QMessageBox.warning(
                        self, "Warning", "No images found in document!"
                    )
                    self.statusBar().showMessage("No images found", 3000)

                doc.close()

            except Exception as e:
                logger.error("Error processing PDF: %s", str(e))
                QMessageBox.critical(
                    self, "Error", f"Error processing PDF: {str(e)}"
                )
                self.statusBar().showMessage("Error during extraction", 3000)

        except Exception as e:
            logger.error("Error in extract operation: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error in extract operation: {str(e)}"
            )
            self.statusBar().showMessage("Error occurred", 3000)

        finally:
            self.progressBar.stop()


def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    import sys
    from PyQt5 import uic, QtWidgets

    main()
