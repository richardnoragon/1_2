"""The reviewed capability matrix is the built-in tool inventory authority."""

from functools import lru_cache
import json
from pathlib import Path

MATRIX_PATH = Path(__file__).resolve().parents[2] / "docs/tool-capability-matrix.json"


@lru_cache(maxsize=1)
def load_inventory():
    """Read declarations without importing any tool code or promoting compliance."""
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    rows = matrix["tools"]
    if matrix["_meta"]["tool_count"] != len(rows):
        raise ValueError("Capability matrix tool_count does not match its entries")
    identities = {}
    for row in rows:
        for key in ("id", "display_name", "module_path", "class_name", "category"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Invalid tool inventory field: {key}")
        for alias in [row["id"], row["display_name"], *row.get("aliases", [])]:
            normalized = "".join(char for char in alias.lower() if char.isalnum())
            if normalized in identities and identities[normalized] != row["id"]:
                raise ValueError(f"Ambiguous tool alias: {alias}")
            identities[normalized] = row["id"]
    return matrix
