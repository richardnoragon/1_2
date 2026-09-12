import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import fitz
from log_config import setup_logger
from src.gui.components.loading_indicator import LoadingIndicator

# Set up logger
logger = setup_logger(__name__)


def add_watermark(
    input_file: str,
    watermark_text: str,
    pages: tuple = None,
    opacity: float = 0.5,
) -> bool:
    """Add watermark to PDF file"""
    try:
        logger.info("Starting watermark application")
        logger.debug(
            "Parameters - Input: %s, Text: %s, Pages: %s, Opacity: %f",
            input_file,
            watermark_text,
            pages,
            opacity,
        )

        # Check if input file exists
        if not os.path.exists(input_file):
            logger.error("Input file not found: %s", input_file)
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Open the PDF
        pdf = fitz.open(input_file)

        # Get pages to process
        if pages:
            page_list = list(pages)
        else:
            page_list = range(len(pdf))

        logger.info("Processing %d pages", len(page_list))

        for page_num in page_list:
            try:
                if page_num >= len(pdf):
                    logger.warning(
                        "Page %d out of range, skipping", page_num + 1
                    )
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
                logger.debug("Adding watermark to page %d", page_num + 1)
                page.insert_text(
                    (x, y),
                    watermark_text,
                    fontsize=36,
                    fontname="helv",
                    rotate=45,
                    opacity=opacity,
                )

            except Exception as e:
                logger.error(
                    "Error processing page %d: %s", page_num + 1, str(e)
                )
                continue

        # Save the output file
        output_file = os.path.splitext(input_file)[0] + "_watermarked.pdf"
        logger.info("Saving watermarked PDF to: %s", output_file)
        pdf.save(output_file)
        pdf.close()

        logger.info("Watermark application completed successfully")
        return True

    except Exception as e:
        logger.error("Error applying watermark: %s", str(e))
        raise


class WatermarkUI(QtWidgets.QMainWindow):
    def __init__(self, config=None):
        try:
            super(WatermarkUI, self).__init__()
            uic.loadUi("watermark.ui", self)

            self.config = config or {}

            # Add progress bar
            self.progressBar = LoadingIndicator(parent=self, message="Working...")
            self.statusBar().addPermanentWidget(self.progressBar)
            self.progressBar.hide()

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.watermarkButton.clicked.connect(self.apply_watermark)
            self.actionExit.triggered.connect(self.close)
            self.opacitySpinBox.valueChanged.connect(self.save_settings)
            self.watermarkEdit.textChanged.connect(self.save_settings)

            # Load saved settings
            self.load_settings()

            logger.info("Watermark tool initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize watermark tool: %s", str(e))
            raise

    def load_settings(self):
        """Load saved settings from config"""
        try:
            # Set opacity
            self.opacitySpinBox.setValue(
                float(self.config.get("opacity", 0.5))
            )

            # Set watermark text
            saved_text = self.config.get("watermark_text", "")
            self.watermarkEdit.setText(saved_text)

            # Load last directory
            self.last_directory = self.config.get("last_directory", "")

        except Exception as e:
            logger.error("Error loading settings: %s", str(e))

    def save_settings(self):
        """Save current settings to config"""
        try:
            from config_manager import ConfigManager

            config_manager = ConfigManager()

            settings = {
                "opacity": self.opacitySpinBox.value(),
                "watermark_text": self.watermarkEdit.text(),
                "last_directory": (
                    self.last_directory
                    if hasattr(self, "last_directory")
                    else ""
                ),
            }

            config_manager.set_module_config("watermark", settings)
            logger.debug("Settings saved successfully")

        except Exception as e:
            logger.error("Error saving settings: %s", str(e))

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select PDF File",
                self.last_directory,  # Use last directory
                "PDF Files (*.pdf)",
            )
            if filename:
                logger.info("Selected input file: %s", filename)
                self.last_directory = os.path.dirname(filename)
                self.inputFileEdit.setText(filename)
                self.save_settings()  # Save the new last directory
        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error selecting file: {str(e)}"
            )

    def apply_watermark(self):
        try:
            input_file = self.inputFileEdit.text()
            watermark_text = self.watermarkEdit.text()
            opacity = self.opacitySpinBox.value()

            if not input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Error", "Please select a PDF file first!"
                )
                return

            if not watermark_text:
                logger.warning("No watermark text provided")
                QMessageBox.warning(
                    self, "Error", "Please enter watermark text!"
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
                    logger.info("Watermarking specific pages: %s", pages)
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
            self.statusBar().showMessage("Loading document...")
            QtWidgets.QApplication.processEvents()

            try:
                # Document loading
                self.progressBar.set_progress(10)
                QtWidgets.QApplication.processEvents()

                # Create watermark
                self.progressBar.set_progress(20)
                self.statusBar().showMessage("Creating watermark...")
                QtWidgets.QApplication.processEvents()

                # Process pages
                self.progressBar.set_progress(30)
                self.statusBar().showMessage("Applying watermark...")
                QtWidgets.QApplication.processEvents()

                logger.info("Starting watermark process")
                success = add_watermark(
                    input_file=input_file,
                    watermark_text=watermark_text,
                    pages=pages,
                    opacity=opacity,
                )

                if success:
                    self.progressBar.set_progress(100)
                    logger.info("Watermark applied successfully")
                    QMessageBox.information(
                        self, "Success", "Watermark applied successfully!"
                    )
                    self.statusBar().showMessage("Watermark complete", 3000)
                else:
                    logger.warning("Failed to apply watermark")
                    QMessageBox.warning(
                        self, "Warning", "Failed to apply watermark"
                    )
                    self.statusBar().showMessage("Watermark failed", 3000)

            except Exception as e:
                logger.error("Error during watermarking: %s", str(e))
                QMessageBox.critical(
                    self, "Error", f"Error applying watermark: {str(e)}"
                )
                self.statusBar().showMessage("Error during watermark", 3000)

        except Exception as e:
            logger.error("Error in watermark operation: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error in watermark operation: {str(e)}"
            )
            self.statusBar().showMessage("Error occurred", 3000)

        finally:
            self.progressBar.stop()


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = WatermarkUI()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
