"""
Error Recovery and Transaction Management for RFU Multi-Pane File Explorer

This module provides comprehensive error recovery, conflict resolution, and
transaction management for file operations with rollback capabilities.

Author: Richard Noragon
Version: 2.0.0
"""

import json
import logging
import shutil
import tempfile
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt5.QtCore import QObject, pyqtSignal

from .file_operations import (
    FileOperation,
    FileOperationError,
    FileOperationResult,
    OperationStatus,
    OperationType,
)


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""

    RETRY = auto()
    SKIP = auto()
    ROLLBACK = auto()
    USER_INTERVENTION = auto()
    ALTERNATIVE_PATH = auto()
    PERMISSION_ELEVATION = auto()
    CLEANUP_AND_RETRY = auto()


class ConflictResolution(Enum):
    """Conflict resolution strategies."""

    OVERWRITE = auto()
    SKIP = auto()
    RENAME = auto()
    MERGE = auto()
    ASK_USER = auto()
    BACKUP_AND_OVERWRITE = auto()


@dataclass
class TransactionEntry:
    """Single transaction entry for rollback support."""

    operation_type: str
    source_path: str
    destination_path: Optional[str] = None
    backup_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    reversible: bool = True


@dataclass
class ErrorContext:
    """Comprehensive error context for recovery decisions."""

    operation_id: str
    error_type: str
    error_message: str
    file_path: str
    error_code: Optional[int] = None
    system_info: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    suggested_strategy: Optional[RecoveryStrategy] = None
    user_action_required: bool = False


