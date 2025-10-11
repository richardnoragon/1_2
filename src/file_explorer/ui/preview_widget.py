"""
PreviewWidget: Display file previews for text and images.

Provides extensible preview handlers for different file types with
graceful fallback for unsupported types.
"""

import logging
from pathlib import Path
from typing import Optional, Protocol

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QLabel,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PreviewHandler(Protocol):
    """Protocol for file preview handlers."""

    def can_preview(self, file_path: Path) -> bool:
        """Check if this handler can preview the file."""
        ...

    def preview(self, file_path: Path, widget: QWidget) -> bool:
        """Generate preview in the widget. Returns success status."""
        ...


class TextPreviewHandler:
    """Handler for text file previews."""

    TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".py",
        ".js",
        ".json",
        ".xml",
        ".html",
        ".css",
        ".log",
        ".ini",
        ".cfg",
        ".yaml",
        ".yml",
    }

    def can_preview(self, file_path: Path) -> bool:
        """Check if file is a text file."""
        return file_path.suffix.lower() in self.TEXT_EXTENSIONS

    def preview(self, file_path: Path, text_edit: QTextEdit) -> bool:
        """
        Load text file into text edit widget.

        Args:
            file_path: Path to file
            text_edit: QTextEdit widget to populate

        Returns:
            True if successful
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read(100000)  # Limit to 100KB
                text_edit.setPlainText(content)
                return True
        except Exception:
            return False


class ImagePreviewHandler:
    """Handler for image file previews."""

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
    }

    def can_preview(self, file_path: Path) -> bool:
        """Check if file is an image."""
        return file_path.suffix.lower() in self.IMAGE_EXTENSIONS

    def preview(self, file_path: Path, label: QLabel) -> bool:
        """
        Load image into label widget.

        Args:
            file_path: Path to image
            label: QLabel widget to display image

        Returns:
            True if successful
        """
        try:
            pixmap = QPixmap(str(file_path))
            if pixmap.isNull():
                return False

            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                800,
                600,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return True
        except Exception:
            return False


class PreviewWidget(QWidget):
    """Widget for previewing files."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the preview widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.PreviewWidget")

        # Preview handlers
        self.handlers = [
            TextPreviewHandler(),
            ImagePreviewHandler(),
        ]

        self.current_file: Optional[Path] = None

        self.setup_ui()

        self.logger.info("PreviewWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Stacked widget for different preview types
        self.stack = QStackedWidget()

        # Text preview
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.stack.addWidget(self.text_preview)

        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.image_preview)

        # Unsupported type message
        self.unsupported_label = QLabel("Preview not available for this file type")
        self.unsupported_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unsupported_label.setStyleSheet("color: gray; font-style: italic;")
        self.stack.addWidget(self.unsupported_label)

        layout.addWidget(self.stack)

    def preview_file(self, file_path: str):
        """
        Preview a file.

        Args:
            file_path: Path to file to preview
        """
        try:
            path = Path(file_path)
            self.current_file = path

            if not path.exists() or not path.is_file():
                self.show_unsupported()
                return

            # Try each handler
            for handler in self.handlers:
                if handler.can_preview(path):
                    if isinstance(handler, TextPreviewHandler):
                        success = handler.preview(path, self.text_preview)
                        if success:
                            self.stack.setCurrentWidget(self.text_preview)
                            self.logger.debug(f"Text preview: {file_path}")
                            return

                    elif isinstance(handler, ImagePreviewHandler):
                        success = handler.preview(path, self.image_preview)
                        if success:
                            self.stack.setCurrentWidget(self.image_preview)
                            self.logger.debug(f"Image preview: {file_path}")
                            return

            # No handler could preview the file
            self.show_unsupported()

        except Exception as e:
            self.logger.error(f"Error previewing file: {e}")
            self.show_unsupported()

    def show_unsupported(self):
        """Show unsupported file type message."""
        self.stack.setCurrentWidget(self.unsupported_label)

    def clear(self):
        """Clear the preview."""
        self.current_file = None
        self.text_preview.clear()
        self.image_preview.clear()
        self.show_unsupported()
