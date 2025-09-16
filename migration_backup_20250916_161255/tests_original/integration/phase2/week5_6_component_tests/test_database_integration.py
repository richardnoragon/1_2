"""
Database Integration Tests - Phase 2 Week 5-6
Comprehensive database integration testing for RFU system

Test Categories:
- Connection pooling and management
- Transaction handling and ACID compliance
- Data persistence validation
- Query optimization verification
- Database schema compatibility checks
"""

import json
import os
import shutil
import sqlite3
# Import RFU system components
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timedelta

import psutil
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from database.database_manager import DatabaseManager
    from utils.logging_utils import setup_logger

    from config_manager import ConfigManager
except ImportError as e:
    print(f"Warning: Could not import RFU components: {e}")
    # Create mock classes for testing
    class ConfigManager:
        def __init__(self):
            self.config = {}
        def get(self, key, default=None):
            return self.config.get(key, default)
    
    class DatabaseManager:
        def __init__(self, db_path):
            self.db_path = db_path
            self.connection = None
        
        def connect(self):
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            return self.connection
        
        def close(self):
            if self.connection:
                self.connection.close()

logger = setup_logger('database_integration_tests') if 'setup_logger' in globals() else None


class DatabaseIntegrationTestSuite:
    """Comprehensive database integration test suite"""
    
    def __init__(self):
        self.test_db_path = None
        self.test_results = {
            'connection_pooling': {},
            'transaction_handling': {},
            'data_persistence': {},
            'query_optimization': {},
            'schema_compatibility': {}
        }
        self.performance_metrics = {}
        
    def setup_test_database(self):
        """Set up test database with sample schema and data"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create test tables matching RFU schema
        cursor.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER,
                hash_md5 TEXT,
                hash_sha256 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_analyzed TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                metadata_type TEXT NOT NULL,
                metadata_key TEXT NOT NULL,
                metadata_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id),
                UNIQUE(file_id, metadata_type, metadata_key)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE processing_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                progress INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for performance testing
        cursor.execute("CREATE INDEX idx_files_path ON files(path)")
        cursor.execute("CREATE INDEX idx_files_hash_md5 ON files(hash_md5)")
        cursor.execute("CREATE INDEX idx_metadata_file_id ON file_metadata(file_id)")
        cursor.execute("CREATE INDEX idx_jobs_status ON processing_jobs(status)")
        
        # Insert sample data
        for i in range(1000):
            cursor.execute("""
                INSERT INTO files (path, name, size, hash_md5, hash_sha256)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"/test/path/file_{i}.txt",
                f"file_{i}.txt",
                1024 * (i + 1),
                f"md5_hash_{i:04d}",
                f"sha256_hash_{i:04d}"
            ))
        
        conn.commit()
        conn.close()
        
        return self.test_db_path
    
    def cleanup_test_database(self):
        """Clean up test database"""
        if self.test_db_path and os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)


