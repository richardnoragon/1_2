# Critical Engine Classification Checklist

**Applicable constitution sections**: §G.6, §III, §III.1
**Related documents**: [docs/critical-engines.md](../../docs/critical-engines.md), [checklist-side-effect-dry-run-compliance.md](checklist-side-effect-dry-run-compliance.md)
**Version**: 1.0 (introduced constitution v1.17.0, 2026-04-04 Q4)

---

## Purpose

This checklist is used by maintainers during PR review to determine whether a
module qualifies as a **critical engine** under §G.6, and to ensure that all
classified critical engines carry the required test coverage and documentation.

A module is a critical engine if it meets **ANY ONE** of the five criteria
below. Failing to classify correctly is a constitutional violation — both
under-classification (hiding a high-risk module from stricter tests) and
over-classification (forcing unnecessary test burden) are problems.

---

## Section A — Criteria Evaluation (§G.6)

For each criterion, answer Yes/No. **Any single Yes = Critical Engine.**

### A1 — Irreversible or Destructive Operations (§G.6(a))

| Check | Yes / No |
|-------|----------|
| Does the module delete, overwrite, secure-wipe, anonymize, or perform lossy transformations? | |
| Could a defect in this module cause permanent data loss? | |
| Does the module produce output that cannot be trivially reversed? | |

**Cross-reference**: §G.4 (Destructive operation), §II.5 (Headless HMAC token for headless destructive ops)

---

### A2 — Large-Scale or Batch Operations (§G.6(b))

| Check | Yes / No |
|-------|----------|
| Can the module operate on multiple files or resources in a single invocation? | |
| Would a single defect propagate across many user assets simultaneously? | |
| Examples: batch renamers, batch converters, batch metadata writers, multi-file processors | |

---

### A3 — High-Impact Data Transformations (§G.6(c))

| Check | Yes / No |
|-------|----------|
| Does the module perform deduplication, compression, OCR, PDF extraction, checksum validation, or image normalization? | |
| Would incorrect behavior silently corrupt or misclassify data without an obvious error? | |
| Is the correctness of the module's output essential to downstream operations? | |

---

### A4 — Untrusted External Input (§G.6(d))

| Check | Yes / No |
|-------|----------|
| Does the module ingest data from an external or untrusted source? | |
| Examples: network sync, remote metadata fetch, external file parsing, archive extraction | |
| Could malformed input trigger incorrect behavior across user assets? | |

---

### A5 — Security-Sensitive Operations (§G.6(e))

| Check | Yes / No |
|-------|----------|
| Does the module interact with encryption, decryption, or key handling? | |
| Does the module perform secure deletion or interact with the secure delete engine? | |
| Does the module handle authentication, token validation (see §G.5), or session data? | |
| Does the module enforce or interact with sandbox boundaries? | |

---

### A6 — Reviewer Override

Even if no criterion above is met, a maintainer MAY classify a module as a
critical engine if its failure mode is high-impact or if its behavior interacts
with other critical engines.

| Check | Yes / No |
|-------|----------|
| Does the reviewer believe the module's failure mode is disproportionately high-impact? | |
| Does the module interact closely with other already-classified critical engines? | |

**If reviewer override is applied**: reasoning MUST be documented in the PR description.

---

## Section B — Classification Decision

| Result | Action |
|--------|--------|
| **Any A1–A5 = Yes** | Module IS a critical engine → proceed to Section C |
| **A6 override applied** | Module IS a critical engine → proceed to Section C + document override in PR |
| **All A1–A5 = No, no override** | Module is NOT a critical engine → no further action required |

---

## Section C — Documentation Requirements (§III.1)

If classified as a critical engine, ALL of the following MUST be completed before merge:

| # | Requirement | Done |
|---|-------------|------|
| C1 | Module metadata file (e.g., `module.yaml` or `module.json`) includes `critical_engine: true` | |
| C2 | Module README includes a `## Critical Engine Classification` section stating which criterion/a apply | |
| C3 | `docs/critical-engines.md` registry entry added or updated for this module | |
| C4 | PR description identifies the applicable §G.6 criterion/a | |
| C5 | If maintainer override (A6), PR description documents the reasoning | |

