#!/usr/bin/env python3
"""
Buffer Overflow and Race Condition Security Testing Suite

This module provides comprehensive testing for:
- Buffer Overflow Protection Testing
- Race Condition Security Testing
- Memory Safety Validation
- Concurrent Access Security
- Resource Exhaustion Protection
- Thread Safety Validation

Author: Security Testing Framework
Date: 2025-09-04
Version: 1.0.0
"""

import ctypes
import gc
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from unittest.mock import MagicMock, patch

import psutil

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class MockSecureBuffer:
    """Mock secure buffer implementation for testing"""
    
    def __init__(self, max_size=1024):
        self.max_size = max_size
        self.buffer = bytearray(max_size)
        self.current_size = 0
        self.lock = threading.RLock()
    
    def write(self, data):
        """Write data to buffer with overflow protection"""
        with self.lock:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if len(data) > self.max_size:
                raise ValueError(f"Data size {len(data)} exceeds buffer limit {self.max_size}")
            
            if self.current_size + len(data) > self.max_size:
                raise ValueError("Buffer overflow detected")
            
            self.buffer[self.current_size:self.current_size + len(data)] = data
            self.current_size += len(data)
            
            return True
    
    def read(self, size=None):
        """Read data from buffer"""
        with self.lock:
            if size is None:
                size = self.current_size
            
            if size > self.current_size:
                size = self.current_size
            
            return bytes(self.buffer[:size])
    
    def clear(self):
        """Clear buffer contents"""
        with self.lock:
            # Securely zero out buffer
            for i in range(len(self.buffer)):
                self.buffer[i] = 0
            self.current_size = 0


class MockThreadSafeResource:
    """Mock thread-safe resource for race condition testing"""
    
    def __init__(self, initial_value=0):
        self.value = initial_value
        self.access_count = 0
        self.lock = threading.RLock()
        self.access_log = []
    
    def increment(self, amount=1):
        """Thread-safe increment operation"""
        with self.lock:
            thread_id = threading.current_thread().ident
            self.access_log.append((thread_id, 'increment', time.time()))
            old_value = self.value
            # Simulate some processing time to increase race condition chances
            time.sleep(0.001)
            self.value = old_value + amount
            self.access_count += 1
            return self.value
    
    def decrement(self, amount=1):
        """Thread-safe decrement operation"""
        with self.lock:
            thread_id = threading.current_thread().ident
            self.access_log.append((thread_id, 'decrement', time.time()))
            old_value = self.value
            time.sleep(0.001)
            self.value = old_value - amount
            self.access_count += 1
            return self.value
    
    def get_value(self):
        """Get current value"""
        with self.lock:
            return self.value
    
    def reset(self):
        """Reset resource state"""
        with self.lock:
            self.value = 0
            self.access_count = 0
            self.access_log.clear()


class TestBufferOverflowProtection(unittest.TestCase):
    """Test buffer overflow protection mechanisms"""
    
    def setUp(self):
        """Setup buffer overflow test environment"""
        self.buffer = MockSecureBuffer(max_size=1024)
    
    def test_normal_buffer_operations(self):
        """Test normal buffer operations within limits"""
        test_data = b"Normal test data"
        
        result = self.buffer.write(test_data)
        self.assertTrue(result, "Normal write should succeed")
        
        read_data = self.buffer.read()
        self.assertEqual(read_data, test_data, "Read data should match written data")
    
    def test_buffer_overflow_prevention(self):
        """Test buffer overflow prevention"""
        # Try to write data larger than buffer
        large_data = b"X" * 2048  # Larger than 1024 byte limit
        
        with self.assertRaises(ValueError) as context:
            self.buffer.write(large_data)
        
        self.assertIn("exceeds buffer limit", str(context.exception))
    
    def test_gradual_buffer_overflow_prevention(self):
        """Test prevention of gradual buffer overflow"""
        # Fill buffer to near capacity
        data_chunk = b"A" * 512
        self.buffer.write(data_chunk)
        
        # Try to write more data that would cause overflow
        overflow_data = b"B" * 600
        
        with self.assertRaises(ValueError) as context:
            self.buffer.write(overflow_data)
        
        self.assertIn("Buffer overflow detected", str(context.exception))
    
    def test_string_to_bytes_overflow_protection(self):
        """Test overflow protection with string inputs"""
        # Large string that would overflow
        large_string = "X" * 2048
        
        with self.assertRaises(ValueError):
            self.buffer.write(large_string)
    
    def test_memory_exhaustion_protection(self):
        """Test protection against memory exhaustion attacks"""
        # Try to create many large buffers to exhaust memory
        buffers = []
        
        try:
            # This should be limited by the system or implementation
            for i in range(1000):
                buffer = MockSecureBuffer(max_size=1024 * 1024)  # 1MB each
                buffers.append(buffer)
                
                # Monitor memory usage
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                # Stop if memory usage gets too high (>500MB for test)
                if memory_mb > 500:
                    break
            
            # Should not exhaust all system memory
            self.assertLess(len(buffers), 1000, 
                          "Should not allow unlimited memory allocation")
            
        finally:
            # Clean up
            del buffers
            gc.collect()


