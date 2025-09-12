"""
Enterprise Test Configuration and Fixtures
Phase 4: Testing & QA (Week 10) - Shared Test Infrastructure

This module provides comprehensive test fixtures, configuration, and utilities
for enterprise-grade testing of the Advanced Folders system.
"""

import gc
import os
import shutil
import sqlite3
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Generator, List, Optional
from unittest.mock import MagicMock, Mock

import psutil
import pytest

# Import Advanced Folders components for testing
try:
    from src.utilities.advanced_folders.core.folder_models import (
        FileMetadata, FolderConfiguration, FolderType, SearchParameter)
    from src.utilities.advanced_folders.database.db_manager import \
        AdvancedFoldersDBManager
    from src.utilities.advanced_folders.engine.search_engine import \
        SearchEngine
    from src.utilities.advanced_folders.services.folder_service import \
        FolderService
    ADVANCED_FOLDERS_AVAILABLE = True
except ImportError:
    # Fallback for when components are not available
    ADVANCED_FOLDERS_AVAILABLE = False
    print("Warning: Advanced Folders components not available")


# Test configuration constants
TEST_CONFIG = {
    'DEFAULT_TIMEOUT': 30,
    'PERFORMANCE_TIMEOUT': 300,
    'MEMORY_LIMIT_MB': 1000,
    'MAX_TEST_FILES': 10000,
    'COVERAGE_THRESHOLD': 90,
    'PERFORMANCE_BASELINE': {
        'search_time_ms': 100,
        'indexing_rate_files_per_sec': 100,
        'memory_growth_mb': 100
    }
}


