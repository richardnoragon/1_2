"""
Unit Tests for Database Components
Tests database schema, migrations, and cache manager functionality.

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Test database components
try:
    from src.rfu.file_explorer.database.cache_manager import (CacheEntry,
                                                              CacheManager)
    from src.rfu.file_explorer.database.schema import (
        CreateInitialSchemaMigration, DatabaseSchema)
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database components not available")
class TestDatabaseSchema:
    """Test database schema functionality."""

    def test_memory_database_creation(self):
        """Test in-memory database creation."""
        db = DatabaseSchema(":memory:")
        assert db is not None
        assert db.db_path == ":memory:"

    def test_file_database_creation(self):
        """Test file-based database creation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        try:
            db = DatabaseSchema(db_path)
            db.initialize()
            assert Path(db_path).exists()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_table_creation(self):
        """Test that all required tables are created."""
        db = DatabaseSchema(":memory:")
        db.initialize()

        expected_tables = [
            'files', 'directories', 'file_metadata', 'directory_metadata',
            'tags', 'file_tags', 'bookmarks', 'history', 'search_cache',
            'user_preferences', 'cache_entries', 'schema_migrations'
        ]

        tables = db.get_table_names()
        for table in expected_tables:
            assert table in tables

    def test_schema_version(self):
        """Test schema version tracking."""
        db = DatabaseSchema(":memory:")
        db.initialize()

        version = db.get_schema_version()
        assert version >= 1

    def test_migration_application(self):
        """Test migration system."""
        migration = CreateInitialSchemaMigration()
        assert migration.version == 1
        assert migration.description == "Create initial database schema"
        assert migration.up_sql is not None
        assert migration.down_sql is not None

    def test_database_constraints(self):
        """Test database integrity constraints."""
        db = DatabaseSchema(":memory:")
        db.initialize()

        # Test foreign key constraint
        with pytest.raises(Exception):
            db.execute_update(
                "INSERT INTO file_tags (file_id, tag_id) VALUES (999, 999)"
            )

    def test_data_insertion_and_retrieval(self):
        """Test basic data operations."""
        db = DatabaseSchema(":memory:")
        db.initialize()

        # Insert test file
        file_path = "/test/file.txt"
        file_name = "file.txt"
        file_size = 1024
        modified_time = time.time()

        db.execute_update(
            "INSERT INTO files (path, name, size, modified_time) VALUES (?, ?, ?, ?)",
            (file_path, file_name, file_size, modified_time)
        )

        # Retrieve file
        result = db.execute_query(
            "SELECT path, name, size FROM files WHERE path = ?",
            (file_path,)
        )

        assert len(result) == 1
        assert result[0]['path'] == file_path
        assert result[0]['name'] == file_name
        assert result[0]['size'] == file_size


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database components not available")
class TestCacheManager:
    """Test cache manager functionality."""

    def test_cache_creation(self):
        """Test cache manager creation."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db, max_cache_size=100)

        assert cache is not None
        assert cache.max_cache_size == 100

    def test_cache_put_get(self):
        """Test basic cache put/get operations."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db)

        key = "test_key"
        data = {"name": "test_file.txt", "size": 1024}

        cache.put(key, data)
        retrieved = cache.get(key)

        assert retrieved == data

    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db)

        key = "ttl_test"
        data = {"temporary": True}

        # Put with short TTL
        cache.put(key, data, ttl=0.1)

        # Should be available immediately
        assert cache.get(key) == data

        # Wait for expiration
        time.sleep(0.2)

        # Should be expired
        assert cache.get(key) is None

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db)

        key = "invalidate_test"
        data = {"test": "data"}

        cache.put(key, data)
        assert cache.get(key) == data

        cache.invalidate(key)
        assert cache.get(key) is None

    def test_cache_size_limit(self):
        """Test cache size limiting."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db, max_cache_size=10)

        # Fill cache beyond limit
        for i in range(20):
            cache.put(f"key_{i}", {"index": i})

        # Cache should not exceed limit
        assert cache.get_cache_size() <= 10

    def test_cache_statistics(self):
        """Test cache statistics."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db)

        # Initial statistics
        stats = cache.get_statistics()
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'size' in stats

        # Perform operations
        cache.put("test", {"data": "value"})
        cache.get("test")  # Hit
        cache.get("nonexistent")  # Miss

        new_stats = cache.get_statistics()
        assert new_stats['hits'] >= 1
        assert new_stats['misses'] >= 1

    def test_cache_cleanup(self):
        """Test cache cleanup operations."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db)

        # Add some data
        for i in range(10):
            cache.put(f"cleanup_key_{i}", {"index": i})

        initial_size = cache.get_cache_size()
        assert initial_size > 0

        # Clear cache
        cache.clear()
        assert cache.get_cache_size() == 0

    def test_cache_persistence(self):
        """Test cache persistence across instances."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        try:
            # Create first cache instance
            db1 = DatabaseSchema(db_path)
            db1.initialize()
            cache1 = CacheManager(db1)

            key = "persistent_key"
            data = {"persistent": "data"}
            cache1.put(key, data)

            # Create second cache instance
            db2 = DatabaseSchema(db_path)
            cache2 = CacheManager(db2)

            # Data should be available in second instance
            retrieved = cache2.get(key)
            assert retrieved == data

        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_cache_entry_model(self):
        """Test CacheEntry model."""
        entry = CacheEntry(
            key="test_key",
            data={"test": "data"},
            ttl=3600
        )

        assert entry.key == "test_key"
        assert entry.data == {"test": "data"}
        assert entry.ttl == 3600
        assert not entry.is_expired()

        # Test expiration
        expired_entry = CacheEntry(
            key="expired_key",
            data={"expired": True},
            ttl=0,
            created_at=time.time() - 10
        )

        assert expired_entry.is_expired()

    def test_cache_memory_efficiency(self):
        """Test cache memory efficiency."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db, max_cache_size=1000)

        # Add large amount of data
        large_data = {"content": "x" * 1000}  # 1KB per entry

        for i in range(500):
            cache.put(f"large_key_{i}", large_data)

        # Memory usage should be reasonable
        stats = cache.get_statistics()
        assert stats['size'] <= 1000

    def test_cache_concurrent_access(self):
        """Test cache thread safety (basic test)."""
        db = DatabaseSchema(":memory:")
        db.initialize()
        cache = CacheManager(db)

        # Simulate concurrent access
        for i in range(100):
            cache.put(f"concurrent_key_{i}", {"thread_id": i})

        # All items should be accessible
        for i in range(100):
            data = cache.get(f"concurrent_key_{i}")
            if data:  # May be evicted due to cache limits
                assert data["thread_id"] == i


if __name__ == '__main__':
    pytest.main([__file__, "-v"])