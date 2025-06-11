import unittest
import os
from tests.test_utils import TestUtils
from en_and_decrypt import Encryptor  # Update based on actual class name

class TestEncryption(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.encryptor = Encryptor()
        
        # Create test file with sensitive content
        self.test_file = os.path.join(self.test_dir, "sensitive.txt")
        self.test_content = "This is sensitive data"
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
            
        self.password = "test_password123"

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_encrypt_decrypt_file(self):
        """Test basic encryption and decryption of a file"""
        # Encrypt the file
        encrypted_file = self.test_file + '.encrypted'
        self.encryptor.encrypt_file(self.test_file, encrypted_file, self.password)
        
        # Verify encrypted file exists and is different from original
        self.assertTrue(os.path.exists(encrypted_file))
        with open(encrypted_file, 'rb') as f:
            encrypted_content = f.read()
            self.assertNotEqual(encrypted_content, self.test_content.encode())
        
        # Decrypt the file
        decrypted_file = os.path.join(self.test_dir, "decrypted.txt")
        self.encryptor.decrypt_file(encrypted_file, decrypted_file, self.password)
        
        # Verify decrypted content matches original
        with open(decrypted_file, 'r') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, self.test_content)

    def test_wrong_password(self):
        """Test decryption with wrong password fails"""
        encrypted_file = self.test_file + '.encrypted'
        self.encryptor.encrypt_file(self.test_file, encrypted_file, self.password)
        
        wrong_password = "wrong_password"
        decrypted_file = os.path.join(self.test_dir, "decrypted.txt")
        
        with self.assertRaises(Exception):  # Update with specific exception
            self.encryptor.decrypt_file(encrypted_file, decrypted_file, wrong_password)

    def test_batch_encryption(self):
        """Test encrypting multiple files"""
        # Create multiple test files
        test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"test_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content {i}")
            test_files.append(file_path)
        
        # Encrypt all files
        encrypted_files = self.encryptor.encrypt_files(test_files, self.password)
        self.assertEqual(len(encrypted_files), len(test_files))
        
        # Verify all files were encrypted
        for enc_file in encrypted_files:
            self.assertTrue(os.path.exists(enc_file))
            self.assertTrue(enc_file.endswith('.encrypted'))

if __name__ == '__main__':
    unittest.main()