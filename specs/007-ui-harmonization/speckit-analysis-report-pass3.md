# SpecKit Analysis Report — Pass 3

**Run date:** 2026-04-26
**Feature:** `007-ui-harmonization` — Unified Look & Feel (Phase 1)
**Pass scope:** Cross-artifact consistency, spec-vs-codebase implementation-readiness audit, and open question resolution
**Builds on:** `speckit-analysis-report.md` (Pass 1), `speckit-analysis-report-pass2.md` (Pass 2)
**Artifacts analyzed:**
- All Pass 1 + Pass 2 artifacts (unchanged)
- `src/gui/themes.py` — `ThemeManager`, `Colors`, `Fonts`, `Typography`
- `src/gui/standard_window.py` — `StandardWindow`
- `src/gui/menu_manager.py` — `MenuManager`
- `src/core/preferences/manager.py` — `PreferenceManager`
- `src/rfu/hub.py` — hub utilities
- `src/tabbed_hub.py` — live GUI hub
- `src/__init__.py` — suite version
- `src/core/constants.py` (via import chain)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| FR coverage | 26 / 26 (100%) — inherited from Pass 2 |
| Pass 3 new findings | 10 |
| CRITICAL (blocks all Phase 3) | 1 — ✅ RESOLVED this pass |
| HIGH (blocks specific task chains) | 4 (4 resolved: P3-H01, P3-H02, P3-H03, P3-H04) |
| MEDIUM (correctness risks) | 3 (3 resolved: P3-M01, P3-M02, P3-M03) |
| LOW (advisory) | 2 — ✅ RESOLVED this pass (P3-L01, P3-L02) |
| Q3 resolved this pass | 1 (UAPService instantiation model) |
| P3-Q1 resolved this pass | 1 (ThemeManager QObject singleton) |
| P3-C01 resolved this pass | 1 (ThemeManager identity) |
| P3-H01 resolved this pass | 1 (ToolManifest creation mandate) |
| P3-H02 resolved this pass | 1 (canonical GUI hub: `src/tabbed_hub.py`) |
| P3-H03 resolved this pass | 1 (ThemeManager.instance()) |
| P3-Q2 resolved this pass | 1 (hub identity: `src/tabbed_hub.py` is canonical) |
| P3-M03 resolved this pass | 1 (`APP_VERSION` from `src/core/constants.py` is canonical; no `__version__.py`) |
| P3-M01 resolved this pass | 1 (File menu rebuilt to unconditional 7-slot model; T039 rewritten) |
| P3-M02 resolved this pass | 1 (`UAPService.apply()` is authoritative geometry; canonical `__init__` lifecycle documented) |
| P3-Q4 resolved this pass | 1 (`APP_VERSION` as canonical version source; no new file) |
| P3-H04 resolved this pass | 1 (`"factory_default"` sentinel accepted via `oneOf` schema; no migration required) |
| P3-Q3 resolved this pass | 1 (`"factory_default"` is a valid `profile_id` via constitutional sentinel exception) |
| P3-Q5 resolved this pass | 1 (UAP tracking field rule — `apply()` stores `_uap_font_family`, `_uap_font_size`, `_uap_browse_root`; `closeEvent()` reads them; geometry read live) |
| P3-L01 resolved this pass | 1 (T032 language corrected: "Modify" → "Add `StandardWindow.closeEvent`"; lifecycle table documented) |
| P3-L02 resolved this pass | 1 (Governance artifact integrity sweep: D1–D3 corrected; Q7 and Q8 closed with canonical decisions) |
| Open questions requiring answers before Phase 3 | 0 (all resolved: P3-Q5) |

**Critical path summary (updated 2026-04-26):** P3-C01 is now **RESOLVED** — `ThemeManager` SHALL become a `QObject`-based singleton. P3-H01 is now **RESOLVED** — `ToolManifestEntry` dataclass and `ToolManifestRegistry` SHALL be created from scratch in T003 (nothing pre-exists). P3-H03 is correspondingly resolved. P3-H02 is now **RESOLVED** — the canonical GUI hub is `src/tabbed_hub.py`; T036 retargeted; I6 governance annotation superseded. P3-H04 is now **RESOLVED** — `"factory_default"` is the constitutional `profile_id` sentinel; schema updated to `oneOf`; INV-002/INV-005 updated; no migration. P3-M03 is **RESOLVED** (see above). All MEDIUM findings are now **RESOLVED** — P3-M01 (File menu unconditional 7-slot), P3-M02 (`UAPService.apply()` authoritative geometry), P3-M03 (`APP_VERSION` canonical). P3-Q5 is now **RESOLVED** — `apply()` stores `_uap_font_family`, `_uap_font_size`, `_uap_browse_root`; `closeEvent()` reads them; geometry read live. P3-L01 is now **RESOLVED** — T032 language corrected; "Modify" → "Add"; lifecycle table documented. P3-L02 is now **RESOLVED** — governance artifact integrity sweep complete; D1–D3 corrected; Q7 and Q8 closed. **All Pass 3 findings are RESOLVED.**

---

## Q3 — `UAPService` Instantiation Model ✅ RESOLVED

**Decision (2026-04-26):** `UAPService` is **stateless**. All reads/writes go directly through `PreferencesStore`. No in-memory caching. Fresh instantiation per call site is valid and intentional.

**Governance Rationale:**
- Every task (T018–T032) reads and writes through the same canonical `PreferencesStore`; no task depends on memoized or warm state.
- Tests in T005 validate behavior strictly through `PreferencesStore`, not service-level caching.
- This ensures deterministic behavior, simplifies testability, and eliminates lifecycle ambiguity.
- If future performance needs arise, caching will be added explicitly at the `PreferencesStore` layer, not implicitly inside `UAPService`.

**Tasks impacted:** T018–T032 — all call `UAPService()` directly. Pattern confirmed valid.
**Tests impacted:** T005 — mock `PreferencesStore`, not `UAPService` state.

> **Governance Annotation — Stateless UAPService (Q3 — Resolved 2026-04-26)**
> The stateless model is intentional and reviewer-proof. Any future contributor who attempts to add in-memory caching inside `UAPService` itself MUST document the rationale as a PR comment and MUST update BC-005 (`apply()` idempotency) accordingly. No caching may be added without updating T005 to assert cache-invalidation behavior.

---

## Implementation Readiness Assessment

