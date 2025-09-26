import os
import pikepdf
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

def split_pdf(input_file: str, output_dir: str, pages_per_file: int = None, page_ranges: list = None) -> bool:
    """Split a PDF file into multiple PDFs"""
    try:
        logger.info("Starting PDF split operation on: %s", input_file)
        logger.debug("Output directory: %s", output_dir)
        logger.debug("Pages per file: %s", pages_per_file)
        logger.debug("Page ranges: %s", page_ranges)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open the PDF
        try:
            pdf = pikepdf.Pdf.open(input_file)
            total_pages = len(pdf.pages)
            logger.debug("PDF opened successfully, total pages: %d", total_pages)
        except FileNotFoundError:
            logger.error("Input file not found: %s", input_file)
            QMessageBox.critical(None, "Error", f"Input file not found: {input_file}")
            return False
        except pikepdf.PdfError as e:
            logger.error("Error opening PDF: %s", str(e))
            QMessageBox.critical(None, "Error", f"Error opening PDF: {str(e)}")
            return False
        
        try:
            if page_ranges:
                # Split by specified ranges
                for i, page_range in enumerate(page_ranges, 1):
                    try:
                        start, end = map(int, page_range.split('-'))
                        if 1 <= start <= end <= total_pages:
                            new_pdf = pikepdf.Pdf.new()
                            for j in range(start-1, end):
                                new_pdf.pages.append(pdf.pages[j])
                            output_file = os.path.join(output_dir, f"split_{i}.pdf")
                            new_pdf.save(output_file)
                            logger.debug("Created split file %d (pages %d-%d): %s", 
                                       i, start, end, output_file)
                        else:
                            logger.warning("Invalid page range: %s", page_range)
                            QMessageBox.warning(None, "Warning", 
                                f"Invalid page range: {page_range}")
                    except ValueError:
                        logger.error("Invalid page range format: %s", page_range)
                        QMessageBox.warning(None, "Warning", 
                            f"Invalid page range format: {page_range}")
                        continue
                        
            elif pages_per_file:
                # Split by number of pages
                total_files = (total_pages + pages_per_file - 1) // pages_per_file
                logger.debug("Splitting into %d files with %d pages each", 
                           total_files, pages_per_file)
                
                for i in range(total_files):
                    start = i * pages_per_file
                    end = min((i + 1) * pages_per_file, total_pages)
                    
                    new_pdf = pikepdf.Pdf.new()
                    for j in range(start, end):
                        new_pdf.pages.append(pdf.pages[j])
                        
                    output_file = os.path.join(output_dir, f"split_{i+1}.pdf")
                    new_pdf.save(output_file)
                    logger.debug("Created split file %d (pages %d-%d): %s", 
                               i+1, start+1, end, output_file)
            
            else:
                # Split into individual pages
                logger.debug("Splitting into individual pages")
                for i in range(total_pages):
                    new_pdf = pikepdf.Pdf.new()
                    new_pdf.pages.append(pdf.pages[i])
                    output_file = os.path.join(output_dir, f"page_{i+1}.pdf")
                    new_pdf.save(output_file)
                    logger.debug("Created page file %d: %s", i+1, output_file)
            
            logger.info("Split operation completed successfully")
            return True
            
        except Exception as e:
            logger.error("Error during split operation: %s", str(e))
            QMessageBox.critical(None, "Error", f"Error during split operation: {str(e)}")
            return False
            
    except Exception as e:
        logger.error("Unexpected error during split operation: %s", str(e), exc_info=True)
        QMessageBox.critical(None, "Error", f"Unexpected error during split operation: {str(e)}")
        return False

