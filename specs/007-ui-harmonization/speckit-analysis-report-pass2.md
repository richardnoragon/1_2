# SpecKit Analysis Report — Pass 2

**Run date**: 2026-04-25 (post-remediation cross-artifact sweep)
**Feature**: `007-ui-harmonization` — UI Harmonization (Phase 1)
**Constitution version**: v1.37.0
**Pass**: 2 of 2 (baseline pass: `speckit-analysis-report.md`)
**Scope**: Cross-artifact consistency and coverage analysis of all spec artifacts after all 20 Pass-1 findings (I1–I9, C1, U1–U5, G1–G3, A1, A2) were resolved.

## Artifacts Analyzed

| Artifact | Path |
|---|---|
| Spec | `specs/007-ui-harmonization/spec.md` |
| Plan | `specs/007-ui-harmonization/plan.md` |
| Tasks | `specs/007-ui-harmonization/tasks.md` |
| Data model | `specs/007-ui-harmonization/data-model.md` |
| UAP contract | `specs/007-ui-harmonization/contracts/uap-preferences.md` |
| AppearanceProfile contract | `specs/007-ui-harmonization/contracts/appearance-profile.md` |
| Menu contract | `specs/007-ui-harmonization/contracts/menu-contract.md` |
| Quickstart | `specs/007-ui-harmonization/quickstart.md` |
| Pass-1 report | `specs/007-ui-harmonization/speckit-analysis-report.md` |

---

## Executive Summary

| Category | Count |
|---|---|
| New findings — HIGH (implementation blockers) | 2 |
| New findings — MEDIUM (correctness risk) | 6 |
| New findings — LOW (advisory / stale text) | 6 |
| **Total new findings** | **14** |
| Pass-1 findings still open | 0 |

All 20 Pass-1 findings remain resolved. This report captures only net-new issues introduced or uncovered after those remediations.

---

## FR Coverage (inherited from Pass 1)

All 26 FRs (FR-001 through FR-026) covered by at least one task and at least one contract. No new FR-coverage gaps identified in this pass.

---

## Constitution Alignment (inherited from Pass 1)

| Section | Status |
|---|---|
| §6.1 Preference keys | ✅ Covered (BC-001 through BC-006c) |
| §7.1 Standard menus | ✅ Covered (FR-004, menu-contract-v1) |
| §7.2 7-menu topology | ⚠️ Phase 1 ships 5 menus — planned gap; N13 advisory recorded; Q8 RESOLVED (2026-04-26) — Phase-2 menus deferred to Phase-2 authoring time |
| §7.3 About dialog | ✅ Covered (FR-017, BC-008, T040) |
| §7.4 Preferences dialog | ✅ Covered (FR-009 A1-resolved, T034–T035) |
| §9.1 TDD gate | 🔲 Not yet verifiable (Phase-2 tests not yet written) |

---

## Open Findings

### HIGH — Implementation Blockers

---

#### N1 — `profile_schema_version`: cross-artifact placement conflict ✅ RESOLVED

**Severity**: HIGH → **RESOLVED (2026-04-26)**
**Affects**: `contracts/appearance-profile.md`, `data-model.md` §6, `tasks.md` T004 (G2 bullet), T018-B

**Governance Decision**: **Option A** — `profile_schema_version` is a required field inside each AppearanceProfile JSON blob.

**Resolution Summary**

Governance ruling chose Option A: schema versioning is a per-profile concern. Each AppearanceProfile MUST contain its own `profile_schema_version` field. This preserves per-profile schema evolution, avoids global version coupling, and aligns with T004, T015, T016, and T018-B.

Updates applied to affected artifacts:

- **`contracts/appearance-profile.md`**: `$id` bumped to `appearance-profile-v2`; `"profile_schema_version"` added to `"required"` and `"properties"` (`"type": "integer", "minimum": 1`); migration section text updated to "Schema version tracked inside each AppearanceProfile JSON object as field `profile_schema_version`"; Version 2 migration entry added; governance annotation added.
- **`data-model.md` §6**: `profile_schema_version → "1"` top-level key removed; example profile blobs updated to show `"profile_schema_version": 2` as an inline field; governance annotation added.
- **`tasks.md` T014**: `profile_schema_version` (value: `2`) added to `FACTORY_DEFAULTS`.
- **`tasks.md` T018-B**: `profile_schema_version` already present in seed field list; resolved — value populated from `FACTORY_DEFAULTS` (schema version 2).

> **Governance Annotation — Placement of `profile_schema_version` (N1)**
> Per-profile schema versioning is the authoritative placement. The top-level `uap.profile_schema_version` key is removed. Each `AppearanceProfile` JSON blob carries its own `profile_schema_version` integer field. This enables independent migration of individual profiles, avoids global version coupling, and aligns T004, T015, T016, and T018-B.

**Reviewer Checklist — Schema Version Placement**

