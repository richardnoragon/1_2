"""
Tool Integration Framework - Phase 4 Implementation
Enterprise-grade tool integration system for RFU Multi-Pane File Explorer

This module provides sophisticated tool integration capabilities with:
- Dynamic tool discovery and registration
- File context awareness and parameter passing
- Tool lifecycle management and state tracking
- Cross-platform compatibility and error handling
- Plugin system foundation with security validation
- Performance optimization and resource management

Author: Enterprise Principal Engineer
Version: 1.0.0
Date: September 13, 2025
"""

import importlib
import logging
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from weakref import WeakSet

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

# RFU Core imports
try:
    from src.config_manager import ConfigManager
    from src.log_manager import get_log_manager
except ImportError:
    # Fallback for development
    ConfigManager = None
    
    def get_log_manager():
        return logging


class ToolStatus(Enum):
    """Tool lifecycle status enumeration."""
    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    SUSPENDED = "suspended"
    ERROR = "error"
    TERMINATED = "terminated"


class ToolCategory(Enum):
    """Tool category classification."""
    FILE_MANAGEMENT = "file_management"
    FILE_OPERATIONS = "file_operations"
    ANALYSIS = "analysis"
    SECURITY = "security"
    PDF_TOOLS = "pdf_tools"
    NETWORK = "network"
    SYSTEM = "system"
    METADATA = "metadata"
    PRIVACY = "privacy"
    CUSTOM = "custom"


class ToolCapability(Enum):
    """Tool capability flags."""
    BATCH_PROCESSING = "batch_processing"
    FILE_CONTEXT_AWARE = "file_context_aware"
    DIRECTORY_OPERATIONS = "directory_operations"
    BACKGROUND_EXECUTION = "background_execution"
    PROGRESS_REPORTING = "progress_reporting"
    CONFIGURATION_EXPORT = "configuration_export"
    PLUGIN_SUPPORT = "plugin_support"
    SECURITY_VALIDATION = "security_validation"


