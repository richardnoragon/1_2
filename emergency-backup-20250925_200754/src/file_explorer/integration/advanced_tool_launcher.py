"""
Advanced Tool Launcher - Phase 4 Implementation
Comprehensive tool launcher with complete file context awareness

This module provides enterprise-grade tool launching capabilities with:
- Complete file context awareness and parameter passing
- Tool lifecycle management and state tracking
- Background execution with progress monitoring
- Security validation and resource management
- Cross-platform compatibility and error handling
- Performance optimization and caching strategies

Author: Enterprise Principal Engineer
Version: 1.0.0
Date: September 13, 2025
"""

import json
import logging
import os
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from weakref import WeakKeyDictionary

try:
    from PyQt5.QtCore import QObject, QTimer, pyqtSignal
    from PyQt5.QtWidgets import QApplication, QMessageBox

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QObject = object
    pyqtSignal = lambda *args: None

from .tool_integration_framework import (
    FileContext,
    ToolCapability,
    ToolInterface,
    ToolMetadata,
    ToolRegistry,
    ToolStatus,
)

try:
    from src.config_manager import ConfigManager
    from src.log_manager import get_log_manager
except ImportError:
    ConfigManager = None

    def get_log_manager():
        return logging


@dataclass
class LaunchConfiguration:
    """Configuration for tool launch operations."""

    tool_name: str
    context: FileContext
    launch_mode: str = "standard"  # standard, background, elevated
    priority: int = 5  # 1-10, higher is more important
    timeout: int = 300  # seconds
    auto_close: bool = False
    save_state: bool = True
    custom_params: Dict[str, Any] = None
    environment_vars: Dict[str, str] = None
    working_directory: Optional[Path] = None

    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}
        if self.environment_vars is None:
            self.environment_vars = {}


@dataclass
class LaunchResult:
    """Result information for tool launch operations."""

    success: bool
    tool_name: str
    launch_time: float
    duration: float
    instance: Optional[ToolInterface] = None
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = None
    resource_usage: Dict[str, Any] = None

    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.resource_usage is None:
            self.resource_usage = {}


class ToolInstanceManager:
    """Manages tool instances and their lifecycle."""

    def __init__(self):
        self.instances: WeakKeyDictionary = WeakKeyDictionary()
        self.instance_metadata: Dict[int, Dict[str, Any]] = {}
        self.logger = get_log_manager().get_logger("ToolInstanceManager")
        self._lock = threading.RLock()

    def register_instance(
        self,
        instance: ToolInterface,
        metadata: ToolMetadata,
        launch_config: LaunchConfiguration,
    ) -> int:
        """Register a tool instance."""
        with self._lock:
            instance_id = id(instance)
            self.instances[instance] = {
                "metadata": metadata,
                "launch_config": launch_config,
                "created_at": time.time(),
                "status": ToolStatus.READY,
            }

            self.instance_metadata[instance_id] = {
                "tool_name": metadata.name,
                "display_name": metadata.display_name,
                "category": metadata.category.value,
                "created_at": time.time(),
                "last_accessed": time.time(),
                "access_count": 0,
            }

            self.logger.info(
                f"Registered tool instance: {metadata.name} (ID: {instance_id})"
            )
            return instance_id

    def update_instance_status(
        self, instance: ToolInterface, status: ToolStatus
    ) -> None:
        """Update instance status."""
        with self._lock:
            if instance in self.instances:
                self.instances[instance]["status"] = status
                self.instances[instance]["last_updated"] = time.time()

                instance_id = id(instance)
                if instance_id in self.instance_metadata:
                    self.instance_metadata[instance_id][
                        "last_accessed"
                    ] = time.time()
                    self.instance_metadata[instance_id]["access_count"] += 1

    def get_instance_info(
        self, instance: ToolInterface
    ) -> Optional[Dict[str, Any]]:
        """Get information about an instance."""
        return self.instances.get(instance)

    def get_all_instances(self) -> List[Dict[str, Any]]:
        """Get information about all instances."""
        with self._lock:
            return [
                {"instance": instance, "instance_id": id(instance), **info}
                for instance, info in self.instances.items()
            ]

    def cleanup_instance(self, instance: ToolInterface) -> None:
        """Cleanup an instance."""
        with self._lock:
            try:
                if hasattr(instance, "cleanup"):
                    instance.cleanup()

                instance_id = id(instance)
                if instance in self.instances:
                    del self.instances[instance]
                if instance_id in self.instance_metadata:
                    del self.instance_metadata[instance_id]

                self.logger.info(f"Cleaned up instance ID: {instance_id}")

            except Exception as e:
                self.logger.error(f"Error during instance cleanup: {e}")