Reviewers MUST verify that:
- `profile_schema_version` appears **inside each AppearanceProfile JSON blob**
- JSON schema lists it in `required` and `properties`
- Migration logic updates the per-profile version (v1 → v2)
- No top-level `uap.*` key exists for schema version
- T004/T015/T016/T018-B tests reference the per-profile field only

---

#### N2 — `is_user_created` field in T018-B absent from AppearanceProfile schema ✅ RESOLVED

**Severity**: HIGH → **RESOLVED (2026-04-26)**
**Affects**: `tasks.md` T018-B, `contracts/appearance-profile.md` JSON schema, `specs/007-ui-harmonization/spec.md` AppearanceProfile entity

**Governance Decision**: **Option C** — `is_user_created` is an optional field with `"default": false`.

**Resolution Summary**

Governance ruling chose Option C: `is_user_created` is added to the JSON schema as an optional property (NOT in `"required"`), with `"default": false`. This preserves backward compatibility, avoids a mandatory schema bump, and allows tools to distinguish system-seeded profiles from user-created ones without relying on `profile_id` conventions.

Updates applied to affected artifacts:

- **`contracts/appearance-profile.md`**: `is_user_created` added to `"properties"` as `{ "type": "boolean", "default": false }`. NOT added to `"required"`. Governance annotation added after INV-006.
- **`data-model.md` §2**: `is_user_created: bool = False` added to `AppearanceProfile` dataclass.
- **`spec.md`**: `is_user_created` (boolean, optional, default `false`) added to `AppearanceProfile` Key Entity attribute list.
- **`tasks.md` T018-B**: Existing `is_user_created=False` seed line is now valid and schema-compliant — no change required.

> **Governance Annotation — `is_user_created` Semantics (N2)**
> Earlier drafts of T018-B seeded `is_user_created=False`, but the field did not exist in the JSON schema, dataclass, or entity definition. `"additionalProperties": false` would have caused schema validation to reject any blob containing it, and the dataclass constructor would have raised `TypeError`.
>
> `is_user_created` is an *optional* field with `"default": false`. It is NOT listed in `"required"`. Existing profiles remain valid without migration. The field allows tools to distinguish system-seeded profiles from user-created ones without relying on `profile_id` conventions.

**Reviewer Checklist — `is_user_created` Consistency**

Reviewers MUST verify that:
- `is_user_created` exists in the JSON schema `"properties"` as `{ "type": "boolean", "default": false }`
- It is **not** listed in `"required"`
- The dataclass includes `is_user_created: bool = False`
- T018-B seeds it as `is_user_created=False`
- No code path assumes it is always present in legacy profile blobs

---

### MEDIUM — Correctness Risks

---

#### N3 — T015 `__post_init__` missing INV-006 (mixed-sentinel) cross-field check ✅ RESOLVED

**Severity**: MEDIUM → **RESOLVED (2026-04-26)**
**Affects**: `tasks.md` T015, `contracts/appearance-profile.md` INV-006

**Resolution Summary**

INV-006 cross-field check added to T015 `__post_init__` validation list. Both mixed-sentinel directions are now explicitly required to raise `ValueError`.

Updates applied:

- **`tasks.md` T015**: New validation bullet added: "INV-006 mixed-sentinel invariant: if `window_x >= 0` and `window_y == -1`, or `window_x == -1` and `window_y >= 0`, `__post_init__` MUST raise `ValueError('mixed sentinel: window_x and window_y must both be -1 or both be non-negative')`. Both directions MUST be enforced." Governance annotation added inline.

> **Governance Annotation — INV-006 Must Be Enforced in `__post_init__` (N3)**
> INV-006 defines a cross-field invariant for window geometry. Earlier drafts of T015 validated only individual fields and omitted the mixed-sentinel check, allowing invalid profiles to be constructed. T004 includes `ValueError`-expecting tests for both mixed-sentinel directions. T015 `__post_init__` MUST enforce INV-006 so that invalid geometry cannot enter the system.

**Reviewer Checklist — Mixed-Sentinel Invariant (INV-006)**

Reviewers MUST verify that:
- T015 `__post_init__` enforces the mixed-sentinel rule
- Both mixed cases (`x >= 0, y == -1` and `x == -1, y >= 0`) raise `ValueError`
- T004 includes the corresponding tests for both directions
- No code path bypasses model validation

---

#### N4 — BC-004 references non-existent method `set_font_size(n)` ✅ RESOLVED

**Severity**: MEDIUM → **RESOLVED (2026-04-26)**
**Affects**: `contracts/uap-preferences.md` BC-004

**Resolution Summary**

BC-004 rewritten to reference the canonical T025 API. The non-existent `set_font_size(n)` reference is replaced with the correct two-step pipeline: `set_font(family, size)` clamps and delegates to `set_font_preferences()`.

Updates applied:

