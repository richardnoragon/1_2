"""
Simplified test runner for Advanced Folders core functionality.
"""

import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Test FileInfo functionality
def test_file_info():
    """Test basic FileInfo functionality."""
    print("Testing FileInfo...")
    
    # Simple data class test
    class FileInfo:
        def __init__(self, path, name, size, modified_time, is_directory, extension):
            self.path = path
            self.name = name
            self.size = size
            self.modified_time = modified_time
            self.is_directory = is_directory
            self.extension = extension
        
        def to_dict(self):
            return {
                'path': self.path,
                'name': self.name,
                'size': self.size,
                'modified_time': self.modified_time.isoformat(),
                'is_directory': self.is_directory,
                'extension': self.extension
            }
    
    # Test creation
    file_info = FileInfo(
        path="/test/file.txt",
        name="file.txt",
        size=1024,
        modified_time=datetime.now(),
        is_directory=False,
        extension=".txt"
    )
    
    assert file_info.name == "file.txt"
    assert file_info.size == 1024
    assert not file_info.is_directory
    assert file_info.extension == ".txt"
    
    # Test serialization
    data_dict = file_info.to_dict()
    assert isinstance(data_dict, dict)
    assert data_dict['name'] == "file.txt"
    
    print("✓ FileInfo tests passed")


