# Specification Analysis Report — 007-ui-harmonization

**Run date:** 2026-04-25  
**Feature:** `007-ui-harmonization` — Unified Look & Feel (Phase 1)  
**Constitution:** v1.37.0 (`/.specify/memory/constitution.md`)  
**Artifacts analyzed:**
- `specs/007-ui-harmonization/spec.md`
- `specs/007-ui-harmonization/plan.md`
- `specs/007-ui-harmonization/tasks.md`
- `specs/007-ui-harmonization/data-model.md`
- `specs/007-ui-harmonization/contracts/uap-preferences.md`
- `specs/007-ui-harmonization/contracts/menu-contract.md`
- `specs/007-ui-harmonization/contracts/appearance-profile.md`
- `specs/007-ui-harmonization/quickstart.md`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| FR coverage | 26 / 26 (100%) |
| Total findings | 17 |
| Resolved (this session) | 20 (I1, C1, I2, I3, I4, I5, I6, I7, I8, I9, U1, U2, U3, U4, U5, G1, G2, G3, A1, A2) |
| Remaining open | 0 |
| HIGH severity remaining | 0 |
| MEDIUM severity remaining | 0 |
| LOW severity remaining | 0 |

Phase 1 scope is intentionally narrower than the full constitution: 5-menu topology vs §7.2's 7 menus, and no Reports/Window menus yet. These are **known planned gaps**, not findings.

---

## FR Coverage Table

| FR | Title | US | Covered by tasks | Status |
|----|-------|----|------------------|--------|
| FR-001 | UAP global preference store | US1 | T013–T018 | ✅ |
| FR-002 | Factory defaults | US1 | T014, T006 | ✅ |
| FR-003 | Last-used mode | US1 | T017–T020 | ✅ |
| FR-004 | Predefined mode | US1 | T020, T024 | ✅ |
| FR-005 | Multiple profiles | US1 | T024 | ✅ |
| FR-006 | AppearanceProfile schema | US1 | T015–T016 | ✅ |
| FR-007 | No `os.chdir()` | US1 | T029 guard | ✅ |
| FR-008 | Standard menu topology | US2 | T039–T041 | ✅ |
| FR-009 | Tool-subclassed Preferences dialog | US1 | T034–T035 | ✅ |
| FR-010 | Per-tool UAP overrides | US1 | T003, T021 | ✅ |
| FR-011 | Cross-session directory propagation | US1 | T019, T032 | ✅ |
| FR-012 | Dependency version lock | US3 | T044 | ✅ |
| FR-013 | Automated dependency audit | US3 | T045 | ✅ |
| FR-014 | Framework docs | US4 | T046 | ✅ |
| FR-015 | Packaging docs | US4 | T047 | ✅ |
| FR-016 | ToolManifest-only enumeration | US2 | T007, T041 | ✅ |
| FR-017 | No hidden/duplicate menus | US2 | T037 | ✅ |
| FR-018 | Font picker dialog | US1 | T028, T010 | ✅ |
| FR-019 | Directory picker dialog | US1 | T029, T011 | ✅ |
| FR-020 | Theme signal bus | US2 | T042 | ✅ |
| FR-021 | Font propagation to all open windows | US1 | T033, T009 | ✅ |
| FR-022 | Geometry propagation to open windows | US2 | T042–T043 | ✅ |
| FR-023 | Window position: center and cascade | US1 | T023 | ✅ |
| FR-024 | File menu action labeling | US2 | T039 | ✅ |
| FR-025 | Hub Appearance tab | US1 | T036 | ✅ |
| FR-026 | Import profile | US1 | T026 | ✅ |

---

## Constitution Alignment

| §  | Rule | Phase 1 compliance |
|----|------|--------------------|
| §7.2 | 7 top-level menus | **Planned gap** — Phase 1 ships 5 menus; Reports and Window deferred to Phase 2. T007/T041 use subset validation (C1 fix applied). |
| §7.3 | File menu structure | ✅ — menu-contract.md enforces canonical topology |
| §7.4 | Preferences dialog | ✅ — FR-009, T034–T035 |
| §8 | Font propagation | ✅ — FR-021, T033; full widget iteration now specified (U1 resolved) |
| §9 | Dependency lock | ✅ — FR-012, T044 |
| §10 | UAP profile system | ✅ — FR-001–FR-006, T013–T026 |

---

## Findings Table

### Resolved Findings

