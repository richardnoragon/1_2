# Tasks: UI Harmonization — Unified Look & Feel

**Feature**: `007-ui-harmonization`
**Date**: 2026-04-25 (regenerated — incorporates 5 clarifications from 2026-04-25)

## UI / Preferences / Documentation Cluster Status

This task file is the repo-authoritative tracker for the UI/preferences/documentation cluster already represented in the active project specs. It is intentionally scoped to the harmonization and preferences workstreams rather than the broader, unrelated backlog. The implementation focus remains on appearance preferences, menu contracts, and documentation traceability across the tracker, operations runbook, and release notes.

- Primary spec anchors: `specs/004-preferences-framework/*`, `specs/007-ui-harmonization/*`
- Documentation focus: `docs/operations/preferences_portability_runbook.md`, `docs/ui-ux-harmonization/`, `docs/release_notes/preferences_framework_release.md`
- Scope boundary: UI/preferences/docs cluster only; no unrelated issue expansion beyond the existing spec-set
**Input**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md),
[quickstart.md](quickstart.md), [research.md](research.md),
[contracts/uap-preferences.md](contracts/uap-preferences.md),
[contracts/menu-contract.md](contracts/menu-contract.md),
[contracts/appearance-profile.md](contracts/appearance-profile.md)
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Clarifications applied**: C1 (phase scope), C2 (FR-024 disabled actions), C3 (10-window SLA cap),
C4 (last_used silent in predefined mode), C5 (ToolManifest-only contract tests)
---

## User Story Map

| ID   | Area | Spec Scenarios | Key FRs |
|------|------|----------------|---------|
| US1  | Unified Appearance Profile (UAP) | 1-5 | FR-001 to FR-007, FR-009 to FR-011, FR-018, FR-019, FR-021 to FR-023, FR-025, FR-026 |
| US2  | Menu Structure Contract | 6-10 | FR-008, FR-016, FR-017, FR-020, FR-024 |
| US3  | Dependency Consistency | 11-12 | FR-012, FR-013 |
| US4  | Framework & Packaging Docs | 13-14 | FR-014, FR-015 |

---

## Dependency Graph

```
T001 (dirs)
  T002 (manager.py uap stubs) <- T001
  T003 (ToolManifest min_window_width/height) <- T001
  T004-T012 (TDD tests, all parallel) <- T001

T013-T015 [P] (uap package skeleton + AppearanceProfile model)
  T016 (to_json/from_json) <- T015
    T017 (UAPSettings) <- T016
      T018 (UAPService.load) <- T017, T002
        T019 (save_last_used) <- T018
        T020 (get_active_settings) <- T018
        T021 (apply) <- T018
        T022 (resolve_directory) <- T018
        T023 (place_window) <- T018
        T024 (profile CRUD) <- T018
        T025 (signal emission) <- T018
        T026 (import_profile) <- T018

T027 (manager.py implement stubs) <- T018

T028 [P] (FontPickerDialog)
T029 [P] (DirectoryPickerDialog)
T030 (UAPAppearanceWidget) <- T028, T029

T031 (StandardWindow.__init__) <- T021, T023
T032 (StandardWindow.closeEvent) <- T019
T033 (StandardWindow signals) <- T025
T034 (settings_dialog Appearance tab) <- T030
T035 (settings_dialog PreferencesDialog) <- T030
T036 (hub.py Appearance tab) <- T030, T024

T037-T040 (menu_manager.py, sequential)
T041 (tool audit) <- T037-T040
T042-T043 (themes.py, sequential)

T044 [P] (requirements.txt audit)
T045 (check_dependencies.py) <- T012 tests
T046 [P] (frameworks doc)
T047 [P] (packaging doc)

T048-T052 (Polish) <- all implementation tasks
```

---

## Phase 1: Setup

- [x] T001 Create missing directories: `src/core/preferences/uap/`, `tests/contracts/gui/`, `tests/unit/preferences/`, `tests/unit/gui/`, `docs/architecture/` (create only those that are absent)

- [x] T002 Add `uap` preference-category stubs to `src/core/preferences/manager.py`: method signatures `get_uap_settings() -> UAPSettings` and `save_uap_settings(settings: UAPSettings) -> None` with bodies `raise NotImplementedError`

