"""
File Operations Module for RFU Multi-Pane File Explorer

This module provides comprehensive, thread-safe file operations with enterprise-grade
features including atomic transactions, progress tracking, error recovery, and
concurrent operation management.

Components:
- FileOperationManager: Central coordination of all file operations
- OperationWorkers: Asynchronous background workers with queue management
- ProgressTracking: Real-time progress monitoring with cancellation support
- ErrorRecovery: Operation rollback and conflict resolution
"""

from .error_recovery import (
    ConflictResolver,
    ErrorRecoveryManager,
    RecoveryStrategy,
    TransactionManager,
)
from .file_operations import (
    FileOperation,
    FileOperationError,
    FileOperationManager,
    FileOperationResult,
    OperationStatus,
    OperationType,
)
from .operation_workers import (
    CopyWorker,
    DeleteWorker,
    FileOperationWorker,
    MoveWorker,
    OperationQueue,
    RenameWorker,
)
from .progress_tracking import (
    OperationProgress,
    ProgressCallback,
    ProgressEvent,
    ProgressTracker,
)

__all__ = [
    # Core operations
    "FileOperationManager",
    "FileOperation",
    "OperationType",
    "OperationStatus",
    "FileOperationError",
    "FileOperationResult",
    # Workers
    "FileOperationWorker",
    "CopyWorker",
    "MoveWorker",
    "DeleteWorker",
    "RenameWorker",
    "OperationQueue",
    # Progress tracking
    "ProgressTracker",
    "OperationProgress",
    "ProgressCallback",
    "ProgressEvent",
    # Error recovery
    "ErrorRecoveryManager",
    "RecoveryStrategy",
    "ConflictResolver",
    "TransactionManager",
]

# Version information
__version__ = "2.0.0"
__author__ = "Richard Noragon"
__maintainer__ = "RFU Development Team"
