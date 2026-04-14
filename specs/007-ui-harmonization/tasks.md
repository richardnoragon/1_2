# Tasks: UI Harmonization — Unified Look & Feel

**Feature**: `007-ui-harmonization`
**Date**: 2026-03-11
**Input**: [plan.md](plan.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md),
[contracts/uap-preferences.md](contracts/uap-preferences.md),
[contracts/menu-contract.md](contracts/menu-contract.md),
[contracts/appearance-profile.md](contracts/appearance-profile.md)
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

---

## Dependency Graph (summary)

```
T001 (structure)
  └─ T002 (UAP preference keys in manager)
       └─ T003 (AppearanceProfile / UAPSettings models)
            └─ T004 (UAPService)
                 └─ T005 (platform defaults)
                 └─ T010 (failing unit tests for UAPService)  ← TDD gate
       └─ T011 (FontPickerDialog)
       └─ T012 (DirectoryPickerDialog)
  └─ T006 (failing menu contract tests)                       ← TDD gate
  └─ T007 (failing About dialog content test)                 ← TDD gate
  └─ T008 (failing UAP propagation integration test)          ← TDD gate
  └─ T009 (dependency audit script)

T010 passes → T013 (UAPService implementation)
T010 passes → T014 (StandardWindow.apply_uap)
T006 passes → T015 (MenuManager View menu additions)
T007 passes → T016 (About dialog version fields)
T008 passes → T017 (hub Appearance panel wiring)
T011+T012 done → T015 (View menu actions open dialogs)
T013+T014+T015+T016+T017 done → T018 (theme propagation signal)
T018 done → T019 (integration: UAP across two windows)
T019 done → T020 (tool audit: tools not subclassing StandardWindow)
T020 done → T021 (coverage gate)
T009 done → T022 (docs: frameworks-and-dependencies.md)
T022 done → T023 (docs: packaging-style.md)
```

---

## Phase 3.1 — Setup

- [ ] **T001** Create missing directories:
  `src/core/preferences/uap/`,
  `src/gui/dialogs/` (if absent),
  `tests/contract/gui/`,
  `tests/unit/preferences/`,
  `tests/unit/gui/`,
  `tests/integration/`,
  `docs/architecture/` (if absent)

- [ ] **T002** [P] Register `uap` preference category in `src/core/preferences/manager.py`:
  add convenience method stubs `get_uap_settings()` and `save_uap_settings()`.

---

## Phase 3.2 — Tests First (TDD) ⚠️  COMPLETE BEFORE 3.3

> Every test below MUST be written in full and MUST FAIL before any
> corresponding implementation is written.

- [ ] **T003** [P] Write failing unit tests for `AppearanceProfile` and `UAPSettings` dataclasses
  in `tests/unit/preferences/test_uap_models.py`:
  - Serialization round-trip (to/from JSON)
  - Field validation (width ≥ 400, height ≥ 300, font size 6–32)
  - `is_default` uniqueness invariant (at most one per user)

- [ ] **T004** [P] Write failing unit tests for `UAPService` in
  `tests/unit/preferences/test_uap_service.py`:
  - `load()` returns factory defaults when no UAP keys exist in store
  - `save_last_used(width, height, font_family, font_size, directory)` persists keys
  - `get_active_settings()` returns last-used or active profile depending on mode
  - `apply(window)` calls `window.resize()`, `window.setFont()`, sets browse path
  - `resolve_directory(path)` returns `Path.home()` when path does not exist
  - Profile CRUD: create, get, rename, duplicate, delete (prevent deleting last profile)

- [ ] **T005** [P] Write failing unit tests for platform-aware defaults in
  `tests/unit/preferences/test_uap_defaults.py`:
  - Windows → `"Segoe UI"`, macOS → `"Helvetica Neue"`, Linux → `"DejaVu Sans"`
  - Default size 1000 × 700, font size 10

- [ ] **T006** [P] Write failing menu contract tests in
  `tests/contract/gui/test_menu_contract.py`:
  - For every class listed in `ToolManifest` (or discovered via
    `src.core.tool_interface_validator`):
    - Menu bar present
    - Top-level labels are exactly `["File", "Edit", "View", "Tools", "Help"]` in that order
    - File menu contains actions `open_file`, `save_file`, `save_as_file`,
      `import_data`, `export_data`, `show_preferences`, `exit`
    - View menu contains actions `theme`, `font_picker`, `working_directory_picker`
    - Help menu's last action is `about`
  - Use `pytest-qt` with `qtbot` and `QApplication` on offscreen platform.

