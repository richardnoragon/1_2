import logging
import logging.handlers
from pathlib import Path


class LogManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the logging configuration."""
        self.log_dir = Path(__file__).parent.parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up file logging
        self.log_file = self.log_dir / 'rfu.log'
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging settings."""
        logger = logging.getLogger('RFU')
        logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=5*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handlers if they haven't been added already
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
    
    def set_level(self, level):
        """Set the logging level for the RFU logger and its handlers."""
        logger = logging.getLogger('RFU')
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance with the given name."""
        return logging.getLogger(f'RFU.{name}')
