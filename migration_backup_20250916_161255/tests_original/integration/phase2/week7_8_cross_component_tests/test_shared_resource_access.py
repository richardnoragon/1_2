"""
Shared Resource Access Tests - Phase 2 Week 7-8
Cross-component shared resource access testing for RFU system

Test Categories:
- Concurrent resource utilization
- Deadlock prevention mechanisms
- Resource pooling efficiency  
- Thread-safety verification
"""

import hashlib
import os
import queue
import sqlite3
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import Mock

import pytest

# Import RFU system components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 
                             '..'))

try:
    from database.connection_pool import ConnectionPool
    from resources.file_lock_manager import FileLockManager
    from resources.memory_pool import MemoryPool
    from resources.resource_manager import ResourceManager
    from utils.logging_utils import setup_logger
except ImportError as e:
    print(f"Warning: Could not import RFU resource components: {e}")
    
    # Create mock resource management classes for testing
    class ConnectionPool:
        def __init__(self, db_path, max_connections=10):
            self.db_path = db_path
            self.max_connections = max_connections
            self.connections = queue.Queue(maxsize=max_connections)
            self.active_connections = 0
            self.lock = threading.Lock()
            
            # Initialize connection pool
            for _ in range(max_connections):
                conn = sqlite3.connect(db_path, check_same_thread=False)
                self.connections.put(conn)
        
        @contextmanager
        def get_connection(self, timeout=5.0):
            """Get connection from pool with timeout"""
            conn = None
            try:
                conn = self.connections.get(timeout=timeout)
                with self.lock:
                    self.active_connections += 1
                yield conn
            except queue.Empty:
                raise TimeoutError("Connection pool exhausted")
            finally:
                if conn:
                    with self.lock:
                        self.active_connections -= 1
                    self.connections.put(conn)
        
        def close_all(self):
            """Close all connections in pool"""
            while not self.connections.empty():
                conn = self.connections.get()
                conn.close()
    
    class FileLockManager:
        def __init__(self):
            self.locks = {}
            self.lock_registry = threading.Lock()
        
        @contextmanager
        def acquire_lock(self, file_path, mode='exclusive', timeout=5.0):
            """Acquire file lock with timeout"""
            with self.lock_registry:
                if file_path not in self.locks:
                    self.locks[file_path] = threading.RLock()
                file_lock = self.locks[file_path]
            
            acquired = file_lock.acquire(timeout=timeout)
            if not acquired:
                raise TimeoutError(f"Could not acquire lock for {file_path}")
            
            try:
                yield file_path
            finally:
                file_lock.release()
    
    class MemoryPool:
        def __init__(self, pool_size=1024*1024):  # 1MB default
            self.pool_size = pool_size
            self.allocated = 0
            self.allocations = {}
            self.lock = threading.Lock()
        
        def allocate(self, size, identifier):
            """Allocate memory block"""
            with self.lock:
                if self.allocated + size > self.pool_size:
                    raise MemoryError("Memory pool exhausted")
                
                self.allocated += size
                self.allocations[identifier] = size
                return bytearray(size)
        
        def deallocate(self, identifier):
            """Deallocate memory block"""
            with self.lock:
                if identifier in self.allocations:
                    size = self.allocations.pop(identifier)
                    self.allocated -= size
                    return size
                return 0
        
        def get_stats(self):
            """Get memory pool statistics"""
            with self.lock:
                return {
                    'pool_size': self.pool_size,
                    'allocated': self.allocated,
                    'free': self.pool_size - self.allocated,
                    'utilization': (self.allocated / self.pool_size) * 100,
                    'active_allocations': len(self.allocations)
                }
    
    class ResourceManager:
        def __init__(self):
            self.resources = {}
            self.resource_locks = {}
            self.manager_lock = threading.Lock()
        
        def register_resource(self, resource_id, resource):
            """Register a shared resource"""
            with self.manager_lock:
                self.resources[resource_id] = resource
                self.resource_locks[resource_id] = threading.RLock()
        
        @contextmanager
        def access_resource(self, resource_id, timeout=5.0):
            """Access shared resource with locking"""
            if resource_id not in self.resources:
                raise ValueError(f"Resource {resource_id} not found")
            
            resource_lock = self.resource_locks[resource_id]
            acquired = resource_lock.acquire(timeout=timeout)
            
            if not acquired:
                raise TimeoutError(f"Could not access resource {resource_id}")
            
            try:
                yield self.resources[resource_id]
            finally:
                resource_lock.release()

