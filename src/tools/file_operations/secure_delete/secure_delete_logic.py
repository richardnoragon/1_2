"""
Secure Delete Core Logic Module

This module provides secure file deletion functionality with comprehensive
logging capabilities and progress tracking.

Modernized from: archive/legacy_code/file_utilities_2/core/secure_delete_logic.py
"""

import logging
import os
import random
import string
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Constants
CHUNK_SIZE = 1024 * 1024  # 1MB buffer for overwriting
DEFAULT_PASSES = 3
MAX_PASSES = 35


class SecureDeleteLogic:
    """
    Secure file deletion logic with comprehensive security features.

    This class handles secure deletion operations with support for:
    - Multiple overwrite passes with random data
    - Progress reporting capabilities
    - Comprehensive error handling and logging
    - Thread-safe operations
    """

    def __init__(self):
        """Initialize the secure delete logic."""
        self._is_running = False
        self._filepath: Optional[str] = None
        self._current_pass = 0
        self._total_passes = DEFAULT_PASSES
        self._bytes_processed = 0
        self._total_bytes = 0

        # Logging setup
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

        # Operation tracking
        self._operation_start_time = None

        # Statistics tracking
        self.stats = {
            "files_processed": 0,
            "total_bytes_processed": 0,
            "total_time": 0,
            "errors_count": 0,
            "last_operation": None,
        }

    def _setup_logging(self):
        """Setup comprehensive logging for secure delete operations."""
        try:
            # Configure logger for secure delete operations
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)

        except Exception as e:
            print(f"Failed to setup logging: {e}")

    def _get_operation_duration(self) -> float:
        """Get the duration of the current operation in seconds."""
        if self._operation_start_time:
            return (
                datetime.now() - self._operation_start_time
            ).total_seconds()
        return 0.0

    def stop(self) -> None:
        """Stop the deletion process gracefully."""
        self.logger.info("Stopping secure deletion process")
        self._is_running = False

    def _generate_random_bytes(self, length: int) -> bytes:
        """
        Generate a block of cryptographically secure random bytes.

        Args:
            length: Number of bytes to generate

        Returns:
            Random bytes of specified length
        """
        try:
            return os.urandom(length)
        except Exception as e:
            self.logger.error(f"Failed to generate random bytes: {e}")
            # Fallback to less secure but functional random generation
            return bytes(random.getrandbits(8) for _ in range(length))

    def _generate_random_filename(self, length: int = 16) -> str:
        """
        Generate a random filename string.

        Args:
            length: Length of the filename to generate

        Returns:
            Random filename string
        """
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    def delete_file(
        self,
        filepath: str,
        passes: int = DEFAULT_PASSES,
        progress_callback: Optional[Callable[[int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """
        Securely delete a file by overwriting it multiple times.

        Args:
            filepath: Path to the file to be securely deleted
            passes: Number of overwrite passes (1-35)
            progress_callback: Optional callback for progress updates
            cancel_check: Optional callback to check for cancellation

        Returns:
            True if successful, False otherwise
        """
        self._operation_start_time = datetime.now()
        self._is_running = True
        self._filepath = filepath
        self._total_passes = max(1, min(passes, MAX_PASSES))
        self._current_pass = 0
        self._bytes_processed = 0

        self.logger.info(
            f"Starting secure deletion of {filepath} " f"with {passes} passes"
        )

        try:
            # Validate file exists
            if not os.path.isfile(filepath):
                error_msg = f"File not found: {filepath}"
                self.logger.error(error_msg)
                self.stats["errors_count"] += 1
                return False

            # Get file size for progress tracking
            self._total_bytes = os.path.getsize(filepath)
            self.logger.info(f"File size: {self._total_bytes:,} bytes")

            # Perform overwrite passes
            for pass_num in range(self._total_passes):
                if not self._is_running:
                    self.logger.info("Operation stopped by user")
                    return False

                if cancel_check and cancel_check():
                    self.logger.info("Operation cancelled by user")
                    self._is_running = False
                    return False

                self._current_pass = pass_num + 1

                if progress_callback:
                    progress = int(
                        (self._current_pass / self._total_passes) * 100
                    )
                    progress_callback(progress)

                self.logger.info(
                    f"Starting pass {self._current_pass}/"
                    f"{self._total_passes}"
                )

                # Overwrite with random data
                success = self._overwrite_file_pass(filepath)
                if not success:
                    error_msg = f"Failed during pass {self._current_pass}"
                    self.logger.error(error_msg)
                    self.stats["errors_count"] += 1
                    return False

            # Perform file renaming and final deletion
            if self._is_running:
                success = self._perform_final_deletion(filepath)

                if success and progress_callback:
                    progress_callback(100)

                # Update statistics
                if success:
                    self.stats["files_processed"] += 1
                    self.stats["total_bytes_processed"] += self._total_bytes
                    self.stats["total_time"] += self._get_operation_duration()
                    self.stats["last_operation"] = datetime.now().isoformat()

                return success

            return False

        except Exception as e:
            error_msg = f"Secure deletion failed: {str(e)}"
            self.logger.error(error_msg)
            self.stats["errors_count"] += 1
            return False
        finally:
            self._is_running = False

    def _overwrite_file_pass(self, filepath: str) -> bool:
        """
        Perform a single overwrite pass on the file.

        Args:
            filepath: Path to the file to overwrite

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "r+b") as f:
                f.seek(0)
                bytes_written = 0

                while bytes_written < self._total_bytes and self._is_running:
                    # Calculate chunk size for this iteration
                    remaining_bytes = self._total_bytes - bytes_written
                    chunk_size = min(CHUNK_SIZE, remaining_bytes)

                    # Generate and write random data
                    random_data = self._generate_random_bytes(chunk_size)
                    f.write(random_data)
                    bytes_written += chunk_size
                    self._bytes_processed = bytes_written

                    # Ensure data is written to disk
                    f.flush()
                    os.fsync(f.fileno())

                return bytes_written == self._total_bytes

        except Exception as e:
            self.logger.error(f"Failed to overwrite file: {e}")
            return False

    def _perform_final_deletion(self, filepath: str) -> bool:
        """
        Perform final file renaming and deletion.

        Args:
            filepath: Original file path

        Returns:
            True if successful, False otherwise
        """
        try:
            current_path = filepath

            # Rename file multiple times with random names
            for i in range(3):
                if not self._is_running:
                    break

                dir_name = os.path.dirname(current_path)
                new_name = self._generate_random_filename()
                new_path = os.path.join(dir_name, new_name)

                try:
                    os.rename(current_path, new_path)
                    current_path = new_path
                    self.logger.info(f"Renamed to: {new_name}")
                except OSError as e:
                    self.logger.warning(f"Failed to rename file: {e}")
                    break

            # Finally delete the file
            if self._is_running:
                os.remove(current_path)
                success_msg = (
                    f"File securely deleted: " f"{os.path.basename(filepath)}"
                )
                self.logger.info(success_msg)
                return True

            return False

        except Exception as e:
            error_msg = f"Failed during final deletion: {e}"
            self.logger.error(error_msg)
            return False

    def delete_files(
        self,
        filepaths: list,
        passes: int = DEFAULT_PASSES,
        progress_callback: Optional[Callable[[int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """
        Securely delete multiple files.

        Args:
            filepaths: List of file paths to delete
            passes: Number of overwrite passes for each file
            progress_callback: Optional callback for overall progress
            cancel_check: Optional callback to check for cancellation

        Returns:
            True if all files deleted successfully, False otherwise
        """
        if not filepaths:
            return True

        total_files = len(filepaths)
        successful_deletions = 0

        for i, filepath in enumerate(filepaths):
            if cancel_check and cancel_check():
                self.logger.info("Batch deletion cancelled by user")
                break

            success = self.delete_file(filepath, passes)
            if success:
                successful_deletions += 1

            if progress_callback:
                overall_progress = int(((i + 1) / total_files) * 100)
                progress_callback(overall_progress)

        self.logger.info(
            f"Batch deletion completed: "
            f"{successful_deletions}/{total_files} files deleted"
        )

        return successful_deletions == total_files

    def delete_directory(
        self,
        directory_path: str,
        passes: int = DEFAULT_PASSES,
        progress_callback: Optional[Callable[[int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """
        Securely delete a directory and all its contents.

        Args:
            directory_path: Path to the directory to delete
            passes: Number of overwrite passes for each file
            progress_callback: Optional callback for progress updates
            cancel_check: Optional callback to check for cancellation

        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.isdir(directory_path):
                error_msg = f"Directory not found: {directory_path}"
                self.logger.error(error_msg)
                return False

            # Collect all files in directory recursively
            all_files = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)

            # Delete all files securely
            success = self.delete_files(
                all_files, passes, progress_callback, cancel_check
            )

            if success and self._is_running:
                # Remove empty directories
                try:
                    import shutil

                    shutil.rmtree(directory_path)
                    self.logger.info(f"Directory deleted: {directory_path}")
                    return True
                except OSError as e:
                    self.logger.error(f"Failed to remove directory: {e}")
                    return False

            return False

        except Exception as e:
            error_msg = f"Directory deletion failed: {e}"
            self.logger.error(error_msg)
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get operation statistics.

        Returns:
            Dictionary containing operation statistics
        """
        return self.stats.copy()

    def reset_statistics(self):
        """Reset operation statistics."""
        self.stats = {
            "files_processed": 0,
            "total_bytes_processed": 0,
            "total_time": 0,
            "errors_count": 0,
            "last_operation": None,
        }
        self.logger.info("Statistics reset")
