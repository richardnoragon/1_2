"""Shared helpers for SQLite-backed repositories."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from src.database.database_manager import DatabaseManager, get_database_manager


class SQLiteRepository:
    """Provide connection helpers for repositories using DatabaseManager."""

    def __init__(
        self,
        *,
        db_manager: DatabaseManager | None = None,
        database_path: str | Path | None = None,
    ) -> None:
        self._db = db_manager
        self._db_path: Path | None = None
        if self._db is None and database_path is not None:
            self._db_path = Path(database_path)
        if self._db is None and self._db_path is None:
            self._db = get_database_manager()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a SQLite connection with foreign keys enforced."""

        if self._db is not None:
            with self._db.get_connection() as conn:
                conn.execute("PRAGMA foreign_keys=ON")
                yield conn
            return

        if self._db_path is None:
            raise RuntimeError("Repository missing both DatabaseManager and db path")

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            yield conn
        finally:
            conn.close()


__all__ = ["SQLiteRepository"]
