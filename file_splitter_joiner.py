import os
import math
import json
from typing import Dict, Any, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal

# Constants
CHUNK_RW_SIZE = 1024 * 1024  # 1MB read/write buffer
METADATA_FILENAME = "_metadata.json"
PART_EXTENSION = ".part001"  # Extension for first chunk file


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

    def __init__(self) -> None:
        """Initializes the FileOperationLogic."""
        super().__init__()
        self._is_running = False

    def stop(self) -> None:
        """Stops the current operation."""
        self.progress_updated.emit(0, 1, "Stopping operation...")
        self._is_running = False

    def _calculate_split_params(
        self, file_size: int, split_mode: str, value: float,
        unit_multiplier: int = 1
    ) -> Tuple[int, int]:
        """
        Calculates chunk size and number of chunks based on user input.

        Args:
            file_size: The total size of the file to be split.
            split_mode: Either 'size' or 'parts'.
            value: The size value or the number of parts.
            unit_multiplier: Multiplier for size units (e.g., 1024 for KB).

        Returns:
            A tuple containing (chunk_size, num_chunks).

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
            chunk_size = math.ceil(file_size / num_chunks)
        else:
            raise ValueError(f"Invalid split mode: {split_mode}")

        if num_chunks > 9999:  # Limit padding practicality
            raise ValueError("Too many chunks requested (max 9999).")

        return chunk_size, num_chunks

    def split_file(
        self, input_filepath: str, output_dir: str, split_mode: str,
        value: float, unit_multiplier: int = 1
    ) -> None:
        """
        Splits the input file into smaller chunks based on specified mode.

        Args:
            input_filepath: Path to the file to be split.
            output_dir: Directory where chunks will be saved.
            split_mode: Either 'size' or 'parts'.
            value: The size value or the number of parts.
            unit_multiplier: Multiplier for size units.
        """
        self._is_running = True
        try:
            # Input validation
            if not os.path.exists(input_filepath):
                raise FileNotFoundError(f"Input file not found: {input_filepath}")
            
            # Ensure output directory exists or can be created
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            file_size = os.path.getsize(input_filepath)
            base_filename = os.path.basename(input_filepath)

            # --- Handle Empty File ---
            if file_size == 0:
                self.operation_complete.emit(
                    "Input file is empty. No chunks created."
                )
                self._is_running = False
                self.finished.emit()
                return

            # --- Calculate Parameters ---
            chunk_size, num_chunks = self._calculate_split_params(
                file_size, split_mode, value, unit_multiplier
            )

            if num_chunks == 0:  # Should only happen for zero size file
                self.operation_complete.emit(
                    "No chunks needed (likely zero-byte file)."
                )
                self._is_running = False
                self.finished.emit()
                return

            # Determine padding length (e.g., 3 for up to 999 chunks)
            padding = max(3, len(str(num_chunks)))
            chunk_pattern = f"{base_filename}.part{{:0{padding}d}}"

            progress_msg = (
                f"Starting split: {num_chunks} chunks, "
                f"approx size {chunk_size} bytes..."
            )
            self.progress_updated.emit(0, num_chunks, progress_msg)

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
                    
                    progress_msg = (
                        f"Writing chunk {chunk_num}/{num_chunks}: "
                        f"{chunk_filename}"
                    )
                    self.progress_updated.emit(
                        chunks_created, num_chunks, progress_msg
                    )

                    bytes_written_this_chunk = 0
                    try:
                        with open(chunk_filepath, 'wb') as outfile:
                            # Read and write in smaller blocks
                            while bytes_written_this_chunk < chunk_size:
                                if not self._is_running:
                                    break
                                
                                # Calculate remaining for this chunk
                                this_chunk = (
                                    chunk_size - bytes_written_this_chunk
                                )
                                total = (
                                    file_size - bytes_written_total
                                )
                                
                                # Determine read size
                                read_size = min(
                                    CHUNK_RW_SIZE,
                                    this_chunk,
                                    total
                                )

                                if read_size <= 0:
                                    break  # No more data or chunk is full

                                data = infile.read(read_size)
                                if not data:
                                    break  # End of input file

                                outfile.write(data)
                                bytes_written_this_chunk += len(data)
                                bytes_written_total += len(data)

                    except OSError as write_error:
                        # Clean up partial chunk on error
                        if os.path.exists(chunk_filepath):
                            try:
                                os.remove(chunk_filepath)
                            except OSError:
                                pass  # Ignore cleanup errors
                        
                        error_msg = f"Error writing chunk {chunk_filename}"
                        raise OSError(
                            f"{error_msg}: {write_error}"
                        ) from write_error

                    if not self._is_running:
                        # Clean up chunk if cancelled
                        if os.path.exists(chunk_filepath):
                            try:
                                os.remove(chunk_filepath)
                            except OSError:
                                pass  # Ignore cleanup error
                        break

                    chunks_created += 1
                    # Emit progress after chunk write
                    msg = f"Finished chunk {chunk_num}/{num_chunks}"
                    self.progress_updated.emit(
                        chunks_created, num_chunks, msg
                    )

            # --- Finalization ---
            if not self._is_running:
                self.error_occurred.emit("Split operation cancelled.")
            else:
                # Create metadata file
                metadata: Dict[str, Any] = {
                    'original_filename': base_filename,
                    'total_size': file_size,
                    'num_chunks': num_chunks,
                    'chunk_size': chunk_size,
                    'chunk_pattern': chunk_pattern,
                    'padding': padding
                }
                meta_filepath = os.path.join(output_dir, METADATA_FILENAME)
                try:
                    with open(meta_filepath, 'w') as metafile:
                        json.dump(metadata, metafile, indent=4)
                except Exception as e:
                    # Warning only, split succeeded
                    warn_msg = f"Warning: Could not write metadata file: {e}"
                    self.error_occurred.emit(warn_msg)

                complete_msg = (
                    f"File successfully split into {chunks_created} "
                    f"chunks in {output_dir}."
                )
                self.operation_complete.emit(complete_msg)

        # --- Error Handling ---
        except Exception as e:
            # Catch-all for unexpected errors
            msg = f"An unexpected error occurred during split: {e}"
            self.error_occurred.emit(msg)
        finally:
            # Reset state and emit completion signal
            self._is_running = False
            self.finished.emit()

    def join_files(
        self,
        first_chunk_path: str,
        output_filepath: str
    ) -> None:
        """
        Joins file chunks back into a single file.

        Args:
            first_chunk_path: Path to first chunk (e.g., file.part001)
            output_filepath: Path where joined file will be saved
        """
        self._is_running = True
        try:
            # Input validation
            if not os.path.exists(first_chunk_path):
                raise FileNotFoundError(f"Input file not found: {first_chunk_path}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_filepath)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            chunk_dir = os.path.dirname(first_chunk_path)
            chunk_basename = os.path.basename(first_chunk_path)

            # Load or infer parameters
            metadata: Optional[Dict[str, Any]] = None
            num_chunks = 0
            chunk_pattern = ""
            padding = 0
            expected_total_size: Optional[int] = None
            original_filename: Optional[str] = None

            meta_filepath = os.path.join(chunk_dir, METADATA_FILENAME)
            if os.path.exists(meta_filepath):
                try:
                    with open(meta_filepath, 'r') as f:
                        metadata = json.load(f)
                    if metadata is not None:
                        num_chunks = metadata['num_chunks']
                        chunk_pattern = metadata['chunk_pattern']
                        padding = metadata['padding']
                        expected_total_size = metadata.get('total_size')
                        original_filename = metadata.get('original_filename')
                        self.progress_updated.emit(
                            0, 1, f"Loaded metadata for '{original_filename or 'file'}'"
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    self.progress_updated.emit(
                        0, 1, f"Warning: Metadata file invalid ({e}), "
                        "attempting manual join."
                    )
                    metadata = None
            else:
                self.progress_updated.emit(
                    0, 1, "Metadata file not found, attempting manual join."
                )

            # --- Infer Parameters if Metadata Failed/Missing ---
            if not metadata:
                # Infer from first chunk name (e.g., file.part001)
                parts = chunk_basename.rsplit('.part', 1)
                if len(parts) != 2 or not parts[1].isdigit():
                    raise ValueError(
                        "Cannot infer chunk sequence from filename. "
                        "Expected format like 'filename.partXXX'."
                    )

                base_filename_inferred = parts[0]
                padding = len(parts[1])
                # Ensure first part number matches inference logic (should be 1)
                try:
                    if int(parts[1]) != 1:
                        raise ValueError(
                            f"Expected first chunk number to be 1, "
                            f"found {int(parts[1])} in '{chunk_basename}'."
                        )
                except ValueError:
                    raise ValueError("Chunk number suffix is not a valid integer.")

                chunk_pattern = f"{base_filename_inferred}.part{{:0{padding}d}}"

                # Count chunks manually
                num_chunks = 0
                for i in range(1, 10000):  # Check up to 9999 chunks
                    check_path = os.path.join(chunk_dir, chunk_pattern.format(i))
                    if os.path.exists(check_path):
                        num_chunks += 1
                    else:
                        break

                if num_chunks == 0:
                    raise ValueError(
                        "Could not find any valid sequential chunks to join "
                        "starting from the provided file."
                    )

                expected_total_size = None
                original_filename = base_filename_inferred
                self.progress_updated.emit(
                    0, num_chunks, f"Found {num_chunks} potential chunks based on pattern."
                )

            # --- Prepare Output ---
            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except OSError as e:
                    raise OSError(
                        f"Could not create output directory '{output_dir}': {e}"
                    ) from e

            # --- Perform Joining ---
            self.progress_updated.emit(
                0, num_chunks, f"Starting join operation for {num_chunks} chunks..."
            )
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
                            raise FileNotFoundError(
                                f"Missing chunk required for join: {chunk_filename}"
                            )

                        self.progress_updated.emit(
                            chunks_processed, num_chunks,
                            f"Reading chunk {chunk_num}/{num_chunks}: {chunk_filename}"
                        )

                        try:
                            with open(chunk_filepath, 'rb') as infile:
                                while self._is_running:
                                    data = infile.read(CHUNK_RW_SIZE)
                                    if not data:
                                        break
                                    outfile.write(data)
                        except IOError as read_error:
                            raise IOError(
                                f"Error reading chunk {chunk_filename}: {read_error}"
                            ) from read_error
                        except Exception as e:
                            raise IOError(
                                f"Unexpected error processing chunk {chunk_filename}: {e}"
                            ) from e

                        if not self._is_running:
                            break

                        chunks_processed += 1
                        self.progress_updated.emit(
                            chunks_processed, num_chunks,
                            f"Finished processing chunk {chunk_num}/{num_chunks}"
                        )

            except OSError as write_error:
                # Clean up the partially written output file on write error
                if os.path.exists(output_filepath):
                    try:
                        os.remove(output_filepath)
                    except OSError:
                        pass
                raise OSError(
                    f"Error writing to output file '{output_filepath}': {write_error}"
                ) from write_error

            # --- Finalization ---
            if not self._is_running:
                # Clean up partially written output file if cancelled
                if os.path.exists(output_filepath):
                    try:
                        os.remove(output_filepath)
                    except OSError:
                        pass
                self.error_occurred.emit("Join operation cancelled.")
            else:
                # Final Verification
                try:
                    final_size = os.path.getsize(output_filepath)
                except OSError:
                    final_size = -1

                verification_msg = ""
                if expected_total_size is not None and final_size >= 0:
                    if final_size == expected_total_size:
                        verification_msg = (
                            f" Final size ({final_size} bytes) matches expected size."
                        )
                    else:
                        verification_msg = (
                            f" WARNING: Final size ({final_size} bytes) does NOT "
                            f"match expected size ({expected_total_size} bytes)!"