This section compares spec-mandated state against actual codebase state. Items flagged here are NOT necessarily findings — many are expected TDD gaps. Items that contradict the spec or introduce hidden blockers are escalated as findings.

| Spec artifact | Expected state | Actual codebase state | Verdict |
|---|---|---|---|
| `src/core/preferences/uap/` package | NEW (T001 creates) | Does not exist | ✅ Expected TDD gap |
| `src/gui/dialogs/font_picker_dialog.py` | NEW (T028) | Does not exist | ✅ Expected TDD gap |
| `src/gui/dialogs/directory_picker_dialog.py` | NEW (T029) | Does not exist | ✅ Expected TDD gap |
| `src/gui/widgets/uap_appearance_widget.py` | NEW (T030) | Does not exist | ✅ Expected TDD gap |
| `scripts/check_dependencies.py` | NEW (T045) | Does not exist | ✅ Expected TDD gap |
| `docs/architecture/frameworks-and-dependencies.md` | NEW (T046) | Does not exist | ✅ Expected TDD gap |
| `ThemeManager` signals (`uap_font_changed`, etc.) | ADD (T042) | Not present — T042 updated | ✅ P3-C01 RESOLVED |
| `ThemeManager.instance()` | CALL (T031/T032/T033) | Does not exist — T042 adds singleton | ✅ P3-H03 RESOLVED |
| `ThemeManager._registered_windows` | ADD (T042) | Does not exist | ✅ Expected TDD gap |
| `StandardWindow.closeEvent` | ADD (T032) | Does not exist | ✅ P3-L01 RESOLVED — T032 updated to "Add" language |
| `ToolManifest` class | ADD (T003) | Does not exist anywhere — T003 rewritten to CREATE | ✅ P3-H01 RESOLVED |
| `src/tabbed_hub.py` (GUI hub) | MODIFY (T036) | Canonical live GUI hub — T036 retargeted | ✅ P3-H02 RESOLVED |
| `src/__version__.py` | READ (T008/T040) | Does not exist | ✅ P3-M03 RESOLVED — use `APP_VERSION` |
| `MenuManager` File menu structure | MATCHES contract | Diverges (order, completeness) | ✅ P3-M01 RESOLVED (File menu rebuilt to unconditional 7-slot model) |
| `MenuManager._create_view_menu` font/dir actions | ADD (T037/T038) | Not present | ✅ Expected TDD gap |
| `src/core/preferences/manager.py` UAP stubs | ADD (T002) | Not present | ✅ Expected TDD gap |

---

## Pass 3 Findings

---

### CRITICAL — Phase-3 Blockers

---

#### P3-C01 — `ThemeManager` is a plain Python class; cannot emit `pyqtSignal` ✅ RESOLVED

**Severity:** CRITICAL → ✅ RESOLVED (2026-04-26)
**Affects:** `tasks.md` T042, T043, T033, T031, T032, T025; `contracts/uap-preferences.md` BC-007, BC-008

**Finding:**

T042 instructs: _"Add class-level signals: `uap_font_changed = pyqtSignal(str, int)`, `uap_geometry_changed = pyqtSignal(int, int, int, int)`, `changed = pyqtSignal(str)` to `ThemeManager`."_

The actual `ThemeManager` class (in `src/gui/themes.py`, line 738) is a **plain Python utility class** — it does NOT subclass `QObject`. `pyqtSignal` only works on `QObject` subclasses. Adding `pyqtSignal` attributes to a non-QObject class raises a `TypeError` at import time. The current theme propagation uses a callback list (`_theme_changed_callbacks`) instead of Qt signals.

**Canonical Decision (P3-Q1 — Resolved 2026-04-26):**

> **ThemeManager SHALL become a `QObject`-based singleton.**
> - `ThemeManager` will subclass `QObject`.
> - It will expose class-level `pyqtSignal` attributes as required by T042.
> - It will provide a classmethod `instance()` returning the single global instance.
> - All tasks (T025, T033, T042, T043) will reference `ThemeManager.instance()` for signal emission and connection.
> - BC-007 and BC-008 remain valid without modification.
> - The existing `_theme_changed_callbacks` list will be deprecated and removed.

**Canonical skeleton:**

```python
from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    # --- Signals ---
    uap_font_changed = pyqtSignal(str, int)
    uap_geometry_changed = pyqtSignal(int, int, int, int)
    changed = pyqtSignal(str)

    _instance = None

    def __init__(self):
        super().__init__()
        # existing initialization logic goes here

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def set_uap_font(self, family, size):
        # write to PreferenceStore
        self.uap_font_changed.emit(family, size)
        self.changed.emit("uap")

    def set_uap_geometry(self, x, y, w, h):
        # write to PreferenceStore
        self.uap_geometry_changed.emit(x, y, w, h)
        self.changed.emit("uap")
```

**Governance Annotation — ThemeManager as QObject Singleton (P3-C01 — Resolved 2026-04-26):**

> `ThemeManager` SHALL be a `QObject` because it is the canonical source of UAP change notifications. Qt's signal/slot system requires that any class emitting `pyqtSignal` must inherit from `QObject`. ThemeManager is the authoritative owner of UAP state and the single point of truth for theme propagation. Delegating signal emission to any other class would fragment the propagation model, violate BC-007 and BC-008, and introduce governance drift. Therefore, ThemeManager's identity as a QObject singleton is a constitutional requirement.
>
> **Any future contributor who attempts to revert ThemeManager to a plain Python class, introduce callback lists alongside Qt signals, or create a second class as the signal bus MUST document the rationale as a PR comment AND update BC-007 and BC-008 accordingly. No such change may be merged without reviewer sign-off.**

**Tasks updated by this resolution:** T042, T043, T033 (see `tasks.md`). BC-007, BC-008 (see `contracts/uap-preferences.md`).

**Migration notes:**
- Replace all direct `ThemeManager()` instantiation with `ThemeManager.instance()`
- Remove all uses of `_theme_changed_callbacks`
- Replace callback registration with Qt signal connections
- Ensure ThemeManager is constructed early in application startup (before first `StandardWindow.__init__`)
- Update unit tests to use the singleton; update mocks to subclass `QObject` or use `pytest-qt` signal helpers
- Verify signals fire exactly once per change; no duplicate ThemeManager instances; no `TypeError` at import time

---

### HIGH — Correctness / Structural Risks

