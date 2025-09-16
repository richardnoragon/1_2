"""
Performance and Stress Testing for Size Analyzer

This module contains comprehensive performance tests, stress tests,
memory usage validation, and scalability testing for the Size Analyzer.
"""

import os
import time
import threading
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

from file_utilities_2.core.size_analyzer_logic import (
    SizeAnalyzer, SizeAnalyzerWorker
)


class TestSizeAnalyzerPerformance:
    """Test Size Analyzer performance characteristics."""
    
    def test_small_directory_performance(self, size_analyzer, test_files,
                                        temp_dir):
        """Test performance with small directory."""
        start_time = time.time()
        result = size_analyzer.analyze_directory(temp_dir)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Small directory should analyze quickly (< 5 seconds)
        assert analysis_time < 5.0, f"Small directory analysis too slow: {analysis_time}s"
        assert result is not None
        assert result['file_count'] > 0
    
    def test_medium_directory_performance(self, size_analyzer,
                                         performance_test_data):
        """Test performance with medium-sized directory."""
        # Use medium test file
        medium_file = performance_test_data['medium']['path']
        test_dir = os.path.dirname(medium_file)
        
        start_time = time.time()
        result = size_analyzer.analyze_directory(test_dir)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Medium directory should analyze reasonably quickly (< 10 seconds)
        assert analysis_time < 10.0, f"Medium directory analysis too slow: {analysis_time}s"
        assert result is not None
    
    def test_large_directory_performance(self, size_analyzer,
                                        performance_test_data):
        """Test performance with large directory."""
        # Use large test file
        large_file = performance_test_data['large']['path']
        test_dir = os.path.dirname(large_file)
        
        start_time = time.time()
        result = size_analyzer.analyze_directory(test_dir)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Large directory should complete within reasonable time (< 30 seconds)
        assert analysis_time < 30.0, f"Large directory analysis too slow: {analysis_time}s"
        assert result is not None
    
    def test_progress_callback_performance(self, size_analyzer,
                                          performance_test_data):
        """Test that progress callbacks don't significantly impact performance."""
        large_file = performance_test_data['large']['path']
        test_dir = os.path.dirname(large_file)
        
        # Test without progress callback
        start_time = time.time()
        size_analyzer.analyze_directory(test_dir)
        time_without_callback = time.time() - start_time
        
        # Test with progress callback
        progress_calls = []
        
        def progress_callback(percentage):
            progress_calls.append(percentage)
        
        start_time = time.time()
        size_analyzer.analyze_directory(test_dir,
                                       progress_callback=progress_callback)
        time_with_callback = time.time() - start_time
        
        # Callback overhead should be minimal (< 50% increase)
        if time_without_callback > 0:
            overhead_ratio = time_with_callback / time_without_callback
            assert overhead_ratio < 1.5, f"Progress callback overhead too high: {overhead_ratio}"
        
        # Verify callbacks were made
        assert len(progress_calls) > 0
    
    def test_signal_emission_performance(self, qapp, size_analyzer,
                                        performance_test_data):
        """Test that signal emissions don't impact performance significantly."""
        large_file = performance_test_data['large']['path']
        test_dir = os.path.dirname(large_file)
        
        # Connect signal receivers
        signal_counts = {'progress': 0, 'message': 0, 'milestone': 0}
        
        def count_progress(percentage):
            signal_counts['progress'] += 1
        
        def count_message(message):
            signal_counts['message'] += 1
        
        def count_milestone(milestone, percentage):
            signal_counts['milestone'] += 1
        
        size_analyzer.progress_percentage.connect(count_progress)
        size_analyzer.progress_message.connect(count_message)
        size_analyzer.milestone_reached.connect(count_milestone)
        
        start_time = time.time()
        result = size_analyzer.analyze_directory(test_dir)
        analysis_time = time.time() - start_time
        
        # Should complete in reasonable time even with signals
        assert analysis_time < 30.0, f"Analysis with signals too slow: {analysis_time}s"
        assert result is not None
        
        # Verify signals were emitted
        assert signal_counts['progress'] > 0
        assert signal_counts['message'] > 0
        assert signal_counts['milestone'] > 0
    
    def test_format_size_performance(self, size_analyzer):
        """Test format_size method performance."""
        test_sizes = [
            0, 512, 1024, 1048576, 1073741824, 1099511627776
        ] * 1000  # Test with many values
        
        start_time = time.time()
        for size in test_sizes:
            size_analyzer.format_size(size)
        end_time = time.time()
        
        format_time = end_time - start_time
        
        # Should format many sizes quickly (< 1 second for 6000 calls)
        assert format_time < 1.0, f"format_size too slow: {format_time}s for {len(test_sizes)} calls"
    
    def test_export_performance(self, size_analyzer, analysis_results_sample,
                               temp_dir):
        """Test export performance."""
        export_path = os.path.join(temp_dir, 'performance_export.json')
        
        start_time = time.time()
        size_analyzer.export_analysis(analysis_results_sample, export_path)
        export_time = time.time() - start_time
        
        # Export should be fast (< 2 seconds)
        assert export_time < 2.0, f"Export too slow: {export_time}s"
        assert os.path.exists(export_path)


