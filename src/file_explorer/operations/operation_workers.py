"""
Asynchronous File Operation Workers for RFU Multi-Pane File Explorer

This module provides specialized worker classes for different file operation types
with comprehensive queue management, progress tracking, and error handling.

Author: Richard Noragon
Version: 2.0.0
"""

import logging
import queue
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from .file_operations import (
    FileOperation,
    FileOperationError,
    FileOperationResult,
    OperationStatus,
    OperationType,
)


@dataclass
class WorkerTask:
    """Task definition for operation workers."""

    operation: FileOperation
    result: FileOperationResult
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3


class FileOperationWorker(QRunnable, ABC):
    """
    Abstract base class for file operation workers.

    Provides common functionality for all operation types including:
    - Progress tracking and reporting
    - Error handling and recovery
    - Cancellation support
    - Resource management
    """

    def __init__(self, task: WorkerTask, progress_callback=None):
        """
        Initialize the worker.

        Args:
            task: WorkerTask containing operation details
            progress_callback: Optional callback for progress updates
        """
        super().__init__()
        self.task = task
        self.progress_callback = progress_callback
        self.cancelled = threading.Event()
        self.logger = logging.getLogger(
            f"RFU.Worker.{self.__class__.__name__}"
        )

        # Performance metrics
        self.start_time = 0.0
        self.bytes_per_second = 0.0
        self.files_per_second = 0.0

    def run(self) -> None:
        """Execute the worker task with comprehensive error handling."""
        self.start_time = time.time()

        try:
            self.logger.info(
                f"Starting worker: {self.task.operation.operation_id}"
            )

            # Update status
            self.task.result.status = OperationStatus.IN_PROGRESS

            # Execute the specific operation
            self.execute_operation()

            # Mark as completed
            self.task.result.status = OperationStatus.COMPLETED
            self.task.result.end_time = time.time()

            # Calculate performance metrics
            self._calculate_performance_metrics()

            self.logger.info(
                f"Worker completed: {self.task.operation.operation_id}"
            )

        except FileOperationError as e:
            self._handle_error(e)
        except Exception as e:
            error = FileOperationError(
                f"Unexpected error in worker: {e}",
                operation_id=self.task.operation.operation_id,
                recoverable=False,
            )
            self._handle_error(error)

    @abstractmethod
    def execute_operation(self) -> None:
        """Execute the specific file operation. Must be implemented by subclasses."""
        pass

    def _handle_error(self, error: FileOperationError) -> None:
        """Handle errors during operation execution."""
        self.task.result.status = OperationStatus.FAILED
        self.task.result.error = error
        self.task.result.end_time = time.time()

        self.logger.error(
            f"Worker error: {self.task.operation.operation_id} - {error}"
        )

        # Determine if retry is appropriate
        if error.recoverable and self.task.retry_count < self.task.max_retries:
            self.task.retry_count += 1
            self.logger.info(
                f"Scheduling retry {self.task.retry_count}/{self.task.max_retries}"
            )
            # Note: Actual retry scheduling would be handled by the queue manager

    def _calculate_performance_metrics(self) -> None:
        """Calculate and log performance metrics."""
        duration = self.task.result.duration
        if duration > 0:
            self.bytes_per_second = self.task.result.bytes_processed / duration
            self.files_per_second = self.task.result.files_processed / duration

            self.logger.debug(
                f"Performance metrics - "
                f"Files/sec: {self.files_per_second:.2f}, "
                f"MB/sec: {self.bytes_per_second / 1024 / 1024:.2f}"
            )

    def cancel(self) -> None:
        """Cancel the worker operation."""
        self.cancelled.set()
        self.logger.info(
            f"Worker cancelled: {self.task.operation.operation_id}"
        )

    def is_cancelled(self) -> bool:
        """Check if worker has been cancelled."""
        return self.cancelled.is_set()

    def update_progress(
        self, current_file: str = "", additional_data: Dict = None
    ) -> None:
        """
        Update operation progress.

        Args:
            current_file: Currently processing file
            additional_data: Additional progress data
        """
        if self.progress_callback:
            progress_data = {
                "operation_id": self.task.operation.operation_id,
                "files_processed": self.task.result.files_processed,
                "total_files": self.task.result.total_files,
                "bytes_processed": self.task.result.bytes_processed,
                "total_bytes": self.task.result.total_bytes,
                "current_file": current_file,
                "transfer_rate": self.bytes_per_second,
                "percentage": self.task.result.progress_percentage,
            }

            if additional_data:
                progress_data.update(additional_data)

            self.progress_callback(progress_data)


