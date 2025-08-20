"""
Phase 4 Performance Testing Suite

Performance testing to validate <100ms encryption latency, <5% database size increase,
<30s migration completion, and overall system performance under load.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import unittest
import tempfile
import shutil
import os
import time
import sqlite3
import threading
import statistics
import psutil
import gc
from datetime import datetime, timezone

# Import components for performance testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rfu.database.database_manager import DatabaseManager
from rfu.database.migration_manager import MigrationManager
from rfu.core.directory_security.directory_security_manager import DirectorySecurityManager
from rfu.core.directory_security.directory_encryption import DirectoryPathEncryption
from rfu.core.directory_security.pii_detector import PIIDetector
from rfu.core.directory_security.directory_audit import DirectoryAuditLogger


class PerformanceTestEnvironment:
    """Performance test environment setup"""
    
    def __init__(self):
        self.temp_dir = None
        self.db_path = None
        self.db_manager = None
        self.security_manager = None
        self.initial_db_size = 0
    
    def setup(self):
        """Setup performance test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="rfu_performance_test_")
        self.db_path = os.path.join(self.temp_dir, "performance_test.db")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Apply all migrations and measure initial size
        migration_manager = MigrationManager(self.db_manager)
        migration_manager.apply_pending_migrations()
        
        self.initial_db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        # Initialize security manager
        self.security_manager = DirectorySecurityManager(self.db_manager)
        
        return self.security_manager, self.db_manager
    
    def teardown(self):
        """Cleanup performance test environment"""
        if self.db_manager:
            self.db_manager.close()
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def get_current_db_size(self):
        """Get current database size"""
        return os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
    
    def get_db_size_increase_percent(self):
        """Get database size increase percentage"""
        current_size = self.get_current_db_size()
        if self.initial_db_size == 0:
            return 0
        return ((current_size - self.initial_db_size) / self.initial_db_size) * 100


class PerformanceTimer:
    """Utility class for performance timing"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        gc.collect()  # Clean up before timing
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
    
    @property
    def elapsed_time(self):
        """Get elapsed time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def elapsed_ms(self):
        """Get elapsed time in milliseconds"""
        if self.elapsed_time:
            return self.elapsed_time * 1000
        return None