- **`contracts/uap-preferences.md` BC-004**: Rewritten to: "`UAPService.set_font(family, size)` MUST clamp `size` to [6, 32] before calling `set_font_preferences()`. It MUST NOT raise for out-of-range `size`. `set_font_preferences()` MUST persist only font fields and MUST NOT write geometry or directory fields." Governance annotation added.

> **Governance Annotation — BC-004 Corrected (N4)**
> Earlier drafts referenced a legacy method `set_font_size(n)` that does not exist in the UAPService API. Font size clamping occurs in `set_font(family, size)` and persistence is delegated to `set_font_preferences()`. This aligns BC-004 with T025 and the incremental-write persistence model established by A2.

**Reviewer Checklist — Font Update API Consistency**

Reviewers MUST verify that:
- BC-004 references `set_font(family, size)` — NOT `set_font_size`
- No code or spec references `set_font_size`
- `set_font()` clamps size to `[6, 32]`
- `set_font_preferences()` persists only font fields
- No incremental update path performs a full-state write

---

#### N5 — T005 has no test case for `set_font_preferences()` (introduced by A2) ✅ RESOLVED

**Severity**: MEDIUM → **RESOLVED (2026-04-26)**
**Affects**: `tasks.md` T005

**Resolution Summary**

`set_font_preferences()` isolation test added to T005. The test verifies the method writes only font fields and leaves all geometry and directory fields unchanged.

Updates applied:

- **`tasks.md` T005**: New bullet added: "`set_font_preferences(family, size)` MUST write only `last_used_font_family` and `last_used_font_size`; MUST NOT mutate `last_used_width`, `last_used_height`, `last_used_x`, `last_used_y`, or `last_used_directory`. Test MUST assert that all geometry and directory fields remain unchanged after the call." Governance annotation added inline.

> **Governance Annotation — `set_font_preferences()` Isolation Test Required (N5)**
> A2 introduced `set_font_preferences()` as the canonical font-only persistence method. Earlier drafts of T005 did not include a test for this method, leaving its isolation invariant unverified. T005 MUST test that `set_font_preferences()` writes only font fields and does not modify geometry or directory. This ensures consistency with the persistence model defined in BC-006 and T025/T032.

**Reviewer Checklist — Font Preferences Isolation**

Reviewers MUST verify that:
- T005 includes a test for `set_font_preferences()`
- Only `last_used_font_family` and `last_used_font_size` are updated
- `last_used_width`, `last_used_height`, `last_used_x`, `last_used_y`, and `last_used_directory` remain unchanged
- No incremental update path performs a full-state write

---

#### N6 — T021 `apply()` font propagation does not mandate `findChildren(QWidget)` iteration ✅ RESOLVED

**Severity**: MEDIUM → **RESOLVED (2026-04-26)**
**Affects**: `tasks.md` T021

**Resolution Summary**

T021 font application bullet updated to explicitly mandate `window.findChildren(QWidget)` iteration, matching T033's `_on_uap_font_changed` implementation. The vague phrase "on window and all child widgets" is replaced with the enforceable two-step pattern.

Updates applied:

- **`tasks.md` T021**: Font bullet replaced with: "**Apply font:** call `window.setFont(QFont(font_family, font_size))`; then iterate `window.findChildren(QWidget)` and call `.setFont(QFont(font_family, font_size))` on each child widget — this propagation mechanism MUST match the implementation used in T033's `_on_uap_font_changed` handler (U1)." Governance annotation added inline.

> **Governance Annotation — T021 Must Mirror T033 Font Propagation (N6)**
> Earlier drafts of T021 stated that fonts must be applied to "all child widgets" but did not specify the mechanism. T021 MUST use the same propagation mechanism as T033: iterating `window.findChildren(QWidget)` and calling `.setFont()` on each child. This ensures consistent font propagation at both window-open time and runtime font-change events, and satisfies FR-021's requirement that every widget receives the update.

**Reviewer Checklist — Font Propagation (T021/T033 Consistency)**

Reviewers MUST verify that:
- T021 explicitly iterates `window.findChildren(QWidget)` and calls `.setFont()` on each child
- T033 uses the same mechanism
- No implementation relies solely on `window.setFont()`
- FR-021's requirement ("every widget") is satisfied
- Custom widgets with explicit fonts receive updates at both window-open time and runtime change

---

#### N7 — T028 `FontPickerDialog` OK handler double-applies font to parent window ✅ RESOLVED

**Severity**: MEDIUM → **RESOLVED (2026-04-26)**
**Affects**: `tasks.md` T028

**Resolution Summary**

T028 OK-handler updated to signal-only propagation. The direct `parent_window.setFont()` call is removed. Font changes now propagate exclusively through the `uap_font_changed` signal via T033.

Updates applied:

- **`tasks.md` T028**: OK-handler bullet replaced with: "Call `UAPService().set_font(family, size)` — the resulting `uap_font_changed` signal MUST propagate the font change to `parent_window` and all child widgets via T033; no direct `parent_window.setFont()` call is permitted." Governance annotation added inline.

> **Governance Annotation — T028 Must Not Mutate the Window Directly (N7)**
> Earlier drafts of T028 directly applied the font to the parent window before calling `UAPService.set_font()`. This caused redundant updates and inconsistent propagation, because only the signal path (T033) performs the full `findChildren()` sweep. T028 MUST rely exclusively on the `uap_font_changed` signal for font propagation. All font updates MUST flow through: `UAPService.set_font()` → `set_font_preferences()` → `ThemeManager.uap_font_changed.emit()` → `StandardWindow._on_uap_font_changed` → `setFont()` + `findChildren()` sweep.

**Reviewer Checklist — T028 OK Handler**

Reviewers MUST verify that:
- T028 does NOT call `parent_window.setFont()`
- T028 calls only `UAPService().set_font(family, size)`
- Font propagation occurs exclusively via the T033 signal handler
- No duplicate or partial propagation paths exist
- The `findChildren()` sweep is performed only once, by T033

---

#### N8 — Factory-default profile identity ambiguous: INV-002 uses name; T018-B/T024 use `profile_id` ✅ RESOLVED

**Severity**: MEDIUM → **RESOLVED (2026-04-26)**
**Affects**: `contracts/appearance-profile.md` INV-002, `tasks.md` T018-B, T024

**Governance Decision**: Factory-default profile identity is unified. Both `profile_id = "factory_default"` AND `profile_name = "Default"` are canonical. The deletion guard MUST check `profile_id`, not `profile_name`.

**Resolution Summary**

INV-002 updated to specify both identifiers and mandate the `profile_id`-based deletion guard. T018-B seed updated to include `profile_name = "Default"`. T024 `delete_profile` bullet clarified to mandate `profile_id == "factory_default"` check.

Updates applied:

- **`contracts/appearance-profile.md` INV-002**: Rewritten to: "The factory-default profile (`profile_id = \"factory_default\"`, `profile_name = \"Default\"`) MUST always exist and MUST NOT be deletable. The deletion guard MUST check `profile_id == \"factory_default\"`, not `profile_name`."
- **`tasks.md` T018-B**: `profile_name = "Default"` added to the factory-default seed field list.
- **`tasks.md` T024**: `delete_profile` bullet updated: "the guard MUST check `profile_id == \"factory_default\"`, not `profile_name`."

> **Governance Annotation — Factory-Default Profile Identity (N8)**
> Earlier drafts inconsistently identified the factory-default profile by name (`"Default"`) and by ID (`"factory_default"`). This created ambiguity in deletion guards and seeding logic. The factory-default profile is uniquely identified by `profile_id = "factory_default"` AND `profile_name = "Default"`. The deletion guard MUST check `profile_id` because names are mutable and can collide with user-created profiles. T018-B MUST seed both fields to ensure INV-002 is satisfied from first load.

**Reviewer Checklist — Factory-Default Profile Identity**

Reviewers MUST verify that:
- The factory default is seeded with `profile_id = "factory_default"` AND `profile_name = "Default"`
- T018-B seeds both fields
- T024 deletion guard checks `profile_id == "factory_default"`, not `profile_name`
- INV-002 specifies both identifiers and the `profile_id`-based guard
- No other profile uses `profile_id = "factory_default"`
- A user-created profile named `"Default"` would NOT be treated as the factory default

---

### LOW — Advisory / Stale Text

---

#### N9 — data-model.md §1 entity diagram uses stale method name `record_last_used` ✅ RESOLVED

**Severity**: LOW → **RESOLVED (2026-04-26)**
**Affects**: `data-model.md` §1

**Resolution Summary**

`record_last_used` replaced with `save_last_used` in the §1 Entity Relationship Overview diagram.

Updates applied:

- **`data-model.md` §1**: Diagram line updated from `(via UAPService.record_last_used)` to `(via UAPService.save_last_used)`.

> **Governance Annotation — §1 Diagram Must Reference Canonical API (N9)**
> Earlier drafts referenced `record_last_used`, a legacy method removed during I3 remediation. The canonical API is `save_last_used()`, which performs the full-state write during window close (T032). All diagrams and references MUST use `save_last_used()`.

---

#### N10 — data-model.md §5 references deprecated `tabbed_hub.py` ✅ RESOLVED

**Severity**: LOW → **RESOLVED (2026-04-26)**
**Affects**: `data-model.md` §5

**Resolution Summary**

`tabbed_hub.py` replaced with `src/rfu/hub.py` in the §5 ToolManifest Entry preamble.

Updates applied:

- **`data-model.md` §5**: Preamble updated from `tabbed_hub.py` to `src/rfu/hub.py`.

