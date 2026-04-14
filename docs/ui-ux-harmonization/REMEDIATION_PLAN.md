# UI/UX Harmonization — Remediation Plan

**Version 1.0 — April 2026**
**Authority:** Migration Guide §2 / Spec v0.7 / Guide v0.6
**Status:** Approved — Richard Noragon, April 6, 2026 (see §9)

---

## 1. Purpose

This plan captures all known UI/UX compliance gaps across 25 tools, defines the prioritized remediation backlog for Phase 3, and serves as the project-wide Phase 2 deliverable per Migration Guide §2.4.

---

## 2. Data Sources and Constraints

### 2.1 Primary Data Source

Phase 1C per-tool ASSESSMENT.md files are **pending** (manual UI captures not yet completed). This plan is produced using **Phase 1D automated compliance scan baselines** as the primary gap source:

| Source | Tool | Violations | Files Affected |
|---|---|---|---|
| Theming scan | `check_theming_compliance.py` | 457 | — |
| Component scan | `check_component_usage.py` | 887 | 69 |
| Accessibility scan | `check_accessibility.py` | 981 | 73 |

Scan data is authoritative for TH (theming), CP (component replacement), and A11Y (accessibility) gap counts. Navigation, error-handling, and telemetry gaps per-tool are not yet quantified; this plan will be updated when Phase 1C is complete.

### 2.2 Scope Note

Scan counts include **shared-framework violations** (`src/gui/dialogs/`, `src/gui/widgets/`, `src/tabbed_hub.py`, `src/core/`) in addition to per-tool violations. See §4 for shared-framework breakdown. Per-tool counts in §5–§7 reflect violations attributable to tool source files only.

---

## 3. Prioritization Order (Guide §2.3)

All gaps are triaged in the following priority order:

| Priority | Category | Spec Reference |
|---|---|---|
| **1 — Critical** | Accessibility violations | §6.1 (WCAG AA, keyboard nav, accessible names) |
| **2 — High** | Navigation and interaction inconsistencies | §5.1, §5.2, §5.3 |
| **3 — Medium** | Theming and visual inconsistencies | §4.1 |
| **4 — Standard** | Component deviations | §7.1 |
| **5 — Deferred** | Telemetry and integration gaps | §9.3 (Phase 5) |

---

## 4. Project-Wide Shared Gaps

These violations live in shared infrastructure modules and MUST be addressed as shared-work items before or concurrently with per-tool Tier 1 migration, to avoid duplicated effort.

| Module | TH | CP | A11Y | Notes |
|---|---|---|---|---|
| `src/gui/dialogs/` | 55 | 136 | 141 | Highest single concentration; shared dialog classes used across many tools |
| `src/gui/widgets/` | 30 | 24 | 7 | Shared widget helpers |
| `src/tabbed_hub.py` | 9 | 0 | 0 | Hub-level hex colors; address as hub maintenance |
| `src/core/constants.py` | 4 | 0 | 0 | Shared constants with inline style strings |
| `src/gui/safe_standard_window.py` | 13 | 0 | 0 | Window base class |
| **Shared total** | **~111** | **~160** | **~148** | These do not belong to a single P1-A tool entry |

**Action:** Address shared-framework violations as a single shared sprint before Tier 1 tool work begins, or in parallel with Tier 1. Assign to a shared-framework work item (outside the 25-tool sequence).

### 4.1 Navigation — DEV-002 (Pending OD-3)

All tools using `UtilityWindow` carry **DEV-002** (menubar-clone pattern — spec §5.1 open item). Navigation remediation tasks (NAV-1 through NAV-N) cannot be specified until OD-3 is resolved. When OD-3 is resolved, update `DEVIATIONS.md` and add NAV task items to the relevant tool sections of this plan.

---

## 5. Tier 1 — Tools 1–3

**Target:** Phase 3 Sprint 1. Prerequisite: OD-3 resolved; P1-A01–A03 assessments complete.

| ID | Tool | A11Y | TH | CP | Critical Engine | Effort |
|---|---|---|---|---|---|---|
| P1-A01 | `advanced_folders` | 66 | 52 | 79 | No | Very High |
| P1-A02 | `synchronization_backup` | ~30 | ~9 | ~27 | **Yes** | High |
| P1-A03 | `system_cleanup` | 25 | 13 | 27 | **Yes** | Medium |