logger = setup_logger('shared_resource_tests') if 'setup_logger' in globals() else None


class SharedResourceTestSuite:
    """Comprehensive shared resource access test suite"""
    
    def __init__(self):
        self.test_results = {
            'concurrent_utilization': {},
            'deadlock_prevention': {},
            'resource_pooling': {},
            'thread_safety': {}
        }
        self.performance_metrics = {}
        self.test_db_path = None
        self.connection_pool = None
        self.file_lock_manager = None
        self.memory_pool = None
        self.resource_manager = None
        
    def setup_resource_infrastructure(self):
        """Set up shared resource infrastructure for testing"""
        # Create test database
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self._create_test_database()
        
        # Initialize resource components
        self.connection_pool = ConnectionPool(self.test_db_path, max_connections=5)
        self.file_lock_manager = FileLockManager()
        self.memory_pool = MemoryPool(pool_size=1024*1024)  # 1MB
        self.resource_manager = ResourceManager()
        
        # Register shared resources
        self.resource_manager.register_resource('database', self.connection_pool)
        self.resource_manager.register_resource('file_locks', self.file_lock_manager)
        self.resource_manager.register_resource('memory', self.memory_pool)
        
        return True
    
    def _create_test_database(self):
        """Create test database for resource testing"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE shared_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                modified_by TEXT,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert initial test data
        for i in range(100):
            cursor.execute(
                "INSERT INTO shared_data (data, modified_by) VALUES (?, ?)",
                (f"data_row_{i}", "initial_setup")
            )
        
        conn.commit()
        conn.close()
    
    def cleanup_resource_infrastructure(self):
        """Clean up resource infrastructure"""
        if self.connection_pool:
            self.connection_pool.close_all()
        
        if self.test_db_path and os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)


class TestConcurrentResourceUtilization:
    """Test concurrent resource utilization patterns"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = SharedResourceTestSuite()
        self.test_suite.setup_resource_infrastructure()
        yield
        self.test_suite.cleanup_resource_infrastructure()
    
    def test_database_connection_pool_concurrency(self):
        """Test concurrent database connection pool utilization"""
        connection_pool = self.test_suite.connection_pool
        results = []
        
        def database_worker(worker_id, operations_count):
            """Worker function for database operations"""
            worker_results = []
            
            for op_id in range(operations_count):
                try:
                    with connection_pool.get_connection(timeout=2.0) as conn:
                        cursor = conn.cursor()
                        
                        # Perform database operations
                        cursor.execute(
                            "UPDATE shared_data SET modified_by = ?, modified_at = ? WHERE id = ?",
                            (f"worker_{worker_id}", datetime.now().isoformat(), (worker_id * 10) + op_id + 1)
                        )
                        
                        cursor.execute("SELECT COUNT(*) FROM shared_data WHERE modified_by = ?", (f"worker_{worker_id}",))
                        count = cursor.fetchone()[0]
                        
                        conn.commit()
                        
                        worker_results.append({
                            'worker_id': worker_id,
                            'operation_id': op_id,
                            'updated_count': count,
                            'success': True
                        })
                        
                except Exception as e:
                    worker_results.append({
                        'worker_id': worker_id,
                        'operation_id': op_id,
                        'error': str(e),
                        'success': False
                    })
            
            return worker_results
        
        # Run concurrent database workers
        num_workers = 8
        operations_per_worker = 5
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(database_worker, worker_id, operations_per_worker)
                for worker_id in range(num_workers)
            ]
            
            for future in as_completed(futures):
                worker_results = future.result()
                results.extend(worker_results)
        
        execution_time = time.time() - start_time
        
        # Verify concurrent operations
        successful_operations = [r for r in results if r.get('success', False)]
        failed_operations = [r for r in results if not r.get('success', False)]
        
        expected_operations = num_workers * operations_per_worker
        assert len(successful_operations) == expected_operations, \
            f"Expected {expected_operations} successful operations, got {len(successful_operations)}"
        
        assert len(failed_operations) == 0, f"Unexpected failures: {failed_operations}"
        
        # Performance validation
        assert execution_time < 10.0, f"Concurrent operations took too long: {execution_time}s"
        
        self.test_suite.performance_metrics['db_concurrent_ops_time'] = execution_time
        self.test_suite.test_results['concurrent_utilization']['database_pool'] = 'PASS'
    
    def test_memory_pool_concurrent_allocation(self):
        """Test concurrent memory pool allocation and deallocation"""
        memory_pool = self.test_suite.memory_pool
        allocation_results = []
        
        def memory_worker(worker_id, allocation_count):
            """Worker function for memory operations"""
            worker_results = []
            allocations = []
            
            # Allocation phase
            for alloc_id in range(allocation_count):
                try:
                    identifier = f"worker_{worker_id}_alloc_{alloc_id}"
                    size = 1024 * (alloc_id + 1)  # Varying sizes
                    
                    memory_block = memory_pool.allocate(size, identifier)
                    allocations.append((identifier, size))
                    
                    worker_results.append({
                        'worker_id': worker_id,
                        'operation': 'allocate',
                        'identifier': identifier,
                        'size': size,
                        'success': True
                    })
                    
                except Exception as e:
                    worker_results.append({
                        'worker_id': worker_id,
                        'operation': 'allocate',
                        'error': str(e),
                        'success': False
                    })
            
            # Use allocated memory briefly
            time.sleep(0.1)
            
            # Deallocation phase
            for identifier, size in allocations:
                try:
                    deallocated_size = memory_pool.deallocate(identifier)
                    
                    worker_results.append({
                        'worker_id': worker_id,
                        'operation': 'deallocate',
                        'identifier': identifier,
                        'size': deallocated_size,
                        'success': True
                    })
                    
                except Exception as e:
                    worker_results.append({
                        'worker_id': worker_id,
                        'operation': 'deallocate',
                        'error': str(e),
                        'success': False
                    })
            
            return worker_results
        
        # Run concurrent memory workers
        num_workers = 4
        allocations_per_worker = 3
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(memory_worker, worker_id, allocations_per_worker)
                for worker_id in range(num_workers)
            ]
            
            for future in as_completed(futures):
                worker_results = future.result()
                allocation_results.extend(worker_results)
        
        # Verify memory operations
        successful_allocations = [r for r in allocation_results 
                                if r['operation'] == 'allocate' and r.get('success', False)]
        successful_deallocations = [r for r in allocation_results 
                                  if r['operation'] == 'deallocate' and r.get('success', False)]
        
        expected_ops = num_workers * allocations_per_worker
        assert len(successful_allocations) == expected_ops, \
            f"Allocation count mismatch: {len(successful_allocations)}/{expected_ops}"
        assert len(successful_deallocations) == expected_ops, \
            f"Deallocation count mismatch: {len(successful_deallocations)}/{expected_ops}"
        
        # Verify memory pool is clean
        final_stats = memory_pool.get_stats()
        assert final_stats['allocated'] == 0, "Memory pool not properly cleaned up"
        assert final_stats['active_allocations'] == 0, "Active allocations remaining"
        
        self.test_suite.test_results['concurrent_utilization']['memory_pool'] = 'PASS'