- [x] T003 [P3-H01 — Resolved 2026-04-26] Create `ToolManifestEntry` dataclass and `ToolManifestRegistry` in `src/core/tool_manifest.py`:

  > **There is nothing to verify or extend. `ToolManifest` does not exist anywhere in the codebase. T003 MUST create it from scratch.**

  **T003-A — Create the dataclass**
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
      tool_version: str | None = None
  ```
  > **Data-model boundary (I2):** Window position fields (`window_x`, `window_y`) MUST NOT be added to `ToolManifestEntry`. Those are per-user state and belong exclusively in `AppearanceProfile` / `UAPSettings`.

  **T003-B — Create the registry and seed entries**
  ```python
  class ToolManifestRegistry:
      _entries: dict = {}

      @classmethod
      def register(cls, entry: ToolManifestEntry) -> None:
          cls._entries[entry.tool_id] = entry

      @classmethod
      def get(cls, tool_id: str) -> ToolManifestEntry | None:
          return cls._entries.get(tool_id)

      @classmethod
      def all(cls) -> list[ToolManifestEntry]:
          return list(cls._entries.values())
  ```
  Seed at least **two** canonical entries with non-zero `min_window_width` and `min_window_height`:
  ```python
  ToolManifestRegistry.register(ToolManifestEntry(
      tool_id="tool.alpha", display_name="Alpha Tool",
      module_path="src.tools.alpha", class_name="AlphaGUI",
      category="analysis", min_window_width=480, min_window_height=320,
  ))
  ToolManifestRegistry.register(ToolManifestEntry(
      tool_id="tool.beta", display_name="Beta Tool",
      module_path="src.tools.beta", class_name="BetaGUI",
      category="analysis", min_window_width=600, min_window_height=400,
  ))
  ```
  These entries are used by T041 for audit validation. T041 MUST NOT seed or mutate manifest data.

  > **Governance Annotation — ToolManifest Creation Mandate (P3-H01 — Resolved 2026-04-26):**
  > The ToolManifest does not pre-exist in the codebase. All "verify fields if absent" language from earlier drafts is hereby superseded. T003 MUST create `ToolManifestEntry` and `ToolManifestRegistry` from scratch. T007, T041, and T048 all depend on this registry — none may run before T003 is complete. Any audit against an empty manifest is a blocking issue.

---

## Phase 2: TDD Gate - All Tests MUST Be Written and MUST FAIL Before Phase 3

> WARNING CRITICAL: Write every test below in full. Run the suite and confirm each test FAILS. No implementation code until the entire Phase 2 block is red.

- [x] T004 [P] Write failing unit tests for `AppearanceProfile` and `UAPSettings` in `tests/unit/preferences/test_uap_models.py`:
  - `AppearanceProfile`: instantiation with required fields; `to_json()` / `from_json()` round-trip; field validation (`window_width >= 400`, `window_height >= 300`, `font_size` in [6, 32], `window_x >= -1`, `window_y >= -1`); `is_default` at-most-one invariant (INV-001)
  - `UAPSettings`: all defaults match `FACTORY_DEFAULTS`; `mode` accepts only `"last_used"` and `"predefined"`
  - **Mixed-sentinel invariant (U5):** Creating an `AppearanceProfile` with `window_x >= 0` and `window_y == -1`, or with `window_x == -1` and `window_y >= 0`, MUST raise `ValueError` — mixed sentinel values violate INV-006. Test MUST cover both directions of the violation.
  - **Schema version presence (G2):** Serializing a valid `AppearanceProfile` via `to_json()` MUST include `"profile_schema_version": <int>` in the output JSON. Deserializing via `from_json()` MUST preserve the version number exactly as stored. No profile MUST be serialized without a schema version.
  - **v1→v2 migration (G2):** A v1 profile JSON (missing any v2-only fields) passed through the migration logic MUST produce a profile with `profile_schema_version == 2`, all v2 fields populated with the defaults defined in the migration table, all v1 fields preserved unchanged, and no fields introduced that are not defined in the migration table.
  - **Factory-default round-trip (P3-H04 — Resolved 2026-04-26):** A round-trip test (`to_json()` / `from_json()`) for the factory-default profile MUST pass. The test SHALL NOT assert UUID4 format for `profile_id`. The schema allows `"factory_default"` via `oneOf`; any validator that rejects it is a blocking issue.

  > **Governance Annotation — Mixed-Sentinel Invariant Enforcement (U5):**
  > INV-006 requires that `window_x` and `window_y` are either both `-1` (sentinel / default placement) or both non-negative (explicit position). Earlier drafts did not include a test for the mixed case (e.g., `x=100, y=-1`), allowing invalid geometry to pass model validation undetected.
  > T004 MUST include a `ValueError`-expecting test for both directions of the mixed-sentinel violation. This ensures the invariant is enforced at the model layer so that invalid profiles cannot be persisted, migrated, or applied to a tool window.

  > **Governance Annotation — Schema Version Enforcement (G2):**
  > The migration table defines `profile_schema_version`, but earlier drafts did not include tests verifying its presence in serialized output or exercising v1→v2 migration. Schema versioning is a first-class contract requirement, not a convenience field.
  > T004 MUST assert that `profile_schema_version` is present in every serialized profile and MUST include a v1→v2 migration test that verifies the exact field transformations defined in the migration table. This prevents silent schema drift, ensures forward-compatibility, and maintains a coherent migration history.

- [x] T005 [P] Write failing unit tests for `UAPService` in `tests/unit/preferences/test_uap_service.py`:
  > **Canonical test surface (I3):** T005 is the authoritative test for the `UAPService` persistence API. All tests MUST use `save_last_used(width, height, x, y, font_family, font_size, directory)` — no Qt-object-based variant.
  - `load()` returns factory defaults when no `uap` keys exist in store
  - `save_last_used()` writes all seven `last_used_*` keys unconditionally regardless of `mode` (BC-006, C4)
  - `get_active_settings()` returns last-used values when `mode == "last_used"`; returns `AppearanceProfile` when `mode == "predefined"`
  - `apply(window)` calls `window.resize()`, `window.setFont()`, sets browse path; clamps to `max(uap_value, tool.min_width/height)`
  - `resolve_directory(path)` returns `Path.home()` for non-existent path; returns input path when it exists
  - `place_window(window, open_windows=[])` centres when coords are `(-1, -1)` and no other windows open; cascades (+20, +20) when one window already open
  - Profile CRUD: create, get, list, rename, duplicate, set_active; `delete_profile` blocks deletion of last profile and factory default (INV-002)
  - `set_font()` clamps size to [6, 32] (BC-004); switching to `"last_used"` clears `active_profile_id` (BC-003)
  - **`set_font_preferences()` isolation (N5):** `set_font_preferences(family, size)` MUST write only `last_used_font_family` and `last_used_font_size`; MUST NOT mutate `last_used_width`, `last_used_height`, `last_used_x`, `last_used_y`, or `last_used_directory`. Test MUST assert that all geometry and directory fields remain unchanged after the call.

  > **Governance Annotation — `set_font_preferences()` Isolation Test Required (N5 — Resolved 2026-04-26)**
  > A2 introduced `set_font_preferences()` as the canonical font-only persistence method. Earlier drafts of T005 did not include a test for this method, leaving its isolation invariant unverified. T005 MUST test that `set_font_preferences()` writes only font fields and does not modify geometry or directory. This ensures consistency with the persistence model defined in BC-006 and T025/T032.

- [x] T006 [P] Write failing unit tests for platform-aware defaults in `tests/unit/preferences/test_uap_defaults.py`:
  - `get_platform_font_family()` returns `"Segoe UI"` on Windows, `"Helvetica Neue"` on macOS, `"DejaVu Sans"` on Linux
  - `FACTORY_DEFAULTS` has `width=1000`, `height=700`, `font_size=10`, `mode="last_used"`, `window_x=-1`, `window_y=-1`

- [x] T007 [P] Write failing menu-contract tests in `tests/contracts/gui/test_menu_contract.py`:
  > **Prerequisite: T003 MUST be complete.** `ToolManifestRegistry` must exist and be populated before T007 runs.
  > **Anti-vacuity rule:** T007 SHALL fail (not pass) if `ToolManifestRegistry.all()` returns zero entries. A passing result against an empty registry is a governance illusion — zero tools validated is zero compliance evidence, not universal compliance.
  - Source of tools: **`ToolManifestRegistry.all()` only, no module scanning** (C5, FR-016)
  - For each registered tool class: instantiate with `qtbot` on offscreen platform; assert menu bar present; Phase-1 required menus `{"File", "Edit", "View", "Tools", "Help"}` MUST be a **subset** of the tool's actual top-level labels (use `assert required.issubset(actual_labels)`) — tests MUST NOT assert `len(menus) == 5` or any fixed count (C1, extensible to 7-menu constitution §7.2)
  - File menu: all standard action slots present; **inapplicable** (disabled) actions have their **generic label unchanged** (MUST NOT be renamed); **applicable** (enabled) actions MAY carry a tool-relevant label — contract tests assert the slot is present and enabled, not the specific label text (FR-024)
  - View menu: contains `theme` submenu, `font_picker` action, `working_directory_picker` action
  - Help menu: last action is `about`
  - Edit and Tools menus: present but contents NOT validated

- [x] T008 [P] Write failing About-dialog content test in `tests/contracts/gui/test_about_dialog.py`:
  - About dialog shows: tool name, suite version (from `APP_VERSION` in `src/core/constants.py`), tool `__version__` (falls back to suite version when absent), Python version (`sys.version`), `PYQT_VERSION_STR`, `QT_VERSION_STR`

- [x] T009 [P] Write failing UAP propagation integration test in `tests/integration/test_uap_propagation.py`:
  - Minimal `StandardWindow` subclass opens at UAP defaults; `resize()` and `setFont()` called with correct values
  - Font change via `UAPService.set_font()` propagates to a second already-open window within 500ms (capped at <=10 windows) (C3, BC-007)
  - Directory change inherited by subsequently opened window (last-used mode)
  - **Predefined-mode scenario (C4, BC-006)**: switch to predefined; open window (profile applied); close window; assert all `last_used_*` keys updated in store despite predefined mode
  - Cascade placement: two windows with (-1,-1) coords; second window position = first window pos + (20, 20) (FR-023)
  - `resolve_directory()` fallback: non-existent stored dir; window browse root equals `Path.home()`
  - **Full-widget font propagation (U1):** After `UAPService.set_font()`, assert that `QLabel`, `QMenuBar`, `QToolBar`, `QTableView`, and `QPushButton` instances inside the window all report the updated font via `.font()`. MUST NOT rely solely on top-level `window.font()`.
  - **Custom widget compliance (U1):** Any custom widget with a manually-set font MUST connect to `uap_font_changed` and update its internal font; test that such a widget receives the signal and applies the font.

- [x] T010 [P] Write failing `FontPickerDialog` tests in `tests/unit/gui/test_font_picker_dialog.py`:
  - Dialog opens without crash on offscreen platform
  - Font family list is non-empty (populated from `QFontDatabase`)
  - Size spinner range is exactly 6-32
  - OK propagates `(family, size)` to `window.setFont()` mock
  - Live preview label text changes on every family/size selection change
  - Cancel leaves window font unchanged

- [x] T011 [P] Write failing `DirectoryPickerDialog` tests in `tests/unit/gui/test_directory_picker_dialog.py`:
  - Dialog opens without crash on offscreen platform
  - Current browse root shown in read-only field
  - OK with "Apply to all tools" checked calls `UAPService.set_directory(new_path)` (BC-006b, I4); MUST NOT call `set_geometry()` or `save_last_used()` for directory-only updates
  - OK with "Apply to all tools" unchecked does NOT call `set_directory()`; browse root updated session-scoped only
  - Non-existent path selected: inline error shown; dialog not closed

- [x] T012 [P] Write failing dependency-audit tests in `tests/unit/test_check_dependencies.py`:
  - All installed versions match `requirements.txt` -> exit code 0
  - One package version mismatches -> exit code 1; MISMATCH line printed
  - `--platform win32` flag on Linux: `; sys_platform=="linux"` lines skipped; `; sys_platform=="win32"` lines evaluated
  - Blank lines and `#` comment lines skipped without error
  - Installed package not in `requirements.txt` -> UNDECLARED line printed

