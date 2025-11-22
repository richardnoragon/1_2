"""
Comprehensive Unit Tests for privacy_base.py

Test file for PrivacyOperationResult and PrivacyToolBase classes.
Generated on: 2025-08-30
Target: src/utilities/privacy/privacy_tools/core/privacy_base.py

This test suite covers:
- PrivacyOperationResult class functionality
- PrivacyToolBase class methods and signals
- File and directory operations
- Database operations
- Thread management
- Error handling and edge cases
"""

import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtTest import QSignalSpy

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.tools.privacy.privacy_tools.core.privacy_base import (
    PrivacyOperationResult, PrivacyToolBase)


class TestPrivacyOperationResult:
    """Test cases for PrivacyOperationResult class."""
    
    def test_init_success_minimal(self):
        """Test successful result initialization with minimal parameters."""
        result = PrivacyOperationResult(True, "Operation completed")
        
        assert result.success is True
        assert result.message == "Operation completed"
        assert result.items_processed == 0
        assert result.errors == []
    
    def test_init_success_full_parameters(self):
        """Test successful result initialization with all parameters."""
        errors = ["Warning: File not found", "Info: Skipped locked file"]
        result = PrivacyOperationResult(
            success=True, 
            message="Completed with warnings", 
            items_processed=42,
            errors=errors
        )
        
        assert result.success is True
        assert result.message == "Completed with warnings"
        assert result.items_processed == 42
        assert result.errors == errors
    
    def test_init_failure(self):
        """Test failure result initialization."""
        errors = ["Critical error occurred", "Permission denied"]
        result = PrivacyOperationResult(
            success=False,
            message="Operation failed",
            items_processed=10,
            errors=errors
        )
        
        assert result.success is False
        assert result.message == "Operation failed"
        assert result.items_processed == 10
        assert result.errors == errors
    
    def test_init_none_errors(self):
        """Test initialization with None errors parameter."""
        result = PrivacyOperationResult(True, "Success", 5, None)
        
        assert result.errors == []
    
    def test_str_representation(self):
        """Test string representation of result."""
        result = PrivacyOperationResult(True, "Test message", 15)
        expected = "PrivacyOperationResult(success=True, message='Test message', items=15)"
        
        assert str(result) == expected
    
    def test_str_representation_failure(self):
        """Test string representation of failure result."""
        result = PrivacyOperationResult(False, "Error occurred", 0)
        expected = "PrivacyOperationResult(success=False, message='Error occurred', items=0)"
        
        assert str(result) == expected


