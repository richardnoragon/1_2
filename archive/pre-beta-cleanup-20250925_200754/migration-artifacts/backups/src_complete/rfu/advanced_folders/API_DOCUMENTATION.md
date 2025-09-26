# Advanced Folders API Documentation

## Overview

This document provides comprehensive API documentation for the Advanced Folders system, including all public interfaces, data structures, and usage examples.

## Module Structure

```
src.rfu.advanced_folders
├── models/
│   ├── folder_configuration.py
│   └── search_parameters.py
├── core/
│   ├── file_system_scanner.py
│   ├── search_engine.py
│   ├── search_cache.py
│   ├── metadata_pipeline.py
│   └── performance_monitor.py
└── exceptions/
    └── advanced_folders_exceptions.py
```

## Models API

### folder_configuration.py

#### Enums

##### SortOption
```python
class SortOption(Enum):
    NAME = "name"
    SIZE = "size"
    MODIFIED = "modified"
    TYPE = "type"
    CREATED = "created"
```

##### ViewMode
```python
class ViewMode(Enum):
    LIST = "list"
    GRID = "grid"
    DETAILS = "details"
    TREE = "tree"
```

##### FilterOption
```python
class FilterOption(Enum):
    ALL_FILES = "all"
    DOCUMENTS = "documents"
    IMAGES = "images"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVES = "archives"
    CUSTOM = "custom"
```

#### Classes

##### FolderConfiguration
```python
@dataclass
class FolderConfiguration:
    """Configuration settings for a managed folder."""
    
    # Required fields
    folder_path: str
    display_name: str
    sort_option: SortOption
    view_mode: ViewMode
    
    # Optional fields with defaults
    filter_options: List[FilterOption] = field(default_factory=lambda: [FilterOption.ALL_FILES])
    is_recursive: bool = True
    auto_scan: bool = False
    scan_interval_minutes: int = 60
    exclusion_patterns: List[str] = field(default_factory=list)
    
    # Metadata fields
    created_time: Optional[datetime] = None
    last_scan_time: Optional[datetime] = None
    is_active: bool = True
    
    def save(self, db_path: str) -> None:
        """Save configuration to database."""
    
    @classmethod
    def load(cls, db_path: str, folder_path: str) -> Optional['FolderConfiguration']:
        """Load configuration from database."""
    
    @classmethod
    def load_all(cls, db_path: str) -> List['FolderConfiguration']:
        """Load all configurations from database."""
    
    def delete(self, db_path: str) -> None:
        """Delete configuration from database."""
    
    def update_last_scan(self, db_path: str) -> None:
        """Update last scan time."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderConfiguration':
        """Create from dictionary representation."""
    
    def validate(self) -> bool:
        """Validate configuration settings."""
```

**Usage Example:**
```python
config = FolderConfiguration(
    folder_path="/home/user/documents",
    display_name="My Documents",
    sort_option=SortOption.MODIFIED,
    view_mode=ViewMode.DETAILS,
    is_recursive=True,
    auto_scan=True,
    exclusion_patterns=["*.tmp", ".*"]
)

# Save to database
config.save("config.db")

# Load from database
loaded_config = FolderConfiguration.load("config.db", "/home/user/documents")
```

### search_parameters.py

#### Enums

##### SearchScope
```python
class SearchScope(Enum):
    CURRENT_FOLDER = "current"
    ALL_FOLDERS = "all"
    SELECTED_FOLDERS = "selected"
    CUSTOM_PATH = "custom"
```

##### SearchType
```python
class SearchType(Enum):
    FILENAME = "filename"
    CONTENT = "content"
    METADATA = "metadata"
    COMBINED = "combined"
```

#### Classes

##### SearchParameters
```python
@dataclass
class SearchParameters:
    """Parameters for search operations."""
    
    # Required fields
    query: str
    scope: SearchScope
    search_type: SearchType
    
    # Optional fields with defaults
    case_sensitive: bool = False
    include_subdirectories: bool = True
    use_regex: bool = False
    
    # File filtering
    file_size_min: Optional[int] = None
    file_size_max: Optional[int] = None
    date_modified_after: Optional[datetime] = None
    date_modified_before: Optional[datetime] = None
    file_extensions: Optional[List[str]] = None
    
    # Advanced options
    max_results: int = 1000
    search_timeout_seconds: int = 30
    folder_paths: Optional[List[str]] = None  # For SELECTED_FOLDERS scope
    
    def is_valid(self) -> bool:
        """Validate search parameters."""
    
    def get_cache_key(self) -> str:
        """Generate cache key for parameters."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchParameters':
        """Create from dictionary representation."""
```

