"""
File Splitter Logging Integration

This module provides structured logging integration for the file splitter
with file_utilities_2 patterns, including centralized logging, log rotation,
and performance monitoring.
"""

import logging
import logging.handlers
import os
from typing import Optional


class FileSplitterLogger:
    """
    Centralized logging for file splitter operations.

    Provides structured logging with file_utilities_2 integration,
    log rotation, and performance monitoring.
    """

    def __init__(
        self,
        name: str = "file_splitter",
        level: str = "INFO",
        log_dir: Optional[str] = None,
    ):
        """
        Initialize file splitter logger.

        Args:
            name: Logger name
            level: Logging level
            log_dir: Custom log directory (optional)
        """
        self.name = name
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.log_dir = log_dir or self._get_default_log_dir()

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Setup logger
        self.logger = self._setup_logger()

        self.logger.info(f"FileSplitterLogger initialized: {self.log_dir}")

    def _get_default_log_dir(self) -> str:
        """Get default log directory."""
        log_dir = os.path.expanduser("~/.file_utilities_2/logs")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        logger = logging.getLogger(self.name)

        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()

        # Set level
        logger.setLevel(self.level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(funcName)s:%(lineno)d - %(message)s"
        )

        # File handler with rotation
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Get the main logger instance."""
        return self.logger


def get_file_splitter_logger(
    name: str = "file_splitter",
    level: str = "INFO",
    log_dir: Optional[str] = None,
) -> logging.Logger:
    """
    Get configured logger for file splitter operations.

    Args:
        name: Logger name
        level: Logging level
        log_dir: Custom log directory

    Returns:
        Configured logger instance
    """
    splitter_logger = FileSplitterLogger(name, level, log_dir)
    return splitter_logger.get_logger()