| ID | Severity | Category | Summary | Resolution |
|----|----------|----------|---------|------------|
| **I1** | HIGH | Inconsistency | FR-024 spec body conflicted with C2 clarification and menu-contract.md — said to rename inapplicable actions | **RESOLVED** — spec.md FR-024 replaced with final harmonized 3-section text; menu-contract.md updated; T039 updated with `enable_file_action(action_id, label=None)` API |
| **C1** | HIGH | Constitution | FR-008 contracts 5 menus; §7.2 defines 7 — no safeguard against freezing the Phase-1 structure | **RESOLVED** — T007 updated to use `required.issubset(actual_labels)`; T041 has Phase-1 Boundary Note; Governance Reviewer Checklist item added |
| **I2** | HIGH | Inconsistency | T003 added `window_x/y` to `ToolManifest` — wrong; these are user state, not tool declarations | **RESOLVED** — T003 rewritten to verify `min_window_width`/`min_window_height` only; data-model §5 boundary note added; Reviewer Checklist item added |
| **I3** | HIGH | Inconsistency | BC-006 used `record_last_used(window: QMainWindow)`; tasks T005/T019/T032 used `save_last_used(7 params)` | **RESOLVED** — BC-006 rewritten with canonical 7-primitive signature; Qt-dependent variant removed; T005 canonical-test note added; Reviewer Checklist item added |
| **I4** | MEDIUM | Inconsistency | T029 called `set_geometry(...)` for directory — wrong API; `set_geometry` is geometry-only | **RESOLVED** — BC-006b/BC-006c added to uap-preferences.md; T011/T025/T029 corrected to use `set_directory(path)`; Contract Integrity Rules blockquote added; Reviewer Checklist item added |
| **I5** | MEDIUM | Inconsistency | `tests/contract/gui/` path in plan.md and all contract "Tested by" headers did not match actual filesystem `tests/contracts/` (with 's') | **RESOLVED** — Search-replaced `tests/contract/` → `tests/contracts/` in plan.md, menu-contract.md, uap-preferences.md, quickstart.md, research.md (7 occurrences); Path Consistency Check added to Governance Reviewer Checklist in tasks.md |
| **I6** | MEDIUM | Inconsistency | plan.md source tree listed `src/tabbed_hub.py` — file does not exist; actual file is `src/rfu/hub.py`; residual `tests/contract/` (no 's') also present in source tree block | **RESOLVED** — plan.md source tree updated to `src/rfu/hub.py`; residual `tests/contract/` in source tree block corrected to `tests/contracts/`; Governance Annotation added to plan.md; Hub Path Check added to Governance Reviewer Checklist in tasks.md |
| **I7** | HIGH | Inconsistency | FR-013 stated audit script MUST exit non-zero when a platform conditional evaluates to `False` on the current machine — making the script unusable on Linux/macOS. *(Severity upgraded to HIGH from MEDIUM in initial triage.)* | **RESOLVED** — FR-013 rewritten with 3-rule structure: (1) skip by default when condition is `False`; (2) non-zero exit only under explicit `--platform=<value>` override; (3) non-conditional lines always evaluated. Clarification paragraph and Governance Annotation added to spec.md FR-013. Platform Condition Check added to Governance Reviewer Checklist in tasks.md. |
| **I8** | MEDIUM | Inconsistency | Migration table in appearance-profile.md Version 2 row claimed to add `window_x`/`window_y`, but both fields are already in the Version 1 `"required"` array — a self-contradiction that would corrupt migration logic and schema version tests. | **RESOLVED** — Version 2 row removed; Version 1 entry updated to clarify all fields including `window_x`/`window_y` are present from the initial schema; Governance Annotation added to appearance-profile.md; Migration Table Normalization Rule added inline; Migration Table Consistency Check added to Governance Reviewer Checklist in tasks.md. |
| **I9** | MEDIUM | Inconsistency | T003 only verified `min_window_width`/`min_window_height` field existence on `ToolManifest`; no task seeded actual manifest entries with values before T041's audit, making audit results nondeterministic. | **RESOLVED** — T003-B sub-step added to tasks.md seeding two canonical manifest entries (`example_tool_a`: 480×320, `example_tool_b`: 600×400); Governance Annotation added to T003 block; T041 clarification added stating it MUST NOT seed data; Manifest Seeding Check added to Governance Reviewer Checklist in tasks.md. |
| **U1** | HIGH | Underspecification | FR-021 requires font propagation to every widget. T033 only called `self.setFont()` on the window — Qt only propagates this to children that have not had their own `setFont()` called explicitly. Custom widgets with manually-set fonts would silently retain old fonts. T009 had no assertions for `QLabel`, `QMenuBar`, `QTableView`, etc. | **RESOLVED** — T033 strengthened: `_on_uap_font_changed` now iterates `findChildren(QWidget)` and calls `setFont()` on every child; custom widget compliance requirement documented; Governance Annotation added to T033 block. T009 expanded with two new bullets: full-widget font assertions for `QLabel`/`QMenuBar`/`QToolBar`/`QTableView`/`QPushButton`; and custom-widget signal compliance test. FR-021 Font Propagation Check added to Governance Reviewer Checklist in tasks.md. |
| **U2** | MEDIUM | Underspecification | Two competing window-tracking WeakSets: module-level `_open_windows` in `standard_window.py` (T031) and `ThemeManager._registered_windows` (T042). Dual ownership caused undefined lifecycle tracking, duplicate signal fan-out, and divergence risk. | **RESOLVED** — ThemeManager designated as sole authoritative window registry; T031 updated to register via `ThemeManager.instance().register()`; T032 updated to deregister via `ThemeManager.instance().unregister()`; T042 annotated as the only registry; `registered_windows()` snapshot helper added to T042; Governance Annotation added to T031 block; Window Registry Ownership Check added to Governance Reviewer Checklist in tasks.md. |
| **U3** | MEDIUM | Underspecification | FR-006 requires a factory-default `AppearanceProfile` to always exist and never be deletable. No task seeded this profile on first load. T018 only handled scalar defaults inside `UAPSettings`, leaving first-run behavior undefined: tools could start with no profile, deletion guard (`INV-002`) operated on an empty set, and T042/T033 propagation could fire with no profile to read. | **RESOLVED** — T018-B sub-step added to tasks.md: seeds `profile_id="factory_default"`, `is_default=True`, `is_user_created=False`, all schema fields from `FACTORY_DEFAULTS`; persisted in the same write-flush as scalar key seeding; guard ensures T018-B runs only when no profiles exist; `delete_profile("factory_default")` must raise `ValueError` (T024 INV-002). Clarification paragraph and Governance Annotation added to T018 block. Factory Default AppearanceProfile Consistency Check added to Governance Reviewer Checklist in tasks.md. |
| **U4** | MEDIUM | Underspecification | Race condition scenario undefined: two tools simultaneously update the working directory via `set_directory()`, which performs a read-modify-write on `UAPSettings`. No locking or concurrency policy was documented, producing nondeterministic directory state and untestable semantics. | **RESOLVED** — BC-006b updated with normative last-write-wins rule (4-point definition): no locking required, last write wins, tools MUST NOT assume exclusivity; Governance Annotation added to BC-006b in uap-preferences.md explaining why last-write-wins is the correct model for a single-user desktop. T029 bullet added referencing last-write-wins and prohibiting locking. Directory Update Semantics Check added to Governance Reviewer Checklist in tasks.md. |
| **U5** | LOW | Underspecification | INV-006 defines the mixed-sentinel rule: `window_x` and `window_y` must both be `-1` or both be non-negative. No test in T004 covered the mixed case (e.g., `x=100, y=-1`), allowing invalid geometry to pass model validation undetected. | **RESOLVED** — T004 expanded with a mixed-sentinel test bullet covering both violation directions (`x >= 0, y == -1` and `x == -1, y >= 0`), each asserting `ValueError`; Governance Annotation added to T004 block explaining why model-layer enforcement is required; Mixed-Sentinel Invariant Check added to Governance Reviewer Checklist in tasks.md. T005 unchanged (model invariants are not duplicated at service layer). |
| **G1** | LOW | Governance Gap | `src/gui/widgets/uap_appearance_widget.py` is created by T030 but was absent from the plan.md source-change inventory, causing reviewer confusion, incomplete PR diffs, and governance drift between plan.md and the actual repo. | **RESOLVED** — `src/gui/widgets/uap_appearance_widget.py` added to plan.md source tree under a new `src/gui/widgets/` entry; Governance Annotation added to plan.md source tree block explaining source tree completeness requirement; Source Tree Completeness Check added to Governance Reviewer Checklist in tasks.md. |
| **G2** | LOW | Governance Gap | `profile_schema_version` is defined in the migration table but no test verified its presence in serialized output, and v1→v2 migration was never exercised. Silent schema drift and forward-compatibility failures could go undetected. | **RESOLVED** — T004 expanded with two new bullets: (1) schema version presence — `to_json()` MUST include `profile_schema_version`, `from_json()` MUST preserve it; (2) v1→v2 migration test — verifies `profile_schema_version == 2`, all v2 fields populated per migration table, all v1 fields preserved, no extra fields introduced. Governance Annotation added to T004 block. Schema Version Consistency Check added to Governance Reviewer Checklist in tasks.md. |
| **G3** | LOW | Governance Gap | `import_profile` (T026) had no documented behavior for undersized `window_width`/`window_height` relative to a tool's `min_window_width`/`min_window_height`. T021 (`apply()`) clamps at apply-time but the import step did not normalize, creating undefined split-brain semantics. | **RESOLVED** — Canonical decision established: import preserves, apply clamps. T026 expanded with normative geometry-preservation bullet and Governance Annotation clarifying the import-vs-apply boundary. FR-026 in spec.md updated with normative note (import MUST NOT mutate geometry; normalization occurs exclusively in T021). Geometry Import Semantics Check added to Governance Reviewer Checklist in tasks.md. |
| **A1** | LOW | Ambiguity | FR-009 contained a self-contradiction: one sentence required all tools to subclass `PreferencesDialog`; the next allowed tools with no extra preferences to instantiate the base class directly without subclassing — two mutually exclusive statements. | **RESOLVED** — FR-009 rewritten with two clear normative rules: (1) tools with extra preferences MUST subclass and use `addTab()`; (2) tools with no extra preferences MUST instantiate the base class directly. Governance Annotation added to FR-009 in spec.md explaining the contradiction and the corrected model. FR-009 coverage row status note updated. PreferencesDialog Integration Check added to Governance Reviewer Checklist in tasks.md. |
| **A2** | LOW | Ambiguity | `save_last_used()` was called from both T025 (`set_font`) and T032 (`closeEvent`). The T025 call wrote a full-state snapshot with only the font updated, silently overwriting geometry and directory fields with stale values from the previous `closeEvent` — a partial-state write bug. | **RESOLVED** — Canonical persistence model established: `save_last_used()` is a full-state write and MUST only be called from `closeEvent` (T032). `set_font()` rewritten to call `set_font_preferences(family, size)` instead. `set_font_preferences()` added to T025 as a font-only setter. T032 annotated as the exclusive full-state write location. Normative clarification added to BC-006 in uap-preferences.md. Governance Annotation added to T025 block. Persistence API Consistency Check added to Governance Reviewer Checklist in tasks.md. |

