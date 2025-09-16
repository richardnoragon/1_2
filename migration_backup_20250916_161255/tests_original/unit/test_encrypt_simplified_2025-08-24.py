"""
Simplified comprehensive unit tests for encrypt.py
Test file for PDF encryption/decryption functionality
Created: 2025-08-24
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from io import BytesIO
from unittest.mock import Mock, mock_open, patch

import pytest

# Add the source directory to the path for imports
test_dir = os.path.dirname(__file__)
src_dir = os.path.join(test_dir, '..', '..', 'src', 'utilities', 
                       'pdf_tools', 'pdf_security')
sys.path.insert(0, src_dir)

# Create a minimal mock for imports that might not be available
class MockPdfReader:
    def __init__(self, file_path):
        self.is_encrypted = False
        self.pages = []
    
    def decrypt(self, password):
        return True

class MockPdfWriter:
    def __init__(self):
        self.pages = []
    
    def add_page(self, page):
        self.pages.append(page)
    
    def encrypt(self, password):
        pass
    
    def write(self, file_obj):
        file_obj.write(b"mock_pdf_data")

# Mock external dependencies
sys.modules['PyPDF2'] = Mock()
sys.modules['PyPDF2'].PdfReader = MockPdfReader
sys.modules['PyPDF2'].PdfWriter = MockPdfWriter
sys.modules['pyAesCrypt'] = Mock()
sys.modules['PyQt5'] = Mock()
sys.modules['PyQt5.QtWidgets'] = Mock()
sys.modules['log_config'] = Mock()

# Import the module under test after mocking
import encrypt


class TestEncryptBasicFunctionality:
    """Basic functionality tests for encrypt.py"""
    
    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_file_path(self, temp_directory):
        """Create a sample file for testing"""
        file_path = os.path.join(temp_directory, "test.pdf")
        with open(file_path, 'w') as f:
            f.write("sample content")
        return file_path
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing"""
        with patch('encrypt.logger') as mock_log:
            yield mock_log

    def test_buffer_size_constant(self):
        """Test BUFFER_SIZE constant exists and has correct value"""
        assert hasattr(encrypt, 'BUFFER_SIZE')
        assert encrypt.BUFFER_SIZE == 64 * 1024

    def test_is_encrypted_with_mock_file(self, sample_file_path, mock_logger):
        """Test is_encrypted function with mocked file"""
        with patch('builtins.open', mock_open()):
            result = encrypt.is_encrypted(sample_file_path)
            assert isinstance(result, bool)
            mock_logger.debug.assert_called()

    def test_is_encrypted_file_not_found(self, mock_logger):
        """Test is_encrypted with non-existent file"""
        with patch('encrypt.QMessageBox') as mock_msgbox:
            result = encrypt.is_encrypted("non_existent.pdf")
            assert result is False
            mock_logger.error.assert_called()

    def test_encrypt_pdf_basic(self, sample_file_path, mock_logger):
        """Test basic encrypt_pdf functionality"""
        with patch('builtins.open', mock_open()):
            result = encrypt.encrypt_pdf(sample_file_path, "password")
            # Function should attempt to return output filename
            expected_output = sample_file_path.replace(".pdf", "_encrypted.pdf")
            assert result == expected_output

    def test_decrypt_pdf_basic(self, sample_file_path, mock_logger):
        """Test basic decrypt_pdf functionality"""
        with patch('builtins.open', mock_open()):
            with patch('encrypt.PdfReader') as mock_reader_class:
                mock_reader = Mock()
                mock_reader.is_encrypted = True
                mock_reader.decrypt.return_value = True
                mock_reader.pages = []
                mock_reader_class.return_value = mock_reader
                
                result = encrypt.decrypt_pdf(sample_file_path, "password")
                expected_output = sample_file_path.replace(".pdf", "_decrypted.pdf")
                assert result == expected_output

    def test_cipher_stream_basic(self, mock_logger):
        """Test basic cipher_stream functionality"""
        input_buffer = BytesIO(b"test data")
        
        with patch('encrypt.pyAesCrypt') as mock_aes:
            mock_aes.encryptStream = Mock()
            result = encrypt.cipher_stream(input_buffer, "password")
            assert isinstance(result, BytesIO)

    def test_decipher_file_basic(self, temp_directory, mock_logger):
        """Test basic decipher_file functionality"""
        input_file = os.path.join(temp_directory, "input.txt")
        output_file = os.path.join(temp_directory, "output.txt")
        
        with open(input_file, 'w') as f:
            f.write("test content")
        
        with patch('encrypt.pyAesCrypt') as mock_aes:
            mock_aes.decryptFile = Mock()
            result = encrypt.decipher_file(input_file, output_file, "password")
            assert result is True

    def test_encrypt_decrypt_file_basic_params(self, sample_file_path, mock_logger):
        """Test encrypt_decrypt_file with basic parameters"""
        with patch('encrypt.encrypt_pdf') as mock_encrypt:
            mock_encrypt.return_value = "output.pdf"
            
            result = encrypt.encrypt_decrypt_file(
                input_file=sample_file_path,
                password="test_password",
                action="encrypt",
                level=1
            )
            assert result is True

    def test_password_action_class(self):
        """Test Password action class"""
        import argparse
        parser = argparse.ArgumentParser()
        namespace = argparse.Namespace()
        action = encrypt.Password(None, 'password')
        
        action(parser, namespace, "test_password", None)
        assert namespace.password == "test_password"

    def test_is_valid_path_with_file(self, sample_file_path):
        """Test is_valid_path with existing file"""
        result = encrypt.is_valid_path(sample_file_path)
        assert result == sample_file_path

    def test_is_valid_path_with_directory(self, temp_directory):
        """Test is_valid_path with existing directory"""
        result = encrypt.is_valid_path(temp_directory)
        assert result == temp_directory

    def test_is_valid_path_invalid(self):
        """Test is_valid_path with invalid path"""
        with pytest.raises(ValueError):
            encrypt.is_valid_path("non_existent_path_12345")

    def test_is_valid_path_empty(self):
        """Test is_valid_path with empty string"""
        with pytest.raises(ValueError):
            encrypt.is_valid_path("")

    def test_encrypt_decrypt_file_no_input_file(self, mock_logger):
        """Test encrypt_decrypt_file with no input file"""
        with patch('encrypt.QMessageBox'):
            result = encrypt.encrypt_decrypt_file(
                input_file=None,
                password="password"
            )
            assert result is False

    def test_encrypt_decrypt_file_no_password(self, sample_file_path, mock_logger):
        """Test encrypt_decrypt_file with no password"""
        with patch('encrypt.QMessageBox'):
            result = encrypt.encrypt_decrypt_file(
                input_file=sample_file_path,
                password=None
            )
            assert result is False

    def test_encrypt_decrypt_file_level_2_encrypt(self, sample_file_path, mock_logger):
        """Test encrypt_decrypt_file with level 2 encryption"""
        with patch('encrypt.encrypt_pdf') as mock_encrypt_pdf, \
             patch('encrypt.cipher_stream') as mock_cipher, \
             patch('builtins.open', mock_open()), \
             patch('os.remove'):
            
            mock_encrypt_pdf.return_value = "intermediate.pdf"
            mock_cipher.return_value = BytesIO(b"encrypted_data")
            
            result = encrypt.encrypt_decrypt_file(
                input_file=sample_file_path,
                password="password",
                action="encrypt",
                level=2
            )
            assert result is True

    def test_encrypt_decrypt_file_level_2_decrypt(self, sample_file_path, mock_logger):
        """Test encrypt_decrypt_file with level 2 decryption"""
        with patch('encrypt.decipher_file') as mock_decipher, \
             patch('encrypt.decrypt_pdf') as mock_decrypt, \
             patch('os.remove'):
            
            mock_decipher.return_value = True
            mock_decrypt.return_value = "decrypted.pdf"
            
            result = encrypt.encrypt_decrypt_file(
                input_file=sample_file_path,
                password="password",
                action="decrypt", 
                level=2
            )
            assert result is True


