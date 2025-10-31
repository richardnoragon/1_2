"""
Database Logging Handler for Richard's File Utilities

This module provides a logging handler that stores log records
in the SQLite database for persistent logging and analysis.
"""

import logging
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from .database_manager import get_database_manager
    from .database_models import AppLog

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class DatabaseLogHandler(logging.Handler):
    """Custom logging handler that stores logs in SQLite database."""

    def __init__(self, session_id: Optional[str] = None):
        """Initialize the database log handler."""
        super().__init__()
        self.session_id = session_id
        self.db_manager = None

        if DATABASE_AVAILABLE:
            try:
                self.db_manager = get_database_manager()
                self.enabled = True
            except Exception:
                self.enabled = False
        else:
            self.enabled = False

    def emit(self, record: logging.LogRecord):
        """Emit a log record to the database."""
        if not self.enabled or not self.db_manager:
            return

        try:
            # Extract tool name from logger name
            tool_name = None
            if hasattr(record, "tool_name"):
                tool_name = record.tool_name
            elif "." in record.name:
                parts = record.name.split(".")
                if len(parts) > 2:
                    tool_name = parts[2]  # e.g., RFU.Tool.PDF -> PDF

            # Prepare metadata
            metadata = {}

            # Add exception information if present
            if record.exc_info:
                metadata["exception"] = {
                    "type": record.exc_info[0].__name__,
                    "message": str(record.exc_info[1]),
                    "traceback": traceback.format_exception(*record.exc_info),
                }

            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ]:
                    metadata[key] = str(value)

            # Create log entry
            log_entry = AppLog(
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                tool_name=tool_name,
                session_id=self.session_id,
                metadata=metadata if metadata else {},
            )

            # Store in database
            self._store_log_entry(log_entry)

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

    def _store_log_entry(self, log_entry: AppLog):
        """Store log entry in database."""
        try:
            query = """
                INSERT INTO app_logs 
                (timestamp, level, logger_name, message, module, function, 
                 line_number, tool_name, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                (
                    log_entry.timestamp.isoformat()
                    if log_entry.timestamp
                    else None
                ),
                log_entry.level,
                log_entry.logger_name,
                log_entry.message,
                log_entry.module,
                log_entry.function,
                log_entry.line_number,
                log_entry.tool_name,
                log_entry.session_id,
                json.dumps(log_entry.metadata) if log_entry.metadata else None,
            )

            self.db_manager.execute_update(query, params)

        except Exception:
            # Silently fail to avoid infinite recursion
            pass


class DatabaseLogService:
    """Service for querying and managing logs in the database."""

    def __init__(self):
        """Initialize the database log service."""
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = get_database_manager()
                self.enabled = True
            except Exception:
                self.enabled = False
        else:
            self.enabled = False

    def get_logs(
        self,
        level: Optional[str] = None,
        tool_name: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list:
        """Get logs with filtering options."""
        if not self.enabled:
            return []

        try:
            # Build query
            query = "SELECT * FROM app_logs WHERE 1=1"
            params = []

            if level:
                query += " AND level = ?"
                params.append(level)

            if tool_name:
                query += " AND tool_name = ?"
                params.append(tool_name)

            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            results = self.db_manager.execute_query(query, tuple(params))

            # Convert to AppLog objects
            logs = []
            for row in results:
                metadata = {}
                if row["metadata"]:
                    try:
                        metadata = json.loads(row["metadata"])
                    except json.JSONDecodeError:
                        pass

                log = AppLog(
                    id=row["id"],
                    timestamp=(
                        datetime.fromisoformat(row["timestamp"])
                        if row["timestamp"]
                        else None
                    ),
                    level=row["level"],
                    logger_name=row["logger_name"],
                    message=row["message"],
                    module=row["module"],
                    function=row["function"],
                    line_number=row["line_number"],
                    tool_name=row["tool_name"],
                    session_id=row["session_id"],
                    metadata=metadata,
                )
                logs.append(log)

            return logs

        except Exception:
            return []

    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        if not self.enabled:
            return {}

        try:
            stats = {}

            # Total logs
            result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM app_logs"
            )
            stats["total_logs"] = result[0]["count"] if result else 0

            # Logs by level
            result = self.db_manager.execute_query(
                "SELECT level, COUNT(*) as count FROM app_logs GROUP BY level ORDER BY count DESC"
            )
            stats["by_level"] = {row["level"]: row["count"] for row in result}

            # Logs by tool
            result = self.db_manager.execute_query(
                "SELECT tool_name, COUNT(*) as count FROM app_logs WHERE tool_name IS NOT NULL GROUP BY tool_name ORDER BY count DESC LIMIT 10"
            )
            stats["by_tool"] = {
                row["tool_name"]: row["count"] for row in result
            }

            # Recent activity (last 24 hours)
            result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM app_logs WHERE timestamp >= datetime('now', '-1 day')"
            )
            stats["last_24_hours"] = result[0]["count"] if result else 0

            return stats

        except Exception:
            return {}

    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """Clean up logs older than specified days."""
        if not self.enabled:
            return 0

        # Validate retention_days parameter to prevent injection
        if not isinstance(retention_days, int) or retention_days <= 0:
            return 0

        try:
            cutoff_date = datetime.now().isoformat()
            # Use parameterized query to prevent SQL injection
            query = (
                "DELETE FROM app_logs WHERE timestamp < "
                "datetime(?, ? || ' days')"
            )
            affected = self.db_manager.execute_update(
                query, (cutoff_date, f"-{retention_days}")
            )
            return affected
        except Exception:
            return 0

    def export_logs(self, export_path: str, **filters) -> bool:
        """Export logs to a file."""
        if not self.enabled:
            return False

        try:
            logs = self.get_logs(
                **filters, limit=10000
            )  # Large limit for export

            export_data = []
            for log in logs:
                export_data.append(
                    {
                        "timestamp": (
                            log.timestamp.isoformat()
                            if log.timestamp
                            else None
                        ),
                        "level": log.level,
                        "logger_name": log.logger_name,
                        "message": log.message,
                        "module": log.module,
                        "function": log.function,
                        "line_number": log.line_number,
                        "tool_name": log.tool_name,
                        "session_id": log.session_id,
                        "metadata": log.metadata,
                    }
                )

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception:
            return False


# Global instance
_database_log_service = None


def get_database_log_service() -> DatabaseLogService:
    """Get the global DatabaseLogService instance."""
    global _database_log_service
    if _database_log_service is None:
        _database_log_service = DatabaseLogService()
    return _database_log_service
