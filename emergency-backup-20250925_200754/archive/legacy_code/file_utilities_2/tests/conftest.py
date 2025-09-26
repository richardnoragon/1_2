"""
Test Configuration and Fixtures for Size Analyzer Comprehensive Testing Suite

This module provides pytest fixtures, mock objects, and test configuration
for comprehensive testing of the Size Analyzer migration.
"""

import os
import sys
import tempfile
import shutil
import json
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
from file_utilities_2.core.size_analyzer_logging import SizeAnalyzerLogger
from file_utilities_2.integration.hub_connector import HubConnector


class MockHubInstance:
    """Mock hub instance for testing hub integration."""
    
    def __init__(self):
        self.registered_tools = {}
        self.messages = []
        self.events = []
        self.resources = {}
        self.tool_progress = {}
        
    def register_tool(self, tool_name: str, connector):
        """Register a tool with the mock hub."""
        self.registered_tools[tool_name] = connector
        return True
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the mock hub."""
        if tool_name in self.registered_tools:
            del self.registered_tools[tool_name]
    
    def receive_message(self, message):
        """Receive a message from a tool."""
        self.messages.append(message)
    
    def broadcast_event(self, tool_name: str, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all tools."""
        self.events.append({
            'tool_name': tool_name,
            'event_type': event_type,
            'data': data
        })
    
    def request_resource(self, tool_name: str, resource_type: str, requirements: Dict[str, Any]) -> bool:
        """Handle resource requests."""
        # Always grant resources for testing
        self.resources[f"{tool_name}_{resource_type}"] = requirements
        return True
    
    def update_tool_progress(self, tool_name: str, percentage: int, message: str):
        """Update tool progress."""
        self.tool_progress[tool_name] = {
            'percentage': percentage,
            'message': message
        }