- [ ] **T007** [P] Write failing About dialog content test in
  `tests/contract/gui/test_about_dialog.py`:
  - Dialog displays tool name, RFU suite version, Python version,
    PyQt5 version (`PYQT_VERSION_STR`), Qt version (`QT_VERSION_STR`)

- [ ] **T008** [P] Write failing integration test for UAP propagation in
  `tests/integration/test_uap_propagation.py`:
  - Launch a minimal `StandardWindow` subclass → verify geometry matches UAP defaults
  - Save new font via `UAPService` → open second window → verify same font applied
  - Save last-used directory → open third window → verify browse root
  - Verify predefined profile overrides last-used values

- [ ] **T009** [P] Write dependency audit script `scripts/check_dependencies.py`:
  - Parse `requirements.txt` (skip comment lines and conditionals)
  - Compare against `pip list --format=json` output
  - Print mismatches with INSTALLED vs REQUIRED versions
  - Exit code 0 if all match; exit code 1 on any mismatch
  - Add `tests/unit/test_check_dependencies.py` that mocks pip output and
    asserts correct exit codes

---

## Phase 3.3 — Core Implementation  (ONLY after all Phase 3.2 tests are FAILING)

- [ ] **T010** [P] Create `src/core/preferences/uap/__init__.py` (empty, exposes public API)

- [ ] **T011** [P] Create `src/core/preferences/uap/defaults.py`:
  - `get_platform_font_family() -> str` — Segoe UI / Helvetica Neue / DejaVu Sans
  - `FACTORY_DEFAULTS: dict` — width=1000, height=700, font_size=10, mode="last_used"

- [ ] **T012** [P] Create `src/core/preferences/uap/models.py`:
  - `@dataclass class AppearanceProfile` (fields per data-model.md §2)
  - `@dataclass class UAPSettings` (fields per data-model.md §3)
  - `AppearanceProfile.to_json() / from_json()` serialization
  - Field validators via `__post_init__`

- [ ] **T013** Create `src/core/preferences/uap/service.py` — `UAPService`:
  - `load() -> UAPSettings`
  - `save_last_used(width, height, font_family, font_size, directory) -> None`
  - `get_active_settings() -> UAPSettings | AppearanceProfile`
  - `apply(window: QMainWindow) -> None`
  - `resolve_directory(path: str) -> Path` (fallback to home + status-bar warning)
  - Profile CRUD: `create_profile`, `get_profile`, `list_profiles`,
    `rename_profile`, `duplicate_profile`, `delete_profile`, `set_active_profile`

- [ ] **T014** Modify `src/core/preferences/manager.py` — implement `get_uap_settings()`
  and `save_uap_settings()` stubs added in T002.

- [ ] **T015** [P] Create `src/gui/dialogs/font_picker_dialog.py` — `FontPickerDialog`:
  - Font family list (proportional and monospace, filtered via `QFontDatabase`)
  - Size spinner (6–32pt)
  - Live preview label
  - OK / Cancel — on OK: `window.setFont(QFont(family, size))` + `UAPService.save_last_used()`

- [ ] **T016** [P] Create `src/gui/dialogs/directory_picker_dialog.py` — `DirectoryPickerDialog`:
  - Current path display (read-only)
  - Browse button → `QFileDialog.getExistingDirectory`
  - Checkbox: "Apply to all tools (update profile)"
  - OK / Cancel — on OK: sets window browse root + optionally calls
    `UAPService.save_last_used()` for directory

- [ ] **T017** Modify `src/gui/menu_manager.py` — add to `_create_view_menu()`:
  - `font_picker` action → opens `FontPickerDialog`
  - `working_directory_picker` action → opens `DirectoryPickerDialog`

- [ ] **T018** Modify `src/gui/standard_window.py`:
  - In `__init__`: call `UAPService().apply(self)` after `setup_ui()`
  - In `closeEvent`: call `UAPService().save_last_used(...)` with current geometry, font, browse path
  - Connect to `ThemeManager` signal bus for live theme propagation