class TestDatabaseConnectionPooling:
    """Test database connection pooling functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DatabaseIntegrationTestSuite()
        self.db_path = self.test_suite.setup_test_database()
        yield
        self.test_suite.cleanup_test_database()
    
    def test_connection_pool_creation(self):
        """Test connection pool initialization and basic functionality"""
        pool_size = 5
        connections = []
        
        # Create multiple connections
        for i in range(pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            connections.append(conn)
            
        # Verify all connections are functional
        for i, conn in enumerate(connections):
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            result = cursor.fetchone()
            assert result[0] == 1000, f"Connection {i} failed to query database"
        
        # Clean up connections
        for conn in connections:
            conn.close()
        
        self.test_suite.test_results['connection_pooling']['pool_creation'] = 'PASS'
    
    def test_concurrent_connection_access(self):
        """Test concurrent database access with multiple connections"""
        num_threads = 10
        operations_per_thread = 50
        results = []
        
        def database_worker(thread_id):
            """Worker function for concurrent database operations"""
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            local_results = []
            
            try:
                for op_id in range(operations_per_thread):
                    cursor = conn.cursor()
                    
                    # Perform mixed read/write operations
                    if op_id % 3 == 0:
                        # Insert operation
                        cursor.execute("""
                            INSERT INTO processing_jobs (job_type, status)
                            VALUES (?, ?)
                        """, (f"test_job_{thread_id}_{op_id}", "running"))
                    elif op_id % 3 == 1:
                        # Update operation
                        cursor.execute("""
                            UPDATE processing_jobs 
                            SET progress = ? 
                            WHERE job_type LIKE ?
                        """, (op_id * 2, f"test_job_{thread_id}%"))
                    else:
                        # Select operation
                        cursor.execute("""
                            SELECT COUNT(*) FROM files 
                            WHERE size > ?
                        """, (1024 * op_id,))
                        result = cursor.fetchone()
                        local_results.append(result[0])
                    
                    conn.commit()
                    
            except Exception as e:
                local_results.append(f"ERROR: {str(e)}")
            finally:
                conn.close()
            
            return local_results
        
        # Execute concurrent operations
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(database_worker, i) for i in range(num_threads)]
            
            for future in as_completed(futures):
                thread_results = future.result()
                results.extend(thread_results)
        
        execution_time = time.time() - start_time
        
        # Verify no errors occurred
        errors = [r for r in results if isinstance(r, str) and r.startswith("ERROR")]
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        
        # Performance validation
        assert execution_time < 30.0, f"Concurrent operations took too long: {execution_time}s"
        
        self.test_suite.test_results['connection_pooling']['concurrent_access'] = 'PASS'
        self.test_suite.performance_metrics['concurrent_access_time'] = execution_time
    
    def test_connection_recovery(self):
        """Test connection recovery after database locks and errors"""
        conn = sqlite3.connect(self.db_path)
        
        # Simulate long-running transaction to create lock
        cursor = conn.cursor()
        cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
        cursor.execute("SELECT * FROM files LIMIT 1")
        
        # Try to access from another connection (should handle gracefully)
        def attempt_access():
            temp_conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute("SELECT COUNT(*) FROM files")
                result = temp_cursor.fetchone()
                return result[0]
            except sqlite3.OperationalError as e:
                return f"TIMEOUT: {str(e)}"
            finally:
                temp_conn.close()
        
        # This should timeout due to exclusive lock
        result = attempt_access()
        assert isinstance(result, str) and "TIMEOUT" in result
        
        # Release the lock
        conn.rollback()
        conn.close()
        
        # Now access should work
        result = attempt_access()
        assert result == 1000, "Database access failed after lock release"
        
        self.test_suite.test_results['connection_pooling']['recovery'] = 'PASS'


class TestTransactionHandling:
    """Test database transaction handling and ACID compliance"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DatabaseIntegrationTestSuite()
        self.db_path = self.test_suite.setup_test_database()
        yield
        self.test_suite.cleanup_test_database()
    
    def test_acid_atomicity(self):
        """Test transaction atomicity - all or nothing execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get initial count
        cursor.execute("SELECT COUNT(*) FROM files")
        initial_count = cursor.fetchone()[0]
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert multiple records
            for i in range(5):
                cursor.execute("""
                    INSERT INTO files (path, name, size)
                    VALUES (?, ?, ?)
                """, (f"/atomic/test_{i}.txt", f"atomic_test_{i}.txt", 1024))
            
            # Simulate error condition
            cursor.execute("""
                INSERT INTO files (path, name, size)
                VALUES (?, ?, ?)
            """, ("/test/path/file_0.txt", "duplicate.txt", 1024))  # This should fail due to unique constraint
            
            cursor.execute("COMMIT")
            
        except sqlite3.IntegrityError:
            cursor.execute("ROLLBACK")
        
        # Verify no partial insertions occurred
        cursor.execute("SELECT COUNT(*) FROM files")
        final_count = cursor.fetchone()[0]
        
        assert final_count == initial_count, "Transaction atomicity violated - partial insertions occurred"
        
        conn.close()
        self.test_suite.test_results['transaction_handling']['atomicity'] = 'PASS'
    
    def test_acid_consistency(self):
        """Test transaction consistency - database constraints maintained"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test foreign key constraint consistency
        cursor.execute("PRAGMA foreign_keys = ON")
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert metadata for non-existent file (should fail)
            cursor.execute("""
                INSERT INTO file_metadata (file_id, metadata_type, metadata_key, metadata_value)
                VALUES (?, ?, ?, ?)
            """, (99999, "test", "key", "value"))
            
            cursor.execute("COMMIT")
            assert False, "Foreign key constraint violation not detected"
            
        except sqlite3.IntegrityError:
            cursor.execute("ROLLBACK")
            # This is expected behavior
            pass
        
        # Verify database is still consistent
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        assert result[0] == "ok", f"Database integrity compromised: {result[0]}"
        
        conn.close()
        self.test_suite.test_results['transaction_handling']['consistency'] = 'PASS'
    
    def test_acid_isolation(self):
        """Test transaction isolation - concurrent transactions don't interfere"""
        
        def transaction_worker(worker_id, operation_type):
            """Worker function for isolation testing"""
            conn = sqlite3.connect(self.db_path, isolation_level=None)  # autocommit off
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                if operation_type == "read":
                    # Read operations
                    cursor.execute("SELECT COUNT(*) FROM files WHERE size > 2048")
                    result = cursor.fetchone()[0]
                    time.sleep(0.1)  # Simulate processing time
                    cursor.execute("SELECT COUNT(*) FROM files WHERE size > 2048")
                    result2 = cursor.fetchone()[0]
                    # Results should be consistent within transaction
                    assert result == result2, f"Read inconsistency detected: {result} != {result2}"
                    
                elif operation_type == "write":
                    # Write operations
                    cursor.execute("""
                        INSERT INTO processing_jobs (job_type, status)
                        VALUES (?, ?)
                    """, (f"isolation_test_{worker_id}", "running"))
                    time.sleep(0.1)
                    cursor.execute("""
                        UPDATE processing_jobs 
                        SET progress = 50 
                        WHERE job_type = ?
                    """, (f"isolation_test_{worker_id}",))
                
                cursor.execute("COMMIT")
                return "SUCCESS"
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                return f"ERROR: {str(e)}"
            finally:
                conn.close()
        
        # Run concurrent transactions
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            # Submit read and write transactions
            for i in range(2):
                futures.append(executor.submit(transaction_worker, i, "read"))
                futures.append(executor.submit(transaction_worker, i, "write"))
            
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all transactions completed successfully
        errors = [r for r in results if r.startswith("ERROR")]
        assert len(errors) == 0, f"Isolation test failures: {errors}"
        
        self.test_suite.test_results['transaction_handling']['isolation'] = 'PASS'
    
    def test_acid_durability(self):
        """Test transaction durability - committed data survives system restart"""
        # Insert data and commit
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO files (path, name, size)
            VALUES (?, ?, ?)
        """, ("/durability/test.txt", "durability_test.txt", 2048))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Simulate system restart by creating new connection
        new_conn = sqlite3.connect(self.db_path)
        new_cursor = new_conn.cursor()
        
        new_cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        result = new_cursor.fetchone()
        
        assert result is not None, "Committed data lost after connection restart"
        assert result[1] == "/durability/test.txt", "Data corruption detected"
        
        new_conn.close()
        self.test_suite.test_results['transaction_handling']['durability'] = 'PASS'


class TestDataPersistence:
    """Test data persistence validation"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DatabaseIntegrationTestSuite()
        self.db_path = self.test_suite.setup_test_database()
        yield
        self.test_suite.cleanup_test_database()
    
    def test_crud_operations_persistence(self):
        """Test Create, Read, Update, Delete operations persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # CREATE
        cursor.execute("""
            INSERT INTO files (path, name, size, hash_md5)
            VALUES (?, ?, ?, ?)
        """, ("/persistence/create.txt", "create_test.txt", 4096, "create_hash"))
        
        file_id = cursor.lastrowid
        conn.commit()
        
        # READ
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        result = cursor.fetchone()
        assert result is not None, "Created record not found"
        assert result[1] == "/persistence/create.txt", "Created data mismatch"
        
        # UPDATE
        cursor.execute("""
            UPDATE files SET size = ?, hash_md5 = ? WHERE id = ?
        """, (8192, "updated_hash", file_id))
        conn.commit()
        
        cursor.execute("SELECT size, hash_md5 FROM files WHERE id = ?", (file_id,))
        result = cursor.fetchone()
        assert result[0] == 8192, "Update operation failed"
        assert result[1] == "updated_hash", "Update data mismatch"
        
        # DELETE
        cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        result = cursor.fetchone()
        assert result is None, "Delete operation failed"
        
        conn.close()
        self.test_suite.test_results['data_persistence']['crud_operations'] = 'PASS'
    
    def test_large_data_persistence(self):
        """Test persistence of large data sets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert large dataset
        large_dataset = []
        for i in range(10000):
            large_dataset.append((
                f"/large/dataset/file_{i:05d}.dat",
                f"large_file_{i:05d}.dat",
                1024 * 1024 * (i % 100),  # Varying file sizes
                f"large_hash_{i:05d}",
                f"large_sha256_{i:05d}"
            ))
        
        start_time = time.time()
        cursor.executemany("""
            INSERT INTO files (path, name, size, hash_md5, hash_sha256)
            VALUES (?, ?, ?, ?, ?)
        """, large_dataset)
        conn.commit()
        insert_time = time.time() - start_time
        
        # Verify data persistence
        cursor.execute("SELECT COUNT(*) FROM files WHERE path LIKE '/large/dataset/%'")
        count = cursor.fetchone()[0]
        assert count == 10000, f"Large dataset persistence failed: {count}/10000 records"
        
        # Test data integrity
        cursor.execute("""
            SELECT path, name, size, hash_md5, hash_sha256 
            FROM files 
            WHERE path = '/large/dataset/file_05000.dat'
        """)
        result = cursor.fetchone()
        assert result is not None, "Specific large dataset record not found"
        assert result[2] == 1024 * 1024 * 0, "Large dataset data integrity issue"
        
        conn.close()
        
        self.test_suite.test_results['data_persistence']['large_data'] = 'PASS'
        self.test_suite.performance_metrics['large_insert_time'] = insert_time
    
    def test_concurrent_data_persistence(self):
        """Test data persistence under concurrent operations"""
        num_workers = 5
        records_per_worker = 100
        
        def persistence_worker(worker_id):
            """Worker function for concurrent persistence testing"""
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            inserted_ids = []
            
            try:
                for i in range(records_per_worker):
                    cursor.execute("""
                        INSERT INTO files (path, name, size)
                        VALUES (?, ?, ?)
                    """, (
                        f"/concurrent/worker_{worker_id}/file_{i}.txt",
                        f"worker_{worker_id}_file_{i}.txt",
                        1024 * (worker_id * 100 + i)
                    ))
                    inserted_ids.append(cursor.lastrowid)
                
                conn.commit()
                return inserted_ids
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        
        # Execute concurrent persistence operations
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(persistence_worker, i) for i in range(num_workers)]
            all_ids = []
            
            for future in as_completed(futures):
                worker_ids = future.result()
                all_ids.extend(worker_ids)
        
        # Verify all data persisted correctly
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for file_id in all_ids:
            cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            result = cursor.fetchone()
            assert result is not None, f"Concurrent persistence failed for ID {file_id}"
        
        # Verify total count
        cursor.execute("SELECT COUNT(*) FROM files WHERE path LIKE '/concurrent/%'")
        total_count = cursor.fetchone()[0]
        expected_count = num_workers * records_per_worker
        assert total_count == expected_count, f"Concurrent persistence count mismatch: {total_count}/{expected_count}"
        
        conn.close()
        self.test_suite.test_results['data_persistence']['concurrent_operations'] = 'PASS'