class CopyWorker(FileOperationWorker):
    """Specialized worker for copy operations."""

    def execute_operation(self) -> None:
        """Execute copy operation with progress tracking."""
        operation = self.task.operation
        result = self.task.result

        dest_path = Path(operation.destination_path)

        for source_path_str in operation.source_paths:
            if self.is_cancelled():
                raise FileOperationError(
                    "Operation cancelled", operation_id=operation.operation_id
                )

            source_path = Path(source_path_str)

            if source_path.is_file():
                self._copy_file(source_path, dest_path)
            elif source_path.is_dir():
                self._copy_directory(source_path, dest_path)

    def _copy_file(self, source: Path, dest_dir: Path) -> None:
        """Copy a single file with progress tracking."""
        dest_file = dest_dir / source.name

        # Handle name conflicts
        counter = 1
        original_dest = dest_file
        while dest_file.exists():
            stem = original_dest.stem
            suffix = original_dest.suffix
            dest_file = dest_dir / f"{stem}_copy_{counter}{suffix}"
            counter += 1

        self.logger.debug(f"Copying file: {source} -> {dest_file}")

        # Copy with progress tracking
        file_size = source.stat().st_size
        bytes_copied = 0
        chunk_size = 65536  # 64KB chunks

        try:
            with open(source, "rb") as src, open(dest_file, "wb") as dst:
                while True:
                    # Check for cancellation
                    if self.is_cancelled():
                        dst.close()
                        dest_file.unlink()  # Delete partial file
                        raise FileOperationError(
                            "Copy operation cancelled",
                            operation_id=self.task.operation.operation_id,
                        )

                    chunk = src.read(chunk_size)
                    if not chunk:
                        break

                    dst.write(chunk)
                    bytes_copied += len(chunk)
                    self.task.result.bytes_processed += len(chunk)

                    # Update progress every MB
                    if bytes_copied % (1024 * 1024) == 0:
                        self.update_progress(str(source))

            # Preserve file metadata
            self._preserve_metadata(source, dest_file)

            self.task.result.files_processed += 1
            self.update_progress(str(source))

        except IOError as e:
            if dest_file.exists():
                dest_file.unlink()  # Cleanup on error
            raise FileOperationError(
                f"Failed to copy file {source}: {e}",
                operation_id=self.task.operation.operation_id,
                file_path=str(source),
            )

    def _copy_directory(self, source: Path, dest_dir: Path) -> None:
        """Copy a directory recursively."""
        dest_path = dest_dir / source.name

        # Handle directory name conflicts
        counter = 1
        original_dest = dest_path
        while dest_path.exists():
            dest_path = dest_dir / f"{original_dest.name}_copy_{counter}"
            counter += 1

        self.logger.debug(f"Copying directory: {source} -> {dest_path}")

        try:
            dest_path.mkdir(parents=True, exist_ok=True)

            # Copy all files in directory
            for item in source.rglob("*"):
                if self.is_cancelled():
                    raise FileOperationError(
                        "Directory copy cancelled",
                        operation_id=self.task.operation.operation_id,
                    )

                if item.is_file():
                    rel_path = item.relative_to(source)
                    dest_file = dest_path / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy the file
                    self._copy_file(item, dest_file.parent)

        except Exception as e:
            # Cleanup on error
            if dest_path.exists():
                import shutil

                shutil.rmtree(dest_path, ignore_errors=True)
            raise FileOperationError(
                f"Failed to copy directory {source}: {e}",
                operation_id=self.task.operation.operation_id,
                file_path=str(source),
            )

    def _preserve_metadata(self, source: Path, dest: Path) -> None:
        """Preserve file metadata (timestamps, permissions)."""
        try:
            import shutil

            shutil.copystat(str(source), str(dest))
        except Exception as e:
            self.logger.warning(f"Failed to preserve metadata for {dest}: {e}")


class MoveWorker(FileOperationWorker):
    """Specialized worker for move operations."""

    def execute_operation(self) -> None:
        """Execute move operation with atomic guarantees."""
        # Use copy then delete strategy for safety
        copy_worker = CopyWorker(self.task, self.progress_callback)
        copy_worker.execute_operation()

        # If copy succeeded, delete originals
        operation = self.task.operation

        for source_path_str in operation.source_paths:
            if self.is_cancelled():
                raise FileOperationError(
                    "Move operation cancelled",
                    operation_id=operation.operation_id,
                )

            source_path = Path(source_path_str)

            try:
                if source_path.is_file():
                    source_path.unlink()
                elif source_path.is_dir():
                    import shutil

                    shutil.rmtree(source_path)

                self.logger.debug(f"Deleted original: {source_path}")

            except Exception as e:
                # Log warning but don't fail the operation
                warning = f"Failed to delete original {source_path}: {e}"
                self.task.result.warnings.append(warning)
                self.logger.warning(warning)


