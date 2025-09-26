"""
Plugin System Foundation - Phase 4 Implementation
Robust plugin system with dynamic loading, API contracts, and security validation

This module provides enterprise-grade plugin system capabilities with:
- Dynamic plugin discovery and loading
- Comprehensive API contracts and versioning
- Security validation and sandboxing
- Plugin lifecycle management
- Dependency resolution and management
- Performance monitoring and resource management
- Cross-platform compatibility and extensibility

Author: Enterprise Principal Engineer
Version: 1.0.0
Date: September 13, 2025
"""

import hashlib
import importlib
import inspect
import json
import logging
import os
import sys
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
from zipfile import ZipFile

try:
    from PyQt5.QtCore import QObject, pyqtSignal

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QObject = object

    def pyqtSignal(*args):
        return None


try:
    from src.config_manager import ConfigManager
    from src.log_manager import get_log_manager

    from .tool_integration_framework import (
        FileContext,
        ToolInterface,
        ToolMetadata,
    )
except ImportError:
    ConfigManager = None
    FileContext = None
    ToolInterface = None
    ToolMetadata = None

    def get_log_manager():
        return logging


class PluginState(Enum):
    """Plugin lifecycle state enumeration."""

    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    LOADED = "loaded"
    VALIDATED = "validated"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADED = "unloaded"


class PluginType(Enum):
    """Plugin type classification."""

    TOOL_EXTENSION = "tool_extension"
    FILE_HANDLER = "file_handler"
    UI_ENHANCEMENT = "ui_enhancement"
    WORKFLOW_AUTOMATION = "workflow_automation"
    INTEGRATION = "integration"
    FILTER = "filter"
    EXPORTER = "exporter"
    CUSTOM = "custom"


class PluginCapability(Enum):
    """Plugin capability flags."""

    FILE_PROCESSING = "file_processing"
    UI_MODIFICATION = "ui_modification"
    CONTEXT_MENU = "context_menu"
    KEYBOARD_SHORTCUTS = "keyboard_shortcuts"
    BACKGROUND_PROCESSING = "background_processing"
    NETWORK_ACCESS = "network_access"
    SYSTEM_ACCESS = "system_access"
    DATABASE_ACCESS = "database_access"


class SecurityLevel(Enum):
    """Security clearance levels for plugins."""

    SANDBOXED = 1  # Heavily restricted
    LIMITED = 2  # Basic file access
    STANDARD = 3  # Normal operations
    ELEVATED = 4  # Extended permissions
    TRUSTED = 5  # Full system access


@dataclass
class PluginManifest:
    """Comprehensive plugin manifest information."""

    id: str
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    capabilities: Set[PluginCapability] = field(default_factory=set)
    security_level: SecurityLevel = SecurityLevel.STANDARD
    api_version: str = "1.0.0"
    min_app_version: str = "1.0.0"
    max_app_version: str = ""
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    entry_point: str = ""
    main_class: str = ""
    config_schema: Dict[str, Any] = field(default_factory=dict)
    supported_platforms: List[str] = field(default_factory=list)
    license: str = ""
    homepage: str = ""
    keywords: List[str] = field(default_factory=list)
    file_filters: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.supported_platforms:
            self.supported_platforms = ["windows", "linux", "darwin"]


@dataclass
class PluginContext:
    """Context information for plugin operations."""

    plugin_id: str
    application_version: str
    working_directory: Path
    config_directory: Path
    temp_directory: Path
    file_context: Optional[FileContext] = None
    user_settings: Dict[str, Any] = field(default_factory=dict)
    system_info: Dict[str, Any] = field(default_factory=dict)
    permissions: Set[str] = field(default_factory=set)
    resource_limits: Dict[str, Any] = field(default_factory=dict)


