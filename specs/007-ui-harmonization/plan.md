# Implementation Plan: UI Harmonization — Unified Look & Feel

**Branch**: `007-ui-harmonization` | **Date**: 2026-03-11 | **Spec**: [specs/007-ui-harmonization/spec.md](spec.md)
**Input**: [specs/007-ui-harmonization/spec.md](spec.md) + [research.md](research.md)

## Summary

Deliver a Unified Appearance Profile (UAP) system that gives every RFU tool window the same geometry, font, and working directory; enforce a verified menu contract across all tools; lock all package dependencies to declared versions in `requirements.txt`; and publish architecture documents describing frameworks, dependencies, and packaging style.

---

## Technical Context

**Language/Version**: Python 3.12 (`.venv312`)
**Primary Dependencies**: PyQt5 5.15.11, argon2-cffi 23.1.0, cryptography 44.0.2
**Storage**: SQLite via `PreferencesStore`; JSON fallback; `requirements.txt` for version lock
**Testing**: pytest 8.3.5, pytest-qt 4.4.0, pytest-cov 6.1.0
**Target Platform**: Windows-primary (pywin32), cross-platform paths via `pathlib.Path`
**Project Type**: Single project (all source under `src/`)
**Performance Goals**: UAP apply ≤ 50ms per window open; theme propagation to all open windows ≤ 500ms
**Constraints**: Menu contract tests run without a display (use `QApplication` with offscreen platform); no new pip packages introduced
**Scale/Scope**: ~30–40 tool window classes; 1 hub; 1 preferences store

---

## Constitution Check

### Principle V — Simplicity & Extensible Modularity

**UAP**: Implemented as a new preference category (`uap`) on the existing `PreferenceManager` — no new subsystem. Single responsibility: store and apply appearance settings.

**Menu contract**: Extended inside `MenuManager._create_view_menu()`. Tool contract enforced via `tool_interface_validator.py` pipeline (already exists). New dialogs go into `src/gui/dialogs/` which is the established location.

**Validation**: `FontPickerDialog` and `DirectoryPickerDialog` are single-responsibility, discoverable. Both registered with `ComponentGuardian`.

**Risk of violation**: NONE — this feature consolidates existing fragmentation rather than adding abstraction layers.

### Principle VI — User Preference Management & Personalization

UAP lives in preference category `uap` with namespaced keys. Profile objects are versioned JSON blobs. Export/import honoured via existing `portability.py`. Sensitive values: none (paths and fonts are not secrets). Migration: additive MINOR change — no breaking key renames.

**COMPLIANT** ✅

### Principle III — Test-Driven Quality

Menu contract tests (pytest-qt, offscreen) and dependency audit test are written before implementation. Coverage gate ≥ 85% maintained. UAP service has unit tests. No new functionality ships without a failing test that passes after implementation.

**COMPLIANT** ✅

### Principle IV — Performance & Scalability

UAP apply is a single `resize()` + `setFont()` + path assignment — O(1). Theme propagation via Qt signal bus is O(n open windows) — acceptable. No directory tree scans triggered at window open.

**COMPLIANT** ✅

---

## Project Structure

### Documentation (this feature)

```text
specs/007-ui-harmonization/
├── spec.md              ✅ done
├── research.md          ✅ done
├── plan.md              ← this file
├── data-model.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
│   ├── uap-preferences.md
│   ├── menu-contract.md
│   └── appearance-profile.md
└── tasks.md             ← Phase 2 output (/tasks command)
```

### Source Code Changes (repository root)

