"""
Secure Delete Logging Module

This module provides comprehensive logging capabilities for secure delete
operations with hub integration and structured logging support.

Migrated from: secure_delete.py logging functionality
Target: file_utilities_2 package integration
"""

import os
import logging
import logging.handlers
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json


class SecureDeleteLogger:
    """
    Enhanced logging system for secure delete operations.

    Provides structured logging with hub integration, file rotation,
    and comprehensive audit trail capabilities.
    """

    def __init__(
        self, name: str = "SecureDelete", log_dir: Optional[str] = None
    ):
        """
        Initialize the secure delete logger.

        Args:
            name: Logger name
            log_dir: Custom log directory path
        """
        self.name = name
        self.log_dir = (
            Path(log_dir) if log_dir else self._get_default_log_dir()
        )
        self.log_file = self.log_dir / f"{name.lower()}.log"
        self.audit_file = self.log_dir / f"{name.lower()}_audit.jsonl"

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logger
        self.logger = logging.getLogger(name)
        self._setup_logger()

        # Audit trail for secure operations
        self.audit_enabled = True

    def _get_default_log_dir(self) -> Path:
        """Get default log directory."""
        if os.name == "nt":  # Windows
            log_base = Path(
                os.environ.get(
                    "LOCALAPPDATA", Path.home() / "AppData" / "Local"
                )
            )
        else:  # Unix-like systems
            log_base = (
                Path("/var/log")
                if os.access("/var/log", os.W_OK)
                else Path.home() / ".local" / "share"
            )

        return log_base / "file_utilities_2" / "logs"

    def _setup_logger(self):
        """Setup logger with file rotation and formatting."""
        # Clear existing handlers
        self.logger.handlers.clear()

        # Set log level
        self.logger.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Logger initialized: {self.name}")

    def log_operation_start(
        self, filepath: str, passes: int, file_size: int
    ) -> str:
        """
        Log the start of a secure delete operation.

        Args:
            filepath: Path of file being deleted
            passes: Number of overwrite passes
            file_size: Size of file in bytes

        Returns:
            Operation ID for tracking
        """
        operation_id = self._generate_operation_id()

        log_data = {
            "operation_id": operation_id,
            "event_type": "operation_start",
            "filepath": filepath,
            "passes": passes,
            "file_size": file_size,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            f"Starting secure deletion: {filepath} "
            f"({file_size:,} bytes, {passes} passes) [ID: {operation_id}]"
        )

        if self.audit_enabled:
            self._write_audit_log(log_data)

        return operation_id

    def log_operation_progress(
        self,
        operation_id: str,
        current_pass: int,
        total_passes: int,
        bytes_processed: int,
        total_bytes: int,
    ):
        """
        Log progress of secure delete operation.

        Args:
            operation_id: Operation tracking ID
            current_pass: Current overwrite pass
            total_passes: Total overwrite passes
            bytes_processed: Bytes processed so far
            total_bytes: Total bytes to process
        """
        percentage = (
            (bytes_processed / total_bytes * 100) if total_bytes > 0 else 0
        )

        log_data = {
            "operation_id": operation_id,
            "event_type": "operation_progress",
            "current_pass": current_pass,
            "total_passes": total_passes,
            "bytes_processed": bytes_processed,
            "total_bytes": total_bytes,
            "percentage": round(percentage, 2),
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.debug(
            f"Progress [ID: {operation_id}]: Pass {current_pass}/{total_passes}, "
            f"{bytes_processed:,}/{total_bytes:,} bytes ({percentage:.1f}%)"
        )

        if self.audit_enabled:
            self._write_audit_log(log_data)

    def log_operation_complete(
        self,
        operation_id: str,
        filepath: str,
        duration: float,
        passes_completed: int,
    ):
        """
        Log successful completion of secure delete operation.

        Args:
            operation_id: Operation tracking ID
            filepath: Path of deleted file
            duration: Operation duration in seconds
            passes_completed: Number of passes completed
        """
        log_data = {
            "operation_id": operation_id,
            "event_type": "operation_complete",
            "filepath": filepath,
            "duration": duration,
            "passes_completed": passes_completed,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            f"Secure deletion completed: {filepath} "
            f"({passes_completed} passes, {duration:.2f}s) [ID: {operation_id}]"
        )

        if self.audit_enabled:
            self._write_audit_log(log_data)

    def log_operation_error(
        self,
        operation_id: str,
        filepath: str,
        error_message: str,
        error_details: Dict[str, Any],
    ):
        """
        Log error during secure delete operation.

        Args:
            operation_id: Operation tracking ID
            filepath: Path of file being deleted
            error_message: Error message
            error_details: Additional error details
        """
        log_data = {
            "operation_id": operation_id,
            "event_type": "operation_error",
            "filepath": filepath,
            "error_message": error_message,
            "error_details": error_details,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.error(
            f"Secure deletion failed: {filepath} - {error_message} "
            f"[ID: {operation_id}]"
        )

        if self.audit_enabled:
            self._write_audit_log(log_data)

    def log_hub_event(
        self, event_type: str, message: str, details: Dict[str, Any]
    ):
        """
        Log hub integration events.

        Args:
            event_type: Type of hub event
            message: Event message
            details: Event details
        """
        log_data = {
            "event_type": f"hub_{event_type}",
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(f"Hub event [{event_type}]: {message}")

        if self.audit_enabled:
            self._write_audit_log(log_data)

    def log_security_event(
        self, event_type: str, filepath: str, details: Dict[str, Any]
    ):
        """
        Log security-related events.

        Args:
            event_type: Type of security event
            filepath: File path involved
            details: Event details
        """
        log_data = {
            "event_type": f"security_{event_type}",
            "filepath": filepath,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.warning(f"Security event [{event_type}]: {filepath}")

        if self.audit_enabled:
            self._write_audit_log(log_data)

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import uuid

        short_uuid = str(uuid.uuid4())[:8]
        return f"SD_{timestamp}_{short_uuid}"

    def _write_audit_log(self, log_data: Dict[str, Any]):
        """
        Write structured audit log entry.

        Args:
            log_data: Log data to write
        """
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")

    def get_operation_logs(self, operation_id: str) -> list:
        """
        Get all log entries for a specific operation.

        Args:
            operation_id: Operation tracking ID

        Returns:
            List of log entries for the operation
        """
        logs = []
        try:
            if self.audit_file.exists():
                with open(self.audit_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            if log_entry.get("operation_id") == operation_id:
                                logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"Failed to read operation logs: {e}")

        return logs

    def get_recent_operations(self, limit: int = 50) -> list:
        """
        Get recent secure delete operations.

        Args:
            limit: Maximum number of operations to return

        Returns:
            List of recent operations
        """
        operations = []
        try:
            if self.audit_file.exists():
                with open(self.audit_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Process lines in reverse order (most recent first)
                for line in reversed(
                    lines[-limit * 10 :]
                ):  # Read more to filter
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get("event_type") == "operation_start":
                            operations.append(log_entry)
                            if len(operations) >= limit:
                                break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Failed to read recent operations: {e}")

        return operations

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files.

        Args:
            days_to_keep: Number of days of logs to keep
        """
        try:
            cutoff_time = datetime.now().timestamp() - (
                days_to_keep * 24 * 3600
            )

            # Clean up rotated log files
            for log_file in self.log_dir.glob(f"{self.name.lower()}.log.*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.logger.info(f"Cleaned up old log file: {log_file}")

            # Clean up old audit entries (keep file, remove old entries)
            if self.audit_file.exists():
                self._cleanup_audit_file(cutoff_time)

        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")

    def _cleanup_audit_file(self, cutoff_time: float):
        """Clean up old entries from audit file."""
        try:
            temp_file = self.audit_file.with_suffix(".tmp")
            entries_kept = 0

            with (
                open(self.audit_file, "r", encoding="utf-8") as infile,
                open(temp_file, "w", encoding="utf-8") as outfile,
            ):

                for line in infile:
                    try:
                        log_entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(
                            log_entry["timestamp"]
                        ).timestamp()

                        if entry_time >= cutoff_time:
                            outfile.write(line)
                            entries_kept += 1
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Keep malformed entries to avoid data loss
                        outfile.write(line)
                        entries_kept += 1

            # Replace original file with cleaned version
            temp_file.replace(self.audit_file)
            self.logger.info(
                f"Cleaned audit file, kept {entries_kept} entries"
            )

        except Exception as e:
            self.logger.error(f"Failed to cleanup audit file: {e}")
            # Remove temp file if it exists
            if temp_file.exists():
                temp_file.unlink()

    def set_log_level(self, level: str):
        """
        Set logging level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            log_level = getattr(logging, level.upper())
            self.logger.setLevel(log_level)
            self.logger.info(f"Log level set to: {level}")
        except AttributeError:
            self.logger.error(f"Invalid log level: {level}")

    def enable_audit(self, enabled: bool = True):
        """
        Enable or disable audit logging.

        Args:
            enabled: Whether to enable audit logging
        """
        self.audit_enabled = enabled
        self.logger.info(
            f"Audit logging {'enabled' if enabled else 'disabled'}"
        )

    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.

        Returns:
            Dictionary containing log statistics
        """
        stats = {
            "log_dir": str(self.log_dir),
            "log_file": str(self.log_file),
            "audit_file": str(self.audit_file),
            "log_file_exists": self.log_file.exists(),
            "audit_file_exists": self.audit_file.exists(),
            "audit_enabled": self.audit_enabled,
        }

        try:
            if self.log_file.exists():
                stats["log_file_size"] = self.log_file.stat().st_size
                stats["log_file_modified"] = datetime.fromtimestamp(
                    self.log_file.stat().st_mtime
                ).isoformat()

            if self.audit_file.exists():
                stats["audit_file_size"] = self.audit_file.stat().st_size
                stats["audit_file_modified"] = datetime.fromtimestamp(
                    self.audit_file.stat().st_mtime
                ).isoformat()

                # Count audit entries
                with open(self.audit_file, "r", encoding="utf-8") as f:
                    stats["audit_entries"] = sum(1 for _ in f)

        except Exception as e:
            stats["error"] = str(e)

        return stats


# Global logger instance
_logger_instance: Optional[SecureDeleteLogger] = None


def get_logger() -> SecureDeleteLogger:
    """
    Get the global logger instance.

    Returns:
        SecureDeleteLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SecureDeleteLogger()
    return _logger_instance


def initialize_logger(
    name: str = "SecureDelete", log_dir: Optional[str] = None
) -> SecureDeleteLogger:
    """
    Initialize the global logger instance.

    Args:
        name: Logger name
        log_dir: Custom log directory

    Returns:
        SecureDeleteLogger instance
    """
    global _logger_instance
    _logger_instance = SecureDeleteLogger(name, log_dir)
    return _logger_instance
