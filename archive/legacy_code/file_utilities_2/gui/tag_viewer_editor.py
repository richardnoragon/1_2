"""Audio/Video metadata tag viewer and editor.

This module provides functionality to view and edit metadata tags in various
audio and video file formats using a graphical interface.

Migrated to file_utilities_2 architecture with StandardWindow inheritance
and integrated ThemeManager support.
"""

import os
import sys

# Third-party imports
from mutagen._file import File  # Note: Using internal module
from typing import Any, cast, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic

# Local imports - file_utilities_2 architecture
from .standard_window import StandardWindow
from .themes import ThemeManager

# Supported file extensions and their descriptions
FILE_FILTERS = (
    "Audio Files (*.mp3 *.flac *.m4a);;"
    "Video Files (*.mp4 *.m4v);;"
    "All Files (*.*)"
)


class TagViewerEditor(StandardWindow):
    """Audio/Video metadata tag viewer and editor window.
    
    Provides a graphical interface for viewing and editing metadata tags
    in audio/video files.
    
    Attributes:
        _current_file: Path to the currently loaded file
        _current_tags: Metadata tags for current file
        _metadata_model: Model for metadata table view
    """

    _current_file: Optional[str]
    _current_tags: Optional[Any]
    _metadata_model: QStandardItemModel

    def __init__(self) -> None:
        """Initialize the tag viewer/editor window.
        
        Sets up:
        - UI components and layout using StandardWindow pattern
        - Metadata table model
        - Signal connections
        - Theme integration
        """
        # Initialize StandardWindow with appropriate title
        super().__init__(title="Audio/Video Tag Editor")
        
        # Load UI and setup components
        self._load_ui()
        self._setup_ui_components()
        self._init_metadata_model()
        self._connect_signals()
        
        # Initialize current file state
        self._current_file = None
        self._current_tags = None
        
        # Configure the metadata table
        self.metadataTable.horizontalHeader().setStretchLastSection(True)
        
        # Show the window
        self.show()
        
    def _load_ui(self) -> None:
        """Load UI file using file_utilities_2 pattern."""
        ui_file = os.path.join(
            os.path.dirname(__file__), "tag_viewer_editor.ui"
        )
        uic.loadUi(ui_file, self)
        
    def _setup_ui_components(self) -> None:
        """Setup UI components with theme integration."""
        # Apply theme styling to maintain consistency
        ThemeManager.apply_utility_window_theme(self)
        
        # Style input fields
        ThemeManager.style_input_field(self.filePathEdit)
        ThemeManager.style_input_field(self.keyEdit)
        ThemeManager.style_input_field(self.valueEdit)
        
        # Style buttons
        ThemeManager.style_primary_button(self.browseButton)
        ThemeManager.style_primary_button(self.updateButton)
        
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
            tags: Any = cast(Any, File(file_path))
            if not tags:
                msg: str = "File format not supported or file does not exist."
                self._show_error("Error", msg)
                return

            self._current_file = file_path
            self._current_tags = tags
            
            # Update file path display
            self.filePathEdit.setText(file_path)
            
            # Display metadata
            self._display_metadata()
            
            # Update status
            self.show_status_message(f"Loaded: {os.path.basename(file_path)}")

        except Exception as e:
            msg: str = f"Could not load metadata: {str(e)}"
            self._show_error("Error", msg)

    def _display_metadata(self) -> None:
        """Display metadata tags in the table view."""
        if not self._current_tags:
            return

        # Clear existing items
        self._metadata_model.removeRows(0, self._metadata_model.rowCount())

        # Add each tag to the model
        for tag, value in self._current_tags.items():
            tag_item: QStandardItem = QStandardItem(str(tag))
            value_item: QStandardItem = QStandardItem(str(value))
            self._metadata_model.appendRow([tag_item, value_item])

    def _update_tag(self) -> None:
        """Update or add a tag in the current file."""
        if not self._current_tags or not self._current_file:
            return

        tag: str = self.keyEdit.text().strip()
        value: str = self.valueEdit.text().strip()

        if not tag or not value:
            self._show_warning(
                "Warning",
                "Please enter both tag name and value"
            )
            return

        try:
            # Update tag value
            self._current_tags[tag] = value
            cast(Any, self._current_tags).save()

            # Refresh display
            self._display_metadata()

            # Clear input fields
            self.keyEdit.clear()
            self.valueEdit.clear()
            
            # Update status
            self.show_status_message(f"Updated tag: {tag}")

        except Exception as e:
            self._show_error(
                "Error",
                f"Failed to update tag: {str(e)}"
            )

    def _on_table_click(self, index: QModelIndex) -> None:
        """Handle table row selection."""
        if not index.isValid():
            return

        # Get selected tag name and value
        row: int = index.row()
        tag_item: Optional[QStandardItem] = self._metadata_model.item(row, 0)
        if not tag_item:
            return
        tag: str = tag_item.text()
            
        value_item: Optional[QStandardItem] = self._metadata_model.item(row, 1)
        if not value_item:
            return
        value: str = value_item.text()

        # Update input fields
        self.keyEdit.setText(tag)
        self.valueEdit.setText(value)

    def _show_error(self, title: str, message: str) -> None:
        """Show error dialog using PyQt5 directly."""
        QMessageBox.critical(self, title, message)

    def _show_warning(self, title: str, message: str) -> None:
        """Show warning dialog using PyQt5 directly."""
        QMessageBox.warning(self, title, message)

    def _show_info(self, title: str, message: str) -> None:
        """Show info dialog using PyQt5 directly."""
        QMessageBox.information(self, title, message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagViewerEditor()
    sys.exit(app.exec_())
