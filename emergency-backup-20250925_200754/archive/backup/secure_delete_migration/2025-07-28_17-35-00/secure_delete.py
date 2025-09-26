import os
import sys
import random
import string
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QLabel, QComboBox)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from gui.standard_window import StandardWindow
from gui.themes import ThemeManager, Colors
from gui.common.dialogs import get_open_file_name

CHUNK_SIZE = 1024 * 1024  # 1MB buffer for overwriting


class SecureDeleteLogic(QObject):
    """Handles the logic for securely deleting (shredding) files."""
    progress_updated = pyqtSignal(int, int, str)  # value, total, message
    file_progress = pyqtSignal(int, int)        # bytes_processed, total_bytes
    operation_complete = pyqtSignal(str)          # success message
    error_occurred = pyqtSignal(str)            # error message
    finished = pyqtSignal()                       # signals thread completion

    def __init__(self) -> None:
        """Initialize the secure delete logic."""
        super().__init__()
        self._is_running = False
        self._filepath: Optional[str] = None

    def stop(self) -> None:
        """Stop the deletion process."""
        self.progress_updated.emit(0, 1, "Stopping deletion...")
        self._is_running = False

    def _generate_random_bytes(self, length: int) -> bytes:
        """Generate a block of random bytes."""
        return os.urandom(length)

    def _generate_random_filename(self, length: int = 16) -> str:
        """Generate a random filename string."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def shred_file(self, filepath: str, passes: int = 3) -> None:
        """Securely delete a file by overwriting it multiple times."""
        self._is_running = True
        self._filepath = filepath
        
        try:
            if not os.path.isfile(filepath):
                self.error_occurred.emit(f"File not found: {filepath}")
                return

            file_size = os.path.getsize(filepath)
            
            for pass_num in range(passes):
                if not self._is_running:
                    break
                
                self.progress_updated.emit(
                    pass_num + 1, passes,
                    f"Pass {pass_num + 1}/{passes}"
                )
                
                # Overwrite with random data
                with open(filepath, 'r+b') as f:
                    f.seek(0)
                    bytes_written = 0
                    
                    while bytes_written < file_size and self._is_running:
                        chunk_size = min(CHUNK_SIZE, file_size - bytes_written)
                        random_data = self._generate_random_bytes(chunk_size)
                        f.write(random_data)
                        bytes_written += chunk_size
                        
                        self.file_progress.emit(bytes_written, file_size)
                        
                        # Flush to ensure data is written to disk
                        f.flush()
                        os.fsync(f.fileno())

            if self._is_running:
                # Rename file multiple times
                current_path = filepath
                for i in range(3):
                    if not self._is_running:
                        break
                    dir_name = os.path.dirname(current_path)
                    new_name = self._generate_random_filename()
                    new_path = os.path.join(dir_name, new_name)
                    try:
                        os.rename(current_path, new_path)
                        current_path = new_path
                    except OSError:
                        break

                # Finally delete the file
                if self._is_running:
                    os.remove(current_path)
                    self.operation_complete.emit(
                        f"File securely deleted: {os.path.basename(filepath)}")

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class SecureDeleteGUI(StandardWindow):
    """Secure file deletion utility with standardized styling."""
    
    def __init__(self) -> None:
        super().__init__("Secure File Delete")
        self.delete_thread: Optional[QThread] = None
        self.delete_logic: Optional[SecureDeleteLogic] = None
        self.file_path: Optional[str] = None
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Setup the user interface with standardized styling."""
        # Create header
        header = self.create_header("Secure File Delete")
        self.main_layout.addWidget(header)
        
        # Create file selection group
        file_group = self.create_group_box("File Selection")
        file_layout = QVBoxLayout()
        
        # File path display
        self.file_label = QLabel("No file selected")
        ThemeManager.style_label(self.file_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        select_btn = self.create_button("Select File", self.select_file)
        delete_btn = self.create_button("Secure Delete", self.start_deletion)
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(delete_btn)
        
        file_layout.addWidget(self.file_label)
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        self.main_layout.addWidget(file_group)
        
        # Create options group
        options_group = self.create_group_box("Options")
        options_layout = QVBoxLayout()
        
        # Passes selection
        passes_layout = QHBoxLayout()
        passes_label = QLabel("Overwrite Passes:")
        ThemeManager.style_label(passes_label)
        
        self.passes_combo = self.create_combo_box()
        self.passes_combo.addItems(["1", "3", "7", "35"])
        self.passes_combo.setCurrentText("3")
        
        passes_layout.addWidget(passes_label)
        passes_layout.addWidget(self.passes_combo)
        passes_layout.addStretch()
        
        options_layout.addLayout(passes_layout)
        options_group.setLayout(options_layout)
        self.main_layout.addWidget(options_group)
        
        # Create progress group
        progress_group = self.create_group_box("Progress")
        progress_layout = QVBoxLayout()
        
        # Progress bars
        self.overall_progress = self.create_progress_bar()
        self.file_progress = self.create_progress_bar()
        
        self.overall_label = QLabel("Ready")
        self.file_label = QLabel("")
        ThemeManager.style_label(self.overall_label)
        ThemeManager.style_label(self.file_label)
        
        progress_layout.addWidget(self.overall_label)
        progress_layout.addWidget(self.overall_progress)
        progress_layout.addWidget(self.file_label)
        progress_layout.addWidget(self.file_progress)
        
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)
        
        # Create info group
        info_group = self.create_group_box("Information")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "This tool securely deletes files by overwriting them multiple times\n"
            "with random data, making recovery impossible.\n\n"
            "Warning: This operation is irreversible!"
        )
        info_text.setWordWrap(True)
        ThemeManager.style_label(info_text)
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        self.main_layout.addWidget(info_group)
        
        # Set up drag and drop
        self.setAcceptDrops(True)
        
    def create_combo_box(self) -> QComboBox:
        """Create a standardized combo box."""
        combo = QComboBox()
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {Colors.TEXT_DISABLED};
                border-radius: 4px;
                padding: 8px 12px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
                min-height: 30px;
            }}
            QComboBox:focus {{
                border: 2px solid {Colors.ACCENT};
            }}
        """)
        return combo
        
    def select_file(self) -> None:
        """Select file to securely delete."""
        file_path = get_open_file_name(self, "Select File to Delete")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.show_status_message(f"Selected: {file_path}")
            
    def start_deletion(self) -> None:
        """Start the secure deletion process."""
        if not hasattr(self, 'file_path') or self.file_path is None:
            self.show_error_dialog("Error", "Please select a file first")
            return
            
        passes = int(self.passes_combo.currentText())
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to securely delete:\n{os.path.basename(self.file_path)}\n\n"
            f"This operation will use {passes} overwrite passes and cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # Start deletion
        self.overall_progress.setVisible(True)
        self.file_progress.setVisible(True)
        
        self.delete_logic = SecureDeleteLogic()
        self.delete_thread = QThread()
        self.delete_logic.moveToThread(self.delete_thread)
        
        # Connect signals
        self.delete_logic.progress_updated.connect(self.update_overall_progress)
        self.delete_logic.file_progress.connect(self.update_file_progress)
        self.delete_logic.operation_complete.connect(self.deletion_complete)
        self.delete_logic.error_occurred.connect(self.handle_error)
        self.delete_logic.finished.connect(self.delete_thread.quit)
        self.delete_thread.started.connect(
            lambda: self.delete_logic.shred_file(str(self.file_path), passes))
        
        self.delete_thread.start()
        
    def update_overall_progress(self, value: int, total: int, message: str) -> None:
        """Update overall progress."""
        self.overall_progress.setMaximum(total)
        self.overall_progress.setValue(value)
        self.overall_label.setText(message)
        self.show_status_message(message)
        
    def update_file_progress(self, processed: int, total: int) -> None:
        """Update file progress."""
        self.file_progress.setMaximum(total)
        self.file_progress.setValue(processed)
        self.file_label.setText(f"Processing: {processed}/{total} bytes")
        
    def deletion_complete(self, message: str) -> None:
        """Handle successful deletion."""
        self.overall_progress.setVisible(False)
        self.file_progress.setVisible(False)
        self.file_label.setText("")
        self.file_label.setText("No file selected")
        self.show_info_dialog("Success", message)
        
    def handle_error(self, error_message: str) -> None:
        """Handle errors during deletion."""
        self.overall_progress.setVisible(False)
        self.file_progress.setVisible(False)
        self.show_error_dialog("Error", error_message)
        
    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        """Handle drag enter events."""
        if a0.mimeData().hasUrls():
            a0.acceptProposedAction()
            
    def dropEvent(self, a0: QDropEvent) -> None:
        """Handle drop events."""
        files = [u.toLocalFile() for u in a0.mimeData().urls()]
        for file_path in files:
            if os.path.isfile(file_path):
                self.file_path = file_path
                self.file_label.setText(os.path.basename(file_path))
                self.show_status_message(f"Dropped: {file_path}")
                break
                
    def closeEvent(self, a0) -> None:
        """Clean up when closing."""
        if self.delete_thread and self.delete_thread.isRunning():
            if self.delete_logic:
                self.delete_logic.stop()
            self.delete_thread.quit()
            self.delete_thread.wait()
        a0.accept()


def main() -> None:
    """Main function to run the secure delete utility."""
    app = QApplication(sys.argv)
    window = SecureDeleteGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

