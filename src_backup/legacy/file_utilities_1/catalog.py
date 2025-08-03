"""File cataloging tool with HTML report generation.

This module provides functionality to create HTML catalogs of files
with optional metadata and duplicate detection capabilities.
"""

import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import List, Optional, TextIO, Tuple

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5 import uic

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.common.base_window import BaseWindow
from gui.common.dialogs import get_existing_directory, show_error_dialog


class CatalogWindow(BaseWindow):
    """Main window for directory cataloging operations.
    
    This window provides a graphical interface for creating HTML catalogs of
    directory contents with various options for metadata inclusion.
    
    Features:
    - Directory selection and recursive scanning
    - File size and date display options
    - Duplicate file detection
    - HTML report generation with customizable styling
    
    Attributes:
        _current_dir (str): Path to currently selected directory
        _last_catalog (Optional[str]): Path to most recently generated catalog
        _list_model (QStandardItemModel): Model for main file list view
    """
    # Default paths
    _ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
    _ICON_NAME = "catalog.png"
    _UI_FILE = "catalog.ui"

    # Size formatting units
    _SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def __init__(self) -> None:
        """Initialize the CatalogWindow.
        
        Sets up:
        - UI components and layout
        - Data models and internal state
        - Signal connections
        - Icons and initial UI state
        """
        super().__init__()
        self._init_models()
        self._setup_ui()  # Load UI before connecting signals
        self._setup_icons()
        self._connect_signals()  # Connect signals after UI is loaded
        self._set_initial_state()
        self.show()
        
    def _init_models(self) -> None:
        """Initialize data models and internal state."""
        self._current_dir = ""
        self._last_catalog: Optional[str] = None
        self._list_model = QStandardItemModel()
        self.listListView.setModel(self._list_model)
    
    def _setup_ui(self) -> None:
        """Initialize and load the UI file.
        
        Raises:
            FileNotFoundError: If UI file doesn't exist
            ValueError: If UI file is empty
        """
        try:
            ui_file = Path(__file__).parent / self._UI_FILE
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
                
            if not ui_file.stat().st_size:
                raise ValueError("UI file is empty")
                
            uic.loadUi(str(ui_file), self)
            
        except (FileNotFoundError, ValueError) as e:
            show_error_dialog(str(e), "UI Error", self)
            sys.exit(1)
            
        except Exception as e:
            show_error_dialog(f"Failed to initialize UI: {e}", "Error", self)
            sys.exit(1)
    
    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots.
        
        Connects:
        - Directory selection buttons
        - Catalog generation button
        - Menu actions
        """
        # Connect buttons
        if hasattr(self, 'selectFolderButton'):
            self.selectFolderButton.clicked.connect(self._load_directory)
        if hasattr(self, 'catalogPushButton'):
            self.catalogPushButton.clicked.connect(self._generate_catalog)
            
        # Connect menu actions
        if hasattr(self, 'actionexit'):
            self.actionexit.triggered.connect(self.close)
        if hasattr(self, 'actionselect'):
            self.actionselect.triggered.connect(self._load_directory)
        if hasattr(self, 'actionopen_catalog'):
            self.actionopen_catalog.triggered.connect(self._open_last_catalog)
        
    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements.
        
        Disables catalog-related controls until a directory is selected.
        """
        self.catalogPushButton.setEnabled(False)
        self.actionopen_catalog.setEnabled(False)
        self.status_label.setText("Select a folder to begin")
    
    def _setup_icons(self) -> None:
        """Load application icons from the icons folder."""
        icon_file = Path(self._ICON_PATH) / self._ICON_NAME
        if icon_file.exists():
            self.setWindowIcon(QIcon(str(icon_file)))
    
    def _format_size(self, size: int) -> str:
        """Format file size to human readable format.
        
        Args:
            size: Size in bytes to format
            
        Returns:
            str: Formatted size string with appropriate unit
        """
        for unit in self._SIZE_UNITS:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} {self._SIZE_UNITS[-1]}"
    
    def _load_directory(self) -> None:
        """Load directory and display files in the list view.
        
        Prompts user to select a directory and updates the UI accordingly.
        """
        directory = get_existing_directory(self, "Select Directory")
        if directory:
            self._current_dir = directory
            self.directory_label.setText(directory)
            self._update_file_list()
            self.catalogPushButton.setEnabled(True)
            self.status_label.setText("Ready to generate catalog")
    
    def _update_file_list(self) -> None:
        """Update the list view with files from the selected directory.
        
        Lists files according to the recursive option setting. Shows relative
        paths when in recursive mode.
        """
        self._list_model.clear()
        
        try:
            files = self._get_file_list()
            for file_info in sorted(files):
                self._add_file_to_list(file_info)
                
        except OSError as e:
            show_error_dialog(
                f"Could not read directory: {str(e)}",
                title="Error",
                parent=self
            )
            
    def _get_file_list(self) -> List[Tuple[str, str]]:
        """Get list of files from the current directory.
        
        Returns:
            List[Tuple[str, str]]: List of (display_path, full_path) tuples
        """
        files = []
        base_path = Path(self._current_dir)
        
        if self.recursiveCheckBox.isChecked():
            # Recursive mode - walk directory tree
            for path in base_path.rglob('*'):
                if path.is_file():
                    rel_path = str(path.relative_to(base_path))
                    files.append((rel_path, str(path)))
        else:
            # Non-recursive mode - list current directory only
            for path in base_path.iterdir():
                if path.is_file():
                    files.append((path.name, str(path)))
                    
        return files
    
    def _add_file_to_list(self, file_info: Tuple[str, str]) -> None:
        """Add a file entry to the list model.
        
        Args:
            file_info: Tuple of (display_path, full_path)
        """
        display_path, _ = file_info
        item = QStandardItem(display_path)
        self._list_model.appendRow(item)
    
    def _check_duplicate(self, file_path: str) -> bool:
        """Check if a file is a duplicate by comparing content with other files.
        
        Performs byte-by-byte comparison with other files in the directory tree.
        Skip unreadable files.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if duplicate is found, False otherwise
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return False
            
        try:
            content = file_path.read_bytes()
            base_path = Path(self._current_dir)
            
            # Check against all other files
            for other_path in base_path.rglob('*'):
                if (other_path.is_file() and
                    other_path != file_path and
                    other_path.stat().st_size == len(content)):
                    try:
                        if other_path.read_bytes() == content:
                            return True
                    except OSError:
                        continue
                        
            return False
            
        except OSError:
            return False

    # HTML templates
    _HTML_HEADER = """<!DOCTYPE html>