@dataclass
class FileContext:
    """File context information for tool operations."""
    selected_files: List[Path] = field(default_factory=list)
    current_directory: Optional[Path] = None
    pane_index: int = 0
    selection_count: int = 0
    total_size: int = 0
    file_types: Set[str] = field(default_factory=set)
    has_subdirectories: bool = False
    is_readonly: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate derived properties after initialization."""
        if self.selected_files:
            self.selection_count = len(self.selected_files)
            self.total_size = sum(
                f.stat().st_size for f in self.selected_files 
                if f.exists() and f.is_file()
            )
            self.file_types = {
                f.suffix.lower() for f in self.selected_files 
                if f.suffix
            }
            self.has_subdirectories = any(
                f.is_dir() for f in self.selected_files 
                if f.exists()
            )


@dataclass
class ToolMetadata:
    """Comprehensive tool metadata information."""
    name: str
    display_name: str
    description: str
    version: str
    category: ToolCategory
    capabilities: Set[ToolCapability] = field(default_factory=set)
    module_path: str = ""
    class_name: str = ""
    icon_path: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    file_type_filters: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    security_level: str = "standard"  # standard, elevated, restricted
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    compatibility: Dict[str, Any] = field(default_factory=dict)


class ToolInterface(ABC):
    """Abstract base class for RFU tool integration."""
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata information."""
        pass
    
    @abstractmethod
    def initialize(self, context: FileContext) -> bool:
        """Initialize tool with file context."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute tool operation."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup tool resources."""
        pass
    
    def validate_context(self, context: FileContext) -> bool:
        """Validate if tool can handle the given context."""
        return True
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get tool configuration."""
        return {}
    
    def set_configuration(self, config: Dict[str, Any]) -> None:
        """Set tool configuration."""
        pass


class ToolRegistry:
    """Centralized registry for tool management and discovery."""
    
    def __init__(self):
        self.tools: Dict[str, ToolMetadata] = {}
        self.instances: Dict[str, ToolInterface] = {}
        self.status_tracker: Dict[str, ToolStatus] = {}
        self.load_times: Dict[str, float] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self.logger = get_log_manager().get_logger('ToolRegistry')
        self._lock = threading.RLock()
    
    def register_tool(self, tool_metadata: ToolMetadata) -> bool:
        """Register a tool in the registry."""
        with self._lock:
            try:
                self.tools[tool_metadata.name] = tool_metadata
                self.status_tracker[tool_metadata.name] = ToolStatus.REGISTERED
                self.usage_stats[tool_metadata.name] = {
                    'launch_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'last_used': None,
                    'average_duration': 0.0
                }
                self.logger.info(f"Registered tool: {tool_metadata.name}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to register tool {tool_metadata.name}: {e}")
                return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the registry."""
        with self._lock:
            try:
                if tool_name in self.tools:
                    # Cleanup instance if exists
                    if tool_name in self.instances:
                        self.instances[tool_name].cleanup()
                        del self.instances[tool_name]
                    
                    del self.tools[tool_name]
                    del self.status_tracker[tool_name]
                    if tool_name in self.load_times:
                        del self.load_times[tool_name]
                    if tool_name in self.usage_stats:
                        del self.usage_stats[tool_name]
                    
                    self.logger.info(f"Unregistered tool: {tool_name}")
                    return True
                return False
            except Exception as e:
                self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
                return False
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self.tools.get(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """Get all tools in a specific category."""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def get_tools_by_capability(self, capability: ToolCapability) -> List[ToolMetadata]:
        """Get all tools with a specific capability."""
        return [tool for tool in self.tools.values() if capability in tool.capabilities]
    
    def search_tools(self, query: str) -> List[ToolMetadata]:
        """Search tools by name, description, or keywords."""
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or
                query_lower in tool.display_name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in keyword.lower() for keyword in tool.keywords)):
                results.append(tool)
        
        return results
    
    def get_tool_status(self, tool_name: str) -> ToolStatus:
        """Get current status of a tool."""
        return self.status_tracker.get(tool_name, ToolStatus.UNKNOWN)
    
    def update_tool_status(self, tool_name: str, status: ToolStatus) -> None:
        """Update tool status."""
        with self._lock:
            self.status_tracker[tool_name] = status
            self.logger.debug(f"Tool {tool_name} status updated to {status.value}")
    
    def get_usage_statistics(self, tool_name: str) -> Dict[str, Any]:
        """Get usage statistics for a tool."""
        return self.usage_stats.get(tool_name, {})
    
    def record_tool_usage(self, tool_name: str, success: bool, duration: float) -> None:
        """Record tool usage statistics."""
        with self._lock:
            if tool_name in self.usage_stats:
                stats = self.usage_stats[tool_name]
                stats['launch_count'] += 1
                if success:
                    stats['success_count'] += 1
                else:
                    stats['error_count'] += 1
                stats['last_used'] = time.time()
                
                # Update average duration
                current_avg = stats['average_duration']
                launch_count = stats['launch_count']
                stats['average_duration'] = ((current_avg * (launch_count - 1)) + duration) / launch_count


