"""
Core encryption/decryption logic with progress tracking and hub integration.

This module provides the core encryption and decryption functionality
separated from the GUI, with comprehensive progress tracking, error handling,
and hub integration capabilities.
"""

import os
import time
import datetime
from typing import Optional, Dict, Any

from PyQt5.QtCore import QObject, pyqtSignal
from cryptography.fernet import Fernet, InvalidToken


class EncryptionLogic(QObject):
    """
    Core encryption/decryption logic with progress tracking and hub integration.

    This class handles all cryptographic operations, progress tracking, and
    communication with the hub system for resource coordination.
    """

    # Progress tracking signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    file_progress = pyqtSignal(int, int)  # processed_bytes, total
    operation_complete = pyqtSignal(str)  # completion_message
    error_occurred = pyqtSignal(str)  # error_message
    milestone_reached = pyqtSignal(str, dict)  # milestone_name, details

    # Hub integration signals
    hub_progress_update = pyqtSignal(int, str)  # percentage, message
    hub_status_change = pyqtSignal(str, dict)  # status, details
    hub_error_report = pyqtSignal(str, dict)  # error_message, details

    # Operation control signals
    operation_started = pyqtSignal(str, dict)  # operation_type, params
    operation_cancelled = pyqtSignal(str)  # cancellation_reason

    # Constants
    ENCRYPTED_EXTENSION = ".encrypted"
    KEY_EXTENSION = ".key"
    CHUNK_SIZE = 8192  # 8KB chunks for progress tracking

    def __init__(
        self, hub_instance=None, config_instance=None, logger_instance=None
    ):
        """
        Initialize EncryptionLogic with optional dependencies.

        Args:
            hub_instance: Optional hub instance for integration
            config_instance: Optional configuration instance
            logger_instance: Optional logger instance
        """
        super().__init__()

        self.hub_instance = hub_instance
        self.config_instance = config_instance
        self.logger_instance = logger_instance

        # Operation state
        self._is_running = False
        self._should_stop = False
        self._current_operation = None
        self._operation_start_time = None

        # Statistics
        self._operations_completed = 0
        self._total_bytes_processed = 0
        self._error_count = 0
        self._uptime_start = time.time()

        # Progress tracking
        self._progress_callback = None
        self._last_progress_update = 0
        self._progress_update_interval = 0.1  # Update every 100ms

    def generate_key(self) -> bytes:
        """
        Generate a new Fernet encryption key.

        Returns:
            bytes: 32-byte Fernet key

        Raises:
            Exception: If key generation fails
        """
        try:
            key = Fernet.generate_key()

            if self.logger_instance:
                self.logger_instance.log_security_event(
                    "key_generation",
                    {"timestamp": datetime.datetime.now().isoformat()},
                )

            return key

        except Exception as e:
            error_msg = f"Failed to generate encryption key: {str(e)}"
            self.error_occurred.emit(error_msg)
            if self.hub_instance:
                self.hub_error_report.emit(
                    error_msg, {"operation": "key_generation"}
                )
            raise

    def validate_key(self, key: bytes) -> bool:
        """
        Validate Fernet key format and structure.

        Args:
            key: Key bytes to validate

        Returns:
            bool: True if key is valid, False otherwise
        """
        try:
            if not isinstance(key, bytes):
                return False

            if len(key) != 44:  # Fernet keys are 44 bytes when base64 encoded
                return False

            # Try to create a Fernet instance to validate the key
            Fernet(key)
            return True

        except Exception:
            return False

    def save_key(self, key: bytes, file_path: str) -> bool:
        """
        Save encryption key to file with proper permissions.

        Args:
            key: Key bytes to save
            file_path: Target file path

        Returns:
            bool: True if save successful, False otherwise

        Raises:
            PermissionError: If file cannot be written
            OSError: If file system error occurs
        """
        try:
            if not self.validate_key(key):
                raise ValueError("Invalid key format")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as key_file:
                key_file.write(key)

            # Set restrictive permissions (owner read/write only)
            try:
                os.chmod(file_path, 0o600)
            except OSError:
                pass  # Ignore permission errors on Windows

            if self.logger_instance:
                self.logger_instance.log_security_event(
                    "key_saved",
                    {
                        "file_path": file_path,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                )

            return True

        except Exception as e:
            error_msg = f"Failed to save key: {str(e)}"
            self.error_occurred.emit(error_msg)
            if self.hub_instance:
                self.hub_error_report.emit(
                    error_msg,
                    {"operation": "key_save", "file_path": file_path},
                )
            raise

    def load_key(self, file_path: str) -> bytes:
        """
        Load encryption key from file with validation.

        Args:
            file_path: Path to key file

        Returns:
            bytes: Loaded key bytes

        Raises:
            FileNotFoundError: If key file doesn't exist
            ValueError: If key format is invalid
            PermissionError: If file cannot be read
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Key file not found: {file_path}")

            with open(file_path, "rb") as key_file:
                key = key_file.read()

            if not self.validate_key(key):
                raise ValueError("Invalid key format in file")

            if self.logger_instance:
                self.logger_instance.log_security_event(
                    "key_loaded",
                    {
                        "file_path": file_path,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                )

            return key

        except Exception as e:
            error_msg = f"Failed to load key: {str(e)}"
            self.error_occurred.emit(error_msg)
            if self.hub_instance:
                self.hub_error_report.emit(
                    error_msg,
                    {"operation": "key_load", "file_path": file_path},
                )
            raise

    def encrypt_file(
        self, file_path: str, key: bytes, output_path: str = None
    ) -> bool:
        """
        Encrypt a single file with progress tracking.

        Args:
            file_path: Path to file to encrypt
            key: Encryption key
            output_path: Optional output path (defaults to file_path +
                        '.encrypted')

        Returns:
            bool: True if encryption successful, False otherwise

        Raises:
            FileNotFoundError: If input file doesn't exist
            PermissionError: If file access denied
            Exception: If encryption fails
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if not self.validate_key(key):
                raise ValueError("Invalid encryption key")

            if output_path is None:
                output_path = file_path + self.ENCRYPTED_EXTENSION

            # Check if already encrypted
            if file_path.endswith(self.ENCRYPTED_EXTENSION):
                self.error_occurred.emit("File is already encrypted")
                return False

            file_size = os.path.getsize(file_path)
            fernet = Fernet(key)

            # Start operation
            self._start_operation(
                "encrypt_file",
                {
                    "file_path": file_path,
                    "output_path": output_path,
                    "file_size": file_size,
                },
            )

            # Emit milestone
            self.milestone_reached.emit(
                "encryption_started",
                {"file_path": file_path, "file_size": file_size},
            )

            processed_bytes = 0

            with open(file_path, "rb") as infile:
                with open(output_path, "wb") as outfile:
                    while True:
                        if self._should_stop:
                            self.operation_cancelled.emit(
                                "User requested cancellation"
                            )
                            return False

                        chunk = infile.read(self.CHUNK_SIZE)
                        if not chunk:
                            break

                        # For small files, encrypt all at once
                        # For large files, we'd need to implement streaming
                        if processed_bytes == 0:  # First chunk, read all
                            infile.seek(0)
                            data = infile.read()
                            encrypted_data = fernet.encrypt(data)
                            outfile.write(encrypted_data)
                            processed_bytes = file_size
                            break

                        processed_bytes += len(chunk)

                        # Update progress
                        filename = os.path.basename(file_path)
                        self._update_progress(
                            processed_bytes,
                            file_size,
                            f"Encrypting {filename}",
                        )

            # Complete operation
            self._complete_operation(
                "encrypt_file",
                {
                    "file_path": file_path,
                    "output_path": output_path,
                    "bytes_processed": processed_bytes,
                },
            )

            self.milestone_reached.emit(
                "encryption_completed",
                {
                    "file_path": file_path,
                    "output_path": output_path,
                    "bytes_processed": processed_bytes,
                },
            )

            return True

        except Exception as e:
            error_msg = f"Encryption failed for {file_path}: {str(e)}"
            self.error_occurred.emit(error_msg)
            if self.hub_instance:
                self.hub_error_report.emit(
                    error_msg,
                    {"operation": "encrypt_file", "file_path": file_path},
                )
            self._error_count += 1
            return False

    def decrypt_file(
        self, file_path: str, key: bytes, output_path: str = None
    ) -> bool:
        """
        Decrypt a single file with progress tracking.

        Args:
            file_path: Path to encrypted file
            key: Decryption key
            output_path: Optional output path (defaults to removing .encrypted)

        Returns:
            bool: True if decryption successful, False otherwise

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file is not encrypted or corrupted
            InvalidToken: If key is incorrect
            PermissionError: If file access denied
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if not self.validate_key(key):
                raise ValueError("Invalid decryption key")

            if not file_path.endswith(self.ENCRYPTED_EXTENSION):
                self.error_occurred.emit("File is not encrypted")
                return False

            if output_path is None:
                output_path = file_path.replace(self.ENCRYPTED_EXTENSION, "")

            file_size = os.path.getsize(file_path)
            fernet = Fernet(key)

            # Start operation
            self._start_operation(
                "decrypt_file",
                {
                    "file_path": file_path,
                    "output_path": output_path,
                    "file_size": file_size,
                },
            )

            # Emit milestone
            self.milestone_reached.emit(
                "decryption_started",
                {"file_path": file_path, "file_size": file_size},
            )

            with open(file_path, "rb") as infile:
                with open(output_path, "wb") as outfile:
                    encrypted_data = infile.read()

                    if self._should_stop:
                        self.operation_cancelled.emit(
                            "User requested cancellation"
                        )
                        return False

                    # Update progress
                    self._update_progress(
                        file_size // 2,
                        file_size,
                        f"Decrypting {os.path.basename(file_path)}",
                    )

                    try:
                        decrypted_data = fernet.decrypt(encrypted_data)
                        outfile.write(decrypted_data)
                    except InvalidToken:
                        raise ValueError("Invalid key or corrupted file")

                    # Update progress
                    self._update_progress(
                        file_size, file_size, f"Decryption complete"
                    )

            # Complete operation
            self._complete_operation(
                "decrypt_file",
                {
                    "file_path": file_path,
                    "output_path": output_path,
                    "bytes_processed": file_size,
                },
            )

            self.milestone_reached.emit(
                "decryption_completed",
                {
                    "file_path": file_path,
                    "output_path": output_path,
                    "bytes_processed": file_size,
                },
            )

            return True

        except Exception as e:
            error_msg = f"Decryption failed for {file_path}: {str(e)}"
            self.error_occurred.emit(error_msg)
            if self.hub_instance:
                self.hub_error_report.emit(
                    error_msg,
                    {"operation": "decrypt_file", "file_path": file_path},
                )
            self._error_count += 1
            return False

    def encrypt_directory(
        self, directory_path: str, key: bytes, recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Encrypt all files in a directory with detailed results.

        Args:
            directory_path: Path to directory
            key: Encryption key
            recursive: Whether to process subdirectories

        Returns:
            Dict containing operation results
        """
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "duration": 0,
            "total_bytes": 0,
        }

        try:
            start_time = time.time()

            # Collect files to process
            files_to_process = []
            for root, dirs, files in os.walk(directory_path):
                if not recursive and root != directory_path:
                    continue

                for filename in files:
                    if not filename.endswith(self.ENCRYPTED_EXTENSION):
                        file_path = os.path.join(root, filename)
                        files_to_process.append(file_path)

            results["total_files"] = len(files_to_process)

            # Start batch operation
            self._start_operation(
                "encrypt_directory",
                {
                    "directory_path": directory_path,
                    "total_files": results["total_files"],
                    "recursive": recursive,
                },
            )

            # Process each file
            for i, file_path in enumerate(files_to_process):
                if self._should_stop:
                    self.operation_cancelled.emit(
                        "User requested cancellation"
                    )
                    break

                try:
                    file_size = os.path.getsize(file_path)
                    results["total_bytes"] += file_size

                    # Update overall progress
                    self._update_progress(
                        i,
                        len(files_to_process),
                        f"Encrypting file {i+1} of {len(files_to_process)}",
                    )

                    if self.encrypt_file(file_path, key):
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(
                            f"Failed to encrypt {file_path}"
                        )

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    results["errors"].append(error_msg)

            results["duration"] = time.time() - start_time

            # Complete operation
            self._complete_operation("encrypt_directory", results)

            return results

        except Exception as e:
            error_msg = f"Directory encryption failed: {str(e)}"
            self.error_occurred.emit(error_msg)
            results["errors"].append(error_msg)
            return results

    def decrypt_directory(
        self, directory_path: str, key: bytes, recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Decrypt all .encrypted files in directory with detailed results.

        Args:
            directory_path: Path to directory
            key: Decryption key
            recursive: Whether to process subdirectories

        Returns:
            Dict containing operation results
        """
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "duration": 0,
            "total_bytes": 0,
        }

        try:
            start_time = time.time()

            # Collect encrypted files to process
            files_to_process = []
            for root, dirs, files in os.walk(directory_path):
                if not recursive and root != directory_path:
                    continue

                for filename in files:
                    if filename.endswith(self.ENCRYPTED_EXTENSION):
                        file_path = os.path.join(root, filename)
                        files_to_process.append(file_path)

            results["total_files"] = len(files_to_process)

            # Start batch operation
            self._start_operation(
                "decrypt_directory",
                {
                    "directory_path": directory_path,
                    "total_files": results["total_files"],
                    "recursive": recursive,
                },
            )

            # Process each file
            for i, file_path in enumerate(files_to_process):
                if self._should_stop:
                    self.operation_cancelled.emit(
                        "User requested cancellation"
                    )
                    break

                try:
                    file_size = os.path.getsize(file_path)
                    results["total_bytes"] += file_size

                    # Update overall progress
                    self._update_progress(
                        i,
                        len(files_to_process),
                        f"Decrypting file {i+1} of {len(files_to_process)}",
                    )

                    if self.decrypt_file(file_path, key):
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(
                            f"Failed to decrypt {file_path}"
                        )

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    results["errors"].append(error_msg)

            results["duration"] = time.time() - start_time

            # Complete operation
            self._complete_operation("decrypt_directory", results)

            return results

        except Exception as e:
            error_msg = f"Directory decryption failed: {str(e)}"
            self.error_occurred.emit(error_msg)
            results["errors"].append(error_msg)
            return results

    def stop(self):
        """
        Stop current operation gracefully.

        Sets internal cancellation flag and allows current chunk to complete
        before stopping. Safe to call multiple times.
        """
        self._should_stop = True
        if self._current_operation:
            self.operation_cancelled.emit(
                f"Stopping {self._current_operation}"
            )

    def is_running(self) -> bool:
        """
        Check if an operation is currently running.

        Returns:
            bool: True if operation in progress, False otherwise
        """
        return self._is_running

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive operation statistics.

        Returns:
            Dict containing operation statistics
        """
        uptime = time.time() - self._uptime_start

        return {
            "operations_completed": self._operations_completed,
            "total_bytes_processed": self._total_bytes_processed,
            "average_speed": (
                self._total_bytes_processed / uptime if uptime > 0 else 0
            ),
            "error_count": self._error_count,
            "uptime": uptime,
            "current_operation": self._current_operation,
            "is_running": self._is_running,
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get detailed performance metrics.

        Returns:
            Dict containing performance metrics
        """
        import psutil

        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "memory_usage": memory_info.rss,
                "cpu_percent": process.cpu_percent(),
                "operations_completed": self._operations_completed,
                "total_bytes_processed": self._total_bytes_processed,
                "error_count": self._error_count,
            }
        except ImportError:
            return {
                "memory_usage": 0,
                "cpu_percent": 0,
                "operations_completed": self._operations_completed,
                "total_bytes_processed": self._total_bytes_processed,
                "error_count": self._error_count,
            }

    def _start_operation(
        self, operation_type: str, parameters: Dict[str, Any]
    ):
        """Start a new operation with tracking."""
        self._is_running = True
        self._should_stop = False
        self._current_operation = operation_type
        self._operation_start_time = time.time()

        self.operation_started.emit(operation_type, parameters)

        if self.hub_instance:
            self.hub_status_change.emit(
                "operation_started",
                {"operation_type": operation_type, "parameters": parameters},
            )

    def _complete_operation(
        self, operation_type: str, results: Dict[str, Any]
    ):
        """Complete an operation with tracking."""
        self._is_running = False
        self._current_operation = None
        self._operations_completed += 1

        if "bytes_processed" in results:
            self._total_bytes_processed += results["bytes_processed"]

        duration = (
            time.time() - self._operation_start_time
            if self._operation_start_time
            else 0
        )

        completion_msg = (
            f"{operation_type} completed in {duration:.2f} seconds"
        )
        self.operation_complete.emit(completion_msg)

        if self.hub_instance:
            self.hub_status_change.emit(
                "operation_completed",
                {
                    "operation_type": operation_type,
                    "results": results,
                    "duration": duration,
                },
            )

    def _update_progress(self, current: int, total: int, message: str):
        """Update progress with throttling."""
        current_time = time.time()

        # Throttle progress updates
        if (
            current_time - self._last_progress_update
            < self._progress_update_interval
        ):
            return

        self._last_progress_update = current_time

        # Emit progress signals
        self.progress_updated.emit(current, total, message)
        self.file_progress.emit(current, total)

        # Calculate percentage for hub
        percentage = int((current / total) * 100) if total > 0 else 0
        self.hub_progress_update.emit(percentage, message)