class MockFileSystem:
    """Mock file system for controlled testing."""
    
    def __init__(self):
        self.files = {}
        self.directories = set()
        
    def add_file(self, path: str, size: int, content: str = None):
        """Add a mock file."""
        self.files[path] = {
            'size': size,
            'content': content or f"Mock content for {path}",
            'modified': 1640995200  # Fixed timestamp
        }
        # Add parent directories
        parent = os.path.dirname(path)
        while parent and parent != '/':
            self.directories.add(parent)
            parent = os.path.dirname(parent)
    
    def add_directory(self, path: str):
        """Add a mock directory."""
        self.directories.add(path)
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return path in self.files or path in self.directories
    
    def isfile(self, path: str) -> bool:
        """Check if path is a file."""
        return path in self.files
    
    def isdir(self, path: str) -> bool:
        """Check if path is a directory."""
        return path in self.directories
    
    def getsize(self, path: str) -> int:
        """Get file size."""
        return self.files.get(path, {}).get('size', 0)
    
    def listdir(self, path: str) -> List[str]:
        """List directory contents."""
        contents = []
        for file_path in self.files:
            if os.path.dirname(file_path) == path:
                contents.append(os.path.basename(file_path))
        for dir_path in self.directories:
            if os.path.dirname(dir_path) == path:
                contents.append(os.path.basename(dir_path))
        return contents
    
    def walk(self, path: str):
        """Mock os.walk functionality."""
        visited = set()
        
        def _walk(current_path):
            if current_path in visited:
                return
            visited.add(current_path)
            
            dirs = []
            files = []
            
            # Find direct children
            for file_path in self.files:
                if os.path.dirname(file_path) == current_path:
                    files.append(os.path.basename(file_path))
            
            for dir_path in self.directories:
                if os.path.dirname(dir_path) == current_path:
                    dirs.append(os.path.basename(dir_path))
            
            yield current_path, dirs, files
            
            # Recurse into subdirectories
            for dir_name in dirs:
                subdir_path = os.path.join(current_path, dir_name)
                yield from _walk(subdir_path)
        
        yield from _walk(path)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    # Don't quit the app as it might be used by other tests


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_path = tempfile.mkdtemp(prefix="size_analyzer_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_files(temp_dir):
    """Create test files with known content and sizes."""
    files = {}
    
    # Create various test files
    test_data = {
        'empty.txt': b'',
        'small.txt': b'Hello, World!' * 10,
        'medium.txt': b'A' * 1024,  # 1KB
        'large.txt': b'B' * (1024 * 1024),  # 1MB
        'binary.bin': bytes(range(256)) * 100,  # Binary file
        'unicode.txt': 'Hello 世界! 🌍'.encode('utf-8') * 50
    }
    
    for filename, content in test_data.items():
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        files[filename] = {
            'path': file_path,
            'size': len(content),
            'content': content
        }
    
    # Create subdirectory with files
    subdir = os.path.join(temp_dir, 'subdir')
    os.makedirs(subdir)
    
    subfile_path = os.path.join(subdir, 'subfile.txt')
    subfile_content = b'Subdirectory file content'
    with open(subfile_path, 'wb') as f:
        f.write(subfile_content)
    
    files['subdir/subfile.txt'] = {
        'path': subfile_path,
        'size': len(subfile_content),
        'content': subfile_content
    }
    
    return files


@pytest.fixture
def mock_hub():
    """Create mock hub instance for testing."""
    return MockHubInstance()


@pytest.fixture
def mock_file_system():
    """Create mock file system for controlled testing."""
    fs = MockFileSystem()
    
    # Add some default test structure
    fs.add_directory('/test')
    fs.add_directory('/test/subdir')
    fs.add_file('/test/file1.txt', 100)
    fs.add_file('/test/file2.txt', 200)
    fs.add_file('/test/subdir/file3.txt', 300)
    
    return fs


@pytest.fixture
def size_analyzer():
    """Create SizeAnalyzer instance for testing."""
    return SizeAnalyzer()


@pytest.fixture
def size_analyzer_with_hub(mock_hub):
    """Create SizeAnalyzer instance with hub integration."""
    analyzer = SizeAnalyzer()
    analyzer.set_hub_connector(mock_hub)
    return analyzer


@pytest.fixture
def size_analyzer_gui(qapp, mock_hub):
    """Create SizeAnalyzerGUI instance for testing."""
    gui = SizeAnalyzerGUI(hub_instance=mock_hub)
    yield gui
    gui.close()


@pytest.fixture
def size_analyzer_config():
    """Create SizeAnalyzerConfig instance for testing."""
    with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
        config = SizeAnalyzerConfig()
        return config


@pytest.fixture
def size_analyzer_logger():
    """Create SizeAnalyzerLogger instance for testing."""
    with patch('file_utilities_2.core.size_analyzer_logging.LogManager'):
        logger = SizeAnalyzerLogger()
        return logger


@pytest.fixture
def hub_connector():
    """Create HubConnector instance for testing."""
    return HubConnector("Test Tool")


@pytest.fixture
def mock_progress_callback():
    """Create mock progress callback for testing."""
    callback = Mock()
    callback.call_count = 0
    
    def track_calls(*args, **kwargs):
        callback.call_count += 1
        return callback.return_value
    
    callback.side_effect = track_calls
    return callback


@pytest.fixture
def performance_test_data(temp_dir):
    """Create large test data for performance testing."""
    files = {}
    
    # Create files of various sizes for performance testing
    sizes = {
        'tiny': 1024,           # 1KB
        'small': 10 * 1024,     # 10KB
        'medium': 100 * 1024,   # 100KB
        'large': 1024 * 1024,   # 1MB
        'xlarge': 10 * 1024 * 1024  # 10MB
    }
    
    for name, size in sizes.items():
        file_path = os.path.join(temp_dir, f'{name}_file.dat')
        with open(file_path, 'wb') as f:
            # Write in chunks to avoid memory issues
            chunk_size = min(size, 8192)
            written = 0
            while written < size:
                chunk = b'X' * min(chunk_size, size - written)
                f.write(chunk)
                written += len(chunk)
        
        files[name] = {
            'path': file_path,
            'size': size
        }
    
    return files


@pytest.fixture
def stress_test_structure(temp_dir):
    """Create complex directory structure for stress testing."""
    structure = {
        'root': temp_dir,
        'files': [],
        'directories': []
    }
    
    # Create nested directory structure
    for i in range(5):  # 5 levels deep
        level_dir = os.path.join(temp_dir, *[f'level_{j}' for j in range(i + 1)])
        os.makedirs(level_dir, exist_ok=True)
        structure['directories'].append(level_dir)
        
        # Add files at each level
        for j in range(10):  # 10 files per level
            file_path = os.path.join(level_dir, f'file_{j}.txt')
            content = f'Content for level {i}, file {j}\n' * (j + 1)
            with open(file_path, 'w') as f:
                f.write(content)
            structure['files'].append(file_path)
    
    return structure


@pytest.fixture
def mock_os_operations():
    """Mock OS operations for controlled testing."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.isdir') as mock_isdir, \
         patch('os.path.isfile') as mock_isfile, \
         patch('os.path.getsize') as mock_getsize, \
         patch('os.listdir') as mock_listdir, \
         patch('os.walk') as mock_walk, \
         patch('os.stat') as mock_stat:
        
        # Configure default behaviors
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 1024
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        
        # Mock stat result
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat_result.st_mtime = 1640995200
        mock_stat.return_value = mock_stat_result
        
        # Mock walk result
        mock_walk.return_value = [
            ('/test', ['subdir'], ['file1.txt', 'file2.txt']),
            ('/test/subdir', [], ['file3.txt'])
        ]
        
        yield {
            'exists': mock_exists,
            'isdir': mock_isdir,
            'isfile': mock_isfile,
            'getsize': mock_getsize,
            'listdir': mock_listdir,
            'walk': mock_walk,
            'stat': mock_stat
        }


@pytest.fixture
def analysis_results_sample():
    """Sample analysis results for testing."""
    return {
        'path': '/test/directory',
        'total_size': 1024000,
        'file_count': 100,
        'directory_count': 10,
        'files': [
            {
                'name': 'large_file.txt',
                'path': '/test/directory/large_file.txt',
                'size': 500000,
                'extension': '.txt',
                'modified': 1640995200
            },
            {
                'name': 'medium_file.dat',
                'path': '/test/directory/medium_file.dat',
                'size': 250000,
                'extension': '.dat',
                'modified': 1640995200
            }
        ],
        'file_types': {
            '.txt': {
                'count': 50,
                'total_size': 600000,
                'average_size': 12000
            },
            '.dat': {
                'count': 30,
                'total_size': 300000,
                'average_size': 10000
            },
            '.bin': {
                'count': 20,
                'total_size': 124000,
                'average_size': 6200
            }
        },
        'largest_files': [
            {
                'name': 'huge_file.txt',
                'path': '/test/directory/huge_file.txt',
                'size': 500000,
                'extension': '.txt',
                'modified': 1640995200
            }
        ],
        'directory_tree': {
            'name': 'directory',
            'path': '/test/directory',
            'size': 1024000,
            'children': {}
        },
        'performance_metrics': {
            'start_time': '2024-01-01T00:00:00',
            'end_time': '2024-01-01T00:01:00',
            'files_per_second': 100.0,
            'bytes_per_second': 1024000.0,
            'peak_memory_usage': 50000000
        }
    }


# Test utilities
class TestSignalReceiver(QObject):
    """Test utility for receiving and tracking PyQt signals."""
    
    def __init__(self):
        super().__init__()
        self.signals_received = []
        self.signal_counts = {}
    
    def receive_signal(self, *args, **kwargs):
        """Generic signal receiver."""
        signal_data = {
            'args': args,
            'kwargs': kwargs,
            'timestamp': pytest.approx(1640995200, abs=1000000)  # Flexible timestamp
        }
        self.signals_received.append(signal_data)
        
        # Count signals by type
        signal_type = kwargs.get('signal_type', 'unknown')
        self.signal_counts[signal_type] = self.signal_counts.get(signal_type, 0) + 1
    
    def clear(self):
        """Clear received signals."""
        self.signals_received.clear()
        self.signal_counts.clear()
    
    def get_signal_count(self, signal_type: str = None) -> int:
        """Get count of received signals."""
        if signal_type:
            return self.signal_counts.get(signal_type, 0)
        return len(self.signals_received)


def create_test_directory_structure(base_path: str, structure: Dict[str, Any]):
    """Create a test directory structure from a dictionary specification."""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # It's a directory
            os.makedirs(path, exist_ok=True)
            create_test_directory_structure(path, content)
        else:
            # It's a file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(str(content))


def assert_analysis_results_valid(results: Dict[str, Any]):
    """Assert that analysis results have the expected structure and types."""
    required_keys = [
        'path', 'total_size', 'file_count', 'directory_count',
        'files', 'file_types', 'largest_files', 'directory_tree'
    ]
    
    for key in required_keys:
        assert key in results, f"Missing required key: {key}"
    
    assert isinstance(results['total_size'], int)
    assert isinstance(results['file_count'], int)
    assert isinstance(results['directory_count'], int)
    assert isinstance(results['files'], list)
    assert isinstance(results['file_types'], dict)
    assert isinstance(results['largest_files'], list)
    assert isinstance(results['directory_tree'], dict)


def assert_performance_metrics_valid(metrics: Dict[str, Any]):
    """Assert that performance metrics have the expected structure."""
    required_keys = [
        'start_time', 'end_time', 'files_per_second', 'bytes_per_second'
    ]
    
    for key in required_keys:
        assert key in metrics, f"Missing required performance metric: {key}"
    
    assert isinstance(metrics['files_per_second'], (int, float))
    assert isinstance(metrics['bytes_per_second'], (int, float))
    assert metrics['files_per_second'] >= 0
    assert metrics['bytes_per_second'] >= 0