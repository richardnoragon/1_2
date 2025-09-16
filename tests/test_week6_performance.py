"""Performance and Load Testing Suite for Week 6 Deliverables.

Enterprise-grade performance testing including:
- Backend integration performance under load
- Real-time search performance and memory usage
- Preview pane loading performance with large files
- Keyboard shortcuts responsiveness
- Accessibility compliance under stress
- Multi-threaded operation validation
"""

import gc
import os
import resource
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import Mock, patch

import psutil
import pytest
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.advanced_folders.core import (FolderConfiguration,
                                                 SearchFilter)
from src.tools.advanced_folders.gui.accessibility_manager import \
    AccessibilityManager
from src.tools.advanced_folders.gui.keyboard_shortcuts import \
    KeyboardShortcutsManager
from src.tools.advanced_folders.gui.preview_pane import PreviewPaneWidget
from src.tools.advanced_folders.integration.backend_integration import \
    BackendIntegrationManager
from src.tools.advanced_folders.integration.realtime_search import \
    RealtimeSearchManager
from src.tools.advanced_folders.models import FileMetadata, SearchParameter


class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.start_memory = None
        self.start_time = None
        self.process = psutil.Process()
    
    def start_monitoring(self):
        """Start performance monitoring."""
        gc.collect()  # Clean up before monitoring
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_time = time.time()
    
    def stop_monitoring(self):
        """Stop monitoring and return metrics."""
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'duration': end_time - self.start_time,
            'memory_used': end_memory - self.start_memory,
            'peak_memory': end_memory,
            'cpu_percent': self.process.cpu_percent()
        }


