"""
RightPaneTab enumeration.

Defines available tabs in the right pane.
"""

from enum import Enum


class RightPaneTab(Enum):
    """Right pane tab identifiers."""

    PREVIEW = "preview"
    PROPERTIES = "properties"

    def __str__(self):
        """String representation."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "RightPaneTab":
        """Create enum from string value."""
        for tab in cls:
            if tab.value == value:
                return tab
        raise ValueError(f"Invalid right pane tab: {value}")
