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
 └─ writes-on-close ──▶ UAPSettings.last_used_*        (via UAPService.save_last_used)

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
    profile_schema_version: int = 2  # per-profile schema version (N1)
    is_user_created: bool = False    # False for system-seeded profiles (N2)
```

---

## 3. UAPSettings

Runtime-readable aggregate of the user's current UAP state.  
Populated by `UAPService.load()` from individual `uap.*` preference keys.

> **Clarification (2026-04-25)**: `last_used_*` values are updated unconditionally on every window close, regardless of `mode`. In `predefined` mode the hub applies the active profile on open but continues to silently record the user's actual usage in `last_used_*`. No prompt is shown on mode switch.

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

## 5. ToolManifest Entry (P3-H01 — Resolved 2026-04-26: created from scratch)

> **`ToolManifestEntry` and `ToolManifestRegistry` do not pre-exist in the codebase. T003 SHALL create both from scratch in `src/core/tool_manifest.py`.** Earlier wording that referred to "extending" entries in `src/rfu/hub.py` is superseded. Additionally, `src/rfu/hub.py` is NOT a GUI hub (see P3-H02 — Resolved 2026-04-26); the canonical GUI hub is `src/tabbed_hub.py`.

**Canonical file:** `src/core/tool_manifest.py`

> **Data-model boundary (I2):** Window position persistence is user-specific and MUST be stored only in `AppearanceProfile` / `UAPSettings`. `ToolManifest` MUST NOT contain per-user window state such as `window_x` or `window_y`.

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
  profile:<uuid4-A>         → '{"profile_id": "...", "profile_name": "Default", ..., "profile_schema_version": 2}'
  profile:<uuid4-B>         → '{"profile_id": "...", "profile_name": "Work", ..., "profile_schema_version": 2}'
```

> **Governance Annotation — `profile_schema_version` removed from top-level keys (N1 — Resolved 2026-04-26)**
> Earlier drafts listed `profile_schema_version` as a top-level `uap.*` key alongside `mode`, `active_profile_id`, etc.
>
> Per the N1 governance decision (Option A), `profile_schema_version` is stored **inside each AppearanceProfile JSON blob**, not as a top-level key.
>
> No top-level `uap.*` key exists for profile schema version. The version is serialized as a required field within the `profile:<uuid>` JSON value (see `contracts/appearance-profile.md`).
>
> Schema versioning is a *per-profile* concern. Each AppearanceProfile blob carries its own `profile_schema_version` integer, enabling independent migration of individual profiles without global version coupling.

---

## 7. DependencyRecord (documentation only)

Used in `docs/architecture/frameworks-and-dependencies.md`.

```
| Package | Pinned Version | Category | Role | Rationale |
```

Not stored in the preference system; lives in Markdown documentation.
