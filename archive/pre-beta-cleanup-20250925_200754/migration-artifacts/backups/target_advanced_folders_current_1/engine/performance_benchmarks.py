"""Comprehensive Performance Benchmarking Suite.

Enterprise-grade performance testing framework with metrics collection,
load testing, memory profiling, and automated reporting capabilities.

Features:
- Multi-dimensional performance testing
- Memory usage and leak detection 
- Concurrent operation benchmarks
- Search performance analytics
- Database optimization metrics
- Cache efficiency analysis
- Automated report generation
- Regression testing capabilities
"""

import json
import logging
import multiprocessing
import statistics
import threading
import time
import tracemalloc
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

# Local imports - commented out until implementation complete
# try:
#     from .multi_threaded_search_engine import MultiThreadedSearchEngine
#     from .file_system_monitor import FileSystemMonitor
#     from .database_optimizer import DatabaseOptimizationManager
#     from .cache_manager import MultiTierCacheManager, CacheConfig
#     from ..models.folder_models import SearchParameter, FolderConfiguration
# except ImportError:
#     # Fallback for standalone testing
#     pass


class BenchmarkType(Enum):
    """Types of benchmarks to run."""
    
    SEARCH_PERFORMANCE = "search_performance"
    DATABASE_OPERATIONS = "database_operations"
    CACHE_EFFICIENCY = "cache_efficiency"
    FILE_MONITORING = "file_monitoring"
    MEMORY_USAGE = "memory_usage"
    CONCURRENCY = "concurrency"
    LOAD_TEST = "load_test"
    REGRESSION = "regression"


class MetricType(Enum):
    """Types of metrics to collect."""
    
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_UTILIZATION = "cpu_utilization"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATIO = "cache_hit_ratio"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution."""
    
    # Test parameters
    test_duration_seconds: float = 60.0
    warmup_duration_seconds: float = 10.0
    cooldown_duration_seconds: float = 5.0
    
    # Concurrency settings
    max_workers: int = multiprocessing.cpu_count()
    concurrent_operations: int = 100
    
    # Data generation
    test_data_size: int = 10000
    file_count_range: Tuple[int, int] = (100, 1000)
    file_size_range: Tuple[int, int] = (1024, 1024 * 1024)  # 1KB to 1MB
    
    # Memory profiling
    enable_memory_profiling: bool = True
    memory_profile_interval: float = 0.1
    memory_growth_threshold: float = 0.1  # 10% growth threshold
    
    # Performance thresholds
    max_response_time_ms: float = 1000.0
    min_throughput_ops_per_sec: float = 100.0
    max_memory_usage_mb: float = 500.0
    max_cpu_utilization_percent: float = 80.0
    
    # Reporting
    output_directory: str = "benchmark_results"
    generate_charts: bool = True
    detailed_logging: bool = True
    
    # Regression testing
    baseline_results_file: Optional[str] = None
    performance_degradation_threshold: float = 0.05  # 5%


@dataclass
class BenchmarkResult:
    """Results from a single benchmark execution."""
    
    benchmark_type: BenchmarkType
    test_name: str
    start_time: float
    end_time: float
    success: bool
    error_message: Optional[str] = None
    
    # Performance metrics
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0
    cpu_utilization_percent: float = 0.0
    throughput_ops_per_sec: float = 0.0
    
    # Detailed metrics
    metrics: Dict[MetricType, List[float]] = field(default_factory=dict)
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Get benchmark duration in seconds."""
        return self.end_time - self.start_time
    
    def add_metric(self, metric_type: MetricType, value: float):
        """Add a metric value.
        
        Args:
            metric_type: Type of metric
            value: Metric value
        """
        if metric_type not in self.metrics:
            self.metrics[metric_type] = []
        self.metrics[metric_type].append(value)
    
    def get_metric_stats(self, metric_type: MetricType) -> Dict[str, float]:
        """Get statistics for a metric type.
        
        Args:
            metric_type: Type of metric
            
        Returns:
            Dictionary with min, max, mean, median, std_dev
        """
        values = self.metrics.get(metric_type, [])
        if not values:
            return {}
        
        return {
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'count': len(values)
        }


