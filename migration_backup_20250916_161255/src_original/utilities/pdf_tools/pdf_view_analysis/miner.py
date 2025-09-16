# this is for doing some math operations
import math
# this is for handling the PDF operations
import fitz
# importing Qt components
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
import sys
# importing PhotoImage from tkinter
from tkinter import PhotoImage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('miner.ui', self)
        self.pdf_miner = None
        self.current_page = 0
        
        # Connect the exit action
        self.actionExit.triggered.connect(self.close)
        # Connect the open action
        self.actionOpen.triggered.connect(self.open_pdf)
        
    def open_pdf(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF files (*.pdf)")
        if filepath:
            self.pdf_miner = PDFMiner(filepath)
            self.show_page(0)
            
    def show_page(self, page_num):
        if self.pdf_miner:
            image = self.pdf_miner.get_page(page_num)
            # Convert PhotoImage to QImage/QPixmap for Qt
            # Implementation will need to be adjusted based on your needs
            self.pdfView.setPixmap(QPixmap.fromImage(image))

class PDFMiner:
    def __init__(self, filepath):
        # creating the file path
        self.filepath = filepath
        # opening the pdf document
        self.pdf = fitz.open(self.filepath)
        # loading the first page of the pdf document
        self.first_page = self.pdf.load_page(0)
        # getting the height and width of the first page
        self.width, self.height = self.first_page.rect.width, self.first_page.rect.height
        # initializing the zoom values of the page
        zoomdict = {800:0.8, 700:0.6, 600:1.0, 500:1.0}
        # getting the width value
        width = int(math.floor(self.width / 100.0) * 100)
        # zooming the page
        self.zoom = zoomdict[width]
        
    # this will get the metadata from the document like 
    # author, name of document, number of pages  
    def get_metadata(self):
        # getting metadata from the open PDF document
        metadata = self.pdf.metadata
        # getting number of pages from the open PDF document
        numPages = self.pdf.page_count
        # returning the metadata and the numPages
        return metadata, numPages
    
    # the function for getting the page
    def get_page(self, page_num):
        # loading the page
        page = self.pdf.load_page(page_num)
        # checking if zoom is True
        if self.zoom:
            # creating a Matrix whose zoom factor is self.zoom
            mat = fitz.Matrix(self.zoom, self.zoom)
            # gets the image of the page
            pix = page.get_pixmap(matrix=mat)
        # returns the image of the page  
        else:
            pix = page.get_pixmap()
            
        # Convert pixmap to QImage
        img_data = pix.samples
        qimg = QImage(img_data, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        return qimg
    
    # function to get text from the current page
    def get_text(self, page_num):
        # loading the page
        page = self.pdf.load_page(page_num)
        # getting text from the loaded page
        text = page.getText('text')
        # returning text
        return text

# Main entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())