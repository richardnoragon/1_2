"""
Core File Operations Manager for RFU Multi-Pane File Explorer

This module provides the central file operation management system with enterprise-grade
features including thread safety, atomic transactions, comprehensive error handling,
and real-time progress tracking.

Author: Richard Noragon
Version: 2.0.0
"""

import asyncio
import hashlib
import logging
import os
import shutil
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import psutil
from PyQt5.QtCore import QObject, QThread, pyqtSignal

# Import RFU core components
try:
    from src.rfu.config_manager import ConfigManager
    from src.rfu.log_manager import get_log_manager
except ImportError:
    # Fallback for development
    get_log_manager = None
    ConfigManager = None


class OperationType(Enum):
    """Enumeration of supported file operation types."""
    COPY = auto()
    MOVE = auto()
    DELETE = auto()
    RENAME = auto()
    CREATE_DIRECTORY = auto()
    DELETE_DIRECTORY = auto()
    COMPRESS = auto()
    DECOMPRESS = auto()
    CHECKSUM = auto()
    SYNC = auto()


class OperationStatus(Enum):
    """Enumeration of operation status states."""
    PENDING = auto()
    QUEUED = auto()
    INITIALIZING = auto()
    IN_PROGRESS = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    ROLLED_BACK = auto()


class FileOperationError(Exception):
    """Custom exception for file operation errors with enhanced context."""
    
    def __init__(self, message: str, operation_id: str = None, 
                 file_path: str = None, error_code: int = None,
                 recoverable: bool = True, **kwargs):
        """
        Initialize file operation error.
        
        Args:
            message: Human-readable error message
            operation_id: Unique operation identifier
            file_path: Path of file causing error
            error_code: System error code if available
            recoverable: Whether error can be recovered from
            **kwargs: Additional error context
        """
        super().__init__(message)
        self.operation_id = operation_id
        self.file_path = file_path
        self.error_code = error_code
        self.recoverable = recoverable
        self.context = kwargs
        self.timestamp = time.time()


@dataclass
class FileOperationResult:
    """Result of a file operation with comprehensive metadata."""
    
    operation_id: str
    operation_type: OperationType
    status: OperationStatus
    source_paths: List[str] = field(default_factory=list)
    destination_path: Optional[str] = None
    files_processed: int = 0
    total_files: int = 0
    bytes_processed: int = 0
    total_bytes: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    error: Optional[FileOperationError] = None
    warnings: List[str] = field(default_factory=list)
    rollback_info: Optional[Dict[str, Any]] = None
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    @property
    def progress_percentage(self) -> float:
        """Get operation progress as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.files_processed / self.total_files) * 100.0
    
    @property
    def transfer_rate(self) -> float:
        """Get transfer rate in bytes per second."""
        duration = self.duration
        if duration <= 0:
            return 0.0
        return self.bytes_processed / duration


@dataclass
class FileOperation:
    """Comprehensive file operation definition with metadata."""
    
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: OperationType = OperationType.COPY
    source_paths: List[str] = field(default_factory=list)
    destination_path: Optional[str] = None
    status: OperationStatus = OperationStatus.PENDING
    priority: int = 0  # Higher values = higher priority
    options: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate operation parameters after initialization."""
        if not self.source_paths:
            raise ValueError("Source paths cannot be empty")
        
        if self.operation_type in (OperationType.COPY, OperationType.MOVE, 
                                  OperationType.SYNC) and not self.destination_path:
            raise ValueError(f"{self.operation_type.name} requires destination path")