---

## Phase 3: UAP Core (US1) - Stories 1-5

> Prerequisite: All Phase 2 tests written and FAIL.

- [x] T013 [P] [US1] Create `src/core/preferences/uap/__init__.py` - expose: `from .service import UAPService`, `from .models import AppearanceProfile, UAPSettings`, `from .defaults import FACTORY_DEFAULTS, get_platform_font_family`

- [x] T014 [P] [US1] Create `src/core/preferences/uap/defaults.py`:
  - `get_platform_font_family() -> str`: `"Segoe UI"` (win32), `"Helvetica Neue"` (darwin), `"DejaVu Sans"` (other) via `sys.platform`
  - `FACTORY_DEFAULTS: dict` with keys `width`, `height`, `font_size`, `mode`, `window_x`, `window_y`, `profile_schema_version` (value: `2` — current AppearanceProfile schema version per N1 governance decision)

- [x] T015 [P] [US1] Create `src/core/preferences/uap/models.py` - `AppearanceProfile` dataclass:
  - All fields from `contracts/appearance-profile.md` including `window_x: int = -1` and `window_y: int = -1`
  - `__post_init__` validates: `window_width >= 400`, `window_height >= 300`, `font_size` in [6, 32], `window_x >= -1`, `window_y >= -1`; raises `ValueError` on violation
  - **INV-006 mixed-sentinel invariant (N3):** If `window_x >= 0` and `window_y == -1`, or `window_x == -1` and `window_y >= 0`, `__post_init__` MUST raise `ValueError("mixed sentinel: window_x and window_y must both be -1 or both be non-negative")`. Both directions of the violation MUST be enforced.

  > **Governance Annotation — INV-006 Must Be Enforced in `__post_init__` (N3 — Resolved 2026-04-26)**
  > INV-006 defines a cross-field invariant for window geometry. Earlier drafts of T015 validated only individual fields and omitted the mixed-sentinel check, allowing invalid profiles to be constructed. T004 now includes `ValueError`-expecting tests for both mixed-sentinel directions. T015 `__post_init__` MUST enforce INV-006 so that invalid geometry cannot enter the system. T004 tests rely on this enforcement.

- [x] T016 [US1] Add `AppearanceProfile.to_json() -> str` and `AppearanceProfile.from_json(s: str) -> AppearanceProfile` to `src/core/preferences/uap/models.py`; set `updated_at` to current ISO 8601 on every field mutation (INV-004)

- [x] T017 [US1] Add `UAPSettings` dataclass to `src/core/preferences/uap/models.py`:
  - Fields per `data-model.md section 3` including `last_used_x: int = -1`, `last_used_y: int = -1`
  - Docstring note: `last_used_*` are always kept current regardless of `mode` (C4)

- [x] T018 [US1] Create `src/core/preferences/uap/service.py` - `UAPService` class with `load() -> UAPSettings` reading all `uap.*` preference keys; returns `FACTORY_DEFAULTS`-based defaults for any missing key

  **T018-B — Seed Factory-Default AppearanceProfile on First Load (U3)**
  After `load()` initialises scalar keys, query the profile store:
  - If zero `AppearanceProfile` records exist, seed one factory-default profile with:
    - `profile_id = "factory_default"` — **this sentinel is correct and SHALL NOT be replaced with a UUID (P3-H04 — Resolved 2026-04-26)**
    - `profile_name = "Default"`
    - `is_default = True`
    - `is_user_created = False`
    - all required schema fields (`window_x`, `window_y`, `width`, `height`, `font_family`, `font_size`, `directory`, `profile_schema_version`) populated from `FACTORY_DEFAULTS`
  - Persist the seeded profile immediately (same transaction / write-flush as the scalar key initialisation)
  - The factory-default profile MUST be treated as non-deletable — `delete_profile("factory_default")` MUST raise `ValueError` (see T024 `INV-002`)
  - T018-B MUST NOT run if any profile records already exist; this is a first-load-only guard

  > **Clarification:**
  > T018 handles scalar defaults for `UAPSettings`, but FR-006 requires a full `AppearanceProfile` object to exist at all times.
  > T018-B ensures that a factory-default profile is created on first load when no profiles exist.
  > This seeded profile MUST be treated as non-deletable and MUST remain available to all tools from the moment the service is first initialised.

  > **Governance Annotation — Factory Default AppearanceProfile (U3):**
  > FR-006 requires that a factory-default `AppearanceProfile` always exist and never be deletable.
  > Earlier drafts relied on scalar fallback values in `UAPSettings.load()`, which do not create or persist a full profile object. Without a seeded profile, first-run behavior is undefined: tools may start with no appearance profile, deletion-guard logic (`INV-002`) operates on an empty set, and T042/T033 font and theme propagation may fire with no profile to read.
  >
  > T018-B closes this gap by seeding the factory-default profile during the same pass that seeds scalar keys. The profile is created once, persisted immediately, and the `is_user_created=False` / `is_default=True` flags ensure it is excluded from all delete operations throughout the system's lifetime.

