"""
History Manager for RFU Multi-Pane File Explorer

This module provides persistent navigation history with favorites management
and intelligent path tracking.

Author: Richard Noragon
Version: 2.0.0
"""

import json
import logging
import sqlite3
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


@dataclass
class HistoryEntry:
    """Represents a single navigation history entry."""

    path: str
    timestamp: str
    access_count: int = 1
    last_accessed: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    is_favorite: bool = False
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def __post_init__(self):
        """Post-initialization validation."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def update_access(self) -> None:
        """Update access information."""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoryEntry":
        """Create from dictionary."""
        return cls(**data)


class HistoryDatabase:
    """SQLite database for persistent history storage."""

    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        self.lock = threading.RLock()
        self.logger = logging.getLogger("RFU.HistoryDatabase")

        self._ensure_database()

    def _ensure_database(self) -> None:
        """Ensure database and tables exist."""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS navigation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        last_accessed TEXT NOT NULL,
                        is_favorite BOOLEAN DEFAULT FALSE,
                        tags TEXT DEFAULT '',
                        notes TEXT DEFAULT '',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_path ON navigation_history(path)
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_last_accessed 
                    ON navigation_history(last_accessed)
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_is_favorite 
                    ON navigation_history(is_favorite)
                """
                )

                conn.commit()
                conn.close()

        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")

    def add_entry(self, entry: HistoryEntry) -> bool:
        """
        Add or update history entry.

        Args:
            entry: History entry to add

        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)

                # Convert tags to JSON string
                tags_json = json.dumps(entry.tags)

                conn.execute(
                    """
                    INSERT OR REPLACE INTO navigation_history 
                    (path, timestamp, access_count, last_accessed, is_favorite, tags, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        entry.path,
                        entry.timestamp,
                        entry.access_count,
                        entry.last_accessed,
                        entry.is_favorite,
                        tags_json,
                        entry.notes,
                    ),
                )

                conn.commit()
                conn.close()
                return True

        except sqlite3.Error as e:
            self.logger.error(f"Failed to add history entry: {e}")
            return False

    def get_entry(self, path: str) -> Optional[HistoryEntry]:
        """
        Get history entry by path.

        Args:
            path: Path to look up

        Returns:
            HistoryEntry or None: Entry if found
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    """
                    SELECT path, timestamp, access_count, last_accessed, 
                           is_favorite, tags, notes
                    FROM navigation_history 
                    WHERE path = ?
                """,
                    (path,),
                )

                row = cursor.fetchone()
                conn.close()

                if row:
                    tags = json.loads(row[5]) if row[5] else []
                    return HistoryEntry(
                        path=row[0],
                        timestamp=row[1],
                        access_count=row[2],
                        last_accessed=row[3],
                        is_favorite=bool(row[4]),
                        tags=tags,
                        notes=row[6],
                    )

        except (sqlite3.Error, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get history entry: {e}")

        return None

    def get_recent_entries(self, limit: int = 50) -> List[HistoryEntry]:
        """
        Get recent history entries.

        Args:
            limit: Maximum number of entries

        Returns:
            List of recent history entries
        """
        entries = []

        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    """
                    SELECT path, timestamp, access_count, last_accessed, 
                           is_favorite, tags, notes
                    FROM navigation_history 
                    ORDER BY last_accessed DESC
                    LIMIT ?
                """,
                    (limit,),
                )

                for row in cursor.fetchall():
                    tags = json.loads(row[5]) if row[5] else []
                    entry = HistoryEntry(
                        path=row[0],
                        timestamp=row[1],
                        access_count=row[2],
                        last_accessed=row[3],
                        is_favorite=bool(row[4]),
                        tags=tags,
                        notes=row[6],
                    )
                    entries.append(entry)

                conn.close()

        except (sqlite3.Error, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get recent entries: {e}")

        return entries

    def get_favorites(self) -> List[HistoryEntry]:
        """
        Get favorite entries.

        Returns:
            List of favorite history entries
        """
        entries = []

        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    """
                    SELECT path, timestamp, access_count, last_accessed, 
                           is_favorite, tags, notes
                    FROM navigation_history 
                    WHERE is_favorite = TRUE
                    ORDER BY last_accessed DESC
                """
                )

                for row in cursor.fetchall():
                    tags = json.loads(row[5]) if row[5] else []
                    entry = HistoryEntry(
                        path=row[0],
                        timestamp=row[1],
                        access_count=row[2],
                        last_accessed=row[3],
                        is_favorite=bool(row[4]),
                        tags=tags,
                        notes=row[6],
                    )
                    entries.append(entry)

                conn.close()

        except (sqlite3.Error, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get favorites: {e}")

        return entries

    def search_entries(self, query: str) -> List[HistoryEntry]:
        """
        Search history entries.

        Args:
            query: Search query

        Returns:
            List of matching entries
        """
        entries = []

        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    """
                    SELECT path, timestamp, access_count, last_accessed, 
                           is_favorite, tags, notes
                    FROM navigation_history 
                    WHERE path LIKE ? OR notes LIKE ? OR tags LIKE ?
                    ORDER BY access_count DESC, last_accessed DESC
                """,
                    (f"%{query}%", f"%{query}%", f"%{query}%"),
                )

                for row in cursor.fetchall():
                    tags = json.loads(row[5]) if row[5] else []
                    entry = HistoryEntry(
                        path=row[0],
                        timestamp=row[1],
                        access_count=row[2],
                        last_accessed=row[3],
                        is_favorite=bool(row[4]),
                        tags=tags,
                        notes=row[6],
                    )
                    entries.append(entry)

                conn.close()

        except (sqlite3.Error, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to search entries: {e}")

        return entries

    def delete_entry(self, path: str) -> bool:
        """
        Delete history entry.

        Args:
            path: Path to delete

        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.execute(
                    "DELETE FROM navigation_history WHERE path = ?", (path,)
                )
                conn.commit()
                conn.close()
                return True

        except sqlite3.Error as e:
            self.logger.error(f"Failed to delete entry: {e}")
            return False

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Clean up old history entries.

        Args:
            days: Age threshold in days

        Returns:
            int: Number of entries deleted
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    """
                    DELETE FROM navigation_history 
                    WHERE last_accessed < ? AND is_favorite = FALSE
                """,
                    (cutoff_date,),
                )

                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()

                self.logger.info(
                    f"Cleaned up {deleted_count} old history entries"
                )
                return deleted_count

        except sqlite3.Error as e:
            self.logger.error(f"Failed to cleanup old entries: {e}")
            return 0