---

#### P3-H01 — `ToolManifest` class does not exist in the codebase ✅ RESOLVED

**Severity:** HIGH → ✅ RESOLVED (2026-04-26)
**Affects:** `tasks.md` T003, T003-B, T007, T041, T048; `data-model.md` §5

**Finding:**

The spec treats `ToolManifest` as an existing registry that T003 _extends_. A codebase-wide search finds zero occurrences of `ToolManifest` in any `.py` file under `src/`. The data-model §5 section describes the `ToolManifestEntry` dataclass but no implementation exists.

T003 said _"Verify that each `ToolManifest` entry includes `min_window_width` and `min_window_height` fields; add them if absent."_ — there was nothing to verify or extend. T003 must create the class from scratch.

**Canonical Decision (P3-H01 — Resolved 2026-04-26):**

> **T003 SHALL create `ToolManifestEntry` (dataclass) and `ToolManifestRegistry` (class-based) from scratch.** There is nothing to extend. The "verify fields if absent" language is replaced with "Create dataclass and registry."
>
> - `ToolManifestEntry` fields per `data-model.md` §5: `tool_id`, `display_name`, `module_path`, `class_name`, `category`, `min_window_width`, `min_window_height`, `tool_version`
> - `ToolManifestRegistry` maps `tool_id → ToolManifestEntry`; supports `register()`, `get()`, `all()`
> - Canonical file: `src/core/tool_manifest.py`
> - T003-B seeds at least two entries with non-zero `min_window_width`/`min_window_height`
> - T007 declares prerequisite: T003 complete; **T007 SHALL fail if registry contains zero entries** (not vacuously pass)
> - T041 reads but MUST NOT write to the registry

**Canonical skeleton:**

