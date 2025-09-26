"""
Batch Processing Engine for PDF Tools Hub
Provides queue-based batch operations, resource management, and optimization.
"""

import os
import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from threading import Thread, Lock, Event
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QProgressDialog, QMessageBox

from progress_manager import get_progress_manager, OperationStatus
from error_manager import get_error_manager, handle_error
from log_config import setup_logger

logger = setup_logger(__name__)


class BatchJobStatus(Enum):
    """Status of a batch job."""

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchJobPriority(Enum):
    """Priority levels for batch jobs."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class BatchJobItem:
    """Individual item in a batch job."""

    input_file: str
    output_file: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: BatchJobStatus = BatchJobStatus.QUEUED
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def processing_time(self) -> Optional[float]:
        """Get processing time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class BatchJob:
    """A batch processing job."""

    job_id: str
    tool_name: str
    operation_type: str
    items: List[BatchJobItem]
    priority: BatchJobPriority = BatchJobPriority.NORMAL
    status: BatchJobStatus = BatchJobStatus.QUEUED
    progress_callback: Optional[Callable] = None
    completion_callback: Optional[Callable] = None
    created_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def total_items(self) -> int:
        """Get total number of items."""
        return len(self.items)

    @property
    def completed_items(self) -> int:
        """Get number of completed items."""
        return len(
            [
                item
                for item in self.items
                if item.status == BatchJobStatus.COMPLETED
            ]
        )

    @property
    def failed_items(self) -> int:
        """Get number of failed items."""
        return len(
            [
                item
                for item in self.items
                if item.status == BatchJobStatus.FAILED
            ]
        )

    @property
    def progress_percent(self) -> float:
        """Get progress as percentage."""
        if self.total_items == 0:
            return 100.0
        processed = self.completed_items + self.failed_items
        return (processed / self.total_items) * 100

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        processed = self.completed_items + self.failed_items
        if processed == 0:
            return 0.0
        return (self.completed_items / processed) * 100

    @property
    def estimated_remaining_time(self) -> Optional[float]:
        """Estimate remaining time based on current progress."""
        if not self.start_time or self.completed_items == 0:
            return None

        elapsed = time.time() - self.start_time
        avg_time_per_item = elapsed / self.completed_items
        remaining_items = (
            self.total_items - self.completed_items - self.failed_items
        )

        return remaining_items * avg_time_per_item


