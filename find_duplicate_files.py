import multiprocessing
import threading
import hashlib
import logging
import os
import sys
import time
import shutil
from datetime import datetime
from typing import List, Tuple, Dict

from queue import Queue, Empty
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from gui.common.base_window import BaseWindow
from gui.common.dialogs import (
    show_error_dialog, show_info_dialog, get_existing_directory
)


# Larger files are read by chunks.
CRITIC_SIZE = 100_000_000  # 100 MB.
# Larger files are ignored.
MAX_SIZE = 500_000_000  # 500 MB.

# Strategy constants
MOVE_TO_FOLDER = "Move to Folder"
DELETE_OLDEST = "Delete Oldest Files"
DELETE_NEWEST = "Delete Newest Files"


def get_file_id(file: Path, digest: str) -> str:
    """
    Return the file ID for the specified file.
    A file ID is composed by the file name, a separator
    and the MD5 digest. Duplicate files will have the
    same file ID.
    
    Args:
        file: Path object for the file
        digest: MD5 digest string
        
    Returns:
        File ID string in format "filename|digest"
    """
    return f"{file.name}|{digest}"


def safe_print(print_lock: threading.Lock, *args: object) -> None:
    """
    Like `print()`, but thread-safe.
    
    Args:
        print_lock: Thread lock for safe printing
        *args: Arguments to print
    """
    print_lock.acquire()
    print(*args)
    print_lock.release()


def get_file_md5(file: Path, size: int) -> str:
    """
    Read the contents of the specified `file` and return
    its MD5 digest.
    
    Args:
        file: Path object for the file
        size: File size in bytes
        
    Returns:
        MD5 digest as hexadecimal string
    """
    h = hashlib.md5()
    split = size > CRITIC_SIZE
    with file.open("rb") as f:
        while True:
            # If necessary, read by chunks.
            chunk: bytes = f.read(CRITIC_SIZE if split else -1)
            if chunk:
                h.update(chunk)
            else:
                break
    return h.hexdigest()


def worker(task_queue: Queue[Path],
           print_lock: threading.Lock,
           processed_files: List[Tuple[Path, str]],
           abort: threading.Event) -> None:
    """
    Process files from the `task_queue` until the queue
    is empty or the `abort` flag is set.
    
    Args:
        task_queue: Queue containing Path objects to process
        print_lock: Thread lock for safe printing
        processed_files: List to append processed file data
        abort: Event to signal thread abortion
    """
    while True:
        try:
            file = task_queue.get_nowait()
        except Empty:
            if abort.is_set():
                break
            else:
                continue
        process_file(file, processed_files, print_lock)
        task_queue.task_done()


def process_file(file: Path,
                 processed_files: List[Tuple[Path, str]],
                 print_lock: threading.Lock) -> None:
    """
    Calculate the MD5 digest for the specified `file` and append
    it to the `processed_files` list.
    
    Args:
        file: Path object for the file to process
        processed_files: List to append (file, digest) tuples
        print_lock: Thread lock for safe printing
    """
    size = file.stat().st_size
    # Ignore large files.
    if size > MAX_SIZE:
        safe_print(print_lock, file, "omitted (too big).")
        return
    try:
        hexdigest = get_file_md5(file, size)
    except IOError:
        logging.error(f"Could not read {file}")
    else:
        processed_files.append((file, hexdigest))