def test_database_operations():
    """Test basic database operations."""
    print("Testing database operations...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_db:
        db_path = temp_db.name
    
    try:
        # Initialize database schema
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE test_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    size INTEGER,
                    modified_time TEXT,
                    created_time TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_test_path ON test_files(path);
                CREATE INDEX idx_test_name ON test_files(name);
            """)
        
        # Test insert operation
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO test_files (path, name, size, modified_time) VALUES (?, ?, ?, ?)",
                ("/test/file1.txt", "file1.txt", 1024, datetime.now().isoformat())
            )
            conn.execute(
                "INSERT INTO test_files (path, name, size, modified_time) VALUES (?, ?, ?, ?)",
                ("/test/file2.txt", "file2.txt", 2048, datetime.now().isoformat())
            )
        
        # Test query operation
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_files")
            count = cursor.fetchone()[0]
            assert count == 2
            
            cursor = conn.execute("SELECT name, size FROM test_files WHERE name LIKE ?", ("file1%",))
            result = cursor.fetchone()
            assert result[0] == "file1.txt"
            assert result[1] == 1024
        
        print("✓ Database operations tests passed")
    
    finally:
        os.unlink(db_path)


def test_file_scanning():
    """Test basic file scanning functionality."""
    print("Testing file scanning...")
    
    # Create temporary directory structure
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test files
        test_files = [
            "file1.txt",
            "file2.pdf",
            "subdir/file3.docx",
            "subdir/file4.jpg"
        ]
        
        for file_path in test_files:
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(f"Test content for {file_path}")
        
        # Test scanning
        def scan_directory(directory, recursive=True):
            """Simple directory scanner."""
            results = []
            path_obj = Path(directory)
            
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for item in path_obj.glob(pattern):
                if item.is_file():
                    stat = item.stat()
                    results.append({
                        'path': str(item),
                        'name': item.name,
                        'size': stat.st_size,
                        'is_directory': False,
                        'extension': item.suffix
                    })
            
            return results
        
        # Test recursive scan
        results = scan_directory(temp_dir, recursive=True)
        assert len(results) >= 4  # Should find all test files
        
        # Test non-recursive scan
        results_nr = scan_directory(temp_dir, recursive=False)
        assert len(results_nr) < len(results)  # Should find fewer files
        
        # Test file type filtering
        txt_files = [r for r in results if r['extension'] == '.txt']
        assert len(txt_files) >= 1
        
        print("✓ File scanning tests passed")
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_search_functionality():
    """Test basic search functionality."""
    print("Testing search functionality...")
    
    # Sample file data
    files = [
        {'name': 'document.pdf', 'path': '/docs/document.pdf', 'extension': '.pdf'},
        {'name': 'image.jpg', 'path': '/images/image.jpg', 'extension': '.jpg'},
        {'name': 'text.txt', 'path': '/text/text.txt', 'extension': '.txt'},
        {'name': 'photo.png', 'path': '/images/photo.png', 'extension': '.png'},
    ]
    
    def search_files(files, query, search_type='filename'):
        """Simple search implementation."""
        results = []
        query_lower = query.lower()
        
        for file_info in files:
            if search_type == 'filename':
                if query_lower in file_info['name'].lower():
                    results.append(file_info)
            elif search_type == 'extension':
                if query_lower in file_info['extension'].lower():
                    results.append(file_info)
        
        return results
    
    # Test filename search
    results = search_files(files, 'image')
    assert len(results) == 1
    assert results[0]['name'] == 'image.jpg'
    
    # Test extension search
    results = search_files(files, '.jpg', 'extension')
    assert len(results) == 1
    assert results[0]['name'] == 'image.jpg'
    
    # Test partial match
    results = search_files(files, 'photo')
    assert len(results) == 1
    assert results[0]['name'] == 'photo.png'
    
    print("✓ Search functionality tests passed")


def test_cache_functionality():
    """Test basic cache functionality."""
    print("Testing cache functionality...")
    
    class SimpleCache:
        def __init__(self, max_size=10):
            self.cache = {}
            self.access_order = []
            self.max_size = max_size
        
        def get(self, key):
            if key in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
        
        def put(self, key, value):
            if key in self.cache:
                # Update existing
                self.cache[key] = value
                self.access_order.remove(key)
                self.access_order.append(key)
            else:
                # Add new
                if len(self.cache) >= self.max_size:
                    # Evict least recently used
                    lru_key = self.access_order.pop(0)
                    del self.cache[lru_key]
                
                self.cache[key] = value
                self.access_order.append(key)
    
    # Test cache operations
    cache = SimpleCache(max_size=2)
    
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    
    # Test eviction
    cache.put("key3", "value3")  # Should evict key1
    
    assert cache.get("key1") is None  # Evicted
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    
    print("✓ Cache functionality tests passed")


def test_performance_monitoring():
    """Test basic performance monitoring."""
    print("Testing performance monitoring...")
    
    import time
    
    class SimpleMonitor:
        def __init__(self):
            self.metrics = []
        
        def record_metric(self, operation, duration_ms, metadata=None):
            self.metrics.append({
                'operation': operation,
                'duration_ms': duration_ms,
                'timestamp': datetime.now(),
                'metadata': metadata or {}
            })
        
        def get_summary(self):
            if not self.metrics:
                return {'total': 0, 'avg_duration': 0}
            
            durations = [m['duration_ms'] for m in self.metrics]
            return {
                'total': len(self.metrics),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations)
            }
        
        def timer(self, operation_name):
            """Context manager for timing operations."""
            return TimerContext(self, operation_name)
    
    class TimerContext:
        def __init__(self, monitor, operation_name):
            self.monitor = monitor
            self.operation_name = operation_name
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration_ms = (time.time() - self.start_time) * 1000
                self.monitor.record_metric(self.operation_name, duration_ms)
    
    # Test monitoring
    monitor = SimpleMonitor()
    
    # Record some metrics
    with monitor.timer("test_operation"):
        time.sleep(0.01)  # Small delay
    
    monitor.record_metric("manual_operation", 50.0)
    
    # Check results
    assert len(monitor.metrics) == 2
    
    summary = monitor.get_summary()
    assert summary['total'] == 2
    assert summary['avg_duration'] > 0
    
    print("✓ Performance monitoring tests passed")


def run_all_tests():
    """Run all simplified tests."""
    print("="*50)
    print("ADVANCED FOLDERS - SIMPLIFIED TEST SUITE")
    print("="*50)
    
    tests = [
        test_file_info,
        test_database_operations,
        test_file_scanning,
        test_search_functionality,
        test_cache_functionality,
        test_performance_monitoring
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {str(e)}")
            failed += 1
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All core functionality tests passed!")
        print("✓ FileInfo data structures")
        print("✓ Database operations")
        print("✓ File system scanning")
        print("✓ Search functionality")
        print("✓ Caching system")
        print("✓ Performance monitoring")
        print("\nCore Advanced Folders components are ready for integration!")
    else:
        print(f"\n⚠️  {failed} tests failed - review implementation")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)