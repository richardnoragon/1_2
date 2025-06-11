import unittest
import os
import shutil
from tests.test_utils import TestUtils
from compress_decompress import Compressor  # Update based on actual class name

class TestCompression(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.compressor = Compressor()
        
        # Create test directory structure
        self.source_dir = os.path.join(self.test_dir, "source")
        os.makedirs(self.source_dir)
        
        # Create various test files
        self.text_file = os.path.join(self.source_dir, "text.txt")
        with open(self.text_file, 'w') as f:
            f.write("Test content\n" * 1000)  # Create some compressible content
            
        self.binary_file = os.path.join(self.source_dir, "binary.dat")
        with open(self.binary_file, 'wb') as f:
            f.write(os.urandom(1024 * 100))  # 100KB of random data
            
        # Create subdirectory with files
        self.sub_dir = os.path.join(self.source_dir, "subdir")
        os.makedirs(self.sub_dir)
        self.sub_file = os.path.join(self.sub_dir, "subfile.txt")
        with open(self.sub_file, 'w') as f:
            f.write("Subdirectory content")

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_compress_single_file_zip(self):
        """Test compressing a single file to ZIP format"""
        output_file = os.path.join(self.test_dir, "compressed.zip")
        
        # Compress file
        self.compressor.compress_file(self.text_file, output_file, format='zip')
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        self.assertTrue(os.path.getsize(output_file) < os.path.getsize(self.text_file))
        
        # Extract and verify
        extract_dir = os.path.join(self.test_dir, "extracted")
        self.compressor.decompress_file(output_file, extract_dir)
        
        extracted_file = os.path.join(extract_dir, os.path.basename(self.text_file))
        self.assertTrue(os.path.exists(extracted_file))
        with open(self.text_file, 'rb') as f1, open(extracted_file, 'rb') as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_compress_directory_7z(self):
        """Test compressing an entire directory to 7Z format"""
        output_file = os.path.join(self.test_dir, "compressed.7z")
        
        # Compress directory
        self.compressor.compress_directory(
            self.source_dir,
            output_file,
            format='7z'
        )
        
        # Verify archive was created
        self.assertTrue(os.path.exists(output_file))
        
        # Extract and verify
        extract_dir = os.path.join(self.test_dir, "extracted")
        self.compressor.decompress_file(output_file, extract_dir)
        
        # Verify directory structure was preserved
        extracted_text = os.path.join(
            extract_dir,
            os.path.basename(self.source_dir),
            os.path.basename(self.text_file)
        )
        extracted_subfile = os.path.join(
            extract_dir,
            os.path.basename(self.source_dir),
            "subdir",
            os.path.basename(self.sub_file)
        )
        
        self.assertTrue(os.path.exists(extracted_text))
        self.assertTrue(os.path.exists(extracted_subfile))

    def test_compress_with_password(self):
        """Test password-protected compression"""
        output_file = os.path.join(self.test_dir, "protected.zip")
        password = "test_password123"
        
        # Compress with password
        self.compressor.compress_file(
            self.text_file,
            output_file,
            format='zip',
            password=password
        )
        
        # Try to extract without password (should fail)
        extract_dir = os.path.join(self.test_dir, "extracted_no_pass")
        with self.assertRaises(Exception):  # Update with specific exception
            self.compressor.decompress_file(output_file, extract_dir)
        
        # Extract with correct password
        extract_dir = os.path.join(self.test_dir, "extracted_with_pass")
        self.compressor.decompress_file(
            output_file,
            extract_dir,
            password=password
        )
        
        # Verify extraction
        extracted_file = os.path.join(
            extract_dir,
            os.path.basename(self.text_file)
        )
        self.assertTrue(os.path.exists(extracted_file))

    def test_compression_formats(self):
        """Test different compression formats"""
        formats = ['zip', '7z', 'tar.gz', 'tar.bz2']
        for fmt in formats:
            output_file = os.path.join(self.test_dir, f"compressed.{fmt}")
            
            # Compress
            self.compressor.compress_file(
                self.text_file,
                output_file,
                format=fmt
            )
            
            # Verify
            self.assertTrue(
                os.path.exists(output_file),
                f"Failed to create {fmt} archive"
            )
            
            # Extract
            extract_dir = os.path.join(self.test_dir, f"extracted_{fmt}")
            self.compressor.decompress_file(output_file, extract_dir)
            
            # Verify content
            extracted_file = os.path.join(
                extract_dir,
                os.path.basename(self.text_file)
            )
            self.assertTrue(
                os.path.exists(extracted_file),
                f"Failed to extract {fmt} archive"
            )

    def test_progress_tracking(self):
        """Test progress reporting during compression/decompression"""
        progress_values = []
        
        def progress_callback(percent):
            progress_values.append(percent)
        
        # Compress with progress tracking
        output_file = os.path.join(self.test_dir, "progress_test.zip")
        self.compressor.compress_directory(
            self.source_dir,
            output_file,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test non-existent input file
        with self.assertRaises(FileNotFoundError):
            self.compressor.compress_file(
                "nonexistent.file",
                "output.zip"
            )
        
        # Test invalid format
        with self.assertRaises(ValueError):
            self.compressor.compress_file(
                self.text_file,
                "output.invalid",
                format="invalid"
            )
        
        # Test invalid password
        with self.assertRaises(Exception):  # Update with specific exception
            self.compressor.decompress_file(
                os.path.join(self.test_dir, "protected.zip"),
                self.test_dir,
                password="wrong_password"
            )

if __name__ == '__main__':
    unittest.main()