class DuplicateFinderApp(BaseWindow):
    """A class that handles duplicate finder app and inherits
    from BaseWindow.
    """
    
    def __init__(self) -> None:
        """Initialize the duplicate finder application."""
        super().__init__()
        # Create a central widget and set it
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Load the UI file onto the central widget
        uic.loadUi('find_duplicate_files.ui', self.central_widget)

        # Set window properties
        self.setWindowTitle("Find Duplicate Files")
        self.setMinimumSize(600, 400)

        # Connect signals using line continuation for long lines
        self.central_widget.buttonBrowseFolder.clicked.connect(
            self.browse_folder)
        self.central_widget.buttonFindDuplicates.clicked.connect(
            self.find_duplicates)
        self.central_widget.buttonApplyAction.clicked.connect(
            self.apply_action)
        self.central_widget.duplicatesTable.itemSelectionChanged.connect(
            self.update_preview)

        # Initialize preview widgets
        self.central_widget.previewLabel.setScaledContents(True)
        self.central_widget.textPreview.setVisible(False)
        
        # Store duplicate files data
        self.duplicate_groups: Dict[str, List[Path]] = {}

        # Add Exit menu item
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close)

        # Add Exit to the menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(exit_action)

        # Set default folder path
        self.central_widget.lineEditFolder.setText("C:\\Users")

    def update_preview(self) -> None:
        """Update the preview area when a file is selected in the table."""
        selected_items = self.central_widget.duplicatesTable.selectedItems()
        if not selected_items:
            return
            
        file_path = Path(selected_items[1].text())  # Path is in second column
        try:
            self._handle_file_preview(file_path)
        except Exception as e:
            logging.error(f"Preview error for {file_path}: {e}")
            self.central_widget.previewLabel.setText(
                f"Error loading preview: {str(e)}")
            self.central_widget.previewLabel.setVisible(True)
            self.central_widget.textPreview.setVisible(False)

    def _handle_file_preview(self, file_path: Path) -> None:
        """Handle file preview based on file type."""
        image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        text_exts = {
            '.txt', '.py', '.csv', '.md', '.log', '.json', '.xml', '.html'
        }
        
        if file_path.suffix.lower() in image_exts:
            pixmap = QPixmap(str(file_path))
            self.central_widget.previewLabel.setPixmap(pixmap.scaled(
                300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.central_widget.previewLabel.setVisible(True)
            self.central_widget.textPreview.setVisible(False)
        
        # Handle text files
        elif file_path.suffix.lower() in text_exts:
            with open(file_path, 'r', encoding='utf-8') as f:
                preview_text = f.read(1000)  # First 1000 characters
                if len(preview_text) == 1000:
                    preview_text += "\n... (file truncated)"
            self.central_widget.textPreview.setText(preview_text)
            self.central_widget.textPreview.setVisible(True)
            self.central_widget.previewLabel.setVisible(False)
        
        else:
            self.central_widget.previewLabel.setText(
                "Preview not available for this file type")
            self.central_widget.previewLabel.setVisible(True)
            self.central_widget.textPreview.setVisible(False)

    def apply_action(self) -> None:
        """Apply the selected deletion strategy to duplicate files."""
        strategy = self.central_widget.deleteStrategyCombo.currentText()
        
        if strategy == MOVE_TO_FOLDER:
            folder = get_existing_directory(self, "Select Destination Folder")
            if not folder:
                return
                
        if not self._confirm_action(strategy):
            return

        success_count, error_count = self._process_files(strategy)
        self._show_results(success_count, error_count)
        self.find_duplicates()  # Refresh the display

    def _confirm_action(self, strategy: str) -> bool:
        """Confirm the action with the user.
        
        Args:
            strategy: The deletion strategy to confirm
            
        Returns:
            True if user confirms, False otherwise
        """
        reply = QtWidgets.QMessageBox.question(
            self, 'Confirm Action',
            f'Are you sure you want to {strategy.lower()}?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        return reply == QtWidgets.QMessageBox.Yes

    def _process_files(self, strategy: str) -> Tuple[int, int]:
        """Process files according to the selected strategy.
        
        Args:
            strategy: The deletion strategy to apply
            
        Returns:
            Tuple of (success_count, error_count)
        """
        success_count = 0
        error_count = 0
        folder = None
        
        if strategy == MOVE_TO_FOLDER:
            folder = get_existing_directory(self, "Select Destination Folder")
            if not folder:
                return 0, 0
        
        for file_id, files in self.duplicate_groups.items():
            if len(files) <= 1:  # Skip if no duplicates
                continue
                
            files_to_process = self._get_files_to_process(files, strategy)
            
            for file in files_to_process:
                try:
                    self._process_single_file(file, strategy, folder)
                    success_count += 1
                except Exception as e:
                    logging.error(f"Error processing {file}: {e}")
                    error_count += 1
        
        return success_count, error_count

    def _get_files_to_process(self, files: List[Path],
                              strategy: str) -> List[Path]:
        """Get list of files to process based on strategy.
        
        Args:
            files: List of duplicate files
            strategy: The deletion strategy
            
        Returns:
            List of files to process
        """
        if strategy == DELETE_OLDEST:
            # Sort by modification time, keep newest
            sorted_files = sorted(files, key=lambda x: x.stat().st_mtime)
            return sorted_files[:-1]  # All except the newest
        elif strategy == DELETE_NEWEST:
            # Sort by modification time, keep oldest
            sorted_files = sorted(files, key=lambda x: x.stat().st_mtime)
            return sorted_files[1:]  # All except the oldest
        else:  # MOVE_TO_FOLDER
            return files[1:]  # All except the first occurrence

    def _process_single_file(self, file: Path, strategy: str,
                           folder: str = None) -> None:
        """Process a single file according to the strategy.
        
        Args:
            file: File to process
            strategy: The deletion strategy
            folder: Destination folder for move operations
        """
        if strategy == MOVE_TO_FOLDER:
            dest = self._get_unique_destination(Path(folder), file)
            shutil.move(str(file), str(dest))
        else:
            file.unlink()  # Delete the file

    def _get_unique_destination(self, dest_folder: Path,
                              file: Path) -> Path:
        """Get unique destination path for file move operation.
        
        Args:
            dest_folder: Destination folder
            file: File to move
            
        Returns:
            Unique destination Path
        """
        dest = dest_folder / file.name
        counter = 1
        while dest.exists():
            stem = dest.stem
            if '_copy' in stem:
                stem = stem[:stem.rfind('_copy')]
            new_name = f"{stem}_copy{counter}{dest.suffix}"
            dest = dest_folder / new_name
            counter += 1
        return dest

    def _show_results(self, success_count: int, error_count: int) -> None:
        """Show operation results to user.
        
        Args:
            success_count: Number of successfully processed files
            error_count: Number of errors encountered
        """
        show_info_dialog(
            self, "Operation Complete",
            f"Successfully processed {success_count} files.\n"
            f"Errors encountered: {error_count}")

    def browse_folder(self) -> None:
        """Show folder selection dialog."""
        folder = get_existing_directory(self, "Select Folder")
        if folder:
            self.central_widget.lineEditFolder.setText(folder)

    def find_duplicates(self) -> None:
        """Validate input and start duplicate search."""
        folder = self.central_widget.lineEditFolder.text().strip()
        file_name = self.central_widget.lineEditFile.text().strip()

        if not folder:
            show_error_dialog(self, "Error", "Please select a folder.")
            return

        if not file_name:
            show_error_dialog(self, "Error", "Please enter a file name.")
            return

        self.run_duplicate_search(folder, file_name)

    def run_duplicate_search(self, folder: str, file_name: str) -> None:
        """Find and display duplicate files.
        
        Args:
            folder: Directory path to search for duplicates
            file_name: Output file name for results
        """
        start_time: float = time.perf_counter()
        logging.basicConfig(
            filename="duplicate_search.log",
            level=logging.DEBUG
        )

        root = Path(folder)

        if not root.exists():
            show_error_dialog(self, "Error",
                f"Directory {root} does not exist.")
            return

        # List of processed files.
        processed_files: List[Tuple[Path, str]] = []
        task_queue: Queue[Path] = Queue()
        print_lock = threading.Lock()
        cores = multiprocessing.cpu_count()
        logging.info(f"{cores} CPU cores available.")
        threads: List[threading.Thread] = []
        abort = threading.Event()

        for _ in range(cores):
            t: threading.Thread = threading.Thread(
                target=worker,
                args=(task_queue, print_lock, processed_files, abort)
            )
            t.start()
            threads.append(t)

        print("Processing files...")
        try:
            # Populate queue with files under root directory
            for path, dirnames, filenames in os.walk(root):
                for filename in filenames:
                    task_queue.put(Path(path, filename))
        except KeyboardInterrupt:
            logging.info("Manually stopped.")

        abort.set()
        for t in threads:
            t.join()

        print(len(processed_files), "processed files.")
        print("Comparing processed files (might take a while)...")

        processed_files_ids = [
            get_file_id(file, digest)
            for file, digest in processed_files
        ]
        duplicate_files: Dict[str, List[Path]] = {}

        for file_data, file_id in zip(processed_files, processed_files_ids):
            file, _digest = file_data
            matches: int = processed_files_ids.count(file_id)
            if matches > 1:
                try:
                    files = duplicate_files[file_id]
                except KeyError:
                    duplicate_files[file_id] = files = []
                files.append(file)

        self.duplicate_groups = duplicate_files
        table = self.central_widget.duplicatesTable
        table.setRowCount(0)
        
        for file_id, files in duplicate_files.items():
            for file in files:
                row = table.rowCount()
                table.insertRow(row)
                
                stats = file.stat()
                modified_time = datetime.fromtimestamp(stats.st_mtime)
                
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(file.name))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(file)))
                size_text = f"{stats.st_size:,} bytes"
                table.setItem(row, 2, QtWidgets.QTableWidgetItem(size_text))
                date_text = modified_time.strftime("%Y-%m-%d %H:%M:%S")
                table.setItem(row, 3, QtWidgets.QTableWidgetItem(date_text))

        table.resizeColumnsToContents()
        
        total_files = sum(len(files) for files in duplicate_files.values())
        show_info_dialog(
            self, "Search Complete",
            f"Found {len(duplicate_files)} groups of duplicate files.\n"
            f"Total files: {total_files}")

        print("Writing results...")
        with open(file_name, "w", encoding="utf8") as f:
            for files in duplicate_files.values():
                matches = len(files)
                # Since `files` have duplicate files, then every file
                # in the list has the same name. Just pick the first one.
                f.write(f"{files[0].name} found {matches} times:\n")
                # Write the full path of each duplicate file.
                for file in files:
                    f.write(f"\t{file}\n")

        print(len(duplicate_files), "duplicate files found.")
        end_time: float = time.perf_counter()
        print("Elapsed time:", end_time - start_time, "seconds.")


def main() -> None:
    """Main function to run the duplicate finder application."""
    app = QtWidgets.QApplication(sys.argv)
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