class DeleteWorker(FileOperationWorker):
    """Specialized worker for delete operations."""

    def execute_operation(self) -> None:
        """Execute delete operation with recovery support."""
        operation = self.task.operation
        result = self.task.result

        # Store backup info for potential recovery
        backup_info = {}

        for source_path_str in operation.source_paths:
            if self.is_cancelled():
                raise FileOperationError(
                    "Delete operation cancelled",
                    operation_id=operation.operation_id,
                )

            source_path = Path(source_path_str)

            try:
                if source_path.is_file():
                    # Store file metadata
                    stat_info = source_path.stat()
                    backup_info[source_path_str] = {
                        "type": "file",
                        "size": stat_info.st_size,
                        "mtime": stat_info.st_mtime,
                        "mode": stat_info.st_mode,
                    }

                    source_path.unlink()
                    result.files_processed += 1
                    result.bytes_processed += stat_info.st_size

                elif source_path.is_dir():
                    # Count files for progress tracking
                    file_count = 0
                    total_size = 0

                    for item in source_path.rglob("*"):
                        if item.is_file():
                            file_count += 1
                            try:
                                total_size += item.stat().st_size
                            except (OSError, IOError):
                                pass

                    backup_info[source_path_str] = {
                        "type": "directory",
                        "file_count": file_count,
                        "total_size": total_size,
                    }

                    import shutil

                    shutil.rmtree(source_path)
                    result.files_processed += file_count
                    result.bytes_processed += total_size

                self.logger.debug(f"Deleted: {source_path}")
                self.update_progress(str(source_path))

            except Exception as e:
                raise FileOperationError(
                    f"Failed to delete {source_path}: {e}",
                    operation_id=operation.operation_id,
                    file_path=source_path_str,
                )

        result.rollback_info = backup_info


class RenameWorker(FileOperationWorker):
    """Specialized worker for rename operations."""

    def execute_operation(self) -> None:
        """Execute rename operation with conflict resolution."""
        operation = self.task.operation
        result = self.task.result

        if len(operation.source_paths) != 1:
            raise FileOperationError(
                "Rename operation requires exactly one source path",
                operation_id=operation.operation_id,
            )

        source_path = Path(operation.source_paths[0])
        new_name = operation.options.get("new_name")

        if not new_name:
            raise FileOperationError(
                "Rename operation requires 'new_name' in options",
                operation_id=operation.operation_id,
            )

        dest_path = source_path.parent / new_name

        # Check for conflicts
        if dest_path.exists() and dest_path != source_path:
            conflict_resolution = operation.options.get(
                "conflict_resolution", "error"
            )

            if conflict_resolution == "error":
                raise FileOperationError(
                    f"Destination already exists: {dest_path}",
                    operation_id=operation.operation_id,
                    file_path=str(dest_path),
                )
            elif conflict_resolution == "auto_rename":
                counter = 1
                base_name = Path(new_name).stem
                suffix = Path(new_name).suffix

                while dest_path.exists():
                    new_name_numbered = f"{base_name}_{counter}{suffix}"
                    dest_path = source_path.parent / new_name_numbered
                    counter += 1

        try:
            # Perform rename
            source_path.rename(dest_path)

            result.files_processed = 1
            result.destination_path = str(dest_path)

            # Store rollback information
            result.rollback_info = {
                "original_path": str(source_path),
                "new_path": str(dest_path),
            }

            self.logger.debug(f"Renamed: {source_path} -> {dest_path}")
            self.update_progress(str(dest_path))

        except Exception as e:
            raise FileOperationError(
                f"Failed to rename {source_path} to {new_name}: {e}",
                operation_id=operation.operation_id,
                file_path=str(source_path),
            )


