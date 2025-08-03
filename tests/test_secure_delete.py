import unittest
import os
import time
from tests.test_utils import TestUtils
from file_utilities_2.core.secure_delete_logic import SecureDeleteLogic

from core.error_handler import error_handler


class TestSecureDelete(unittest.TestCase):
    """A class that handles test secure delete."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.secure_delete = SecureDeleteLogic()
        
        # Create test files with known content
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"secure_test_{i}.txt")
            with open(file_path, 'wb') as f:
                f.write(b'S' * 1024)  # 1KB of data
            self.test_files.append(file_path)

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_single_pass_wipe(self):
        """Test single-pass secure deletion"""
        test_file = self.test_files[0]
        
        # Perform secure deletion
        self.secure_delete.delete_file(test_file, passes=1)
        
        # Verify file is gone
        self.assertFalse(os.path.exists(test_file))
        
        # If possible, verify file data is not recoverable
        if hasattr(self.secure_delete, 'check_file_remains'):
            self.assertFalse(self.secure_delete.check_file_remains(test_file))

    def test_multi_pass_wipe(self):
        """Test multi-pass secure deletion"""
        test_file = self.test_files[0]
        passes = 3
        
        # Perform secure deletion
        self.secure_delete.delete_file(test_file, passes=passes)
        
        # Verify file is gone
        self.assertFalse(os.path.exists(test_file))

    def test_batch_deletion(self):
        """Test deleting multiple files securely"""
        # Delete all test files
        self.secure_delete.delete_files(self.test_files)
        
        # Verify all files are gone
        for file_path in self.test_files:
            self.assertFalse(os.path.exists(file_path))

    def test_directory_deletion(self):
        """Test secure directory deletion"""
        # Create a test directory with files
        test_subdir = os.path.join(self.test_dir, "secure_test_dir")
        os.makedirs(test_subdir)
        
        for i in range(2):
            file_path = os.path.join(test_subdir, f"file_{i}.txt")
            with open(file_path, 'w') as f:
                f.write("test content")
        
        # Perform secure deletion
        self.secure_delete.delete_directory(test_subdir)
        
        # Verify directory is gone
        self.assertFalse(os.path.exists(test_subdir))

    def test_progress_callback(self):
        """Test progress reporting during secure deletion"""
        progress_values = []
        
        def progress_callback(percent):
            """progresscallback.
        Args:
            percent (Any): Description of percent"""
            progress_values.append(percent)
        
        # Create a larger test file
        large_file = os.path.join(self.test_dir, "large_file.dat")
        with open(large_file, 'wb') as f:
            f.write(b'L' * (1024 * 1024))  # 1MB file
        
        # Delete with progress tracking
        self.secure_delete.delete_file(
            large_file,
            passes=3,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_cancel_deletion(self):
        """Test cancellation of secure deletion"""
        cancel_flag = {'cancel': False}
        progress_values = []
        
        def progress_callback(percent):
            """progresscallback.
        Args:
            percent (Any): Description of percent"""
            progress_values.append(percent)
            if percent > 50:
                cancel_flag['cancel'] = True
        
        # Create a large test file
        large_file = os.path.join(self.test_dir, "large_file.dat")
        with open(large_file, 'wb') as f:
            f.write(b'L' * (1024 * 1024 * 10))  # 10MB file
        
        # Attempt deletion with cancellation
        self.secure_delete.delete_file(
            large_file,
            passes=3,
            progress_callback=progress_callback,
            cancel_check=lambda: cancel_flag['cancel']
        )
        
        # Verify operation was cancelled
        self.assertTrue(50 < progress_values[-1] < 100)

    @unittest.skipIf(os.name != 'posix', "File permission tests require POSIX")
    def test_handle_readonly_files(self):
        """Test handling of read-only files"""
        test_file = self.test_files[0]
        
        # Make file read-only
        os.chmod(test_file, 0o444)
        
        # Attempt secure deletion
        self.secure_delete.delete_file(test_file)
        
        # Verify file is gone despite being read-only
        self.assertFalse(os.path.exists(test_file))

if __name__ == '__main__':
    unittest.main()