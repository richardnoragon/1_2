import os
import shutil
import sys
import tempfile
import unittest

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utilities.file_operations.secure_delete.secure_delete_logic import \
    SecureDeleteLogic


class TestSecureDelete(unittest.TestCase):
    """A class that handles test secure delete."""
    
    def setUp(self):
        """Setup test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="secure_delete_test_")
        self.secure_delete = SecureDeleteLogic()
        
        # Create test files with known content
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"secure_test_{i}.txt")
            with open(file_path, 'wb') as f:
                f.write(b'S' * 1024)  # 1KB of data
            self.test_files.append(file_path)

    def tearDown(self):
        """Cleanup test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_single_pass_wipe(self):
        """Test single-pass secure deletion"""
        test_file = self.test_files[0]
        
        # Perform secure deletion
        result = self.secure_delete.delete_file(test_file, passes=1)
        
        # Verify file is gone and operation succeeded
        self.assertTrue(result, "Secure deletion should succeed")
        self.assertFalse(os.path.exists(test_file))

    def test_multi_pass_wipe(self):
        """Test multi-pass secure deletion"""
        test_file = self.test_files[0]
        passes = 3
        
        # Perform secure deletion
        result = self.secure_delete.delete_file(test_file, passes=passes)
        
        # Verify file is gone and operation succeeded
        self.assertTrue(result, "Multi-pass secure deletion should succeed")
        self.assertFalse(os.path.exists(test_file))

    def test_batch_deletion(self):
        """Test deleting multiple files securely"""
        # Delete all test files
        result = self.secure_delete.delete_files(self.test_files)
        
        # Verify all files are gone and operation succeeded
        self.assertTrue(result, "Batch deletion should succeed")
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
        result = self.secure_delete.delete_directory(test_subdir)
        
        # Verify directory is gone and operation succeeded
        self.assertTrue(result, "Directory deletion should succeed")
        self.assertFalse(os.path.exists(test_subdir))

    def test_progress_callback(self):
        """Test progress reporting during secure deletion"""
        progress_values = []
        
        def progress_callback(percent):
            """Progress callback for testing."""
            progress_values.append(percent)
        
        # Create a larger test file
        large_file = os.path.join(self.test_dir, "large_file.dat")
        with open(large_file, 'wb') as f:
            f.write(b'L' * (1024 * 1024))  # 1MB file
        
        # Delete with progress tracking
        result = self.secure_delete.delete_file(
            large_file,
            passes=3,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported and operation succeeded
        self.assertTrue(result, "Secure deletion with progress should succeed")
        self.assertTrue(len(progress_values) > 0, "Progress should be reported")
        self.assertEqual(progress_values[-1], 100, 
                        "Final progress should be 100%")

    def test_cancel_deletion(self):
        """Test cancellation of secure deletion"""
        cancel_flag = {'cancel': False}
        progress_values = []
        
        def progress_callback(percent):
            """Progress callback that triggers cancellation."""
            progress_values.append(percent)
            if percent > 50:
                cancel_flag['cancel'] = True
        
        # Create a large test file
        large_file = os.path.join(self.test_dir, "large_file.dat")
        with open(large_file, 'wb') as f:
            f.write(b'L' * (1024 * 1024 * 2))  # 2MB file
        
        # Attempt deletion with cancellation
        result = self.secure_delete.delete_file(
            large_file,
            passes=3,
            progress_callback=progress_callback,
            cancel_check=lambda: cancel_flag['cancel']
        )
        
        # Verify operation was cancelled
        self.assertFalse(result, "Cancelled operation should return False")
        if progress_values:
            self.assertLess(progress_values[-1], 100, 
                          "Progress should be less than 100% when cancelled")

    @unittest.skipIf(os.name != 'posix', "File permission tests require POSIX")
    def test_handle_readonly_files(self):
        """Test handling of read-only files"""
        test_file = self.test_files[0]
        
        # Make file read-only
        os.chmod(test_file, 0o444)
        
        # Attempt secure deletion
        result = self.secure_delete.delete_file(test_file)
        
        # Verify file is gone and operation succeeded
        self.assertTrue(result, "Read-only file deletion should succeed")
        self.assertFalse(os.path.exists(test_file))

    def test_statistics_tracking(self):
        """Test statistics tracking functionality"""
        # Reset statistics
        self.secure_delete.reset_statistics()
        initial_stats = self.secure_delete.get_statistics()
        
        # Verify initial statistics
        self.assertEqual(initial_stats['files_processed'], 0)
        self.assertEqual(initial_stats['total_bytes_processed'], 0)
        
        # Delete a test file
        test_file = self.test_files[0]
        result = self.secure_delete.delete_file(test_file)
        
        # Verify statistics were updated
        self.assertTrue(result, "File deletion should succeed")
        updated_stats = self.secure_delete.get_statistics()
        self.assertEqual(updated_stats['files_processed'], 1)
        self.assertGreater(updated_stats['total_bytes_processed'], 0)


if __name__ == '__main__':
    unittest.main()