- [x] T019 [US1] Add `UAPService.save_last_used(width, height, x, y, font_family, font_size, directory) -> None` to `src/core/preferences/uap/service.py` - writes all seven `uap.last_used_*` keys unconditionally regardless of current `mode` (BC-006, C4)

- [x] T020 [US1] Add `UAPService.get_active_settings() -> UAPSettings | AppearanceProfile` to `src/core/preferences/uap/service.py` - returns `AppearanceProfile` when `mode == "predefined"`; returns `UAPSettings` (last-used) when `mode == "last_used"`

- [x] T021 [US1] Add `UAPService.apply(window: QMainWindow, manifest_entry=None) -> None` to `src/core/preferences/uap/service.py`:
  - `window.resize(max(active_width, manifest_entry.min_window_width or 400), max(active_height, manifest_entry.min_window_height or 300))`
  - **`apply()` is the final geometry step (P3-M02 — Resolved 2026-04-26):** After `apply()` returns, no subsequent `resize()` or `move()` call SHALL be issued in `__init__`. Any geometry set before `apply()` (e.g. `_setup_window()` placeholder resize) is intentionally superseded.
  - **Apply font:** call `window.setFont(QFont(font_family, font_size))`; then iterate `window.findChildren(QWidget)` and call `.setFont(QFont(font_family, font_size))` on each child widget — this propagation mechanism MUST match the implementation used in T033's `_on_uap_font_changed` handler (U1)
  - Set browse root via `window.set_browse_root(directory)` (or equivalent attribute)

  > **Governance Annotation — T021 Must Mirror T033 Font Propagation (N6 — Resolved 2026-04-26)**
  > Earlier drafts of T021 stated that fonts must be applied to "all child widgets" but did not specify the mechanism. T021 MUST use the same propagation mechanism as T033: iterating `window.findChildren(QWidget)` and calling `.setFont()` on each child. This ensures consistent font propagation at both window-open time and runtime font-change events, and satisfies FR-021's requirement that every widget receives the update.
  - Skip resize if window declares `QSizePolicy.Fixed` on both axes

- [x] T022 [US1] Add `UAPService.resolve_directory(path: str) -> Path` to `src/core/preferences/uap/service.py`:
  - Returns `Path(path)` if it resolves to an existing directory
  - Returns `Path.home()` otherwise; logs `WARNING: stored directory 'X' not found - using home directory`; stored preference NOT modified (BC-002)

- [x] T023 [US1] Add `UAPService.place_window(window: QMainWindow, open_windows: list) -> None` to `src/core/preferences/uap/service.py` (FR-023):
  - Stored `(x, y) != (-1, -1)`: call `window.move(x, y)` and return
  - `(-1, -1)` and `len(open_windows) == 0`: centre on primary screen via `QScreen.availableGeometry().center()`
  - `(-1, -1)` and `len(open_windows) > 0`: move to last opened window position + (+20, +20)

- [x] T024 [US1] Add `UAPService` profile CRUD methods to `src/core/preferences/uap/service.py`:
  - `create_profile(name: str) -> AppearanceProfile` - UUID4, `is_default=False`, inherits current last-used values
  - `get_profile(profile_id: str) -> AppearanceProfile`
  - `list_profiles() -> list[AppearanceProfile]`
  - `rename_profile(profile_id: str, new_name: str) -> None`
  - `duplicate_profile(profile_id: str, new_name: str) -> AppearanceProfile`
  - `delete_profile(profile_id: str) -> None` - raise `ValueError` if last profile or factory default (INV-002); the guard MUST check `profile_id == "factory_default"`, not `profile_name` — **`"factory_default"` is the permanent sentinel identity; do NOT replace this check with a UUID comparison (P3-H04 — Resolved 2026-04-26)**
  - `set_active_profile(profile_id: str) -> None` - sets `uap.active_profile_id` and `uap.mode = "predefined"`

- [x] T025 [US1] Add `UAPService` signal methods to `src/core/preferences/uap/service.py`:
  - `set_font(family: str, size: int) -> None` - clamp size to [6, 32] (BC-004); MUST NOT call `save_last_used()`; MUST call `set_font_preferences(family, size)` to persist font fields only (A2); emit `ThemeManager.instance().uap_font_changed.emit(family, size)`
  - `set_font_preferences(font_family: str, font_size: int) -> None` - persist only `last_used_font_family` and `last_used_font_size` fields in `UAPSettings`; MUST NOT modify geometry, directory, or any other appearance fields (A2)
  - `set_geometry(width: int, height: int, x: int, y: int) -> None` - persist geometry fields only; emit `ThemeManager.instance().uap_geometry_changed.emit(width, height, x, y)`; MUST NOT modify directory or appearance fields (BC-006c, I4)
  - `set_directory(path: str) -> None` - persist last-used directory field only; MUST NOT modify geometry or appearance fields (BC-006b, I4)

  > **Governance Annotation — Full-State vs Incremental Writes (A2):**
  > Earlier drafts allowed `set_font()` (T025) to call `save_last_used()`, which wrote a full-state snapshot. This caused a partial-state write: font updates silently overwrote the stored geometry and directory fields with stale values from the previous `closeEvent`.
  > `save_last_used()` is a full-state write and MUST only be called from `closeEvent` (T032). Incremental updates MUST use field-specific setters (`set_font_preferences`, `set_geometry`, `set_directory`) that update only their respective fields. This preserves state integrity and prevents cross-field corruption.

- [x] T026 [US1] Add `UAPService.import_profile(data: str) -> AppearanceProfile` to `src/core/preferences/uap/service.py` (FR-026):
  - Parse JSON into `AppearanceProfile`; collect reset descriptions for incompatible fields (directory non-existent, font not in `QFontDatabase`)
  - If any resets: show `QMessageBox.warning` listing each reset field and reason; user clicks OK
  - Write corrected profile to store; return resulting `AppearanceProfile`
  - **Geometry normalization semantics (G3):** T026 MUST preserve imported `window_width` and `window_height` values exactly as provided, even if they are below the tool's `min_window_width` or `min_window_height`. T026 MUST NOT clamp or normalize window geometry. Undersized values are clamped at apply-time by T021 (`window_width >= min_window_width`; `window_height >= min_window_height`). Import is a pure data-loading operation.

  > **Governance Annotation — Import vs Apply Geometry Semantics (G3):**
  > FR-026 defines behavior for incompatible fields during import but did not specify how undersized window dimensions should be handled. This annotation establishes that import MUST preserve geometry exactly as provided. Normalization occurs only during apply-time (T021), which has access to the tool's `min_window_width` and `min_window_height`. Clamping at import-time would require tool-specific knowledge, violating the governance boundary between the import operation and the tool layer. Keeping normalization in T021 ensures consistent geometry handling across all tools and prevents import-time mutation of user data.

- [x] T027 [US1] Implement `get_uap_settings()` and `save_uap_settings()` in `src/core/preferences/manager.py` - replace `raise NotImplementedError` stubs with delegation to `UAPService`

