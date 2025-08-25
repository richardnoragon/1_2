"""
Basic unit tests for encrypt.py - Final Version
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

# Add the source directory to the path for imports
test_dir = os.path.dirname(__file__)
src_dir = os.path.join(test_dir, '..', '..', 'src', 'utilities', 
                       'pdf_tools', 'pdf_security')
sys.path.insert(0, src_dir)

# Mock all external dependencies
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

# Mock all external modules
sys.modules['PyPDF2'] = Mock()
sys.modules['PyPDF2'].PdfReader = MockPdfReader
sys.modules['PyPDF2'].PdfWriter = MockPdfWriter
sys.modules['pyAesCrypt'] = Mock()
sys.modules['PyQt5'] = Mock()
sys.modules['PyQt5.QtWidgets'] = Mock()
sys.modules['log_config'] = Mock()

# Import the module under test
import encrypt


def test_buffer_size_constant():
    """Test BUFFER_SIZE constant"""
    assert hasattr(encrypt, 'BUFFER_SIZE')
    assert encrypt.BUFFER_SIZE == 64 * 1024
    print("✓ BUFFER_SIZE constant test passed")


def test_is_encrypted_basic():
    """Test is_encrypted function"""
    with patch('builtins.open', mock_open()), \
         patch('encrypt.logger') as mock_logger:
        result = encrypt.is_encrypted("test.pdf")
        assert isinstance(result, bool)
        print("✓ is_encrypted basic test passed")


def test_is_encrypted_file_not_found():
    """Test is_encrypted with non-existent file"""
    with patch('encrypt.logger') as mock_logger, \
         patch('encrypt.QMessageBox'):
        result = encrypt.is_encrypted("non_existent.pdf")
        assert result is False
        print("✓ is_encrypted file not found test passed")


def test_encrypt_pdf_basic():
    """Test encrypt_pdf function"""
    temp_dir = tempfile.mkdtemp()
    try:
        test_file = os.path.join(temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("test")
        
        with patch('builtins.open', mock_open()), \
             patch('encrypt.logger'):
            result = encrypt.encrypt_pdf(test_file, "password")
            expected = test_file.replace(".pdf", "_encrypted.pdf")
            assert result == expected
            print("✓ encrypt_pdf basic test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_decrypt_pdf_basic():
    """Test decrypt_pdf function"""
    temp_dir = tempfile.mkdtemp()
    try:
        test_file = os.path.join(temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("test")
        
        with patch('builtins.open', mock_open()), \
             patch('encrypt.PdfReader') as mock_reader_class, \
             patch('encrypt.logger'):
            
            mock_reader = Mock()
            mock_reader.is_encrypted = True
            mock_reader.decrypt.return_value = True
            mock_reader.pages = []
            mock_reader_class.return_value = mock_reader
            
            result = encrypt.decrypt_pdf(test_file, "password")
            expected = test_file.replace(".pdf", "_decrypted.pdf")
            assert result == expected
            print("✓ decrypt_pdf basic test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cipher_stream():
    """Test cipher_stream function"""
    input_buffer = BytesIO(b"test data")
    
    with patch('encrypt.pyAesCrypt') as mock_aes, \
         patch('encrypt.logger'):
        mock_aes.encryptStream = Mock()
        result = encrypt.cipher_stream(input_buffer, "password")
        assert isinstance(result, BytesIO)
        print("✓ cipher_stream test passed")


def test_decipher_file():
    """Test decipher_file function"""
    temp_dir = tempfile.mkdtemp()
    try:
        input_file = os.path.join(temp_dir, "input.txt")
        output_file = os.path.join(temp_dir, "output.txt")
        
        with open(input_file, 'w') as f:
            f.write("test")
        
        with patch('encrypt.pyAesCrypt') as mock_aes, \
             patch('encrypt.logger'):
            mock_aes.decryptFile = Mock()
            result = encrypt.decipher_file(input_file, output_file, "password")
            assert result is True
            print("✓ decipher_file test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_encrypt_decrypt_file_level1():
    """Test encrypt_decrypt_file with level 1"""
    temp_dir = tempfile.mkdtemp()
    try:
        test_file = os.path.join(temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("test")
        
        with patch('encrypt.encrypt_pdf') as mock_encrypt, \
             patch('encrypt.logger'):
            mock_encrypt.return_value = "output.pdf"
            
            result = encrypt.encrypt_decrypt_file(
                input_file=test_file,
                password="password",
                action="encrypt",
                level=1
            )
            assert result is True
            print("✓ encrypt_decrypt_file level 1 test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_password_action():
    """Test Password action class"""
    import argparse
    parser = argparse.ArgumentParser()
    namespace = argparse.Namespace()
    action = encrypt.Password(None, 'password')
    
    action(parser, namespace, "test_password", None)
    assert namespace.password == "test_password"
    print("✓ Password action test passed")


def test_is_valid_path():
    """Test is_valid_path function"""
    temp_dir = tempfile.mkdtemp()
    try:
        # Test with existing directory
        result = encrypt.is_valid_path(temp_dir)
        assert result == temp_dir
        
        # Test with non-existent path
        try:
            encrypt.is_valid_path("non_existent_12345")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        
        print("✓ is_valid_path test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_error_handling():
    """Test error handling scenarios"""
    with patch('encrypt.logger') as mock_logger, \
         patch('encrypt.QMessageBox'):
        
        # Test with no input file
        result = encrypt.encrypt_decrypt_file(
            input_file=None,
            password="password"
        )
        assert result is False
        
        # Test with no password
        result = encrypt.encrypt_decrypt_file(
            input_file="test.pdf",
            password=None
        )
        assert result is False
        
        print("✓ Error handling tests passed")


def run_all_tests():
    """Run all tests and generate results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE UNIT TESTS FOR ENCRYPT.PY")
    print(f"Test Execution Timestamp: {timestamp}")
    print(f"{'='*60}\n")
    
    tests = [
        test_buffer_size_constant,
        test_is_encrypted_basic,
        test_is_encrypted_file_not_found,
        test_encrypt_pdf_basic,
        test_decrypt_pdf_basic,
        test_cipher_stream,
        test_decipher_file,
        test_encrypt_decrypt_file_level1,
        test_password_action,
        test_is_valid_path,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"TEST RESULTS SUMMARY:")
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print(f"{'='*60}")
    
    # Generate results file
    results_file = os.path.join(os.path.dirname(__file__), 
                               f"result_encrypt_test_summary_2025-08-24.txt")
    
    with open(results_file, 'w') as f:
        f.write("ENCRYPT.PY UNIT TEST RESULTS\n")
        f.write("=" * 30 + "\n\n")
        f.write(f"Execution Timestamp: {timestamp}\n")
        f.write(f"Total Tests: {len(tests)}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Success Rate: {(passed/len(tests)*100):.1f}%\n\n")
        
        f.write("TEST COVERAGE AREAS:\n")
        f.write("- PDF Encryption Functions\n")
        f.write("- PDF Decryption Functions\n")
        f.write("- Stream Cipher Operations\n")
        f.write("- File Validation\n")
        f.write("- Error Handling\n")
        f.write("- Password Handling\n")
        f.write("- Path Validation\n")
        f.write("- Composite Operations\n")
    
    print(f"Results saved to: {results_file}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)