> **Governance Annotation — §5 Must Reference Canonical Hub Path (N10)**
> Earlier drafts referenced `tabbed_hub.py`, a deprecated file path superseded by `src/rfu/hub.py` (see I6). The canonical ToolManifest registry resides in `src/rfu/hub.py`. All documentation MUST reference this path.

---

#### N11 — T036 parenthetical `(or src/rfu/tabbed_hub.py)` — residual deprecated path ✅ RESOLVED

**Severity**: LOW → **RESOLVED (2026-04-26)**
**Affects**: `tasks.md` T036

**Resolution Summary**

Parenthetical `(or src/rfu/tabbed_hub.py)` removed from T036. The task now references only `src/rfu/hub.py`.

Updates applied:

- **`tasks.md` T036**: Task line updated from `Modify src/rfu/hub.py (or src/rfu/tabbed_hub.py)` to `Modify src/rfu/hub.py`.

> **Governance Annotation — T036 Must Reference Canonical Hub Path (N11)**
> Earlier drafts referenced `src/rfu/tabbed_hub.py`, a deprecated file path removed during I6 remediation. The canonical hub implementation resides exclusively in `src/rfu/hub.py`. All tasks MUST reference this path.

---

#### N12 — quickstart.md pytest command path is malformed ✅ RESOLVED

**Severity**: LOW → **RESOLVED (2026-04-26)**
**Affects**: `quickstart.md`

**Resolution Summary**

Malformed single-path pytest command replaced with the correct two-path invocation targeting two separate test files.

Updates applied:

- **`quickstart.md`**: "Running the Contract Tests" command updated from `tests/contracts/gui/tests/unit/preferences/test_uap_service.py` to `tests/contracts/gui/test_menu_contract.py tests/unit/preferences/test_uap_service.py`.

> **Governance Annotation — Quickstart Must Use Correct Test Paths (N12)**
> Earlier drafts contained a malformed pytest path that incorrectly concatenated two directories, pointing to a file that does not exist. The contract suite consists of two independent test files that must each be invoked explicitly. The corrected command reflects the canonical directory structure established in I5 and prevents onboarding errors.

---

#### N13 — menu-contract.md "AFTER Help" constraint may conflict with Phase-2 constitutional 7-menu order ✅ RESOLVED

**Severity**: LOW (advisory) → **RESOLVED (2026-04-26)**
**Affects**: `contracts/menu-contract.md`

**Resolution Summary**

Phase-boundary governance advisory added to `menu-contract.md`. The "AFTER Help" clause is explicitly scoped to the Phase-1 5-menu topology and MUST NOT constrain Phase-2 constitutional menu placement.

Updates applied:

- **`contracts/menu-contract.md`**: Advisory block added immediately after the "AFTER Help" constraint line, scoping it to Phase-1 and recording the Phase-2 constitutional 7-menu order (`File, Edit, View, Tools, Reports, Window, Help`) as the authoritative topology for Phase-2.

> **Governance Annotation — Menu Ordering Across Phase Boundaries (N13)**
> The Phase-1 contract rule "Additional tool-specific menus MAY be appended AFTER Help" was correct for the 5-menu topology but is provisional. Constitution §7.2 defines a 7-menu topology for Phase-2 that supersedes this rule. Phase-2 MUST update the contract to reflect the constitutional ordering and MUST NOT rely on the Phase-1 append-after-Help rule. Recording this advisory now prevents Phase-2 contract tests from locking in the wrong ordering rule.

**Reviewer Checklist — Menu Ordering Across Phases**

Reviewers MUST verify that:
- Phase-1 uses the 5-menu topology with "append after Help" semantics
- Phase-2 uses the constitutional 7-menu topology (`File, Edit, View, Tools, Reports, Window, Help`)
- No Phase-2 contract or test encodes the Phase-1 append-after-Help rule
- Tool-specific menus in Phase-2 follow the constitutional order
- No artifact mixes Phase-1 and Phase-2 ordering rules

---

#### N14 — plan.md AppearanceProfile example JSON omits `window_x` and `window_y` ✅ RESOLVED

**Severity**: LOW → **RESOLVED (2026-04-26)**
**Affects**: `plan.md`

**Resolution Summary**

`window_x` and `window_y` added to the AppearanceProfile example JSON in `plan.md`. The example now matches the `"required"` array in `contracts/appearance-profile.md`.

Updates applied:

- **`plan.md`**: `"window_x": -1` and `"window_y": -1` added to the example JSON blob in the `contracts/appearance-profile.md` section (sentinel values, consistent with INV-005). Governance annotation added below the example.

> **Governance Annotation — Example JSON Must Match Schema `required` Array (N14)**
> Earlier drafts omitted `window_x` and `window_y` from the plan.md example AppearanceProfile JSON. These fields have been part of the Version-1 schema since the initial definition (I8). `plan.md` is onboarding-critical and its examples directly influence contributor implementations. All example JSON MUST include every field in the schema `"required"` list. Omitting required fields silently guides contributors toward schema-invalid `to_json()` / `from_json()` implementations.