```text
src/
├── gui/
│   ├── dialogs/
│   │   ├── font_picker_dialog.py        NEW — shared FontPickerDialog
│   │   └── directory_picker_dialog.py   NEW — shared DirectoryPickerDialog
│   ├── menu_manager.py                  MODIFY — add Font… + Working Directory… to View menu
│   ├── settings_dialog.py               MODIFY — ensure Appearance tab covers full UAP
│   ├── standard_window.py               MODIFY — apply UAP on init; listen for UAP change signal
│   └── themes.py                        MODIFY — add signal bus for theme propagation to open windows
│
├── core/
│   └── preferences/
│       ├── uap/
│       │   ├── __init__.py              NEW
│       │   ├── models.py                NEW — AppearanceProfile, UAPSettings dataclasses
│       │   ├── service.py               NEW — UAPService (get, set, apply, profiles CRUD)
│       │   └── defaults.py              NEW — platform-aware factory defaults
│       └── manager.py                   MODIFY — add uap convenience methods
│
└── tabbed_hub.py                        MODIFY — Appearance settings panel wires to UAPService

tests/
├── contract/
│   └── gui/
│       └── test_menu_contract.py        NEW — verifies menu topology for every registered tool
├── unit/
│   ├── preferences/
│   │   └── test_uap_service.py          NEW — UAP CRUD, apply, defaults, persistence
│   └── gui/
│       ├── test_font_picker_dialog.py   NEW
│       └── test_directory_picker_dialog.py  NEW
└── integration/
    └── test_uap_propagation.py          NEW — UAP applied on StandardWindow init

scripts/
└── check_dependencies.py               NEW — compares requirements.txt vs pip list

docs/
└── architecture/
    ├── frameworks-and-dependencies.md   NEW — full dependency inventory
    └── packaging-style.md               NEW — venv conventions, requirements rules, onboarding
```

---

## Phase 0 — Research ✅ Complete

See [research.md](research.md). All NEEDS CLARIFICATION items resolved.

---

## Phase 1 — Contracts & Data Model

### 1.1 Contracts

#### `contracts/uap-preferences.md`
Defines the preference API contract for the `uap` category:
- `uap.mode` → `"last_used"` | `"predefined"` (string)
- `uap.active_profile_id` → UUID string or empty (predefined mode only)
- `uap.last_used_width` → integer ≥ 400
- `uap.last_used_height` → integer ≥ 300
- `uap.last_used_font_family` → non-empty string
- `uap.last_used_font_size` → integer in [6, 32]
- `uap.last_used_directory` → absolute path string (validated on read; falls back to home if invalid)
- `uap.profile:<uuid>` → JSON-serialized `AppearanceProfile` dict

#### `contracts/menu-contract.md`
Defines the required menu topology:
- Top-level order: `File (0)`, `Edit (1)`, `View (2)`, `Tools (3)`, `Help (4)`
- File actions (ordered): `open_file`, `save_file`, `save_as_file`, `—`, `import_data`, `export_data`, `—`, `show_preferences`, `—`, `exit`
- View actions (must include): `theme` (submenu), `font_picker`, `working_directory_picker`
- Help actions (must include): `about`
- Contract tested by `tests/contract/gui/test_menu_contract.py`

#### `contracts/appearance-profile.md`
JSON schema for a serialized `AppearanceProfile`:
```json
{
  "profile_id": "<uuid4>",
  "profile_name": "<string, 1-64 chars>",
  "is_default": false,
  "window_width": 1000,
  "window_height": 700,
  "font_family": "Segoe UI",
  "font_size": 10,
  "working_directory": "<absolute path or empty>",
  "created_at": "<ISO8601>",
  "updated_at": "<ISO8601>"
}
```

### 1.2 Data Model
See [data-model.md](data-model.md) for entity diagrams and preference schema definitions.

### 1.3 Quickstart
See [quickstart.md](quickstart.md) for developer setup and first-run verification steps.

---

## Complexity Tracking

| Risk | Likelihood | Mitigation |
|---|---|---|
| Tools that bypass `StandardWindow.__init__` won't receive UAP | Medium | `tool_interface_validator` audit catches missing base class |
| `QFont` availability on offscreen test platform | Low | `pytest-qt` with offscreen platform handles this; existing test suite proves it |
| Directory missing at startup | Low | `UAPService.resolve_directory()` falls back to `Path.home()` + logs warning |
| Predefined profile conflicts with tool min-size | Low | `UAPService.apply()` enforces `max(uap_width, tool.min_window_width)` |

---

## Progress Tracking

- [x] Phase 0: Research — 2026-03-11
- [x] Phase 1 contracts drafted — 2026-03-11
- [x] Phase 1 data model — 2026-03-11
- [x] Phase 1 quickstart — 2026-03-11
- [x] Phase 2: Tasks (`/tasks` command) — 2026-03-11
- [ ] Phase 3: Implementation
- [ ] Phase 4: Integration & Polish