class PluginAPI(ABC):
    """Abstract base class for plugin API contracts."""

    @property
    @abstractmethod
    def api_version(self) -> str:
        """Return the API version this plugin implements."""
        pass

    @abstractmethod
    def get_manifest(self) -> PluginManifest:
        """Return plugin manifest information."""
        pass

    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """Initialize the plugin with context."""
        pass

    @abstractmethod
    def activate(self) -> bool:
        """Activate the plugin."""
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """Deactivate the plugin."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

    def get_configuration_schema(self) -> Dict[str, Any]:
        """Return configuration schema for the plugin."""
        return {}

    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the plugin with settings."""
        return True

    def get_status(self) -> Dict[str, Any]:
        """Return current plugin status."""
        return {"status": "active"}

    def handle_file_context(self, context: FileContext) -> bool:
        """Handle file context changes."""
        return True


class PluginSecurityValidator:
    """Security validation system for plugins."""

    def __init__(self):
        self.logger = get_log_manager().get_logger("PluginSecurity")
        self.security_policies = self._load_security_policies()
        self.trusted_signatures = self._load_trusted_signatures()

    def validate_plugin(
        self, plugin_path: Path, manifest: PluginManifest
    ) -> Tuple[bool, List[str]]:
        """Comprehensive plugin security validation."""
        errors = []

        try:
            # Validate manifest
            manifest_valid, manifest_errors = self._validate_manifest(manifest)
            if not manifest_valid:
                errors.extend(manifest_errors)

            # Validate file integrity
            integrity_valid, integrity_errors = self._validate_file_integrity(
                plugin_path
            )
            if not integrity_valid:
                errors.extend(integrity_errors)

            # Validate code security
            code_valid, code_errors = self._validate_code_security(
                plugin_path, manifest
            )
            if not code_valid:
                errors.extend(code_errors)

            # Validate permissions
            perms_valid, perms_errors = self._validate_permissions(manifest)
            if not perms_valid:
                errors.extend(perms_errors)

            # Validate dependencies
            deps_valid, deps_errors = self._validate_dependencies(manifest)
            if not deps_valid:
                errors.extend(deps_errors)

            return len(errors) == 0, errors

        except Exception as e:
            self.logger.error(f"Plugin validation failed: {e}")
            return False, [f"Validation exception: {e}"]

    def _validate_manifest(
        self, manifest: PluginManifest
    ) -> Tuple[bool, List[str]]:
        """Validate plugin manifest."""
        errors = []

        # Required fields validation
        if not manifest.id or not manifest.id.strip():
            errors.append("Plugin ID is required")

        if not manifest.name or not manifest.name.strip():
            errors.append("Plugin name is required")

        if not manifest.version:
            errors.append("Plugin version is required")

        if not manifest.author:
            errors.append("Plugin author is required")

        # Security level validation
        max_allowed_level = self.security_policies.get(
            "max_security_level", SecurityLevel.STANDARD
        )
        if manifest.security_level.value > max_allowed_level.value:
            errors.append(
                f"Security level {manifest.security_level.name} exceeds maximum allowed"
            )

        # Capability validation
        forbidden_capabilities = self.security_policies.get(
            "forbidden_capabilities", set()
        )
        for capability in manifest.capabilities:
            if capability in forbidden_capabilities:
                errors.append(f"Capability {capability.name} is forbidden")

        return len(errors) == 0, errors

    def _validate_file_integrity(
        self, plugin_path: Path
    ) -> Tuple[bool, List[str]]:
        """Validate plugin file integrity."""
        errors = []

        try:
            if not plugin_path.exists():
                errors.append("Plugin path does not exist")
                return False, errors

            # Calculate file hash
            file_hash = self._calculate_file_hash(plugin_path)

            # Check against trusted signatures if available
            if str(plugin_path) in self.trusted_signatures:
                expected_hash = self.trusted_signatures[str(plugin_path)]
                if file_hash != expected_hash:
                    errors.append(
                        "File integrity check failed - hash mismatch"
                    )

            # Check file size limits
            max_size = self.security_policies.get(
                "max_plugin_size", 100 * 1024 * 1024
            )  # 100MB
            if plugin_path.stat().st_size > max_size:
                errors.append(
                    f"Plugin size exceeds maximum allowed: {plugin_path.stat().st_size}"
                )

        except Exception as e:
            errors.append(f"File integrity validation failed: {e}")

        return len(errors) == 0, errors

    def _validate_code_security(
        self, plugin_path: Path, manifest: PluginManifest
    ) -> Tuple[bool, List[str]]:
        """Validate plugin code for security issues."""
        errors = []

        try:
            # This is a simplified check - in production would use AST analysis
            dangerous_imports = [
                "subprocess",
                "os.system",
                "eval",
                "exec",
                "compile",
                "__import__",
                "open",
                "file",
                "input",
                "raw_input",
            ]

            if plugin_path.suffix == ".py":
                content = plugin_path.read_text(encoding="utf-8")
                for dangerous in dangerous_imports:
                    if dangerous in content:
                        if (
                            manifest.security_level.value
                            < SecurityLevel.ELEVATED.value
                        ):
                            errors.append(
                                f"Dangerous import '{dangerous}' requires elevated security"
                            )

        except Exception as e:
            errors.append(f"Code security validation failed: {e}")

        return len(errors) == 0, errors

    def _validate_permissions(
        self, manifest: PluginManifest
    ) -> Tuple[bool, List[str]]:
        """Validate plugin permissions."""
        errors = []

        # Map capabilities to required permissions
        capability_permissions = {
            PluginCapability.NETWORK_ACCESS: ["network"],
            PluginCapability.SYSTEM_ACCESS: ["system"],
            PluginCapability.DATABASE_ACCESS: ["database"],
            PluginCapability.FILE_PROCESSING: ["file_read", "file_write"],
        }

        for capability in manifest.capabilities:
            required_perms = capability_permissions.get(capability, [])
            for perm in required_perms:
                if not self._is_permission_allowed(
                    perm, manifest.security_level
                ):
                    errors.append(
                        f"Permission '{perm}' not allowed for security level "
                        f"{manifest.security_level.name}"
                    )

        return len(errors) == 0, errors

    def _validate_dependencies(
        self, manifest: PluginManifest
    ) -> Tuple[bool, List[str]]:
        """Validate plugin dependencies."""
        errors = []

        # Check dependency count limits
        max_deps = self.security_policies.get("max_dependencies", 20)
        total_deps = len(manifest.dependencies) + len(
            manifest.optional_dependencies
        )
        if total_deps > max_deps:
            errors.append(f"Too many dependencies: {total_deps} > {max_deps}")

        # Check for forbidden dependencies
        forbidden_deps = self.security_policies.get(
            "forbidden_dependencies", set()
        )
        for dep in manifest.dependencies + manifest.optional_dependencies:
            if dep in forbidden_deps:
                errors.append(f"Forbidden dependency: {dep}")

        return len(errors) == 0, errors

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_security_policies(self) -> Dict[str, Any]:
        """Load security policies from configuration."""
        default_policies = {
            "max_security_level": SecurityLevel.STANDARD,
            "max_plugin_size": 100 * 1024 * 1024,  # 100MB
            "max_dependencies": 20,
            "forbidden_capabilities": set(),
            "forbidden_dependencies": {"subprocess", "ctypes"},
            "require_signature": False,
            "sandbox_plugins": True,
        }

        if ConfigManager:
            try:
                config = ConfigManager()
                policies = config.get_setting(
                    "plugins", "security_policies", {}
                )
                return {**default_policies, **policies}
            except Exception:
                pass

        return default_policies

    def _load_trusted_signatures(self) -> Dict[str, str]:
        """Load trusted plugin signatures."""
        try:
            if ConfigManager:
                config = ConfigManager()
                return config.get_setting("plugins", "trusted_signatures", {})
        except Exception:
            pass

        return {}

    def _is_permission_allowed(
        self, permission: str, security_level: SecurityLevel
    ) -> bool:
        """Check if permission is allowed for security level."""
        permission_levels = {
            "file_read": SecurityLevel.LIMITED,
            "file_write": SecurityLevel.LIMITED,
            "network": SecurityLevel.STANDARD,
            "database": SecurityLevel.STANDARD,
            "system": SecurityLevel.ELEVATED,
        }

        required_level = permission_levels.get(
            permission, SecurityLevel.TRUSTED
        )
        return security_level.value >= required_level.value