class TestBackendIntegrationPerformance:
    """Performance tests for Backend Integration Manager."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.processEvents()
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    @pytest.fixture
    def backend_manager(self, app):
        """Create backend manager for performance testing."""
        mock_db = Mock()
        mock_repo = Mock()
        
        with patch('src.tools.advanced_folders.database.AdvancedFoldersDBManager', return_value=mock_db), \
             patch('src.tools.advanced_folders.repositories.RepositoryManager', return_value=mock_repo):
            manager = BackendIntegrationManager()
            yield manager
            manager.shutdown()
    
    def test_concurrent_folder_operations(self, backend_manager, performance_monitor):
        """Test concurrent folder operations performance."""
        performance_monitor.start_monitoring()
        
        def create_folder_config(folder_id):
            """Create folder configuration in thread."""
            config = FolderConfiguration(
                name=f"Test Folder {folder_id}",
                base_path=f"/test/path/{folder_id}",
                patterns=["*.txt", "*.doc"]
            )
            return backend_manager.create_folder_configuration(config)
        
        # Run 50 concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_folder_config, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        metrics = performance_monitor.stop_monitoring()
        
        # Validate performance
        assert all(result.success for result in results)
        assert metrics['duration'] < 5.0  # Should complete in < 5 seconds
        assert metrics['memory_used'] < 100  # Should use < 100MB additional memory
    
    def test_bulk_search_operations(self, backend_manager, performance_monitor):
        """Test bulk search operations performance."""
        performance_monitor.start_monitoring()
        
        def perform_search(query_id):
            """Perform search operation."""
            search_params = SearchParameter(
                patterns=[f"*query_{query_id}*"],
                include_subdirectories=True,
                case_sensitive=False
            )
            return backend_manager.search_folder(f"folder_{query_id}", search_params)
        
        # Run 100 search operations
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(perform_search, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]
        
        metrics = performance_monitor.stop_monitoring()
        
        # Validate performance
        assert all(result.success for result in results)
        assert metrics['duration'] < 10.0  # Should complete in < 10 seconds
        assert metrics['cpu_percent'] < 80  # Should not max out CPU
    
    def test_memory_usage_under_load(self, backend_manager, performance_monitor):
        """Test memory usage during extended operations."""
        performance_monitor.start_monitoring()
        
        # Perform many operations to test memory management
        for batch in range(10):
            # Create batch of configurations
            configs = [
                FolderConfiguration(f"Batch{batch}_Folder{i}", f"/path/{batch}/{i}", ["*.txt"])
                for i in range(20)
            ]
            
            # Process batch
            for config in configs:
                backend_manager.create_folder_configuration(config)
            
            # Force garbage collection
            gc.collect()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Memory usage should be reasonable
        assert metrics['memory_used'] < 200  # Should use < 200MB additional
        assert metrics['duration'] < 30.0  # Should complete in < 30 seconds
    
    def test_performance_monitoring_accuracy(self, backend_manager):
        """Test performance monitoring system accuracy."""
        # Perform operations and check monitoring
        for i in range(10):
            config = FolderConfiguration(f"Test{i}", f"/path/{i}", ["*.txt"])
            backend_manager.create_folder_configuration(config)
        
        # Get performance metrics
        metrics = backend_manager.get_performance_metrics()
        
        assert metrics['total_operations'] >= 10
        assert metrics['average_duration'] > 0
        assert metrics['success_rate'] > 0.8  # At least 80% success rate


class TestRealtimeSearchPerformance:
    """Performance tests for Realtime Search Manager."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.processEvents()
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    @pytest.fixture
    def search_manager(self, app):
        """Create search manager for performance testing."""
        mock_backend = Mock()
        mock_backend.quick_search.return_value = Mock(success=True, results=[])
        
        manager = RealtimeSearchManager(mock_backend)
        yield manager
        manager.shutdown()
    
    def test_rapid_search_debouncing(self, search_manager, performance_monitor, app):
        """Test performance of rapid search requests with debouncing."""
        performance_monitor.start_monitoring()
        
        # Simulate rapid typing (100 search requests in quick succession)
        for i in range(100):
            search_manager.search(f"test_query_{i}")
        
        # Wait for debounce to complete
        QTest.qWait(search_manager.debounce_delay + 200)
        app.processEvents()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle rapid requests efficiently
        assert metrics['duration'] < 2.0  # Should complete quickly due to debouncing
        assert search_manager.backend_manager.quick_search.call_count < 10  # Debouncing should limit calls
    
    def test_search_cache_performance(self, search_manager, performance_monitor):
        """Test search cache performance with large datasets."""
        performance_monitor.start_monitoring()
        
        # Fill cache with many entries
        unique_queries = [f"unique_query_{i}" for i in range(500)]
        
        # First pass - populate cache
        for query in unique_queries:
            search_manager.search(query)
        
        # Second pass - should use cache
        for query in unique_queries:
            search_manager.search(query)
        
        metrics = performance_monitor.stop_monitoring()
        
        # Cache should improve performance
        assert len(search_manager.search_cache) == 500
        assert metrics['memory_used'] < 50  # Cache should be memory efficient
    
    def test_concurrent_search_requests(self, search_manager, performance_monitor):
        """Test concurrent search request handling."""
        performance_monitor.start_monitoring()
        
        def perform_search(query_id):
            """Perform search in thread."""
            search_manager.search(f"concurrent_query_{query_id}")
            return True
        
        # Run 30 concurrent searches
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(perform_search, i) for i in range(30)]
            results = [future.result() for future in as_completed(futures)]
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle concurrent requests
        assert all(results)
        assert metrics['duration'] < 3.0  # Should complete efficiently
    
    def test_memory_leak_prevention(self, search_manager, performance_monitor):
        """Test memory leak prevention in search operations."""
        performance_monitor.start_monitoring()
        
        # Perform many searches to test for memory leaks
        for cycle in range(20):
            # Batch of searches
            for i in range(50):
                search_manager.search(f"cycle_{cycle}_query_{i}")
            
            # Clear cache periodically
            if cycle % 5 == 0:
                search_manager.clear_cache()
            
            # Force garbage collection
            gc.collect()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Memory usage should be controlled
        assert metrics['memory_used'] < 100  # Should not leak significant memory


