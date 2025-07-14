import unittest
import os
import tempfile
import shutil
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class TestEncryptionDecryption(unittest.TestCase):
    """Comprehensive test suite for encryption and decryption."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.password = "test_password_123"
        self.wrong_password = "wrong_password_456"
        
        # Create test files
        self.create_test_files()
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create various test files for encryption testing."""
        # Text file with sensitive content
        self.text_file = os.path.join(self.test_dir, "sensitive.txt")
        with open(self.text_file, 'w') as f:
            f.write("This is sensitive data that needs encryption.\n" * 100)
        
        # Binary file
        self.binary_file = os.path.join(self.test_dir, "data.bin")
        with open(self.binary_file, 'wb') as f:
            f.write(b'Binary sensitive data ' * 1000)
        
        # Small file
        self.small_file = os.path.join(self.test_dir, "small.txt")
        with open(self.small_file, 'w') as f:
            f.write("Small content")
        
        # Large file
        self.large_file = os.path.join(self.test_dir, "large.txt")
        with open(self.large_file, 'w') as f:
            f.write("Large content " * 10000)
    
    def generate_key_from_password(self, password: str) -> bytes:
        """Generate a Fernet key from a password."""
        # Use fixed salt for testing consistency
        salt = b'test_salt_fixed_16'  # 16 bytes for testing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def test_fernet_encryption_decryption(self):
        """Test Fernet encryption and decryption."""
        # Generate key
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        # Test data
        test_data = b"This is test data for encryption"
        
        # Encrypt
        encrypted = fernet.encrypt(test_data)
        
        # Verify encryption changed the data
        self.assertNotEqual(encrypted, test_data)
        self.assertTrue(isinstance(encrypted, bytes))
        
        # Decrypt
        decrypted = fernet.decrypt(encrypted)
        
        # Verify decryption restored original data
        self.assertEqual(decrypted, test_data)
    
    def test_file_encryption_decryption(self):
        """Test file encryption and decryption."""
        # Read original file content
        with open(self.text_file, 'rb') as f:
            original_content = f.read()
        
        # Generate key
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        # Encrypt file
        encrypted_file = self.text_file + '.encrypted'
        with open(self.text_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Verify encrypted file exists and is different
        self.assertTrue(os.path.exists(encrypted_file))
        with open(encrypted_file, 'rb') as f:
            encrypted_content = f.read()
            self.assertNotEqual(encrypted_content, original_content)
        
        # Decrypt file
        decrypted_file = os.path.join(self.test_dir, "decrypted.txt")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:
                encrypted_data = infile.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        # Verify decrypted content matches original
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, original_content)
    
    def test_binary_file_encryption(self):
        """Test encryption of binary files."""
        # Read original binary file content
        with open(self.binary_file, 'rb') as f:
            original_content = f.read()
        
        # Generate key
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        # Encrypt binary file
        encrypted_file = self.binary_file + '.encrypted'
        with open(self.binary_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Decrypt binary file
        decrypted_file = os.path.join(self.test_dir, "decrypted.bin")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:
                encrypted_data = infile.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        # Verify binary content integrity
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, original_content)
    
    def test_wrong_password_decryption(self):
        """Test decryption with wrong password fails."""
        # Read original file content
        with open(self.text_file, 'rb') as f:
            original_content = f.read()
        
        # Encrypt with correct password
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        encrypted_file = self.text_file + '.encrypted'
        with open(self.text_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Try to decrypt with wrong password
        wrong_key = self.generate_key_from_password(self.wrong_password)
        wrong_fernet = Fernet(wrong_key)
        
        with open(encrypted_file, 'rb') as infile:
            encrypted_data = infile.read()
            
        # This should raise an exception
        with self.assertRaises(Exception):
            wrong_fernet.decrypt(encrypted_data)
    
    def test_small_file_encryption(self):
        """Test encryption of small files."""
        # Read original file content
        with open(self.small_file, 'rb') as f:
            original_content = f.read()
        
        # Generate key
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        # Encrypt small file
        encrypted_file = self.small_file + '.encrypted'
        with open(self.small_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Decrypt small file
        decrypted_file = os.path.join(self.test_dir, "decrypted_small.txt")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:
                encrypted_data = infile.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        # Verify content integrity
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, original_content)
    
    def test_large_file_encryption(self):
        """Test encryption of large files (within Fernet limits)."""
        # Create a moderately large file (within Fernet limits)
        large_content = b"Large content " * 1000  # ~15KB, well within limits
        large_file = os.path.join(self.test_dir, "large.txt")
        with open(large_file, 'wb') as f:
            f.write(large_content)
        
        # Read original file content
        with open(large_file, 'rb') as f:
            original_content = f.read()
        
        # Generate key
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        # Encrypt file
        encrypted_file = large_file + '.encrypted'
        with open(large_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Decrypt file
        decrypted_file = os.path.join(self.test_dir, "decrypted_large.txt")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:
                encrypted_data = infile.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        # Verify content integrity
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, original_content)
    
    def test_key_generation(self):
        """Test key generation functionality."""
        # Test Fernet key generation
        key1 = Fernet.generate_key()
        key2 = Fernet.generate_key()
        
        # Verify keys are different
        self.assertNotEqual(key1, key2)
        self.assertEqual(len(key1), 44)  # 32 bytes, base64 encoded
        
        # Test password-based key generation
        key1 = self.generate_key_from_password(self.password)
        key2 = self.generate_key_from_password(self.password)
        
        # Same password should generate same key
        self.assertEqual(key1, key2)
        
        # Different passwords should generate different keys
        key3 = self.generate_key_from_password(self.wrong_password)
        self.assertNotEqual(key1, key3)
    
    def test_empty_file_encryption(self):
        """Test encryption of empty files."""
        # Create empty file
        empty_file = os.path.join(self.test_dir, "empty.txt")
        with open(empty_file, 'w'):
            pass  # Create empty file
        
        # Generate key
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        # Encrypt empty file
        encrypted_file = empty_file + '.encrypted'
        with open(empty_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Decrypt empty file
        decrypted_file = os.path.join(self.test_dir, "decrypted_empty.txt")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:
                encrypted_data = infile.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        # Verify content integrity
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, b'')
    
    def test_encryption_metadata_preservation(self):
        """Test that encryption doesn't corrupt file metadata."""
        # Create test file with known content
        test_content = b"Test content for metadata preservation"
        test_file = os.path.join(self.test_dir, "metadata_test.txt")
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Generate key
        key = self.generate_key_from_password(self.password)
        fernet = Fernet(key)
        
        # Encrypt file
        encrypted_file = test_file + '.encrypted'
        with open(test_file, 'rb') as infile:
            with open(encrypted_file, 'wb') as outfile:
                data = infile.read()
                encrypted_data = fernet.encrypt(data)
                outfile.write(encrypted_data)
        
        # Decrypt file
        decrypted_file = os.path.join(self.test_dir, "decrypted_metadata.txt")
        with open(encrypted_file, 'rb') as infile:
            with open(decrypted_file, 'wb') as outfile:
                encrypted_data = infile.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                outfile.write(decrypted_data)
        
        # Verify content integrity
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
            self.assertEqual(decrypted_content, test_content)


class TestEncryptionIntegration(unittest.TestCase):
    """Integration tests for encryption and decryption workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.password = "integration_test_password"
        
        # Create test directory structure
        self.source_dir = os.path.join(self.test_dir, "encryption_source")
        os.makedirs(self.source_dir)
        
        # Create test files
        self.create_integration_test_files()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def create_integration_test_files(self):
        """Create test files for integration testing."""
        # Create files of different types
        
        # Text files
        for i in range(3):
            file_path = os.path.join(self.source_dir, f"text_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Text file {i} content\n" * 100)
        
        # Binary files
        for i in range(2):
            file_path = os.path.join(self.source_dir, f"binary_{i}.bin")
            with open(file_path, 'wb') as f:
                f.write(b'Binary data ' * 1000)
        
        # Nested directory structure
        nested_dir = os.path.join(self.source_dir, "subdir", "nested")
        os.makedirs(nested_dir)
        
        nested_file = os.path.join(nested_dir, "nested.txt")
        with open(nested_file, 'w') as f:
            f.write("Nested file content\n" * 50)
    
    def test_batch_file_encryption(self):
        """Test encrypting multiple files."""
        # Get all files in source directory
        files_to_encrypt = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                files_to_encrypt.append(file_path)
        
        # Generate key
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        # Encrypt all files
        encrypted_files = []
        for file_path in files_to_encrypt:
            encrypted_file = file_path + '.encrypted'
            with open(file_path, 'rb') as infile:
                with open(encrypted_file, 'wb') as outfile:
                    data = infile.read()
                    encrypted_data = fernet.encrypt(data)
                    outfile.write(encrypted_data)
            encrypted_files.append(encrypted_file)
        
        # Verify all files were encrypted
        self.assertEqual(len(encrypted_files), len(files_to_encrypt))
        for enc_file in encrypted_files:
            self.assertTrue(os.path.exists(enc_file))
        
        # Decrypt all files
        decrypted_files = []
        for encrypted_file in encrypted_files:
            original_path = encrypted_file.replace('.encrypted', '')
            decrypted_file = original_path + '.decrypted'
            
            with open(encrypted_file, 'rb') as infile:
                with open(decrypted_file, 'wb') as outfile:
                    encrypted_data = infile.read()
                    decrypted_data = fernet.decrypt(encrypted_data)
                    outfile.write(decrypted_data)
            decrypted_files.append(decrypted_file)
        
        # Verify all files were decrypted
        self.assertEqual(len(decrypted_files), len(files_to_encrypt))
        
        # Verify content integrity for all files
        for original_path, decrypted_path in zip(
            files_to_encrypt, decrypted_files
        ):
            with open(original_path, 'rb') as f1, open(
                decrypted_path, 'rb'
            ) as f2:
                self.assertEqual(f1.read(), f2.read())
    
    def test_encryption_with_different_passwords(self):
        """Test encryption with different passwords."""
        test_file = os.path.join(self.source_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content for password comparison")
        
        # Read original content
        with open(test_file, 'rb') as f:
            original_content = f.read()
        
        # Encrypt with different passwords
        passwords = ["password1", "password2", "password3"]
        encrypted_files = []
        
        for password in passwords:
            key = self.generate_key_from_password(password)
            fernet = Fernet(key)
            
            encrypted_file = os.path.join(
                self.test_dir, f"encrypted_{password}.bin"
            )
            
            with open(test_file, 'rb') as infile:
                with open(encrypted_file, 'wb') as outfile:
                    data = infile.read()
                    encrypted_data = fernet.encrypt(data)
                    outfile.write(encrypted_data)
            
            encrypted_files.append(encrypted_file)
        
        # Verify all encrypted files are different
        encrypted_contents = []
        for enc_file in encrypted_files:
            with open(enc_file, 'rb') as f:
                encrypted_contents.append(f.read())
        
        # All encrypted contents should be different
        self.assertEqual(len(encrypted_contents), len(set(encrypted_contents)))
        
        # Verify each can be decrypted with correct password
        for password, encrypted_file in zip(passwords, encrypted_files):
            key = self.generate_key_from_password(password)
            fernet = Fernet(key)
            
            decrypted_file = os.path.join(
                self.test_dir, f"decrypted_{password}.txt"
            )
            
            with open(encrypted_file, 'rb') as infile:
                with open(decrypted_file, 'wb') as outfile:
                    encrypted_data = infile.read()
                    decrypted_data = fernet.decrypt(encrypted_data)
                    outfile.write(decrypted_data)
            
            # Verify content integrity
            with open(decrypted_file, 'rb') as f:
                self.assertEqual(f.read(), original_content)
    
    def generate_key_from_password(self, password: str) -> bytes:
        """Generate a Fernet key from a password."""
        salt = b'stable_salt_for_integration_testing'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key


if __name__ == '__main__':
    unittest.main()