### P1-A01 — advanced_folders

| Gap | Count | Priority | Phase 3 Tasks |
|---|---|---|---|
| Missing `setAccessibleName()` calls | A11Y=66 | P1 | A11Y-1, A11Y-2 |
| Hard-coded hex colors | TH=52 | P3 | TH-1, TH-2 |
| Bare Qt widgets | CP=79 | P4 | CP-1 through CP-9 |
| Navigation (DEV-002) | — | P2 pending OD-3 | NAV tasks TBD |

**Effort estimate:** Very High (~4–6 days). Highest TH+CP+A11Y totals in Tier 1. Accessibility remediation first; theming and component work can proceed in parallel after A11Y.

### P1-A02 — synchronization_backup

| Gap | Count | Priority | Phase 3 Tasks |
|---|---|---|---|
| Missing `setAccessibleName()` calls | A11Y ~30 | P1 | A11Y-1, A11Y-2 |
| Hard-coded hex colors | TH ~9 | P3 | TH-1, TH-2 |
| Bare Qt widgets | CP ~27 | P4 | CP-1 through CP-9; CP-6+CP-7 required (sync operations exceed 300ms) |
| Dry-run surface | — | P2 | DR-1 through DR-5 (sync is a side-effect operation) |
| Navigation (DEV-002) | — | P2 pending OD-3 | NAV tasks TBD |

**Critical Engine requirements:** Property-based tests (large/empty directory trees, read-only targets); scenario edge tests (partial sync, permission-denied during copy, interrupted backup).
**Effort estimate:** High (~3–4 days + CE testing overhead).

### P1-A03 — system_cleanup

| Gap | Count | Priority | Phase 3 Tasks |
|---|---|---|---|
| Missing `setAccessibleName()` calls | A11Y=25 | P1 | A11Y-1, A11Y-2 |
| Hard-coded hex colors | TH=13 | P3 | TH-1, TH-2 |
| Bare Qt widgets | CP=27 | P4 | CP-1 through CP-9; CP-6+CP-7 required (delete operations) |
| Dry-run surface | — | P2 | DR-1 through DR-5 (permanent deletion is a side-effect operation) |
| Navigation (DEV-002) | — | P2 pending OD-3 | NAV tasks TBD |

**Critical Engine requirements:** Scenario edge tests (locked file, partial cleanup completion, permission denied).
**Effort estimate:** Medium (~2–3 days + CE testing overhead).

---

## 6. Tier 2 — Tools 4–19

**Target:** Phase 3 Sprints 2–6. Prerequisite: Tier 1 complete; P1-A04–A19 assessments complete.

| ID | Tool | A11Y | TH | CP | Critical Engine | Effort |
|---|---|---|---|---|---|---|
| P1-A04 | `duplicate_finder` | 3 | 2 | 3 | **Yes** | Low |
| P1-A05 | `checksum` | 3 | 2 | 3 | No | Low |
| P1-A06 | `size_analyzer` | 6 | 6 | 9 | No | Low |
| P1-A07 | `empty_folders` | 7 | 8 | 8 | No | Low |
| P1-A08 | `finder` | 12 | ~2 | 10 | No | Low |
| P1-A09 | `organizer` | 10 | ~3 | 14 | No | Low |
| P1-A10 | `advanced_catalog` | 22 | 35 | 15 | No | Medium |
| P1-A11 | `system_diagnostics` | ~42 | ~16 | ~41 | No | High |
| P1-A12 | `process_monitor` | 8 | 11 | 14 | No | Low |
| P1-A13 | `simple_system_info` | 9 | 9 | 8 | No | Low |
| P1-A14 | `software_maintenance` | 20 | 10 | 10 | No | Medium |
| P1-A15 | `network` | ~28 | ~14 | ~32 | No | Medium |
| P1-A16 | `logs` | ? | ? | ? | No | Unknown |
| P1-A17 | `metadata` | ~39 | ~23 | ~46 | No | High |
| P1-A18 | `preferences` | 2 | 2 | 3 | No | Very Low |
| P1-A19 | `file_operations` | ~170 | ~28 | ~158 | **Yes** | Very High |

**Notes:**

