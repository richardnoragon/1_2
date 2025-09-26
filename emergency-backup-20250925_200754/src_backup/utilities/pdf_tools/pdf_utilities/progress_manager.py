"""
Progress Tracking System for PDF Tools Hub
Provides unified progress tracking, batch operation support, and real-time updates.
"""

import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from log_config import setup_logger

logger = setup_logger(__name__)


class OperationStatus(Enum):
    """Status of an operation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ProgressInfo:
    """Information about operation progress."""
    operation_id: str
    tool_name: str
    operation_type: str
    status: OperationStatus
    progress_percent: int = 0
    current_step: str = ""
    total_steps: int = 1
    current_step_index: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    files_processed: int = 0
    total_files: int = 0
    current_file: Optional[str] = None
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    @property
    def estimated_remaining(self) -> Optional[float]:
        """Estimate remaining time based on current progress."""
        if self.progress_percent <= 0:
            return None
        
        elapsed = self.elapsed_time
        if elapsed <= 0:
            return None
        
        total_estimated = elapsed * 100 / self.progress_percent
        return max(0, total_estimated - elapsed)
    
    @property
    def is_active(self) -> bool:
        """Check if operation is currently active."""
        return self.status in [OperationStatus.RUNNING, OperationStatus.PAUSED]
    
    @property
    def is_finished(self) -> bool:
        """Check if operation is finished."""
        return self.status in [
            OperationStatus.COMPLETED, 
            OperationStatus.FAILED, 
            OperationStatus.CANCELLED
        ]


class BatchOperation:
    """Manages batch operations with progress tracking."""
    
    def __init__(self, operation_id: str, tool_name: str, 
                 operation_type: str, files: List[str]):
        self.operation_id = operation_id
        self.tool_name = tool_name
        self.operation_type = operation_type
        self.files = files
        self.current_file_index = 0
        self.completed_files: List[str] = []
        self.failed_files: List[str] = []
        self.progress_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def start_next_file(self) -> Optional[str]:
        """Get the next file to process."""
        if self.current_file_index >= len(self.files):
            return None
        
        current_file = self.files[self.current_file_index]
        self.current_file_index += 1
        
        # Update progress
        progress_percent = int((self.current_file_index / len(self.files)) * 100)
        
        if self.progress_callback:
            self.progress_callback(
                self.operation_id,
                progress_percent,
                f"Processing {current_file}",
                self.current_file_index,
                len(self.files),
                current_file
            )
        
        return current_file
    
    def mark_file_completed(self, file_path: str):
        """Mark a file as completed."""
        if file_path not in self.completed_files:
            self.completed_files.append(file_path)
        
        logger.debug(f"File completed: {file_path}")
    
    def mark_file_failed(self, file_path: str, error: str):
        """Mark a file as failed."""
        if file_path not in self.failed_files:
            self.failed_files.append(file_path)
        
        logger.warning(f"File failed: {file_path} - {error}")
    
    @property
    def is_complete(self) -> bool:
        """Check if batch operation is complete."""
        return self.current_file_index >= len(self.files)
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        total_processed = len(self.completed_files) + len(self.failed_files)
        if total_processed == 0:
            return 0.0
        return (len(self.completed_files) / total_processed) * 100


class ProgressManager(QObject):
    """
    Centralized progress tracking manager for PDF tools.
    
    Provides unified progress tracking, batch operation support,
    cancellation capabilities, and real-time updates.
    """
    
    # Signals for progress updates
    progress_updated = pyqtSignal(str, int, str)  # operation_id, percent, message
    operation_started = pyqtSignal(str, str, str)  # operation_id, tool_name, type
    operation_completed = pyqtSignal(str, bool, str)  # operation_id, success, message
    operation_cancelled = pyqtSignal(str)  # operation_id
    batch_file_completed = pyqtSignal(str, str, bool)  # operation_id, file, success
    
    def __init__(self):
        super().__init__()
        self.operations: Dict[str, ProgressInfo] = {}
        self.batch_operations: Dict[str, BatchOperation] = {}
        self.operation_counter = 0
        
        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._periodic_update)
        self.update_timer.start(1000)  # Update every second
        
        logger.info("Progress Manager initialized")
    
    def create_operation(self, tool_name: str, operation_type: str,
                        total_files: int = 1) -> str:
        """
        Create a new operation and return its ID.
        
        Args:
            tool_name: Name of the tool performing the operation
            operation_type: Type of operation (e.g., 'split', 'merge', 'extract')
            total_files: Total number of files to process
            
        Returns:
            Unique operation ID
        """
        self.operation_counter += 1
        operation_id = f"{tool_name}_{operation_type}_{self.operation_counter}"
        
        progress_info = ProgressInfo(
            operation_id=operation_id,
            tool_name=tool_name,
            operation_type=operation_type,
            status=OperationStatus.PENDING,
            total_files=total_files
        )
        
        self.operations[operation_id] = progress_info
        
        logger.info(f"Created operation: {operation_id}")
        return operation_id
    
    def create_batch_operation(self, tool_name: str, operation_type: str,
                              files: List[str]) -> str:
        """
        Create a batch operation for multiple files.
        
        Args:
            tool_name: Name of the tool
            operation_type: Type of operation
            files: List of files to process
            
        Returns:
            Unique operation ID
        """
        operation_id = self.create_operation(tool_name, operation_type, len(files))
        
        batch_op = BatchOperation(operation_id, tool_name, operation_type, files)
        batch_op.set_progress_callback(self._batch_progress_callback)
        self.batch_operations[operation_id] = batch_op
        
        logger.info(f"Created batch operation: {operation_id} with {len(files)} files")
        return operation_id
    
    def start_operation(self, operation_id: str, initial_message: str = ""):
        """Start an operation."""
        if operation_id not in self.operations:
            logger.error(f"Operation not found: {operation_id}")
            return
        
        progress_info = self.operations[operation_id]
        progress_info.status = OperationStatus.RUNNING
        progress_info.start_time = time.time()
        progress_info.current_step = initial_message or "Starting..."
        
        self.operation_started.emit(
            operation_id, 
            progress_info.tool_name, 
            progress_info.operation_type
        )
        
        logger.info(f"Started operation: {operation_id}")
    
    def update_progress(self, operation_id: str, progress_percent: int,
                       message: str = "", current_file: Optional[str] = None):
        """
        Update operation progress.
        
        Args:
            operation_id: Operation ID
            progress_percent: Progress percentage (0-100)
            message: Current status message
            current_file: Currently processing file
        """
        if operation_id not in self.operations:
            logger.warning(f"Operation not found for progress update: {operation_id}")
            return
        
        progress_info = self.operations[operation_id]
        progress_info.progress_percent = max(0, min(100, progress_percent))
        progress_info.current_step = message
        
        if current_file:
            progress_info.current_file = current_file
        
        # Emit progress signal
        self.progress_updated.emit(operation_id, progress_percent, message)
        
        # Auto-complete if 100%
        if progress_percent >= 100 and progress_info.status == OperationStatus.RUNNING:
            self.complete_operation(operation_id, True, "Operation completed successfully")
    
    def complete_operation(self, operation_id: str, success: bool, 
                          message: str = ""):
        """Complete an operation."""
        if operation_id not in self.operations:
            logger.error(f"Operation not found: {operation_id}")
            return
        
        progress_info = self.operations[operation_id]
        progress_info.status = OperationStatus.COMPLETED if success else OperationStatus.FAILED
        progress_info.end_time = time.time()
        progress_info.progress_percent = 100 if success else progress_info.progress_percent
        
        if not success and message:
            progress_info.error_message = message
        
        self.operation_completed.emit(operation_id, success, message)
        
        # Clean up batch operation if exists
        if operation_id in self.batch_operations:
            batch_op = self.batch_operations[operation_id]
            logger.info(
                f"Batch operation completed: {operation_id}, "
                f"Success rate: {batch_op.success_rate:.1f}%"
            )
        
        logger.info(f"Completed operation: {operation_id}, Success: {success}")
    
    def cancel_operation(self, operation_id: str):
        """Cancel an operation."""
        if operation_id not in self.operations:
            logger.error(f"Operation not found: {operation_id}")
            return
        
        progress_info = self.operations[operation_id]
        progress_info.status = OperationStatus.CANCELLED
        progress_info.end_time = time.time()
        
        self.operation_cancelled.emit(operation_id)
        
        logger.info(f"Cancelled operation: {operation_id}")
    
    def pause_operation(self, operation_id: str):
        """Pause an operation."""
        if operation_id not in self.operations:
            logger.error(f"Operation not found: {operation_id}")
            return
        
        progress_info = self.operations[operation_id]
        if progress_info.status == OperationStatus.RUNNING:
            progress_info.status = OperationStatus.PAUSED
            logger.info(f"Paused operation: {operation_id}")
    
    def resume_operation(self, operation_id: str):
        """Resume a paused operation."""
        if operation_id not in self.operations:
            logger.error(f"Operation not found: {operation_id}")
            return
        
        progress_info = self.operations[operation_id]
        if progress_info.status == OperationStatus.PAUSED:
            progress_info.status = OperationStatus.RUNNING
            logger.info(f"Resumed operation: {operation_id}")
    
    def get_operation_info(self, operation_id: str) -> Optional[ProgressInfo]:
        """Get operation information."""
        return self.operations.get(operation_id)
    
    def get_batch_operation(self, operation_id: str) -> Optional[BatchOperation]:
        """Get batch operation."""
        return self.batch_operations.get(operation_id)
    
    def get_active_operations(self) -> List[ProgressInfo]:
        """Get all active operations."""
        return [info for info in self.operations.values() if info.is_active]
    
    def get_operations_by_tool(self, tool_name: str) -> List[ProgressInfo]:
        """Get all operations for a specific tool."""
        return [info for info in self.operations.values() 
                if info.tool_name == tool_name]
    
    def cleanup_completed_operations(self, max_age_hours: int = 24):
        """Clean up old completed operations."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for operation_id, progress_info in self.operations.items():
            if (progress_info.is_finished and 
                progress_info.end_time and
                current_time - progress_info.end_time > max_age_seconds):
                to_remove.append(operation_id)
        
        for operation_id in to_remove:
            del self.operations[operation_id]
            if operation_id in self.batch_operations:
                del self.batch_operations[operation_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old operations")
    
    def _batch_progress_callback(self, operation_id: str, progress_percent: int,
                                message: str, current_index: int, total_files: int,
                                current_file: str):
        """Callback for batch operation progress."""
        self.update_progress(operation_id, progress_percent, message, current_file)
        
        # Update files processed count
        if operation_id in self.operations:
            self.operations[operation_id].files_processed = current_index
    
    def _periodic_update(self):
        """Periodic update for active operations."""
        # Clean up old operations periodically
        if len(self.operations) > 100:  # Arbitrary threshold
            self.cleanup_completed_operations(1)  # Clean up operations older than 1 hour


# Global instance
_progress_manager_instance: Optional[ProgressManager] = None


def get_progress_manager() -> ProgressManager:
    """Get the global progress manager instance."""
    global _progress_manager_instance
    if _progress_manager_instance is None:
        _progress_manager_instance = ProgressManager()
    return _progress_manager_instance


# Convenience functions for easy integration
def create_operation(tool_name: str, operation_type: str, 
                    total_files: int = 1) -> str:
    """Create a new operation."""
    return get_progress_manager().create_operation(tool_name, operation_type, total_files)


def create_batch_operation(tool_name: str, operation_type: str, 
                          files: List[str]) -> str:
    """Create a batch operation."""
    return get_progress_manager().create_batch_operation(tool_name, operation_type, files)


def start_operation(operation_id: str, initial_message: str = ""):
    """Start an operation."""
    get_progress_manager().start_operation(operation_id, initial_message)


def update_progress(operation_id: str, progress_percent: int, 
                   message: str = "", current_file: Optional[str] = None):
    """Update operation progress."""
    get_progress_manager().update_progress(operation_id, progress_percent, message, current_file)


def complete_operation(operation_id: str, success: bool, message: str = ""):
    """Complete an operation."""
    get_progress_manager().complete_operation(operation_id, success, message)


def cancel_operation(operation_id: str):
    """Cancel an operation."""
    get_progress_manager().cancel_operation(operation_id)


if __name__ == '__main__':
    # Test the progress manager
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create progress manager
    pm = get_progress_manager()
    
    # Test single operation
    op_id = create_operation("test_tool", "test_operation")
    start_operation(op_id, "Starting test...")
    
    for i in range(0, 101, 10):
        update_progress(op_id, i, f"Progress: {i}%")
        app.processEvents()
        time.sleep(0.1)
    
    complete_operation(op_id, True, "Test completed")
    
    # Test batch operation
    files = [f"file_{i}.pdf" for i in range(5)]
    batch_id = create_batch_operation("batch_tool", "batch_test", files)
    start_operation(batch_id, "Starting batch...")
    
    batch_op = pm.get_batch_operation(batch_id)
    while not batch_op.is_complete:
        current_file = batch_op.start_next_file()
        if current_file:
            # Simulate processing
            time.sleep(0.2)
            app.processEvents()
            batch_op.mark_file_completed(current_file)
    
    complete_operation(batch_id, True, "Batch completed")
    
    print("Progress manager test completed")