**Reviewer Checklist — Example JSON Completeness**

Reviewers MUST verify that:
- All example JSON in `plan.md` includes every field in the schema's `"required"` list
- `window_x` and `window_y` are present in the AppearanceProfile example
- No example contradicts the canonical schema in `contracts/appearance-profile.md`
- No example omits fields that would cause schema validation failures

---

## Governance Reviewer Checklist — Pass 2 Status

| # | Item | Status |
|---|---|---|
| 1 | `profile_schema_version` placement resolved (N1) | ✅ Resolved — Option A: per-profile field inside AppearanceProfile JSON blob; schema v2; data-model §6 updated; T014 FACTORY_DEFAULTS updated |
| 2 | `is_user_created` field resolved (N2) | ✅ Resolved — Option C: optional field `{ "type": "boolean", "default": false }` in properties; NOT in required; dataclass default `False`; spec.md updated |
| 3 | T015 includes INV-006 cross-field check (N3) | ✅ Resolved — INV-006 mixed-sentinel bullet added to T015 `__post_init__`; governance annotation added |
| 4 | BC-004 references correct method name (N4) | ✅ Resolved — BC-004 rewritten to reference `set_font(family, size)` → `set_font_preferences()`; governance annotation added |
| 5 | T005 covers `set_font_preferences()` (N5) | ✅ Resolved — isolation test bullet added to T005; governance annotation added |
| 6 | T021 mandates `findChildren` for font propagation (N6) | ✅ Resolved — `findChildren(QWidget)` iteration explicitly mandated in T021 font bullet; governance annotation added |
| 7 | T028 OK-handler uses signal only (N7) | ✅ Resolved — direct `parent_window.setFont()` call removed; signal-only path via T033 mandated; governance annotation added |
| 8 | Factory-default identity aligned across INV-002/T018-B/T024 (N8) | ✅ Resolved — INV-002 updated with dual identity + `profile_id` guard; T018-B seeds `profile_name`; T024 guard clarified |
| 9 | data-model §1 uses `save_last_used` (N9) | ✅ Resolved — `record_last_used` replaced with `save_last_used` in §1 entity diagram |
| 10 | data-model §5 references `src/rfu/hub.py` (N10) | ✅ Resolved — `tabbed_hub.py` replaced with `src/rfu/hub.py` in §5 preamble |
| 11 | T036 parenthetical removed (N11) | ✅ Resolved — `(or src/rfu/tabbed_hub.py)` parenthetical removed from T036 |
| 12 | quickstart.md pytest paths corrected (N12) | ✅ Resolved — malformed concatenated path replaced with correct two-path invocation |
| 13 | Phase-2 menu positions recorded (N13) | ✅ Resolved — Phase-2 advisory added to menu-contract.md; "AFTER Help" rule scoped to Phase-1 topology; constitutional 7-menu order recorded |
| 14 | plan.md example JSON includes `window_x`/`window_y` (N14) | ✅ Resolved — `window_x: -1` and `window_y: -1` added to example JSON; governance annotation added |

---

## Questions for Implementation Clarification

The following questions require answers before Phase-2 (TDD) implementation begins. They correspond directly to findings that block one or more tasks.

### Q1 — `profile_schema_version`: per-profile field or per-category key? *(blocks N1)*

> **RESOLVED (2026-04-26) — Decision: Option A.** `profile_schema_version` is a per-profile field inside each AppearanceProfile JSON blob. `contracts/appearance-profile.md` schema bumped to v2 with `profile_schema_version` in `required` + `properties`. `data-model.md` §6 top-level key removed. `tasks.md` T014 `FACTORY_DEFAULTS` updated to include `profile_schema_version: 2`. See N1 resolution above.

**Context** *(historical, for audit trail)*: The data-model (§6) and migration table treated `profile_schema_version` as a top-level `uap.*` preference key stored alongside `mode`, `active_profile_id`, etc. The G2 remediation in T004 treated it as a field inside each serialized `AppearanceProfile` JSON blob — and T018-B seeded it as a profile attribute.

The JSON schema had `"additionalProperties": false` and omitted `profile_schema_version` from `"required"` and `"properties"`, so the schema would reject a profile blob that contained it.

~~**Decision needed**: Is `profile_schema_version`:~~
~~- **(A) A per-profile field** — inside each `AppearanceProfile` blob; requires JSON schema update (add to `required` + `properties`; schema version bump to v2)?~~
~~- **(B) A per-category top-level key** — stored as `uap.profile_schema_version` alongside `mode`; G2 test scope corrected to check the UAPSettings key, not `to_json()` output; T018-B corrected to not seed it on the profile?~~

### Q2 — `is_user_created`: persisted field or service-layer tag? *(blocks N2)*

