import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from log_config import setup_logger
from config_manager import ConfigManager


# Helper function to get absolute path to resources
def get_absolute_path(relative_path):
    """Get absolute path to resource, works regardless of how the script is run"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)


# Set up logger for main application
logger = setup_logger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(MainWindow, self).__init__()
            logger.info("Starting main application window")
            
            # Initialize configuration manager
            self.config_manager = ConfigManager()
            logger.debug("Configuration manager initialized")
            
            # Load UI using absolute path
            ui_path = get_absolute_path('main.ui')
            logger.debug(f"Loading UI file from: {ui_path}")
            uic.loadUi(ui_path, self)
            logger.debug("Main UI file loaded successfully")

            # Enable drag and drop
            self.setAcceptDrops(True)

            # Connect Basic Operations buttons
            self.compressButton.clicked.connect(self.open_compress)
            self.splitButton.clicked.connect(self.open_split)
            self.mergeButton.clicked.connect(self.open_merge)
            self.pageAdminButton.clicked.connect(self.open_page_admin)
            self.viewButton.clicked.connect(self.open_view)
            self.minerButton.clicked.connect(self.open_miner)

            # Connect Administration buttons
            self.settingsButton.clicked.connect(self.open_settings)
            self.logsButton.clicked.connect(self.open_logs)

            # Connect Content Extraction buttons
            self.extractTextButton.clicked.connect(self.open_extract_text)
            self.extractImagesButton.clicked.connect(self.open_extract_images)
            self.extractTablesCamelotButton.clicked.connect(
                self.open_extract_tables
            )
            self.extractLinksButton.clicked.connect(self.open_extract_links)
            self.extractMetadataButton.clicked.connect(
                self.open_extract_metadata
            )

            # Connect Security buttons
            self.encryptButton.clicked.connect(self.open_encrypt)

            # Connect Enhancement buttons
            self.watermarkButton.clicked.connect(self.open_watermark)
            self.ocrButton.clicked.connect(self.open_ocr)
            self.highlightButton.clicked.connect(self.open_highlight)

            # Connect Conversion buttons
            self.convertToDocxButton.clicked.connect(
                self.open_convert_to_docx
            )
            self.convertToImageButton.clicked.connect(
                self.open_convert_to_image
            )
            self.convertHtmlToPdfButton.clicked.connect(
                self.open_convert_html_to_pdf
            )

            # Connect menu actions
            self.actionExit.triggered.connect(self.close)
            self.actionSettings.triggered.connect(self.open_settings)
            self.actionLogs.triggered.connect(self.open_logs)
            
            logger.debug("All button connections established successfully")
            self.show()
            
        except Exception as e:
            logger.critical(
                "Failed to initialize main window: %s",
                str(e),
                exc_info=True
            )
            msg = f"Failed to initialize main window: {str(e)}"
            QMessageBox.critical(self, "Fatal Error", msg)
            self.close()
    
    def dragEnterEvent(self, event):
        """Handle drag enter events for files"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Handle drop events for files"""
        files = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.toLocalFile().lower().endswith('.pdf')
        ]

        if not files:
            return
            
        # If multiple files are dropped, open merge
        if len(files) > 1:
            from merg import MergeUI
            self.window = MergeUI()
            self.window.files = files
            self.window.fileList.addItems([os.path.basename(f) for f in files])
            self.window.update_button_states()
            self.window.show()
        # If single file is dropped, show options
        else:
            options = [
                "View", "Compress", "Split", "Extract Text",
                "Extract Images", "Extract Tables", "OCR",
                "Extract Links", "Extract Metadata", "Watermark"
            ]
            item, ok = QtWidgets.QInputDialog.getItem(
                self,
                "Select Operation",
                "Choose operation for the PDF file:",
                options, 0, False
            )
            
            if ok and item:
                method_map = {
                    "View": self.open_view,
                    "Compress": self.open_compress,
                    "Split": self.open_split,
                    "Extract Text": self.open_extract_text,
                    "Extract Images": self.open_extract_images,
                    "Extract Tables": self.open_extract_tables,
                    "OCR": self.open_ocr,
                    "Extract Links": self.open_extract_links,
                    "Extract Metadata": self.open_extract_metadata,
                    "Watermark": self.open_watermark
                }
                
                # Open selected module
                if item in method_map:
                    # Store the file path to be used by the module
                    self.dropped_file = files[0]
                    method_map[item]()

    def open_module(self, module_name: str, ui_class):
        """Helper function to open module windows"""
        try:
            logger.info("Opening module: %s", module_name)
            # Get module configuration
            module_config = self.config_manager.get_module_config(
                module_name.lower().replace(" ", "_")
            )
            # Create module window with configuration
            self.window = ui_class(config=module_config)
            # If there's a dropped file, set it in the module
            if hasattr(self, 'dropped_file'):
                if hasattr(self.window, 'inputFileEdit'):
                    self.window.inputFileEdit.setText(self.dropped_file)
                    # Enable buttons for file selection
                    if hasattr(self.window, 'current_file'):
                        self.window.current_file = self.dropped_file
                    if hasattr(self.window, 'processButton'):
                        self.window.processButton.setEnabled(True)
                    if hasattr(self.window, 'extractButton'):
                        self.window.extractButton.setEnabled(True)
                    if hasattr(self.window, 'compressButton'):
                        self.window.compressButton.setEnabled(True)
                delattr(self, 'dropped_file')  # Clear the stored path
            self.window.show()
        except Exception as e:
            logger.error("Failed to open %s module: %s", module_name, str(e))
            msg = f"Failed to open {module_name} module: {str(e)}"
            QMessageBox.critical(self, "Error", msg)
    
    def open_compress(self):
        from compress import CompressUI
        self.open_module("Compress", CompressUI)
    
    def open_watermark(self):
        from watermark import WatermarkUI
        self.open_module("Watermark", WatermarkUI)
    
    def open_split(self):
        from split import SplitUI
        self.open_module("Split", SplitUI)
    
    def open_merge(self):
        from merg import MergeUI
        self.open_module("Merge", MergeUI)
    
    def open_extract_text(self):
        from extract_text import ExtractTextUI
        self.open_module("Extract Text", ExtractTextUI)
    
    def open_extract_images(self):
        from extract_image_cli import ExtractImageUI
        self.open_module("Extract Images", ExtractImageUI)
    
    def open_extract_tables(self):
        from extract_tables_camelot import ExtractTablesCamelotUI
        self.open_module("Extract Tables", ExtractTablesCamelotUI)
    
    def open_extract_links(self):
        from extract_links import ExtractLinksUI
        self.open_module("Extract Links", ExtractLinksUI)
    
    def open_extract_metadata(self):
        from extract_metadata import ExtractMetadataUI
        self.open_module("Extract Metadata", ExtractMetadataUI)
    
    def open_encrypt(self):
        from encrypt import EncryptUI
        self.open_module("Encrypt", EncryptUI)
    
    def open_ocr(self):
        from ocr import OCRUI
        self.open_module("OCR", OCRUI)
    
    def open_highlight(self):
        from highlight import HighlightUI
        self.open_module("Highlight", HighlightUI)

    def open_page_admin(self):
        from page_administration import PageAdministrationUI
        self.open_module("Page Administration", PageAdministrationUI)

    def open_view(self):
        from view import ViewUI
        self.open_module("View", ViewUI)

    def open_miner(self):
        from miner import MinerUI
        self.open_module("Miner", MinerUI)

    def open_convert_to_docx(self):
        from convert_to_docx import ConvertWindow
        self.open_module("Convert to DOCX", ConvertWindow)

    def open_convert_to_image(self):
        from convert_to_image import ConvertToImageUI
        self.open_module("Convert to Image", ConvertToImageUI)

    def open_convert_html_to_pdf(self):
        from convert_html_to_pdf import HtmlToPdfConverter
        self.open_module("Convert HTML to PDF", HtmlToPdfConverter)

    def open_settings(self):
        """Open the settings manager window"""
        from settings_manager import SettingsManagerUI
        self.settings_window = SettingsManagerUI()
        self.settings_window.show()

    def open_logs(self):
        """Open the log manager window"""
        from log_manager import LogManagerUI
        self.log_window = LogManagerUI()
        self.log_window.show()


def main():
    try:
        logger.info("Initializing PDF Utility application")
        
        # Create logs directory if it doesn't exist
        logs_dir = get_absolute_path('logs')
        os.makedirs(logs_dir, exist_ok=True)
        logger.debug(f"Logs directory ensured at: {logs_dir}")
        
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        
        logger.info("Application started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(
            "Application failed to start: %s",
            str(e),
            exc_info=True
        )
        msg = f"Application failed to start: {str(e)}"
        QMessageBox.critical(None, "Fatal Error", msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