class ToolDiscovery:
    """Advanced tool discovery system with multiple strategies."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.logger = get_log_manager().get_logger('ToolDiscovery')
        self.discovery_paths = [
            Path("src/utilities"),
            Path("src/tools"),
            Path("plugins")
        ]
        self.exclude_patterns = {
            '__pycache__',
            '*.pyc',
            '*.pyo',
            'tests',
            'test_*',
            '*_test.py'
        }
    
    def discover_all_tools(self) -> List[ToolMetadata]:
        """Discover all available tools using multiple strategies."""
        discovered_tools = []
        
        try:
            # File system discovery
            fs_tools = self._discover_from_filesystem()
            discovered_tools.extend(fs_tools)
            
            # Module introspection discovery
            module_tools = self._discover_from_modules()
            discovered_tools.extend(module_tools)
            
            # Configuration-based discovery
            config_tools = self._discover_from_configuration()
            discovered_tools.extend(config_tools)
            
            # Remove duplicates
            unique_tools = self._deduplicate_tools(discovered_tools)
            
            self.logger.info(f"Discovered {len(unique_tools)} unique tools")
            return unique_tools
            
        except Exception as e:
            self.logger.error(f"Tool discovery failed: {e}")
            return []
    
    def _discover_from_filesystem(self) -> List[ToolMetadata]:
        """Discover tools by scanning the filesystem."""
        tools = []
        
        for base_path in self.discovery_paths:
            if not base_path.exists():
                continue
            
            for py_file in base_path.rglob("*.py"):
                if self._should_exclude_file(py_file):
                    continue
                
                try:
                    tool_metadata = self._extract_tool_metadata_from_file(py_file)
                    if tool_metadata:
                        tools.append(tool_metadata)
                except Exception as e:
                    self.logger.debug(f"Failed to extract metadata from {py_file}: {e}")
        
        return tools
    
    def _discover_from_modules(self) -> List[ToolMetadata]:
        """Discover tools through module introspection."""
        tools = []
        
        # Known tool module patterns
        module_patterns = [
            "src.tools.*.*.*.py",
            "src.tools.*.*"
        ]
        
        for pattern in module_patterns:
            try:
                # This would need implementation based on actual module structure
                pass
            except Exception as e:
                self.logger.debug(f"Module discovery failed for pattern {pattern}: {e}")
        
        return tools
    
    def _discover_from_configuration(self) -> List[ToolMetadata]:
        """Discover tools from configuration files."""
        tools = []
        
        if ConfigManager:
            try:
                config = ConfigManager()
                tool_configs = config.get_setting('tools', 'registered_tools', {})
                
                for tool_name, tool_config in tool_configs.items():
                    metadata = self._create_metadata_from_config(tool_name, tool_config)
                    if metadata:
                        tools.append(metadata)
                        
            except Exception as e:
                self.logger.debug(f"Configuration-based discovery failed: {e}")
        
        return tools
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from discovery."""
        for pattern in self.exclude_patterns:
            if pattern.startswith('*') and file_path.name.endswith(pattern[1:]):
                return True
            elif pattern.endswith('*') and file_path.name.startswith(pattern[:-1]):
                return True
            elif pattern in str(file_path):
                return True
        return False
    
    def _extract_tool_metadata_from_file(self, file_path: Path) -> Optional[ToolMetadata]:
        """Extract tool metadata from Python file."""
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Look for tool metadata patterns
            if 'class' in content and ('GUI' in content or 'Window' in content or 'Tool' in content):
                # Extract class names
                import re
                class_pattern = r'class\s+(\w+(?:GUI|Window|Tool|App))\s*\([^)]*\):'
                matches = re.findall(class_pattern, content)
                
                if matches:
                    class_name = matches[0]
                    
                    # Determine category from path
                    category = self._determine_category_from_path(file_path)
                    
                    # Create basic metadata
                    metadata = ToolMetadata(
                        name=class_name.lower().replace('gui', '').replace('window', '').replace('app', ''),
                        display_name=class_name,
                        description=f"Tool from {file_path.name}",
                        version="1.0.0",
                        category=category,
                        module_path=self._get_module_path(file_path),
                        class_name=class_name,
                        capabilities={ToolCapability.FILE_CONTEXT_AWARE}
                    )
                    
                    return metadata
            
        except Exception as e:
            self.logger.debug(f"Failed to extract metadata from {file_path}: {e}")
        
        return None
    
    def _determine_category_from_path(self, file_path: Path) -> ToolCategory:
        """Determine tool category from file path."""
        path_str = str(file_path).lower()
        
        if 'file_management' in path_str:
            return ToolCategory.FILE_MANAGEMENT
        elif 'file_operations' in path_str:
            return ToolCategory.FILE_OPERATIONS
        elif 'analysis' in path_str:
            return ToolCategory.ANALYSIS
        elif 'security' in path_str:
            return ToolCategory.SECURITY
        elif 'pdf' in path_str:
            return ToolCategory.PDF_TOOLS
        elif 'network' in path_str:
            return ToolCategory.NETWORK
        elif 'system' in path_str:
            return ToolCategory.SYSTEM
        elif 'metadata' in path_str:
            return ToolCategory.METADATA
        elif 'privacy' in path_str:
            return ToolCategory.PRIVACY
        else:
            return ToolCategory.CUSTOM
    
    def _get_module_path(self, file_path: Path) -> str:
        """Convert file path to module import path."""
        # Convert path to module notation
        relative_path = file_path.relative_to(Path.cwd())
        module_path = str(relative_path.with_suffix('')).replace('\\', '.').replace('/', '.')
        return module_path
    
    def _create_metadata_from_config(self, tool_name: str, config: Dict[str, Any]) -> Optional[ToolMetadata]:
        """Create tool metadata from configuration."""
        try:
            metadata = ToolMetadata(
                name=tool_name,
                display_name=config.get('display_name', tool_name),
                description=config.get('description', ''),
                version=config.get('version', '1.0.0'),
                category=ToolCategory(config.get('category', 'custom')),
                module_path=config.get('module_path', ''),
                class_name=config.get('class_name', ''),
                capabilities=set(ToolCapability(cap) for cap in config.get('capabilities', [])),
                dependencies=config.get('dependencies', []),
                security_level=config.get('security_level', 'standard')
            )
            return metadata
        except Exception as e:
            self.logger.error(f"Failed to create metadata from config for {tool_name}: {e}")
            return None
    
    def _deduplicate_tools(self, tools: List[ToolMetadata]) -> List[ToolMetadata]:
        """Remove duplicate tools from discovery results."""
        unique_tools = {}
        
        for tool in tools:
            key = f"{tool.name}_{tool.class_name}"
            if key not in unique_tools:
                unique_tools[key] = tool
            else:
                # Keep the one with more complete metadata
                existing = unique_tools[key]
                if len(tool.description) > len(existing.description):
                    unique_tools[key] = tool
        
        return list(unique_tools.values())