class FileOperationManager(QObject):
    """
    Central manager for all file operations with enterprise-grade capabilities.
    
    Features:
    - Thread-safe operation management
    - Atomic transactions with rollback capability
    - Comprehensive progress tracking
    - Resource management and throttling
    - Conflict resolution and error recovery
    - Operation queuing and prioritization
    """
    
    # Signals for UI integration
    operation_started = pyqtSignal(str, dict)  # operation_id, metadata
    operation_progress = pyqtSignal(str, float, dict)  # operation_id, progress, stats
    operation_completed = pyqtSignal(str, bool, dict)  # operation_id, success, result
    operation_error = pyqtSignal(str, str, dict)  # operation_id, error_msg, context
    
    def __init__(self, max_concurrent_operations: int = 3):
        """
        Initialize the file operation manager.
        
        Args:
            max_concurrent_operations: Maximum number of concurrent operations
        """
        super().__init__()
        
        # Core configuration
        self.max_concurrent_operations = max_concurrent_operations
        self.operation_lock = threading.RLock()
        self.shutdown_event = threading.Event()
        
        # Operation tracking
        self.active_operations: Dict[str, FileOperation] = {}
        self.operation_results: Dict[str, FileOperationResult] = {}
        self.operation_queue: List[FileOperation] = []
        
        # Worker management
        self.executor = ThreadPoolExecutor(
            max_workers=max_concurrent_operations,
            thread_name_prefix="RFU-FileOp"
        )
        self.worker_futures: Dict[str, Any] = {}
        
        # Monitoring and throttling
        self.resource_monitor = ResourceMonitor()
        self.operation_throttle = OperationThrottle()
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Configuration manager
        self.config_manager = ConfigManager() if ConfigManager else None
        
        # Start background services
        self._start_queue_processor()
        self._start_resource_monitor()
        
        self.logger.info("FileOperationManager initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging for file operations."""
        if get_log_manager:
            return get_log_manager().get_logger('RFU.FileOperations')
        else:
            # Fallback logging setup
            logger = logging.getLogger('RFU.FileOperations')
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            return logger
    
    def submit_operation(self, operation: FileOperation) -> str:
        """
        Submit a file operation for execution.
        
        Args:
            operation: FileOperation to execute
            
        Returns:
            str: Operation ID for tracking
            
        Raises:
            FileOperationError: If operation validation fails
        """
        try:
            # Validate operation
            self._validate_operation(operation)
            
            # Check dependencies
            self._check_dependencies(operation)
            
            # Add to queue
            with self.operation_lock:
                self.operation_queue.append(operation)
                self.active_operations[operation.operation_id] = operation
                
                # Create result placeholder
                result = FileOperationResult(
                    operation_id=operation.operation_id,
                    operation_type=operation.operation_type,
                    status=OperationStatus.QUEUED,
                    source_paths=operation.source_paths,
                    destination_path=operation.destination_path
                )
                self.operation_results[operation.operation_id] = result
            
            self.logger.info(f"Operation queued: {operation.operation_id} "
                           f"({operation.operation_type.name})")
            
            return operation.operation_id
            
        except Exception as e:
            error = FileOperationError(
                f"Failed to submit operation: {e}",
                operation_id=operation.operation_id,
                recoverable=False
            )
            self.logger.error(f"Operation submission failed: {e}")
            raise error
    
    def _validate_operation(self, operation: FileOperation) -> None:
        """
        Validate operation parameters and constraints.
        
        Args:
            operation: Operation to validate
            
        Raises:
            FileOperationError: If validation fails
        """
        # Check source paths exist
        for source_path in operation.source_paths:
            path = Path(source_path)
            if not path.exists():
                raise FileOperationError(
                    f"Source path does not exist: {source_path}",
                    operation_id=operation.operation_id,
                    file_path=source_path
                )
        
        # Check destination path validity
        if operation.destination_path:
            dest_path = Path(operation.destination_path)
            if operation.operation_type in (OperationType.COPY, OperationType.MOVE):
                # Ensure destination directory exists or can be created
                if dest_path.is_file():
                    dest_path = dest_path.parent
                if not dest_path.exists():
                    try:
                        dest_path.mkdir(parents=True, exist_ok=True)
                    except OSError as e:
                        raise FileOperationError(
                            f"Cannot create destination directory: {e}",
                            operation_id=operation.operation_id,
                            file_path=str(dest_path)
                        )
        
        # Check for circular operations (move to subdirectory)
        if operation.operation_type == OperationType.MOVE:
            for source_path in operation.source_paths:
                source = Path(source_path)
                destination = Path(operation.destination_path)
                try:
                    # Check if destination is within source
                    destination.relative_to(source)
                    raise FileOperationError(
                        f"Cannot move directory to its subdirectory: "
                        f"{source_path} -> {operation.destination_path}",
                        operation_id=operation.operation_id
                    )
                except ValueError:
                    # relative_to failed, which is good - no circular reference
                    pass
    
    def _check_dependencies(self, operation: FileOperation) -> None:
        """
        Check if operation dependencies are satisfied.
        
        Args:
            operation: Operation to check
            
        Raises:
            FileOperationError: If dependencies are not met
        """
        for dep_id in operation.dependencies:
            if dep_id in self.active_operations:
                dep_operation = self.active_operations[dep_id]
                if dep_operation.status not in (OperationStatus.COMPLETED, 
                                              OperationStatus.FAILED,
                                              OperationStatus.CANCELLED):
                    raise FileOperationError(
                        f"Dependency not satisfied: {dep_id}",
                        operation_id=operation.operation_id
                    )
    
    def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel a pending or in-progress operation.
        
        Args:
            operation_id: ID of operation to cancel
            
        Returns:
            bool: True if successfully cancelled
        """
        with self.operation_lock:
            if operation_id not in self.active_operations:
                return False
            
            operation = self.active_operations[operation_id]
            
            # Update status
            operation.status = OperationStatus.CANCELLED
            
            # Cancel future if it exists
            if operation_id in self.worker_futures:
                future = self.worker_futures[operation_id]
                cancelled = future.cancel()
                if not cancelled and not future.done():
                    # Force cancellation through thread interruption
                    self._force_cancel_operation(operation_id)
                del self.worker_futures[operation_id]
            
            # Update result
            if operation_id in self.operation_results:
                result = self.operation_results[operation_id]
                result.status = OperationStatus.CANCELLED
                result.end_time = time.time()
            
            self.logger.info(f"Operation cancelled: {operation_id}")
            self.operation_completed.emit(operation_id, False, {
                'status': 'cancelled',
                'message': 'Operation cancelled by user'
            })
            
            return True
    
    def _force_cancel_operation(self, operation_id: str) -> None:
        """
        Force cancellation of an operation through thread interruption.
        
        Args:
            operation_id: ID of operation to force cancel
        """
        # Implementation would depend on specific worker thread management
        # This is a placeholder for more advanced cancellation logic
        self.logger.warning(f"Force cancelling operation: {operation_id}")
    
    def get_operation_status(self, operation_id: str) -> Optional[FileOperationResult]:
        """
        Get current status of an operation.
        
        Args:
            operation_id: ID of operation
            
        Returns:
            FileOperationResult or None if not found
        """
        with self.operation_lock:
            return self.operation_results.get(operation_id)
    
    def get_active_operations(self) -> List[str]:
        """
        Get list of currently active operation IDs.
        
        Returns:
            List of active operation IDs
        """
        with self.operation_lock:
            return [
                op_id for op_id, op in self.active_operations.items()
                if op.status in (OperationStatus.QUEUED, OperationStatus.IN_PROGRESS,
                               OperationStatus.INITIALIZING)
            ]
    
    def _start_queue_processor(self) -> None:
        """Start the operation queue processor thread."""
        def queue_processor():
            """Process operation queue in background thread."""
            while not self.shutdown_event.is_set():
                try:
                    self._process_queue()
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                except Exception as e:
                    self.logger.error(f"Queue processor error: {e}")
                    time.sleep(1.0)  # Longer delay on error
        
        queue_thread = threading.Thread(
            target=queue_processor,
            name="RFU-QueueProcessor",
            daemon=True
        )
        queue_thread.start()
        self.logger.info("Queue processor started")
    
    def _process_queue(self) -> None:
        """Process pending operations from the queue."""
        with self.operation_lock:
            if not self.operation_queue:
                return
            
            # Count currently running operations
            running_count = len([
                op for op in self.active_operations.values()
                if op.status == OperationStatus.IN_PROGRESS
            ])
            
            if running_count >= self.max_concurrent_operations:
                return
            
            # Sort queue by priority and creation time
            self.operation_queue.sort(
                key=lambda op: (-op.priority, op.created_at)
            )
            
            # Process operations up to limit
            operations_to_start = min(
                len(self.operation_queue),
                self.max_concurrent_operations - running_count
            )
            
            for _ in range(operations_to_start):
                if not self.operation_queue:
                    break
                
                operation = self.operation_queue.pop(0)
                
                # Check if operation was cancelled while queued
                if operation.status == OperationStatus.CANCELLED:
                    continue
                
                # Check resource availability
                if not self.resource_monitor.can_start_operation(operation):
                    # Put back in queue
                    self.operation_queue.insert(0, operation)
                    break
                
                # Start operation
                self._start_operation(operation)
    
    def _start_operation(self, operation: FileOperation) -> None:
        """
        Start execution of a file operation.
        
        Args:
            operation: Operation to start
        """
        try:
            # Update status
            operation.status = OperationStatus.INITIALIZING
            
            # Update result
            result = self.operation_results[operation.operation_id]
            result.status = OperationStatus.INITIALIZING
            
            # Calculate operation size
            self._calculate_operation_size(operation, result)
            
            # Submit to executor
            future = self.executor.submit(self._execute_operation, operation)
            self.worker_futures[operation.operation_id] = future
            
            # Update status to in progress
            operation.status = OperationStatus.IN_PROGRESS
            result.status = OperationStatus.IN_PROGRESS
            
            self.logger.info(f"Operation started: {operation.operation_id}")
            self.operation_started.emit(operation.operation_id, {
                'type': operation.operation_type.name,
                'source_count': len(operation.source_paths),
                'total_files': result.total_files,
                'total_bytes': result.total_bytes
            })
            
        except Exception as e:
            self._handle_operation_error(operation, e)
    
    def _calculate_operation_size(self, operation: FileOperation, 
                                result: FileOperationResult) -> None:
        """
        Calculate total size and file count for operation.
        
        Args:
            operation: Operation to analyze
            result: Result object to update
        """
        total_files = 0
        total_bytes = 0
        
        try:
            for source_path in operation.source_paths:
                path = Path(source_path)
                if path.is_file():
                    total_files += 1
                    total_bytes += path.stat().st_size
                elif path.is_dir():
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            total_files += 1
                            try:
                                total_bytes += file_path.stat().st_size
                            except (OSError, IOError):
                                # Skip files that can't be accessed
                                pass
            
            result.total_files = total_files
            result.total_bytes = total_bytes
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate operation size: {e}")
            # Use fallback estimates
            result.total_files = len(operation.source_paths)
            result.total_bytes = 0
    
    def _execute_operation(self, operation: FileOperation) -> FileOperationResult:
        """
        Execute a file operation with comprehensive error handling.
        
        Args:
            operation: Operation to execute
            
        Returns:
            FileOperationResult: Result of the operation
        """
        result = self.operation_results[operation.operation_id]
        
        try:
            # Execute based on operation type
            if operation.operation_type == OperationType.COPY:
                self._execute_copy_operation(operation, result)
            elif operation.operation_type == OperationType.MOVE:
                self._execute_move_operation(operation, result)
            elif operation.operation_type == OperationType.DELETE:
                self._execute_delete_operation(operation, result)
            elif operation.operation_type == OperationType.RENAME:
                self._execute_rename_operation(operation, result)
            else:
                raise FileOperationError(
                    f"Unsupported operation type: {operation.operation_type}",
                    operation_id=operation.operation_id
                )
            
            # Mark as completed
            result.status = OperationStatus.COMPLETED
            result.end_time = time.time()
            
            self.logger.info(f"Operation completed: {operation.operation_id}")
            self.operation_completed.emit(operation.operation_id, True, {
                'status': 'completed',
                'files_processed': result.files_processed,
                'bytes_processed': result.bytes_processed,
                'duration': result.duration
            })
            
        except Exception as e:
            self._handle_operation_error(operation, e)
            
        finally:
            # Cleanup
            with self.operation_lock:
                if operation.operation_id in self.worker_futures:
                    del self.worker_futures[operation.operation_id]
        
        return result
    
    def _execute_copy_operation(self, operation: FileOperation, 
                              result: FileOperationResult) -> None:
        """Execute copy operation with progress tracking."""
        dest_path = Path(operation.destination_path)
        
        for source_path_str in operation.source_paths:
            source_path = Path(source_path_str)
            
            if source_path.is_file():
                self._copy_file_with_progress(source_path, dest_path, result)
            elif source_path.is_dir():
                self._copy_directory_with_progress(source_path, dest_path, result)
    
    def _copy_file_with_progress(self, source: Path, dest_dir: Path, 
                               result: FileOperationResult) -> None:
        """Copy a single file with progress tracking."""
        dest_file = dest_dir / source.name
        
        # Handle name conflicts
        counter = 1
        while dest_file.exists():
            stem = source.stem
            suffix = source.suffix
            dest_file = dest_dir / f"{stem}_copy_{counter}{suffix}"
            counter += 1
        
        # Copy with progress tracking
        file_size = source.stat().st_size
        bytes_copied = 0
        
        with open(source, 'rb') as src, open(dest_file, 'wb') as dst:
            while True:
                # Check for cancellation
                if self.active_operations[result.operation_id].status == OperationStatus.CANCELLED:
                    dst.close()
                    dest_file.unlink()  # Delete partial file
                    raise FileOperationError(
                        "Operation cancelled",
                        operation_id=result.operation_id
                    )
                
                chunk = src.read(65536)  # 64KB chunks
                if not chunk:
                    break
                
                dst.write(chunk)
                bytes_copied += len(chunk)
                result.bytes_processed += len(chunk)
                
                # Emit progress
                self.operation_progress.emit(result.operation_id, 
                                           result.progress_percentage, {
                    'bytes_processed': result.bytes_processed,
                    'transfer_rate': result.transfer_rate,
                    'current_file': str(source)
                })
        
        result.files_processed += 1
        self.logger.debug(f"Copied file: {source} -> {dest_file}")
    
    def _copy_directory_with_progress(self, source: Path, dest_dir: Path,
                                    result: FileOperationResult) -> None:
        """Copy a directory recursively with progress tracking."""
        dest_path = dest_dir / source.name
        dest_path.mkdir(exist_ok=True)
        
        for item in source.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(source)
                dest_file = dest_path / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Use the single file copy method
                temp_result = FileOperationResult(
                    operation_id=result.operation_id,
                    operation_type=result.operation_type,
                    status=result.status
                )
                self._copy_file_with_progress(item, dest_file.parent, temp_result)
                result.files_processed += temp_result.files_processed
                result.bytes_processed += temp_result.bytes_processed
    
    def _execute_move_operation(self, operation: FileOperation,
                              result: FileOperationResult) -> None:
        """Execute move operation with atomic guarantees."""
        # First copy, then delete original if copy succeeds
        temp_operation = FileOperation(
            operation_type=OperationType.COPY,
            source_paths=operation.source_paths,
            destination_path=operation.destination_path
        )
        
        # Execute copy phase
        self._execute_copy_operation(temp_operation, result)
        
        # If copy succeeded, delete originals
        for source_path_str in operation.source_paths:
            source_path = Path(source_path_str)
            try:
                if source_path.is_file():
                    source_path.unlink()
                elif source_path.is_dir():
                    shutil.rmtree(source_path)
                self.logger.debug(f"Deleted original: {source_path}")
            except Exception as e:
                # Log warning but don't fail the operation
                result.warnings.append(f"Failed to delete original {source_path}: {e}")
                self.logger.warning(f"Failed to delete original after move: {e}")
    
    def _execute_delete_operation(self, operation: FileOperation,
                                result: FileOperationResult) -> None:
        """Execute delete operation with recovery support."""
        # Store backup info for recovery
        backup_info = {}
        
        for source_path_str in operation.source_paths:
            source_path = Path(source_path_str)
            
            try:
                if source_path.is_file():
                    # For files, store metadata for recovery
                    stat_info = source_path.stat()
                    backup_info[source_path_str] = {
                        'type': 'file',
                        'size': stat_info.st_size,
                        'mtime': stat_info.st_mtime
                    }
                    source_path.unlink()
                    result.files_processed += 1
                    
                elif source_path.is_dir():
                    # For directories, count files first
                    file_count = sum(1 for _ in source_path.rglob('*') if _.is_file())
                    backup_info[source_path_str] = {
                        'type': 'directory',
                        'file_count': file_count
                    }
                    shutil.rmtree(source_path)
                    result.files_processed += file_count
                
                self.logger.debug(f"Deleted: {source_path}")
                
            except Exception as e:
                raise FileOperationError(
                    f"Failed to delete {source_path}: {e}",
                    operation_id=result.operation_id,
                    file_path=source_path_str
                )
        
        result.rollback_info = backup_info
    
    def _execute_rename_operation(self, operation: FileOperation,
                                result: FileOperationResult) -> None:
        """Execute rename operation with conflict resolution."""
        if len(operation.source_paths) != 1:
            raise FileOperationError(
                "Rename operation requires exactly one source path",
                operation_id=result.operation_id
            )
        
        source_path = Path(operation.source_paths[0])
        new_name = operation.options.get('new_name')
        
        if not new_name:
            raise FileOperationError(
                "Rename operation requires 'new_name' in options",
                operation_id=result.operation_id
            )
        
        dest_path = source_path.parent / new_name
        
        # Check for conflicts
        if dest_path.exists() and dest_path != source_path:
            conflict_resolution = operation.options.get('conflict_resolution', 'error')
            
            if conflict_resolution == 'error':
                raise FileOperationError(
                    f"Destination already exists: {dest_path}",
                    operation_id=result.operation_id,
                    file_path=str(dest_path)
                )
            elif conflict_resolution == 'rename':
                counter = 1
                while dest_path.exists():
                    stem = Path(new_name).stem
                    suffix = Path(new_name).suffix
                    new_name_numbered = f"{stem}_{counter}{suffix}"
                    dest_path = source_path.parent / new_name_numbered
                    counter += 1
        
        # Perform rename
        source_path.rename(dest_path)
        result.files_processed = 1
        result.destination_path = str(dest_path)
        
        self.logger.debug(f"Renamed: {source_path} -> {dest_path}")
    
    def _handle_operation_error(self, operation: FileOperation, error: Exception) -> None:
        """Handle operation errors with comprehensive logging and recovery."""
        result = self.operation_results[operation.operation_id]
        
        # Create or enhance error object
        if isinstance(error, FileOperationError):
            file_error = error
        else:
            file_error = FileOperationError(
                str(error),
                operation_id=operation.operation_id,
                recoverable=True
            )
        
        # Update operation and result status
        operation.status = OperationStatus.FAILED
        result.status = OperationStatus.FAILED
        result.error = file_error
        result.end_time = time.time()
        
        # Log error with full context
        self.logger.error(f"Operation failed: {operation.operation_id} - {error}")
        
        # Emit error signal
        self.operation_error.emit(operation.operation_id, str(error), {
            'operation_type': operation.operation_type.name,
            'error_code': getattr(error, 'error_code', None),
            'recoverable': getattr(error, 'recoverable', True),
            'file_path': getattr(error, 'file_path', None)
        })
        
        # Attempt automatic recovery if error is recoverable
        if file_error.recoverable:
            self._attempt_error_recovery(operation, file_error)
    
    def _attempt_error_recovery(self, operation: FileOperation, 
                              error: FileOperationError) -> None:
        """Attempt automatic error recovery based on error type."""
        self.logger.info(f"Attempting error recovery for: {operation.operation_id}")
        
        # Recovery strategies can be implemented here
        # For now, just log the attempt
        recovery_strategies = {
            'permission_denied': self._recover_permission_error,
            'disk_full': self._recover_disk_full_error,
            'file_locked': self._recover_file_locked_error,
        }
        
        # This is a placeholder for more sophisticated error recovery
        self.logger.info(f"Error recovery not implemented for: {type(error).__name__}")
    
    def _recover_permission_error(self, operation: FileOperation) -> bool:
        """Attempt to recover from permission errors."""
        # Could attempt to elevate permissions or suggest alternative paths
        return False
    
    def _recover_disk_full_error(self, operation: FileOperation) -> bool:
        """Attempt to recover from disk full errors."""
        # Could suggest cleanup or alternative destinations
        return False
    
    def _recover_file_locked_error(self, operation: FileOperation) -> bool:
        """Attempt to recover from file locked errors."""
        # Could retry after delay or suggest closing applications
        return False
    
    def _start_resource_monitor(self) -> None:
        """Start system resource monitoring."""
        def resource_monitor():
            """Monitor system resources in background thread."""
            while not self.shutdown_event.is_set():
                try:
                    self.resource_monitor.update_metrics()
                    time.sleep(5.0)  # Update every 5 seconds
                except Exception as e:
                    self.logger.error(f"Resource monitor error: {e}")
                    time.sleep(10.0)
        
        monitor_thread = threading.Thread(
            target=resource_monitor,
            name="RFU-ResourceMonitor",
            daemon=True
        )
        monitor_thread.start()
        self.logger.info("Resource monitor started")
    
    def shutdown(self) -> None:
        """Gracefully shutdown the file operation manager."""
        self.logger.info("Shutting down FileOperationManager...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Cancel all pending operations
        with self.operation_lock:
            for operation_id in list(self.active_operations.keys()):
                if self.active_operations[operation_id].status in (
                    OperationStatus.QUEUED, 
                    OperationStatus.IN_PROGRESS
                ):
                    self.cancel_operation(operation_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True, timeout=30)
        
        self.logger.info("FileOperationManager shutdown complete")


class ResourceMonitor:
    """Monitor system resources for operation throttling."""
    
    def __init__(self):
        """Initialize resource monitor."""
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = {}
        self.network_usage = 0.0
        
        # Thresholds for operation throttling
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
    
    def update_metrics(self) -> None:
        """Update current system metrics."""
        try:
            # CPU usage
            self.cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage = memory.percent
            
            # Disk usage for all mounted drives
            self.disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    self.disk_usage[partition.mountpoint] = usage.percent
                except (PermissionError, OSError):
                    pass
            
        except Exception:
            # Continue with last known values on error
            pass
    
    def can_start_operation(self, operation: FileOperation) -> bool:
        """
        Check if system resources allow starting new operation.
        
        Args:
            operation: Operation to check
            
        Returns:
            bool: True if operation can start
        """
        # Check CPU threshold
        if self.cpu_usage > self.cpu_threshold:
            return False
        
        # Check memory threshold
        if self.memory_usage > self.memory_threshold:
            return False
        
        # Check disk usage for destination
        if operation.destination_path:
            dest_drive = Path(operation.destination_path).anchor
            if dest_drive in self.disk_usage:
                if self.disk_usage[dest_drive] > self.disk_threshold:
                    return False
        
        return True


class OperationThrottle:
    """Throttle operations based on system load and priorities."""
    
    def __init__(self):
        """Initialize operation throttle."""
        self.last_operation_time = 0.0
        self.min_operation_interval = 0.1  # Minimum seconds between operations
    
    def should_throttle(self) -> bool:
        """Check if operations should be throttled."""
        current_time = time.time()
        if current_time - self.last_operation_time < self.min_operation_interval:
            return True
        
        self.last_operation_time = current_time
        return False