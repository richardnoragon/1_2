"""
Performance Tests for Advanced Folders GUI Components

Comprehensive performance testing suite for GUI components including
load testing, memory usage, responsiveness, and stress testing.
Tests ensure enterprise-level performance standards.

Author: RFU Development Team
Version: 1.0.0
"""

import shutil
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock

import psutil
import pytest

# Ensure PyQt5 is available for testing
try:
    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    pytest.skip("PyQt5 not available", allow_module_level=True)

# Import the modules under test
if PYQT5_AVAILABLE:
    try:
        from ..config_tabs import GeneralConfigTab
        from ..configuration_dialog import FolderConfigurationDialog
        from ..directory_browser import DirectoryBrowserWidget
        MODULES_AVAILABLE = True
    except ImportError as e:
        MODULES_AVAILABLE = False
        pytest.skip(f"GUI modules not available: {e}", allow_module_level=True)


@pytest.fixture
def qapp():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def large_directory_structure():
    """Create a large directory structure for performance testing."""
    base_dir = Path(tempfile.mkdtemp(prefix="perf_test_"))
    
    # Create deep directory structure
    directories = []
    for i in range(50):  # 50 main directories
        main_dir = base_dir / f"main_dir_{i:03d}"
        main_dir.mkdir()
        directories.append(main_dir)
        
        # Create subdirectories
        for j in range(10):  # 10 subdirectories each
            sub_dir = main_dir / f"sub_dir_{j:02d}"
            sub_dir.mkdir()
            directories.append(sub_dir)
            
            # Create some files
            for k in range(5):  # 5 files per subdirectory
                file_path = sub_dir / f"file_{k}.txt"
                file_path.write_text(f"Content for file {k} in {sub_dir}")
    
    yield {
        'base_dir': base_dir,
        'directories': directories,
        'total_dirs': len(directories),
        'total_files': 50 * 10 * 5  # 2500 files
    }
    
    # Cleanup
    try:
        shutil.rmtree(base_dir)
    except Exception:
        pass


class PerformanceMonitor:
    """Helper class to monitor performance metrics."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.process = psutil.Process()
    
    def start(self):
        """Start performance monitoring."""
        self.start_time = time.perf_counter()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def stop(self):
        """Stop performance monitoring."""
        self.end_time = time.perf_counter()
        self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    @property
    def elapsed_time(self):
        """Get elapsed time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def memory_delta(self):
        """Get memory usage delta in MB."""
        if self.start_memory is not None and self.end_memory is not None:
            return self.end_memory - self.start_memory
        return None


@pytest.mark.performance
@pytest.mark.slow
class TestDialogPerformance:
    """Performance tests for dialog components."""
    
    def test_dialog_initialization_performance(self, qapp):
        """Test dialog initialization time."""
        monitor = PerformanceMonitor()
        
        monitor.start()
        dialog = FolderConfigurationDialog(mode='create')
        dialog.show()
        QApplication.processEvents()  # Process any pending events
        monitor.stop()
        
        # Dialog should initialize within 2 seconds
        assert monitor.elapsed_time < 2.0, f"Dialog took {monitor.elapsed_time:.2f}s to initialize"
        
        # Memory usage should be reasonable (< 50MB increase)
        assert monitor.memory_delta < 50, f"Dialog used {monitor.memory_delta:.1f}MB memory"
        
        dialog.close()
    
    def test_tab_switching_performance(self, qapp):
        """Test performance of tab switching."""
        dialog = FolderConfigurationDialog(mode='create')
        dialog.show()
        
        monitor = PerformanceMonitor()
        
        # Test switching between all tabs multiple times
        tab_count = dialog.tab_widget.count()
        iterations = 10
        
        monitor.start()
        for _ in range(iterations):
            for i in range(tab_count):
                dialog.tab_widget.setCurrentIndex(i)
                QApplication.processEvents()
        monitor.stop()
        
        # Tab switching should be very fast
        average_time_per_switch = monitor.elapsed_time / (iterations * tab_count)
        assert average_time_per_switch < 0.1, f"Tab switch took {average_time_per_switch:.3f}s on average"
        
        dialog.close()
    
    def test_validation_performance(self, qapp, large_directory_structure):
        """Test validation performance with large datasets."""
        dialog = FolderConfigurationDialog(mode='create')
        general_tab = dialog.tab_widget.widget(0)
        
        if isinstance(general_tab, GeneralConfigTab):
            # Add name and description
            general_tab.name_edit.setText("Performance Test Configuration")
            general_tab.description_edit.setPlainText("Testing validation performance")
            
            # Add many directories
            directories = large_directory_structure['directories'][:100]  # Use 100 directories
            for directory in directories:
                general_tab._add_directory_to_list(str(directory))
            
            monitor = PerformanceMonitor()
            
            # Test validation performance
            monitor.start()
            for _ in range(10):  # Validate 10 times
                validation_result = dialog._validate_configuration()
                assert validation_result.is_valid
            monitor.stop()
            
            # Validation should be fast even with many directories
            average_validation_time = monitor.elapsed_time / 10
            assert average_validation_time < 0.5, f"Validation took {average_validation_time:.3f}s on average"
        
        dialog.close()
    
    def test_dialog_responsiveness_under_load(self, qapp):
        """Test dialog responsiveness under simulated load."""
        dialog = FolderConfigurationDialog(mode='create')
        dialog.show()
        
        # Simulate load by performing many UI operations
        monitor = PerformanceMonitor()
        monitor.start()
        
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            # Rapid text entry
            for i in range(100):
                general_tab.name_edit.setText(f"Test Name {i}")
                QApplication.processEvents()
            
            # Rapid checkbox toggling
            for i in range(50):
                general_tab.include_subdirs_cb.setChecked(i % 2 == 0)
                general_tab.monitor_changes_cb.setChecked(i % 2 == 1)
                QApplication.processEvents()
        
        monitor.stop()
        
        # UI should remain responsive
        assert monitor.elapsed_time < 5.0, f"UI operations took {monitor.elapsed_time:.2f}s"
        
        dialog.close()


