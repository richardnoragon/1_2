"""Tool Manifest — declares tool identity and minimum geometry constraints.

ToolManifestEntry contains only tool-authored declarations (e.g. min_window_width,
min_window_height).  User-state fields (window_x, window_y) MUST NOT appear here
— those belong exclusively in AppearanceProfile / UAPSettings.  (I2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ToolManifestEntry:
    """Metadata for a registered tool.

    Attributes:
        tool_id:           Unique kebab-case identifier, e.g. "duplicate-finder".
        display_name:      Human-readable label shown in the hub.
        module_path:       Dotted import path, e.g. "src.tools.analysis.duplicate_finder".
        class_name:        Class to instantiate, e.g. "DuplicateFinderApp".
        category:          Logical grouping key, e.g. "analysis".
        min_window_width:  Minimum width enforced by UAPService.apply().  Default 400.
        min_window_height: Minimum height enforced by UAPService.apply().  Default 300.
        tool_version:      Optional semver string.
        uap_exempt:        When True the tool is excluded from UAP apply/audit.
        headless_incompatible: When True the tool cannot be instantiated headlessly.
        headless_reason:   One-line reason why the tool is headless-incompatible.
    """

    tool_id: str
    display_name: str
    module_path: str
    class_name: str
    category: str
    min_window_width: int = 400
    min_window_height: int = 300
    tool_version: Optional[str] = None
    uap_exempt: bool = False
    headless_incompatible: bool = False
    headless_reason: Optional[str] = None


class ToolManifestRegistry:
    """Registry of all known tools.

    T041 MUST NOT seed, mutate, or add entries to this registry.
    T041 MUST fail if ``all()`` returns fewer than two entries.
    """

    _entries: Dict[str, ToolManifestEntry] = {}

    @classmethod
    def register(cls, entry: ToolManifestEntry) -> None:
        """Register a tool entry.  Overwrites an existing entry with the same tool_id."""
        cls._entries[entry.tool_id] = entry

    @classmethod
    def get(cls, tool_id: str) -> Optional[ToolManifestEntry]:
        """Return the entry for *tool_id*, or None if not found."""
        return cls._entries.get(tool_id)

    @classmethod
    def all(cls) -> List[ToolManifestEntry]:
        """Return a snapshot list of all registered entries."""
        return list(cls._entries.values())

    @classmethod
    def clear(cls) -> None:
        """Remove all entries.  Use only in tests."""
        cls._entries.clear()


# ---------------------------------------------------------------------------
# Seed entries — canonical baseline used by T041 audit and T007 contract tests
# ---------------------------------------------------------------------------
ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="tool.alpha",
        display_name="Alpha Tool",
        module_path="src.tools.alpha",
        class_name="AlphaGUI",
        category="analysis",
        min_window_width=480,
        min_window_height=320,
    )
)

ToolManifestRegistry.register(
    ToolManifestEntry(
        tool_id="tool.beta",
        display_name="Beta Tool",
        module_path="src.tools.beta",
        class_name="BetaGUI",
        category="analysis",
        min_window_width=600,
        min_window_height=400,
    )
)