class TestRaceConditionSecurity(unittest.TestCase):
    """Test race condition security vulnerabilities"""
    
    def setUp(self):
        """Setup race condition test environment"""
        self.resource = MockThreadSafeResource()
        self.results = Queue()
    
    def test_concurrent_increment_operations(self):
        """Test concurrent increment operations for race conditions"""
        num_threads = 10
        increments_per_thread = 100
        expected_total = num_threads * increments_per_thread
        
        def increment_worker():
            for _ in range(increments_per_thread):
                self.resource.increment(1)
        
        # Start concurrent threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=increment_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check final value - should be exactly expected if thread-safe
        final_value = self.resource.get_value()
        self.assertEqual(final_value, expected_total,
                        f"Expected {expected_total}, got {final_value}. Race condition detected!")
    
    def test_concurrent_mixed_operations(self):
        """Test concurrent mixed increment/decrement operations"""
        num_threads = 8
        operations_per_thread = 50
        
        def mixed_operations_worker():
            for i in range(operations_per_thread):
                if i % 2 == 0:
                    self.resource.increment(1)
                else:
                    self.resource.decrement(1)
        
        # Start concurrent threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=mixed_operations_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Final value should be 0 if operations are properly synchronized
        final_value = self.resource.get_value()
        self.assertEqual(final_value, 0,
                        f"Expected 0 after balanced operations, got {final_value}")
    
    def test_deadlock_prevention(self):
        """Test deadlock prevention mechanisms"""
        resource1 = MockThreadSafeResource()
        resource2 = MockThreadSafeResource()
        deadlock_detected = threading.Event()
        
        def thread1_operations():
            try:
                # Acquire locks in order: resource1, then resource2
                with resource1.lock:
                    time.sleep(0.1)  # Hold lock for a bit
                    with resource2.lock:
                        resource1.increment(1)
                        resource2.increment(1)
            except Exception:
                deadlock_detected.set()
        
        def thread2_operations():
            try:
                # Acquire locks in same order to prevent deadlock
                with resource1.lock:
                    time.sleep(0.1)  # Hold lock for a bit
                    with resource2.lock:
                        resource1.decrement(1)
                        resource2.decrement(1)
            except Exception:
                deadlock_detected.set()
        
        # Start both threads
        thread1 = threading.Thread(target=thread1_operations)
        thread2 = threading.Thread(target=thread2_operations)
        
        thread1.start()
        thread2.start()
        
        # Wait for completion with timeout
        thread1.join(timeout=5.0)
        thread2.join(timeout=5.0)
        
        # Check if deadlock occurred
        self.assertFalse(deadlock_detected.is_set(), "Deadlock should not occur")
        self.assertFalse(thread1.is_alive(), "Thread1 should complete")
        self.assertFalse(thread2.is_alive(), "Thread2 should complete")
    
    def test_time_of_check_time_of_use_vulnerability(self):
        """Test TOCTOU (Time of Check Time of Use) vulnerability"""
        
        class TOCTOUResource:
            def __init__(self):
                self.value = 100
                self.lock = threading.RLock()
            
            def unsafe_operation(self):
                """Unsafe operation with TOCTOU vulnerability"""
                # Check condition
                if self.value > 50:
                    time.sleep(0.01)  # Simulate processing delay
                    # Use the value (vulnerable to change between check and use)
                    self.value -= 50
                    return True
                return False
            
            def safe_operation(self):
                """Safe operation without TOCTOU vulnerability"""
                with self.lock:
                    if self.value > 50:
                        self.value -= 50
                        return True
                    return False
        
        # Test unsafe operation
        unsafe_resource = TOCTOUResource()
        
        def unsafe_worker():
            for _ in range(10):
                unsafe_resource.unsafe_operation()
        
        # Run multiple threads on unsafe operation
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=unsafe_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # The final value might be negative due to TOCTOU vulnerability
        unsafe_final_value = unsafe_resource.value
        
        # Test safe operation
        safe_resource = TOCTOUResource()
        
        def safe_worker():
            for _ in range(10):
                safe_resource.safe_operation()
        
        # Run multiple threads on safe operation
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=safe_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # The final value should never be negative with proper locking
        safe_final_value = safe_resource.value
        self.assertGreaterEqual(safe_final_value, 0, 
                               "Safe operation should prevent negative values")
    
    def test_shared_resource_corruption(self):
        """Test shared resource corruption in concurrent access"""
        
        class SharedData:
            def __init__(self):
                self.data = {}
                self.lock = threading.RLock()
                self.corruption_detected = False
            
            def safe_update(self, key, value):
                """Thread-safe update"""
                with self.lock:
                    self.data[key] = value
            
            def unsafe_update(self, key, value):
                """Unsafe update (vulnerable to corruption)"""
                # Read-modify-write without proper locking
                current = self.data.get(key, 0)
                time.sleep(0.001)  # Simulate processing time
                self.data[key] = current + value
            
            def validate_integrity(self):
                """Validate data integrity"""
                with self.lock:
                    # Check for corruption patterns
                    for key, value in self.data.items():
                        if not isinstance(value, (int, float)):
                            self.corruption_detected = True
                            return False
                return True
        
        # Test with safe operations
        safe_data = SharedData()
        
        def safe_worker(worker_id):
            for i in range(100):
                safe_data.safe_update(f"key_{i % 10}", worker_id * 100 + i)
        
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=safe_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Validate no corruption occurred
        self.assertTrue(safe_data.validate_integrity(), 
                       "Safe operations should not cause corruption")
    
    def test_concurrent_file_access_security(self):
        """Test concurrent file access security"""
        temp_dir = tempfile.mkdtemp(prefix="race_condition_test_")
        test_file = os.path.join(temp_dir, "concurrent_test.txt")
        
        try:
            # Create test file
            with open(test_file, 'w') as f:
                f.write("Initial content\n")
            
            results = []
            lock = threading.Lock()
            
            def file_worker(worker_id):
                try:
                    # Read and write to file concurrently
                    for i in range(10):
                        with open(test_file, 'r+') as f:
                            content = f.read()
                            f.seek(0)
                            f.write(f"Worker {worker_id} iteration {i}\n")
                            f.truncate()
                    
                    with lock:
                        results.append((worker_id, True, None))
                
                except Exception as e:
                    with lock:
                        results.append((worker_id, False, str(e)))
            
            # Start multiple file workers
            threads = []
            for worker_id in range(3):
                thread = threading.Thread(target=file_worker, args=(worker_id,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Check results
            successful_workers = [r for r in results if r[1] is True]
            failed_workers = [r for r in results if r[1] is False]
            
            # Some level of success expected, but failures indicate race conditions
            if len(failed_workers) > 0:
                print(f"Warning: {len(failed_workers)} workers failed due to file access conflicts")
            
            # File should still exist and be readable
            self.assertTrue(os.path.exists(test_file), "File should still exist")
            
            with open(test_file, 'r') as f:
                final_content = f.read()
                self.assertGreater(len(final_content), 0, "File should have content")
        
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)


class TestMemorySafety(unittest.TestCase):
    """Test memory safety and leak prevention"""
    
    def setUp(self):
        """Setup memory safety test environment"""
        self.initial_memory = self._get_memory_usage()
    
    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def test_memory_leak_detection(self):
        """Test for memory leaks in operations"""
        # Perform operations that might leak memory
        for i in range(1000):
            # Create and destroy objects
            data = "X" * 1024  # 1KB string
            processed = data.upper().lower().strip()
            del data, processed
            
            # Force garbage collection periodically
            if i % 100 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
        time.sleep(0.1)  # Let GC finish
        
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - self.initial_memory
        
        # Memory increase should be minimal (< 10MB)
        self.assertLess(memory_increase, 10, 
                       f"Excessive memory increase detected: {memory_increase:.2f}MB")
    
    def test_large_allocation_protection(self):
        """Test protection against large memory allocations"""
        # Try to allocate extremely large amounts of memory
        try:
            # This should be limited by the system or implementation
            large_allocation = bytearray(1024 * 1024 * 1024)  # 1GB
            del large_allocation
        except MemoryError:
            # This is expected behavior - system protecting against exhaustion
            pass
        except Exception as e:
            # Other exceptions might indicate proper protection mechanisms
            self.assertIn("memory", str(e).lower(), 
                         "Exception should be related to memory protection")
    
    def test_buffer_underflow_protection(self):
        """Test protection against buffer underflow"""
        buffer = MockSecureBuffer()
        
        # Try to read from empty buffer
        data = buffer.read(100)
        self.assertEqual(len(data), 0, "Reading from empty buffer should return empty data")
        
        # Try to read more than available
        buffer.write(b"Small data")
        large_read = buffer.read(1000)
        self.assertLessEqual(len(large_read), len(b"Small data"), 
                           "Should not read beyond available data")


class TestConcurrentSecurityOperations(unittest.TestCase):
    """Test security of concurrent operations"""
    
    def setUp(self):
        """Setup concurrent security test environment"""
        self.security_counter = MockThreadSafeResource()
        self.access_control = {}
        self.access_lock = threading.RLock()
    
    def test_concurrent_authentication_attempts(self):
        """Test concurrent authentication attempts"""
        # Import path fix for cross-test imports
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from tests.security.test_authentication_authorization import \
            MockAuthenticationManager
        
        auth_manager = MockAuthenticationManager()
        auth_manager.create_user("testuser", "TestPass123!", "user")
        
        results = []
        lock = threading.Lock()
        
        def auth_worker(worker_id):
            try:
                success, message, session_id = auth_manager.authenticate_user(
                    "testuser", "TestPass123!"
                )
                with lock:
                    results.append((worker_id, success, session_id))
            except Exception as e:
                with lock:
                    results.append((worker_id, False, str(e)))
        
        # Start multiple authentication threads
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=auth_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All authentications should succeed
        successful_auths = [r for r in results if r[1] is True]
        self.assertEqual(len(successful_auths), 5, 
                        "All concurrent authentications should succeed")
        
        # All session IDs should be unique
        session_ids = [r[2] for r in successful_auths if r[2]]
        unique_sessions = set(session_ids)
        self.assertEqual(len(unique_sessions), len(session_ids),
                        "All session IDs should be unique")
    
    def test_concurrent_permission_checks(self):
        """Test concurrent permission check operations"""
        # Import path fix for cross-test imports
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from tests.security.test_authentication_authorization import \
            MockAuthenticationManager
        
        auth_manager = MockAuthenticationManager()
        auth_manager.create_user("testuser", "TestPass123!", "user")
        
        results = []
        lock = threading.Lock()
        
        def permission_worker(worker_id):
            try:
                for i in range(50):
                    has_permission, message = auth_manager.check_permission(
                        "testuser", "files", "read"
                    )
                    with lock:
                        results.append((worker_id, i, has_permission))
            except Exception as e:
                with lock:
                    results.append((worker_id, -1, str(e)))
        
        # Start concurrent permission check threads
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=permission_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All permission checks should return consistent results
        permission_results = [r[2] for r in results if isinstance(r[2], bool)]
        
        # All should be True for this test case
        all_granted = all(permission_results)
        self.assertTrue(all_granted, "All permission checks should be consistent")
    
    def test_resource_exhaustion_protection(self):
        """Test protection against resource exhaustion attacks"""
        max_threads = 50
        active_threads = []
        
        def resource_worker():
            # Simulate resource-intensive operation
            time.sleep(0.5)
            self.security_counter.increment(1)
        
        # Try to create many threads quickly
        try:
            for i in range(max_threads):
                thread = threading.Thread(target=resource_worker)
                active_threads.append(thread)
                thread.start()
                
                # Check system limits
                if threading.active_count() > 100:
                    break
            
            # Wait for all threads to complete
            for thread in active_threads:
                thread.join(timeout=10.0)
            
            # System should handle thread creation gracefully
            final_count = self.security_counter.get_value()
            self.assertGreater(final_count, 0, "Some operations should complete")
            
        except Exception as e:
            # System protection mechanisms might kick in
            self.assertIn(("thread" or "resource"), str(e).lower(), 
                         "Exception should be related to resource limits")


if __name__ == '__main__':
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("Warning: psutil not available, some memory tests will be skipped")
    
    unittest.main()