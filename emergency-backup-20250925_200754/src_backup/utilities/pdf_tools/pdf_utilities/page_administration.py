import sys
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QApplication,
    QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5 import uic
import fitz  # PyMuPDF
from log_config import setup_logger
import os

# Set up logger
logger = setup_logger(__name__)


class PageAdministrationUI(QMainWindow):
    def __init__(self):
        try:
            super(PageAdministrationUI, self).__init__()
            logger.info("Initializing Page Administration UI")
            
            # Load UI
            uic.loadUi('page_administration.ui', self)
            logger.debug("UI file loaded successfully")
            
            # Initialize variables
            self.current_file = None
            self.doc = None
            self.pdf_files = []
            
            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.deleteButton.clicked.connect(self.delete_pages)
            self.rotateButton.clicked.connect(self.rotate_pages)
            self.moveButton.clicked.connect(self.move_pages)
            self.combineButton.clicked.connect(self.combine_pdfs)
            self.splitButton.clicked.connect(self.split_pdf)
            self.reorderButton.clicked.connect(self.reorder_pages)
            self.actionExit.triggered.connect(self.close)
            
            # Initially disable operation buttons
            self.deleteButton.setEnabled(False)
            self.rotateButton.setEnabled(False)
            self.moveButton.setEnabled(False)
            self.splitButton.setEnabled(False)
            self.reorderButton.setEnabled(False)
            
            # Set up PDF files list for combining
            self.pdfFilesList.setDragDropMode(self.pdfFilesList.InternalMove)
            
            logger.debug("UI signals connected successfully")
            self.show()
            
        except Exception as e:
            logger.error("Failed to initialize UI: %s", str(e), exc_info=True)
            msg = f"Failed to initialize UI: {str(e)}"
            QMessageBox.critical(self, "Error", msg)
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
                
                # Open the PDF and show page count
                self.doc = fitz.open(filename)
                info = f"Page Information: {self.doc.page_count} pages"
                self.pageInfoLabel.setText(info)
                
                # Enable operation buttons
                self.deleteButton.setEnabled(True)
                self.rotateButton.setEnabled(True)
                self.moveButton.setEnabled(True)
                self.splitButton.setEnabled(True)
                self.reorderButton.setEnabled(True)
                
        except Exception as e:
            logger.error("Error browsing file: %s", str(e))
            msg = f"Error selecting file: {str(e)}"
            QMessageBox.critical(self, "Error", msg)

    def parse_page_numbers(self, text):
        """Parse page numbers from text input (e.g., '1,2,3' or '1-3')"""
        try:
            pages = []
            parts = text.strip().split(',')
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    # Convert to 0-based index
                    pages.extend(range(start - 1, end))
                else:
                    # Convert to 0-based index
                    pages.append(int(part) - 1)
            return sorted(pages)
        except Exception as e:
            logger.error("Error parsing page numbers: %s", str(e))
            msg = ("Invalid page number format. Use comma-separated numbers "
                   "or ranges (e.g., 1,2,3 or 1-3)")
            raise ValueError(msg)

    def delete_pages(self):
        try:
            if not self.doc:
                msg = "Please select a PDF file first!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            pages_text = self.pagesEdit.text().strip()
            if not pages_text:
                msg = "Please enter page numbers to delete!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            pages = self.parse_page_numbers(pages_text)
            if not pages:
                msg = "No valid pages specified!"
                QMessageBox.warning(self, "Warning", msg)
                return
                
            # Validate page numbers
            if max(pages) >= self.doc.page_count:
                msg = "Page number(s) exceed document length!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            # Delete pages in reverse order to maintain correct indices
            for page_num in sorted(pages, reverse=True):
                self.doc.delete_page(page_num)
            
            # Save changes
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Modified PDF",
                "",
                "PDF Files (*.pdf)"
            )
            if output_file:
                self.doc.save(output_file)
                QMessageBox.information(
                    self,
                    "Success",
                    "Pages deleted successfully!"
                )
                logger.info("Pages deleted and saved to: %s", output_file)
                
        except Exception as e:
            logger.error("Error deleting pages: %s", str(e))
            msg = f"Error deleting pages: {str(e)}"
            QMessageBox.critical(self, "Error", msg)

    def rotate_pages(self):
        try:
            if not self.doc:
                msg = "Please select a PDF file first!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            pages_text = self.pagesEdit.text().strip()
            if not pages_text:
                msg = "Please enter page numbers to rotate!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            pages = self.parse_page_numbers(pages_text)
            if not pages:
                msg = "No valid pages specified!"
                QMessageBox.warning(self, "Warning", msg)
                return
                
            # Validate page numbers
            if max(pages) >= self.doc.page_count:
                msg = "Page number(s) exceed document length!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            # Get rotation angle
            rotation_text = self.rotationCombo.currentText()
            if "90° Clockwise" in rotation_text:
                angle = 90
            elif "Counter-clockwise" in rotation_text:
                angle = -90
            else:
                angle = 180
            
            # Rotate pages
            for page_num in pages:
                page = self.doc[page_num]
                page.set_rotation(page.rotation + angle)
            
            # Save changes
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Modified PDF",
                "",
                "PDF Files (*.pdf)"
            )
            if output_file:
                self.doc.save(output_file)
                QMessageBox.information(
                    self,
                    "Success",
                    "Pages rotated successfully!"
                )
                logger.info("Pages rotated and saved to: %s", output_file)
                
        except Exception as e:
            logger.error("Error rotating pages: %s", str(e))
            msg = f"Error rotating pages: {str(e)}"
            QMessageBox.critical(self, "Error", msg)

    def move_pages(self):
        try:
            if not self.doc:
                msg = "Please select a PDF file first!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            pages_text = self.pagesEdit.text().strip()
            if not pages_text:
                msg = "Please enter page numbers to move!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            target_text = self.targetPageEdit.text().strip()
            if not target_text:
                msg = "Please enter a target page number!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            try:
                target_page = int(target_text) - 1  # Convert to 0-based index
                if target_page < 0 or target_page > self.doc.page_count:
                    raise ValueError("Target page number out of range")
            except ValueError:
                msg = "Invalid target page number!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            pages = self.parse_page_numbers(pages_text)
            if not pages:
                msg = "No valid pages specified!"
                QMessageBox.warning(self, "Warning", msg)
                return
                
            # Validate page numbers
            if max(pages) >= self.doc.page_count:
                msg = "Page number(s) exceed document length!"
                QMessageBox.warning(self, "Warning", msg)
                return
            
            # Move pages (currently only moves first page)
            self.doc.move_page(pages[0], target_page)
            
            # Save changes
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Modified PDF",
                "",
                "PDF Files (*.pdf)"
            )
            if output_file:
                self.doc.save(output_file)
                QMessageBox.information(
                    self,
                    "Success",
                    "Pages moved successfully!"
                )
                logger.info("Pages moved and saved to: %s", output_file)
                
        except Exception as e:
            logger.error("Error moving pages: %s", str(e))
            msg = f"Error moving pages: {str(e)}"
            QMessageBox.critical(self, "Error", msg)

    def combine_pdfs(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select PDF Files to Combine",
                "",
                "PDF Files (*.pdf)"
            )
            
            if not files:
                return
                
            # Clear and populate the list widget
            self.pdfFilesList.clear()
            for file in files:
                item = QListWidgetItem(os.path.basename(file))
                item.setData(Qt.UserRole, file)
                self.pdfFilesList.addItem(item)
            
            # Get output filename
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Combined PDF",
                "",
                "PDF Files (*.pdf)"
            )
            
            if not output_file:
                return
                
            # Create new PDF
            result_doc = fitz.open()
            
            # Add pages from each file in order
            for i in range(self.pdfFilesList.count()):
                item = self.pdfFilesList.item(i)
                pdf_path = item.data(Qt.UserRole)
                doc = fitz.open(pdf_path)
                result_doc.insert_pdf(doc)
                doc.close()
            
            result_doc.save(output_file)
            result_doc.close()
            
            QMessageBox.information(
                self,
                "Success",
                "PDFs combined successfully!"
            )
            logger.info("PDFs combined and saved to: %s", output_file)
            
        except Exception as e:
            logger.error("Error combining PDFs: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Error combining PDFs: {str(e)}"
            )

    def split_pdf(self):
        try:
            if not self.doc:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select a PDF file first!"
                )
                return
            
            split_type = self.splitTypeCombo.currentText()
            
            # Get output directory
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory for Split PDFs"
            )
            
            if not output_dir:
                return
            
            if split_type == "Split by Page Count":
                pages_per_doc = self.get_integer_input(
                    "Pages per Document",
                    "Enter number of pages per document:"
                )
                if not pages_per_doc:
                    return
                    
                # Split into chunks
                for i in range(0, self.doc.page_count, pages_per_doc):
                    new_doc = fitz.open()
                    end_page = min(
                        i + pages_per_doc - 1,
                        self.doc.page_count - 1
                    )
                    new_doc.insert_pdf(
                        self.doc,
                        from_page=i,
                        to_page=end_page
                    )
                    output_file = os.path.join(
                        output_dir,
                        f"split_{i//pages_per_doc + 1}.pdf"
                    )
                    new_doc.save(output_file)
                    new_doc.close()
                    
            elif split_type == "Split by Sections":
                section_pages = self.parse_page_numbers(self.pagesEdit.text())
                if not section_pages:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "Please enter section break page numbers!"
                    )
                    return
                
                # Add start and end pages
                section_pages = [0] + section_pages + [self.doc.page_count]
                
                # Create sections
                for i in range(len(section_pages) - 1):
                    new_doc = fitz.open()
                    new_doc.insert_pdf(
                        self.doc,
                        from_page=section_pages[i],
                        to_page=section_pages[i + 1] - 1
                    )
                    output_file = os.path.join(
                        output_dir,
                        f"section_{i + 1}.pdf"
                    )
                    new_doc.save(output_file)
                    new_doc.close()
                    
            elif split_type == "Split by Headings":
                # This would require text analysis to find headings
                msg = ("Splitting by headings requires text analysis. "
                      "This feature is coming soon!")
                QMessageBox.information(self, "Information", msg)
                return
            
            QMessageBox.information(
                self,
                "Success",
                f"PDF split successfully! Files saved in: {output_dir}"
            )
            logger.info("PDF split into multiple files in: %s", output_dir)
            
        except Exception as e:
            logger.error("Error splitting PDF: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Error splitting PDF: {str(e)}"
            )

    def reorder_pages(self):
        try:
            if not self.doc:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select a PDF file first!"
                )
                return
            
            new_order_text = self.reorderPagesEdit.text().strip()
            if not new_order_text:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please enter the new page order!"
                )
                return
            
            try:
                new_order = [
                    int(x.strip()) - 1
                    for x in new_order_text.split(',')
                ]
                if not all(0 <= x < self.doc.page_count for x in new_order):
                    raise ValueError("Page numbers out of range")
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Invalid page order format!"
                )
                return
            
            # Create new document with reordered pages
            new_doc = fitz.open()
            for page_num in new_order:
                new_doc.insert_pdf(
                    self.doc,
                    from_page=page_num,
                    to_page=page_num
                )
            
            # Save changes
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Reordered PDF",
                "",
                "PDF Files (*.pdf)"
            )
            
            if output_file:
                new_doc.save(output_file)
                new_doc.close()
                QMessageBox.information(
                    self,
                    "Success",
                    "Pages reordered successfully!"
                )
                logger.info("Pages reordered and saved to: %s", output_file)
                
        except Exception as e:
            logger.error("Error reordering pages: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Error reordering pages: {str(e)}"
            )

    def get_integer_input(self, title, message):
        """Helper method to get integer input from user"""
        while True:
            text, ok = QInputDialog.getText(self, title, message)
            if not ok:
                return None
            try:
                value = int(text)
                if value > 0:
                    return value
            except ValueError:
                pass
            QMessageBox.warning(
                self,
                "Warning",
                "Please enter a valid positive number!"
            )

    def closeEvent(self, event):
        """Clean up resources when closing"""
        try:
            if self.doc:
                self.doc.close()
            event.accept()
        except Exception as e:
            logger.error("Error closing document: %s", str(e))
            event.accept()


def main():
    try:
        app = QApplication(sys.argv)
        _ = PageAdministrationUI()
        logger.info("Application started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        msg = f"Application failed to start: {str(e)}"
        QMessageBox.critical(None, "Fatal Error", msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
