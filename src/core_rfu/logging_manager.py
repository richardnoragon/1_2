import logging
import logging.handlers
from pathlib import Path
import os
import time


class LogManager:
    """A class that handles log manager."""

    _instance = None

    def __new__(cls, log_file=None):
        """new.
        Args:
            cls (Any): Description of cls
            log_file (str, optional): Path to log file"""
        # For testing, allow creating new instances when log_file is provided
        if log_file is not None:
            instance = super(LogManager, cls).__new__(cls)
            instance._initialize(log_file)
            return instance

        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._initialize(log_file)
        return cls._instance

    def _initialize(self, log_file=None):
        """Initialize the logging configuration."""
        if log_file:
            self.log_file = Path(log_file)
            self.log_dir = self.log_file.parent
        else:
            self.log_dir = Path(__file__).parent.parent / "logs"
            self.log_file = self.log_dir / "rfu.log"

        self.log_dir.mkdir(exist_ok=True)
        self.context = {}

        # Set up file logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging settings."""
        # Create a unique logger name based on log file path for test isolation
        logger_name = f"RFU.{self.log_file.stem}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(
            logging.DEBUG
        )  # Default to DEBUG to capture all levels

        # Also configure the main RFU logger for test compatibility
        main_logger = logging.getLogger("RFU")
        main_logger.setLevel(
            logging.INFO
        )  # As expected by test_log_initialization

        # Clear any existing handlers to avoid conflicts
        logger.handlers.clear()

        # Create log file if it doesn't exist
        self.log_file.touch(exist_ok=True)

        # File handler with rotation - set to DEBUG to capture all messages
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)

        # Add handlers to both loggers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Add handlers to main RFU logger for test compatibility
        if not main_logger.handlers:
            main_logger.addHandler(file_handler)
            main_logger.addHandler(console_handler)

        self.logger = logger

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._log_with_context(logging.DEBUG, message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._log_with_context(logging.INFO, message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._log_with_context(logging.WARNING, message)

    def error(self, message: str, exc_info=None) -> None:
        """Log an error message."""
        self._log_with_context(logging.ERROR, message, exc_info=exc_info)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._log_with_context(logging.CRITICAL, message)

    def _log_with_context(
        self, level: int, message: str, exc_info=None
    ) -> None:
        """Log a message with context information."""
        if self.context:
            context_str = " ".join(
                [f"{k}:{v}" for k, v in self.context.items()]
            )
            message = f"[{context_str}] {message}"

        if exc_info:
            self.logger.log(level, message, exc_info=True)
        else:
            self.logger.log(level, message)

    def set_context(self, **kwargs) -> None:
        """Set context information for logging."""
        self.context.update(kwargs)

    def configure(
        self, max_size: int = None, backup_count: int = None
    ) -> None:
        """Configure log rotation settings."""
        if max_size is not None or backup_count is not None:
            # Remove existing file handlers from both loggers
            self.logger.handlers = [
                h
                for h in self.logger.handlers
                if not isinstance(h, logging.handlers.RotatingFileHandler)
            ]

            main_logger = logging.getLogger("RFU")
            main_logger.handlers = [
                h
                for h in main_logger.handlers
                if not isinstance(h, logging.handlers.RotatingFileHandler)
            ]

            # Add new rotating file handler with new settings
            file_handler = CustomRotatingFileHandler(
                self.log_file,
                maxBytes=max_size or 5 * 1024 * 1024,
                backupCount=backup_count or 5,
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            main_logger.addHandler(file_handler)

    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom log handler."""
        self.logger.addHandler(handler)

    def cleanup_old_logs(self, max_age_days: int) -> None:
        """Clean up old log files."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 60 * 60)

        # Find all log files in the directory
        for file_path in self.log_dir.glob("*.log"):
            if file_path != self.log_file:  # Don't delete current log
                try:
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        file_path.unlink()
                except (OSError, FileNotFoundError):
                    pass

    def set_level(self, level):
        """Set the logging level for the RFU logger and its handlers."""
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(level)
        # Keep file handler at DEBUG to capture all messages for tests
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, logging.handlers.RotatingFileHandler
            ):
                handler.setLevel(
                    level
                )  # Console handler follows the set level

    @staticmethod
    def get_logger(name: str):
        """Get a logger instance with the given name."""
        return logging.getLogger(f"RFU.{name}")


class CustomRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Custom rotating file handler that creates rotation files
    in the expected format (base.1.log instead of base.log.1)."""

    def doRollover(self):
        """Override rollover to rename files to match test expectations."""
        # Do the normal rollover first
        super().doRollover()

        # Now rename the files to match test expectations
        base_name = os.path.splitext(self.baseFilename)[0]

        for i in range(1, self.backupCount + 1):
            # Standard Python format: test.log.1, test.log.2, etc.
            python_format = f"{self.baseFilename}.{i}"
            # Expected test format: test.1.log, test.2.log, etc.
            test_format = f"{base_name}.{i}.log"

            if os.path.exists(python_format):
                # Rename to expected format
                if os.path.exists(test_format):
                    os.remove(test_format)
                os.rename(python_format, test_format)