class TestSizeAnalyzerStressTesting:
    """Test Size Analyzer under stress conditions."""
    
    def test_many_small_files_stress(self, size_analyzer, temp_dir):
        """Test analysis with many small files."""
        # Create many small files
        num_files = 1000
        for i in range(num_files):
            file_path = os.path.join(temp_dir, f'small_file_{i:04d}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Content {i}')
        
        start_time = time.time()
        result = size_analyzer.analyze_directory(temp_dir)
        analysis_time = time.time() - start_time
        
        # Should handle many files (< 60 seconds for 1000 files)
        assert analysis_time < 60.0, f"Many files analysis too slow: {analysis_time}s"
        assert result['file_count'] == num_files
    
    def test_deep_directory_structure_stress(self, size_analyzer, temp_dir):
        """Test analysis with deeply nested directory structure."""
        # Create deep nesting
        current_dir = temp_dir
        depth = 20
        
        for i in range(depth):
            current_dir = os.path.join(current_dir, f'level_{i}')
            os.makedirs(current_dir, exist_ok=True)
            
            # Add a file at each level
            file_path = os.path.join(current_dir, f'file_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Content at level {i}')
        
        start_time = time.time()
        result = size_analyzer.analyze_directory(temp_dir)
        analysis_time = time.time() - start_time
        
        # Should handle deep nesting (< 30 seconds)
        assert analysis_time < 30.0, f"Deep nesting analysis too slow: {analysis_time}s"
        assert result['file_count'] == depth
        assert result['directory_count'] >= depth
    
    def test_mixed_file_sizes_stress(self, size_analyzer, temp_dir):
        """Test analysis with mixed file sizes."""
        # Create files of various sizes
        file_sizes = [
            (1, 'tiny'),
            (1024, 'small'),
            (10240, 'medium'),
            (102400, 'large'),
            (1024000, 'xlarge')
        ]
        
        for size, name in file_sizes:
            for i in range(10):  # 10 files of each size
                file_path = os.path.join(temp_dir, f'{name}_{i}.dat')
                with open(file_path, 'wb') as f:
                    f.write(b'X' * size)
        
        start_time = time.time()
        result = size_analyzer.analyze_directory(temp_dir)
        analysis_time = time.time() - start_time
        
        # Should handle mixed sizes (< 45 seconds)
        assert analysis_time < 45.0, f"Mixed sizes analysis too slow: {analysis_time}s"
        assert result['file_count'] == len(file_sizes) * 10
    
    def test_concurrent_analysis_stress(self, temp_dir, test_files):
        """Test concurrent analysis operations."""
        num_threads = 5
        results = []
        errors = []
        
        def run_analysis():
            try:
                analyzer = SizeAnalyzer()
                result = analyzer.analyze_directory(temp_dir)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run concurrent analyses
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=run_analysis)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=60)  # 60 second timeout per thread
        
        total_time = time.time() - start_time
        
        # Should complete all analyses (< 120 seconds total)
        assert total_time < 120.0, f"Concurrent analysis too slow: {total_time}s"
        assert len(errors) == 0, f"Errors in concurrent analysis: {errors}"
        assert len(results) == num_threads
    
    def test_rapid_cancellation_stress(self, size_analyzer, temp_dir):
        """Test rapid cancellation and restart."""
        num_iterations = 10
        
        for i in range(num_iterations):
            # Start analysis
            analyzer = SizeAnalyzer()
            
            # Cancel immediately
            analyzer.cancel_operation()
            
            # Verify cancellation
            assert analyzer._should_cancel is True
        
        # Final analysis should work normally
        result = size_analyzer.analyze_directory(temp_dir)
        assert result is not None
    
    def test_memory_stress_large_directory(self, size_analyzer, temp_dir):
        """Test memory usage with large directory."""
        try:
            import psutil
            process = psutil.Process()
            
            # Create many files to stress memory
            num_files = 5000
            for i in range(num_files):
                file_path = os.path.join(temp_dir, f'stress_file_{i:05d}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'Stress test content {i}\n' * 10)
            
            # Get initial memory
            initial_memory = process.memory_info().rss
            
            # Run analysis
            result = size_analyzer.analyze_directory(temp_dir)
            
            # Get peak memory
            peak_memory = process.memory_info().rss
            memory_increase = peak_memory - initial_memory
            
            # Memory increase should be reasonable (< 500MB)
            assert memory_increase < 500 * 1024 * 1024, f"Memory usage too high: {memory_increase} bytes"
            assert result['file_count'] == num_files
            
        except ImportError:
            # psutil not available, skip memory test
            pass


class TestSizeAnalyzerWorkerPerformance:
    """Test SizeAnalyzerWorker performance."""
    
    def test_worker_thread_performance(self, qapp, size_analyzer, temp_dir,
                                      test_files):
        """Test worker thread performance."""
        worker = SizeAnalyzerWorker(size_analyzer, temp_dir)
        
        start_time = time.time()
        worker.run()
        worker.wait(30000)  # 30 second timeout
        end_time = time.time()
        
        worker_time = end_time - start_time
        
        # Worker should complete quickly (< 30 seconds)
        assert worker_time < 30.0, f"Worker thread too slow: {worker_time}s"
        assert not worker.isRunning()
    
    def test_worker_cancellation_performance(self, qapp, size_analyzer,
                                           performance_test_data):
        """Test worker cancellation performance."""
        large_file = performance_test_data['large']['path']
        test_dir = os.path.dirname(large_file)
        
        worker = SizeAnalyzerWorker(size_analyzer, test_dir)
        
        # Start worker
        worker.start()
        
        # Cancel quickly
        start_cancel_time = time.time()
        worker.cancel()
        worker.wait(5000)  # 5 second timeout for cancellation
        cancel_time = time.time() - start_cancel_time
        
        # Cancellation should be fast (< 5 seconds)
        assert cancel_time < 5.0, f"Worker cancellation too slow: {cancel_time}s"
        assert not worker.isRunning()
    
    def test_multiple_worker_performance(self, qapp, temp_dir, test_files):
        """Test multiple worker threads performance."""
        num_workers = 3
        workers = []
        
        start_time = time.time()
        
        # Create and start workers
        for i in range(num_workers):
            analyzer = SizeAnalyzer()
            worker = SizeAnalyzerWorker(analyzer, temp_dir)
            workers.append(worker)
            worker.start()
        
        # Wait for all workers
        for worker in workers:
            worker.wait(30000)  # 30 second timeout each
        
        total_time = time.time() - start_time
        
        # Multiple workers should complete reasonably (< 60 seconds)
        assert total_time < 60.0, f"Multiple workers too slow: {total_time}s"
        
        # All workers should be finished
        for worker in workers:
            assert not worker.isRunning()


class TestSizeAnalyzerScalability:
    """Test Size Analyzer scalability characteristics."""
    
    def test_file_count_scalability(self, size_analyzer, temp_dir):
        """Test scalability with increasing file counts."""
        file_counts = [10, 50, 100, 500]
        times = []
        
        for count in file_counts:
            # Create files
            test_dir = os.path.join(temp_dir, f'scale_test_{count}')
            os.makedirs(test_dir, exist_ok=True)
            
            for i in range(count):
                file_path = os.path.join(test_dir, f'file_{i:04d}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'Content {i}')
            
            # Time analysis
            start_time = time.time()
            result = size_analyzer.analyze_directory(test_dir)
            analysis_time = time.time() - start_time
            
            times.append(analysis_time)
            assert result['file_count'] == count
        
        # Time should scale reasonably (not exponentially)
        # Each increase should not be more than 5x the previous
        for i in range(1, len(times)):
            if times[i-1] > 0:
                scale_factor = times[i] / times[i-1]
                expected_scale = file_counts[i] / file_counts[i-1]
                # Allow some overhead, but should be roughly linear
                assert scale_factor < expected_scale * 2, f"Poor scalability at {file_counts[i]} files"
    
    def test_directory_depth_scalability(self, size_analyzer, temp_dir):
        """Test scalability with increasing directory depth."""
        depths = [5, 10, 15, 20]
        times = []
        
        for depth in depths:
            # Create deep structure
            test_dir = os.path.join(temp_dir, f'depth_test_{depth}')
            current_dir = test_dir
            
            for i in range(depth):
                current_dir = os.path.join(current_dir, f'level_{i}')
                os.makedirs(current_dir, exist_ok=True)
                
                # Add file at each level
                file_path = os.path.join(current_dir, f'file_{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'Level {i} content')
            
            # Time analysis
            start_time = time.time()
            result = size_analyzer.analyze_directory(test_dir)
            analysis_time = time.time() - start_time
            
            times.append(analysis_time)
            assert result['file_count'] == depth
        
        # Time should scale reasonably with depth
        for i in range(1, len(times)):
            if times[i-1] > 0:
                scale_factor = times[i] / times[i-1]
                # Should not be exponential growth
                assert scale_factor < 3.0, f"Poor depth scalability at depth {depths[i]}"
    
    def test_file_size_scalability(self, size_analyzer, temp_dir):
        """Test scalability with increasing file sizes."""
        file_sizes = [1024, 10240, 102400, 1024000]  # 1KB to 1MB
        times = []
        
        for size in file_sizes:
            # Create file of specific size
            test_dir = os.path.join(temp_dir, f'size_test_{size}')
            os.makedirs(test_dir, exist_ok=True)
            
            file_path = os.path.join(test_dir, f'large_file_{size}.dat')
            with open(file_path, 'wb') as f:
                f.write(b'X' * size)
            
            # Time analysis
            start_time = time.time()
            result = size_analyzer.analyze_directory(test_dir)
            analysis_time = time.time() - start_time
            
            times.append(analysis_time)
            assert result['total_size'] >= size
        
        # File size should not significantly impact analysis time
        # (since we're just getting file stats, not reading content)
        max_time = max(times)
        min_time = min(times)
        
        if min_time > 0:
            time_ratio = max_time / min_time
            # Should not vary by more than 3x
            assert time_ratio < 3.0, f"File size impacts performance too much: {time_ratio}x"


class TestSizeAnalyzerResourceUsage:
    """Test Size Analyzer resource usage characteristics."""
    
    def test_cpu_usage_monitoring(self, size_analyzer, performance_test_data):
        """Test CPU usage during analysis."""
        try:
            import psutil
            process = psutil.Process()
            
            large_file = performance_test_data['large']['path']
            test_dir = os.path.dirname(large_file)
            
            # Monitor CPU usage
            cpu_samples = []
            
            def monitor_cpu():
                for _ in range(10):  # Sample for 10 iterations
                    cpu_samples.append(process.cpu_percent())
                    time.sleep(0.1)
            
            # Start monitoring
            monitor_thread = threading.Thread(target=monitor_cpu)
            monitor_thread.start()
            
            # Run analysis
            result = size_analyzer.analyze_directory(test_dir)
            
            monitor_thread.join()
            
            # Verify reasonable CPU usage
            if cpu_samples:
                avg_cpu = sum(cpu_samples) / len(cpu_samples)
                max_cpu = max(cpu_samples)
                
                # Should not consume excessive CPU (< 80% average)
                assert avg_cpu < 80.0, f"Average CPU usage too high: {avg_cpu}%"
                assert max_cpu < 100.0, f"Peak CPU usage too high: {max_cpu}%"
            
            assert result is not None
            
        except ImportError:
            # psutil not available, skip CPU test
            pass
    
    def test_memory_leak_detection(self, size_analyzer, temp_dir):
        """Test for memory leaks during repeated analysis."""
        try:
            import psutil
            import gc
            
            process = psutil.Process()
            
            # Create test files
            for i in range(100):
                file_path = os.path.join(temp_dir, f'leak_test_{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'Leak test content {i}\n' * 100)
            
            # Get initial memory
            gc.collect()
            initial_memory = process.memory_info().rss
            
            # Run multiple analyses
            for i in range(10):
                result = size_analyzer.analyze_directory(temp_dir)
                assert result is not None
                
                # Force garbage collection
                gc.collect()
            
            # Get final memory
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be minimal (< 50MB)
            assert memory_increase < 50 * 1024 * 1024, f"Possible memory leak: {memory_increase} bytes"
            
        except ImportError:
            # psutil not available, skip memory test
            pass
    
    def test_file_handle_management(self, size_analyzer, temp_dir):
        """Test proper file handle management."""
        try:
            import psutil
            process = psutil.Process()
            
            # Create many files
            num_files = 500
            for i in range(num_files):
                file_path = os.path.join(temp_dir, f'handle_test_{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'Handle test {i}')
            
            # Get initial file handle count
            initial_handles = process.num_fds() if hasattr(process, 'num_fds') else 0
            
            # Run analysis
            result = size_analyzer.analyze_directory(temp_dir)
            
            # Get final file handle count
            final_handles = process.num_fds() if hasattr(process, 'num_fds') else 0
            
            # File handles should not leak significantly
            handle_increase = final_handles - initial_handles
            assert handle_increase < 10, f"File handle leak detected: {handle_increase} handles"
            
            assert result is not None
            assert result['file_count'] == num_files
            
        except (ImportError, AttributeError):
            # psutil not available or no num_fds method, skip test
            pass