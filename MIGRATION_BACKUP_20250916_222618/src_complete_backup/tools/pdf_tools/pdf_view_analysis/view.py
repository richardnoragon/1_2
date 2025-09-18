from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sys
import fitz  # PyMuPDF
import os
from config_manager import ConfigManager
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

class PDFViewer(QMainWindow):
    def __init__(self):
        try:
            super(PDFViewer, self).__init__()
            self.config = ConfigManager()
            
            # Load UI
            uic.loadUi('view.ui', self)
            
            # Load settings
            self.load_settings()
            
            # Initialize variables
            self.doc = None
            self.current_page = 0
            self.total_pages = 0
            
            # Connect signals
            self.actionOpen.triggered.connect(self.open_file)
            self.actionExit.triggered.connect(self.close)
            self.previousButton.clicked.connect(self.previous_page)
            self.nextButton.clicked.connect(self.next_page)
            
            # Disable navigation buttons initially
            self.previousButton.setEnabled(False)
            self.nextButton.setEnabled(False)
            
            logger.info("PDF viewer initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize viewer: %s", str(e))
            QMessageBox.critical(self, "Error", f"Failed to initialize viewer: {str(e)}")
            self.close()
    
    def load_settings(self):
        """Load settings from configuration"""
        try:
            # Load last directory
            last_dir = self.config.get_setting('general', 'last_opened_dir', '')
            self.last_directory = last_dir if last_dir else os.path.expanduser('~')
            
            # Load viewer specific settings
            viewer_config = self.config.get_module_config('viewer')
            self.zoom_factor = viewer_config.get('zoom_factor', 1.0)
            self.default_page = viewer_config.get('default_page', 1)
        except Exception as e:
            logger.warning("Error loading settings: %s", str(e))
            QMessageBox.warning(self, "Warning", f"Error loading settings: {str(e)}")
            # Use defaults
            self.last_directory = os.path.expanduser('~')
            self.zoom_factor = 1.0
            self.default_page = 1
    
    def save_settings(self):
        """Save settings to configuration"""
        try:
            self.config.set_setting('general', 'last_opened_dir', self.last_directory)
        except Exception as e:
            logger.warning("Error saving settings: %s", str(e))
            QMessageBox.warning(self, "Warning", f"Error saving settings: {str(e)}")
    
    def open_file(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Open PDF file",
                self.last_directory,
                "PDF Files (*.pdf)"
            )
            
            if file_name:
                logger.info("Selected input file: %s", file_name)
                self.last_directory = os.path.dirname(file_name)
                self.save_settings()
                
                try:
                    # Close previous document if open
                    if self.doc:
                        self.doc.close()
                    
                    logger.info("Loading PDF file: %s", file_name)
                    self.doc = fitz.open(file_name)
                    self.total_pages = len(self.doc)
                    self.current_page = self.default_page - 1  # Convert to 0-based index
                    
                    if self.total_pages > 0:
                        self.show_page()
                        self.previousButton.setEnabled(True)
                        self.nextButton.setEnabled(True)
                        self.statusBar().showMessage(f"Loaded {os.path.basename(file_name)}", 3000)
                        logger.info("PDF file loaded successfully")
                    else:
                        logger.warning("The PDF file is empty")
                        QMessageBox.warning(self, "Warning", "The PDF file is empty")
                        self.statusBar().showMessage("Empty PDF file", 3000)
                        
                except fitz.FileDataError:
                    logger.error("Invalid or corrupted PDF file")
                    QMessageBox.critical(self, "Error", "Invalid or corrupted PDF file")
                except Exception as e:
                    logger.error("Could not open PDF file: %s", str(e))
                    QMessageBox.critical(self, "Error", f"Could not open PDF file: {str(e)}")
                    
        except Exception as e:
            logger.error("Error in file open operation: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error in file open operation: {str(e)}")
    
    def show_page(self):
        try:
            if self.doc and 0 <= self.current_page < self.total_pages:
                page = self.doc[self.current_page]
                
                try:
                    # Get zoom factor from config
                    zoom = self.zoom_factor
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
                    
                    pixmap = QPixmap.fromImage(img)
                    self.pdfView.setScene(QtWidgets.QGraphicsScene())
                    self.pdfView.scene().addPixmap(pixmap)
                    self.pdfView.fitInView(self.pdfView.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
                    
                    # Update page label
                    self.pageLabel.setText(f"Page {self.current_page + 1} of {self.total_pages}")
                    logger.debug("Displaying page %d", self.current_page + 1)
                    
                except Exception as e:
                    logger.warning("Error rendering page %d: %s", self.current_page + 1, str(e))
                    QMessageBox.warning(self, "Warning", f"Error rendering page {self.current_page + 1}: {str(e)}")
                    
        except Exception as e:
            logger.error("Error displaying page: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error displaying page: {str(e)}")
    
    def previous_page(self):
        try:
            if self.doc and self.current_page > 0:
                self.current_page -= 1
                self.show_page()
            self.previousButton.setEnabled(self.current_page > 0)
            self.nextButton.setEnabled(True)
            logger.debug("Moving to previous page: %d", self.current_page + 1)
        except Exception as e:
            logger.error("Error navigating to previous page: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error navigating to previous page: {str(e)}")
    
    def next_page(self):
        try:
            if self.doc and self.current_page < self.total_pages - 1:
                self.current_page += 1
                self.show_page()
            self.nextButton.setEnabled(self.current_page < self.total_pages - 1)
            self.previousButton.setEnabled(True)
            logger.debug("Moving to next page: %d", self.current_page + 1)
        except Exception as e:
            logger.error("Error navigating to next page: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error navigating to next page: {str(e)}")
    
    def closeEvent(self, event):
        """Clean up resources when closing"""
        try:
            if self.doc:
                self.doc.close()
            event.accept()
            logger.info("PDF viewer closed")
        except Exception as e:
            logger.warning("Error cleaning up resources: %s", str(e))
            event.accept()

def main():
    try:
        app = QApplication(sys.argv)
        window = PDFViewer()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()