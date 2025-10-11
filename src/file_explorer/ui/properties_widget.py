"""
PropertiesWidget: Display file metadata and properties.

Shows file size, modified date, permissions, and full path for
the selected file.
"""

import logging
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class PropertiesWidget(QWidget):
    """Widget displaying file properties and metadata."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the properties widget.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger("RFU.FileExplorer.PropertiesWidget")

        self.current_file: Optional[Path] = None

        self.setup_ui()

        self.logger.info("PropertiesWidget initialized")

    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Properties group
        properties_group = QGroupBox("File Properties")
        form_layout = QFormLayout()

        # Property labels
        self.name_label = QLabel()
        self.name_label.setWordWrap(True)
        form_layout.addRow("Name:", self.name_label)

        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        form_layout.addRow("Path:", self.path_label)

        self.size_label = QLabel()
        form_layout.addRow("Size:", self.size_label)

        self.modified_label = QLabel()
        form_layout.addRow("Modified:", self.modified_label)

        self.permissions_label = QLabel()
        form_layout.addRow("Permissions:", self.permissions_label)

        self.type_label = QLabel()
        form_layout.addRow("Type:", self.type_label)

        properties_group.setLayout(form_layout)
        layout.addWidget(properties_group)

        layout.addStretch()

        # Initialize with empty state
        self.clear()

    def show_properties(self, file_path: str):
        """
        Show properties for a file.

        Args:
            file_path: Path to file
        """
        try:
            path = Path(file_path)
            self.current_file = path

            if not path.exists():
                self.clear()
                self.name_label.setText("File not found")
                return

            # Name
            self.name_label.setText(path.name)

            # Path
            self.path_label.setText(str(path.parent))

            # Size
            if path.is_file():
                size_bytes = path.stat().st_size
                size_str = self.format_size(size_bytes)
                self.size_label.setText(size_str)
            else:
                self.size_label.setText("N/A (Directory)")

            # Modified date
            mtime = path.stat().st_mtime
            modified_dt = datetime.fromtimestamp(mtime)
            modified_str = modified_dt.strftime("%Y-%m-%d %H:%M:%S")
            self.modified_label.setText(modified_str)

            # Permissions
            permissions_str = self.format_permissions(path)
            self.permissions_label.setText(permissions_str)

            # Type
            if path.is_file():
                file_type = path.suffix or "File"
                self.type_label.setText(file_type)
            elif path.is_dir():
                self.type_label.setText("Directory")
            else:
                self.type_label.setText("Unknown")

            self.logger.debug(f"Showing properties for: {file_path}")

        except Exception as e:
            self.logger.error(f"Error showing properties: {e}")
            self.clear()
            self.name_label.setText(f"Error: {e}")

    def format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def format_permissions(self, path: Path) -> str:
        """
        Format file permissions.

        Args:
            path: File path

        Returns:
            Formatted permissions string
        """
        try:
            mode = path.stat().st_mode

            # Read/Write/Execute for owner
            perms = []
            if mode & stat.S_IRUSR:
                perms.append("Read")
            if mode & stat.S_IWUSR:
                perms.append("Write")
            if mode & stat.S_IXUSR:
                perms.append("Execute")

            if not perms:
                return "No permissions"

            return ", ".join(perms)

        except Exception:
            return "Unknown"

    def clear(self):
        """Clear the properties display."""
        self.current_file = None
        self.name_label.setText("No file selected")
        self.path_label.setText("")
        self.size_label.setText("")
        self.modified_label.setText("")
        self.permissions_label.setText("")
        self.type_label.setText("")
