# File Management E2E Testing Utilities Specification

**Created:** 2025-09-04  
**Purpose:** Comprehensive specification for unified testing utilities and fixtures  
**Target Implementation:** `tests/e2e/file_management_test_utilities.py`  

## Overview

This document specifies the unified testing utilities and fixtures that provide the foundation for all File Management E2E tests. The utilities follow established patterns from existing E2E tests while providing specialized functionality for File Management tool testing.

## Core Utility Classes

### 1. FileManagementTestEnvironment

**Purpose:** Comprehensive test environment setup and management

```python
class FileManagementTestEnvironment:
    """
    Master test environment for File Management E2E tests
    Provides unified setup, data generation, and cleanup
    """
    
    def __init__(self, config=None):
        self.config = config or self._get_default_config()
        self.test_datasets = {}
        self.mock_hub = None
        self.performance_monitor = None
        self.temp_directories = []
        self.resource_tracker = None
    
    def setup_complete_environment(self):
        """Set up complete test environment with all components"""
        # Initialize mock hub
        # Create test datasets  
        # Setup performance monitoring
        # Initialize resource tracking
        
    def create_test_dataset(self, dataset_type, **kwargs):
        """Create specialized test datasets for different scenarios"""
        # Supported types: 'small', 'medium', 'large', 'enterprise'
        # Specialized: 'search_optimized', 'catalog_optimized', 'rename_optimized', 'organization_optimized'
        
    def get_mock_tool(self, tool_name):
        """Get configured mock tool instance"""
        # Returns: MockFileFinderTool, MockCatalogFilesTool, MockFileRenameTool, MockFileOrganizationTool
        
    def cleanup_environment(self):
        """Comprehensive cleanup of all test resources"""
        # Cleanup test datasets
        # Close mock components
        # Clear temporary files
        # Reset environment state
```

### 2. FileManagementTestDataFactory

**Purpose:** Realistic test data generation with specialized datasets

```python
class FileManagementTestDataFactory:
    """
    Advanced test data factory for File Management scenarios
    Creates realistic datasets optimized for specific test types
    """
    
    # Dataset Size Configurations
    DATASET_CONFIGS = {
        'small': {
            'file_count': 50,
            'directory_depth': 3,
            'max_file_size': 1024 * 1024,  # 1MB
            'total_size_limit': 50 * 1024 * 1024  # 50MB
        },
        'medium': {
            'file_count': 500,
            'directory_depth': 5,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'total_size_limit': 500 * 1024 * 1024  # 500MB
        },
        'large': {
            'file_count': 2000,
            'directory_depth': 8,
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'total_size_limit': 2 * 1024 * 1024 * 1024  # 2GB
        },
        'enterprise': {
            'file_count': 10000,
            'directory_depth': 12,
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'total_size_limit': 10 * 1024 * 1024 * 1024  # 10GB
        }
    }
    
    @staticmethod
    def create_search_optimized_dataset(base_path, size='medium'):
        """Create dataset optimized for File Finder testing"""
        # Features:
        # - Mixed file types with searchable content
        # - Realistic file naming patterns
        # - Varied file sizes and dates
        # - Text files with searchable keywords
        # - Binary files for comprehensive testing
        
    @staticmethod
    def create_catalog_optimized_dataset(base_path, size='medium'):
        """Create dataset optimized for Catalog Files testing"""
        # Features:
        # - Rich metadata in files
        # - Hierarchical directory structure
        # - Mixed media types with thumbnail potential
        # - Consistent naming conventions
        # - Realistic project/document structure
        
    @staticmethod
    def create_rename_optimized_dataset(base_path, size='medium'):
        """Create dataset optimized for File Rename testing"""
        # Features:
        # - Files with pattern-friendly names
        # - Sequential numbering opportunities
        # - Mixed extensions for pattern testing
        # - Metadata-rich files for substitution
        # - Conflict-prone naming scenarios
        
    @staticmethod
    def create_organization_optimized_dataset(base_path, size='medium'):
        """Create dataset optimized for File Organization testing"""
        # Features:
        # - Mixed file types for categorization
        # - Unorganized structure requiring sorting
        # - Duplicate files for conflict testing
        # - Various file sizes and dates
        # - Rule-matchable characteristics
        
    @staticmethod
    def create_cross_tool_dataset(base_path, size='medium'):
        """Create dataset for cross-tool integration testing"""
        # Features:
        # - Compatible with all File Management tools
        # - Rich metadata and content
        # - Hierarchical structure
        # - Integration-friendly data flow
        # - Performance testing capabilities
```

### 3. FileManagementMockFramework