class ToolLauncher(QObject):
    """Advanced tool launcher with comprehensive lifecycle management."""
    
    # Signals for tool lifecycle events
    tool_launch_requested = pyqtSignal(str, dict)
    tool_launched = pyqtSignal(str, object)
    tool_launch_failed = pyqtSignal(str, str)
    tool_status_changed = pyqtSignal(str, str)
    
    def __init__(self, registry: ToolRegistry):
        super().__init__()
        self.registry = registry
        self.logger = get_log_manager().get_logger('ToolLauncher')
        self.active_tools: WeakSet = WeakSet()
        self.launch_history: List[Dict[str, Any]] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ToolLauncher")
        self._security_validator = ToolSecurityValidator()
        self._performance_monitor = ToolPerformanceMonitor()
    
    def launch_tool(self, tool_name: str, context: FileContext, **kwargs) -> bool:
        """Launch a tool with the provided context."""
        try:
            # Validate tool exists
            metadata = self.registry.get_tool_metadata(tool_name)
            if not metadata:
                self.logger.error(f"Tool not found in registry: {tool_name}")
                self.tool_launch_failed.emit(tool_name, "Tool not found")
                return False
            
            # Security validation
            if not self._security_validator.validate_tool_launch(metadata, context):
                self.logger.error(f"Security validation failed for tool: {tool_name}")
                self.tool_launch_failed.emit(tool_name, "Security validation failed")
                return False
            
            # Update status
            self.registry.update_tool_status(tool_name, ToolStatus.LOADING)
            self.tool_status_changed.emit(tool_name, ToolStatus.LOADING.value)
            
            # Launch in background thread
            future = self.thread_pool.submit(self._launch_tool_async, tool_name, context, **kwargs)
            
            # Record launch attempt
            self._record_launch_attempt(tool_name, context)
            
            self.logger.info(f"Tool launch initiated: {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch tool {tool_name}: {e}")
            self.tool_launch_failed.emit(tool_name, str(e))
            return False
    
    def _launch_tool_async(self, tool_name: str, context: FileContext, **kwargs) -> None:
        """Asynchronously launch tool in background thread."""
        start_time = time.time()
        success = False
        
        try:
            metadata = self.registry.get_tool_metadata(tool_name)
            
            # Load tool class
            tool_instance = self._load_tool_instance(metadata)
            if not tool_instance:
                raise Exception(f"Failed to load tool instance for {tool_name}")
            
            # Update status
            self.registry.update_tool_status(tool_name, ToolStatus.INITIALIZING)
            self.tool_status_changed.emit(tool_name, ToolStatus.INITIALIZING.value)
            
            # Initialize tool
            if not tool_instance.initialize(context):
                raise Exception(f"Tool initialization failed for {tool_name}")
            
            # Update status
            self.registry.update_tool_status(tool_name, ToolStatus.READY)
            self.tool_status_changed.emit(tool_name, ToolStatus.READY.value)
            
            # Execute tool
            if hasattr(tool_instance, 'show'):
                QApplication.instance().postEvent(
                    QApplication.instance(),
                    lambda: tool_instance.show()
                )
            elif hasattr(tool_instance, 'execute'):
                tool_instance.execute(**kwargs)
            
            # Track active tool
            self.active_tools.add(tool_instance)
            
            # Update status
            self.registry.update_tool_status(tool_name, ToolStatus.RUNNING)
            self.tool_status_changed.emit(tool_name, ToolStatus.RUNNING.value)
            
            # Emit success signal
            self.tool_launched.emit(tool_name, tool_instance)
            
            success = True
            self.logger.info(f"Tool launched successfully: {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Tool launch failed for {tool_name}: {e}")
            self.registry.update_tool_status(tool_name, ToolStatus.ERROR)
            self.tool_launch_failed.emit(tool_name, str(e))
        
        finally:
            # Record performance metrics
            duration = time.time() - start_time
            self.registry.record_tool_usage(tool_name, success, duration)
            self._performance_monitor.record_launch_metrics(tool_name, duration, success)
    
    def _load_tool_instance(self, metadata: ToolMetadata) -> Optional[ToolInterface]:
        """Load and instantiate a tool class."""
        try:
            # Import module
            module = importlib.import_module(metadata.module_path)
            
            # Get tool class
            tool_class = getattr(module, metadata.class_name)
            
            # Create instance
            tool_instance = tool_class()
            
            # Record load time
            self.registry.load_times[metadata.name] = time.time()
            
            return tool_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load tool instance {metadata.name}: {e}")
            return None
    
    def _record_launch_attempt(self, tool_name: str, context: FileContext) -> None:
        """Record tool launch attempt in history."""
        launch_record = {
            'tool_name': tool_name,
            'timestamp': time.time(),
            'context': {
                'file_count': context.selection_count,
                'total_size': context.total_size,
                'pane_index': context.pane_index,
                'current_directory': str(context.current_directory) if context.current_directory else None
            }
        }
        
        self.launch_history.append(launch_record)
        
        # Keep only last 100 records
        if len(self.launch_history) > 100:
            self.launch_history = self.launch_history[-100:]
    
    def get_active_tools(self) -> List[ToolInterface]:
        """Get list of currently active tools."""
        return list(self.active_tools)
    
    def get_launch_history(self) -> List[Dict[str, Any]]:
        """Get tool launch history."""
        return self.launch_history.copy()
    
    def shutdown_all_tools(self) -> None:
        """Shutdown all active tools."""
        for tool in list(self.active_tools):
            try:
                tool.cleanup()
            except Exception as e:
                self.logger.error(f"Failed to cleanup tool: {e}")
        
        self.active_tools.clear()
        self.thread_pool.shutdown(wait=True)


