"""
Richards File Utilities (RFU) - Main Entry Point.

This module serves as the central entry point for the RFU application,
handling initialization of logging, configuration, and the Qt application.
"""

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# Add the src directory to Python path for relative imports
script_dir = Path(__file__).parent
src_dir = script_dir.parent
sys.path.insert(0, str(src_dir))

# Import with fallback for direct execution
try:
    from .hub import RFUHub
except ImportError:
    from tabbed_hub import RFUHub


def main():
    """
    Initialize and run the Richards File Utilities application.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Initialize logging first
    try:
        from .log_manager import get_log_manager
    except ImportError:
        from log_manager import get_log_manager

    logger = get_log_manager().get_logger("Main")
    logger.info("Starting Richards Files Utilities")

    try:
        # Initialize configuration
        try:
            from .config_manager import get_config_manager
        except ImportError:
            from config_manager import get_config_manager

        config = get_config_manager()
        logging_level = config.get_setting("general", "logging_level", "INFO")
        debug_enabled = config.get_setting(
            "general", "enable_debug_logging", False
        )

        # Initialize network connectivity configuration
        # try:
        #     from network_connectivity.config import (
        #         get_network_config_manager)
        #     network_config = get_network_config_manager()
        #     logger.info('Network connectivity configuration initialized')
        # except Exception as e:
        #     logger.warning('Failed to initialize network connectivity '
        #                    'config: %s', e)

        # Set logging level based on configuration
        if debug_enabled:
            get_log_manager().set_level("DEBUG")
        else:
            get_log_manager().set_level(logging_level)

        # Create Qt application with proper cleanup
        app = QApplication(sys.argv)
        logger.info("Qt Application initialized")

        # Create and show main window
        window = RFUHub()
        window.show()
        logger.info("Main window displayed")

        # Start event loop
        return_code = app.exec_()
        logger.info("Application shutting down")

        # Ensure proper cleanup
        try:
            if hasattr(window, "gui_hub") and window.gui_hub:
                window.gui_hub.close()
            app.quit()
            app.deleteLater()
        except Exception as e:
            logger.error("Error during final cleanup: %s", e)

        return return_code

    except Exception as e:
        logger.critical("Critical error in main: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