**Purpose:** Comprehensive mock framework for all File Management tools

```python
class FileManagementMockFramework:
    """
    Unified mock framework providing consistent interfaces
    across all File Management tools
    """
    
    def __init__(self, hub_config=None):
        self.hub = MockRFUHub(hub_config)
        self.mock_tools = {}
        self.signal_trackers = {}
        self.performance_monitors = {}
        
    def create_mock_file_finder(self, config=None):
        """Create configured MockFileFinderTool"""
        return MockFileFinderTool(config or self._get_finder_config())
        
    def create_mock_catalog_files(self, config=None):
        """Create configured MockCatalogFilesTool"""
        return MockCatalogFilesTool(config or self._get_catalog_config())
        
    def create_mock_file_rename(self, config=None):
        """Create configured MockFileRenameTool"""
        return MockFileRenameTool(config or self._get_rename_config())
        
    def create_mock_file_organization(self, config=None):
        """Create configured MockFileOrganizationTool"""
        return MockFileOrganizationTool(config or self._get_organization_config())
        
    def setup_cross_tool_integration(self, tools):
        """Configure tools for cross-integration testing"""
        # Setup data flow between tools
        # Configure shared resources
        # Enable progress coordination
        
    def simulate_concurrent_operations(self, tools, operations):
        """Simulate concurrent tool operations"""
        # Thread management for concurrent testing
        # Resource contention simulation
        # Progress coordination across tools
```

### 4. FileManagementPerformanceMonitor

**Purpose:** Performance monitoring and benchmarking utilities

```python
class FileManagementPerformanceMonitor:
    """
    Performance monitoring and benchmarking for File Management operations
    """
    
    # Performance Targets (from requirements analysis)
    PERFORMANCE_TARGETS = {
        'file_finder': {
            'text_search': 15,      # seconds
            'recursive_scan': 30,   # seconds
            'result_export': 10     # seconds
        },
        'catalog_files': {
            'html_generation': 30,   # seconds
            'recursive_catalog': 60, # seconds
            'export_operations': 20  # seconds
        },
        'file_rename': {
            'batch_rename': 20,      # seconds
            'pattern_application': 25, # seconds
            'undo_operations': 5     # seconds
        },
        'file_organization': {
            'rule_based_sort': 35,   # seconds
            'directory_creation': 40, # seconds
            'conflict_resolution': 15 # seconds
        }
    }
    
    def __init__(self):
        self.operation_metrics = {}
        self.resource_usage = {}
        self.performance_history = {}
        
    def start_monitoring(self, tool_name, operation_name):
        """Start monitoring for specific operation"""
        # Initialize performance tracking
        # Start resource monitoring
        # Record baseline metrics
        
    def stop_monitoring(self, tool_name, operation_name):
        """Stop monitoring and record results"""
        # Calculate operation duration
        # Record final resource usage
        # Validate against targets
        # Store results for analysis
        
    def validate_performance_targets(self, tool_name, operation_name, duration):
        """Validate operation against performance targets"""
        # Compare against established targets
        # Generate performance report
        # Flag performance regressions
        
    def get_memory_usage(self):
        """Get current memory usage for monitoring"""
        # Cross-platform memory monitoring
        # Resource tracking utilities
        
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        # Operation summaries
        # Target compliance analysis
        # Performance trends
        # Recommendations
```

### 5. FileManagementSignalTracker

**Purpose:** Signal tracking and workflow validation utilities

```python
class FileManagementSignalTracker:
    """
    Signal tracking for workflow validation
    Based on patterns from existing SizeAnalyzer tests
    """
    
    def __init__(self, tool_instance):
        self.tool_instance = tool_instance
        self.workflow_events = []
        self.signal_connections = {}
        self.progress_history = []
        self.error_events = []
        
    def connect_all_signals(self):
        """Connect to all tool signals for comprehensive tracking"""
        # Progress signals
        # Completion signals
        # Error signals
        # Milestone signals
        # Cancellation signals
        
    def track_progress(self, current, total):
        """Track progress signal emissions"""
        self.workflow_events.append(f"Progress: {current}/{total}")
        self.progress_history.append({'current': current, 'total': total, 'timestamp': 'mock'})
        
    def track_percentage(self, percentage):
        """Track percentage progress signals"""
        self.workflow_events.append(f"Percentage: {percentage}%")
        
    def track_message(self, message):
        """Track message signals"""
        self.workflow_events.append(f"Message: {message}")
        
    def track_milestone(self, milestone, percentage):
        """Track milestone achievements"""
        self.workflow_events.append(f"Milestone: {milestone} ({percentage}%)")
        
    def track_completion(self, result):
        """Track operation completion"""
        self.workflow_events.append(f"Completion: {result}")
        
    def track_error(self, error):
        """Track error occurrences"""
        self.workflow_events.append(f"Error: {error}")
        self.error_events.append(error)
        
    def validate_signal_progression(self):
        """Validate expected signal progression"""
        # Check for required signals
        # Validate signal order
        # Verify completion sequences
        # Detect missing signals
        
    def get_workflow_summary(self):
        """Get comprehensive workflow summary"""
        return {
            'total_events': len(self.workflow_events),
            'progress_events': len([e for e in self.workflow_events if 'Progress:' in e]),
            'milestone_events': len([e for e in self.workflow_events if 'Milestone:' in e]),
            'error_events': len(self.error_events),
            'completion_status': 'Completion:' in str(self.workflow_events)
        }
```

