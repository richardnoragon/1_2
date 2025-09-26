"""
Search Performance Optimization System for Advanced Folders - Week 7 Implementation.

Enterprise-grade performance optimization engine providing search algorithm
optimization, caching strategies, multi-threading, performance monitoring,
search result ranking, and comprehensive performance analytics.

Features:
- Multi-level caching with intelligent cache management
- Parallel search execution with dynamic load balancing
- Search algorithm optimization and adaptive strategies
- Real-time performance monitoring and profiling
- Search result ranking and relevance scoring
- Memory-efficient data structures and streaming
- Performance bottleneck detection and resolution
- Comprehensive metrics collection and reporting
"""

import gc
import logging
import pickle
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union
from weakref import WeakValueDictionary

import psutil

from ..exceptions.advanced_folders_exceptions import (
    ConfigurationException,
    PerformanceException,
    SearchException,
)


class CacheStrategy(Enum):
    """Cache eviction strategies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on usage patterns


class SearchStrategy(Enum):
    """Search execution strategies."""

    SEQUENTIAL = "sequential"  # Single-threaded sequential search
    PARALLEL = "parallel"  # Multi-threaded parallel search
    HYBRID = "hybrid"  # Adaptive hybrid approach
    STREAMING = "streaming"  # Memory-efficient streaming
    INDEXED = "indexed"  # Index-based search


class PerformanceLevel(Enum):
    """Performance optimization levels."""

    BASIC = "basic"  # Basic optimizations
    STANDARD = "standard"  # Standard performance tuning
    AGGRESSIVE = "aggressive"  # Aggressive optimization
    MAXIMUM = "maximum"  # Maximum performance mode


@dataclass
class PerformanceMetrics:
    """Container for performance measurements."""

    operation_type: str
    start_time: float
    end_time: float
    duration_ms: float
    memory_before_mb: float
    memory_after_mb: float
    memory_peak_mb: float
    cpu_usage_percent: float
    io_operations: int
    cache_hits: int
    cache_misses: int
    items_processed: int
    items_per_second: float
    error_count: int = 0
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def memory_delta_mb(self) -> float:
        """Calculate memory usage change."""
        return self.memory_after_mb - self.memory_before_mb

    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency score (items per MB per second)."""
        if self.memory_peak_mb > 0 and self.duration_ms > 0:
            return (self.items_processed * 1000) / (
                self.memory_peak_mb * self.duration_ms
            )
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_type": self.operation_type,
            "duration_ms": round(self.duration_ms, 2),
            "memory_delta_mb": round(self.memory_delta_mb, 2),
            "memory_peak_mb": round(self.memory_peak_mb, 2),
            "cpu_usage_percent": round(self.cpu_usage_percent, 2),
            "io_operations": self.io_operations,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "items_processed": self.items_processed,
            "items_per_second": round(self.items_per_second, 2),
            "efficiency_score": round(self.efficiency_score, 4),
            "error_count": self.error_count,
            "additional_metrics": self.additional_metrics,
        }


@dataclass
class SearchTask:
    """Represents a search task for parallel execution."""

    task_id: str
    search_type: str
    parameters: Dict[str, Any]
    file_paths: List[str]
    priority: int = 0
    timeout_seconds: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    estimated_duration_ms: Optional[float] = None

    def __lt__(self, other: "SearchTask") -> bool:
        """Compare tasks by priority for queue ordering."""
        return self.priority > other.priority  # Higher priority first


