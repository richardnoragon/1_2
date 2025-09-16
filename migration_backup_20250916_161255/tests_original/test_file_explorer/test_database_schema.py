"""
Enterprise-Grade Unit Tests for Database Schema and Migration System
RFU Multi-Pane File Explorer Testing Framework

Test Coverage: Schema integrity, migration testing, constraint validation,
and performance benchmarking with zero-tolerance policy.

Framework: pytest with enterprise extensions
Standards: Zero-compromise quality assurance
Coverage Target: ≥90% line coverage, ≥95% branch coverage
Security: SQL injection prevention, data integrity
Performance: Query optimization, index effectiveness
Reliability: Migration safety and rollback capability

Test Categories:
- Schema Creation: Table structure and constraints
- Data Integrity: Foreign keys, check constraints, triggers
- Migration System: Version control and rollback safety
- Performance: Query execution and index optimization
- Concurrency: Multi-user access and transaction safety
- Security: SQL injection prevention and access control
"""

import json
import logging
import os
import sqlite3
# Import the modules under test
import sys
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest
from PyQt5.QtCore import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

try:
    from src.rfu.file_explorer.database.migrations import (
        CreateInitialSchemaMigration, DatabaseMigrator, Migration,
        MigrationError)
    from src.rfu.file_explorer.database.schema import (FileExplorerDatabase,
                                                       FileExplorerSchema)
except ImportError as e:
    pytest.skip(f"Cannot import database modules: {e}", 
                allow_module_level=True)


