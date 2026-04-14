# Contract: UAP Preferences API

**Contract ID**: `uap-preferences-v1`
**Feature**: `007-ui-harmonization`
**Owner**: `src/core/preferences/uap/service.py`
**Tested by**: `tests/contract/gui/test_menu_contract.py`, `tests/unit/preferences/test_uap_service.py`

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
`UAPService.set_font_size(n)` MUST clamp `n` to [6, 32] before persisting. It MUST NOT raise for out-of-range input.

### BC-005 — apply() is idempotent
Calling `UAPService.apply(window)` twice on the same window MUST produce the same visual result. It MUST NOT accumulate font or geometry changes.

### BC-006 — last_used updated on window close
`StandardWindow.closeEvent()` MUST call `UAPService.record_last_used(window)` to persist current geometry, font, and browse path before the window is destroyed (last-used mode only).

### BC-007 — Font change propagates live to all open windows
When `UAPService.set_font(family, size)` is called (from any tool or hub), a `uap_font_changed` signal MUST be emitted on the shared signal bus. All registered `StandardWindow` instances MUST update their font within 500 ms.

### BC-008 — Geometry change propagates live to all open windows
When `UAPService.set_geometry(width, height, x, y)` is called, a `uap_geometry_changed` signal MUST be emitted. All registered `StandardWindow` instances MUST resize and reposition within 500 ms.

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