- [ ] **T019** Modify `src/gui/settings_dialog.py` — Appearance tab:
  - Profile mode selector (radio: Last Used / Predefined)
  - Window width + height spinboxes
  - Font family combo + size spinner
  - Working directory field + Browse button
  - Profile list (for predefined mode): New, Rename, Duplicate, Delete, Set Active

- [ ] **T020** Modify `src/rfu/hub.py` (or `tabbed_hub.py`):
  - Add Appearance settings panel that wires to `UAPService`
  - Emit UAP change signal so all open windows refresh

- [ ] **T021** Modify `src/gui/themes.py`:
  - Add `ThemeManager.changed` signal (if not already present)
  - Broadcast to all registered `StandardWindow` instances via weak-reference list
  - Propagation target: ≤ 500ms for ≤ 40 open windows

- [ ] **T022** Update Help → About action in `src/gui/menu_manager.py`:
  - About dialog box displays tool name, suite version (`src/__version__.py`),
    Python version, `PYQT_VERSION_STR`, `QT_VERSION_STR`

---

## Phase 3.4 — Integration & Audit

- [ ] **T023** [P] Run `tool_interface_validator` audit and list every tool class that does
  NOT subclass `StandardWindow` or `SafeStandardWindow`. For each:
  - If fixable: update the class to subclass `StandardWindow`
  - If it cannot (e.g., modal dialog fixed-size): add a `ToolManifest` entry with
    `min_window_width` / `min_window_height` and a `uap_exempt: True` flag with
    documented reason

- [ ] **T024** [P] Create `docs/architecture/frameworks-and-dependencies.md`
  (full dependency inventory per FR-014; see template below).

- [ ] **T025** [P] Create `docs/architecture/packaging-style.md`
  (packaging conventions per FR-015; see template below).

- [ ] **T026** Write failing test `tests/unit/gui/test_font_picker_dialog.py`:
  - Dialog opens without crashing (offscreen)
  - OK propagates selected font to mock window
  - Cancel leaves window font unchanged

- [ ] **T027** [P] Write failing test `tests/unit/gui/test_directory_picker_dialog.py`:
  - Dialog opens without crashing
  - Checkbox state controls whether `UAPService.save_last_used` is called
  - Non-existent path shows error

---

## Phase 3.5 — Polish & Coverage Gate

- [ ] **T028** Run full test suite and confirm ≥ 85% line coverage:
  ```powershell
  python -m pytest tests/ --cov=src --cov-report=term-missing -v
  ```
  Fix any uncovered lines in new modules (not existing code).

- [ ] **T029** Run dependency audit script and confirm exit code 0:
  ```powershell
  python scripts/check_dependencies.py
  ```

- [ ] **T030** Manual smoke test per quickstart.md §Verifying UAP Manually:
  - Launch hub, open three different tools, confirm same window size, font, directory
  - Change font in one tool, open fourth tool, confirm font propagated
  - Switch to predefined profile, confirm all new windows use profile values

- [ ] **T031** Update `specs/007-ui-harmonization/plan.md` progress tracking:
  mark Phase 3 and Phase 4 complete.

---

## Parallel Execution Guide

Tasks marked **[P]** have no shared-file dependencies and can be worked on
simultaneously by multiple developers or agent turns:

| Parallel Slot A | Parallel Slot B | Parallel Slot C |
|---|---|---|
| T003 (model tests) | T004 (service tests) | T005 (defaults tests) |
| T006 (menu contract tests) | T007 (about tests) | T008 (propagation tests) |
| T011 (defaults.py) | T012 (models.py) | T009 (check_dependencies.py) |
| T015 (FontPickerDialog) | T016 (DirectoryPickerDialog) | T026/T027 (dialog tests) |
| T023 (tool audit) | T024 (frameworks doc) | T025 (packaging doc) |

Sequential dependencies MUST be respected:
- T013 (UAPService) requires T012 (models) and T011 (defaults) complete
- T018 (StandardWindow) requires T013 and T015 and T016 complete
- T020 (hub wiring) requires T013 complete
- T028 (coverage gate) requires all implementation tasks complete
