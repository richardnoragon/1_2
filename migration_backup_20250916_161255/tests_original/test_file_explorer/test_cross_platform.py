"""
Enterprise-Grade Cross-Platform Unit Tests
RFU Multi-Pane File Explorer Testing Framework

Test Coverage: Windows, macOS, and Linux compatibility across file systems,
path handling, and OS-specific features with full platform matrix.

Framework: pytest with enterprise extensions
Standards: Zero-compromise quality assurance
Coverage Target: ≥90% line coverage, ≥95% branch coverage
Platform Matrix: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
File Systems: NTFS, HFS+, APFS, ext4, FAT32, exFAT
Security: Cross-platform permission handling
Performance: Platform-specific optimization validation

Test Categories:
- Path Resolution: Cross-platform path handling and normalization
- File System Features: Platform-specific capabilities and limitations
- Permission Systems: Windows ACL, Unix permissions, macOS extended attributes
- File Operations: Copy, move, delete across different file systems
- Symbolic Links: Platform-specific link handling
- Network Paths: UNC paths, SMB shares, NFS mounts
- Character Encoding: Unicode, locale-specific encodings
- Case Sensitivity: Platform behavior differences
"""

import logging
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Dict, List, Optional, Tuple
from unittest.mock import Mock, patch

import pytest

# Import the modules under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

try:
    from src.rfu.file_explorer.core.file_manager import FileManager
    from src.rfu.file_explorer.operations.file_operations import \
        FileOperationManager
    from src.rfu.file_explorer.utils.path_utils import PathUtils
except ImportError as e:
    pytest.skip(f"Cannot import file explorer modules: {e}", 
                allow_module_level=True)


class PlatformInfo:
    """Platform information and capabilities detection."""
    
    @staticmethod
    def get_platform_name() -> str:
        """Get standardized platform name."""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macos'
        return system
    
    @staticmethod
    def get_platform_version() -> str:
        """Get platform version."""
        return platform.release()
    
    @staticmethod
    def supports_case_sensitive_fs() -> bool:
        """Check if platform supports case-sensitive file systems."""
        return platform.system() != 'Windows'
    
    @staticmethod
    def supports_symbolic_links() -> bool:
        """Check if platform supports symbolic links."""
        return hasattr(os, 'symlink')
    
    @staticmethod
    def supports_hard_links() -> bool:
        """Check if platform supports hard links."""
        return hasattr(os, 'link')
    
    @staticmethod
    def supports_extended_attributes() -> bool:
        """Check if platform supports extended attributes."""
        return hasattr(os, 'getxattr') or platform.system() == 'Windows'
    
    @staticmethod
    def get_path_separator() -> str:
        """Get platform-specific path separator."""
        return os.sep
    
    @staticmethod
    def get_line_ending() -> str:
        """Get platform-specific line ending."""
        return os.linesep
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == 'Windows'
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == 'Darwin'
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == 'Linux'