**Usage Example:**
```python
params = SearchParameters(
    query="document",
    scope=SearchScope.ALL_FOLDERS,
    search_type=SearchType.FILENAME,
    case_sensitive=False,
    file_extensions=[".pdf", ".docx"],
    file_size_min=1024,  # 1KB minimum
    date_modified_after=datetime(2023, 1, 1)
)

if params.is_valid():
    cache_key = params.get_cache_key()
    print(f"Cache key: {cache_key}")
```

## Core API

### file_system_scanner.py

#### Data Classes

##### FileInfo
```python
@dataclass
class FileInfo:
    """Information about a file or directory."""
    
    path: str
    name: str
    size: int
    modified_time: datetime
    is_directory: bool
    extension: str
    permissions: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileInfo':
        """Create from dictionary representation."""
```

##### ScanStatistics
```python
@dataclass
class ScanStatistics:
    """Statistics from a file system scan."""
    
    total_files: int
    total_directories: int
    total_size_bytes: int
    scan_duration_seconds: float
    files_per_second: float
    errors_encountered: int
    largest_file_size: int
    smallest_file_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
```

#### Classes

##### FileSystemScanner
```python
class FileSystemScanner:
    """Enterprise-grade file system scanner."""
    
    def __init__(
        self,
        max_workers: int = 4,
        follow_symlinks: bool = False,
        check_permissions: bool = True
    ):
        """Initialize scanner."""
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
        exclusion_patterns: Optional[List[str]] = None,
        max_files: Optional[int] = None,
        include_hidden: bool = False
    ) -> List[FileInfo]:
        """Scan directory and return file information."""
    
    def scan_directories(
        self,
        directories: List[str],
        recursive: bool = True,
        **kwargs
    ) -> List[FileInfo]:
        """Scan multiple directories concurrently."""
    
    def get_scan_statistics(self) -> ScanStatistics:
        """Get statistics from the last scan."""
    
    def cancel_scan(self) -> None:
        """Cancel ongoing scan operation."""
    
    def is_scanning(self) -> bool:
        """Check if scan is in progress."""
```

**Usage Example:**
```python
scanner = FileSystemScanner(max_workers=8, follow_symlinks=False)

# Basic scan
files = scanner.scan_directory("/path/to/scan", recursive=True)

# Filtered scan
pdf_files = scanner.scan_directory(
    "/documents",
    file_extensions=[".pdf"],
    exclusion_patterns=["*draft*", "*.tmp"]
)

# Get statistics
stats = scanner.get_scan_statistics()
print(f"Scanned {stats.total_files} files in {stats.scan_duration_seconds:.2f}s")
```

##### BatchFileSystemScanner
```python
class BatchFileSystemScanner:
    """Batch processing scanner for large operations."""
    
    def __init__(
        self,
        max_workers: int = 4,
        batch_size: int = 1000,
        progress_callback: Optional[Callable] = None
    ):
        """Initialize batch scanner."""
    
    def scan_with_progress(
        self,
        directory: str,
        **kwargs
    ) -> Iterator[List[FileInfo]]:
        """Scan directory with progress reporting."""
    
    def estimate_scan_time(self, directory: str) -> float:
        """Estimate scan time for directory."""
```

### search_engine.py

#### Data Classes

##### SearchMetrics
```python
@dataclass
class SearchMetrics:
    """Metrics for search operations."""
    
    total_searches: int
    total_indexed_files: int
    average_search_time_ms: float
    index_size_bytes: int
    last_index_update: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
```

#### Classes

##### SearchEngine
```python
class SearchEngine:
    """Scalable search engine for file indexing and searching."""
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        use_memory_index: bool = True,
        index_strategy: str = "hybrid"  # "memory", "database", "hybrid"
    ):
        """Initialize search engine."""
    
    def add_file(self, file_info: FileInfo) -> None:
        """Add file to search index."""
    
    def add_files(self, files: List[FileInfo]) -> None:
        """Add multiple files to search index."""
    
    def remove_file(self, file_path: str) -> None:
        """Remove file from search index."""
    
    def update_file(self, file_info: FileInfo) -> None:
        """Update file information in index."""
    
    def search(
        self,
        parameters: SearchParameters,
        limit: Optional[int] = None
    ) -> List[FileInfo]:
        """Search for files matching parameters."""
    
    def search_async(
        self,
        parameters: SearchParameters,
        callback: Callable[[List[FileInfo]], None]
    ) -> None:
        """Perform asynchronous search."""
    
    def rebuild_index(self) -> None:
        """Rebuild the search index."""
    
    def optimize_index(self) -> None:
        """Optimize index for better performance."""
    
    def get_search_metrics(self) -> SearchMetrics:
        """Get search engine metrics."""
    
    def get_indexed_file_count(self) -> int:
        """Get total number of indexed files."""
    
    def clear_index(self) -> None:
        """Clear all indexed data."""
```

