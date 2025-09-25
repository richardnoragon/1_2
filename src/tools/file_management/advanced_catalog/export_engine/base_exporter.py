"""Base exporter interface for the Advanced File Catalog Generator.

This module defines the abstract base class and common functionality
for all export formats.
"""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ExportFormat(Enum):
    """Enumeration of supported export formats."""

    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    EXCEL = "excel"


class BaseExporter(ABC):
    """Abstract base class for all export formats."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.color_preservation = True
        self.accessibility_mode = False
        self.progress_callback = None

    @abstractmethod
    def export(self, catalog_data, output_path: Path) -> bool:
        """Export catalog data to specified format.

        Args:
            catalog_data: CatalogData instance containing file information
            output_path: Path where the exported file should be saved

        Returns:
            bool: True if export was successful, False otherwise
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this format."""
        pass

    @abstractmethod
    def validate_options(self) -> bool:
        """Validate export options.

        Returns:
            bool: True if options are valid, False otherwise
        """
        pass

    def set_accessibility_mode(self, enabled: bool) -> None:
        """Enable/disable accessibility features."""
        self.accessibility_mode = enabled

    def set_color_preservation(self, enabled: bool) -> None:
        """Enable/disable color preservation."""
        self.color_preservation = enabled

    def set_progress_callback(self, callback) -> None:
        """Set progress callback function."""
        self.progress_callback = callback

    def _report_progress(self, percentage: int, message: str = "") -> None:
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(percentage, message)

    def _format_size(self, size: int) -> str:
        """Format file size to human readable format."""
        units = ["B", "KB", "MB", "GB", "TB"]
        size_float = float(size)

        for unit in units:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024

        return f"{size_float:.1f} {units[-1]}"

    def _format_date(
        self, date: datetime, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Format datetime to string."""
        return date.strftime(format_str)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    def _escape_csv(self, text: str) -> str:
        """Escape CSV special characters."""
        if "," in text or '"' in text or "\n" in text:
            return f'"{text.replace('"', '""')}"'
        return text

    def _get_color_hex(self, entry) -> str:
        """Get hex color for an entry."""
        if entry.color_category and self.color_preservation:
            return entry.color_category.color_hex
        return "#FFFFFF"

    def _get_color_rgb(self, entry) -> tuple:
        """Get RGB color for an entry."""
        if entry.color_category and self.color_preservation:
            return entry.color_category.color_rgb
        return (255, 255, 255)

    def _get_accessibility_icon(self, entry) -> str:
        """Get accessibility icon for an entry."""
        if entry.color_category and self.accessibility_mode:
            return entry.color_category.icon
        return ""

    def _get_accessibility_label(self, entry) -> str:
        """Get accessibility label for an entry."""
        if entry.color_category and self.accessibility_mode:
            return entry.color_category.accessibility_label
        return ""

    def _create_export_metadata(self, catalog_data) -> Dict[str, Any]:
        """Create metadata for the export."""
        return {
            "export_format": self.get_file_extension(),
            "export_time": datetime.now().isoformat(),
            "source_directory": (
                str(catalog_data.source_directory)
                if catalog_data.source_directory
                else None
            ),
            "total_files": len(catalog_data.entries),
            "total_size": catalog_data.statistics.total_size,
            "sort_criteria": catalog_data.sort_criteria.value,
            "color_scheme": catalog_data.color_scheme.value,
            "color_preservation": self.color_preservation,
            "accessibility_mode": self.accessibility_mode,
            "exporter_options": self.options,
        }

    def _validate_output_path(self, output_path: Path) -> bool:
        """Validate that output path is writable."""
        try:
            # Check if parent directory exists and is writable
            parent_dir = output_path.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)

            # Test write access by creating a temporary file
            test_file = (
                parent_dir / f".test_write_{datetime.now().timestamp()}"
            )
            test_file.touch()
            test_file.unlink()

            return True
        except (OSError, PermissionError):
            return False

    def _get_file_type_icon(self, file_type) -> str:
        """Get icon for file type."""
        icons = {
            "document": "📄",
            "image": "🖼️",
            "video": "🎥",
            "audio": "🎵",
            "archive": "📦",
            "executable": "⚙️",
            "code": "💻",
            "data": "📊",
            "other": "❓",
        }
        return icons.get(
            file_type.value if hasattr(file_type, "value") else str(file_type),
            "❓",
        )