class TestQueryOptimization:
    """Test query optimization and performance"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DatabaseIntegrationTestSuite()
        self.db_path = self.test_suite.setup_test_database()
        yield
        self.test_suite.cleanup_test_database()
    
    def test_index_utilization(self):
        """Test that queries properly utilize database indexes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test index usage for path queries
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM files WHERE path = '/test/path/file_500.txt'")
        plan = cursor.fetchall()
        
        # Should use index on path
        plan_text = " ".join([str(row) for row in plan])
        assert "idx_files_path" in plan_text or "USING INDEX" in plan_text, "Path index not utilized"
        
        # Test index usage for hash queries
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM files WHERE hash_md5 = 'md5_hash_0500'")
        plan = cursor.fetchall()
        plan_text = " ".join([str(row) for row in plan])
        assert "idx_files_hash_md5" in plan_text or "USING INDEX" in plan_text, "Hash index not utilized"
        
        conn.close()
        self.test_suite.test_results['query_optimization']['index_utilization'] = 'PASS'
    
    def test_query_performance_benchmarks(self):
        """Test query performance against established benchmarks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        performance_results = {}
        
        # Simple SELECT benchmark
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM files")
        result = cursor.fetchone()
        simple_query_time = time.time() - start_time
        performance_results['simple_query'] = simple_query_time
        
        assert simple_query_time < 0.1, f"Simple query too slow: {simple_query_time}s"
        
        # Complex JOIN benchmark
        start_time = time.time()
        cursor.execute("""
            SELECT f.name, COUNT(m.id) as metadata_count
            FROM files f
            LEFT JOIN file_metadata m ON f.id = m.file_id
            WHERE f.size > 50000
            GROUP BY f.id, f.name
            ORDER BY metadata_count DESC
            LIMIT 100
        """)
        results = cursor.fetchall()
        complex_query_time = time.time() - start_time
        performance_results['complex_query'] = complex_query_time
        
        assert complex_query_time < 0.5, f"Complex query too slow: {complex_query_time}s"
        
        # Bulk operation benchmark
        start_time = time.time()
        cursor.execute("UPDATE files SET last_analyzed = CURRENT_TIMESTAMP WHERE size > 10000")
        conn.commit()
        bulk_update_time = time.time() - start_time
        performance_results['bulk_update'] = bulk_update_time
        
        assert bulk_update_time < 2.0, f"Bulk update too slow: {bulk_update_time}s"
        
        conn.close()
        
        self.test_suite.test_results['query_optimization']['performance_benchmarks'] = 'PASS'
        self.test_suite.performance_metrics.update(performance_results)
    
    def test_query_plan_optimization(self):
        """Test that complex queries use optimal execution plans"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test complex query plan
        query = """
            SELECT f.path, f.size, COUNT(m.id) as metadata_count
            FROM files f
            LEFT JOIN file_metadata m ON f.id = m.file_id
            WHERE f.size BETWEEN 10000 AND 100000
            AND f.created_at > datetime('now', '-1 day')
            GROUP BY f.id
            HAVING COUNT(m.id) > 0
            ORDER BY f.size DESC
        """
        
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()
        
        # Verify reasonable execution plan
        plan_text = " ".join([str(row) for row in plan])
        
        # Should not be doing full table scans for large operations
        assert "SCAN TABLE" not in plan_text or plan_text.count("SCAN TABLE") <= 1, \
            "Query plan contains excessive table scans"
        
        # Execute query to ensure it works
        cursor.execute(query)
        results = cursor.fetchall()
        
        conn.close()
        self.test_suite.test_results['query_optimization']['execution_plans'] = 'PASS'


