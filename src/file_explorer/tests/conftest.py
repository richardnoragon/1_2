"""
Test Fixtures and Mock Utilities for RFU File Explorer Tests

This module provides common test fixtures, mock utilities, and test data
generators for the comprehensive test suite.

Features:
- Mock filesystem with realistic file structures
- Database fixtures with test data
- GUI test helpers and automation utilities
- Performance measurement tools
- Cross-platform test utilities
- Memory monitoring helpers

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0
"""

import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock

import pytest


class MockFileSystem:
    """Mock filesystem for testing."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.files: Dict[str, Any] = {}
        self.directories: Dict[str, List[str]] = {}
    
    def create_directory_structure(self):
        """Create realistic directory structure."""
        # Directory structure
        directories = [
            "Documents",
            "Documents/Projects",
            "Documents/Projects/Python",
            "Documents/Projects/Web",
            "Documents/Archive",
            "Pictures",
            "Pictures/2023",
            "Pictures/2024",
            "Music",
            "Music/Rock",
            "Music/Classical",
            "Videos",
            "Downloads",
            "Desktop"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.directories[directory] = []
        
        # File structure with realistic content
        files = [
            # Documents
            ("Documents/readme.txt", "This is a comprehensive readme file.\nIt contains project information."),
            ("Documents/notes.md", "# Project Notes\n\n## Overview\nThis project is for testing."),
            ("Documents/config.json", '{"theme": "dark", "language": "en", "auto_save": true}'),
            
            # Python projects
            ("Documents/Projects/Python/main.py", "#!/usr/bin/env python3\nprint('Hello, World!')"),
            ("Documents/Projects/Python/requirements.txt", "pytest>=7.0\nPyQt5>=5.15\nsqlalchemy>=1.4"),
            ("Documents/Projects/Python/config.ini", "[DEFAULT]\ndebug = true\nlog_level = INFO"),
            
            # Web projects
            ("Documents/Projects/Web/index.html", "<!DOCTYPE html>\n<html>\n<head><title>Test</title></head>\n<body>Test</body>\n</html>"),
            ("Documents/Projects/Web/style.css", "body { font-family: Arial, sans-serif; margin: 20px; }"),
            ("Documents/Projects/Web/script.js", "console.log('Web application loaded');"),
            
            # Archive
            ("Documents/Archive/old_project.zip", b"PK\x03\x04fake_zip_data"),
            ("Documents/Archive/backup_2023.tar.gz", b"\x1f\x8b\x08fake_tar_gz_data"),
            
            # Pictures (binary data simulation)
            ("Pictures/2023/vacation.jpg", b"\xff\xd8\xff\xe0fake_jpeg_header"),
            ("Pictures/2023/family.png", b"\x89PNG\r\nfake_png_header"),
            ("Pictures/2024/landscape.tiff", b"IIfake_tiff_header"),
            
            # Music (binary data simulation)
            ("Music/Rock/song1.mp3", b"ID3fake_mp3_data"),
            ("Music/Classical/symphony.flac", b"fLaCfake_flac_data"),
            
            # Videos (binary data simulation)
            ("Videos/tutorial.mp4", b"\x00\x00\x00\x20ftypfake_mp4_data"),
            ("Videos/presentation.avi", b"RIFF\x00\x00\x00\x00AVIfake_avi_data"),
            
            # Downloads
            ("Downloads/installer.exe", b"MZ\x90\x00fake_exe_header"),
            ("Downloads/document.pdf", b"%PDF-1.4fake_pdf_content"),
            ("Downloads/archive.rar", b"Rar!fake_rar_data"),
            
            # Desktop
            ("Desktop/shortcut.lnk", b"L\x00\x00\x00fake_link_data"),
            ("Desktop/todo.txt", "1. Complete file explorer\n2. Add tests\n3. Write documentation")
        ]
        
        for file_path, content in files:
            file_obj = self.base_path / file_path
            if isinstance(content, str):
                file_obj.write_text(content, encoding='utf-8')
            else:
                file_obj.write_bytes(content)
            
            # Add to tracking
            directory = str(Path(file_path).parent)
            if directory in self.directories:
                self.directories[directory].append(Path(file_path).name)
            
            self.files[file_path] = {
                'size': len(content),
                'type': 'text' if isinstance(content, str) else 'binary'
            }
        
        return self.base_path


class DatabaseFixtures:
    """Database test fixtures and utilities."""
    
    @staticmethod
    def create_test_database():
        """Create in-memory test database."""
        try:
            from src.file_explorer.database.schema import DatabaseSchema
            db = DatabaseSchema(":memory:")
            db.initialize()
            return db
        except ImportError:
            return MagicMock()
    
    @staticmethod
    def populate_test_data(database, mock_filesystem: MockFileSystem):
        """Populate database with test data."""
        if isinstance(database, MagicMock):
            return
        
        # Add file metadata
        for file_path, file_info in mock_filesystem.files.items():
            full_path = mock_filesystem.base_path / file_path
            if full_path.exists():
                stat_info = full_path.stat()
                
                database.execute_update(
                    """INSERT INTO files (path, name, size, modified_time, created_time, file_type)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        str(full_path),
                        full_path.name,
                        stat_info.st_size,
                        stat_info.st_mtime,
                        stat_info.st_ctime,
                        file_info['type']
                    )
                )
        
        # Add directory metadata
        for directory in mock_filesystem.directories:
            dir_path = mock_filesystem.base_path / directory
            if dir_path.exists():
                stat_info = dir_path.stat()
                
                database.execute_update(
                    """INSERT INTO directories (path, name, modified_time, created_time, file_count)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        str(dir_path),
                        dir_path.name,
                        stat_info.st_mtime,
                        stat_info.st_ctime,
                        len(list(dir_path.iterdir()))
                    )
                )


class PerformanceMonitor:
    """Performance monitoring utilities for tests."""
    
    def __init__(self):
        self.start_time = None
        self.measurements = {}
    
    def start_measurement(self, name: str):
        """Start timing measurement."""
        self.start_time = time.perf_counter()
        self.measurements[name] = {'start': self.start_time}
    
    def end_measurement(self, name: str):
        """End timing measurement."""
        end_time = time.perf_counter()
        if name in self.measurements:
            self.measurements[name]['end'] = end_time
            self.measurements[name]['duration'] = end_time - self.measurements[name]['start']
        return self.measurements[name]['duration']
    
    def get_measurement(self, name: str) -> float:
        """Get measurement duration."""
        return self.measurements.get(name, {}).get('duration', 0.0)
    
    def assert_performance(self, name: str, max_duration: float):
        """Assert performance meets threshold."""
        duration = self.get_measurement(name)
        assert duration <= max_duration, f"{name} took {duration:.3f}s, expected <= {max_duration:.3f}s"


class MemoryMonitor:
    """Memory monitoring utilities for tests."""
    
    def __init__(self):
        self.initial_memory = None
        self.peak_memory = None
        
    def start_monitoring(self):
        """Start memory monitoring."""
        try:
            import psutil
            process = psutil.Process()
            self.initial_memory = process.memory_info().rss
            self.peak_memory = self.initial_memory
        except ImportError:
            self.initial_memory = 0
            self.peak_memory = 0
    
    def check_memory(self):
        """Check current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            current_memory = process.memory_info().rss
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
            return current_memory
        except ImportError:
            return 0
    
    def get_memory_increase(self) -> int:
        """Get memory increase since start."""
        current = self.check_memory()
        return current - self.initial_memory if self.initial_memory else 0
    
    def assert_memory_limit(self, max_increase_mb: int):
        """Assert memory increase is within limit."""
        increase = self.get_memory_increase()
        increase_mb = increase / (1024 * 1024)
        assert increase_mb <= max_increase_mb, f"Memory increased by {increase_mb:.1f}MB, expected <= {max_increase_mb}MB"


class GUITestHelper:
    """GUI testing utilities."""
    
    def __init__(self):
        self.qt_available = False
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtTest import QTest
            from PyQt5.QtWidgets import QApplication
            self.QTest = QTest
            self.Qt = Qt
            self.QApplication = QApplication
            self.qt_available = True
        except ImportError:
            pass
    
    def click_button(self, button, delay_ms: int = 100):
        """Click button with delay."""
        if not self.qt_available:
            return
        
        self.QTest.mouseClick(button, self.Qt.LeftButton)
        self.QTest.qWait(delay_ms)
    
    def type_text(self, widget, text: str, delay_ms: int = 50):
        """Type text into widget."""
        if not self.qt_available:
            return
        
        widget.setFocus()
        self.QTest.qWait(delay_ms)
        
        for char in text:
            self.QTest.keyClick(widget, char)
    
    def wait_for_condition(self, condition_func, timeout_ms: int = 5000):
        """Wait for condition to become true."""
        if not self.qt_available:
            return True
        
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout_ms:
            if condition_func():
                return True
            self.QTest.qWait(100)
        return False


class CrossPlatformTestHelper:
    """Cross-platform testing utilities."""
    
    @staticmethod
    def get_platform_specific_paths():
        """Get platform-specific test paths."""
        import sys
        
        if sys.platform == "win32":
            return {
                'home': Path.home(),
                'temp': Path(os.environ.get('TEMP', tempfile.gettempdir())),
                'desktop': Path.home() / 'Desktop',
                'documents': Path.home() / 'Documents'
            }
        elif sys.platform == "darwin":
            return {
                'home': Path.home(),
                'temp': Path(tempfile.gettempdir()),
                'desktop': Path.home() / 'Desktop',
                'documents': Path.home() / 'Documents'
            }
        else:  # Linux and other Unix-like
            return {
                'home': Path.home(),
                'temp': Path(tempfile.gettempdir()),
                'desktop': Path.home() / 'Desktop',
                'documents': Path.home() / 'Documents'
            }
    
    @staticmethod
    def create_platform_test_files(base_path: Path):
        """Create platform-specific test files."""
        import sys
        
        if sys.platform == "win32":
            # Windows-specific files
            (base_path / "windows_file.txt").write_text("Windows test file")
            (base_path / "file_with_spaces.txt").write_text("File with spaces")
            
        elif sys.platform == "darwin":
            # macOS-specific files
            (base_path / "macos_file.txt").write_text("macOS test file")
            (base_path / ".DS_Store").write_bytes(b"fake_ds_store_data")
            
        else:
            # Linux-specific files
            (base_path / "linux_file.txt").write_text("Linux test file")
            (base_path / ".hidden_file").write_text("Hidden file content")


# Test Data Generators
class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_large_directory(base_path: Path, num_files: int = 1000, num_dirs: int = 100):
        """Generate large directory structure for performance testing."""
        # Create subdirectories
        for i in range(num_dirs):
            dir_path = base_path / f"subdir_{i:03d}"
            dir_path.mkdir(exist_ok=True)
        
        # Create files
        for i in range(num_files):
            file_path = base_path / f"file_{i:04d}.txt"
            content = f"Test file {i}\n" + "Content line\n" * (i % 10 + 1)
            file_path.write_text(content)
        
        return base_path
    
    @staticmethod
    def generate_mixed_content_directory(base_path: Path):
        """Generate directory with mixed content types."""
        content_types = [
            ("text_files", ".txt", lambda i: f"Text file {i} content"),
            ("images", ".jpg", lambda i: b"fake_image_data_" + str(i).encode()),
            ("documents", ".pdf", lambda i: b"fake_pdf_data_" + str(i).encode()),
            ("archives", ".zip", lambda i: b"fake_zip_data_" + str(i).encode()),
            ("code", ".py", lambda i: f"# Python file {i}\nprint('Hello {i}')"),
        ]
        
        for content_type, extension, generator in content_types:
            type_dir = base_path / content_type
            type_dir.mkdir(exist_ok=True)
            
            for i in range(10):
                file_path = type_dir / f"file_{i:02d}{extension}"
                content = generator(i)
                
                if isinstance(content, str):
                    file_path.write_text(content)
                else:
                    file_path.write_bytes(content)
        
        return base_path
    
    @staticmethod
    def generate_nested_directory_structure(base_path: Path, depth: int = 5, width: int = 3):
        """Generate deeply nested directory structure."""
        def create_level(current_path: Path, current_depth: int):
            if current_depth >= depth:
                return
            
            for i in range(width):
                dir_name = f"level_{current_depth}_dir_{i}"
                dir_path = current_path / dir_name
                dir_path.mkdir(exist_ok=True)
                
                # Add some files at each level
                for j in range(2):
                    file_path = dir_path / f"file_{j}.txt"
                    file_path.write_text(f"Content at depth {current_depth}, file {j}")
                
                # Recurse to next level
                create_level(dir_path, current_depth + 1)
        
        create_level(base_path, 0)
        return base_path


# Pytest Fixtures
@pytest.fixture(scope="session")
def performance_monitor():
    """Performance monitor fixture."""
    return PerformanceMonitor()


@pytest.fixture(scope="session")
def memory_monitor():
    """Memory monitor fixture."""
    monitor = MemoryMonitor()
    monitor.start_monitoring()
    return monitor


@pytest.fixture(scope="session")
def gui_helper():
    """GUI test helper fixture."""
    return GUITestHelper()


@pytest.fixture
def mock_filesystem():
    """Mock filesystem fixture."""
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_fs = MockFileSystem(Path(temp_dir))
        mock_fs.create_directory_structure()
        yield mock_fs


@pytest.fixture
def test_database(mock_filesystem):
    """Test database with mock data."""
    db = DatabaseFixtures.create_test_database()
    DatabaseFixtures.populate_test_data(db, mock_filesystem)
    return db


@pytest.fixture
def large_directory():
    """Large directory for performance testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        TestDataGenerator.generate_large_directory(base_path, 100, 20)  # Smaller for CI
        yield base_path


@pytest.fixture
def mixed_content_directory():
    """Directory with mixed content types."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        TestDataGenerator.generate_mixed_content_directory(base_path)
        yield base_path


@pytest.fixture
def nested_directory():
    """Deeply nested directory structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        TestDataGenerator.generate_nested_directory_structure(base_path, 4, 3)  # Smaller for CI
        yield base_path


@pytest.fixture
def platform_paths():
    """Platform-specific paths."""
    return CrossPlatformTestHelper.get_platform_specific_paths()


if __name__ == '__main__':
    # Test fixture creation
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_fs = MockFileSystem(Path(temp_dir))
        mock_fs.create_directory_structure()
        print(f"Created mock filesystem in: {temp_dir}")
        print(f"Files created: {len(mock_fs.files)}")
        print(f"Directories created: {len(mock_fs.directories)}")