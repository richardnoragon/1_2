"""Database-backed logging utilities for RFU."""

from __future__ import annotations

import json
import logging
import traceback
from datetime import datetime
from functools import lru_cache
from sqlite3 import Error as SQLiteError
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    cast,
)

try:
    from .database_manager import get_database_manager as _get_database_manager
except ImportError:  # pragma: no cover - handled by DATABASE_AVAILABLE flag
    _get_database_manager: Optional[Callable[[], Any]] = None

try:
    from .database_models import AppLog as _resolved_app_log
except ImportError:  # pragma: no cover - handled by DATABASE_AVAILABLE flag
    _resolved_app_log: Optional[Type[Any]] = None

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from .database_models import AppLog as AppLogType
else:
    AppLogType = Any

GetDatabaseManager = Optional[Callable[[], Any]]
get_database_manager: GetDatabaseManager
if _get_database_manager is not None:
    get_database_manager = _get_database_manager
else:
    get_database_manager = None

_AppLogClass: Optional[Type[Any]]
if _resolved_app_log is not None:
    _AppLogClass = _resolved_app_log
else:
    _AppLogClass = None

DATABASE_AVAILABLE = get_database_manager is not None and _AppLogClass is not None

_RESERVED_LOG_RECORD_FIELDS = {
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
}

_LOGGING_RUNTIME_ERRORS = (
    SQLiteError,
    ValueError,
    TypeError,
    RuntimeError,
    OSError,
    AttributeError,
    KeyError,
)


def _is_ready() -> bool:
    return (
        DATABASE_AVAILABLE
        and get_database_manager is not None
        and _AppLogClass is not None
    )