class ErrorRecoveryManager(QObject):
    """
    Comprehensive error recovery and transaction management system.

    Features:
    - Automatic error classification and recovery
    - Transaction logging with rollback support
    - Conflict resolution strategies
    - User intervention coordination
    - System state restoration
    - Retry logic with exponential backoff
    """

    # Signals for UI integration
    recovery_needed = pyqtSignal(str, dict)  # operation_id, error_context
    recovery_completed = pyqtSignal(
        str, bool, str
    )  # operation_id, success, message
    user_intervention_required = pyqtSignal(str, dict)  # operation_id, context
    rollback_started = pyqtSignal(str)  # operation_id
    rollback_completed = pyqtSignal(str, bool)  # operation_id, success

    def __init__(self):
        """Initialize the error recovery manager."""
        super().__init__()

        # Recovery state management
        self.active_recoveries: Dict[str, ErrorContext] = {}
        self.recovery_history: List[ErrorContext] = []
        self.recovery_lock = threading.RLock()

        # Transaction management
        self.transaction_manager = TransactionManager()

        # Conflict resolution
        self.conflict_resolver = ConflictResolver()

        # Setup logging
        self.logger = logging.getLogger("RFU.ErrorRecovery")

        # Error classification patterns
        self.error_patterns = self._initialize_error_patterns()

        self.logger.info("ErrorRecoveryManager initialized")

    def _initialize_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error classification patterns."""
        return {
            "permission_denied": {
                "keywords": ["permission", "access", "denied", "forbidden"],
                "strategy": RecoveryStrategy.PERMISSION_ELEVATION,
                "retry_delay": 1.0,
                "max_retries": 2,
            },
            "file_not_found": {
                "keywords": ["not found", "no such file", "cannot find"],
                "strategy": RecoveryStrategy.SKIP,
                "retry_delay": 0.0,
                "max_retries": 0,
            },
            "disk_full": {
                "keywords": ["disk full", "no space", "insufficient space"],
                "strategy": RecoveryStrategy.ALTERNATIVE_PATH,
                "retry_delay": 5.0,
                "max_retries": 1,
            },
            "file_locked": {
                "keywords": ["locked", "in use", "sharing violation"],
                "strategy": RecoveryStrategy.RETRY,
                "retry_delay": 2.0,
                "max_retries": 5,
            },
            "network_error": {
                "keywords": [
                    "network",
                    "unreachable",
                    "timeout",
                    "connection",
                ],
                "strategy": RecoveryStrategy.RETRY,
                "retry_delay": 10.0,
                "max_retries": 3,
            },
            "file_exists": {
                "keywords": ["already exists", "file exists"],
                "strategy": RecoveryStrategy.USER_INTERVENTION,
                "retry_delay": 0.0,
                "max_retries": 0,
            },
        }

    def handle_error(
        self, operation: FileOperation, error: FileOperationError
    ) -> RecoveryStrategy:
        """
        Handle an operation error with automatic recovery.

        Args:
            operation: Failed operation
            error: Error information

        Returns:
            RecoveryStrategy: Strategy to apply
        """
        with self.recovery_lock:
            # Create error context
            context = self._create_error_context(operation, error)

            # Classify error and determine strategy
            strategy = self._classify_error(error)
            context.suggested_strategy = strategy

            # Store active recovery
            self.active_recoveries[operation.operation_id] = context

            self.logger.info(
                f"Handling error for {operation.operation_id}: "
                f"{error} -> {strategy}"
            )

            # Emit signal for UI notification
            self.recovery_needed.emit(
                operation.operation_id,
                {
                    "error_type": context.error_type,
                    "error_message": context.error_message,
                    "file_path": context.file_path,
                    "strategy": strategy.name,
                    "retry_count": context.retry_count,
                    "max_retries": context.max_retries,
                },
            )

            # Execute recovery strategy
            return self._execute_recovery_strategy(
                operation, context, strategy
            )

    def _create_error_context(
        self, operation: FileOperation, error: FileOperationError
    ) -> ErrorContext:
        """Create comprehensive error context."""
        import psutil

        # Get system information
        system_info = {
            "disk_usage": {},
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent(),
            "available_space": {},
        }

        # Get disk usage for relevant paths
        paths_to_check = []
        if operation.source_paths:
            paths_to_check.extend(operation.source_paths)
        if operation.destination_path:
            paths_to_check.append(operation.destination_path)

        for path_str in paths_to_check:
            try:
                path = Path(path_str)
                if path.exists():
                    drive = path.anchor
                    if drive not in system_info["available_space"]:
                        usage = shutil.disk_usage(drive)
                        system_info["available_space"][drive] = {
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                        }
            except Exception:
                pass

        return ErrorContext(
            operation_id=operation.operation_id,
            error_type=type(error).__name__,
            error_message=str(error),
            file_path=getattr(error, "file_path", ""),
            error_code=getattr(error, "error_code", None),
            system_info=system_info,
        )

    def _classify_error(self, error: FileOperationError) -> RecoveryStrategy:
        """
        Classify error and determine appropriate recovery strategy.

        Args:
            error: Error to classify

        Returns:
            RecoveryStrategy: Recommended strategy
        """
        error_message = str(error).lower()

        # Check against known patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            keywords = pattern_info["keywords"]
            if any(keyword in error_message for keyword in keywords):
                self.logger.debug(f"Error classified as: {pattern_name}")
                return pattern_info["strategy"]

        # Default strategy for unknown errors
        if getattr(error, "recoverable", True):
            return RecoveryStrategy.RETRY
        else:
            return RecoveryStrategy.ROLLBACK

    def _execute_recovery_strategy(
        self,
        operation: FileOperation,
        context: ErrorContext,
        strategy: RecoveryStrategy,
    ) -> RecoveryStrategy:
        """
        Execute the determined recovery strategy.

        Args:
            operation: Failed operation
            context: Error context
            strategy: Strategy to execute

        Returns:
            RecoveryStrategy: Actual strategy executed
        """
        try:
            if strategy == RecoveryStrategy.RETRY:
                return self._execute_retry_strategy(operation, context)
            elif strategy == RecoveryStrategy.SKIP:
                return self._execute_skip_strategy(operation, context)
            elif strategy == RecoveryStrategy.ROLLBACK:
                return self._execute_rollback_strategy(operation, context)
            elif strategy == RecoveryStrategy.USER_INTERVENTION:
                return self._execute_user_intervention_strategy(
                    operation, context
                )
            elif strategy == RecoveryStrategy.ALTERNATIVE_PATH:
                return self._execute_alternative_path_strategy(
                    operation, context
                )
            elif strategy == RecoveryStrategy.PERMISSION_ELEVATION:
                return self._execute_permission_elevation_strategy(
                    operation, context
                )
            elif strategy == RecoveryStrategy.CLEANUP_AND_RETRY:
                return self._execute_cleanup_retry_strategy(operation, context)
            else:
                self.logger.warning(f"Unknown recovery strategy: {strategy}")
                return RecoveryStrategy.ROLLBACK

        except Exception as e:
            self.logger.error(f"Recovery strategy execution failed: {e}")
            return RecoveryStrategy.ROLLBACK

    def _execute_retry_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute retry recovery strategy with exponential backoff."""
        if context.retry_count >= context.max_retries:
            self.logger.info(
                f"Max retries exceeded for {operation.operation_id}"
            )
            return RecoveryStrategy.ROLLBACK

        # Calculate retry delay with exponential backoff
        base_delay = self.error_patterns.get(
            context.error_type.lower(), {}
        ).get("retry_delay", 1.0)

        delay = base_delay * (2**context.retry_count)

        self.logger.info(
            f"Retrying operation {operation.operation_id} "
            f"in {delay} seconds (attempt {context.retry_count + 1})"
        )

        # Schedule retry (this would be handled by the operation manager)
        context.retry_count += 1

        return RecoveryStrategy.RETRY

    def _execute_skip_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute skip recovery strategy."""
        self.logger.info(
            f"Skipping failed item in operation {operation.operation_id}"
        )

        # Mark context as resolved
        context.user_action_required = False

        # Move to history
        self.recovery_history.append(context)
        if operation.operation_id in self.active_recoveries:
            del self.active_recoveries[operation.operation_id]

        self.recovery_completed.emit(
            operation.operation_id, True, "Item skipped"
        )

        return RecoveryStrategy.SKIP

    def _execute_rollback_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute rollback recovery strategy."""
        self.logger.info(f"Rolling back operation {operation.operation_id}")

        self.rollback_started.emit(operation.operation_id)

        try:
            # Use transaction manager to rollback
            success = self.transaction_manager.rollback_operation(
                operation.operation_id
            )

            if success:
                self.logger.info(
                    f"Rollback successful for {operation.operation_id}"
                )
                self.rollback_completed.emit(operation.operation_id, True)
                self.recovery_completed.emit(
                    operation.operation_id,
                    True,
                    "Operation rolled back successfully",
                )
            else:
                self.logger.error(
                    f"Rollback failed for {operation.operation_id}"
                )
                self.rollback_completed.emit(operation.operation_id, False)
                self.recovery_completed.emit(
                    operation.operation_id, False, "Rollback failed"
                )

            # Clean up
            self.recovery_history.append(context)
            if operation.operation_id in self.active_recoveries:
                del self.active_recoveries[operation.operation_id]

            return RecoveryStrategy.ROLLBACK

        except Exception as e:
            self.logger.error(f"Rollback execution failed: {e}")
            self.rollback_completed.emit(operation.operation_id, False)
            return RecoveryStrategy.ROLLBACK

    def _execute_user_intervention_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute user intervention recovery strategy."""
        self.logger.info(
            f"Requesting user intervention for {operation.operation_id}"
        )

        context.user_action_required = True

        # Emit signal for UI to handle user interaction
        self.user_intervention_required.emit(
            operation.operation_id,
            {
                "error_message": context.error_message,
                "file_path": context.file_path,
                "operation_type": operation.operation_type.name,
                "possible_actions": self._get_possible_user_actions(context),
            },
        )

        return RecoveryStrategy.USER_INTERVENTION

    def _execute_alternative_path_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute alternative path recovery strategy."""
        self.logger.info(
            f"Seeking alternative path for {operation.operation_id}"
        )

        # Try to find alternative destination
        if operation.destination_path:
            alternative = self._find_alternative_destination(
                operation.destination_path
            )
            if alternative:
                operation.destination_path = alternative
                self.logger.info(f"Alternative path found: {alternative}")
                return RecoveryStrategy.RETRY

        # If no alternative found, request user intervention
        return self._execute_user_intervention_strategy(operation, context)

    def _execute_permission_elevation_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute permission elevation recovery strategy."""
        self.logger.info(
            f"Attempting permission elevation for {operation.operation_id}"
        )

        # This would typically involve:
        # 1. Requesting administrator privileges
        # 2. Retrying the operation with elevated permissions
        # 3. Falling back to user intervention if elevation fails

        # For now, request user intervention
        return self._execute_user_intervention_strategy(operation, context)

    def _execute_cleanup_retry_strategy(
        self, operation: FileOperation, context: ErrorContext
    ) -> RecoveryStrategy:
        """Execute cleanup and retry recovery strategy."""
        self.logger.info(
            f"Cleaning up and retrying for {operation.operation_id}"
        )

        try:
            # Attempt cleanup operations
            self._cleanup_partial_files(operation)

            # Retry the operation
            return self._execute_retry_strategy(operation, context)

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return RecoveryStrategy.ROLLBACK

    def _get_possible_user_actions(self, context: ErrorContext) -> List[str]:
        """Get list of possible user actions for error context."""
        actions = ["retry", "skip", "cancel"]

        if "exists" in context.error_message.lower():
            actions.extend(["overwrite", "rename", "merge"])

        if "permission" in context.error_message.lower():
            actions.append("elevate_permissions")

        if "space" in context.error_message.lower():
            actions.extend(["cleanup_disk", "choose_different_location"])

        return actions

    def _find_alternative_destination(
        self, original_path: str
    ) -> Optional[str]:
        """Find alternative destination path for disk space issues."""
        original = Path(original_path)

        # Try common alternative locations
        alternatives = [
            Path.home() / "Desktop" / original.name,
            Path.home() / "Documents" / original.name,
            Path(tempfile.gettempdir()) / original.name,
        ]

        for alt in alternatives:
            try:
                if alt.parent.exists():
                    # Check available space
                    usage = shutil.disk_usage(alt.parent)
                    if usage.free > 1024 * 1024 * 100:  # At least 100MB free
                        return str(alt)
            except Exception:
                continue

        return None

    def _cleanup_partial_files(self, operation: FileOperation) -> None:
        """Clean up partially created files from failed operation."""
        # This would implement cleanup logic based on the operation type
        # and transaction log entries
        pass

    def handle_user_response(
        self,
        operation_id: str,
        action: str,
        additional_data: Dict[str, Any] = None,
    ) -> bool:
        """
        Handle user response to intervention request.

        Args:
            operation_id: Operation requiring intervention
            action: User-selected action
            additional_data: Additional data for the action

        Returns:
            bool: True if response handled successfully
        """
        with self.recovery_lock:
            if operation_id not in self.active_recoveries:
                return False

            context = self.active_recoveries[operation_id]

            self.logger.info(f"User response for {operation_id}: {action}")

            try:
                if action == "retry":
                    context.retry_count = 0  # Reset retry count
                    return True
                elif action == "skip":
                    self.recovery_completed.emit(
                        operation_id, True, "Skipped by user"
                    )
                    return True
                elif action == "cancel":
                    self.recovery_completed.emit(
                        operation_id, False, "Cancelled by user"
                    )
                    return True
                elif action == "overwrite":
                    # Handle overwrite logic
                    return self._handle_overwrite_action(
                        operation_id, additional_data
                    )
                elif action == "rename":
                    # Handle rename logic
                    return self._handle_rename_action(
                        operation_id, additional_data
                    )
                else:
                    self.logger.warning(f"Unknown user action: {action}")
                    return False

            finally:
                # Clean up if action was final
                if action in ["skip", "cancel"]:
                    self.recovery_history.append(context)
                    del self.active_recoveries[operation_id]

    def _handle_overwrite_action(
        self, operation_id: str, additional_data: Dict[str, Any]
    ) -> bool:
        """Handle user's overwrite action."""
        # Implementation for overwrite logic
        self.logger.info(f"Handling overwrite for {operation_id}")
        return True

    def _handle_rename_action(
        self, operation_id: str, additional_data: Dict[str, Any]
    ) -> bool:
        """Handle user's rename action."""
        # Implementation for rename logic
        new_name = additional_data.get("new_name") if additional_data else None
        if new_name:
            self.logger.info(f"Handling rename for {operation_id}: {new_name}")
            return True
        return False


