#!/usr/bin/env python3
"""
Metadata Tools E2E Testing Utilities

Unified testing utilities and fixtures for Metadata Tools E2E tests.
Provides comprehensive testing infrastructure following established patterns
from existing E2E test frameworks.

Created: 2025-09-04
Purpose: Foundation for Metadata Tools E2E test implementation
Coverage: Image Metadata, Office Metadata, File Touch
"""

import json
import os
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Performance monitoring imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import random


@dataclass
class MetadataDatasetConfig:
    """Configuration for Metadata Tools test dataset generation"""
    file_count: int
    directory_depth: int
    max_file_size: int
    total_size_limit: int
    image_files_count: int = 50
    office_files_count: int = 30
    timestamp_files_count: int = 100
    metadata_richness: float = 0.80
    gps_enabled_percentage: float = 0.40
    specialized_content: bool = False


class MockMetadataToolBase:
    """Base mock class for all Metadata tools"""
    
    def __init__(self, tool_name: str, capabilities: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.capabilities = capabilities or {}
        self.status = 'initialized'
        self.progress = 0
        self.operation_history = []
        self.resource_usage = {'memory': 0, 'cpu': 0, 'disk_io': 0}
        self.workflow_events = []
        self._should_cancel = False
        self._performance_metrics = {
            'start_time': None,
            'end_time': None,
            'operations_count': 0,
            'bytes_processed': 0,
            'files_processed': 0,
            'metadata_operations_count': 0
        }
        
        # Signal simulation for PyQt5 integration
        self.progress_updated = Mock()
        self.progress_percentage = Mock()
        self.progress_message = Mock()
        self.operation_complete = Mock()
        self.error_occurred = Mock()
        self.operation_cancelled = Mock()
        
        # Metadata Tools specific signals
        self.metadata_loaded = Mock()
        self.metadata_saved = Mock()
        self.file_processed = Mock()
        self.batch_completed = Mock()
        self.timestamp_modified = Mock()
        self.privacy_scan_complete = Mock()
    
    def show(self) -> str:
        """Simulate tool display"""
        self.status = 'running'
        self.workflow_events.append(f"Tool {self.tool_name} displayed")
        return f"Mock {self.tool_name} tool displayed"
    
    def close(self) -> str:
        """Simulate tool closure"""
        self.status = 'closed'
        self.workflow_events.append(f"Tool {self.tool_name} closed")
        return f"Mock {self.tool_name} tool closed"
    
    def process_data(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Core data processing simulation"""
        if self._should_cancel:
            self.operation_cancelled.emit()
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        
        # Update performance metrics
        self._performance_metrics['start_time'] = datetime.now()
        self._performance_metrics['operations_count'] += 1
        self._performance_metrics['bytes_processed'] += len(str(data))
        self._performance_metrics['files_processed'] += kwargs.get('file_count', 1)
        self._performance_metrics['metadata_operations_count'] += kwargs.get('metadata_ops', 1)
        
        # Simulate progress reporting
        total_files = kwargs.get('file_count', 1)
        for i in range(min(total_files, 5)):  # Limited simulation
            self.progress_updated.emit(i + 1, total_files)
            percentage = int((i + 1) / min(total_files, 5) * 100)
            self.progress_percentage.emit(percentage)
            self.file_processed.emit(f"file_{i}")
            time.sleep(0.001)  # Minimal delay
        
        # Simulate resource usage
        self.resource_usage['memory'] += 25
        self.resource_usage['cpu'] += 12
        self.resource_usage['disk_io'] += len(str(data)) // 256
        
        # Log operation
        operation_log = {
            'timestamp': datetime.now().isoformat(),
            'operation': f"{self.tool_name}_operation",
            'data_size': len(str(data)),
            'files_processed': self._performance_metrics['files_processed'],
            'kwargs': kwargs
        }
        self.operation_history.append(operation_log)
        
        self._performance_metrics['end_time'] = datetime.now()
        
        result = {
            "status": "success",
            "result": f"processed_by_{self.tool_name}",
            "operations_count": self._performance_metrics['operations_count'],
            "files_processed": self._performance_metrics['files_processed'],
            "metadata_operations": self._performance_metrics['metadata_operations_count'],
            "timestamp": datetime.now().isoformat()
        }
        
        self.operation_complete.emit(result)
        return result
    
    def simulate_error(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Error injection for testing"""
        self.workflow_events.append(f"Error simulated: {error_type} - {error_message}")
        error_result = {"status": "error", "error_type": error_type, "message": error_message}
        self.error_occurred.emit(error_message)
        return error_result
    
    def cancel_operation(self):
        """Cancellation support"""
        self._should_cancel = True
        self.workflow_events.append("Operation cancellation requested")


class MockImageMetadataTool(MockMetadataToolBase):
    """Specialized mock for Image Metadata tool"""
    
    def __init__(self):
        super().__init__("ImageMetadata", {
            'supported_formats': ['jpg', 'jpeg', 'tiff', 'tif'],
            'exif_extraction': True,
            'exif_editing': True,
            'gps_processing': True,
            'batch_processing': True
        })
        self.exif_data = {}
        self.gps_coordinates = {}
    
    def extract_exif_data(self, image_path: str, include_gps: bool = True) -> Dict[str, Any]:
        """Simulate EXIF data extraction"""
        exif_data = self._generate_mock_exif_data(image_path, include_gps)
        self.exif_data[image_path] = exif_data
        
        return self.process_data(f"extract_exif_{image_path}",
                               file_count=1,
                               metadata_ops=1,
                               results_count=len(exif_data))
    
    def _generate_mock_exif_data(self, image_path: str, include_gps: bool) -> Dict[str, Any]:
        """Generate realistic EXIF data"""
        exif_data = {
            'camera_settings': {
                'make': random.choice(['Canon', 'Nikon', 'Sony']),
                'model': random.choice(['EOS R5', 'D850', 'A7R IV']),
                'datetime': datetime.now().strftime('%Y:%m:%d %H:%M:%S'),
                'iso_speed': random.choice([100, 400, 800, 1600]),
                'exposure_time': f"1/{random.randint(60, 1000)}",
                'f_number': f"f/{random.uniform(1.4, 8):.1f}"
            },
            'image_info': {
                'width': random.randint(3000, 6000),
                'height': random.randint(2000, 4000),
                'color_space': 'sRGB',
                'orientation': random.choice([1, 3, 6, 8])
            }
        }
        
        if include_gps and random.random() < 0.5:
            exif_data['gps_info'] = {
                'latitude': round(random.uniform(-90.0, 90.0), 6),
                'longitude': round(random.uniform(-180.0, 180.0), 6),
                'altitude': round(random.uniform(0, 1000), 2)
            }
            self.gps_coordinates[image_path] = exif_data['gps_info']
        
        return exif_data
    
    def validate_gps_coordinates(self, image_paths: List[str]) -> Dict[str, Any]:
        """Simulate GPS coordinate validation"""
        validation_results = []
        
        for image_path in image_paths:
            if image_path in self.gps_coordinates:
                gps_data = self.gps_coordinates[image_path]
                lat_valid = -90 <= gps_data['latitude'] <= 90
                lon_valid = -180 <= gps_data['longitude'] <= 180
                
                validation_results.append({
                    'file_path': image_path,
                    'latitude_valid': lat_valid,
                    'longitude_valid': lon_valid,
                    'overall_valid': lat_valid and lon_valid
                })
            else:
                validation_results.append({
                    'file_path': image_path,
                    'has_gps_data': False,
                    'overall_valid': False
                })
        
        valid_count = len([r for r in validation_results if r.get('overall_valid', False)])
        
        return self.process_data(f"validate_gps_{len(image_paths)}_images",
                               file_count=len(image_paths),
                               metadata_ops=len(image_paths),
                               results_count=valid_count)


class MockOfficeMetadataTool(MockMetadataToolBase):
    """Specialized mock for Office Metadata tool"""
    
    def __init__(self):
        super().__init__("OfficeMetadata", {
            'supported_formats': ['docx', 'xlsx', 'pptx', 'pdf'],
            'privacy_analysis': True,
            'batch_processing': True,
            'template_application': True
        })
        self.document_properties = {}
        self.privacy_concerns = {}
    
    def extract_document_properties(self, document_path: str) -> Dict[str, Any]:
        """Simulate document property extraction"""
        properties = self._generate_mock_document_properties(document_path)
        self.document_properties[document_path] = properties
        
        privacy_analysis = self._analyze_privacy_concerns(properties)
        self.privacy_concerns[document_path] = privacy_analysis
        
        return self.process_data(f"extract_properties_{document_path}",
                               file_count=1,
                               metadata_ops=1,
                               results_count=len(properties))
    
    def _generate_mock_document_properties(self, document_path: str) -> Dict[str, Any]:
        """Generate realistic document properties"""
        file_ext = os.path.splitext(document_path)[1].lower()
        
        return {
            'core_properties': {
                'title': f"Test Document {random.randint(1, 100)}",
                'creator': random.choice(['John Doe', 'Jane Smith']),
                'subject': 'Test Subject',
                'keywords': 'test, document, metadata',
                'created': datetime.now().isoformat(),
                'modified': datetime.now().isoformat()
            },
            'app_properties': {
                'application': self._get_application_name(file_ext),
                'company': random.choice(['Test Company', 'Sample Corp']),
                'version': f"{random.randint(14, 20)}.0"
            }
        }
    
    def _get_application_name(self, file_ext: str) -> str:
        """Get application name based on file extension"""
        app_map = {
            '.docx': 'Microsoft Word', '.xlsx': 'Microsoft Excel',
            '.pptx': 'Microsoft PowerPoint', '.pdf': 'Adobe Acrobat'
        }
        return app_map.get(file_ext, 'Unknown Application')
    
    def _analyze_privacy_concerns(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document properties for privacy concerns"""
        concerns = []
        core_props = properties.get('core_properties', {})
        
        if core_props.get('creator'):
            concerns.append(f"Author name: {core_props['creator']}")
        
        return {
            'privacy_concerns': concerns,
            'risk_level': 'medium' if concerns else 'low',
            'recommendations': ['Consider removing personal information'] if concerns else []
        }


class MockFileTouchTool(MockMetadataToolBase):
    """Specialized mock for File Touch tool"""
    
    def __init__(self):
        super().__init__("FileTouch", {
            'timestamp_modification': True,
            'batch_operations': True,
            'profile_management': True,
            'cross_platform_support': True
        })
        self.file_timestamps = {}
        self.modification_history = []
    
    def get_file_timestamps(self, file_path: str) -> Dict[str, Any]:
        """Simulate file timestamp retrieval"""
        now = datetime.now()
        timestamps = {
            'access_time': now - timedelta(hours=1),
            'modification_time': now - timedelta(days=1),
            'creation_time': now - timedelta(days=30),
            'file_path': file_path
        }
        
        self.file_timestamps[file_path] = timestamps
        
        return self.process_data(f"get_timestamps_{file_path}",
                               file_count=1,
                               metadata_ops=1,
                               results_count=1)
    
    def modify_timestamps(self, file_path: str, new_timestamps: Dict[str, datetime]) -> Dict[str, Any]:
        """Simulate timestamp modification"""
        # Store original for rollback
        if file_path in self.file_timestamps:
            original = self.file_timestamps[file_path].copy()
        else:
            original = self.get_file_timestamps(file_path)
        
        # Apply modifications
        updated = self.file_timestamps.get(file_path, {}).copy()
        updated.update(new_timestamps)
        self.file_timestamps[file_path] = updated
        
        # Store in history
        self.modification_history.append({
            'file_path': file_path,
            'original_timestamps': original,
            'new_timestamps': new_timestamps,
            'timestamp': datetime.now().isoformat()
        })
        
        self.timestamp_modified.emit(file_path)
        
        return self.process_data(f"modify_timestamps_{file_path}",
                               file_count=1,
                               metadata_ops=len(new_timestamps),
                               results_count=1)


class MetadataToolsTestDataFactory:
    """Advanced test data factory for Metadata Tools scenarios"""
    
    DATASET_CONFIGS = {
        'small': MetadataDatasetConfig(
            file_count=100,
            directory_depth=3,
            max_file_size=10 * 1024 * 1024,  # 10MB
            total_size_limit=200 * 1024 * 1024,  # 200MB
            image_files_count=20,
            office_files_count=15,
            timestamp_files_count=65
        ),
        'medium': MetadataDatasetConfig(
            file_count=500,
            directory_depth=5,
            max_file_size=100 * 1024 * 1024,  # 100MB
            total_size_limit=2 * 1024 * 1024 * 1024,  # 2GB
            image_files_count=100,
            office_files_count=50,
            timestamp_files_count=350
        ),
        'large': MetadataDatasetConfig(
            file_count=2000,
            directory_depth=7,
            max_file_size=500 * 1024 * 1024,  # 500MB
            total_size_limit=10 * 1024 * 1024 * 1024,  # 10GB
            image_files_count=500,
            office_files_count=200,
            timestamp_files_count=1300
        )
    }
    
    @staticmethod
    def create_metadata_tools_dataset(base_path: Optional[str], size: str = 'medium') -> str:
        """Create dataset optimized for Metadata Tools testing"""
        if base_path is None:
            base_path = tempfile.mkdtemp(prefix=f'metadata_test_{size}_')
        
        config = MetadataToolsTestDataFactory.DATASET_CONFIGS[size]
        os.makedirs(base_path, exist_ok=True)
        
        # Create metadata-optimized structure
        structure = {
            'images': {},
            'documents': {},
            'timestamp_files': {},
            'mixed_content': {}
        }
        
        MetadataToolsTestDataFactory._create_structure(base_path, structure, config)
        return base_path
    
    @staticmethod
    def _create_structure(base_path: str, structure: Dict[str, Any], config: MetadataDatasetConfig) -> None:
        """Create physical file structure"""
        file_extensions = {
            'images': ['.jpg', '.jpeg', '.tiff'],
            'documents': ['.docx', '.xlsx', '.pptx', '.pdf'],
            'timestamp_files': ['.txt', '.log', '.data'],
            'mixed_content': ['.txt', '.jpg', '.docx']
        }
        
        for category, substruct in structure.items():
            dir_path = os.path.join(base_path, category)
            os.makedirs(dir_path, exist_ok=True)
            
            # Determine file counts based on category
            if category == 'images':
                file_count = config.image_files_count
            elif category == 'documents':
                file_count = config.office_files_count
            elif category == 'timestamp_files':
                file_count = config.timestamp_files_count
            else:
                file_count = 20
            
            extensions = file_extensions.get(category, ['.txt'])
            
            for i in range(file_count):
                ext = random.choice(extensions)
                filename = f"{category}_file_{i:03d}{ext}"
                filepath = os.path.join(dir_path, filename)
                
                # Create appropriate content
                if ext in ['.jpg', '.jpeg', '.tiff']:
                    # Create minimal image file header
                    with open(filepath, 'wb') as f:
                        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01')
                else:
                    content = f"Test content for {filename}\nGenerated for metadata testing\n"
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)


class MetadataToolsPerformanceMonitor:
    """Performance monitoring for Metadata Tools"""
    
    PERFORMANCE_TARGETS = {
        'image_metadata': {
            'exif_extraction': 20,
            'batch_processing': 60,
            'gps_validation': 15,
            'format_conversion': 30
        },
        'office_metadata': {
            'property_extraction': 25,
            'batch_processing': 90,
            'privacy_analysis': 45,
            'template_application': 35
        },
        'file_touch': {
            'timestamp_reading': 5,
            'batch_modification': 30,
            'profile_application': 20,
            'cross_platform_test': 15
        }
    }
    
    def __init__(self):
        self.operation_metrics = {}
        
    def start_monitoring(self, tool_name: str, operation_name: str) -> None:
        """Start monitoring for specific operation"""
        key = f"{tool_name}.{operation_name}"
        self.operation_metrics[key] = {
            'start_time': time.time(),
            'start_memory': self._get_memory_usage()
        }
        
    def stop_monitoring(self, tool_name: str, operation_name: str) -> Dict[str, Any]:
        """Stop monitoring and record results"""
        key = f"{tool_name}.{operation_name}"
        
        if key not in self.operation_metrics:
            return {"status": "error", "message": "Monitoring not started"}
        
        metrics = self.operation_metrics[key]
        duration = time.time() - metrics['start_time']
        
        result = {
            'duration': duration,
            'target_met': self._validate_performance_target(tool_name, operation_name, duration)
        }
        
        del self.operation_metrics[key]
        return result
        
    def _validate_performance_target(self, tool_name: str, operation_name: str, duration: float) -> bool:
        """Validate operation against performance targets"""
        targets = self.PERFORMANCE_TARGETS.get(tool_name, {})
        target_time = targets.get(operation_name)
        return duration <= target_time if target_time else True
        
    def _get_memory_usage(self) -> int:
        """Get current memory usage"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss
            except Exception:
                pass
        return 0


class MetadataToolsSignalTracker:
    """Signal tracking for Metadata Tools workflow validation"""
    
    def __init__(self, tool_instance: MockMetadataToolBase):
        self.tool_instance = tool_instance
        self.workflow_events = []
        self.error_events = []
        
    def connect_all_signals(self) -> None:
        """Connect to all tool signals for comprehensive tracking"""
        self.tool_instance.progress_updated.connect(self.track_progress)
        self.tool_instance.operation_complete.connect(self.track_completion)
        self.tool_instance.error_occurred.connect(self.track_error)
        
    def track_progress(self, current: int, total: int) -> None:
        """Track progress signal emissions"""
        self.workflow_events.append(f"Progress: {current}/{total}")
        
    def track_completion(self, result: Any) -> None:
        """Track operation completion"""
        self.workflow_events.append(f"Completion: {result}")
        
    def track_error(self, error: str) -> None:
        """Track error occurrences"""
        self.workflow_events.append(f"Error: {error}")
        self.error_events.append(error)
        
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        return {
            'total_events': len(self.workflow_events),
            'error_events': len(self.error_events),
            'completion_status': 'Completion:' in str(self.workflow_events)
        }


class MockMetadataToolsHub:
    """Mock RFU Hub for Metadata Tools E2E testing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.registered_tools = {}
        self.tool_status = {}
        self.hub_events = []
        self.resource_allocation = {'max_threads': 4, 'max_memory_mb': 1024}
    
    def register_tool(self, tool_name: str, tool_instance: MockMetadataToolBase) -> bool:
        """Register a Metadata tool with the hub"""
        self.registered_tools[tool_name] = tool_instance
        self.tool_status[tool_name] = {
            'status': 'registered',
            'last_activity': datetime.now().isoformat()
        }
        self.hub_events.append(f"Tool registered: {tool_name}")
        return True
    
    def open_image_metadata(self) -> MockImageMetadataTool:
        tool = MockImageMetadataTool()
        self.register_tool('image_metadata', tool)
        return tool
    
    def open_office_metadata(self) -> MockOfficeMetadataTool:
        tool = MockOfficeMetadataTool()
        self.register_tool('office_metadata', tool)
        return tool
    
    def open_file_touch(self) -> MockFileTouchTool:
        tool = MockFileTouchTool()
        self.register_tool('file_touch', tool)
        return tool


# Pytest Fixtures

@pytest.fixture(scope="function")
def image_metadata_test_environment():
    """Specialized environment for Image Metadata testing"""
    test_path = MetadataToolsTestDataFactory.create_metadata_tools_dataset(None, 'medium')
    hub = MockMetadataToolsHub()
    mock_image_metadata = hub.open_image_metadata()
    
    yield {
        'test_data_path': test_path,
        'tool': mock_image_metadata,
        'signal_tracker': MetadataToolsSignalTracker(mock_image_metadata),
        'performance_monitor': MetadataToolsPerformanceMonitor(),
        'hub': hub
    }
    
    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def office_metadata_test_environment():
    """Specialized environment for Office Metadata testing"""
    test_path = MetadataToolsTestDataFactory.create_metadata_tools_dataset(None, 'medium')
    hub = MockMetadataToolsHub()
    mock_office_metadata = hub.open_office_metadata()
    
    yield {
        'test_data_path': test_path,
        'tool': mock_office_metadata,
        'signal_tracker': MetadataToolsSignalTracker(mock_office_metadata),
        'performance_monitor': MetadataToolsPerformanceMonitor(),
        'hub': hub
    }
    
    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def file_touch_test_environment():
    """Specialized environment for File Touch testing"""
    test_path = MetadataToolsTestDataFactory.create_metadata_tools_dataset(None, 'medium')
    hub = MockMetadataToolsHub()
    mock_file_touch = hub.open_file_touch()
    
    yield {
        'test_data_path': test_path,
        'tool': mock_file_touch,
        'signal_tracker': MetadataToolsSignalTracker(mock_file_touch),
        'performance_monitor': MetadataToolsPerformanceMonitor(),
        'hub': hub
    }
    
    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


# Utility Functions

def assert_performance_target(duration: float, tool_name: str, operation_name: str) -> None:
    """Assert operation meets performance targets"""
    targets = MetadataToolsPerformanceMonitor.PERFORMANCE_TARGETS
    target_time = targets.get(tool_name, {}).get(operation_name)
    
    if target_time:
        assert duration <= target_time, f"{tool_name}.{operation_name} took {duration:.2f}s, target: {target_time}s"


if __name__ == "__main__":
    print("Metadata Tools E2E Testing Utilities - Ready for use")
    print(f"Available dataset types: {list(MetadataToolsTestDataFactory.DATASET_CONFIGS.keys())}")
    print(f"Performance targets defined for: {list(MetadataToolsPerformanceMonitor.PERFORMANCE_TARGETS.keys())}")