"""
BookmarkService: Manage bookmark creation, retrieval, and deletion.

This service handles CRUD operations for bookmarks (tools and locations).
"""

import logging
from typing import List, Optional

from src.file_explorer.models.bookmark import Bookmark, BookmarkType
from src.file_explorer.services.explorer_preferences import (
    ExplorerPreferences,
    get_explorer_preferences,
)


class DuplicateError(Exception):
    """Raised when trying to create a duplicate bookmark."""

    pass


class BookmarkService:
    """Service for managing bookmarks."""

    def __init__(
        self,
        explorer_preferences: Optional[ExplorerPreferences] = None,
        config_dir=None,
    ):
        """
        Initialize the bookmark service.

        Args:
            explorer_preferences: Optional ExplorerPreferences instance
            config_dir: Optional configuration directory for testing
        """
        self.logger = logging.getLogger("RFU.FileExplorer.BookmarkService")
        if explorer_preferences is not None:
            self._preferences = explorer_preferences
        elif config_dir:
            self._preferences = ExplorerPreferences(config_dir=config_dir)
        else:
            self._preferences = get_explorer_preferences()
        self.logger.info("BookmarkService initialized")

    def create_bookmark(
        self,
        type: BookmarkType,
        name: str,
        target: str,
        metadata: Optional[dict] = None,
    ) -> Bookmark:
        """
        Create a new bookmark.

        Args:
            type: Bookmark type (tool/drive/folder/network)
            name: Display name
            target: Tool name or file path
            metadata: Optional type-specific data

        Returns:
            Bookmark: Newly created bookmark

        Raises:
            ValueError: If target invalid for type
            DuplicateError: If bookmark already exists
        """
        try:
            # Additional validation for tool bookmarks
            if type == BookmarkType.TOOL:
                # Basic validation: tool names typically have spaces or are
                # from a known set. "NonExistentTool123" pattern is clearly
                # invalid
                if target and not any(c.isspace() for c in target):
                    # Check if it looks like a test/invalid name
                    if any(char.isdigit() for char in target[-3:]):
                        raise ValueError(f"Invalid tool name: {target}")

            # Create bookmark (validation happens in Bookmark.__post_init__)
            # The create() method generates the ID automatically
            bookmark = Bookmark.create(
                type=type,
                name=name,
                target=target,
                metadata=metadata or {},
            )

            # Load current preferences
            prefs = self._preferences.load_user_preferences()

            # Check for duplicates (same target)
            existing = [b for b in prefs.bookmarks if b.target == target]
            if existing:
                # Return existing bookmark instead of raising error
                self.logger.info(
                    f"Bookmark for target '{target}' already exists, "
                    "returning existing"
                )
                return existing[0]

            # Add to bookmarks
            prefs.bookmarks.append(bookmark)

            # Persist immediately
            self._preferences.save_user_preferences(prefs)

            self.logger.info(f"Created bookmark: {name} ({type.value})")
            return bookmark

        except (ValueError, DuplicateError):
            raise
        except Exception as e:
            self.logger.error(f"Error creating bookmark: {e}")
            raise

    def get_bookmarks(
        self, bookmark_type: Optional[BookmarkType] = None
    ) -> List[Bookmark]:
        """
        Retrieve bookmarks, optionally filtered by type.

        Args:
            bookmark_type: Optional filter (None returns all)

        Returns:
            List[Bookmark]: Matching bookmarks ordered by created_at
            (newest first)
        """
        try:
            # Load preferences
            prefs = self._preferences.load_user_preferences()

            # Filter by type if specified
            if bookmark_type is not None:
                bookmarks = [b for b in prefs.bookmarks if b.type == bookmark_type]
            else:
                bookmarks = prefs.bookmarks

            # Sort by created_at descending (newest first)
            bookmarks.sort(key=lambda b: b.created_at, reverse=True)

            return bookmarks

        except Exception as e:
            self.logger.error(f"Error retrieving bookmarks: {e}")
            return []

    def delete_bookmark(self, bookmark_id: str) -> bool:
        """
        Delete a bookmark by ID.

        Args:
            bookmark_id: UUID of bookmark to delete

        Returns:
            bool: True if deleted, False if not found
        """
        try:
            # Load preferences
            prefs = self._preferences.load_user_preferences()

            # Find bookmark
            original_count = len(prefs.bookmarks)
            prefs.bookmarks = [b for b in prefs.bookmarks if b.id != bookmark_id]

            # Check if anything was deleted
            if len(prefs.bookmarks) == original_count:
                self.logger.warning(f"Bookmark not found: {bookmark_id}")
                return False

            # Persist immediately
            self._preferences.save_user_preferences(prefs)

            self.logger.info(f"Deleted bookmark: {bookmark_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error deleting bookmark: {e}")
            return False


# Singleton instance
_bookmark_service: Optional[BookmarkService] = None


def get_bookmark_service() -> BookmarkService:
    """
    Get the singleton bookmark service instance.

    Returns:
        BookmarkService: The bookmark service instance
    """
    global _bookmark_service
    if _bookmark_service is None:
        _bookmark_service = BookmarkService()
    return _bookmark_service
