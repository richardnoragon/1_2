import os
import time
import random
import string
from PyQt5.QtCore import QObject, pyqtSignal
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread
from PyQt5 import uic
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QUrl

CHUNK_SIZE = 1024 * 1024  # 1MB buffer for overwriting


class SecureDeleteLogic(QObject):
    """Handles the logic for securely deleting (shredding) files."""
    progress_updated = pyqtSignal(int, int, str)  # value, total, message (e.g., pass/total_passes)
    file_progress = pyqtSignal(int, int)        # bytes_processed, total_bytes (for current pass)
    operation_complete = pyqtSignal(str)          # success message
    error_occurred = pyqtSignal(str)            # error message
    finished = pyqtSignal()                       # signals thread completion

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._filepath = None

    def stop(self):
        self.progress_updated.emit(0, 1, "Stopping deletion...")
        self._is_running = False

    def _generate_random_bytes(self, length):
        """Generates a block of random bytes."""
        return os.urandom(length)

    def _generate_random_filename(self, length=16):
        """Generates a random filename string."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def shred_file(self, filepath, passes=3):
        """Securely deletes a file by overwriting it multiple times."""
        self._is_running = True
        self._filepath = filepath
        current_pass = 0

        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            if not os.path.isfile(filepath):
                raise ValueError(f"Path is not a file: {filepath}")

            if passes <= 0:
                raise ValueError("Number of passes must be positive.")

            file_size = os.path.getsize(filepath)
            self.progress_updated.emit(0, passes, f"Starting secure delete for {os.path.basename(filepath)} ({passes} passes)")

            # --- Overwriting Passes ---
            for i in range(passes):
                if not self._is_running:
                    break
                current_pass = i + 1
                pass_message = f"Overwrite Pass {current_pass}/{passes}"
                self.progress_updated.emit(current_pass - 1, passes, pass_message)
                self.file_progress.emit(0, file_size)

                bytes_written_this_pass = 0
                pattern_type = ""

                # Define patterns (simple approach based on pass number)
                if i == 0:
                    pattern = b'\x00'
                    pattern_type = "(Zeros)"
                elif i == 1 and passes > 1:
                    pattern = b'\xFF'
                    pattern_type = "(Ones)"
                else:
                    pattern = None  # Indicates random data per chunk
                    pattern_type = "(Random)"

                self.progress_updated.emit(current_pass - 1, passes, f"{pass_message} {pattern_type}")

                try:
                    # Use 'rb+' to open for reading/writing without truncating
                    with open(filepath, 'rb+') as f:
                        while bytes_written_this_pass < file_size:
                            if not self._is_running:
                                break

                            chunk_fill_size = min(CHUNK_SIZE, file_size - bytes_written_this_pass)

                            if pattern is not None:
                                data_to_write = pattern * chunk_fill_size
                            else:
                                data_to_write = self._generate_random_bytes(chunk_fill_size)

                            f.seek(bytes_written_this_pass)
                            f.write(data_to_write)
                            bytes_written_this_pass += len(data_to_write)
                            self.file_progress.emit(bytes_written_this_pass, file_size)

                        if not self._is_running:
                            break

                        # Ensure data is physically written (crucial!)
                        f.flush()
                        os.fsync(f.fileno())

                except Exception as e:
                    # Catch errors during file access within a pass
                    raise IOError(f"Error during overwrite pass {current_pass}: {e}") from e

            if not self._is_running:
                self.error_occurred.emit("Deletion cancelled during overwriting.")
                # State is uncertain, do not proceed with delete/rename
                self.finished.emit()
                return

            # --- Rename before final delete (Obscurity) ---
            self.progress_updated.emit(passes, passes, "Renaming file...")
            new_name = self._generate_random_filename()
            dir_path = os.path.dirname(filepath)
            new_filepath = os.path.join(dir_path, new_name)
            try:
                # Ensure file is closed before renaming
                # Rename might fail if handle still open, but 'with open' handles closure.
                os.rename(filepath, new_filepath)
                self._filepath = new_filepath  # Update path for deletion
                self.progress_updated.emit(passes, passes, "File renamed.")
            except Exception as e:
                # If rename fails, still try to delete original path but warn
                self.error_occurred.emit(f"Warning: Could not rename file before deletion: {e}. Attempting deletion of original name.")

            # --- Final Deletion ---
            if not self._is_running:  # Check again before final delete
                self.error_occurred.emit("Deletion cancelled before final removal.")
                # We might have renamed, state is uncertain.
                self.finished.emit()
                return

            self.progress_updated.emit(passes, passes, f"Deleting file entry: {os.path.basename(self._filepath)}")
            try:
                os.remove(self._filepath)
                self.operation_complete.emit(f"File securely deleted: {os.path.basename(filepath)} (final name: {os.path.basename(self._filepath)})")
            except Exception as e:
                raise OSError(f"Error deleting final file entry '{self._filepath}': {e}") from e

        except (FileNotFoundError, ValueError, IOError, OSError) as e:
            if self._is_running:  # Don't emit error if stopped
                self.error_occurred.emit(f"Error: {e}")
        except PermissionError as e:
            if self._is_running:
                self.error_occurred.emit(f"Permission Error: {e}. Check file permissions.")
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(f"An unexpected error occurred: {e}")
        finally:
            self._is_running = False
            self.finished.emit()


class SecureDeleteThread(QThread):
    def __init__(self, logic, filepath, passes):
        super().__init__()
        self.logic = logic
        self.filepath = filepath
        self.passes = passes
        
    def run(self):
        self.logic.shred_file(self.filepath, self.passes)


class SecureDeleteGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Get the directory containing the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the absolute path to the UI file
        ui_file = os.path.join(current_dir, "secure_delete.ui")
        uic.loadUi(ui_file, self)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.filePathEdit.setAcceptDrops(True)
        
        # Initialize attributes and connect signals 
        self.logic = SecureDeleteLogic()
        self.delete_thread = None
        
        # Connect signals
        self.browseButton.clicked.connect(self.browse_file)
        self.deleteButton.clicked.connect(self.secure_delete)
        self.cancelButton.clicked.connect(self.cancel_delete)
        self.actionExit.triggered.connect(self.close)
        
        # Connect logic signals
        self.logic.progress_updated.connect(self.update_progress)
        self.logic.file_progress.connect(self.update_file_progress)
        self.logic.operation_complete.connect(self.operation_complete)
        self.logic.error_occurred.connect(self.show_error)
        self.logic.finished.connect(self.operation_finished)
        
        self.show()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            # Use the first dropped item's path
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                self.filePathEdit.setText(path)
                self.deleteButton.setEnabled(True)
            else:
                self.show_error("Please drop a file, not a folder")
    
    def browse_file(self):
        """Open file dialog to select a file to delete."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Securely Delete",
            "",
            "All Files (*.*)"
        )
        if filepath:
            self.filePathEdit.setText(filepath)
            self.deleteButton.setEnabled(True)
    
    def secure_delete(self):
        """Start the secure deletion process."""
        filepath = self.filePathEdit.text()
        if not filepath:
            self.show_error("Please select a file to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.warning(
            self,
            "Confirm Secure Delete",
            f"Are you sure you want to securely delete this file?\n{filepath}\n\n"
            "This operation cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Get number of passes
            passes = self.passesSpinBox.value()
            
            # Disable UI elements
            self.deleteButton.setEnabled(False)
            self.browseButton.setEnabled(False)
            self.passesSpinBox.setEnabled(False)
            self.cancelButton.setEnabled(True)
            
            # Start deletion in a separate thread
            self.delete_thread = SecureDeleteThread(self.logic, filepath, passes)
            self.delete_thread.start()
    
    def cancel_delete(self):
        """Cancel the secure deletion process."""
        if self.logic._is_running:
            self.logic.stop()
            self.statusLabel.setText("Canceling deletion...")
            self.cancelButton.setEnabled(False)
    
    def update_progress(self, value, total, message):
        """Update the overall progress and status message."""
        progress = (value / total) * 100
        self.progressBar.setValue(int(progress))
        self.statusLabel.setText(message)
    
    def update_file_progress(self, bytes_processed, total_bytes):
        """Update the progress for current file operation."""
        if total_bytes > 0:
            progress = (bytes_processed / total_bytes) * 100
            self.progressBar.setValue(int(progress))
    
    def operation_complete(self, message):
        """Handle completion of the secure deletion."""
        self.statusLabel.setText(message)
        QMessageBox.information(self, "Operation Complete", message)
        self.reset_ui()
    
    def show_error(self, message):
        """Display error message."""
        self.statusLabel.setText(f"Error: {message}")
        QMessageBox.critical(self, "Error", message)
        self.reset_ui()
    
    def operation_finished(self):
        """Reset UI after operation completes or fails."""
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI elements to initial state."""
        self.deleteButton.setEnabled(True)
        self.browseButton.setEnabled(True)
        self.passesSpinBox.setEnabled(True)
        self.cancelButton.setEnabled(False)
        self.progressBar.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecureDeleteGUI()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from config_manager import ConfigManager

class SecureDelete(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("secure_delete.ui", self)
        
        # Load settings
        config = ConfigManager()
        default_passes = config.get_setting("secure_delete", "default_passes")
        self.passesSpinBox.setValue(default_passes)
        
        # Apply current theme
        theme = config.get_setting("general", "theme")
        if theme == "dark":
            self.apply_dark_theme()
    
    def apply_dark_theme(self):
        """Apply dark theme to this window."""
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QWidget { color: #ffffff; }
            QPushButton { 
                background-color: #3b3b3b;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #4b4b4b; }
            QLineEdit {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 5px;
            }
            QSpinBox {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 5px;
            }
            QLabel { color: #ffffff; }
            QProgressBar {
                border: 1px solid #555555;
                background-color: #3b3b3b;
                color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4b4b4b;
            }
        """)