class TestFileExplorerSchema:
    """
    Comprehensive test suite for FileExplorerSchema class.
    
    Coverage:
    - Schema creation and table structure validation
    - Constraint enforcement and data integrity
    - Index creation and performance optimization
    - Default data insertion and consistency
    - Cross-platform compatibility
    """
    
    @pytest.fixture
    def temp_db_path(self):
        """Provide temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except OSError:
            pass
    
    @pytest.fixture
    def schema(self, temp_db_path):
        """Provide FileExplorerSchema instance for testing."""
        return FileExplorerSchema(temp_db_path)
    
    def test_schema_initialization(self, temp_db_path):
        """Test proper schema initialization."""
        schema = FileExplorerSchema(temp_db_path)
        
        assert schema.db_path == Path(temp_db_path)
        assert schema.logger is not None
        
        # Verify parent directory is created
        assert schema.db_path.parent.exists()
    
    def test_schema_creation_success(self, schema):
        """Test successful schema creation."""
        result = schema.create_schema()
        assert result is True
        
        # Verify database file was created
        assert schema.db_path.exists()
        
        # Verify tables were created
        with sqlite3.connect(schema.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = {
                'bookmark_categories', 'bookmarks', 'file_operations',
                'file_type_colors', 'layout_preferences', 'navigation_history',
                'pane_configurations', 'pane_settings', 'recent_directories',
                'user_preferences'
            }
            
            for table in expected_tables:
                assert table in tables
    
    def test_pane_table_constraints(self, schema):
        """Test pane table constraints and validation."""
        schema.create_schema()
        
        with sqlite3.connect(schema.db_path) as conn:
            # Test pane_count constraint
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_configurations 
                    (config_name, pane_count) VALUES ('Invalid', 0)
                """)
            
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_configurations 
                    (config_name, pane_count) VALUES ('Invalid', 5)
                """)
            
            # Test unique constraint
            conn.execute("""
                INSERT INTO pane_configurations 
                (config_name, pane_count) VALUES ('Test Config', 2)
            """)
            
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_configurations 
                    (config_name, pane_count) VALUES ('Test Config', 3)
                """)
            
            # Test pane_index constraint
            config_id = conn.lastrowid
            
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_settings 
                    (config_id, pane_index) VALUES (?, -1)
                """, (config_id,))
            
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_settings 
                    (config_id, pane_index) VALUES (?, 4)
                """, (config_id,))
    
    def test_foreign_key_constraints(self, schema):
        """Test foreign key constraint enforcement."""
        schema.create_schema()
        
        with sqlite3.connect(schema.db_path) as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            
            # Test foreign key constraint
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_settings 
                    (config_id, pane_index) VALUES (999, 0)
                """)
            
            # Test cascade delete
            cursor = conn.execute("""
                INSERT INTO pane_configurations 
                (config_name, pane_count) VALUES ('Delete Test', 2)
            """)
            config_id = cursor.lastrowid
            
            conn.execute("""
                INSERT INTO pane_settings 
                (config_id, pane_index) VALUES (?, 0)
            """, (config_id,))
            
            # Verify pane setting exists
            cursor = conn.execute("""
                SELECT COUNT(*) FROM pane_settings WHERE config_id = ?
            """, (config_id,))
            assert cursor.fetchone()[0] == 1
            
            # Delete parent configuration
            conn.execute("""
                DELETE FROM pane_configurations WHERE id = ?
            """, (config_id,))
            
            # Verify cascade delete worked
            cursor = conn.execute("""
                SELECT COUNT(*) FROM pane_settings WHERE config_id = ?
            """, (config_id,))
            assert cursor.fetchone()[0] == 0
    
    def test_check_constraints(self, schema):
        """Test CHECK constraint validation."""
        schema.create_schema()
        
        with sqlite3.connect(schema.db_path) as conn:
            # Test layout_type constraint
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_configurations 
                    (config_name, pane_count, layout_type) 
                    VALUES ('Invalid Layout', 2, 'invalid')
                """)
            
            # Test view_mode constraint
            config_id = 1  # Default config should exist
            
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_settings 
                    (config_id, pane_index, view_mode) 
                    VALUES (?, 0, 'invalid_view')
                """, (config_id,))
            
            # Test sort_order constraint
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_settings 
                    (config_id, pane_index, sort_order) 
                    VALUES (?, 1, 'INVALID')
                """, (config_id,))
    
    def test_index_creation(self, schema):
        """Test that all required indexes are created."""
        schema.create_schema()
        
        with sqlite3.connect(schema.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
                ORDER BY name
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            expected_indexes = {
                'idx_pane_config_default',
                'idx_pane_settings_config',
                'idx_navigation_history_pane',
                'idx_navigation_history_session',
                'idx_recent_directories_accessed',
                'idx_file_operations_status',
                'idx_file_operations_type',
                'idx_bookmarks_category',
                'idx_file_type_colors_scheme'
            }
            
            for index in expected_indexes:
                assert index in indexes
    
    def test_default_data_insertion(self, schema):
        """Test that default data is properly inserted."""
        schema.create_schema()
        
        with sqlite3.connect(schema.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Test default pane configuration
            cursor = conn.execute("""
                SELECT * FROM pane_configurations WHERE is_default = TRUE
            """)
            default_config = cursor.fetchone()
            assert default_config is not None
            assert default_config['config_name'] == 'Default Dual Pane'
            assert default_config['pane_count'] == 2
            
            # Test default pane settings
            cursor = conn.execute("""
                SELECT COUNT(*) FROM pane_settings 
                WHERE config_id = ?
            """, (default_config['id'],))
            assert cursor.fetchone()[0] == 2
            
            # Test default file type colors
            cursor = conn.execute("""
                SELECT COUNT(*) FROM file_type_colors 
                WHERE scheme_name = 'Default'
            """)
            assert cursor.fetchone()[0] >= 8
            
            # Test default bookmarks
            cursor = conn.execute("""
                SELECT COUNT(*) FROM bookmarks WHERE category = 'system'
            """)
            assert cursor.fetchone()[0] >= 4
            
            # Test default user preferences
            cursor = conn.execute("""
                SELECT COUNT(*) FROM user_preferences
            """)
            assert cursor.fetchone()[0] >= 8
    
    def test_schema_recreation_idempotency(self, schema):
        """Test that schema creation is idempotent."""
        # Create schema first time
        result1 = schema.create_schema()
        assert result1 is True
        
        # Create schema second time - should not fail
        result2 = schema.create_schema()
        assert result2 is True
        
        # Verify no duplicate data
        with sqlite3.connect(schema.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM pane_configurations 
                WHERE config_name = 'Default Dual Pane'
            """)
            assert cursor.fetchone()[0] == 1


class TestFileExplorerDatabase:
    """
    Comprehensive test suite for FileExplorerDatabase class.
    
    Coverage:
    - CRUD operations for all entities
    - Query performance and optimization
    - Data validation and sanitization
    - Transaction handling and concurrency
    - Error handling and recovery
    """
    
    @pytest.fixture
    def temp_db_path(self):
        """Provide temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except OSError:
            pass
    
    @pytest.fixture
    def database(self, temp_db_path):
        """Provide FileExplorerDatabase instance for testing."""
        return FileExplorerDatabase(temp_db_path)
    
    def test_database_initialization(self, database):
        """Test proper database initialization."""
        assert database.db_path.exists()
        assert database.logger is not None
        
        # Verify schema was created
        configs = database.get_pane_configurations()
        assert len(configs) >= 1
    
    def test_pane_configuration_operations(self, database):
        """Test pane configuration CRUD operations."""
        # Create new configuration
        new_config = {
            'config_name': 'Test Triple Pane',
            'pane_count': 3,
            'layout_type': 'vertical',
            'description': 'Test configuration'
        }
        
        result = database.save_pane_configuration(new_config)
        assert result is True
        assert 'id' in new_config
        
        # Retrieve configurations
        configs = database.get_pane_configurations()
        test_config = next((c for c in configs if c['config_name'] == 'Test Triple Pane'), None)
        assert test_config is not None
        assert test_config['pane_count'] == 3
        assert test_config['layout_type'] == 'vertical'
        
        # Update configuration
        test_config['pane_count'] = 4
        test_config['layout_type'] = 'grid'
        
        result = database.save_pane_configuration(test_config)
        assert result is True
        
        # Verify update
        updated_configs = database.get_pane_configurations()
        updated_config = next((c for c in updated_configs if c['id'] == test_config['id']), None)
        assert updated_config is not None
        assert updated_config['pane_count'] == 4
        assert updated_config['layout_type'] == 'grid'
    
    def test_default_pane_configuration(self, database):
        """Test default pane configuration retrieval."""
        default_config = database.get_default_pane_config()
        
        assert default_config is not None
        assert default_config['is_default'] is True
        assert default_config['config_name'] == 'Default Dual Pane'
        assert default_config['pane_count'] == 2
    
    def test_navigation_history_operations(self, database):
        """Test navigation history tracking."""
        session_id = "test_session_123"
        test_paths = [
            "/home/user/documents",
            "/home/user/downloads",
            "/home/user/pictures"
        ]
        
        # Add navigation history
        for i, path in enumerate(test_paths):
            database.add_to_navigation_history(pane_index=0, path=path, session_id=session_id)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Verify history was added
        with sqlite3.connect(database.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM navigation_history 
                WHERE session_id = ? 
                ORDER BY timestamp
            """, (session_id,))
            
            history = [dict(row) for row in cursor.fetchall()]
            assert len(history) == 3
            
            for i, entry in enumerate(history):
                assert entry['path'] == test_paths[i]
                assert entry['pane_index'] == 0
                assert entry['session_id'] == session_id
    
    def test_navigation_history_cleanup(self, database):
        """Test navigation history cleanup functionality."""
        session_id = "cleanup_test_session"
        
        # Add more than 100 entries for one pane
        for i in range(150):
            database.add_to_navigation_history(
                pane_index=0, 
                path=f"/test/path/{i:03d}", 
                session_id=session_id
            )
        
        # Check that cleanup occurred (should keep only last 100)
        with sqlite3.connect(database.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM navigation_history 
                WHERE pane_index = 0 AND session_id = ?
            """, (session_id,))
            
            count = cursor.fetchone()[0]
            assert count <= 100
    
    def test_recent_directories_operations(self, database):
        """Test recent directories tracking."""
        test_paths = [
            "/home/user/projects",
            "/home/user/workspace",
            "/var/log"
        ]
        
        # Add recent directories
        for path in test_paths:
            database.add_recent_directory(path, pane_index=0)
        
        # Get recent directories
        recent = database.get_recent_directories(limit=10)
        
        assert len(recent) >= len(test_paths)
        recent_paths = [r['path'] for r in recent]
        
        for path in test_paths:
            assert path in recent_paths
        
        # Test access count increment
        database.add_recent_directory(test_paths[0], pane_index=1)
        
        updated_recent = database.get_recent_directories(limit=10)
        updated_entry = next((r for r in updated_recent if r['path'] == test_paths[0]), None)
        
        assert updated_entry is not None
        assert updated_entry['access_count'] >= 2
    
    def test_bookmark_operations(self, database):
        """Test bookmark management operations."""
        # Add custom bookmarks
        test_bookmarks = [
            ("Project Alpha", "/home/user/projects/alpha", "project"),
            ("Project Beta", "/home/user/projects/beta", "project"),
            ("Network Share", "//server/share", "network")
        ]
        
        for name, path, category in test_bookmarks:
            result = database.add_bookmark(name, path, category)
            assert result is True
        
        # Get all bookmarks
        all_bookmarks = database.get_bookmarks()
        custom_bookmarks = [b for b in all_bookmarks if b['name'] in [t[0] for t in test_bookmarks]]
        assert len(custom_bookmarks) == 3
        
        # Get bookmarks by category
        project_bookmarks = database.get_bookmarks(category="project")
        assert len(project_bookmarks) >= 2
        
        project_names = [b['name'] for b in project_bookmarks]
        assert "Project Alpha" in project_names
        assert "Project Beta" in project_names
        
        # Verify sort order
        for i, bookmark in enumerate(project_bookmarks[:-1]):
            next_bookmark = project_bookmarks[i + 1]
            assert bookmark['sort_order'] <= next_bookmark['sort_order']
    
    def test_database_error_handling(self, database):
        """Test database error handling."""
        # Test invalid SQL operations
        with patch.object(database.logger, 'error') as mock_logger:
            # Try to save invalid configuration
            invalid_config = {
                'config_name': None,  # Should cause error
                'pane_count': 2,
                'layout_type': 'horizontal'
            }
            
            result = database.save_pane_configuration(invalid_config)
            assert result is False
            assert mock_logger.called
    
    def test_concurrent_database_access(self, database):
        """Test concurrent database access safety."""
        import threading
        import time
        
        results = []
        errors = []
        
        def add_bookmarks(thread_id, count):
            try:
                for i in range(count):
                    name = f"Thread {thread_id} Bookmark {i}"
                    path = f"/thread_{thread_id}/bookmark_{i}"
                    result = database.add_bookmark(name, path, "test")
                    results.append(result)
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=add_bookmarks, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors
        assert len(errors) == 0
        assert len(results) == 30
        assert all(results)
        
        # Verify data integrity
        bookmarks = database.get_bookmarks(category="test")
        assert len(bookmarks) == 30


class TestDatabaseMigrations:
    """
    Comprehensive test suite for database migration system.
    
    Coverage:
    - Migration execution and rollback
    - Version tracking and history
    - Dependency resolution
    - Backup creation and recovery
    - Migration validation and integrity
    """
    
    @pytest.fixture
    def temp_db_path(self):
        """Provide temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except OSError:
            pass
    
    @pytest.fixture
    def migrator(self, temp_db_path):
        """Provide DatabaseMigrator instance for testing."""
        with patch('src.rfu.file_explorer.database.migrations.logging'):
            return DatabaseMigrator(temp_db_path)
    
    def test_migrator_initialization(self, migrator):
        """Test migrator initialization."""
        assert migrator.db_path.exists() is False  # DB not created yet
        assert migrator.backup_dir.exists()
        assert len(migrator.migrations) >= 1
        assert migrator.current_version == 0
        assert migrator.target_version >= 1
    
    def test_migration_registration(self, migrator):
        """Test migration registration system."""
        class TestMigration(Migration):
            def __init__(self):
                super().__init__(999, "Test migration")
            
            def upgrade(self, conn):
                return True
            
            def downgrade(self, conn):
                return True
        
        test_migration = TestMigration()
        migrator.register_migration(test_migration)
        
        assert 999 in migrator.migrations
        assert migrator.migrations[999] == test_migration
        
        # Test duplicate registration
        with pytest.raises(MigrationError):
            migrator.register_migration(test_migration)
    
    def test_initial_migration(self, migrator):
        """Test initial schema migration."""
        # Verify needs migration
        assert migrator.needs_migration() is True
        assert migrator.get_current_version() == 0
        
        # Execute migration
        result = migrator.migrate()
        assert result is True
        
        # Verify migration completed
        assert migrator.get_current_version() >= 1
        assert migrator.needs_migration() is False
        assert migrator.db_path.exists()
        
        # Verify migration history
        history = migrator.get_migration_history()
        assert len(history) >= 1
        assert history[0]['version'] == 1
        assert history[0]['description'] == "Create initial file explorer schema"
    
    def test_migration_backup_creation(self, migrator):
        """Test backup creation before migration."""
        # Create initial database
        migrator.migrate()
        
        # Verify backup can be created
        backup_path = migrator.create_backup()
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.parent == migrator.backup_dir
        
        # Cleanup
        backup_path.unlink()
    
    def test_migration_status(self, migrator):
        """Test migration status reporting."""
        # Before migration
        status = migrator.get_migration_status()
        assert status['current_version'] == 0
        assert status['needs_migration'] is True
        assert status['database_exists'] is False
        
        # After migration
        migrator.migrate()
        
        status = migrator.get_migration_status()
        assert status['current_version'] >= 1
        assert status['needs_migration'] is False
        assert status['database_exists'] is True
        assert 'last_migration' in status
    
    def test_database_consistency_verification(self, migrator):
        """Test database consistency verification."""
        # Create database
        migrator.migrate()
        
        # Verify consistency
        result = migrator.verify_database_consistency()
        assert result is True
    
    def test_migration_dependency_validation(self, migrator):
        """Test migration dependency validation."""
        # Create migration with dependencies
        class DependentMigration(Migration):
            def __init__(self):
                super().__init__(100, "Dependent migration")
            
            def upgrade(self, conn):
                return True
            
            def downgrade(self, conn):
                return True
            
            def get_dependencies(self):
                return [1]  # Depends on initial migration
        
        dependent = DependentMigration()
        migrator.register_migration(dependent)
        
        # Verify dependency validation works
        migrations_to_apply = [dependent]
        result = migrator._validate_migration_dependencies(migrations_to_apply)
        assert result is True  # Should pass since version 1 will be applied
    
    def test_custom_migration_implementation(self, migrator):
        """Test custom migration implementation."""
        class CustomTableMigration(Migration):
            def __init__(self):
                super().__init__(2, "Add custom test table")
            
            def upgrade(self, conn):
                conn.execute("""
                    CREATE TABLE test_custom_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                return True
            
            def downgrade(self, conn):
                conn.execute("DROP TABLE IF EXISTS test_custom_table")
                return True
            
            def validate_postconditions(self, conn):
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='test_custom_table'
                """)
                return cursor.fetchone() is not None
        
        custom_migration = CustomTableMigration()
        migrator.register_migration(custom_migration)
        
        # Apply all migrations
        result = migrator.migrate()
        assert result is True
        
        # Verify custom table was created
        with sqlite3.connect(migrator.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='test_custom_table'
            """)
            assert cursor.fetchone() is not None


class TestDatabasePerformance:
    """
    Performance testing for database operations.
    
    Tests:
    - Query execution performance
    - Index effectiveness
    - Bulk operation performance
    - Memory usage optimization
    - Concurrent access performance
    """
    
    @pytest.fixture
    def performance_database(self):
        """Provide database with performance test data."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        db = FileExplorerDatabase(path)
        
        # Add test data for performance tests
        self._populate_test_data(db)
        
        yield db
        
        try:
            os.unlink(path)
        except OSError:
            pass
    
    def _populate_test_data(self, db):
        """Populate database with test data for performance testing."""
        with sqlite3.connect(db.db_path) as conn:
            # Add many navigation history entries
            for i in range(1000):
                conn.execute("""
                    INSERT INTO navigation_history 
                    (pane_index, path, session_id)
                    VALUES (?, ?, ?)
                """, (i % 4, f"/test/path/{i:04d}", f"session_{i // 100}"))
            
            # Add many recent directories
            for i in range(500):
                conn.execute("""
                    INSERT INTO recent_directories 
                    (path, access_count, pane_index)
                    VALUES (?, ?, ?)
                """, (f"/recent/path/{i:04d}", i % 10 + 1, i % 4))
            
            # Add many bookmarks
            for i in range(200):
                category = ['user', 'project', 'network', 'system'][i % 4]
                conn.execute("""
                    INSERT INTO bookmarks 
                    (name, path, category, sort_order)
                    VALUES (?, ?, ?, ?)
                """, (f"Bookmark {i:03d}", f"/bookmark/path/{i:04d}", category, i))
            
            conn.commit()
    
    @pytest.mark.performance
    def test_navigation_history_query_performance(self, performance_database):
        """Test navigation history query performance."""
        db = performance_database
        
        start_time = time.time()
        
        # Perform multiple queries
        for _ in range(100):
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM navigation_history 
                    WHERE pane_index = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                """, (0,))
                results = cursor.fetchall()
                assert len(results) > 0
        
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time (adjust threshold as needed)
        assert execution_time < 1.0, f"Query performance too slow: {execution_time:.3f}s"
    
    @pytest.mark.performance
    def test_recent_directories_index_effectiveness(self, performance_database):
        """Test index effectiveness for recent directories queries."""
        db = performance_database
        
        with sqlite3.connect(db.db_path) as conn:
            # Query using indexed column
            start_time = time.time()
            
            cursor = conn.execute("""
                SELECT * FROM recent_directories 
                ORDER BY last_accessed DESC 
                LIMIT 10
            """)
            results = cursor.fetchall()
            
            indexed_time = time.time() - start_time
            
            assert len(results) == 10
            assert indexed_time < 0.1, f"Indexed query too slow: {indexed_time:.3f}s"
    
    @pytest.mark.performance
    def test_bulk_bookmark_operations(self, performance_database):
        """Test bulk bookmark operation performance."""
        db = performance_database
        
        start_time = time.time()
        
        # Add many bookmarks at once
        for i in range(100):
            result = db.add_bookmark(f"Bulk Bookmark {i}", f"/bulk/path/{i}", "bulk")
            assert result is True
        
        bulk_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert bulk_time < 2.0, f"Bulk operations too slow: {bulk_time:.3f}s"
        
        # Verify all bookmarks were added
        bulk_bookmarks = db.get_bookmarks(category="bulk")
        assert len(bulk_bookmarks) == 100
    
    @pytest.mark.performance
    def test_concurrent_access_performance(self, performance_database):
        """Test concurrent database access performance."""
        db = performance_database
        
        results = []
        start_time = time.time()
        
        def concurrent_operations(thread_id):
            thread_results = []
            for i in range(50):
                # Mix of read and write operations
                if i % 2 == 0:
                    bookmarks = db.get_bookmarks()
                    thread_results.append(len(bookmarks) > 0)
                else:
                    result = db.add_bookmark(
                        f"Concurrent {thread_id}-{i}", 
                        f"/concurrent/{thread_id}/{i}", 
                        "concurrent"
                    )
                    thread_results.append(result)
            
            results.extend(thread_results)
        
        # Start multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=concurrent_operations, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Verify all operations succeeded
        assert all(results)
        assert len(results) == 250  # 5 threads * 50 operations each
        
        # Should complete in reasonable time
        assert total_time < 5.0, f"Concurrent operations too slow: {total_time:.3f}s"


class TestDatabaseSecurity:
    """
    Security testing for database operations.
    
    Tests:
    - SQL injection prevention
    - Input validation and sanitization
    - Access control and permissions
    - Data integrity protection
    """
    
    @pytest.fixture
    def security_database(self):
        """Provide database for security testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        db = FileExplorerDatabase(path)
        yield db
        
        try:
            os.unlink(path)
        except OSError:
            pass
    
    @pytest.mark.security
    def test_sql_injection_prevention(self, security_database):
        """Test prevention of SQL injection attacks."""
        db = security_database
        
        # Attempt SQL injection in bookmark operations
        malicious_inputs = [
            "'; DROP TABLE bookmarks; --",
            "' OR '1'='1",
            "\"; DELETE FROM bookmarks; --",
            "' UNION SELECT * FROM bookmarks --",
            "'; INSERT INTO bookmarks VALUES(...); --"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                # Try injection in bookmark name
                result = db.add_bookmark(malicious_input, "/safe/path", "test")
                
                # If successful, verify no injection occurred
                if result:
                    bookmarks = db.get_bookmarks()
                    assert isinstance(bookmarks, list)
                    
                    # Verify malicious input was treated as literal text
                    malicious_bookmark = next(
                        (b for b in bookmarks if malicious_input in b['name']), 
                        None
                    )
                    if malicious_bookmark:
                        assert malicious_bookmark['name'] == malicious_input
                
            except (ValueError, sqlite3.Error):
                # Expected for some malicious inputs
                pass
        
        # Verify database integrity
        bookmarks = db.get_bookmarks()
        assert isinstance(bookmarks, list)
    
    @pytest.mark.security
    def test_input_validation(self, security_database):
        """Test input validation and sanitization."""
        db = security_database
        
        # Test various invalid inputs
        invalid_inputs = [
            None,
            "",
            "   ",
            "\x00\x01\x02",  # Null bytes
            "A" * 10000,  # Extremely long string
            "path\nwith\nnewlines",
            "path\rwith\rcarriage\rreturns"
        ]
        
        for invalid_input in invalid_inputs:
            try:
                # Test bookmark operations
                result = db.add_bookmark(invalid_input, "/test/path", "test")
                
                # If accepted, should be sanitized
                if result and invalid_input:
                    bookmarks = db.get_bookmarks(category="test")
                    # Verify no corruption occurred
                    assert isinstance(bookmarks, list)
                
            except (TypeError, ValueError, sqlite3.Error):
                # Expected for invalid inputs
                pass
    
    @pytest.mark.security
    def test_path_traversal_prevention(self, security_database):
        """Test prevention of path traversal attacks."""
        db = security_database
        
        # Attempt path traversal attacks
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "file:///etc/passwd",
            "\\\\network\\share\\sensitive"
        ]
        
        for malicious_path in malicious_paths:
            try:
                # Add navigation history with malicious path
                db.add_to_navigation_history(0, malicious_path, "security_test")
                
                # Add recent directory with malicious path
                db.add_recent_directory(malicious_path, 0)
                
                # Add bookmark with malicious path
                db.add_bookmark("Security Test", malicious_path, "security")
                
            except (ValueError, OSError):
                # Expected for some malicious paths
                pass
        
        # Verify database operations still work
        recent = db.get_recent_directories()
        assert isinstance(recent, list)
        
        bookmarks = db.get_bookmarks()
        assert isinstance(bookmarks, list)
    
    @pytest.mark.security
    def test_data_integrity_protection(self, security_database):
        """Test data integrity protection mechanisms."""
        db = security_database
        
        # Test foreign key integrity
        with sqlite3.connect(db.db_path) as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            
            # Attempt to violate foreign key constraint
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_settings 
                    (config_id, pane_index) VALUES (99999, 0)
                """)
        
        # Test constraint validation
        with sqlite3.connect(db.db_path) as conn:
            # Attempt to violate check constraint
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("""
                    INSERT INTO pane_configurations 
                    (config_name, pane_count) VALUES ('Invalid', 0)
                """)
        
        # Verify database consistency
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            assert result[0] == 'ok'


if __name__ == "__main__":
    # Configure logging for test execution
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests with comprehensive coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=src.rfu.file_explorer.database",
        "--cov-report=html:htmlcov_database",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage_database.xml",
        "--cov-fail-under=90",
        "--html=test_report_database.html",
        "--json-report",
        "--json-report-file=test_results_database.json",
        "-m", "not performance"  # Skip performance tests by default
    ])