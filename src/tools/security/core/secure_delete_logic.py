"""
Secure Delete Core Logic Module

This module provides the core secure file deletion functionality with enhanced
hub integration, resource management, and comprehensive logging capabilities.

Migrated from: secure_delete.py
Target: file_utilities_2 package integration
"""

import os
import random
import string
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Import hub integration components
from ..integration.hub_connector import HubConnector, HubCommunicationProtocol

# Constants
CHUNK_SIZE = 1024 * 1024  # 1MB buffer for overwriting
DEFAULT_PASSES = 3
MAX_PASSES = 35


class SecureDeleteLogic(QObject):
    """
    Enhanced secure file deletion logic with hub integration.

    This class handles the core secure deletion operations with support for:
    - Multiple overwrite passes with random data
    - Progress reporting to hub
    - Resource management coordination
    - Comprehensive error handling and logging
    - Thread-safe operations
    """

    # Enhanced signal definitions for hub integration
    progress_updated = pyqtSignal(int, int, str)  # value, total, message
    file_progress = pyqtSignal(int, int)  # bytes_processed, total_bytes
    operation_complete = pyqtSignal(str)  # success message
    error_occurred = pyqtSignal(str)  # error message
    finished = pyqtSignal()  # signals thread completion

    # Hub integration signals
    hub_progress_update = pyqtSignal(int, str)  # percentage, message
    hub_status_change = pyqtSignal(str, dict)  # status, details
    hub_error_report = pyqtSignal(str, dict)  # error_message, details

    def __init__(self, hub_instance=None):
        """
        Initialize the secure delete logic with hub integration.

        Args:
            hub_instance: Reference to the hub for integration
        """
        super().__init__()
        self._is_running = False
        self._filepath: Optional[str] = None
        self._current_pass = 0
        self._total_passes = DEFAULT_PASSES
        self._bytes_processed = 0
        self._total_bytes = 0

        # Hub integration setup
        self.hub_connector = HubConnector("SecureDelete", hub_instance)
        self._setup_hub_integration()

        # Logging setup
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

        # Resource management
        self._resource_allocated = False
        self._operation_start_time = None

        # Statistics tracking
        self.stats = {
            "files_processed": 0,
            "total_bytes_processed": 0,
            "total_time": 0,
            "errors_count": 0,
            "last_operation": None,
        }

    def _setup_hub_integration(self):
        """Setup hub integration and connect signals."""
        try:
            # Register with hub
            self.hub_connector.register_with_hub()

            # Connect internal signals to hub reporting
            self.progress_updated.connect(self._report_progress_to_hub)
            self.error_occurred.connect(self._report_error_to_hub)
            self.operation_complete.connect(self._report_completion_to_hub)

            self.logger.info("Hub integration setup completed")

        except Exception as e:
            self.logger.error(f"Failed to setup hub integration: {e}")

    def _setup_logging(self):
        """Setup comprehensive logging for secure delete operations."""
        try:
            # Configure logger for secure delete operations
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)

            if not self.logger.handlers:
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)

        except Exception as e:
            print(f"Failed to setup logging: {e}")

    def _report_progress_to_hub(self, value: int, total: int, message: str):
        """Report progress updates to hub."""
        try:
            if total > 0:
                percentage = int((value / total) * 100)
                self.hub_connector.report_progress_to_hub(percentage, message)
                self.hub_progress_update.emit(percentage, message)

        except Exception as e:
            self.logger.error(f"Failed to report progress to hub: {e}")

    def _report_error_to_hub(self, error_message: str):
        """Report errors to hub."""
        try:
            error_details = {
                "filepath": self._filepath,
                "current_pass": self._current_pass,
                "total_passes": self._total_passes,
                "bytes_processed": self._bytes_processed,
                "timestamp": datetime.now().isoformat(),
            }

            self.hub_connector.report_error_to_hub(
                error_message, error_details
            )
            self.hub_error_report.emit(error_message, error_details)

            # Update statistics
            self.stats["errors_count"] += 1

        except Exception as e:
            self.logger.error(f"Failed to report error to hub: {e}")

    def _report_completion_to_hub(self, success_message: str):
        """Report successful completion to hub."""
        try:
            completion_details = {
                "filepath": self._filepath,
                "passes_completed": self._total_passes,
                "bytes_processed": self._total_bytes,
                "operation_time": self._get_operation_duration(),
                "timestamp": datetime.now().isoformat(),
            }

            self.hub_connector.report_status_to_hub(
                "completed", completion_details
            )

            # Update statistics
            self.stats["files_processed"] += 1
            self.stats["total_bytes_processed"] += self._total_bytes
            self.stats["total_time"] += self._get_operation_duration()
            self.stats["last_operation"] = datetime.now().isoformat()

        except Exception as e:
            self.logger.error(f"Failed to report completion to hub: {e}")

    def _get_operation_duration(self) -> float:
        """Get the duration of the current operation in seconds."""
        if self._operation_start_time:
            return (
                datetime.now() - self._operation_start_time
            ).total_seconds()
        return 0.0

    def _request_resources(self) -> bool:
        """Request necessary resources from hub."""
        try:
            # Request disk resource for secure deletion
            disk_granted = self.hub_connector.request_hub_resources(
                "disk", {"operation": "secure_delete", "priority": "high"}
            )

            if disk_granted:
                self._resource_allocated = True
                self.logger.info(
                    "Disk resources allocated for secure deletion"
                )
                return True
            else:
                self.logger.warning("Failed to allocate disk resources")
                return False

        except Exception as e:
            self.logger.error(f"Failed to request resources: {e}")
            return False

    def _release_resources(self):
        """Release allocated resources."""
        try:
            if self._resource_allocated:
                # Resources are automatically released by hub connector
                self._resource_allocated = False
                self.logger.info("Resources released")

        except Exception as e:
            self.logger.error(f"Failed to release resources: {e}")

    def stop(self) -> None:
        """Stop the deletion process gracefully."""
        self.logger.info("Stopping secure deletion process")
        self.progress_updated.emit(0, 1, "Stopping deletion...")
        self._is_running = False

        # Report status to hub
        try:
            self.hub_connector.report_status_to_hub(
                "stopped",
                {
                    "reason": "user_requested",
                    "progress": f"{self._current_pass}/{self._total_passes}",
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            self.logger.error(f"Failed to report stop status: {e}")

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

    def shred_file(self, filepath: str, passes: int = DEFAULT_PASSES) -> None:
        """
        Securely delete a file by overwriting it multiple times.

        Args:
            filepath: Path to the file to be securely deleted
            passes: Number of overwrite passes (1-35)
        """
        self._operation_start_time = datetime.now()
        self._is_running = True
        self._filepath = filepath
        self._total_passes = max(1, min(passes, MAX_PASSES))
        self._current_pass = 0
        self._bytes_processed = 0

        self.logger.info(
            f"Starting secure deletion of {filepath} with {passes} passes"
        )

        try:
            # Request resources from hub
            if not self._request_resources():
                self.error_occurred.emit(
                    "Failed to allocate required resources"
                )
                return

            # Report operation start to hub
            self.hub_connector.report_status_to_hub(
                "started",
                {
                    "filepath": filepath,
                    "passes": passes,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Validate file exists
            if not os.path.isfile(filepath):
                error_msg = f"File not found: {filepath}"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # Get file size for progress tracking
            self._total_bytes = os.path.getsize(filepath)
            self.logger.info(f"File size: {self._total_bytes:,} bytes")

            # Perform overwrite passes
            for pass_num in range(self._total_passes):
                if not self._is_running:
                    self.logger.info("Operation stopped by user")
                    break

                self._current_pass = pass_num + 1
                pass_message = (
                    f"Pass {self._current_pass}/{self._total_passes}"
                )

                self.progress_updated.emit(
                    self._current_pass, self._total_passes, pass_message
                )

                self.logger.info(f"Starting {pass_message}")

                # Overwrite with random data
                success = self._overwrite_file_pass(filepath)
                if not success:
                    error_msg = f"Failed during {pass_message}"
                    self.logger.error(error_msg)
                    self.error_occurred.emit(error_msg)
                    return

            # Perform file renaming and final deletion
            if self._is_running:
                self._perform_final_deletion(filepath)

        except Exception as e:
            error_msg = f"Secure deletion failed: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self._release_resources()
            self.finished.emit()

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

                    # Report file-level progress
                    self.file_progress.emit(bytes_written, self._total_bytes)

                    # Ensure data is written to disk
                    f.flush()
                    os.fsync(f.fileno())

                return bytes_written == self._total_bytes

        except Exception as e:
            self.logger.error(f"Failed to overwrite file: {e}")
            return False

    def _perform_final_deletion(self, filepath: str):
        """
        Perform final file renaming and deletion.

        Args:
            filepath: Original file path
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
                    f"File securely deleted: {os.path.basename(filepath)}"
                )
                self.logger.info(success_msg)
                self.operation_complete.emit(success_msg)

        except Exception as e:
            error_msg = f"Failed during final deletion: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)

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

    def cleanup(self):
        """Cleanup resources and hub connections."""
        try:
            self._release_resources()
            self.hub_connector.cleanup()
            self.logger.info("SecureDeleteLogic cleanup completed")
        except Exception as e:
            self.logger.error(f"Failed to cleanup: {e}")
