# Tool Capability Matrix Template

**Constitution Reference**: §12  
**Version**: 1.37.0  
**Added**: 2026-04-24 (harmonization2 Phase 4)

---

## Overview

This is the canonical reviewer-facing template for tracking Tool Capability
Matrix compliance across all tools in the RFU suite. One row per tool, one
column per capability code. The machine-readable version is maintained in
`docs/tool-capability-matrix.json`.

---

## Capability Code Reference

| Code | Domain | Required | Constitution Ref |
|------|--------|----------|-----------------|
| **TH** | Theming compliance (tokens, live updates) | Yes | §Additional Constraint (theming) |
| **DR** | Dry-run support before destructive actions | Yes | §II.1 |
| **CP** | Shared components (buttons, modals, toasts) | Yes | §10.5, §10.6 |
| **A11Y** | Accessibility compliance | Yes | §7 Additional Constraint |
| **PERF** | UI-thread audit, worker offloading | Yes | §IV, §10.7 |
| **ERR** | Error handling contract | Yes | §10.8 |
| **GRD** | Guardian registration & fallback | Yes | §V |
| **TEL** | Telemetry events (load, action, error, perf) | Yes | §III |
| **STR** | Centralized strings (`ui_strings.py`) | Yes | §11.4.6 |
| **CE** | Critical Engine tests (if classified) | Conditional | §III, §G.6 |
| **HUB** | Hub integration & relaunch | Yes | §9.8 |
| **MEN** | Menu architecture compliance | Yes | §7 |
| **NOM** | Nomenclature — structural UI naming: menu items, action labels, command names, reserved verbs (§7.4.1, §7.4.4) | Yes | §12.1 |
| **FNT** | Font token compliance (spec resolved in v1.37.0; implementation tracked via TODO(FONT_TOKENS_IMPL)) | Yes | §11.4.8 |
| **LYT** | Layout structure compliance (spec resolved in v1.37.0; implementation tracked via TODO(LAYOUT_TOKENS_IMPL)) | Yes | §11.4.9 |
| **WRD** | Wording/Microcopy — contextual runtime text: tooltips, body text, error messages, toasts (§7.4.2, §7.4.3) | Yes | §12.1 |
| **INT** | UI Interaction Contract compliance | Yes | §10 |
| **OPS** | Operational Guarantees compliance | Yes | §13.2 |
| **CI** | CI rule compliance | Yes | §11 |
| **L10N** | Localization readiness | Future | §13.4.1 |

**Status values**: ☑ Compliant · ☐ Non-Compliant · N/A Not Applicable · ? Unknown

---

## Per-Tool Matrix

| Tool | TH | DR | CP | A11Y | PERF | ERR | GRD | TEL | STR | CE | HUB | MEN | NOM | FNT | LYT | WRD | INT | OPS | CI | L10N | Owner | Last Reviewed | Phase Gate |
|------|----|----|----|----|------|-----|-----|-----|-----|-----|-----|----|----|----|----|-----|-----|-----|----|----|-------|---------------|------------|
| FileFinder | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| CatalogWindow | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| CopyMoveSyncDelete | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☑ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| SizeAnalyzer | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| DuplicateFinder | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☑ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| SecureDelete | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☑ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| EnAndDecrypt | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☑ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |
| NetworkConnectivity | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | N/A | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | — | — | Phase 1 |

*All remaining tools to be populated during Phase 4 harmonization sweep.*

---

## Governance Rules

### Adding a new tool

1. Add a row with all capabilities set to ☐
2. Assign an owner
3. Schedule Phase Gate review
4. CI MUST reject the tool if any required capability remains ☐ after the Phase Gate

### Completing a capability

1. Implement per the relevant spec document
2. Run CI gate for that capability
3. Update status from ☐ to ☑
4. Record reviewer and date

### Partial compliance

Partial compliance (capability in progress) MUST be tracked in the Notes column
and MUST NOT be recorded as ☑. CI MUST treat Partial as non-compliant (§11.7).

### Open Constitutional TODO Prioritization (Execution Policy)

The following unresolved constitutional TODOs are governance-tracked and MUST be
triaged each release planning cycle. Priority determines enforcement urgency.

#### P0 — CI/Governance blockers

