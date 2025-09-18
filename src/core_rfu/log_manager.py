"""
Centralized logging manager for Richard's File Utilities.

This module provides consistent logging functionality across all components
with configurable levels, file rotation, and structured logging.
Enhanced with SQLite database logging support.
"""

import logging
import logging.handlers
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock

# Import database logging support
try:
    from src.core.database_logging import DatabaseLogHandler
    DATABASE_LOGGING_AVAILABLE = True
except ImportError:
    DATABASE_LOGGING_AVAILABLE = False


class LogManager:
    """Centralized logging manager with singleton pattern."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LogManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the logging manager."""
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """Setup the logging configuration."""
        # Create logs directory
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        
        # Main log file
        self.main_log_file = self.log_dir / 'rfu.log'
        
        # Generate session ID for this application run
        self.session_id = str(uuid.uuid4())
        
        # Configure root logger
        self.root_logger = logging.getLogger('RFU')
        self.root_logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.root_logger.handlers.clear()
        
        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
            '[%(filename)s:%(lineno)d]'
        )
        
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handler with rotation
        self._setup_file_handler()
        
        # Setup console handler
        self._setup_console_handler()
        
        # Setup database handler if available
        self._setup_database_handler()
        
        # Store loggers for cleanup
        self._loggers: Dict[str, logging.Logger] = {}
        
        # Log the initialization
        self.root_logger.info(f"LogManager initialized successfully (Session: {self.session_id})")
    
    def _setup_database_handler(self):
        """Setup database logging handler."""
        try:
            if DATABASE_LOGGING_AVAILABLE:
                # DatabaseLogHandler already imported globally
                handler = DatabaseLogHandler(session_id=self.session_id)
                handler.setLevel(logging.DEBUG)
                self.root_logger.addHandler(handler)
                self.database_handler = handler
                self.root_logger.info("Database logging handler enabled")
            else:
                self.database_handler = None
                self.root_logger.warning("Database logging not available")
        except Exception as e:
            self.database_handler = None
            msg = f"Failed to setup database logging: {e}"
            self.root_logger.error(msg)
    
    def _setup_file_handler(self):
        """Setup rotating file handler."""
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                self.main_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self.detailed_formatter)
            self.root_logger.addHandler(file_handler)
            self.file_handler = file_handler
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
            self.file_handler = None
    
    def _setup_console_handler(self):
        """Setup console handler."""
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(self.simple_formatter)
            self.root_logger.addHandler(console_handler)
            self.console_handler = console_handler
        except Exception as e:
            print(f"Failed to setup console logging: {e}")
            self.console_handler = None
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific component.
        
        Args:
            name: Logger name (typically module or class name)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        # Ensure name is prefixed with RFU
        if not name.startswith('RFU.'):
            logger_name = f'RFU.{name}'
        else:
            logger_name = name
        
        # Return existing logger if already created
        if logger_name in self._loggers:
            return self._loggers[logger_name]
        
        # Create new logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Store reference
        self._loggers[logger_name] = logger
        
        return logger
    
    def set_level(self, level: str):
        """
        Set the logging level for all loggers.
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', etc.)
        """
        try:
            log_level = getattr(logging, level.upper())
            self.root_logger.setLevel(log_level)
            
            # Update console handler level
            if self.console_handler:
                self.console_handler.setLevel(log_level)
            
            # Update all existing loggers
            for logger in self._loggers.values():
                logger.setLevel(log_level)
                
            self.root_logger.info(f"Logging level set to {level.upper()}")
            
        except AttributeError:
            self.root_logger.error(f"Invalid logging level: {level}")
    
    def set_console_level(self, level: str):
        """
        Set the console logging level separately from file logging.
        
        Args:
            level: Console logging level
        """
        try:
            log_level = getattr(logging, level.upper())
            if self.console_handler:
                self.console_handler.setLevel(log_level)
            self.root_logger.info(
                f"Console logging level set to {level.upper()}"
            )
        except AttributeError:
            self.root_logger.error(f"Invalid console logging level: {level}")
    
    def add_file_handler(self, name: str, filename: str,
                         level: str = 'INFO') -> bool:
        """
        Add a separate file handler for a specific component.
        
        Args:
            name: Handler name
            filename: Log filename
            level: Logging level for this handler
            
        Returns:
            bool: True if handler was added successfully
        """
        try:
            log_file = self.log_dir / filename
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            
            log_level = getattr(logging, level.upper())
            handler.setLevel(log_level)
            handler.setFormatter(self.detailed_formatter)
            
            # Add to root logger
            self.root_logger.addHandler(handler)
            
            self.root_logger.info(f"Added file handler '{name}' -> {filename}")
            return True
            
        except Exception as e:
            self.root_logger.error(f"Failed to add file handler '{name}': {e}")
            return False
    
    def log_structured(self, level: str, component: str, message: str,
                       **kwargs):
        """
        Log a structured message with additional context.
        
        Args:
            level: Log level
            component: Component name
            message: Log message
            **kwargs: Additional context data
        """
        logger = self.get_logger(component)
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Build structured message
        if kwargs:
            context = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | Context: {context}"
        else:
            full_message = message
        
        logger.log(log_level, full_message)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dict with logging statistics
        """
        stats = {
            'log_directory': str(self.log_dir),
            'main_log_file': str(self.main_log_file),
            'active_loggers': len(self._loggers),
            'logger_names': list(self._loggers.keys()),
            'root_level': logging.getLevelName(self.root_logger.level),
            'handlers': len(self.root_logger.handlers)
        }
        
        # Add file size if file exists
        if self.main_log_file.exists():
            stats['main_log_size_bytes'] = self.main_log_file.stat().st_size
        
        return stats
    
    def cleanup(self):
        """Cleanup logging resources."""
        try:
            # Close all handlers
            for handler in self.root_logger.handlers[:]:
                handler.close()
                self.root_logger.removeHandler(handler)
            
            # Clear logger references
            self._loggers.clear()
            
            self.root_logger.info("LogManager cleanup completed")
            
        except Exception as e:
            print(f"Error during LogManager cleanup: {e}")


# Global instance
_log_manager = None


def get_log_manager() -> LogManager:
    """Get the global LogManager instance."""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


# Convenience function for backward compatibility
def get_log_manager_instance():
    """Get LogManager instance (backward compatibility)."""
    return get_log_manager()