class SplitUI(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(SplitUI, self).__init__()
            logger.info("Initializing Split UI")
            
            # Load UI
            uic.loadUi('split.ui', self)
            logger.debug("UI file loaded successfully")
            
            # Add progress bar
            self.progressBar = QtWidgets.QProgressBar()
            self.statusBar().addPermanentWidget(self.progressBar)
            self.progressBar.hide()
            
            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.browseOutputButton.clicked.connect(self.browse_output_dir)
            self.splitButton.clicked.connect(self.split_pdf)
            self.actionExit.triggered.connect(self.close)
            
            # Initialize state
            self.current_file = None
            self.current_output_dir = None
            self.splitButton.setEnabled(False)
            
            logger.debug("UI signals connected successfully")
            self.show()
            
        except Exception as e:
            logger.error("Failed to initialize UI: %s", str(e), exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to initialize UI: {str(e)}")
            self.close()
    
    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select PDF File",
                "",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                logger.info("Selected input file: %s", filename)
                self.current_file = filename
                self.inputFileEdit.setText(filename)
                self.update_split_button()
                
        except Exception as e:
            logger.error("Error browsing file: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error browsing file: {str(e)}")
    
    def browse_output_dir(self):
        try:
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory"
            )
            
            if directory:
                logger.info("Selected output directory: %s", directory)
                self.current_output_dir = directory
                self.outputDirEdit.setText(directory)
                self.update_split_button()
                
        except Exception as e:
            logger.error("Error selecting output directory: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error selecting output directory: {str(e)}")
    
    def update_split_button(self):
        """Enable split button only if both input and output are selected"""
        self.splitButton.setEnabled(bool(self.current_file and self.current_output_dir))
    
    def split_pdf(self):
        try:
            if not self.current_file or not self.current_output_dir:
                logger.warning("Missing input file or output directory")
                QMessageBox.warning(self, "Warning", "Please select both input file and output directory!")
                return
            
            # Get split parameters
            pages_per_file = None
            page_ranges = None
            
            if self.pagesPerFileRadio.isChecked():
                try:
                    pages_per_file = int(self.pagesPerFileEdit.text())
                    if pages_per_file <= 0:
                        raise ValueError("Pages per file must be positive")
                except ValueError as e:
                    logger.error("Invalid pages per file value: %s", str(e))
                    QMessageBox.critical(self, "Error", "Please enter a valid positive number for pages per file!")
                    return
                    
            elif self.pageRangesRadio.isChecked():
                ranges_text = self.pageRangesEdit.text().strip()
                if ranges_text:
                    page_ranges = [r.strip() for r in ranges_text.split(',')]
                else:
                    logger.warning("No page ranges specified")
                    QMessageBox.warning(self, "Warning", "Please enter page ranges!")
                    return
            
            self.progressBar.show()
            self.progressBar.setValue(0)
            self.statusBar().showMessage("Preparing to split PDF...")
            QtWidgets.QApplication.processEvents()

            # Load document
            self.progressBar.setValue(10)
            self.statusBar().showMessage("Loading document...")
            QtWidgets.QApplication.processEvents()
            
            try:
                doc = fitz.open(self.current_file)
                total_pages = doc.page_count
                
                self.progressBar.setValue(20)
                self.statusBar().showMessage("Analyzing document structure...")
                QtWidgets.QApplication.processEvents()
                
                # Calculate total operations
                if pages_per_file:
                    total_splits = (total_pages + pages_per_file - 1) // pages_per_file
                else:
                    total_splits = len(page_ranges)
                
                # Process splits
                current_split = 0
                base_progress = 20  # Starting progress after document load
                progress_per_split = (90 - base_progress) / total_splits  # Leave 10% for finalization
                
                if split_pdf(self.current_file, self.current_output_dir, 
                           pages_per_file, page_ranges,
                           progress_callback=lambda x: self.update_progress(x, base_progress)):
                    self.progressBar.setValue(100)
                    logger.info("Split operation completed successfully")
                    QMessageBox.information(self, "Success", 
                        f"PDF split successfully!\nOutput saved to: {self.current_output_dir}")
                    self.statusBar().showMessage("Split complete", 3000)
                else:
                    logger.warning("Split operation failed")
                    QMessageBox.warning(self, "Warning", "Failed to split PDF!")
                    self.statusBar().showMessage("Split failed", 3000)
                
            except Exception as e:
                logger.error("Error during split operation: %s", str(e), exc_info=True)
                QMessageBox.critical(self, "Error", f"Error during split operation: {str(e)}")
                self.statusBar().showMessage("Error during split", 3000)
            
        except Exception as e:
            logger.error("Error in split operation: %s", str(e), exc_info=True)
            QMessageBox.critical(self, "Error", f"Error in split operation: {str(e)}")
            self.statusBar().showMessage("Error occurred", 3000)
        
        finally:
            self.progressBar.hide()
            
    def update_progress(self, percent, base_progress):
        """Update progress bar during split operation"""
        progress = base_progress + int(percent * (90 - base_progress) / 100)
        self.progressBar.setValue(progress)
        self.statusBar().showMessage(f"Splitting PDF... {percent}%")
        QtWidgets.QApplication.processEvents()

def main():
    try:
        logger.info("Starting Split PDF application")
        app = QtWidgets.QApplication(sys.argv)
        window = SplitUI()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e), exc_info=True)
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()