class BatchProcessor(QObject):
    """
    Queue-based batch processing engine for PDF operations.

    Manages multiple batch jobs, resource allocation, and provides
    progress tracking and error handling.
    """

    # Signals for batch processing events
    job_started = pyqtSignal(str)  # job_id
    job_completed = pyqtSignal(str, bool, str)  # job_id, success, message
    job_progress = pyqtSignal(str, float, str)  # job_id, percent, current_item
    item_completed = pyqtSignal(str, str, bool)  # job_id, item_file, success

    def __init__(self, max_concurrent_jobs: int = 2):
        super().__init__()
        self.max_concurrent_jobs = max_concurrent_jobs
        self.jobs: Dict[str, BatchJob] = {}
        self.job_queue = Queue()
        self.running_jobs: Dict[str, Thread] = {}
        self.job_counter = 0
        self.is_processing = False
        self.pause_event = Event()
        self.pause_event.set()  # Start unpaused

        # Thread safety
        self.jobs_lock = Lock()

        # Progress and error managers
        self.progress_manager = get_progress_manager()
        self.error_manager = get_error_manager()

        # Processing thread
        self.processor_thread = Thread(target=self._process_queue, daemon=True)
        self.processor_thread.start()

        logger.info(
            f"Batch Processor initialized with {max_concurrent_jobs} concurrent jobs"
        )

    def create_batch_job(
        self,
        tool_name: str,
        operation_type: str,
        input_files: List[str],
        output_dir: Optional[str] = None,
        parameters: Dict[str, Any] = None,
        priority: BatchJobPriority = BatchJobPriority.NORMAL,
    ) -> str:
        """
        Create a new batch job.

        Args:
            tool_name: Name of the tool to use
            operation_type: Type of operation
            input_files: List of input files
            output_dir: Output directory (optional)
            parameters: Operation parameters
            priority: Job priority

        Returns:
            Unique job ID
        """
        if parameters is None:
            parameters = {}

        # Generate job ID
        self.job_counter += 1
        job_id = f"batch_{tool_name}_{operation_type}_{self.job_counter}"

        # Create batch items
        items = []
        for input_file in input_files:
            output_file = None
            if output_dir:
                filename = os.path.basename(input_file)
                name, ext = os.path.splitext(filename)
                output_file = os.path.join(
                    output_dir, f"{name}_processed{ext}"
                )

            item = BatchJobItem(
                input_file=input_file,
                output_file=output_file,
                parameters=parameters.copy(),
            )
            items.append(item)

        # Create batch job
        batch_job = BatchJob(
            job_id=job_id,
            tool_name=tool_name,
            operation_type=operation_type,
            items=items,
            priority=priority,
        )

        # Store job
        with self.jobs_lock:
            self.jobs[job_id] = batch_job

        # Add to queue
        self.job_queue.put((priority.value, job_id))

        logger.info(f"Created batch job {job_id} with {len(items)} items")
        return job_id

    def start_job(
        self,
        job_id: str,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None,
    ):
        """
        Start a batch job.

        Args:
            job_id: Job ID to start
            progress_callback: Callback for progress updates
            completion_callback: Callback for completion
        """
        with self.jobs_lock:
            if job_id not in self.jobs:
                logger.error(f"Job not found: {job_id}")
                return

            job = self.jobs[job_id]
            job.progress_callback = progress_callback
            job.completion_callback = completion_callback
            job.status = BatchJobStatus.QUEUED

        logger.info(f"Started batch job: {job_id}")

    def pause_job(self, job_id: str):
        """Pause a batch job."""
        with self.jobs_lock:
            if job_id in self.jobs:
                self.jobs[job_id].status = BatchJobStatus.PAUSED
                logger.info(f"Paused batch job: {job_id}")

    def resume_job(self, job_id: str):
        """Resume a paused batch job."""
        with self.jobs_lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                if job.status == BatchJobStatus.PAUSED:
                    job.status = BatchJobStatus.QUEUED
                    # Re-add to queue
                    self.job_queue.put((job.priority.value, job_id))
                    logger.info(f"Resumed batch job: {job_id}")

    def cancel_job(self, job_id: str):
        """Cancel a batch job."""
        with self.jobs_lock:
            if job_id in self.jobs:
                self.jobs[job_id].status = BatchJobStatus.CANCELLED
                logger.info(f"Cancelled batch job: {job_id}")

    def pause_all_processing(self):
        """Pause all batch processing."""
        self.pause_event.clear()
        logger.info("Paused all batch processing")

    def resume_all_processing(self):
        """Resume all batch processing."""
        self.pause_event.set()
        logger.info("Resumed all batch processing")

    def get_job_info(self, job_id: str) -> Optional[BatchJob]:
        """Get job information."""
        with self.jobs_lock:
            return self.jobs.get(job_id)

    def get_active_jobs(self) -> List[BatchJob]:
        """Get all active jobs."""
        with self.jobs_lock:
            return [
                job
                for job in self.jobs.values()
                if job.status
                in [BatchJobStatus.RUNNING, BatchJobStatus.QUEUED]
            ]

    def get_job_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        with self.jobs_lock:
            total_jobs = len(self.jobs)
            running_jobs = len(
                [
                    j
                    for j in self.jobs.values()
                    if j.status == BatchJobStatus.RUNNING
                ]
            )
            queued_jobs = len(
                [
                    j
                    for j in self.jobs.values()
                    if j.status == BatchJobStatus.QUEUED
                ]
            )
            completed_jobs = len(
                [
                    j
                    for j in self.jobs.values()
                    if j.status == BatchJobStatus.COMPLETED
                ]
            )

            return {
                "total_jobs": total_jobs,
                "running_jobs": running_jobs,
                "queued_jobs": queued_jobs,
                "completed_jobs": completed_jobs,
                "queue_size": self.job_queue.qsize(),
                "max_concurrent": self.max_concurrent_jobs,
            }

    def _process_queue(self):
        """Main processing loop (runs in separate thread)."""
        while True:
            try:
                # Wait if paused
                self.pause_event.wait()

                # Check if we can start a new job
                if len(self.running_jobs) >= self.max_concurrent_jobs:
                    time.sleep(0.1)
                    continue

                # Get next job from queue
                try:
                    priority, job_id = self.job_queue.get(timeout=1.0)
                except Empty:
                    continue

                # Check if job is still valid
                with self.jobs_lock:
                    if job_id not in self.jobs:
                        continue

                    job = self.jobs[job_id]
                    if job.status != BatchJobStatus.QUEUED:
                        continue

                    # Mark as running
                    job.status = BatchJobStatus.RUNNING
                    job.start_time = time.time()

                # Start processing thread for this job
                job_thread = Thread(
                    target=self._process_job, args=(job_id,), daemon=True
                )
                self.running_jobs[job_id] = job_thread
                job_thread.start()

                logger.debug(f"Started processing job: {job_id}")

            except Exception as e:
                logger.error(
                    f"Error in batch processing queue: {e}", exc_info=True
                )
                time.sleep(1.0)

    def _process_job(self, job_id: str):
        """Process a single batch job."""
        try:
            with self.jobs_lock:
                if job_id not in self.jobs:
                    return
                job = self.jobs[job_id]

            logger.info(f"Processing batch job: {job_id}")
            self.job_started.emit(job_id)

            # Create progress operation
            operation_id = self.progress_manager.create_batch_operation(
                job.tool_name,
                job.operation_type,
                [item.input_file for item in job.items],
            )
            self.progress_manager.start_operation(
                operation_id, "Starting batch job..."
            )

            # Process each item
            for i, item in enumerate(job.items):
                # Check if job was cancelled
                if job.status == BatchJobStatus.CANCELLED:
                    break

                # Wait if paused
                while job.status == BatchJobStatus.PAUSED:
                    time.sleep(0.1)

                try:
                    item.start_time = time.time()
                    item.status = BatchJobStatus.RUNNING

                    # Update progress
                    progress_percent = (i / len(job.items)) * 100
                    current_item = os.path.basename(item.input_file)

                    self.progress_manager.update_progress(
                        operation_id,
                        int(progress_percent),
                        f"Processing {current_item}",
                        item.input_file,
                    )

                    if job.progress_callback:
                        job.progress_callback(
                            job_id, progress_percent, current_item
                        )

                    self.job_progress.emit(
                        job_id, progress_percent, current_item
                    )

                    # Process the item (this would call the actual tool)
                    success = self._process_item(job, item)

                    item.end_time = time.time()
                    item.status = (
                        BatchJobStatus.COMPLETED
                        if success
                        else BatchJobStatus.FAILED
                    )

                    self.item_completed.emit(job_id, item.input_file, success)

                    logger.debug(
                        f"Processed item {i+1}/{len(job.items)}: {item.input_file}"
                    )

                except Exception as e:
                    item.end_time = time.time()
                    item.status = BatchJobStatus.FAILED
                    item.error_message = str(e)

                    # Handle error
                    error_context = {
                        "tool_name": job.tool_name,
                        "operation_type": job.operation_type,
                        "file_path": item.input_file,
                        "job_id": job_id,
                    }
                    handle_error(e, error_context)

                    logger.error(
                        f"Failed to process item {item.input_file}: {e}"
                    )

            # Complete the job
            job.end_time = time.time()

            if job.status == BatchJobStatus.CANCELLED:
                job.status = BatchJobStatus.CANCELLED
                message = "Job was cancelled"
                success = False
            elif job.failed_items == 0:
                job.status = BatchJobStatus.COMPLETED
                message = f"All {job.total_items} items processed successfully"
                success = True
            else:
                job.status = BatchJobStatus.COMPLETED
                message = (
                    f"Job completed with {job.failed_items} failures "
                    f"out of {job.total_items} items"
                )
                success = job.completed_items > 0

            # Update progress manager
            self.progress_manager.complete_operation(
                operation_id, success, message
            )

            # Notify completion
            if job.completion_callback:
                job.completion_callback(job_id, success, message)

            self.job_completed.emit(job_id, success, message)

            logger.info(f"Completed batch job {job_id}: {message}")

        except Exception as e:
            logger.error(
                f"Error processing batch job {job_id}: {e}", exc_info=True
            )

            with self.jobs_lock:
                if job_id in self.jobs:
                    self.jobs[job_id].status = BatchJobStatus.FAILED
                    self.jobs[job_id].end_time = time.time()

            self.job_completed.emit(job_id, False, f"Job failed: {str(e)}")

        finally:
            # Remove from running jobs
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    def _process_item(self, job: BatchJob, item: BatchJobItem) -> bool:
        """
        Process a single item in a batch job.

        This is a placeholder that should be overridden or extended
        to call the actual tool processing functions.
        """
        try:
            # This is where you would call the actual tool processing
            # For now, we'll simulate processing
            time.sleep(0.1)  # Simulate processing time

            # In a real implementation, you would:
            # 1. Import the appropriate tool module
            # 2. Call the tool's processing function
            # 3. Handle tool-specific parameters
            # 4. Return success/failure based on tool result

            logger.debug(f"Simulated processing of {item.input_file}")
            return True

        except Exception as e:
            logger.error(f"Error processing item {item.input_file}: {e}")
            return False


