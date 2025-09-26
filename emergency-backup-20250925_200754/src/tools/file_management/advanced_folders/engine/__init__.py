"""Advanced Folders Search Engine Package.

Enterprise-grade search engine implementation with multi-threading,
caching, and performance optimization capabilities.
"""

from .cache_manager import CacheConfig, CacheMetrics, SearchCacheManager
from .file_system_scanner import (
    FileSystemScanner,
    ScannerConfig,
    ScanResult,
    ScanWorker,
)
from .multi_threaded_search_engine import (
    MultiThreadedSearchEngine,
    SearchEngineConfig,
    SearchEngineMetrics,
    SearchResult,
    SearchTask,
    SearchWorker,
)
from .performance_monitor import (
    MetricsCollector,
    PerformanceMonitor,
    PerformanceReport,
)

__all__ = [
    "MultiThreadedSearchEngine",
    "SearchWorker",
    "SearchTask",
    "SearchResult",
    "SearchEngineConfig",
    "SearchEngineMetrics",
    "FileSystemScanner",
    "ScanWorker",
    "ScanResult",
    "ScannerConfig",
    "SearchCacheManager",
    "CacheConfig",
    "CacheMetrics",
    "PerformanceMonitor",
    "MetricsCollector",
    "PerformanceReport",
]
