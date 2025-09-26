# Import Libraries
import os
import sys
from pathlib import Path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QMenuBar, QMenu, QAction
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

try:
    from pdf2docx import parse
    from typing import Tuple
except ImportError as e:
    logger.critical("Required package not found: %s", str(e))
    print(f"Error: Required package not found. Please run 'pip install pdf2docx' ({str(e)})")
    sys.exit(1)

def convert_pdf2docx(input_file: str, output_file: str, pages: Tuple = None):
    """Converts pdf to docx"""
    try:
        if not os.path.exists(input_file):
            logger.error("Input file not found: %s", input_file)
            raise FileNotFoundError(f"Input file '{input_file}' not found")
            
        if pages:
            pages = [int(i) for i in list(pages) if i.isnumeric()]
            
        logger.info("Converting PDF to DOCX: %s -> %s", input_file, output_file)
        logger.debug("Pages to convert: %s", pages if pages else "all")
        
        result = parse(pdf_file=input_file,
                      docx_with_path=output_file, pages=pages)
        
        summary = {
            "File": input_file, 
            "Pages": str(pages), 
            "Output File": output_file
        }
        # Printing Summary
        logger.info("Conversion summary:")
        for key, value in summary.items():
            logger.info("%s: %s", key, value)
        
        return result
        
    except Exception as e:
        logger.error("Error converting PDF to DOCX: %s", str(e))
        print(f"Error converting PDF to DOCX: {str(e)}")
        sys.exit(1)

# create folder for converted files
def create_folder(folder_name: str):
    """Creates folder if it does not exist"""
    try:
        if not os.path.exists(folder_name):
            logger.info("Creating folder: %s", folder_name)
            os.makedirs(folder_name)
            return True
        return True
    except Exception as e:
        logger.error("Error creating folder %s: %s", folder_name, str(e))
        return False

# move converted files to folder
def move_files(input_file: str, output_file: str, folder_name: str):
    """Moves converted files to folder"""
    try:
        if not os.path.exists(folder_name):
            logger.warning("Destination folder does not exist: %s", folder_name)
            return False
            
        import shutil
        logger.info("Moving files to %s", folder_name)
        shutil.move(input_file, os.path.join(folder_name, os.path.basename(input_file)))
        shutil.move(output_file, os.path.join(folder_name, os.path.basename(output_file)))
        logger.info("Files moved successfully")
        return True
    except Exception as e:
        logger.error("Error moving files: %s", str(e))
        return False

class ConvertWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.initUI()
            logger.info("PDF to DOCX converter initialized")
        except Exception as e:
            logger.error("Failed to initialize PDF to DOCX converter: %s", str(e))
            raise

    def initUI(self):
        try:
            self.setWindowTitle('PDF to DOCX Converter')
            self.setGeometry(100, 100, 600, 400)
            
            # Set font for the entire application
            app_font = QtGui.QFont()
            app_font.setPointSize(12)
            QApplication.setFont(app_font)
            
            # Create menu bar
            menubar = self.menuBar()
            file_menu = menubar.addMenu('File')
            
            # Create actions
            open_action = QAction('Open PDF', self)
            open_action.triggered.connect(self.select_pdf)
            
            exit_action = QAction('Exit', self)
            exit_action.triggered.connect(self.close)
            
            # Add actions to menu
            file_menu.addAction(open_action)
            file_menu.addSeparator()
            file_menu.addAction(exit_action)
            
            # Create central widget
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            
            # Create layout
            layout = QtWidgets.QVBoxLayout(central_widget)
            
            # Add widgets
            self.status_label = QtWidgets.QLabel('Select a PDF file to convert')
            layout.addWidget(self.status_label)
            
            select_button = QtWidgets.QPushButton('Select PDF')
            select_button.clicked.connect(self.select_pdf)
            layout.addWidget(select_button)
            
            self.progress_label = QtWidgets.QLabel('')
            layout.addWidget(self.progress_label)
            
            logger.debug("UI initialized successfully")
            
        except Exception as e:
            logger.error("Error initializing UI: %s", str(e))
            raise

    def select_pdf(self):
        try:
            input_file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
            if input_file:
                logger.info("Selected input file: %s", input_file)
                output_file = input_file.rsplit('.', 1)[0] + '.docx'
                try:
                    self.status_label.setText(f'Converting: {os.path.basename(input_file)}')
                    QApplication.processEvents()
                    
                    result = convert_pdf2docx(input_file, output_file)
                    
                    if result:
                        logger.info("Conversion successful: %s", output_file)
                        QMessageBox.information(self, 'Success', 
                            f'File converted successfully!\nSaved as: {os.path.basename(output_file)}')
                    self.status_label.setText('Select a PDF file to convert')
                    
                except Exception as e:
                    logger.error("Error converting file: %s", str(e))
                    QMessageBox.critical(self, 'Error', f'Error converting file: {str(e)}')
                    self.status_label.setText('Error occurred during conversion')
                    
        except Exception as e:
            logger.error("Error in file selection: %s", str(e))
            QMessageBox.critical(self, 'Error', f'Error selecting file: {str(e)}')

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = ConvertWindow()
        window.show()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)