```python
# src/core/tool_manifest.py
from dataclasses import dataclass

@dataclass
class ToolManifestEntry:
    tool_id: str             # e.g. "duplicate-finder"
    display_name: str
    module_path: str         # e.g. "src.tools.analysis.duplicate_finder"
    class_name: str          # e.g. "DuplicateFinderApp"
    category: str            # e.g. "analysis"
    min_window_width: int    # default 400
    min_window_height: int   # default 300
    tool_version: str | None = None

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

**Seed entries (T003-B):**

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

**Why T007 MUST fail on an empty registry:**

> A passing result against an empty registry is a **governance illusion** — it implies "all tools meet the contract" when "all tools" is actually zero tools. This violates the Single-Source-of-Truth principle (no tools validated = no compliance evidence), breaks the T003→T007→T041→T048 dependency chain, and makes the entire audit pipeline non-auditable. A test that passes without exercising its subject is not a test — it is a lie. T007 MUST fail when the registry contains zero entries to preserve audit integrity.

**Governance Annotation — ToolManifest Creation Mandate (P3-H01 — Resolved 2026-04-26):**

> The ToolManifest is the canonical registry of all tools. The Constitution (§5) defines `ToolManifestEntry` as the authoritative description of each tool's identity, geometry constraints, and metadata. Because T003, T007, T041, and T048 all depend on this registry, its existence is a constitutional requirement. Without a real ToolManifest, contract tests become vacuous, audits become meaningless, and governance drift becomes inevitable.
>
> **Any task that assumes `ToolManifest` existed before T003 completes is in error. No downstream task (T007, T041, T048) may run before T003 is complete. Any audit against an empty manifest is a blocking issue.**

**Tasks updated:** T003, T003-B, T007, T041 (see `tasks.md`). `data-model.md` §5 updated to reflect canonical file location.

---

#### P3-H02 — `src/rfu/hub.py` is not the GUI hub; T036 targets the wrong file ✅ RESOLVED

**Severity:** HIGH → ✅ RESOLVED (2026-04-26)
**Affects:** `tasks.md` T036; `plan.md` source tree; `contracts/menu-contract.md`; all spec references to `src/rfu/hub.py` as GUI hub

**Finding:**

T036 instructed: _"Modify `src/rfu/hub.py` — add Appearance tab (FR-025): Embed `UAPAppearanceWidget` as a dedicated tab..."_

The actual `src/rfu/hub.py` contains only:
- `ValidatorNotifier` protocol
- `IdleWatcherConfig` dataclass
- Idle-timeout watcher utilities and observer registration functions
- Thread-locking (`RLock`) for notification coordination

It has **no GUI code, no `QWidget` subclass, no tabs, and no window** to embed an Appearance tab into. The live tabbed GUI hub that users interact with is `src/tabbed_hub.py`.

Governance Pass 1 (I6) and Pass 2 (N10, N11) _incorrectly corrected_ all spec references from `tabbed_hub.py` to `src/rfu/hub.py`, making the spec **less** accurate. This was a **Phase-3 constitutional misalignment**: the spec pointed at a file that is not, and never was, the GUI hub.

**Canonical Decision (P3-Q2 — Resolved 2026-04-26):**

> **The canonical GUI Hub SHALL remain `src/tabbed_hub.py`.**
>
> - All GUI-hub-related tasks (T036, FR-025, Appearance tab integration) SHALL target `src/tabbed_hub.py`.
> - `src/rfu/hub.py` SHALL retain its identity as the idle-watcher / validator-utilities module. No GUI code SHALL be added to it.
> - All spec references that point to `src/rfu/hub.py` as the GUI hub are hereby reverted to `src/tabbed_hub.py`.
> - No task SHALL attempt to migrate GUI hub functionality into `src/rfu/` during Phase 3.
> - A future migration (if desired) SHALL be explicitly scheduled in Phase 4 or Phase 5, not implicitly assumed.

**Governance rationale:**

Migrating the GUI hub into `src/rfu/` would require rewriting imports, tests, window initialization, tool-launch logic, hub-navigation logic, and FR-025 integration — a Phase-5 refactor, not a Phase-3 fix. Governance must reflect architectural truth. The GUI hub _is_ `src/tabbed_hub.py`. Governance annotations (I6, N10, N11) that overwrote that truth are superseded by this canonical decision.

**Governance Annotation — Hub Identity (P3-H02 — Resolved 2026-04-26):**

> **The GUI Hub SHALL be implemented in `src/tabbed_hub.py` unless explicitly superseded by a future migration task (Phase 4 or later).**
>
> `src/rfu/hub.py` is NOT a GUI module; it contains idle-watcher utilities only. No task SHALL implicitly relocate the GUI hub by referencing a different file path. All hub-related tasks MUST target `src/tabbed_hub.py`.
>
> **Any future contributor who modifies `src/rfu/hub.py` for GUI work MUST document the rationale as a PR comment and MUST reference an explicit migration task. No such change may be merged without reviewer sign-off.**
>
> The governance annotations I6 (from Pass 1) and N10/N11 (from Pass 2) that mandated `src/rfu/hub.py` as the GUI hub are hereby superseded by this decision. Pass 3 is the authoritative record. Historical annotations in speckit-analysis-report.md and speckit-analysis-report-pass2.md are retained as-is for auditability but are no longer operative.

**Migration notes for developers:**

- Do **not** modify `src/rfu/hub.py` for GUI work — it is and SHALL remain an idle-watcher utility module.
- All GUI hub changes (including FR-025 Appearance tab) belong in `src/tabbed_hub.py`.
- If future refactoring moves the hub into `src/rfu/`, it must be explicitly planned, scheduled, governed, and reviewed — for Phase 3, no relocation occurs.

**Tasks updated:** T036 retargeted to `src/tabbed_hub.py` (see `tasks.md`). Plan.md source tree updated. Hub Path Check in governance reviewer checklist updated.

---

#### P3-H03 — `ThemeManager.instance()` does not exist ✅ RESOLVED

**Severity:** HIGH → ✅ RESOLVED (2026-04-26, resolved together with P3-C01)
**Affects:** `tasks.md` T031, T032, T033, T042; all call sites using `ThemeManager.instance()`

**Finding:**

T031 calls `ThemeManager.instance().register(self)`. T032 calls `ThemeManager.instance().unregister(self)`. T033 calls `ThemeManager.instance().uap_font_changed`. T042 adds `register/unregister/registered_windows` to `ThemeManager`.

The actual `ThemeManager` class has no `instance()` classmethod. It is a pure static utility class, not a singleton.

**Resolution:** P3-C01 canonical decision mandates that `ThemeManager` becomes a `QObject`-based singleton. T042 adds `_instance = None` class variable and `instance()` classmethod returning the singleton. All T031/T032/T033/T042 call patterns using `ThemeManager.instance()` are now valid. See P3-C01 resolution above for full skeleton.

---

#### P3-H04 — `profile_id` UUID schema constraint contradicts `"factory_default"` sentinel ✅ RESOLVED

**Severity:** HIGH → ✅ RESOLVED (2026-04-26)
**Resolved by:** P3-Q3 (Profile Identity Rule)
**Affects:** `contracts/appearance-profile.md` schema, INV-002, INV-005; `tasks.md` T004, T018-B, T024

**Finding:**

The spec simultaneously required `profile_id` to be a UUID4 (`format: uuid`, INV-005) AND the factory-default profile to use `profile_id = "factory_default"` (INV-002, T018-B, T024). This was a hard schema-level contradiction: `from_json()` on the factory-default profile would raise `ValidationError`, T004 round-trip tests would fail for the wrong reason, and T018-B/T024 would become unimplementable.

**Canonical Decision (P3-Q3 — Resolved 2026-04-26):**

> **`profile_id` SHALL accept either a UUID4 OR the reserved sentinel `"factory_default"`.**
>
> - The factory-default profile is constitutionally exempt from UUID4 constraints.
> - All user-created profiles MUST use UUID4 identifiers.
> - No migration is required — no existing profile records use `"factory_default"` as a UUID.

**Schema fix (authoritative):**

```json
"profile_id": {
  "type": "string",
  "oneOf": [
    { "format": "uuid" },
    { "enum": ["factory_default"] }
  ]
}
```

**Invariant fixes:**
- **INV-005 (updated):** `profile_id` MUST be a UUID4 for all user-created profiles. The factory-default profile SHALL use the reserved sentinel `"factory_default"` and is exempt from the UUID4 requirement.
- **INV-002 (clarified):** The factory-default profile SHALL always exist and SHALL use `profile_id = "factory_default"`. The sentinel is the stable, constitutional identity of this profile and SHALL NOT be replaced with a UUID.

**Constitutional Annotation — `profile_id` Sentinel Exception (P3-H04 — Resolved 2026-04-26):**

> **The factory-default profile SHALL use the reserved sentinel `"factory_default"` as its `profile_id`.** This sentinel is exempt from UUID4 constraints. All user-created profiles MUST use UUID4 identifiers. This rule is constitutional because the factory-default profile is a structural singleton whose identity must be stable, human-readable, and non-colliding across all installations.
>
> **Any contributor who attempts to replace `"factory_default"` with a UUID, enforce UUID4 validation on this sentinel, or remove the `oneOf` exception MUST document the rationale as a PR comment and update INV-002 and INV-005 accordingly. No such change may be merged without reviewer sign-off.**

**Reviewer checklist (P3-H04 closure):**

Reviewers MUST verify: (1) JSON schema `profile_id` uses `oneOf` allowing `"factory_default"`; (2) JSON schema still enforces UUID4 for all other values; (3) INV-005 updated to reflect sentinel exception; (4) INV-002 consistent with sentinel as constitutional identity; (5) T018-B seeds `"factory_default"` and no code alters it; (6) T024 deletion guard checks `profile_id == "factory_default"` (not `profile_name`); (7) T004 round-trip test passes for factory-default profile; (8) no code attempts to validate `"factory_default"` as a UUID.

**Artifacts updated:** `contracts/appearance-profile.md` (schema, INV-002, INV-005, governance annotation); `tasks.md` T004, T018-B, T024.

---

#### P3-M03 — `src/__version__.py` does not exist; T008/T040 reference it ✅ RESOLVED

**Severity:** MEDIUM → ✅ RESOLVED (2026-04-26)
**Affects:** `tasks.md` T008, T040; `quickstart.md`; `contracts/menu-contract.md` About Dialog

**Finding:**

T008 and T040 referenced `src/__version__.py` as the source of the suite version for the About dialog. That file does not exist. The canonical version is `APP_VERSION` in `src/core/constants.py`, accessible as `from src.core.constants import APP_VERSION`.

**Canonical Decision (P3-Q4 — Resolved 2026-04-26):**

> **The canonical suite version SHALL be sourced from `APP_VERSION` in `src/core/constants.py`.**
>
> - No `src/__version__.py` file SHALL be created in Phase 3.
> - T008 SHALL reference `from src.core.constants import APP_VERSION` (not `src/__version__.py`).
> - T040 SHALL reference `from src.core.constants import APP_VERSION` (not `src/__version__.py`).
> - Any other task, contract, or quickstart reference to `src/__version__.py` SHALL be updated to `APP_VERSION`.

**Rationale (Option C over A/B):**
- Option A (create `__version__.py`) introduces a second version source; risks divergence with `APP_VERSION` unless carefully maintained
- Option B (`from src import __version__`) is still indirect; less explicit than the constant itself
- Option C (`APP_VERSION` directly) is the actual source of truth, requires zero new files, and aligns with the existing architecture

**Constitutional Annotation — Canonical Version Source (P3-M03 — Resolved 2026-04-26):**

> **The suite version SHALL be defined in a single location: `src.core.constants.APP_VERSION`.** This constant is the authoritative version source for About dialogs, CLI version output, logging, diagnostics, and documentation. No additional version files SHALL be created unless explicitly authorized in a future governance phase.
>
> **Any contributor who references `src/__version__.py` or introduces a second version source MUST document the rationale as a PR comment and update this finding. No such change may be merged without reviewer sign-off.**

**Reviewer checklist (P3-M03 closure):**

Reviewers MUST verify: (1) no reference to `src/__version__.py` in any task; (2) no reference to `src/__version__.py` in any contract; (3) no reference to `src/__version__.py` in `quickstart.md`; (4) T008 reads version from `APP_VERSION`; (5) T040 reads version from `APP_VERSION`; (6) About dialog displays `APP_VERSION`; (7) no duplicate version sources exist; (8) version bump workflow still targets `APP_VERSION` only.

**Tasks updated:** T008 and T040 (see `tasks.md`).

---

### LOW — Advisory

---

#### P3-L01 — T032 says "Modify `closeEvent`" but `StandardWindow` has no `closeEvent` ✅ RESOLVED

**Severity:** LOW → ✅ RESOLVED (2026-04-26)
**Resolved by:** P3-L01 (Spec-Language Clarification)
**Affects:** `tasks.md` T032

**Finding:**

T032 instructed: _"Modify `src/gui/standard_window.py` — `closeEvent`."_ The current `StandardWindow` has no `closeEvent` override. The method will be **added** (inherited Qt default is to call `super().closeEvent(event)` implicitly).

This was not a logic error — TDD tasks routinely ADD methods to files they "modify." However, the word "Modify" could confuse an implementer into searching for an existing `closeEvent` to edit, and the spec did not define the method signature, lifecycle ordering, or how UAP tracking fields are accessed at close time.

**Canonical Decision (P3-L01 — Resolved 2026-04-26):**

> **T032 SHALL instruct the implementer to *add* `StandardWindow.closeEvent(self, event: QCloseEvent) -> None` rather than "modify" it.**
>
> The task SHALL explicitly define: the method signature, the required call order, how UAP tracking fields are accessed, and the requirement to call `super().closeEvent(event)` last.

**Corrected T032 implementation (authoritative):**

```python
def closeEvent(self, event: QCloseEvent) -> None:
    # 1. Read UAP tracking fields set by UAPService.apply()
    font_family = self._uap_font_family
    font_size = self._uap_font_size
    browse_root = self._uap_browse_root

    # 2. Read geometry live from the window
    g = self.geometry()
    x, y, w, h = g.x(), g.y(), g.width(), g.height()

    # 3. Persist last-used settings
    UAPService().save_last_used(w, h, x, y, font_family, font_size, browse_root)

    # 4. Unregister window from ThemeManager
    ThemeManager.instance().unregister(self)

    # 5. Call superclass implementation
    super().closeEvent(event)
