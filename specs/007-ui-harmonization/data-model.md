# Data Model: UI Harmonization

**Feature**: `007-ui-harmonization`
**Date**: 2026-03-11

---

## 1. Entity Relationship Overview

```
User (from identity layer)
 └─ has many ──▶ AppearanceProfile   (stored as uap.profile:<uuid> preference values)
 └─ has one  ──▶ UAPSettings         (stored as individual uap.* preference keys)

StandardWindow (runtime)
 └─ reads-on-open ──▶ UAPSettings / AppearanceProfile  (via UAPService)
 └─ writes-on-close ──▶ UAPSettings.last_used_*        (via UAPService.record_last_used)

MenuManager (runtime)
 └─ provides ──▶ FontPickerDialog     (one shared instance per window)
 └─ provides ──▶ DirectoryPickerDialog (one shared instance per window)

ToolManifest (static registry)
 └─ describes ──▶ StandardWindow subclasses (tool_id, min_width, min_height)
```

---

## 2. AppearanceProfile

Stored as a JSON-serialized string under preference key `uap.profile:<uuid4>`.

```python
@dataclass
class AppearanceProfile:
    profile_id: str          # UUID4 string
    profile_name: str        # 1–64 chars
    is_default: bool         # True for factory-default; at most one per user
    window_width: int        # px, ≥ 400
    window_height: int       # px, ≥ 300
    window_x: int            # screen x; -1 = use center/cascade default
    window_y: int            # screen y; -1 = use center/cascade default
    font_family: str         # e.g. "Segoe UI"
    font_size: int           # 6–32 pt
    working_directory: str   # absolute path, "" = use home
    created_at: str          # ISO 8601
    updated_at: str          # ISO 8601
```

---

## 3. UAPSettings

Runtime-readable aggregate of the user's current UAP state.  
Populated by `UAPService.load()` from individual `uap.*` preference keys.

```python
@dataclass
class UAPSettings:
    mode: str                     # "last_used" | "predefined"
    active_profile_id: str        # UUID4 or "" (last-used mode)
    last_used_width: int          # px
    last_used_height: int         # px
    last_used_x: int              # screen x; -1 = use center/cascade default
    last_used_y: int              # screen y; -1 = use center/cascade default
    last_used_font_family: str
    last_used_font_size: int      # pt
    last_used_directory: str      # absolute path
```

---

## 4. MenuContract (static validation only)

Not persisted. Used only by contract tests.

```python
@dataclass
class MenuContract:
    top_level_labels: list[str]      # ["File", "Edit", "View", "Tools", "Help"]
    file_required_action_ids: list[str]
    view_required_action_ids: list[str]
    help_required_action_ids: list[str]
```

---

## 5. ToolManifest Entry (existing, extended)

Existing tool manifest entries in `tabbed_hub.py` are extended with optional UAP override fields:

```python
@dataclass
class ToolManifestEntry:
    tool_id: str             # e.g. "duplicate-finder"
    display_name: str
    module_path: str         # e.g. "src.tools.analysis.duplicate_finder"
    class_name: str          # e.g. "DuplicateFinderApp"
    category: str            # e.g. "analysis"
    min_window_width: int    # default 400 — used by UAPService.apply()
    min_window_height: int   # default 300
    tool_version: str | None = None  # from module __version__; falls back to suite version if absent
```

---

## 6. Preference Key Layout

```
user_id: "richard"
preference_category: "uap"

Keys:
  mode                      → "last_used"
  active_profile_id         → ""
  last_used_width           → "1000"
  last_used_height          → "700"
  last_used_x               → "-1"
  last_used_y               → "-1"
  last_used_font_family     → "Segoe UI"
  last_used_font_size       → "10"
  last_used_directory       → "C:\\Projects"
  profile_schema_version    → "1"
  profile:<uuid4-A>         → '{"profile_id": "...", "profile_name": "Default", ...}'
  profile:<uuid4-B>         → '{"profile_id": "...", "profile_name": "Work", ...}'
```

---

## 7. DependencyRecord (documentation only)

Used in `docs/architecture/frameworks-and-dependencies.md`.

```
| Package | Pinned Version | Category | Role | Rationale |
```

Not stored in the preference system; lives in Markdown documentation.
