"""
File Explorer Database Schema

This module defines the database schema for the multi-pane file explorer,
including user preferences, pane configurations, and file operation history.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class FileExplorerSchema:
    """Manages the database schema for the file explorer."""

    def __init__(self, db_path: str = "data/file_explorer.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger("RFU.FileExplorer.Schema")

    def create_schema(self) -> bool:
        """Create all required tables for the file explorer."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys=ON")

                # Create all tables
                self._create_pane_tables(conn)
                self._create_preferences_tables(conn)
                self._create_history_tables(conn)
                self._create_bookmark_tables(conn)

                # Create indexes
                self._create_indexes(conn)

                # Insert default data
                self._insert_default_data(conn)

                conn.commit()

            self.logger.info("File explorer schema created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create schema: {e}")
            return False

    def _create_pane_tables(self, conn: sqlite3.Connection):
        """Create pane-related tables."""

        # Pane configurations
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pane_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT NOT NULL UNIQUE,
                pane_count INTEGER NOT NULL CHECK (pane_count BETWEEN 1 AND 4),
                is_default BOOLEAN DEFAULT FALSE,
                layout_type TEXT NOT NULL DEFAULT 'horizontal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Individual pane settings
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pane_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER REFERENCES pane_configurations(id) ON DELETE CASCADE,
                pane_index INTEGER NOT NULL CHECK (pane_index BETWEEN 0 AND 3),
                default_path TEXT,
                view_mode TEXT DEFAULT 'list',
                sort_column TEXT DEFAULT 'name',
                sort_order TEXT DEFAULT 'ASC',
                show_hidden BOOLEAN DEFAULT FALSE,
                column_widths TEXT,
                UNIQUE(config_id, pane_index)
            )
        """
        )

        # Pane layout preferences
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS layout_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_name TEXT NOT NULL UNIQUE,
                window_geometry TEXT,
                pane_splitter_sizes TEXT,
                toolbar_visible BOOLEAN DEFAULT TRUE,
                statusbar_visible BOOLEAN DEFAULT TRUE,
                sidebar_visible BOOLEAN DEFAULT TRUE,
                sidebar_width INTEGER DEFAULT 200,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    def _create_preferences_tables(self, conn: sqlite3.Connection):
        """Create preference-related tables."""

        # File type color schemes
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_type_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheme_name TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                foreground_color TEXT NOT NULL,
                background_color TEXT,
                font_weight TEXT DEFAULT 'normal',
                font_style TEXT DEFAULT 'normal',
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(scheme_name, file_extension)
            )
        """
        )

        # Explorer preference storage is handled by PreferenceManager; the
        # legacy explorer-specific user_preferences table was removed in beta.

    def _create_history_tables(self, conn: sqlite3.Connection):
        """Create history-related tables."""

        # Navigation history
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS navigation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pane_index INTEGER NOT NULL,
                path TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT NOT NULL
            )
        """
        )

        # Recent directories
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recent_directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                access_count INTEGER DEFAULT 1,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pane_index INTEGER,
                display_name TEXT
            )
        """
        )

        # File operations log
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                source_path TEXT NOT NULL,
                destination_path TEXT,
                file_size BIGINT,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_ms INTEGER
            )
        """
        )

    def _create_bookmark_tables(self, conn: sqlite3.Connection):
        """Create bookmark-related tables."""

        # Bookmarks and favorites
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                icon_path TEXT,
                category TEXT DEFAULT 'user',
                sort_order INTEGER DEFAULT 0,
                is_favorite BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP
            )
        """
        )

        # Bookmark categories
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookmark_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance."""

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_pane_config_default ON pane_configurations(is_default)",
            "CREATE INDEX IF NOT EXISTS idx_pane_settings_config ON pane_settings(config_id)",
            "CREATE INDEX IF NOT EXISTS idx_navigation_history_pane ON navigation_history(pane_index)",
            "CREATE INDEX IF NOT EXISTS idx_navigation_history_session ON navigation_history(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_recent_directories_accessed ON recent_directories(last_accessed)",
            "CREATE INDEX IF NOT EXISTS idx_file_operations_status ON file_operations(status)",
            "CREATE INDEX IF NOT EXISTS idx_file_operations_type ON file_operations(operation_type)",
            "CREATE INDEX IF NOT EXISTS idx_bookmarks_category ON bookmarks(category)",
            "CREATE INDEX IF NOT EXISTS idx_file_type_colors_scheme ON file_type_colors(scheme_name)",
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

    def _insert_default_data(self, conn: sqlite3.Connection):
        """Insert default configuration data."""

        # Default pane configuration
        conn.execute(
            """
            INSERT OR IGNORE INTO pane_configurations 
            (config_name, pane_count, is_default, layout_type)
            VALUES ('Default Dual Pane', 2, TRUE, 'horizontal')
        """
        )

        config_id = conn.lastrowid or 1

        # Default pane settings
        home_path = str(Path.home())
        documents_path = str(Path.home() / "Documents")

        pane_settings = [
            (config_id, 0, home_path, "list", "name", "ASC", False),
            (config_id, 1, documents_path, "list", "name", "ASC", False),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO pane_settings 
            (config_id, pane_index, default_path, view_mode, sort_column, sort_order, show_hidden)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            pane_settings,
        )

        # Default layout preferences
        conn.execute(
            """
            INSERT OR IGNORE INTO layout_preferences 
            (preference_name, toolbar_visible, statusbar_visible, sidebar_visible, sidebar_width)
            VALUES ('Default Layout', TRUE, TRUE, TRUE, 200)
        """
        )

        # Default file type colors
        default_colors = [
            ("Default", ".txt", "#000000", "", "normal", "normal"),
            ("Default", ".py", "#0066cc", "", "normal", "normal"),
            ("Default", ".jpg", "#cc6600", "", "normal", "normal"),
            ("Default", ".png", "#cc6600", "", "normal", "normal"),
            ("Default", ".pdf", "#cc0000", "", "normal", "normal"),
            ("Default", ".zip", "#660099", "", "normal", "normal"),
            ("Default", ".exe", "#990000", "", "bold", "normal"),
            ("Default", ".dll", "#666666", "", "normal", "normal"),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO file_type_colors 
            (scheme_name, file_extension, foreground_color, background_color, 
             font_weight, font_style)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            default_colors,
        )

        # Default bookmarks
        default_bookmarks = [
            ("Home", home_path, "", "system", 0, True),
            ("Documents", documents_path, "", "system", 1, True),
            (
                "Downloads",
                str(Path.home() / "Downloads"),
                "",
                "system",
                2,
                True,
            ),
            ("Desktop", str(Path.home() / "Desktop"), "", "system", 3, True),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO bookmarks 
            (name, path, icon_path, category, sort_order, is_favorite)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            default_bookmarks,
        )

        # Default bookmark categories
        categories = [
            ("system", "System locations", 0),
            ("user", "User bookmarks", 1),
            ("project", "Project folders", 2),
            ("network", "Network locations", 3),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO bookmark_categories 
            (name, description, sort_order)
            VALUES (?, ?, ?)
        """,
            categories,
        )


