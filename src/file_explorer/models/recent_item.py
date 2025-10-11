"""
Recent item data model.

Represents recently accessed tools or locations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict


class RecentItemType(Enum):
    """Types of recent items."""

    TOOL = "tool"
    LOCATION = "location"

    def __str__(self):
        """String representation."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "RecentItemType":
        """Create enum from string value."""
        for rtype in cls:
            if rtype.value == value:
                return rtype
        raise ValueError(f"Invalid recent item type: {value}")


@dataclass
class RecentItem:
    """Recently accessed tool or location."""

    type: RecentItemType
    name: str
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)

    @classmethod
    def create(
        cls, type: RecentItemType, name: str, metadata: Dict = None
    ) -> "RecentItem":
        """Factory method to create a new recent item."""
        return cls(
            type=type, name=name, timestamp=datetime.now(), metadata=metadata or {}
        )

    def __post_init__(self):
        """Validate recent item data."""
        if not self.name:
            raise ValueError("name is required")

        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

        if self.timestamp > datetime.now():
            raise ValueError("timestamp cannot be in the future")

    def update_timestamp(self):
        """Update timestamp to current time."""
        self.timestamp = datetime.now()

    @classmethod
    def from_dict(cls, data: dict) -> "RecentItem":
        """
        Create RecentItem from dictionary.

        Args:
            data: Dictionary containing recent item data

        Returns:
            RecentItem: Restored recent item object
        """
        return cls(
            type=RecentItemType.from_string(data["type"]),
            name=data["name"],
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if isinstance(data["timestamp"], str)
                else data["timestamp"]
            ),
            metadata=data.get("metadata", {}),
        )