```

**Canonical lifecycle table (complete `__init__` → `closeEvent` ordering):**

| Step | Method | Action |
|------|--------|--------|
| 1 | `__init__()` | Entry point |
| 2 | `_setup_window()` | Placeholder resize (non-authoritative) |
| 3 | `_setup_ui()` | Widget construction |
| 4 | `UAPService.apply()` **(T031)** | Authoritative geometry, font, `_uap_*` fields set |
| 5 | `_create_status_bar()` | Status bar |
| 6 | `show()` | Window visible at UAP geometry |
| 7 | `closeEvent()` **(T032)** | Reads `_uap_*` fields; live geometry; persists; unregisters |

**Constitutional Annotation — Spec-Language Clarification (P3-L01 — Resolved 2026-04-26):**

> **Tasks SHALL use "Add" when introducing new methods and "Modify" only when editing existing methods.** This rule prevents implementer confusion and ensures task instructions accurately reflect the state of the codebase. `StandardWindow.closeEvent()` is a required method and SHALL be added by T032.
>
> **Any contributor who changes the call order within `closeEvent()` (e.g. calling `super()` before `unregister()`, or reading font from `self.font()`) MUST document the rationale as a PR comment. No such change may be merged without reviewer sign-off.**

**Reviewer checklist (P3-L01 closure):**

Reviewers MUST verify: (1) T032 heading uses "Add `closeEvent`" not "Modify"; (2) `StandardWindow` contains a `closeEvent(self, event: QCloseEvent) -> None` override; (3) method reads `_uap_font_family`, `_uap_font_size`, `_uap_browse_root`; (4) geometry read live from `self.geometry()`; (5) `save_last_used()` called with correct parameter order `(w, h, x, y, font_family, font_size, browse_root)`; (6) `ThemeManager.instance().unregister(self)` called before `super()`; (7) `super().closeEvent(event)` called last; (8) no `self.font()` read; (9) no `UAPService().get_active_settings()` at close. **Any deviation in call order or attribute source is a blocking issue.**

**Tasks updated:** T032 heading and body (see `tasks.md`).

---

#### P3-L02 — Governance artifact integrity defects (D1–D3, Q7–Q8) ✅ RESOLVED

**Severity:** LOW (governance hygiene) → ✅ RESOLVED (2026-04-26)
**Resolved by:** P3-L02 (Governance Artifact Integrity Sweep)
**Affects:** `speckit-analysis-report-pass3.md` (D1–D3); `speckit-analysis-report-pass2.md` (Q7, Q8)

**Finding:**

Five defects were identified in the governance reporting layer itself after Phase-3 finding resolution was complete:

- **D1** — Codebase delta table row for `MenuManager` File menu structure still showed `⚠️ See P3-M01` despite P3-M01 being fully RESOLVED.
- **D2** — Stray literal `fss` appeared between the P3-H04 `---` separator and the `#### P3-M03` heading — artifact noise prohibited in governance documents.
- **D3** — Executive summary table missing two resolution rows: `P3-Q5 resolved this pass` and `P3-L01 resolved this pass`; LOW row did not reflect RESOLVED state.
- **Q7** — Two sub-decisions left open: pre-population of `uap_exempt` set; T041 vs T048 ordering. Neither had a canonical ruling.
- **Q8** — Q8 decision text ended with two open options; N13 advisory recorded the constitutional order but the Q8 question body was never closed.