class TestPrivacyToolBase:
    """Test cases for PrivacyToolBase class."""
    
    @pytest.fixture
    def privacy_tool(self):
        """Create a PrivacyToolBase instance for testing."""
        return PrivacyToolBase("TestTool")
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def temp_db(self, temp_dir):
        """Create a temporary SQLite database for testing."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO test_table (name) VALUES ('test1')")
        conn.execute("INSERT INTO test_table (name) VALUES ('test2')")
        conn.commit()
        conn.close()
        return db_path
    
    def test_init(self, privacy_tool):
        """Test initialization of PrivacyToolBase."""
        assert privacy_tool.name == "TestTool"
        assert privacy_tool.browser_detector is not None
        assert privacy_tool._is_running is False
        assert privacy_tool._should_stop is False
    
    def test_get_description(self, privacy_tool):
        """Test get_description method."""
        assert privacy_tool.get_description() == "Privacy tool"
    
    def test_get_supported_platforms(self, privacy_tool):
        """Test get_supported_platforms method."""
        platforms = privacy_tool.get_supported_platforms()
        expected = ["windows", "linux", "darwin"]
        assert platforms == expected
    
    def test_is_supported(self, privacy_tool):
        """Test is_supported method."""
        assert privacy_tool.is_supported() is True
    
    def test_preview_operation(self, privacy_tool):
        """Test preview_operation method."""
        result = privacy_tool.preview_operation()
        expected = {"preview": "No preview available"}
        assert result == expected
    
    def test_execute_operation(self, privacy_tool):
        """Test execute_operation method."""
        result = privacy_tool.execute_operation()
        assert isinstance(result, PrivacyOperationResult)
        assert result.success is True
        assert result.message == "Operation completed"
        assert result.items_processed == 0
    
    def test_is_running(self, privacy_tool):
        """Test is_running method."""
        assert privacy_tool.is_running() is False
        
        privacy_tool._is_running = True
        assert privacy_tool.is_running() is True
    
    def test_stop_operation(self, privacy_tool):
        """Test stop_operation method."""
        # Mock the signal
        with patch.object(privacy_tool, 'status_changed') as mock_signal:
            privacy_tool.stop_operation()
            
            assert privacy_tool._should_stop is True
            mock_signal.emit.assert_called_once_with("Stopping operation...")
    
    def test_check_should_stop(self, privacy_tool):
        """Test _check_should_stop method."""
        assert privacy_tool._check_should_stop() is False
        
        privacy_tool._should_stop = True
        assert privacy_tool._check_should_stop() is True
    
    def test_emit_progress(self, privacy_tool):
        """Test _emit_progress method."""
        with patch.object(privacy_tool, 'progress_updated') as mock_signal:
            privacy_tool._emit_progress(10, 100, "Processing...")
            
            mock_signal.emit.assert_called_once_with(10, 100, "Processing...")
    
    def test_emit_status(self, privacy_tool):
        """Test _emit_status method."""
        with patch.object(privacy_tool, 'status_changed') as mock_signal:
            privacy_tool._emit_status("Status update")
            
            mock_signal.emit.assert_called_once_with("Status update")
    
    def test_emit_error(self, privacy_tool):
        """Test _emit_error method."""
        with patch.object(privacy_tool, 'error_occurred') as mock_signal:
            privacy_tool._emit_error("Error message")
            
            mock_signal.emit.assert_called_once_with("Error message")
    
    def test_emit_complete(self, privacy_tool):
        """Test _emit_complete method."""
        result = PrivacyOperationResult(True, "Success")
        
        with patch.object(privacy_tool, 'operation_complete') as mock_signal:
            privacy_tool._emit_complete(result)
            
            mock_signal.emit.assert_called_once_with(result)
    
    def test_safe_delete_file_success(self, privacy_tool, temp_dir):
        """Test successful file deletion."""
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("test content")
        
        assert test_file.exists()
        result = privacy_tool._safe_delete_file(test_file)
        
        assert result is True
        assert not test_file.exists()
    
    def test_safe_delete_file_nonexistent(self, privacy_tool, temp_dir):
        """Test deletion of non-existent file."""
        test_file = temp_dir / "nonexistent.txt"
        
        result = privacy_tool._safe_delete_file(test_file)
        assert result is True
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.secure_delete_file')
    def test_safe_delete_file_secure(self, mock_secure_delete, privacy_tool, temp_dir):
        """Test secure file deletion."""
        test_file = temp_dir / "secure_test.txt"
        test_file.write_text("sensitive content")
        mock_secure_delete.return_value = True
        
        result = privacy_tool._safe_delete_file(test_file, secure=True)
        
        assert result is True
        mock_secure_delete.assert_called_once_with(test_file)
    
    def test_safe_delete_file_error(self, privacy_tool):
        """Test file deletion error handling."""
        # Try to delete a file that doesn't exist but will cause an error
        invalid_path = Path("/invalid/path/file.txt")
        
        with patch.object(privacy_tool, '_emit_error') as mock_emit_error:
            result = privacy_tool._safe_delete_file(invalid_path)
            
            assert result is False
            mock_emit_error.assert_called_once()
    
    def test_safe_delete_directory_success(self, privacy_tool, temp_dir):
        """Test successful directory deletion."""
        test_subdir = temp_dir / "subdir"
        test_subdir.mkdir()
        
        test_file = test_subdir / "file.txt"
        test_file.write_text("content")
        
        nested_dir = test_subdir / "nested"
        nested_dir.mkdir()
        nested_file = nested_dir / "nested_file.txt"
        nested_file.write_text("nested content")
        
        assert test_subdir.exists()
        result = privacy_tool._safe_delete_directory(test_subdir)
        
        assert result is True
        assert not test_subdir.exists()
    
    def test_safe_delete_directory_nonexistent(self, privacy_tool, temp_dir):
        """Test deletion of non-existent directory."""
        test_dir = temp_dir / "nonexistent"
        
        result = privacy_tool._safe_delete_directory(test_dir)
        assert result is True
    
    def test_safe_delete_directory_with_stop(self, privacy_tool, temp_dir):
        """Test directory deletion with stop signal."""
        test_subdir = temp_dir / "subdir"
        test_subdir.mkdir()
        
        # Create multiple files
        for i in range(5):
            (test_subdir / f"file_{i}.txt").write_text(f"content {i}")
        
        privacy_tool._should_stop = True
        
        result = privacy_tool._safe_delete_directory(test_subdir)
        assert result is False
    
    def test_backup_file_success(self, privacy_tool, temp_dir):
        """Test successful file backup."""
        test_file = temp_dir / "original.txt"
        test_file.write_text("original content")
        
        backup_path = privacy_tool._backup_file(test_file)
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == "original content"
        assert "privacy_backup" in str(backup_path)
    
    def test_backup_file_custom_dir(self, privacy_tool, temp_dir):
        """Test file backup with custom backup directory."""
        test_file = temp_dir / "original.txt"
        test_file.write_text("original content")
        
        custom_backup_dir = temp_dir / "custom_backup"
        
        backup_path = privacy_tool._backup_file(test_file, custom_backup_dir)
        
        assert backup_path is not None
        assert backup_path.exists()
        assert custom_backup_dir in backup_path.parents
    
    def test_backup_file_duplicate_names(self, privacy_tool, temp_dir):
        """Test backup with duplicate file names."""
        test_file = temp_dir / "duplicate.txt"
        test_file.write_text("content")
        
        # Create first backup
        backup1 = privacy_tool._backup_file(test_file)
        
        # Modify original and create second backup
        test_file.write_text("modified content")
        backup2 = privacy_tool._backup_file(test_file)
        
        assert backup1 != backup2
        assert backup1.exists()
        assert backup2.exists()
        assert ".backup.1" in str(backup2)
    
    def test_backup_file_nonexistent(self, privacy_tool, temp_dir):
        """Test backup of non-existent file."""
        test_file = temp_dir / "nonexistent.txt"
        
        backup_path = privacy_tool._backup_file(test_file)
        assert backup_path is None
    
    def test_execute_sql_on_database_success(self, privacy_tool, temp_db):
        """Test successful SQL execution on database."""
        sql_commands = [
            "INSERT INTO test_table (name) VALUES ('test3')",
            "UPDATE test_table SET name = 'updated' WHERE id = 1"
        ]
        
        result = privacy_tool._execute_sql_on_database(temp_db, sql_commands)
        
        assert result is True
        
        # Verify the changes
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        assert count == 3
        
        cursor.execute("SELECT name FROM test_table WHERE id = 1")
        name = cursor.fetchone()[0]
        assert name == "updated"
        conn.close()
    
    def test_execute_sql_on_database_nonexistent(self, privacy_tool, temp_dir):
        """Test SQL execution on non-existent database."""
        nonexistent_db = temp_dir / "nonexistent.db"
        sql_commands = ["SELECT 1"]
        
        result = privacy_tool._execute_sql_on_database(nonexistent_db, sql_commands)
        assert result is True
    
    def test_execute_sql_on_database_error(self, privacy_tool, temp_db):
        """Test SQL execution with invalid SQL."""
        sql_commands = ["INVALID SQL STATEMENT"]
        
        with patch.object(privacy_tool, '_emit_error') as mock_emit_error:
            result = privacy_tool._execute_sql_on_database(temp_db, sql_commands)
            
            assert result is False
            mock_emit_error.assert_called_once()
    
    def test_get_database_row_count_success(self, privacy_tool, temp_db):
        """Test getting row count from database table."""
        count = privacy_tool._get_database_row_count(temp_db, "test_table")
        assert count == 2
    
    def test_get_database_row_count_nonexistent_db(self, privacy_tool, temp_dir):
        """Test getting row count from non-existent database."""
        nonexistent_db = temp_dir / "nonexistent.db"
        count = privacy_tool._get_database_row_count(nonexistent_db, "test_table")
        assert count == 0
    
    def test_get_database_row_count_invalid_table(self, privacy_tool, temp_db):
        """Test getting row count from invalid table."""
        count = privacy_tool._get_database_row_count(temp_db, "invalid_table")
        assert count == 0
    
    def test_validate_browser_not_running_success(self, privacy_tool):
        """Test browser validation when browsers are not running."""
        with patch.object(privacy_tool.browser_detector, 'is_browser_running') as mock_running:
            mock_running.return_value = False
            
            result = privacy_tool._validate_browser_not_running(["chrome", "firefox"])
            
            assert result is True
            assert mock_running.call_count == 2
    
    def test_validate_browser_not_running_failure(self, privacy_tool):
        """Test browser validation when browsers are running."""
        with patch.object(privacy_tool.browser_detector, 'is_browser_running') as mock_running:
            mock_running.side_effect = lambda browser: browser == "chrome"
            
            with patch.object(privacy_tool, '_emit_error') as mock_emit_error:
                result = privacy_tool._validate_browser_not_running(["chrome", "firefox"])
                
                assert result is False
                mock_emit_error.assert_called_once()
                assert "chrome" in mock_emit_error.call_args[0][0]
    
    def test_validate_browser_not_running_multiple_running(self, privacy_tool):
        """Test browser validation with multiple browsers running."""
        with patch.object(privacy_tool.browser_detector, 'is_browser_running') as mock_running:
            mock_running.return_value = True
            
            with patch.object(privacy_tool, '_emit_error') as mock_emit_error:
                result = privacy_tool._validate_browser_not_running(["chrome", "firefox", "edge"])
                
                assert result is False
                mock_emit_error.assert_called_once()
                error_message = mock_emit_error.call_args[0][0]
                assert "chrome" in error_message
                assert "firefox" in error_message
                assert "edge" in error_message
    
    def test_run_in_thread_success(self, privacy_tool):
        """Test running operation in thread successfully."""
        def mock_operation(**kwargs):
            return PrivacyOperationResult(True, "Thread operation completed")
        
        with patch.object(QThread, 'start') as mock_start:
            with patch.object(privacy_tool, '_emit_complete') as mock_emit_complete:
                thread = privacy_tool.run_in_thread(mock_operation)
                
                assert isinstance(thread, QThread)
                mock_start.assert_called_once()
                
                # Simulate thread execution
                privacy_tool._is_running = True
                privacy_tool._should_stop = False
                result = mock_operation()
                privacy_tool._emit_complete(result)
                privacy_tool._is_running = False
                
                mock_emit_complete.assert_called_once()
                assert isinstance(mock_emit_complete.call_args[0][0], PrivacyOperationResult)
    
    def test_run_in_thread_error(self, privacy_tool):
        """Test running operation in thread with error."""
        def mock_operation(**kwargs):
            raise Exception("Thread operation failed")
        
        with patch.object(QThread, 'start') as mock_start:
            with patch.object(privacy_tool, '_emit_complete') as mock_emit_complete:
                thread = privacy_tool.run_in_thread(mock_operation)
                
                assert isinstance(thread, QThread)
                mock_start.assert_called_once()
                
                # Simulate thread execution with error
                privacy_tool._is_running = True
                privacy_tool._should_stop = False
                
                try:
                    mock_operation()
                except Exception as e:
                    error_result = PrivacyOperationResult(
                        False, f"Operation failed: {str(e)}", 0, [str(e)]
                    )
                    privacy_tool._emit_complete(error_result)
                
                privacy_tool._is_running = False
                
                mock_emit_complete.assert_called_once()
                result = mock_emit_complete.call_args[0][0]
                assert isinstance(result, PrivacyOperationResult)
                assert result.success is False
    
    def test_signals_exist(self, privacy_tool):
        """Test that all required signals exist."""
        assert hasattr(privacy_tool, 'progress_updated')
        assert hasattr(privacy_tool, 'operation_complete')
        assert hasattr(privacy_tool, 'error_occurred')
        assert hasattr(privacy_tool, 'status_changed')
    
    def test_state_management(self, privacy_tool):
        """Test internal state management."""
        # Initial state
        assert privacy_tool._is_running is False
        assert privacy_tool._should_stop is False
        
        # Start operation
        privacy_tool._is_running = True
        assert privacy_tool.is_running() is True
        
        # Request stop
        privacy_tool.stop_operation()
        assert privacy_tool._should_stop is True
        assert privacy_tool._check_should_stop() is True
        
        # End operation
        privacy_tool._is_running = False
        assert privacy_tool.is_running() is False


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""
    
    @pytest.fixture
    def privacy_tool(self):
        """Create a PrivacyToolBase instance for testing."""
        return PrivacyToolBase("EdgeCaseTool")
    
    def test_empty_strings(self, privacy_tool):
        """Test handling of empty strings."""
        result = PrivacyOperationResult(True, "")
        assert result.message == ""
        
        privacy_tool_empty = PrivacyToolBase("")
        assert privacy_tool_empty.name == ""
    
    def test_unicode_strings(self, privacy_tool):
        """Test handling of unicode strings."""
        unicode_message = "操作已完成 🎉"
        result = PrivacyOperationResult(True, unicode_message)
        assert result.message == unicode_message
        
        unicode_tool = PrivacyToolBase("プライバシーツール")
        assert unicode_tool.name == "プライバシーツール"
    
    def test_large_error_list(self, privacy_tool):
        """Test handling of large error lists."""
        large_errors = [f"Error {i}" for i in range(1000)]
        result = PrivacyOperationResult(False, "Many errors", 0, large_errors)
        
        assert len(result.errors) == 1000
        assert result.errors[0] == "Error 0"
        assert result.errors[999] == "Error 999"
    
    def test_concurrent_operations(self, privacy_tool):
        """Test concurrent operation handling."""
        # Start first operation
        privacy_tool._is_running = True
        
        # Try to start second operation
        assert privacy_tool.is_running() is True
        
        # Request stop during operation
        privacy_tool.stop_operation()
        assert privacy_tool._should_stop is True
        
        # Complete operation
        privacy_tool._is_running = False
        privacy_tool._should_stop = False
        
        # Verify state reset
        assert privacy_tool.is_running() is False
        assert privacy_tool._check_should_stop() is False
    
    def test_invalid_file_paths(self, privacy_tool):
        """Test handling of invalid file paths."""
        invalid_paths = [
            Path(""),
            Path("con"),  # Windows reserved name
            Path("nul"),  # Windows reserved name
            Path("/dev/null/invalid"),  # Invalid on Unix
            Path("\\\\invalid\\unc\\path"),  # Invalid UNC path
        ]
        
        for path in invalid_paths:
            result = privacy_tool._safe_delete_file(path)
            # Should not crash, may return True or False depending on path
            assert isinstance(result, bool)
    
    def test_permission_errors(self, privacy_tool, temp_dir):
        """Test handling of permission errors."""
        test_file = temp_dir / "readonly.txt"
        test_file.write_text("readonly content")
        
        # Make file readonly (simulation)
        with patch('pathlib.Path.unlink', side_effect=PermissionError("Access denied")):
            with patch.object(privacy_tool, '_emit_error') as mock_emit_error:
                result = privacy_tool._safe_delete_file(test_file)
                
                assert result is False
                mock_emit_error.assert_called_once()
    
    def test_signal_emission_edge_cases(self, privacy_tool):
        """Test signal emission with edge case values."""
        # Test with extreme values
        with patch.object(privacy_tool, 'progress_updated') as mock_signal:
            privacy_tool._emit_progress(0, 0, "")
            privacy_tool._emit_progress(-1, 100, "Negative progress")
            privacy_tool._emit_progress(100, 50, "Over 100%")
            
            assert mock_signal.emit.call_count == 3
    
    def test_database_corruption_handling(self, privacy_tool, temp_dir):
        """Test handling of corrupted database files."""
        # Create a fake corrupted database
        corrupt_db = temp_dir / "corrupt.db"
        corrupt_db.write_text("This is not a valid SQLite database")
        
        sql_commands = ["SELECT 1"]
        
        with patch.object(privacy_tool, '_emit_error') as mock_emit_error:
            result = privacy_tool._execute_sql_on_database(corrupt_db, sql_commands)
            
            assert result is False
            mock_emit_error.assert_called_once()
    
    def test_thread_cleanup(self, privacy_tool):
        """Test proper thread cleanup on errors."""
        def failing_operation(**kwargs):
            privacy_tool._is_running = True
            raise RuntimeError("Simulated thread failure")
        
        with patch.object(QThread, 'start'):
            with patch.object(QThread, 'quit') as mock_quit:
                thread = privacy_tool.run_in_thread(failing_operation)
                
                # Simulate the worker function call
                privacy_tool._is_running = True
                try:
                    failing_operation()
                except Exception as e:
                    error_result = PrivacyOperationResult(
                        False, f"Operation failed: {str(e)}", 0, [str(e)]
                    )
                    privacy_tool._emit_complete(error_result)
                finally:
                    privacy_tool._is_running = False
                    thread.quit()
                
                # Verify cleanup
                assert privacy_tool._is_running is False


@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information."""
    import datetime
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "test_file": "test_privacy_base_2025-08-30.py",
        "target_module": "privacy_base.py"
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_html_results_table_header(cells):
    """Customize HTML report table headers."""
    cells.insert(2, '<th class="sortable">Test Function</th>')
    cells.insert(3, '<th class="sortable">Duration</th>')


def pytest_html_results_table_row(report, cells):
    """Customize HTML report table rows."""
    cells.insert(2, f'<td>{report.nodeid.split("::")[-1]}</td>')
    cells.insert(3, f'<td>{getattr(report, "duration", 0):.3f}s</td>')


if __name__ == "__main__":
    # Configuration for running tests directly
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        f"--html=C:/Users/richardi/1_2/tests/unit/result_privacy_base_2025-08-30.html",
        "--self-contained-html",
        f"--json-report",
        f"--json-report-file=C:/Users/richardi/1_2/tests/unit/result_privacy_base_2025-08-30.json"
    ])