**Usage Example:**
```python
engine = SearchEngine(db_path="search.db", index_strategy="hybrid")

# Index files
scanner = FileSystemScanner()
files = scanner.scan_directory("/documents")
engine.add_files(files)

# Search
params = SearchParameters(
    query="report",
    scope=SearchScope.ALL_FOLDERS,
    search_type=SearchType.FILENAME
)
results = engine.search(params, limit=50)

# Async search
def handle_results(results):
    print(f"Found {len(results)} files")

engine.search_async(params, handle_results)
```

##### MemorySearchIndex
```python
class MemorySearchIndex:
    """In-memory search index for fast searching."""
    
    def __init__(self):
        """Initialize memory index."""
    
    def add_file(self, file_info: FileInfo) -> None:
        """Add file to memory index."""
    
    def search(self, parameters: SearchParameters) -> List[FileInfo]:
        """Search memory index."""
    
    def get_file_count(self) -> int:
        """Get indexed file count."""
    
    def clear(self) -> None:
        """Clear memory index."""
```

##### DatabaseSearchIndex
```python
class DatabaseSearchIndex:
    """Database-backed search index for persistent storage."""
    
    def __init__(self, db_path: str):
        """Initialize database index."""
    
    def add_file(self, file_info: FileInfo) -> None:
        """Add file to database index."""
    
    def search(self, parameters: SearchParameters) -> List[FileInfo]:
        """Search database index."""
    
    def get_file_count(self) -> int:
        """Get indexed file count."""
    
    def optimize(self) -> None:
        """Optimize database index."""
```

### search_cache.py

#### Data Classes

##### CacheStatistics
```python
@dataclass
class CacheStatistics:
    """Statistics for cache operations."""
    
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    memory_usage_bytes: int
    database_entries: int
    expired_entries: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
```

#### Classes

##### SearchResultCache
```python
class SearchResultCache:
    """Multi-tier caching system for search results."""
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        memory_cache_size: int = 1000,
        default_ttl_hours: int = 24
    ):
        """Initialize search cache."""
    
    def store_results(
        self,
        parameters: SearchParameters,
        results: List[FileInfo],
        ttl_hours: Optional[int] = None
    ) -> None:
        """Store search results in cache."""
    
    def get_results(
        self,
        parameters: SearchParameters
    ) -> Optional[List[FileInfo]]:
        """Retrieve search results from cache."""
    
    def invalidate_cache(
        self,
        pattern: Optional[str] = None
    ) -> None:
        """Invalidate cache entries."""
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
    
    def get_statistics(self) -> CacheStatistics:
        """Get cache statistics."""
    
    def clear_cache(self) -> None:
        """Clear all cache data."""
    
    def set_ttl(self, default_ttl_hours: int) -> None:
        """Set default TTL for new entries."""
```

**Usage Example:**
```python
cache = SearchResultCache(
    db_path="cache.db",
    memory_cache_size=500,
    default_ttl_hours=12
)

# Store results
cache.store_results(search_params, search_results, ttl_hours=6)

# Retrieve results
cached_results = cache.get_results(search_params)
if cached_results:
    print(f"Cache hit: {len(cached_results)} results")
else:
    print("Cache miss - performing new search")

# Maintenance
expired_count = cache.cleanup_expired()
print(f"Cleaned up {expired_count} expired entries")
```

##### LRUCache
```python
class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize LRU cache."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
    
    def remove(self, key: str) -> bool:
        """Remove key from cache."""
    
    def clear(self) -> None:
        """Clear all cache entries."""
    
    def size(self) -> int:
        """Get current cache size."""
```

### metadata_pipeline.py

#### Classes

##### MetadataExtractionPipeline
```python
class MetadataExtractionPipeline:
    """Extensible metadata extraction pipeline."""
    
    def __init__(
        self,
        enable_caching: bool = True,
        cache_size: int = 1000
    ):
        """Initialize metadata pipeline."""
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a single file."""
    
    def extract_batch(
        self,
        file_paths: List[str],
        max_workers: int = 4
    ) -> Dict[str, Dict[str, Any]]:
        """Extract metadata from multiple files."""
    
    def register_extractor(
        self,
        extractor: 'BaseMetadataExtractor'
    ) -> None:
        """Register custom metadata extractor."""
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get metadata extraction statistics."""
    
    def clear_cache(self) -> None:
        """Clear metadata cache."""
```

