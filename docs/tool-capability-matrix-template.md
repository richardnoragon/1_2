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
| **FNT** | Font token compliance (deferred — see TODO(FONT_TOKENS_SPEC)) | Yes | §11.4.8 |
| **LYT** | Layout structure compliance (deferred — see §8.9 and TODO(LAYOUT_TOKENS_SPEC)) | Yes | §11.4.9 |
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
