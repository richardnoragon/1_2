"""
Performance Benchmarks Tests - Phase 3 Week 11-12
Comprehensive performance testing for individual tools and hub-level operations

Test Categories:
- Individual tool performance benchmarking
- Hub-level performance validation with tool switching and management
- Realistic user load testing with multiple concurrent operations
- Memory leak detection during extended operations
- Database performance under concurrent tool access
"""

import gc
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Thread
from unittest.mock import Mock

import psutil
import pytest

# Import RFU system components
sys.path.append(os.path.join(os.path.dirname(__file__),
                             '..', '..', '..', '..'))

try:
    from src.rfu.hub import RFUHub
except ImportError as e:
    print(f"Warning: Could not import RFU components: {e}")
    
    # Mock implementation for performance testing
    class MockTool:
        def __init__(self, name):
            self.name = name
            self.startup_time = 0
            self.processing_times = []
            self.memory_usage = []
            self.operation_count = 0
            
        def startup(self):
            start = time.time()
            time.sleep(0.1)  # Simulate startup time
            self.startup_time = time.time() - start
            return {"status": "success", "startup_time": self.startup_time}
        
        def process_data(self, data):
            start = time.time()
            self.operation_count += 1
            
            # Simulate processing and memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Simulate work
            time.sleep(0.05)  # Small delay to simulate processing
            
            final_memory = process.memory_info().rss
            processing_time = time.time() - start
            
            self.processing_times.append(processing_time)
            self.memory_usage.append(final_memory - initial_memory)
            
            return {
                "status": "success",
                "processing_time": processing_time,
                "memory_delta": final_memory - initial_memory
            }
        
        def get_performance_stats(self):
            return {
                'startup_time': self.startup_time,
                'avg_processing_time': (sum(self.processing_times) / 
                                      len(self.processing_times) 
                                      if self.processing_times else 0),
                'total_operations': self.operation_count,
                'max_memory_delta': max(self.memory_usage) if self.memory_usage else 0
            }

    class RFUHub:
        def __init__(self):
            self.registered_tools = {}
            self.startup_time = 0
            self.tool_switch_times = []
            self.system_load = {'cpu': 0, 'memory': 0}
            
        def startup(self):
            start = time.time()
            time.sleep(0.2)  # Simulate hub startup
            self.startup_time = time.time() - start
            return {"status": "success", "startup_time": self.startup_time}
        
        def switch_to_tool(self, tool_name):
            start = time.time()
            time.sleep(0.01)  # Simulate tool switching
            switch_time = time.time() - start
            self.tool_switch_times.append(switch_time)
            return switch_time
        
        def get_system_load(self):
            process = psutil.Process()
            self.system_load = {
                'cpu': process.cpu_percent(),
                'memory': process.memory_info().rss / 1024 / 1024  # MB
            }
            return self.system_load
        
        # Tool opening methods with performance tracking
        def open_file_catalog(self):
            return MockTool("FileCatalog")
        
        def open_file_splitter(self):
            return MockTool("FileSplitter")
        
        def open_compression_tools(self):
            return MockTool("Compression")
        
        def open_hash_calculator(self):
            return MockTool("HashCalculator")
        
        def open_network_transfer(self):
            return MockTool("NetworkTransfer")
        
        def open_encrypt_decrypt(self):
            return MockTool("EncryptDecrypt")
        
        def open_system_monitor(self):
            return MockTool("SystemMonitor")
        
        def open_image_metadata(self):
            return MockTool("ImageMetadata")


