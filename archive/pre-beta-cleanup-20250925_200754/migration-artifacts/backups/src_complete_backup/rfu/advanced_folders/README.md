# Advanced Folders System - Technical Documentation

## Overview

The Advanced Folders system is a comprehensive file management enhancement for Richard's File Utilities (RFU) that provides enterprise-grade file organization, search, and monitoring capabilities. This documentation covers the technical architecture, API reference, integration patterns, and usage guidelines.

## System Architecture

### Core Components

```
Advanced Folders System
├── Models Layer
│   ├── folder_configuration.py    # Folder settings and preferences
│   └── search_parameters.py       # Search query configurations
├── Core Engine Layer
│   ├── file_system_scanner.py     # File discovery and indexing
│   ├── search_engine.py           # Search algorithms and indexing
│   ├── search_cache.py            # Multi-tier caching system
│   ├── metadata_pipeline.py       # File metadata extraction
│   └── performance_monitor.py     # Performance tracking and optimization
├── Exception Layer
│   └── advanced_folders_exceptions.py  # Comprehensive error handling
└── Tests Layer
    ├── test_advanced_folders.py   # Comprehensive test suite
    └── test_core_functionality.py # Core functionality validation
```

### Data Flow Architecture

```
File System → Scanner → Search Engine → Cache → UI
     ↓           ↓           ↓           ↓      ↑
Metadata → Extraction → Indexing → Storage → Results
     ↓           ↓           ↓           ↓
Performance → Monitoring → Metrics → Optimization
```

## API Reference

### FileSystemScanner

**Purpose**: Enterprise-grade file system scanning with multi-threading and comprehensive metadata extraction.

#### Classes

##### FileSystemScanner

```python
class FileSystemScanner:
    def __init__(self, max_workers: int = 4, follow_symlinks: bool = False)
    
    def scan_directory(
        self, 
        directory: str, 
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
        exclusion_patterns: Optional[List[str]] = None,
        max_files: Optional[int] = None
    ) -> List[FileInfo]
    
    def get_scan_statistics(self) -> ScanStatistics
```

**Example Usage:**
```python
scanner = FileSystemScanner(max_workers=8)
files = scanner.scan_directory(
    "/path/to/directory",
    recursive=True,
    file_extensions=['.pdf', '.docx', '.txt'],
    exclusion_patterns=['*.tmp', '.*']
)
stats = scanner.get_scan_statistics()
print(f"Scanned {stats.total_files} files in {stats.scan_duration_seconds:.2f}s")
```

##### FileInfo

```python
@dataclass
class FileInfo:
    path: str
    name: str
    size: int
    modified_time: datetime
    is_directory: bool
    extension: str
    permissions: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]
    def from_dict(cls, data: Dict[str, Any]) -> 'FileInfo'
```

### SearchEngine

**Purpose**: Scalable search engine supporting 10M+ files with memory/database indexing strategies.

#### Classes

##### SearchEngine

```python
class SearchEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        use_memory_index: bool = True,
        index_strategy: str = "hybrid"
    )
    
    def add_file(self, file_info: FileInfo) -> None
    def remove_file(self, file_path: str) -> None
    def search(self, parameters: SearchParameters) -> List[FileInfo]
    def get_search_metrics(self) -> SearchMetrics
    def rebuild_index(self) -> None
```

**Example Usage:**
```python
engine = SearchEngine(db_path="search_index.db")

# Index files
for file_info in scanned_files:
    engine.add_file(file_info)

# Search
params = SearchParameters(
    query="document",
    scope=SearchScope.ALL_FOLDERS,
    search_type=SearchType.FILENAME,
    case_sensitive=False
)
results = engine.search(params)
```

##### SearchParameters

```python
@dataclass
class SearchParameters:
    query: str
    scope: SearchScope
    search_type: SearchType
    case_sensitive: bool = False
    include_subdirectories: bool = True
    file_size_min: Optional[int] = None
    file_size_max: Optional[int] = None
    date_modified_after: Optional[datetime] = None
    date_modified_before: Optional[datetime] = None
    file_extensions: Optional[List[str]] = None
    
    def is_valid(self) -> bool
    def get_cache_key(self) -> str
```

### SearchResultCache

**Purpose**: Multi-tier caching system with TTL management and cache invalidation.

#### Classes

##### SearchResultCache

```python
class SearchResultCache:
    def __init__(
        self,
        db_path: Optional[str] = None,
        memory_cache_size: int = 1000,
        default_ttl_hours: int = 24
    )
    
    def store_results(
        self, 
        parameters: SearchParameters, 
        results: List[FileInfo],
        ttl_hours: Optional[int] = None
    ) -> None
    
    def get_results(self, parameters: SearchParameters) -> Optional[List[FileInfo]]
    def invalidate_cache(self, pattern: Optional[str] = None) -> None
    def get_statistics(self) -> CacheStatistics
    def cleanup_expired(self) -> int
```

