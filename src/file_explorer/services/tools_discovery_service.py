"""
ToolsDiscoveryService: Discover and retrieve RFU executable tools.

This service integrates with the RFU tool registry to provide searchable
access to all available tools.
"""

import logging
from typing import List, Optional

from src.file_explorer.models.tool import Tool


class ToolsDiscoveryService:
    """Service for discovering RFU executable tools."""

    def __init__(self, main_app=None):
        """
        Initialize the tools discovery service.

        Args:
            main_app: Optional main application instance with tool_categories.
                     If None, will attempt to import from RFU main.py
        """
        self.logger = logging.getLogger("RFU.FileExplorer.ToolsDiscoveryService")
        self._main_app = main_app
        self._cache: Optional[List[Tool]] = None
        self.logger.info("ToolsDiscoveryService initialized")

    def get_all_tools(self) -> List[Tool]:
        """
        Retrieve all executable RFU tools.

        Returns:
            List[Tool]: All registered tools
        """
        if self._cache is not None:
            return self._cache

        try:
            tools = []

            # Get main app instance
            main_app = self._get_main_app()
            if main_app is None:
                return []

            # Iterate through tool categories
            for category_widget in main_app.tool_categories:
                category_name = category_widget.category_name

                # Iterate through tools in each category
                for tool_button in category_widget.tool_buttons:
                    # Skip non-executable items (separators, folders)
                    if hasattr(tool_button, "is_separator"):
                        continue
                    if not hasattr(tool_button, "name"):
                        continue

                    # Create Tool object
                    launcher = getattr(tool_button, "launcher", None)
                    if launcher is None:
                        launcher = lambda: None  # noqa: E731

                    executable_path = getattr(tool_button, "executable_path", None)
                    if executable_path is None:
                        executable_path = ""

                    tool = Tool(
                        name=tool_button.name,
                        description=getattr(tool_button, "description", ""),
                        category=category_name,
                        launcher=launcher,
                        icon=getattr(tool_button, "icon", None),
                        executable_path=executable_path,
                    )
                    tools.append(tool)

            # Sort by category, then name
            tools.sort(key=lambda t: (t.category, t.name))

            # Cache result
            self._cache = tools

            self.logger.info(f"Discovered {len(tools)} tools")
            return tools

        except Exception as e:
            self.logger.error(f"Error getting all tools: {e}")
            return []

    def search_tools(self, query: str) -> List[Tool]:
        """
        Search tools by name or description.

        Args:
            query: Search string (case-insensitive)

        Returns:
            List[Tool]: Matching tools
        """
        try:
            all_tools = self.get_all_tools()
            query_lower = query.lower()

            matching_tools = [
                tool
                for tool in all_tools
                if query_lower in tool.name.lower()
                or query_lower in tool.description.lower()
            ]

            return matching_tools

        except Exception as e:
            self.logger.error(f"Error searching tools: {e}")
            return []

    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """
        Retrieve a specific tool by name.

        Args:
            name: Tool name

        Returns:
            Optional[Tool]: Tool if found, None otherwise
        """
        try:
            all_tools = self.get_all_tools()

            for tool in all_tools:
                if tool.name == name:
                    return tool

            return None

        except Exception as e:
            self.logger.error(f"Error getting tool by name: {e}")
            return None

    def _get_main_app(self):
        """
        Get the main application instance.

        Returns:
            Main application instance or None
        """
        # If test main_app provided, use it
        if self._main_app is not None:
            return self._main_app

        # Try to import from RFU main.py
        try:
            # In production, this would get the running app instance
            # from src.rfu import main
            # return main.get_app_instance()
            pass
        except ImportError:
            pass

        # Fallback: return None
        self.logger.warning("Could not load main app, tools discovery unavailable")
        return None


# Singleton instance
_tools_discovery_service: Optional[ToolsDiscoveryService] = None


def get_tools_discovery_service() -> ToolsDiscoveryService:
    """
    Get the singleton tools discovery service instance.

    Returns:
        ToolsDiscoveryService: The tools discovery service instance
    """
    global _tools_discovery_service
    if _tools_discovery_service is None:
        _tools_discovery_service = ToolsDiscoveryService()
    return _tools_discovery_service
