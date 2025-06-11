import os
import math
import json
from PyQt5.QtCore import QObject, pyqtSignal
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QUrl

# Constants
CHUNK_RW_SIZE = 1024 * 1024  # 1MB read/write buffer
METADATA_FILENAME = "_metadata.json"


class FileOperationLogic(QObject):
    """Handles the logic for splitting and joining files."""
    # Signals for UI updates
    # value, total, message
    progress_updated = pyqtSignal(int, int, str)
    # success message
    operation_complete = pyqtSignal(str)
    # error message
    error_occurred = pyqtSignal(str)
    # signals thread completion
    finished = pyqtSignal()

    def __init__(self):
        """Initializes the FileOperationLogic."""
        super().__init__()
        self._is_running = False

    def stop(self):
        """Stops the current operation."""
        self.progress_updated.emit(0, 1, "Stopping operation...")
        self._is_running = False

    def _calculate_split_params(self, file_size, split_mode, value, unit_multiplier=1):
        """
        Calculates chunk size and number of chunks based on user input.

        Args:
            file_size (int): The total size of the file to be split.
            split_mode (str): Either 'size' or 'parts'.
            value (float or int): The size value or the number of parts.
            unit_multiplier (int, optional): Multiplier for size units (e.g., 1024 for KB). Defaults to 1.

        Returns:
            tuple[int, int]: A tuple containing (chunk_size, num_chunks).

        Raises:
            ValueError: If input parameters are invalid (e.g., non-positive).
        """
        if file_size == 0:
            return 0, 0  # No chunks needed for an empty file

        if split_mode == 'size':
            chunk_size = int(value * unit_multiplier)
            if chunk_size <= 0:
                raise ValueError("Chunk size must be positive.")
            # If chunk size >= file size, create only one chunk
            if chunk_size >= file_size:
                num_chunks = 1
                chunk_size = file_size
            else:
                num_chunks = math.ceil(file_size / chunk_size)
        elif split_mode == 'parts':
            num_chunks = int(value)
            if num_chunks <= 0:
                raise ValueError("Number of parts must be positive.")
            # Calculate chunk size, ensure last chunk handles remainder
            # Use ceiling to ensure num_chunks is met, last chunk might be smaller
            chunk_size = math.ceil(file_size / num_chunks)
        else:
            raise ValueError(f"Invalid split mode: {split_mode}")

        # Limit padding practicalities and potential excessive chunk creation
        if num_chunks > 9999:
            raise ValueError("Too many chunks requested (max 9999).")

        return chunk_size, num_chunks

    def split_file(self, input_filepath, output_dir, split_mode, value, unit_multiplier=1):
        """
        Splits the input file into smaller chunks based on specified mode and value.

        Args:
            input_filepath (str): Path to the file to be split.
            output_dir (str): Directory where chunks will be saved.
            split_mode (str): Either 'size' or 'parts'.
            value (float or int): The size value or the number of parts.
            unit_multiplier (int, optional): Multiplier for size units. Defaults to 1.
        """
        self._is_running = True
        try:
            # --- Input Validation ---
            if not os.path.exists(input_filepath):
                raise FileNotFoundError(f"Input file not found: {input_filepath}")
            if not os.path.isfile(input_filepath):
                raise ValueError(f"Input path is not a file: {input_filepath}")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            elif not os.path.isdir(output_dir):
                raise ValueError(f"Output path is not a directory: {output_dir}")

            file_size = os.path.getsize(input_filepath)
            base_filename = os.path.basename(input_filepath)

            # --- Handle Empty File ---
            if file_size == 0:
                self.operation_complete.emit("Input file is empty. No chunks created.")
                self._is_running = False
                self.finished.emit()
                return

            # --- Calculate Parameters ---
            chunk_size, num_chunks = self._calculate_split_params(
                file_size, split_mode, value, unit_multiplier
            )

            if num_chunks == 0: # Should only happen for zero size file, handled above
                self.operation_complete.emit("No chunks needed (likely zero-byte file).")
                self._is_running = False
                self.finished.emit()
                return

            # Determine padding length (e.g., 3 for up to 999 chunks -> .part001)
            padding = max(3, len(str(num_chunks)))
            chunk_pattern = f"{base_filename}.part{{:0{padding}d}}"

            self.progress_updated.emit(0, num_chunks, f"Starting split: {num_chunks} chunks, approx size {chunk_size} bytes...")

            # --- Perform Splitting ---
            bytes_written_total = 0
            chunks_created = 0
            with open(input_filepath, 'rb') as infile:
                for i in range(num_chunks):
                    if not self._is_running:
                        break
                    chunk_num = i + 1
                    chunk_filename = chunk_pattern.format(chunk_num)
                    chunk_filepath = os.path.join(output_dir, chunk_filename)
                    self.progress_updated.emit(
                        chunks_created, num_chunks,
                        f"Writing chunk {chunk_num}/{num_chunks}: {chunk_filename}"
                    )

                    bytes_written_this_chunk = 0
                    try:
                        with open(chunk_filepath, 'wb') as outfile:
                            # Read and write in smaller blocks within the larger chunk target
                            while bytes_written_this_chunk < chunk_size:
                                if not self._is_running:
                                    break
                                # Calculate remaining needed for this chunk
                                remaining_in_chunk = chunk_size - bytes_written_this_chunk
                                # Determine read size: min of buffer, remaining in chunk, remaining in file
                                read_size = min(CHUNK_RW_SIZE, remaining_in_chunk, file_size - bytes_written_total)

                                if read_size <= 0:  # No more data left in file or chunk full
                                    break

                                data = infile.read(read_size)
                                if not data:  # End of input file reached unexpectedly
                                    break

                                outfile.write(data)
                                bytes_written_this_chunk += len(data)
                                bytes_written_total += len(data)

                    except OSError as write_error:
                         # Try to clean up the partially written chunk on error
                         if os.path.exists(chunk_filepath):
                              try: os.remove(chunk_filepath)
                              except OSError: pass # Ignore cleanup error
                         raise OSError(f"Error writing chunk {chunk_filename}: {write_error}") from write_error

                    if not self._is_running:
                        # Clean up the chunk if cancelled during write
                        if os.path.exists(chunk_filepath):
                              try: os.remove(chunk_filepath)
                              except OSError: pass # Ignore cleanup error
                        break

                    chunks_created += 1
                    # Emit progress *after* chunk is successfully written
                    self.progress_updated.emit(chunks_created, num_chunks, f"Finished chunk {chunk_num}/{num_chunks}")

            # --- Finalization ---
            if not self._is_running:
                # TODO: Consider option to clean up all successfully written chunks on cancel?
                self.error_occurred.emit("Split operation cancelled.")
            else:
                # Create metadata file
                metadata = {
                    'original_filename': base_filename,
                    'total_size': file_size,
                    'num_chunks': num_chunks,
                    # Note: This might be approximate if split by parts, use ceiling value
                    'chunk_size': chunk_size,
                    'chunk_pattern': chunk_pattern,
                    'padding': padding
                }
                meta_filepath = os.path.join(output_dir, METADATA_FILENAME)
                try:
                    with open(meta_filepath, 'w') as metafile:
                        json.dump(metadata, metafile, indent=4)
                except Exception as e:
                    # Emit as warning, split itself succeeded
                    self.error_occurred.emit(f"Warning: Could not write metadata file: {e}")

                self.operation_complete.emit(f"File successfully split into {chunks_created} chunks in {output_dir}.")

        # --- Error Handling ---
        except (FileNotFoundError, ValueError, IOError) as e:
            self.error_occurred.emit(f"Error: {e}")
        except PermissionError as e:
            self.error_occurred.emit(f"Permission Error: {e}. Check file/directory permissions.")
        except OSError as e:
            self.error_occurred.emit(f"Disk Error: {e}. Check available disk space or permissions.")
        except Exception as e:
            # Catch-all for unexpected errors
            self.error_occurred.emit(f"An unexpected error occurred during split: {e}")
        finally:
            # Ensure state is reset and thread signal is emitted regardless of outcome
            self._is_running = False
            self.finished.emit()

    def join_files(self, first_chunk_path, output_filepath):
        """
        Joins file chunks (starting from the specified first chunk) back into a single file.

        Args:
            first_chunk_path (str): Path to the first chunk file (e.g., file.part001).
            output_filepath (str): Path where the joined file will be saved.
        """
        self._is_running = True
        try:
            # --- Input Validation ---
            if not os.path.exists(first_chunk_path):
                raise FileNotFoundError(f"First chunk file not found: {first_chunk_path}")
            if not os.path.isfile(first_chunk_path):
                raise ValueError(f"Selected path is not a file: {first_chunk_path}")

            chunk_dir = os.path.dirname(first_chunk_path)
            chunk_basename = os.path.basename(first_chunk_path)

            # --- Load Metadata or Infer Parameters ---
            metadata = None
            num_chunks = 0
            chunk_pattern = ""
            padding = 0
            expected_total_size = None
            original_filename = None # Used for output filename suggestion if not provided

            meta_filepath = os.path.join(chunk_dir, METADATA_FILENAME)
            if os.path.exists(meta_filepath):
                try:
                    with open(meta_filepath, 'r') as f:
                        metadata = json.load(f)
                    num_chunks = metadata['num_chunks']
                    chunk_pattern = metadata['chunk_pattern']
                    padding = metadata['padding']
                    # Optional fields from metadata
                    expected_total_size = metadata.get('total_size')
                    original_filename = metadata.get('original_filename')
                    self.progress_updated.emit(0, 1, f"Loaded metadata for '{original_filename or 'file'}'")
                except (json.JSONDecodeError, KeyError, Exception) as e:
                    self.progress_updated.emit(0, 1, f"Warning: Metadata file invalid ({e}), attempting manual join.")
                    metadata = None  # Reset on failure, proceed with inference
            else:
                 self.progress_updated.emit(0, 1, "Metadata file not found, attempting manual join.")


            # --- Infer Parameters if Metadata Failed/Missing ---
            if not metadata:
                # Infer from first chunk name (e.g., file.part001)
                parts = chunk_basename.rsplit('.part', 1) # Use rsplit for names like "archive.tar.gz.part001"
                if len(parts) != 2 or not parts[1].isdigit():
                    raise ValueError("Cannot infer chunk sequence from filename. Expected format like 'filename.partXXX'.")

                base_filename_inferred = parts[0]
                padding = len(parts[1])
                # Ensure first part number matches inference logic (should be 1)
                try:
                    if int(parts[1]) != 1:
                         raise ValueError(f"Expected first chunk number to be 1, found {int(parts[1])} in '{chunk_basename}'.")
                except ValueError: # Should not happen due to isdigit() check, but safety first
                     raise ValueError("Chunk number suffix is not a valid integer.")

                chunk_pattern = f"{base_filename_inferred}.part{{:0{padding}d}}"

                # Count chunks manually (less reliable but necessary fallback)
                num_chunks = 0
                for i in range(1, 10000):  # Check up to 9999 chunks
                    check_path = os.path.join(chunk_dir, chunk_pattern.format(i))
                    if os.path.exists(check_path):
                        num_chunks += 1
                    else:
                        break  # Stop at the first missing chunk in sequence

                if num_chunks == 0: # Should be at least 1 if first_chunk_path exists
                    raise ValueError("Could not find any valid sequential chunks to join starting from the provided file.")

                expected_total_size = None  # Cannot know for sure without metadata
                original_filename = base_filename_inferred # Use inferred name
                self.progress_updated.emit(0, num_chunks, f"Found {num_chunks} potential chunks based on pattern.")

            # --- Prepare Output ---
            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except OSError as e:
                     raise OSError(f"Could not create output directory '{output_dir}': {e}") from e

            # --- Perform Joining ---
            self.progress_updated.emit(0, num_chunks, f"Starting join operation for {num_chunks} chunks...")
            bytes_written_total = 0
            chunks_processed = 0

            try:
                with open(output_filepath, 'wb') as outfile:
                    for i in range(num_chunks):
                        if not self._is_running:
                            break
                        chunk_num = i + 1
                        chunk_filename = chunk_pattern.format(chunk_num)
                        chunk_filepath = os.path.join(chunk_dir, chunk_filename)

                        if not os.path.exists(chunk_filepath):
                            raise FileNotFoundError(f"Missing chunk required for join: {chunk_filename}")

                        self.progress_updated.emit(
                            chunks_processed, num_chunks,
                            f"Reading chunk {chunk_num}/{num_chunks}: {chunk_filename}"
                        )

                        try:
                            with open(chunk_filepath, 'rb') as infile:
                                while self._is_running:
                                    data = infile.read(CHUNK_RW_SIZE)
                                    if not data:
                                        break  # End of current chunk
                                    outfile.write(data)
                                    bytes_written_total += len(data)
                        except IOError as read_error:
                            raise IOError(f"Error reading chunk {chunk_filename}: {read_error}") from read_error
                        except Exception as e: # Catch unexpected read errors
                            raise IOError(f"Unexpected error processing chunk {chunk_filename}: {e}") from e

                        if not self._is_running:
                            break

                        chunks_processed += 1
                        # Emit progress *after* chunk is successfully processed
                        self.progress_updated.emit(chunks_processed, num_chunks, f"Finished processing chunk {chunk_num}/{num_chunks}")

            except OSError as write_error:
                # Clean up the partially written output file on write error
                if os.path.exists(output_filepath):
                    try: os.remove(output_filepath)
                    except OSError: pass # Ignore cleanup error
                raise OSError(f"Error writing to output file '{output_filepath}': {write_error}") from write_error

            # --- Finalization ---
            if not self._is_running:
                # Clean up partially written output file if cancelled
                if os.path.exists(output_filepath):
                    try:
                        os.remove(output_filepath)
                    except OSError:
                        pass # Ignore cleanup error
                self.error_occurred.emit("Join operation cancelled.")
            else:
                # Final Verification (optional, but recommended)
                try:
                    final_size = os.path.getsize(output_filepath)
                except OSError:
                    final_size = -1 # Indicate size check failed

                verification_msg = ""
                if expected_total_size is not None and final_size >= 0:
                    if final_size == expected_total_size:
                        verification_msg = f" Final size ({final_size} bytes) matches expected size."
                    else:
                        verification_msg = f" WARNING: Final size ({final_size} bytes) does NOT match expected size ({expected_total_size} bytes)!"
                elif final_size < 0:
                    verification_msg = " Could not verify final file size."

                self.operation_complete.emit(f"Successfully joined {chunks_processed} chunks into {output_filepath}.{verification_msg}")

        # --- Error Handling ---
        except (FileNotFoundError, ValueError, IOError) as e:
            self.error_occurred.emit(f"Error: {e}")
        except PermissionError as e:
            self.error_occurred.emit(f"Permission Error: {e}. Check file/directory permissions.")
        except OSError as e:
             # Catch disk space issues during join or dir creation
            self.error_occurred.emit(f"Disk Error: {e}. Check available disk space or permissions.")
        except Exception as e:
            # Catch-all for unexpected errors
            self.error_occurred.emit(f"An unexpected error occurred during join: {e}")
        finally:
            # Ensure state is reset and thread signal is emitted regardless of outcome
            self._is_running = False
            self.finished.emit()


class FileSplitJoinGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Get the absolute path of the directory containing the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the absolute path to the UI file
        ui_file = os.path.join(script_dir, "file_splitter_joiner.ui")
        
        # Check if UI file exists
        if not os.path.exists(ui_file):
            raise FileNotFoundError(f"UI file not found: {ui_file}")
            
        # Load the UI file
        uic.loadUi(ui_file, self)
        
        # Initialize backend logic
        self.logic = FileOperationLogic()
        
        # Connect signals from backend
        self.logic.progress_updated.connect(self.update_progress)
        self.logic.operation_complete.connect(self.operation_completed)
        self.logic.error_occurred.connect(self.show_error)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.splitInputPath.setAcceptDrops(True)
        self.splitOutputPath.setAcceptDrops(True)
        self.joinInputPath.setAcceptDrops(True)
        self.joinOutputPath.setAcceptDrops(True)
        
        # Connect UI elements
        self.setup_connections()
        
        # Setup initial state
        self.splitBySize.toggled.connect(self.update_split_controls)
        self.splitByParts.toggled.connect(self.update_split_controls)
        
        # Show the window
        self.show()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            return
            
        path = urls[0].toLocalFile()
        focused_widget = QApplication.focusWidget()
        
        if focused_widget == self.splitInputPath:
            if os.path.isfile(path):
                self.splitInputPath.setText(path)
            else:
                self.show_error("Please drop a file for splitting")
        elif focused_widget == self.splitOutputPath:
            if os.path.isdir(path):
                self.splitOutputPath.setText(path)
            else:
                self.show_error("Please drop a folder for output")
        elif focused_widget == self.joinInputPath:
            if os.path.isfile(path) and path.endswith('.part001'):
                self.joinInputPath.setText(path)
                # Try to suggest output filename by removing .part001
                suggested_output = path[:-8]
                self.joinOutputPath.setText(suggested_output)
            else:
                self.show_error("Please drop a .part001 file for joining")
        elif focused_widget == self.joinOutputPath:
            if os.path.isdir(os.path.dirname(path)):
                self.joinOutputPath.setText(path)
    
    def setup_connections(self):
        """Setup signal/slot connections for UI elements."""
        # Split tab connections
        self.splitBrowseInput.clicked.connect(self.browse_split_input)
        self.splitBrowseOutput.clicked.connect(self.browse_split_output)
        self.splitButton.clicked.connect(self.start_split)
        
        # Join tab connections
        self.joinBrowseInput.clicked.connect(self.browse_join_input)
        self.joinBrowseOutput.clicked.connect(self.browse_join_output)
        self.joinButton.clicked.connect(self.start_join)

        # Menu connections
        self.actionExit.triggered.connect(self.close)
    
    def update_split_controls(self):
        """Enable/disable appropriate controls based on split mode."""
        self.sizeValue.setEnabled(self.splitBySize.isChecked())
        self.sizeUnit.setEnabled(self.splitBySize.isChecked())
        self.partsValue.setEnabled(self.splitByParts.isChecked())
    
    def browse_split_input(self):
        """Open file dialog to select input file for splitting."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Split", "",
            "All Files (*.*)"
        )
        if file_path:
            self.splitInputPath.setText(file_path)
    
    def browse_split_output(self):
        """Open directory dialog to select output location for split files."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if dir_path:
            self.splitOutputPath.setText(dir_path)
    
    def browse_join_input(self):
        """Open file dialog to select first chunk file for joining."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select First Chunk (.part001)", "",
            "Part Files (*.part001);;All Files (*.*)"
        )
        if file_path:
            self.joinInputPath.setText(file_path)
            # Try to suggest output filename by removing .part001
            if file_path.lower().endswith('.part001'):
                suggested_output = file_path[:-8]  # Remove .part001
                self.joinOutputPath.setText(suggested_output)
    
    def browse_join_output(self):
        """Open file dialog to select output file for joined result."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "",
            "All Files (*.*)"
        )
        if file_path:
            self.joinOutputPath.setText(file_path)
    
    def start_split(self):
        """Start the file split operation."""
        input_path = self.splitInputPath.text()
        output_dir = self.splitOutputPath.text()
        
        if not input_path or not output_dir:
            self.show_error("Please select both input file and output directory.")
            return
        
        if not os.path.exists(input_path):
            self.show_error("Input file does not exist.")
            return
        
        # Calculate split parameters
        if self.splitBySize.isChecked():
            split_mode = 'size'
            value = float(self.sizeValue.value())
            unit_multiplier = {
                0: 1,  # Bytes
                1: 1024,  # KB
                2: 1024 * 1024,  # MB
                3: 1024 * 1024 * 1024  # GB
            }[self.sizeUnit.currentIndex()]
        else:  # Split by parts
            split_mode = 'parts'
            value = self.partsValue.value()
            unit_multiplier = 1
        
        # Start the operation
        try:
            self.statusLabel.setText("Starting split operation...")
            self.progressBar.setValue(0)
            self.logic.split_file(input_path, output_dir, split_mode, value, unit_multiplier)
        except Exception as e:
            self.show_error(f"Failed to start split operation: {str(e)}")
    
    def start_join(self):
        """Start the file join operation."""
        input_path = self.joinInputPath.text()
        output_path = self.joinOutputPath.text()
        
        if not input_path or not output_path:
            self.show_error("Please select both input chunk and output file.")
            return
        
        if not input_path.lower().endswith('.part001'):
            self.show_error("Please select the first chunk file (ending with .part001)")
            return
        
        if not os.path.exists(input_path):
            self.show_error("Input chunk file does not exist.")
            return
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                self.show_error(f"Could not create output directory: {e}")
                return
        
        # Start the operation
        try:
            self.statusLabel.setText("Starting join operation...")
            self.progressBar.setValue(0)
            self.logic.join_files(input_path, output_path)
        except Exception as e:
            self.show_error(f"Failed to start join operation: {str(e)}")
    
    def update_progress(self, value, total, message):
        """Update progress bar and status message."""
        if total > 0:
            percentage = int((value / total) * 100)
            self.progressBar.setValue(percentage)
        self.statusLabel.setText(message)
    
    def operation_completed(self, message):
        """Handle successful operation completion."""
        self.progressBar.setValue(100)
        self.statusLabel.setText(message)
        QMessageBox.information(self, "Operation Complete", message)
    
    def show_error(self, message):
        """Display error message to user."""
        self.statusLabel.setText(f"Error: {message}")
        QMessageBox.critical(self, "Error", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileSplitJoinGUI()
    sys.exit(app.exec_())