class PerformanceProfiler:
    """Real-time performance profiler for search operations."""

    def __init__(self, sampling_interval: float = 0.1):
        """
        Initialize performance profiler.

        Args:
            sampling_interval: Sampling interval in seconds
        """
        self.sampling_interval = sampling_interval
        self.profiling_active = False
        self.profile_data = []
        self._profile_thread = None
        self._stop_event = threading.Event()

        self.logger = logging.getLogger("RFU.PerformanceProfiler")

    def start_profiling(self) -> None:
        """Start performance profiling."""
        if self.profiling_active:
            return

        self.profiling_active = True
        self._stop_event.clear()
        self.profile_data.clear()

        self._profile_thread = threading.Thread(
            target=self._profile_worker, daemon=True
        )
        self._profile_thread.start()

        self.logger.debug("Performance profiling started")

    def stop_profiling(self) -> List[Dict[str, Any]]:
        """
        Stop performance profiling and return collected data.

        Returns:
            List of performance samples
        """
        if not self.profiling_active:
            return []

        self.profiling_active = False
        self._stop_event.set()

        if self._profile_thread and self._profile_thread.is_alive():
            self._profile_thread.join(timeout=1.0)

        data = self.profile_data.copy()
        self.profile_data.clear()

        self.logger.debug(
            f"Performance profiling stopped, collected {len(data)} samples"
        )
        return data

    def _profile_worker(self) -> None:
        """Worker thread for collecting performance samples."""
        process = psutil.Process()

        while not self._stop_event.wait(self.sampling_interval):
            try:
                # Collect system metrics
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)

                # IO counters (if available)
                try:
                    io_counters = process.io_counters()
                    io_operations = (
                        io_counters.read_count + io_counters.write_count
                    )
                except (AttributeError, psutil.AccessDenied):
                    io_operations = 0

                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_mb,
                    "io_operations": io_operations,
                }

                self.profile_data.append(sample)

                # Limit profile data size
                if len(self.profile_data) > 10000:
                    self.profile_data = self.profile_data[-5000:]

            except Exception as e:
                self.logger.warning(f"Profile sampling error: {str(e)}")