---

### Open Findings

#### HIGH

*No HIGH findings remain open.*

#### MEDIUM

| ID | Location | Summary |
|----|----------|---------|
| **I5** | plan.md line 152; contracts "Tested by" headers | ~~Path inconsistency: `tests/contract/gui/` (no 's') in plan.md and contract "Tested by" lines vs actual filesystem `tests/contracts/` (with 's'). Will cause CI path-not-found errors.~~ **RESOLVED — see Resolved Findings table.** |
| **I6** | plan.md source tree line 99 | ~~plan.md lists `src/tabbed_hub.py` as a file to modify. No such file exists; the actual file is `src/rfu/hub.py`.~~ **RESOLVED — see Resolved Findings table.** |
| **I7** | spec.md FR-013 | ~~FR-013 stated audit script MUST exit non-zero when platform conditional evaluates to `False` on current machine — making the script unusable on Linux/macOS. Default behavior was ambiguous.~~ **RESOLVED — see Resolved Findings table.** |
| **I8** | contracts/appearance-profile.md Migration table | ~~Migration table Version 2 row claimed to add `window_x`/`window_y`, but both fields are already in the Version 1 `"required"` array — self-contradiction.~~ **RESOLVED — see Resolved Findings table.** |
| **I9** | tasks.md T003, T041 | ~~No task seeded `ToolManifest` entries with `min_window_width`/`min_window_height` values; T041 audit would run against empty or default manifests producing nondeterministic results.~~ **RESOLVED — see Resolved Findings table.** |
| **U2** | tasks.md T031–T033, T042 | ~~Two competing window-tracking sets: `_open_windows` in `standard_window.py` and `ThemeManager._registered_windows` in T042. Undefined ownership; both accumulate windows; signal slots iterate both.~~ **RESOLVED — see Resolved Findings table.** |
| **U3** | spec FR-006; tasks.md T018 | ~~FR-006 states a factory-default `AppearanceProfile` MUST always exist and MUST NOT be deletable. No task seeds this factory default at first run. T018 covers `load()` returning `FACTORY_DEFAULTS` for missing keys, but that is for `UAPSettings` scalar keys — not for the full `AppearanceProfile` JSON object stored as the factory default.~~ **RESOLVED — see Resolved Findings table.** |
| **U4** | tasks.md T029; spec FR-019 | ~~Race condition scenario undefined: two tools simultaneously update the working directory (e.g., two DirectoryPickerDialog windows open in parallel). `set_directory()` performs a read-modify-write on `UAPSettings`. No locking or last-write-wins policy is documented.~~ **RESOLVED — see Resolved Findings table.** |