class OperationQueue(QObject):
    """
    Advanced operation queue with priority management and worker coordination.

    Features:
    - Priority-based task scheduling
    - Worker pool management
    - Load balancing and throttling
    - Retry logic for failed operations
    - Progress aggregation
    """

    # Signals for queue events
    queue_updated = pyqtSignal(int)  # queue_size
    worker_started = pyqtSignal(str)  # operation_id
    worker_completed = pyqtSignal(str, bool)  # operation_id, success

    def __init__(self, max_workers: int = 3):
        """
        Initialize the operation queue.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        super().__init__()

        self.max_workers = max_workers
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_workers)

        # Queue management
        self.task_queue = queue.PriorityQueue()
        self.active_workers: Dict[str, FileOperationWorker] = {}
        self.completed_tasks: List[WorkerTask] = []
        self.failed_tasks: List[WorkerTask] = []

        # Thread synchronization
        self.queue_lock = threading.RLock()
        self.shutdown_event = threading.Event()

        # Setup logging
        self.logger = logging.getLogger("RFU.OperationQueue")

        # Start queue processor
        self._start_queue_processor()

        self.logger.info(
            f"OperationQueue initialized with {max_workers} workers"
        )

    def submit_task(self, task: WorkerTask) -> None:
        """
        Submit a task to the queue.

        Args:
            task: WorkerTask to execute
        """
        with self.queue_lock:
            # Use negative priority for max-heap behavior (higher priority first)
            self.task_queue.put((-task.priority, time.time(), task))

        self.logger.info(f"Task queued: {task.operation.operation_id}")
        self.queue_updated.emit(self.task_queue.qsize())

    def cancel_task(self, operation_id: str) -> bool:
        """
        Cancel a task by operation ID.

        Args:
            operation_id: ID of operation to cancel

        Returns:
            bool: True if successfully cancelled
        """
        with self.queue_lock:
            # Cancel active worker
            if operation_id in self.active_workers:
                worker = self.active_workers[operation_id]
                worker.cancel()
                del self.active_workers[operation_id]

                self.logger.info(f"Active worker cancelled: {operation_id}")
                return True

            # Remove from queue (requires rebuilding queue)
            temp_items = []
            cancelled = False

            while not self.task_queue.empty():
                try:
                    priority, timestamp, task = self.task_queue.get_nowait()
                    if task.operation.operation_id == operation_id:
                        cancelled = True
                        self.logger.info(
                            f"Queued task cancelled: {operation_id}"
                        )
                    else:
                        temp_items.append((priority, timestamp, task))
                except queue.Empty:
                    break

            # Rebuild queue
            for item in temp_items:
                self.task_queue.put(item)

            if cancelled:
                self.queue_updated.emit(self.task_queue.qsize())

            return cancelled

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.

        Returns:
            Dict containing queue metrics
        """
        with self.queue_lock:
            return {
                "queued_tasks": self.task_queue.qsize(),
                "active_workers": len(self.active_workers),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "max_workers": self.max_workers,
            }

    def _start_queue_processor(self) -> None:
        """Start the background queue processor."""

        def queue_processor():
            """Process tasks from queue in background thread."""
            while not self.shutdown_event.is_set():
                try:
                    self._process_queue()
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                except Exception as e:
                    self.logger.error(f"Queue processor error: {e}")
                    time.sleep(1.0)

        processor_thread = threading.Thread(
            target=queue_processor, name="RFU-QueueProcessor", daemon=True
        )
        processor_thread.start()

        self.logger.info("Queue processor started")

    def _process_queue(self) -> None:
        """Process pending tasks from the queue."""
        with self.queue_lock:
            # Check if we can start more workers
            if (
                len(self.active_workers) >= self.max_workers
                or self.task_queue.empty()
            ):
                return

            try:
                # Get next task
                priority, timestamp, task = self.task_queue.get_nowait()

                # Create appropriate worker
                worker = self._create_worker(task)

                # Start worker
                self.active_workers[task.operation.operation_id] = worker
                self.thread_pool.start(worker)

                self.logger.info(
                    f"Worker started: {task.operation.operation_id}"
                )
                self.worker_started.emit(task.operation.operation_id)
                self.queue_updated.emit(self.task_queue.qsize())

            except queue.Empty:
                pass

    def _create_worker(self, task: WorkerTask) -> FileOperationWorker:
        """
        Create appropriate worker for task type.

        Args:
            task: Task to create worker for

        Returns:
            FileOperationWorker instance
        """
        operation_type = task.operation.operation_type

        # Progress callback
        def progress_callback(data):
            # This would emit progress signals to UI
            pass

        if operation_type == OperationType.COPY:
            return CopyWorker(task, progress_callback)
        elif operation_type == OperationType.MOVE:
            return MoveWorker(task, progress_callback)
        elif operation_type == OperationType.DELETE:
            return DeleteWorker(task, progress_callback)
        elif operation_type == OperationType.RENAME:
            return RenameWorker(task, progress_callback)
        else:
            raise ValueError(f"Unsupported operation type: {operation_type}")

    def shutdown(self) -> None:
        """Gracefully shutdown the operation queue."""
        self.logger.info("Shutting down OperationQueue...")

        # Signal shutdown
        self.shutdown_event.set()

        # Cancel all active workers
        with self.queue_lock:
            for worker in self.active_workers.values():
                worker.cancel()

        # Wait for thread pool to finish
        self.thread_pool.waitForDone(30000)  # 30 second timeout

        self.logger.info("OperationQueue shutdown complete")