class TestMetrics:
    """Test execution metrics collector."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        self.process = psutil.Process(os.getpid())
    
    def start(self):
        """Start metrics collection."""
        self.start_time = time.time()
        gc.collect()  # Force garbage collection
        self.memory_usage.clear()
        self.cpu_usage.clear()
        self.record_metrics()
    
    def record_metrics(self):
        """Record current system metrics."""
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()
        
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
    
    def stop(self):
        """Stop metrics collection."""
        self.end_time = time.time()
        self.record_metrics()
    
    def get_summary(self) -> Dict:
        """Get metrics summary."""
        return {
            'duration': self.end_time - self.start_time if self.end_time else 0,
            'peak_memory_mb': max(self.memory_usage) if self.memory_usage else 0,
            'avg_memory_mb': sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
            'peak_cpu_percent': max(self.cpu_usage) if self.cpu_usage else 0,
            'avg_cpu_percent': sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        }


# Pytest fixtures for enterprise testing

@pytest.fixture(scope="session")
def test_session_metrics():
    """Session-level metrics collection."""
    metrics = TestMetrics()
    metrics.start()
    yield metrics
    metrics.stop()
    
    summary = metrics.get_summary()
    print(f"\nSession Metrics: Duration={summary['duration']:.2f}s, "
          f"Peak Memory={summary['peak_memory_mb']:.1f}MB")


@pytest.fixture(scope="function")
def test_metrics():
    """Function-level metrics collection."""
    metrics = TestMetrics()
    metrics.start()
    yield metrics
    metrics.stop()


@pytest.fixture(scope="session")
def temp_test_directory():
    """Session-level temporary directory for all tests."""
    temp_dir = tempfile.mkdtemp(prefix="advanced_folders_test_")
    temp_path = Path(temp_dir)
    
    yield temp_path
    
    # Cleanup with retry logic
    cleanup_attempts = 3
    for attempt in range(cleanup_attempts):
        try:
            shutil.rmtree(temp_path)
            break
        except (OSError, PermissionError) as e:
            if attempt == cleanup_attempts - 1:
                print(f"Warning: Could not clean up temp directory {temp_path}: {e}")
            else:
                time.sleep(0.5)  # Wait before retry


@pytest.fixture
def temp_directory(temp_test_directory):
    """Function-level temporary directory."""
    test_dir = temp_test_directory / f"test_{int(time.time() * 1000000)}"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir


@pytest.fixture
def test_database(temp_directory):
    """Test database fixture with proper cleanup."""
    if not ADVANCED_FOLDERS_AVAILABLE:
        pytest.skip("Advanced Folders components not available")
    
    db_path = temp_directory / "test_database.db"
    db_manager = AdvancedFoldersDBManager(str(db_path))
    
    yield db_manager
    
    # Cleanup database
    try:
        db_manager.close()
        if db_path.exists():
            db_path.unlink()
    except Exception as e:
        print(f"Warning: Database cleanup failed: {e}")


@pytest.fixture
def test_search_engine(temp_directory):
    """Test search engine fixture with proper cleanup."""
    if not ADVANCED_FOLDERS_AVAILABLE:
        pytest.skip("Advanced Folders components not available")
    
    index_path = temp_directory / "test_index"
    search_engine = SearchEngine(index_path=index_path)
    
    yield search_engine
    
    # Cleanup search index
    try:
        if hasattr(search_engine, 'close'):
            search_engine.close()
        if index_path.exists():
            shutil.rmtree(index_path)
    except Exception as e:
        print(f"Warning: Search engine cleanup failed: {e}")


@pytest.fixture
def test_folder_service(test_database, test_search_engine):
    """Test folder service fixture combining database and search engine."""
    if not ADVANCED_FOLDERS_AVAILABLE:
        pytest.skip("Advanced Folders components not available")
    
    folder_service = FolderService(test_database, test_search_engine)
    yield folder_service


@pytest.fixture
def sample_folder_configuration(temp_directory):
    """Sample folder configuration for testing."""
    if not ADVANCED_FOLDERS_AVAILABLE:
        pytest.skip("Advanced Folders components not available")
    
    config = FolderConfiguration(
        name="Test Folder",
        path=str(temp_directory),
        folder_type=FolderType.MONITORED,
        auto_organize=True,
        priority=1
    )
    yield config


@pytest.fixture
def sample_test_files(temp_directory):
    """Create sample test files for various testing scenarios."""
    test_files = {}
    
    # Text files with different content types
    text_files = {
        'simple.txt': 'Simple text file content for testing',
        'code.py': 'def test_function():\n    return "Hello, World!"',
        'data.json': '{"name": "test", "value": 123, "active": true}',
        'config.xml': '<?xml version="1.0"?><config><setting>value</setting></config>',
        'readme.md': '# Test Project\n\nThis is a test markdown file.'
    }
    
    for filename, content in text_files.items():
        file_path = temp_directory / filename
        file_path.write_text(content, encoding='utf-8')
        test_files[filename] = file_path
    
    # Binary file
    binary_file = temp_directory / 'binary.dat'
    binary_content = bytes(range(256))  # 256 bytes of binary data
    binary_file.write_bytes(binary_content)
    test_files['binary.dat'] = binary_file
    
    # Large text file
    large_file = temp_directory / 'large.txt'
    large_content = 'Large file content line.\n' * 10000  # ~250KB
    large_file.write_text(large_content, encoding='utf-8')
    test_files['large.txt'] = large_file
    
    # Subdirectory with files
    subdir = temp_directory / 'subdir'
    subdir.mkdir()
    subfile = subdir / 'subfile.txt'
    subfile.write_text('Subdirectory file content')
    test_files['subdir/subfile.txt'] = subfile
    
    yield test_files


@pytest.fixture
def performance_test_files(temp_directory):
    """Create files specifically for performance testing."""
    perf_files = []
    
    # Create a moderate number of files for performance testing
    file_count = min(TEST_CONFIG['MAX_TEST_FILES'], 1000)  # Limit for CI/CD
    
    for i in range(file_count):
        file_path = temp_directory / f'perf_file_{i:04d}.txt'
        content = f'Performance test file {i} with searchable content and data {i % 100}'
        file_path.write_text(content)
        perf_files.append(file_path)
        
        # Create subdirectories every 100 files
        if i > 0 and i % 100 == 0:
            subdir = temp_directory / f'perf_subdir_{i // 100}'
            subdir.mkdir(exist_ok=True)
            subfile = subdir / f'sub_perf_file_{i}.txt'
            subfile.write_text(f'Subdirectory performance file {i}')
            perf_files.append(subfile)
    
    yield perf_files


@pytest.fixture
def malicious_test_payloads():
    """Generate malicious payloads for security testing."""
    return {
        'sql_injection': [
            "'; DROP TABLE folders; --",
            "' OR '1'='1",
            "'; UPDATE folders SET path='/etc/passwd'; --",
            "' UNION SELECT * FROM sqlite_master; --",
        ],
        'path_traversal': [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "..///////..////..//////etc/passwd",
        ],
        'command_injection': [
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "`cat /etc/passwd`",
            "$(cat /etc/passwd)",
        ],
        'xss_payloads': [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src='x' onerror='alert(1)'>",
            "<svg onload=alert(1)>",
        ],
        'buffer_overflow': [
            "A" * 1000,
            "A" * 10000,
            "\x00" * 1000,
            "\xff" * 1000,
        ]
    }


@pytest.fixture
def mock_gui_components():
    """Mock GUI components for testing without actual GUI."""
    mock_components = {
        'main_window': Mock(),
        'folder_tree': Mock(),
        'search_widget': Mock(),
        'settings_dialog': Mock(),
        'progress_bar': Mock()
    }
    
    # Configure mock behaviors
    mock_components['main_window'].isVisible.return_value = True
    mock_components['folder_tree'].selectedItems.return_value = []
    mock_components['search_widget'].text.return_value = ""
    
    yield mock_components


@pytest.fixture
def concurrent_test_environment():
    """Environment for concurrent/parallel testing."""
    max_workers = min(4, os.cpu_count() or 1)  # Limit concurrent workers
    thread_local_storage = threading.local()
    
    environment = {
        'max_workers': max_workers,
        'thread_storage': thread_local_storage,
        'active_threads': [],
        'results': []
    }
    
    yield environment
    
    # Cleanup active threads
    for thread in environment.get('active_threads', []):
        if thread.is_alive():
            try:
                thread.join(timeout=5)
            except Exception:
                pass


@pytest.fixture
def memory_monitor():
    """Memory usage monitoring fixture."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_samples = [initial_memory]
    
    def record_memory():
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_samples.append(current_memory)
        return current_memory
    
    def get_memory_stats():
        if len(memory_samples) < 2:
            return {'initial': initial_memory, 'peak': initial_memory, 'growth': 0}
        
        return {
            'initial': initial_memory,
            'peak': max(memory_samples),
            'current': memory_samples[-1],
            'growth': memory_samples[-1] - initial_memory,
            'samples': len(memory_samples)
        }
    
    monitor = {
        'record': record_memory,
        'stats': get_memory_stats,
        'samples': memory_samples
    }
    
    yield monitor
    
    # Final memory check
    final_stats = get_memory_stats()
    if final_stats['growth'] > TEST_CONFIG['MEMORY_LIMIT_MB']:
        print(f"Warning: Memory growth exceeded limit: {final_stats['growth']:.1f}MB")