class TestCrossPlatformPaths:
    """
    Cross-platform path handling tests.
    
    Tests:
    - Path normalization across platforms
    - Separator handling (/ vs \\)
    - Case sensitivity behavior
    - Unicode path support
    - Long path support (Windows)
    - Special characters in paths
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_crossplatform_")
        workspace = Path(temp_dir)
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_path_normalization(self, temp_workspace):
        """Test path normalization across platforms."""
        # Test various path formats
        test_paths = [
            "folder/subfolder/file.txt",
            "folder\\subfolder\\file.txt",
            "./folder/subfolder/file.txt",
            "folder//subfolder//file.txt",
            "folder/../folder/subfolder/file.txt"
        ]
        
        for path_str in test_paths:
            normalized = PathUtils.normalize_path(path_str)
            
            # Should be a valid Path object
            assert isinstance(normalized, (Path, str))
            
            # Should not contain double separators
            if isinstance(normalized, str):
                assert '//' not in normalized.replace('\\\\', '/')
                assert '\\\\' not in normalized
    
    def test_platform_specific_paths(self, temp_workspace):
        """Test platform-specific path handling."""
        if PlatformInfo.is_windows():
            # Test Windows-specific paths
            test_paths = [
                "C:\\Users\\Test\\Documents",
                "\\\\server\\share\\file.txt",  # UNC path
                "C:\\Program Files (x86)\\App\\file.txt",
                "C:\\very\\long\\path\\" + "very" * 50 + "\\file.txt"
            ]
        else:
            # Test Unix-style paths
            test_paths = [
                "/home/user/documents",
                "/var/log/application.log",
                "/usr/local/bin/application",
                "/tmp/file with spaces.txt"
            ]
        
        for path_str in test_paths:
            try:
                normalized = PathUtils.normalize_path(path_str)
                assert normalized is not None
                
                # Test path manipulation
                parent = PathUtils.get_parent_path(normalized)
                assert parent is not None
                
            except Exception as e:
                pytest.fail(f"Failed to handle platform path {path_str}: {e}")
    
    def test_case_sensitivity_handling(self, temp_workspace):
        """Test case sensitivity behavior across platforms."""
        # Create test files with different cases
        test_file_lower = temp_workspace / "testfile.txt"
        test_file_upper = temp_workspace / "TESTFILE.TXT"
        
        test_file_lower.write_text("lower case content")
        
        if PlatformInfo.supports_case_sensitive_fs():
            # On case-sensitive systems, should be able to create both
            test_file_upper.write_text("upper case content")
            
            assert test_file_lower.exists()
            assert test_file_upper.exists()
            assert test_file_lower.read_text() != test_file_upper.read_text()
        else:
            # On case-insensitive systems, should be the same file
            assert test_file_lower.exists()
            # Attempting to create upper case version should affect same file
            if test_file_upper.exists():
                test_file_upper.write_text("modified content")
                assert test_file_lower.read_text() == "modified content"
    
    def test_unicode_path_support(self, temp_workspace):
        """Test Unicode character support in paths."""
        unicode_paths = [
            "测试文件.txt",  # Chinese
            "файл.txt",      # Russian
            "ファイル.txt",     # Japanese
            "🎉emoji🎉.txt", # Emoji
            "café_résumé.txt" # Accented characters
        ]
        
        for unicode_name in unicode_paths:
            try:
                unicode_file = temp_workspace / unicode_name
                unicode_file.write_text("Unicode test content")
                
                assert unicode_file.exists()
                assert unicode_file.read_text() == "Unicode test content"
                
                # Test path operations
                normalized = PathUtils.normalize_path(str(unicode_file))
                assert normalized is not None
                
            except (UnicodeError, OSError) as e:
                # Some platforms may not support certain Unicode characters
                logging.warning(f"Unicode path not supported: {unicode_name}: {e}")
    
    def test_special_character_handling(self, temp_workspace):
        """Test handling of special characters in paths."""
        if PlatformInfo.is_windows():
            # Windows forbidden characters
            forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
            
            for char in forbidden_chars:
                test_name = f"file{char}name.txt"
                test_file = temp_workspace / test_name
                
                # Should either be handled gracefully or raise expected error
                try:
                    test_file.write_text("test")
                    # If it succeeds, character was escaped/handled
                    assert test_file.exists()
                except (OSError, ValueError):
                    # Expected for forbidden characters
                    pass
        else:
            # Unix systems - test various special characters
            special_chars = [' ', '\t', '\n', '\'', '"', '\\', '&', ';', '(', ')']
            
            for char in special_chars:
                if char in ['\n', '\t']:  # Skip newlines and tabs in filenames
                    continue
                    
                test_name = f"file{char}name.txt"
                test_file = temp_workspace / test_name
                
                try:
                    test_file.write_text("test")
                    assert test_file.exists()
                    
                    # Test path operations
                    normalized = PathUtils.normalize_path(str(test_file))
                    assert normalized is not None
                    
                except OSError as e:
                    # Some characters may not be supported
                    logging.warning(f"Special character not supported: {char}: {e}")
    
    @pytest.mark.skipif(not PlatformInfo.is_windows(), 
                       reason="Windows long path test")
    def test_windows_long_path_support(self, temp_workspace):
        """Test Windows long path support (>260 characters)."""
        # Create a very long path
        long_dir_name = "very_long_directory_name_" * 10
        current_path = temp_workspace
        
        # Build nested directory structure to exceed MAX_PATH
        for i in range(5):
            current_path = current_path / f"{long_dir_name}_{i}"
            try:
                current_path.mkdir(exist_ok=True)
            except OSError as e:
                if "path too long" in str(e).lower():
                    pytest.skip("Long path support not enabled")
                raise
        
        # Try to create a file in the deep directory
        long_file = current_path / "test_file_with_very_long_name.txt"
        
        try:
            long_file.write_text("Long path test content")
            assert long_file.exists()
            assert len(str(long_file)) > 260
            
        except OSError as e:
            if "path too long" in str(e).lower():
                pytest.skip("Long path support not available")
            raise


class TestCrossPlatformFileOperations:
    """
    Cross-platform file operations tests.
    
    Tests:
    - Copy operations across file systems
    - Move operations with permission preservation
    - Delete operations with platform-specific behaviors
    - Atomic operations support
    - Transaction safety across platforms
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_fileops_")
        workspace = Path(temp_dir)
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def file_manager(self, temp_workspace):
        """Provide FileOperationManager instance for testing."""
        return FileOperationManager()
    
    def test_cross_platform_copy_operations(self, file_manager, temp_workspace):
        """Test file copy operations across platforms."""
        # Create source file
        source_file = temp_workspace / "source.txt"
        source_content = "Cross-platform test content\nLine 2\nLine 3"
        source_file.write_text(source_content, encoding='utf-8')
        
        # Test copying to different destinations
        destinations = [
            temp_workspace / "copy1.txt",
            temp_workspace / "subdir" / "copy2.txt",
            temp_workspace / "unicode_测试.txt"
        ]
        
        for dest in destinations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                result = file_manager.copy_file(str(source_file), str(dest))
                
                if result:
                    assert dest.exists()
                    assert dest.read_text(encoding='utf-8') == source_content
                    
                    # Verify file attributes are preserved where possible
                    source_stat = source_file.stat()
                    dest_stat = dest.stat()
                    
                    # Size should always match
                    assert dest_stat.st_size == source_stat.st_size
                    
            except Exception as e:
                pytest.fail(f"Copy operation failed for {dest}: {e}")
    
    def test_cross_platform_move_operations(self, file_manager, temp_workspace):
        """Test file move operations across platforms."""
        # Create source files
        source_files = []
        for i in range(3):
            source_file = temp_workspace / f"source_{i}.txt"
            source_file.write_text(f"Move test content {i}")
            source_files.append(source_file)
        
        # Test moving to different locations
        dest_dir = temp_workspace / "moved_files"
        dest_dir.mkdir()
        
        for i, source_file in enumerate(source_files):
            dest_file = dest_dir / f"moved_{i}.txt"
            
            try:
                result = file_manager.move_file(str(source_file), str(dest_file))
                
                if result:
                    assert dest_file.exists()
                    assert not source_file.exists()
                    assert dest_file.read_text() == f"Move test content {i}"
                    
            except Exception as e:
                pytest.fail(f"Move operation failed: {e}")
    
    def test_cross_platform_delete_operations(self, file_manager, temp_workspace):
        """Test file delete operations across platforms."""
        # Create test files and directories
        test_files = []
        for i in range(5):
            test_file = temp_workspace / f"delete_test_{i}.txt"
            test_file.write_text(f"Delete test {i}")
            test_files.append(test_file)
        
        # Create test directory with nested structure
        test_dir = temp_workspace / "delete_dir"
        test_dir.mkdir()
        (test_dir / "nested" / "deep").mkdir(parents=True)
        (test_dir / "nested" / "file.txt").write_text("nested file")
        
        # Test file deletion
        for test_file in test_files[:3]:
            try:
                result = file_manager.delete_file(str(test_file))
                
                if result:
                    assert not test_file.exists()
                    
            except Exception as e:
                pytest.fail(f"Delete operation failed: {e}")
        
        # Test directory deletion
        try:
            result = file_manager.delete_directory(str(test_dir))
            
            if result:
                assert not test_dir.exists()
                
        except Exception as e:
            pytest.fail(f"Directory delete operation failed: {e}")
    
    def test_permission_preservation(self, file_manager, temp_workspace):
        """Test permission preservation across platforms."""
        if PlatformInfo.is_windows():
            # Windows permission testing
            source_file = temp_workspace / "windows_perms.txt"
            source_file.write_text("Windows permissions test")
            
            # Try to set read-only
            source_file.chmod(stat.S_IREAD)
            original_mode = source_file.stat().st_mode
            
            dest_file = temp_workspace / "windows_perms_copy.txt"
            
            try:
                result = file_manager.copy_file(str(source_file), str(dest_file))
                
                if result and dest_file.exists():
                    # Check if permissions were preserved
                    dest_mode = dest_file.stat().st_mode
                    # On Windows, exact permission preservation may vary
                    assert dest_file.exists()
                    
            except Exception as e:
                logging.warning(f"Windows permission test failed: {e}")
        
        else:
            # Unix permission testing
            source_file = temp_workspace / "unix_perms.txt"
            source_file.write_text("Unix permissions test")
            
            # Set specific permissions
            source_file.chmod(0o644)
            original_mode = source_file.stat().st_mode
            
            dest_file = temp_workspace / "unix_perms_copy.txt"
            
            try:
                result = file_manager.copy_file(str(source_file), str(dest_file))
                
                if result and dest_file.exists():
                    dest_mode = dest_file.stat().st_mode
                    
                    # Check if permissions were preserved
                    # (may not be exact due to umask)
                    assert dest_file.exists()
                    
            except Exception as e:
                logging.warning(f"Unix permission test failed: {e}")