> **RESOLVED (2026-04-26) — Decision: Option C.** `is_user_created` is an optional schema field with `"default": false`. Added to `"properties"` in `contracts/appearance-profile.md`; NOT in `"required"`. `data-model.md` §2 updated with `is_user_created: bool = False`. `spec.md` AppearanceProfile entity updated. T018-B `is_user_created=False` seed line is now valid. See N2 resolution above.

**Context** *(historical, for audit trail)*: T018-B seeded the factory-default `AppearanceProfile` with `is_user_created=False`. This field did not exist in the JSON schema, data-model dataclass, or spec entity. The schema's `"additionalProperties": false` would have caused any blob containing it to fail validation, and the dataclass constructor would have raised `TypeError`.

~~**Decision needed**: Is `is_user_created`:~~
~~- **(A) A persisted field** in `AppearanceProfile` — add to schema as required or optional?~~
~~- **(B) A service-layer-only runtime concept** — factory default identified solely by `profile_id = "factory_default"`; remove from T018-B seed call?~~
~~- **(C) An optional schema field** with `"default": false` — no migration required?~~

### Q3 — `UAPService` instantiation model *(implementation risk)*

**Context**: Multiple tasks call `UAPService()` (fresh instantiation at each call site):
- T028 OK: `UAPService().set_font(family, size)`
- T029 OK: `UAPService().set_directory(new_path)`

If `UAPService` holds in-memory state (a preferences cache, for example), creating a new instance per call will bypass that cache. `ThemeManager` uses a singleton pattern (`ThemeManager.instance()`). No equivalent is specified for `UAPService`.

**Decision needed**: Should `UAPService` be implemented as a singleton (class-level `instance()` method), or is it designed to be fully stateless (all reads/writes go directly to the preference store, no in-memory caching)?

### Q4 — T028 font application: direct call or signal only? *(resolves N7)*

**Context**: T028's OK-handler spec calls `parent_window.setFont()` directly before `UAPService().set_font()`. Because `set_font()` emits `uap_font_changed`, T033's slot on `parent_window` will also be invoked — propagating the font to all children via `findChildren`. The direct call does not iterate children, so only the signal path covers full propagation.

**Decision needed**: Should T028's OK-handler:
- **(A) Remove the direct `parent_window.setFont()` call** — rely entirely on the `uap_font_changed` signal emitted by `UAPService.set_font()` to reach all windows including `parent_window`?
- **(B) Keep both** — the direct call is intentional for immediate UI feedback before the signal propagates?

### Q5 — T021 `apply()` font propagation: `findChildren` or Qt propagation? *(resolves N6)*

**Context**: U1 found that Qt's default `setFont()` propagation does not reach children with explicitly-set fonts. T033 was corrected to iterate `findChildren(QWidget)`. T021's `apply()` (initial font-on-open) uses the phrase "on window and all child widgets" without specifying the mechanism.

**Decision needed**: Should T021 `apply()` use the same `findChildren(QWidget)` approach as T033, or is Qt's default `setFont()` propagation sufficient for initial apply (because no child has yet set an explicit font at window-open time)?

### Q6 — Factory-default identity guard: `profile_id` or `profile_name`? *(resolves N8)*

**Context**: INV-002 identifies the factory default by `profile_name = "Default"`. T024's deletion guard triggers on `delete_profile("factory_default")` (by `profile_id`). T018-B does not specify a `profile_name` for the seeded default.

**Decision needed**: Should the deletion guard check:
- **(A) `profile_id == "factory_default"`** (T024 approach) — update INV-002 to match, add `profile_name = "Default"` to T018-B seed?
- **(B) `profile_name == "Default"`** (INV-002 approach) — update T024 to pass by name, update T018-B to specify the name?

### Q7 — Tool harmonization scope for T041 and T048 ✅ RESOLVED

> **RESOLVED (2026-04-26) — Decision: P3-Q7.**

**Q7-A — UAP Exemption List:**
> No pre-populated exemption list SHALL exist in Phase-3. All tools SHALL be assumed to subclass `StandardWindow` unless explicitly exempted in Phase-4 UX harmonization.

Rationale: Phase-3 is about correctness, not UX exceptions. Pre-populating an exemption list before the Phase-4 harmonization sweep would constitutionalize decisions that have not yet been audited.

**Q7-B — T041 vs T048 Ordering:**
> T041 SHALL remain an independent headless audit pass. T048 SHALL depend on T041 but SHALL NOT subsume it.

Rationale: T041 is a constitutional audit (menu topology verification); T048 is an inheritance sweep (StandardWindow migration). They address different concerns and must remain distinct steps to preserve auditability.

> **Governance Annotation — Tool Harmonization Scope (P3-Q7)**
> Phase-3 does not define a `uap_exempt` pre-population set. Any tool requiring exemption from StandardWindow subclassing MUST be identified during the T048 sweep and recorded explicitly at that time. T041 MUST remain a standalone audit step and MUST NOT be folded into T048 as a sub-step.

