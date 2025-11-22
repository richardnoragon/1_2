"""
Comprehensive unit tests for platform_utils.py

Test file generated on: 2025-08-30
Author: GitHub Copilot
Framework: pytest

Tests cover all functions and methods in platform_utils.py with appropriate assertions,
edge cases, and mock data. Includes setup and teardown methods for test data preparation and cleanup.
"""

import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

# Add the src directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.tools.privacy.privacy_tools.core.platform_utils import PlatformUtils

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestPlatformUtils:
    """Test class for PlatformUtils with comprehensive coverage."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test method."""
        # Get the current test name for logging
        test_name = getattr(self, '_testMethodName', 'unknown_test')
        print(f"\nStarting test: {test_name}")
        
        # Setup
        self.test_temp_dir = Path(tempfile.mkdtemp())
        self.test_files = []
        
        yield
        
        # Teardown
        print(f"Completed test: {test_name}")
        
        # Clean up any test files created
        for file_path in self.test_files:
            if file_path.exists():
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                except Exception:
                    pass
        
        # Clean up temp directory
        if self.test_temp_dir.exists():
            try:
                shutil.rmtree(self.test_temp_dir)
            except Exception:
                pass
        
        # Performance tracking
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        if hasattr(self, '_start_memory'):
            memory_delta = (memory_info.rss - self._start_memory) / 1024 / 1024  # MB
            if memory_delta > 1:  # Only report if > 1MB change
                print(f"Slow test detected: {getattr(self, '_test_time', 0):.2f}s, memory delta: {memory_delta:.2f}MB")
    
    def create_test_file(self, content: str = "test content") -> Path:
        """Helper method to create test files."""
        test_file = self.test_temp_dir / f"test_file_{len(self.test_files)}.txt"
        test_file.write_text(content)
        self.test_files.append(test_file)
        return test_file
    
    def create_test_directory(self) -> Path:
        """Helper method to create test directories."""
        test_dir = self.test_temp_dir / f"test_dir_{len(self.test_files)}"
        test_dir.mkdir(exist_ok=True)
        self.test_files.append(test_dir)
        return test_dir

    # Platform Detection Tests
    
    def test_get_platform(self):
        """Test platform detection."""
        result = PlatformUtils.get_platform()
        assert isinstance(result, str)
        assert result in ["windows", "darwin", "linux"]
        
        # Test with mocked platform
        with patch('platform.system', return_value='Windows'):
            assert PlatformUtils.get_platform() == "windows"
        
        with patch('platform.system', return_value='Darwin'):
            assert PlatformUtils.get_platform() == "darwin"
        
        with patch('platform.system', return_value='Linux'):
            assert PlatformUtils.get_platform() == "linux"
    
    def test_is_windows(self):
        """Test Windows platform detection."""
        with patch.object(PlatformUtils, 'get_platform', return_value='windows'):
            assert PlatformUtils.is_windows() is True
        
        with patch.object(PlatformUtils, 'get_platform', return_value='darwin'):
            assert PlatformUtils.is_windows() is False
        
        with patch.object(PlatformUtils, 'get_platform', return_value='linux'):
            assert PlatformUtils.is_windows() is False
    
    def test_is_macos(self):
        """Test macOS platform detection."""
        with patch.object(PlatformUtils, 'get_platform', return_value='darwin'):
            assert PlatformUtils.is_macos() is True
        
        with patch.object(PlatformUtils, 'get_platform', return_value='windows'):
            assert PlatformUtils.is_macos() is False
        
        with patch.object(PlatformUtils, 'get_platform', return_value='linux'):
            assert PlatformUtils.is_macos() is False
    
    def test_is_linux(self):
        """Test Linux platform detection."""
        with patch.object(PlatformUtils, 'get_platform', return_value='linux'):
            assert PlatformUtils.is_linux() is True
        
        with patch.object(PlatformUtils, 'get_platform', return_value='windows'):
            assert PlatformUtils.is_linux() is False
        
        with patch.object(PlatformUtils, 'get_platform', return_value='darwin'):
            assert PlatformUtils.is_linux() is False

    # Directory Path Tests
    
    def test_get_home_directory(self):
        """Test home directory retrieval."""
        result = PlatformUtils.get_home_directory()
        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_dir()
        
        # Test that it returns the actual home directory
        expected = Path.home()
        assert result == expected
    
    @patch.dict(os.environ, {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'})
    def test_get_appdata_directory_windows(self):
        """Test app data directory on Windows."""
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch.object(PlatformUtils, 'is_macos', return_value=False), \
             patch.object(PlatformUtils, 'is_linux', return_value=False):
            
            result = PlatformUtils.get_appdata_directory()
            assert result == Path('C:\\Users\\Test\\AppData\\Roaming')
    
    def test_get_appdata_directory_macos(self):
        """Test app data directory on macOS."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=True), \
             patch.object(PlatformUtils, 'is_linux', return_value=False), \
             patch.object(PlatformUtils, 'get_home_directory', return_value=Path('/Users/test')):
            
            result = PlatformUtils.get_appdata_directory()
            assert result == Path('/Users/test/Library/Application Support')
    
    def test_get_appdata_directory_linux(self):
        """Test app data directory on Linux."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=False), \
             patch.object(PlatformUtils, 'is_linux', return_value=True), \
             patch.object(PlatformUtils, 'get_home_directory', return_value=Path('/home/test')):
            
            result = PlatformUtils.get_appdata_directory()
            assert result == Path('/home/test/.config')
    
    def test_get_appdata_directory_unknown_platform(self):
        """Test app data directory on unknown platform."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=False), \
             patch.object(PlatformUtils, 'is_linux', return_value=False):
            
            result = PlatformUtils.get_appdata_directory()
            assert result is None
    
    @patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'})
    def test_get_local_appdata_directory_windows(self):
        """Test local app data directory on Windows."""
        with patch.object(PlatformUtils, 'is_windows', return_value=True):
            result = PlatformUtils.get_local_appdata_directory()
            assert result == Path('C:\\Users\\Test\\AppData\\Local')
    
    def test_get_local_appdata_directory_non_windows(self):
        """Test local app data directory on non-Windows platforms."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'get_appdata_directory', return_value=Path('/test/path')):
            
            result = PlatformUtils.get_local_appdata_directory()
            assert result == Path('/test/path')
    
    def test_get_temp_directory(self):
        """Test temporary directory retrieval."""
        result = PlatformUtils.get_temp_directory()
        assert isinstance(result, Path)
        # The implementation returns cwd/temp, so test accordingly
        expected = Path.cwd() / "temp"
        assert result == expected
    
    def test_get_trash_directory_windows(self):
        """Test trash directory on Windows."""
        with patch.object(PlatformUtils, 'is_windows', return_value=True):
            result = PlatformUtils.get_trash_directory()
            # Windows returns None due to complex Recycle Bin structure
            assert result is None
    
    def test_get_trash_directory_macos(self):
        """Test trash directory on macOS."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=True), \
             patch.object(PlatformUtils, 'get_home_directory', return_value=Path('/Users/test')):
            
            result = PlatformUtils.get_trash_directory()
            assert result == Path('/Users/test/.Trash')
    
    def test_get_trash_directory_linux_xdg_exists(self):
        """Test trash directory on Linux with XDG directory existing."""
        mock_home = Path('/home/test')
        
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=False), \
             patch.object(PlatformUtils, 'is_linux', return_value=True), \
             patch.object(PlatformUtils, 'get_home_directory', return_value=mock_home):
            
            # Mock the specific path exists method
            with patch.object(Path, 'exists') as mock_exists:
                mock_exists.return_value = True
                
                result = PlatformUtils.get_trash_directory()
                expected = mock_home / '.local' / 'share' / 'Trash'
                assert result == expected
    
    def test_get_trash_directory_linux_fallback(self):
        """Test trash directory on Linux with fallback paths."""
        mock_home = Path('/home/test')
        
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=False), \
             patch.object(PlatformUtils, 'is_linux', return_value=True), \
             patch.object(PlatformUtils, 'get_home_directory', return_value=mock_home):
            
            # Mock Path.exists to return appropriate values
            with patch.object(Path, 'exists') as mock_exists:
                # First call (XDG trash dir) returns False, second call (fallback) returns True
                mock_exists.side_effect = [False, True]
                
                result = PlatformUtils.get_trash_directory()
                assert result == Path('/tmp/.Trash-1000')

    # Path Utility Tests
    
    def test_expand_environment_variables(self):
        """Test environment variable expansion."""
        # Test with mock environment variables
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = PlatformUtils.expand_environment_variables('$TEST_VAR/path')
            # The exact result depends on the platform's variable expansion
            assert isinstance(result, str)
        
        # Test with user home expansion
        result = PlatformUtils.expand_environment_variables('~/test')
        assert isinstance(result, str)
        assert result.startswith(str(Path.home()))
    
    def test_safe_path_join(self):
        """Test safe path joining."""
        result = PlatformUtils.safe_path_join('path1', 'path2', 'path3')
        assert isinstance(result, Path)
        expected = Path('path1') / 'path2' / 'path3'
        assert result == expected
        
        # Test with empty parts
        result = PlatformUtils.safe_path_join()
        assert isinstance(result, Path)
        
        # Test with single part
        result = PlatformUtils.safe_path_join('single')
        assert result == Path('single')

    # Admin/Root Privilege Tests
    
    def test_is_admin_windows_true(self):
        """Test admin check on Windows returning True."""
        mock_ctypes = MagicMock()
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 1
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', mock_ctypes.windll):
            
            result = PlatformUtils.is_admin()
            assert result is True
    
    def test_is_admin_windows_false(self):
        """Test admin check on Windows returning False."""
        mock_ctypes = MagicMock()
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 0
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', mock_ctypes.windll):
            
            result = PlatformUtils.is_admin()
            assert result is False
    
    def test_is_admin_unix_root(self):
        """Test admin check on Unix systems with root privileges."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False):
            # On Windows, os.geteuid doesn't exist, so we'll skip this test
            if hasattr(os, 'geteuid'):
                with patch('os.geteuid', return_value=0):
                    result = PlatformUtils.is_admin()
                    assert result is True
            else:
                # On Windows, this test should be skipped
                pytest.skip("os.geteuid not available on Windows")
    
    def test_is_admin_unix_non_root(self):
        """Test admin check on Unix systems without root privileges."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False):
            # On Windows, os.geteuid doesn't exist, so we'll skip this test
            if hasattr(os, 'geteuid'):
                with patch('os.geteuid', return_value=1000):
                    result = PlatformUtils.is_admin()
                    assert result is False
            else:
                # On Windows, this test should be skipped
                pytest.skip("os.geteuid not available on Windows")
    
    def test_is_admin_exception(self):
        """Test admin check when exception occurs."""
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll') as mock_windll:
            
            # Make ctypes.windll raise an exception
            mock_windll.shell32.IsUserAnAdmin.side_effect = Exception("Test exception")
            
            result = PlatformUtils.is_admin()
            assert result is False
    
    def test_request_admin_privileges_non_windows(self):
        """Test requesting admin privileges on non-Windows systems."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False):
            result = PlatformUtils.request_admin_privileges()
            assert result is False
    
    def test_request_admin_privileges_already_admin(self):
        """Test requesting admin privileges when already admin."""
        mock_ctypes = MagicMock()
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 1
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', mock_ctypes.windll):
            
            result = PlatformUtils.request_admin_privileges()
            assert result is True
    
    def test_request_admin_privileges_elevate(self):
        """Test requesting admin privileges when elevation needed."""
        mock_ctypes = MagicMock()
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 0
        mock_ctypes.windll.shell32.ShellExecuteW.return_value = 1
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', mock_ctypes.windll), \
             patch('sys.executable', 'python.exe'), \
             patch('sys.argv', ['script.py', 'arg1']):
            
            result = PlatformUtils.request_admin_privileges()
            assert result is False  # Returns False after attempting elevation
            mock_ctypes.windll.shell32.ShellExecuteW.assert_called_once()

    # File Security Tests
    
    def test_secure_delete_file_nonexistent(self):
        """Test secure deletion of non-existent file."""
        non_existent_file = self.test_temp_dir / "non_existent.txt"
        result = PlatformUtils.secure_delete_file(non_existent_file)
        assert result is True
    
    def test_secure_delete_file_success(self):
        """Test successful secure file deletion."""
        test_file = self.create_test_file("sensitive data to be securely deleted")
        assert test_file.exists()
        
        result = PlatformUtils.secure_delete_file(test_file, passes=2)
        assert result is True
        assert not test_file.exists()
    
    def test_secure_delete_file_permission_error(self):
        """Test secure deletion with permission error."""
        test_file = self.create_test_file("test content")
        
        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = PlatformUtils.secure_delete_file(test_file)
            assert result is False
    
    def test_secure_delete_file_large_file(self):
        """Test secure deletion of larger file."""
        # Create a larger test file
        large_content = "x" * 16384  # 16KB
        test_file = self.create_test_file(large_content)
        
        result = PlatformUtils.secure_delete_file(test_file, passes=1)
        assert result is True
        assert not test_file.exists()

    # Trash/Recycle Bin Tests
    
    def test_empty_trash_windows_success(self):
        """Test successful trash emptying on Windows."""
        mock_ctypes = MagicMock()
        mock_ctypes.windll.shell32.SHEmptyRecycleBinW.return_value = 0
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', mock_ctypes.windll), \
             patch('ctypes.wintypes'):
            
            result = PlatformUtils.empty_trash()
            assert result is True
    
    def test_empty_trash_windows_failure(self):
        """Test failed trash emptying on Windows."""
        mock_ctypes = MagicMock()
        mock_ctypes.windll.shell32.SHEmptyRecycleBinW.return_value = 1
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', mock_ctypes.windll), \
             patch('ctypes.wintypes'):
            
            result = PlatformUtils.empty_trash()
            assert result is False
    
    def test_empty_trash_macos_success(self):
        """Test successful trash emptying on macOS."""
        # Create a mock trash directory with files
        mock_trash_dir = MagicMock()
        mock_trash_dir.exists.return_value = True
        
        # Mock files in trash
        mock_file1 = MagicMock()
        mock_file1.is_file.return_value = True
        mock_file1.is_dir.return_value = False
        
        mock_dir1 = MagicMock()
        mock_dir1.is_file.return_value = False
        mock_dir1.is_dir.return_value = True
        
        mock_trash_dir.iterdir.return_value = [mock_file1, mock_dir1]
        
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=True), \
             patch.object(PlatformUtils, 'get_trash_directory', return_value=mock_trash_dir), \
             patch.object(PlatformUtils, 'secure_delete_file', return_value=True), \
             patch('shutil.rmtree'):
            
            result = PlatformUtils.empty_trash()
            assert result is True
    
    def test_empty_trash_linux_success(self):
        """Test successful trash emptying on Linux."""
        # Create mock trash directory structure
        mock_trash_dir = MagicMock()
        mock_trash_dir.exists.return_value = True
        
        mock_files_dir = MagicMock()
        mock_files_dir.exists.return_value = True
        mock_info_dir = MagicMock()
        mock_info_dir.exists.return_value = True
        
        # Mock the path operations
        mock_trash_dir.__truediv__ = lambda self, other: mock_files_dir if other == "files" else mock_info_dir
        
        # Mock files in directories
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.is_dir.return_value = False
        mock_files_dir.iterdir.return_value = [mock_file]
        mock_info_dir.iterdir.return_value = [mock_file]
        
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=False), \
             patch.object(PlatformUtils, 'is_linux', return_value=True), \
             patch.object(PlatformUtils, 'get_trash_directory', return_value=mock_trash_dir), \
             patch.object(PlatformUtils, 'secure_delete_file', return_value=True):
            
            result = PlatformUtils.empty_trash()
            assert result is True
    
    def test_empty_trash_no_trash_directory(self):
        """Test trash emptying when no trash directory exists."""
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch.object(PlatformUtils, 'is_macos', return_value=True), \
             patch.object(PlatformUtils, 'get_trash_directory', return_value=None):
            
            result = PlatformUtils.empty_trash()
            assert result is False
    
    def test_empty_trash_exception(self):
        """Test trash emptying when exception occurs."""
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('ctypes.windll', side_effect=Exception("Test exception")):
            
            result = PlatformUtils.empty_trash()
            assert result is False

    # Process Management Tests
    
    def test_get_running_processes_windows_success(self):
        """Test getting running processes on Windows successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '"process1.exe","PID","Session Name","Session#","Mem Usage"\n"process2.exe","1234","Console","1","1,024 K"\n"process3.exe","5678","Console","1","2,048 K"'
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('subprocess.run', return_value=mock_result):
            
            result = PlatformUtils.get_running_processes()
            assert isinstance(result, list)
            assert len(result) == 2  # Excluding header
            assert "process2.exe" in result
            assert "process3.exe" in result
    
    def test_get_running_processes_windows_failure(self):
        """Test getting running processes on Windows with failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('subprocess.run', return_value=mock_result):
            
            result = PlatformUtils.get_running_processes()
            assert result == []
    
    def test_get_running_processes_unix_success(self):
        """Test getting running processes on Unix systems successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "COMMAND\nprocess1\nprocess2\nprocess3"
        
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch('subprocess.run', return_value=mock_result):
            
            result = PlatformUtils.get_running_processes()
            assert isinstance(result, list)
            assert len(result) == 3  # Excluding header
            assert "process1" in result
            assert "process2" in result
            assert "process3" in result
    
    def test_get_running_processes_exception(self):
        """Test getting running processes when exception occurs."""
        with patch('subprocess.run', side_effect=Exception("Test exception")):
            result = PlatformUtils.get_running_processes()
            assert result == []
    
    def test_is_process_running_found(self):
        """Test checking if a process is running and found."""
        with patch.object(PlatformUtils, 'get_running_processes', 
                         return_value=['process1.exe', 'python.exe', 'notepad.exe']):
            
            result = PlatformUtils.is_process_running('python')
            assert result is True
            
            result = PlatformUtils.is_process_running('PYTHON')  # Case insensitive
            assert result is True
    
    def test_is_process_running_not_found(self):
        """Test checking if a process is running and not found."""
        with patch.object(PlatformUtils, 'get_running_processes', 
                         return_value=['process1.exe', 'notepad.exe']):
            
            result = PlatformUtils.is_process_running('python')
            assert result is False
    
    def test_is_process_running_empty_list(self):
        """Test checking if a process is running with empty process list."""
        with patch.object(PlatformUtils, 'get_running_processes', return_value=[]):
            result = PlatformUtils.is_process_running('python')
            assert result is False
    
    def test_kill_process_windows_success(self):
        """Test killing process on Windows successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('subprocess.run', return_value=mock_result):
            
            result = PlatformUtils.kill_process('notepad.exe')
            assert result is True
    
    def test_kill_process_windows_failure(self):
        """Test killing process on Windows with failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        
        with patch.object(PlatformUtils, 'is_windows', return_value=True), \
             patch('subprocess.run', return_value=mock_result):
            
            result = PlatformUtils.kill_process('nonexistent.exe')
            assert result is False
    
    def test_kill_process_unix_success(self):
        """Test killing process on Unix systems successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        with patch.object(PlatformUtils, 'is_windows', return_value=False), \
             patch('subprocess.run', return_value=mock_result):
            
            result = PlatformUtils.kill_process('python')
            assert result is True
    
    def test_kill_process_exception(self):
        """Test killing process when exception occurs."""
        with patch('subprocess.run', side_effect=Exception("Test exception")):
            result = PlatformUtils.kill_process('python')
            assert result is False

    # Integration and Edge Case Tests
    
    def test_platform_constants(self):
        """Test platform constants are properly defined."""
        assert PlatformUtils.WINDOWS == "windows"
        assert PlatformUtils.MACOS == "darwin"
        assert PlatformUtils.LINUX == "linux"
    
    def test_class_methods_are_class_methods(self):
        """Test that all methods are properly decorated as class methods."""
        # This test ensures all public methods are class methods
        methods_to_check = [
            'get_platform', 'is_windows', 'is_macos', 'is_linux',
            'get_home_directory', 'get_appdata_directory', 'get_local_appdata_directory',
            'get_temp_directory', 'get_trash_directory', 'expand_environment_variables',
            'safe_path_join', 'is_admin', 'request_admin_privileges', 'secure_delete_file',
            'empty_trash', 'get_running_processes', 'is_process_running', 'kill_process'
        ]
        
        for method_name in methods_to_check:
            # Get the method from the class, not an instance
            method = getattr(PlatformUtils, method_name)
            # Check if it's callable (which it should be for class methods)
            assert callable(method), f"{method_name} should be callable"
            # For class methods, we can also check that they can be called on the class
            try:
                # This just checks that the method is bound to the class
                assert hasattr(method, '__self__'), f"{method_name} should be bound to the class"
            except AttributeError:
                # Some methods might not have __self__ attribute, but should still be callable
                pass
    
    def test_complex_integration_scenario(self):
        """Test a complex scenario combining multiple methods."""
        # Test a scenario where we check platform, get directories, and handle files
        test_file = self.create_test_file("integration test content")
        
        # This should work regardless of the actual platform
        platform = PlatformUtils.get_platform()
        home_dir = PlatformUtils.get_home_directory()
        
        assert isinstance(platform, str)
        assert isinstance(home_dir, Path)
        assert home_dir.exists()
        
        # Test path operations
        joined_path = PlatformUtils.safe_path_join(str(home_dir), "test", "path")
        assert isinstance(joined_path, Path)
        
        # Test secure deletion
        result = PlatformUtils.secure_delete_file(test_file)
        assert result is True
        assert not test_file.exists()
    
    @pytest.mark.parametrize("platform_name,expected_windows,expected_macos,expected_linux", [
        ("windows", True, False, False),
        ("darwin", False, True, False),
        ("linux", False, False, True),
        ("unknown", False, False, False)
    ])
    def test_platform_detection_parametrized(self, platform_name, expected_windows, expected_macos, expected_linux):
        """Parametrized test for platform detection methods."""
        with patch.object(PlatformUtils, 'get_platform', return_value=platform_name):
            assert PlatformUtils.is_windows() == expected_windows
            assert PlatformUtils.is_macos() == expected_macos
            assert PlatformUtils.is_linux() == expected_linux
    
    def test_edge_case_empty_environment_variables(self):
        """Test behavior with empty or missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            # Test Windows appdata with no environment variables
            with patch.object(PlatformUtils, 'is_windows', return_value=True):
                result = PlatformUtils.get_appdata_directory()
                assert result is None
                
                result = PlatformUtils.get_local_appdata_directory()
                assert result is None
    
    def test_error_handling_in_file_operations(self):
        """Test error handling in various file operations."""
        # Test with a file that doesn't exist but in a directory that requires permissions
        restricted_path = Path("/root/nonexistent.txt") if not PlatformUtils.is_windows() else Path("C:\\Windows\\System32\\nonexistent.txt")
        
        # These should handle errors gracefully
        result = PlatformUtils.secure_delete_file(restricted_path)
        # Should return True for non-existent files
        assert result is True
    
    def test_path_handling_with_special_characters(self):
        """Test path handling with special characters."""
        special_parts = ["test with spaces", "test-with-dashes", "test_with_underscores", "test.with.dots"]
        result = PlatformUtils.safe_path_join(*special_parts)
        
        assert isinstance(result, Path)
        # The path should contain all parts
        path_str = str(result)
        for part in special_parts:
            assert part in path_str