class ConflictResolver:
    """Handles file conflicts during operations."""

    def __init__(self):
        """Initialize conflict resolver."""
        self.logger = logging.getLogger("RFU.ConflictResolver")

    def resolve_conflict(
        self, source_path: str, dest_path: str, strategy: ConflictResolution
    ) -> Tuple[bool, str]:
        """
        Resolve file conflict using specified strategy.

        Args:
            source_path: Source file path
            dest_path: Destination file path
            strategy: Resolution strategy

        Returns:
            Tuple of (success, new_dest_path)
        """
        if strategy == ConflictResolution.OVERWRITE:
            return True, dest_path
        elif strategy == ConflictResolution.SKIP:
            return False, dest_path
        elif strategy == ConflictResolution.RENAME:
            new_path = self._generate_unique_name(dest_path)
            return True, new_path
        elif strategy == ConflictResolution.BACKUP_AND_OVERWRITE:
            backup_path = self._create_backup(dest_path)
            if backup_path:
                return True, dest_path
            return False, dest_path
        else:
            return False, dest_path

    def _generate_unique_name(self, path: str) -> str:
        """Generate unique filename to avoid conflicts."""
        path_obj = Path(path)
        counter = 1

        while path_obj.exists():
            stem = path_obj.stem
            suffix = path_obj.suffix
            new_name = f"{stem}_{counter}{suffix}"
            path_obj = path_obj.parent / new_name
            counter += 1

        return str(path_obj)

    def _create_backup(self, path: str) -> Optional[str]:
        """Create backup of existing file."""
        try:
            path_obj = Path(path)
            backup_name = (
                f"{path_obj.stem}_backup_{int(time.time())}{path_obj.suffix}"
            )
            backup_path = path_obj.parent / backup_name

            shutil.copy2(str(path_obj), str(backup_path))
            self.logger.info(f"Backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None


class TransactionManager:
    """Manages file operation transactions with rollback support."""

    def __init__(self):
        """Initialize transaction manager."""
        self.transactions: Dict[str, List[TransactionEntry]] = {}
        self.transaction_lock = threading.RLock()
        self.logger = logging.getLogger("RFU.TransactionManager")

    def start_transaction(self, operation_id: str) -> None:
        """Start a new transaction."""
        with self.transaction_lock:
            self.transactions[operation_id] = []
            self.logger.debug(f"Transaction started: {operation_id}")

    def add_entry(self, operation_id: str, entry: TransactionEntry) -> None:
        """Add entry to transaction log."""
        with self.transaction_lock:
            if operation_id not in self.transactions:
                self.transactions[operation_id] = []
            self.transactions[operation_id].append(entry)
            self.logger.debug(f"Transaction entry added: {operation_id}")

    def commit_transaction(self, operation_id: str) -> None:
        """Commit transaction (remove from active transactions)."""
        with self.transaction_lock:
            if operation_id in self.transactions:
                del self.transactions[operation_id]
                self.logger.debug(f"Transaction committed: {operation_id}")

    def rollback_operation(self, operation_id: str) -> bool:
        """
        Rollback all operations in transaction.

        Args:
            operation_id: Transaction to rollback

        Returns:
            bool: True if rollback successful
        """
        with self.transaction_lock:
            if operation_id not in self.transactions:
                return True  # Nothing to rollback

            entries = self.transactions[operation_id]
            success = True

            # Process entries in reverse order
            for entry in reversed(entries):
                try:
                    if not self._rollback_entry(entry):
                        success = False
                except Exception as e:
                    self.logger.error(f"Rollback entry failed: {e}")
                    success = False

            # Clean up transaction
            del self.transactions[operation_id]

            self.logger.info(
                f"Transaction rollback: {operation_id} " f"(success={success})"
            )
            return success

    def _rollback_entry(self, entry: TransactionEntry) -> bool:
        """Rollback a single transaction entry."""
        if not entry.reversible:
            return True  # Can't rollback, but not an error

        try:
            if entry.operation_type == "copy":
                # Remove copied file
                if (
                    entry.destination_path
                    and Path(entry.destination_path).exists()
                ):
                    Path(entry.destination_path).unlink()
                    return True
            elif entry.operation_type == "move":
                # Move file back to original location
                if (
                    entry.destination_path
                    and entry.source_path
                    and Path(entry.destination_path).exists()
                ):
                    Path(entry.destination_path).rename(entry.source_path)
                    return True
            elif entry.operation_type == "delete":
                # Restore from backup if available
                if (
                    entry.backup_path
                    and entry.source_path
                    and Path(entry.backup_path).exists()
                ):
                    shutil.copy2(entry.backup_path, entry.source_path)
                    return True
            elif entry.operation_type == "rename":
                # Rename back to original
                if (
                    entry.destination_path
                    and entry.source_path
                    and Path(entry.destination_path).exists()
                ):
                    Path(entry.destination_path).rename(entry.source_path)
                    return True

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to rollback entry {entry.operation_type}: {e}"
            )
            return False