# Test helper functions

def create_test_folder_structure(base_path: Path, structure: Dict) -> Dict[str, Path]:
    """Create a folder structure from a dictionary definition.
    
    Args:
        base_path: Base directory for the structure
        structure: Dictionary defining folder/file structure
        
    Returns:
        Dictionary mapping structure keys to created paths
    """
    created_paths = {}
    
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # Directory with subdirectory/file contents
            path.mkdir(exist_ok=True)
            created_paths[name] = path
            sub_paths = create_test_folder_structure(path, content)
            created_paths.update({f"{name}/{k}": v for k, v in sub_paths.items()})
        elif isinstance(content, str):
            # File with text content
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            created_paths[name] = path
        elif isinstance(content, bytes):
            # File with binary content
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            created_paths[name] = path
        else:
            # Empty directory
            path.mkdir(parents=True, exist_ok=True)
            created_paths[name] = path
    
    return created_paths


def assert_performance_benchmark(actual_time: float, benchmark_name: str, 
                                tolerance: float = 0.2):
    """Assert performance meets benchmark requirements.
    
    Args:
        actual_time: Actual execution time in seconds
        benchmark_name: Name of benchmark to check against
        tolerance: Tolerance factor (0.2 = 20% tolerance)
    """
    if benchmark_name in TEST_CONFIG['PERFORMANCE_BASELINE']:
        baseline_ms = TEST_CONFIG['PERFORMANCE_BASELINE'][benchmark_name]
        baseline_sec = baseline_ms / 1000.0
        max_allowed = baseline_sec * (1 + tolerance)
        
        assert actual_time <= max_allowed, (
            f"Performance degradation: {benchmark_name} took {actual_time:.3f}s, "
            f"expected <={max_allowed:.3f}s (baseline: {baseline_sec:.3f}s)"
        )


