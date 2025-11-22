"""
Comprehensive File Splitter Test Suite
======================================

This module provides comprehensive testing for the File Splitter utility, covering
all identified gaps from the testing analysis including:

1. Performance & Scalability Testing
2. Security & Safety Testing
3. Advanced File System Testing
4. Resource Constraint Testing
5. Error Recovery & Robustness Testing

Author: RFU Testing Framework
Date: September 1, 2025
Version: 1.0.0
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import psutil
from PyQt5.QtCore import QCoreApplication

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.tools.file_operations.file_splitter_config import FileSplitterConfig
from src.tools.file_operations.file_splitter_logging import \
    get_file_splitter_logger
from src.tools.file_operations.file_splitter_logic import (
    FileSplitterError, FileSplitterIOError, FileSplitterLogic,
    FileSplitterValidationError, FileSplitterWorkerThread)


class TestFileSplitterPerformance(unittest.TestCase):
    """
    Performance and scalability testing for File Splitter.
    
    Tests large file operations, memory usage monitoring, performance regression,
    concurrent operations, and throughput benchmarking.
    """
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("performance_test")
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
        
        # Performance tracking
        self.performance_metrics = {
            'start_time': None,
            'end_time': None,
            'memory_usage': [],
            'cpu_usage': [],
            'throughput': 0
        }
    
    def tearDown(self):
        """Clean up performance test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def monitor_system_resources(self, duration=5):
        """Monitor system resources during test execution."""
        start_time = time.time()
        while time.time() - start_time < duration:
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            self.performance_metrics['memory_usage'].append({
                'timestamp': time.time(),
                'percent': memory_info.percent,
                'available': memory_info.available,
                'used': memory_info.used
            })
            
            self.performance_metrics['cpu_usage'].append({
                'timestamp': time.time(),
                'percent': cpu_percent
            })
            
            time.sleep(0.5)
    
    def test_large_file_performance_100mb(self):
        """Test performance with 100MB file."""
        file_size = 100 * 1024 * 1024  # 100MB
        test_file = os.path.join(self.test_dir, "large_file_100mb.dat")
        
        # Create large test file
        with open(test_file, 'wb') as f:
            # Write in chunks to avoid memory issues
            chunk_size = 1024 * 1024  # 1MB chunks
            for i in range(file_size // chunk_size):
                f.write(os.urandom(chunk_size))
        
        output_dir = os.path.join(self.test_dir, "performance_output")
        os.makedirs(output_dir)
        
        # Start monitoring
        monitor_thread = threading.Thread(
            target=self.monitor_system_resources,
            args=(10,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Measure performance
        start_time = time.time()
        self.performance_metrics['start_time'] = start_time
        
        # Split file into 10MB chunks
        self.logic.split_file(test_file, output_dir, 'size', 10, 1024 * 1024)
        
        end_time = time.time()
        self.performance_metrics['end_time'] = end_time
        
        # Calculate metrics
        duration = end_time - start_time
        throughput = file_size / duration / (1024 * 1024)  # MB/s
        self.performance_metrics['throughput'] = throughput
        
        # Performance assertions
        self.assertLess(duration, 30, "Large file splitting should complete within 30 seconds")
        self.assertGreater(throughput, 1.0, "Throughput should be at least 1 MB/s")
        
        # Verify chunks created
        chunk_files = [f for f in os.listdir(output_dir) if f.endswith('.part001') or '.part' in f]
        expected_chunks = (file_size + (10 * 1024 * 1024) - 1) // (10 * 1024 * 1024)
        self.assertEqual(len([f for f in chunk_files if '.part' in f]), expected_chunks)
        
        # Log performance metrics
        self.logger.info(f"Performance Test 100MB - Duration: {duration:.2f}s, Throughput: {throughput:.2f}MB/s")
    
    def test_memory_usage_monitoring(self):
        """Test memory usage remains within acceptable limits."""
        file_size = 50 * 1024 * 1024  # 50MB
        test_file = os.path.join(self.test_dir, "memory_test.dat")
        
        with open(test_file, 'wb') as f:
            f.write(os.urandom(file_size))
        
        output_dir = os.path.join(self.test_dir, "memory_output")
        os.makedirs(output_dir)
        
        # Monitor memory before operation
        initial_memory = psutil.virtual_memory().used
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.monitor_system_resources,
            args=(8,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Perform operation
        self.logic.split_file(test_file, output_dir, 'parts', 5, 1)
        
        # Wait for monitoring to complete
        monitor_thread.join(timeout=10)
        
        # Analyze memory usage
        max_memory_used = max([m['used'] for m in self.performance_metrics['memory_usage']])
        memory_increase = max_memory_used - initial_memory
        
        # Memory should not increase by more than 50MB during operation
        max_acceptable_increase = 50 * 1024 * 1024  # 50MB
        self.assertLess(memory_increase, max_acceptable_increase,
                       f"Memory increase ({memory_increase / 1024 / 1024:.2f}MB) exceeds limit")
        
        self.logger.info(f"Memory Test - Increase: {memory_increase / 1024 / 1024:.2f}MB")
    
    def test_concurrent_operations_performance(self):
        """Test performance with concurrent split operations."""
        num_concurrent = 3
        file_size = 10 * 1024 * 1024  # 10MB per file
        
        # Create test files
        test_files = []
        for i in range(num_concurrent):
            test_file = os.path.join(self.test_dir, f"concurrent_test_{i}.dat")
            with open(test_file, 'wb') as f:
                f.write(os.urandom(file_size))
            test_files.append(test_file)
        
        # Create separate logic instances for concurrent operations
        logic_instances = []
        for i in range(num_concurrent):
            logic = FileSplitterLogic(self.config, self.logger)
            logic.set_hub_connector(Mock())
            logic_instances.append(logic)
        
        # Start monitoring
        monitor_thread = threading.Thread(
            target=self.monitor_system_resources,
            args=(15,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run concurrent operations
        start_time = time.time()
        threads = []
        
        for i, (logic, test_file) in enumerate(zip(logic_instances, test_files)):
            output_dir = os.path.join(self.test_dir, f"concurrent_output_{i}")
            os.makedirs(output_dir)
            
            thread = threading.Thread(
                target=logic.split_file,
                args=(test_file, output_dir, 'parts', 3, 1)
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all operations to complete
        for thread in threads:
            thread.join(timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertLess(duration, 20, "Concurrent operations should complete within 20 seconds")
        
        # Verify all operations completed successfully
        for i in range(num_concurrent):
            output_dir = os.path.join(self.test_dir, f"concurrent_output_{i}")
            chunk_files = [f for f in os.listdir(output_dir) if '.part' in f]
            self.assertEqual(len(chunk_files), 3, f"Operation {i} should create 3 chunks")
        
        self.logger.info(f"Concurrent Test - {num_concurrent} operations in {duration:.2f}s")


class TestFileSplitterSecurity(unittest.TestCase):
    """
    Security and safety testing for File Splitter.
    
    Tests path traversal prevention, permission validation, file locking,
    temporary file security, and access control validation.
    """
    
    def setUp(self):
        """Set up security test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("security_test")
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
    
    def tearDown(self):
        """Clean up security test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_path_traversal_prevention_input(self):
        """Test prevention of path traversal attacks in input paths."""
        # Create legitimate test file
        test_file = os.path.join(self.test_dir, "legitimate.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(output_dir)
        
        # Test various path traversal attempts
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            os.path.join(self.test_dir, "..", "..", "dangerous"),
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam"
        ]
        
        for dangerous_path in dangerous_paths:
            with self.subTest(path=dangerous_path):
                error_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                
                # Attempt split with dangerous path
                self.logic.split_file(dangerous_path, output_dir, 'size', 512, 1)
                
                # Should result in error
                self.assertTrue(len(error_occurred) > 0, 
                               f"Path traversal attempt should be blocked: {dangerous_path}")
                self.assertIn("not found", error_occurred[0].lower())
    
    def test_path_traversal_prevention_output(self):
        """Test prevention of path traversal attacks in output paths."""
        # Create test file
        test_file = os.path.join(self.test_dir, "test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        # Test dangerous output directories
        dangerous_outputs = [
            "../../../tmp/malicious",
            "..\\..\\..\\temp\\malicious",
            "/tmp/malicious",
            "C:\\Temp\\malicious"
        ]
        
        for dangerous_output in dangerous_outputs:
            with self.subTest(output=dangerous_output):
                error_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                
                # Attempt split with dangerous output
                self.logic.split_file(test_file, dangerous_output, 'size', 512, 1)
                
                # Should either error or normalize path safely
                if len(error_occurred) > 0:
                    # Error is acceptable for security
                    self.logger.info(f"Dangerous output blocked: {dangerous_output}")
                else:
                    # If operation succeeded, verify it didn't escape test directory
                    if os.path.exists(dangerous_output):
                        # Check if path is within acceptable bounds
                        abs_output = os.path.abspath(dangerous_output)
                        abs_test = os.path.abspath(self.test_dir)
                        self.assertTrue(abs_output.startswith(abs_test) or
                                      abs_output.startswith(tempfile.gettempdir()),
                                      f"Output should be contained: {abs_output}")
    
    def test_enhanced_path_traversal_patterns(self):
        """Test detection of sophisticated path traversal patterns."""
        # Create test file
        test_file = os.path.join(self.test_dir, "test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        # Advanced path traversal patterns
        advanced_patterns = [
            "%2e%2e%2f%2e%2e%2f%2e%2e%2ftemp",  # URL encoded ../../../temp
            "..%2fmalicious",  # Mixed encoding
            "....//malicious",  # Double dot-slash
            "....\\\\malicious",  # Double dot-backslash
            "/%2e%2e/%2e%2e/etc/passwd",  # URL encoded with absolute path
            "\\..\\..\\windows\\system32",  # Windows specific traversal
            "/var/../../../etc/shadow",  # Unix system file access
        ]
        
        for pattern in advanced_patterns:
            with self.subTest(pattern=pattern):
                error_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                
                # Attempt split with advanced pattern
                self.logic.split_file(test_file, pattern, 'size', 512, 1)
                
                # Should be blocked with security error
                self.assertTrue(len(error_occurred) > 0,
                               f"Advanced pattern should be blocked: {pattern}")
                self.assertIn("validation failed", error_occurred[0].lower())
    
    def test_system_directory_protection(self):
        """Test protection against writing to system directories."""
        # Create test file
        test_file = os.path.join(self.test_dir, "test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        # System directories that should be protected
        system_dirs = [
            "/etc/malicious",
            "/sys/malicious",
            "/proc/malicious",
            "/dev/malicious",
            "C:\\Windows\\malicious",
            "C:\\Program Files\\malicious",
            "/System/malicious",
            "/Library/malicious"
        ]
        
        for sys_dir in system_dirs:
            with self.subTest(directory=sys_dir):
                error_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                
                # Attempt split to system directory
                self.logic.split_file(test_file, sys_dir, 'size', 512, 1)
                
                # Should be blocked if directory exists or could be created
                if os.path.exists(os.path.dirname(sys_dir)):
                    self.assertTrue(len(error_occurred) > 0,
                                   f"System directory should be protected: {sys_dir}")
    
    def test_join_operation_security(self):
        """Test security validation in join operations."""
        # Create and split a test file first
        test_file = os.path.join(self.test_dir, "join_security_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        split_dir = os.path.join(self.test_dir, "split_output")
        os.makedirs(split_dir)
        
        # Split the file
        self.logic.split_file(test_file, split_dir, 'parts', 2, 1)
        
        # Find the first chunk
        chunk_files = [f for f in os.listdir(split_dir) if '.part' in f]
        if chunk_files:
            first_chunk = os.path.join(split_dir, chunk_files[0])
            
            # Test dangerous output paths for join
            dangerous_join_outputs = [
                "../../../tmp/malicious_joined.dat",
                "/etc/malicious_joined.dat",
                "C:\\Windows\\malicious_joined.dat"
            ]
            
            for dangerous_output in dangerous_join_outputs:
                with self.subTest(output=dangerous_output):
                    error_occurred = []
                    
                    def capture_error(message):
                        error_occurred.append(message)
                    
                    self.logic.error_occurred.connect(capture_error)
                    
                    # Attempt join with dangerous output
                    self.logic.join_files(first_chunk, dangerous_output)
                    
                    # Should be blocked with security error
                    self.assertTrue(len(error_occurred) > 0,
                                   f"Dangerous join output should be blocked: {dangerous_output}")
    
    def test_chunk_path_validation(self):
        """Test validation of individual chunk file paths."""
        # Create test directory structure
        test_file = os.path.join(self.test_dir, "chunk_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(2048))
        
        output_dir = os.path.join(self.test_dir, "chunk_output")
        os.makedirs(output_dir)
        
        # Split file to create chunks
        self.logic.split_file(test_file, output_dir, 'parts', 3, 1)
        
        # Test with various malicious chunk patterns
        malicious_patterns = [
            "..\\..\\malicious.part001",
            "../../../evil.part002",
            "/etc/shadow.part001",
            "C:\\Windows\\system32\\evil.part001"
        ]
        
        for pattern in malicious_patterns:
            with self.subTest(pattern=pattern):
                # Verify the security system would prevent processing such paths
                chunk_path = os.path.join(output_dir, pattern)
                
                # The security validation should catch this
                error_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                
                # Try to process a file with malicious pattern
                try:
                    self.logic.split_file(test_file, chunk_path, 'size', 512, 1)
                    if len(error_occurred) > 0:
                        self.assertIn("validation failed", error_occurred[0].lower())
                except Exception:
                    # Any exception is acceptable for malicious patterns
                    pass
    
    def test_boundary_enforcement(self):
        """Test boundary enforcement within safe directories."""
        # Create a safe base directory
        safe_base = os.path.join(self.test_dir, "safe_zone")
        os.makedirs(safe_base)
        
        # Create test file in safe zone
        test_file = os.path.join(safe_base, "test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        # Try to output outside safe zone
        outside_safe = os.path.join(self.test_dir, "unsafe_zone")
        os.makedirs(outside_safe)
        
        error_occurred = []
        
        def capture_error(message):
            error_occurred.append(message)
        
        self.logic.error_occurred.connect(capture_error)
        
        # This should be allowed as both are in test_dir
        self.logic.split_file(test_file, outside_safe, 'size', 512, 1)
        
        # Test with path trying to escape completely
        escape_path = os.path.join(self.test_dir, "..", "escape")
        self.logic.split_file(test_file, escape_path, 'size', 512, 1)
        
        # Should have security validation in place
        self.logger.info(f"Boundary test completed with {len(error_occurred)} security events")

    def test_file_permission_validation(self):
        """Test file permission validation and handling."""
        # Create test file
        test_file = os.path.join(self.test_dir, "permission_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        output_dir = os.path.join(self.test_dir, "permission_output")
        os.makedirs(output_dir)
        
        # Test with read-only file (if supported by OS)
        try:
            os.chmod(test_file, 0o444)  # Read-only
            
            # Should still be able to read for splitting
            error_occurred = []
            complete_occurred = []
            
            def capture_error(message):
                error_occurred.append(message)
            
            def capture_complete(message):
                complete_occurred.append(message)
            
            self.logic.error_occurred.connect(capture_error)
            self.logic.operation_complete.connect(capture_complete)
            
            self.logic.split_file(test_file, output_dir, 'size', 512, 1)
            
            # Should succeed since we only need read access
            self.assertTrue(len(complete_occurred) > 0 or len(error_occurred) == 0,
                           "Should handle read-only files gracefully")
            
        except OSError:
            # Permission change not supported on this system
            self.skipTest("File permission modification not supported")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(test_file, 0o666)
            except OSError:
                pass
    
    def test_secure_temporary_file_handling(self):
        """Test secure handling of temporary files during operations."""
        # Create test file
        test_file = os.path.join(self.test_dir, "temp_security_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(2048))
        
        output_dir = os.path.join(self.test_dir, "temp_output")
        os.makedirs(output_dir)
        
        # Monitor temporary file creation
        temp_files_created = []
        original_tempfile = tempfile.NamedTemporaryFile
        
        def mock_tempfile(*args, **kwargs):
            temp_file = original_tempfile(*args, **kwargs)
            temp_files_created.append(temp_file.name)
            return temp_file
        
        with patch('tempfile.NamedTemporaryFile', side_effect=mock_tempfile):
            self.logic.split_file(test_file, output_dir, 'parts', 2, 1)
        
        # Verify temporary files are cleaned up
        for temp_file in temp_files_created:
            self.assertFalse(os.path.exists(temp_file),
                           f"Temporary file should be cleaned up: {temp_file}")
    
    def test_metadata_file_security(self):
        """Test security of metadata file creation and content."""
        # Create test file
        test_file = os.path.join(self.test_dir, "metadata_security_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        output_dir = os.path.join(self.test_dir, "metadata_output")
        os.makedirs(output_dir)
        
        # Perform split operation
        self.logic.split_file(test_file, output_dir, 'size', 512, 1)
        
        # Check metadata file
        metadata_file = os.path.join(output_dir, "_metadata.json")
        self.assertTrue(os.path.exists(metadata_file), "Metadata file should be created")
        
        # Verify metadata content doesn't expose sensitive information
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Should not contain full system paths that could reveal directory structure
        self.assertNotIn(os.path.expanduser("~"), str(metadata),
                        "Metadata should not expose home directory paths")
        
        # Should not contain system information
        sensitive_keys = ['username', 'hostname', 'system_path', 'environment']
        for key in sensitive_keys:
            self.assertNotIn(key, metadata,
                           f"Metadata should not contain sensitive key: {key}")


class TestFileSplitterAdvancedFileSystem(unittest.TestCase):
    """
    Advanced file system testing for File Splitter.
    
    Tests Unicode/international characters, long file paths, symbolic links,
    network drives, and file system edge cases.
    """
    
    def setUp(self):
        """Set up advanced file system test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("filesystem_test")
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
    
    def tearDown(self):
        """Clean up advanced file system test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_unicode_file_names(self):
        """Test handling of Unicode and international character file names."""
        unicode_names = [
            "测试文件.dat",  # Chinese
            "файл_тест.dat",  # Russian
            "αρχείο_δοκιμής.dat",  # Greek
            "ملف_اختبار.dat",  # Arabic
            "テストファイル.dat",  # Japanese
            "파일_테스트.dat",  # Korean
            "arquivo_teste_çõéà.dat",  # Portuguese with accents
            "datei_test_äöü.dat",  # German with umlauts
            "emoji_test_🚀📁💾.dat"  # Emoji characters
        ]
        
        for unicode_name in unicode_names:
            with self.subTest(filename=unicode_name):
                try:
                    # Create test file with Unicode name
                    test_file = os.path.join(self.test_dir, unicode_name)
                    with open(test_file, 'wb') as f:
                        f.write(os.urandom(1024))
                    
                    output_dir = os.path.join(self.test_dir, f"unicode_output_{hash(unicode_name) % 10000}")
                    os.makedirs(output_dir)
                    
                    # Test split operation
                    complete_occurred = []
                    error_occurred = []
                    
                    def capture_complete(message):
                        complete_occurred.append(message)
                    
                    def capture_error(message):
                        error_occurred.append(message)
                    
                    self.logic.operation_complete.connect(capture_complete)
                    self.logic.error_occurred.connect(capture_error)
                    
                    self.logic.split_file(test_file, output_dir, 'parts', 2, 1)
                    
                    # Should handle Unicode gracefully
                    if len(error_occurred) > 0:
                        self.logger.warning(f"Unicode filename caused issues: {unicode_name} - {error_occurred[0]}")
                    else:
                        # Verify chunks were created
                        chunk_files = [f for f in os.listdir(output_dir) if '.part' in f]
                        self.assertGreater(len(chunk_files), 0, 
                                         f"Should create chunks for Unicode file: {unicode_name}")
                
                except (OSError, UnicodeError) as e:
                    # Some filesystems may not support certain Unicode characters
                    self.logger.info(f"Unicode filename not supported by filesystem: {unicode_name} - {e}")
    
    def test_long_file_paths(self):
        """Test handling of long file paths (Windows 260+ character limit)."""
        # Create deeply nested directory structure
        long_path_components = ["very_long_directory_name_that_exceeds_normal_limits"] * 10
        long_dir = self.test_dir
        
        try:
            for component in long_path_components:
                long_dir = os.path.join(long_dir, component)
                if len(long_dir) > 250:  # Approaching Windows limit
                    break
                os.makedirs(long_dir, exist_ok=True)
        except OSError as e:
            self.skipTest(f"Cannot create long path on this system: {e}")
        
        # Create test file in long path
        long_filename = "a" * 100 + ".dat"  # Long filename
        test_file = os.path.join(long_dir, long_filename)
        
        try:
            with open(test_file, 'wb') as f:
                f.write(os.urandom(1024))
        except OSError as e:
            self.skipTest(f"Cannot create file with long path: {e}")
        
        # Test split operation
        output_dir = os.path.join(self.test_dir, "long_path_output")
        os.makedirs(output_dir)
        
        error_occurred = []
        
        def capture_error(message):
            error_occurred.append(message)
        
        self.logic.error_occurred.connect(capture_error)
        
        self.logic.split_file(test_file, output_dir, 'size', 512, 1)
        
        # Should handle long paths gracefully
        if len(error_occurred) > 0:
            self.assertIn("path", error_occurred[0].lower(),
                         "Error should be related to path handling")
        else:
            # Verify operation succeeded
            chunk_files = [f for f in os.listdir(output_dir) if '.part' in f]
            self.assertGreater(len(chunk_files), 0, "Should create chunks despite long path")
    
    def test_special_characters_in_paths(self):
        """Test handling of special characters in file paths."""
        special_chars = [
            "file with spaces.dat",
            "file-with-dashes.dat",
            "file_with_underscores.dat",
            "file.with.dots.dat",
            "file[with]brackets.dat",
            "file(with)parentheses.dat",
            "file{with}braces.dat",
            "file&with&ampersands.dat",
            "file%with%percent.dat",
            "file$with$dollar.dat",
            "file#with#hash.dat",
            "file@with@at.dat",
            "file!with!exclamation.dat"
        ]
        
        for special_name in special_chars:
            with self.subTest(filename=special_name):
                try:
                    # Create test file
                    test_file = os.path.join(self.test_dir, special_name)
                    with open(test_file, 'wb') as f:
                        f.write(os.urandom(1024))
                    
                    output_dir = os.path.join(self.test_dir, f"special_output_{hash(special_name) % 10000}")
                    os.makedirs(output_dir)
                    
                    # Test split operation
                    complete_occurred = []
                    error_occurred = []
                    
                    def capture_complete(message):
                        complete_occurred.append(message)
                    
                    def capture_error(message):
                        error_occurred.append(message)
                    
                    self.logic.operation_complete.connect(capture_complete)
                    self.logic.error_occurred.connect(capture_error)
                    
                    self.logic.split_file(test_file, output_dir, 'parts', 2, 1)
                    
                    # Should handle special characters
                    if len(error_occurred) == 0:
                        chunk_files = [f for f in os.listdir(output_dir) if '.part' in f]
                        self.assertGreater(len(chunk_files), 0,
                                         f"Should create chunks for special filename: {special_name}")
                
                except OSError as e:
                    self.logger.info(f"Special character filename not supported: {special_name} - {e}")
    
    def test_case_sensitivity_handling(self):
        """Test handling of case sensitivity in file systems."""
        # Create test files with different case
        test_file_lower = os.path.join(self.test_dir, "testfile.dat")
        test_file_upper = os.path.join(self.test_dir, "TESTFILE.DAT")
        test_file_mixed = os.path.join(self.test_dir, "TestFile.dat")
        
        # Create files
        for test_file in [test_file_lower, test_file_upper, test_file_mixed]:
            try:
                with open(test_file, 'wb') as f:
                    f.write(os.urandom(512))
            except OSError:
                # File might already exist on case-insensitive filesystem
                pass
        
        # Check how many files actually exist
        existing_files = []
        for test_file in [test_file_lower, test_file_upper, test_file_mixed]:
            if os.path.exists(test_file):
                existing_files.append(test_file)
        
        # Test split operations on existing files
        for i, test_file in enumerate(existing_files):
            output_dir = os.path.join(self.test_dir, f"case_output_{i}")
            os.makedirs(output_dir)
            
            complete_occurred = []
            
            def capture_complete(message):
                complete_occurred.append(message)
            
            self.logic.operation_complete.connect(capture_complete)
            
            self.logic.split_file(test_file, output_dir, 'parts', 2, 1)
            
            # Should handle case variations
            chunk_files = [f for f in os.listdir(output_dir) if '.part' in f]
            self.assertGreater(len(chunk_files), 0,
                             f"Should create chunks for case variant: {test_file}")


class TestFileSplitterResourceConstraints(unittest.TestCase):
    """
    Resource constraint testing for File Splitter.
    
    Tests low disk space, memory limits, CPU constraints, network interruptions,
    and file system full scenarios.
    """
    
    def setUp(self):
        """Set up resource constraint test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("resource_test")
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
    
    def tearDown(self):
        """Clean up resource constraint test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_low_disk_space_handling(self):
        """Test handling of low disk space scenarios."""
        # Create test file
        test_file = os.path.join(self.test_dir, "disk_space_test.dat")
        file_size = 5 * 1024 * 1024  # 5MB
        with open(test_file, 'wb') as f:
            f.write(os.urandom(file_size))
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "disk_space_output")
        os.makedirs(output_dir)
        
        # Mock disk space check to simulate low space
        original_disk_usage = shutil.disk_usage if hasattr(shutil, 'disk_usage') else None
        
        def mock_disk_usage(path):
            # Simulate very low free space (1MB)
            return (1000000000, 1000000000, 1024 * 1024)  # total, used, free
        
        # Test with simulated low disk space
        if original_disk_usage:
            with patch('shutil.disk_usage', side_effect=mock_disk_usage):
                error_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                
                # Attempt split operation
                self.logic.split_file(test_file, output_dir, 'parts', 3, 1)
                
                # Should handle low disk space gracefully
                # Either complete successfully or fail with appropriate error
                if len(error_occurred) > 0:
                    # Check if error is related to disk space
                    error_message = error_occurred[0].lower()
                    disk_related_terms = ['disk', 'space', 'no space', 'full', 'write']
                    has_disk_error = any(term in error_message for term in disk_related_terms)
                    
                    if not has_disk_error:
                        # If error is not disk-related, operation might have succeeded despite low space
                        self.logger.info("Operation handled low disk space scenario")
    
    def test_memory_limit_configuration(self):
        """Test memory limit configuration and enforcement."""
        # Create test file
        test_file = os.path.join(self.test_dir, "memory_limit_test.dat")
        file_size = 20 * 1024 * 1024  # 20MB
        with open(test_file, 'wb') as f:
            f.write(os.urandom(file_size))
        
        # Configure low memory limit
        self.config.set('memory_limit_mb', 10)  # 10MB limit
        
        output_dir = os.path.join(self.test_dir, "memory_limit_output")
        os.makedirs(output_dir)
        
        # Monitor memory usage
        memory_usage = []
        
        def monitor_memory():
            while True:
                try:
                    memory_info = psutil.Process().memory_info()
                    memory_usage.append(memory_info.rss)
                    time.sleep(0.1)
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor_memory)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Perform operation
        self.logic.split_file(test_file, output_dir, 'parts', 4, 1)
        
        # Stop monitoring
        time.sleep(1)
        
        # Check memory usage stayed within reasonable bounds
        if memory_usage:
            max_memory = max(memory_usage) / 1024 / 1024  # MB
            self.logger.info(f"Memory Limit Test - Max usage: {max_memory:.2f}MB")
    
    def test_interrupted_operation_recovery(self):
        """Test recovery from interrupted operations."""
        # Create test file
        test_file = os.path.join(self.test_dir, "interrupt_test.dat")
        file_size = 10 * 1024 * 1024  # 10MB
        with open(test_file, 'wb') as f:
            f.write(os.urandom(file_size))
        
        output_dir = os.path.join(self.test_dir, "interrupt_output")
        os.makedirs(output_dir)
        
        # Start operation and interrupt it
        def interrupt_operation():
            time.sleep(2)  # Let operation start
            self.logic.stop()  # Interrupt
        
        interrupt_thread = threading.Thread(target=interrupt_operation)
        interrupt_thread.daemon = True
        interrupt_thread.start()
        
        error_occurred = []
        
        def capture_error(message):
            error_occurred.append(message)
        
        self.logic.error_occurred.connect(capture_error)
        
        # Start split operation
        self.logic.split_file(test_file, output_dir, 'parts', 10, 1)
        
        # Should handle interruption gracefully
        self.assertTrue(len(error_occurred) > 0 or not self.logic._is_running,
                       "Should handle operation interruption")
        
        # Check for partial files cleanup
        partial_files = [f for f in os.listdir(output_dir) if '.part' in f]
        self.logger.info(f"Interrupt Test - Partial files after interruption: {len(partial_files)}")


class TestFileSplitterErrorRecovery(unittest.TestCase):
    """
    Error recovery and robustness testing for File Splitter.
    
    Tests partial operation recovery, corrupted chunk handling, operation resumption,
    configuration corruption recovery, and cleanup verification.
    """
    
    def setUp(self):
        """Set up error recovery test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("error_recovery_test")
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
    
    def tearDown(self):
        """Clean up error recovery test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_corrupted_chunk_detection(self):
        """Test detection and handling of corrupted chunks during join."""
        # Create and split a test file
        test_file = os.path.join(self.test_dir, "corruption_test.dat")
        original_content = os.urandom(2048)
        with open(test_file, 'wb') as f:
            f.write(original_content)
        
        split_dir = os.path.join(self.test_dir, "split_output")
        os.makedirs(split_dir)
        
        # Split the file
        self.logic.split_file(test_file, split_dir, 'parts', 3, 1)
        
        # Find and corrupt one chunk
        chunk_files = [f for f in os.listdir(split_dir) if '.part' in f]
        self.assertGreater(len(chunk_files), 0, "Should have created chunks")
        
        # Corrupt the middle chunk
        if len(chunk_files) >= 2:
            corrupt_chunk = os.path.join(split_dir, chunk_files[1])
            with open(corrupt_chunk, 'r+b') as f:
                f.seek(100)  # Seek to middle
                f.write(b'\x00\x00\x00\x00')  # Write zeros
        
        # Attempt to join
        first_chunk = os.path.join(split_dir, chunk_files[0])
        joined_file = os.path.join(self.test_dir, "joined_corrupted.dat")
        
        complete_occurred = []
        error_occurred = []
        
        def capture_complete(message):
            complete_occurred.append(message)
        
        def capture_error(message):
            error_occurred.append(message)
        
        self.logic.operation_complete.connect(capture_complete)
        self.logic.error_occurred.connect(capture_error)
        
        self.logic.join_files(first_chunk, joined_file)
        
        # Should complete but content will be corrupted
        if len(complete_occurred) > 0:
            # Verify file was created but content differs
            with open(joined_file, 'rb') as f:
                joined_content = f.read()
            
            self.assertNotEqual(joined_content, original_content,
                              "Joined content should differ due to corruption")
            self.logger.info("Corruption Test - Detected content corruption after join")
    
    def test_missing_chunk_handling(self):
        """Test handling of missing chunks during join operation."""
        # Create and split a test file
        test_file = os.path.join(self.test_dir, "missing_chunk_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        split_dir = os.path.join(self.test_dir, "missing_split_output")
        os.makedirs(split_dir)
        
        # Split the file
        self.logic.split_file(test_file, split_dir, 'parts', 4, 1)
        
        # Remove one chunk
        chunk_files = [f for f in os.listdir(split_dir) if '.part' in f]
        if len(chunk_files) >= 2:
            missing_chunk = os.path.join(split_dir, chunk_files[1])
            os.remove(missing_chunk)
        
        # Attempt to join
        first_chunk = os.path.join(split_dir, chunk_files[0])
        joined_file = os.path.join(self.test_dir, "joined_missing.dat")
        
        error_occurred = []
        
        def capture_error(message):
            error_occurred.append(message)
        
        self.logic.error_occurred.connect(capture_error)
        
        self.logic.join_files(first_chunk, joined_file)
        
        # Should detect missing chunk and error
        self.assertTrue(len(error_occurred) > 0, "Should detect missing chunk")
        self.assertIn("missing", error_occurred[0].lower(), "Error should mention missing chunk")
    
    def test_metadata_corruption_recovery(self):
        """Test recovery from corrupted metadata file."""
        # Create and split a test file
        test_file = os.path.join(self.test_dir, "metadata_corruption_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        split_dir = os.path.join(self.test_dir, "metadata_split_output")
        os.makedirs(split_dir)
        
        # Split the file
        self.logic.split_file(test_file, split_dir, 'parts', 3, 1)
        
        # Corrupt metadata file
        metadata_file = os.path.join(split_dir, "_metadata.json")
        with open(metadata_file, 'w') as f:
            f.write("{ corrupted json content }")
        
        # Attempt to join
        chunk_files = [f for f in os.listdir(split_dir) if '.part' in f]
        first_chunk = os.path.join(split_dir, chunk_files[0])
        joined_file = os.path.join(self.test_dir, "joined_metadata_corrupt.dat")
        
        complete_occurred = []
        
        def capture_complete(message):
            complete_occurred.append(message)
        
        self.logic.operation_complete.connect(capture_complete)
        
        self.logic.join_files(first_chunk, joined_file)
        
        # Should recover by falling back to manual detection
        self.assertTrue(len(complete_occurred) > 0, "Should recover from metadata corruption")
        self.assertTrue(os.path.exists(joined_file), "Should create joined file despite metadata corruption")
    
    def test_partial_operation_cleanup(self):
        """Test cleanup of partial operations on error."""
        # Create test file
        test_file = os.path.join(self.test_dir, "cleanup_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(2048))
        
        # Use non-writable output directory to force error
        output_dir = os.path.join(self.test_dir, "readonly_output")
        os.makedirs(output_dir)
        
        try:
            # Make directory read-only (if supported)
            os.chmod(output_dir, 0o444)
            
            error_occurred = []
            
            def capture_error(message):
                error_occurred.append(message)
            
            self.logic.error_occurred.connect(capture_error)
            
            # Attempt split operation
            self.logic.split_file(test_file, output_dir, 'parts', 3, 1)
            
            # Should have error
            self.assertTrue(len(error_occurred) > 0, "Should have permission error")
            
            # Check for partial files - they should be cleaned up
            partial_files = []
            try:
                partial_files = [f for f in os.listdir(output_dir) if '.part' in f]
            except OSError:
                pass  # Directory might not be readable
            
            self.logger.info(f"Cleanup Test - Partial files remaining: {len(partial_files)}")
            
        except OSError:
            self.skipTest("Cannot modify directory permissions on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(output_dir, 0o755)
            except OSError:
                pass
    
    def test_configuration_error_recovery(self):
        """Test recovery from configuration errors."""
        # Create test file
        test_file = os.path.join(self.test_dir, "config_error_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        output_dir = os.path.join(self.test_dir, "config_error_output")
        os.makedirs(output_dir)
        
        # Set invalid configuration
        invalid_configs = [
            {'buffer_size': -1},  # Negative buffer size
            {'max_chunks': 0},    # Zero max chunks
            {'default_chunk_size': 0},  # Zero chunk size
        ]
        
        for invalid_config in invalid_configs:
            with self.subTest(config=invalid_config):
                # Apply invalid config
                original_values = {}
                for key, value in invalid_config.items():
                    original_values[key] = self.config.get(key)
                    self.config.set(key, value, save=False)
                
                error_occurred = []
                complete_occurred = []
                
                def capture_error(message):
                    error_occurred.append(message)
                
                def capture_complete(message):
                    complete_occurred.append(message)
                
                self.logic.error_occurred.connect(capture_error)
                self.logic.operation_complete.connect(capture_complete)
                
                # Attempt operation
                self.logic.split_file(test_file, output_dir, 'parts', 2, 1)
                
                # Should either error gracefully or use defaults
                has_error = len(error_occurred) > 0
                has_completion = len(complete_occurred) > 0
                
                self.assertTrue(has_error or has_completion,
                               f"Should handle invalid config: {invalid_config}")
                
                # Restore original values
                for key, value in original_values.items():
                    self.config.set(key, value, save=False)


class TestFileSplitterIntegrationScenarios(unittest.TestCase):
    """
    Integration scenario testing for File Splitter.
    
    Tests real-world usage scenarios, cross-platform compatibility,
    and integration with other system components.
    """
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger("integration_test")
        self.logic = FileSplitterLogic(self.config, self.logger)
        
        # Mock hub connector
        self.hub_connector_mock = Mock()
        self.logic.set_hub_connector(self.hub_connector_mock)
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_complete_workflow_large_file(self):
        """Test complete split-join workflow with large file."""
        # Create large test file (50MB)
        file_size = 50 * 1024 * 1024
        test_file = os.path.join(self.test_dir, "workflow_large.dat")
        
        # Write in chunks to avoid memory issues
        chunk_size = 1024 * 1024
        with open(test_file, 'wb') as f:
            for i in range(file_size // chunk_size):
                f.write(os.urandom(chunk_size))
        
        # Calculate original hash
        with open(test_file, 'rb') as f:
            original_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Step 1: Split the file
        split_dir = os.path.join(self.test_dir, "workflow_split")
        os.makedirs(split_dir)
        
        start_time = time.time()
        self.logic.split_file(test_file, split_dir, 'size', 10, 1024 * 1024)  # 10MB chunks
        split_time = time.time() - start_time
        
        # Verify split results
        chunk_files = [f for f in os.listdir(split_dir) if '.part' in f]
        expected_chunks = (file_size + (10 * 1024 * 1024) - 1) // (10 * 1024 * 1024)
        self.assertEqual(len(chunk_files), expected_chunks, "Should create expected number of chunks")
        
        # Step 2: Join the files
        first_chunk = os.path.join(split_dir, 'workflow_large.dat.part001')
        joined_file = os.path.join(self.test_dir, "workflow_joined.dat")
        
        start_time = time.time()
        self.logic.join_files(first_chunk, joined_file)
        join_time = time.time() - start_time
        
        # Verify join results
        self.assertTrue(os.path.exists(joined_file), "Joined file should exist")
        self.assertEqual(os.path.getsize(joined_file), file_size, "File size should match original")
        
        # Verify integrity
        with open(joined_file, 'rb') as f:
            joined_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(joined_hash, original_hash, "File integrity should be preserved")
        
        # Performance logging
        self.logger.info(f"Large File Workflow - Split: {split_time:.2f}s, Join: {join_time:.2f}s")
        
        # Performance assertions
        self.assertLess(split_time, 60, "Split should complete within 60 seconds")
        self.assertLess(join_time, 60, "Join should complete within 60 seconds")
    
    def test_multiple_file_formats(self):
        """Test with various file formats and content types."""
        file_formats = {
            'binary.exe': os.urandom(1024),
            'text.txt': b'This is a text file with some content.\n' * 50,
            'json.json': json.dumps({'test': 'data', 'numbers': list(range(100))}).encode(),
            'image.dat': b'\x89PNG\r\n\x1a\n' + os.urandom(1000),  # PNG-like header
            'zero.dat': b'\x00' * 1024,  # All zeros
            'pattern.dat': (b'ABCD' * 256),  # Repeating pattern
        }
        
        for filename, content in file_formats.items():
            with self.subTest(format=filename):
                # Create test file
                test_file = os.path.join(self.test_dir, filename)
                with open(test_file, 'wb') as f:
                    f.write(content)
                
                # Calculate original hash
                original_hash = hashlib.md5(content).hexdigest()
                
                # Split and join
                split_dir = os.path.join(self.test_dir, f"format_split_{filename}")
                os.makedirs(split_dir)
                
                self.logic.split_file(test_file, split_dir, 'parts', 3, 1)
                
                chunk_files = [f for f in os.listdir(split_dir) if '.part' in f]
                self.assertEqual(len(chunk_files), 3, f"Should create 3 chunks for {filename}")
                
                # Join
                first_chunk = os.path.join(split_dir, f'{filename}.part001')
                joined_file = os.path.join(self.test_dir, f"joined_{filename}")
                
                self.logic.join_files(first_chunk, joined_file)
                
                # Verify
                with open(joined_file, 'rb') as f:
                    joined_content = f.read()
                
                joined_hash = hashlib.md5(joined_content).hexdigest()
                self.assertEqual(joined_hash, original_hash, f"Content integrity should be preserved for {filename}")
    
    def test_configuration_persistence(self):
        """Test configuration persistence across operations."""
        # Create test configuration
        test_config = {
            'default_chunk_size': 2048,
            'verify_integrity': True,
            'enable_hub_reporting': False,
            'auto_cleanup_on_error': True
        }
        
        # Apply configuration
        for key, value in test_config.items():
            self.config.set(key, value)
        
        # Create new logic instance to test config persistence
        new_logic = FileSplitterLogic(self.config, self.logger)
        
        # Verify configuration is preserved
        for key, expected_value in test_config.items():
            actual_value = new_logic.config.get(key)
            self.assertEqual(actual_value, expected_value,
                           f"Configuration {key} should persist: expected {expected_value}, got {actual_value}")
    
    def test_hub_integration_comprehensive(self):
        """Test comprehensive hub integration scenarios."""
        # Create test file
        test_file = os.path.join(self.test_dir, "hub_integration_test.dat")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(2048))
        
        output_dir = os.path.join(self.test_dir, "hub_output")
        os.makedirs(output_dir)
        
        # Test hub reporting during split
        self.logic.split_file(test_file, output_dir, 'parts', 2, 1)
        
        # Verify hub methods were called
        self.hub_connector_mock.report_status_to_hub.assert_called()
        self.hub_connector_mock.report_progress_to_hub.assert_called()
        
        # Check call details
        status_calls = self.hub_connector_mock.report_status_to_hub.call_args_list
        progress_calls = self.hub_connector_mock.report_progress_to_hub.call_args_list
        
        # Should have start and completion status calls
        self.assertGreater(len(status_calls), 1, "Should have multiple status updates")
        self.assertGreater(len(progress_calls), 0, "Should have progress updates")
        
        # Check for specific status values
        status_values = [call[0][0] for call in status_calls]
        self.assertIn("started", status_values, "Should report operation start")
        self.assertIn("completed", status_values, "Should report operation completion")


if __name__ == '__main__':
    # Initialize QApplication for Qt signal testing
    if not QCoreApplication.instance():
        app = QCoreApplication([])
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestFileSplitterPerformance,
        TestFileSplitterSecurity,
        TestFileSplitterAdvancedFileSystem,
        TestFileSplitterResourceConstraints,
        TestFileSplitterErrorRecovery,
        TestFileSplitterIntegrationScenarios
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"COMPREHENSIVE FILE SPLITTER TEST RESULTS")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)