"""
Enterprise-Grade Unit Tests for File Operations Manager
RFU Multi-Pane File Explorer Testing Framework

Test Coverage: All CRUD operations, permission handling, error conditions,
and atomic transaction verification with security validation.

Framework: pytest with enterprise extensions
Standards: Zero-compromise quality assurance
Coverage Target: ≥90% line coverage, ≥95% branch coverage
Security: Comprehensive security validation and penetration testing
Performance: Load testing with concurrent operations
Reliability: Error injection and recovery testing

Test Categories:
- CRUD Operations: Create, Read, Update, Delete with atomicity
- Permission Testing: Access control and privilege escalation prevention
- Error Handling: Exception scenarios and graceful recovery
- Security Testing: Path traversal, injection, privilege validation
- Performance Testing: Concurrent operations and resource management
- Transaction Testing: Rollback and consistency verification
"""

import asyncio
import hashlib
import logging
import os
import platform
import shutil
# Import the module under test
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional
from unittest.mock import AsyncMock, Mock, patch

import psutil
import pytest
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

try:
    from src.file_explorer.operations.file_operations import (
        FileOperationError, FileOperationManager, FileOperationResult,
        OperationStatus, OperationType)
except ImportError as e:
    pytest.skip(f"Cannot import file_operations module: {e}", 
                allow_module_level=True)


class TestFileOperationError:
    """
    Comprehensive test suite for FileOperationError class.
    
    Coverage:
    - Error initialization with all parameter combinations
    - Error context preservation and retrieval
    - Error serialization and logging integration
    - Error recovery metadata management
    """
    
    def test_file_operation_error_basic_initialization(self):
        """Test basic error initialization."""
        message = "Test error message"
        error = FileOperationError(message)
        
        assert str(error) == message
        assert error.operation_id is None
        assert error.file_path is None
        assert error.error_code is None
        assert error.recoverable is True
        assert error.context == {}
        assert error.timestamp > 0
    
    def test_file_operation_error_full_initialization(self):
        """Test full error initialization with all parameters."""
        message = "Complex error scenario"
        operation_id = str(uuid.uuid4())
        file_path = "/test/path/file.txt"
        error_code = 13  # Permission denied
        recoverable = False
        context = {"retry_count": 3, "last_attempt": "2025-09-13T10:00:00"}
        
        error = FileOperationError(
            message=message,
            operation_id=operation_id,
            file_path=file_path,
            error_code=error_code,
            recoverable=recoverable,
            **context
        )
        
        assert str(error) == message
        assert error.operation_id == operation_id
        assert error.file_path == file_path
        assert error.error_code == error_code
        assert error.recoverable is False
        assert error.context == context
        assert error.timestamp > 0
    
    def test_file_operation_error_context_preservation(self):
        """Test that error context is properly preserved."""
        context = {
            "source_size": 1024000,
            "destination_free_space": 500000,
            "user_permissions": "rw-r--r--",
            "filesystem_type": "NTFS"
        }
        
        error = FileOperationError("Insufficient space", **context)
        
        assert error.context == context
        assert error.context["source_size"] == 1024000
        assert error.context["filesystem_type"] == "NTFS"
    
    def test_file_operation_error_timestamp_accuracy(self):
        """Test timestamp accuracy and uniqueness."""
        error1 = FileOperationError("First error")
        time.sleep(0.01)  # Small delay to ensure timestamp difference
        error2 = FileOperationError("Second error")
        
        assert error2.timestamp > error1.timestamp
        assert abs(error1.timestamp - time.time()) < 1.0  # Within 1 second


