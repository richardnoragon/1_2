"""
User preferences data model.

Consolidated user configuration for Multi-Pane Explorer.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .bookmark import Bookmark
from .hub_interface_mode import HubInterfaceMode
from .left_pane_tab import LeftPaneTab
from .pane_configuration import LayoutType, PaneConfiguration
from .recent_item import RecentItem
from .right_pane_tab import RightPaneTab


@dataclass
class UserPreferences:
    """Complete user preferences for Multi-Pane Explorer."""

    # Hub mode
    active_hub_mode: HubInterfaceMode = HubInterfaceMode.MULTI_PANE

    # Pane configuration
    pane_config: PaneConfiguration = field(
        default_factory=lambda: PaneConfiguration(1, LayoutType.DISABLED, {})
    )

    # Left pane
    left_default_tab: LeftPaneTab = LeftPaneTab.RECENT
    bookmarks: List[Bookmark] = field(default_factory=list)

    # Center panes
    center_default_root: Path = field(default_factory=Path.home)
    center_last_paths: List[Optional[Path]] = field(
        default_factory=lambda: [Path.home()]
    )

    # Right pane
    right_default_tab: RightPaneTab = RightPaneTab.PREVIEW

    # Recent items
    recent_tools: List[RecentItem] = field(default_factory=list)
    recent_locations: List[RecentItem] = field(default_factory=list)
    recent_max_per_section: int = 10

    def __post_init__(self):
        """Validate preferences."""
        # Ensure path objects
        if not isinstance(self.center_default_root, Path):
            self.center_default_root = Path(self.center_default_root)

        self.center_last_paths = [
            Path(p) if not isinstance(p, Path) else p
            for p in self.center_last_paths
            if p is not None
        ]

        # Validate recent items limits
        if self.recent_max_per_section < 5:
            raise ValueError("recent_max_per_section must be >= 5")

        if self.recent_max_per_section > 50:
            raise ValueError("recent_max_per_section must be <= 50")

        # Trim recent items to max limit
        self.recent_tools = self.recent_tools[: self.recent_max_per_section]
        self.recent_locations = self.recent_locations[: self.recent_max_per_section]

    @classmethod
    def create_defaults(cls) -> "UserPreferences":
        """Create default preferences."""
        return cls()

    def to_dict(self) -> dict:
        """
        Convert preferences to dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of preferences
        """
        return {
            "active_hub_mode": self.active_hub_mode.value,
            "pane_config": {
                "pane_count": self.pane_config.pane_count,
                "layout_type": self.pane_config.layout_type.value,
                "splitter_states": {
                    k: v.hex() if isinstance(v, bytes) else v
                    for k, v in self.pane_config.splitter_states.items()
                },
            },
            "left_default_tab": self.left_default_tab.value,
            "bookmarks": [
                {
                    "id": b.id,
                    "type": b.type.value,
                    "name": b.name,
                    "target": b.target,
                    "created_at": b.created_at.isoformat(),
                    "metadata": b.metadata,
                }
                for b in self.bookmarks
            ],
            "center_default_root": str(self.center_default_root),
            "center_last_paths": [
                str(p) if p else None for p in self.center_last_paths
            ],
            "right_default_tab": self.right_default_tab.value,
            "recent_tools": [
                {
                    "type": r.type.value,
                    "name": r.name,
                    "timestamp": r.timestamp.isoformat(),
                    "metadata": r.metadata,
                }
                for r in self.recent_tools
            ],
            "recent_locations": [
                {
                    "type": r.type.value,
                    "name": r.name,
                    "timestamp": r.timestamp.isoformat(),
                    "metadata": r.metadata,
                }
                for r in self.recent_locations
            ],
            "recent_max_per_section": self.recent_max_per_section,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """
        Create preferences from dictionary (JSON deserialization).

        Args:
            data: Dictionary containing preference data

        Returns:
            UserPreferences: Restored preferences object

        Raises:
            ValueError: If data is invalid
            KeyError: If required keys are missing
        """
        from datetime import datetime

        from .bookmark import BookmarkType
        from .recent_item import RecentItemType

        # Parse hub mode
        active_hub_mode = HubInterfaceMode.from_string(
            data.get("active_hub_mode", "multi_pane")
        )

        # Parse pane configuration
        pane_config_data = data.get("pane_config", {})
        pane_config = PaneConfiguration(
            pane_count=pane_config_data.get("pane_count", 1),
            layout_type=LayoutType.from_string(
                pane_config_data.get("layout_type", "disabled")
            ),
            splitter_states={
                k: bytes.fromhex(v) if isinstance(v, str) else v
                for k, v in pane_config_data.get("splitter_states", {}).items()
            },
        )

        # Parse left pane tab
        left_default_tab = LeftPaneTab.from_string(
            data.get("left_default_tab", "recent")
        )

        # Parse bookmarks
        bookmarks = []
        for b_data in data.get("bookmarks", []):
            bookmark = Bookmark.from_dict(b_data)
            bookmarks.append(bookmark)

        # Parse center pane paths
        center_default_root = Path(data.get("center_default_root", Path.home()))
        center_last_paths = [
            Path(p) if p else None for p in data.get("center_last_paths", [Path.home()])
        ]

        # Parse right pane tab
        right_default_tab = RightPaneTab.from_string(
            data.get("right_default_tab", "preview")
        )

        # Parse recent items
        recent_tools = []
        for r_data in data.get("recent_tools", []):
            recent_item = RecentItem.from_dict(r_data)
            recent_tools.append(recent_item)

        recent_locations = []
        for r_data in data.get("recent_locations", []):
            recent_item = RecentItem.from_dict(r_data)
            recent_locations.append(recent_item)

        recent_max_per_section = data.get("recent_max_per_section", 10)

        return cls(
            active_hub_mode=active_hub_mode,
            pane_config=pane_config,
            left_default_tab=left_default_tab,
            bookmarks=bookmarks,
            center_default_root=center_default_root,
            center_last_paths=center_last_paths,
            right_default_tab=right_default_tab,
            recent_tools=recent_tools,
            recent_locations=recent_locations,
            recent_max_per_section=recent_max_per_section,
        )
