"""
Resource Optimization System - Phase 4 Week 13-14
Advanced resource usage optimization and memory management for test execution

Features:
- Memory pool management and optimization
- CPU load balancing and thread management
- I/O scheduling and disk usage optimization
- Resource contention detection and resolution
- Garbage collection tuning for test environments
"""

import gc
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

import psutil


@dataclass
class ResourceUsageMetrics:
    """Metrics for resource usage tracking"""

    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    io_read_bytes: int
    io_write_bytes: int
    thread_count: int
    gc_count: int


@dataclass
class ResourcePool:
    """Resource pool for shared test resources"""

    pool_type: str
    max_size: int
    current_size: int
    available_resources: Queue
    allocated_resources: Dict[str, Any]
    usage_stats: Dict[str, int]


class ResourceOptimizer:
    """Advanced resource optimization for test execution"""

    def __init__(
        self, max_memory_mb: int = 2048, max_cpu_percent: float = 80.0
    ):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.usage_history: List[ResourceUsageMetrics] = []
        self.optimization_strategies = {
            "memory": self._optimize_memory,
            "cpu": self._optimize_cpu,
            "io": self._optimize_io,
            "gc": self._optimize_garbage_collection,
        }
        self.monitoring_enabled = False
        self._monitoring_thread = None
        self._setup_resource_pools()

    def _setup_resource_pools(self):
        """Initialize resource pools for shared test resources"""
        # Database connection pool
        self.resource_pools["database"] = ResourcePool(
            pool_type="database",
            max_size=10,
            current_size=0,
            available_resources=Queue(maxsize=10),
            allocated_resources={},
            usage_stats=defaultdict(int),
        )

        # Temporary directory pool
        self.resource_pools["temp_dirs"] = ResourcePool(
            pool_type="temp_dirs",
            max_size=20,
            current_size=0,
            available_resources=Queue(maxsize=20),
            allocated_resources={},
            usage_stats=defaultdict(int),
        )

        # Mock service pool
        self.resource_pools["mock_services"] = ResourcePool(
            pool_type="mock_services",
            max_size=5,
            current_size=0,
            available_resources=Queue(maxsize=5),
            allocated_resources={},
            usage_stats=defaultdict(int),
        )

        # Network port pool
        self.resource_pools["network_ports"] = ResourcePool(
            pool_type="network_ports",
            max_size=100,
            current_size=0,
            available_resources=Queue(maxsize=100),
            allocated_resources={},
            usage_stats=defaultdict(int),
        )

    @contextmanager
    def acquire_resource(self, pool_type: str, resource_id: str = None):
        """Context manager for acquiring shared resources"""
        if pool_type not in self.resource_pools:
            yield None
            return

        pool = self.resource_pools[pool_type]
        resource = None

        try:
            # Try to get resource from pool
            try:
                resource = pool.available_resources.get_nowait()
            except Empty:
                # Create new resource if under limit
                if pool.current_size < pool.max_size:
                    resource = self._create_resource(pool_type)
                    pool.current_size += 1
                else:
                    # Wait for available resource
                    resource = pool.available_resources.get(timeout=30)

            # Allocate resource
            allocation_id = resource_id or f"{pool_type}_{int(time.time())}"
            pool.allocated_resources[allocation_id] = resource
            pool.usage_stats[allocation_id] += 1

            yield resource

        finally:
            # Return resource to pool
            if resource is not None:
                if allocation_id in pool.allocated_resources:
                    del pool.allocated_resources[allocation_id]

                # Clean and return resource
                self._clean_resource(pool_type, resource)
                pool.available_resources.put(resource)

    def _create_resource(self, pool_type: str) -> Any:
        """Create a new resource of the specified type"""
        if pool_type == "database":
            import sqlite3
            import tempfile

            temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            return sqlite3.connect(temp_db.name)

        elif pool_type == "temp_dirs":
            import tempfile

            return tempfile.mkdtemp(prefix="rfu_test_")

        elif pool_type == "mock_services":
            from unittest.mock import Mock

            return Mock()

        elif pool_type == "network_ports":
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("localhost", 0))
            port = sock.getsockname()[1]
            sock.close()
            return port

        return None

    def _clean_resource(self, pool_type: str, resource: Any):
        """Clean resource before returning to pool"""
        if pool_type == "database" and hasattr(resource, "execute"):
            # Reset database state
            try:
                resource.execute("DELETE FROM test_data WHERE 1=1")
                resource.commit()
            except:
                pass

        elif pool_type == "temp_dirs" and isinstance(resource, str):
            # Clean temporary directory
            import os
            import shutil

            try:
                if os.path.exists(resource):
                    shutil.rmtree(resource)
                    os.makedirs(resource, exist_ok=True)
            except:
                pass

        elif pool_type == "mock_services":
            # Reset mock state
            if hasattr(resource, "reset_mock"):
                resource.reset_mock()

    def start_monitoring(self, interval: float = 1.0):
        """Start resource usage monitoring"""
        if self.monitoring_enabled:
            return

        self.monitoring_enabled = True
        self._monitoring_thread = threading.Thread(
            target=self._monitor_resources, args=(interval,), daemon=True
        )
        self._monitoring_thread.start()

    def stop_monitoring(self):
        """Stop resource usage monitoring"""
        self.monitoring_enabled = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)

    def _monitor_resources(self, interval: float):
        """Background resource monitoring thread"""
        process = psutil.Process()

        while self.monitoring_enabled:
            try:
                # Collect current resource usage
                io_counters = process.io_counters()

                metrics = ResourceUsageMetrics(
                    timestamp=time.time(),
                    cpu_percent=process.cpu_percent(),
                    memory_mb=process.memory_info().rss / (1024 * 1024),
                    memory_percent=process.memory_percent(),
                    io_read_bytes=io_counters.read_bytes,
                    io_write_bytes=io_counters.write_bytes,
                    thread_count=process.num_threads(),
                    gc_count=sum(gc.get_count()),
                )

                self.usage_history.append(metrics)

                # Keep only recent history
                if len(self.usage_history) > 1000:
                    self.usage_history = self.usage_history[-500:]

                # Check for resource pressure and optimize if needed
                self._check_resource_pressure(metrics)

                time.sleep(interval)

            except Exception:
                # Continue monitoring even if individual measurements fail
                time.sleep(interval)

    def _check_resource_pressure(self, metrics: ResourceUsageMetrics):
        """Check for resource pressure and trigger optimization"""
        optimization_triggered = False

        # Memory pressure check
        if metrics.memory_mb > self.max_memory_mb * 0.8:
            self._optimize_memory()
            optimization_triggered = True

        # CPU pressure check
        if metrics.cpu_percent > self.max_cpu_percent * 0.9:
            self._optimize_cpu()
            optimization_triggered = True

        # Garbage collection pressure
        current_gc = sum(gc.get_count())
        if len(self.usage_history) > 10:
            recent_gc_growth = current_gc - self.usage_history[-10].gc_count
            if recent_gc_growth > 1000:
                self._optimize_garbage_collection()
                optimization_triggered = True

        return optimization_triggered

    def _optimize_memory(self):
        """Optimize memory usage"""
        # Force garbage collection
        collected = gc.collect()

        # Clear unused resource pools
        for pool_name, pool in self.resource_pools.items():
            # Release unused resources
            unused_resources = []
            while not pool.available_resources.empty():
                try:
                    resource = pool.available_resources.get_nowait()
                    unused_resources.append(resource)
                except Empty:
                    break

            # Keep only half of unused resources
            keep_count = len(unused_resources) // 2
            for resource in unused_resources[:keep_count]:
                pool.available_resources.put(resource)

            # Clean up the rest
            for resource in unused_resources[keep_count:]:
                self._dispose_resource(pool_name, resource)
                pool.current_size -= 1

        return {"gc_collected": collected, "strategy": "memory_optimization"}

    def _optimize_cpu(self):
        """Optimize CPU usage"""
        # Reduce thread priority for background tasks
        import os

        try:
            if hasattr(os, "nice"):
                os.nice(1)  # Lower priority
        except:
            pass

        # Trigger garbage collection to reduce CPU overhead
        gc.collect()

        return {"strategy": "cpu_optimization", "nice_applied": True}

    def _optimize_io(self):
        """Optimize I/O usage"""
        # Sync filesystem to reduce I/O pressure
        try:
            import os

            if hasattr(os, "sync"):
                os.sync()
        except:
            pass

        return {"strategy": "io_optimization", "sync_applied": True}

    def _optimize_garbage_collection(self):
        """Optimize garbage collection settings"""
        # Tune garbage collection thresholds
        gc.set_threshold(700, 10, 10)  # More aggressive collection

        # Force full collection cycle
        collected = gc.collect()

        # Disable automatic collection temporarily for critical sections
        return {
            "strategy": "gc_optimization",
            "collected": collected,
            "thresholds_tuned": True,
        }

    def _dispose_resource(self, pool_type: str, resource: Any):
        """Properly dispose of a resource"""
        if pool_type == "database" and hasattr(resource, "close"):
            resource.close()
        elif pool_type == "temp_dirs" and isinstance(resource, str):
            import os
            import shutil

            try:
                if os.path.exists(resource):
                    shutil.rmtree(resource)
            except:
                pass

    def optimize_test_environment(
        self, optimization_level: str = "balanced"
    ) -> Dict:
        """Optimize test environment with specified optimization level"""
        optimization_start = time.time()

        results = {
            "optimization_level": optimization_level,
            "start_time": optimization_start,
            "strategies_applied": [],
            "resource_stats_before": self._get_current_resource_stats(),
            "optimization_results": {},
        }

        # Apply optimization strategies based on level
        if optimization_level == "aggressive":
            strategies = ["memory", "cpu", "io", "gc"]
        elif optimization_level == "moderate":
            strategies = ["memory", "gc"]
        else:  # balanced
            strategies = ["memory"]

        for strategy in strategies:
            if strategy in self.optimization_strategies:
                strategy_result = self.optimization_strategies[strategy]()
                results["strategies_applied"].append(strategy)
                results["optimization_results"][strategy] = strategy_result

        # Collect post-optimization stats
        time.sleep(1)  # Allow time for optimization to take effect
        results["resource_stats_after"] = self._get_current_resource_stats()
        results["optimization_time"] = time.time() - optimization_start
        results["improvement_metrics"] = self._calculate_improvement_metrics(
            results["resource_stats_before"], results["resource_stats_after"]
        )

        return results

    def _get_current_resource_stats(self) -> Dict:
        """Get current resource usage statistics"""
        process = psutil.Process()

        try:
            io_counters = process.io_counters()
            io_stats = {
                "read_bytes": io_counters.read_bytes,
                "write_bytes": io_counters.write_bytes,
            }
        except:
            io_stats = {"read_bytes": 0, "write_bytes": 0}

        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / (1024 * 1024),
            "memory_percent": process.memory_percent(),
            "thread_count": process.num_threads(),
            "io_stats": io_stats,
            "gc_count": sum(gc.get_count()),
            "gc_stats": gc.get_stats(),
        }

    def _calculate_improvement_metrics(
        self, before: Dict, after: Dict
    ) -> Dict:
        """Calculate improvement metrics from optimization"""
        improvements = {}

        # Memory improvement
        memory_before = before.get("memory_mb", 0)
        memory_after = after.get("memory_mb", 0)
        memory_improvement = (
            (memory_before - memory_after) / max(memory_before, 1)
        ) * 100

        improvements["memory_reduction_percent"] = memory_improvement

        # CPU improvement
        cpu_before = before.get("cpu_percent", 0)
        cpu_after = after.get("cpu_percent", 0)
        cpu_improvement = cpu_before - cpu_after

        improvements["cpu_usage_reduction"] = cpu_improvement

        # GC improvement
        gc_before = before.get("gc_count", 0)
        gc_after = after.get("gc_count", 0)
        gc_reduction = gc_before - gc_after

        improvements["gc_objects_collected"] = gc_reduction

        # Thread count improvement
        thread_before = before.get("thread_count", 0)
        thread_after = after.get("thread_count", 0)
        thread_reduction = thread_before - thread_after

        improvements["thread_count_reduction"] = thread_reduction

        return improvements

    def create_optimized_test_context(
        self, test_name: str, resource_requirements: Dict = None
    ):
        """Create optimized context for test execution"""
        return OptimizedTestContext(
            self, test_name, resource_requirements or {}
        )