**Canonical Decisions (P3-L02 — Resolved 2026-04-26):**

> **D1:** All delta table rows MUST reflect the final resolved status of Pass-3 findings. No `⚠️` markers are permitted after a finding is RESOLVED.
>
> **D2:** Artifact noise (stray text, placeholder fragments) is prohibited in governance documents. It creates ambiguity in diff-based audits.
>
> **D3:** Executive summaries MUST include a row for every finding and every Q-class question resolved in the pass, including advisory and LOW-severity items.
>
> **Q7-A:** No pre-populated `uap_exempt` list SHALL exist in Phase-3. All tools are assumed to subclass `StandardWindow` unless explicitly exempted during the Phase-4 UX harmonization sweep.
>
> **Q7-B:** T041 SHALL remain an independent headless audit pass. T048 SHALL depend on T041 but SHALL NOT subsume it.
>
> **Q8:** `menu-contract.md` SHALL NOT pre-reserve Phase-2 menu positions in Phase-3. The constitutional 7-menu order is recorded via N13 advisory. Phase-2 menus SHALL be introduced only when Phase-2 begins.

**Constitutional Annotation — Governance Artifact Integrity (P3-L02 — Resolved 2026-04-26):**

> Governance artifacts (analysis reports, delta tables, executive summaries) SHALL be kept in strict alignment with resolved findings. No stale markers, missing rows, or ambiguous placeholders are permitted. All Q-class questions MUST be explicitly closed with a canonical decision before the phase closes. This rule prevents governance drift originating from the documentation layer.

**Reviewer Checklist (P3-L02 closure):**

Reviewers MUST verify: (1) no `⚠️` markers remain in any delta table row where the finding is RESOLVED; (2) no stray artifact text appears between section headings; (3) executive summary includes a row for every resolved finding and Q-class item; (4) Q7-A and Q7-B decisions are recorded in `speckit-analysis-report-pass2.md`; (5) Q8 decision is recorded in `speckit-analysis-report-pass2.md`; (6) no unresolved Q-class items remain in any Pass report; (7) all governance artifacts reflect Phase-3 final state.

**Artifacts updated:** `speckit-analysis-report-pass3.md` (D1–D3); `speckit-analysis-report-pass2.md` (Q7, Q8).

---

## Open Questions for Implementation — Pass 3

All five questions raised in this pass have been resolved. The resolutions are recorded below for audit trail purposes.

---

### P3-Q1 — How does `ThemeManager` gain `pyqtSignal` without being a `QObject`? ✅ RESOLVED

**Decision (2026-04-26):** Option A — **`ThemeManager` SHALL subclass `QObject` and become a singleton.**

**Canonical Decision:**

> `ThemeManager` SHALL subclass `QObject`. Class-level `pyqtSignal` attributes SHALL be added as required by T042. A classmethod `instance()` SHALL return the single global instance. All tasks (T025, T033, T042, T043) SHALL reference `ThemeManager.instance()`. BC-007 and BC-008 remain valid. The existing callback list is deprecated and removed.

See P3-C01 above for the full skeleton, governance annotation, and migration notes.

**Rationale for Option A over alternatives:**
- Option B (separate `UAPSignalBus`) creates two classes with overlapping authority — reviewers will challenge why ThemeManager is not the canonical source, and BC-007/BC-008 would need rewriting.
- Option C (module-level `_signal_emitter`) is a fragile workaround with no Qt lifecycle guarantees.
- Option A is reviewer-proof, architecturally clean, future-proof for additional signals, and requires zero contract rewrites.

---

### P3-Q2 — Which file is the live GUI hub that T036 must modify? ✅ RESOLVED

**Decision (2026-04-26):** Option A — **The canonical GUI Hub SHALL remain `src/tabbed_hub.py`.**

**Canonical Decision:**

> T036 and all GUI-hub tasks SHALL target `src/tabbed_hub.py`. `src/rfu/hub.py` retains its identity as the idle-watcher utility module. Governance annotations I6/N10/N11 that mandated `src/rfu/hub.py` as the hub are superseded. No hub migration occurs during Phase 3. Any future migration is explicitly deferred to Phase 4 or later.

See P3-H02 above for the full canonical decision, governance annotation, and migration notes.

**Rationale for Option A over alternatives:**
- Option B (migrate hub to `src/rfu/`) would require rewriting imports, tests, launch logic, and FR-025 integration — a Phase-5 refactor, not a Phase-3 fix.
- Option C (extend `src/rfu/hub.py` with GUI code) mixes utility protocols with GUI window code in one file — a design violation.
- Option A preserves architectural truth, controls scope, and requires zero infrastructure changes.

---

### P3-Q3 — Is `"factory_default"` a valid `profile_id`, or must all IDs be UUID4? ✅ RESOLVED

**Decision (2026-04-26):** Option C-variant — **`profile_id` accepts UUID4 OR the reserved sentinel `"factory_default"` via `oneOf` schema.**

**Canonical Decision:**

> `profile_id` SHALL accept either a valid UUID4 OR the exact string `"factory_default"`. The factory-default profile is constitutionally exempt from UUID4 constraints. All user-created profiles MUST use UUID4 identifiers. The schema has been updated to a `oneOf` form that enforces both rules simultaneously. See P3-H04 above for the full resolution, constitutional annotation, and reviewer checklist.

**Rationale for `oneOf` over Options A/B:**
- Option A (relax to plain `"type": "string"`) removes all format enforcement for user-created profiles — any non-UUID string would pass schema validation, creating a weak contract
- Option B (fixed magic UUID) is less readable, conflicts with the reuse-prohibition in INV-005, and would require updating T018-B and T024 with a hardcoded constant
- `oneOf` is reviewer-proof: UUID4 is still strictly enforced for all user-created profiles; only `"factory_default"` is excepted

