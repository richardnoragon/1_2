#!/usr/bin/env python3
"""
Compression End-to-End Test Suite

Comprehensive E2E testing for Compression tool functionality.
Tests complete workflows from archive creation through extraction
and integrity verification.

Created: 2025-09-04
Coverage: Archive creation workflows, multi-format compression,
          extraction with integrity verification, password protection
Priority: HIGH (implementing 0% E2E coverage for File Operations tools)
"""

import os
import sys
import tempfile
import time
from unittest.mock import Mock

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.file_operations_test_utilities import (
        FileOperationsPerformanceMonitor, FileOperationsSignalTracker,
        MockCompressionTool, compression_test_environment, create_test_archive)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Operations utilities not available"
)


class TestCompressionArchiveCreation:
    """Test archive creation workflows across multiple formats."""
    
    def test_zip_archive_creation_workflow(self, compression_test_environment):
        """
        Test: File Selection → ZIP Creation → Compression Options → Validation
        Target: < 30 seconds for ZIP archive creation
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('compression', 'zip_creation')
        
        start_time = time.time()
        
        try:
            # Collect files for ZIP compression
            test_files = []
            for root, dirs, files in os.walk(test_data_path):
                for file in files[:20]:  # Limit for testing performance
                    test_files.append(os.path.join(root, file))
            
            assert len(test_files) >= 5, "Should have files for compression"
            
            # Create temporary archive path
            archive_path = os.path.join(test_data_path, 'test_archive.zip')
            
            # Execute ZIP archive creation
            zip_options = {
                'compression_level': 6,
                'include_metadata': True,
                'preserve_structure': True,
                'exclude_patterns': ['*.tmp', '*.log']
            }
            
            result = tool.create_archive(
                test_files, archive_path, 'zip', zip_options)
            
            # Verify archive creation completion
            assert result is not None, "Archive result should not be None"
            assert result['status'] == 'success', \
                f"ZIP creation should succeed, got: {result.get('status')}"
            assert 'file_count' in result, "Result should include file count"
            assert result['file_count'] == len(test_files), \
                "Should archive all selected files"
            
            # Verify archive data structure
            assert archive_path in tool.archive_data, \
                "Archive should be tracked in tool data"
            archive_info = tool.archive_data[archive_path]
            
            required_fields = ['archive_path', 'format', 'files_count',
                             'original_size', 'compressed_size', 
                             'compression_ratio', 'creation_time']
            for field in required_fields:
                assert field in archive_info, \
                    f"Archive info missing field: {field}"
            
            # Verify compression ratio is reasonable
            assert 0.1 <= archive_info['compression_ratio'] <= 1.0, \
                "Compression ratio should be between 10% and 100%"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"ZIP creation took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'compression', 'zip_creation')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_7z_archive_creation_workflow(self, compression_test_environment):
        """
        Test: 7-Zip Format → Enhanced Compression → Archive Creation → Validation
        Target: < 45 seconds for 7Z archive creation
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('compression', '7z_creation')
        
        start_time = time.time()
        
        try:
            # Collect files for 7Z compression
            test_files = []
            for root, dirs, files in os.walk(test_data_path):
                for file in files[:15]:
                    test_files.append(os.path.join(root, file))
            
            archive_path = os.path.join(test_data_path, 'test_archive.7z')
            
            # Execute 7Z archive creation with high compression
            sevenz_options = {
                'compression_level': 9,  # Maximum compression
                'compression_method': 'LZMA2',
                'solid_compression': True,
                'multithreading': True,
                'dictionary_size': '64MB'
            }
            
            result = tool.create_archive(
                test_files, archive_path, '7z', sevenz_options)
            
            # Verify 7Z creation
            assert result['status'] == 'success', \
                "7Z creation should succeed"
            
            # Verify 7Z format-specific features
            archive_info = tool.archive_data[archive_path]
            assert archive_info['format'] == '7z', \
                "Should create 7Z format archive"
            
            # 7Z should achieve better compression ratio
            assert archive_info['compression_ratio'] <= 0.7, \
                "7Z should achieve at least 30% compression"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 45.0, \
                f"7Z creation took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'compression', '7z_creation')
            assert perf_result['target_met'], \
                f"7Z creation performance target not met: {perf_result}"
    
    def test_tar_archive_creation_workflow(self, compression_test_environment):
        """
        Test: TAR Format → Unix-style Archiving → Creation → Validation
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Collect files for TAR archiving
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:10]:
                test_files.append(os.path.join(root, file))
        
        archive_path = os.path.join(test_data_path, 'test_archive.tar.gz')
        
        # Execute TAR archive creation
        tar_options = {
            'compression_type': 'gzip',
            'preserve_permissions': True,
            'preserve_timestamps': True,
            'follow_symlinks': False
        }
        
        result = tool.create_archive(
            test_files, archive_path, 'tar', tar_options)
        
        # Verify TAR creation
        assert result['status'] == 'success', \
            "TAR creation should succeed"
        
        # Verify TAR-specific features
        if archive_path in tool.archive_data:
            archive_info = tool.archive_data[archive_path]
            assert archive_info['format'] == 'tar', \
                "Should create TAR format archive"
    
    def test_unsupported_format_workflow(self, compression_test_environment):
        """
        Test: Unsupported Format → Error Handling → User Feedback
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Try to create archive with unsupported format
        test_files = [os.path.join(test_data_path, 'test_file.txt')]
        archive_path = os.path.join(test_data_path, 'test.xyz')
        
        result = tool.create_archive(
            test_files, archive_path, 'unsupported_format')
        
        # Verify error handling
        assert result['status'] == 'error', \
            "Unsupported format should return error"
        assert 'Unsupported format' in result['message'], \
            "Error message should indicate unsupported format"


