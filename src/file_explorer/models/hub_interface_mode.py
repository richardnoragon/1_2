"""
HubInterfaceMode enumeration.

Defines the top-level user experience modes for the RFU hub.
"""

from enum import Enum


class HubInterfaceMode(Enum):
    """Hub interface mode selection."""

    MULTI_PANE = "multi_pane"
    TABBED = "tabbed"

    def __str__(self):
        """String representation."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "HubInterfaceMode":
        """Create enum from string value."""
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"Invalid hub mode: {value}")