---

### P3-Q4 — Create `src/__version__.py` or update references? ✅ RESOLVED

**Decision (2026-04-26):** Option C — **Use `APP_VERSION` from `src/core/constants.py` directly; no new file.**

**Canonical Decision:**

> The canonical suite version is `APP_VERSION` in `src/core/constants.py`. All task and contract references to `src/__version__.py` SHALL be updated. No new file is created. See P3-M03 above for the full resolution, constitutional annotation, and reviewer checklist.

**Rationale for Option C over A/B:**
- Option A (`__version__.py`) introduces a second version source with divergence risk
- Option B (`from src import __version__`) is indirect and still proxied
- Option C is the actual source of truth, requires no new files, and matches the architecture

---

### P3-Q5 — How does `StandardWindow.closeEvent` access UAP tracking fields? ✅ RESOLVED

**Severity:** ADVISORY → ✅ RESOLVED (2026-04-26)
**Resolved by:** P3-Q5 (UAP Tracking Field Rule)
**Affects:** `tasks.md` T031, T032

**Context:** T032 calls `UAPService().save_last_used(..., font_family, font_size, browse_root)`. These are not QMainWindow attributes. T031 (`apply()`) sets the geometry and font; T032 (`closeEvent`) must capture them. Without an explicit lifecycle rule, each implementer could choose a different strategy, producing divergent and untestable behavior.

**Canonical Decision (P3-Q5 — Resolved 2026-04-26):**

> **`StandardWindow` SHALL store UAP-tracking fields as instance attributes during `UAPService.apply()`, and `closeEvent()` SHALL read these attributes.**
>
> These attributes SHALL be:
> - `self._uap_font_family`
> - `self._uap_font_size`
> - `self._uap_browse_root`
>
> Geometry SHALL be read live from the window (`self.geometry()`).

This is **Option A** — the only Phase-3-correct choice.

**Why Option A over alternatives:**
- **Deterministic and testable:** T004, T018, T021, T032 all become deterministic; unit tests can assert exact values; no Qt-dependent behavior leaks into persistence logic.
- **Matches the UAP lifecycle:** `apply()` is the authoritative moment when UAP settings are applied; `closeEvent()` is the authoritative moment when they are persisted; tracking fields bridge these two lifecycle points.
- **Avoids Qt coupling (Option B rejected):** Option B fails if a widget overrides the font, a stylesheet overrides the font, a theme change occurs mid-session, or a dialog temporarily changes the font.
- **Avoids store-stale risk (Option C rejected):** Option C fails if the user changed font mid-session, the store is stale, or the store was not updated after a UI change.

**Canonical implementation requirements:**

*T031 — `apply()` SHALL store:*
```python
self._uap_font_family = font_family
self._uap_font_size = font_size
self._uap_browse_root = browse_root
```
These MUST be set after applying the font and directory.

*T032 — `closeEvent()` SHALL read:*
```python
font_family = self._uap_font_family
font_size = self._uap_font_size
browse_root = self._uap_browse_root
g = self.geometry()
x, y, w, h = g.x(), g.y(), g.width(), g.height()
UAPService().save_last_used(w, h, x, y, font_family, font_size, browse_root)
```

**Constitutional Annotation — UAP Tracking Field Rule (P3-Q5 — Resolved 2026-04-26):**

> **`UAPService.apply()` SHALL store UAP-tracking fields on the window instance.** `StandardWindow.closeEvent()` SHALL read these fields to persist the last-used UAP state. Geometry SHALL be read live from the window; font and browse-root SHALL be read from tracking fields. This rule is constitutional because UAP persistence must reflect the user's actual session state, not Qt-derived or store-derived approximations.
>
> **Any contributor who reads font or browse-root via `self.font()`, `self.browse_root`, or `UAPService().get_active_settings()` in `closeEvent` instead of the designated tracking attributes MUST document the rationale as a PR comment and update this finding. No such change may be merged without reviewer sign-off.**

**Reviewer checklist (P3-Q5 closure):**

Reviewers MUST verify: (1) `apply()` sets `_uap_font_family`, `_uap_font_size`, `_uap_browse_root` as instance attributes; (2) these fields are set after applying font and directory; (3) `closeEvent()` reads these three attributes; (4) geometry is read live via `self.geometry()`; (5) no code re-reads UAP state from the store at close; (6) no code reads font from `self.font()` in `closeEvent`; (7) no code infers `browse_root` from UI state; (8) T031 and T032 both explicitly specify this lifecycle. **Any deviation from the tracking-attribute pattern is a blocking issue.**

**Tasks updated:** T031 (instance attributes documented in `apply()` spec), T032 (reads tracking attributes; geometry live from `self.geometry()`).

---

## Governance Reviewer Checklist — Pass 3

- **ThemeManager Identity Checklist (P3-C01 — RESOLVED):** ThemeManager SHALL be a `QObject` subclass. Reviewers SHALL verify: (1) class inherits from `QObject`; (2) all signals declared as class attributes; (3) singleton `instance()` method exists and is used everywhere; (4) no callback lists or ad-hoc observer patterns remain; (5) no direct instantiation (`ThemeManager()`) anywhere in the codebase; (6) all signal connections use `ThemeManager.instance()`; (7) no other class emits UAP signals. **`pyqtSignal` on a non-`QObject` raises `TypeError` at import time and will break all tests — zero exceptions.**

- **ToolManifest Creation Check (P3-H01 — RESOLVED):** T003 SHALL create `ToolManifestEntry` dataclass and `ToolManifestRegistry` in `src/core/tool_manifest.py`. Reviewers SHALL verify: (1) both classes exist before T007 runs; (2) registry `all()` returns a list; (3) T003-B seeds ≥ 2 entries with non-zero `min_window_width`/`min_window_height`; (4) T007 fails (not passes vacuously) when registry is empty; (5) T041 reads but never writes to the registry. **Any audit against an empty manifest is a blocking issue.**