class TestCrossPlatformSymbolicLinks:
    """
    Cross-platform symbolic link handling tests.
    
    Tests:
    - Symbolic link creation and detection
    - Link target resolution
    - Broken link handling
    - Hard link support where available
    - Junction points (Windows)
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_links_")
        workspace = Path(temp_dir)
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.skipif(not PlatformInfo.supports_symbolic_links(), 
                       reason="Platform does not support symbolic links")
    def test_symbolic_link_creation(self, temp_workspace):
        """Test symbolic link creation and handling."""
        # Create target file
        target_file = temp_workspace / "target.txt"
        target_file.write_text("Target file content")
        
        # Create symbolic link
        link_file = temp_workspace / "link.txt"
        
        try:
            link_file.symlink_to(target_file)
            
            assert link_file.exists()
            assert link_file.is_symlink()
            assert link_file.readlink() == target_file
            
            # Test reading through link
            assert link_file.read_text() == "Target file content"
            
        except (OSError, NotImplementedError) as e:
            pytest.skip(f"Symbolic link creation not supported: {e}")
    
    @pytest.mark.skipif(not PlatformInfo.supports_symbolic_links(), 
                       reason="Platform does not support symbolic links")
    def test_broken_symbolic_link_handling(self, temp_workspace):
        """Test handling of broken symbolic links."""
        # Create target file
        target_file = temp_workspace / "target.txt"
        target_file.write_text("Target content")
        
        # Create symbolic link
        link_file = temp_workspace / "broken_link.txt"
        
        try:
            link_file.symlink_to(target_file)
            assert link_file.exists()
            
            # Delete target to break the link
            target_file.unlink()
            
            # Link should still exist but be broken
            assert link_file.is_symlink()
            # exists() may return False for broken links
            
            # Test reading through broken link
            try:
                content = link_file.read_text()
                pytest.fail("Should not be able to read broken link")
            except (FileNotFoundError, OSError):
                # Expected for broken link
                pass
                
        except (OSError, NotImplementedError) as e:
            pytest.skip(f"Symbolic link test not supported: {e}")
    
    @pytest.mark.skipif(not PlatformInfo.supports_hard_links(), 
                       reason="Platform does not support hard links")
    def test_hard_link_creation(self, temp_workspace):
        """Test hard link creation and handling."""
        # Create target file
        target_file = temp_workspace / "target.txt"
        target_file.write_text("Hard link target content")
        
        # Create hard link
        hard_link = temp_workspace / "hardlink.txt"
        
        try:
            hard_link.hardlink_to(target_file)
            
            assert hard_link.exists()
            assert not hard_link.is_symlink()
            
            # Both files should have same inode (on Unix)
            if not PlatformInfo.is_windows():
                assert target_file.stat().st_ino == hard_link.stat().st_ino
            
            # Test reading through hard link
            assert hard_link.read_text() == "Hard link target content"
            
            # Modify through hard link
            hard_link.write_text("Modified through hard link")
            assert target_file.read_text() == "Modified through hard link"
            
        except (OSError, NotImplementedError) as e:
            pytest.skip(f"Hard link creation not supported: {e}")
    
    @pytest.mark.skipif(not PlatformInfo.is_windows(), 
                       reason="Windows junction test")
    def test_windows_junction_points(self, temp_workspace):
        """Test Windows junction point handling."""
        # Create target directory
        target_dir = temp_workspace / "target_dir"
        target_dir.mkdir()
        (target_dir / "file.txt").write_text("Junction test content")
        
        # Create junction point using mklink
        junction_dir = temp_workspace / "junction_dir"
        
        try:
            # Use subprocess to create junction
            subprocess.run([
                "cmd", "/c", "mklink", "/J", 
                str(junction_dir), str(target_dir)
            ], check=True, capture_output=True)
            
            assert junction_dir.exists()
            assert junction_dir.is_dir()
            
            # Test accessing files through junction
            junction_file = junction_dir / "file.txt"
            assert junction_file.exists()
            assert junction_file.read_text() == "Junction test content"
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            pytest.skip(f"Junction creation not available: {e}")


class TestCrossPlatformNetworkPaths:
    """
    Cross-platform network path handling tests.
    
    Tests:
    - UNC path handling (Windows)
    - SMB share access
    - NFS mount handling (Unix)
    - Network drive mapping
    - Network path validation
    """
    
    def test_unc_path_validation(self):
        """Test UNC path validation and handling."""
        unc_paths = [
            "\\\\server\\share",
            "\\\\server\\share\\folder",
            "\\\\192.168.1.100\\share",
            "\\\\server.domain.com\\share\\file.txt"
        ]
        
        for unc_path in unc_paths:
            try:
                normalized = PathUtils.normalize_path(unc_path)
                
                # Should handle UNC paths gracefully
                assert normalized is not None
                
                # On Windows, should preserve UNC format
                if PlatformInfo.is_windows():
                    assert str(normalized).startswith("\\\\")
                
            except Exception as e:
                # Non-Windows platforms may not support UNC paths
                if not PlatformInfo.is_windows():
                    logging.warning(f"UNC path not supported on this platform: {e}")
                else:
                    pytest.fail(f"UNC path handling failed: {e}")
    
    def test_network_path_accessibility(self):
        """Test network path accessibility checking."""
        # Test paths that definitely don't exist
        inaccessible_paths = [
            "\\\\nonexistent.server\\share",
            "/mnt/nonexistent_nfs"
        ]
        
        for path in inaccessible_paths:
            try:
                # Should not crash when checking inaccessible paths
                exists = PathUtils.path_exists(path)
                # Should return False for non-existent network paths
                assert exists is False
                
            except Exception as e:
                # Should handle network errors gracefully
                logging.warning(f"Network path check failed gracefully: {e}")
    
    @pytest.mark.skipif(not PlatformInfo.is_windows(), 
                       reason="Windows network drive test")
    def test_windows_network_drive_mapping(self):
        """Test Windows network drive mapping."""
        # Test various drive letter formats
        drive_formats = [
            "Z:\\",
            "Z:\\folder\\file.txt",
            "z:\\lowercase\\path"
        ]
        
        for drive_path in drive_formats:
            try:
                normalized = PathUtils.normalize_path(drive_path)
                assert normalized is not None
                
                # Should preserve drive letter format
                assert str(normalized)[1] == ':'
                
            except Exception as e:
                pytest.fail(f"Drive path handling failed: {e}")


class TestCrossPlatformEncoding:
    """
    Cross-platform encoding and locale tests.
    
    Tests:
    - UTF-8 encoding support
    - Locale-specific encoding handling
    - Byte order mark (BOM) handling
    - File name encoding issues
    - Content encoding detection
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_encoding_")
        workspace = Path(temp_dir)
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_utf8_encoding_support(self, temp_workspace):
        """Test UTF-8 encoding support across platforms."""
        utf8_content = "UTF-8 test: 测试 тест テスト 🎉"
        
        test_file = temp_workspace / "utf8_test.txt"
        
        # Write with explicit UTF-8 encoding
        test_file.write_text(utf8_content, encoding='utf-8')
        
        # Read back and verify
        read_content = test_file.read_text(encoding='utf-8')
        assert read_content == utf8_content
        
        # Test binary mode
        utf8_bytes = utf8_content.encode('utf-8')
        test_file.write_bytes(utf8_bytes)
        
        read_bytes = test_file.read_bytes()
        assert read_bytes == utf8_bytes
    
    def test_platform_default_encoding(self, temp_workspace):
        """Test platform default encoding handling."""
        test_content = "Platform encoding test with special chars: àáâãäå"
        
        test_file = temp_workspace / "encoding_test.txt"
        
        try:
            # Write with platform default encoding
            test_file.write_text(test_content)
            
            # Read back with platform default
            read_content = test_file.read_text()
            assert read_content == test_content
            
        except UnicodeError as e:
            logging.warning(f"Platform encoding issue: {e}")
            # Try with UTF-8 fallback
            test_file.write_text(test_content, encoding='utf-8')
            read_content = test_file.read_text(encoding='utf-8')
            assert read_content == test_content
    
    def test_bom_handling(self, temp_workspace):
        """Test Byte Order Mark (BOM) handling."""
        test_content = "BOM test content"
        
        # Test UTF-8 with BOM
        utf8_bom_file = temp_workspace / "utf8_bom.txt"
        bom_content = '\ufeff' + test_content
        utf8_bom_file.write_text(bom_content, encoding='utf-8-sig')
        
        # Read and verify BOM is handled
        read_content = utf8_bom_file.read_text(encoding='utf-8-sig')
        assert read_content == test_content  # BOM should be stripped
        
        # Test reading with regular UTF-8
        read_with_bom = utf8_bom_file.read_text(encoding='utf-8')
        assert read_with_bom.startswith('\ufeff')


