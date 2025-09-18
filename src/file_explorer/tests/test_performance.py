"""
Performance Tests for RFU File Explorer
Tests performance characteristics and stress scenarios.

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0
"""

import gc
import time
from pathlib import Path

import pytest


class TestPerformanceThresholds:
    """Performance threshold constants."""
    
    MAX_STARTUP_TIME = 5.0  # seconds
    MAX_CACHE_ACCESS_TIME = 0.1  # seconds
    MAX_DIRECTORY_LOAD_TIME = 3.0  # seconds
    MAX_MEMORY_INCREASE_MB = 100  # MB


class TestCachePerformance:
    """Test cache system performance."""
    
    def test_cache_put_performance(self, test_database, performance_monitor):
        """Test cache put operation performance."""
        try:
            from src.file_explorer.database.cache_manager import \
                CacheManager
        except ImportError:
            pytest.skip("Cache manager not available")
        
        cache = CacheManager(test_database, max_cache_size=10000)
        
        performance_monitor.start_measurement("cache_put_1k")
        
        # Put 1000 items
        for i in range(1000):
            cache.put(f"perf_key_{i}", {
                "index": i,
                "data": f"value_{i}",
                "content": "x" * 100  # 100 chars per item
            })
        
        duration = performance_monitor.end_measurement("cache_put_1k")
        
        # Should put 1000 items quickly
        assert duration < 2.0
        print(f"Cache put 1000 items in {duration:.3f}s")
    
    def test_cache_get_performance(self, test_database, performance_monitor):
        """Test cache get operation performance."""
        try:
            from src.file_explorer.database.cache_manager import \
                CacheManager
        except ImportError:
            pytest.skip("Cache manager not available")
        
        cache = CacheManager(test_database, max_cache_size=10000)
        
        # Populate cache
        for i in range(1000):
            cache.put(f"get_perf_key_{i}", {"index": i})
        
        performance_monitor.start_measurement("cache_get_1k")
        
        # Get 1000 items
        for i in range(1000):
            cache.get(f"get_perf_key_{i}")
        
        duration = performance_monitor.end_measurement("cache_get_1k")
        
        # Should get 1000 items very quickly
        assert duration < TestPerformanceThresholds.MAX_CACHE_ACCESS_TIME
        print(f"Cache get 1000 items in {duration:.3f}s")
    
    def test_cache_large_dataset_performance(self, test_database, performance_monitor):
        """Test cache performance with large dataset."""
        try:
            from src.file_explorer.database.cache_manager import \
                CacheManager
        except ImportError:
            pytest.skip("Cache manager not available")
        
        cache = CacheManager(test_database, max_cache_size=50000)
        
        # Large dataset test
        num_items = 10000
        
        performance_monitor.start_measurement("cache_large_put")
        
        for i in range(num_items):
            large_data = {
                "index": i,
                "content": f"Large content item {i} " * 10,  # ~200 bytes
                "metadata": {"size": i * 100, "type": "test"}
            }
            cache.put(f"large_key_{i}", large_data)
        
        put_duration = performance_monitor.end_measurement("cache_large_put")
        
        # Sample get performance
        performance_monitor.start_measurement("cache_large_get_sample")
        
        for i in range(0, num_items, 100):  # Sample every 100th item
            cache.get(f"large_key_{i}")
        
        get_duration = performance_monitor.end_measurement("cache_large_get_sample")
        
        # Performance assertions
        assert put_duration < 10.0  # 10k items in 10 seconds
        assert get_duration < 1.0   # 100 samples in 1 second
        
        print(f"Large dataset: put {num_items} items in {put_duration:.3f}s")
        print(f"Large dataset: get sample in {get_duration:.3f}s")


class TestDirectoryWatcherPerformance:
    """Test directory watcher performance."""
    
    def test_watcher_startup_performance(self, mock_filesystem, performance_monitor):
        """Test directory watcher startup time."""
        try:
            from src.file_explorer.utils.directory_watcher import \
                DirectoryWatcher
        except ImportError:
            pytest.skip("Directory watcher not available")
        
        watcher = DirectoryWatcher()
        
        performance_monitor.start_measurement("watcher_startup")
        
        watcher.add_watch_path(str(mock_filesystem.base_path))
        watcher.start_monitoring()
        
        startup_duration = performance_monitor.end_measurement("watcher_startup")
        
        assert startup_duration < 2.0
        print(f"Watcher startup in {startup_duration:.3f}s")
        
        watcher.cleanup()
    
    def test_watcher_many_files_performance(self, large_directory, performance_monitor):
        """Test watcher performance with many files."""
        try:
            from src.file_explorer.utils.directory_watcher import \
                DirectoryWatcher
        except ImportError:
            pytest.skip("Directory watcher not available")
        
        watcher = DirectoryWatcher()
        
        performance_monitor.start_measurement("watcher_large_dir")
        
        watcher.add_watch_path(str(large_directory))
        watcher.start_monitoring()
        
        # Wait a bit for initial scan
        time.sleep(0.5)
        
        setup_duration = performance_monitor.end_measurement("watcher_large_dir")
        
        assert setup_duration < 3.0
        print(f"Watcher large directory setup in {setup_duration:.3f}s")
        
        watcher.cleanup()


