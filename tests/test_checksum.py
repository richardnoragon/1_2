import unittest
import os
import hashlib
from tests.test_utils import TestUtils
from check_sum import Checksummer  # Update based on actual class name

class TestChecksummer(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.checksummer = Checksummer()
        
        # Create test files with known content
        self.test_files = {}
        contents = {
            'empty': b'',
            'small': b'Hello, World!',
            'medium': b'A' * 1024,  # 1KB
            'large': b'B' * (1024 * 1024)  # 1MB
        }
        
        for name, content in contents.items():
            path = os.path.join(self.test_dir, f"{name}.txt")
            with open(path, 'wb') as f:
                f.write(content)
            self.test_files[name] = {
                'path': path,
                'content': content,
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'sha256': hashlib.sha256(content).hexdigest()
            }

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_calculate_md5(self):
        """Test MD5 checksum calculation"""
        for name, info in self.test_files.items():
            checksum = self.checksummer.calculate_md5(info['path'])
            self.assertEqual(
                checksum,
                info['md5'],
                f"MD5 mismatch for {name} file"
            )

    def test_calculate_sha1(self):
        """Test SHA1 checksum calculation"""
        for name, info in self.test_files.items():
            checksum = self.checksummer.calculate_sha1(info['path'])
            self.assertEqual(
                checksum,
                info['sha1'],
                f"SHA1 mismatch for {name} file"
            )

    def test_calculate_sha256(self):
        """Test SHA256 checksum calculation"""
        for name, info in self.test_files.items():
            checksum = self.checksummer.calculate_sha256(info['path'])
            self.assertEqual(
                checksum,
                info['sha256'],
                f"SHA256 mismatch for {name} file"
            )

    def test_batch_checksum(self):
        """Test calculating checksums for multiple files"""
        files = [info['path'] for info in self.test_files.values()]
        results = self.checksummer.calculate_batch(files, algorithm='sha256')
        
        for file_path, checksum in results.items():
            # Find the corresponding test file info
            file_name = os.path.basename(file_path).split('.')[0]
            expected = self.test_files[file_name]['sha256']
            self.assertEqual(checksum, expected)

    def test_verify_checksum(self):
        """Test checksum verification"""
        for info in self.test_files.values():
            # Test successful verification
            self.assertTrue(
                self.checksummer.verify_file(
                    info['path'],
                    info['sha256'],
                    algorithm='sha256'
                )
            )
            
            # Test failed verification
            self.assertFalse(
                self.checksummer.verify_file(
                    info['path'],
                    'invalid_checksum',
                    algorithm='sha256'
                )
            )

    def test_progress_tracking(self):
        """Test progress reporting during checksum calculation"""
        progress_values = []
        
        def progress_callback(percent):
            progress_values.append(percent)
        
        # Calculate checksum with progress tracking
        self.checksummer.calculate_sha256(
            self.test_files['large']['path'],
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_verify_from_file(self):
        """Test verifying checksums from a checksum file"""
        # Create a checksum file
        checksum_file = os.path.join(self.test_dir, "checksums.txt")
        with open(checksum_file, 'w') as f:
            for name, info in self.test_files.items():
                f.write(f"{info['sha256']} *{os.path.basename(info['path'])}\n")
        
        # Verify checksums
        results = self.checksummer.verify_from_file(
            checksum_file,
            self.test_dir
        )
        
        # Check results
        self.assertEqual(len(results), len(self.test_files))
        for file_path, verified in results.items():
            self.assertTrue(verified)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            self.checksummer.calculate_md5("nonexistent.file")
        
        # Test invalid algorithm
        with self.assertRaises(ValueError):
            self.checksummer.calculate_batch(
                [self.test_files['small']['path']],
                algorithm='invalid'
            )
        
        # Test invalid checksum format
        with self.assertRaises(ValueError):
            self.checksummer.verify_file(
                self.test_files['small']['path'],
                'invalid_format_checksum'
            )

if __name__ == '__main__':
    unittest.main()