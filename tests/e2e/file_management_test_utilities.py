#!/usr/bin/env python3
"""
File Management E2E Testing Utilities

Unified testing utilities and fixtures for File Management E2E tests.
Provides comprehensive testing infrastructure following established patterns
from existing E2E tests.

Created: 2025-09-04
Purpose: Foundation for File Management E2E test implementation
Coverage: File Finder, Catalog Files, File Rename, File Organization
"""

import functools
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

# Performance monitoring imports
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Test data generation imports
import random
import string
from dataclasses import dataclass


@dataclass
class DatasetConfig:
    """Configuration for test dataset generation"""

    file_count: int
    directory_depth: int
    max_file_size: int
    total_size_limit: int
    specialized_content: bool = False


class MockFileManagementTool:
    """
    Base mock class for all File Management tools
    Provides realistic behavior simulation while maintaining test reliability
    """

    def __init__(
        self, tool_name: str, capabilities: Optional[Dict[str, Any]] = None
    ):
        self.tool_name = tool_name
        self.capabilities = capabilities or {}
        self.status = "initialized"
        self.progress = 0
        self.operation_history = []
        self.resource_usage = {"memory": 0, "cpu": 0, "disk_io": 0}
        self.workflow_events = []
        self.error_simulation_config = {}
        self._should_cancel = False
        self._performance_metrics = {
            "start_time": None,
            "end_time": None,
            "operations_count": 0,
            "bytes_processed": 0,
        }

        # Signal simulation
        self.progress_updated = Mock()
        self.progress_percentage = Mock()
        self.progress_message = Mock()
        self.milestone_reached = Mock()
        self.operation_complete = Mock()
        self.error_occurred = Mock()
        self.operation_cancelled = Mock()

    def show(self) -> str:
        """Simulate tool display"""
        self.status = "running"
        self.workflow_events.append(f"Tool {self.tool_name} displayed")
        return f"Mock {self.tool_name} tool displayed"

    def close(self) -> str:
        """Simulate tool closure"""
        self.status = "closed"
        self.workflow_events.append(f"Tool {self.tool_name} closed")
        return f"Mock {self.tool_name} tool closed"

    def process_data(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Core data processing simulation
        Provides realistic behavior with performance tracking
        """
        if self._should_cancel:
            self.operation_cancelled.emit()
            return {
                "status": "cancelled",
                "message": "Operation cancelled by user",
            }

        # Update performance metrics
        self._performance_metrics["start_time"] = datetime.now()
        self._performance_metrics["operations_count"] += 1
        self._performance_metrics["bytes_processed"] += len(str(data))

        # Simulate progress reporting
        self.progress_updated.emit(1, 1)
        self.progress_percentage.emit(100)
        self.progress_message.emit(f"Processing data with {self.tool_name}")

        # Simulate resource usage
        self.resource_usage["memory"] += 10
        self.resource_usage["cpu"] += 5
        self.resource_usage["disk_io"] += len(str(data)) // 1024

        # Log operation
        operation_log = {
            "timestamp": datetime.now().isoformat(),
            "operation": f"{self.tool_name}_processing",
            "data_size": len(str(data)),
            "kwargs": kwargs,
        }
        self.operation_history.append(operation_log)

        # Simulate processing time for realistic behavior
        time.sleep(0.01)  # Minimal delay for realistic simulation

        self._performance_metrics["end_time"] = datetime.now()

        result = {
            "status": "success",
            "result": f"processed_by_{self.tool_name}",
            "operations_count": self._performance_metrics["operations_count"],
            "timestamp": datetime.now().isoformat(),
        }

        self.operation_complete.emit(result)
        return result

    def get_resource_usage(self) -> Dict[str, int]:
        """Get current resource usage"""
        return self.resource_usage.copy()

    def simulate_error(
        self, error_type: str, error_message: str
    ) -> Dict[str, Any]:
        """Error injection for testing error handling"""
        self.workflow_events.append(
            f"Error simulated: {error_type} - {error_message}"
        )
        error_result = {
            "status": "error",
            "error_type": error_type,
            "message": error_message,
        }
        self.error_occurred.emit(error_message)
        return error_result

    def cancel_operation(self):
        """Cancellation support"""
        self._should_cancel = True
        self.workflow_events.append("Operation cancellation requested")


class MockFileFinderTool(MockFileManagementTool):
    """
    Specialized mock for File Finder tool
    Implements search functionality simulation
    """

    def __init__(self):
        super().__init__(
            "FileFinder",
            {
                "text_search": True,
                "file_type_filtering": True,
                "size_parameters": True,
                "date_range_filtering": True,
                "export_formats": ["json", "csv", "txt"],
            },
        )
        self.search_results = []
        self.current_search_criteria = {}

    def search_files(
        self, directory_path: str, search_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate file search operation"""
        self.current_search_criteria = search_criteria

        # Simulate search results based on criteria
        mock_results = self._generate_mock_search_results(
            directory_path, search_criteria
        )
        self.search_results = mock_results

        return self.process_data(
            f"search_{directory_path}",
            criteria=search_criteria,
            results_count=len(mock_results),
        )

    def _generate_mock_search_results(
        self, directory_path: str, criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate realistic mock search results"""
        file_extensions = [
            ".txt",
            ".pdf",
            ".doc",
            ".jpg",
            ".png",
            ".mp4",
            ".zip",
        ]
        mock_files = []

        # Generate based on search criteria
        result_count = (
            random.randint(5, 50)
            if "text" in criteria
            else random.randint(1, 20)
        )

        for i in range(result_count):
            mock_file = {
                "name": f"mock_file_{i:03d}{random.choice(file_extensions)}",
                "path": os.path.join(directory_path, f"mock_file_{i:03d}"),
                "size": random.randint(1024, 10 * 1024 * 1024),
                "modified_date": datetime.now()
                - timedelta(days=random.randint(1, 365)),
                "file_type": random.choice(file_extensions)[1:],  # Remove dot
            }
            mock_files.append(mock_file)

        return mock_files

    def export_results(
        self, export_format: str, output_path: str
    ) -> Dict[str, Any]:
        """Simulate result export functionality"""
        if export_format not in self.capabilities["export_formats"]:
            return {
                "status": "error",
                "message": f"Unsupported format: {export_format}",
            }

        return self.process_data(
            f"export_{export_format}",
            output_path=output_path,
            results_count=len(self.search_results),
        )


class MockCatalogFilesTool(MockFileManagementTool):
    """
    Specialized mock for Catalog Files tool
    Implements HTML catalog generation simulation
    """

    def __init__(self):
        super().__init__(
            "CatalogFiles",
            {
                "html_generation": True,
                "recursive_cataloging": True,
                "metadata_inclusion": True,
                "template_customization": True,
                "export_formats": ["html", "pdf", "json"],
            },
        )
        self.catalog_data = {}
        self.generation_options = {}

    def generate_catalog(
        self, directory_path: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Simulate HTML catalog generation"""
        self.generation_options = options or {}

        # Simulate catalog data generation
        catalog_info = self._generate_mock_catalog_data(
            directory_path, options
        )
        self.catalog_data = catalog_info

        return self.process_data(
            f"catalog_{directory_path}",
            options=options,
            file_count=catalog_info["file_count"],
        )

    def _generate_mock_catalog_data(
        self, directory_path: str, options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate mock catalog data structure"""
        options = options or {}

        # Simulate directory scanning
        file_count = (
            random.randint(10, 500)
            if options.get("recursive")
            else random.randint(5, 50)
        )

        catalog_data = {
            "directory": directory_path,
            "file_count": file_count,
            "total_size": random.randint(
                1024 * 1024, 100 * 1024 * 1024
            ),  # 1MB - 100MB
            "generation_date": datetime.now().isoformat(),
            "options": options,
            "files": [],
        }

        # Generate mock file entries
        for i in range(file_count):
            file_entry = {
                "name": f"catalog_file_{i:03d}.txt",
                "size": random.randint(1024, 1024 * 1024),
                "type": "text",
                "modified": (
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ).isoformat(),
            }
            catalog_data["files"].append(file_entry)

        return catalog_data

    def export_catalog(
        self, format_type: str, output_path: str
    ) -> Dict[str, Any]:
        """Simulate catalog export functionality"""
        if not self.catalog_data:
            return {"status": "error", "message": "No catalog data available"}

        return self.process_data(
            f"export_catalog_{format_type}",
            output_path=output_path,
            format=format_type,
        )


class MockRFUHub:
    """
    Mock RFU Hub for File Management E2E testing
    Provides hub integration functionality
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.registered_tools = {}
        self.tool_status = {}
        self.system_metrics = {"cpu": 0, "memory": 0, "disk": 0}
        self.hub_events = []
        self.resource_allocation = {"max_threads": 4, "max_memory_mb": 512}

    def register_tool(
        self, tool_name: str, tool_instance: MockFileManagementTool
    ) -> bool:
        """Register a file management tool with the hub"""
        self.registered_tools[tool_name] = tool_instance
        self.tool_status[tool_name] = {
            "status": "registered",
            "last_activity": datetime.now().isoformat(),
        }
        self.hub_events.append(f"Tool registered: {tool_name}")
        return True

    def open_file_finder(self) -> MockFileFinderTool:
        tool = MockFileFinderTool()
        self.register_tool("file_finder", tool)
        return tool

    def open_catalog_files(self) -> MockCatalogFilesTool:
        tool = MockCatalogFilesTool()
        self.register_tool("catalog_files", tool)
        return tool

    def open_file_rename(self) -> "MockFileRenameTool":
        tool = MockFileRenameTool()
        self.register_tool("file_rename", tool)
        return tool

    def open_file_organization(self) -> "MockFileOrganizationTool":
        tool = MockFileOrganizationTool()
        self.register_tool("file_organization", tool)
        return tool


class MockFileOrganizationTool(MockFileManagementTool):
    """
    Specialized mock for File Organization tool
    Implements rule-based organization simulation
    """

    def __init__(self):
        super().__init__(
            "FileOrganization",
            {
                "rule_based_organization": True,
                "directory_creation": True,
                "file_type_categorization": True,
                "conflict_resolution": True,
                "organization_modes": [
                    "by_type",
                    "by_date",
                    "by_size",
                    "custom_rules",
                ],
            },
        )
        self.organization_rules = []
        self.organization_results = []
        self.directory_structure = {}

    def create_organization_rules(
        self, rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate organization rule creation"""
        self.organization_rules = rules
        return self.process_data("create_rules", rules_count=len(rules))

    def organize_files(
        self,
        source_directory: str,
        rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Simulate file organization operation"""
        active_rules = rules or self.organization_rules

        if not active_rules:
            return {
                "status": "error",
                "message": "No organization rules defined",
            }

        # Simulate organization process
        organization_results = self._simulate_file_organization(
            source_directory, active_rules
        )
        self.organization_results = organization_results

        return self.process_data(
            f"organize_{source_directory}",
            rules_count=len(active_rules),
            files_organized=len(organization_results),
        )

    def _simulate_file_organization(
        self, source_directory: str, rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Simulate the file organization process"""
        # Generate mock files to organize
        file_count = random.randint(10, 100)
        organization_results = []

        file_types = ["documents", "images", "videos", "archives", "other"]

        for i in range(file_count):
            file_name = f"file_{i:03d}.txt"
            file_type = random.choice(file_types)
            destination = os.path.join(source_directory, file_type, file_name)

            # Simulate organization operation
            result = {
                "source": os.path.join(source_directory, file_name),
                "destination": destination,
                "rule_applied": f"Type-based rule: {file_type}",
                "status": "success" if random.random() > 0.05 else "conflict",
            }
            organization_results.append(result)

        return organization_results

    def resolve_conflicts(
        self, conflict_resolution_strategy: str
    ) -> Dict[str, Any]:
        """Simulate conflict resolution"""
        conflicts = [
            r for r in self.organization_results if r["status"] == "conflict"
        ]

        if not conflicts:
            return {"status": "success", "message": "No conflicts to resolve"}

        # Simulate conflict resolution
        for conflict in conflicts:
            conflict["status"] = "resolved"
            conflict["resolution"] = conflict_resolution_strategy

        return self.process_data(
            "resolve_conflicts",
            conflicts_resolved=len(conflicts),
            strategy=conflict_resolution_strategy,
        )


class MockFileRenameTool(MockFileManagementTool):
    """
    Specialized mock for File Rename tool
    Implements batch rename and pattern-based renaming simulation
    """

    def __init__(self):
        super().__init__(
            "FileRename",
            {
                "batch_rename": True,
                "pattern_based_rename": True,
                "preview_functionality": True,
                "undo_capability": True,
                "rename_modes": ["sequential", "pattern", "metadata"],
            },
        )
        self.rename_operations = []
        self.rename_history = []
        self.preview_data = []

    def preview_rename(
        self, files: List[str], rename_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate rename preview functionality"""
        preview_results = []

        for i, file_path in enumerate(files):
            original_name = os.path.basename(file_path)
            # Simulate pattern application
            new_name = self._apply_rename_pattern(
                original_name, rename_pattern, i
            )

            preview_results.append(
                {
                    "original": original_name,
                    "new": new_name,
                    "path": file_path,
                    "status": "ready",
                }
            )

        self.preview_data = preview_results
        return self.process_data(
            f"preview_rename_{len(files)}_files", pattern=rename_pattern
        )

    def apply_rename(
        self, confirmed_operations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Simulate rename operation application"""
        operations = confirmed_operations or self.preview_data

        # Simulate rename execution
        results = []
        for operation in operations:
            # Simulate potential conflicts or errors
            if random.random() < 0.05:  # 5% chance of simulated error
                result = {
                    "operation": operation,
                    "status": "error",
                    "message": "Simulated file access error",
                }
            else:
                result = {
                    "operation": operation,
                    "status": "success",
                    "message": f"Renamed {operation['original']} to {operation['new']}",
                }
            results.append(result)

        # Add to history for undo functionality
        self.rename_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "operations": operations,
                "results": results,
            }
        )

        return self.process_data(f"apply_rename_{len(operations)}_files")

    def _apply_rename_pattern(
        self, original_name: str, pattern: Dict[str, Any], index: int
    ) -> str:
        """Simulate pattern application logic"""
        if pattern.get("mode") == "sequential":
            base_name = pattern.get("base_name", "file")
            extension = os.path.splitext(original_name)[1]
            return f"{base_name}_{index:03d}{extension}"
        elif pattern.get("mode") == "pattern":
            # Simulate regex pattern application
            return f"pattern_applied_{original_name}"
        else:
            return f"renamed_{original_name}"

    def undo_last_operation(self) -> Dict[str, Any]:
        """Simulate undo functionality"""
        if not self.rename_history:
            return {"status": "error", "message": "No operations to undo"}

        last_operation = self.rename_history.pop()
        return self.process_data(
            "undo_operation",
            operations_count=len(last_operation["operations"]),
        )


class FileManagementTestDataFactory:
    """
    Advanced test data factory for File Management scenarios
    Creates realistic datasets optimized for specific test types
    """

    # Dataset Size Configurations
    DATASET_CONFIGS = {
        "small": DatasetConfig(
            file_count=50,
            directory_depth=3,
            max_file_size=1024 * 1024,  # 1MB
            total_size_limit=50 * 1024 * 1024,  # 50MB
        ),
        "medium": DatasetConfig(
            file_count=500,
            directory_depth=5,
            max_file_size=10 * 1024 * 1024,  # 10MB
            total_size_limit=500 * 1024 * 1024,  # 500MB
        ),
        "large": DatasetConfig(
            file_count=2000,
            directory_depth=8,
            max_file_size=50 * 1024 * 1024,  # 50MB
            total_size_limit=2 * 1024 * 1024 * 1024,  # 2GB
        ),
    }

    @staticmethod
    def create_search_optimized_dataset(
        base_path: Optional[str], size: str = "medium"
    ) -> str:
        """Create dataset optimized for File Finder testing"""
        if base_path is None:
            base_path = tempfile.mkdtemp(prefix=f"fm_search_{size}_")

        config = FileManagementTestDataFactory.DATASET_CONFIGS[size]

        # Create search-friendly structure
        search_structure = {
            "documents": {
                "reports": {},
                "manuals": {},
            },
            "code": {
                "python": {},
                "javascript": {},
            },
            "media": {
                "images": {},
            },
        }

        FileManagementTestDataFactory._create_structure(
            base_path, search_structure, config
        )
        FileManagementTestDataFactory._create_searchable_content(
            base_path, config
        )

        return base_path

    @staticmethod
    def _create_structure(
        base_path: str, structure: Dict[str, Any], config: DatasetConfig
    ) -> None:
        """Create physical file structure"""
        file_extensions = {
            "documents": [".txt", ".doc", ".pdf"],
            "code": [".py", ".js"],
            "media": [".jpg", ".png"],
        }

        def populate_structure(
            current_path: str, struct: Dict[str, Any], depth: int = 0
        ) -> None:
            if depth > config.directory_depth:
                return

            for name, substruct in struct.items():
                dir_path = os.path.join(current_path, name)
                os.makedirs(dir_path, exist_ok=True)

                # Create files in this directory
                extensions = file_extensions.get(name, [".txt"])
                files_per_dir = min(config.file_count // (2**depth), 20)

                for i in range(files_per_dir):
                    ext = random.choice(extensions)
                    filename = f"{name}_file_{i:03d}{ext}"
                    filepath = os.path.join(dir_path, filename)

                    content_size = random.randint(
                        1024, min(config.max_file_size, 1024 * 1024)
                    )
                    content = f"Test content for {filename}\n" * (
                        content_size // 50
                    )

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)

                # Recurse into subdirectories
                if isinstance(substruct, dict):
                    populate_structure(dir_path, substruct, depth + 1)

        populate_structure(base_path, structure)

    @staticmethod
    def _create_searchable_content(
        base_path: str, config: DatasetConfig
    ) -> None:
        """Create files with searchable content"""
        search_keywords = ["project", "report", "analysis", "documentation"]

        # Create mixed content directory
        mixed_dir = os.path.join(base_path, "mixed_content")
        os.makedirs(mixed_dir, exist_ok=True)

        for i in range(10):
            filename = f"searchable_{i:02d}.txt"
            filepath = os.path.join(mixed_dir, filename)

            content_lines = []
            for j in range(20):
                line = f"Line {j} containing {random.choice(search_keywords)} information."
                content_lines.append(line)

            content = "\n".join(content_lines)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)


class FileManagementPerformanceMonitor:
    """
    Performance monitoring and benchmarking for File Management operations
    """

    PERFORMANCE_TARGETS = {
        "file_finder": {
            "text_search": 15,
            "recursive_scan": 30,
            "result_export": 10,
        }
    }

    def __init__(self):
        self.operation_metrics = {}

    def start_monitoring(self, tool_name: str, operation_name: str) -> None:
        """Start monitoring for specific operation"""
        key = f"{tool_name}.{operation_name}"
        self.operation_metrics[key] = {
            "start_time": time.time(),
            "start_memory": self._get_memory_usage(),
        }

    def stop_monitoring(
        self, tool_name: str, operation_name: str
    ) -> Dict[str, Any]:
        """Stop monitoring and record results"""
        key = f"{tool_name}.{operation_name}"

        if key not in self.operation_metrics:
            return {"status": "error", "message": "Monitoring not started"}

        metrics = self.operation_metrics[key]
        duration = time.time() - metrics["start_time"]

        result = {
            "duration": duration,
            "target_met": self._validate_performance_target(
                tool_name, operation_name, duration
            ),
        }

        del self.operation_metrics[key]
        return result

    def _validate_performance_target(
        self, tool_name: str, operation_name: str, duration: float
    ) -> bool:
        """Validate operation against performance targets"""
        targets = self.PERFORMANCE_TARGETS.get(tool_name, {})
        target_time = targets.get(operation_name)
        return duration <= target_time if target_time else True

    def _get_memory_usage(self) -> int:
        """Get current memory usage for monitoring"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss
            except Exception:
                pass
        return 0


class FileManagementSignalTracker:
    """
    Signal tracking for workflow validation
    """

    def __init__(self, tool_instance: MockFileManagementTool):
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
            "total_events": len(self.workflow_events),
            "error_events": len(self.error_events),
            "completion_status": "Completion:" in str(self.workflow_events),
        }


# Pytest Fixtures


@pytest.fixture(scope="function")
def file_finder_test_environment():
    """Specialized environment for File Finder testing"""
    test_path = FileManagementTestDataFactory.create_search_optimized_dataset(
        None, "medium"
    )
    hub = MockRFUHub()
    mock_finder = hub.open_file_finder()

    yield {
        "test_data_path": test_path,
        "tool": mock_finder,
        "signal_tracker": FileManagementSignalTracker(mock_finder),
        "performance_monitor": FileManagementPerformanceMonitor(),
        "hub": hub,
    }

    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def file_rename_test_environment():
    """Specialized environment for File Rename testing"""
    test_path = FileManagementTestDataFactory.create_search_optimized_dataset(
        None, "medium"
    )
    hub = MockRFUHub()
    mock_rename = hub.open_file_rename()

    yield {
        "test_data_path": test_path,
        "tool": mock_rename,
        "signal_tracker": FileManagementSignalTracker(mock_rename),
        "performance_monitor": FileManagementPerformanceMonitor(),
        "hub": hub,
    }

    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def catalog_files_test_environment():
    """Specialized environment for Catalog Files testing"""
    test_path = FileManagementTestDataFactory.create_search_optimized_dataset(
        None, "medium"
    )
    hub = MockRFUHub()
    mock_catalog = hub.open_catalog_files()

    yield {
        "test_data_path": test_path,
        "tool": mock_catalog,
        "signal_tracker": FileManagementSignalTracker(mock_catalog),
        "performance_monitor": FileManagementPerformanceMonitor(),
        "hub": hub,
    }

    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture(scope="function")
def file_rename_test_environment():
    """Specialized environment for File Rename testing"""
    test_path = FileManagementTestDataFactory.create_search_optimized_dataset(
        None, "medium"
    )
    hub = MockRFUHub()
    mock_rename = hub.open_file_rename()

    yield {
        "test_data_path": test_path,
        "tool": mock_rename,
        "signal_tracker": FileManagementSignalTracker(mock_rename),
        "performance_monitor": FileManagementPerformanceMonitor(),
        "hub": hub,
    }

    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)


# Utility Functions


def assert_performance_target(
    duration: float, tool_name: str, operation_name: str
) -> None:
    """Assert operation meets performance targets"""
    targets = FileManagementPerformanceMonitor.PERFORMANCE_TARGETS
    target_time = targets.get(tool_name, {}).get(operation_name)

    if target_time:
        assert (
            duration <= target_time
        ), f"{tool_name}.{operation_name} took {duration:.2f}s, target: {target_time}s"


if __name__ == "__main__":
    print("File Management E2E Testing Utilities - Ready for use")
    print(
        f"Available dataset types: {list(FileManagementTestDataFactory.DATASET_CONFIGS.keys())}"
    )
    print(
        f"Performance targets defined for: {list(FileManagementPerformanceMonitor.PERFORMANCE_TARGETS.keys())}"
    )


@pytest.fixture(scope="function")
def file_organization_test_environment():
    """Specialized environment for File Organization testing"""
    test_path = FileManagementTestDataFactory.create_search_optimized_dataset(
        None, "medium"
    )
    hub = MockRFUHub()
    mock_organization = hub.open_file_organization()

    yield {
        "test_data_path": test_path,
        "tool": mock_organization,
        "signal_tracker": FileManagementSignalTracker(mock_organization),
        "performance_monitor": FileManagementPerformanceMonitor(),
        "hub": hub,
    }

    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)