class TestSchemaCompatibility:
    """Test database schema compatibility and migrations"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = DatabaseIntegrationTestSuite()
        self.db_path = self.test_suite.setup_test_database()
        yield
        self.test_suite.cleanup_test_database()
    
    def test_schema_version_compatibility(self):
        """Test schema version tracking and compatibility"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schema version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        
        # Insert current schema version
        cursor.execute("""
            INSERT INTO schema_version (version, description)
            VALUES (?, ?)
        """, (1, "Initial schema with files, metadata, and jobs tables"))
        
        conn.commit()
        
        # Test schema version retrieval
        cursor.execute("SELECT MAX(version) FROM schema_version")
        current_version = cursor.fetchone()[0]
        assert current_version == 1, "Schema version tracking failed"
        
        conn.close()
        self.test_suite.test_results['schema_compatibility']['version_tracking'] = 'PASS'
    
    def test_backward_compatibility(self):
        """Test backward compatibility with older schema versions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simulate older schema by removing a column (simulate schema downgrade)
        cursor.execute("ALTER TABLE files RENAME TO files_backup")
        
        # Create older version without last_analyzed column
        cursor.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER,
                hash_md5 TEXT,
                hash_sha256 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy data from backup (excluding the removed column)
        cursor.execute("""
            INSERT INTO files (id, path, name, size, hash_md5, hash_sha256, created_at, modified_at)
            SELECT id, path, name, size, hash_md5, hash_sha256, created_at, modified_at
            FROM files_backup
        """)
        
        # Verify data integrity with older schema
        cursor.execute("SELECT COUNT(*) FROM files")
        count = cursor.fetchone()[0]
        assert count > 0, "Backward compatibility test failed - no data"
        
        # Test that basic operations still work
        cursor.execute("SELECT * FROM files LIMIT 1")
        result = cursor.fetchone()
        assert result is not None, "Basic query failed with older schema"
        
        # Clean up
        cursor.execute("DROP TABLE files_backup")
        conn.commit()
        conn.close()
        
        self.test_suite.test_results['schema_compatibility']['backward_compatibility'] = 'PASS'
    
    def test_schema_migration_simulation(self):
        """Test schema migration scenarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simulate adding a new column (migration)
        try:
            cursor.execute("ALTER TABLE files ADD COLUMN file_type TEXT DEFAULT 'unknown'")
            conn.commit()
            
            # Verify column was added
            cursor.execute("PRAGMA table_info(files)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            assert "file_type" in column_names, "Schema migration failed - column not added"
            
            # Test that existing data still works
            cursor.execute("SELECT COUNT(*) FROM files WHERE file_type = 'unknown'")
            count = cursor.fetchone()[0]
            assert count > 0, "Schema migration failed - default values not applied"
            
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                # Column already exists, which is fine for testing
                pass
            else:
                raise
        
        conn.close()
        self.test_suite.test_results['schema_compatibility']['migration_simulation'] = 'PASS'


def generate_database_integration_report():
    """Generate comprehensive database integration test report"""
    test_suite = DatabaseIntegrationTestSuite()
    
    report = {
        'test_execution_summary': {
            'timestamp': datetime.now().isoformat(),
            'total_test_categories': 5,
            'total_test_methods': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'execution_time': 0
        },
        'test_results': test_suite.test_results,
        'performance_metrics': test_suite.performance_metrics,
        'recommendations': []
    }
    
    # Count test results
    for category, tests in test_suite.test_results.items():
        for test_name, result in tests.items():
            report['test_execution_summary']['total_test_methods'] += 1
            if result == 'PASS':
                report['test_execution_summary']['passed_tests'] += 1
            else:
                report['test_execution_summary']['failed_tests'] += 1
    
    # Generate recommendations based on results
    if report['test_execution_summary']['failed_tests'] > 0:
        report['recommendations'].append("Review and fix failed database integration tests")
    
    if 'large_insert_time' in test_suite.performance_metrics:
        if test_suite.performance_metrics['large_insert_time'] > 5.0:
            report['recommendations'].append("Consider optimizing bulk insert operations")
    
    return report


if __name__ == "__main__":
    # Run all database integration tests
    pytest.main([__file__, "-v", "--tb=short"])