class ToolSecurityValidator:
    """Security validation system for tool operations."""
    
    def __init__(self):
        self.logger = get_log_manager().get_logger('ToolSecurity')
        self.security_policies = self._load_security_policies()
    
    def validate_tool_launch(self, metadata: ToolMetadata, context: FileContext) -> bool:
        """Validate tool launch against security policies."""
        try:
            # Check security level requirements
            if not self._validate_security_level(metadata.security_level):
                return False
            
            # Validate file access permissions
            if not self._validate_file_access(metadata, context):
                return False
            
            # Check dependency security
            if not self._validate_dependencies(metadata.dependencies):
                return False
            
            # Validate resource requirements
            if not self._validate_resource_limits(metadata.resource_requirements):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Security validation error: {e}")
            return False
    
    def _load_security_policies(self) -> Dict[str, Any]:
        """Load security policies from configuration."""
        default_policies = {
            'max_file_count': 10000,
            'max_total_size': 10 * 1024 * 1024 * 1024,  # 10GB
            'allowed_extensions': set(),  # Empty set means all allowed
            'blocked_extensions': {'.exe', '.bat', '.cmd', '.ps1'},
            'require_elevated_for': {'system', 'security'},
            'resource_limits': {
                'max_memory_mb': 2048,
                'max_cpu_percent': 80,
                'max_execution_time': 3600  # 1 hour
            }
        }
        
        if ConfigManager:
            try:
                config = ConfigManager()
                policies = config.get_setting('security', 'tool_policies', default_policies)
                return {**default_policies, **policies}
            except Exception:
                pass
        
        return default_policies
    
    def _validate_security_level(self, security_level: str) -> bool:
        """Validate security level requirements."""
        # This would integrate with actual security subsystem
        return security_level in {'standard', 'elevated', 'restricted'}
    
    def _validate_file_access(self, metadata: ToolMetadata, context: FileContext) -> bool:
        """Validate file access permissions."""
        policies = self.security_policies
        
        # Check file count limits
        if context.selection_count > policies['max_file_count']:
            self.logger.warning(f"File count exceeds limit: {context.selection_count}")
            return False
        
        # Check total size limits
        if context.total_size > policies['max_total_size']:
            self.logger.warning(f"Total size exceeds limit: {context.total_size}")
            return False
        
        # Check file extensions
        blocked_extensions = policies.get('blocked_extensions', set())
        if blocked_extensions and context.file_types.intersection(blocked_extensions):
            self.logger.warning(f"Blocked file types detected: {context.file_types.intersection(blocked_extensions)}")
            return False
        
        return True
    
    def _validate_dependencies(self, dependencies: List[str]) -> bool:
        """Validate tool dependencies for security."""
        # This would check dependencies against security databases
        # For now, basic validation
        return len(dependencies) < 50  # Arbitrary limit
    
    def _validate_resource_limits(self, resource_requirements: Dict[str, Any]) -> bool:
        """Validate resource requirements against limits."""
        limits = self.security_policies.get('resource_limits', {})
        
        max_memory = resource_requirements.get('memory_mb', 0)
        if max_memory > limits.get('max_memory_mb', float('inf')):
            return False
        
        max_cpu = resource_requirements.get('cpu_percent', 0)
        if max_cpu > limits.get('max_cpu_percent', 100):
            return False
        
        return True


