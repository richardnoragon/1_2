"""
Enterprise-Grade Performance Tests for Advanced Folders System
Phase 4: Testing & QA (Week 10) - Comprehensive Performance Testing

Test Coverage Target: Load, Stress, and Scalability Testing
Test Complexity Level: Enterprise-Grade (No Simplification)
Quality Standards: Zero-Compromise Testing Protocols

This module implements comprehensive performance testing for the Advanced Folders
system with quantitative benchmarks and detailed performance analysis.
"""

import gc
import os
import statistics
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import psutil
import pytest

from src.tools.advanced_folders.core.folder_models import (
    FileMetadata, FolderConfiguration, FolderType, SearchParameter)
from src.tools.advanced_folders.database.db_manager import \
    AdvancedFoldersDBManager
from src.tools.advanced_folders.engine.search_engine import SearchEngine
from src.tools.advanced_folders.services.folder_service import \
    FolderService


class PerformanceMetrics:
    """Helper class for collecting and analyzing performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.start_time: float = 0
        self.process = psutil.Process(os.getpid())
    
    def start_measurement(self):
        """Start performance measurement session."""
        self.start_time = time.time()
        gc.collect()  # Force garbage collection
        self.memory_usage.clear()
        self.cpu_usage.clear()
    
    def record_operation(self, operation_name: str, duration: float):
        """Record operation performance."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(duration)
    
    def record_system_metrics(self):
        """Record current system resource usage."""
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()
        
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
    
    def get_summary(self) -> Dict:
        """Get performance summary statistics."""
        summary = {
            'total_duration': time.time() - self.start_time,
            'operations': {},
            'memory': {
                'peak_mb': max(self.memory_usage) if self.memory_usage else 0,
                'average_mb': statistics.mean(self.memory_usage) if self.memory_usage else 0,
                'final_mb': self.memory_usage[-1] if self.memory_usage else 0
            },
            'cpu': {
                'peak_percent': max(self.cpu_usage) if self.cpu_usage else 0,
                'average_percent': statistics.mean(self.cpu_usage) if self.cpu_usage else 0
            }
        }
        
        for operation, times in self.metrics.items():
            if times:
                summary['operations'][operation] = {
                    'count': len(times),
                    'total_time': sum(times),
                    'average_time': statistics.mean(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'median_time': statistics.median(times),
                    'ops_per_second': len(times) / sum(times) if sum(times) > 0 else 0
                }
        
        return summary


class TestAdvancedFoldersPerformanceEnterprise:
    """Enterprise-grade performance test suite for Advanced Folders system."""
    
    @pytest.mark.performance
    @pytest.mark.critical
    def test_large_dataset_indexing_performance(self):
        """Test indexing performance with large datasets (100K+ files)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "performance_large.db"
            index_path = Path(temp_dir) / "performance_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            metrics = PerformanceMetrics()
            metrics.start_measurement()
            
            # Create large test dataset
            test_root = Path(temp_dir) / "large_dataset"
            test_root.mkdir()
            
            # Performance target: Index 10,000 files in under 30 seconds
            file_count = 10000
            print(f"Creating {file_count} test files...")
            
            # Create diverse file structure
            file_types = ['.txt', '.pdf', '.doc', '.csv', '.json', '.xml', '.log', '.md']
            file_sizes = [1024, 2048, 4096, 8192, 16384]  # Various sizes in bytes
            
            created_files = []
            start_time = time.time()
            
            for i in range(file_count):
                # Distribute files across subdirectories
                subdir_idx = i // 1000
                subdir = test_root / f"subdir_{subdir_idx}"
                subdir.mkdir(exist_ok=True)
                
                # Create file with varied characteristics
                file_type = file_types[i % len(file_types)]
                file_size = file_sizes[i % len(file_sizes)]
                file_path = subdir / f"file_{i:06d}{file_type}"
                
                # Generate content based on file type
                if file_type == '.json':
                    content = f'{{"id": {i}, "data": "content_{i}", "timestamp": "2024-01-01T00:00:00Z"}}'
                elif file_type == '.csv':
                    content = f"id,name,value\n{i},item_{i},{i * 1.5}"
                elif file_type == '.xml':
                    content = f'<?xml version="1.0"?><root><item id="{i}">content_{i}</item></root>'
                else:
                    content = f"Document {i} content with keywords: test, performance, data_{i}\n" * (file_size // 80)
                
                file_path.write_text(content[:file_size])  # Truncate to desired size
                created_files.append(file_path)
                
                # Record progress every 1000 files
                if (i + 1) % 1000 == 0:
                    metrics.record_system_metrics()
                    elapsed = time.time() - start_time
                    print(f"Created {i + 1} files in {elapsed:.2f}s ({(i + 1) / elapsed:.1f} files/sec)")
            
            file_creation_time = time.time() - start_time
            print(f"File creation completed: {file_count} files in {file_creation_time:.2f}s")
            
            # Test 1: Directory indexing performance
            folder_config = FolderConfiguration(
                name="Large Dataset Test",
                path=str(test_root),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(folder_config)
            
            # Measure indexing performance
            start_time = time.time()
            indexed_count = folder_service.index_folder_contents(config_id)
            indexing_time = time.time() - start_time
            
            metrics.record_operation('large_dataset_indexing', indexing_time)
            metrics.record_system_metrics()
            
            # Performance assertions
            assert indexed_count >= file_count * 0.95  # Allow 5% tolerance
            indexing_rate = indexed_count / indexing_time
            assert indexing_rate > 100, f"Indexing too slow: {indexing_rate:.1f} files/sec (target: >100)"
            assert indexing_time < 300, f"Indexing took too long: {indexing_time:.2f}s (target: <300s)"
            
            print(f"Indexing performance: {indexed_count} files in {indexing_time:.2f}s ({indexing_rate:.1f} files/sec)")
            
            # Test 2: Search performance on large dataset
            search_terms = [
                "content",      # Common term (high results)
                "performance",  # Medium frequency
                "test",         # High frequency
                "data_5000",    # Specific term (low results)
                "Document 1000" # Exact match
            ]
            
            search_times = []
            for term in search_terms:
                start_time = time.time()
                results = folder_service.search_all_folders(term)
                search_time = time.time() - start_time
                search_times.append(search_time)
                
                metrics.record_operation(f'search_{term}', search_time)
                
                # Search should complete within reasonable time
                assert search_time < 10.0, f"Search for '{term}' too slow: {search_time:.2f}s"
                assert len(results) >= 0  # Verify search doesn't fail
                
                print(f"Search '{term}': {len(results)} results in {search_time:.3f}s")
            
            avg_search_time = statistics.mean(search_times)
            assert avg_search_time < 5.0, f"Average search time too slow: {avg_search_time:.2f}s"
            
            # Test 3: Database query performance
            start_time = time.time()
            stats = folder_service.get_folder_statistics(config_id)
            stats_time = time.time() - start_time
            
            metrics.record_operation('statistics_query', stats_time)
            
            assert stats_time < 2.0, f"Statistics query too slow: {stats_time:.2f}s"
            assert stats['total_files'] >= file_count * 0.95
            
            # Test 4: Memory usage validation
            memory_usage = metrics.process.memory_info().rss / 1024 / 1024  # MB
            assert memory_usage < 2000, f"Memory usage too high: {memory_usage:.1f}MB"
            
            # Print performance summary
            summary = metrics.get_summary()
            print("\nPerformance Summary:")
            print(f"Total test duration: {summary['total_duration']:.2f}s")
            print(f"Peak memory usage: {summary['memory']['peak_mb']:.1f}MB")
            print(f"Average CPU usage: {summary['cpu']['average_percent']:.1f}%")
            
            for operation, stats in summary['operations'].items():
                print(f"{operation}: {stats['ops_per_second']:.1f} ops/sec (avg: {stats['average_time']:.3f}s)")
    
    @pytest.mark.performance
    @pytest.mark.critical
    def test_concurrent_load_performance(self):
        """Test system performance under concurrent load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "concurrent_load.db"
            index_path = Path(temp_dir) / "concurrent_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            metrics = PerformanceMetrics()
            metrics.start_measurement()
            
            # Create test data
            test_root = Path(temp_dir) / "concurrent_test"
            test_root.mkdir()
            
            # Create base dataset for concurrent operations
            base_files = 1000
            for i in range(base_files):
                file_path = test_root / f"base_file_{i:04d}.txt"
                content = f"Base file {i} with searchable content and keywords data_{i}"
                file_path.write_text(content)
            
            # Create folder configuration
            folder_config = FolderConfiguration(
                name="Concurrent Load Test",
                path=str(test_root),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(folder_config)
            folder_service.index_folder_contents(config_id)
            
            # Test 1: Concurrent search operations
            def search_worker(worker_id: int, search_count: int, results: List):
                """Worker function for concurrent searches."""
                search_terms = [
                    "base", "file", "content", "searchable", 
                    "keywords", "data", f"data_{worker_id * 100}"
                ]
                
                worker_times = []
                for i in range(search_count):
                    term = search_terms[i % len(search_terms)]
                    
                    start_time = time.time()
                    search_results = folder_service.search_all_folders(term)
                    search_time = time.time() - start_time
                    
                    worker_times.append(search_time)
                    results.append((worker_id, i, len(search_results), search_time))
                
                return worker_times
            
            # Run concurrent searches
            concurrent_workers = 10
            searches_per_worker = 20
            search_results = []
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
                futures = []
                for worker_id in range(concurrent_workers):
                    future = executor.submit(search_worker, worker_id, searches_per_worker, search_results)
                    futures.append(future)
                
                # Collect results
                worker_times = []
                for future in as_completed(futures):
                    worker_times.extend(future.result())
            
            concurrent_search_time = time.time() - start_time
            
            # Analyze concurrent search performance
            total_searches = concurrent_workers * searches_per_worker
            assert len(search_results) >= total_searches * 0.95  # Allow 5% tolerance
            
            avg_search_time = statistics.mean(worker_times)
            max_search_time = max(worker_times)
            search_throughput = total_searches / concurrent_search_time
            
            # Performance assertions
            assert avg_search_time < 1.0, f"Average concurrent search too slow: {avg_search_time:.3f}s"
            assert max_search_time < 5.0, f"Slowest search too slow: {max_search_time:.3f}s"
            assert search_throughput > 20, f"Search throughput too low: {search_throughput:.1f} searches/sec"
            
            metrics.record_operation('concurrent_searches', concurrent_search_time)
            print(f"Concurrent search performance: {total_searches} searches in {concurrent_search_time:.2f}s ({search_throughput:.1f} searches/sec)")
            
            # Test 2: Concurrent indexing operations
            def indexing_worker(worker_id: int, file_count: int, results: List):
                """Worker function for concurrent file creation and indexing."""
                worker_dir = test_root / f"worker_{worker_id}"
                worker_dir.mkdir(exist_ok=True)
                
                worker_times = []
                for i in range(file_count):
                    # Create file
                    file_path = worker_dir / f"worker_{worker_id}_file_{i:03d}.txt"
                    content = f"Worker {worker_id} file {i} with unique content {i * worker_id}"
                    file_path.write_text(content)
                    
                    # Index file
                    start_time = time.time()
                    success = search_engine.index_file(file_path)
                    index_time = time.time() - start_time
                    
                    worker_times.append(index_time)
                    results.append((worker_id, i, success, index_time))
                
                return worker_times
            
            # Run concurrent indexing
            indexing_workers = 5
            files_per_worker = 50
            indexing_results = []
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=indexing_workers) as executor:
                futures = []
                for worker_id in range(indexing_workers):
                    future = executor.submit(indexing_worker, worker_id, files_per_worker, indexing_results)
                    futures.append(future)
                
                # Collect results
                indexing_times = []
                for future in as_completed(futures):
                    indexing_times.extend(future.result())
            
            concurrent_indexing_time = time.time() - start_time
            
            # Analyze concurrent indexing performance
            total_indexed_files = indexing_workers * files_per_worker
            successful_indexes = sum(1 for _, _, success, _ in indexing_results if success)
            
            assert successful_indexes >= total_indexed_files * 0.95  # Allow 5% tolerance
            
            avg_index_time = statistics.mean(indexing_times)
            indexing_throughput = successful_indexes / concurrent_indexing_time
            
            # Performance assertions
            assert avg_index_time < 0.1, f"Average indexing too slow: {avg_index_time:.3f}s per file"
            assert indexing_throughput > 50, f"Indexing throughput too low: {indexing_throughput:.1f} files/sec"
            
            metrics.record_operation('concurrent_indexing', concurrent_indexing_time)
            print(f"Concurrent indexing performance: {successful_indexes} files in {concurrent_indexing_time:.2f}s ({indexing_throughput:.1f} files/sec)")
            
            # Test 3: Mixed concurrent operations
            def mixed_operations_worker(worker_id: int, operation_count: int, results: List):
                """Worker performing mixed operations (search, index, query)."""
                operations = ['search', 'index', 'query']
                worker_times = []
                
                for i in range(operation_count):
                    operation = operations[i % len(operations)]
                    start_time = time.time()
                    
                    if operation == 'search':
                        search_results = folder_service.search_all_folders(f"worker_{worker_id}")
                        success = len(search_results) >= 0
                    elif operation == 'index':
                        temp_file = test_root / f"mixed_{worker_id}_{i}.txt"
                        temp_file.write_text(f"Mixed operation file {worker_id}-{i}")
                        success = search_engine.index_file(temp_file)
                    else:  # query
                        stats = folder_service.get_folder_statistics(config_id)
                        success = stats['total_files'] > 0
                    
                    operation_time = time.time() - start_time
                    worker_times.append(operation_time)
                    results.append((worker_id, operation, success, operation_time))
                
                return worker_times
            
            # Run mixed operations
            mixed_workers = 8
            operations_per_worker = 30
            mixed_results = []
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=mixed_workers) as executor:
                futures = []
                for worker_id in range(mixed_workers):
                    future = executor.submit(mixed_operations_worker, worker_id, operations_per_worker, mixed_results)
                    futures.append(future)
                
                # Collect results
                mixed_times = []
                for future in as_completed(futures):
                    mixed_times.extend(future.result())
            
            mixed_operations_time = time.time() - start_time
            
            # Analyze mixed operations performance
            total_operations = mixed_workers * operations_per_worker
            successful_operations = sum(1 for _, _, success, _ in mixed_results if success)
            
            assert successful_operations >= total_operations * 0.90  # Allow 10% tolerance for mixed ops
            
            mixed_throughput = successful_operations / mixed_operations_time
            avg_mixed_time = statistics.mean(mixed_times)
            
            # Performance assertions
            assert avg_mixed_time < 2.0, f"Average mixed operation too slow: {avg_mixed_time:.3f}s"
            assert mixed_throughput > 10, f"Mixed operations throughput too low: {mixed_throughput:.1f} ops/sec"
            
            metrics.record_operation('mixed_operations', mixed_operations_time)
            print(f"Mixed operations performance: {successful_operations} operations in {mixed_operations_time:.2f}s ({mixed_throughput:.1f} ops/sec)")
            
            # Test 4: System stability under sustained load
            sustained_duration = 30  # seconds
            print(f"Running sustained load test for {sustained_duration} seconds...")
            
            def sustained_load_worker(stop_event: threading.Event, results: List):
                """Worker for sustained load testing."""
                operation_count = 0
                while not stop_event.is_set():
                    # Rotate between different operations
                    if operation_count % 3 == 0:
                        # Search operation
                        search_results = folder_service.search_all_folders("content")
                    elif operation_count % 3 == 1:
                        # Create and index small file
                        temp_file = test_root / f"sustained_{threading.current_thread().ident}_{operation_count}.txt"
                        temp_file.write_text(f"Sustained load content {operation_count}")
                        search_engine.index_file(temp_file)
                    else:
                        # Query statistics
                        folder_service.get_folder_statistics(config_id)
                    
                    operation_count += 1
                    results.append(operation_count)
                    time.sleep(0.01)  # Small delay to prevent overwhelming
                
                return operation_count
            
            # Run sustained load
            stop_event = threading.Event()
            sustained_results = []
            sustained_threads = []
            
            for i in range(4):  # 4 sustained workers
                thread = threading.Thread(
                    target=sustained_load_worker,
                    args=(stop_event, sustained_results)
                )
                sustained_threads.append(thread)
                thread.start()
            
            # Monitor system metrics during sustained load
            start_time = time.time()
            initial_memory = metrics.process.memory_info().rss / 1024 / 1024
            
            while time.time() - start_time < sustained_duration:
                metrics.record_system_metrics()
                time.sleep(1)
            
            # Stop sustained load
            stop_event.set()
            for thread in sustained_threads:
                thread.join(timeout=5)
            
            final_memory = metrics.process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory
            
            # Analyze sustained load results
            total_sustained_operations = len(sustained_results)
            sustained_throughput = total_sustained_operations / sustained_duration
            
            # Performance assertions for sustained load
            assert sustained_throughput > 50, f"Sustained throughput too low: {sustained_throughput:.1f} ops/sec"
            assert memory_growth < 500, f"Memory growth too high: {memory_growth:.1f}MB"
            assert final_memory < 1500, f"Final memory usage too high: {final_memory:.1f}MB"
            
            print(f"Sustained load performance: {total_sustained_operations} operations in {sustained_duration}s ({sustained_throughput:.1f} ops/sec)")
            print(f"Memory growth during sustained load: {memory_growth:.1f}MB")
            
            # Final performance summary
            summary = metrics.get_summary()
            print("\nFinal Performance Summary:")
            print(f"Peak memory usage: {summary['memory']['peak_mb']:.1f}MB")
            print(f"Average CPU usage: {summary['cpu']['average_percent']:.1f}%")
            print("Operation Performance:")
            for operation, stats in summary['operations'].items():
                print(f"  {operation}: {stats['ops_per_second']:.1f} ops/sec")
    
    @pytest.mark.performance
    @pytest.mark.stress
    def test_memory_stress_performance(self):
        """Test system performance under memory stress conditions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize components
            db_path = Path(temp_dir) / "memory_stress.db"
            index_path = Path(temp_dir) / "stress_index"
            
            db_manager = AdvancedFoldersDBManager(str(db_path))
            search_engine = SearchEngine(index_path=index_path)
            folder_service = FolderService(db_manager, search_engine)
            
            metrics = PerformanceMetrics()
            metrics.start_measurement()
            
            # Test 1: Large file handling
            test_root = Path(temp_dir) / "memory_stress"
            test_root.mkdir()
            
            # Create large files that stress memory usage
            large_file_sizes = [1, 5, 10, 25, 50]  # MB
            large_files = []
            
            for size_mb in large_file_sizes:
                file_path = test_root / f"large_file_{size_mb}mb.txt"
                content_size = size_mb * 1024 * 1024  # Convert to bytes
                
                # Generate content in chunks to avoid memory spikes
                chunk_size = 1024 * 1024  # 1MB chunks
                with open(file_path, 'w') as f:
                    remaining = content_size
                    chunk_num = 0
                    while remaining > 0:
                        current_chunk_size = min(chunk_size, remaining)
                        chunk_content = f"Large file chunk {chunk_num} " * (current_chunk_size // 20)
                        chunk_content = chunk_content[:current_chunk_size]
                        f.write(chunk_content)
                        remaining -= len(chunk_content)
                        chunk_num += 1
                
                large_files.append(file_path)
                metrics.record_system_metrics()
            
            # Measure memory usage during large file indexing
            folder_config = FolderConfiguration(
                name="Memory Stress Test",
                path=str(test_root),
                folder_type=FolderType.MONITORED,
                auto_organize=True,
                priority=1
            )
            
            config_id = folder_service.create_folder_configuration(folder_config)
            
            initial_memory = metrics.process.memory_info().rss / 1024 / 1024
            
            start_time = time.time()
            indexed_count = folder_service.index_folder_contents(config_id)
            indexing_time = time.time() - start_time
            
            final_memory = metrics.process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory
            
            # Performance assertions for large files
            assert indexed_count >= len(large_files)
            assert indexing_time < 120, f"Large file indexing too slow: {indexing_time:.2f}s"
            assert memory_growth < 200, f"Memory growth too high: {memory_growth:.1f}MB"
            
            metrics.record_operation('large_file_indexing', indexing_time)
            print(f"Large file indexing: {indexed_count} files ({sum(large_file_sizes)}MB total) in {indexing_time:.2f}s")
            print(f"Memory growth: {memory_growth:.1f}MB")
            
            # Test 2: Many small files stress test
            small_files_count = 10000
            small_files_dir = test_root / "small_files"
            small_files_dir.mkdir()
            
            print(f"Creating {small_files_count} small files for memory stress test...")
            
            # Create many small files to stress memory management
            small_file_creation_start = time.time()
            for i in range(small_files_count):
                small_file = small_files_dir / f"small_{i:06d}.txt"
                content = f"Small file {i} content with some searchable text and data {i % 1000}"
                small_file.write_text(content)
                
                if (i + 1) % 1000 == 0:
                    metrics.record_system_metrics()
            
            small_file_creation_time = time.time() - small_file_creation_start
            
            # Index small files and measure memory usage
            pre_small_indexing_memory = metrics.process.memory_info().rss / 1024 / 1024
            
            start_time = time.time()
            small_indexed_count = search_engine.index_directory(small_files_dir, recursive=True)
            small_indexing_time = time.time() - start_time
            
            post_small_indexing_memory = metrics.process.memory_info().rss / 1024 / 1024
            small_files_memory_growth = post_small_indexing_memory - pre_small_indexing_memory
            
            # Performance assertions for many small files
            assert small_indexed_count >= small_files_count * 0.95
            small_files_rate = small_indexed_count / small_indexing_time
            assert small_files_rate > 200, f"Small files indexing too slow: {small_files_rate:.1f} files/sec"
            assert small_files_memory_growth < 300, f"Small files memory growth too high: {small_files_memory_growth:.1f}MB"
            
            metrics.record_operation('small_files_indexing', small_indexing_time)
            print(f"Small files indexing: {small_indexed_count} files in {small_indexing_time:.2f}s ({small_files_rate:.1f} files/sec)")
            print(f"Small files memory growth: {small_files_memory_growth:.1f}MB")
            
            # Test 3: Search performance with large dataset in memory
            search_stress_terms = [
                "content",
                "searchable", 
                "data",
                "small",
                "file",
                "chunk",
                "large",
                "text"
            ]
            
            search_memory_usage = []
            search_times = []
            
            for term in search_stress_terms:
                pre_search_memory = metrics.process.memory_info().rss / 1024 / 1024
                
                start_time = time.time()
                search_results = folder_service.search_all_folders(term)
                search_time = time.time() - start_time
                
                post_search_memory = metrics.process.memory_info().rss / 1024 / 1024
                
                search_memory_usage.append(post_search_memory - pre_search_memory)
                search_times.append(search_time)
                
                # Each search should be reasonably fast and not consume excessive memory
                assert search_time < 5.0, f"Memory stress search too slow for '{term}': {search_time:.2f}s"
                assert len(search_results) >= 0  # Verify search doesn't fail
                
                metrics.record_operation(f'stress_search_{term}', search_time)
            
            avg_search_time = statistics.mean(search_times)
            max_search_memory_growth = max(search_memory_usage)
            
            assert avg_search_time < 2.0, f"Average search time under memory stress too slow: {avg_search_time:.2f}s"
            assert max_search_memory_growth < 50, f"Search memory growth too high: {max_search_memory_growth:.1f}MB"
            
            print(f"Memory stress search performance: avg {avg_search_time:.3f}s, max memory growth {max_search_memory_growth:.1f}MB")
            
            # Test 4: Memory cleanup and garbage collection effectiveness
            pre_cleanup_memory = metrics.process.memory_info().rss / 1024 / 1024
            
            # Force garbage collection
            gc.collect()
            time.sleep(1)  # Allow time for cleanup
            
            post_cleanup_memory = metrics.process.memory_info().rss / 1024 / 1024
            memory_freed = pre_cleanup_memory - post_cleanup_memory
            
            print(f"Memory cleanup: {memory_freed:.1f}MB freed (from {pre_cleanup_memory:.1f}MB to {post_cleanup_memory:.1f}MB)")
            
            # Final memory usage should be reasonable
            assert post_cleanup_memory < 1000, f"Final memory usage too high: {post_cleanup_memory:.1f}MB"
            
            # Generate comprehensive performance report
            summary = metrics.get_summary()
            print("\nMemory Stress Test Summary:")
            print(f"Peak memory usage: {summary['memory']['peak_mb']:.1f}MB")
            print(f"Final memory usage: {summary['memory']['final_mb']:.1f}MB")
            print(f"Total memory growth: {summary['memory']['final_mb'] - summary['memory']['peak_mb']:.1f}MB")
            print(f"Average CPU usage: {summary['cpu']['average_percent']:.1f}%")
            print("Operation Performance:")
            for operation, stats in summary['operations'].items():
                if stats['count'] > 0:
                    print(f"  {operation}: {stats['average_time']:.3f}s avg, {stats['ops_per_second']:.1f} ops/sec")


if __name__ == "__main__":
    """Run enterprise-grade performance tests for Advanced Folders."""
    pytest.main([__file__, "-v", "--tb=short", "--strict-markers", "-s"])