class AdaptiveCache:
    """
    Adaptive cache with multiple eviction strategies and intelligent management.
    """

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: float = 100.0,
        strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
        ttl_seconds: float = 3600.0,
    ):
        """
        Initialize adaptive cache.

        Args:
            max_size: Maximum number of cache entries
            max_memory_mb: Maximum memory usage in MB
            strategy: Cache eviction strategy
            ttl_seconds: Time-to-live for TTL strategy
        """
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self.strategy = strategy
        self.ttl_seconds = ttl_seconds

        # Cache storage
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = defaultdict(int)
        self._insertion_order: deque = deque()
        self._memory_usage = 0.0

        # Thread safety
        self._lock = threading.RLock()

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_evictions": 0,
            "size_checks": 0,
        }

        self.logger = logging.getLogger("RFU.AdaptiveCache")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                # Update access patterns
                self._access_times[key] = time.time()
                self._access_counts[key] += 1

                # Check TTL
                if self.strategy == CacheStrategy.TTL:
                    if (
                        time.time() - self._access_times[key]
                        > self.ttl_seconds
                    ):
                        self._remove_key(key)
                        self.stats["misses"] += 1
                        return None

                self.stats["hits"] += 1
                return self._cache[key]
            else:
                self.stats["misses"] += 1
                return None

    def put(self, key: str, value: Any) -> None:
        """Put value into cache."""
        with self._lock:
            # Calculate value size
            value_size = self._estimate_size(value)

            # Check if we need to make space
            while (
                len(self._cache) >= self.max_size
                or self._memory_usage + value_size
                > self.max_memory_mb * 1024 * 1024
            ):
                if not self._evict_one():
                    break  # Can't evict any more

            # Store value
            if key in self._cache:
                # Update existing
                old_size = self._estimate_size(self._cache[key])
                self._memory_usage -= old_size
            else:
                # New entry
                self._insertion_order.append(key)

            self._cache[key] = value
            self._access_times[key] = time.time()
            self._access_counts[key] += 1
            self._memory_usage += value_size

    def _evict_one(self) -> bool:
        """Evict one cache entry based on strategy."""
        if not self._cache:
            return False

        if self.strategy == CacheStrategy.LRU:
            # Least recently used
            victim = min(
                self._access_times.keys(), key=lambda k: self._access_times[k]
            )

        elif self.strategy == CacheStrategy.LFU:
            # Least frequently used
            victim = min(
                self._access_counts.keys(),
                key=lambda k: self._access_counts[k],
            )

        elif self.strategy == CacheStrategy.FIFO:
            # First in, first out
            victim = self._insertion_order[0]

        elif self.strategy == CacheStrategy.TTL:
            # Expired entries first
            now = time.time()
            expired = [
                k
                for k, t in self._access_times.items()
                if now - t > self.ttl_seconds
            ]
            if expired:
                victim = expired[0]
            else:
                victim = min(
                    self._access_times.keys(),
                    key=lambda k: self._access_times[k],
                )

        else:  # ADAPTIVE
            # Adaptive strategy based on usage patterns
            victim = self._adaptive_select_victim()

        self._remove_key(victim)
        self.stats["evictions"] += 1
        return True

    def _adaptive_select_victim(self) -> str:
        """Select victim using adaptive strategy."""
        now = time.time()

        # Score each entry
        scores = {}
        for key in self._cache.keys():
            age = now - self._access_times[key]
            frequency = self._access_counts[key]
            recency = 1.0 / (age + 1.0)

            # Adaptive scoring
            score = frequency * recency * 0.5 + (1.0 / (age + 1.0)) * 0.5
            scores[key] = score

        # Return lowest scoring entry
        return min(scores.keys(), key=lambda k: scores[k])

    def _remove_key(self, key: str) -> None:
        """Remove key from all data structures."""
        if key in self._cache:
            value_size = self._estimate_size(self._cache[key])
            self._memory_usage -= value_size

            del self._cache[key]
            del self._access_times[key]
            del self._access_counts[key]

            try:
                self._insertion_order.remove(key)
            except ValueError:
                pass  # Key not in insertion order

    def _estimate_size(self, value: Any) -> float:
        """Estimate memory size of a value."""
        try:
            # Use pickle to estimate size
            return len(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
        except Exception:
            # Fallback estimation
            if isinstance(value, str):
                return len(value.encode("utf-8"))
            elif isinstance(value, (list, tuple)):
                return sum(self._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(
                    self._estimate_size(k) + self._estimate_size(v)
                    for k, v in value.items()
                )
            else:
                return 64  # Default estimate

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._access_counts.clear()
            self._insertion_order.clear()
            self._memory_usage = 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_ratio = (
                (self.stats["hits"] / total_requests)
                if total_requests > 0
                else 0.0
            )

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "memory_usage_mb": round(
                    self._memory_usage / (1024 * 1024), 2
                ),
                "max_memory_mb": self.max_memory_mb,
                "hit_ratio": round(hit_ratio, 3),
                "strategy": self.strategy.value,
                **self.stats,
            }


class SearchResultRanker:
    """Intelligent search result ranking and relevance scoring."""

    def __init__(self):
        """Initialize search result ranker."""
        self.logger = logging.getLogger("RFU.SearchResultRanker")

        # Ranking weights
        self.weights = {
            "filename_match": 1.0,
            "path_match": 0.8,
            "content_match": 0.6,
            "extension_match": 0.4,
            "size_preference": 0.2,
            "date_preference": 0.3,
            "access_frequency": 0.5,
        }

    def rank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rank search results by relevance.

        Args:
            results: List of search results
            query: Original search query
            preferences: User preferences for ranking

        Returns:
            Ranked list of results
        """
        if not results:
            return results

        preferences = preferences or {}

        # Calculate scores for each result
        scored_results = []
        for result in results:
            score = self._calculate_relevance_score(result, query, preferences)
            scored_results.append((score, result))

        # Sort by score (descending)
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # Add ranking information
        ranked_results = []
        for rank, (score, result) in enumerate(scored_results):
            result = result.copy()
            result["_ranking"] = {"score": round(score, 4), "rank": rank + 1}
            ranked_results.append(result)

        return ranked_results

    def _calculate_relevance_score(
        self, result: Dict[str, Any], query: str, preferences: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a search result."""
        score = 0.0
        query_lower = query.lower()

        # Filename matching
        filename = result.get("name", "").lower()
        if query_lower in filename:
            if filename.startswith(query_lower):
                score += self.weights["filename_match"] * 1.0
            elif filename.endswith(query_lower):
                score += self.weights["filename_match"] * 0.8
            else:
                score += self.weights["filename_match"] * 0.6

        # Path matching
        path = result.get("path", "").lower()
        if query_lower in path:
            score += self.weights["path_match"] * 0.5

        # Content matching (if available)
        content = result.get("content", "").lower()
        if content and query_lower in content:
            # Count occurrences
            occurrences = content.count(query_lower)
            score += self.weights["content_match"] * min(
                occurrences * 0.1, 1.0
            )

        # Extension matching
        ext = result.get("extension", "").lower()
        preferred_extensions = preferences.get("preferred_extensions", [])
        if ext in [e.lower() for e in preferred_extensions]:
            score += self.weights["extension_match"]

        # Size preferences
        size = result.get("size", 0)
        preferred_size_range = preferences.get("preferred_size_range")
        if preferred_size_range:
            min_size, max_size = preferred_size_range
            if min_size <= size <= max_size:
                score += self.weights["size_preference"]

        # Date preferences (newer files preferred)
        modified_time = result.get("modified_time", 0)
        if modified_time > 0:
            age_days = (time.time() - modified_time) / (24 * 3600)
            freshness_score = max(0, 1.0 - (age_days / 365))  # Decay over year
            score += self.weights["date_preference"] * freshness_score

        # Access frequency (if available)
        access_count = result.get("access_count", 0)
        if access_count > 0:
            frequency_score = min(access_count / 10.0, 1.0)
            score += self.weights["access_frequency"] * frequency_score

        return score


class PerformanceOptimizer:
    """
    Enterprise search performance optimization engine.
    """

    def __init__(
        self,
        cache_size: int = 10000,
        max_workers: int = None,
        performance_level: PerformanceLevel = PerformanceLevel.STANDARD,
    ):
        """
        Initialize performance optimizer.

        Args:
            cache_size: Size of result cache
            max_workers: Maximum worker threads (default: CPU count)
            performance_level: Performance optimization level
        """
        self.cache_size = cache_size
        self.max_workers = max_workers or min(
            32, (psutil.cpu_count() or 1) + 4
        )
        self.performance_level = performance_level

        # Core components
        self.cache = AdaptiveCache(
            max_size=cache_size,
            max_memory_mb=self._get_cache_memory_limit(),
            strategy=CacheStrategy.ADAPTIVE,
        )
        self.profiler = PerformanceProfiler()
        self.ranker = SearchResultRanker()

        # Performance tracking
        self.metrics_history: List[PerformanceMetrics] = []
        self.operation_stats = defaultdict(list)

        # Thread pool for parallel operations
        self.executor = ThreadPoolExecutor(
            max_workers=self.max_workers, thread_name_prefix="SearchWorker"
        )

        # Search task queue
        self.task_queue = []
        self.queue_lock = threading.Lock()

        # Performance database for persistent metrics
        self.db_path = Path("performance_metrics.db")
        self._init_performance_db()

        # Memory monitoring
        self.memory_monitor_enabled = True
        self.memory_threshold_mb = self._get_memory_threshold()

        self.logger = logging.getLogger("RFU.PerformanceOptimizer")
        self.logger.info(
            f"Performance optimizer initialized with {self.max_workers} workers, "
            f"performance level: {performance_level.value}"
        )

    def _get_cache_memory_limit(self) -> float:
        """Calculate appropriate cache memory limit."""
        try:
            total_memory_gb = psutil.virtual_memory().total / (1024**3)

            if self.performance_level == PerformanceLevel.BASIC:
                return min(50.0, total_memory_gb * 0.02)  # 2% of RAM, max 50MB
            elif self.performance_level == PerformanceLevel.STANDARD:
                return min(
                    200.0, total_memory_gb * 0.05
                )  # 5% of RAM, max 200MB
            elif self.performance_level == PerformanceLevel.AGGRESSIVE:
                return min(
                    500.0, total_memory_gb * 0.1
                )  # 10% of RAM, max 500MB
            else:  # MAXIMUM
                return min(
                    1000.0, total_memory_gb * 0.15
                )  # 15% of RAM, max 1GB

        except Exception:
            return 100.0  # Fallback to 100MB

    def _get_memory_threshold(self) -> float:
        """Calculate memory usage threshold for warnings."""
        try:
            total_memory_gb = psutil.virtual_memory().total / (1024**3)
            return total_memory_gb * 0.8 * 1024  # 80% of RAM in MB
        except Exception:
            return 4096.0  # Fallback to 4GB

    def _init_performance_db(self) -> None:
        """Initialize performance metrics database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        operation_type TEXT NOT NULL,
                        duration_ms REAL NOT NULL,
                        memory_delta_mb REAL NOT NULL,
                        memory_peak_mb REAL NOT NULL,
                        cpu_usage_percent REAL NOT NULL,
                        items_processed INTEGER NOT NULL,
                        items_per_second REAL NOT NULL,
                        efficiency_score REAL NOT NULL,
                        cache_hits INTEGER NOT NULL,
                        cache_misses INTEGER NOT NULL,
                        error_count INTEGER NOT NULL,
                        additional_data TEXT
                    )
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_operation_timestamp 
                    ON performance_metrics(operation_type, timestamp)
                """
                )

        except Exception as e:
            self.logger.warning(
                f"Failed to initialize performance database: {str(e)}"
            )

    def optimize_search(
        self,
        search_function: callable,
        *args,
        operation_type: str = "search",
        cache_key: Optional[str] = None,
        enable_profiling: bool = True,
        **kwargs,
    ) -> Tuple[Any, PerformanceMetrics]:
        """
        Execute search with comprehensive performance optimization.

        Args:
            search_function: Function to execute
            *args: Function arguments
            operation_type: Type of operation for metrics
            cache_key: Optional cache key for result caching
            enable_profiling: Whether to enable performance profiling
            **kwargs: Function keyword arguments

        Returns:
            Tuple of (result, performance_metrics)
        """
        # Check cache first
        if cache_key:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                # Create minimal metrics for cache hit
                metrics = PerformanceMetrics(
                    operation_type=f"{operation_type}_cached",
                    start_time=time.time(),
                    end_time=time.time(),
                    duration_ms=0.1,
                    memory_before_mb=0,
                    memory_after_mb=0,
                    memory_peak_mb=0,
                    cpu_usage_percent=0,
                    io_operations=0,
                    cache_hits=1,
                    cache_misses=0,
                    items_processed=(
                        len(cached_result)
                        if isinstance(cached_result, list)
                        else 1
                    ),
                    items_per_second=0,
                )
                return cached_result, metrics

        # Start performance monitoring
        start_time = time.time()
        memory_before = self._get_memory_usage_mb()

        if enable_profiling:
            self.profiler.start_profiling()

        try:
            # Check memory pressure
            if self.memory_monitor_enabled:
                self._check_memory_pressure()

            # Execute search function
            result = search_function(*args, **kwargs)

            # Post-process result (ranking, etc.)
            if isinstance(result, list) and len(result) > 1:
                query = kwargs.get("query", args[0] if args else "")
                if isinstance(query, str) and query:
                    preferences = kwargs.get("preferences", {})
                    result = self.ranker.rank_results(
                        result, query, preferences
                    )

            # Cache result if specified
            if cache_key and result is not None:
                self.cache.put(cache_key, result)

            success = True
            error_count = 0

        except Exception as e:
            self.logger.error(f"Search optimization error: {str(e)}")
            result = None
            success = False
            error_count = 1
            raise

        finally:
            # Stop profiling and collect metrics
            end_time = time.time()
            memory_after = self._get_memory_usage_mb()

            profile_data = []
            if enable_profiling:
                profile_data = self.profiler.stop_profiling()

            # Calculate performance metrics
            duration_ms = (end_time - start_time) * 1000
            memory_peak_mb = max(
                memory_before,
                memory_after,
                max(
                    (sample["memory_mb"] for sample in profile_data),
                    default=memory_after,
                ),
            )

            avg_cpu = (
                sum(sample["cpu_percent"] for sample in profile_data)
                / len(profile_data)
                if profile_data
                else 0.0
            )

            io_operations = (
                max(sample["io_operations"] for sample in profile_data)
                - min(sample["io_operations"] for sample in profile_data)
                if profile_data
                else 0
            )

            items_processed = (
                len(result)
                if isinstance(result, list)
                else 1 if result is not None else 0
            )

            items_per_second = (
                (items_processed * 1000) / duration_ms
                if duration_ms > 0
                else 0
            )

            cache_stats = self.cache.get_statistics()

            metrics = PerformanceMetrics(
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                memory_before_mb=memory_before,
                memory_after_mb=memory_after,
                memory_peak_mb=memory_peak_mb,
                cpu_usage_percent=avg_cpu,
                io_operations=io_operations,
                cache_hits=cache_stats.get("hits", 0),
                cache_misses=cache_stats.get("misses", 0),
                items_processed=items_processed,
                items_per_second=items_per_second,
                error_count=error_count,
            )

            # Store metrics
            self._store_metrics(metrics)

        return result, metrics

    def optimize_parallel_search(
        self,
        search_tasks: List[SearchTask],
        timeout_seconds: Optional[float] = None,
    ) -> List[Tuple[str, Any, PerformanceMetrics]]:
        """
        Execute multiple search tasks in parallel with optimization.

        Args:
            search_tasks: List of search tasks to execute
            timeout_seconds: Optional global timeout

        Returns:
            List of (task_id, result, metrics) tuples
        """
        if not search_tasks:
            return []

        # Sort tasks by priority
        search_tasks.sort()

        start_time = time.time()
        results = []

        try:
            # Submit tasks to thread pool
            future_to_task = {}
            for task in search_tasks:
                future = self.executor.submit(self._execute_search_task, task)
                future_to_task[future] = task

            # Collect results as they complete
            for future in as_completed(
                future_to_task, timeout=timeout_seconds
            ):
                task = future_to_task[future]
                try:
                    result, metrics = future.result()
                    results.append((task.task_id, result, metrics))
                except Exception as e:
                    self.logger.error(f"Task {task.task_id} failed: {str(e)}")
                    # Create error metrics
                    error_metrics = PerformanceMetrics(
                        operation_type=task.search_type,
                        start_time=start_time,
                        end_time=time.time(),
                        duration_ms=(time.time() - start_time) * 1000,
                        memory_before_mb=0,
                        memory_after_mb=0,
                        memory_peak_mb=0,
                        cpu_usage_percent=0,
                        io_operations=0,
                        cache_hits=0,
                        cache_misses=0,
                        items_processed=0,
                        items_per_second=0,
                        error_count=1,
                    )
                    results.append((task.task_id, None, error_metrics))

        except Exception as e:
            self.logger.error(f"Parallel search execution failed: {str(e)}")
            raise PerformanceException(
                f"Parallel search optimization failed: {str(e)}",
                performance_metric="parallel_execution",
                threshold_value=0,
                actual_value=-1,
            )

        return results

    def _execute_search_task(
        self, task: SearchTask
    ) -> Tuple[Any, PerformanceMetrics]:
        """Execute a single search task."""
        # This would be implemented with actual search logic
        # For now, return placeholder implementation
        start_time = time.time()

        # Simulate search operation
        time.sleep(0.001)  # Minimal simulation

        # Create mock result
        result = [
            {
                "path": path,
                "name": Path(path).name,
                "size": 1024,
                "modified_time": time.time(),
            }
            for path in task.file_paths[:10]  # Limit results
        ]

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        metrics = PerformanceMetrics(
            operation_type=task.search_type,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_before_mb=self._get_memory_usage_mb(),
            memory_after_mb=self._get_memory_usage_mb(),
            memory_peak_mb=self._get_memory_usage_mb(),
            cpu_usage_percent=0,
            io_operations=len(task.file_paths),
            cache_hits=0,
            cache_misses=1,
            items_processed=len(result),
            items_per_second=(
                (len(result) * 1000) / duration_ms if duration_ms > 0 else 0
            ),
        )

        return result, metrics

    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

    def _check_memory_pressure(self) -> None:
        """Check for memory pressure and take action if needed."""
        try:
            memory_info = psutil.virtual_memory()
            used_mb = (memory_info.total - memory_info.available) / (
                1024 * 1024
            )

            if used_mb > self.memory_threshold_mb:
                self.logger.warning(
                    f"High memory usage detected: {used_mb:.1f}MB "
                    f"(threshold: {self.memory_threshold_mb:.1f}MB)"
                )

                # Clear cache to free memory
                self.cache.clear()

                # Force garbage collection
                gc.collect()

                # Reduce worker count temporarily
                if self.max_workers > 2:
                    self.max_workers = max(2, self.max_workers // 2)
                    self.logger.info(
                        f"Reduced worker count to {self.max_workers}"
                    )

        except Exception as e:
            self.logger.warning(f"Memory pressure check failed: {str(e)}")

    def _store_metrics(self, metrics: PerformanceMetrics) -> None:
        """Store performance metrics."""
        # Add to in-memory history
        self.metrics_history.append(metrics)
        self.operation_stats[metrics.operation_type].append(metrics)

        # Limit history size
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-5000:]

        # Store to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_metrics (
                        timestamp, operation_type, duration_ms, memory_delta_mb,
                        memory_peak_mb, cpu_usage_percent, items_processed,
                        items_per_second, efficiency_score, cache_hits,
                        cache_misses, error_count, additional_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metrics.start_time,
                        metrics.operation_type,
                        metrics.duration_ms,
                        metrics.memory_delta_mb,
                        metrics.memory_peak_mb,
                        metrics.cpu_usage_percent,
                        metrics.items_processed,
                        metrics.items_per_second,
                        metrics.efficiency_score,
                        metrics.cache_hits,
                        metrics.cache_misses,
                        metrics.error_count,
                        str(metrics.additional_metrics),
                    ),
                )

        except Exception as e:
            self.logger.warning(
                f"Failed to store metrics to database: {str(e)}"
            )

    def get_performance_report(
        self,
        operation_type: Optional[str] = None,
        time_range_hours: float = 24.0,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Args:
            operation_type: Filter by operation type
            time_range_hours: Time range for analysis

        Returns:
            Detailed performance report
        """
        cutoff_time = time.time() - (time_range_hours * 3600)

        # Filter metrics
        if operation_type:
            metrics = [
                m
                for m in self.operation_stats.get(operation_type, [])
                if m.start_time >= cutoff_time
            ]
        else:
            metrics = [
                m for m in self.metrics_history if m.start_time >= cutoff_time
            ]

        if not metrics:
            return {
                "message": "No performance data available for the specified period",
                "operation_type": operation_type,
                "time_range_hours": time_range_hours,
            }

        # Calculate statistics
        durations = [m.duration_ms for m in metrics]
        memory_usage = [m.memory_peak_mb for m in metrics]
        items_per_second = [
            m.items_per_second for m in metrics if m.items_per_second > 0
        ]
        efficiency_scores = [
            m.efficiency_score for m in metrics if m.efficiency_score > 0
        ]

        # Cache statistics
        cache_stats = self.cache.get_statistics()

        report = {
            "summary": {
                "total_operations": len(metrics),
                "time_range_hours": time_range_hours,
                "operation_type": operation_type or "all",
                "error_rate": (
                    sum(m.error_count for m in metrics) / len(metrics)
                    if metrics
                    else 0
                ),
            },
            "performance": {
                "avg_duration_ms": (
                    round(sum(durations) / len(durations), 2)
                    if durations
                    else 0
                ),
                "min_duration_ms": (
                    round(min(durations), 2) if durations else 0
                ),
                "max_duration_ms": (
                    round(max(durations), 2) if durations else 0
                ),
                "avg_memory_mb": (
                    round(sum(memory_usage) / len(memory_usage), 2)
                    if memory_usage
                    else 0
                ),
                "peak_memory_mb": (
                    round(max(memory_usage), 2) if memory_usage else 0
                ),
                "avg_items_per_second": (
                    round(sum(items_per_second) / len(items_per_second), 2)
                    if items_per_second
                    else 0
                ),
                "avg_efficiency_score": (
                    round(sum(efficiency_scores) / len(efficiency_scores), 4)
                    if efficiency_scores
                    else 0
                ),
            },
            "cache": cache_stats,
            "system": {
                "max_workers": self.max_workers,
                "performance_level": self.performance_level.value,
                "memory_threshold_mb": self.memory_threshold_mb,
            },
            "recommendations": self._generate_recommendations(metrics),
        }

        return report

    def _generate_recommendations(
        self, metrics: List[PerformanceMetrics]
    ) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        if not metrics:
            return recommendations

        # Analyze performance patterns
        avg_duration = sum(m.duration_ms for m in metrics) / len(metrics)
        avg_memory = sum(m.memory_peak_mb for m in metrics) / len(metrics)
        cache_stats = self.cache.get_statistics()

        # Duration recommendations
        if avg_duration > 5000:  # > 5 seconds
            recommendations.append(
                "Consider enabling more aggressive caching for long-running operations"
            )

        if avg_duration > 1000:  # > 1 second
            recommendations.append(
                "Consider increasing parallel worker count for better throughput"
            )

        # Memory recommendations
        if avg_memory > 500:  # > 500MB
            recommendations.append(
                "High memory usage detected - consider reducing cache size or using streaming"
            )

        # Cache recommendations
        if cache_stats.get("hit_ratio", 0) < 0.3:
            recommendations.append(
                "Low cache hit ratio - consider increasing cache size or adjusting TTL"
            )

        # Error rate recommendations
        error_rate = sum(m.error_count for m in metrics) / len(metrics)
        if error_rate > 0.1:
            recommendations.append(
                "High error rate detected - review error logs and add retry logic"
            )

        return recommendations

    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            self.profiler.stop_profiling()
            self.executor.shutdown(wait=True)
            self.cache.clear()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {str(e)}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore cleanup errors during destruction