## Specialized Test Fixtures

### 1. Core Test Fixtures

```python
@pytest.fixture(scope="function")
def file_management_environment():
    """Standard test environment for File Management E2E tests"""
    env = FileManagementTestEnvironment()
    env.setup_complete_environment()
    
    yield env
    
    env.cleanup_environment()

@pytest.fixture(scope="function") 
def mock_hub_with_tools():
    """Mock hub with all File Management tools registered"""
    framework = FileManagementMockFramework()
    
    tools = {
        'file_finder': framework.create_mock_file_finder(),
        'catalog_files': framework.create_mock_catalog_files(),
        'file_rename': framework.create_mock_file_rename(),
        'file_organization': framework.create_mock_file_organization()
    }
    
    # Register all tools with mock hub
    for tool_name, tool_instance in tools.items():
        framework.hub.register_tool(tool_name, tool_instance)
    
    yield {'hub': framework.hub, 'tools': tools, 'framework': framework}

@pytest.fixture(params=['small', 'medium', 'large'])
def scalable_test_dataset(request):
    """Parametrized fixture for scalable testing"""
    dataset_size = request.param
    base_path = FileManagementTestDataFactory.create_cross_tool_dataset(None, dataset_size)
    
    yield {'path': base_path, 'size': dataset_size}
    
    # Cleanup
    import shutil
    shutil.rmtree(base_path, ignore_errors=True)
```

### 2. Tool-Specific Fixtures

```python
@pytest.fixture
def file_finder_test_environment():
    """Specialized environment for File Finder testing"""
    env = FileManagementTestEnvironment()
    test_path = FileManagementTestDataFactory.create_search_optimized_dataset(None, 'medium')
    mock_finder = env.mock_framework.create_mock_file_finder()
    
    yield {
        'environment': env,
        'test_data_path': test_path,
        'tool': mock_finder,
        'signal_tracker': FileManagementSignalTracker(mock_finder),
        'performance_monitor': FileManagementPerformanceMonitor()
    }
    
    env.cleanup_environment()

@pytest.fixture
def catalog_files_test_environment():
    """Specialized environment for Catalog Files testing"""
    env = FileManagementTestEnvironment()
    test_path = FileManagementTestDataFactory.create_catalog_optimized_dataset(None, 'medium')
    mock_catalog = env.mock_framework.create_mock_catalog_files()
    
    yield {
        'environment': env,
        'test_data_path': test_path,
        'tool': mock_catalog,
        'signal_tracker': FileManagementSignalTracker(mock_catalog),
        'performance_monitor': FileManagementPerformanceMonitor()
    }
    
    env.cleanup_environment()

# Similar fixtures for file_rename_test_environment and file_organization_test_environment
```

### 3. Integration Test Fixtures

```python
@pytest.fixture
def cross_tool_integration_environment():
    """Environment for cross-tool integration testing"""
    framework = FileManagementMockFramework()
    test_path = FileManagementTestDataFactory.create_cross_tool_dataset(None, 'medium')
    
    # Create all tools
    tools = {
        'file_finder': framework.create_mock_file_finder(),
        'catalog_files': framework.create_mock_catalog_files(),
        'file_rename': framework.create_mock_file_rename(),
        'file_organization': framework.create_mock_file_organization()
    }
    
    # Setup cross-tool integration
    framework.setup_cross_tool_integration(tools)
    
    # Create signal trackers for each tool
    signal_trackers = {
        name: FileManagementSignalTracker(tool) 
        for name, tool in tools.items()
    }
    
    yield {
        'framework': framework,
        'test_data_path': test_path,
        'tools': tools,
        'signal_trackers': signal_trackers,
        'hub': framework.hub,
        'performance_monitor': FileManagementPerformanceMonitor()
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(test_path, ignore_errors=True)
```

