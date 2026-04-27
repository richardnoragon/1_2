# Contract: UAP Preferences API

**Contract ID**: `uap-preferences-v1`
**Feature**: `007-ui-harmonization`
**Owner**: `src/core/preferences/uap/service.py`
**Tested by**: `tests/contracts/gui/test_menu_contract.py`, `tests/unit/preferences/test_uap_service.py`

---

## Category Namespace

All UAP keys live under the `uap` category in `PreferenceManager`.
User-scoped: `preference_category = "uap"`, per active `user_id`.

---

## Keys and Types

| Key | Type | Default | Constraints |
|---|---|---|---|
| `mode` | string | `"last_used"` | Must be `"last_used"` or `"predefined"` |
| `active_profile_id` | string (UUID4) | `""` | Empty string in last-used mode; valid UUID4 in predefined mode |
| `last_used_width` | integer | `1000` | ≥ 400 |
| `last_used_height` | integer | `700` | ≥ 300 |
| `last_used_x` | integer | `-1` | ≥ -1; -1 means use center/cascade default |
| `last_used_y` | integer | `-1` | ≥ -1; -1 means use center/cascade default |
| `last_used_font_family` | string | platform default | Non-empty; validated against QFontDatabase on apply |
| `last_used_font_size` | integer | `10` | 6 ≤ size ≤ 32 |
| `last_used_directory` | string | `str(Path.home())` | Absolute path; falls back to home if path no longer exists. Affects `QFileDialog` starting path only; no `os.chdir()` side effects. |
| `profile:<uuid4>` | JSON string | — | Serialized `AppearanceProfile` (see appearance-profile.md) |

---

## Behaviour Contracts

### BC-001 — Read with missing key returns default
`UAPService.get(key)` MUST return the declared default if the key is absent from the store. It MUST NOT raise.

### BC-002 — Invalid directory falls back silently
When `last_used_directory` resolves to a path that does not exist or is not a directory, `UAPService.resolve_directory()` MUST return `Path.home()` and log a WARNING. The stored value MUST remain unchanged.

### BC-003 — Mode switch clears active_profile_id
When mode is set to `"last_used"`, `active_profile_id` MUST be cleared to `""`. When mode is set to `"predefined"`, `active_profile_id` MUST be set to a valid profile UUID before the mode write is committed.

### BC-004 — Font size clamped on write
`UAPService.set_font(family, size)` MUST clamp `size` to the inclusive range `[6, 32]` before calling `set_font_preferences()`. It MUST NOT raise an error for out-of-range `size`; instead it MUST coerce the value into the valid range. `set_font_preferences()` MUST persist only the font-related fields (`last_used_font_family`, `last_used_font_size`) and MUST NOT write geometry or directory fields.

> **Governance Annotation — BC-004 Corrected (N4 — Resolved 2026-04-26)**
> Earlier drafts referenced a legacy method `set_font_size(n)` that does not exist in the UAPService API. Font size clamping occurs in `set_font(family, size)` and persistence is delegated to `set_font_preferences()`. This aligns BC-004 with T025 and the incremental-write persistence model established by A2.

### BC-005 — apply() is idempotent
Calling `UAPService.apply(window)` twice on the same window MUST produce the same visual result. It MUST NOT accumulate font or geometry changes.

### BC-006 — last_used always updated regardless of mode
`StandardWindow.closeEvent()` MUST call `UAPService.save_last_used(width, height, x, y, font_family, font_size, directory)` to persist current geometry, font, and browse path **regardless of whether the current mode is `last_used` or `predefined`**. In predefined mode the values are silently persisted but not applied on next open (the active profile governs). No confirmation dialog or prompt is shown when switching modes.

The canonical method signature is:

```python
save_last_used(
    width: int,
    height: int,
    x: int,
    y: int,
    font_family: str,
    font_size: int,
    directory: str,
) -> None
```

This method MUST accept only primitive parameters and MUST NOT depend on Qt widget instances or require a `QMainWindow` object. Implementation MUST persist these values into `UAPSettings` / `AppearanceProfile` as defined in data-model §5.

> **Clarification (2026-04-25, I3)**: `save_last_used()` supersedes earlier references to `record_last_used(window)`. The Qt-object-based signature is removed. All tasks and tests MUST use `save_last_used(...)` as the canonical API. The mode only controls which values are *applied* on open, not whether they are *recorded* on close.

