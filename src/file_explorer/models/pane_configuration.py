"""
Pane configuration models.

Defines pane count and layout arrangement types.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class LayoutType(Enum):
    """Layout arrangement types for center panes."""

    DISABLED = "disabled"  # 1 pane only, no layout
    HORIZONTAL = "horizontal"  # Side-by-side arrangement
    VERTICAL = "vertical"  # Top-to-bottom arrangement
    GRID = "grid"  # 2x2 grid arrangement

    def __str__(self):
        """String representation."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "LayoutType":
        """Create enum from string value."""
        for layout in cls:
            if layout.value == value:
                return layout
        raise ValueError(f"Invalid layout type: {value}")


@dataclass
class PaneConfiguration:
    """Configuration for pane count and layout."""

    pane_count: int  # 1, 2, 3, or 4
    layout_type: LayoutType
    splitter_states: Dict[str, bytes] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate pane configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not 1 <= self.pane_count <= 4:
            raise ValueError(f"pane_count must be 1-4, got {self.pane_count}")

        # Validation rules for layout type
        if self.pane_count == 1 and self.layout_type != LayoutType.DISABLED:
            raise ValueError("pane_count=1 requires layout_type=DISABLED")

        if self.pane_count == 2:
            if self.layout_type not in [LayoutType.HORIZONTAL, LayoutType.VERTICAL]:
                raise ValueError("pane_count=2 requires HORIZONTAL or VERTICAL layout")

        if self.pane_count >= 3:
            if self.layout_type == LayoutType.DISABLED:
                raise ValueError(
                    f"pane_count={self.pane_count} cannot use DISABLED layout"
                )