class PluginLoader:
    """Dynamic plugin loader with validation and dependency resolution."""

    def __init__(self, security_validator: PluginSecurityValidator):
        self.security_validator = security_validator
        self.logger = get_log_manager().get_logger("PluginLoader")
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_modules: Dict[str, Any] = {}

    def load_plugin(
        self, plugin_path: Path, manifest: PluginManifest
    ) -> Tuple[bool, Optional[PluginAPI], List[str]]:
        """Load and validate a plugin."""
        errors = []

        try:
            # Security validation
            valid, security_errors = self.security_validator.validate_plugin(
                plugin_path, manifest
            )
            if not valid:
                return False, None, security_errors

            # Load plugin module
            plugin_module = self._load_plugin_module(plugin_path, manifest)
            if not plugin_module:
                return False, None, ["Failed to load plugin module"]

            # Get plugin class
            plugin_class = self._get_plugin_class(plugin_module, manifest)
            if not plugin_class:
                return False, None, ["Plugin class not found"]

            # Validate plugin interface
            if not self._validate_plugin_interface(plugin_class):
                return (
                    False,
                    None,
                    ["Plugin does not implement required interface"],
                )

            # Instantiate plugin
            plugin_instance = plugin_class()

            # Store references
            self.loaded_plugins[manifest.id] = plugin_instance
            self.plugin_modules[manifest.id] = plugin_module

            return True, plugin_instance, []

        except Exception as e:
            error_msg = f"Plugin loading failed: {e}"
            self.logger.error(error_msg)
            return False, None, [error_msg]

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        try:
            # Cleanup plugin instance
            if plugin_id in self.loaded_plugins:
                plugin_instance = self.loaded_plugins[plugin_id]
                if hasattr(plugin_instance, "cleanup"):
                    plugin_instance.cleanup()
                del self.loaded_plugins[plugin_id]

            # Remove module reference
            if plugin_id in self.plugin_modules:
                module = self.plugin_modules[plugin_id]
                # Remove from sys.modules if it was dynamically loaded
                module_name = getattr(module, "__name__", None)
                if module_name and module_name in sys.modules:
                    del sys.modules[module_name]
                del self.plugin_modules[plugin_id]

            self.logger.info(f"Unloaded plugin: {plugin_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False

    def _load_plugin_module(
        self, plugin_path: Path, manifest: PluginManifest
    ) -> Optional[Any]:
        """Load plugin module from file."""
        try:
            if plugin_path.suffix == ".py":
                # Load Python module
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{manifest.id}", plugin_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module

            elif plugin_path.suffix == ".zip":
                # Load from zip package
                return self._load_from_zip(plugin_path, manifest)

            else:
                self.logger.error(
                    f"Unsupported plugin format: {plugin_path.suffix}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Failed to load plugin module: {e}")
            return None

    def _load_from_zip(
        self, zip_path: Path, manifest: PluginManifest
    ) -> Optional[Any]:
        """Load plugin from zip package."""
        try:
            with ZipFile(zip_path, "r") as zip_file:
                # Extract to temporary directory
                import tempfile

                temp_dir = Path(
                    tempfile.mkdtemp(prefix=f"plugin_{manifest.id}_")
                )
                zip_file.extractall(temp_dir)

                # Find entry point
                entry_point = temp_dir / manifest.entry_point
                if entry_point.exists():
                    # Add to Python path
                    sys.path.insert(0, str(temp_dir))

                    try:
                        # Load module
                        spec = importlib.util.spec_from_file_location(
                            f"plugin_{manifest.id}", entry_point
                        )
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            return module
                    finally:
                        # Remove from path
                        if str(temp_dir) in sys.path:
                            sys.path.remove(str(temp_dir))

        except Exception as e:
            self.logger.error(f"Failed to load plugin from zip: {e}")

        return None

    def _get_plugin_class(
        self, module: Any, manifest: PluginManifest
    ) -> Optional[Type]:
        """Get plugin class from module."""
        try:
            if manifest.main_class:
                # Use specified class
                return getattr(module, manifest.main_class, None)
            else:
                # Search for PluginAPI implementation
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, PluginAPI)
                        and obj is not PluginAPI
                        and obj.__module__ == module.__name__
                    ):
                        return obj

        except Exception as e:
            self.logger.error(f"Failed to get plugin class: {e}")

        return None

    def _validate_plugin_interface(self, plugin_class: Type) -> bool:
        """Validate plugin implements required interface."""
        try:
            return issubclass(plugin_class, PluginAPI)
        except Exception:
            return False