@pytest.mark.skipif(not pytest.importorskip("PyQt5", reason="PyQt5 not available"))
class TestUIPerformance:
    """Test UI component performance."""
    
    def test_pane_creation_performance(self, qapp, performance_monitor):
        """Test file explorer pane creation performance."""
        from src.file_explorer.ui.file_explorer_pane import \
            FileExplorerPane
        from src.file_explorer.ui.pane_manager import (PaneConfiguration,
                                                           PaneType)
        
        performance_monitor.start_measurement("pane_creation_batch")
        
        panes = []
        for i in range(50):
            config = PaneConfiguration(
                pane_id=f"perf_pane_{i}",
                pane_type=PaneType.FILE_EXPLORER,
                title=f"Performance Pane {i}"
            )
            pane = FileExplorerPane(config)
            panes.append(pane)
        
        creation_duration = performance_monitor.end_measurement("pane_creation_batch")
        
        # Cleanup
        for pane in panes:
            pane.cleanup()
        
        assert creation_duration < 5.0  # 50 panes in 5 seconds
        print(f"Created 50 panes in {creation_duration:.3f}s")
    
    def test_directory_loading_performance(self, qapp, large_directory, performance_monitor):
        """Test directory loading performance in UI."""
        from src.file_explorer.ui.file_explorer_pane import \
            FileExplorerPane
        from src.file_explorer.ui.pane_manager import (PaneConfiguration,
                                                           PaneType)
        
        config = PaneConfiguration(
            pane_id="load_perf_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Load Performance Test"
        )
        
        pane = FileExplorerPane(config)
        
        performance_monitor.start_measurement("directory_load")
        
        pane.set_path(str(large_directory))
        
        # Wait for loading to complete
        time.sleep(1.0)
        
        load_duration = performance_monitor.end_measurement("directory_load")
        
        assert load_duration < TestPerformanceThresholds.MAX_DIRECTORY_LOAD_TIME
        print(f"Directory loaded in {load_duration:.3f}s")
        
        pane.cleanup()
    
    def test_widget_update_performance(self, qapp, performance_monitor):
        """Test widget update performance."""
        from src.file_explorer.ui.custom_widgets import EnhancedStatusBar
        
        status_bar = EnhancedStatusBar()
        
        performance_monitor.start_measurement("widget_updates")
        
        # Rapid updates
        for i in range(10000):
            status_bar.set_file_count(i, i * 1024)
            if i % 100 == 0:
                status_bar.set_main_message(f"Processing {i}/10000", "info")
        
        update_duration = performance_monitor.end_measurement("widget_updates")
        
        assert update_duration < 2.0  # 10k updates in 2 seconds
        print(f"10k widget updates in {update_duration:.3f}s")


class TestMemoryPerformance:
    """Test memory usage and efficiency."""
    
    def test_cache_memory_efficiency(self, test_database, memory_monitor):
        """Test cache memory usage stays reasonable."""
        try:
            from src.file_explorer.database.cache_manager import \
                CacheManager
        except ImportError:
            pytest.skip("Cache manager not available")
        
        cache = CacheManager(test_database, max_cache_size=10000)
        
        # Add large amount of data
        for i in range(5000):
            large_data = {
                "content": "x" * 1000,  # 1KB per item
                "metadata": {"index": i, "type": "large_test"}
            }
            cache.put(f"memory_key_{i}", large_data)
        
        # Force garbage collection
        gc.collect()
        
        memory_monitor.assert_memory_limit(TestPerformanceThresholds.MAX_MEMORY_INCREASE_MB)
        
        memory_increase = memory_monitor.get_memory_increase()
        print(f"Cache memory increase: {memory_increase / (1024*1024):.1f}MB")
    
    @pytest.mark.skipif(not pytest.importorskip("PyQt5", reason="PyQt5 not available"))
    def test_ui_memory_efficiency(self, qapp, memory_monitor):
        """Test UI memory usage stays reasonable."""
        from src.file_explorer.ui.file_explorer_pane import \
            FileExplorerPane
        from src.file_explorer.ui.pane_manager import (PaneConfiguration,
                                                           PaneType)

        # Create and destroy many panes to test for leaks
        for batch in range(10):
            panes = []
            
            # Create batch of panes
            for i in range(20):
                config = PaneConfiguration(
                    pane_id=f"memory_pane_{batch}_{i}",
                    pane_type=PaneType.FILE_EXPLORER,
                    title=f"Memory Test Pane {batch}_{i}"
                )
                pane = FileExplorerPane(config)
                panes.append(pane)
            
            # Cleanup batch
            for pane in panes:
                pane.cleanup()
            
            # Force garbage collection
            gc.collect()
        
        memory_monitor.assert_memory_limit(50)  # 50MB limit for UI tests
        
        memory_increase = memory_monitor.get_memory_increase()
        print(f"UI memory increase: {memory_increase / (1024*1024):.1f}MB")


