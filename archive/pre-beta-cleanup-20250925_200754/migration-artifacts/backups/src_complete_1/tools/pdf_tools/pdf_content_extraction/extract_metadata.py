import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic
import pikepdf
import datetime
from zoneinfo import ZoneInfo
import re
import os
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

def transform_date(date_str: str) -> str:
    """Transform PDF date format to readable format"""
    try:
        # Remove 'D:' prefix and timezone if present
        date_str = date_str.replace('D:', '')
        # Extract components
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(date_str[8:10])
        minute = int(date_str[10:12])
        second = int(date_str[12:14])
        
        # Create datetime object
        dt = datetime.datetime(year, month, day, hour, minute, second)
        logger.debug("Transformed date %s to %s", date_str, dt.isoformat())
        return dt.isoformat()
    except Exception as e:
        logger.error("Error transforming date %s: %s", date_str, str(e))
        return date_str

class MetadataExtractorUI(QMainWindow):
    def __init__(self):
        try:
            super(MetadataExtractorUI, self).__init__()
            uic.loadUi('extract_metadata.ui', self)
            
            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.extractButton.clicked.connect(self.extract_metadata)
            self.actionExit.triggered.connect(self.close)
            
            # Initially disable extract button
            self.extractButton.setEnabled(False)
            
            logger.info("Metadata extractor initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize metadata extractor: %s", str(e))
            QMessageBox.critical(self, "Error", f"Failed to initialize UI: {str(e)}")
            self.close()

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, 
                "Select PDF file", 
                "", 
                "PDF Files (*.pdf)"
            )
            if filename:
                logger.info("Selected input file: %s", filename)
                self.inputFileEdit.setText(filename)
                self.extractButton.setEnabled(True)
                self.outputText.clear()
        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error browsing file: {str(e)}")

    def extract_metadata(self):
        try:
            input_file = self.inputFileEdit.text()
            if not input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(self, "Warning", "Please select a PDF file first")
                return
                
            if not os.path.exists(input_file):
                logger.error("File not found: %s", input_file)
                QMessageBox.critical(self, "Error", f"File not found: {input_file}")
                return
                
            self.statusBar().showMessage("Extracting metadata...")
            QtWidgets.QApplication.processEvents()
            
            try:
                logger.info("Opening PDF file: %s", input_file)
                with pikepdf.Pdf.open(input_file) as pdf:
                    # Get document info dictionary
                    docinfo = pdf.docinfo
                    if docinfo:
                        # Convert metadata to readable format
                        metadata = []
                        logger.info("Found metadata in PDF file")
                        for key, value in docinfo.items():
                            # Remove the leading '/' from key
                            key = str(key).lstrip('/')
                            
                            # Handle different types of values
                            if isinstance(value, str):
                                # Transform date strings
                                if 'Date' in key and value.startswith('D:'):
                                    value = transform_date(value)
                            
                            metadata.append(f"{key}: {value}")
                            logger.debug("Metadata: %s = %s", key, value)
                        
                        self.outputText.setText("\n".join(metadata))
                        msg = "Metadata extraction complete"
                        logger.info(msg)
                        self.statusBar().showMessage(msg, 3000)
                    else:
                        msg = "No metadata found in the PDF"
                        logger.info(msg)
                        QMessageBox.information(self, "Info", msg)
                        self.statusBar().showMessage(msg, 3000)
                        
            except pikepdf.PdfError as e:
                msg = f"Invalid or corrupted PDF file: {str(e)}"
                logger.error(msg)
                QMessageBox.critical(self, "Error", msg)
                self.statusBar().showMessage("Metadata extraction failed", 3000)
                
        except Exception as e:
            msg = f"Error extracting metadata: {str(e)}"
            logger.error(msg)
            QMessageBox.critical(self, "Error", msg)
            self.statusBar().showMessage("Error extracting metadata", 3000)

def main():
    try:
        app = QApplication(sys.argv)
        window = MetadataExtractorUI()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