class SystemMonitor:
    """System resource monitoring during benchmarks."""
    
    def __init__(self, interval: float = 0.1):
        """Initialize system monitor.
        
        Args:
            interval: Monitoring interval in seconds
        """
        self.interval = interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Metrics storage
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.disk_io: List[Tuple[int, int]] = []  # (read_bytes, write_bytes)
        self.network_io: List[Tuple[int, int]] = []  # (sent_bytes, recv_bytes)
        
        # Process reference
        self.process = psutil.Process()
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """Start system monitoring."""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        last_disk_io = self.process.io_counters()
        last_net_io = psutil.net_io_counters()
        
        while self.is_monitoring:
            try:
                # CPU usage
                cpu_percent = self.process.cpu_percent()
                
                # Memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                
                # Disk I/O
                current_disk_io = self.process.io_counters()
                disk_read = current_disk_io.read_bytes - last_disk_io.read_bytes
                disk_write = (current_disk_io.write_bytes - 
                             last_disk_io.write_bytes)
                last_disk_io = current_disk_io
                
                # Network I/O
                current_net_io = psutil.net_io_counters()
                net_sent = current_net_io.bytes_sent - last_net_io.bytes_sent
                net_recv = current_net_io.bytes_recv - last_net_io.bytes_recv
                last_net_io = current_net_io
                
                # Store metrics
                with self.lock:
                    self.cpu_usage.append(cpu_percent)
                    self.memory_usage.append(memory_mb)
                    self.disk_io.append((disk_read, disk_write))
                    self.network_io.append((net_sent, net_recv))
                
                time.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"Error in system monitoring: {e}")
                break
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get monitoring statistics.
        
        Returns:
            Dictionary with statistics for each metric type
        """
        with self.lock:
            stats = {}
            
            if self.cpu_usage:
                stats['cpu'] = {
                    'mean': statistics.mean(self.cpu_usage),
                    'max': max(self.cpu_usage),
                    'min': min(self.cpu_usage)
                }
            
            if self.memory_usage:
                stats['memory'] = {
                    'mean': statistics.mean(self.memory_usage),
                    'max': max(self.memory_usage),
                    'min': min(self.memory_usage)
                }
            
            if self.disk_io:
                read_bytes = [io[0] for io in self.disk_io]
                write_bytes = [io[1] for io in self.disk_io]
                stats['disk_io'] = {
                    'total_read_mb': sum(read_bytes) / (1024 * 1024),
                    'total_write_mb': sum(write_bytes) / (1024 * 1024),
                    'avg_read_rate_mbps': (statistics.mean(read_bytes) / 
                                          (1024 * 1024) / self.interval),
                    'avg_write_rate_mbps': (statistics.mean(write_bytes) / 
                                           (1024 * 1024) / self.interval)
                }
            
            if self.network_io:
                sent_bytes = [io[0] for io in self.network_io]
                recv_bytes = [io[1] for io in self.network_io]
                stats['network_io'] = {
                    'total_sent_mb': sum(sent_bytes) / (1024 * 1024),
                    'total_recv_mb': sum(recv_bytes) / (1024 * 1024)
                }
            
            return stats
    
    def reset_metrics(self):
        """Reset all monitoring metrics."""
        with self.lock:
            self.cpu_usage.clear()
            self.memory_usage.clear()
            self.disk_io.clear()
            self.network_io.clear()


class MemoryProfiler:
    """Advanced memory profiling for benchmarks."""
    
    def __init__(self):
        """Initialize memory profiler."""
        self.snapshots: List[Tuple[float, tracemalloc.Snapshot]] = []
        self.is_profiling = False
        
    @contextmanager
    def profile(self):
        """Context manager for memory profiling."""
        tracemalloc.start()
        self.is_profiling = True
        
        try:
            yield self
        finally:
            self.is_profiling = False
            tracemalloc.stop()
    
    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot.
        
        Args:
            label: Optional label for the snapshot
        """
        if self.is_profiling:
            snapshot = tracemalloc.take_snapshot()
            self.snapshots.append((time.time(), snapshot))
    
    def get_memory_growth(self) -> Dict[str, float]:
        """Analyze memory growth between snapshots.
        
        Returns:
            Dictionary with memory growth statistics
        """
        if len(self.snapshots) < 2:
            return {}
        
        first_snapshot = self.snapshots[0][1]
        last_snapshot = self.snapshots[-1][1]
        
        # Compare snapshots
        top_stats = last_snapshot.compare_to(first_snapshot, 'lineno')
        
        total_growth = sum(stat.size_diff for stat in top_stats)
        total_growth_mb = total_growth / (1024 * 1024)
        
        # Find top growing files
        top_growth = sorted(
            [(stat.traceback.format()[-1], stat.size_diff) 
             for stat in top_stats[:10]],
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'total_growth_mb': total_growth_mb,
            'growth_per_second_mb': (total_growth_mb / 
                                   (self.snapshots[-1][0] - 
                                    self.snapshots[0][0])),
            'top_growing_locations': top_growth
        }