class ContextProcessor:
    """Processes and enriches file contexts for tool launching."""

    def __init__(self):
        self.logger = get_log_manager().get_logger("ContextProcessor")
        self.cache = {}
        self._cache_lock = threading.RLock()

    def process_context(
        self, context: FileContext, metadata: ToolMetadata
    ) -> FileContext:
        """Process and enrich context for specific tool."""
        try:
            # Create enhanced context copy
            enhanced_context = FileContext(
                selected_files=context.selected_files.copy(),
                current_directory=context.current_directory,
                pane_index=context.pane_index,
                selection_count=context.selection_count,
                total_size=context.total_size,
                file_types=context.file_types.copy(),
                has_subdirectories=context.has_subdirectories,
                is_readonly=context.is_readonly,
                metadata=context.metadata.copy(),
            )

            # Add tool-specific metadata
            enhanced_context.metadata["tool_capabilities"] = [
                cap.value for cap in metadata.capabilities
            ]
            enhanced_context.metadata["tool_category"] = (
                metadata.category.value
            )
            enhanced_context.metadata["supports_batch"] = (
                ToolCapability.BATCH_PROCESSING in metadata.capabilities
            )

            # Add file analysis if needed
            if ToolCapability.FILE_CONTEXT_AWARE in metadata.capabilities:
                self._analyze_file_context(enhanced_context)

            # Add security context
            enhanced_context.metadata["security_level"] = (
                metadata.security_level
            )

            return enhanced_context

        except Exception as e:
            self.logger.error(f"Context processing failed: {e}")
            return context  # Return original on error

    def _analyze_file_context(self, context: FileContext) -> None:
        """Analyze files in context for additional metadata."""
        try:
            # Analyze file patterns
            file_patterns = {}
            for file_path in context.selected_files:
                if file_path.exists() and file_path.is_file():
                    suffix = file_path.suffix.lower()
                    if suffix:
                        file_patterns[suffix] = (
                            file_patterns.get(suffix, 0) + 1
                        )

            context.metadata["file_patterns"] = file_patterns

            # Analyze directory structure
            if context.has_subdirectories:
                dir_info = self._analyze_directory_structure(
                    context.selected_files
                )
                context.metadata["directory_analysis"] = dir_info

            # Check for special files
            special_files = self._identify_special_files(
                context.selected_files
            )
            if special_files:
                context.metadata["special_files"] = special_files

        except Exception as e:
            self.logger.debug(f"File context analysis failed: {e}")

    def _analyze_directory_structure(
        self, files: List[Path]
    ) -> Dict[str, Any]:
        """Analyze directory structure."""
        dirs = [f for f in files if f.exists() and f.is_dir()]
        if not dirs:
            return {}

        return {
            "directory_count": len(dirs),
            "max_depth": max(len(d.parts) for d in dirs),
            "total_subdirs": sum(
                len(list(d.rglob("*"))) for d in dirs if d.exists()
            ),
        }

    def _identify_special_files(self, files: List[Path]) -> List[str]:
        """Identify special file types."""
        special_patterns = {
            "config": [".ini", ".conf", ".config", ".json", ".yaml", ".yml"],
            "executable": [".exe", ".bat", ".cmd", ".sh"],
            "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "database": [".db", ".sqlite", ".mdb"],
            "log": [".log", ".txt"],
        }

        special_files = []
        for file_path in files:
            if file_path.exists() and file_path.is_file():
                suffix = file_path.suffix.lower()
                for category, extensions in special_patterns.items():
                    if suffix in extensions:
                        special_files.append(f"{category}:{file_path.name}")
                        break

        return special_files


