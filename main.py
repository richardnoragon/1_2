import sys
from PyQt5.QtWidgets import QApplication
from rfuhub import RFUHub
from log_manager import LogManager
from config_manager import ConfigManager

from core.error_handler import error_handler



def main():
    """main."""
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