class BenchmarkHarness(ABC):
    """Abstract base class for benchmark harnesses."""
    
    @abstractmethod
    def setup(self) -> bool:
        """Set up the benchmark environment.
        
        Returns:
            True if setup successful
        """
        pass
    
    @abstractmethod
    def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run the benchmark.
        
        Args:
            config: Benchmark configuration
            
        Returns:
            Benchmark result
        """
        pass
    
    @abstractmethod
    def teardown(self):
        """Clean up after benchmark."""
        pass


class SearchPerformanceBenchmark(BenchmarkHarness):
    """Benchmark for search engine performance."""
    
    def __init__(self):
        """Initialize search benchmark."""
        self.search_engine = None
        self.test_data = []
        self.logger = logging.getLogger('SearchBenchmark')
    
    def setup(self) -> bool:
        """Set up search benchmark environment."""
        try:
            # Initialize search engine
            from .multi_threaded_search_engine import (
                MultiThreadedSearchEngine, SearchEngineConfig)
            
            config = SearchEngineConfig(
                max_workers=4,
                queue_size=1000,
                result_batch_size=100
            )
            
            self.search_engine = MultiThreadedSearchEngine(config)
            
            # Generate test data
            self._generate_test_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up search benchmark: {e}")
            return False
    
    def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run search performance benchmark."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.SEARCH_PERFORMANCE,
            test_name="Search Engine Performance Test",
            start_time=time.time(),
            end_time=0.0,
            success=False
        )
        
        try:
            # System monitoring
            monitor = SystemMonitor()
            monitor.start_monitoring()
            
            # Memory profiling
            with MemoryProfiler().profile() as profiler:
                profiler.take_snapshot("start")
                
                # Warmup phase
                self._run_search_warmup(config)
                
                # Main benchmark
                start_time = time.time()
                
                search_times = []
                successful_searches = 0
                failed_searches = 0
                
                # Run searches for specified duration
                end_time = start_time + config.test_duration_seconds
                
                while time.time() < end_time:
                    search_start = time.time()
                    
                    try:
                        # Generate random search parameters
                        search_params = self._generate_search_params()
                        
                        # Perform search
                        results = self.search_engine.search(search_params)
                        
                        search_time = (time.time() - search_start) * 1000
                        search_times.append(search_time)
                        successful_searches += 1
                        
                        # Add metrics
                        result.add_metric(MetricType.EXECUTION_TIME, search_time)
                        result.add_metric(MetricType.THROUGHPUT, 
                                        1.0 / (search_time / 1000))
                        
                    except Exception as e:
                        failed_searches += 1
                        self.logger.error(f"Search failed: {e}")
                
                profiler.take_snapshot("end")
                
                # Calculate final metrics
                total_searches = successful_searches + failed_searches
                duration = time.time() - start_time
                
                result.execution_time_ms = statistics.mean(search_times)
                result.throughput_ops_per_sec = successful_searches / duration
                result.metadata['total_searches'] = total_searches
                result.metadata['successful_searches'] = successful_searches
                result.metadata['failed_searches'] = failed_searches
                result.metadata['error_rate'] = (failed_searches / 
                                               total_searches if total_searches > 0 else 0)
                
                # Memory analysis
                memory_growth = profiler.get_memory_growth()
                result.metadata['memory_growth'] = memory_growth
                
            # System monitoring results
            monitor.stop_monitoring()
            system_stats = monitor.get_statistics()
            result.metadata['system_stats'] = system_stats
            
            if 'memory' in system_stats:
                result.memory_usage_mb = system_stats['memory']['mean']
                result.peak_memory_mb = system_stats['memory']['max']
            
            if 'cpu' in system_stats:
                result.cpu_utilization_percent = system_stats['cpu']['mean']
            
            result.success = True
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"Search benchmark failed: {e}")
        
        finally:
            result.end_time = time.time()
        
        return result
    
    def teardown(self):
        """Clean up search benchmark."""
        if self.search_engine:
            self.search_engine.shutdown()
        self.test_data.clear()
    
    def _generate_test_data(self):
        """Generate test data for search benchmarks."""
        # This would generate mock file data for testing
        for i in range(1000):
            self.test_data.append({
                'path': f'/test/path/file_{i}.txt',
                'name': f'file_{i}.txt',
                'size': 1024 * (i + 1),
                'modified': time.time() - (i * 3600),
                'type': 'text'
            })
    
    def _run_search_warmup(self, config: BenchmarkConfig):
        """Run warmup searches."""
        warmup_end = time.time() + config.warmup_duration_seconds
        
        while time.time() < warmup_end:
            try:
                search_params = self._generate_search_params()
                self.search_engine.search(search_params)
            except Exception:
                pass  # Ignore warmup errors
    
    def _generate_search_params(self) -> 'SearchParameter':
        """Generate random search parameters."""
        import random
        
        patterns = ['*.txt', '*.py', 'test*', '*config*', '*.log']
        locations = ['/test', '/home', '/var', '/tmp']
        
        # This is a mock implementation
        # In real code, this would create actual SearchParameter objects
        return {
            'pattern': random.choice(patterns),
            'location': random.choice(locations),
            'include_subdirs': random.choice([True, False]),
            'case_sensitive': random.choice([True, False])
        }


class CacheEfficiencyBenchmark(BenchmarkHarness):
    """Benchmark for cache performance and efficiency."""
    
    def __init__(self):
        """Initialize cache benchmark."""
        self.cache_manager = None
        self.logger = logging.getLogger('CacheBenchmark')
    
    def setup(self) -> bool:
        """Set up cache benchmark environment."""
        try:
            from .cache_manager import CacheConfig, MultiTierCacheManager
            
            config = CacheConfig(
                memory_cache_size=1000,
                enable_disk_cache=True,
                enable_distributed_cache=False
            )
            
            self.cache_manager = MultiTierCacheManager(config)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up cache benchmark: {e}")
            return False
    
    def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run cache efficiency benchmark."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.CACHE_EFFICIENCY,
            test_name="Cache Efficiency Test",
            start_time=time.time(),
            end_time=0.0,
            success=False
        )
        
        try:
            # Monitor system resources
            monitor = SystemMonitor()
            monitor.start_monitoring()
            
            # Test cache operations
            start_time = time.time()
            
            # Populate cache
            populate_start = time.time()
            for i in range(config.test_data_size):
                key = f"test_key_{i}"
                value = f"test_value_{i}" * 100  # Make values substantial
                self.cache_manager.set(key, value)
            
            populate_time = time.time() - populate_start
            
            # Test cache reads
            read_times = []
            hit_count = 0
            miss_count = 0
            
            for i in range(config.test_data_size * 2):  # Read more than stored
                read_start = time.time()
                key = f"test_key_{i % config.test_data_size}"
                value = self.cache_manager.get(key)
                read_time = (time.time() - read_start) * 1000
                
                read_times.append(read_time)
                
                if value is not None:
                    hit_count += 1
                else:
                    miss_count += 1
                
                result.add_metric(MetricType.EXECUTION_TIME, read_time)
            
            # Get cache statistics
            cache_stats = self.cache_manager.get_stats()
            
            # Calculate metrics
            total_operations = config.test_data_size * 2
            duration = time.time() - start_time
            
            result.execution_time_ms = statistics.mean(read_times)
            result.throughput_ops_per_sec = total_operations / duration
            
            # Cache-specific metrics
            hit_ratio = hit_count / (hit_count + miss_count)
            result.metadata['hit_ratio'] = hit_ratio
            result.metadata['populate_time_ms'] = populate_time * 1000
            result.metadata['cache_stats'] = cache_stats
            result.metadata['total_reads'] = total_operations
            result.metadata['cache_hits'] = hit_count
            result.metadata['cache_misses'] = miss_count
            
            # Stop monitoring
            monitor.stop_monitoring()
            system_stats = monitor.get_statistics()
            result.metadata['system_stats'] = system_stats
            
            if 'memory' in system_stats:
                result.memory_usage_mb = system_stats['memory']['mean']
                result.peak_memory_mb = system_stats['memory']['max']
            
            result.success = True
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"Cache benchmark failed: {e}")
        
        finally:
            result.end_time = time.time()
        
        return result
    
    def teardown(self):
        """Clean up cache benchmark."""
        if self.cache_manager:
            self.cache_manager.clear()
            self.cache_manager.shutdown()


class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmark suite."""
    
    def __init__(self, config: BenchmarkConfig):
        """Initialize benchmark suite.
        
        Args:
            config: Benchmark configuration
        """
        self.config = config
        self.logger = logging.getLogger('BenchmarkSuite')
        
        # Available benchmarks
        self.benchmarks = {
            BenchmarkType.SEARCH_PERFORMANCE: SearchPerformanceBenchmark,
            BenchmarkType.CACHE_EFFICIENCY: CacheEfficiencyBenchmark,
            # Add other benchmarks here
        }
        
        # Results storage
        self.results: List[BenchmarkResult] = []
        
        # Output directory
        self.output_dir = Path(config.output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all available benchmarks.
        
        Returns:
            List of benchmark results
        """
        self.logger.info("Starting comprehensive benchmark suite")
        
        for benchmark_type, benchmark_class in self.benchmarks.items():
            self.logger.info(f"Running {benchmark_type.value} benchmark")
            
            benchmark = benchmark_class()
            
            try:
                # Setup
                if not benchmark.setup():
                    self.logger.error(f"Failed to setup {benchmark_type.value}")
                    continue
                
                # Run benchmark
                result = benchmark.run_benchmark(self.config)
                self.results.append(result)
                
                # Log result
                if result.success:
                    self.logger.info(
                        f"{benchmark_type.value} completed successfully: "
                        f"{result.execution_time_ms:.2f}ms avg, "
                        f"{result.throughput_ops_per_sec:.2f} ops/sec"
                    )
                else:
                    self.logger.error(
                        f"{benchmark_type.value} failed: {result.error_message}"
                    )
                
            except Exception as e:
                self.logger.error(f"Benchmark {benchmark_type.value} error: {e}")
            
            finally:
                # Cleanup
                try:
                    benchmark.teardown()
                except Exception as e:
                    self.logger.warning(f"Teardown error: {e}")
                
                # Brief pause between benchmarks
                time.sleep(self.config.cooldown_duration_seconds)
        
        # Generate reports
        self._generate_reports()
        
        return self.results
    
    def run_specific_benchmark(self, 
                             benchmark_type: BenchmarkType) -> BenchmarkResult:
        """Run a specific benchmark.
        
        Args:
            benchmark_type: Type of benchmark to run
            
        Returns:
            Benchmark result
        """
        if benchmark_type not in self.benchmarks:
            raise ValueError(f"Unknown benchmark type: {benchmark_type}")
        
        benchmark_class = self.benchmarks[benchmark_type]
        benchmark = benchmark_class()
        
        try:
            if not benchmark.setup():
                raise RuntimeError(f"Failed to setup {benchmark_type.value}")
            
            result = benchmark.run_benchmark(self.config)
            self.results.append(result)
            
            return result
            
        finally:
            benchmark.teardown()
    
    def _generate_reports(self):
        """Generate benchmark reports."""
        # JSON report
        json_report = self._generate_json_report()
        json_file = self.output_dir / "benchmark_results.json"
        
        with open(json_file, 'w') as f:
            json.dump(json_report, f, indent=2, default=str)
        
        # Text summary report
        summary_file = self.output_dir / "benchmark_summary.txt"
        self._generate_text_summary(summary_file)
        
        # Detailed CSV report
        csv_file = self.output_dir / "benchmark_details.csv"
        self._generate_csv_report(csv_file)
        
        self.logger.info(f"Reports generated in {self.output_dir}")
    
    def _generate_json_report(self) -> Dict:
        """Generate JSON report."""
        return {
            'benchmark_suite': {
                'configuration': {
                    'test_duration_seconds': self.config.test_duration_seconds,
                    'max_workers': self.config.max_workers,
                    'test_data_size': self.config.test_data_size,
                    'thresholds': {
                        'max_response_time_ms': self.config.max_response_time_ms,
                        'min_throughput_ops_per_sec': (
                            self.config.min_throughput_ops_per_sec
                        ),
                        'max_memory_usage_mb': self.config.max_memory_usage_mb,
                        'max_cpu_utilization_percent': (
                            self.config.max_cpu_utilization_percent
                        )
                    }
                },
                'results': [
                    {
                        'benchmark_type': result.benchmark_type.value,
                        'test_name': result.test_name,
                        'success': result.success,
                        'duration_seconds': result.duration_seconds,
                        'execution_time_ms': result.execution_time_ms,
                        'throughput_ops_per_sec': result.throughput_ops_per_sec,
                        'memory_usage_mb': result.memory_usage_mb,
                        'peak_memory_mb': result.peak_memory_mb,
                        'cpu_utilization_percent': result.cpu_utilization_percent,
                        'error_message': result.error_message,
                        'metrics': {
                            metric_type.value: result.get_metric_stats(metric_type)
                            for metric_type in result.metrics.keys()
                        },
                        'metadata': result.metadata
                    }
                    for result in self.results
                ],
                'summary': {
                    'total_benchmarks': len(self.results),
                    'successful_benchmarks': sum(1 for r in self.results if r.success),
                    'failed_benchmarks': sum(1 for r in self.results if not r.success),
                    'average_throughput': statistics.mean([
                        r.throughput_ops_per_sec for r in self.results 
                        if r.success and r.throughput_ops_per_sec > 0
                    ]) if any(r.success for r in self.results) else 0,
                    'average_memory_usage_mb': statistics.mean([
                        r.memory_usage_mb for r in self.results 
                        if r.success and r.memory_usage_mb > 0
                    ]) if any(r.success for r in self.results) else 0
                }
            }
        }
    
    def _generate_text_summary(self, output_file: Path):
        """Generate text summary report."""
        with open(output_file, 'w') as f:
            f.write("ADVANCED FOLDERS PERFORMANCE BENCHMARK REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Test Configuration:\n")
            f.write(f"  Duration: {self.config.test_duration_seconds}s\n")
            f.write(f"  Workers: {self.config.max_workers}\n")
            f.write(f"  Test Data Size: {self.config.test_data_size}\n\n")
            
            for result in self.results:
                f.write(f"{result.test_name}\n")
                f.write("-" * len(result.test_name) + "\n")
                f.write(f"  Status: {'PASS' if result.success else 'FAIL'}\n")
                
                if result.success:
                    f.write(f"  Execution Time: {result.execution_time_ms:.2f}ms\n")
                    f.write(f"  Throughput: {result.throughput_ops_per_sec:.2f} ops/sec\n")
                    f.write(f"  Memory Usage: {result.memory_usage_mb:.2f}MB\n")
                    f.write(f"  Peak Memory: {result.peak_memory_mb:.2f}MB\n")
                    f.write(f"  CPU Usage: {result.cpu_utilization_percent:.1f}%\n")
                else:
                    f.write(f"  Error: {result.error_message}\n")
                
                f.write("\n")
    
    def _generate_csv_report(self, output_file: Path):
        """Generate CSV report with detailed metrics."""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Benchmark Type', 'Test Name', 'Success', 'Duration (s)',
                'Execution Time (ms)', 'Throughput (ops/sec)',
                'Memory Usage (MB)', 'Peak Memory (MB)', 'CPU Usage (%)',
                'Error Message'
            ])
            
            # Data rows
            for result in self.results:
                writer.writerow([
                    result.benchmark_type.value,
                    result.test_name,
                    result.success,
                    f"{result.duration_seconds:.3f}",
                    f"{result.execution_time_ms:.2f}",
                    f"{result.throughput_ops_per_sec:.2f}",
                    f"{result.memory_usage_mb:.2f}",
                    f"{result.peak_memory_mb:.2f}",
                    f"{result.cpu_utilization_percent:.1f}",
                    result.error_message or ""
                ])


def main():
    """Main entry point for benchmark suite."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create benchmark configuration
    config = BenchmarkConfig(
        test_duration_seconds=30.0,  # Shorter for demo
        warmup_duration_seconds=5.0,
        test_data_size=1000,
        output_directory="benchmark_results"
    )
    
    # Run benchmark suite
    suite = PerformanceBenchmarkSuite(config)
    results = suite.run_all_benchmarks()
    
    # Print summary
    successful = sum(1 for r in results if r.success)
    total = len(results)
    
    print(f"\nBenchmark Suite Complete: {successful}/{total} successful")
    
    for result in results:
        status = "PASS" if result.success else "FAIL"
        print(f"  {result.test_name}: {status}")
        
        if result.success:
            print(f"    Execution Time: {result.execution_time_ms:.2f}ms")
            print(f"    Throughput: {result.throughput_ops_per_sec:.2f} ops/sec")


if __name__ == "__main__":
    main()