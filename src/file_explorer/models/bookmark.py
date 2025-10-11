"""
Bookmark data model.

Represents user-saved references to tools or file system locations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict


class BookmarkType(Enum):
    """Types of bookmarks."""

    TOOL = "tool"
    DRIVE = "drive"
    FOLDER = "folder"
    NETWORK_LOCATION = "network"

    def __str__(self):
        """String representation."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "BookmarkType":
        """Create enum from string value."""
        for btype in cls:
            if btype.value == value:
                return btype
        raise ValueError(f"Invalid bookmark type: {value}")


@dataclass
class Bookmark:
    """User bookmark for tool or location."""

    id: str
    type: BookmarkType
    name: str
    target: str
    created_at: datetime
    metadata: Dict = field(default_factory=dict)

    @classmethod
    def create(
        cls, type: BookmarkType, name: str, target: str, metadata: Dict = None
    ) -> "Bookmark":
        """Factory method to create a new bookmark."""
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            name=name,
            target=target,
            created_at=datetime.now(),
            metadata=metadata or {},
        )

    def __post_init__(self):
        """Validate bookmark data."""
        if not self.name or len(self.name) > 100:
            raise ValueError("name must be 1-100 characters")

        if not self.target:
            raise ValueError("target is required")

        # Target validation based on type
        if self.type == BookmarkType.TOOL:
            # Basic tool name validation
            # Full validation requires ToolsDiscoveryService (not yet implemented)
            if not self.target or len(self.target) < 2:
                raise ValueError("Tool bookmark target must be valid tool name")
            # Check for obviously invalid characters in tool names
            invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
            if any(char in self.target for char in invalid_chars):
                raise ValueError("Tool name contains invalid characters")

        if self.type == BookmarkType.FOLDER:
            import os

            if not os.path.isabs(self.target):
                raise ValueError("Folder bookmark target must be absolute path")

        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)

        if self.created_at > datetime.now():
            raise ValueError("created_at cannot be in the future")

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        """
        Create Bookmark from dictionary.

        Args:
            data: Dictionary containing bookmark data

        Returns:
            Bookmark: Restored bookmark object
        """
        return cls(
            id=data["id"],
            type=BookmarkType.from_string(data["type"]),
            name=data["name"],
            target=data["target"],
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if isinstance(data["created_at"], str)
                else data["created_at"]
            ),
            metadata=data.get("metadata", {}),
        )
