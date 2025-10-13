#!/usr/bin/env python3
"""
Tool Integration for Multi-Pane File Explorer

Provides unified tool launching and integration capabilities with
comprehensive error handling and fallback mechanisms.

Author: Enterprise Code Guardian Team
Version: 1.0.0
Created: September 28, 2025
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from PyQt5.QtCore import QObject, pyqtSignal

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QObject = object


class ToolIntegration(QObject if QT_AVAILABLE else object):
    """
    Unified tool integration system with enterprise-grade reliability.

    Responsibilities:
    - Discover and catalog available tools
    - Provide unified tool launching interface
    - Handle tool import strategies with fallbacks
    - Coordinate tool communication with explorer
    """

    # Signals
    toolLaunched = pyqtSignal(str) if QT_AVAILABLE else None
    toolFailed = pyqtSignal(str, str) if QT_AVAILABLE else None

    def __init__(self, controller):
        """Initialize tool integration."""
        if QT_AVAILABLE:
            super().__init__()

        self.logger = logging.getLogger("RFU.ToolIntegration")
        self.controller = controller

        # Tool registry
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self.tool_categories: Dict[str, List[str]] = {}

        # Import strategies
        self.import_strategies = [
            self._import_direct,
            self._import_with_src_prefix,
            self._import_legacy_path,
            self._import_relative,
        ]

        self.logger.info("Tool integration initialized")

    def setup(self):
        """Setup tool integration system."""
        try:
            self._discover_tools()
            self._organize_tool_categories()
            self.logger.info("Tool integration setup completed")
        except Exception as e:
            self.logger.error(f"Error setting up tool integration: {e}")

    def _discover_tools(self):
        """Discover available tools from standard locations."""
        try:
            # Define standard tool configurations
            standard_tools = {
                "File Finder": {
                    "module": "src.tools.file_management.finder.file_finder",
                    "class": "FileFinderWindow",
                    "category": "File Management",
                    "description": "Search and find files",
                },
                "Size Analyzer": {
                    "module": "src.tools.analysis.size_analyzer",
                    "class": "SizeAnalyzerGUI",
                    "category": "Analysis",
                    "description": "Analyze disk space usage",
                },
                "Duplicate Finder": {
                    "module": "src.tools.analysis.find_duplicate_files",
                    "class": "DuplicateFinderApp",
                    "category": "Analysis",
                    "description": "Find and remove duplicates",
                },
                "Encrypt/Decrypt": {
                    "module": "src.tools.security.en_and_decrypt",
                    "class": "EnAndDecryptGUI",
                    "category": "Security",
                    "description": "File encryption/decryption",
                },
                "Secure Delete": {
                    "module": "src.tools.security.secure_delete",
                    "class": "SecureDeleteGUI",
                    "category": "Security",
                    "description": "Secure file deletion",
                },
                "Network Scanner": {
                    "module": "src.tools.network.scanner.network_scanner",
                    "class": "NetworkScannerGUI",
                    "category": "Network",
                    "description": "Scan network devices",
                },
            }

            # Test tool availability
            for tool_name, config in standard_tools.items():
                if self._test_tool_availability(config):
                    self.available_tools[tool_name] = config
                    self.logger.debug(f"Tool {tool_name} available")
                else:
                    self.logger.debug(f"Tool {tool_name} not available")

            self.logger.info(f"Discovered {len(self.available_tools)} tools")

        except Exception as e:
            self.logger.error(f"Error discovering tools: {e}")

    def _test_tool_availability(self, config: Dict[str, Any]) -> bool:
        """Test if a tool is available for import."""
        try:
            module_name = config.get("module", "")
            class_name = config.get("class", "")

            if not module_name or not class_name:
                return False

            # Try each import strategy
            for strategy in self.import_strategies:
                try:
                    tool_class = strategy(module_name, class_name)
                    if tool_class:
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            self.logger.debug(f"Tool availability test failed: {e}")
            return False

    def _organize_tool_categories(self):
        """Organize tools into categories."""
        try:
            self.tool_categories.clear()

            for tool_name, config in self.available_tools.items():
                category = config.get("category", "Other")
                if category not in self.tool_categories:
                    self.tool_categories[category] = []
                self.tool_categories[category].append(tool_name)

            self.logger.info(
                f"Organized tools into {len(self.tool_categories)} categories"
            )

        except Exception as e:
            self.logger.error(f"Error organizing tool categories: {e}")

    def launch(self, tool_name: str, **kwargs) -> bool:
        """
        Launch specified tool with unified interface.

        Args:
            tool_name: Name of tool to launch
            **kwargs: Additional parameters for tool

        Returns:
            bool: True if successfully launched
        """
        try:
            if tool_name not in self.available_tools:
                self.logger.warning(f"Tool {tool_name} not available")
                if self.toolFailed:
                    self.toolFailed.emit(tool_name, "Tool not available")
                return False

            config = self.available_tools[tool_name]
            module_name = config["module"]
            class_name = config["class"]

            # Try to import and launch tool
            tool_class = self._import_tool_class(module_name, class_name)
            if not tool_class:
                if self.toolFailed:
                    self.toolFailed.emit(tool_name, "Import failed")
                return False

            # Create and show tool instance
            tool_instance = tool_class()
            tool_instance.show()

            # Emit success signal
            if self.toolLaunched:
                self.toolLaunched.emit(tool_name)

            self.logger.info(f"Successfully launched tool: {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error launching tool {tool_name}: {e}")
            if self.toolFailed:
                self.toolFailed.emit(tool_name, str(e))
            return False

    def _import_tool_class(self, module_name: str, class_name: str):
        """Import tool class using available strategies."""
        try:
            # Try each import strategy
            for strategy in self.import_strategies:
                try:
                    tool_class = strategy(module_name, class_name)
                    if tool_class:
                        return tool_class
                except Exception as e:
                    self.logger.debug(f"Import strategy failed: {e}")
                    continue

            self.logger.error(
                f"All import strategies failed for {module_name}.{class_name}"
            )
            return None

        except Exception as e:
            self.logger.error(f"Error importing tool class: {e}")
            return None

    def _import_direct(self, module_name: str, class_name: str):
        """Direct import strategy."""
        try:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name, None)
        except (ImportError, AttributeError):
            return None

    def _import_with_src_prefix(self, module_name: str, class_name: str):
        """Import with src prefix strategy."""
        try:
            if not module_name.startswith("src."):
                prefixed_module = f"src.{module_name}"
            else:
                prefixed_module = module_name

            module = __import__(prefixed_module, fromlist=[class_name])
            return getattr(module, class_name, None)
        except (ImportError, AttributeError):
            return None

    def _import_legacy_path(self, module_name: str, class_name: str):
        """Legacy path import strategy."""
        try:
            # Convert src.tools to utilities for legacy compatibility
            legacy_module = module_name.replace("src.tools.", "src.utilities.")
            module = __import__(legacy_module, fromlist=[class_name])
            return getattr(module, class_name, None)
        except (ImportError, AttributeError):
            return None

    def _import_relative(self, module_name: str, class_name: str):
        """Relative import strategy."""
        try:
            # Remove src prefix for relative import
            relative_module = module_name.replace("src.", "")
            module = __import__(relative_module, fromlist=[class_name])
            return getattr(module, class_name, None)
        except (ImportError, AttributeError):
            return None

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.available_tools.keys())

    def get_tool_categories(self) -> Dict[str, List[str]]:
        """Get tools organized by category."""
        return dict(self.tool_categories)

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return self.available_tools.get(tool_name)

    def is_tool_available(self, tool_name: str) -> bool:
        """Check if tool is available for launch."""
        return tool_name in self.available_tools

    def refresh_tool_discovery(self):
        """Refresh tool discovery process."""
        try:
            self.logger.info("Refreshing tool discovery")
            old_count = len(self.available_tools)

            self._discover_tools()
            self._organize_tool_categories()

            new_count = len(self.available_tools)
            msg = f"Tool discovery refreshed: {old_count} -> {new_count} tools"
            self.logger.info(msg)

        except Exception as e:
            self.logger.error(f"Error refreshing tool discovery: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get tool integration status."""
        return {
            "total_tools": len(self.available_tools),
            "categories": len(self.tool_categories),
            "tools_by_category": {
                category: len(tools) for category, tools in self.tool_categories.items()
            },
            "available_tools": list(self.available_tools.keys()),
        }

    def cleanup(self):
        """Clean up tool integration."""
        try:
            self.logger.info("Cleaning up tool integration")
            self.available_tools.clear()
            self.tool_categories.clear()
            self.logger.info("Tool integration cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during tool integration cleanup: {e}")