- [x] T028 [P] [US1] Create `src/gui/dialogs/font_picker_dialog.py` - `FontPickerDialog(QDialog)` (FR-018):
  - `QListWidget` of font families from `QFontDatabase`
  - `QSpinBox` size picker range 6-32
  - Live preview `QLabel` updating on every selection change
  - OK: call `UAPService().set_font(family, size)` — the resulting `uap_font_changed` signal MUST propagate the font change to `parent_window` and all child widgets via T033; no direct `parent_window.setFont()` call is permitted
  - Cancel: no changes made

  > **Governance Annotation — T028 Must Not Mutate the Window Directly (N7 — Resolved 2026-04-26)**
  > Earlier drafts of T028 directly applied the font to the parent window before calling `UAPService.set_font()`. This caused redundant updates and inconsistent propagation, because only the signal path (T033) performs the full `findChildren()` sweep. T028 MUST rely exclusively on the `uap_font_changed` signal for font propagation. All font updates MUST flow through: `UAPService.set_font()` → `set_font_preferences()` → `ThemeManager.uap_font_changed.emit()` → `StandardWindow._on_uap_font_changed` → `setFont()` + `findChildren()` sweep.

- [x] T029 [P] [US1] Create `src/gui/dialogs/directory_picker_dialog.py` - `DirectoryPickerDialog(QDialog)` (FR-019):
  - Read-only `QLineEdit` showing current browse root
  - Browse `QPushButton` triggers `QFileDialog.getExistingDirectory()` (no `os.chdir()` calls, FR-007)
  - `QCheckBox` "Apply to all tools (update profile)" - checked by default
  - OK checked: calls `UAPService().set_directory(new_path)` (BC-006b, I4); sets window browse root; MUST NOT call `set_geometry(...)`
  - OK unchecked: sets window browse root only (session-scoped, not persisted); does NOT call `set_directory()`
  - Non-existent path: show inline `QLabel` error in red; do not `accept()` dialog
  - **T029 MUST rely on last-write-wins semantics as defined in BC-006b (U4).** T029 MUST NOT attempt to serialize, lock, or coordinate directory updates across tools.

- [x] T030 [P] [US1] Create `src/gui/widgets/uap_appearance_widget.py` - `UAPAppearanceWidget(QWidget)`:
  - Mode radio group: "Last Used" / "Predefined"
  - Profile `QComboBox` + buttons: New, Rename, Duplicate, Delete, Set Active (enabled in Predefined mode only)
  - Window width `QSpinBox` (>= 400) and height `QSpinBox` (>= 300)
  - Window X / Y `QSpinBox` fields + "Use default placement" `QCheckBox` writing sentinel (-1, -1)
  - Font family `QComboBox` + size `QSpinBox`
  - Working directory `QLineEdit` + Browse `QPushButton`
  - Apply `QPushButton`: writes all values via `UAPService`; triggers live propagation signals

- [x] T031 [US1] Modify `src/gui/standard_window.py` - `__init__` (after `_setup_ui()`, before `_create_status_bar()`) **(P3-M02 — Resolved 2026-04-26: insertion point is canonical)**:
  - Call `UAPService().apply(self, self._get_manifest_entry())`
  - Call `UAPService().place_window(self, ThemeManager.instance().registered_windows())`
  - Register `self` with **ThemeManager** via `ThemeManager.instance().register(self)` — MUST NOT add `self` to any module-level `_open_windows` set (U2)
  - **Note:** `_setup_window()`'s `self.resize()` call is a non-authoritative placeholder and is intentionally superseded by `UAPService().apply()`. No `resize()` or `move()` call SHALL follow `apply()` in `__init__`. See canonical lifecycle table in P3-M02 resolution.
  - **UAP Tracking Attributes (P3-Q5 — Resolved 2026-04-26):** After applying font and directory, `apply()` MUST store:
    - `self._uap_font_family = font_family`
    - `self._uap_font_size = font_size`
    - `self._uap_browse_root = browse_root`
  - These are instance attributes on `StandardWindow`; `closeEvent()` (T032) reads them at close time. They MUST be set after the font and directory are applied, not before.

  > **Governance Annotation — Single Window Registry (U2):**
  > Earlier drafts registered open windows in both a module-level `_open_windows` WeakSet in `standard_window.py` and in `ThemeManager._registered_windows`. This created dual ownership, duplicate signal fan-out, and inconsistent lifecycle tracking.
  > **ThemeManager is the sole authoritative owner of window registration** because all theme, font, and geometry propagation signals originate there. The module-level `_open_windows` registry MUST NOT exist. T031 MUST delegate all registration to `ThemeManager.instance().register()`.

- [x] T032 [US1] Add `StandardWindow.closeEvent(self, event: QCloseEvent) -> None` to `src/gui/standard_window.py` **(P3-L01 pending; P3-Q5 — Resolved 2026-04-26)**:
  - **Read tracking attributes (P3-Q5):** Font and browse-root SHALL be read from instance attributes set by `apply()` (T031):
    ```python
    font_family = self._uap_font_family
    font_size = self._uap_font_size
    browse_root = self._uap_browse_root
    ```
  - **Read geometry live:** Geometry SHALL be read live from the window at close time:
    ```python
    g = self.geometry()
    x, y, w, h = g.x(), g.y(), g.width(), g.height()
    ```
  - Call `UAPService().save_last_used(w, h, x, y, font_family, font_size, browse_root)` unconditionally (BC-006, C4)
  - Deregister via `ThemeManager.instance().unregister(self)` before `super().closeEvent(event)` — MUST NOT remove from any module-level `_open_windows` set (U2)
  - **Full-state persistence (A2):** T032 MUST be the exclusive location where `save_last_used()` is invoked. No other task or method MUST call `save_last_used()`. T032 gathers the authoritative geometry, font, and directory values and persists them as a complete snapshot.
  - MUST NOT read font from `self.font()` or `self.fontInfo()`; MUST NOT re-call `UAPService().get_active_settings()` at close time.

- [x] T033 [US1] Modify `src/gui/standard_window.py` - connect to signal bus:
  - All widgets SHALL connect to ThemeManager signals via the singleton (P3-C01 — Resolved 2026-04-26):
    - `ThemeManager.instance().uap_font_changed.connect(self._on_uap_font_changed)`
    - `ThemeManager.instance().uap_geometry_changed.connect(self._on_uap_geometry_changed)`
  - No callback-list registration is allowed
  - `_on_uap_font_changed(family, size)` MUST:
    1. Call `self.setFont(QFont(family, size))` on the window
    2. Iterate ALL child widgets via `self.findChildren(QWidget)` and call `.setFont(QFont(family, size))` on each — calling only `self.setFont()` is insufficient (FR-021, U1)
    3. Target widgets include at minimum: `QLabel`, `QPushButton`, `QMenuBar`, `QToolBar`, `QTableView`, `QTreeView`, `QLineEdit`
  - `_on_uap_geometry_changed(w, h, x, y)` MUST call `self.resize(w, h)` and `self.move(x, y)` (skip fixed-size windows)
  - **Custom widget compliance (U1):** Custom widgets that set their own font via `setFont()` MUST connect to `uap_font_changed` and update their internal font; failure to do so is a violation of FR-021

  > **Governance Annotation — Full Font Propagation (U1):**
  > FR-021 requires the selected font to apply to **every widget** in the tool. Qt's `QWidget.setFont()` propagates to children by default, but only if those children have not had a font explicitly set via their own `setFont()` call. Any widget with an explicit font set will not inherit the parent's propagated font.
  > T033 MUST therefore iterate `findChildren(QWidget)` and call `setFont()` on each child explicitly, in addition to calling it on the window itself. Custom widgets that set fonts internally MUST connect to `uap_font_changed`.

