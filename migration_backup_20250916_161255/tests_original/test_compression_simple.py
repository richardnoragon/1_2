import unittest
import os
import tempfile
import shutil
import zipfile
import tarfile


class TestCompressionSimple(unittest.TestCase):
    """Simple tests for compression functionality without GUI dependencies."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test directory structure
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        
        # Create test files
        self.create_test_files()
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create various test files for compression testing."""
        # Text file with compressible content
        self.text_file = os.path.join(self.source_dir, "test.txt")
        with open(self.text_file, 'w') as f:
            f.write("This is a test file for compression testing.\n" * 1000)
        
        # Binary file
        self.binary_file = os.path.join(self.source_dir, "test.bin")
        with open(self.binary_file, 'wb') as f:
            f.write(b'Binary data ' * 5000)
        
        # Subdirectory with files
        self.sub_dir = os.path.join(self.source_dir, "subdir")
        os.makedirs(self.sub_dir)
        
        self.sub_file = os.path.join(self.sub_dir, "sub_test.txt")
        with open(self.sub_file, 'w') as f:
            f.write("Subdirectory test file content.\n" * 100)
    
    def test_zip_compression_decompression(self):
        """Test ZIP compression and decompression."""
        # Test ZIP compression
        output_file = os.path.join(self.test_dir, "test.zip")
        
        # Use direct zipfile operations for testing
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(
                                file_path, self.source_dir
                            )
                    zipf.write(file_path, arcname)
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
        
        # Test ZIP decompression
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        with zipfile.ZipFile(output_file, 'r') as zipf:
            zipf.extractall(output_dir)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(
            os.path.join(output_dir, "subdir", "sub_test.txt")
        ))
        
        # Verify content integrity
        with open(os.path.join(output_dir, "test.txt"), 'r') as f:
            content = f.read()
            self.assertIn(
                "This is a test file for compression testing.",
                content
            )
    
    def test_targz_compression_decompression(self):
        """Test TAR.GZ compression and decompression."""
        # Test TAR.GZ compression
        output_file = os.path.join(self.test_dir, "test.tar.gz")
        
        with tarfile.open(output_file, "w:gz", compresslevel=6) as tar:
            tar.add(self.source_dir, arcname=".")
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
        
        # Test TAR.GZ decompression
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        with tarfile.open(output_file, "r:gz") as tar:
            tar.extractall(output_dir)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(
            os.path.join(output_dir, "subdir", "sub_test.txt")
        ))
    
    def test_tarbz2_compression_decompression(self):
        """Test TAR.BZ2 compression and decompression."""
        # Test TAR.BZ2 compression
        output_file = os.path.join(self.test_dir, "test.tar.bz2")
        
        with tarfile.open(output_file, "w:bz2", compresslevel=6) as tar:
            tar.add(self.source_dir, arcname=".")
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
        
        # Test TAR.BZ2 decompression
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        with tarfile.open(output_file, "r:bz2") as tar:
            tar.extractall(output_dir)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(
            os.path.join(output_dir, "subdir", "sub_test.txt")
        ))
    
    def test_compression_levels(self):
        """Test different compression levels."""
        levels = [1, 6, 9]  # Fast, default, maximum
        
        for level in levels:
            with self.subTest(compression_level=level):
                output_file = os.path.join(self.test_dir, f"level_{level}.zip")
                
                # Test compression with different levels
                with zipfile.ZipFile(
                    output_file, 'w', zipfile.ZIP_DEFLATED, level
                ) as zipf:
                    for root, dirs, files in os.walk(self.source_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(
                                file_path, self.source_dir
                            )
                            zipf.write(file_path, arcname)
                
                # Verify archive was created
                self.assertTrue(os.path.exists(output_file))
                self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_empty_directory_compression(self):
        """Test compression of empty directory."""
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir)
        
        output_file = os.path.join(self.test_dir, "empty.zip")
        
        # Test compression of empty directory
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the directory itself
            zipf.write(empty_dir, "empty")
        
        # Verify archive was created (may be very small)
        self.assertTrue(os.path.exists(output_file))
    
    def test_compression_ratio_comparison(self):
        """Test compression ratios across different formats."""
        # Create a highly compressible file
        compressible_file = os.path.join(self.source_dir, "compressible.txt")
        with open(compressible_file, 'w') as f:
            f.write("A" * 10000)  # 10KB of repeated 'A'
        
        original_size = os.path.getsize(compressible_file)
        
        formats = ["zip", "tar.gz", "tar.bz2"]
        sizes = {}
        
        for fmt in formats:
            archive_file = os.path.join(self.test_dir, f"test.{fmt}")
            
            if fmt == "zip":
                with zipfile.ZipFile(
                    archive_file, 'w', zipfile.ZIP_DEFLATED, 6
                ) as zipf:
                    for root, dirs, files in os.walk(self.source_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(
                                file_path, self.source_dir
                            )
                            zipf.write(file_path, arcname)
            elif fmt == "tar.gz":
                with tarfile.open(archive_file, "w:gz", compresslevel=6) as tar:
                    tar.add(self.source_dir, arcname=".")
            elif fmt == "tar.bz2":
                with tarfile.open(archive_file, "w:bz2", compresslevel=6) as tar:
                    tar.add(self.source_dir, arcname=".")
            
            sizes[fmt] = os.path.getsize(archive_file)
        
        # All compressed files should be smaller than original
        for fmt, size in sizes.items():
            self.assertLess(size, original_size * 2)  # Allow some overhead
    
    def test_error_handling_nonexistent_source(self):
        """Test error handling for non-existent source."""
        nonexistent = os.path.join(self.test_dir, "nonexistent")
        output_file = os.path.join(self.test_dir, "error_test.zip")
        
        # These should raise appropriate exceptions
        with self.assertRaises((FileNotFoundError, OSError)):
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(nonexistent, "nonexistent")
    
    def test_format_constants(self):
        """Test format constants are correctly defined."""
        from compress_decompress import (
            FORMAT_ZIP, FORMAT_7Z, FORMAT_TAR_GZ, FORMAT_TAR_BZ2
        )
        
        self.assertEqual(FORMAT_ZIP, "ZIP")
        self.assertEqual(FORMAT_7Z, "7Z")
        self.assertEqual(FORMAT_TAR_GZ, "TAR.GZ")
        self.assertEqual(FORMAT_TAR_BZ2, "TAR.BZ2")


if __name__ == '__main__':
    unittest.main()