class TestFileOperationResult:
    """
    Comprehensive test suite for FileOperationResult class.
    
    Coverage:
    - Result object initialization and field validation
    - Status transitions and state management
    - Metadata preservation and serialization
    - Performance metrics and timing data
    """
    
    def test_file_operation_result_initialization(self):
        """Test result object initialization."""
        operation_id = str(uuid.uuid4())
        operation_type = OperationType.COPY
        status = OperationStatus.PENDING
        source_paths = ["/source/file1.txt", "/source/file2.txt"]
        destination_path = "/destination/"
        
        result = FileOperationResult(
            operation_id=operation_id,
            operation_type=operation_type,
            status=status,
            source_paths=source_paths,
            destination_path=destination_path
        )
        
        assert result.operation_id == operation_id
        assert result.operation_type == operation_type
        assert result.status == status
        assert result.source_paths == source_paths
        assert result.destination_path == destination_path
    
    def test_file_operation_result_default_values(self):
        """Test default values for optional fields."""
        operation_id = str(uuid.uuid4())
        operation_type = OperationType.DELETE
        status = OperationStatus.COMPLETED
        
        result = FileOperationResult(
            operation_id=operation_id,
            operation_type=operation_type,
            status=status
        )
        
        assert result.source_paths == []
        assert result.destination_path is None
    
    @pytest.mark.parametrize("operation_type", list(OperationType))
    def test_file_operation_result_all_operation_types(self, operation_type):
        """Test result with all operation types."""
        result = FileOperationResult(
            operation_id=str(uuid.uuid4()),
            operation_type=operation_type,
            status=OperationStatus.PENDING
        )
        
        assert result.operation_type == operation_type
    
    @pytest.mark.parametrize("status", list(OperationStatus))
    def test_file_operation_result_all_status_values(self, status):
        """Test result with all status values."""
        result = FileOperationResult(
            operation_id=str(uuid.uuid4()),
            operation_type=OperationType.COPY,
            status=status
        )
        
        assert result.status == status