- [x] T034 [US1] Modify `src/gui/settings_dialog.py` - Appearance tab:
  - Embed `UAPAppearanceWidget` as the `"Appearance"` tab content
  - Wire Apply / OK to flush all widget values through `UAPService` (persist + emit signals)

- [x] T035 [US1] Modify `src/gui/settings_dialog.py` - base `PreferencesDialog`:
  - Ensure `addTab(widget: QWidget, label: str)` is public for tool subclasses to inject tool-specific tabs (FR-009)
  - Tools with no extra preferences use base class directly without subclassing

- [x] T036 [US1] [P3-H02 — Resolved 2026-04-26] Modify `src/tabbed_hub.py` — add `Appearance` tab (FR-025):
  > **This task targets `src/tabbed_hub.py`, the canonical GUI hub. Do NOT modify `src/rfu/hub.py` — that file contains only idle-watcher utilities and has no GUI code.**
  - Embed `UAPAppearanceWidget` as a dedicated tab labelled `"Appearance"` before tool category tabs
  - Ensure tab order matches Hub UX spec
  - Ensure tab icon and label follow UI harmonization rules
  - Hub changes propagate immediately to open tool windows via `UAPService` signals

---

## Phase 4: Menu Contract (US2) - Stories 6-10

- [x] T037 [US2] Modify `src/gui/menu_manager.py` - `_create_view_menu()` (FR-004, FR-018):
  - Add `font_picker` action labelled `&Font...`; triggered: instantiate `FontPickerDialog(parent=self)` and `exec_()`
  - Insert before any tool-specific view additions

- [x] T038 [US2] Modify `src/gui/menu_manager.py` - `_create_view_menu()` (FR-004, FR-019):
  - Add `working_directory_picker` action labelled `&Working Directory...`; triggered: instantiate `DirectoryPickerDialog(parent=self)` and `exec_()`

- [x] T039 [US2] Rebuild `src/gui/menu_manager.py` - `_create_file_menu()` to match contract topology (FR-024, P3-M01 — Resolved 2026-04-26):
  - **Remove all `window_type` conditionals** from File menu slot creation — no slot may be conditionally present or absent
  - Create all 7 canonical File menu actions **unconditionally**, in contract-mandated order, each default-disabled (`setEnabled(False)`) except `"exit"` which SHALL always be enabled:

    | Position | Action | Action ID | Default State |
    |----------|--------|-----------|---------------|
    | 1 | Open | `"open_file"` | disabled |
    | 2 | Save | `"save"` | disabled |
    | 3 | Save As | `"save_as"` | disabled |
    | — | separator | — | — |
    | 4 | Import | `"import"` | disabled |
    | 5 | Export | `"export"` | disabled |
    | — | separator | — | — |
    | 6 | Preferences | `"preferences"` | disabled |
    | — | separator | — | — |
    | 7 | Exit | `"exit"` | **always enabled** |

  - **Remove `print_document`** (Ctrl+P) — this action has no position in the contract and Phase 3 does not authorize extension slots
  - **Fix all action IDs** to use canonical IDs from the table above; remove legacy IDs `"save_file"`, `"export_data"`, `"import_data"`
  - Expose `enable_file_action(action_id: str, label: str | None = None) -> None`:
    - Enables the slot; if `label` is provided, renames it to the tool-relevant label (e.g. `"Open Report…"`)
    - If `label` is `None`, the generic label is preserved unchanged
    - **Inapplicable** (never enabled) slots MUST NOT be renamed — generic label is mandatory
    - Slots are NEVER hidden, NEVER removed, NEVER reordered
  - This task supersedes all earlier conditional logic in `_create_file_menu()`; rebuild end-to-end, do not patch

  > **Governance Annotation — Unconditional File Menu (P3-M01 — Resolved 2026-04-26):**
  > The File menu must never change structure based on `window_type`. Presence is structural; applicability is expressed via enabled/disabled state only. This is constitutional: cross-tool consistency is a core governance invariant.
  > Any contributor who restores `window_type` conditionals or reorders actions MUST update `menu-contract.md` and document the change in a PR comment. No such change may be merged without reviewer sign-off.

- [x] T040 [US2] Modify `src/gui/menu_manager.py` - `_create_about_action()` (FR-017):
  - About `QMessageBox` body: tool name, suite version from `APP_VERSION` in `src/core/constants.py` (P3-M03 — Resolved 2026-04-26; `src/__version__.py` SHALL NOT be used), tool `__version__` (fallback: "same as suite"), `sys.version`, `PYQT_VERSION_STR`, `QT_VERSION_STR`

- [x] T041 [US2] Run `ToolManifestRegistry`-registered tool audit for each registered tool class:
  > **Prerequisite: T003 MUST be complete.** Registry must exist and contain ≥ 2 seeded entries.
  > **Phase-1 Baseline (C1):** The 5-menu topology (File, Edit, View, Tools, Help) is the Phase-1 minimum contract. Tools MUST implement at least these menus. The contract MUST remain extensible to the full 7-menu topology defined in Constitution §7.2. Tests MUST NOT assert `len(menus) == 5` or otherwise freeze the Phase-1 structure.
  > **T041 MUST NOT seed, mutate, or add entries to the registry (I9). T041 MUST fail if `ToolManifestRegistry.all()` returns fewer than two entries.**
  - Instantiate headlessly with `qtbot` offscreen; verify menu topology (T007 tests must pass)
  - Fix any menu structure violation in the tool's own module
  - Tool that cannot be headlessly instantiated: add `headless_incompatible: True` to `ToolManifestEntry` with one-line reason

- [x] T042 [US2] Modify `src/gui/themes.py` - `ThemeManager` (FR-020, FR-021, FR-022):
  - **Refactor `ThemeManager` into a QObject-based singleton (P3-C01 — Resolved 2026-04-26):**
    - Change class definition to `class ThemeManager(QObject):`
    - Add `_instance = None` class variable
    - Add `@classmethod def instance(cls):` returning the singleton (construct on first call)
    - Remove `_theme_changed_callbacks` and all callback-list infrastructure
  - Add class-level signals: `uap_font_changed = pyqtSignal(str, int)`, `uap_geometry_changed = pyqtSignal(int, int, int, int)`, `changed = pyqtSignal(str)`
  - Add `_registered_windows: weakref.WeakSet[QMainWindow]` instance attribute — this is the **only** authoritative window registry; no other WeakSet tracking open windows MUST exist anywhere in the codebase (U2)
  - Add `register(window)` and `unregister(window)` instance methods (called via `ThemeManager.instance()`)
  - Add `registered_windows() -> list[QMainWindow]` helper returning a snapshot list (used by T031 for placement)
  - All UAP propagation tasks SHALL use `ThemeManager.instance()` for signal emission and registration
  - No direct instantiation (`ThemeManager()`) MUST appear anywhere in the codebase after this task

  > **Governance Annotation — ThemeManager Identity (P3-C01 — Resolved 2026-04-26)**
  > `ThemeManager` is now a `QObject`-based singleton. This is a constitutional requirement: `pyqtSignal` only works on `QObject` subclasses. Any reversion to a plain Python class raises `TypeError` at import time and breaks all UAP tests. Any future change to ThemeManager's identity MUST be documented in a PR comment and MUST update BC-007 and BC-008.

