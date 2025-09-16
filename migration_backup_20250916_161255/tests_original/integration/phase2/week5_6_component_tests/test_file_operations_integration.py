"""
File Operation Integration Tests - Phase 2 Week 5-6
Comprehensive file operation integration testing for RFU system

Test Categories:
- File I/O operations (read, write, copy, move, delete)
- Permission handling and access control
- Concurrent access scenarios and file locking
- Large file processing and streaming
- Cross-platform file system compatibility
"""

import hashlib
import json
import mmap
import os
import platform
import shutil
import stat
# Import RFU system components
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import psutil
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from utils.file_operations import FileOperations
    from utils.file_utils import FileUtils
    from utils.logging_utils import setup_logger
except ImportError as e:
    print(f"Warning: Could not import RFU components: {e}")
    # Create mock classes for testing
    class FileOperations:
        @staticmethod
        def copy_file(src, dst):
            shutil.copy2(src, dst)
        
        @staticmethod
        def move_file(src, dst):
            shutil.move(src, dst)
        
        @staticmethod
        def delete_file(path):
            os.remove(path)
    
    class FileUtils:
        @staticmethod
        def get_file_hash(path, algorithm='md5'):
            hash_obj = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        
        @staticmethod
        def get_file_info(path):
            stat_info = os.stat(path)
            return {
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'created': stat_info.st_ctime,
                'permissions': oct(stat_info.st_mode)
            }

logger = setup_logger('file_operations_integration_tests') if 'setup_logger' in globals() else None


