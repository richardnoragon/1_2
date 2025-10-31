"""Unified error handling utilities for RFU."""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox


class ErrorHandler(QObject):
    """Centralized error handling with GUI-friendly fallbacks."""

    error_occurred = pyqtSignal(str, str)  # title, message

    def __init__(self) -> None:
        super().__init__()
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._configure()

    def _configure(self) -> None:
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "rfu.log"

        self.logger = logging.getLogger("RFU.ErrorHandler")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)

            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            stream_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        if exception:
            self.logger.error("%s: %s", message, exception)
        else:
            self.logger.error(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    # ------------------------------------------------------------------
    # Dialog helpers
    # ------------------------------------------------------------------
    def _exec_dialog(self, dialog: QMessageBox) -> None:
        try:
            dialog.exec_()
        except Exception as exc:  # pragma: no cover - GUI safety net
            print(f"Dialog display failed: {exc}")

    def show_error_dialog(
        self, title: str, message: str, details: Optional[str] = None
    ) -> None:
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        if details:
            dialog.setDetailedText(details)
        self._exec_dialog(dialog)
        self.error_occurred.emit(title, message)

    def show_warning_dialog(self, title: str, message: str) -> None:
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        self._exec_dialog(dialog)

    def show_info_dialog(self, title: str, message: str) -> None:
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Information)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        self._exec_dialog(dialog)

    # ------------------------------------------------------------------
    # Exception handling
    # ------------------------------------------------------------------
    def handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        self.logger.error("Uncaught exception: %s", error_msg)

        if QApplication.instance() is not None:
            self.show_error_dialog("Unexpected Error", str(exc_value))

    def handle_error(
        self,
        error: Exception,
        operation: str,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        show_dialog: bool = True,
    ) -> bool:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context_line = f"Context: {context}\n" if context else ""
        formatted = traceback.format_exc()
        if formatted.strip() == "NoneType: None":
            formatted = ""
        traceback_line = formatted if formatted else ""

        details = (
            f"Timestamp: {timestamp}\n"
            f"Operation: {operation}\n"
            f"Error: {error}\n"
            f"{context_line}Traceback:\n{traceback_line}"
        )
        self.logger.error(details)

        if show_dialog:
            default_msg = (
                f"An error occurred while {operation}.\n"
                "The error has been logged for review."
            )
            message = user_message or default_msg
            self.show_error_dialog("Operation Failed", message, details)

        return False


# ----------------------------------------------------------------------
# Convenience helpers mirroring legacy interface
# ----------------------------------------------------------------------
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def safe_execute(func: Callable[..., Any], *args, **kwargs) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        get_error_handler().log_error(f"Error executing {func.__name__}", exc)
        return None


def handle_gui_error(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - GUI wrapper
            get_error_handler().show_error_dialog(
                "GUI Error",
                f"An error occurred in {func.__name__}: {exc}",
                traceback.format_exc(),
            )
            return None

    return wrapper


error_handler = get_error_handler()
sys.excepthook = error_handler.handle_exception