- [x] T043 [US2] Modify `src/gui/themes.py` - signal broadcast (FR-020, BC-007, BC-008):
  - All UAP changes SHALL be emitted through the ThemeManager singleton — no direct callback invocation is permitted:
    - `ThemeManager.instance().uap_font_changed.emit(family, size)`
    - `ThemeManager.instance().uap_geometry_changed.emit(x, y, w, h)`
    - `ThemeManager.instance().changed.emit("uap")`
  - `uap_font_changed` slot: iterate `_registered_windows`; call `w.setFont(QFont(family, size))` on each; SLA: all <= 10 open windows updated within 500ms (C3)
  - `uap_geometry_changed` slot: iterate; `w.resize(w_, h_)`; `w.move(x, y)` (skip QSizePolicy.Fixed windows)
  - `changed` (theme) slot: iterate; re-apply theme stylesheet via `ThemeManager.instance().apply(w)`

---

## Phase 5: Dependency Consistency (US3) - Stories 11-12

- [x] T044 [P] [US3] Audit `requirements.txt` (FR-012):
  - Every package line must use exact pinned version (`==`, not `>=` or `~=`)
  - Every package line must end with a `# <purpose-category>` comment
  - Add missing pins and comments; commit alongside this task

- [x] T045 [US3] Create `scripts/check_dependencies.py` (FR-013):
  - Parse `requirements.txt` (skip blank lines and `#` comment lines; strip inline comments)
  - Evaluate `; sys_platform==...` markers against actual `sys.platform`, or against `--platform <target>` override if flag supplied
  - Compare package-version dict against `pip list --format=json`
  - Print `MISMATCH: <pkg> required=<ver> installed=<ver>` for each mismatch
  - Print `UNDECLARED: <pkg> installed=<ver>` for installed packages absent from `requirements.txt`
  - Exit 0 if no mismatches; exit 1 if any mismatch

---

## Phase 6: Framework & Packaging Docs (US4) - Stories 13-14

- [x] T046 [P] [US4] Create `docs/architecture/frameworks-and-dependencies.md` (FR-014):
  - Table: Package | Pinned Version | Role in Suite | Rationale | Minimum Acceptable Version
  - Rows for: PyQt5, argon2-cffi, cryptography, pywin32 (Windows), pytest, pytest-qt, and all other direct runtime dependencies
  - Update policy: "This document MUST be updated in the same PR as any dependency version change"

- [x] T047 [P] [US4] Create `docs/architecture/packaging-style.md` (FR-015):
  - Section: Virtual environment conventions (`.venv312/`, why 3.12, side-by-side venv naming)
  - Section: `requirements.txt` format rules (pinned `==`, purpose comment, no ranges, no `*`)
  - Section: "How to add a new dependency" step-by-step checklist (install, pip freeze, add comment, update docs, run audit script)
  - Section: Activation scripts overview (`activate_env.bat`, `activate_env.ps1`, `activate_env.sh`, `activate_env.py`) with usage examples

---

## Final Phase: Integration & Polish

- [x] T048 Run tool-interface audit - list every class registered in `ToolManifestRegistry` (canonical source: `src/core/tool_manifest.py`, created in T003) that does not subclass `StandardWindow` or `SafeStandardWindow`:
  > **Prerequisite: T003 MUST be complete.** "All registered tools" means `ToolManifestRegistry.all()`, not any other enumeration.
  - Fixable: update class declaration to inherit `StandardWindow`
  - Unfixable (e.g., fixed-size modal): add `uap_exempt: True` field and one-line reason to its `ToolManifestEntry`

- [x] T049 Run full test suite with coverage gate:
  ```powershell
  python -m pytest tests/ --cov=src/core/preferences/uap --cov=src/gui/dialogs --cov=src/gui/widgets/uap_appearance_widget.py --cov-report=term-missing -v
  ```
  Fix uncovered branches in new code only; do NOT modify pre-existing modules to hit coverage targets

- [x] T050 Run dependency audit script and confirm exit code 0:
  ```powershell
  python scripts/check_dependencies.py
  ```
  Resolve every MISMATCH or UNDECLARED before proceeding

- [x] T051 Manual smoke test per quickstart.md section "Verifying UAP Manually":
  - Launch hub; open File Finder, Duplicate Finder, PDF Merge - confirm identical window size, font, browse root
  - Change font inside Duplicate Finder; open fourth tool - confirm new font applied
  - Switch to predefined profile "Work" (1200 x 900, Segoe UI 11pt, C:\Projects); open two more tools - confirm profile applied; close a tool and verify `last_used_*` keys updated in `config/rfu_config.json`

- [x] T052 Update `specs/007-ui-harmonization/plan.md` progress tracking - mark Phase 3 and Phase 4 complete; record completion date

---

## Parallel Execution Guide

Tasks marked [P] touch separate files and can be executed simultaneously:

| Slot A | Slot B | Slot C |
|--------|--------|--------|
| T004 (model tests) | T005 (service tests) | T006 (defaults tests) |
| T007 (contract tests) | T008 (about tests) | T009 (propagation tests) |
| T010 (FontPicker tests) | T011 (DirPicker tests) | T012 (dep audit tests) |
| T013 (uap __init__) | T014 (defaults.py) | T015 (models.py AppearanceProfile) |
| T028 (FontPickerDialog) | T029 (DirPickerDialog) | T030 (UAPAppearanceWidget) |
| T044 (requirements.txt) | T046 (frameworks doc) | T047 (packaging doc) |

Sequential chains (same file - do NOT parallelize):
- T015 -> T016 -> T017 (models.py additions)
- T018 -> T019 -> T020 -> T021 -> T022 -> T023 -> T024 -> T025 -> T026 (service.py additions)
- T031 -> T032 -> T033 (standard_window.py modifications)
- T034 -> T035 (settings_dialog.py modifications)
- T037 -> T038 -> T039 -> T040 (menu_manager.py modifications)
- T042 -> T043 (themes.py modifications)

---

## Implementation Strategy

**MVP** (US1 only - Scenarios 1-5):
T001-T003 (setup) -> T004-T012 (TDD, all red) -> T013-T036 (UAP implementation). Run T049 scoped to UAP package.

**Increment 2** (US2 - Scenarios 6-10): T037-T043.

**Increment 3** (US3 + US4 - Scenarios 11-14): T044-T047.

**Polish**: T048-T052.

---

## Governance Reviewer Checklist

