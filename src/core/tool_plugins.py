"""Explicit, atomic registration of locally installed Python tool plugins.

Reading a manifest never imports its entry points. Python code is imported only
when the user launches a tool through the normal lifecycle resolver.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.core.tool_manifest import ToolManifestEntry, ToolManifestRegistry

_IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
_MODULE = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\Z")


def load_manifest(path: Path | str) -> list[ToolManifestEntry]:
    """Validate the entire version-1 manifest before changing the registry.

    Plugins cannot replace built-in tools or existing plugin entries, including
    aliases formed by case/punctuation-insensitive display-name lookup.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "tools"}:
        raise ValueError("Manifest requires schema_version and tools only")
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ValueError("Unsupported plugin manifest version")
    rows = payload["tools"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Manifest must declare at least one tool")
    entries = []
    normalize = lambda value: "".join(c for c in value.lower() if c.isalnum())
    used = {normalize(value) for entry in ToolManifestRegistry.all()
            for value in (entry.tool_id, entry.display_name, *entry.aliases)}
    required = {"tool_id", "display_name", "module_path", "class_name", "category"}
    optional = {"tool_version", "min_window_width", "min_window_height", "undo_supported", "commands", "preferences", "telemetry"}
    for row in rows:
        if not isinstance(row, dict) or not required <= row.keys() or row.keys() - required - optional:
            raise ValueError("Invalid plugin tool fields")
        if any(not isinstance(row[key], str) or not row[key].strip() for key in required):
            raise ValueError("Tool identity fields must be nonempty strings")
        if not _IDENTIFIER.fullmatch(row["tool_id"]):
            raise ValueError("tool_id must use kebab-case")
        if not _MODULE.fullmatch(row["module_path"]) or not row["class_name"].isidentifier():
            raise ValueError("Entry point must be a Python module and class")
        for key in ("min_window_width", "min_window_height"):
            if key in row and (type(row[key]) is not int or not 1 <= row[key] <= 16384):
                raise ValueError("Window minimums must be integers from 1 to 16384")
        if "tool_version" in row and not isinstance(row["tool_version"], str):
            raise ValueError("tool_version must be a string")
        if "undo_supported" in row and type(row["undo_supported"]) is not bool:
            raise ValueError("undo_supported must be a boolean")
        from src.core.plugin_contracts import validate_contracts
        validate_contracts(row)
        aliases = {normalize(row["tool_id"]), normalize(row["display_name"])}
        if aliases & used:
            raise ValueError(f"Tool identity conflicts with an existing tool: {row['tool_id']}")
        used.update(aliases)
        entries.append(ToolManifestEntry(**row))
    for entry in entries:
        ToolManifestRegistry.register(entry)
    return entries
