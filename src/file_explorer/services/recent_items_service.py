"""
RecentItemsService: Track recently accessed tools and locations.

This service implements LRU (Least Recently Used) cache with configurable limits.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.file_explorer.models.recent_item import RecentItem, RecentItemType
from src.file_explorer.services.preference_service import (
    PreferenceService,
    get_preference_service,
)


class RecentItemsService:
    """Service for tracking recent tools and locations."""

    def __init__(self, preference_service=None, config_dir=None, max_items=None):
        """
        Initialize the recent items service.

        Args:
            preference_service: Optional PreferenceService instance
            config_dir: Optional configuration directory for testing
            max_items: Optional max items limit (for testing)
        """
        self.logger = logging.getLogger("RFU.FileExplorer.RecentItemsService")
        if config_dir:
            self.preference_service = PreferenceService(config_dir)
        else:
            self.preference_service = preference_service or get_preference_service()
        self.logger.info("RecentItemsService initialized")

    def add_tool(self, tool_name: str, metadata: Optional[dict] = None) -> None:
        """
        Record a tool access.

        Args:
            tool_name: Name of the tool
            metadata: Optional metadata (category, icon, etc.)
        """
        try:
            # Load preferences
            prefs = self.preference_service.load_preferences()

            # Check if tool already exists
            existing_index = None
            for i, item in enumerate(prefs.recent_tools):
                if item.name == tool_name:
                    existing_index = i
                    break

            if existing_index is not None:
                # Update timestamp and move to front
                item = prefs.recent_tools.pop(existing_index)
                item.update_timestamp()
                prefs.recent_tools.insert(0, item)
                self.logger.debug(f"Updated recent tool: {tool_name}")
            else:
                # Create new recent item
                recent_item = RecentItem.create(
                    type=RecentItemType.TOOL,
                    name=tool_name,
                    metadata=metadata or {},
                )

                # Add to front of list
                prefs.recent_tools.insert(0, recent_item)
                self.logger.debug(f"Added recent tool: {tool_name}")

            # Enforce limit (evict oldest if needed)
            max_items = prefs.recent_max_per_section
            if len(prefs.recent_tools) > max_items:
                evicted = prefs.recent_tools[max_items:]
                prefs.recent_tools = prefs.recent_tools[:max_items]
                self.logger.debug(
                    f"Evicted {len(evicted)} old tool(s) from recent list"
                )

            # Persist immediately
            self.preference_service.save_preferences(prefs)

        except Exception as e:
            self.logger.error(f"Error adding recent tool: {e}")

    def add_location(self, path: Path, metadata: Optional[dict] = None) -> None:
        """
        Record a location access.

        Args:
            path: File system path
            metadata: Optional metadata (is_directory, size, etc.)
        """
        try:
            # Convert path to string
            path_str = str(path)

            # Load preferences
            prefs = self.preference_service.load_preferences()

            # Check if location already exists
            existing_index = None
            for i, item in enumerate(prefs.recent_locations):
                if item.name == path_str:
                    existing_index = i
                    break

            if existing_index is not None:
                # Update timestamp and move to front
                item = prefs.recent_locations.pop(existing_index)
                item.update_timestamp()
                prefs.recent_locations.insert(0, item)
                self.logger.debug(f"Updated recent location: {path_str}")
            else:
                # Create new recent item
                recent_item = RecentItem.create(
                    type=RecentItemType.LOCATION,
                    name=path_str,
                    metadata=metadata or {},
                )

                # Add to front of list
                prefs.recent_locations.insert(0, recent_item)
                self.logger.debug(f"Added recent location: {path_str}")

            # Enforce limit (evict oldest if needed)
            max_items = prefs.recent_max_per_section
            if len(prefs.recent_locations) > max_items:
                evicted = prefs.recent_locations[max_items:]
                prefs.recent_locations = prefs.recent_locations[:max_items]
                self.logger.debug(
                    f"Evicted {len(evicted)} old location(s) from recent list"
                )

            # Persist immediately
            self.preference_service.save_preferences(prefs)

        except Exception as e:
            self.logger.error(f"Error adding recent location: {e}")

    def get_recent_tools(self) -> List[RecentItem]:
        """
        Retrieve recent tools list.

        Returns:
            List[RecentItem]: Recent tools, newest first (max 10)
        """
        try:
            prefs = self.preference_service.load_preferences()
            return prefs.recent_tools

        except Exception as e:
            self.logger.error(f"Error retrieving recent tools: {e}")
            return []

    def get_recent_locations(self) -> List[RecentItem]:
        """
        Retrieve recent locations list.

        Returns:
            List[RecentItem]: Recent locations, newest first (max 10)
        """
        try:
            prefs = self.preference_service.load_preferences()
            return prefs.recent_locations

        except Exception as e:
            self.logger.error(f"Error retrieving recent locations: {e}")
            return []

    def clear_recent(self, item_type: Optional[RecentItemType] = None) -> None:
        """
        Clear recent items.

        Args:
            item_type: Optional filter (None clears both tools and locations)
        """
        try:
            prefs = self.preference_service.load_preferences()

            if item_type is None:
                # Clear both
                prefs.recent_tools = []
                prefs.recent_locations = []
                self.logger.info("Cleared all recent items")
            elif item_type == RecentItemType.TOOL:
                prefs.recent_tools = []
                self.logger.info("Cleared recent tools")
            elif item_type == RecentItemType.LOCATION:
                prefs.recent_locations = []
                self.logger.info("Cleared recent locations")

            # Persist immediately
            self.preference_service.save_preferences(prefs)

        except Exception as e:
            self.logger.error(f"Error clearing recent items: {e}")


# Singleton instance
_recent_items_service: Optional[RecentItemsService] = None


def get_recent_items_service() -> RecentItemsService:
    """
    Get the singleton recent items service instance.

    Returns:
        RecentItemsService: The recent items service instance
    """
    global _recent_items_service
    if _recent_items_service is None:
        _recent_items_service = RecentItemsService()
    return _recent_items_service