**Usage Example:**
```python
pipeline = MetadataExtractionPipeline(enable_caching=True)

# Extract from single file
metadata = pipeline.extract_metadata("/path/to/document.pdf")
print(f"Pages: {metadata.get('page_count', 'Unknown')}")

# Batch extraction
file_paths = ["/path/to/file1.jpg", "/path/to/file2.mp3"]
batch_metadata = pipeline.extract_batch(file_paths, max_workers=8)

for file_path, metadata in batch_metadata.items():
    print(f"{file_path}: {metadata}")
```

##### BaseMetadataExtractor
```python
class BaseMetadataExtractor:
    """Base class for metadata extractors."""
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions."""
        raise NotImplementedError
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from file."""
        raise NotImplementedError
    
    def can_extract(self, file_path: str) -> bool:
        """Check if extractor can handle file."""
        extension = Path(file_path).suffix.lower()
        return extension in self.get_supported_extensions()
```

##### ImageMetadataExtractor
```python
class ImageMetadataExtractor(BaseMetadataExtractor):
    """Metadata extractor for image files."""
    
    def get_supported_extensions(self) -> List[str]:
        """Returns: ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp']"""
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata including EXIF data."""
```

### performance_monitor.py

#### Enums

##### PerformanceMetricType
```python
class PerformanceMetricType(Enum):
    SYSTEM_CPU = "system_cpu"
    SYSTEM_MEMORY = "system_memory"
    SYSTEM_DISK_IO = "system_disk_io"
    SEARCH_OPERATION = "search_operation"
    SCAN_OPERATION = "scan_operation"
    CACHE_OPERATION = "cache_operation"
    METADATA_EXTRACTION = "metadata_extraction"
    DATABASE_QUERY = "database_query"
```

##### AlertLevel
```python
class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
```

#### Data Classes

##### PerformanceMetric
```python
@dataclass
class PerformanceMetric:
    """Individual performance metric measurement."""
    
    timestamp: datetime
    metric_type: PerformanceMetricType
    operation_name: str
    duration_ms: float
    resource_usage: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
```

##### PerformanceSummary
```python
@dataclass
class PerformanceSummary:
    """Summary of performance metrics over time period."""
    
    start_time: datetime
    end_time: datetime
    total_operations: int
    average_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    operations_per_second: float
    error_rate: float
    resource_usage_avg: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
```

#### Classes

##### PerformanceMonitor
```python
class PerformanceMonitor:
    """Enterprise performance monitoring system."""
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        max_memory_metrics: int = 10000,
        alert_thresholds: Optional[Dict[str, float]] = None,
        enable_system_monitoring: bool = True,
        monitoring_interval_seconds: float = 5.0
    ):
        """Initialize performance monitor."""
    
    def record_metric(
        self,
        metric_type: PerformanceMetricType,
        operation_name: str,
        duration_ms: float,
        resource_usage: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a performance metric."""
    
    def get_timer(
        self,
        operation_name: str,
        metric_type: PerformanceMetricType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'PerformanceTimer':
        """Get performance timer context manager."""
    
    def get_metrics_summary(
        self,
        metric_type: Optional[PerformanceMetricType] = None,
        time_window_minutes: int = 60,
        operation_name: Optional[str] = None
    ) -> PerformanceSummary:
        """Get performance summary for criteria."""
    
    def get_recent_alerts(self, limit: int = 50) -> List['PerformanceAlert']:
        """Get recent performance alerts."""
    
    def get_optimization_recommendations(self) -> List['OptimizationRecommendation']:
        """Generate optimization recommendations."""
    
    def export_metrics(
        self,
        output_path: str,
        format_type: str = "json",
        time_window_hours: int = 24
    ) -> None:
        """Export metrics data to file."""
    
    def start_monitoring(self) -> None:
        """Start background system monitoring."""
    
    def stop_monitoring(self) -> None:
        """Stop background system monitoring."""
```