**Template for module README section**:
```markdown
## Critical Engine Classification
This module is classified as a critical engine under §G.6 because:
- Criterion (X): <brief justification>
[Repeat for each criterion that applies]
```

**Template for metadata file**:
```yaml
critical_engine: true
critical_engine_criteria:
  - "§G.6(X): <brief justification>"
```

---

## Section D — Test Coverage Requirements (§III)

All critical engines MUST have property-based or scenario edge tests covering
ALL FIVE of the following scenarios:

| # | Scenario | Tests Present | CI Passes |
|---|----------|---------------|-----------|
| D1 | Empty input | | |
| D2 | Single-element input | | |
| D3 | Maximum-expected-size input | | |
| D4 | Random/unexpected input (fuzz or property-based) | | |
| D5 | Adversarial/malformed input | | |

**No minimum test count** is prescribed beyond satisfying all five scenarios.

**FAIL conditions (any one = PR blocked)**:
- Any of the five scenarios has no test coverage
- Tests exist but are skipped, disabled, or marked TODO
- Tests exist but do not actually exercise the module under test

---

## Section E — CI Enforcement Gates

| # | CI Check | Gate Failure Condition |
|---|----------|------------------------|
| E1 | Module metadata scan | Module marked `critical_engine: true` but missing any of the five §III test scenarios |
| E2 | Module metadata scan | Module added/modified without a classification declaration |
| E3 | Coverage enforcement | Critical engine module has < 85% line coverage (matches global floor) |
| E4 | Test execution | Any test for a critical engine is skipped or disabled without documented exception |
| E5 | Registry check | `docs/critical-engines.md` not updated to reflect new or changed classification |

---

## Section F — Known Critical Engines (Current Registry Snapshot)

See `docs/critical-engines.md` for the authoritative and up-to-date registry.
The table below lists founding classifications:

| Module | §G.6 Criteria | Source |
|--------|---------------|--------|
| Duplicate detection engine | (b), (c) | §III original parenthetical (illustrative) |
| Secure delete engine | (a), (e) | §III original parenthetical (illustrative) |
| Batch processors | (a), (b) | §III original parenthetical (illustrative) |
| PDF tools / processors | (c), (d) | §G.6 new examples (Q4) |
| Compression engine | (c) | §G.6 new examples (Q4) |
| Network sync module | (d) | §G.6 new examples (Q4) |
| Archive extractor | (d) | §G.6 new examples (Q4) |
| OCR engine | (c), (d) | §G.6 new examples (Q4) |

---

## Section G — Cross-References

| Reference | Location | Notes |
|-----------|----------|-------|
| §G.6 — Critical engine | constitution.md §G Normative Glossary | Normative criteria definition |
| §III — Test-Driven Quality | constitution.md §III | Five-scenario test requirement |
| §III.1 — Classification Authority | constitution.md §III.1 | Who may classify; governance model |
| §G.4 — Destructive operation | constitution.md §G.4 | Criterion (a) cross-reference |
| §II — Safety & Data Integrity | constitution.md §II | Dry-run and confirmation for criterion (a) engines |
| §G.5 — Headless HMAC token | constitution.md §G.5 | Applies to criterion (e): token validation |
| docs/critical-engines.md | docs/ | Authoritative module registry |
| checklist-side-effect-dry-run-compliance.md | .specify/memory/ | For modules meeting criterion (a) |
| checklist-hmac-token-compliance.md | .specify/memory/ | For modules meeting criterion (e): token validation |

---

## Reviewer Sign-Off

| Reviewer | Role | Classification Decision | Date |
|----------|------|------------------------|------|
| | | ☐ Critical Engine  ☐ Not Critical  ☐ Override Applied | |
| | | ☐ Critical Engine  ☐ Not Critical  ☐ Override Applied | |

**PR MUST NOT merge if the module is classified as a critical engine and any
Section C documentation item or any Section D test scenario is unresolved.**