class TestConcurrencyPerformance:
    """Test performance under concurrent conditions."""
    
    def test_cache_concurrent_access(self, test_database, performance_monitor):
        """Test cache performance under concurrent access simulation."""
        try:
            from src.file_explorer.database.cache_manager import \
                CacheManager
        except ImportError:
            pytest.skip("Cache manager not available")
        
        cache = CacheManager(test_database, max_cache_size=10000)
        
        performance_monitor.start_measurement("concurrent_cache")
        
        # Simulate concurrent access patterns
        for round_num in range(10):
            # Writer phase
            for i in range(100):
                key = f"concurrent_{round_num}_{i}"
                data = {"round": round_num, "index": i, "data": f"content_{i}"}
                cache.put(key, data)
            
            # Reader phase
            for i in range(100):
                key = f"concurrent_{round_num}_{i}"
                cache.get(key)
            
            # Mixed phase
            for i in range(50):
                read_key = f"concurrent_{round_num}_{i}"
                write_key = f"concurrent_{round_num}_mixed_{i}"
                cache.get(read_key)
                cache.put(write_key, {"mixed": True, "index": i})
        
        concurrent_duration = performance_monitor.end_measurement("concurrent_cache")
        
        assert concurrent_duration < 5.0
        print(f"Concurrent cache operations in {concurrent_duration:.3f}s")
    
    def test_database_concurrent_operations(self, test_database, performance_monitor):
        """Test database performance under load."""
        performance_monitor.start_measurement("database_load")
        
        # Simulate heavy database usage
        for batch in range(20):
            # Insert batch
            for i in range(50):
                test_database.execute_update(
                    "INSERT INTO files (path, name, size) VALUES (?, ?, ?)",
                    (f"/test/batch_{batch}/file_{i}.txt", f"file_{i}.txt", i * 1024)
                )
            
            # Query batch
            results = test_database.execute_query(
                "SELECT COUNT(*) as count FROM files WHERE path LIKE ?",
                (f"/test/batch_{batch}/%",)
            )
            
            assert results[0]['count'] == 50
        
        db_duration = performance_monitor.end_measurement("database_load")
        
        assert db_duration < 10.0  # 1000 operations in 10 seconds
        print(f"Database load test in {db_duration:.3f}s")


class TestStressTests:
    """Stress testing for extreme conditions."""
    
    def test_large_file_listing_stress(self, performance_monitor):
        """Test stress with very large file listings."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Create stress test structure
            num_files = 2000  # Large but manageable for CI
            
            performance_monitor.start_measurement("stress_file_creation")
            
            for i in range(num_files):
                file_path = base_path / f"stress_file_{i:04d}.txt"
                file_path.write_text(f"Stress test file {i}")
            
            creation_duration = performance_monitor.end_measurement("stress_file_creation")
            
            # Test file listing performance
            performance_monitor.start_measurement("stress_file_listing")
            
            files = list(base_path.iterdir())
            
            listing_duration = performance_monitor.end_measurement("stress_file_listing")
            
            assert len(files) == num_files
            assert creation_duration < 30.0  # 2k files in 30 seconds
            assert listing_duration < 2.0   # List 2k files in 2 seconds
            
            print(f"Created {num_files} files in {creation_duration:.3f}s")
            print(f"Listed {num_files} files in {listing_duration:.3f}s")
    
    def test_deep_directory_stress(self, performance_monitor):
        """Test stress with deeply nested directories."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Create deep directory structure
            depth = 50  # Deep but manageable
            current_path = base_path
            
            performance_monitor.start_measurement("deep_dir_creation")
            
            for i in range(depth):
                current_path = current_path / f"level_{i:02d}"
                current_path.mkdir()
                
                # Add a file at each level
                test_file = current_path / f"file_at_level_{i}.txt"
                test_file.write_text(f"File at depth {i}")
            
            creation_duration = performance_monitor.end_measurement("deep_dir_creation")
            
            # Test traversal performance
            performance_monitor.start_measurement("deep_dir_traversal")
            
            all_files = list(base_path.rglob("*"))
            
            traversal_duration = performance_monitor.end_measurement("deep_dir_traversal")
            
            assert len(all_files) == depth * 2  # depth dirs + depth files
            assert creation_duration < 5.0
            assert traversal_duration < 2.0
            
            print(f"Created depth {depth} structure in {creation_duration:.3f}s")
            print(f"Traversed structure in {traversal_duration:.3f}s")


if __name__ == '__main__':
    pytest.main([__file__, "-v", "-s"])  # -s to see print output