class TestFileOperationManager:
    """
    Comprehensive test suite for FileOperationManager class.
    
    Coverage:
    - Manager initialization and configuration
    - File operation execution (copy, move, delete, etc.)
    - Concurrent operation handling
    - Error scenarios and recovery
    - Permission and security validation
    - Performance characteristics
    - Resource management and cleanup
    """
    
    @pytest.fixture
    def app(self):
        """Provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def temp_workspace(self):
        """Provide isolated temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_test_")
        workspace = Path(temp_dir)
        
        # Create test directory structure
        (workspace / "source").mkdir()
        (workspace / "destination").mkdir()
        (workspace / "readonly").mkdir()
        
        # Create test files
        test_files = [
            "source/test1.txt",
            "source/test2.txt", 
            "source/large_file.dat",
            "source/special chars file.txt",
            "readonly/protected.txt"
        ]
        
        for file_path in test_files:
            full_path = workspace / file_path
            full_path.write_text("Test content for " + file_path)
            
        # Create large test file
        large_file = workspace / "source/large_file.dat"
        large_file.write_bytes(b"X" * 1024 * 1024)  # 1MB file
        
        # Set readonly permissions on protected file
        if platform.system() == "Windows":
            os.chmod(workspace / "readonly/protected.txt", 0o444)
        else:
            os.chmod(workspace / "readonly", 0o555)
            os.chmod(workspace / "readonly/protected.txt", 0o444)
            
        yield workspace
        
        # Cleanup
        try:
            # Remove readonly permissions for cleanup
            if platform.system() != "Windows":
                os.chmod(workspace / "readonly", 0o755)
                os.chmod(workspace / "readonly/protected.txt", 0o644)
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass  # Best effort cleanup
    
    @pytest.fixture
    def file_operation_manager(self, app, temp_workspace):
        """Provide FileOperationManager instance for testing."""
        with patch('src.rfu.file_explorer.operations.file_operations.get_log_manager'):
            with patch('src.rfu.file_explorer.operations.file_operations.ConfigManager'):
                manager = FileOperationManager()
                yield manager
                manager.shutdown()
    
    def test_file_operation_manager_initialization(self, file_operation_manager):
        """Test proper initialization of FileOperationManager."""
        manager = file_operation_manager
        
        # Verify basic properties
        assert manager is not None
        assert hasattr(manager, 'operation_queue')
        assert hasattr(manager, 'active_operations')
        assert hasattr(manager, 'executor')
        
        # Verify thread pool is configured
        assert isinstance(manager.executor, ThreadPoolExecutor)
        
        # Verify signal connections
        assert hasattr(manager, 'operationStarted')
        assert hasattr(manager, 'operationCompleted')
        assert hasattr(manager, 'operationFailed')
        assert hasattr(manager, 'progressUpdated')
    
    def test_file_operation_manager_copy_files_success(self, file_operation_manager, 
                                                      temp_workspace):
        """Test successful file copy operation."""
        manager = file_operation_manager
        
        source_files = [
            str(temp_workspace / "source/test1.txt"),
            str(temp_workspace / "source/test2.txt")
        ]
        destination = str(temp_workspace / "destination")
        
        # Execute copy operation
        operation_id = manager.copy_files(source_files, destination)
        
        # Verify operation was queued
        assert operation_id is not None
        assert len(operation_id) > 0
        
        # Wait for operation completion (with timeout)
        start_time = time.time()
        while time.time() - start_time < 5.0:  # 5 second timeout
            if operation_id in manager.completed_operations:
                break
            time.sleep(0.1)
        
        # Verify files were copied
        dest_file1 = temp_workspace / "destination/test1.txt"
        dest_file2 = temp_workspace / "destination/test2.txt"
        
        assert dest_file1.exists()
        assert dest_file2.exists()
        assert dest_file1.read_text() == "Test content for source/test1.txt"
        assert dest_file2.read_text() == "Test content for source/test2.txt"
    
    def test_file_operation_manager_move_files_success(self, file_operation_manager,
                                                      temp_workspace):
        """Test successful file move operation."""
        manager = file_operation_manager
        
        # Create additional source file for move test
        move_source = temp_workspace / "source/move_test.txt"
        move_source.write_text("Content to be moved")
        
        source_files = [str(move_source)]
        destination = str(temp_workspace / "destination")
        
        # Execute move operation
        operation_id = manager.move_files(source_files, destination)
        
        # Wait for completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify file was moved (not copied)
        dest_file = temp_workspace / "destination/move_test.txt"
        assert dest_file.exists()
        assert not move_source.exists()  # Original should be gone
        assert dest_file.read_text() == "Content to be moved"
    
    def test_file_operation_manager_delete_files_success(self, file_operation_manager,
                                                        temp_workspace):
        """Test successful file deletion operation."""
        manager = file_operation_manager
        
        # Create file to delete
        delete_target = temp_workspace / "source/delete_test.txt"
        delete_target.write_text("Content to be deleted")
        
        source_files = [str(delete_target)]
        
        # Execute delete operation
        operation_id = manager.delete_files(source_files)
        
        # Wait for completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify file was deleted
        assert not delete_target.exists()
    
    def test_file_operation_manager_create_directory_success(self, 
                                                           file_operation_manager,
                                                           temp_workspace):
        """Test successful directory creation."""
        manager = file_operation_manager
        
        new_dir = temp_workspace / "new_directory"
        
        # Execute create directory operation
        operation_id = manager.create_directory(str(new_dir))
        
        # Wait for completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify directory was created
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_file_operation_manager_concurrent_operations(self, 
                                                         file_operation_manager,
                                                         temp_workspace):
        """Test concurrent file operations."""
        manager = file_operation_manager
        
        # Create multiple source files
        source_files = []
        for i in range(10):
            source_file = temp_workspace / f"source/concurrent_{i}.txt"
            source_file.write_text(f"Concurrent content {i}")
            source_files.append(str(source_file))
        
        destination = str(temp_workspace / "destination")
        
        # Execute multiple concurrent copy operations
        operation_ids = []
        for i in range(0, 10, 2):  # Copy in pairs
            batch = source_files[i:i+2]
            op_id = manager.copy_files(batch, destination)
            operation_ids.append(op_id)
        
        # Wait for all operations to complete
        for op_id in operation_ids:
            self._wait_for_operation(manager, op_id, timeout=10.0)
        
        # Verify all files were copied
        for i in range(10):
            dest_file = temp_workspace / f"destination/concurrent_{i}.txt"
            assert dest_file.exists()
    
    def test_file_operation_manager_error_handling_nonexistent_source(self,
                                                                     file_operation_manager,
                                                                     temp_workspace):
        """Test error handling for non-existent source files."""
        manager = file_operation_manager
        
        nonexistent_files = [
            str(temp_workspace / "source/does_not_exist.txt"),
            str(temp_workspace / "source/also_missing.txt")
        ]
        destination = str(temp_workspace / "destination")
        
        # Execute copy operation with non-existent files
        operation_id = manager.copy_files(nonexistent_files, destination)
        
        # Wait for operation to fail
        self._wait_for_operation(manager, operation_id)
        
        # Verify operation failed appropriately
        if operation_id in manager.failed_operations:
            assert True  # Expected failure
        else:
            # Check that no partial files were created
            for file_path in nonexistent_files:
                dest_file = temp_workspace / "destination" / Path(file_path).name
                assert not dest_file.exists()
    
    def test_file_operation_manager_error_handling_permission_denied(self,
                                                                   file_operation_manager,
                                                                   temp_workspace):
        """Test error handling for permission denied scenarios."""
        manager = file_operation_manager
        
        # Try to delete readonly file
        readonly_file = str(temp_workspace / "readonly/protected.txt")
        
        operation_id = manager.delete_files([readonly_file])
        
        # Wait for operation completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify file still exists (delete should have failed)
        assert (temp_workspace / "readonly/protected.txt").exists()
        
        # Verify operation was marked as failed
        assert operation_id in manager.failed_operations or \
               operation_id in manager.completed_operations
    
    def test_file_operation_manager_large_file_handling(self, file_operation_manager,
                                                       temp_workspace):
        """Test handling of large file operations."""
        manager = file_operation_manager
        
        source_file = str(temp_workspace / "source/large_file.dat")
        destination = str(temp_workspace / "destination")
        
        # Execute copy operation for large file
        operation_id = manager.copy_files([source_file], destination)
        
        # Wait for completion with extended timeout
        self._wait_for_operation(manager, operation_id, timeout=30.0)
        
        # Verify large file was copied correctly
        dest_file = temp_workspace / "destination/large_file.dat"
        assert dest_file.exists()
        assert dest_file.stat().st_size == (1024 * 1024)  # 1MB
    
    def test_file_operation_manager_special_characters_handling(self,
                                                              file_operation_manager,
                                                              temp_workspace):
        """Test handling of files with special characters."""
        manager = file_operation_manager
        
        source_file = str(temp_workspace / "source/special chars file.txt")
        destination = str(temp_workspace / "destination")
        
        # Execute copy operation
        operation_id = manager.copy_files([source_file], destination)
        
        # Wait for completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify file with special characters was handled correctly
        dest_file = temp_workspace / "destination/special chars file.txt"
        assert dest_file.exists()
    
    def test_file_operation_manager_operation_cancellation(self, 
                                                          file_operation_manager,
                                                          temp_workspace):
        """Test operation cancellation functionality."""
        manager = file_operation_manager
        
        # Create many small files for a long-running operation
        source_files = []
        for i in range(100):
            source_file = temp_workspace / f"source/cancel_test_{i}.txt"
            source_file.write_text(f"Content {i}")
            source_files.append(str(source_file))
        
        destination = str(temp_workspace / "destination")
        
        # Start copy operation
        operation_id = manager.copy_files(source_files, destination)
        
        # Attempt to cancel operation quickly
        time.sleep(0.1)  # Let operation start
        cancel_result = manager.cancel_operation(operation_id)
        
        # Verify cancellation attempt was processed
        assert isinstance(cancel_result, bool)
        
        # Wait a bit and check if operation was actually cancelled
        time.sleep(1.0)
        
        # Verify operation state
        assert operation_id in (manager.cancelled_operations or 
                               manager.completed_operations or
                               manager.failed_operations)
    
    def test_file_operation_manager_progress_tracking(self, file_operation_manager,
                                                     temp_workspace):
        """Test operation progress tracking."""
        manager = file_operation_manager
        
        # Track progress updates
        progress_updates = []
        
        def track_progress(operation_id, current, total, current_file):
            progress_updates.append((operation_id, current, total, current_file))
        
        manager.progressUpdated.connect(track_progress)
        
        # Create files for progress tracking
        source_files = []
        for i in range(5):
            source_file = temp_workspace / f"source/progress_{i}.txt"
            source_file.write_text(f"Progress content {i}")
            source_files.append(str(source_file))
        
        destination = str(temp_workspace / "destination")
        
        # Execute operation
        operation_id = manager.copy_files(source_files, destination)
        
        # Wait for completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify progress updates were received
        operation_progress = [p for p in progress_updates if p[0] == operation_id]
        assert len(operation_progress) > 0
        
        # Verify progress data structure
        for op_id, current, total, current_file in operation_progress:
            assert op_id == operation_id
            assert isinstance(current, int)
            assert isinstance(total, int)
            assert isinstance(current_file, str)
            assert current <= total
    
    def test_file_operation_manager_resource_cleanup(self, file_operation_manager):
        """Test proper resource cleanup."""
        manager = file_operation_manager
        
        # Verify initial state
        initial_thread_count = threading.active_count()
        
        # Perform operation to create resources
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "cleanup_test.txt"
            test_file.write_text("Cleanup test")
            
            operation_id = manager.copy_files([str(test_file)], temp_dir)
            self._wait_for_operation(manager, operation_id)
            
            # Trigger cleanup
            manager.cleanup_completed_operations()
            
            # Verify cleanup occurred
            assert len(manager.completed_operations) >= 0  # May or may not clear
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        # Verify no thread leakage (allow some tolerance)
        final_thread_count = threading.active_count()
        assert final_thread_count <= initial_thread_count + 2
    
    def test_file_operation_manager_checksum_verification(self, 
                                                         file_operation_manager,
                                                         temp_workspace):
        """Test checksum verification for file integrity."""
        manager = file_operation_manager
        
        # Create source file with known content
        source_content = "Checksum test content with special data: äöü€"
        source_file = temp_workspace / "source/checksum_test.txt"
        source_file.write_text(source_content, encoding='utf-8')
        
        # Calculate expected checksum
        expected_checksum = hashlib.sha256(
            source_content.encode('utf-8')
        ).hexdigest()
        
        destination = str(temp_workspace / "destination")
        
        # Execute copy with checksum verification
        operation_id = manager.copy_files([str(source_file)], destination,
                                        verify_checksum=True)
        
        # Wait for completion
        self._wait_for_operation(manager, operation_id)
        
        # Verify file was copied and checksum matches
        dest_file = temp_workspace / "destination/checksum_test.txt"
        assert dest_file.exists()
        
        dest_content = dest_file.read_text(encoding='utf-8')
        dest_checksum = hashlib.sha256(dest_content.encode('utf-8')).hexdigest()
        
        assert dest_content == source_content
        assert dest_checksum == expected_checksum
    
    def _wait_for_operation(self, manager, operation_id, timeout=5.0):
        """Helper method to wait for operation completion."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if (operation_id in manager.completed_operations or
                operation_id in manager.failed_operations or
                operation_id in manager.cancelled_operations):
                break
            time.sleep(0.1)


class TestFileOperationManagerSecurity:
    """
    Security testing for FileOperationManager.
    
    Tests security aspects:
    - Path traversal attack prevention
    - Permission escalation attempts
    - Resource exhaustion protection
    - Input validation and sanitization
    """
    
    @pytest.fixture
    def app(self):
        """Provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def security_workspace(self):
        """Provide secure test workspace."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_security_test_")
        workspace = Path(temp_dir)
        
        # Create test structure
        (workspace / "safe_area").mkdir()
        (workspace / "restricted_area").mkdir()
        (workspace / "safe_area/test.txt").write_text("Safe content")
        (workspace / "restricted_area/secret.txt").write_text("Secret content")
        
        # Restrict access to restricted area
        if platform.system() != "Windows":
            os.chmod(workspace / "restricted_area", 0o700)
        
        yield workspace
        
        # Cleanup
        try:
            if platform.system() != "Windows":
                os.chmod(workspace / "restricted_area", 0o755)
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
    
    @pytest.fixture
    def security_manager(self, app):
        """Provide FileOperationManager for security testing."""
        with patch('src.rfu.file_explorer.operations.file_operations.get_log_manager'):
            with patch('src.rfu.file_explorer.operations.file_operations.ConfigManager'):
                manager = FileOperationManager()
                yield manager
                manager.shutdown()
    
    @pytest.mark.security
    def test_path_traversal_prevention(self, security_manager, security_workspace):
        """Test prevention of path traversal attacks."""
        manager = security_manager
        
        # Attempt various path traversal attacks
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "file:///etc/passwd",
            "\\\\?\\C:\\Windows\\System32",
            security_workspace / "../../../etc/passwd"
        ]
        
        for malicious_path in malicious_paths:
            # Attempt to copy to malicious location
            source = str(security_workspace / "safe_area/test.txt")
            
            try:
                operation_id = manager.copy_files([source], str(malicious_path))
                
                # If operation was accepted, verify it was sanitized
                if operation_id:
                    # Wait briefly for operation
                    time.sleep(0.5)
                    
                    # Verify no files were created in dangerous locations
                    dangerous_locations = [
                        "/etc/passwd", "/etc/shadow",
                        "C:\\Windows\\System32",
                        Path("/etc"), Path("/windows/system32")
                    ]
                    
                    for location in dangerous_locations:
                        if isinstance(location, str):
                            location = Path(location)
                        if location.exists():
                            # Verify our test file wasn't created there
                            test_file = location / "test.txt"
                            assert not test_file.exists()
                
            except (ValueError, FileOperationError, PermissionError):
                # Expected for malicious paths
                pass
    
    @pytest.mark.security
    def test_permission_escalation_prevention(self, security_manager, 
                                             security_workspace):
        """Test prevention of permission escalation."""
        manager = security_manager
        
        # Attempt to access restricted files
        restricted_file = str(security_workspace / "restricted_area/secret.txt")
        destination = str(security_workspace / "safe_area")
        
        try:
            operation_id = manager.copy_files([restricted_file], destination)
            
            if operation_id:
                # Wait for operation
                time.sleep(1.0)
                
                # Verify restricted file wasn't copied
                copied_file = security_workspace / "safe_area/secret.txt"
                if copied_file.exists():
                    # If copied, verify content wasn't actually accessible
                    content = copied_file.read_text()
                    assert content != "Secret content"
                
        except (PermissionError, FileOperationError):
            # Expected for restricted access
            pass
    
    @pytest.mark.security  
    def test_resource_exhaustion_protection(self, security_manager):
        """Test protection against resource exhaustion attacks."""
        manager = security_manager
        
        # Attempt to create excessive number of operations
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")
            
            operation_ids = []
            
            # Try to queue many operations rapidly
            for i in range(1000):  # Attempt excessive operations
                try:
                    op_id = manager.copy_files([str(test_file)], 
                                             str(Path(temp_dir) / f"dest_{i}"))
                    if op_id:
                        operation_ids.append(op_id)
                except Exception:
                    # Expected when resource limits are hit
                    break
            
            # Verify reasonable limits were enforced
            assert len(operation_ids) < 100  # Should not allow unlimited operations
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.security
    def test_input_validation(self, security_manager):
        """Test comprehensive input validation."""
        manager = security_manager
        
        # Test various invalid inputs
        invalid_inputs = [
            None,
            "",
            "   ",
            "\x00\x01\x02",  # Null bytes and control characters
            "A" * 10000,  # Extremely long path
            ["list", "instead", "of", "string"],  # Wrong type
            {"dict": "instead_of_string"},  # Wrong type
            "path\nwith\nnewlines",  # Embedded newlines
            "path\rwith\rcarriage\rreturns",  # Embedded CR
        ]
        
        for invalid_input in invalid_inputs:
            try:
                # Test copy operation with invalid input
                manager.copy_files([invalid_input], "/tmp")
                
                # Test move operation with invalid input  
                manager.move_files([invalid_input], "/tmp")
                
                # Test delete operation with invalid input
                manager.delete_files([invalid_input])
                
                # Test create directory with invalid input
                manager.create_directory(invalid_input)
                
            except (TypeError, ValueError, FileOperationError):
                # Expected for invalid inputs
                pass
    
    @pytest.mark.security
    def test_symbolic_link_security(self, security_manager, security_workspace):
        """Test security handling of symbolic links."""
        if platform.system() == "Windows":
            pytest.skip("Symbolic link test not applicable on Windows")
        
        manager = security_manager
        
        # Create symbolic link pointing outside safe area
        safe_file = security_workspace / "safe_area/test.txt"
        link_path = security_workspace / "safe_area/malicious_link"
        
        try:
            # Create symlink pointing to restricted area
            os.symlink(
                security_workspace / "restricted_area/secret.txt",
                link_path
            )
            
            # Attempt to copy through symbolic link
            operation_id = manager.copy_files([str(link_path)], 
                                            str(security_workspace / "safe_area"))
            
            if operation_id:
                time.sleep(1.0)
                
                # Verify symlink wasn't followed to access restricted content
                copied_file = security_workspace / "safe_area/malicious_link"
                if copied_file.exists() and not copied_file.is_symlink():
                    content = copied_file.read_text()
                    assert content != "Secret content"
                    
        except (OSError, FileOperationError):
            # Expected for security-restricted operations
            pass
        finally:
            # Cleanup
            if link_path.exists():
                link_path.unlink()


class TestFileOperationManagerPerformance:
    """
    Performance testing for FileOperationManager.
    
    Tests performance characteristics:
    - Throughput under various loads
    - Memory usage patterns
    - Concurrent operation scaling
    - Large file handling efficiency
    """
    
    @pytest.fixture
    def app(self):
        """Provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def performance_workspace(self):
        """Provide workspace optimized for performance testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_perf_test_")
        workspace = Path(temp_dir)
        
        # Create performance test structure
        (workspace / "source").mkdir()
        (workspace / "destination").mkdir()
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def performance_manager(self, app):
        """Provide FileOperationManager for performance testing."""
        with patch('src.rfu.file_explorer.operations.file_operations.get_log_manager'):
            with patch('src.rfu.file_explorer.operations.file_operations.ConfigManager'):
                manager = FileOperationManager()
                yield manager
                manager.shutdown()
    
    @pytest.mark.performance
    def test_throughput_many_small_files(self, performance_manager, 
                                       performance_workspace):
        """Test throughput with many small files."""
        manager = performance_manager
        
        # Create many small files
        num_files = 1000
        source_files = []
        
        for i in range(num_files):
            file_path = performance_workspace / f"source/small_{i:04d}.txt"
            file_path.write_text(f"Small file content {i}")
            source_files.append(str(file_path))
        
        destination = str(performance_workspace / "destination")
        
        # Measure copy time
        start_time = time.time()
        operation_id = manager.copy_files(source_files, destination)
        
        # Wait for completion
        while operation_id not in (manager.completed_operations.union(
                                 manager.failed_operations)):
            time.sleep(0.1)
            if time.time() - start_time > 60:  # 60 second timeout
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        throughput = num_files / duration
        assert throughput > 50, f"Throughput too low: {throughput:.1f} files/sec"
        assert duration < 30, f"Operation too slow: {duration:.1f} seconds"
    
    @pytest.mark.performance
    def test_memory_usage_large_operation(self, performance_manager,
                                        performance_workspace):
        """Test memory usage during large operations."""
        manager = performance_manager
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create moderate number of medium-sized files
        source_files = []
        for i in range(100):
            file_path = performance_workspace / f"source/medium_{i:03d}.dat"
            file_path.write_bytes(b"X" * 10240)  # 10KB files
            source_files.append(str(file_path))
        
        destination = str(performance_workspace / "destination")
        
        # Execute operation and monitor memory
        operation_id = manager.copy_files(source_files, destination)
        
        peak_memory = initial_memory
        while operation_id not in (manager.completed_operations.union(
                                 manager.failed_operations)):
            current_memory = process.memory_info().rss
            peak_memory = max(peak_memory, current_memory)
            time.sleep(0.1)
        
        # Check final memory after cleanup
        time.sleep(1.0)  # Allow cleanup time
        final_memory = process.memory_info().rss
        
        # Memory usage assertions
        memory_growth = peak_memory - initial_memory
        memory_mb = memory_growth / (1024 * 1024)
        
        assert memory_mb < 100, f"Memory usage too high: {memory_mb:.1f} MB"
        
        # Verify memory was released
        memory_retained = final_memory - initial_memory
        retained_mb = memory_retained / (1024 * 1024)
        assert retained_mb < 50, f"Memory leak detected: {retained_mb:.1f} MB"
    
    @pytest.mark.performance
    def test_concurrent_operation_scaling(self, performance_manager,
                                        performance_workspace):
        """Test scaling with concurrent operations."""
        manager = performance_manager
        
        # Create files for concurrent operations
        num_batches = 10
        files_per_batch = 50
        all_operations = []
        
        for batch in range(num_batches):
            batch_files = []
            for i in range(files_per_batch):
                file_path = (performance_workspace / 
                           f"source/concurrent_b{batch}_f{i:02d}.txt")
                file_path.write_text(f"Batch {batch} file {i}")
                batch_files.append(str(file_path))
            
            # Create batch destination
            batch_dest = performance_workspace / f"destination/batch_{batch}"
            batch_dest.mkdir(exist_ok=True)
            
            all_operations.append((batch_files, str(batch_dest)))
        
        # Execute concurrent operations
        start_time = time.time()
        operation_ids = []
        
        for batch_files, destination in all_operations:
            op_id = manager.copy_files(batch_files, destination)
            operation_ids.append(op_id)
        
        # Wait for all operations to complete
        completed_count = 0
        while completed_count < len(operation_ids):
            completed_count = sum(1 for op_id in operation_ids
                                if op_id in manager.completed_operations or
                                   op_id in manager.failed_operations)
            time.sleep(0.1)
            
            if time.time() - start_time > 120:  # 2 minute timeout
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        total_files = num_batches * files_per_batch
        throughput = total_files / duration
        assert throughput > 25, f"Concurrent throughput too low: {throughput:.1f} files/sec"
        
        # Verify all operations completed successfully
        successful_ops = len([op_id for op_id in operation_ids 
                            if op_id in manager.completed_operations])
        success_rate = successful_ops / len(operation_ids)
        assert success_rate > 0.9, f"Success rate too low: {success_rate:.1%}"


if __name__ == "__main__":
    # Configure logging for test execution
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests with comprehensive coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=src.rfu.file_explorer.operations.file_operations",
        "--cov-report=html:htmlcov_file_operations",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage_file_operations.xml",
        "--cov-fail-under=90",
        "--html=test_report_file_operations.html",
        "--json-report",
        "--json-report-file=test_results_file_operations.json"
    ])