class FileOperationIntegrationTestSuite:
    """Comprehensive file operation integration test suite"""
    
    def __init__(self):
        self.test_dir = None
        self.test_results = {
            'file_io_operations': {},
            'permission_handling': {},
            'concurrent_access': {},
            'large_file_processing': {},
            'cross_platform_compatibility': {}
        }
        self.performance_metrics = {}
        
    def setup_test_directory(self):
        """Set up test directory structure with sample files"""
        self.test_dir = tempfile.mkdtemp(prefix='rfu_file_test_')
        
        # Create directory structure
        dirs = [
            'input',
            'output',
            'temp',
            'large_files',
            'permissions_test',
            'concurrent_test',
            'nested/deep/structure'
        ]
        
        for dir_path in dirs:
            os.makedirs(os.path.join(self.test_dir, dir_path), exist_ok=True)
        
        # Create sample files with different sizes and content
        sample_files = {
            'small_text.txt': b'This is a small test file.',
            'medium_binary.dat': os.urandom(1024 * 100),  # 100KB
            'unicode_content.txt': 'Unicode test: αβγδε ñáéíóú 中文 🌟✨'.encode('utf-8'),
            'empty_file.dat': b'',
            'special_chars.txt': b'File with special chars: !@#$%^&*()[]{}|;:,.<>?'
        }
        
        for filename, content in sample_files.items():
            file_path = os.path.join(self.test_dir, 'input', filename)
            with open(file_path, 'wb') as f:
                f.write(content)
        
        # Create large test file
        large_file_path = os.path.join(self.test_dir, 'large_files', 'large_test.dat')
        with open(large_file_path, 'wb') as f:
            # Write 10MB of test data
            for i in range(10240):
                f.write(b'A' * 1024)
        
        return self.test_dir
    
    def cleanup_test_directory(self):
        """Clean up test directory"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestFileIOOperations:
    """Test basic file I/O operations"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = FileOperationIntegrationTestSuite()
        self.test_dir = self.test_suite.setup_test_directory()
        yield
        self.test_suite.cleanup_test_directory()
    
    def test_file_reading_operations(self):
        """Test various file reading operations"""
        input_dir = os.path.join(self.test_dir, 'input')
        
        # Test reading different file types
        test_cases = [
            ('small_text.txt', b'This is a small test file.'),
            ('unicode_content.txt', 'Unicode test: αβγδε ñáéíóú 中文 🌟✨'.encode('utf-8')),
            ('empty_file.dat', b'')
        ]
        
        for filename, expected_content in test_cases:
            file_path = os.path.join(input_dir, filename)
            
            # Test binary reading
            with open(file_path, 'rb') as f:
                content = f.read()
            assert content == expected_content, f"Binary read failed for {filename}"
            
            # Test chunked reading
            with open(file_path, 'rb') as f:
                chunks = []
                while True:
                    chunk = f.read(10)  # Small chunks
                    if not chunk:
                        break
                    chunks.append(chunk)
            
            reconstructed = b''.join(chunks)
            assert reconstructed == expected_content, f"Chunked read failed for {filename}"
        
        self.test_suite.test_results['file_io_operations']['reading'] = 'PASS'
    
    def test_file_writing_operations(self):
        """Test various file writing operations"""
        output_dir = os.path.join(self.test_dir, 'output')
        
        # Test different write modes and content types
        test_cases = [
            ('write_binary.dat', b'Binary data: \x00\x01\x02\x03\xFF'),
            ('write_text.txt', 'Text content with unicode: café'.encode('utf-8')),
            ('write_large_chunks.dat', b'CHUNK' * 1000)
        ]
        
        for filename, content in test_cases:
            file_path = os.path.join(output_dir, filename)
            
            # Test standard writing
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Verify written content
            with open(file_path, 'rb') as f:
                written_content = f.read()
            assert written_content == content, f"Write verification failed for {filename}"
            
            # Test append mode
            append_content = b' APPENDED'
            with open(file_path, 'ab') as f:
                f.write(append_content)
            
            with open(file_path, 'rb') as f:
                final_content = f.read()
            assert final_content == content + append_content, f"Append operation failed for {filename}"
        
        self.test_suite.test_results['file_io_operations']['writing'] = 'PASS'
    
    def test_file_copy_operations(self):
        """Test file copy operations with various scenarios"""
        input_dir = os.path.join(self.test_dir, 'input')
        output_dir = os.path.join(self.test_dir, 'output')
        
        # Test copying different file types
        test_files = ['small_text.txt', 'medium_binary.dat', 'unicode_content.txt', 'empty_file.dat']
        
        for filename in test_files:
            src_path = os.path.join(input_dir, filename)
            dst_path = os.path.join(output_dir, f'copy_{filename}')
            
            # Perform copy operation
            start_time = time.time()
            shutil.copy2(src_path, dst_path)
            copy_time = time.time() - start_time
            
            # Verify copy integrity
            assert os.path.exists(dst_path), f"Copy failed - destination not found: {filename}"
            
            # Compare file sizes
            src_size = os.path.getsize(src_path)
            dst_size = os.path.getsize(dst_path)
            assert src_size == dst_size, f"Copy size mismatch for {filename}: {src_size} != {dst_size}"
            
            # Compare file content
            with open(src_path, 'rb') as f:
                src_content = f.read()
            with open(dst_path, 'rb') as f:
                dst_content = f.read()
            assert src_content == dst_content, f"Copy content mismatch for {filename}"
            
            # Compare metadata (timestamps should be preserved with copy2)
            src_stat = os.stat(src_path)
            dst_stat = os.stat(dst_path)
            assert abs(src_stat.st_mtime - dst_stat.st_mtime) < 1, f"Metadata not preserved for {filename}"
        
        self.test_suite.test_results['file_io_operations']['copying'] = 'PASS'
    
    def test_file_move_operations(self):
        """Test file move operations"""
        temp_dir = os.path.join(self.test_dir, 'temp')
        output_dir = os.path.join(self.test_dir, 'output')
        
        # Create test files for moving
        test_files = ['move_test_1.txt', 'move_test_2.dat', 'move_test_3.bin']
        
        for filename in test_files:
            src_path = os.path.join(temp_dir, filename)
            
            # Create source file
            test_content = f'Move test content for {filename}'.encode('utf-8')
            with open(src_path, 'wb') as f:
                f.write(test_content)
            
            dst_path = os.path.join(output_dir, f'moved_{filename}')
            
            # Perform move operation
            shutil.move(src_path, dst_path)
            
            # Verify move operation
            assert not os.path.exists(src_path), f"Source file still exists after move: {filename}"
            assert os.path.exists(dst_path), f"Destination file not found after move: {filename}"
            
            # Verify content integrity
            with open(dst_path, 'rb') as f:
                moved_content = f.read()
            assert moved_content == test_content, f"Move content integrity failed for {filename}"
        
        self.test_suite.test_results['file_io_operations']['moving'] = 'PASS'
    
    def test_file_deletion_operations(self):
        """Test file deletion operations"""
        temp_dir = os.path.join(self.test_dir, 'temp')
        
        # Create test files for deletion
        test_files = ['delete_test_1.txt', 'delete_test_2.dat']
        created_files = []
        
        for filename in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f'Content for {filename}')
            created_files.append(file_path)
            assert os.path.exists(file_path), f"Test file creation failed: {filename}"
        
        # Test individual file deletion
        for file_path in created_files:
            os.remove(file_path)
            assert not os.path.exists(file_path), f"File deletion failed: {file_path}"
        
        # Test deletion of non-existent file (should handle gracefully)
        non_existent = os.path.join(temp_dir, 'non_existent.txt')
        try:
            os.remove(non_existent)
            assert False, "Should have raised exception for non-existent file"
        except FileNotFoundError:
            pass  # Expected behavior
        
        self.test_suite.test_results['file_io_operations']['deletion'] = 'PASS'