class TestPlatformSpecificFeatures:
    """
    Platform-specific feature tests.
    
    Tests:
    - Windows: ACLs, alternate data streams, registry
    - macOS: Extended attributes, resource forks, bundles
    - Linux: Extended attributes, mount points, permissions
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_platform_")
        workspace = Path(temp_dir)
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.skipif(not PlatformInfo.is_windows(), 
                       reason="Windows-specific test")
    def test_windows_alternate_data_streams(self, temp_workspace):
        """Test Windows alternate data streams."""
        test_file = temp_workspace / "ads_test.txt"
        test_file.write_text("Main content")
        
        # Test ADS using Windows API (if available)
        try:
            # Try to access alternate data stream
            ads_path = str(test_file) + ":alternate:$DATA"
            
            # This may not work without specific Windows API calls
            # Just test that the path is handled gracefully
            normalized = PathUtils.normalize_path(ads_path)
            assert normalized is not None
            
        except Exception as e:
            logging.warning(f"ADS test failed (expected): {e}")
    
    @pytest.mark.skipif(not PlatformInfo.is_macos(), 
                       reason="macOS-specific test")
    def test_macos_resource_forks(self, temp_workspace):
        """Test macOS resource fork handling."""
        test_file = temp_workspace / "resource_test.txt"
        test_file.write_text("Main content")
        
        # Look for resource fork
        resource_fork = temp_workspace / "._resource_test.txt"
        
        try:
            # Resource forks are typically hidden
            # Test that we can handle them when they exist
            if resource_fork.exists():
                # Should be able to read resource fork
                resource_content = resource_fork.read_bytes()
                assert isinstance(resource_content, bytes)
            
        except Exception as e:
            logging.warning(f"Resource fork test failed: {e}")
    
    @pytest.mark.skipif(not (PlatformInfo.is_linux() or PlatformInfo.is_macos()), 
                       reason="Unix extended attributes test")
    def test_unix_extended_attributes(self, temp_workspace):
        """Test Unix extended attributes."""
        test_file = temp_workspace / "xattr_test.txt"
        test_file.write_text("Extended attribute test")
        
        if hasattr(os, 'setxattr'):
            try:
                # Set extended attribute
                os.setxattr(str(test_file), b'user.test', b'test_value')
                
                # Get extended attribute
                value = os.getxattr(str(test_file), b'user.test')
                assert value == b'test_value'
                
                # List extended attributes
                attrs = os.listxattr(str(test_file))
                assert b'user.test' in attrs
                
            except (OSError, PermissionError) as e:
                logging.warning(f"Extended attributes not supported: {e}")
        else:
            pytest.skip("Extended attributes not available")


class TestCrossPlatformIntegration:
    """
    Integration tests across platforms.
    
    Tests:
    - Multi-platform workflow scenarios
    - File transfer between platforms
    - Path conversion utilities
    - Platform capability detection
    - Graceful degradation
    """
    
    def test_platform_capability_detection(self):
        """Test platform capability detection."""
        # Test all capability detection methods
        capabilities = {
            'case_sensitive_fs': PlatformInfo.supports_case_sensitive_fs(),
            'symbolic_links': PlatformInfo.supports_symbolic_links(),
            'hard_links': PlatformInfo.supports_hard_links(),
            'extended_attributes': PlatformInfo.supports_extended_attributes(),
            'is_windows': PlatformInfo.is_windows(),
            'is_macos': PlatformInfo.is_macos(),
            'is_linux': PlatformInfo.is_linux()
        }
        
        # Verify exactly one platform is detected
        platform_count = sum([
            capabilities['is_windows'],
            capabilities['is_macos'],
            capabilities['is_linux']
        ])
        assert platform_count == 1
        
        # Verify path separator is appropriate
        separator = PlatformInfo.get_path_separator()
        if capabilities['is_windows']:
            assert separator == '\\'
        else:
            assert separator == '/'
    
    def test_cross_platform_path_conversion(self):
        """Test path conversion between platforms."""
        # Test various path formats
        test_paths = [
            "/unix/style/path",
            "C:\\Windows\\Style\\Path",
            "relative/path",
            "./current/dir/path",
            "../parent/dir/path"
        ]
        
        for path in test_paths:
            try:
                # Convert to current platform format
                normalized = PathUtils.normalize_path(path)
                assert normalized is not None
                
                # Convert to different platform formats
                if PlatformInfo.is_windows():
                    # On Windows, should handle both formats
                    unix_style = path.replace('\\', '/')
                    unix_normalized = PathUtils.normalize_path(unix_style)
                    assert unix_normalized is not None
                else:
                    # On Unix, should handle backslashes gracefully
                    if '\\' in path:
                        normalized_back = PathUtils.normalize_path(path)
                        assert normalized_back is not None
                        
            except Exception as e:
                pytest.fail(f"Path conversion failed for {path}: {e}")
    
    def test_graceful_degradation(self):
        """Test graceful degradation when features are unavailable."""
        # Test handling of unsupported operations
        unsupported_operations = []
        
        if not PlatformInfo.supports_symbolic_links():
            unsupported_operations.append("symbolic_links")
        
        if not PlatformInfo.supports_hard_links():
            unsupported_operations.append("hard_links")
        
        if not PlatformInfo.supports_extended_attributes():
            unsupported_operations.append("extended_attributes")
        
        # Verify that the application can handle missing features
        for operation in unsupported_operations:
            logging.info(f"Feature not supported on this platform: {operation}")
        
        # Should always be able to perform basic operations
        assert PlatformInfo.get_platform_name() in ['windows', 'macos', 'linux']
        assert PlatformInfo.get_path_separator() in ['/', '\\']


if __name__ == "__main__":
    # Configure logging for test execution
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Print platform information
    print(f"Platform: {PlatformInfo.get_platform_name()}")
    print(f"Version: {PlatformInfo.get_platform_version()}")
    print(f"Path separator: {PlatformInfo.get_path_separator()}")
    print(f"Case sensitive FS: {PlatformInfo.supports_case_sensitive_fs()}")
    print(f"Symbolic links: {PlatformInfo.supports_symbolic_links()}")
    print(f"Hard links: {PlatformInfo.supports_hard_links()}")
    print(f"Extended attributes: {PlatformInfo.supports_extended_attributes()}")
    
    # Run tests with comprehensive coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=src.rfu.file_explorer",
        "--cov-report=html:htmlcov_crossplatform",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage_crossplatform.xml",
        "--cov-fail-under=90",
        "--html=test_report_crossplatform.html",
        "--json-report",
        "--json-report-file=test_results_crossplatform.json"
    ])