class TestEncryptionPerformance(unittest.TestCase):
    """Test encryption operation performance"""
    
    def setUp(self):
        """Setup encryption performance test environment"""
        self.env = PerformanceTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.encryption = DirectoryPathEncryption()
        self.test_user = "performance_test_user"
    
    def tearDown(self):
        """Cleanup encryption performance test environment"""
        self.env.teardown()
    
    def test_encryption_latency_requirement(self):
        """Test encryption latency <100ms requirement"""
        test_paths = [
            "C:\\Users\\test\\Documents\\Personal\\Financial\\TaxReturns",
            "/home/user/Documents/Personal/Medical/Records/2024",
            "C:\\Very\\Long\\Path\\With\\Many\\Segments\\And\\Unicode\\Characters\\测试\\路径",
            "/short/path",
            "\\\\network\\share\\very\\long\\network\\path\\to\\sensitive\\data"
        ]
        
        encryption_times = []
        decryption_times = []
        
        for test_path in test_paths:
            with self.subTest(path=test_path):
                # Test encryption performance
                with PerformanceTimer("encryption") as timer:
                    encrypt_result = self.encryption.encrypt_directory_path(test_path, self.test_user)
                
                self.assertTrue(encrypt_result.success, f"Encryption should succeed for {test_path}")
                encryption_time = timer.elapsed_ms
                encryption_times.append(encryption_time)
                
                # Verify encryption latency requirement
                self.assertLess(encryption_time, 100, 
                              f"Encryption should be <100ms, got {encryption_time:.2f}ms for {test_path}")
                
                # Test decryption performance
                with PerformanceTimer("decryption") as timer:
                    decrypt_result = self.encryption.decrypt_directory_path(
                        encrypt_result.encrypted_data, encrypt_result.salt,
                        encrypt_result.nonce, self.test_user, encrypt_result.integrity_hash
                    )
                
                self.assertTrue(decrypt_result.success, f"Decryption should succeed for {test_path}")
                decryption_time = timer.elapsed_ms
                decryption_times.append(decryption_time)
                
                # Verify decryption latency requirement
                self.assertLess(decryption_time, 100,
                              f"Decryption should be <100ms, got {decryption_time:.2f}ms for {test_path}")
        
        # Report performance statistics
        avg_encryption_time = statistics.mean(encryption_times)
        avg_decryption_time = statistics.mean(decryption_times)
        max_encryption_time = max(encryption_times)
        max_decryption_time = max(decryption_times)
        
        print(f"\n--- Encryption Performance Results ---")
        print(f"Average encryption time: {avg_encryption_time:.2f}ms")
        print(f"Maximum encryption time: {max_encryption_time:.2f}ms")
        print(f"Average decryption time: {avg_decryption_time:.2f}ms")
        print(f"Maximum decryption time: {max_decryption_time:.2f}ms")
        
        # All operations should be well under 100ms
        self.assertLess(max_encryption_time, 100, "Maximum encryption time should be <100ms")
        self.assertLess(max_decryption_time, 100, "Maximum decryption time should be <100ms")
    
    def test_bulk_encryption_performance(self):
        """Test bulk encryption performance"""
        batch_sizes = [10, 50, 100]
        
        for batch_size in batch_sizes:
            with self.subTest(batch_size=batch_size):
                test_paths = [f"C:\\Users\\test\\Documents\\Batch_{i}\\Personal" 
                             for i in range(batch_size)]
                
                # Test batch encryption
                with PerformanceTimer(f"bulk_encryption_{batch_size}") as timer:
                    results = []
                    for path in test_paths:
                        result = self.encryption.encrypt_directory_path(path, self.test_user)
                        results.append(result)
                
                batch_time = timer.elapsed_time
                avg_time_per_operation = (batch_time / batch_size) * 1000  # Convert to ms
                
                # All operations should succeed
                successful_results = [r for r in results if r.success]
                self.assertEqual(len(successful_results), batch_size, 
                               f"All {batch_size} encryptions should succeed")
                
                # Average time per operation should still be <100ms
                self.assertLess(avg_time_per_operation, 100,
                              f"Average time per encryption in batch of {batch_size} should be <100ms, got {avg_time_per_operation:.2f}ms")
                
                print(f"Batch {batch_size}: Total time {batch_time:.2f}s, Avg per operation {avg_time_per_operation:.2f}ms")
    
    def test_encryption_memory_usage(self):
        """Test encryption memory usage"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Encrypt many paths to test memory usage
        large_paths = [f"C:\\Users\\test\\Documents\\MemoryTest_{i}\\VeryLongDirectoryNameForMemoryTesting" 
                      for i in range(100)]
        
        encrypted_results = []
        for path in large_paths:
            result = self.encryption.encrypt_directory_path(path, self.test_user)
            if result.success:
                encrypted_results.append(result)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        print(f"\n--- Memory Usage Results ---")
        print(f"Initial memory: {initial_memory:.2f} MB")
        print(f"Peak memory: {peak_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Memory increase should be reasonable (less than 50MB for 100 operations)
        self.assertLess(memory_increase, 50, 
                       f"Memory increase should be <50MB, got {memory_increase:.2f}MB")


class TestDirectoryOperationPerformance(unittest.TestCase):
    """Test directory operation performance"""
    
    def setUp(self):
        """Setup directory operation performance test environment"""
        self.env = PerformanceTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.test_user = "directory_performance_user"
    
    def tearDown(self):
        """Cleanup directory operation performance test environment"""
        self.env.teardown()
    
    def test_directory_storage_performance(self):
        """Test directory storage operation performance"""
        test_scenarios = [
            ("simple_path", "C:\\Users\\test\\Documents"),
            ("pii_sensitive", "C:\\Users\\john.doe\\Personal\\Financial"),
            ("long_path", "C:\\Very\\Long\\Path\\With\\Many\\Segments\\And\\Special\\Characters\\测试\\ñoñó\\🔒"),
            ("network_path", "\\\\server\\share\\department\\personal"),
        ]
        
        storage_times = []
        retrieval_times = []
        stored_hashes = []
        
        for scenario_name, test_path in test_scenarios:
            with self.subTest(scenario=scenario_name, path=test_path):
                # Test storage performance
                with PerformanceTimer(f"store_{scenario_name}") as timer:
                    storage_result = self.security_manager.store_directory_preference(
                        self.test_user, f"perf_tool_{scenario_name}", "performance", test_path
                    )
                
                storage_time = timer.elapsed_ms
                storage_times.append(storage_time)
                
                self.assertTrue(storage_result.success, f"Storage should succeed for {scenario_name}")
                self.assertLess(storage_time, 100, 
                              f"Storage should be <100ms for {scenario_name}, got {storage_time:.2f}ms")
                
                stored_hashes.append((scenario_name, storage_result.path_hash))
        
        # Test retrieval performance
        for scenario_name, path_hash in stored_hashes:
            with PerformanceTimer(f"retrieve_{scenario_name}") as timer:
                retrieval_result = self.security_manager.retrieve_directory_preference(
                    self.test_user, path_hash
                )
            
            retrieval_time = timer.elapsed_ms
            retrieval_times.append(retrieval_time)
            
            self.assertTrue(retrieval_result.success, f"Retrieval should succeed for {scenario_name}")
            self.assertLess(retrieval_time, 100,
                          f"Retrieval should be <100ms for {scenario_name}, got {retrieval_time:.2f}ms")
        
        # Performance summary
        avg_storage_time = statistics.mean(storage_times)
        avg_retrieval_time = statistics.mean(retrieval_times)
        
        print(f"\n--- Directory Operation Performance ---")
        print(f"Average storage time: {avg_storage_time:.2f}ms")
        print(f"Average retrieval time: {avg_retrieval_time:.2f}ms")
        print(f"Max storage time: {max(storage_times):.2f}ms")
        print(f"Max retrieval time: {max(retrieval_times):.2f}ms")
    
    def test_concurrent_directory_operations(self):
        """Test concurrent directory operation performance"""
        num_threads = 10
        operations_per_thread = 10
        
        results = []
        errors = []
        operation_times = []
        
        def concurrent_operations(thread_id):
            thread_times = []
            try:
                for i in range(operations_per_thread):
                    path = f"C:\\Users\\concurrent_{thread_id}\\Documents\\File_{i}"
                    
                    with PerformanceTimer(f"concurrent_{thread_id}_{i}") as timer:
                        result = self.security_manager.store_directory_preference(
                            f"concurrent_user_{thread_id}", f"tool_{thread_id}_{i}", 
                            "concurrent", path
                        )
                    
                    thread_times.append(timer.elapsed_ms)
                    results.append((thread_id, i, result.success if result else False))
                
                operation_times.extend(thread_times)
            
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Start concurrent threads
        start_time = time.perf_counter()
        threads = []
        
        for i in range(num_threads):
            thread = threading.Thread(target=concurrent_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.perf_counter() - start_time
        
        # Analyze results
        total_operations = num_threads * operations_per_thread
        successful_operations = len([r for r in results if r[2]])
        
        self.assertEqual(len(errors), 0, f"Should have no errors in concurrent operations: {errors}")
        self.assertGreaterEqual(successful_operations, total_operations * 0.95, 
                              "At least 95% of concurrent operations should succeed")
        
        if operation_times:
            avg_concurrent_time = statistics.mean(operation_times)
            max_concurrent_time = max(operation_times)
            
            print(f"\n--- Concurrent Operation Performance ---")
            print(f"Total operations: {total_operations}")
            print(f"Successful operations: {successful_operations}")
            print(f"Total time: {total_time:.2f}s")
            print(f"Operations per second: {successful_operations / total_time:.2f}")
            print(f"Average operation time: {avg_concurrent_time:.2f}ms")
            print(f"Maximum operation time: {max_concurrent_time:.2f}ms")
            
            # Even under concurrent load, operations should be reasonably fast
            self.assertLess(avg_concurrent_time, 200, 
                          f"Average concurrent operation time should be <200ms, got {avg_concurrent_time:.2f}ms")
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        dataset_sizes = [100, 500, 1000]
        
        for size in dataset_sizes:
            with self.subTest(dataset_size=size):
                print(f"\n--- Testing dataset size: {size} ---")
                
                # Create large dataset
                paths = [f"C:\\Users\\dataset_{size}\\Documents\\Directory_{i}" for i in range(size)]
                
                # Test bulk storage
                storage_start = time.perf_counter()
                stored_hashes = []
                
                for i, path in enumerate(paths):
                    result = self.security_manager.store_directory_preference(
                        self.test_user, f"dataset_tool_{i}", "dataset", path
                    )
                    if result.success:
                        stored_hashes.append(result.path_hash)
                    
                    # Progress reporting for large datasets
                    if (i + 1) % 100 == 0:
                        elapsed = time.perf_counter() - storage_start
                        rate = (i + 1) / elapsed
                        print(f"Stored {i + 1}/{size} directories at {rate:.1f} ops/sec")
                
                storage_time = time.perf_counter() - storage_start
                storage_rate = len(stored_hashes) / storage_time
                
                # Test listing performance
                listing_start = time.perf_counter()
                user_directories = self.security_manager.list_user_directories(self.test_user)
                listing_time = time.perf_counter() - listing_start
                
                # Test retrieval performance (sample)
                sample_size = min(50, len(stored_hashes))
                sample_hashes = stored_hashes[:sample_size]
                
                retrieval_start = time.perf_counter()
                successful_retrievals = 0
                
                for hash_val in sample_hashes:
                    result = self.security_manager.retrieve_directory_preference(
                        self.test_user, hash_val
                    )
                    if result.success:
                        successful_retrievals += 1
                
                retrieval_time = time.perf_counter() - retrieval_start
                retrieval_rate = successful_retrievals / retrieval_time if retrieval_time > 0 else 0
                
                print(f"Storage: {len(stored_hashes)} dirs in {storage_time:.2f}s ({storage_rate:.1f} ops/sec)")
                print(f"Listing: {len(user_directories)} dirs in {listing_time:.3f}s")
                print(f"Retrieval: {successful_retrievals} dirs in {retrieval_time:.2f}s ({retrieval_rate:.1f} ops/sec)")
                
                # Performance requirements
                self.assertGreater(storage_rate, 10, f"Storage rate should be >10 ops/sec for dataset {size}")
                self.assertLess(listing_time, 1.0, f"Listing should be <1s for dataset {size}")
                self.assertGreater(retrieval_rate, 20, f"Retrieval rate should be >20 ops/sec for dataset {size}")


class TestDatabasePerformance(unittest.TestCase):
    """Test database performance and size requirements"""
    
    def setUp(self):
        """Setup database performance test environment"""
        self.env = PerformanceTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.test_user = "db_performance_user"
    
    def tearDown(self):
        """Cleanup database performance test environment"""
        self.env.teardown()
    
    def test_database_size_increase_requirement(self):
        """Test database size increase <5% requirement"""
        initial_size = self.env.get_current_db_size()
        print(f"\nInitial database size: {initial_size / 1024:.2f} KB")
        
        # Add substantial amount of test data
        num_directories = 200
        paths_data = []
        
        for i in range(num_directories):
            # Mix of different path types and sensitivities
            if i % 4 == 0:
                path = f"C:\\Users\\user_{i}\\Documents\\Personal\\Financial"
            elif i % 4 == 1:
                path = f"C:\\Users\\user_{i}\\Documents\\Work\\Projects"
            elif i % 4 == 2:
                path = f"/home/user_{i}/.ssh/keys"
            else:
                path = f"C:\\Program Files\\Application_{i}\\Data"
            
            result = self.security_manager.store_directory_preference(
                self.test_user, f"perf_tool_{i}", "performance", path
            )
            
            if result.success:
                paths_data.append((path, result.path_hash, result.pii_sensitive))
        
        # Add audit log entries
        audit_logger = DirectoryAuditLogger(self.db_manager)
        for i in range(100):
            audit_logger.log_directory_operation(
                self.test_user, f"resource_{i}", "performance_test", True,
                {"test_data": f"performance_test_entry_{i}", "iteration": i}
            )
        
        final_size = self.env.get_current_db_size()
        size_increase_percent = self.env.get_db_size_increase_percent()
        
        print(f"Final database size: {final_size / 1024:.2f} KB")
        print(f"Size increase: {(final_size - initial_size) / 1024:.2f} KB ({size_increase_percent:.2f}%)")
        print(f"Data stored: {len(paths_data)} directories, 100 audit entries")
        
        # Database size increase should be <5%
        self.assertLess(size_increase_percent, 5.0,
                       f"Database size increase should be <5%, got {size_increase_percent:.2f}%")
        
        # Verify data integrity after size test
        user_directories = self.security_manager.list_user_directories(self.test_user)
        self.assertGreaterEqual(len(user_directories), len(paths_data) * 0.95,
                              "At least 95% of stored directories should be retrievable")
    
    def test_migration_performance_requirement(self):
        """Test migration completion <30s requirement"""
        # This test measures migration performance on a fresh database
        temp_dir = tempfile.mkdtemp(prefix="migration_perf_test_")
        try:
            db_path = os.path.join(temp_dir, "migration_performance.db")
            db_manager = DatabaseManager(db_path)
            migration_manager = MigrationManager(db_manager)
            
            # Measure migration time
            with PerformanceTimer("all_migrations") as timer:
                success = migration_manager.apply_pending_migrations()
            
            migration_time = timer.elapsed_time
            
            self.assertTrue(success, "Migrations should complete successfully")
            self.assertLess(migration_time, 30.0,
                          f"Migrations should complete in <30s, took {migration_time:.2f}s")
            
            print(f"\n--- Migration Performance ---")
            print(f"All migrations completed in: {migration_time:.2f}s")
            
            # Verify all expected tables exist
            applied_migrations = migration_manager.get_applied_migrations()
            self.assertGreater(len(applied_migrations), 0, "Should have applied migrations")
            
            db_manager.close()
        
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def test_query_performance(self):
        """Test database query performance"""
        # Add test data for query performance testing
        num_entries = 500
        stored_hashes = []
        
        for i in range(num_entries):
            path = f"C:\\Users\\query_test_{i}\\Documents\\File_{i}"
            result = self.security_manager.store_directory_preference(
                f"query_user_{i % 10}", f"query_tool_{i}", "query_test", path
            )
            if result.success:
                stored_hashes.append(result.path_hash)
        
        # Test various query types
        query_tests = [
            ("list_user_directories", lambda: self.security_manager.list_user_directories("query_user_0")),
            ("list_all_directories", lambda: self.security_manager.list_user_directories(None)),
            ("retrieve_specific", lambda: self.security_manager.retrieve_directory_preference("query_user_0", stored_hashes[0]) if stored_hashes else None),
            ("count_directories", lambda: len(self.security_manager.list_user_directories(None))),
        ]
        
        query_results = {}
        
        for query_name, query_func in query_tests:
            with PerformanceTimer(query_name) as timer:
                result = query_func()
            
            query_time = timer.elapsed_ms
            query_results[query_name] = query_time
            
            # All queries should be reasonably fast
            self.assertLess(query_time, 1000, 
                          f"Query '{query_name}' should be <1000ms, got {query_time:.2f}ms")
        
        print(f"\n--- Query Performance Results ---")
        for query_name, query_time in query_results.items():
            print(f"{query_name}: {query_time:.2f}ms")


class TestSystemResourceUsage(unittest.TestCase):
    """Test system resource usage"""
    
    def setUp(self):
        """Setup system resource test environment"""
        self.env = PerformanceTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.process = psutil.Process()
    
    def tearDown(self):
        """Cleanup system resource test environment"""
        self.env.teardown()
    
    def test_cpu_usage_under_load(self):
        """Test CPU usage under load"""
        # Monitor CPU usage during intensive operations
        cpu_measurements = []
        
        def monitor_cpu():
            for _ in range(20):  # Monitor for 20 seconds
                cpu_percent = self.process.cpu_percent(interval=1)
                cpu_measurements.append(cpu_percent)
        
        # Start CPU monitoring in background
        cpu_thread = threading.Thread(target=monitor_cpu)
        cpu_thread.start()
        
        # Perform intensive operations
        for i in range(100):
            path = f"C:\\Users\\cpu_test_{i}\\Documents\\IntensiveTest"
            self.security_manager.store_directory_preference(
                f"cpu_user_{i}", f"cpu_tool_{i}", "cpu_test", path
            )
        
        cpu_thread.join()
        
        if cpu_measurements:
            avg_cpu = statistics.mean(cpu_measurements)
            max_cpu = max(cpu_measurements)
            
            print(f"\n--- CPU Usage Under Load ---")
            print(f"Average CPU usage: {avg_cpu:.2f}%")
            print(f"Maximum CPU usage: {max_cpu:.2f}%")
            
            # CPU usage should be reasonable (not constantly pegged at 100%)
            self.assertLess(avg_cpu, 80, f"Average CPU usage should be <80%, got {avg_cpu:.2f}%")
    
    def test_memory_usage_patterns(self):
        """Test memory usage patterns"""
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_measurements = []
        
        # Perform operations and monitor memory
        for batch in range(10):  # 10 batches of operations
            batch_start_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Batch of operations
            for i in range(50):
                path = f"C:\\Users\\memory_test_{batch}_{i}\\Documents"
                self.security_manager.store_directory_preference(
                    f"memory_user_{batch}", f"memory_tool_{i}", "memory_test", path
                )
            
            batch_end_memory = self.process.memory_info().rss / 1024 / 1024
            memory_measurements.append(batch_end_memory)
            
            # Force garbage collection
            gc.collect()
        
        final_memory = self.process.memory_info().rss / 1024 / 1024
        peak_memory = max(memory_measurements)
        memory_growth = final_memory - initial_memory
        
        print(f"\n--- Memory Usage Patterns ---")
        print(f"Initial memory: {initial_memory:.2f} MB")
        print(f"Peak memory: {peak_memory:.2f} MB")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory growth: {memory_growth:.2f} MB")
        
        # Memory growth should be reasonable
        self.assertLess(memory_growth, 100, 
                       f"Memory growth should be <100MB, got {memory_growth:.2f}MB")
        
        # Peak memory shouldn't be excessive
        self.assertLess(peak_memory - initial_memory, 150,
                       f"Peak memory increase should be <150MB, got {peak_memory - initial_memory:.2f}MB")


def run_performance_tests():
    """Run all Phase 4 performance tests"""
    test_classes = [
        TestEncryptionPerformance,
        TestDirectoryOperationPerformance,
        TestDatabasePerformance,
        TestSystemResourceUsage
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Phase 4 Performance Testing Suite...")
    print("=" * 60)
    
    success = run_performance_tests()
    
    print("=" * 60)
    if success:
        print("✅ All performance tests passed! Performance requirements met.")
    else:
        print("❌ Some performance tests failed. Please review performance optimization.")
    
    print("\nPerformance test coverage includes:")
    print("- Encryption latency validation (<100ms)")
    print("- Directory operation performance testing")
    print("- Database size increase monitoring (<5%)")
    print("- Migration completion time validation (<30s)")
    print("- Concurrent operation performance")
    print("- Large dataset handling")
    print("- System resource usage monitoring")
    print("- Memory usage pattern analysis")
    print("- CPU usage under load testing")
    print("- Query performance optimization")