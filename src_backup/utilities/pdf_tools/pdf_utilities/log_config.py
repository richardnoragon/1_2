"""
Logging Configuration Bridge for PDF Utilities
This module provides a bridge between PDF utilities and the main project's
logging system. Created during Phase 2.2 of PDF utilities integration.
"""

import sys
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Add parent directory to path to import main project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.logging_manager import LogManager
    MAIN_LOGGING_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    LogManager = None
    MAIN_LOGGING_AVAILABLE = False


def setup_logger(name):
    """
    Set up a logger with bridge to main logging system.
    
    Args:
        name: The name of the logger (typically __name__ from calling module)
        
    Returns:
        Logger: Configured logger instance
    """
    if MAIN_LOGGING_AVAILABLE and LogManager is not None:
        # Use main project logging system
        # Extract module name from full path for cleaner logger names
        if '.' in name:
            module_name = name.split('.')[-1]
        else:
            module_name = name
            
        # Remove common file extensions if present
        if module_name.endswith('.py'):
            module_name = module_name[:-3]
            
        # Create PDF-specific logger name
        logger_name = f'PDF.{module_name}'
        return LogManager().get_logger(logger_name)
    else:
        # Fallback to original logging system for development/testing
        return _setup_fallback_logger(name)


def _setup_fallback_logger(name):
    """
    Fallback logger setup when main logging system is not available.
    
    Args:
        name: The name of the logger
        
    Returns:
        Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create logger
    logger = logging.getLogger(name)
    if logger.handlers:  # Return if logger is already configured
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (rotating log files) - use main log name for consistency
    log_file = os.path.join('logs', 'rfu_pdf_fallback.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# For backward compatibility
def get_logger(name):
    """Get a logger instance - alias for setup_logger."""
    return setup_logger(name)


if __name__ == '__main__':
    # Test the logging bridge
    test_logger = setup_logger(__name__)
    
    test_logger.info("Testing PDF logging bridge")
    test_logger.debug("Debug message test")
    test_logger.warning("Warning message test")
    test_logger.error("Error message test")
    
    # Test with module-like name
    module_logger = setup_logger('pdf_utilities.extract_text')
    module_logger.info("Testing module-style logger name")
    
    print("Logging bridge test completed successfully!")
    print(f"Main logging available: {MAIN_LOGGING_AVAILABLE}")