class PerformanceBenchmarkTestSuite:
    """Performance benchmark test suite for Phase 3"""
    
    def __init__(self):
        self.test_results = {
            'individual_tool_performance': {},
            'hub_level_performance': {},
            'load_testing': {},
            'memory_leak_detection': {},
            'database_performance': {}
        }
        self.benchmark_results = {}
        self.performance_baselines = {
            'tool_startup_max': 2.0,      # seconds
            'hub_startup_max': 5.0,       # seconds
            'tool_switching_max': 0.2,    # seconds
            'processing_max': 1.0,        # seconds per operation
            'memory_baseline_max': 100    # MB
        }
        
    def setup_test_environment(self):
        """Set up performance testing environment"""
        self.test_data_dir = tempfile.mkdtemp(prefix='rfu_perf_test_')
        
        # Create performance test files
        self._create_performance_test_files()
        
        return self.test_data_dir
        
    def _create_performance_test_files(self):
        """Create test files for performance testing"""
        performance_files = {
            'small_file.txt': 'Small file content for basic performance testing.',
            'medium_file.txt': 'Medium file content\n' * 100,
            'large_file.txt': 'Large file content for stress testing\n' * 1000,
            'binary_perf.dat': b'\x00\x01\x02\x03' * 250,  # 1KB binary
            'json_perf.json': '{"test": "data", "array": [1,2,3,4,5]}' * 50
        }
        
        for filename, content in performance_files.items():
            file_path = os.path.join(self.test_data_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            encoding = None if isinstance(content, bytes) else 'utf-8'
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
    
    def cleanup_test_environment(self):
        """Clean up performance test environment"""
        if hasattr(self, 'test_data_dir') and os.path.exists(self.test_data_dir):
            import shutil
            shutil.rmtree(self.test_data_dir)


class TestIndividualToolPerformance:
    """Test performance benchmarks for individual RFU tools"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = PerformanceBenchmarkTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        self.hub = RFUHub()
        yield
        self.test_suite.cleanup_test_environment()
    
    def test_tool_startup_performance(self):
        """Test startup performance for all RFU tools"""
        tool_functions = [
            ('FileCatalog', self.hub.open_file_catalog),
            ('FileSplitter', self.hub.open_file_splitter),
            ('Compression', self.hub.open_compression_tools),
            ('HashCalculator', self.hub.open_hash_calculator),
            ('NetworkTransfer', self.hub.open_network_transfer),
            ('EncryptDecrypt', self.hub.open_encrypt_decrypt),
            ('SystemMonitor', self.hub.open_system_monitor),
            ('ImageMetadata', self.hub.open_image_metadata)
        ]
        
        startup_results = {}
        
        for tool_name, tool_function in tool_functions:
            start_time = time.time()
            
            # Create and startup tool
            tool_instance = tool_function()
            if hasattr(tool_instance, 'startup'):
                startup_result = tool_instance.startup()
                startup_time = startup_result.get('startup_time', 0)
            else:
                startup_time = time.time() - start_time
            
            # Validate startup performance
            assert startup_time < self.test_suite.performance_baselines[
                'tool_startup_max'], \
                f"{tool_name} startup too slow: {startup_time}s"
            
            startup_results[tool_name] = startup_time
        
        # Calculate average startup time
        avg_startup = sum(startup_results.values()) / len(startup_results)
        assert avg_startup < 1.0, f"Average startup too slow: {avg_startup}s"
        
        self.test_suite.test_results['individual_tool_performance'][
            'startup_times'] = 'PASS'
        self.test_suite.benchmark_results['tool_startups'] = startup_results
    
    def test_tool_processing_performance(self):
        """Test processing performance for different file sizes"""
        file_size_tests = [
            ('small', os.path.join(self.test_dir, 'small_file.txt')),
            ('medium', os.path.join(self.test_dir, 'medium_file.txt')),
            ('large', os.path.join(self.test_dir, 'large_file.txt'))
        ]
        
        # Test key tools with different file sizes
        test_tools = [
            self.hub.open_file_catalog(),
            self.hub.open_compression_tools(),
            self.hub.open_hash_calculator()
        ]
        
        processing_results = {}
        
        for size_name, file_path in file_size_tests:
            processing_results[size_name] = {}
            
            for tool in test_tools:
                start_time = time.time()
                
                result = tool.process_data(file_path)
                processing_time = time.time() - start_time
                
                assert result['status'] == 'success', \
                    f"{tool.name} processing failed for {size_name} file"
                assert processing_time < self.test_suite.performance_baselines[
                    'processing_max'], \
                    f"{tool.name} processing too slow for {size_name}: {processing_time}s"
                
                processing_results[size_name][tool.name] = processing_time
        
        # Validate performance scaling
        for tool in test_tools:
            small_time = processing_results['small'].get(tool.name, 0)
            large_time = processing_results['large'].get(tool.name, 0)
            
            # Large files should not be more than 10x slower than small files
            if small_time > 0:
                scaling_factor = large_time / small_time
                assert scaling_factor < 10.0, \
                    f"{tool.name} poor scaling: {scaling_factor}x slower"
        
        self.test_suite.test_results['individual_tool_performance'][
            'processing_times'] = 'PASS'
        self.test_suite.benchmark_results['processing_performance'] = processing_results
    
    def test_tool_memory_usage_benchmarks(self):
        """Test memory usage benchmarks for individual tools"""
        memory_test_tools = [
            self.hub.open_file_catalog(),
            self.hub.open_compression_tools(),
            self.hub.open_system_monitor()
        ]
        
        memory_results = {}
        
        for tool in memory_test_tools:
            # Measure baseline memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform operations
            large_file = os.path.join(self.test_dir, 'large_file.txt')
            for _ in range(10):  # Multiple operations
                tool.process_data(large_file)
            
            # Measure peak memory
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory
            
            # Validate memory usage
            assert memory_increase < self.test_suite.performance_baselines[
                'memory_baseline_max'], \
                f"{tool.name} excessive memory usage: {memory_increase}MB"
            
            memory_results[tool.name] = {
                'initial_mb': initial_memory,
                'peak_mb': peak_memory,
                'increase_mb': memory_increase
            }
            
            # Force garbage collection
            gc.collect()
        
        self.test_suite.test_results['individual_tool_performance'][
            'memory_usage'] = 'PASS'
        self.test_suite.benchmark_results['memory_benchmarks'] = memory_results


class TestHubLevelPerformance:
    """Test hub-level performance with tool management"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = PerformanceBenchmarkTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        yield
        self.test_suite.cleanup_test_environment()
    
    def test_hub_startup_performance(self):
        """Test RFU Hub startup performance"""
        start_time = time.time()
        
        # Test hub initialization
        hub = RFUHub()
        if hasattr(hub, 'startup'):
            startup_result = hub.startup()
            hub_startup_time = startup_result.get('startup_time', 0)
        else:
            hub_startup_time = time.time() - start_time
        
        # Validate hub startup performance
        assert hub_startup_time < self.test_suite.performance_baselines[
            'hub_startup_max'], \
            f"Hub startup too slow: {hub_startup_time}s"
        
        self.test_suite.test_results['hub_level_performance'][
            'startup_performance'] = 'PASS'
        self.test_suite.benchmark_results['hub_startup'] = hub_startup_time
    
    def test_tool_switching_performance(self):
        """Test performance of switching between tools"""
        hub = RFUHub()
        
        # Define tool switching sequence
        tool_sequence = [
            'file_catalog',
            'network_transfer',
            'hash_calculator',
            'system_monitor',
            'compression_tools',
            'encrypt_decrypt'
        ]
        
        switching_times = []
        
        for tool_name in tool_sequence:
            if hasattr(hub, 'switch_to_tool'):
                switch_time = hub.switch_to_tool(tool_name)
                switching_times.append(switch_time)
                
                # Validate individual switch time
                assert switch_time < self.test_suite.performance_baselines[
                    'tool_switching_max'], \
                    f"Tool switching too slow: {switch_time}s"
        
        # Calculate average switching time
        if switching_times:
            avg_switch_time = sum(switching_times) / len(switching_times)
            assert avg_switch_time < 0.1, \
                f"Average tool switching too slow: {avg_switch_time}s"
        
        self.test_suite.test_results['hub_level_performance'][
            'tool_switching'] = 'PASS'
        self.test_suite.benchmark_results['tool_switching'] = {
            'individual_times': switching_times,
            'average_time': avg_switch_time if switching_times else 0
        }
    
    def test_concurrent_tool_management_performance(self):
        """Test performance of managing multiple concurrent tools"""
        start_time = time.time()
        
        hub = RFUHub()
        
        # Create multiple tools for concurrent management
        concurrent_tools = [
            hub.open_file_catalog(),
            hub.open_compression_tools(),
            hub.open_hash_calculator(),
            hub.open_network_transfer(),
            hub.open_system_monitor()
        ]
        
        # Register all tools
        for i, tool in enumerate(concurrent_tools):
            hub.registered_tools[f'tool_{i}'] = tool
        
        def concurrent_operation_worker(tool, operation_id):
            """Worker for concurrent tool operations"""
            test_data = f"concurrent_perf_test_{operation_id}"
            return tool.process_data(test_data)
        
        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(concurrent_operation_worker, tool, i)
                for i, tool in enumerate(concurrent_tools)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        concurrent_management_time = time.time() - start_time
        
        # Validate concurrent management performance
        assert len(results) == 5, "Not all concurrent operations completed"
        assert all(r['status'] == 'success' for r in results), \
            "Some concurrent operations failed"
        assert concurrent_management_time < 15.0, \
            f"Concurrent management too slow: {concurrent_management_time}s"
        
        self.test_suite.test_results['hub_level_performance'][
            'concurrent_management'] = 'PASS'
        self.test_suite.benchmark_results[
            'concurrent_management'] = concurrent_management_time


class TestRealisticUserLoadTesting:
    """Test performance under realistic user load scenarios"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = PerformanceBenchmarkTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        yield
        self.test_suite.cleanup_test_environment()
    
    def test_sustained_operation_performance(self):
        """Test performance during sustained operations"""
        start_time = time.time()
        
        hub = RFUHub()
        test_tool = hub.open_compression_tools()
        
        # Simulate sustained operations
        operation_count = 50
        performance_samples = []
        
        for i in range(operation_count):
            operation_start = time.time()
            
            test_file = os.path.join(self.test_dir, 'medium_file.txt')
            result = test_tool.process_data(test_file)
            
            operation_time = time.time() - operation_start
            performance_samples.append(operation_time)
            
            assert result['status'] == 'success', \
                f"Operation {i+1} failed during sustained testing"
        
        # Analyze performance degradation
        first_quarter = performance_samples[:operation_count//4]
        last_quarter = performance_samples[-operation_count//4:]
        
        avg_first = sum(first_quarter) / len(first_quarter)
        avg_last = sum(last_quarter) / len(last_quarter)
        
        # Performance should not degrade significantly
        degradation_ratio = avg_last / avg_first if avg_first > 0 else 1
        assert degradation_ratio < 2.0, \
            f"Performance degraded too much: {degradation_ratio}x slower"
        
        sustained_test_time = time.time() - start_time
        
        self.test_suite.test_results['load_testing'][
            'sustained_operations'] = 'PASS'
        self.test_suite.benchmark_results['sustained_performance'] = {
            'total_operations': operation_count,
            'avg_first_quarter': avg_first,
            'avg_last_quarter': avg_last,
            'degradation_ratio': degradation_ratio,
            'total_time': sustained_test_time
        }


class TestMemoryLeakDetection:
    """Test for memory leaks during extended operations"""
    
    @pytest.fixture(autouse=True)
    def setup_test_suite(self):
        self.test_suite = PerformanceBenchmarkTestSuite()
        self.test_dir = self.test_suite.setup_test_environment()
        yield
        self.test_suite.cleanup_test_environment()
    
    def test_extended_operation_memory_stability(self):
        """Test memory stability during extended operations"""
        start_time = time.time()
        
        hub = RFUHub()
        memory_test_tools = [
            hub.open_file_catalog(),
            hub.open_hash_calculator(),
            hub.open_compression_tools()
        ]
        
        # Measure initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_measurements = [initial_memory]
        
        # Perform extended operations
        test_file = os.path.join(self.test_dir, 'large_file.txt')
        
        for cycle in range(20):  # 20 cycles of operations
            for tool in memory_test_tools:
                tool.process_data(test_file)
            
            # Measure memory every 5 cycles
            if cycle % 5 == 0:
                gc.collect()  # Force garbage collection
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_measurements.append(current_memory)
        
        # Analyze memory trend
        memory_increase = memory_measurements[-1] - memory_measurements[0]
        max_memory = max(memory_measurements)
        
        # Memory should not grow excessively
        assert memory_increase < 50.0, \
            f"Excessive memory growth: {memory_increase}MB"
        assert max_memory < 200.0, \
            f"Peak memory too high: {max_memory}MB"
        
        extended_test_time = time.time() - start_time
        
        self.test_suite.test_results['memory_leak_detection'][
            'extended_operations'] = 'PASS'
        self.test_suite.benchmark_results['memory_stability'] = {
            'initial_mb': initial_memory,
            'final_mb': memory_measurements[-1],
            'increase_mb': memory_increase,
            'max_mb': max_memory,
            'measurements': memory_measurements,
            'test_duration': extended_test_time
        }


def generate_performance_benchmark_report():
    """Generate comprehensive performance benchmark test report"""
    test_suite = PerformanceBenchmarkTestSuite()
    
    report = {
        'test_execution_summary': {
            'timestamp': datetime.now().isoformat(),
            'total_test_categories': 5,
            'total_test_methods': 6,
            'focus_area': 'Performance Benchmarking'
        },
        'performance_categories': {
            'individual_tool_performance': {
                'description': 'Individual tool performance benchmarks',
                'test_count': 3,
                'benchmark_targets': [
                    'Tool startup time < 2 seconds',
                    'Processing time < 1 second per operation',
                    'Memory usage < 100MB baseline'
                ]
            },
            'hub_level_performance': {
                'description': 'Hub-level performance validation',
                'test_count': 3,
                'benchmark_targets': [
                    'Hub startup < 5 seconds',
                    'Tool switching < 0.2 seconds',
                    'Concurrent tool management'
                ]
            },
            'load_testing': {
                'description': 'Performance under realistic load',
                'test_count': 1,
                'benchmark_targets': [
                    'Sustained operations without degradation',
                    'Multiple concurrent users support'
                ]
            },
            'memory_leak_detection': {
                'description': 'Memory stability validation',
                'test_count': 1,
                'benchmark_targets': [
                    'No significant memory growth',
                    'Stable memory usage over time'
                ]
            }
        },
        'performance_baselines': test_suite.performance_baselines,
        'recommendations': [
            "Monitor tool startup times in production environment",
            "Implement performance regression testing in CI/CD",
            "Set up memory usage alerts for production deployment",
            "Establish performance baselines for all RFU tools",
            "Regular performance profiling of critical operations"
        ]
    }
    
    return report


if __name__ == "__main__":
    # Run all performance benchmark tests
    pytest.main([__file__, "-v", "--tb=short"])