**Context** *(historical, for audit trail)*: T041 requires headless instantiation of every `ToolManifest`-registered tool class to audit menu topology. T048 requires identifying all tools that do NOT subclass `StandardWindow` for migration. The codebase has approximately 30–40 tool windows.

### Q8 — Phase-2 "Reports" and "Window" menu positions ✅ RESOLVED

> **RESOLVED (2026-04-26) — Decision: P3-Q8.**

> `menu-contract.md` SHALL NOT pre-reserve Phase-2 menu positions in Phase-3. The constitutional 7-menu order (`File, Edit, View, Tools, Reports, Window, Help`) is recorded as an advisory via N13, but Phase-2 menus SHALL be introduced only when Phase-2 begins.

Rationale: Phase-3 must not constitutionalize future menus prematurely. Pre-updating the Phase-1 contract with Phase-2 positions would conflate two governance phases and could cause Phase-1 contract tests to encode Phase-2 semantics before Phase-2 has been specified.

> **Governance Annotation — Menu Position Reservation (P3-Q8)**
> The "AFTER Help" constraint in `menu-contract.md` is explicitly scoped to the Phase-1 5-menu topology (see N13 advisory). Phase-2 MUST update `menu-contract.md` to reflect the constitutional 7-menu order at Phase-2 contract-authoring time. No Phase-3 artifact SHALL pre-encode Phase-2 menu positions.

**Context** *(historical, for audit trail)*: `menu-contract.md` allows additional menus "AFTER Help". Constitution §7.2 defines a 7-menu topology but does not specify exact positions in the Phase-1 document. When Phase 2 adds Reports and Window menus, their positions in the constitutional order (`File → Edit → View → Tools → Reports → Window → Help`) do not match the "append after Help" rule.

---

## Recommended Resolution Order

| Priority | Finding | Blocking? | Recommended fix location |
|---|---|---|---|
| 1 | **N1** — `profile_schema_version` placement | ✅ Resolved (2026-04-26) | Option A applied: appearance-profile.md schema bumped to v2; data-model §6 top-level key removed; T014 FACTORY_DEFAULTS updated |
| 2 | **N2** — `is_user_created` not in schema | ✅ Resolved (2026-04-26) | Option C applied: optional property added to appearance-profile.md; dataclass default False; spec.md updated; T018-B valid as-is |
| 3 | **N3** — T015 missing INV-006 check | ✅ Resolved (2026-04-26) | INV-006 mixed-sentinel bullet added to T015 `__post_init__`; governance annotation added inline |
| 4 | **N4** — BC-004 wrong method name | ✅ Resolved (2026-04-26) | BC-004 rewritten in uap-preferences.md: `set_font_size` → `set_font(family, size)` + `set_font_preferences()` pipeline |
| 5 | **N5** — T005 missing `set_font_preferences` test | ✅ Resolved (2026-04-26) | `set_font_preferences()` isolation test bullet added to T005; governance annotation added inline |
| 6 | **N6** — T021 no `findChildren` mandate | ✅ Resolved (2026-04-26) | `findChildren(QWidget)` iteration explicitly mandated in T021 font bullet; governance annotation added |
| 7 | **N7** — T028 double font application | ✅ Resolved (2026-04-26) | Direct `parent_window.setFont()` call removed from T028; signal-only path via T033 mandated; governance annotation added |
| 8 | **N8** — factory default identity ambiguity | ✅ Resolved (2026-04-26) | INV-002 updated with dual identity + `profile_id` guard; T018-B seeds `profile_name`; T024 guard clarified |
| 9 | **N9** — data-model §1 stale method name | ✅ Resolved (2026-04-26) | `record_last_used` replaced with `save_last_used` in §1 entity diagram |
| 10 | **N11** — T036 deprecated parenthetical | ✅ Resolved (2026-04-26) | `(or src/rfu/tabbed_hub.py)` parenthetical removed from T036 |
| 11 | **N10** — data-model §5 stale hub reference | ✅ Resolved (2026-04-26) | `tabbed_hub.py` replaced with `src/rfu/hub.py` in §5 preamble |
| 12 | **N12** — quickstart malformed pytest path | ✅ Resolved (2026-04-26) | Malformed concatenated path replaced with correct two-file invocation |
| 13 | **N14** — plan.md missing window_x/y | ✅ Resolved (2026-04-26) | `window_x: -1` and `window_y: -1` added to example JSON; governance annotation added |
| 14 | **N13** — menu-contract Phase-2 positions | ✅ Resolved (2026-04-26) | Phase-2 advisory added to menu-contract.md; constitutional 7-menu order recorded; Q8 closed |

---

*End of SpecKit Analysis Report — Pass 2*