- **Menu Extensibility Check (C1):** Confirm that no test or spec text freezes the top-level menu count at 5. All tests MUST allow extension to the 7-menu constitutional topology (Constitution §7.2).
- **FR-024 Label Invariance:** Confirm that contract tests do not assert the specific label text of applicable (enabled) File menu actions; only slot presence and enabled state are validated.
- **TDD Gate:** Confirm all Phase-2 tests (T004–T012) are written and failing red before any Phase-3 implementation code is merged.
- **ToolManifest-only enumeration:** Confirm no test uses module scanning or `tool_interface_validator` to discover tools (C5, FR-016).
- **Manifest Purity Check (I2):** Confirm that `ToolManifest` contains only tool-authored declarations (e.g., `min_window_width`, `min_window_height`) and no user-state fields such as `window_x` or `window_y`.
- **UAPService API Consistency Check (I3):** Confirm that `UAPService` exposes only the primitive-parameter `save_last_used(width, height, x, y, font_family, font_size, directory)` method and does not define a Qt-dependent variant (`record_last_used(window)`).
- **Directory Persistence Check (I4):** Confirm that directory updates use `set_directory(path)` and do not overload `set_geometry(...)` or `save_last_used(...)` for directory-only operations.
- **Path Consistency Check (I5):** Confirm that all "Tested by" headers and plan.md references use `tests/contracts/` (plural). Any occurrence of `tests/contract/` (singular) MUST be treated as a blocking issue.
- **Hub Identity Check (P3-H02 — Resolved 2026-04-26):** The canonical GUI hub is `src/tabbed_hub.py`. Confirm that T036 targets `src/tabbed_hub.py` and NOT `src/rfu/hub.py`. Confirm that `src/rfu/hub.py` contains only idle-watcher utilities and no GUI code. Confirm plan.md source tree lists `src/tabbed_hub.py` as the MODIFY target. Governance annotations I6 (Pass 1) and N10/N11 (Pass 2) that mandated `src/rfu/hub.py` as the GUI hub are superseded by P3-H02. Any task that targets `src/rfu/hub.py` for GUI work MUST be treated as a blocking issue.
- **Platform Condition Check (I7):** Confirm that FR-013 is implemented such that platform-conditional lines evaluating to `False` on the current machine are **skipped** by default and do not cause a non-zero exit. Confirm that non-zero exit due to platform mismatch occurs only when `--platform=<value>` is explicitly provided. The implementation MUST NOT treat platform-conditional mismatches as failures under default evaluation.
- **Migration Table Consistency Check (I8):** Confirm that the AppearanceProfile migration table does not list `window_x`/`window_y` as added in Version 2 or any later version. These fields are present in the Version 1 `"required"` array. Any version entry claiming to add a field that already exists in an earlier version's `"required"` array MUST be treated as a blocking issue.
- **Manifest Creation & Seeding Check (P3-H01 — Resolved 2026-04-26):** Confirm that T003 CREATES `ToolManifestEntry` dataclass and `ToolManifestRegistry` in `src/core/tool_manifest.py` (nothing pre-exists). Confirm T003-B seeds at least two entries with non-zero `min_window_width` and `min_window_height`. Confirm T007 fails (not passes) when the registry is empty. Confirm T041 reads but never writes to the registry. Any audit against an empty manifest is a blocking issue.
- **FR-021 Font Propagation Check (U1):** Confirm that T033's `_on_uap_font_changed` slot iterates `findChildren(QWidget)` and calls `setFont()` on every child widget, not only the top-level window. Confirm T009 includes assertions for `QLabel`, `QMenuBar`, `QToolBar`, and `QTableView`. Confirm custom widgets with manually-set fonts connect to `uap_font_changed`.
- **Window Registry Ownership Check (U2):** Confirm that no module-level `_open_windows` WeakSet exists in `standard_window.py`. Confirm T031 registers via `ThemeManager.instance().register()` and T032 deregisters via `ThemeManager.instance().unregister()`. Confirm T042 treats `ThemeManager._registered_windows` as the only authoritative window registry. Any second registry is a blocking issue.
- **profile_id Sentinel Exception Check (P3-H04 — Resolved 2026-04-26):** JSON schema for `profile_id` now uses `oneOf` allowing `"format": "uuid"` or `"enum": ["factory_default"]`. Reviewers SHALL confirm: (1) T018-B seeds `profile_id="factory_default"` without modification; (2) T024 deletion guard checks `profile_id == "factory_default"`; (3) T004 round-trip test does not assert UUID4 format for the factory-default profile; (4) no validator in the codebase attempts to parse `"factory_default"` as a UUID4. Any code that calls a UUID validator on `profile_id` without first checking for the sentinel is a blocking issue.
- **Directory Update Semantics Check (U4):** Confirm that BC-006b defines last-write-wins semantics for concurrent `set_directory()` calls. Confirm T029 and all other directory-setting paths rely exclusively on last-write-wins. Confirm no `set_directory()` call site introduces locking, queuing, or merge logic. Confirm no tool assumes exclusive write access to the directory field.
- **Mixed-Sentinel Invariant Check (U5):** Confirm that T004 includes a `ValueError`-expecting test for both directions of the INV-006 violation: `window_x >= 0` with `window_y == -1`, and `window_x == -1` with `window_y >= 0`. Confirm the model enforces this invariant at construction or validation time. Confirm no code path allows a mixed-sentinel profile to be persisted or applied.
- **Source Tree Completeness Check (G1):** Confirm that `src/gui/widgets/uap_appearance_widget.py` is listed under `src/gui/widgets/` in plan.md. Confirm that every file created or modified by a task appears in the plan.md source-change inventory. Any task-created file missing from plan.md is a blocking traceability issue.
- **Schema Version Consistency Check (G2):** Confirm that T004 asserts `profile_schema_version` is present in every serialized `AppearanceProfile` output. Confirm that T004 includes a v1→v2 migration test verifying correct field transformations per the migration table. Confirm no profile is serialized without a schema version. Confirm migration logic sets `profile_schema_version` correctly and introduces no fields outside the migration table.
- **Geometry Import Semantics Check (G3):** Confirm that T026 does NOT clamp or normalize `window_width` or `window_height`. Confirm that FR-026 includes the normative note specifying import-preserves / apply-clamps semantics. Confirm that T021 is the only place where geometry normalization occurs. Confirm no tool attempts to clamp geometry during import. Confirm import remains a pure data-loading operation.
- **PreferencesDialog Integration Check (A1):** Confirm that tools with extra preferences subclass `PreferencesDialog` and use `addTab()`. Confirm that tools with no extra preferences instantiate the base class directly without subclassing. Confirm no tool subclasses `PreferencesDialog` without adding tabs. Confirm FR-009 reflects the corrected non-contradictory semantics.
- **Persistence API Consistency Check (A2):** Confirm that `save_last_used()` is called ONLY in T032 (`closeEvent`). Confirm that T025 (`set_font`) calls `set_font_preferences()` and does NOT call `save_last_used()`. Confirm that geometry updates use `set_geometry()`, directory updates use `set_directory()`, and no incremental update path writes fields outside its own scope. Confirm BC-006 reflects the clarified full-state write semantics.

---

## Format Validation

- All 52 tasks follow: - [ ] T### [P?] [USx?] Description with file path
- No bold task IDs
- Setup and Foundational phases: no story label
- US1-US4 phases: story labels present
- Polish phase: no story label
- Total tasks: 52 (T001-T052)
- Parallel tasks: 18 marked [P]
- US1 tasks: T013-T036 (24 tasks)
- US2 tasks: T037-T043 (7 tasks)
- US3 tasks: T044-T045 (2 tasks)
- US4 tasks: T046-T047 (2 tasks)