class TestEncryptErrorHandling:
    """Error handling tests for encrypt.py"""
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing"""
        with patch('encrypt.logger') as mock_log:
            yield mock_log

    def test_is_encrypted_permission_error(self, mock_logger):
        """Test is_encrypted with permission error"""
        with patch('builtins.open', side_effect=PermissionError()), \
             patch('encrypt.QMessageBox'):
            result = encrypt.is_encrypted("test.pdf")
            assert result is False
            mock_logger.error.assert_called()

    def test_encrypt_pdf_file_not_found(self, mock_logger):
        """Test encrypt_pdf with non-existent file"""
        with patch('encrypt.QMessageBox'):
            result = encrypt.encrypt_pdf("non_existent.pdf", "password")
            assert result is None
            mock_logger.error.assert_called()

    def test_decrypt_pdf_not_encrypted(self, mock_logger):
        """Test decrypt_pdf with unencrypted file"""
        with patch('builtins.open', mock_open()), \
             patch('encrypt.PdfReader') as mock_reader_class, \
             patch('encrypt.QMessageBox'):
            
            mock_reader = Mock()
            mock_reader.is_encrypted = False
            mock_reader_class.return_value = mock_reader
            
            result = encrypt.decrypt_pdf("test.pdf", "password")
            assert result is None
            mock_logger.warning.assert_called()

    def test_cipher_stream_exception(self, mock_logger):
        """Test cipher_stream with exception"""
        with patch('encrypt.pyAesCrypt') as mock_aes, \
             patch('encrypt.QMessageBox'):
            
            mock_aes.encryptStream.side_effect = Exception("Test error")
            
            result = encrypt.cipher_stream(BytesIO(b"data"), "password")
            assert result is None
            mock_logger.error.assert_called()

    def test_decipher_file_bad_password(self, mock_logger):
        """Test decipher_file with bad password"""
        with patch('encrypt.pyAesCrypt') as mock_aes, \
             patch('encrypt.QMessageBox'):
            
            mock_aes.decryptFile.side_effect = ValueError("Bad password")
            
            result = encrypt.decipher_file("input.txt", "output.txt", "wrong")
            assert result is False
            mock_logger.error.assert_called()


def generate_test_results():
    """Generate test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE UNIT TESTS FOR ENCRYPT.PY")
    print(f"Test Execution Timestamp: {timestamp}")
    print(f"{'='*60}")
    
    # Count test functions
    test_classes = [TestEncryptBasicFunctionality, TestEncryptErrorHandling]
    total_tests = 0
    for test_class in test_classes:
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        total_tests += len(test_methods)
        print(f"{test_class.__name__}: {len(test_methods)} tests")
    
    print(f"Total Tests: {total_tests}")
    print(f"{'='*60}")

if __name__ == "__main__":
    generate_test_results()
    
    # Run tests with basic reporting
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        f"--html=result_encrypt_basic_report_2025-08-24.html",
        "--self-contained-html"
    ])
    
    print(f"\nTest execution completed with exit code: {exit_code}")
    print("Generated files:")
    print("- result_encrypt_basic_report_2025-08-24.html")
    
    exit(exit_code)