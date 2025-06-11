import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout
import subprocess
from rfuhub import RFUHub
from log_manager import LogManager
from config_manager import ConfigManager


class RenameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rename Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class CatalogWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Catalog Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class CopyMoveSyncDeleteWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Copy/Move/Sync/Delete Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class OrganizeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organize Window")
        self.setGeometry(100, 100, 400, 300)
        self.show()


class MyGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My GUI")
        self.setGeometry(100, 100, 400, 300)

        # Create push buttons
        self.rename_button = QPushButton("Rename", self)
        self.catalog_button = QPushButton("Catalog", self)
        self.cmsd_button = QPushButton("Copy/Move/Sync/Delete", self)
        self.organize_button = QPushButton("Organize", self)

        # Connect buttons to slots
        self.rename_button.clicked.connect(self.open_rename_window)
        self.catalog_button.clicked.connect(self.open_catalog_window)
        self.cmsd_button.clicked.connect(self.open_cmsd_window)
        self.organize_button.clicked.connect(self.open_organize_window)

        # Create layout and add buttons
        layout = QVBoxLayout()
        layout.addWidget(self.rename_button)
        layout.addWidget(self.catalog_button)
        layout.addWidget(self.cmsd_button)
        layout.addWidget(self.organize_button)

        # Set the central widget of the main window
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_rename_window(self):
        # self.rename_window = RenameWindow()
        subprocess.call(["python", "rename.py"])

    def open_catalog_window(self):
        self.catalog_window = CatalogWindow()

    def open_cmsd_window(self):
        self.cmsd_window = CopyMoveSyncDeleteWindow()

    def open_organize_window(self):
        self.organize_window = OrganizeWindow()


def main():
    # Initialize logging first
    logger = LogManager().get_logger('Main')
    logger.info('Starting Richards Files Utilities')
    
    try:
        # Initialize configuration
        config = ConfigManager()
        logging_level = config.get_setting('general', 'logging_level', 'INFO')
        debug_enabled = config.get_setting('general', 'enable_debug_logging', False)
        
        # Set logging level based on configuration
        if debug_enabled:
            LogManager().set_level('DEBUG')
        else:
            LogManager().set_level(logging_level)
            
        # Create Qt application
        app = QApplication(sys.argv)
        logger.info('Qt Application initialized')
        
        # Create and show main window
        window = RFUHub()
        window.show()
        logger.info('Main window displayed')
        
        # Start event loop
        return_code = app.exec_()
        logger.info('Application shutting down')
        return return_code
        
    except Exception as e:
        logger.critical(f'Critical error in main: {str(e)}', exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
