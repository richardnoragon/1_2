"""
Center pane data model.

Represents a file/directory navigation view instance.
"""

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CenterPane:
    """File navigation pane state."""

    id: str
    current_path: Path
    history: List[Path] = field(default_factory=list)
    history_index: int = 0
    selected_items: List[Path] = field(default_factory=list)
    view_mode: str = "list"  # "list", "grid", "detail"

    @classmethod
    def create(cls, initial_path: Path) -> "CenterPane":
        """Factory method to create a new pane."""
        return cls(
            id=str(uuid.uuid4()),
            current_path=initial_path,
            history=[initial_path],
            history_index=0,
        )

    def __post_init__(self):
        """Validate pane data."""
        if not isinstance(self.current_path, Path):
            self.current_path = Path(self.current_path)

        if not self.history:
            self.history = [self.current_path]

        if self.history_index < 0 or self.history_index >= len(self.history):
            raise ValueError("history_index out of bounds")

        # Validate selected items are within current path
        for item in self.selected_items:
            if not isinstance(item, Path):
                raise ValueError("selected_items must be Path objects")

    def navigate_to(self, path: Path):
        """Navigate to a new path."""
        # Trim forward history when navigating to new location
        self.history = self.history[: self.history_index + 1]
        self.history.append(path)
        self.history_index = len(self.history) - 1
        self.current_path = path
        self.selected_items = []

    def can_go_back(self) -> bool:
        """Check if back navigation is possible."""
        return self.history_index > 0

    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible."""
        return self.history_index < len(self.history) - 1

    def go_back(self):
        """Navigate backward in history."""
        if self.can_go_back():
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.selected_items = []

    def go_forward(self):
        """Navigate forward in history."""
        if self.can_go_forward():
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.selected_items = []
