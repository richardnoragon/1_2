"""Size Analyzer tool for analyzing directory contents and sizes.

This module provides functionality to analyze directory structures and calculate
various statistics about file and folder sizes.
"""

import os

from core.error_handler import error_handler
import sys
from typing import Dict, TypeAlias, Union

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic

from gui.common.base_window import BaseWindow
from gui.common.dialogs import get_existing_directory, show_error_dialog

# Type aliases for clearer type hints
Path = str
Count = int
Size = int
Average = float

# Type alias for directory statistics dictionary
DirStats: TypeAlias = Dict[str, Union[Path, Count, Size, Average]]


class SizeAnalyzerWindow(BaseWindow):
    """Main window for the Size Analyzer tool.
    
    This window provides a graphical interface for analyzing directory contents
    and calculating size-related statistics.
    
    Features:
    - Directory selection and browsing
    - File and folder counting
    - Size calculations (total and averages)
    - Results visualization
    
    Attributes:
        _current_dir (Union[str, None]): Path to currently selected directory
        _list_model (QStandardItemModel): Model for main file list view
        _select_model (QStandardItemModel): Model for selection view
        _selected_files (list[str]): List of currently selected files
    """
    
    # Default directory when no selection is made
    DEFAULT_DIR = "."
    
    # Result format strings
    FORMAT_STRINGS = {
        'directory': 'Directory: {}',
        'total_files': 'Total files: {}',
        'total_folders': 'Total folders: {}',
        'total_size': 'Total size: {:,} bytes',
        'avg_file_size': 'Average file size: {:,.2f} bytes',
        'avg_folder_size': 'Average folder size: {:,.2f} bytes'
    }

    def __init__(self) -> None:
        """Initialize the SizeAnalyzerWindow.
        
        Sets up:
        - UI components and layout
        - Data models
        - Signal connections
        """
        super().__init__()
        self._setup_ui()
        self._init_models()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize and load the UI file.
        
        Loads and validates the UI definition file. Sets up the UI components
        and displays the window.
        
        Raises:
            FileNotFoundError: If UI file doesn't exist
            ValueError: If UI file is empty
            Exception: For any other initialization errors
        """
        try:
            ui_file = self._get_ui_file_path()
            self._validate_ui_file(ui_file)
            uic.loadUi(ui_file, self)
            self.show()
            
        except (FileNotFoundError, ValueError) as e:
            self._handle_ui_error(str(e), "UI Error")
            
        except Exception as e:
            self._handle_ui_error(f"Failed to initialize UI: {e}", "Error")
            
    def _get_ui_file_path(self) -> str:
        """Get the absolute path to the UI file.
        
        Returns:
            str: Absolute path to size_analyzer.ui
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, 'size_analyzer.ui')
        
    def _validate_ui_file(self, ui_file: str) -> None:
        """Validate that the UI file exists and is not empty.
        
        Args:
            ui_file: Path to the UI file to validate
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty
        """
        if not os.path.exists(ui_file):
            raise FileNotFoundError(f"UI file not found: {ui_file}")
            
        if not os.path.getsize(ui_file):
            raise ValueError("UI file is empty")
            
    def _handle_ui_error(self, message: str, title: str) -> None:
        """Handle UI initialization errors.
        
        Args:
            message: Error message to display
            title: Dialog title
        """
        show_error_dialog(message, title, self)
        sys.exit(1)

    def _init_models(self) -> None:
        """Initialize data models and internal state.
        
        Sets up:
        - File list model
        - Selection model
        - Selected files list
        - Current directory
        """
        self._current_dir = self.DEFAULT_DIR
        self._list_model = QStandardItemModel()
        self._select_model = QStandardItemModel()
        self._selected_files = []

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers.
        
        Connects:
        - Directory selection action
        - Exit action
        - Analyze button
        """
        self.actionselect.triggered.connect(self._load_directory)
        self.actionexit.triggered.connect(self.close)
        self.size_analyzer_button.clicked.connect(self._analyze_directory)

    def _load_directory(self) -> None:
        """Load files from user-selected directory into the view.
        
        Shows a directory selection dialog and populates the file list
        with files (not directories) from the selected path.
        """
        selected_dir = get_existing_directory(self, "Select Directory")
        if not selected_dir:
            return
            return
            
        self._current_dir = selected_dir
        self._update_file_list()
        
    def _update_file_list(self) -> None:
        """Update the file list view with files from current directory.
        
        Populates the list view with all files (not directories) from the
        current directory. Shows error dialog if directory access fails.
        """
        try:
            self._list_model.clear()
            if not self._validate_current_dir():
                return
                
            files = self._get_files_in_directory()
            self._populate_file_list(files)
            self.output_ListView.setModel(self._list_model)
            
        except (PermissionError, OSError) as e:
            self._handle_directory_error(e)
            
    def _validate_current_dir(self) -> bool:
        """Check if current directory is set and accessible.
        
        Returns:
            bool: True if directory is valid, False otherwise
        """
        if not self._current_dir:
            self._show_message("Please select a directory first")
            return False
            
        if not os.path.exists(self._current_dir):
            self._show_message("Selected directory no longer exists")
            return False
            
        if not os.path.isdir(self._current_dir):
            self._show_message("Selected path is not a directory")
            return False
            
        return True
        
    def _get_files_in_directory(self) -> list[str]:
        """Get list of files in the current directory.
        
        Returns:
            list[str]: List of filenames (excluding directories)
            
        Raises:
            OSError: If directory cannot be read
        """
        dir_path = str(self._current_dir)
        return [
            filename for filename in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, filename))
        ]
        
    def _populate_file_list(self, files: list[str]) -> None:
        """Add files to the list model.
        
        Args:
            files: List of filenames to add to the model
        """
        for filename in files:
            self._list_model.appendRow(QStandardItem(filename))
            
    def _handle_directory_error(self, error: Exception) -> None:
        """Handle directory access errors.
        
        Args:
            error: The exception that occurred
        """
        show_error_dialog(
            f"Failed to read directory: {error}",
            "Directory Error",
            self
        )

    def _analyze_directory(self) -> None:
        """Analyze the selected directory and display statistics.
        
        This method:
        1. Validates the current directory selection
        2. Calculates directory statistics recursively
        3. Displays the results in the UI
        4. Handles any errors that occur during analysis
        """
        if not self._validate_current_dir():
            return

        try:
            stats = self._calculate_directory_stats(self._current_dir)
            self._display_analysis_results(stats)
            
        except OSError as e:
            self._handle_analysis_error(e)
            
    def _handle_analysis_error(self, error: OSError) -> None:
        """Handle errors that occur during directory analysis.
        
        Args:
            error: The OS error that occurred
        """
        show_error_dialog(
            f"Failed to analyze directory: {error}",
            "Analysis Error",
            self
        )

    def _calculate_directory_stats(
        self,
        dir_path: Path
    ) -> Dict[str, Union[Path, Count, Size, Average]]:
        """Calculate statistics for a directory.
        
        Recursively scans directory contents to calculate:
        - Total number of files and folders
        - Total size of all files
        - Average file and folder sizes
        
        Args:
            dir_path: Path to the directory to analyze
            
        Returns:
            Dictionary containing directory statistics
            
        Raises:
            OSError: If directory cannot be read
        """
        scan_stats = self._scan_directory(dir_path)
        
        total_files = int(scan_stats['total_files'])
        total_folders = int(scan_stats['total_folders'])
        total_size = int(scan_stats['total_size'])
        
        return {
            'path': dir_path,
            'total_files': total_files,
            'total_folders': total_folders,
            'total_size': total_size,
            'avg_file_size': self._calculate_average(total_size, total_files),
            'avg_folder_size': self._calculate_average(
                total_size, total_folders
            )
        }
        
    def _calculate_average(self, total: int, count: int) -> float:
        """Calculate average from total and count.
        
        Args:
            total: Total value (e.g., total size)
            count: Number of items (e.g., file count)
            
        Returns:
            float: Average value or 0 if count is 0
        """
        return float(total / count if count > 0 else 0)
        
    def _scan_directory(self, dir_path: Path) -> Dict[str, Count | Size]:
        """Recursively scan a directory to gather statistics.
        
        Traverses the directory tree and accumulates:
        - Number of files encountered
        - Number of subdirectories encountered
        - Total size of all files
        
        Args:
            dir_path: Directory path to scan
            
        Returns:
            Dictionary with counts of files, folders and total size
            
        Raises:
            OSError: If a directory cannot be accessed
        """
        stats = self._init_scan_stats()
        
        try:
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    try:
                        self._process_dir_entry(entry, stats)
                    except OSError:
                        continue  # Skip inaccessible entries
                        
        except OSError as e:
            self._handle_scan_error(dir_path, e)
            
        return stats
        
    def _init_scan_stats(self) -> Dict[str, Count | Size]:
        """Initialize directory scan statistics.
        
        Returns:
            Dictionary with counters initialized to 0
        """
        return {
            'total_files': 0,
            'total_folders': 0,
            'total_size': 0
        }
        
    def _process_dir_entry(
        self,
        entry: os.DirEntry,
        stats: Dict[str, Count | Size]
    ) -> None:
        """Process a directory entry and update statistics.
        
        Args:
            entry: Directory entry to process
            stats: Statistics dictionary to update
            
        Raises:
            OSError: If entry cannot be accessed
        """
        if entry.is_dir(follow_symlinks=False):
            stats['total_folders'] += 1
            sub_stats = self._scan_directory(entry.path)
            self._merge_stats(stats, sub_stats)
        else:
            stats['total_files'] += 1
            stats['total_size'] += entry.stat().st_size
            
    def _merge_stats(
        self,
        target: Dict[str, Count | Size],
        source: Dict[str, Count | Size]
    ) -> None:
        """Merge source statistics into target statistics.
        
        Args:
            target: Target statistics dictionary to update
            source: Source statistics to merge from
        """
        for key in ['total_files', 'total_folders', 'total_size']:
            target[key] = target[key] + int(source[key])
            
    def _handle_scan_error(self, dir_path: Path, error: OSError) -> None:
        """Handle errors during directory scanning.
        
        Args:
            dir_path: Path where error occurred
            error: The OS error that occurred
        """
        show_error_dialog(
            f"Error scanning {dir_path}: {error}",
            "Scan Error",
            self
        )

    def _display_analysis_results(
        self,
        stats: Dict[str, Union[Path, Count, Size, Average]]
    ) -> None:
        """Display directory analysis results.
        
        Formats and displays:
        - Directory path
        - Total file and folder counts
        - Total size of all files
        - Average file and folder sizes
        
        Args:
            stats: Dictionary containing directory statistics
        """
        formats = self.FORMAT_STRINGS
        output = self._format_analysis_results(stats, formats)
        self._update_output_view(output)

    def _format_analysis_results(
        self,
        stats: Dict[str, Union[Path, Count, Size, Average]],
        formats: Dict[str, str]
    ) -> list[str]:
        """Format analysis results for display.
        
        Args:
            stats: Dictionary containing directory statistics
            formats: Format strings for each statistic type
            
        Returns:
            list[str]: Formatted output lines
        """
        stat_order = [
            ('directory', 'path'),
            ('total_files', 'total_files'),
            ('total_folders', 'total_folders'),
            ('total_size', 'total_size'),
            ('avg_file_size', 'avg_file_size'),
            ('avg_folder_size', 'avg_folder_size')
        ]
        
        return [
            formats[format_key].format(stats[stat_key])
            for format_key, stat_key in stat_order
        ]
        
    def _update_output_view(self, lines: list[str]) -> None:
        """Update the output view with new content.
        
        Args:
            lines: List of text lines to display
        """
        output_model = QStandardItemModel()
        for line in lines:
            output_model.appendRow(QStandardItem(line))
        self.output_ListView.setModel(output_model)
        
    def _show_message(self, message: str) -> None:
        """Display a message in the output view.
        
        Used for showing status messages, warnings and errors.
        
        Args:
            message: Message to display
        """
        self._update_output_view([message])

    def cleanup(self) -> None:
        """Clean up application resources.
        
        Frees resources held by:
        - List model
        - Selection model
        - Selected files list
        """
        self._list_model.clear()
        self._select_model.clear()
        self._selected_files.clear()

    def close(self) -> bool:
        """Close the window.
        
        Performs cleanup and closes the window.
        
        Returns:
            bool: True if the window was closed successfully
        """
        self.cleanup()
        return super().close()


def main() -> None:
    """Application entry point.
    
    This function:
    1. Creates the main application instance
    2. Shows the main window
    3. Starts the event loop
    4. Handles any fatal errors
    5. Ensures clean shutdown
    
    The application will exit when:
    - The user closes the window
    - A fatal error occurs during startup
    """
    try:
        app = QApplication(sys.argv)
        window = SizeAnalyzerWindow()
        window.show()
        exit_code = app.exec_()
        sys.exit(exit_code)
        
    except Exception as e:
        show_error_dialog(
            f"Application failed to start: {e}",
            "Fatal Error",
            None
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