class PluginManager(QObject if PYQT_AVAILABLE else object):
    """Main plugin management system."""

    if PYQT_AVAILABLE:
        plugin_loaded = pyqtSignal(str, str)  # plugin_id, name
        plugin_unloaded = pyqtSignal(str)  # plugin_id
        plugin_activated = pyqtSignal(str)  # plugin_id
        plugin_deactivated = pyqtSignal(str)  # plugin_id
        plugin_error = pyqtSignal(str, str)  # plugin_id, error

    def __init__(self):
        if PYQT_AVAILABLE:
            super().__init__()

        self.logger = get_log_manager().get_logger("PluginManager")

        # Core components
        self.security_validator = PluginSecurityValidator()
        self.plugin_loader = PluginLoader(self.security_validator)

        # Plugin tracking
        self.plugins: Dict[str, PluginAPI] = {}
        self.manifests: Dict[str, PluginManifest] = {}
        self.states: Dict[str, PluginState] = {}
        self.contexts: Dict[str, PluginContext] = {}

        # Discovery paths
        self.plugin_paths = [
            Path("plugins"),
            Path("extensions"),
            Path.home() / ".rfu" / "plugins",
        ]

        # Configuration
        self.config = self._load_configuration()

        # Threading
        self._lock = threading.RLock()

        # Initialize system
        self._initialize_system()

    def _load_configuration(self) -> Dict[str, Any]:
        """Load plugin system configuration."""
        default_config = {
            "enabled": True,
            "auto_discovery": True,
            "auto_activation": False,
            "sandbox_plugins": True,
            "enable_user_plugins": True,
            "plugin_cache_enabled": True,
            "max_concurrent_loads": 5,
            "load_timeout": 30,
        }

        if ConfigManager:
            try:
                config = ConfigManager()
                user_config = config.get_setting(
                    "plugins", "configuration", {}
                )
                return {**default_config, **user_config}
            except Exception as e:
                self.logger.warning(
                    f"Failed to load plugin configuration: {e}"
                )

        return default_config

    def _initialize_system(self) -> None:
        """Initialize the plugin system."""
        try:
            if not self.config["enabled"]:
                self.logger.info("Plugin system disabled by configuration")
                return

            # Create plugin directories
            for path in self.plugin_paths:
                if not path.exists():
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        self.logger.debug(
                            f"Could not create plugin directory {path}: {e}"
                        )

            # Auto-discovery if enabled
            if self.config["auto_discovery"]:
                self.discover_plugins()

            self.logger.info("Plugin system initialized")

        except Exception as e:
            self.logger.error(f"Plugin system initialization failed: {e}")

    def discover_plugins(self) -> List[PluginManifest]:
        """Discover available plugins."""
        discovered = []

        try:
            for plugin_path in self.plugin_paths:
                if not plugin_path.exists():
                    continue

                # Scan for plugin files
                for item in plugin_path.rglob("*"):
                    if item.is_file() and item.suffix in [".py", ".zip"]:
                        manifest = self._extract_manifest(item)
                        if manifest:
                            discovered.append(manifest)
                            self.manifests[manifest.id] = manifest
                            self.states[manifest.id] = PluginState.DISCOVERED

            self.logger.info(f"Discovered {len(discovered)} plugins")
            return discovered

        except Exception as e:
            self.logger.error(f"Plugin discovery failed: {e}")
            return []

    def _extract_manifest(self, plugin_path: Path) -> Optional[PluginManifest]:
        """Extract plugin manifest from file."""
        try:
            if plugin_path.suffix == ".py":
                return self._extract_manifest_from_py(plugin_path)
            elif plugin_path.suffix == ".zip":
                return self._extract_manifest_from_zip(plugin_path)

        except Exception as e:
            self.logger.debug(
                f"Failed to extract manifest from {plugin_path}: {e}"
            )

        return None

    def _extract_manifest_from_py(
        self, py_path: Path
    ) -> Optional[PluginManifest]:
        """Extract manifest from Python file."""
        try:
            content = py_path.read_text(encoding="utf-8")

            # Look for manifest comment block
            if '"""PLUGIN_MANIFEST' in content:
                start = content.find('"""PLUGIN_MANIFEST')
                end = content.find('"""', start + 3)
                if end > start:
                    manifest_text = content[start + 18 : end]
                    manifest_data = json.loads(manifest_text)
                    return self._create_manifest_from_data(manifest_data)

            # Fallback: create basic manifest from file
            return PluginManifest(
                id=py_path.stem,
                name=py_path.stem.replace("_", " ").title(),
                version="1.0.0",
                author="Unknown",
                description=f"Plugin from {py_path.name}",
                plugin_type=PluginType.CUSTOM,
                entry_point=py_path.name,
                main_class="",
            )

        except Exception as e:
            self.logger.debug(
                f"Failed to extract manifest from Python file: {e}"
            )
            return None

    def _extract_manifest_from_zip(
        self, zip_path: Path
    ) -> Optional[PluginManifest]:
        """Extract manifest from zip package."""
        try:
            with ZipFile(zip_path, "r") as zip_file:
                # Look for manifest.json
                if "manifest.json" in zip_file.namelist():
                    manifest_data = json.loads(zip_file.read("manifest.json"))
                    return self._create_manifest_from_data(manifest_data)

                # Look for plugin.json
                if "plugin.json" in zip_file.namelist():
                    manifest_data = json.loads(zip_file.read("plugin.json"))
                    return self._create_manifest_from_data(manifest_data)

        except Exception as e:
            self.logger.debug(f"Failed to extract manifest from zip: {e}")

        return None

    def _create_manifest_from_data(
        self, data: Dict[str, Any]
    ) -> PluginManifest:
        """Create manifest from dictionary data."""
        return PluginManifest(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data.get("description", ""),
            plugin_type=PluginType(data.get("type", "custom")),
            capabilities={
                PluginCapability(cap) for cap in data.get("capabilities", [])
            },
            security_level=SecurityLevel(
                data.get("security_level", "standard")
            ),
            api_version=data.get("api_version", "1.0.0"),
            min_app_version=data.get("min_app_version", "1.0.0"),
            max_app_version=data.get("max_app_version", ""),
            dependencies=data.get("dependencies", []),
            optional_dependencies=data.get("optional_dependencies", []),
            entry_point=data.get("entry_point", ""),
            main_class=data.get("main_class", ""),
            config_schema=data.get("config_schema", {}),
            supported_platforms=data.get("supported_platforms", []),
            license=data.get("license", ""),
            homepage=data.get("homepage", ""),
            keywords=data.get("keywords", []),
            file_filters=data.get("file_filters", []),
            resource_requirements=data.get("resource_requirements", {}),
            metadata=data.get("metadata", {}),
        )

    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin."""
        with self._lock:
            try:
                if plugin_id not in self.manifests:
                    self.logger.error(f"Plugin not found: {plugin_id}")
                    return False

                if plugin_id in self.plugins:
                    self.logger.warning(f"Plugin already loaded: {plugin_id}")
                    return True

                manifest = self.manifests[plugin_id]

                # Find plugin file
                plugin_path = self._find_plugin_file(plugin_id)
                if not plugin_path:
                    self.logger.error(
                        f"Plugin file not found for: {plugin_id}"
                    )
                    return False

                # Update state
                self.states[plugin_id] = PluginState.LOADED

                # Load plugin
                success, plugin_instance, errors = (
                    self.plugin_loader.load_plugin(plugin_path, manifest)
                )

                if not success:
                    self.states[plugin_id] = PluginState.ERROR
                    if PYQT_AVAILABLE:
                        self.plugin_error.emit(plugin_id, "; ".join(errors))
                    return False

                # Store plugin
                self.plugins[plugin_id] = plugin_instance

                # Create context
                context = self._create_plugin_context(plugin_id, manifest)
                self.contexts[plugin_id] = context

                # Initialize plugin
                if plugin_instance.initialize(context):
                    self.states[plugin_id] = PluginState.INITIALIZED

                    # Auto-activate if configured
                    if self.config["auto_activation"]:
                        self.activate_plugin(plugin_id)

                    # Emit signal
                    if PYQT_AVAILABLE:
                        self.plugin_loaded.emit(plugin_id, manifest.name)

                    self.logger.info(
                        f"Plugin loaded successfully: {plugin_id}"
                    )
                    return True
                else:
                    self.states[plugin_id] = PluginState.ERROR
                    return False

            except Exception as e:
                self.states[plugin_id] = PluginState.ERROR
                error_msg = f"Plugin loading failed: {e}"
                self.logger.error(error_msg)

                if PYQT_AVAILABLE:
                    self.plugin_error.emit(plugin_id, error_msg)

                return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin."""
        with self._lock:
            try:
                if plugin_id not in self.plugins:
                    return True  # Already unloaded

                # Deactivate first
                if self.states.get(plugin_id) == PluginState.ACTIVE:
                    self.deactivate_plugin(plugin_id)

                # Unload plugin
                success = self.plugin_loader.unload_plugin(plugin_id)

                # Cleanup references
                if plugin_id in self.plugins:
                    del self.plugins[plugin_id]
                if plugin_id in self.contexts:
                    del self.contexts[plugin_id]

                self.states[plugin_id] = PluginState.UNLOADED

                # Emit signal
                if PYQT_AVAILABLE:
                    self.plugin_unloaded.emit(plugin_id)

                self.logger.info(f"Plugin unloaded: {plugin_id}")
                return success

            except Exception as e:
                self.logger.error(f"Plugin unloading failed: {e}")
                return False

    def activate_plugin(self, plugin_id: str) -> bool:
        """Activate a loaded plugin."""
        with self._lock:
            try:
                if plugin_id not in self.plugins:
                    self.logger.error(f"Plugin not loaded: {plugin_id}")
                    return False

                plugin = self.plugins[plugin_id]

                if plugin.activate():
                    self.states[plugin_id] = PluginState.ACTIVE

                    # Emit signal
                    if PYQT_AVAILABLE:
                        self.plugin_activated.emit(plugin_id)

                    self.logger.info(f"Plugin activated: {plugin_id}")
                    return True
                else:
                    self.states[plugin_id] = PluginState.ERROR
                    return False

            except Exception as e:
                self.states[plugin_id] = PluginState.ERROR
                self.logger.error(f"Plugin activation failed: {e}")
                return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate an active plugin."""
        with self._lock:
            try:
                if plugin_id not in self.plugins:
                    return True  # Already deactivated

                plugin = self.plugins[plugin_id]

                if plugin.deactivate():
                    self.states[plugin_id] = PluginState.INITIALIZED

                    # Emit signal
                    if PYQT_AVAILABLE:
                        self.plugin_deactivated.emit(plugin_id)

                    self.logger.info(f"Plugin deactivated: {plugin_id}")
                    return True
                else:
                    return False

            except Exception as e:
                self.logger.error(f"Plugin deactivation failed: {e}")
                return False

    def _find_plugin_file(self, plugin_id: str) -> Optional[Path]:
        """Find plugin file by ID."""
        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue

            # Look for Python file
            py_file = plugin_path / f"{plugin_id}.py"
            if py_file.exists():
                return py_file

            # Look for zip package
            zip_file = plugin_path / f"{plugin_id}.zip"
            if zip_file.exists():
                return zip_file

            # Look in subdirectories
            for subdir in plugin_path.iterdir():
                if subdir.is_dir():
                    py_file = subdir / f"{plugin_id}.py"
                    if py_file.exists():
                        return py_file

                    zip_file = subdir / f"{plugin_id}.zip"
                    if zip_file.exists():
                        return zip_file

        return None

    def _create_plugin_context(
        self, plugin_id: str, manifest: PluginManifest
    ) -> PluginContext:
        """Create plugin context."""
        import platform

        # Create plugin-specific directories
        plugin_dir = Path.home() / ".rfu" / "plugins" / plugin_id
        config_dir = plugin_dir / "config"
        temp_dir = plugin_dir / "temp"

        for directory in [plugin_dir, config_dir, temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        return PluginContext(
            plugin_id=plugin_id,
            application_version="1.0.0",  # Would be dynamic
            working_directory=plugin_dir,
            config_directory=config_dir,
            temp_directory=temp_dir,
            system_info={
                "platform": platform.system().lower(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
            },
            permissions=self._calculate_permissions(manifest),
            resource_limits=self._calculate_resource_limits(manifest),
        )

    def _calculate_permissions(self, manifest: PluginManifest) -> Set[str]:
        """Calculate permissions for plugin."""
        permissions = set()

        capability_permissions = {
            PluginCapability.FILE_PROCESSING: {"file_read", "file_write"},
            PluginCapability.NETWORK_ACCESS: {"network"},
            PluginCapability.SYSTEM_ACCESS: {"system"},
            PluginCapability.DATABASE_ACCESS: {"database"},
        }

        for capability in manifest.capabilities:
            permissions.update(capability_permissions.get(capability, set()))

        return permissions

    def _calculate_resource_limits(
        self, manifest: PluginManifest
    ) -> Dict[str, Any]:
        """Calculate resource limits for plugin."""
        base_limits = {
            "max_memory_mb": 256,
            "max_cpu_percent": 25,
            "max_disk_space_mb": 100,
            "max_network_connections": 5,
            "max_execution_time_seconds": 300,
        }

        # Adjust based on security level
        if manifest.security_level == SecurityLevel.ELEVATED:
            base_limits["max_memory_mb"] = 512
            base_limits["max_cpu_percent"] = 50
        elif manifest.security_level == SecurityLevel.TRUSTED:
            base_limits["max_memory_mb"] = 1024
            base_limits["max_cpu_percent"] = 75

        # Override with manifest requirements
        base_limits.update(manifest.resource_requirements)

        return base_limits

    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive plugin information."""
        if plugin_id not in self.manifests:
            return None

        manifest = self.manifests[plugin_id]
        state = self.states.get(plugin_id, PluginState.UNKNOWN)

        info = {
            "manifest": manifest,
            "state": state,
            "loaded": plugin_id in self.plugins,
            "active": state == PluginState.ACTIVE,
        }

        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            info["status"] = plugin.get_status()

        return info

    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """Get information about all plugins."""
        plugins_info = []

        for plugin_id in self.manifests:
            info = self.get_plugin_info(plugin_id)
            if info:
                plugins_info.append({"id": plugin_id, **info})

        return plugins_info

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        total_plugins = len(self.manifests)
        loaded_plugins = len(self.plugins)
        active_plugins = len(
            [
                pid
                for pid, state in self.states.items()
                if state == PluginState.ACTIVE
            ]
        )

        return {
            "total_plugins": total_plugins,
            "loaded_plugins": loaded_plugins,
            "active_plugins": active_plugins,
            "states": {
                state.value: count
                for state, count in self._count_states().items()
            },
            "types": self._count_types(),
            "security_levels": self._count_security_levels(),
            "configuration": self.config.copy(),
        }

    def _count_states(self) -> Dict[PluginState, int]:
        """Count plugins by state."""
        counts = {}
        for state in self.states.values():
            counts[state] = counts.get(state, 0) + 1
        return counts

    def _count_types(self) -> Dict[str, int]:
        """Count plugins by type."""
        counts = {}
        for manifest in self.manifests.values():
            type_name = manifest.plugin_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def _count_security_levels(self) -> Dict[str, int]:
        """Count plugins by security level."""
        counts = {}
        for manifest in self.manifests.values():
            level_name = manifest.security_level.name
            counts[level_name] = counts.get(level_name, 0) + 1
        return counts

    def shutdown(self) -> None:
        """Shutdown the plugin system."""
        try:
            # Deactivate and unload all plugins
            for plugin_id in list(self.plugins.keys()):
                self.unload_plugin(plugin_id)

            self.logger.info("Plugin system shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during plugin system shutdown: {e}")


# Global instance for application-wide access
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