class TestPermissionHandling:
    """Test file permission handling and access control"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = FileOperationIntegrationTestSuite()
        self.test_dir = self.test_suite.setup_test_directory()
        yield
        self.test_suite.cleanup_test_directory()
    
    def test_permission_reading(self):
        """Test reading file permissions"""
        permissions_dir = os.path.join(self.test_dir, 'permissions_test')
        test_file = os.path.join(permissions_dir, 'permission_test.txt')
        
        # Create test file
        with open(test_file, 'w') as f:
            f.write('Permission test content')
        
        # Get and verify permissions
        file_stat = os.stat(test_file)
        permissions = stat.filemode(file_stat.st_mode)
        
        # Basic permission verification
        assert permissions is not None, "Failed to read file permissions"
        assert len(permissions) == 10, f"Invalid permission format: {permissions}"
        
        # Test permission components
        assert permissions[0] in ['-', 'd', 'l'], f"Invalid file type indicator: {permissions[0]}"
        
        self.test_suite.test_results['permission_handling']['reading'] = 'PASS'
    
    def test_permission_modification(self):
        """Test modifying file permissions"""
        if platform.system() == 'Windows':
            # Windows has limited POSIX permission support
            self.test_suite.test_results['permission_handling']['modification'] = 'SKIP_WINDOWS'
            return
        
        permissions_dir = os.path.join(self.test_dir, 'permissions_test')
        test_file = os.path.join(permissions_dir, 'permission_modify_test.txt')
        
        # Create test file
        with open(test_file, 'w') as f:
            f.write('Permission modification test')
        
        # Test making file read-only
        os.chmod(test_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
        # Verify read-only status
        file_stat = os.stat(test_file)
        is_writable = bool(file_stat.st_mode & stat.S_IWUSR)
        assert not is_writable, "File should be read-only"
        
        # Test that write operations fail
        try:
            with open(test_file, 'w') as f:
                f.write('Should fail')
            assert False, "Write to read-only file should have failed"
        except PermissionError:
            pass  # Expected behavior
        
        # Restore write permissions
        os.chmod(test_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        
        # Verify write is now possible
        with open(test_file, 'w') as f:
            f.write('Write should now work')
        
        self.test_suite.test_results['permission_handling']['modification'] = 'PASS'
    
    def test_access_control_validation(self):
        """Test access control validation"""
        permissions_dir = os.path.join(self.test_dir, 'permissions_test')
        
        # Test different access modes
        test_cases = [
            ('readable.txt', os.R_OK),
            ('writable.txt', os.W_OK),
            ('executable.txt', os.X_OK)
        ]
        
        for filename, access_mode in test_cases:
            file_path = os.path.join(permissions_dir, filename)
            
            # Create test file
            with open(file_path, 'w') as f:
                f.write(f'Access test for {filename}')
            
            # Test access check
            has_access = os.access(file_path, access_mode)
            
            # On most systems, newly created files should have read/write access
            if access_mode in [os.R_OK, os.W_OK]:
                assert has_access, f"Expected access not available for {filename}"
        
        self.test_suite.test_results['permission_handling']['access_control'] = 'PASS'


class TestConcurrentAccess:
    """Test concurrent file access scenarios"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = FileOperationIntegrationTestSuite()
        self.test_dir = self.test_suite.setup_test_directory()
        yield
        self.test_suite.cleanup_test_directory()
    
    def test_concurrent_file_reading(self):
        """Test multiple threads reading the same file"""
        concurrent_dir = os.path.join(self.test_dir, 'concurrent_test')
        test_file = os.path.join(concurrent_dir, 'concurrent_read_test.txt')
        
        # Create test file with substantial content
        test_content = 'Concurrent read test content.\n' * 1000
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        def read_worker(worker_id):
            """Worker function for concurrent reading"""
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                return len(content) == len(test_content)
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        # Execute concurrent reads
        num_workers = 10
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(read_worker, i) for i in range(num_workers)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all reads succeeded
        successful_reads = sum(1 for r in results if r is True)
        assert successful_reads == num_workers, f"Concurrent read failures: {results}"
        
        self.test_suite.test_results['concurrent_access']['concurrent_reading'] = 'PASS'
    
    def test_concurrent_file_writing(self):
        """Test concurrent writing to different files"""
        concurrent_dir = os.path.join(self.test_dir, 'concurrent_test')
        
        def write_worker(worker_id):
            """Worker function for concurrent writing"""
            file_path = os.path.join(concurrent_dir, f'concurrent_write_{worker_id}.txt')
            content = f'Worker {worker_id} content: ' + 'X' * 1000
            
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Verify write
                with open(file_path, 'r') as f:
                    written_content = f.read()
                
                return written_content == content
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        # Execute concurrent writes
        num_workers = 10
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(write_worker, i) for i in range(num_workers)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all writes succeeded
        successful_writes = sum(1 for r in results if r is True)
        assert successful_writes == num_workers, f"Concurrent write failures: {results}"
        
        # Verify all files exist
        for i in range(num_workers):
            file_path = os.path.join(concurrent_dir, f'concurrent_write_{i}.txt')
            assert os.path.exists(file_path), f"Concurrent write file missing: {i}"
        
        self.test_suite.test_results['concurrent_access']['concurrent_writing'] = 'PASS'
    
    def test_file_locking_behavior(self):
        """Test file locking behavior during operations"""
        concurrent_dir = os.path.join(self.test_dir, 'concurrent_test')
        test_file = os.path.join(concurrent_dir, 'locking_test.txt')
        
        # Create test file
        with open(test_file, 'w') as f:
            f.write('Locking test content')
        
        # Test exclusive access patterns
        lock_results = []
        
        def lock_test_worker(worker_id, operation_type):
            """Worker to test file locking scenarios"""
            try:
                if operation_type == 'read':
                    with open(test_file, 'r') as f:
                        content = f.read()
                        time.sleep(0.1)  # Hold file open briefly
                    return f"READ_SUCCESS_{worker_id}"
                
                elif operation_type == 'write':
                    with open(test_file, 'a') as f:
                        f.write(f'\nWorker {worker_id} addition')
                        time.sleep(0.1)  # Hold file open briefly
                    return f"WRITE_SUCCESS_{worker_id}"
                
            except Exception as e:
                return f"ERROR_{worker_id}: {str(e)}"
        
        # Test mixed read/write operations
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            
            # Submit mix of read and write operations
            for i in range(3):
                futures.append(executor.submit(lock_test_worker, i, 'read'))
                futures.append(executor.submit(lock_test_worker, i + 3, 'write'))
            
            for future in as_completed(futures):
                lock_results.append(future.result())
        
        # Analyze results
        successful_operations = [r for r in lock_results if 'SUCCESS' in r]
        errors = [r for r in lock_results if 'ERROR' in r]
        
        # Most operations should succeed (depending on OS file locking behavior)
        assert len(successful_operations) >= 4, f"Too many locking failures: {errors}"
        
        self.test_suite.test_results['concurrent_access']['file_locking'] = 'PASS'


