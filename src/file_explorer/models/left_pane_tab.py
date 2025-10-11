"""
LeftPaneTab enumeration.

Defines available tabs in the left pane.
"""

from enum import Enum


class LeftPaneTab(Enum):
    """Left pane tab identifiers."""

    BOOKMARKS = "bookmarks"
    RECENT = "recent"
    TOOLS = "tools"

    def __str__(self):
        """String representation."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "LeftPaneTab":
        """Create enum from string value."""
        for tab in cls:
            if tab.value == value:
                return tab
        raise ValueError(f"Invalid left pane tab: {value}")