class FileExplorerDatabase:
    """Database manager for file explorer operations."""

    def __init__(self, db_path: str = "data/file_explorer.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger("RFU.FileExplorer.Database")

        # Initialize schema
        schema = FileExplorerSchema(db_path)
        if not schema.create_schema():
            raise RuntimeError("Failed to initialize file explorer database")

    def get_pane_configurations(self) -> List[Dict[str, Any]]:
        """Get all pane configurations."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM pane_configurations 
                    ORDER BY is_default DESC, config_name
                """
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get pane configurations: {e}")
            return []

    def get_default_pane_config(self) -> Optional[Dict[str, Any]]:
        """Get the default pane configuration."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM pane_configurations 
                    WHERE is_default = TRUE 
                    LIMIT 1
                """
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get default pane config: {e}")
            return None

    def save_pane_configuration(self, config: Dict[str, Any]) -> bool:
        """Save a pane configuration."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if "id" in config and config["id"]:
                    # Update existing
                    conn.execute(
                        """
                        UPDATE pane_configurations 
                        SET config_name=?, pane_count=?, layout_type=?, updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                    """,
                        (
                            config["config_name"],
                            config["pane_count"],
                            config["layout_type"],
                            config["id"],
                        ),
                    )
                else:
                    # Insert new
                    cursor = conn.execute(
                        """
                        INSERT INTO pane_configurations 
                        (config_name, pane_count, layout_type)
                        VALUES (?, ?, ?)
                    """,
                        (
                            config["config_name"],
                            config["pane_count"],
                            config["layout_type"],
                        ),
                    )
                    config["id"] = cursor.lastrowid

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Failed to save pane configuration: {e}")
            return False

    def add_to_navigation_history(self, pane_index: int, path: str, session_id: str):
        """Add an entry to navigation history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO navigation_history (pane_index, path, session_id)
                    VALUES (?, ?, ?)
                """,
                    (pane_index, path, session_id),
                )

                # Cleanup old entries (keep last 100 per pane)
                conn.execute(
                    """
                    DELETE FROM navigation_history 
                    WHERE pane_index = ? AND id NOT IN (
                        SELECT id FROM navigation_history 
                        WHERE pane_index = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 100
                    )
                """,
                    (pane_index, pane_index),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to add navigation history: {e}")

    def get_recent_directories(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent directories."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM recent_directories 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                """,
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get recent directories: {e}")
            return []

    def add_recent_directory(self, path: str, pane_index: int = None):
        """Add or update a recent directory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Try to update existing entry
                cursor = conn.execute(
                    """
                    UPDATE recent_directories 
                    SET access_count = access_count + 1, 
                        last_accessed = CURRENT_TIMESTAMP,
                        pane_index = ?
                    WHERE path = ?
                """,
                    (pane_index, path),
                )

                if cursor.rowcount == 0:
                    # Insert new entry
                    display_name = Path(path).name or path
                    conn.execute(
                        """
                        INSERT INTO recent_directories 
                        (path, pane_index, display_name)
                        VALUES (?, ?, ?)
                    """,
                        (path, pane_index, display_name),
                    )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to add recent directory: {e}")

    def get_bookmarks(self, category: str = None) -> List[Dict[str, Any]]:
        """Get bookmarks, optionally filtered by category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                if category:
                    cursor = conn.execute(
                        """
                        SELECT * FROM bookmarks 
                        WHERE category = ? 
                        ORDER BY sort_order, name
                    """,
                        (category,),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT * FROM bookmarks 
                        ORDER BY category, sort_order, name
                    """
                    )

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Failed to get bookmarks: {e}")
            return []

    def add_bookmark(self, name: str, path: str, category: str = "user") -> bool:
        """Add a new bookmark."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get next sort order for category
                cursor = conn.execute(
                    """
                    SELECT COALESCE(MAX(sort_order), 0) + 1 
                    FROM bookmarks WHERE category = ?
                """,
                    (category,),
                )
                sort_order = cursor.fetchone()[0]

                conn.execute(
                    """
                    INSERT INTO bookmarks (name, path, category, sort_order)
                    VALUES (?, ?, ?, ?)
                """,
                    (name, path, category, sort_order),
                )

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Failed to add bookmark: {e}")
            return False


# For testing and development
if __name__ == "__main__":
    # Test schema creation
    schema = FileExplorerSchema("test_explorer.db")
    if schema.create_schema():
        print("Schema created successfully")

        # Test database operations
        db = FileExplorerDatabase("test_explorer.db")
        configs = db.get_pane_configurations()
        print(f"Found {len(configs)} pane configurations")

        bookmarks = db.get_bookmarks()
        print(f"Found {len(bookmarks)} bookmarks")
    else:
        print("Schema creation failed")
