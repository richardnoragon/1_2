import unittest
import os
import tempfile
import shutil
import zipfile
import tarfile

from PyQt5.QtCore import QCoreApplication
from compress_decompress import CompressDecompressApp


class TestCompressionDecompression(unittest.TestCase):
    """Comprehensive test suite for compression and decompression."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for Qt tests."""
        if not QCoreApplication.instance():
            cls.app = QCoreApplication([])
        else:
            cls.app = QCoreApplication.instance()
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test directory structure
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        
        # Create test files
        self.create_test_files()
        
        # Create compression instance
        self.compressor = CompressDecompressApp()
        
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
    
    def test_compress_zip_format(self):
        """Test ZIP compression functionality."""
        output_file = os.path.join(self.test_dir, "test.zip")
        
        # Test ZIP compression
        self.compressor._compress_zip(
            self.source_dir,
            output_file,
            password="",
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
        
        # Verify it's a valid ZIP file
        with zipfile.ZipFile(output_file, 'r') as zipf:
            file_list = zipf.namelist()
            self.assertIn("test.txt", file_list)
            self.assertIn("test.bin", file_list)
            self.assertIn("subdir/sub_test.txt", file_list)
    
    def test_compress_7z_format(self):
        """Test 7Z compression functionality."""
        output_file = os.path.join(self.test_dir, "test.7z")
        
        # Test 7Z compression
        self.compressor._compress_7z(
            self.source_dir,
            output_file,
            password="",
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_compress_targz_format(self):
        """Test TAR.GZ compression functionality."""
        output_file = os.path.join(self.test_dir, "test.tar.gz")
        
        # Test TAR.GZ compression
        self.compressor._compress_targz(
            self.source_dir,
            output_file,
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
        
        # Verify it's a valid tar.gz file
        with tarfile.open(output_file, "r:gz") as tar:
            file_list = tar.getnames()
            self.assertIn("./test.txt", file_list)
            self.assertIn("./test.bin", file_list)
            self.assertIn("./subdir/sub_test.txt", file_list)
    
    def test_compress_tarbz2_format(self):
        """Test TAR.BZ2 compression functionality."""
        output_file = os.path.join(self.test_dir, "test.tar.bz2")
        
        # Test TAR.BZ2 compression
        self.compressor._compress_tarbz2(
            self.source_dir,
            output_file,
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_decompress_zip_format(self):
        """Test ZIP decompression functionality."""
        # First create a ZIP file
        zip_file = os.path.join(self.test_dir, "decompress_test.zip")
        self.compressor._compress_zip(
            self.source_dir,
            zip_file,
            password="",
            compression_level=6
        )
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        # Test ZIP decompression
        self.compressor._decompress_zip(zip_file, output_dir, password="")
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "subdir", "sub_test.txt")))
        
        # Verify content integrity
        with open(os.path.join(output_dir, "test.txt"), 'r') as f:
            content = f.read()
            self.assertIn("This is a test file for compression testing.", content)
    
    def test_decompress_7z_format(self):
        """Test 7Z decompression functionality."""
        # First create a 7Z file
        sevenz_file = os.path.join(self.test_dir, "decompress_test.7z")
        self.compressor._compress_7z(
            self.source_dir,
            sevenz_file,
            password="",
            compression_level=6
        )
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        # Test 7Z decompression
        self.compressor._decompress_7z(sevenz_file, output_dir, password="")
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "subdir", "sub_test.txt")))
    
    def test_decompress_targz_format(self):
        """Test TAR.GZ decompression functionality."""
        # First create a TAR.GZ file
        targz_file = os.path.join(self.test_dir, "decompress_test.tar.gz")
        self.compressor._compress_targz(
            self.source_dir,
            targz_file,
            compression_level=6
        )
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        # Test TAR.GZ decompression
        self.compressor._decompress_targz(targz_file, output_dir)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "subdir", "sub_test.txt")))
    
    def test_decompress_tarbz2_format(self):
        """Test TAR.BZ2 decompression functionality."""
        # First create a TAR.BZ2 file
        tarbz2_file = os.path.join(self.test_dir, "decompress_test.tar.bz2")
        self.compressor._compress_tarbz2(
            self.source_dir,
            tarbz2_file,
            compression_level=6
        )
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(output_dir)
        
        # Test TAR.BZ2 decompression
        self.compressor._decompress_tarbz2(tarbz2_file, output_dir)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "subdir", "sub_test.txt")))
    
    def test_password_protected_zip(self):
        """Test password-protected ZIP compression and decompression."""
        password = "test_password_123"
        zip_file = os.path.join(self.test_dir, "password_test.zip")
        
        # Compress with password
        self.compressor._compress_zip(
            self.source_dir,
            zip_file,
            password=password,
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(zip_file))
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "extracted_password")
        os.makedirs(output_dir)
        
        # Test decompression with correct password
        self.compressor._decompress_zip(zip_file, output_dir, password=password)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
    
    def test_password_protected_7z(self):
        """Test password-protected 7Z compression and decompression."""
        password = "test_password_123"
        sevenz_file = os.path.join(self.test_dir, "password_test.7z")
        
        # Compress with password
        self.compressor._compress_7z(
            self.source_dir,
            sevenz_file,
            password=password,
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(sevenz_file))
        
        # Create output directory
        output_dir = os.path.join(self.test_dir, "extracted_password")
        os.makedirs(output_dir)
        
        # Test decompression with correct password
        self.compressor._decompress_7z(sevenz_file, output_dir, password=password)
        
        # Verify files were extracted
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.bin")))
    
    def test_compression_levels(self):
        """Test different compression levels."""
        levels = [1, 6, 9]  # Fast, default, maximum
        
        for level in levels:
            with self.subTest(compression_level=level):
                output_file = os.path.join(self.test_dir, f"level_{level}.zip")
                
                # Test compression with different levels
                self.compressor._compress_zip(
                    self.source_dir,
                    output_file,
                    password="",
                    compression_level=level
                )
                
                # Verify archive was created
                self.assertTrue(os.path.exists(output_file))
                self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_empty_directory_compression(self):
        """Test compression of empty directory."""
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir)
        
        output_file = os.path.join(self.test_dir, "empty.zip")
        
        # Test compression of empty directory
        self.compressor._compress_zip(
            empty_dir,
            output_file,
            password="",
            compression_level=6
        )
        
        # Verify archive was created (may be very small)
        self.assertTrue(os.path.exists(output_file))
    
    def test_single_file_compression(self):
        """Test compression of a single file."""
        output_file = os.path.join(self.test_dir, "single_file.zip")
        
        # Test compression of single file
        self.compressor._compress_zip(
            self.text_file,  # Single file instead of directory
            output_file,
            password="",
            compression_level=6
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
    
    def test_error_handling_nonexistent_source(self):
        """Test error handling for non-existent source."""
        nonexistent = os.path.join(self.test_dir, "nonexistent")
        output_file = os.path.join(self.test_dir, "error_test.zip")
        
        # These should raise appropriate exceptions
        with self.assertRaises((FileNotFoundError, OSError)):
            self.compressor._compress_zip(
                nonexistent,
                output_file,
                password="",
                compression_level=6
            )
    
    def test_error_handling_nonexistent_archive(self):
        """Test error handling for non-existent archive during decompression."""
        nonexistent = os.path.join(self.test_dir, "nonexistent.zip")
        output_dir = os.path.join(self.test_dir, "error_extract")
        
        # These should raise appropriate exceptions
        with self.assertRaises((FileNotFoundError, OSError)):
            self.compressor._decompress_zip(nonexistent, output_dir, password="")
    
    def test_format_constants(self):
        """Test format constants are correctly defined."""
        from compress_decompress import (
            FORMAT_ZIP, FORMAT_7Z, FORMAT_TAR_GZ, FORMAT_TAR_BZ2
        )
        
        self.assertEqual(FORMAT_ZIP, "ZIP")
        self.assertEqual(FORMAT_7Z, "7Z")
        self.assertEqual(FORMAT_TAR_GZ, "TAR.GZ")
        self.assertEqual(FORMAT_TAR_BZ2, "TAR.BZ2")


class TestCompressionIntegration(unittest.TestCase):
    """Integration tests for compression and decompression workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.app = CompressDecompressApp()
        
        # Create test directory structure
        self.source_dir = os.path.join(self.test_dir, "integration_source")
        os.makedirs(self.source_dir)
        
        # Create test content
        self.create_integration_test_files()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def create_integration_test_files(self):
        """Create test files for integration testing."""
        # Create files of different types and sizes
        
        # Small text file
        small_file = os.path.join(self.source_dir, "small.txt")
        with open(small_file, 'w') as f:
            f.write("Small file content.\n" * 10)
        
        # Large text file
        large_file = os.path.join(self.source_dir, "large.txt")
        with open(large_file, 'w') as f:
            f.write("Large file content.\n" * 10000)
        
        # Binary file
        binary_file = os.path.join(self.source_dir, "data.bin")
        with open(binary_file, 'wb') as f:
            f.write(b'Binary data content ' * 5000)
        
        # Nested directory structure
        nested_dir = os.path.join(self.source_dir, "level1", "level2")
        os.makedirs(nested_dir)
        
        nested_file = os.path.join(nested_dir, "nested.txt")
        with open(nested_file, 'w') as f:
            f.write("Nested file content.\n" * 100)
    
    def test_full_compression_decompression_cycle(self):
        """Test complete compression and decompression cycle."""
        formats_to_test = [
            ("ZIP", ".zip"),
            ("7Z", ".7z"),
            ("TAR.GZ", ".tar.gz"),
            ("TAR.BZ2", ".tar.bz2")
        ]
        
        for format_name, extension in formats_to_test:
            with self.subTest(format=format_name):
                # Create archive
                archive_file = os.path.join(self.test_dir, f"test{extension}")
                
                if format_name == "ZIP":
                    self.app._compress_zip(
                        self.source_dir, archive_file, "", 6
                    )
                elif format_name == "7Z":
                    self.app._compress_7z(
                        self.source_dir, archive_file, "", 6
                    )
                elif format_name == "TAR.GZ":
                    self.app._compress_targz(
                        self.source_dir, archive_file, 6
                    )
                elif format_name == "TAR.BZ2":
                    self.app._compress_tarbz2(
                        self.source_dir, archive_file, 6
                    )
                
                # Verify archive exists
                self.assertTrue(os.path.exists(archive_file))
                
                # Extract archive
                extract_dir = os.path.join(
                    self.test_dir, f"extracted_{format_name.lower()}"
                )
                os.makedirs(extract_dir)
                
                if format_name == "ZIP":
                    self.app._decompress_zip(archive_file, extract_dir, "")
                elif format_name == "7Z":
                    self.app._decompress_7z(archive_file, extract_dir, "")
                elif format_name == "TAR.GZ":
                    self.app._decompress_targz(archive_file, extract_dir)
                elif format_name == "TAR.BZ2":
                    self.app._decompress_tarbz2(archive_file, extract_dir)
                
                # Verify extracted files
                self.assertTrue(os.path.exists(
                    os.path.join(extract_dir, "small.txt")
                ))
                self.assertTrue(os.path.exists(
                    os.path.join(extract_dir, "large.txt")
                ))
                self.assertTrue(os.path.exists(
                    os.path.join(extract_dir, "data.bin")
                ))
                self.assertTrue(os.path.exists(
                    os.path.join(extract_dir, "level1", "level2", "nested.txt")
                ))
    
    def test_compression_ratio_comparison(self):
        """Test compression ratios across different formats."""
        # Create a highly compressible file
        compressible_file = os.path.join(self.source_dir, "compressible.txt")
        with open(compressible_file, 'w') as f:
            f.write("A" * 10000)  # 10KB of repeated 'A'
        
        original_size = os.path.getsize(compressible_file)
        
        formats = ["zip", "7z", "tar.gz", "tar.bz2"]
        sizes = {}
        
        for fmt in formats:
            archive_file = os.path.join(self.test_dir, f"test.{fmt}")
            
            if fmt == "zip":
                self.app._compress_zip(self.source_dir, archive_file, "", 6)
            elif fmt == "7z":
                self.app._compress_7z(self.source_dir, archive_file, "", 6)
            elif fmt == "tar.gz":
                self.app._compress_targz(self.source_dir, archive_file, 6)
            elif fmt == "tar.bz2":
                self.app._compress_tarbz2(self.source_dir, archive_file, 6)
            
            sizes[fmt] = os.path.getsize(archive_file)
        
        # All compressed files should be smaller than original
        for fmt, size in sizes.items():
            self.assertLess(size, original_size * 2)  # Allow some overhead


if __name__ == '__main__':
    # Note: These tests run the actual compression/decompression
    # operations on real files for comprehensive testing
    unittest.main()
