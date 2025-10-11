"""
Tool data model.

Represents an executable RFU utility program.
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Tool:
    """RFU executable tool representation."""

    name: str
    description: str
    category: str
    launcher: Callable[[], None]
    icon: Optional[str] = None
    executable_path: str = ""

    def __post_init__(self):
        """Validate tool data."""
        if not self.name or len(self.name) > 50:
            raise ValueError("name must be 1-50 characters")

        if not self.description or len(self.description) > 200:
            raise ValueError("description must be 1-200 characters")

        if not self.category:
            raise ValueError("category is required")

        if not callable(self.launcher):
            raise ValueError("launcher must be callable")

    def launch(self):
        """Launch the tool."""
        self.launcher()