<html>
<head>
    <title>Catalog of {dir_name}</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { color: #2196F3; }
        .file-list { list-style: none; padding: 0; }
        .file-item {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #fff;
        }
        .file-item:hover { background: #f5f5f5; }
        .duplicate { color: #f44336; }
        .file-info { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>File Catalog: {dir_name}</h1>
    <p>Generated on {timestamp}</p>
    <ul class="file-list">
"""
    _HTML_FOOTER = "</ul></body></html>"

    def _generate_catalog(self) -> None:
        """Generate HTML catalog of files.
        
        Creates an HTML report with file listings and optional metadata like
        sizes, dates, and duplicate status.
        """
        if not self._current_dir:
            return
            
        try:
            catalog_path = self._write_catalog_file()
            self._update_ui_after_catalog(catalog_path)
            
        except Exception as e:
            show_error_dialog(
                f"Failed to create catalog: {str(e)}",
                title="Error",
                parent=self
            )
            self.status_label.setText("Error generating catalog")

    def _write_catalog_file(self) -> str:
        """Write the catalog HTML file.
        
        Returns:
            str: Path to the generated catalog file
            
        Raises:
            OSError: If file cannot be written
        """
        catalog_path = os.path.join(self._current_dir, "catalog.html")
        
        with open(catalog_path, "w", encoding='utf-8') as html:
            # Write header
            html.write(self._HTML_HEADER.format(
                dir_name=os.path.basename(self._current_dir),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            # Process and write file entries
            for file_info in self._get_files_to_process():
                self._write_file_entry(html, file_info)
                
            # Close HTML
            html.write(self._HTML_FOOTER)
            
        return catalog_path

    def _get_files_to_process(self) -> List[Tuple[str, str, str]]:
        """Get list of files to include in catalog.
        
        Returns:
            List[Tuple[str, str, str]]: List of (root, filename, rel_path)
        """
        files = []
        base_path = Path(self._current_dir)
        
        if self.recursiveCheckBox.isChecked():
            for path in base_path.rglob('*'):
                if path.is_file():
                    files.append((
                        str(path.parent),
                        path.name,
                        str(path.relative_to(base_path))
                    ))
        else:
            for path in base_path.iterdir():
                if path.is_file():
                    files.append((
                        str(base_path),
                        path.name,
                        path.name
                    ))
                    
        return sorted(files)

    def _write_file_entry(
        self,
        html_file: TextIO,
        file_info: Tuple[str, str, str]
    ) -> None:
        """Write a single file entry to the catalog.
        
        Args:
            html_file: Open file handle for writing HTML
            file_info: Tuple of (root_path, filename, relative_path)
        """
        root, filename, rel_path = file_info
        file_path = os.path.join(root, filename)
        
        try:
            stats = os.stat(file_path)
            is_dup = (
                self.identdupCheckBox.isChecked() and
                self._check_duplicate(file_path)
            )
            
            info_parts = self._get_file_info_parts(stats)
            info_str = " | ".join(info_parts)
            
            dup_class = ' class="duplicate"' if is_dup else ""
            dup_prefix = "DUPLICATE: " if is_dup else ""
            
            # Split long line for readability
            file_link = f"file:///{file_path}"
            file_text = f"{dup_prefix}{rel_path}"
            
            html_file.write(f"""
                <li class="file-item">
                    <div{dup_class}>
                        <a href="{file_link}">{file_text}</a>
                    </div>
                    <div class="file-info">{info_str}</div>
                </li>
            """)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    def _get_file_info_parts(self, stats: 'os.stat_result') -> List[str]:
        """Get formatted file information parts.
        
        Args:
            stats: Result of os.stat() call on file
            
        Returns:
            List[str]: List of formatted info strings
        """
        parts = []
        
        if self.showSizesCheckBox.isChecked():
            parts.append(f"Size: {self._format_size(stats.st_size)}")
            
        if self.showDatesCheckBox.isChecked():
            mtime = datetime.fromtimestamp(stats.st_mtime)
            date_str = mtime.strftime('%Y-%m-%d %H:%M:%S')
            parts.append(f"Modified: {date_str}")
            
        return parts
        
    def _update_ui_after_catalog(self, catalog_path: str) -> None:
        """Update UI state after catalog generation.
        
        Args:
            catalog_path: Path to the generated catalog
        """
        self._last_catalog = catalog_path
        self.actionopen_catalog.setEnabled(True)
        
        reply = QMessageBox.question(
            self,
            "Catalog Created",
            f"Catalog has been created at:\n{catalog_path}\n\n"
            "Would you like to open it now?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self._open_last_catalog()
            
        self.status_label.setText("Catalog generated successfully")
    
    def _open_last_catalog(self) -> None:
        """Open the last generated catalog in the default web browser.
        
        Shows an error dialog if no catalog is available.
        """
        if self._last_catalog and os.path.exists(self._last_catalog):
            webbrowser.open(f"file:///{self._last_catalog}")
        else:
            show_error_dialog(
                "No catalog file available",
                title="Error",
                parent=self
            )


def main() -> None:
    """Main entry point for the catalog application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    _ = CatalogWindow()  # Keep reference to prevent garbage collection
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
