import sys
import pdfkit
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

class HtmlToPdfConverter(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(HtmlToPdfConverter, self).__init__()
            uic.loadUi('convert_html_to_pdf.ui', self)
            
            # Connect buttons to functions
            self.convertUrlButton.clicked.connect(self.convert_from_url)
            self.convertFileButton.clicked.connect(self.convert_from_file)
            self.convertHtmlButton.clicked.connect(self.convert_from_html)
            self.browseButton.clicked.connect(self.browse_file)
            self.actionExit.triggered.connect(self.close)
            
            logger.info("HTML to PDF converter initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize HTML to PDF converter: %s", str(e))
            raise

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select HTML File",
                "",
                "HTML Files (*.html *.htm);;All Files (*.*)"
            )
            if filename:
                logger.info("Selected HTML file: %s", filename)
                self.fileInput.setText(filename)
        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            self.show_error(f"Error selecting file: {str(e)}")

    def save_pdf_dialog(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF File",
                "",
                "PDF Files (*.pdf);;All Files (*.*)"
            )
            if filename:
                logger.info("Selected output PDF file: %s", filename)
            return filename
        except Exception as e:
            logger.error("Error in save dialog: %s", str(e))
            self.show_error(f"Error selecting output file: {str(e)}")
            return None

    def show_error(self, message):
        logger.error(message)
        QMessageBox.critical(self, "Error", message)

    def show_success(self, message):
        logger.info(message)
        QMessageBox.information(self, "Success", message)

    def convert_from_url(self):
        url = self.urlInput.text()
        if not url:
            logger.warning("No URL provided")
            self.show_error("Please enter a URL")
            return
            
        output_file = self.save_pdf_dialog()
        if output_file:
            try:
                logger.info("Converting URL to PDF: %s -> %s", url, output_file)
                self.statusLabel.setText("Converting URL to PDF...")
                pdfkit.from_url(url, output_file, verbose=True)
                self.statusLabel.setText("Ready")
                self.show_success("PDF created successfully!")
                logger.info("URL conversion successful")
            except Exception as e:
                logger.error("Error converting URL: %s", str(e))
                self.show_error(f"Error converting URL: {str(e)}")
                self.statusLabel.setText("Error occurred")

    def convert_from_file(self):
        input_file = self.fileInput.text()
        if not input_file:
            logger.warning("No input file selected")
            self.show_error("Please select an HTML file")
            return
            
        output_file = self.save_pdf_dialog()
        if output_file:
            try:
                logger.info("Converting HTML file to PDF: %s -> %s", input_file, output_file)
                self.statusLabel.setText("Converting file to PDF...")
                pdfkit.from_file(input_file, output_file, verbose=True)
                self.statusLabel.setText("Ready")
                self.show_success("PDF created successfully!")
                logger.info("File conversion successful")
            except Exception as e:
                logger.error("Error converting file: %s", str(e))
                self.show_error(f"Error converting file: %str(e)")
                self.statusLabel.setText("Error occurred")

    def convert_from_html(self):
        html_content = self.htmlInput.toPlainText()
        if not html_content:
            logger.warning("No HTML content provided")
            self.show_error("Please enter HTML content")
            return
            
        output_file = self.save_pdf_dialog()
        if output_file:
            try:
                logger.info("Converting HTML content to PDF: %s", output_file)
                self.statusLabel.setText("Converting HTML to PDF...")
                pdfkit.from_string(html_content, output_file, verbose=True)
                self.statusLabel.setText("Ready")
                self.show_success("PDF created successfully!")
                logger.info("HTML content conversion successful")
            except Exception as e:
                logger.error("Error converting HTML: %s", str(e))
                self.show_error(f"Error converting HTML: %s", str(e))
                self.statusLabel.setText("Error occurred")

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = HtmlToPdfConverter()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()