class LaunchQueue:
    """Queue system for managing tool launch requests."""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.queue: List[LaunchConfiguration] = []
        self.running: Dict[str, Future] = {}
        self.completed: List[LaunchResult] = []
        self.logger = get_log_manager().get_logger("LaunchQueue")
        self._lock = threading.RLock()

    def add_launch(self, config: LaunchConfiguration) -> None:
        """Add launch configuration to queue."""
        with self._lock:
            # Sort by priority (higher priority first)
            self.queue.append(config)
            self.queue.sort(key=lambda x: x.priority, reverse=True)
            self.logger.info(
                f"Added {config.tool_name} to launch queue (priority: {config.priority})"
            )

    def get_next_launch(self) -> Optional[LaunchConfiguration]:
        """Get next launch configuration from queue."""
        with self._lock:
            if self.queue and len(self.running) < self.max_concurrent:
                return self.queue.pop(0)
            return None

    def register_running(self, tool_name: str, future: Future) -> None:
        """Register a running launch."""
        with self._lock:
            self.running[tool_name] = future

    def complete_launch(self, result: LaunchResult) -> None:
        """Mark launch as completed."""
        with self._lock:
            if result.tool_name in self.running:
                del self.running[result.tool_name]

            self.completed.append(result)

            # Keep only last 50 completed launches
            if len(self.completed) > 50:
                self.completed = self.completed[-50:]

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        with self._lock:
            return {
                "queued": len(self.queue),
                "running": len(self.running),
                "completed": len(self.completed),
                "max_concurrent": self.max_concurrent,
                "queue_items": [
                    {
                        "tool_name": config.tool_name,
                        "priority": config.priority,
                        "mode": config.launch_mode,
                    }
                    for config in self.queue
                ],
                "running_items": list(self.running.keys()),
            }