1. `TODO(HUB_MENU_REGISTRY_API)`
2. `TODO(RELAUNCH_TOOL_WINDOW_API)`
3. `TODO(OPS_PHASE3_SPEC)`

Definition of done for P0:
- Spec and API contract published
- Implementation merged
- CI gates switched from deferred/advisory to enforced where applicable

#### P1 — Security and identity operating controls

1. `TODO(HEADLESS_AUTH)`
2. `TODO(AUTO_UNLOCK_WORKFLOW)`
3. `TODO(BREAK_GLASS_PROCEDURE)`
4. `TODO(ROLE_MIGRATION)`
5. `TODO(MFA_POLICY)`
6. `TODO(PII_SCAN_BASELINE)`

Definition of done for P1:
- Security review sign-off
- Test evidence in CI
- Operations runbook updated with owner and cadence

#### P2 — UX and documentation completion

1. `TODO(HUB_UX_COHESION)`
2. `TODO(FONT_TOKENS_IMPL)`
3. `TODO(LAYOUT_TOKENS_IMPL)`
4. `TODO(GUARDIAN_DEGRADED_UX)`
5. `TODO(PORTABILITY_FORMAT)`
6. `TODO(AUTH_DOCS)`
7. `TODO(FILE_VALIDATOR_SIGS)`
8. `TODO(GOVERNANCE_DOC)`

Definition of done for P2:
- Document published and versioned
- Cross-references added to constitution/checklists
- Owner assigned for long-term maintenance

### Required Triage Metadata

For each open TODO, governance tracking MUST capture:

1. Owner role
2. Target milestone/release
3. Enforcement impact (`none`, `deferred gate`, `active gate`)
4. Evidence links (PR, test run, docs)

Without this metadata, a TODO is considered untriaged and release planning is
incomplete.

### Authoritative Owner and Milestone Mapping

| TODO | Owner Role | Target Milestone | Enforcement Impact |
|------|------------|------------------|--------------------|
| TODO(HUB_MENU_REGISTRY_API) | Maintainer | v1.38.0 | deferred gate |
| TODO(RELAUNCH_TOOL_WINDOW_API) | Maintainer | v1.38.0 | deferred gate |
| TODO(OPS_PHASE3_SPEC) | Release Steward | v1.39.0 | deferred gate |
| TODO(HEADLESS_AUTH) | Security | v1.39.0 | none |
| TODO(AUTO_UNLOCK_WORKFLOW) | Security | v1.39.0 | none |
| TODO(BREAK_GLASS_PROCEDURE) | Security | v1.39.0 | none |
| TODO(ROLE_MIGRATION) | Maintainer | v1.39.0 | none |
| TODO(MFA_POLICY) | Security | v1.39.0 | none |
| TODO(PII_SCAN_BASELINE) | Security | v1.40.0 | none |
| TODO(HUB_UX_COHESION) | UX | v1.40.0 | none |
| TODO(FONT_TOKENS_IMPL) | UX | v1.40.0 | none |
| TODO(LAYOUT_TOKENS_IMPL) | UX | v1.40.0 | none |
| TODO(GUARDIAN_DEGRADED_UX) | UX | v1.40.0 | none |
| TODO(PORTABILITY_FORMAT) | Release Steward | v1.40.0 | none |
| TODO(AUTH_DOCS) | Release Steward | v1.40.0 | none |
| TODO(FILE_VALIDATOR_SIGS) | Maintainer | v1.40.0 | none |
| TODO(GOVERNANCE_DOC) | Release Steward | v1.40.0 | none |

---

## Phase Gate Definitions

| Phase Gate | Meaning |
|-----------|---------|
| Phase 1 | Foundation complete (TH, DR, CP, A11Y, PERF, ERR, GRD, TEL, STR) |
| Phase 2 | Interaction model complete (INT, MEN, NOM, FNT, LYT, WRD) |
| Phase 3 | Operational guarantees complete (OPS, HUB) |
| Phase 4 | Full compliance (CI + CE where applicable) |
| Future | Localization readiness (L10N) |

---

## Cross-References

- Constitution §12 (normative)
- Constitution §11 CI Enforcement Specification
- docs/ci-enforcement-spec.md
- .specify/memory/checklist-ci-enforcement-compliance.md