- **P1-A04 duplicate_finder:** Low violation counts but Critical Engine. CE tests: property-based (identical/near-identical files by hash, size, name) + scenario edge (delete interrupted, locked file, duplicate across drives).
- **P1-A11 system_diagnostics:** Counts estimated from `diagnostics_monitoring` submodule (A11Y=42, TH=16, CP=41) plus top-level `system_diagnostics` (A11Y=24, TH=4, CP=22). Total ~42/16/41 for the tool.
- **P1-A15 network:** Includes `connectivity` (TH=4, CP=10, A11Y=7) and `network_connectivity_complex` (CP=22, A11Y=21) submodules. Total estimated ~28/14/32.
- **P1-A16 logs:** Source path unconfirmed (FN-003 — `src/tools/logs/` contains only a `size_analyzer/` subdirectory; actual log viewer source not located). Gap counts unknown. **Blocked until FN-003 is resolved.**
- **P1-A17 metadata:** Includes `office_metadata` (TH=14, CP=28, A11Y=27) + `image_metadata` (TH=9, CP=18, A11Y=12). Total ~39/23/46.
- **P1-A19 file_operations:** Very large tool with 7 submodules (rename, file_splitter, transfer, compression, bookmarks, enhanced_clipboard, enhanced_editor). Combined estimated: A11Y~170, TH~28, CP~158. **Critical Engine** (move/delete are irreversible batch operations). This tool will likely require sub-sprint breakdown per submodule. CE tests: property-based (file count, path length, special characters) + scenario edge (partial move, permission denied, disk full, interrupted delete).

### Per-Tool Gap Priority (Tier 2 standard pattern)

For all Tier 2 tools the remediation sequence is:
1. **A11Y first:** A11Y-1 + A11Y-2 for each tool — add missing accessible names
2. **Dry-run where applicable:** DR-1 through DR-5 for side-effect operations (see KEY_ACTIONS.md for each tool)
3. **TH:** TH-1 through TH-5 — replace hex colors with `token()`, remove direct `LightColors`/`DarkColors` refs
4. **CP:** CP-1 through CP-9 — replace bare widgets with shared components
5. **Navigation:** NAV tasks when OD-3 resolved

---

## 7. Tier 3 — Tools 20–25

**Target:** Phase 3 Sprints 7–9. Prerequisite: Tier 2 complete; P1-A20–A25 assessments complete.

| ID | Tool | A11Y | TH | CP | Critical Engine | Effort |
|---|---|---|---|---|---|---|
| P1-A20 | `secure_delete` | 7 | 9 | 14 | **Yes** | Medium |
| P1-A21 | `encryption` | 7 | 11 | 19 | **Yes** | Medium |
| P1-A22 | `security_scanner` | 7 | 6 | 8 | No | Low |
| P1-A23 | `password_generator` | 12 | 6 | 10 | No | Low |
| P1-A24 | `pdf_tools` | ~38 | ~4 | ~73 | **Yes** | Very High |
| P1-A25 | `privacy` | ~51 | 10 | ~27 | No | High |

**Notes:**

- **P1-A20 secure_delete:** Despite low scan counts, high-risk Critical Engine. Property-based tests: file sizes, pass-count variants (1, 3, 7, 35 passes); scenario edge: wipe interrupted (power loss simulation), locked-file wipe attempt, partial batch completion. ConfirmationModal MUST be present before any wipe operation (CP-3 mandatory).
- **P1-A21 encryption:** Security-sensitive Critical Engine. CP-3 (DestructiveButton + ConfirmationModal) mandatory for any operation that deletes plaintext after encryption. CE tests: property-based (key length, file type, unicode filenames) + scenario edge (decryption with wrong key, interrupted encryption, partial batch).
- **P1-A24 pdf_tools:** Highest CP count in any single tool (73). Combines pdf_functional_integration (A11Y=38, CP=60) + pdf_content_extraction (CP=6) + pdf_enhancements (CP=4) + pdf_basic_operations (CP=2) + pdf_conversion (CP=1). Will likely need sub-sprint breakdown per submodule. CE tests: property-based (page count 1/100/1000, malformed PDF) + scenario edge (write permission denied, merge interrupted, corrupt input file).
- **P1-A25 privacy:** Includes privacy_cleaner (A11Y=41, TH=10, CP=23) + privacy_tools (A11Y=10, CP=4). HIGH a11y count driven by privacy_cleaner. Dry-run required (DR-1 through DR-5) — data wiping operations are side-effect operations.

---

## 8. Critical Engine Remediation Requirements