class AdvancedToolLauncher(QObject if PYQT_AVAILABLE else object):
    """Advanced tool launcher with comprehensive features."""

    if PYQT_AVAILABLE:
        # Signals for Qt integration
        tool_launch_requested = pyqtSignal(str, dict)
        tool_launched = pyqtSignal(str, object, dict)
        tool_launch_failed = pyqtSignal(str, str, dict)
        tool_status_changed = pyqtSignal(str, str)
        launch_progress = pyqtSignal(str, int, str)

    def __init__(self, registry: ToolRegistry):
        if PYQT_AVAILABLE:
            super().__init__()

        self.registry = registry
        self.logger = get_log_manager().get_logger("AdvancedToolLauncher")

        # Core components
        self.instance_manager = ToolInstanceManager()
        self.context_processor = ContextProcessor()
        self.launch_queue = LaunchQueue()

        # Threading
        self.thread_pool = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="ToolLauncher"
        )

        # Configuration
        self.config = self._load_configuration()

        # State tracking
        self.launch_history: List[LaunchResult] = []
        self.performance_metrics: Dict[str, List[float]] = {}

        # Start queue processor
        self._start_queue_processor()

    def _load_configuration(self) -> Dict[str, Any]:
        """Load launcher configuration."""
        default_config = {
            "max_concurrent_launches": 3,
            "default_timeout": 300,
            "enable_performance_monitoring": True,
            "enable_background_launching": True,
            "auto_cleanup_instances": True,
            "save_launch_history": True,
            "cache_contexts": True,
        }

        if ConfigManager:
            try:
                config_manager = ConfigManager()
                user_config = config_manager.get_setting(
                    "tool_launcher", "configuration", {}
                )
                return {**default_config, **user_config}
            except Exception as e:
                self.logger.warning(f"Failed to load configuration: {e}")

        return default_config

    def launch_tool(
        self, tool_name: str, context: FileContext, **kwargs
    ) -> bool:
        """Launch tool with comprehensive configuration."""
        try:
            # Create launch configuration
            launch_config = LaunchConfiguration(
                tool_name=tool_name,
                context=context,
                launch_mode=kwargs.get("launch_mode", "standard"),
                priority=kwargs.get("priority", 5),
                timeout=kwargs.get("timeout", self.config["default_timeout"]),
                auto_close=kwargs.get("auto_close", False),
                save_state=kwargs.get("save_state", True),
                custom_params=kwargs.get("custom_params", {}),
                environment_vars=kwargs.get("environment_vars", {}),
                working_directory=kwargs.get("working_directory"),
            )

            # Validate launch request
            if not self._validate_launch_request(launch_config):
                return False

            # Add to queue
            self.launch_queue.add_launch(launch_config)

            # Emit signal if Qt available
            if PYQT_AVAILABLE:
                self.tool_launch_requested.emit(
                    tool_name, asdict(launch_config)
                )

            self.logger.info(f"Tool launch queued: {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to queue tool launch {tool_name}: {e}")
            return False

    def _validate_launch_request(self, config: LaunchConfiguration) -> bool:
        """Validate launch request."""
        try:
            # Check if tool exists
            metadata = self.registry.get_tool_metadata(config.tool_name)
            if not metadata:
                self.logger.error(f"Tool not found: {config.tool_name}")
                return False

            # Check tool status
            status = self.registry.get_tool_status(config.tool_name)
            if status == ToolStatus.ERROR:
                self.logger.error(f"Tool in error state: {config.tool_name}")
                return False

            # Validate context
            if (
                not config.context.selected_files
                and not config.context.current_directory
            ):
                self.logger.warning(
                    f"Empty context for tool: {config.tool_name}"
                )

            # Check resource limits
            if not self._check_resource_limits(metadata):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Launch validation failed: {e}")
            return False

    def _check_resource_limits(self, metadata: ToolMetadata) -> bool:
        """Check if tool launch would exceed resource limits."""
        try:
            # Check concurrent launches
            queue_status = self.launch_queue.get_queue_status()
            if (
                queue_status["running"]
                >= self.config["max_concurrent_launches"]
            ):
                self.logger.warning("Maximum concurrent launches reached")
                return False

            # Check memory requirements
            required_memory = metadata.resource_requirements.get(
                "memory_mb", 0
            )
            if required_memory > 2048:  # 2GB limit
                self.logger.warning(
                    f"Tool requires too much memory: {required_memory}MB"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"Resource limit check failed: {e}")
            return False

    def _start_queue_processor(self) -> None:
        """Start the queue processor."""
        if PYQT_AVAILABLE:
            self.queue_timer = QTimer()
            self.queue_timer.timeout.connect(self._process_queue)
            self.queue_timer.start(1000)  # Process every second
        else:
            # Use threading for non-Qt environments
            def queue_processor():
                while True:
                    self._process_queue()
                    time.sleep(1)

            queue_thread = threading.Thread(
                target=queue_processor, daemon=True, name="QueueProcessor"
            )
            queue_thread.start()

    def _process_queue(self) -> None:
        """Process the launch queue."""
        try:
            config = self.launch_queue.get_next_launch()
            if config:
                # Submit to thread pool
                future = self.thread_pool.submit(self._execute_launch, config)
                self.launch_queue.register_running(config.tool_name, future)

        except Exception as e:
            self.logger.error(f"Queue processing error: {e}")

    def _execute_launch(self, config: LaunchConfiguration) -> LaunchResult:
        """Execute tool launch in background thread."""
        start_time = time.time()
        result = LaunchResult(
            success=False,
            tool_name=config.tool_name,
            launch_time=start_time,
            duration=0.0,
        )

        try:
            # Get tool metadata
            metadata = self.registry.get_tool_metadata(config.tool_name)
            if not metadata:
                raise ValueError(
                    f"Tool metadata not found: {config.tool_name}"
                )

            # Update status
            self.registry.update_tool_status(
                config.tool_name, ToolStatus.LOADING
            )
            if PYQT_AVAILABLE:
                self.tool_status_changed.emit(
                    config.tool_name, ToolStatus.LOADING.value
                )

            # Process context
            enhanced_context = self.context_processor.process_context(
                config.context, metadata
            )

            # Load tool instance
            tool_instance = self._load_tool_instance(metadata, config)
            if not tool_instance:
                raise RuntimeError(
                    f"Failed to load tool instance: {config.tool_name}"
                )

            # Initialize tool
            self.registry.update_tool_status(
                config.tool_name, ToolStatus.INITIALIZING
            )
            if PYQT_AVAILABLE:
                self.tool_status_changed.emit(
                    config.tool_name, ToolStatus.INITIALIZING.value
                )

            if not tool_instance.initialize(enhanced_context):
                raise RuntimeError(
                    f"Tool initialization failed: {config.tool_name}"
                )

            # Register instance
            instance_id = self.instance_manager.register_instance(
                tool_instance, metadata, config
            )

            # Execute tool
            self.registry.update_tool_status(
                config.tool_name, ToolStatus.RUNNING
            )
            if PYQT_AVAILABLE:
                self.tool_status_changed.emit(
                    config.tool_name, ToolStatus.RUNNING.value
                )

            self._execute_tool_instance(tool_instance, config)

            # Success
            result.success = True
            result.instance = tool_instance
            result.duration = time.time() - start_time

            # Collect performance metrics
            result.performance_metrics = self._collect_performance_metrics(
                config.tool_name, result.duration
            )

            # Emit success signal
            if PYQT_AVAILABLE:
                self.tool_launched.emit(
                    config.tool_name, tool_instance, asdict(result)
                )

            self.logger.info(f"Tool launched successfully: {config.tool_name}")

        except Exception as e:
            result.error_message = str(e)
            self.registry.update_tool_status(
                config.tool_name, ToolStatus.ERROR
            )

            if PYQT_AVAILABLE:
                self.tool_launch_failed.emit(
                    config.tool_name, str(e), asdict(result)
                )

            self.logger.error(f"Tool launch failed: {config.tool_name} - {e}")

        finally:
            result.duration = time.time() - start_time

            # Record metrics
            self.registry.record_tool_usage(
                config.tool_name, result.success, result.duration
            )

            # Add to history
            self.launch_history.append(result)
            if len(self.launch_history) > 100:
                self.launch_history = self.launch_history[-100:]

            # Mark as completed in queue
            self.launch_queue.complete_launch(result)

        return result

    def _load_tool_instance(
        self, metadata: ToolMetadata, config: LaunchConfiguration
    ) -> Optional[ToolInterface]:
        """Load tool instance with configuration."""
        try:
            # Set up environment
            if config.environment_vars:
                for key, value in config.environment_vars.items():
                    os.environ[key] = value

            # Set working directory
            if config.working_directory and config.working_directory.exists():
                os.chdir(str(config.working_directory))

            # Import and instantiate
            import importlib

            module = importlib.import_module(metadata.module_path)
            tool_class = getattr(module, metadata.class_name)

            # Create instance with custom parameters
            if config.custom_params:
                tool_instance = tool_class(**config.custom_params)
            else:
                tool_instance = tool_class()

            return tool_instance

        except Exception as e:
            self.logger.error(
                f"Failed to load tool instance {metadata.name}: {e}"
            )
            return None

    def _execute_tool_instance(
        self, instance: ToolInterface, config: LaunchConfiguration
    ) -> None:
        """Execute the tool instance."""
        try:
            if hasattr(instance, "show") and callable(instance.show):
                # GUI tool
                if PYQT_AVAILABLE and QApplication.instance():
                    # Schedule on main thread
                    QApplication.instance().postEvent(
                        QApplication.instance(), lambda: instance.show()
                    )
                else:
                    instance.show()

            elif hasattr(instance, "execute") and callable(instance.execute):
                # Command-line tool
                instance.execute(**config.custom_params)

            else:
                self.logger.warning(
                    f"Tool has no execution method: {config.tool_name}"
                )

        except Exception as e:
            self.logger.error(
                f"Tool execution failed: {config.tool_name} - {e}"
            )
            raise

    def _collect_performance_metrics(
        self, tool_name: str, duration: float
    ) -> Dict[str, Any]:
        """Collect performance metrics for launch."""
        try:
            metrics = {"launch_duration": duration, "timestamp": time.time()}

            # Add system metrics if available
            try:
                import psutil

                metrics.update(
                    {
                        "memory_usage_mb": psutil.virtual_memory().used
                        / 1024
                        / 1024,
                        "cpu_percent": psutil.cpu_percent(),
                        "disk_usage_percent": psutil.disk_usage("/").percent,
                    }
                )
            except ImportError:
                pass

            # Track tool-specific metrics
            if tool_name not in self.performance_metrics:
                self.performance_metrics[tool_name] = []

            self.performance_metrics[tool_name].append(duration)
            if len(self.performance_metrics[tool_name]) > 20:
                self.performance_metrics[tool_name] = self.performance_metrics[
                    tool_name
                ][-20:]

            return metrics

        except Exception as e:
            self.logger.error(f"Performance metrics collection failed: {e}")
            return {}

    def get_launch_statistics(self) -> Dict[str, Any]:
        """Get comprehensive launch statistics."""
        try:
            successful_launches = [r for r in self.launch_history if r.success]
            failed_launches = [r for r in self.launch_history if not r.success]

            stats = {
                "total_launches": len(self.launch_history),
                "successful_launches": len(successful_launches),
                "failed_launches": len(failed_launches),
                "success_rate": (
                    len(successful_launches) / len(self.launch_history) * 100
                    if self.launch_history
                    else 0
                ),
                "average_launch_time": (
                    sum(r.duration for r in successful_launches)
                    / len(successful_launches)
                    if successful_launches
                    else 0
                ),
                "queue_status": self.launch_queue.get_queue_status(),
                "active_instances": len(
                    self.instance_manager.get_all_instances()
                ),
            }

            # Tool-specific statistics
            tool_stats = {}
            for result in self.launch_history:
                tool_name = result.tool_name
                if tool_name not in tool_stats:
                    tool_stats[tool_name] = {
                        "launches": 0,
                        "successes": 0,
                        "failures": 0,
                        "avg_duration": 0.0,
                    }

                tool_stats[tool_name]["launches"] += 1
                if result.success:
                    tool_stats[tool_name]["successes"] += 1
                else:
                    tool_stats[tool_name]["failures"] += 1

            # Calculate averages
            for tool_name, tool_data in tool_stats.items():
                if tool_name in self.performance_metrics:
                    durations = self.performance_metrics[tool_name]
                    tool_data["avg_duration"] = sum(durations) / len(durations)

            stats["tool_statistics"] = tool_stats

            return stats

        except Exception as e:
            self.logger.error(f"Failed to generate launch statistics: {e}")
            return {}

    def shutdown(self) -> None:
        """Shutdown the launcher system."""
        try:
            # Stop queue processor
            if PYQT_AVAILABLE and hasattr(self, "queue_timer"):
                self.queue_timer.stop()

            # Cleanup all instances
            for instance_info in self.instance_manager.get_all_instances():
                self.instance_manager.cleanup_instance(
                    instance_info["instance"]
                )

            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)

            self.logger.info("Advanced tool launcher shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during launcher shutdown: {e}")


def create_advanced_tool_launcher(
    registry: ToolRegistry,
) -> AdvancedToolLauncher:
    """Factory function to create advanced tool launcher."""
    return AdvancedToolLauncher(registry)