class DatabaseLogHandler(logging.Handler):
    """Custom logging handler that stores logs in the SQLite database."""

    def __init__(self, session_id: Optional[str] = None):
        super().__init__()
        self.session_id = session_id
        self.db_manager: Optional[Any] = None
        self.enabled = self._initialise_database()

    def emit(self, record: logging.LogRecord) -> None:
        if not self._can_emit():
            return

        try:
            log_entry = self._build_log_entry(record)
            self._store_log_entry(log_entry)
        except _LOGGING_RUNTIME_ERRORS as error:
            record.exc_info = (type(error), error, error.__traceback__)
            self.handleError(record)

    def _store_log_entry(self, log_entry: AppLogType) -> None:
        if not self.db_manager:
            return

        query = """
            INSERT INTO app_logs
            (timestamp, level, logger_name, message, module, function,
             line_number, tool_name, session_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            (
                log_entry.timestamp.isoformat()
                if getattr(log_entry, "timestamp", None)
                else None
            ),
            getattr(log_entry, "level", None),
            getattr(log_entry, "logger_name", None),
            getattr(log_entry, "message", None),
            getattr(log_entry, "module", None),
            getattr(log_entry, "function", None),
            getattr(log_entry, "line_number", None),
            getattr(log_entry, "tool_name", None),
            getattr(log_entry, "session_id", None),
            (
                json.dumps(getattr(log_entry, "metadata", {}))
                if getattr(log_entry, "metadata", None)
                else None
            ),
        )

        db_manager = cast(Any, self.db_manager)
        db_manager.execute_update(query, params)

    def _initialise_database(self) -> bool:
        if not _is_ready():
            return False

        try:
            manager_factory = cast(Callable[[], Any], get_database_manager)
            self.db_manager = manager_factory()
        except _LOGGING_RUNTIME_ERRORS:
            self.db_manager = None
            return False

        return self.db_manager is not None

    def _can_emit(self) -> bool:
        return bool(self.enabled and self.db_manager is not None and _AppLogClass)

    def _build_log_entry(self, record: logging.LogRecord) -> AppLogType:
        metadata = self._build_metadata(record)
        app_log_cls = cast(Type[AppLogType], _AppLogClass)
        return app_log_cls(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            tool_name=self._resolve_tool_name(record),
            session_id=self.session_id,
            metadata=metadata,
        )

    def _build_metadata(self, record: logging.LogRecord) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        exception_data = self._exception_payload(record)
        if exception_data:
            metadata["exception"] = exception_data
        metadata.update(self._extra_record_fields(record))
        return metadata

    @staticmethod
    def _resolve_tool_name(record: logging.LogRecord) -> Optional[str]:
        if hasattr(record, "tool_name"):
            value = getattr(record, "tool_name")
            return str(value) if value is not None else None
        if "." not in record.name:
            return None
        parts = record.name.split(".")
        return parts[2] if len(parts) > 2 else None

    @staticmethod
    def _extra_record_fields(record: logging.LogRecord) -> Dict[str, str]:
        extras: Dict[str, str] = {}
        for key, value in record.__dict__.items():
            if key in _RESERVED_LOG_RECORD_FIELDS:
                continue
            extras[key] = str(value)
        return extras

    @staticmethod
    def _exception_payload(record: logging.LogRecord) -> Dict[str, Any]:
        if not record.exc_info:
            return {}

        exc_type, exc_value, exc_tb = record.exc_info
        payload: Dict[str, Any] = {}

        if exc_type is not None:
            payload["type"] = exc_type.__name__
        if exc_value is not None:
            payload["message"] = str(exc_value)
        if exc_type is not None and exc_tb is not None:
            payload["traceback"] = traceback.format_exception(
                exc_type, exc_value, exc_tb
            )

        return payload


class DatabaseLogService:
    """Service for querying and managing logs in the database."""

    def __init__(self) -> None:
        self.db_manager: Optional[Any] = None
        self.enabled = self._initialise_database()

    def get_logs(
        self,
        level: Optional[str] = None,
        tool_name: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AppLogType]:
        if not self.enabled or not self.db_manager:
            return []

        query, params = self._build_log_query(
            level=level,
            tool_name=tool_name,
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        db_manager = cast(Any, self.db_manager)
        try:
            results = db_manager.execute_query(query, params)
        except _LOGGING_RUNTIME_ERRORS:
            return []

        return self._rows_to_logs(results)

    def get_log_statistics(self) -> Dict[str, Any]:
        if not self.enabled or not self.db_manager:
            return {}

        try:
            return {
                "total_logs": self._scalar_query(
                    "SELECT COUNT(*) as count FROM app_logs"
                ),
                "by_level": self._grouped_counts(
                    "SELECT level, COUNT(*) as count "
                    "FROM app_logs GROUP BY level ORDER BY count DESC"
                ),
                "by_tool": self._grouped_counts(
                    "SELECT tool_name, COUNT(*) as count "
                    "FROM app_logs WHERE tool_name IS NOT NULL "
                    "GROUP BY tool_name ORDER BY count DESC LIMIT 10"
                ),
                "last_24_hours": self._scalar_query(
                    "SELECT COUNT(*) as count "
                    "FROM app_logs WHERE timestamp >= "
                    "datetime('now', '-1 day')"
                ),
            }
        except _LOGGING_RUNTIME_ERRORS:
            return {}

    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        if not self.enabled or not self.db_manager:
            return 0
        if not isinstance(retention_days, int) or retention_days <= 0:
            return 0

        try:
            cutoff_date = datetime.now().isoformat()
            query = (
                "DELETE FROM app_logs WHERE timestamp < " "datetime(?, ? || ' days')"
            )
            db_manager = cast(Any, self.db_manager)
            affected = db_manager.execute_update(
                query, (cutoff_date, f"-{retention_days}")
            )
            return int(affected or 0)
        except _LOGGING_RUNTIME_ERRORS:
            return 0

    def export_logs(self, export_path: str, **filters: Any) -> bool:
        if not self.enabled or not self.db_manager:
            return False

        try:
            logs = self.get_logs(**filters, limit=10000)
            export_data = [self._serialise_log(log) for log in logs]
            with open(export_path, "w", encoding="utf-8") as handle:
                json.dump(export_data, handle, indent=2, ensure_ascii=False)
            return True
        except (_LOGGING_RUNTIME_ERRORS, OSError):
            return False

    def _initialise_database(self) -> bool:
        if not _is_ready():
            return False
        try:
            manager_factory = cast(Callable[[], Any], get_database_manager)
            self.db_manager = manager_factory()
        except _LOGGING_RUNTIME_ERRORS:
            self.db_manager = None
            return False
        return bool(self.db_manager and _AppLogClass)

    def _build_log_query(
        self,
        *,
        level: Optional[str],
        tool_name: Optional[str],
        session_id: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int,
    ) -> Tuple[str, Tuple[Any, ...]]:
        query = ["SELECT * FROM app_logs WHERE 1=1"]
        params: List[Any] = []

        def _add_clause(clause: str, value: Any) -> None:
            if value is None:
                return
            query.append(clause)
            params.append(value)

        _add_clause(" AND level = ?", level)
        _add_clause(" AND tool_name = ?", tool_name)
        _add_clause(" AND session_id = ?", session_id)
        _add_clause(
            " AND timestamp >= ?",
            start_time.isoformat() if start_time else None,
        )
        _add_clause(
            " AND timestamp <= ?",
            end_time.isoformat() if end_time else None,
        )

        query.append(" ORDER BY timestamp DESC LIMIT ?")
        params.append(limit)

        return "".join(query), tuple(params)

    def _rows_to_logs(self, rows: Iterable[Dict[str, Any]]) -> List[AppLogType]:
        if _AppLogClass is None:
            return []

        app_log_cls = cast(Type[AppLogType], _AppLogClass)
        logs: List[AppLogType] = []
        for row in rows:
            logs.append(
                app_log_cls(
                    id=row.get("id"),
                    timestamp=self._parse_timestamp(row.get("timestamp")),
                    level=row.get("level"),
                    logger_name=row.get("logger_name"),
                    message=row.get("message"),
                    module=row.get("module"),
                    function=row.get("function"),
                    line_number=row.get("line_number"),
                    tool_name=row.get("tool_name"),
                    session_id=row.get("session_id"),
                    metadata=self._decode_metadata(row.get("metadata")),
                )
            )
        return logs

    @staticmethod
    def _parse_timestamp(raw_timestamp: Optional[str]) -> Optional[datetime]:
        if not raw_timestamp:
            return None
        try:
            return datetime.fromisoformat(raw_timestamp)
        except ValueError:
            return None

    @staticmethod
    def _decode_metadata(raw_metadata: Optional[str]) -> Dict[str, Any]:
        if not raw_metadata:
            return {}
        try:
            decoded = json.loads(raw_metadata)
            return decoded if isinstance(decoded, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _scalar_query(self, query: str) -> int:
        if not self.db_manager:
            return 0
        db_manager = cast(Any, self.db_manager)
        try:
            result = db_manager.execute_query(query)
        except _LOGGING_RUNTIME_ERRORS:
            return 0
        return result[0]["count"] if result else 0

    def _grouped_counts(self, query: str) -> Dict[str, int]:
        if not self.db_manager:
            return {}
        db_manager = cast(Any, self.db_manager)
        try:
            result = db_manager.execute_query(query)
        except _LOGGING_RUNTIME_ERRORS:
            return {}

        groups: Dict[str, int] = {}
        for row in result:
            if isinstance(row, dict):
                key = row.get("tool_name") or row.get("level") or ""
                value = int(row.get("count", 0))
            else:
                key = str(row[0]) if row else ""
                value = int(row[1]) if len(row) > 1 else 0
            if key:
                groups[key] = value
        return groups

    @staticmethod
    def _serialise_log(log: AppLogType) -> Dict[str, Any]:
        timestamp = getattr(log, "timestamp", None)
        return {
            "timestamp": timestamp.isoformat() if timestamp else None,
            "level": getattr(log, "level", None),
            "logger_name": getattr(log, "logger_name", None),
            "message": getattr(log, "message", None),
            "module": getattr(log, "module", None),
            "function": getattr(log, "function", None),
            "line_number": getattr(log, "line_number", None),
            "tool_name": getattr(log, "tool_name", None),
            "session_id": getattr(log, "session_id", None),
            "metadata": getattr(log, "metadata", {}),
        }


@lru_cache(maxsize=1)
def get_database_log_service() -> DatabaseLogService:
    """Return the shared instance of the log service."""
    return DatabaseLogService()