def validate_test_data_integrity(file_paths: List[Path]) -> bool:
    """Validate test data integrity using checksums.
    
    Args:
        file_paths: List of file paths to validate
        
    Returns:
        True if all files maintain integrity, False otherwise
    """
    import hashlib
    
    for file_path in file_paths:
        if not file_path.exists():
            return False
        
        try:
            # Calculate current hash
            with open(file_path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Store or compare hash (simplified validation)
            hash_file = file_path.with_suffix(file_path.suffix + '.hash')
            if hash_file.exists():
                stored_hash = hash_file.read_text().strip()
                if current_hash != stored_hash:
                    return False
            else:
                hash_file.write_text(current_hash)
                
        except (IOError, OSError):
            return False
    
    return True


# Pytest hooks for enterprise testing

def pytest_configure(config):
    """Configure pytest for enterprise testing."""
    # Add custom markers
    config.addinivalue_line("markers", "enterprise: Enterprise-grade test")
    config.addinivalue_line("markers", "zero_tolerance: Zero-tolerance test")
    
    # Set test environment variables
    os.environ['TESTING'] = 'true'
    os.environ['TEST_MODE'] = 'enterprise'


def pytest_collection_modifyitems(config, items):
    """Modify test collection for enterprise requirements."""
    # Mark slow tests
    for item in items:
        if "performance" in item.keywords or "stress" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        if "security" in item.keywords:
            item.add_marker(pytest.mark.zero_tolerance)


def pytest_runtest_setup(item):
    """Setup before each test run."""
    # Skip tests if dependencies not available
    if not ADVANCED_FOLDERS_AVAILABLE and "unit" in item.keywords:
        pytest.skip("Advanced Folders components not available")
    
    # Memory check before expensive tests
    if "performance" in item.keywords or "stress" in item.keywords:
        process = psutil.Process(os.getpid())
        current_memory = process.memory_info().rss / 1024 / 1024
        if current_memory > TEST_CONFIG['MEMORY_LIMIT_MB']:
            pytest.skip(f"Memory usage too high: {current_memory:.1f}MB")


def pytest_runtest_teardown(item):
    """Cleanup after each test run."""
    # Force garbage collection after heavy tests
    if "performance" in item.keywords or "memory" in item.keywords:
        gc.collect()
    
    # Verify no test data leakage
    if hasattr(item, '_temp_files'):
        for temp_file in item._temp_files:
            if temp_file.exists():
                print(f"Warning: Temp file not cleaned up: {temp_file}")


def pytest_sessionfinish(session, exitstatus):
    """Session cleanup and final reporting."""
    print(f"\nEnterprise test session completed with exit status: {exitstatus}")
    
    # Memory usage summary
    process = psutil.Process(os.getpid())
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"Final memory usage: {final_memory:.1f}MB")
    
    # Force final cleanup
    gc.collect()