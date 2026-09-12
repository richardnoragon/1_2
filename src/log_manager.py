"""
Centralized logging manager for Richard's File Utilities.

This module provides consistent logging functionality across all components
with configurable levels, file rotation, and structured logging.
"""

import logging
import logging.handlers
import os
import sys
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional, Set


class LogManager:
    """Compatibility logging manager used by the project tests and runtime code."""

    _instance = None
    _lock = Lock()

    def __new__(cls, log_file: Optional[str | os.PathLike] = None):
        """Ensure singleton behavior unless tests pass an explicit log_file."""
        if log_file is not None:
            instance = super().__new__(cls)
            instance._initialized = False
            instance._module_filters: Set[str] = set()
            instance._init(log_file)
            return instance

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
                    cls._instance._module_filters = set()
                    cls._instance._init()
        return cls._instance

    def __init__(self, log_file: Optional[str | os.PathLike] = None):
        """Allow explicit per-test file paths without disturbing the singleton."""
        if getattr(self, "_initialized", False):
            return
        self._module_filters = set()
        self._init(log_file)

    def _init(self, log_file: Optional[str | os.PathLike] = None):
        """Initialize logging state for the given log file or default directory."""
        if log_file:
            self.log_file = Path(log_file)
            self.log_dir = self.log_file.parent
        else:
            self.log_dir = Path("logs")
            self.log_dir.mkdir(exist_ok=True)
            self.log_file = self.log_dir / "rfu.log"

        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.log_file.parent.mkdir(exist_ok=True, parents=True)
        self.log_file.touch(exist_ok=True)
        self.context = {}
        self._loggers: Dict[str, logging.Logger] = {}
        self._module_filters = set(getattr(self, "_module_filters", set()))

        self.root_logger = logging.getLogger("RFU")
        self.root_logger.setLevel(logging.INFO)
        self.root_logger.handlers.clear()

        self.detailed_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        self.simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        self._setup_file_handler()
        self._setup_console_handler()
        self._initialized = True
        self.root_logger.info("LogManager initialized successfully")

    def _setup_file_handler(self):
        """Setup rotating file handler."""
        try:
            file_handler = CustomRotatingFileHandler(
                self.log_file,
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self.detailed_formatter)
            self.root_logger.addHandler(file_handler)
            self.file_handler = file_handler
        except Exception as exc:  # pragma: no cover - defensive fallback
            print(f"Failed to setup file logging: {exc}")
            self.file_handler = None

    def _setup_console_handler(self):
        """Setup console handler."""
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(self.simple_formatter)
            self.root_logger.addHandler(console_handler)
            self.console_handler = console_handler
        except Exception as exc:  # pragma: no cover - defensive fallback
            print(f"Failed to setup console logging: {exc}")
            self.console_handler = None

    def _log(self, module: str, message: str, level: int = logging.INFO, exc_info: Any = None):
        """Log a message for a specific module, honoring optional filter gate."""
        if self._module_filters and module not in self._module_filters:
            return
        logger = logging.getLogger("RFU")
        if module:
            logger.log(level, f"[{module}] {message}", exc_info=exc_info)
        else:
            logger.log(level, message, exc_info=exc_info)

    def add_filter(self, module_name: str):
        """Restrict logs to a specific module when set."""
        self._module_filters.add(module_name)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for a component."""
        if not name.startswith("RFU."):
            logger_name = f"RFU.{name}"
        else:
            logger_name = name
        if logger_name in self._loggers:
            return self._loggers[logger_name]
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        self._loggers[logger_name] = logger
        return logger

    def _write_log_record(self, level: int, message: str, exc_info: Any = None):
        """Emit a record directly to each handler while honoring each handler's configured threshold."""
        if self.context:
            context_pairs = [f"{key}:{value}" for key, value in self.context.items()]
            message = f"[{', '.join(context_pairs)}] {message}"

        if exc_info is not None and not isinstance(exc_info, tuple) and exc_info is not True:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)

        record = logging.LogRecord(
            self.root_logger.name,
            level,
            __file__,
            0,
            message,
            (),
            exc_info,
        )

        for handler in list(self.root_logger.handlers):
            if record.levelno >= handler.level:
                handler.handle(record)

    def debug(self, message: str):
        self._write_log_record(logging.DEBUG, message)

    def info(self, message: str):
        self._write_log_record(logging.INFO, message)

    def warning(self, message: str):
        self._write_log_record(logging.WARNING, message)

    def error(self, message: str, exc_info: Any = None):
        self._write_log_record(logging.ERROR, message, exc_info=exc_info)

    def critical(self, message: str):
        self._write_log_record(logging.CRITICAL, message)

    def exception(self, message: str):
        self._write_log_record(logging.ERROR, message, exc_info=True)

    def set_context(self, **kwargs):
        self.context.update(kwargs)

    def configure(self, max_size: Optional[int] = None, backup_count: Optional[int] = None):
        """Reconfigure the rotating file handler."""
        if self.file_handler is not None:
            self.root_logger.removeHandler(self.file_handler)
            self.file_handler.close()

        max_size = max_size or 5 * 1024 * 1024
        backup_count = backup_count or 5
        self.file_handler = CustomRotatingFileHandler(
            self.log_file,
            maxBytes=max_size,
            backupCount=backup_count,
        )
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.detailed_formatter)
        self.root_logger.addHandler(self.file_handler)

    def add_handler(self, handler: logging.Handler):
        self.root_logger.addHandler(handler)

    def set_level(self, level):
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self.root_logger.setLevel(level)
        for handler in self.root_logger.handlers:
            if isinstance(handler, logging.Handler):
                handler.setLevel(level)

    def cleanup_old_logs(self, max_age_days: int = 0):
        """Delete stale log files older than the cutoff in days."""
        cutoff = time.time() - (max_age_days * 24 * 60 * 60)
        for file_path in self.log_dir.glob("*.log"):
            if file_path == self.log_file:
                continue
            try:
                if file_path.stat().st_mtime < cutoff:
                    file_path.unlink()
            except (OSError, FileNotFoundError):
                pass

    def cleanup(self) -> bool:
        """Cleanup logging resources."""
        try:
            for handler in self.root_logger.handlers[:]:
                handler.close()
                self.root_logger.removeHandler(handler)
            self._loggers.clear()
            self.root_logger.info("LogManager cleanup completed")
            return True
        except Exception as exc:  # pragma: no cover - defensive fallback
            print(f"Error during LogManager cleanup: {exc}")
            return False

    @staticmethod
    def get_logger(name: str):
        return logging.getLogger(f"RFU.{name}")


_log_manager = None


def get_log_manager() -> LogManager:
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def get_log_manager_instance():
    return get_log_manager()


class CustomRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotate files into legacy base.1.log naming for compatibility tests."""

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        """Expose the legacy Handler.makeRecord API expected by older compatibility tests."""
        if extra is not None:
            return logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
        return logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        base_name = os.path.splitext(self.baseFilename)[0]
        for i in range(self.backupCount - 1, 0, -1):
            src = f"{base_name}.{i}.log"
            dst = f"{base_name}.{i + 1}.log"
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.replace(src, dst)

        if os.path.exists(self.baseFilename):
            os.replace(self.baseFilename, f"{base_name}.1.log")

        self.mode = 'a'
        self.stream = self._open()


__all__ = ["LogManager", "get_log_manager", "get_log_manager_instance", "CustomRotatingFileHandler"]
