"""Audio/Video metadata tag viewer and editor.

This module provides functionality to view and edit metadata tags in various
audio and video file formats using a graphical interface.
"""

import sys

from core.error_handler import error_handler
# Third-party imports
from mutagen._file import File  # Note: Using internal module
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from typing import Any, cast

from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog
)
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem
)
from PyQt5 import uic

# Local imports
from gui.common.base_window import BaseWindow
from gui.common.dialogs import show_error_dialog

# Supported file extensions and their descriptions
FILE_FILTERS = (
    "Audio Files (*.mp3 *.flac *.m4a);;"
    "Video Files (*.mp4 *.m4v);;"
    "All Files (*.*)"
)


class TagViewerEditor(BaseWindow):
    """Audio/Video metadata tag viewer and editor window.
    
    Provides a graphical interface for viewing and editing metadata tags
    in audio/video files.
    
    Attributes:
        _current_file: Path to the currently loaded file
        _current_tags: Metadata tags for current file
        _metadata_model: Model for metadata table view
    """

    _current_file: str | None
    _current_tags: Any | None
    _metadata_model: QStandardItemModel

    def __init__(self) -> None:
        """Initialize the tag viewer/editor window.
        
        Sets up:
        - UI components and layout
        - Metadata table model
        - Signal connections
        """
        super().__init__()
        self._setup_ui()
        self._init_metadata_model()
        self._connect_signals()
        
        # Initialize current file state
        self._current_file = None
        self._current_tags = None
        
        self.show()
        
    def _setup_ui(self) -> None:
        """Load and initialize the UI components."""
        uic.loadUi('tag_viewer_editor.ui', self)
        self.metadataTable.horizontalHeader().setStretchLastSection(True)
        
    def _init_metadata_model(self) -> None:
        """Initialize the metadata table model."""
        self._metadata_model = QStandardItemModel()
        self._metadata_model.setHorizontalHeaderLabels(['Tag', 'Value'])
        self.metadataTable.setModel(self._metadata_model)
        
    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers.
        
        Connects:
        - Open file action and button
        - Exit action
        - Update tag button
        - Table selection changes
        """
        self.actionOpen.triggered.connect(self._browse_file)
        self.actionExit.triggered.connect(self.close)
        self.browseButton.clicked.connect(self._browse_file)
        self.updateButton.clicked.connect(self._update_tag)
        self.metadataTable.clicked.connect(self._on_table_click)
        
    def _browse_file(self) -> None:
        """Open file dialog and load selected audio/video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Audio/Video File",
            "",
            FILE_FILTERS
        )

        if not file_path:
            return

        try:
            tags = cast(Any, File(file_path))
            if not tags:
                msg = "File format not supported or file does not exist."
                show_error_dialog("Error", msg, self)
                return

            self._current_file = file_path
            self._current_tags = tags
            self._display_metadata()

        except Exception as e:
            msg = f"Could not load metadata: {str(e)}"
            show_error_dialog("Error", msg, self)

    def _display_metadata(self) -> None:
        """Display metadata tags in the table view."""
        if not self._current_tags:
            return

        # Clear existing items
        self._metadata_model.removeRows(0, self._metadata_model.rowCount())

        # Add each tag to the model
        for tag, value in self._current_tags.items():
            tag_item = QStandardItem(str(tag))
            value_item = QStandardItem(str(value))
            self._metadata_model.appendRow([tag_item, value_item])

    def _update_tag(self) -> None:
        """Update or add a tag in the current file."""
        if not self._current_tags or not self._current_file:
            return

        tag = self.tagNameEdit.text().strip()
        value = self.tagValueEdit.text().strip()

        if not tag or not value:
            show_error_dialog(
                "Warning",
                "Please enter both tag name and value",
                self
            )
            return

        try:
            # Update tag value
            self._current_tags[tag] = value
            cast(Any, self._current_tags).save()

            # Refresh display
            self._display_metadata()

            # Clear input fields
            self.tagNameEdit.clear()
            self.tagValueEdit.clear()

        except Exception as e:
            show_error_dialog(
                "Error",
                f"Failed to update tag: {str(e)}",
                self
            )

    def _on_table_click(self, index: QModelIndex) -> None:
        """Handle table row selection."""
        if not index.isValid():
            return

        # Get selected tag name and value
        row = index.row()
        item = self._metadata_model.item(row, 0)
        if item:
            tag = item.text()
        else:
            return
            
        item = self._metadata_model.item(row, 1)
        if item:
            value = item.text()
        else:
            return

        # Update input fields
        self.tagNameEdit.setText(tag)
        self.tagValueEdit.setText(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagViewerEditor()
    sys.exit(app.exec_())