**Usage Example:**
```python
monitor = PerformanceMonitor(
    db_path="performance.db",
    enable_system_monitoring=True
)

# Manual metric recording
monitor.record_metric(
    PerformanceMetricType.SEARCH_OPERATION,
    "filename_search",
    120.5,  # duration in ms
    metadata={"query": "document", "results_count": 15}
)

# Using timer context manager
with monitor.get_timer("file_scan", PerformanceMetricType.SCAN_OPERATION):
    scanner.scan_directory("/large/directory")

# Get performance summary
summary = monitor.get_metrics_summary(
    metric_type=PerformanceMetricType.SEARCH_OPERATION,
    time_window_minutes=30
)
print(f"Average search time: {summary.average_duration_ms:.1f}ms")

# Get optimization recommendations
recommendations = monitor.get_optimization_recommendations()
for rec in recommendations:
    print(f"{rec.severity.value}: {rec.title}")
```

##### PerformanceTimer
```python
class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(
        self,
        monitor: PerformanceMonitor,
        operation_name: str,
        metric_type: PerformanceMetricType,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize performance timer."""
    
    def __enter__(self):
        """Start timing operation."""
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metric."""
```

## Exception API

### advanced_folders_exceptions.py

#### Base Exception

##### AdvancedFoldersException
```python
class AdvancedFoldersException(Exception):
    """Base exception for Advanced Folders operations."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        """Initialize exception with context."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
    
    def get_user_message(self) -> str:
        """Get user-friendly error message."""
```

#### Specific Exceptions

##### ConfigurationException
```python
class ConfigurationException(AdvancedFoldersException):
    """Configuration-related errors."""

class InvalidConfigurationException(ConfigurationException):
    """Invalid configuration settings."""

class ConfigurationNotFoundException(ConfigurationException):
    """Configuration not found."""
```

##### FileSystemException
```python
class FileSystemException(AdvancedFoldersException):
    """File system operation errors."""

class DirectoryNotFoundException(FileSystemException):
    """Directory not found."""

class PermissionException(FileSystemException):
    """Permission denied."""

class FileAccessException(FileSystemException):
    """File access error."""
```

##### SearchException
```python
class SearchException(AdvancedFoldersException):
    """Search operation errors."""

class InvalidSearchParametersException(SearchException):
    """Invalid search parameters."""

class SearchIndexException(SearchException):
    """Search index error."""

class SearchTimeoutException(SearchException):
    """Search operation timeout."""
```

## Factory Functions

### Convenience Functions

```python
# Scanner factory
def create_file_scanner(
    performance_mode: str = "balanced",  # "fast", "balanced", "thorough"
    **kwargs
) -> FileSystemScanner:
    """Create optimized file scanner."""

# Search engine factory
def create_search_engine(
    environment_size: str = "medium",  # "small", "medium", "large"
    **kwargs
) -> SearchEngine:
    """Create optimized search engine."""

# Cache factory
def create_search_cache(
    cache_strategy: str = "hybrid",  # "memory", "database", "hybrid"
    **kwargs
) -> SearchResultCache:
    """Create optimized search cache."""

# Performance monitor factory
def create_performance_monitor(
    enable_persistence: bool = True,
    **kwargs
) -> PerformanceMonitor:
    """Create configured performance monitor."""

# Metadata pipeline factory
def create_metadata_pipeline(
    format_support: str = "comprehensive",  # "basic", "extended", "comprehensive"
    **kwargs
) -> MetadataExtractionPipeline:
    """Create configured metadata pipeline."""
```

## Error Codes

### Standard Error Codes

| Code | Category | Description |
|------|----------|-------------|
| AF001 | Configuration | Invalid folder path |
| AF002 | Configuration | Configuration not found |
| AF003 | Configuration | Database connection failed |
| AF101 | FileSystem | Directory not found |
| AF102 | FileSystem | Permission denied |
| AF103 | FileSystem | Disk space insufficient |
| AF201 | Search | Invalid search parameters |
| AF202 | Search | Search timeout |
| AF203 | Search | Index corruption |
| AF301 | Cache | Cache corruption |
| AF302 | Cache | Cache full |
| AF303 | Cache | Cache invalidation failed |
| AF401 | Metadata | Unsupported file type |
| AF402 | Metadata | Extraction failed |
| AF403 | Metadata | Corrupted file |
| AF501 | Performance | Resource exhausted |
| AF502 | Performance | Monitoring failed |

## Version Compatibility

### API Versioning

- **Version 1.0**: Initial release with core functionality
- **Version 1.1**: Enhanced metadata extraction
- **Version 1.2**: Performance optimizations
- **Version 2.0**: Planned - Real-time monitoring

### Backward Compatibility

The API maintains backward compatibility within major versions. Deprecated features are marked and supported for one major version cycle.

### Migration Guides

When upgrading between major versions, migration guides are provided to update existing code and configurations.

---

*This API documentation is part of the Richard's File Utilities (RFU) Advanced Folders system. For implementation details and examples, refer to the main documentation.*