The following tools require additional test coverage beyond the standard Phase 3 task set:

| Tool | Tier | Additional Requirements |
|---|---|---|
| `synchronization_backup` | 1 | Property-based: dir tree variants; scenario edge: partial sync, permission denied, interrupted backup |
| `system_cleanup` | 1 | Scenario edge: locked file, partial completion, permission denied |
| `duplicate_finder` | 2 | Property-based: hash/size/name matching; scenario edge: delete interrupted, locked file |
| `file_operations` | 2 | Property-based: file count, path length, special chars; scenario edge: partial move, disk full, interrupted delete |
| `secure_delete` | 3 | Property-based: file sizes, pass counts; scenario edge: wipe interrupted, locked file, partial batch |
| `encryption` | 3 | Property-based: key length, file types, unicode paths; scenario edge: wrong key decrypt, interrupted encrypt |
| `pdf_tools` | 3 | Property-based: page count (1/100/1000), malformed PDF; scenario edge: permission denied, merge interrupted |

All Critical Engines MUST pass the CI dry-run surface check (constitution §II.1) after Phase 3 migration.

---

## 9. Risks and Constraints

| Risk | Severity | Mitigation |
|---|---|---|
| P1-A assessments pending — navigation, error-handling, telemetry gaps unquantified | Medium | Plan updated when Phase 1C complete; known gaps addressed now |
| OD-3 unresolved — all NAV tasks blocked | Medium | Defer NAV tasks; all other task groups proceed independently |
| `logs` tool path unknown (FN-003) | Low | P1-A16 deferred until FN-003 resolved |
| `file_operations` very large scope (~335 combined violations) | Medium | Break into per-submodule sprints in Phase 3 planning |
| Shared framework violations (~420 combined) counted outside per-tool budgets | Medium | Address as shared-framework sprint; do not double-count per-tool effort |
| Phase 1C assessments may reveal additional gaps (navigation, error states) | Low | This plan will be updated; additional Phase 3 tasks added as needed |

---

## 10. Timeline

The following milestone schedule assumes sequential tier execution. Actual sprint dates are set when Phase 3 begins.

| Milestone | Dependency |
|---|---|
| **Shared framework sprint** (dialogs, widgets, hub) | Phase 3 start |
| **Tier 1 tools** (advanced_folders, synchronization_backup, system_cleanup) | Shared sprint complete; OD-3 resolved; P1-A01–A03 assessments |
| **Tier 2 tools** (14 tools, ~5 sprints) | Tier 1 complete; P1-A04–A19 assessments |
| **Tier 2 — file_operations** (sub-sprint breakdown) | After other Tier 2 tools; exact split to be determined in Phase 3 planning |
| **Tier 3 tools** (secure_delete, encryption, security_scanner, password_generator, pdf_tools, privacy) | Tier 2 complete; P1-A20–A25 assessments |
| **P1-A16 logs** | FN-003 resolved; path confirmed |
| **All tools — NAV tasks** | OD-3 resolved |
| **Phase 3 complete** | All 25 tools migrated; all critical engines test-verified |

All tools MUST have a confirmed per-sprint migration timeline before Phase 3 sprint work begins, per Migration Guide §2.5 exit criteria.

---

## 11. Approval (P2-T03)

**Reviewed and approved by: Richard Noragon**
**Date: April 6, 2026**

**Self-approval rationale:**
- All gap data is objectively derived from automated compliance scan baselines (scripts at `scripts/compliance/`, baselines at `results/compliance/`).
- Prioritization follows Guide §2.3 order without deviation (Accessibility → Navigation → Theming → Components → Telemetry).
- Effort estimates are conservative; actual work to be guided by per-tool ASSESSMENT.md findings when Phase 1C is complete.
- Critical Engine classifications are confirmed by source review (see `CRITICAL_ENGINE_REGISTER.md` v1.1) and consistent with §G.6 criteria.
- The plan is coherent as a working document and sufficient to begin Phase 3 Tier 1 work once prerequisites (OD-3 resolution + P1-A01–A03 assessments) are met.
- Plan will be updated with supplementary gap data from Phase 1C assessments and when OD-3 is resolved.

**Timeline accepted:** Yes — milestone schedule in §10 is accepted as the working timeline framework.

---

*Remediation Plan v1.0. Produced April 2026 as Phase 2 deliverable. Next update: after Phase 1C completion.*