## Utility Functions

### 1. Performance Testing Utilities

```python
def monitor_performance(performance_monitor, tool_name, operation_name):
    """Decorator for performance monitoring"""
    def decorator(test_function):
        @functools.wraps(test_function)
        def wrapper(*args, **kwargs):
            performance_monitor.start_monitoring(tool_name, operation_name)
            try:
                result = test_function(*args, **kwargs)
                return result
            finally:
                performance_monitor.stop_monitoring(tool_name, operation_name)
        return wrapper
    return decorator

def assert_performance_target(duration, tool_name, operation_name):
    """Assert operation meets performance targets"""
    targets = FileManagementPerformanceMonitor.PERFORMANCE_TARGETS
    target_time = targets.get(tool_name, {}).get(operation_name)
    
    if target_time:
        assert duration <= target_time, f"{tool_name}.{operation_name} took {duration}s, target: {target_time}s"

def validate_memory_usage(initial_memory, final_memory, limit_mb=200):
    """Validate memory usage within limits"""
    memory_increase_mb = (final_memory - initial_memory) / (1024 * 1024)
    assert memory_increase_mb < limit_mb, f"Memory usage increased by {memory_increase_mb:.1f}MB, limit: {limit_mb}MB"
```

### 2. Error Simulation Utilities

```python
def simulate_file_system_error(error_type, file_path=None):
    """Simulate various file system errors for testing"""
    error_types = {
        'permission_denied': PermissionError("Access denied"),
        'file_not_found': FileNotFoundError("File not found"),
        'disk_full': OSError("Disk full"),
        'file_in_use': OSError("File is in use"),
        'network_timeout': TimeoutError("Network timeout")
    }
    return error_types.get(error_type, Exception("Unknown error"))

def inject_error_during_operation(mock_tool, error_type, operation_phase):
    """Inject errors at specific operation phases"""
    # Configure mock tool for error injection
    # Set up error timing and conditions
    # Enable error recovery testing

def simulate_cancellation_scenario(mock_tool, cancellation_delay=0.5):
    """Simulate user cancellation during operations"""
    # Setup cancellation timing
    # Configure cancellation signals
    # Enable cancellation testing
```

### 3. Data Validation Utilities

```python
def validate_file_structure_integrity(base_path):
    """Validate file structure integrity after operations"""
    # Check file existence
    # Verify directory structure
    # Validate file permissions
    # Check file content integrity

def validate_export_format(export_file_path, expected_format):
    """Validate export file format compliance"""
    format_validators = {
        'json': validate_json_format,
        'csv': validate_csv_format,
        'html': validate_html_format,
        'xml': validate_xml_format
    }
    
    validator = format_validators.get(expected_format)
    if validator:
        return validator(export_file_path)
    
    return False

def validate_cross_tool_data_consistency(source_data, processed_data):
    """Validate data consistency across tool boundaries"""
    # Check data preservation
    # Validate format consistency
    # Verify metadata integrity
```

## Test Configuration

### 1. Environment Configuration

```python
FILE_MANAGEMENT_TEST_CONFIG = {
    'default_dataset_size': 'medium',
    'performance_monitoring': True,
    'signal_tracking': True,
    'error_injection': False,
    'cleanup_on_completion': True,
    'preserve_on_failure': True,
    'memory_monitoring': True,
    'concurrent_testing': True,
    'cross_tool_integration': True,
    'dataset_caching': True,
    'performance_reporting': True
}
```

### 2. Tool-Specific Configuration

```python
TOOL_SPECIFIC_CONFIGS = {
    'file_finder': {
        'search_timeout': 30,
        'max_results': 10000,
        'supported_formats': ['txt', 'csv', 'json'],
        'recursive_depth_limit': 20
    },
    'catalog_files': {
        'generation_timeout': 60,
        'max_files_per_catalog': 5000,
        'supported_exports': ['html', 'pdf', 'json'],
        'template_customization': True
    },
    'file_rename': {
        'batch_size_limit': 2000,
        'pattern_complexity_limit': 10,
        'undo_history_limit': 50,
        'preview_timeout': 10
    },
    'file_organization': {
        'max_rules': 100,
        'rule_complexity_limit': 20,
        'organization_timeout': 70,
        'conflict_resolution_modes': ['skip', 'rename', 'overwrite']
    }
}
```

This comprehensive testing utilities specification provides the foundation for implementing robust, consistent, and maintainable File Management E2E tests that follow established patterns while meeting the specific requirements of each tool component.