**Example Usage:**
```python
cache = SearchResultCache(db_path="cache.db", memory_cache_size=500)

# Store search results
cache.store_results(search_params, search_results, ttl_hours=12)

# Retrieve cached results
cached_results = cache.get_results(search_params)
if cached_results:
    print(f"Found {len(cached_results)} cached results")
```

### MetadataExtractionPipeline

**Purpose**: Extensible metadata extraction supporting 50+ file formats.

#### Classes

##### MetadataExtractionPipeline

```python
class MetadataExtractionPipeline:
    def __init__(self, enable_caching: bool = True)
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]
    def extract_batch(self, file_paths: List[str]) -> Dict[str, Dict[str, Any]]
    def register_extractor(self, extractor: BaseMetadataExtractor) -> None
    def get_supported_formats(self) -> List[str]
    def get_extraction_statistics(self) -> Dict[str, Any]
```

**Supported File Types:**
- **Images**: JPEG, PNG, GIF, TIFF, BMP (EXIF data, dimensions, camera info)
- **Audio**: MP3, FLAC, OGG, WAV (ID3 tags, duration, bitrate)
- **Documents**: PDF, DOCX, XLSX, PPTX (properties, metadata, content stats)
- **Archives**: ZIP, RAR, 7Z, TAR (contents, compression info)
- **Video**: MP4, AVI, MKV, MOV (duration, resolution, codec info)

**Example Usage:**
```python
pipeline = MetadataExtractionPipeline()

# Extract metadata from single file
metadata = pipeline.extract_metadata("/path/to/document.pdf")
print(f"Pages: {metadata.get('page_count', 'Unknown')}")

# Batch extraction
file_paths = ["/path/to/file1.jpg", "/path/to/file2.mp3"]
batch_metadata = pipeline.extract_batch(file_paths)
```

### PerformanceMonitor

**Purpose**: Enterprise monitoring with metrics collection and optimization recommendations.

#### Classes

##### PerformanceMonitor

```python
class PerformanceMonitor:
    def __init__(
        self,
        db_path: Optional[str] = None,
        max_memory_metrics: int = 10000,
        alert_thresholds: Optional[Dict[str, float]] = None,
        enable_system_monitoring: bool = True
    )
    
    def record_metric(
        self,
        metric_type: PerformanceMetricType,
        operation_name: str,
        duration_ms: float,
        resource_usage: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None
    
    def get_timer(
        self,
        operation_name: str,
        metric_type: PerformanceMetricType
    ) -> PerformanceTimer
    
    def get_metrics_summary(
        self,
        metric_type: Optional[PerformanceMetricType] = None,
        time_window_minutes: int = 60
    ) -> PerformanceSummary
    
    def get_optimization_recommendations(self) -> List[OptimizationRecommendation]
```

**Example Usage:**
```python
monitor = PerformanceMonitor(db_path="performance.db")

# Time operations
with monitor.get_timer("file_scan", PerformanceMetricType.SCAN_OPERATION):
    scan_results = scanner.scan_directory("/large/directory")

# Get performance summary
summary = monitor.get_metrics_summary(time_window_minutes=60)
print(f"Average operation time: {summary.average_duration_ms:.1f}ms")

# Get optimization recommendations
recommendations = monitor.get_optimization_recommendations()
for rec in recommendations:
    print(f"⚠️ {rec.title}: {rec.description}")
```

## Integration with RFU

### Main Application Integration

The Advanced Folders system integrates with the main RFU application through the established hub-and-spoke architecture:

1. **Tool Registration**: Add to main.py tool categories
2. **Database Integration**: Leverage existing database infrastructure
3. **Configuration Management**: Use ConfigManager for settings
4. **Error Handling**: Integrate with centralized logging

### Integration Example

```python
# In main.py
def init_advanced_folders_tab(self):
    """Initialize Advanced Folders tab."""
    advanced_folders_tools = [
        ("Folder Management", "Configure advanced folder settings", 
         self.open_folder_configuration),
        ("Smart Search", "Advanced file search with indexing", 
         self.open_smart_search),
        ("Performance Monitor", "Monitor system performance", 
         self.open_performance_monitor),
    ]
    
    for tool_name, description, handler in advanced_folders_tools:
        self.add_tool_to_tab("Advanced Folders", tool_name, description, handler)

def open_smart_search(self):
    """Launch Smart Search tool."""
    try:
        from src.tools.advanced_folders.smart_search_gui import SmartSearchGUI
        
        if not hasattr(self, 'smart_search_window') or not self.smart_search_window:
            self.smart_search_window = SmartSearchGUI()
            
        self.smart_search_window.show()
        self.smart_search_window.raise_()
        self.smart_search_window.activateWindow()
        
    except Exception as e:
        self.show_error_message("Smart Search Error", f"Failed to open Smart Search: {str(e)}")
```