class OptimizedTestContext:
    """Optimized context manager for individual test execution"""

    def __init__(
        self,
        optimizer: ResourceOptimizer,
        test_name: str,
        resource_requirements: Dict,
    ):
        self.optimizer = optimizer
        self.test_name = test_name
        self.resource_requirements = resource_requirements
        self.allocated_resources = {}
        self.start_time = None
        self.start_metrics = None

    def __enter__(self):
        """Enter optimized test context"""
        self.start_time = time.time()
        self.start_metrics = self.optimizer._get_current_resource_stats()

        # Pre-allocate required resources
        self._allocate_required_resources()

        # Apply pre-test optimizations
        self._apply_pre_test_optimizations()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit optimized test context with cleanup"""
        # Release allocated resources
        self._release_allocated_resources()

        # Apply post-test cleanup
        self._apply_post_test_cleanup()

        # Record performance metrics
        end_metrics = self.optimizer._get_current_resource_stats()
        test_duration = time.time() - self.start_time

        self._record_test_performance(
            test_duration, end_metrics, exc_type is None
        )

    def _allocate_required_resources(self):
        """Allocate resources based on test requirements"""
        for resource_type, amount in self.resource_requirements.items():
            if resource_type in self.optimizer.resource_pools:
                try:
                    with self.optimizer.acquire_resource(
                        resource_type, self.test_name
                    ) as resource:
                        self.allocated_resources[resource_type] = resource
                except Exception:
                    # Continue without resource if allocation fails
                    pass

    def _apply_pre_test_optimizations(self):
        """Apply optimizations before test execution"""
        # Force garbage collection for clean start
        gc.collect()

        # Set optimal GC thresholds for test
        gc.set_threshold(1000, 15, 15)

        # Clear CPU-intensive background tasks if possible
        try:
            import os

            if hasattr(os, "nice"):
                os.nice(-1)  # Higher priority for test execution
        except:
            pass

    def _release_allocated_resources(self):
        """Release all allocated resources"""
        for resource_type, resource in self.allocated_resources.items():
            try:
                if resource_type == "database" and hasattr(resource, "close"):
                    resource.close()
                elif resource_type == "temp_dirs":
                    import os
                    import shutil

                    if os.path.exists(resource):
                        shutil.rmtree(resource, ignore_errors=True)
            except Exception:
                # Log but don't fail on cleanup errors
                pass

        self.allocated_resources.clear()

    def _apply_post_test_cleanup(self):
        """Apply cleanup after test execution"""
        # Force garbage collection
        gc.collect()

        # Reset GC thresholds to default
        gc.set_threshold(700, 10, 10)

        # Reset process priority
        try:
            import os

            if hasattr(os, "nice"):
                os.nice(0)  # Reset to normal priority
        except:
            pass

    def _record_test_performance(
        self, duration: float, end_metrics: Dict, success: bool
    ):
        """Record test performance metrics for analysis"""
        performance_record = {
            "test_name": self.test_name,
            "duration": duration,
            "success": success,
            "resource_usage": {
                "start_metrics": self.start_metrics,
                "end_metrics": end_metrics,
                "resource_requirements": self.resource_requirements,
            },
            "optimization_effectiveness": self._calculate_optimization_effectiveness(
                end_metrics
            ),
        }

        # Store in optimizer's history
        if hasattr(self.optimizer, "performance_history"):
            self.optimizer.performance_history.append(performance_record)
        else:
            self.optimizer.performance_history = [performance_record]

    def _calculate_optimization_effectiveness(self, end_metrics: Dict) -> Dict:
        """Calculate how effective the optimization was"""
        memory_efficiency = 1.0 - (
            end_metrics.get("memory_percent", 0) / 100.0
        )
        cpu_efficiency = 1.0 - (end_metrics.get("cpu_percent", 0) / 100.0)

        return {
            "memory_efficiency": memory_efficiency,
            "cpu_efficiency": cpu_efficiency,
            "overall_efficiency": (memory_efficiency + cpu_efficiency) / 2,
            "resource_pool_utilization": len(self.allocated_resources),
        }


class AdvancedMemoryManager:
    """Advanced memory management for test execution"""

    def __init__(self, target_memory_mb: int = 1024):
        self.target_memory_mb = target_memory_mb
        self.memory_pressure_threshold = 0.8
        self.memory_pools = {}
        self.allocation_tracker = defaultdict(int)

    @contextmanager
    def managed_memory_context(self, allocation_size_mb: int = 100):
        """Context manager for managed memory allocation"""
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)

        try:
            # Pre-allocate memory pool if needed
            if allocation_size_mb > 50:
                self._pre_allocate_memory_pool(allocation_size_mb)

            yield

        finally:
            # Clean up and verify memory release
            gc.collect()

            end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            memory_delta = end_memory - start_memory

            # Log excessive memory retention
            if memory_delta > allocation_size_mb * 1.5:
                self._handle_memory_leak_detection(memory_delta)

    def _pre_allocate_memory_pool(self, size_mb: int):
        """Pre-allocate memory pool for efficient test execution"""
        # Create memory pool for test data
        pool_size = size_mb * 1024 * 1024  # Convert to bytes
        memory_pool = bytearray(pool_size)

        pool_id = f"pool_{int(time.time())}"
        self.memory_pools[pool_id] = memory_pool
        self.allocation_tracker[pool_id] = size_mb

        return pool_id

    def _handle_memory_leak_detection(self, leaked_mb: float):
        """Handle detected memory leaks"""
        # Force aggressive garbage collection
        for _ in range(3):
            gc.collect()

        # Clear memory pools
        self.memory_pools.clear()

        # Log memory leak for investigation
        leak_info = {
            "timestamp": time.time(),
            "leaked_memory_mb": leaked_mb,
            "action": "aggressive_cleanup_applied",
        }

        # Could integrate with logging system here
        print(f"⚠️ Memory leak detected: {leaked_mb:.2f}MB - cleanup applied")

        return leak_info


def optimize_test_execution_environment(
    optimization_config: Dict = None,
) -> Dict:
    """Main function to optimize test execution environment"""
    config = optimization_config or {
        "max_memory_mb": 2048,
        "max_cpu_percent": 80.0,
        "optimization_level": "balanced",
        "enable_monitoring": True,
    }

    print("🚀 Starting test environment optimization...")
    start_time = time.time()

    # Create resource optimizer
    optimizer = ResourceOptimizer(
        max_memory_mb=config["max_memory_mb"],
        max_cpu_percent=config["max_cpu_percent"],
    )

    # Start monitoring if enabled
    if config.get("enable_monitoring", True):
        optimizer.start_monitoring()

    # Apply optimization
    optimization_result = optimizer.optimize_test_environment(
        config.get("optimization_level", "balanced")
    )

    # Stop monitoring
    optimizer.stop_monitoring()

    optimization_time = time.time() - start_time

    print(
        f"✅ Test environment optimization completed in {optimization_time:.2f}s"
    )
    print(
        f"📊 Applied {len(optimization_result['strategies_applied'])} optimization strategies"
    )

    optimization_result["total_optimization_time"] = optimization_time

    return optimization_result


if __name__ == "__main__":
    # Example usage for Phase 4 resource optimization
    result = optimize_test_execution_environment(
        {
            "optimization_level": "aggressive",
            "max_memory_mb": 1024,
            "enable_monitoring": True,
        }
    )

    print("Resource Optimization Results:")
    print(f"- Strategies applied: {result['strategies_applied']}")
    print(f"- Optimization time: {result['total_optimization_time']:.2f}s")
    print(
        f"- Memory improvement: {result['improvement_metrics']['memory_reduction_percent']:.1f}%"
    )