# Global instance
_batch_processor_instance: Optional[BatchProcessor] = None


def get_batch_processor() -> BatchProcessor:
    """Get the global batch processor instance."""
    global _batch_processor_instance
    if _batch_processor_instance is None:
        _batch_processor_instance = BatchProcessor()
    return _batch_processor_instance


# Convenience functions
def create_batch_job(
    tool_name: str,
    operation_type: str,
    input_files: List[str],
    output_dir: Optional[str] = None,
    parameters: Dict[str, Any] = None,
    priority: BatchJobPriority = BatchJobPriority.NORMAL,
) -> str:
    """Create a batch job."""
    return get_batch_processor().create_batch_job(
        tool_name,
        operation_type,
        input_files,
        output_dir,
        parameters,
        priority,
    )


def start_batch_job(
    job_id: str,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
):
    """Start a batch job."""
    get_batch_processor().start_job(
        job_id, progress_callback, completion_callback
    )


if __name__ == "__main__":
    # Test the batch processor
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create batch processor
    bp = get_batch_processor()

    # Test batch job
    test_files = [f"test_file_{i}.pdf" for i in range(5)]
    job_id = create_batch_job("test_tool", "test_operation", test_files)

    def progress_callback(job_id, percent, current_item):
        print(f"Job {job_id}: {percent:.1f}% - {current_item}")

    def completion_callback(job_id, success, message):
        print(f"Job {job_id} completed: {success} - {message}")

    start_batch_job(job_id, progress_callback, completion_callback)

    # Wait for completion
    time.sleep(2)

    print("Batch processor test completed")