### Configuration Integration

```python
# Configuration settings for Advanced Folders
config_manager = get_config_manager()

# Default settings
config_manager.set_setting("advanced_folders", "max_scan_workers", 4)
config_manager.set_setting("advanced_folders", "cache_size_mb", 100)
config_manager.set_setting("advanced_folders", "auto_index", True)
config_manager.set_setting("advanced_folders", "performance_monitoring", True)

# Database paths
config_manager.set_setting("advanced_folders", "search_db_path", "data/search_index.db")
config_manager.set_setting("advanced_folders", "cache_db_path", "data/search_cache.db")
config_manager.set_setting("advanced_folders", "performance_db_path", "data/performance.db")
```

## Database Schema

### Core Tables

#### folder_configurations
```sql
CREATE TABLE folder_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_path TEXT UNIQUE NOT NULL,
    display_name TEXT,
    sort_option TEXT,
    view_mode TEXT,
    filter_options_json TEXT,
    is_recursive BOOLEAN DEFAULT TRUE,
    auto_scan BOOLEAN DEFAULT FALSE,
    scan_interval_minutes INTEGER DEFAULT 60,
    exclusion_patterns_json TEXT,
    created_time TEXT DEFAULT CURRENT_TIMESTAMP,
    last_scan_time TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### search_index
```sql
CREATE TABLE search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    modified_time TEXT,
    is_directory BOOLEAN,
    file_extension TEXT,
    metadata_json TEXT,
    indexed_time TEXT DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT
);
```

#### search_cache
```sql
CREATE TABLE search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    parameters_json TEXT NOT NULL,
    results_json TEXT NOT NULL,
    created_time TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_time TEXT NOT NULL,
    access_count INTEGER DEFAULT 1,
    last_access_time TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### performance_metrics
```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    operation_name TEXT NOT NULL,
    duration_ms REAL NOT NULL,
    resource_usage_json TEXT,
    metadata_json TEXT,
    created_time TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### Exception Hierarchy

```python
AdvancedFoldersException (Base)
├── ConfigurationException
│   ├── InvalidConfigurationException
│   └── ConfigurationNotFound Exception
├── FileSystemException
│   ├── DirectoryNotFoundException
│   ├── PermissionException
│   └── FileAccessException
├── SearchException
│   ├── InvalidSearchParameters Exception
│   ├── SearchIndexException
│   └── SearchTimeoutException
├── CacheException
│   ├── CacheCorruptedException
│   └── CacheFullException
├── MetadataException
│   ├── UnsupportedFileTypeException
│   └── MetadataExtractionException
└── PerformanceException
    ├── MonitoringException
    └── ResourceExhaustedException
```

### Error Handling Best Practices

```python
try:
    scanner = FileSystemScanner()
    results = scanner.scan_directory("/path/to/scan")
    
except PermissionException as e:
    logger.warning(f"Permission denied for {e.path}: {e.message}")
    # Handle gracefully - skip restricted directories
    
except DirectoryNotFoundException as e:
    logger.error(f"Directory not found: {e.path}")
    # Show user-friendly error message
    
except FileSystemException as e:
    logger.error(f"File system error: {e.message}")
    # General file system error handling
    
except AdvancedFoldersException as e:
    logger.error(f"Advanced Folders error: {e.message}")
    # Log error with context and suggestions
    
except Exception as e:
    logger.critical(f"Unexpected error: {str(e)}")
    # Emergency error handling
```

## Performance Optimization

### Recommended Settings

#### For Small Environments (< 10K files)
```python
scanner = FileSystemScanner(max_workers=2)
engine = SearchEngine(use_memory_index=True, index_strategy="memory")
cache = SearchResultCache(memory_cache_size=100)
```

#### For Medium Environments (10K - 100K files)
```python
scanner = FileSystemScanner(max_workers=4)
engine = SearchEngine(use_memory_index=True, index_strategy="hybrid")
cache = SearchResultCache(memory_cache_size=500)
```

#### For Large Environments (100K+ files)
```python
scanner = FileSystemScanner(max_workers=8)
engine = SearchEngine(use_memory_index=False, index_strategy="database")
cache = SearchResultCache(memory_cache_size=1000)
monitor = PerformanceMonitor(enable_system_monitoring=True)
```

### Performance Monitoring

Key metrics to monitor:
- **Scan Performance**: Files per second, directory traversal time
- **Search Performance**: Query response time, index size
- **Cache Performance**: Hit rate, eviction rate
- **System Resources**: CPU, memory, disk I/O

### Optimization Recommendations

The system provides automated optimization recommendations:

1. **High Latency Detection**: Recommends caching, parallelization
2. **Memory Usage Optimization**: Suggests cache size adjustments
3. **Cache Efficiency**: Recommends eviction policy changes
4. **Index Optimization**: Suggests rebuild or strategy changes

## Testing and Validation

### Test Coverage

The test suite provides comprehensive coverage:

- **Unit Tests**: Individual component testing (90%+ coverage)
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Benchmarking and load testing
- **Error Handling Tests**: Exception handling validation

### Running Tests

```bash
# Run all tests
python -m pytest src/rfu/advanced_folders/tests/ -v