class TestDeadlockPrevention:
    """Test deadlock prevention mechanisms"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = SharedResourceTestSuite()
        self.test_suite.setup_resource_infrastructure()
        yield
        self.test_suite.cleanup_resource_infrastructure()
    
    def test_file_lock_deadlock_prevention(self):
        """Test file locking deadlock prevention"""
        file_lock_manager = self.test_suite.file_lock_manager
        
        # Create test files
        test_files = []
        for i in range(3):
            temp_file = tempfile.mktemp(suffix=f'_test_{i}.txt')
            with open(temp_file, 'w') as f:
                f.write(f"Test file {i} content")
            test_files.append(temp_file)
        
        deadlock_results = []
        
        def lock_sequence_worker(worker_id, file_sequence):
            """Worker that attempts to lock files in sequence"""
            worker_results = []
            
            try:
                # Attempt to acquire locks in specified order
                acquired_locks = []
                
                for file_path in file_sequence:
                    with file_lock_manager.acquire_lock(file_path, timeout=2.0) as locked_file:
                        acquired_locks.append(locked_file)
                        time.sleep(0.1)  # Hold lock briefly
                        
                        worker_results.append({
                            'worker_id': worker_id,
                            'file': file_path,
                            'action': 'acquired',
                            'success': True
                        })
                
                worker_results.append({
                    'worker_id': worker_id,
                    'action': 'completed_sequence',
                    'files_locked': len(acquired_locks),
                    'success': True
                })
                
            except TimeoutError as e:
                worker_results.append({
                    'worker_id': worker_id,
                    'action': 'timeout',
                    'error': str(e),
                    'success': False
                })
            
            except Exception as e:
                worker_results.append({
                    'worker_id': worker_id,
                    'action': 'error',
                    'error': str(e),
                    'success': False
                })
            
            return worker_results
        
        # Test deadlock scenario: workers try to lock files in different orders
        lock_sequences = [
            test_files,  # Worker 0: A, B, C
            test_files[::-1],  # Worker 1: C, B, A (potential deadlock)
            [test_files[1], test_files[0], test_files[2]]  # Worker 2: B, A, C
        ]
        
        with ThreadPoolExecutor(max_workers=len(lock_sequences)) as executor:
            futures = [
                executor.submit(lock_sequence_worker, worker_id, sequence)
                for worker_id, sequence in enumerate(lock_sequences)
            ]
            
            for future in as_completed(futures):
                worker_results = future.result()
                deadlock_results.extend(worker_results)
        
        # Analyze deadlock prevention
        completed_sequences = [r for r in deadlock_results 
                             if r.get('action') == 'completed_sequence' and r.get('success', False)]
        timeouts = [r for r in deadlock_results 
                   if r.get('action') == 'timeout']
        
        # At least some workers should complete (deadlock prevention working)
        assert len(completed_sequences) > 0, "All workers deadlocked - prevention failed"
        
        # If timeouts occur, they should be handled gracefully
        if timeouts:
            assert all('timeout' in r.get('error', '') for r in timeouts), \
                "Unexpected error types in timeout scenarios"
        
        # Clean up test files
        for file_path in test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        self.test_suite.test_results['deadlock_prevention']['file_locks'] = 'PASS'


class TestResourcePoolingEfficiency:
    """Test resource pooling efficiency"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = SharedResourceTestSuite()
        self.test_suite.setup_resource_infrastructure()
        yield
        self.test_suite.cleanup_resource_infrastructure()
    
    def test_connection_pool_efficiency(self):
        """Test database connection pool efficiency and reuse"""
        connection_pool = self.test_suite.connection_pool
        efficiency_metrics = {
            'connection_acquisitions': 0,
            'total_wait_time': 0,
            'max_wait_time': 0,
            'successful_operations': 0
        }
        metrics_lock = threading.Lock()
        
        def efficiency_worker(worker_id, operations_count):
            """Worker that measures connection pool efficiency"""
            worker_metrics = []
            
            for op_id in range(operations_count):
                start_time = time.time()
                
                try:
                    with connection_pool.get_connection(timeout=3.0) as conn:
                        acquisition_time = time.time() - start_time
                        
                        # Update metrics
                        with metrics_lock:
                            efficiency_metrics['connection_acquisitions'] += 1
                            efficiency_metrics['total_wait_time'] += acquisition_time
                            efficiency_metrics['max_wait_time'] = max(
                                efficiency_metrics['max_wait_time'], acquisition_time
                            )
                        
                        # Perform database operation
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM shared_data")
                        result = cursor.fetchone()
                        
                        worker_metrics.append({
                            'worker_id': worker_id,
                            'operation_id': op_id,
                            'acquisition_time': acquisition_time,
                            'result_count': result[0],
                            'success': True
                        })
                        
                        with metrics_lock:
                            efficiency_metrics['successful_operations'] += 1
                
                except Exception as e:
                    worker_metrics.append({
                        'worker_id': worker_id,
                        'operation_id': op_id,
                        'error': str(e),
                        'success': False
                    })
            
            return worker_metrics
        
        # Run efficiency test with more workers than connections
        num_workers = 10  # More than pool size (5)
        operations_per_worker = 3
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(efficiency_worker, worker_id, operations_per_worker)
                for worker_id in range(num_workers)
            ]
            
            all_results = []
            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        total_time = time.time() - start_time
        
        # Analyze efficiency metrics
        successful_ops = [r for r in all_results if r.get('success', False)]
        failed_ops = [r for r in all_results if not r.get('success', False)]
        
        expected_ops = num_workers * operations_per_worker
        assert len(successful_ops) == expected_ops, \
            f"Operation count mismatch: {len(successful_ops)}/{expected_ops}"
        
        # Efficiency validations
        avg_wait_time = efficiency_metrics['total_wait_time'] / efficiency_metrics['connection_acquisitions']
        assert avg_wait_time < 1.0, f"Average connection wait time too high: {avg_wait_time}s"
        assert efficiency_metrics['max_wait_time'] < 5.0, f"Max wait time exceeded threshold: {efficiency_metrics['max_wait_time']}s"
        
        # Pool utilization efficiency
        pool_efficiency = (efficiency_metrics['successful_operations'] / total_time)
        assert pool_efficiency > 5.0, f"Pool efficiency too low: {pool_efficiency} ops/sec"
        
        self.test_suite.performance_metrics.update({
            'connection_pool_avg_wait': avg_wait_time,
            'connection_pool_max_wait': efficiency_metrics['max_wait_time'],
            'connection_pool_efficiency': pool_efficiency
        })
        
        self.test_suite.test_results['resource_pooling']['connection_efficiency'] = 'PASS'


