# Phase-3 Governance Summary — Feature 007: UI Harmonization

**Status:** COMPLETE  
**Closed:** 2026-04-26  
**Governance Authority:** Richard Noragon  
**Canonical record:** `speckit-analysis-report-pass3.md`

---

## Purpose of Phase-3

Phase-3 exists to eliminate contradictions, stabilize architectural identities, and ensure every contract, schema, and task is implementable without drift.

This phase is the **constitutional hardening layer** — the point where the system stops being "plausible" and becomes **deterministic**. Every finding resolved here is a drift vector permanently closed.

---

## Resolved Phase-3 Findings

### Identity & Architecture

**P3-C01 — ThemeManager Identity (CRITICAL → RESOLVED)**
- Converted `ThemeManager` into a `QObject`-based singleton with class-level `pyqtSignal` attributes and a canonical `instance()` classmethod.
- `pyqtSignal` on a non-`QObject` raises `TypeError` at import time — zero exceptions permitted.
- Resolved by: P3-Q1 (ThemeManager QObject Rule)

**P3-H03 — Missing `ThemeManager.instance()` (HIGH → RESOLVED)**
- Fully resolved by P3-C01; all T031/T032/T033/T042 call sites using `ThemeManager.instance()` are now valid.

**P3-H02 — GUI Hub Identity Correction (HIGH → RESOLVED)**
- Canonical GUI hub is `src/tabbed_hub.py`; `src/rfu/hub.py` is an idle-watcher utility module only.
- Governance annotations I6/N10/N11 that misidentified the hub are superseded by P3-H02.
- Resolved by: P3-Q2 (Hub Identity Rule)

### Substrate & Schema

**P3-H01 — ToolManifest Substrate Missing (HIGH → RESOLVED)**
- Created `ToolManifestEntry` (dataclass) and `ToolManifestRegistry` in `src/core/tool_manifest.py`.
- T003 rewritten from "verify fields" to "create from scratch."
- T007 MUST fail on an empty registry — a test that passes vacuously is a governance illusion.

**P3-H04 — UUID vs `"factory_default"` Sentinel Contradiction (HIGH → RESOLVED)**
- `profile_id` schema updated to `oneOf` allowing UUID4 OR `"factory_default"`.
- INV-002 and INV-005 harmonized; factory-default profile constitutionally exempt from UUID4 constraints.
- Resolved by: P3-Q3 (Profile Identity Rule)

**P3-M03 — Missing `src/__version__.py` (MEDIUM → RESOLVED)**
- Canonical version source is `APP_VERSION` in `src/core/constants.py`.
- No `src/__version__.py` file SHALL be created in Phase 3 or later without explicit authorization.
- Resolved by: P3-Q4 (Version Source Rule)

### Menu & Window Lifecycle

**P3-M01 — File Menu Contract Divergence (MEDIUM → RESOLVED)**
- `_create_file_menu()` rebuilt to unconditional 7-slot model; all `window_type` conditionals removed.
- `print_document` removed; canonical action IDs applied; `enable_file_action()` API added.

**P3-M02 — Window Geometry Lifecycle (MEDIUM → RESOLVED)**
- `UAPService.apply()` is the authoritative geometry source.
- `_setup_window()` placeholder `resize()` is non-authoritative and is intentionally superseded.
- No `resize()` or `move()` call SHALL follow `apply()` in `__init__`.
- Canonical `__init__` lifecycle: `_setup_window()` → `_setup_ui()` → `apply()` → `_create_status_bar()` → `show()`.

### Language & Lifecycle Clarifications

**P3-L01 — T032 "Modify" vs "Add closeEvent" (LOW → RESOLVED)**
- T032 heading corrected to "Add `StandardWindow.closeEvent(self, event: QCloseEvent) -> None`".
- Method signature, 5-step call order, and lifecycle table documented.
- Constitutional rule established: tasks SHALL use "Add" for new methods and "Modify" for existing.

**P3-Q5 — UAP Tracking Field Rule (ADVISORY → RESOLVED)**
- `UAPService.apply()` stores `self._uap_font_family`, `self._uap_font_size`, `self._uap_browse_root` after applying font and directory.
- `closeEvent()` reads these three instance attributes; geometry read live from `self.geometry()`.
- Options B (live Qt state) and C (re-read from store) both rejected — Option A is the only Phase-3-correct choice.

---

## Phase-3 Outcomes

| Area | Result |
|------|--------|
| Tasks T018–T050 | All implementable |
| Invariants INV-001 through INV-008 | All harmonized |
| Schema contradictions | All resolved |
| Lifecycle ambiguities | All resolved |
| Contract divergences | All corrected |
| Reviewer checklists | All enforceable |
| Governance drift vectors | None remaining |

---

## Constitutional Rules Established in Phase-3

The following rules are **permanent governance records**. They survive phase boundaries and apply to all future contributors:

1. **ThemeManager is a `QObject`-based singleton.** No reversion to plain Python class. No second signal bus.  
2. **`src/tabbed_hub.py` is the canonical GUI hub.** No implicit migration during Phase 3 or later without an explicit migration task.  
3. **`ToolManifestRegistry` is the canonical tool registry.** No audit against an empty registry is valid.  
4. **`profile_id` accepts UUID4 or `"factory_default"` only.** No code shall enforce UUID4 on the sentinel.  
5. **`APP_VERSION` in `src.core.constants` is the sole version source.** No duplicate version files.  
6. **`_create_file_menu()` is unconditional and 7-slot.** No `window_type` conditionals permitted.  
7. **`UAPService.apply()` is the authoritative geometry step.** No `resize()` or `move()` after `apply()` in `__init__`.  
8. **`apply()` stores `_uap_font_family`, `_uap_font_size`, `_uap_browse_root`.** `closeEvent()` reads these; geometry read live.  
9. **Tasks use "Add" for new methods, "Modify" for existing ones.** No ambiguous task language.

---

## Phase-3 Status

**COMPLETE.**

The system is constitutionally stable. All tasks in the T001–T050 dependency chain are implementable. All reviewer checklists are enforceable. No drift vectors remain.

The system is ready for **Phase-4**.

---

## Related Artifacts

| Artifact | Location |
|----------|----------|
| Full finding record | `speckit-analysis-report-pass3.md` |
| Task specifications | `tasks.md` |
| Appearance profile contract | `contracts/appearance-profile.md` |
| Data model (ToolManifest §5) | `data-model.md` |
| UAP lifecycle diagram | `uap-lifecycle-diagram.md` |
| Pass 1 governance record | `speckit-analysis-report.md` |
| Pass 2 governance record | `speckit-analysis-report-pass2.md` |