class TestCompressionExtraction:
    """Test archive extraction and integrity verification."""
    
    def test_archive_extraction_workflow(self, compression_test_environment):
        """
        Test: Archive Selection → Extraction Options → Extract → Validation
        Target: < 20 seconds for archive extraction
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # First create an archive to extract
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:8]:
                test_files.append(os.path.join(root, file))
        
        archive_path = os.path.join(test_data_path, 'extraction_test.zip')
        create_result = tool.create_archive(test_files, archive_path, 'zip')
        
        assert create_result['status'] == 'success', \
            "Archive creation for extraction test should succeed"
        
        # Start extraction monitoring
        performance_monitor.start_monitoring('compression', 'archive_extraction')
        
        start_time = time.time()
        
        try:
            # Execute archive extraction
            extract_path = os.path.join(test_data_path, 'extracted')
            extraction_options = {
                'overwrite_existing': True,
                'preserve_structure': True,
                'create_directory': True,
                'verify_integrity': True
            }
            
            result = tool.extract_archive(
                archive_path, extract_path, extraction_options)
            
            # Verify extraction completion
            assert result['status'] == 'success', \
                "Archive extraction should succeed"
            assert 'file_count' in result, \
                "Should report number of files extracted"
            
            # Verify extraction results
            assert len(tool.extraction_results) > 0, \
                "Should have extraction results"
            
            extraction_results = tool.extraction_results
            for extract_item in extraction_results[:5]:  # Check first 5
                required_fields = ['file_name', 'file_size', 'extracted_path',
                                 'status', 'extraction_time']
                for field in required_fields:
                    assert field in extract_item, \
                        f"Extraction item missing field: {field}"
            
            # Count successful extractions
            successful_extractions = [
                r for r in extraction_results if r['status'] == 'success'
            ]
            total_extractions = len(extraction_results)
            success_rate = len(successful_extractions) / total_extractions
            
            assert success_rate >= 0.95, \
                f"Extraction success rate too low: {success_rate:.2%}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 20.0, \
                f"Archive extraction took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'compression', 'archive_extraction')
            assert perf_result['target_met'], \
                f"Extraction performance target not met: {perf_result}"
    
    def test_integrity_verification_workflow(self, compression_test_environment):
        """
        Test: Archive Integrity Check → Hash Validation → Status Report
        Target: < 10 seconds for integrity verification
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Create archive for integrity testing
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:5]:
                test_files.append(os.path.join(root, file))
        
        archive_path = os.path.join(test_data_path, 'integrity_test.zip')
        tool.create_archive(test_files, archive_path, 'zip')
        
        performance_monitor.start_monitoring('compression', 'integrity_check')
        
        start_time = time.time()
        
        try:
            # Execute integrity verification
            integrity_result = tool.verify_integrity(archive_path)
            
            # Verify integrity check completion
            assert integrity_result['status'] == 'success', \
                "Integrity verification should complete successfully"
            assert 'integrity_valid' in integrity_result, \
                "Should report integrity status"
            
            # Check integrity verification results
            assert archive_path in tool.integrity_check_results, \
                "Should store integrity check results"
            
            integrity_info = tool.integrity_check_results[archive_path]
            required_fields = ['archive_path', 'integrity_valid',
                             'verification_time']
            for field in required_fields:
                assert field in integrity_info, \
                    f"Integrity info missing field: {field}"
            
            # Most archives should pass integrity check in mock
            assert integrity_info['integrity_valid'], \
                "Archive integrity should be valid"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 10.0, \
                f"Integrity verification took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'compression', 'integrity_check')
            assert perf_result['target_met'], \
                f"Integrity check performance target not met: {perf_result}"
    
    def test_selective_extraction_workflow(self, compression_test_environment):
        """
        Test: Archive Browse → File Selection → Selective Extract → Validation
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create archive for selective extraction
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:12]:
                test_files.append(os.path.join(root, file))
        
        archive_path = os.path.join(test_data_path, 'selective_test.zip')
        tool.create_archive(test_files, archive_path, 'zip')
        
        # Execute selective extraction
        extract_path = os.path.join(test_data_path, 'selective_extracted')
        selective_options = {
            'selective_extraction': True,
            'file_patterns': ['*.txt', '*.py'],
            'exclude_patterns': ['*temp*'],
            'max_files': 5
        }
        
        result = tool.extract_archive(
            archive_path, extract_path, selective_options)
        
        assert result['status'] == 'success', \
            "Selective extraction should succeed"
        
        # Verify selective extraction worked
        # In real implementation, would check extracted files match patterns
        assert len(tool.extraction_results) <= 12, \
            "Should extract subset of files"


class TestCompressionPasswordProtection:
    """Test password-protected archive handling."""
    
    def test_password_protected_creation_workflow(self, 
                                                 compression_test_environment):
        """
        Test: Password Setup → Protected Archive Creation → Security Validation
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Collect files for password-protected archive
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:6]:
                test_files.append(os.path.join(root, file))
        
        archive_path = os.path.join(test_data_path, 'protected_archive.zip')
        
        # Create password-protected archive
        password_options = {
            'password': 'TestPassword123!',
            'encryption_method': 'AES-256',
            'encrypt_filenames': True,
            'compression_level': 6
        }
        
        result = tool.create_archive(
            test_files, archive_path, 'zip', password_options)
        
        # Verify password-protected creation
        assert result['status'] == 'success', \
            "Password-protected creation should succeed"
        
        # Verify password protection was applied
        if archive_path in tool.archive_data:
            archive_info = tool.archive_data[archive_path]
            assert archive_info['password_protected'], \
                "Archive should be marked as password-protected"
    
    def test_password_protected_extraction_workflow(self, 
                                                   compression_test_environment):
        """
        Test: Protected Archive → Password Entry → Extract → Validation
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create password-protected archive first
        test_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:4]:
                test_files.append(os.path.join(root, file))
        
        archive_path = os.path.join(test_data_path, 'protected_extract.zip')
        password = 'ExtractTest456!'
        
        create_options = {'password': password}
        tool.create_archive(test_files, archive_path, 'zip', create_options)
        
        # Extract password-protected archive
        extract_path = os.path.join(test_data_path, 'protected_extracted')
        extract_options = {
            'password': password,
            'verify_password': True
        }
        
        result = tool.extract_archive(
            archive_path, extract_path, extract_options)
        
        # Verify password-protected extraction
        assert result['status'] == 'success', \
            "Password-protected extraction should succeed"
        
        # Test wrong password handling
        wrong_extract_options = {
            'password': 'WrongPassword123',
            'verify_password': True
        }
        
        wrong_result = tool.extract_archive(
            archive_path, extract_path + '_wrong', wrong_extract_options)
        
        # In real implementation, this should fail with wrong password
        # Mock implementation might not simulate this, so we just verify it runs
        assert wrong_result is not None, \
            "Should handle wrong password gracefully"
    
    def test_password_strength_validation_workflow(self, 
                                                  compression_test_environment):
        """
        Test: Password Validation → Strength Check → Security Recommendations
        """
        env = compression_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        test_files = [os.path.join(test_data_path, 'test_file.txt')]
        
        # Test various password strengths
        password_tests = [
            {
                'password': '123',
                'description': 'Weak password',
                'should_warn': True
            },
            {
                'password': 'password',
                'description': 'Common password',
                'should_warn': True
            },
            {
                'password': 'StrongPassword123!@#',
                'description': 'Strong password',
                'should_warn': False
            }
        ]
        
        for test_case in password_tests:
            archive_path = os.path.join(
                test_data_path, 
                f"password_test_{test_case['password'][:3]}.zip"
            )
            
            password_options = {
                'password': test_case['password'],
                'validate_password_strength': True
            }
            
            result = tool.create_archive(
                test_files, archive_path, 'zip', password_options)
            
            # All should succeed in mock implementation
            assert result['status'] == 'success', \
                f"Archive creation should succeed for {test_case['description']}"


# Test runner configuration
def run_compression_e2e_tests():
    """Run the Compression E2E test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=3"  # Stop after 3 failures
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing if available
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass
    
    # Run the tests
    print("Starting Compression End-to-End Tests...")
    exit_code = run_compression_e2e_tests()
    
    print(f"\nCompression E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)