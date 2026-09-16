"""Tool Manifest — declares tool identity and minimum geometry constraints.

ToolManifestEntry contains only tool-authored declarations (e.g. min_window_width,
min_window_height).  User-state fields (window_x, window_y) MUST NOT appear here
— those belong exclusively in AppearanceProfile / UAPSettings.  (I2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _normalize_tool_key(value: str) -> str:
    """Normalize a tool label for manifest lookup."""

    return "".join(ch for ch in value.lower().strip() if ch.isalnum())


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
    # None means not yet declared; it must never be presented as supported.
    undo_supported: Optional[bool] = None
    aliases: tuple[str, ...] = ()
    builtin: bool = False
    commands: tuple = ()
    preferences: dict = field(default_factory=dict)
    telemetry: dict = field(default_factory=dict)


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
        return cls._entries.get(tool_id) or cls.lookup(tool_id)

    @classmethod
    def lookup(cls, tool_name: str) -> Optional[ToolManifestEntry]:
        """Find an entry by tool_id or human-readable display name."""

        normalized = _normalize_tool_key(tool_name)
        for entry in cls._entries.values():
            if normalized == _normalize_tool_key(entry.tool_id):
                return entry
            if normalized == _normalize_tool_key(entry.display_name):
                return entry
            if normalized in {_normalize_tool_key(alias) for alias in entry.aliases}:
                return entry
        return None

    @classmethod
    def all(cls) -> List[ToolManifestEntry]:
        """Return a snapshot list of all registered entries."""
        return list(cls._entries.values())

    @classmethod
    def builtins(cls) -> List[ToolManifestEntry]:
        """The governed built-in tools; user-loaded plugins are kept separate."""
        return [entry for entry in cls._entries.values() if entry.builtin]

    @classmethod
    def clear(cls) -> None:
        """Remove all entries.  Use only in tests."""
        cls._entries.clear()


def _register_builtins():
    from src.core.tool_inventory import load_inventory
    for row in load_inventory()["tools"]:
        ToolManifestRegistry.register(ToolManifestEntry(
            tool_id=row["id"], display_name=row["display_name"],
            module_path=row["module_path"], class_name=row["class_name"],
            category=row["category"].lower().replace(" ", "-"),
            aliases=tuple(row.get("aliases", [])), builtin=True,
            undo_supported=row.get("undo_supported"),
        ))


_register_builtins()