class TestLargeFileProcessing:
    """Test large file processing and streaming operations"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = FileOperationIntegrationTestSuite()
        self.test_dir = self.test_suite.setup_test_directory()
        yield
        self.test_suite.cleanup_test_directory()
    
    def test_large_file_reading(self):
        """Test reading large files efficiently"""
        large_file_dir = os.path.join(self.test_dir, 'large_files')
        large_file = os.path.join(large_file_dir, 'large_test.dat')
        
        # Verify large file exists
        assert os.path.exists(large_file), "Large test file not found"
        file_size = os.path.getsize(large_file)
        assert file_size >= 10 * 1024 * 1024, f"Test file too small: {file_size} bytes"
        
        # Test streaming read
        start_time = time.time()
        bytes_read = 0
        chunk_size = 64 * 1024  # 64KB chunks
        
        with open(large_file, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                bytes_read += len(chunk)
        
        read_time = time.time() - start_time
        
        assert bytes_read == file_size, f"Read size mismatch: {bytes_read} != {file_size}"
        
        # Performance check (should read at reasonable speed)
        read_speed_mb_s = (bytes_read / (1024 * 1024)) / read_time
        assert read_speed_mb_s > 5, f"Large file read too slow: {read_speed_mb_s} MB/s"
        
        self.test_suite.test_results['large_file_processing']['reading'] = 'PASS'
        self.test_suite.performance_metrics['large_file_read_speed_mb_s'] = read_speed_mb_s
    
    def test_large_file_copying(self):
        """Test copying large files"""
        large_file_dir = os.path.join(self.test_dir, 'large_files')
        src_file = os.path.join(large_file_dir, 'large_test.dat')
        dst_file = os.path.join(large_file_dir, 'large_test_copy.dat')
        
        # Perform large file copy
        start_time = time.time()
        shutil.copy2(src_file, dst_file)
        copy_time = time.time() - start_time
        
        # Verify copy
        assert os.path.exists(dst_file), "Large file copy failed"
        
        src_size = os.path.getsize(src_file)
        dst_size = os.path.getsize(dst_file)
        assert src_size == dst_size, f"Large file copy size mismatch: {src_size} != {dst_size}"
        
        # Verify content integrity (hash comparison)
        src_hash = self._calculate_file_hash(src_file)
        dst_hash = self._calculate_file_hash(dst_file)
        assert src_hash == dst_hash, "Large file copy content integrity failed"
        
        # Performance validation
        copy_speed_mb_s = (src_size / (1024 * 1024)) / copy_time
        assert copy_speed_mb_s > 5, f"Large file copy too slow: {copy_speed_mb_s} MB/s"
        
        self.test_suite.test_results['large_file_processing']['copying'] = 'PASS'
        self.test_suite.performance_metrics['large_file_copy_speed_mb_s'] = copy_speed_mb_s
    
    def test_memory_mapped_file_access(self):
        """Test memory-mapped file access for large files"""
        large_file_dir = os.path.join(self.test_dir, 'large_files')
        large_file = os.path.join(large_file_dir, 'large_test.dat')
        
        # Test memory mapping
        with open(large_file, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                # Test random access
                file_size = len(mmapped_file)
                
                # Read from beginning
                start_data = mmapped_file[:1024]
                assert len(start_data) == 1024, "Memory map start read failed"
                
                # Read from middle
                middle_pos = file_size // 2
                middle_data = mmapped_file[middle_pos:middle_pos + 1024]
                assert len(middle_data) == 1024, "Memory map middle read failed"
                
                # Read from end
                end_data = mmapped_file[-1024:]
                assert len(end_data) == 1024, "Memory map end read failed"
                
                # Test seeking
                mmapped_file.seek(0)
                seek_data = mmapped_file.read(1024)
                assert seek_data == start_data, "Memory map seek failed"
        
        self.test_suite.test_results['large_file_processing']['memory_mapping'] = 'PASS'
    
    def test_streaming_hash_calculation(self):
        """Test streaming hash calculation for large files"""
        large_file_dir = os.path.join(self.test_dir, 'large_files')
        large_file = os.path.join(large_file_dir, 'large_test.dat')
        
        # Calculate hash using streaming method
        start_time = time.time()
        file_hash = self._calculate_file_hash(large_file)
        hash_time = time.time() - start_time
        
        assert file_hash is not None, "Hash calculation failed"
        assert len(file_hash) == 32, f"Invalid MD5 hash length: {len(file_hash)}"
        
        # Verify consistency
        second_hash = self._calculate_file_hash(large_file)
        assert file_hash == second_hash, "Hash calculation inconsistent"
        
        # Performance validation
        file_size = os.path.getsize(large_file)
        hash_speed_mb_s = (file_size / (1024 * 1024)) / hash_time
        assert hash_speed_mb_s > 5, f"Hash calculation too slow: {hash_speed_mb_s} MB/s"
        
        self.test_suite.test_results['large_file_processing']['streaming_hash'] = 'PASS'
        self.test_suite.performance_metrics['hash_calculation_speed_mb_s'] = hash_speed_mb_s
    
    def _calculate_file_hash(self, file_path, algorithm='md5'):
        """Calculate file hash using streaming method"""
        hash_obj = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()


class TestCrossPlatformCompatibility:
    """Test cross-platform file system compatibility"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = FileOperationIntegrationTestSuite()
        self.test_dir = self.test_suite.setup_test_directory()
        yield
        self.test_suite.cleanup_test_directory()
    
    def test_path_handling(self):
        """Test cross-platform path handling"""
        # Test Path object usage
        test_path = Path(self.test_dir) / 'cross_platform' / 'path_test.txt'
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file using Path object
        test_path.write_text('Cross-platform path test', encoding='utf-8')
        
        # Verify file creation
        assert test_path.exists(), "Path object file creation failed"
        assert test_path.is_file(), "Path object created non-file"
        
        # Test path operations
        assert test_path.suffix == '.txt', "Path suffix detection failed"
        assert test_path.stem == 'path_test', "Path stem detection failed"
        assert test_path.name == 'path_test.txt', "Path name detection failed"
        
        # Test path conversion
        str_path = str(test_path)
        assert os.path.exists(str_path), "Path to string conversion failed"
        
        self.test_suite.test_results['cross_platform_compatibility']['path_handling'] = 'PASS'
    
    def test_filename_character_support(self):
        """Test support for various filename characters"""
        cross_platform_dir = os.path.join(self.test_dir, 'cross_platform')
        os.makedirs(cross_platform_dir, exist_ok=True)
        
        # Test different filename patterns
        # Note: Some characters may not be supported on all platforms
        test_filenames = [
            'basic_filename.txt',
            'file with spaces.txt',
            'file-with-hyphens.txt',
            'file_with_underscores.txt',
            'file.with.dots.txt',
            'file123numbers.txt'
        ]
        
        if platform.system() != 'Windows':
            # Unix-specific characters
            test_filenames.extend([
                'file@symbol.txt',
                'file+plus.txt',
                'file=equals.txt'
            ])
        
        successful_files = []
        failed_files = []
        
        for filename in test_filenames:
            try:
                file_path = os.path.join(cross_platform_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(f'Test content for {filename}')
                
                # Verify file exists
                if os.path.exists(file_path):
                    successful_files.append(filename)
                else:
                    failed_files.append(filename)
                    
            except (OSError, UnicodeError) as e:
                failed_files.append(f"{filename}: {str(e)}")
        
        # Most basic filenames should work on all platforms
        basic_files = [f for f in successful_files if not any(c in f for c in ['@', '+', '='])]
        assert len(basic_files) >= 6, f"Basic filename support failed: {failed_files}"
        
        self.test_suite.test_results['cross_platform_compatibility']['filename_characters'] = 'PASS'
    
    def test_file_system_case_sensitivity(self):
        """Test file system case sensitivity behavior"""
        cross_platform_dir = os.path.join(self.test_dir, 'cross_platform')
        
        # Ensure directory exists
        os.makedirs(cross_platform_dir, exist_ok=True)
        
        # Create files with different cases
        file1 = os.path.join(cross_platform_dir, 'CaseSensitive.txt')
        file2 = os.path.join(cross_platform_dir, 'casesensitive.txt')
        
        with open(file1, 'w') as f:
            f.write('Upper case file')
        
        # Check if we can create a file with different case
        try:
            with open(file2, 'w') as f:
                f.write('Lower case file')
            
            # Check if both files exist (case-sensitive system)
            if os.path.exists(file1) and os.path.exists(file2):
                # On case-sensitive systems, files should have different content
                with open(file1, 'r') as f:
                    content1 = f.read()
                with open(file2, 'r') as f:
                    content2 = f.read()
                
                # On case-insensitive systems (like Windows), the second file overwrites the first
                if content1 == content2:
                    case_sensitive = False  # Case-insensitive filesystem
                else:
                    case_sensitive = True   # Case-sensitive filesystem
            else:
                case_sensitive = False
                
        except OSError:
            # File system doesn't allow different case files
            case_sensitive = False
        
        # Record the file system behavior
        self.test_suite.performance_metrics['filesystem_case_sensitive'] = case_sensitive
        
        self.test_suite.test_results['cross_platform_compatibility']['case_sensitivity'] = 'PASS'
    
    def test_symbolic_link_support(self):
        """Test symbolic link support (where available)"""
        if platform.system() == 'Windows':
            # Symbolic links require special permissions on Windows
            self.test_suite.test_results['cross_platform_compatibility']['symbolic_links'] = 'SKIP_WINDOWS'
            return
        
        cross_platform_dir = os.path.join(self.test_dir, 'cross_platform')
        
        # Create target file
        target_file = os.path.join(cross_platform_dir, 'symlink_target.txt')
        with open(target_file, 'w') as f:
            f.write('Symbolic link target content')
        
        # Create symbolic link
        link_file = os.path.join(cross_platform_dir, 'symlink_test.txt')
        
        try:
            os.symlink(target_file, link_file)
            
            # Verify symbolic link
            assert os.path.islink(link_file), "Symbolic link creation failed"
            assert os.path.exists(link_file), "Symbolic link target not accessible"
            
            # Test reading through symbolic link
            with open(link_file, 'r') as f:
                link_content = f.read()
            
            with open(target_file, 'r') as f:
                target_content = f.read()
            
            assert link_content == target_content, "Symbolic link content mismatch"
            
            self.test_suite.test_results['cross_platform_compatibility']['symbolic_links'] = 'PASS'
            
        except OSError:
            # Symbolic links not supported
            self.test_suite.test_results['cross_platform_compatibility']['symbolic_links'] = 'NOT_SUPPORTED'


def generate_file_operations_integration_report():
    """Generate comprehensive file operations integration test report"""
    test_suite = FileOperationIntegrationTestSuite()
    
    report = {
        'test_execution_summary': {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'total_test_categories': 5,
            'total_test_methods': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0
        },
        'test_results': test_suite.test_results,
        'performance_metrics': test_suite.performance_metrics,
        'platform_specific_notes': [],
        'recommendations': []
    }
    
    # Count test results
    for category, tests in test_suite.test_results.items():
        for test_name, result in tests.items():
            report['test_execution_summary']['total_test_methods'] += 1
            if result == 'PASS':
                report['test_execution_summary']['passed_tests'] += 1
            elif result.startswith('SKIP'):
                report['test_execution_summary']['skipped_tests'] += 1
            else:
                report['test_execution_summary']['failed_tests'] += 1
    
    # Add platform-specific notes
    if platform.system() == 'Windows':
        report['platform_specific_notes'].append("Windows: Limited POSIX permission support")
        report['platform_specific_notes'].append("Windows: Symbolic links require elevated permissions")
    
    # Generate recommendations
    if 'large_file_read_speed_mb_s' in test_suite.performance_metrics:
        speed = test_suite.performance_metrics['large_file_read_speed_mb_s']
        if speed < 50:
            report['recommendations'].append("Consider optimizing large file read operations")
    
    return report


if __name__ == "__main__":
    # Run all file operations integration tests
    pytest.main([__file__, "-v", "--tb=short"])