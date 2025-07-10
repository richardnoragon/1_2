import unittest
import os
import hashlib
from tests.test_utils import TestUtils
from file_splitter_joiner import FileSplitter  # Update based on actual class name

from core.error_handler import error_handler


class TestFileSplitter(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.splitter = FileSplitter()
        
        # Create a test file with known content
        self.test_file = os.path.join(self.test_dir, "large_file.dat")
        self.file_size = 1024 * 1024 * 5  # 5MB
        with open(self.test_file, 'wb') as f:
            f.write(os.urandom(self.file_size))
        
        # Calculate original file hash
        with open(self.test_file, 'rb') as f:
            self.original_hash = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_split_by_size(self):
        """Test splitting file into fixed-size chunks"""
        chunk_size = 1024 * 1024  # 1MB chunks
        output_dir = os.path.join(self.test_dir, "splits")
        os.makedirs(output_dir)
        
        # Split the file
        chunk_files = self.splitter.split_file(
            self.test_file,
            output_dir,
            chunk_size=chunk_size
        )
        
        # Verify chunks
        self.assertEqual(len(chunk_files), 5)  # Should create 5 chunks
        for chunk_file in chunk_files:
            self.assertTrue(os.path.exists(chunk_file))
            self.assertLessEqual(os.path.getsize(chunk_file), chunk_size)

    def test_split_by_parts(self):
        """Test splitting file into specified number of parts"""
        num_parts = 3
        output_dir = os.path.join(self.test_dir, "splits")
        os.makedirs(output_dir)
        
        # Split the file
        chunk_files = self.splitter.split_file(
            self.test_file,
            output_dir,
            num_parts=num_parts
        )
        
        # Verify chunks
        self.assertEqual(len(chunk_files), num_parts)
        expected_size = self.file_size // num_parts
        for chunk_file in chunk_files[:-1]:  # All but last chunk
            self.assertEqual(os.path.getsize(chunk_file), expected_size)

    def test_join_files(self):
        """Test joining split files back together"""
        # First split the file
        chunk_size = 1024 * 1024  # 1MB chunks
        split_dir = os.path.join(self.test_dir, "splits")
        os.makedirs(split_dir)
        
        chunk_files = self.splitter.split_file(
            self.test_file,
            split_dir,
            chunk_size=chunk_size
        )
        
        # Join the chunks
        output_file = os.path.join(self.test_dir, "rejoined_file.dat")
        self.splitter.join_files(chunk_files, output_file)
        
        # Verify joined file
        self.assertTrue(os.path.exists(output_file))
        self.assertEqual(os.path.getsize(output_file), self.file_size)
        
        # Verify content integrity
        with open(output_file, 'rb') as f:
            joined_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(joined_hash, self.original_hash)

    def test_progress_tracking(self):
        """Test progress reporting during split/join operations"""
        progress_values = []
        
        def progress_callback(percent):
            progress_values.append(percent)
        
        # Split with progress tracking
        chunk_size = 1024 * 1024
        split_dir = os.path.join(self.test_dir, "splits")
        os.makedirs(split_dir)
        
        self.splitter.split_file(
            self.test_file,
            split_dir,
            chunk_size=chunk_size,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test non-existent input file
        with self.assertRaises(FileNotFoundError):
            self.splitter.split_file(
                "nonexistent.file",
                self.test_dir,
                chunk_size=1024
            )
        
        # Test invalid chunk size
        with self.assertRaises(ValueError):
            self.splitter.split_file(
                self.test_file,
                self.test_dir,
                chunk_size=0
            )
        
        # Test invalid number of parts
        with self.assertRaises(ValueError):
            self.splitter.split_file(
                self.test_file,
                self.test_dir,
                num_parts=0
            )

    def test_metadata_preservation(self):
        """Test preservation of file metadata during split/join"""
        # Create test file with specific metadata
        test_file = os.path.join(self.test_dir, "metadata_test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Set some file attributes
        os.chmod(test_file, 0o644)
        
        # Split and rejoin
        split_dir = os.path.join(self.test_dir, "splits")
        os.makedirs(split_dir)
        chunks = self.splitter.split_file(test_file, split_dir, chunk_size=2)
        
        output_file = os.path.join(self.test_dir, "rejoined.txt")
        self.splitter.join_files(chunks, output_file)
        
        # Verify metadata was preserved
        self.assertEqual(
            os.stat(test_file).st_mode & 0o777,
            os.stat(output_file).st_mode & 0o777
        )

if __name__ == '__main__':
    unittest.main()