# Run specific test categories
python -m pytest src/rfu/advanced_folders/tests/test_core_functionality.py -v

# Run with coverage
python -m pytest src/rfu/advanced_folders/tests/ --cov=src.rfu.advanced_folders

# Run performance benchmarks
python src/rfu/advanced_folders/tests/test_core_functionality.py
```

### Performance Benchmarks

Expected performance benchmarks:
- **File Scanning**: > 1000 files/second
- **Search Operations**: < 100ms for 10K files
- **Cache Operations**: < 10ms retrieval time
- **Metadata Extraction**: < 50ms per file

## Deployment and Maintenance

### Installation Requirements

```python
# Core requirements
pip install sqlite3
pip install psutil  # For performance monitoring

# Optional metadata extraction requirements
pip install Pillow  # For image metadata
pip install mutagen  # For audio metadata
pip install PyPDF2  # For PDF metadata
pip install python-docx  # For Word document metadata
```

### Database Maintenance

Regular maintenance tasks:
1. **Index Optimization**: Rebuild search indexes monthly
2. **Cache Cleanup**: Remove expired cache entries daily
3. **Performance Data**: Archive old metrics quarterly
4. **Backup**: Regular database backups

```python
# Maintenance example
def perform_maintenance():
    # Clear expired cache entries
    cache.cleanup_expired()
    
    # Rebuild search index if needed
    if should_rebuild_index():
        engine.rebuild_index()
    
    # Archive old performance data
    monitor.archive_old_metrics(days_old=90)
```

### Monitoring and Alerts

Set up monitoring for:
- **Database Size**: Alert when > 1GB
- **Performance Degradation**: Alert when operations > 2x baseline
- **Error Rates**: Alert when error rate > 5%
- **Resource Usage**: Alert when memory/CPU > 80%

## Troubleshooting

### Common Issues

#### 1. Slow Scanning Performance
**Symptoms**: File scanning takes longer than expected
**Solutions**:
- Increase max_workers parameter
- Check disk I/O performance
- Exclude unnecessary directories
- Use SSD storage for better performance

#### 2. Search Results Not Found
**Symptoms**: Files exist but not returned in search
**Solutions**:
- Rebuild search index
- Check file permissions
- Verify indexing is complete
- Check exclusion patterns

#### 3. High Memory Usage
**Symptoms**: Application uses excessive memory
**Solutions**:
- Reduce memory cache size
- Use database-only indexing
- Enable cache cleanup
- Monitor with PerformanceMonitor

#### 4. Cache Miss Rate High
**Symptoms**: Low cache hit rate, poor performance
**Solutions**:
- Increase cache size
- Adjust TTL settings
- Review search patterns
- Optimize cache eviction policy

### Debugging Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Performance profiling
monitor = PerformanceMonitor(enable_system_monitoring=True)

# Cache statistics
stats = cache.get_statistics()
print(f"Hit rate: {stats.hit_rate:.1f}%")

# Search engine metrics
metrics = engine.get_search_metrics()
print(f"Index size: {metrics.total_indexed_files}")
```

## Future Enhancements

### Planned Features

1. **Real-time File Watching**: Monitor file system changes
2. **Content Search**: Full-text search within documents
3. **AI-Powered Categorization**: Automatic file organization
4. **Cloud Integration**: Support for cloud storage providers
5. **Advanced Filters**: Complex query building interface

### Extension Points

The system is designed for extensibility:

- **Custom Metadata Extractors**: Add support for new file types
- **Search Algorithms**: Implement custom search strategies
- **Cache Backends**: Add Redis, Memcached support
- **Performance Metrics**: Add custom monitoring endpoints
- **UI Components**: Create custom search interfaces

## Support and Resources

### Documentation Links
- API Reference: [Internal documentation]
- Configuration Guide: [Configuration documentation]
- Performance Tuning: [Performance documentation]
- Error Codes: [Error handling documentation]

### Support Channels
- Internal Issue Tracker
- Development Team Contact
- User Documentation Wiki
- Community Forums

---

*This documentation is part of the Richard's File Utilities (RFU) Advanced Folders implementation. For questions or issues, contact the development team.*