class ToolPerformanceMonitor:
    """Performance monitoring system for tool operations."""
    
    def __init__(self):
        self.logger = get_log_manager().get_logger('ToolPerformance')
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.RLock()
    
    def record_launch_metrics(self, tool_name: str, duration: float, success: bool) -> None:
        """Record tool launch performance metrics."""
        with self._lock:
            if tool_name not in self.metrics:
                self.metrics[tool_name] = []
            
            metrics = {
                'timestamp': time.time(),
                'duration': duration,
                'success': success,
                'memory_usage': self._get_memory_usage(),
                'cpu_usage': self._get_cpu_usage()
            }
            
            self.metrics[tool_name].append(metrics)
            
            # Keep only last 50 records per tool
            if len(self.metrics[tool_name]) > 50:
                self.metrics[tool_name] = self.metrics[tool_name][-50:]
    
    def get_performance_summary(self, tool_name: str) -> Dict[str, Any]:
        """Get performance summary for a tool."""
        with self._lock:
            if tool_name not in self.metrics or not self.metrics[tool_name]:
                return {}
            
            metrics = self.metrics[tool_name]
            durations = [m['duration'] for m in metrics if m['success']]
            
            if not durations:
                return {'error': 'No successful launches recorded'}
            
            return {
                'total_launches': len(metrics),
                'successful_launches': len(durations),
                'success_rate': len(durations) / len(metrics) * 100,
                'average_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'last_launch': metrics[-1]['timestamp']
            }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0