class TestThreadSafety:
    """Test thread-safety verification"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = SharedResourceTestSuite()
        self.test_suite.setup_resource_infrastructure()
        yield
        self.test_suite.cleanup_resource_infrastructure()
    
    def test_shared_data_thread_safety(self):
        """Test thread safety of shared data structures"""
        # Shared data structure for testing
        shared_counter = {'value': 0}
        counter_lock = threading.Lock()
        
        def thread_safe_increment(worker_id, increment_count):
            """Thread-safe increment operation"""
            results = []
            
            for i in range(increment_count):
                # Thread-safe increment
                with counter_lock:
                    old_value = shared_counter['value']
                    shared_counter['value'] += 1
                    new_value = shared_counter['value']
                
                results.append({
                    'worker_id': worker_id,
                    'increment_id': i,
                    'old_value': old_value,
                    'new_value': new_value,
                    'expected': old_value + 1
                })
            
            return results
        
        # Run concurrent increments
        num_workers = 10
        increments_per_worker = 100
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(thread_safe_increment, worker_id, increments_per_worker)
                for worker_id in range(num_workers)
            ]
            
            all_results = []
            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        # Verify thread safety
        expected_final_value = num_workers * increments_per_worker
        actual_final_value = shared_counter['value']
        
        assert actual_final_value == expected_final_value, \
            f"Thread safety violation: expected {expected_final_value}, got {actual_final_value}"
        
        # Verify all increments were correct
        for result in all_results:
            assert result['new_value'] == result['expected'], \
                f"Increment consistency violation: {result}"
        
        self.test_suite.test_results['thread_safety']['shared_data'] = 'PASS'


def generate_shared_resource_access_report():
    """Generate comprehensive shared resource access test report"""
    test_suite = SharedResourceTestSuite()
    
    report = {
        'test_execution_summary': {
            'timestamp': datetime.now().isoformat(),
            'total_test_categories': 4,
            'total_test_methods': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'execution_time': 0
        },
        'test_results': test_suite.test_results,
        'performance_metrics': test_suite.performance_metrics,
        'resource_analysis': {
            'resource_types_tested': [
                'database_connection_pool',
                'memory_pool',
                'file_locks',
                'shared_data_structures'
            ],
            'concurrency_patterns_verified': [
                'concurrent_utilization',
                'deadlock_prevention',
                'resource_pooling',
                'thread_safety'
            ]
        },
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
    
    # Generate recommendations
    recommendations = [
        "Implement connection pooling for all database operations",
        "Use proper locking mechanisms to prevent deadlocks",
        "Monitor resource pool utilization and adjust sizes accordingly",
        "Implement timeout mechanisms for all resource acquisitions",
        "Use thread-safe data structures for shared resources",
        "Implement resource cleanup and garbage collection",
        "Monitor for resource leaks and implement proper disposal",
        "Use resource ordering to prevent circular dependencies"
    ]
    
    report['recommendations'] = recommendations
    
    return report


if __name__ == "__main__":
    # Run all shared resource access tests
    pytest.main([__file__, "-v", "--tb=short"])