class TestPreviewPanePerformance:
    """Performance tests for Preview Pane Widget."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.processEvents()
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    @pytest.fixture
    def preview_pane(self, app):
        """Create preview pane for performance testing."""
        widget = PreviewPaneWidget()
        yield widget
        widget.close()
    
    def test_large_file_preview_performance(self, preview_pane, performance_monitor, app, tmp_path):
        """Test preview performance with large files."""
        # Create large text file (1MB)
        large_file = tmp_path / "large_test.txt"
        large_content = "This is a test line.\n" * 50000  # ~1MB file
        large_file.write_text(large_content)
        
        performance_monitor.start_monitoring()
        
        # Load large file
        preview_pane.load_file_preview(str(large_file))
        
        # Wait for loading to complete
        QTest.qWait(2000)
        app.processEvents()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle large files efficiently
        assert metrics['duration'] < 5.0  # Should load in < 5 seconds
        assert metrics['memory_used'] < 50  # Should use < 50MB additional memory
    
    def test_rapid_file_switching(self, preview_pane, performance_monitor, app, tmp_path):
        """Test performance of rapid file switching."""
        # Create multiple test files
        test_files = []
        for i in range(20):
            test_file = tmp_path / f"test_{i}.txt"
            test_file.write_text(f"Test content for file {i}\n" * 100)
            test_files.append(str(test_file))
        
        performance_monitor.start_monitoring()
        
        # Rapidly switch between files
        for file_path in test_files:
            preview_pane.load_file_preview(file_path)
            QTest.qWait(50)  # Small delay to simulate rapid switching
            app.processEvents()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle rapid switching efficiently
        assert metrics['duration'] < 10.0  # Should complete in < 10 seconds
    
    def test_concurrent_preview_operations(self, preview_pane, performance_monitor, app, tmp_path):
        """Test concurrent preview operations."""
        # Create test files
        test_files = []
        for i in range(10):
            test_file = tmp_path / f"concurrent_test_{i}.txt"
            test_file.write_text(f"Concurrent test content {i}\n" * 200)
            test_files.append(str(test_file))
        
        performance_monitor.start_monitoring()
        
        # Simulate concurrent preview requests
        for file_path in test_files:
            preview_pane.load_file_preview(file_path)
            app.processEvents()  # Allow processing
        
        # Wait for all operations to complete
        QTest.qWait(3000)
        app.processEvents()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle concurrent operations
        assert metrics['duration'] < 15.0  # Should complete in reasonable time
    
    def test_memory_cleanup_on_file_change(self, preview_pane, performance_monitor, app, tmp_path):
        """Test memory cleanup when changing preview files."""
        # Create files of different sizes
        files = []
        for i, size_multiplier in enumerate([100, 500, 1000, 200, 800]):
            test_file = tmp_path / f"memory_test_{i}.txt"
            content = f"Memory test content line {i}.\n" * size_multiplier
            test_file.write_text(content)
            files.append(str(test_file))
        
        performance_monitor.start_monitoring()
        
        # Load each file and measure memory
        for file_path in files:
            preview_pane.load_file_preview(file_path)
            QTest.qWait(500)
            app.processEvents()
            gc.collect()  # Force garbage collection
        
        metrics = performance_monitor.stop_monitoring()
        
        # Memory should be managed efficiently
        assert metrics['memory_used'] < 100  # Should not accumulate excessive memory


class TestKeyboardShortcutsPerformance:
    """Performance tests for Keyboard Shortcuts Manager."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.processEvents()
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    @pytest.fixture
    def shortcuts_manager(self, app):
        """Create shortcuts manager for performance testing."""
        from PyQt5.QtWidgets import QWidget
        parent = QWidget()
        manager = KeyboardShortcutsManager(parent)
        yield manager
        manager.shutdown()
        parent.close()
    
    def test_large_shortcut_registry_performance(self, shortcuts_manager, performance_monitor):
        """Test performance with large number of shortcuts."""
        performance_monitor.start_monitoring()
        
        # Register many shortcuts
        callbacks = [Mock() for _ in range(500)]
        for i in range(500):
            shortcuts_manager.register_shortcut(
                f'dynamic_action_{i}',
                f'Dynamic Action {i}',
                f'Ctrl+Alt+{i % 10}',  # Some will conflict, which is expected
                callbacks[i],
                'global'
            )
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle large registry efficiently
        assert metrics['duration'] < 5.0  # Should register quickly
        assert len(shortcuts_manager.shortcuts) >= 500
    
    def test_shortcut_lookup_performance(self, shortcuts_manager, performance_monitor):
        """Test shortcut lookup performance."""
        # Add many shortcuts first
        for i in range(200):
            callback = Mock()
            shortcuts_manager.register_shortcut(
                f'lookup_test_{i}',
                f'Lookup Test {i}',
                f'F{(i % 12) + 1}',
                callback,
                'global'
            )
        
        performance_monitor.start_monitoring()
        
        # Perform many lookups
        for i in range(1000):
            action_id = f'lookup_test_{i % 200}'
            all_shortcuts = shortcuts_manager.get_all_shortcuts()
            assert action_id in all_shortcuts or action_id not in all_shortcuts  # Just perform lookup
        
        metrics = performance_monitor.stop_monitoring()
        
        # Lookups should be fast
        assert metrics['duration'] < 2.0  # Should complete quickly
    
    def test_context_switching_performance(self, shortcuts_manager, performance_monitor):
        """Test context switching performance."""
        # Register shortcuts in different contexts
        contexts = ['global', 'search_results', 'folder_tree', 'preview', 'settings']
        
        for context in contexts:
            for i in range(50):
                callback = Mock()
                shortcuts_manager.register_shortcut(
                    f'{context}_action_{i}',
                    f'{context.title()} Action {i}',
                    f'Ctrl+{i % 10}',
                    callback,
                    context
                )
        
        performance_monitor.start_monitoring()
        
        # Rapidly switch contexts
        for _ in range(100):
            for context in contexts:
                shortcuts_manager.set_active_context(context)
        
        metrics = performance_monitor.stop_monitoring()
        
        # Context switching should be fast
        assert metrics['duration'] < 1.0  # Should switch quickly