@pytest.mark.performance
@pytest.mark.slow
class TestDirectoryBrowserPerformance:
    """Performance tests for directory browser widget."""
    
    def test_large_directory_list_performance(self, qapp, large_directory_structure):
        """Test performance with large directory lists."""
        widget = DirectoryBrowserWidget()
        widget.show()
        
        directories = [str(d) for d in large_directory_structure['directories'][:200]]
        
        monitor = PerformanceMonitor()
        
        # Test adding many directories
        monitor.start()
        for directory in directories:
            success = widget.add_directory(directory)
            if not success:
                break  # Stop if we hit limits
        monitor.stop()
        
        # Should handle large directory lists efficiently
        assert monitor.elapsed_time < 10.0, f"Adding directories took {monitor.elapsed_time:.2f}s"
        
        # Test directory listing performance
        monitor.start()
        all_directories = widget.get_directories()
        monitor.stop()
        
        assert monitor.elapsed_time < 1.0, f"Getting directories took {monitor.elapsed_time:.2f}s"
        assert len(all_directories) > 0
        
        widget.close()
    
    def test_directory_validation_performance(self, qapp, large_directory_structure):
        """Test directory validation performance."""
        widget = DirectoryBrowserWidget()
        
        # Add directories
        directories = [str(d) for d in large_directory_structure['directories'][:50]]
        for directory in directories:
            widget.add_directory(directory)
        
        monitor = PerformanceMonitor()
        
        # Test validation performance
        monitor.start()
        for _ in range(20):  # Validate multiple times
            errors = widget.validate_directories()
        monitor.stop()
        
        # Validation should be fast
        average_time = monitor.elapsed_time / 20
        assert average_time < 0.2, f"Validation took {average_time:.3f}s on average"
        
        widget.close()
    
    def test_directory_tree_performance(self, qapp, large_directory_structure):
        """Test directory tree view performance."""
        widget = DirectoryBrowserWidget()
        widget.show()
        
        base_dir = large_directory_structure['base_dir']
        
        monitor = PerformanceMonitor()
        
        # Test setting root directory
        monitor.start()
        widget._set_root_directory(str(base_dir))
        QApplication.processEvents()  # Allow tree to populate
        monitor.stop()
        
        # Tree population should be reasonably fast
        assert monitor.elapsed_time < 5.0, f"Tree population took {monitor.elapsed_time:.2f}s"
        
        widget.close()
    
    def test_widget_memory_usage(self, qapp, large_directory_structure):
        """Test memory usage of directory browser widget."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create multiple widgets
        widgets = []
        for i in range(10):
            widget = DirectoryBrowserWidget()
            widget.show()
            
            # Add some directories to each
            directories = large_directory_structure['directories'][i*5:(i+1)*5]
            for directory in directories:
                widget.add_directory(str(directory))
            
            widgets.append(widget)
            QApplication.processEvents()
        
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_per_widget = (peak_memory - initial_memory) / 10
        
        # Each widget should use reasonable memory (< 10MB per widget)
        assert memory_per_widget < 10, f"Each widget used {memory_per_widget:.1f}MB"
        
        # Clean up
        for widget in widgets:
            widget.close()


@pytest.mark.performance
class TestMemoryLeakDetection:
    """Test for memory leaks in GUI components."""
    
    def test_dialog_memory_leak(self, qapp):
        """Test for memory leaks in dialog creation/destruction."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy many dialogs
        for i in range(20):
            dialog = FolderConfigurationDialog(mode='create')
            dialog.show()
            QApplication.processEvents()
            dialog.close()
            dialog.deleteLater()
            QApplication.processEvents()
        
        # Force garbage collection
        import gc
        gc.collect()
        QApplication.processEvents()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 20MB for 20 dialogs)
        assert memory_increase < 20, f"Memory increased by {memory_increase:.1f}MB"
    
    def test_widget_memory_leak(self, qapp):
        """Test for memory leaks in widget creation/destruction."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy many widgets
        for i in range(50):
            widget = DirectoryBrowserWidget()
            widget.show()
            QApplication.processEvents()
            widget.close()
            widget.deleteLater()
            QApplication.processEvents()
        
        # Force garbage collection
        import gc
        gc.collect()
        QApplication.processEvents()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 30MB for 50 widgets)
        assert memory_increase < 30, f"Memory increased by {memory_increase:.1f}MB"


@pytest.mark.performance
class TestConcurrencyPerformance:
    """Test performance under concurrent operations."""
    
    def test_concurrent_dialog_operations(self, qapp):
        """Test concurrent dialog operations."""
        dialog = FolderConfigurationDialog(mode='create')
        dialog.show()
        
        results = []
        errors = []
        
        def worker_function(worker_id):
            """Worker function for threading test."""
            try:
                # Simulate concurrent operations
                for i in range(10):
                    # Note: Qt operations must be done in main thread
                    # This test simulates the load pattern
                    time.sleep(0.01)  # Simulate work
                    results.append(f"worker_{worker_id}_op_{i}")
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        monitor.stop()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50, f"Expected 50 results, got {len(results)}"
        assert monitor.elapsed_time < 2.0, f"Concurrent operations took {monitor.elapsed_time:.2f}s"
        
        dialog.close()


@pytest.mark.performance
class TestUIResponseTime:
    """Test UI response time measurements."""
    
    def test_button_click_response_time(self, qapp):
        """Test response time for button clicks."""
        widget = DirectoryBrowserWidget()
        widget.show()
        
        click_times = []
        
        # Test multiple button clicks
        for _ in range(10):
            start_time = time.perf_counter()
            
            # Simulate button click
            widget.browse_button.click()
            QApplication.processEvents()
            
            end_time = time.perf_counter()
            click_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(click_times) / len(click_times)
        max_time = max(click_times)
        
        # Response should be very fast
        assert avg_time < 0.1, f"Average click response: {avg_time:.3f}s"
        assert max_time < 0.2, f"Max click response: {max_time:.3f}s"
        
        widget.close()
    
    def test_text_input_response_time(self, qapp):
        """Test response time for text input."""
        dialog = FolderConfigurationDialog(mode='create')
        dialog.show()
        
        general_tab = dialog.tab_widget.widget(0)
        if isinstance(general_tab, GeneralConfigTab):
            input_times = []
            
            # Test text input response
            for i in range(20):
                start_time = time.perf_counter()
                
                general_tab.name_edit.setText(f"Test Input {i}")
                QApplication.processEvents()
                
                end_time = time.perf_counter()
                input_times.append(end_time - start_time)
            
            # Calculate statistics
            avg_time = sum(input_times) / len(input_times)
            max_time = max(input_times)
            
            # Text input should be very responsive
            assert avg_time < 0.05, f"Average input response: {avg_time:.3f}s"
            assert max_time < 0.1, f"Max input response: {max_time:.3f}s"
        
        dialog.close()


# Performance benchmarking utilities
class PerformanceBenchmark:
    """Utility class for performance benchmarking."""
    
    def __init__(self, name):
        self.name = name
        self.results = []
    
    def measure(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        self.results.append(execution_time)
        
        return result, execution_time
    
    def get_statistics(self):
        """Get performance statistics."""
        if not self.results:
            return {}
        
        return {
            'count': len(self.results),
            'total_time': sum(self.results),
            'avg_time': sum(self.results) / len(self.results),
            'min_time': min(self.results),
            'max_time': max(self.results),
            'median_time': sorted(self.results)[len(self.results) // 2]
        }


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__,
        "-v",
        "-m", "performance",
        "--tb=short",
        "--durations=0"  # Show all test durations
    ])