class HistoryManager(QObject):
    """
    Manages navigation history with persistent storage and favorites.

    Features:
    - Persistent SQLite storage
    - Back/forward navigation
    - Favorites management
    - Search functionality
    - Access frequency tracking
    - Automatic cleanup
    - Tag support
    """

    # Signals
    history_changed = pyqtSignal()
    entry_added = pyqtSignal(str)  # path
    entry_removed = pyqtSignal(str)  # path
    favorite_toggled = pyqtSignal(str, bool)  # path, is_favorite
    navigation_state_changed = pyqtSignal(
        bool, bool
    )  # can_go_back, can_go_forward

    def __init__(self, db_path: Optional[str] = None, parent=None):
        """Initialize history manager."""
        super().__init__(parent)

        # Database setup
        if db_path is None:
            db_path = str(Path.home() / ".rfu" / "navigation_history.db")

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.database = HistoryDatabase(db_path)

        # Navigation state
        self.back_history: deque = deque(maxlen=100)
        self.forward_history: deque = deque(maxlen=100)
        self.current_path: Optional[str] = None

        # Settings
        self.max_history_size = 1000
        self.auto_cleanup_days = 30

        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._auto_cleanup)
        self.cleanup_timer.start(24 * 60 * 60 * 1000)  # Daily cleanup

        # Setup logging
        self.logger = logging.getLogger("RFU.HistoryManager")

        self.logger.debug("HistoryManager initialized")

    def navigate_to(self, path: str) -> None:
        """
        Navigate to a new path and update history.

        Args:
            path: Path to navigate to
        """
        # Normalize path
        try:
            normalized_path = str(Path(path).resolve())
        except (OSError, ValueError):
            self.logger.warning(f"Invalid path for navigation: {path}")
            return

        # Don't add if it's the same as current
        if normalized_path == self.current_path:
            return

        # Add current path to back history
        if self.current_path is not None:
            self.back_history.append(self.current_path)

        # Clear forward history (new navigation invalidates forward history)
        self.forward_history.clear()

        # Update current path
        self.current_path = normalized_path

        # Add to database
        self._add_to_database(normalized_path)

        # Emit signals
        self._emit_navigation_state_changed()
        self.entry_added.emit(normalized_path)
        self.history_changed.emit()

        self.logger.debug(f"Navigated to: {normalized_path}")

    def go_back(self) -> Optional[str]:
        """
        Go back in navigation history.

        Returns:
            str or None: Previous path if available
        """
        if not self.can_go_back():
            return None

        # Move current to forward history
        if self.current_path is not None:
            self.forward_history.append(self.current_path)

        # Get previous path
        previous_path = self.back_history.pop()
        self.current_path = previous_path

        # Update database access
        self._update_database_access(previous_path)

        # Emit signals
        self._emit_navigation_state_changed()
        self.history_changed.emit()

        self.logger.debug(f"Went back to: {previous_path}")
        return previous_path

    def go_forward(self) -> Optional[str]:
        """
        Go forward in navigation history.

        Returns:
            str or None: Next path if available
        """
        if not self.can_go_forward():
            return None

        # Move current to back history
        if self.current_path is not None:
            self.back_history.append(self.current_path)

        # Get next path
        next_path = self.forward_history.pop()
        self.current_path = next_path

        # Update database access
        self._update_database_access(next_path)

        # Emit signals
        self._emit_navigation_state_changed()
        self.history_changed.emit()

        self.logger.debug(f"Went forward to: {next_path}")
        return next_path

    def can_go_back(self) -> bool:
        """Check if back navigation is possible."""
        return len(self.back_history) > 0

    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible."""
        return len(self.forward_history) > 0

    def get_back_history(self, limit: int = 10) -> List[str]:
        """
        Get back navigation history.

        Args:
            limit: Maximum number of entries

        Returns:
            List of back history paths
        """
        return list(self.back_history)[-limit:]

    def get_forward_history(self, limit: int = 10) -> List[str]:
        """
        Get forward navigation history.

        Args:
            limit: Maximum number of entries

        Returns:
            List of forward history paths
        """
        return list(self.forward_history)[-limit:]

    def get_recent_history(self, limit: int = 20) -> List[HistoryEntry]:
        """
        Get recent navigation history.

        Args:
            limit: Maximum number of entries

        Returns:
            List of recent history entries
        """
        return self.database.get_recent_entries(limit)

    def get_favorites(self) -> List[HistoryEntry]:
        """Get favorite entries."""
        return self.database.get_favorites()

    def toggle_favorite(self, path: str) -> bool:
        """
        Toggle favorite status of a path.

        Args:
            path: Path to toggle favorite status

        Returns:
            bool: New favorite status
        """
        entry = self.database.get_entry(path)

        if entry is None:
            # Create new entry as favorite
            entry = HistoryEntry(path=path, is_favorite=True)
        else:
            # Toggle existing entry
            entry.is_favorite = not entry.is_favorite

        # Update database
        success = self.database.add_entry(entry)

        if success:
            self.favorite_toggled.emit(path, entry.is_favorite)
            self.history_changed.emit()
            self.logger.info(
                f"Favorite toggled for {path}: {entry.is_favorite}"
            )

        return entry.is_favorite

    def add_favorite(
        self, path: str, notes: str = "", tags: List[str] = None
    ) -> bool:
        """
        Add path as favorite.

        Args:
            path: Path to add as favorite
            notes: Optional notes
            tags: Optional tags

        Returns:
            bool: True if successful
        """
        if tags is None:
            tags = []

        entry = self.database.get_entry(path)

        if entry is None:
            entry = HistoryEntry(
                path=path, is_favorite=True, notes=notes, tags=tags
            )
        else:
            entry.is_favorite = True
            entry.notes = notes
            entry.tags = tags

        success = self.database.add_entry(entry)

        if success:
            self.favorite_toggled.emit(path, True)
            self.history_changed.emit()
            self.logger.info(f"Added favorite: {path}")

        return success

    def remove_favorite(self, path: str) -> bool:
        """
        Remove path from favorites.

        Args:
            path: Path to remove from favorites

        Returns:
            bool: True if successful
        """
        entry = self.database.get_entry(path)

        if entry and entry.is_favorite:
            entry.is_favorite = False
            success = self.database.add_entry(entry)

            if success:
                self.favorite_toggled.emit(path, False)
                self.history_changed.emit()
                self.logger.info(f"Removed favorite: {path}")

            return success

        return False

    def search_history(self, query: str) -> List[HistoryEntry]:
        """
        Search navigation history.

        Args:
            query: Search query

        Returns:
            List of matching entries
        """
        return self.database.search_entries(query)

    def clear_history(self, keep_favorites: bool = True) -> bool:
        """
        Clear navigation history.

        Args:
            keep_favorites: Whether to keep favorite entries

        Returns:
            bool: True if successful
        """
        try:
            if keep_favorites:
                # Clear non-favorite entries
                recent_entries = self.database.get_recent_entries(10000)
                for entry in recent_entries:
                    if not entry.is_favorite:
                        self.database.delete_entry(entry.path)
            else:
                # Clear all entries (would need database method)
                pass

            # Clear in-memory history
            self.back_history.clear()
            self.forward_history.clear()

            self.history_changed.emit()
            self._emit_navigation_state_changed()

            self.logger.info("History cleared")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clear history: {e}")
            return False

    def export_history(self, file_path: str) -> bool:
        """
        Export history to JSON file.

        Args:
            file_path: Export file path

        Returns:
            bool: True if successful
        """
        try:
            entries = self.database.get_recent_entries(10000)
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "entries": [entry.to_dict() for entry in entries],
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"History exported to: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export history: {e}")
            return False

    def import_history(self, file_path: str) -> bool:
        """
        Import history from JSON file.

        Args:
            file_path: Import file path

        Returns:
            bool: True if successful
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            for entry_data in import_data.get("entries", []):
                entry = HistoryEntry.from_dict(entry_data)
                self.database.add_entry(entry)

            self.history_changed.emit()
            self.logger.info(f"History imported from: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import history: {e}")
            return False

    def _add_to_database(self, path: str) -> None:
        """Add path to database."""
        entry = self.database.get_entry(path)

        if entry is None:
            entry = HistoryEntry(path=path)
        else:
            entry.update_access()

        self.database.add_entry(entry)

    def _update_database_access(self, path: str) -> None:
        """Update database access information."""
        entry = self.database.get_entry(path)

        if entry is not None:
            entry.update_access()
            self.database.add_entry(entry)

    def _emit_navigation_state_changed(self) -> None:
        """Emit navigation state changed signal."""
        self.navigation_state_changed.emit(
            self.can_go_back(), self.can_go_forward()
        )

    def _auto_cleanup(self) -> None:
        """Perform automatic cleanup of old entries."""
        deleted_count = self.database.cleanup_old_entries(
            self.auto_cleanup_days
        )
        if deleted_count > 0:
            self.history_changed.emit()

    def get_current_path(self) -> Optional[str]:
        """Get current path."""
        return self.current_path

    def set_auto_cleanup_days(self, days: int) -> None:
        """Set automatic cleanup threshold."""
        self.auto_cleanup_days = days
        self.logger.info(f"Auto cleanup days set to: {days}")