> **Normative Clarification — Full-State Write Semantics (A2):**
> `save_last_used()` is a full-state write and MUST only be invoked during window close (T032). It MUST NOT be called from incremental update paths such as `set_font()`.
> Incremental updates MUST use field-specific setters:
> - `set_font_preferences(font_family, font_size)` — updates `last_used_font_family` and `last_used_font_size` only
> - `set_geometry(width, height, x, y)` — updates geometry fields only (BC-006c)
> - `set_directory(path)` — updates directory field only (BC-006b)
>
> These methods MUST NOT write fields outside their own scope. Calling `save_last_used()` from an incremental update path creates a partial-state write that overwrites geometry and directory with stale values from the previous `closeEvent`.

### BC-007 — Font change propagates live to all open windows
When `UAPService.set_font(family, size)` is called (from any tool or hub), `ThemeManager.instance().uap_font_changed` MUST be emitted. All registered `StandardWindow` instances MUST update their font within **500ms**. This SLA is only enforced for **≤ 10 simultaneously open tool windows**; behaviour beyond this cap is undefined and not tested.

**Canonical signal source:** `ThemeManager` is the exclusive emitter of `uap_font_changed`. Implementations SHALL NOT use callback lists, observer arrays, or ad-hoc notification mechanisms. ThemeManager is a `QObject`-based singleton — signal emission requires calling `ThemeManager.instance().uap_font_changed.emit(family, size)`.

> **Governance Annotation — ThemeManager as Canonical Signal Source (P3-C01 — Resolved 2026-04-26)**
> Earlier implementations used `_theme_changed_callbacks` list for propagation. This is deprecated. All font propagation MUST flow through: `UAPService.set_font()` → `ThemeManager.instance().uap_font_changed.emit()` → `StandardWindow._on_uap_font_changed` → `setFont()` + `findChildren()` sweep.

### BC-008 — Geometry change propagates live to all open windows
When `UAPService.set_geometry(width, height, x, y)` is called, `ThemeManager.instance().uap_geometry_changed` MUST be emitted. All registered `StandardWindow` instances MUST resize and reposition within **500ms**. This SLA is only enforced for **≤ 10 simultaneously open tool windows**; behaviour beyond this cap is undefined and not tested.

**Canonical signal source:** `ThemeManager` is the exclusive emitter of `uap_geometry_changed`. No alternative propagation mechanisms are permitted. Signal emission requires `ThemeManager.instance().uap_geometry_changed.emit(x, y, w, h)`.

### BC-006b — set_directory: dedicated directory-persistence API
`UAPService.set_directory(path: str) -> None` MUST update only the last-used directory field in `UAPSettings`. It MUST NOT modify geometry or appearance fields. It MUST be used by any workflow that updates only the directory (e.g., `DirectoryPickerDialog` "Apply to all tools").

**Directory Update Semantics — Last-Write-Wins (U4):**
When multiple tools update the working directory concurrently, the system MUST apply last-write-wins semantics:
1. `set_directory(path)` performs a read-modify-write on `UAPSettings.directory`.
2. If two or more updates occur in close succession, the update whose write operation completes last MUST become the authoritative value.
3. No locking, queuing, or merge logic is required or permitted.
4. Tools MUST NOT assume that their write is exclusive.

This rule applies to T029 (`DirectoryPickerDialog`), any tool calling `set_directory()`, and any future directory-setting operations.

> **Governance Annotation — Directory Update Concurrency (U4):**
> FR-019 allows tools to update the working directory, but earlier drafts did not define behaviour when multiple tools update the directory concurrently.
> This annotation clarifies that the system uses **last-write-wins** semantics. This avoids the need for locking or coordination in a single-user desktop environment, ensures deterministic and testable behaviour, and prevents race-condition ambiguity.
> Future contributors MUST NOT introduce locking, queuing, or merge logic into `set_directory()` or any directory-setting workflow.

### BC-006c — set_geometry: geometry-only writer
`UAPService.set_geometry(width: int, height: int, x: int, y: int) -> None` MUST update only window geometry fields. It MUST NOT modify directory or appearance fields and MUST NOT be used by directory-related workflows.

> **Contract Integrity Rules (I4):** Geometry, directory, and appearance persistence MUST remain orthogonal. `save_last_used(...)` is the canonical full-state writer. `set_directory(...)` and `set_geometry(...)` are partial-state writers and MUST NOT overwrite fields outside their own scope.

### BC-009 — Window position default: center then cascade
When `last_used_x == -1` or `last_used_y == -1`, `UAPService.apply(window)` MUST center the window on the primary screen. If additional tool windows are opened in the same session, each subsequent window MUST be offset by (+20, +20) from the previously opened window (cascade placement).

---

## Platform-Aware Defaults

| Platform | Default font family |
|---|---|
| Windows | `"Segoe UI"` |
| macOS | `"Helvetica Neue"` |
| Linux | `"DejaVu Sans"` |

Resolved by `src/core/preferences/uap/defaults.py::get_default_font_family()`.
