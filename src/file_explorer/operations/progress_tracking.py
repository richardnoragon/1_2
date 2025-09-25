"""
Progress Tracking System for RFU Multi-Pane File Explorer

This module provides comprehensive real-time progress tracking with cancellation
capability, performance metrics, and detailed operation monitoring.

Author: Richard Noragon
Version: 2.0.0
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class ProgressEvent(Enum):
    """Types of progress events."""

    STARTED = auto()
    PROGRESS_UPDATE = auto()
    FILE_COMPLETED = auto()
    PAUSED = auto()
    RESUMED = auto()
    CANCELLED = auto()
    COMPLETED = auto()
    ERROR = auto()


@dataclass
class OperationProgress:
    """Comprehensive progress information for file operations."""

    operation_id: str
    operation_type: str
    status: str

    # File progress
    files_processed: int = 0
    total_files: int = 0
    current_file: str = ""

    # Byte progress
    bytes_processed: int = 0
    total_bytes: int = 0

    # Timing information
    start_time: float = field(default_factory=time.time)
    last_update_time: float = field(default_factory=time.time)
    estimated_completion_time: Optional[float] = None

    # Performance metrics
    transfer_rate_bps: float = 0.0  # Bytes per second
    files_rate_fps: float = 0.0  # Files per second
    average_file_size: float = 0.0

    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Cancellation support
    can_cancel: bool = True
    can_pause: bool = True
    is_paused: bool = False

    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.files_processed / self.total_files) * 100.0

    @property
    def bytes_percentage(self) -> float:
        """Calculate bytes progress percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_processed / self.total_bytes) * 100.0

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    @property
    def remaining_time(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.progress_percentage <= 0 or self.transfer_rate_bps <= 0:
            return None

        remaining_bytes = self.total_bytes - self.bytes_processed
        return remaining_bytes / self.transfer_rate_bps

    @property
    def human_readable_rate(self) -> str:
        """Get human-readable transfer rate."""
        if self.transfer_rate_bps < 1024:
            return f"{self.transfer_rate_bps:.1f} B/s"
        elif self.transfer_rate_bps < 1024 * 1024:
            return f"{self.transfer_rate_bps / 1024:.1f} KB/s"
        elif self.transfer_rate_bps < 1024 * 1024 * 1024:
            return f"{self.transfer_rate_bps / (1024 * 1024):.1f} MB/s"
        else:
            return f"{self.transfer_rate_bps / (1024 * 1024 * 1024):.1f} GB/s"

    @property
    def human_readable_size(self) -> str:
        """Get human-readable size information."""

        def format_bytes(bytes_val):
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if bytes_val < 1024.0:
                    return f"{bytes_val:.1f} {unit}"
                bytes_val /= 1024.0
            return f"{bytes_val:.1f} PB"

        processed = format_bytes(self.bytes_processed)
        total = format_bytes(self.total_bytes)
        return f"{processed} / {total}"


# Type alias for progress callbacks
ProgressCallback = Callable[[OperationProgress], None]


class ProgressTracker(QObject):
    """
    Advanced progress tracking system with real-time updates and analytics.

    Features:
    - Real-time progress monitoring
    - Performance metrics calculation
    - Time estimation algorithms
    - Multi-operation tracking
    - Cancellation and pause support
    - Progress history and analytics
    """

    # Signals for UI integration
    progress_updated = pyqtSignal(str, dict)  # operation_id, progress_data
    operation_started = pyqtSignal(str, dict)  # operation_id, initial_data
    operation_completed = pyqtSignal(str, dict)  # operation_id, final_data
    operation_cancelled = pyqtSignal(str)  # operation_id
    operation_error = pyqtSignal(str, str)  # operation_id, error_message

    def __init__(self, update_interval_ms: int = 250):
        """
        Initialize the progress tracker.

        Args:
            update_interval_ms: Progress update interval in milliseconds
        """
        super().__init__()

        self.update_interval_ms = update_interval_ms

        # Progress tracking
        self.active_operations: Dict[str, OperationProgress] = {}
        self.operation_history: List[OperationProgress] = []
        self.callbacks: Dict[str, List[ProgressCallback]] = {}

        # Thread safety
        self.progress_lock = threading.RLock()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._periodic_update)
        self.update_timer.start(update_interval_ms)

        # Performance tracking
        self.performance_window = []  # Rolling window for rate calculation
        self.performance_window_size = 10

        # Setup logging
        self.logger = logging.getLogger("RFU.ProgressTracker")

        self.logger.info("ProgressTracker initialized")

    def start_tracking(
        self,
        operation_id: str,
        operation_type: str,
        total_files: int = 0,
        total_bytes: int = 0,
        **kwargs,
    ) -> OperationProgress:
        """
        Start tracking progress for an operation.

        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation (copy, move, delete, etc.)
            total_files: Total number of files to process
            total_bytes: Total bytes to process
            **kwargs: Additional progress parameters

        Returns:
            OperationProgress instance
        """
        with self.progress_lock:
            progress = OperationProgress(
                operation_id=operation_id,
                operation_type=operation_type,
                status="started",
                total_files=total_files,
                total_bytes=total_bytes,
                **kwargs,
            )

            self.active_operations[operation_id] = progress

            self.logger.info(
                f"Started tracking: {operation_id} "
                f"({total_files} files, {total_bytes} bytes)"
            )

            # Emit started signal
            self.operation_started.emit(
                operation_id,
                {
                    "operation_type": operation_type,
                    "total_files": total_files,
                    "total_bytes": total_bytes,
                    "start_time": progress.start_time,
                },
            )

            return progress

    def update_progress(
        self,
        operation_id: str,
        files_processed: int = None,
        bytes_processed: int = None,
        current_file: str = None,
        **kwargs,
    ) -> bool:
        """
        Update progress for an operation.

        Args:
            operation_id: Operation to update
            files_processed: Number of files processed
            bytes_processed: Number of bytes processed
            current_file: Currently processing file
            **kwargs: Additional update parameters

        Returns:
            bool: True if update successful
        """
        with self.progress_lock:
            if operation_id not in self.active_operations:
                return False

            progress = self.active_operations[operation_id]

            # Update progress values
            if files_processed is not None:
                progress.files_processed = files_processed
            if bytes_processed is not None:
                progress.bytes_processed = bytes_processed
            if current_file is not None:
                progress.current_file = current_file

            # Update additional fields
            for key, value in kwargs.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)

            # Update timing
            current_time = time.time()
            progress.last_update_time = current_time

            # Calculate performance metrics
            self._calculate_performance_metrics(progress)

            # Estimate completion time
            self._estimate_completion_time(progress)

            return True

    def _calculate_performance_metrics(
        self, progress: OperationProgress
    ) -> None:
        """Calculate real-time performance metrics."""
        elapsed_time = progress.elapsed_time

        if elapsed_time > 0:
            # Transfer rate (bytes per second)
            progress.transfer_rate_bps = (
                progress.bytes_processed / elapsed_time
            )

            # Files rate (files per second)
            progress.files_rate_fps = progress.files_processed / elapsed_time

            # Average file size
            if progress.files_processed > 0:
                progress.average_file_size = (
                    progress.bytes_processed / progress.files_processed
                )

            # Update performance window for smoothing
            self.performance_window.append(
                {
                    "time": time.time(),
                    "bytes": progress.bytes_processed,
                    "files": progress.files_processed,
                }
            )

            # Keep window size limited
            if len(self.performance_window) > self.performance_window_size:
                self.performance_window.pop(0)

            # Calculate smoothed rates
            if len(self.performance_window) >= 2:
                first = self.performance_window[0]
                last = self.performance_window[-1]
                time_diff = last["time"] - first["time"]

                if time_diff > 0:
                    bytes_diff = last["bytes"] - first["bytes"]
                    files_diff = last["files"] - first["files"]

                    # Use smoothed rates
                    progress.transfer_rate_bps = bytes_diff / time_diff
                    progress.files_rate_fps = files_diff / time_diff

    def _estimate_completion_time(self, progress: OperationProgress) -> None:
        """Estimate operation completion time."""
        if (
            progress.transfer_rate_bps <= 0
            or progress.total_bytes <= progress.bytes_processed
        ):
            progress.estimated_completion_time = None
            return

        remaining_bytes = progress.total_bytes - progress.bytes_processed
        estimated_seconds = remaining_bytes / progress.transfer_rate_bps
        progress.estimated_completion_time = time.time() + estimated_seconds

    def pause_operation(self, operation_id: str) -> bool:
        """
        Pause an operation.

        Args:
            operation_id: Operation to pause

        Returns:
            bool: True if successfully paused
        """
        with self.progress_lock:
            if (
                operation_id not in self.active_operations
                or not self.active_operations[operation_id].can_pause
            ):
                return False

            progress = self.active_operations[operation_id]
            progress.is_paused = True
            progress.status = "paused"

            self.logger.info(f"Operation paused: {operation_id}")

            return True

    def resume_operation(self, operation_id: str) -> bool:
        """
        Resume a paused operation.

        Args:
            operation_id: Operation to resume

        Returns:
            bool: True if successfully resumed
        """
        with self.progress_lock:
            if (
                operation_id not in self.active_operations
                or not self.active_operations[operation_id].is_paused
            ):
                return False

            progress = self.active_operations[operation_id]
            progress.is_paused = False
            progress.status = "in_progress"

            self.logger.info(f"Operation resumed: {operation_id}")

            return True

    def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel an operation.

        Args:
            operation_id: Operation to cancel

        Returns:
            bool: True if successfully cancelled
        """
        with self.progress_lock:
            if (
                operation_id not in self.active_operations
                or not self.active_operations[operation_id].can_cancel
            ):
                return False

            progress = self.active_operations[operation_id]
            progress.status = "cancelled"

            # Move to history
            self.operation_history.append(progress)
            del self.active_operations[operation_id]

            self.logger.info(f"Operation cancelled: {operation_id}")
            self.operation_cancelled.emit(operation_id)

            return True

    def complete_operation(
        self,
        operation_id: str,
        success: bool = True,
        error_message: str = None,
    ) -> bool:
        """
        Mark an operation as completed.

        Args:
            operation_id: Operation to complete
            success: Whether operation completed successfully
            error_message: Error message if operation failed

        Returns:
            bool: True if successfully completed
        """
        with self.progress_lock:
            if operation_id not in self.active_operations:
                return False

            progress = self.active_operations[operation_id]

            if success:
                progress.status = "completed"
                # Ensure progress shows 100%
                progress.files_processed = progress.total_files
                progress.bytes_processed = progress.total_bytes
            else:
                progress.status = "failed"
                if error_message:
                    progress.errors.append(error_message)

            # Final metrics calculation
            self._calculate_performance_metrics(progress)

            # Move to history
            self.operation_history.append(progress)
            del self.active_operations[operation_id]

            self.logger.info(
                f"Operation completed: {operation_id} " f"(success={success})"
            )

            # Emit completion signal
            self.operation_completed.emit(
                operation_id,
                {
                    "success": success,
                    "elapsed_time": progress.elapsed_time,
                    "files_processed": progress.files_processed,
                    "bytes_processed": progress.bytes_processed,
                    "transfer_rate": progress.human_readable_rate,
                    "error_message": error_message,
                },
            )

            return True

    def get_progress(self, operation_id: str) -> Optional[OperationProgress]:
        """
        Get current progress for an operation.

        Args:
            operation_id: Operation ID

        Returns:
            OperationProgress or None if not found
        """
        with self.progress_lock:
            return self.active_operations.get(operation_id)

    def get_all_active_progress(self) -> Dict[str, OperationProgress]:
        """
        Get progress for all active operations.

        Returns:
            Dict of operation_id -> OperationProgress
        """
        with self.progress_lock:
            return self.active_operations.copy()

    def add_callback(
        self, operation_id: str, callback: ProgressCallback
    ) -> None:
        """
        Add a progress callback for an operation.

        Args:
            operation_id: Operation ID
            callback: Callback function to call on progress updates
        """
        if operation_id not in self.callbacks:
            self.callbacks[operation_id] = []
        self.callbacks[operation_id].append(callback)

    def remove_callback(
        self, operation_id: str, callback: ProgressCallback
    ) -> None:
        """
        Remove a progress callback.

        Args:
            operation_id: Operation ID
            callback: Callback function to remove
        """
        if operation_id in self.callbacks:
            try:
                self.callbacks[operation_id].remove(callback)
                if not self.callbacks[operation_id]:
                    del self.callbacks[operation_id]
            except ValueError:
                pass

    def _periodic_update(self) -> None:
        """Periodic update of progress information and callbacks."""
        with self.progress_lock:
            current_operations = list(self.active_operations.items())

        # Update each active operation
        for operation_id, progress in current_operations:
            # Update performance metrics
            self._calculate_performance_metrics(progress)

            # Call registered callbacks
            if operation_id in self.callbacks:
                for callback in self.callbacks[operation_id]:
                    try:
                        callback(progress)
                    except Exception as e:
                        self.logger.error(
                            f"Callback error for {operation_id}: {e}"
                        )

            # Emit progress signal
            self.progress_updated.emit(
                operation_id,
                {
                    "files_processed": progress.files_processed,
                    "total_files": progress.total_files,
                    "bytes_processed": progress.bytes_processed,
                    "total_bytes": progress.total_bytes,
                    "progress_percentage": progress.progress_percentage,
                    "transfer_rate": progress.human_readable_rate,
                    "current_file": progress.current_file,
                    "elapsed_time": progress.elapsed_time,
                    "remaining_time": progress.remaining_time,
                    "status": progress.status,
                },
            )

    def get_operation_history(
        self, limit: int = 50
    ) -> List[OperationProgress]:
        """
        Get operation history.

        Args:
            limit: Maximum number of operations to return

        Returns:
            List of completed operations
        """
        with self.progress_lock:
            return (
                self.operation_history[-limit:]
                if limit > 0
                else self.operation_history.copy()
            )

    def clear_history(self) -> None:
        """Clear operation history."""
        with self.progress_lock:
            self.operation_history.clear()
        self.logger.info("Operation history cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics.

        Returns:
            Dict containing usage statistics
        """
        with self.progress_lock:
            active_count = len(self.active_operations)
            total_completed = len(self.operation_history)

            # Calculate aggregate metrics from history
            total_files = sum(
                op.files_processed for op in self.operation_history
            )
            total_bytes = sum(
                op.bytes_processed for op in self.operation_history
            )
            total_time = sum(op.elapsed_time for op in self.operation_history)

            success_count = sum(
                1 for op in self.operation_history if op.status == "completed"
            )

            return {
                "active_operations": active_count,
                "completed_operations": total_completed,
                "success_rate": (
                    (success_count / total_completed * 100)
                    if total_completed > 0
                    else 0
                ),
                "total_files_processed": total_files,
                "total_bytes_processed": total_bytes,
                "total_processing_time": total_time,
                "average_transfer_rate": (
                    (total_bytes / total_time) if total_time > 0 else 0
                ),
            }
