"""
Base class for all system cleanup tools.

This module provides the foundation for all system cleanup tools,
including common functionality, error handling, and progress tracking.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from .safety_manager import SafetyManager
from .windows_utils import WindowsUtils


class CleanupOperationResult:
    """Result of a cleanup operation."""

    def __init__(
        self,
        success: bool,
        message: str,
        items_processed: int = 0,
        space_freed: int = 0,
        errors: Optional[List[str]] = None,
    ):
        self.success = success
        self.message = message
        self.items_processed = items_processed
        self.space_freed = space_freed  # in bytes
        self.errors = errors or []

    def __str__(self):
        return (
            f"CleanupOperationResult(success={self.success}, "
            f"message='{self.message}', items={self.items_processed}, "
            f"space_freed={self.space_freed})"
        )


class CleanupToolBase(QObject):
    """Base class for all system cleanup tools."""

    # Signals for GUI communication
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    operation_complete = pyqtSignal(object)  # CleanupOperationResult
    error_occurred = pyqtSignal(str)  # error message
    status_changed = pyqtSignal(str)  # status message

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.safety_manager = SafetyManager()
        self._is_running = False
        self._should_stop = False

    def get_description(self) -> str:
        """Get a description of what this tool does."""
        raise NotImplementedError("Subclasses must implement get_description")

    def requires_admin(self) -> bool:
        """Check if this tool requires administrator privileges."""
        raise NotImplementedError("Subclasses must implement requires_admin")

    def is_supported(self) -> bool:
        """Check if this tool is supported on the current system."""
        raise NotImplementedError("Subclasses must implement is_supported")

    def estimate_cleanup_size(self, **kwargs) -> int:
        """Estimate the amount of space that can be freed (in bytes)."""
        raise NotImplementedError("Subclasses must implement estimate_cleanup_size")

    def preview_operation(self, **kwargs) -> Dict[str, Any]:
        """Preview what the operation will do without executing it."""
        raise NotImplementedError("Subclasses must implement preview_operation")

    def execute_operation(self, **kwargs) -> CleanupOperationResult:
        """Execute the cleanup operation."""
        raise NotImplementedError("Subclasses must implement execute_operation")

    def is_running(self) -> bool:
        """Check if the tool is currently running."""
        return self._is_running

    def stop_operation(self) -> None:
        """Request to stop the current operation."""
        self._should_stop = True
        self.status_changed.emit("Stopping operation...")

    def _check_should_stop(self) -> bool:
        """Check if operation should be stopped."""
        return self._should_stop

    def _emit_progress(self, current: int, total: int, message: str) -> None:
        """Emit progress update signal."""
        self.progress_updated.emit(current, total, message)

    def _emit_status(self, message: str) -> None:
        """Emit status change signal."""
        self.status_changed.emit(message)

    def _emit_error(self, message: str) -> None:
        """Emit error signal."""
        self.error_occurred.emit(message)

    def _emit_complete(self, result: CleanupOperationResult) -> None:
        """Emit operation complete signal."""
        self.operation_complete.emit(result)

    def _validate_admin_privileges(self) -> bool:
        """Validate administrator privileges if required."""
        if self.requires_admin() and not WindowsUtils.is_admin():
            self._emit_error(
                f"{self.name} requires administrator privileges. "
                "Please run as administrator."
            )
            return False
        return True

    def _validate_windows_system(self) -> bool:
        """Validate that we're running on Windows."""
        if not WindowsUtils.is_windows():
            self._emit_error(f"{self.name} is only supported on Windows systems.")
            return False
        return True

    def _safe_delete_file(self, file_path: Path, secure: bool = False) -> bool:
        """Safely delete a file with optional secure deletion."""
        try:
            if not file_path.exists():
                return True

            # Check if file is in use
            if WindowsUtils.is_file_in_use(file_path):
                self._emit_error(f"File is in use: {file_path}")
                return False

            return WindowsUtils.safe_delete_file(file_path, secure)

        except Exception as e:
            self._emit_error(f"Failed to delete {file_path}: {str(e)}")
            return False

    def _safe_delete_directory(self, dir_path: Path, secure: bool = False) -> bool:
        """Safely delete a directory and its contents."""
        try:
            if not dir_path.exists():
                return True

            return WindowsUtils.safe_delete_directory(dir_path, secure)

        except Exception as e:
            self._emit_error(f"Failed to delete directory {dir_path}: {str(e)}")
            return False

    def _backup_file(
        self, file_path: Path, backup_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Create a backup of a file before deletion."""
        try:
            return self.safety_manager.backup_file(file_path, backup_dir)
        except Exception as e:
            self._emit_error(f"Failed to backup {file_path}: {str(e)}")
            return None

    def _create_restore_point(self, description: str) -> bool:
        """Create a system restore point."""
        try:
            return self.safety_manager.create_restore_point(description)
        except Exception as e:
            self._emit_error(f"Failed to create restore point: {str(e)}")
            return False

    def _get_directory_size(self, directory: Path) -> int:
        """Get the total size of a directory in bytes."""
        try:
            return WindowsUtils.get_file_size(directory)
        except Exception:
            return 0

    def _get_file_age_days(self, file_path: Path) -> int:
        """Get the age of a file in days."""
        try:
            import time

            file_time = file_path.stat().st_mtime
            current_time = time.time()
            age_seconds = current_time - file_time
            return int(age_seconds / (24 * 3600))
        except Exception:
            return 0

    def _filter_files_by_age(self, files: List[Path], max_age_days: int) -> List[Path]:
        """Filter files by maximum age in days."""
        if max_age_days <= 0:
            return files

        filtered = []
        for file_path in files:
            if self._get_file_age_days(file_path) >= max_age_days:
                filtered.append(file_path)

        return filtered

    def _filter_files_by_size(
        self, files: List[Path], min_size_bytes: int
    ) -> List[Path]:
        """Filter files by minimum size in bytes."""
        if min_size_bytes <= 0:
            return files

        filtered = []
        for file_path in files:
            try:
                if file_path.stat().st_size >= min_size_bytes:
                    filtered.append(file_path)
            except Exception:
                continue

        return filtered

    def _filter_files_by_extension(
        self, files: List[Path], extensions: List[str]
    ) -> List[Path]:
        """Filter files by file extensions."""
        if not extensions:
            return files

        # Normalize extensions (add dot if missing)
        normalized_exts = []
        for ext in extensions:
            if not ext.startswith("."):
                ext = "." + ext
            normalized_exts.append(ext.lower())

        filtered = []
        for file_path in files:
            if file_path.suffix.lower() in normalized_exts:
                filtered.append(file_path)

        return filtered

    def _scan_directory(
        self, directory: Path, recursive: bool = True, file_pattern: str = "*"
    ) -> List[Path]:
        """Scan a directory for files matching a pattern."""
        files = []

        try:
            if not directory.exists():
                return files

            if recursive:
                files = list(directory.rglob(file_pattern))
            else:
                files = list(directory.glob(file_pattern))

            # Filter to only include files (not directories)
            files = [f for f in files if f.is_file()]

        except Exception as e:
            self._emit_error(f"Error scanning directory {directory}: {str(e)}")

        return files

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _validate_operation_parameters(self, **kwargs) -> bool:
        """Validate operation parameters. Override in subclasses."""
        return True

    def run_operation_safely(self, operation_func, **kwargs):
        """Run an operation with comprehensive error handling."""
        self._is_running = True
        self._should_stop = False

        try:
            # Validate system requirements
            if not self._validate_windows_system():
                return CleanupOperationResult(
                    False,
                    "Windows system required",
                    0,
                    0,
                    ["Not running on Windows"],
                )

            if not self._validate_admin_privileges():
                return CleanupOperationResult(
                    False,
                    "Administrator privileges required",
                    0,
                    0,
                    ["Insufficient privileges"],
                )

            if not self._validate_operation_parameters(**kwargs):
                return CleanupOperationResult(
                    False,
                    "Invalid operation parameters",
                    0,
                    0,
                    ["Parameter validation failed"],
                )

            # Execute the operation
            result = operation_func(**kwargs)
            self._emit_complete(result)
            return result

        except Exception as e:
            error_result = CleanupOperationResult(
                False, f"Operation failed: {str(e)}", 0, 0, [str(e)]
            )
            self._emit_complete(error_result)
            return error_result

        finally:
            self._is_running = False