#### LOW

| ID | Location | Summary |
|----|----------|---------|
| **U5** | contracts/appearance-profile.md INV-006; tasks.md T004/T005 | ~~INV-006 defines the mixed-sentinel rule: `window_x` and `window_y` must both be `-1` or both be non-negative. No test in T004 (model tests) or T005 (service tests) covers the mixed case (e.g., `x=100, y=-1`).~~ **RESOLVED — see Resolved Findings table.** |
| **G1** | plan.md source tree | ~~`src/gui/widgets/uap_appearance_widget.py` is created by T030 but is absent from the plan.md source-change inventory.~~ **RESOLVED — see Resolved Findings table.** |
| **G2** | contracts/appearance-profile.md; tasks.md T004/T005 | ~~`profile_schema_version` key is defined in the migration table but no test verifies it is present in serialized output, nor is v1→v2 migration exercised.~~ **RESOLVED — see Resolved Findings table.** |
| **G3** | tasks.md T026; spec FR-026 | ~~`import_profile` is specified to show a warning for incompatible fields but has no documented behavior when `window_width` is below the tool's `min_window_width`. The clamp logic in `apply()` (T021) handles this at apply-time, but the import step does not normalize.~~ **RESOLVED — see Resolved Findings table.** |
| **A1** | spec.md FR-009 | ~~FR-009 contains a self-contradiction: "This dialog is implemented by each tool **subclassing `PreferencesDialog`**" and then "Tools with no extra preferences instantiate and show the base class directly **without subclassing**."~~ **RESOLVED — see Resolved Findings table.** |
| **A2** | tasks.md T025, T032; contracts/uap-preferences.md BC-006 | ~~It is ambiguous whether `save_last_used()` is called only at `closeEvent` (T032) or also immediately when `set_font()` is called (T025 calls `save_last_used` as part of `set_font`). If both code paths call `save_last_used`, the `font_family`/`font_size` fields will be correct but `directory`/geometry may carry stale values from the previous `closeEvent`.~~ **RESOLVED — see Resolved Findings table.** |