class TestAccessibilityPerformance:
    """Performance tests for Accessibility Manager."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.processEvents()
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    @pytest.fixture
    def accessibility_manager(self, app):
        """Create accessibility manager for performance testing."""
        from PyQt5.QtWidgets import QWidget
        parent = QWidget()
        manager = AccessibilityManager(app, parent)
        yield manager
        manager.shutdown()
        parent.close()
    
    def test_large_component_registry_performance(self, accessibility_manager, performance_monitor, app):
        """Test performance with many registered components."""
        performance_monitor.start_monitoring()
        
        # Register many components
        widgets = []
        for i in range(300):
            widget = QWidget()
            widget.setObjectName(f"TestWidget_{i}")
            
            accessibility_manager.register_component(
                widget,
                accessibility_name=f"Test Widget {i}",
                accessibility_description=f"Test widget number {i} for accessibility testing",
                role="generic"
            )
            widgets.append(widget)
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle large registry efficiently
        assert metrics['duration'] < 3.0  # Should register quickly
        assert len(accessibility_manager.registered_components) == 300
        
        # Cleanup
        for widget in widgets:
            widget.close()
    
    def test_accessibility_audit_performance(self, accessibility_manager, performance_monitor, app):
        """Test accessibility audit performance."""
        # Register components with various accessibility issues
        widgets = []
        for i in range(100):
            widget = QWidget()
            widget.setObjectName(f"AuditWidget_{i}")
            
            # Some widgets have good accessibility, others don't
            if i % 3 == 0:
                accessibility_manager.register_component(
                    widget,
                    accessibility_name=f"Good Widget {i}",
                    accessibility_description=f"Well-configured widget {i}"
                )
            else:
                accessibility_manager.register_component(widget)  # Missing accessibility info
            
            widgets.append(widget)
        
        performance_monitor.start_monitoring()
        
        # Run accessibility audit
        audit_results = accessibility_manager.audit_accessibility()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Audit should complete efficiently
        assert metrics['duration'] < 5.0  # Should audit quickly
        assert audit_results['total_components'] == 100
        assert len(audit_results['issues']) > 0  # Should find issues
        
        # Cleanup
        for widget in widgets:
            widget.close()
    
    def test_announcement_system_performance(self, accessibility_manager, performance_monitor, app):
        """Test announcement system performance."""
        performance_monitor.start_monitoring()
        
        # Queue many announcements
        for i in range(100):
            accessibility_manager.announce(
                f"Test announcement {i}",
                "polite" if i % 2 == 0 else "assertive"
            )
        
        # Wait for processing
        QTest.qWait(2000)
        app.processEvents()
        
        metrics = performance_monitor.stop_monitoring()
        
        # Should handle many announcements efficiently
        assert metrics['duration'] < 5.0  # Should process announcements quickly


class TestIntegratedSystemPerformance:
    """Performance tests for integrated system."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
        app.processEvents()
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    def test_full_system_startup_performance(self, app, performance_monitor):
        """Test full system startup performance."""
        performance_monitor.start_monitoring()
        
        # Mock dependencies
        mock_db = Mock()
        mock_repo = Mock()
        
        with patch('src.tools.advanced_folders.database.AdvancedFoldersDBManager', return_value=mock_db), \
             patch('src.tools.advanced_folders.repositories.RepositoryManager', return_value=mock_repo):
            
            # Initialize all components
            backend_manager = BackendIntegrationManager()
            search_manager = RealtimeSearchManager(backend_manager)
            
            from PyQt5.QtWidgets import QWidget
            parent_widget = QWidget()
            
            preview_pane = PreviewPaneWidget()
            shortcuts_manager = KeyboardShortcutsManager(parent_widget)
            accessibility_manager = AccessibilityManager(app, parent_widget)
            
            components = [backend_manager, search_manager, preview_pane, shortcuts_manager, accessibility_manager]
        
        metrics = performance_monitor.stop_monitoring()
        
        # System should start up quickly
        assert metrics['duration'] < 3.0  # Should initialize in < 3 seconds
        assert metrics['memory_used'] < 100  # Should use < 100MB
        
        # Cleanup
        for component in components:
            if hasattr(component, 'shutdown'):
                component.shutdown()
            elif hasattr(component, 'close'):
                component.close()
        
        parent_widget.close()
    
    def test_system_under_concurrent_load(self, app, performance_monitor):
        """Test system performance under concurrent load."""
        mock_db = Mock()
        mock_repo = Mock()
        
        with patch('src.tools.advanced_folders.database.AdvancedFoldersDBManager', return_value=mock_db), \
             patch('src.tools.advanced_folders.repositories.RepositoryManager', return_value=mock_repo):
            
            # Initialize system
            backend_manager = BackendIntegrationManager()
            search_manager = RealtimeSearchManager(backend_manager)
            
            performance_monitor.start_monitoring()
            
            def concurrent_operations():
                """Perform concurrent operations."""
                # Folder operations
                for i in range(10):
                    config = FolderConfiguration(f"Concurrent{i}", f"/path/{i}", ["*.txt"])
                    backend_manager.create_folder_configuration(config)
                
                # Search operations
                for i in range(15):
                    search_manager.search(f"concurrent_query_{i}")
                
                return True
            
            # Run multiple threads performing operations
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(concurrent_operations) for _ in range(3)]
                results = [future.result() for future in as_completed(futures)]
            
            metrics = performance_monitor.stop_monitoring()
            
            # System should handle concurrent load
            assert all(results)
            assert metrics['duration'] < 15.0  # Should complete in reasonable time
            assert metrics['cpu_percent'] < 90  # Should not max out CPU
            
            # Cleanup
            backend_manager.shutdown()
            search_manager.shutdown()


if __name__ == '__main__':
    # Run performance test suite
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-x',  # Stop on first failure
        '--durations=0'  # Show all test durations
    ])