- **Hub Identity Check (P3-H02 — RESOLVED 2026-04-26):** The canonical GUI hub is `src/tabbed_hub.py`. Reviewers SHALL verify: (1) T036 targets `src/tabbed_hub.py`, not `src/rfu/hub.py`; (2) `src/rfu/hub.py` contains only idle-watcher utilities and no GUI code; (3) plan.md source tree lists `src/tabbed_hub.py` as the MODIFY target; (4) no task references `src/rfu/hub.py` for GUI work; (5) no implicit hub migration into `src/rfu/` occurs during Phase 3; (6) governance annotations I6/N10/N11 are treated as superseded by P3-H02. **A task that targets `src/rfu/hub.py` for GUI work will embed the Appearance tab in a non-GUI module — zero exceptions.**

- **`profile_id` Sentinel Exception Check (P3-H04 — RESOLVED 2026-04-26):** The `oneOf` schema exception for `"factory_default"` is in place. Reviewers SHALL verify: (1) JSON schema `profile_id` field uses `oneOf` allowing `"factory_default"` and enforcing UUID4 for all other values; (2) INV-005 reflects the sentinel exception; (3) T004 round-trip test passes for the factory-default profile; (4) T018-B seeds `"factory_default"` without modification; (5) T024 deletion guard checks `profile_id == "factory_default"`. **Any code that validates `"factory_default"` as a UUID4 is a blocking issue.**

- **Version Source Check (P3-M03 — RESOLVED 2026-04-26):** `APP_VERSION` in `src/core/constants.py` is the sole canonical version source. Reviewers SHALL verify: (1) no reference to `src/__version__.py` remains in any task or contract; (2) T008 and T040 import `APP_VERSION` from `src.core.constants`; (3) About dialog displays `APP_VERSION`; (4) no duplicate version sources exist. **Any `src/__version__.py` reference is a blocking issue.**

- **closeEvent Instance Attributes (P3-Q5 — RESOLVED 2026-04-26):** `apply()` sets `_uap_font_family`, `_uap_font_size`, `_uap_browse_root` after applying font and directory; `closeEvent()` reads them; geometry read live via `self.geometry()`. Reviewers SHALL verify: (1) all three instance attributes set in `apply()`; (2) `closeEvent()` reads all three; (3) no `self.font()` or store re-read in `closeEvent()`; (4) T031 spec explicitly documents these attributes. **Any deviation from the tracking-attribute pattern is a blocking issue.**

- **File Menu Structure Check (P3-M01 — RESOLVED 2026-04-26):** `_create_file_menu()` rebuilt to unconditional 7-slot model. Reviewers SHALL verify: (1) no `window_type` conditional in `_create_file_menu()`; (2) all 7 slots present in contract order; (3) `"exit"` always enabled; (4) Import before Export; (5) no `print_document` action; (6) all action IDs match canonical table; (7) legacy IDs `"save_file"`, `"export_data"`, `"import_data"` absent; (8) `enable_file_action()` API implemented. **Any conditional slot presence is a blocking issue.**

- **`apply()` Lifecycle Ordering Check (P3-M02 — RESOLVED 2026-04-26):** `UAPService.apply()` is the authoritative geometry source. Reviewers SHALL verify: (1) T031 calls `UAPService().apply()` after `_setup_ui()` and before `_create_status_bar()`; (2) no `resize()` or `move()` follows `apply()` in `__init__`; (3) `_setup_window()` `resize()` annotated as non-authoritative; (4) window shown at UAP geometry. **Any resize after `apply()` in `__init__` is a blocking issue.**

---

## Phase-3 Closure Artifacts

Phase-3 is **COMPLETE** as of 2026-04-26. The following closure artifacts are now part of the canonical record:

| Artifact | File | Purpose |
|----------|------|---------|
| Governance Summary | `phase3-governance-summary.md` | Ledger-ready close-the-books record; constitutional rules list |
| UAP Lifecycle Diagram | `uap-lifecycle-diagram.md` | Visual lifecycle map; reviewer watchlist; signal flow |

---

## Pass 3 Findings Summary Table

| ID | Severity | Artifact | Summary |
|----|----------|----------|---------|
| **Q3** | ✅ RESOLVED | T018–T032 | `UAPService` is stateless; all state in `PreferencesStore` |
| **P3-C01** | ✅ RESOLVED | `themes.py`, T042, T033, T025 | `ThemeManager` → `QObject` singleton; signals + `instance()` added; T042/T043/T033/BC-007/BC-008 updated |
| **P3-H01** | ✅ RESOLVED | `tasks.md` T003/T007/T041, `data-model.md` §5 | `ToolManifestEntry` + `ToolManifestRegistry` to be created in `src/core/tool_manifest.py`; T003 rewritten; T007 fails on empty registry |
| **P3-H02** | ✅ RESOLVED | `tasks.md` T036, `plan.md` | T036 retargeted to `src/tabbed_hub.py`; hub identity governance annotation added; I6/N10/N11 superseded |
| **P3-H03** | ✅ RESOLVED | `themes.py`, T031–T033 | `ThemeManager.instance()` added by P3-C01 resolution |
| **P3-H04** | ✅ RESOLVED | `appearance-profile.md`, T004, T018-B, T024 | `"factory_default"` sentinel accepted via `oneOf` schema; INV-002/INV-005 updated; constitutional annotation added; no migration required |
| **P3-M01** | ✅ RESOLVED | `menu_manager.py`, T039 | File menu rebuilt to unconditional 7-slot model; all conditionals removed; `print_document` removed; canonical action IDs applied; `enable_file_action()` API added |
| **P3-M02** | ✅ RESOLVED | `standard_window.py`, T031, T021 | `UAPService.apply()` is authoritative geometry; canonical `__init__` lifecycle documented; `_setup_window()` resize annotated as non-authoritative placeholder |
| **P3-M03** | ✅ RESOLVED | T008, T040, quickstart | `APP_VERSION` in `src/core/constants.py` is canonical; no `src/__version__.py` to be created |
| **P3-L01** | ✅ RESOLVED | `tasks.md` T032 | T032 language corrected: "Modify" → "Add `StandardWindow.closeEvent`"; method signature, 5-step call order, UAP tracking field access, and lifecycle table fully specified |
| **P3-L02** | ✅ RESOLVED | `speckit-analysis-report-pass3.md`, `speckit-analysis-report-pass2.md` | Governance artifact integrity sweep: D1 (stale ⚠️), D2 (stray `fss`), D3 (missing exec summary rows), Q7 (T041/T048 scope), Q8 (Phase-2 menu positions) — all corrected |