class ToolIntegrationManager:
    """Main tool integration management system."""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.discovery = ToolDiscovery(self.registry)
        self.launcher = ToolLauncher(self.registry)
        self.logger = get_log_manager().get_logger('ToolIntegration')
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self) -> None:
        """Initialize the tool integration system."""
        try:
            # Discover all available tools
            self.logger.info("Starting tool discovery...")
            discovered_tools = self.discovery.discover_all_tools()
            
            # Register discovered tools
            registration_count = 0
            for tool_metadata in discovered_tools:
                if self.registry.register_tool(tool_metadata):
                    registration_count += 1
            
            self.logger.info(f"Tool integration system initialized: "
                           f"{registration_count} tools registered from {len(discovered_tools)} discovered")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tool integration system: {e}")
    
    def get_available_tools(self) -> List[ToolMetadata]:
        """Get list of all available tools."""
        return list(self.registry.tools.values())
    
    def get_tools_for_context(self, context: FileContext) -> List[ToolMetadata]:
        """Get tools that can handle the given file context."""
        compatible_tools = []
        
        for metadata in self.registry.tools.values():
            # Check file type compatibility
            if metadata.file_type_filters:
                if not any(file_type in metadata.file_type_filters for file_type in context.file_types):
                    continue
            
            # Check capability compatibility
            if context.has_subdirectories and ToolCapability.DIRECTORY_OPERATIONS not in metadata.capabilities:
                continue
            
            compatible_tools.append(metadata)
        
        return compatible_tools
    
    def launch_tool_with_context(self, tool_name: str, context: FileContext, **kwargs) -> bool:
        """Launch a tool with file context."""
        return self.launcher.launch_tool(tool_name, context, **kwargs)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'total_tools': len(self.registry.tools),
            'active_tools': len(self.launcher.get_active_tools()),
            'categories': {category.value: len(self.registry.get_tools_by_category(category)) 
                          for category in ToolCategory},
            'recent_launches': len([h for h in self.launcher.get_launch_history() 
                                  if time.time() - h['timestamp'] < 3600]),  # Last hour
            'registry_status': 'operational',
            'launcher_status': 'operational'
        }
    
    def shutdown(self) -> None:
        """Shutdown the tool integration system."""
        try:
            self.launcher.shutdown_all_tools()
            self.logger.info("Tool integration system shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during tool integration system shutdown: {e}")


# Global instance for application-wide access
_tool_integration_manager = None

def get_tool_integration_manager() -> ToolIntegrationManager:
    """Get the global tool integration manager instance."""
    global _tool_integration_manager
    if _tool_integration_manager is None:
        _tool_integration_manager = ToolIntegrationManager()
    return _tool_integration_manager