---

## Governance Reviewer Checklist Status

| Item | Status |
|------|--------|
| Menu Extensibility Check (C1) — no test freezes menu count at 5 | ✅ Fixed — T007 uses `issubset`; T041 has Phase-1 Boundary Note |
| FR-024 Label Invariance — contract tests assert slot presence/enabled, not label text | ✅ Fixed — T007 updated |
| TDD Gate — Phase-2 tests written and failing before Phase-3 code | 🔲 Not yet verifiable (pre-implementation) |
| ToolManifest-only enumeration (C5, FR-016) | ✅ Specified in T007, T041 |
| Manifest Purity Check (I2) — no user-state fields in ToolManifest | ✅ Fixed — T003, data-model §5 |
| UAPService API Consistency (I3) — no Qt-dependent `record_last_used` variant | ✅ Fixed — BC-006 rewritten |
| Directory Persistence Check (I4) — directory uses `set_directory()`, not `set_geometry()` | ✅ Fixed — BC-006b/c, T029 |
| Path Consistency Check (I5) — all "Tested by" paths use `tests/contracts/` (plural) | ✅ Fixed — 7 occurrences corrected across plan.md, menu-contract.md, uap-preferences.md, quickstart.md, research.md |
| Hub Path Check (I6) — plan.md references `src/rfu/hub.py`, not deprecated `src/tabbed_hub.py` | ✅ Fixed — plan.md source tree updated; governance annotation added; residual `tests/contract/` in source tree block also corrected |
| Platform Condition Check (I7) — platform-conditional lines skipped by default; non-zero exit only under `--platform` override | ✅ Fixed — FR-013 rewritten with 3-rule structure; Governance Annotation added to spec.md; Reviewer Checklist item added to tasks.md |
| Migration Table Consistency Check (I8) — no field listed as "added" in a later version if it already exists in an earlier version's `"required"` array | ✅ Fixed — Version 2 row removed from appearance-profile.md; Governance Annotation and Migration Table Normalization Rule added; Reviewer Checklist item added to tasks.md |
| Manifest Seeding Check (I9) — T003 seeds ≥2 manifest entries with explicit values; T041 audits only, never seeds | ✅ Fixed — T003-B sub-step added; T041 clarification added; Governance Annotation added to T003 block; Reviewer Checklist item added to tasks.md |
| FR-021 Font Propagation Check (U1) — T033 iterates `findChildren(QWidget)`; T009 asserts child-widget fonts; custom widgets connect to `uap_font_changed` | ✅ Fixed — T033 strengthened with `findChildren` iteration and custom-widget compliance note; T009 expanded with two full-propagation test bullets; Governance Annotation added to T033; Reviewer Checklist item added to tasks.md |
| Window Registry Ownership Check (U2) — ThemeManager is sole window registry; no module-level `_open_windows` in standard_window.py | ✅ Fixed — T031 uses `ThemeManager.register()`; T032 uses `ThemeManager.unregister()`; T042 annotated as only registry; `registered_windows()` helper added; Governance Annotation in T031; Reviewer Checklist item added to tasks.md |
| Factory Default AppearanceProfile Consistency Check (U3) — T018-B seeds factory-default profile on first load; profile is non-deletable; no tool starts without a profile | ✅ Fixed — T018-B sub-step added; Clarification and Governance Annotation added to T018 block; `delete_profile("factory_default")` raises `ValueError` (T024 INV-002); Reviewer Checklist item added to tasks.md |
| Directory Update Semantics Check (U4) — BC-006b defines last-write-wins; no locking in `set_directory()` or T029 | ✅ Fixed — BC-006b updated with 4-point last-write-wins rule; Governance Annotation added; T029 bullet references semantics and prohibits locking; Reviewer Checklist item added to tasks.md |
| Mixed-Sentinel Invariant Check (U5) — T004 asserts `ValueError` for both INV-006 violation directions | ✅ Fixed — T004 expanded with mixed-sentinel test bullet (both directions); Governance Annotation added to T004 block; Reviewer Checklist item added to tasks.md; T005 unchanged (model invariants not duplicated at service layer) |
| Source Tree Completeness Check (G1) — `uap_appearance_widget.py` listed in plan.md; all task-created files appear in source-change inventory | ✅ Fixed — `src/gui/widgets/uap_appearance_widget.py` added to plan.md source tree; Governance Annotation added to plan.md; Reviewer Checklist item added to tasks.md |
| Schema Version Consistency Check (G2) — T004 asserts `profile_schema_version` in serialized output; v1→v2 migration test present | ✅ Fixed — T004 expanded with schema version presence bullet and v1→v2 migration test bullet; Governance Annotation added to T004 block; Reviewer Checklist item added to tasks.md |
| Geometry Import Semantics Check (G3) — T026 does not clamp geometry; FR-026 includes import-preserves/apply-clamps normative note; T021 is sole normalization point | ✅ Fixed — T026 expanded with geometry-preservation bullet and Governance Annotation; FR-026 updated with normative note; Reviewer Checklist item added to tasks.md |
| PreferencesDialog Integration Check (A1) — tools with extra preferences subclass and use `addTab()`; tools without subclass-free preferences instantiate base class directly | ✅ Fixed — FR-009 rewritten with two clear normative rules; Governance Annotation added to spec.md FR-009; Reviewer Checklist item added to tasks.md |
| Persistence API Consistency Check (A2) — `save_last_used()` called only in T032; T025 uses `set_font_preferences()`; no incremental path writes fields outside its scope | ✅ Fixed — T025 rewritten to call `set_font_preferences()` (not `save_last_used()`); `set_font_preferences()` added as font-only setter; T032 annotated as exclusive full-state write; Normative Clarification added to BC-006; Governance Annotation added to T025 block; Reviewer Checklist item added to tasks.md |

---

## Recommended Resolution Order

**All findings fully resolved.**

*No further advisory items remain. The specification is ready for implementation.*

---

*Report generated by `/speckit.analyze` — 2026-04-25. Reflect current artifact state as of this date.*
