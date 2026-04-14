# Critical Engines Registry

**Governing constitution sections**: §G.6, §III, §III.1
**Version**: 1.0 (established constitution v1.17.0, 2026-04-04 Q4)
**Maintainer checklist**: [.specify/memory/checklist-critical-engine-classification.md](../.specify/memory/checklist-critical-engine-classification.md)

---

## Purpose

This file is the authoritative registry of all modules classified as critical
engines under §G.6 of the project constitution. It MUST be updated whenever:

- A new module is classified as a critical engine (§III.1)
- An existing classification is revised or removed
- A maintainer override is applied (Section A6 of the checklist)

The CI pipeline MUST reference this file to enforce the §III property-based /
scenario edge test requirement.

---

## §G.6 Criteria Reference

A module qualifies as a critical engine if it meets **ANY ONE** of:

| Criterion | Summary |
|-----------|---------|
| **(a)** | Performs irreversible or destructive operations (§G.4: delete, overwrite, wipe, anonymization, lossy transform) |
| **(b)** | Large-scale or batch operations on multiple user assets |
| **(c)** | High-impact data transformations where correctness is essential (dedup, compression, OCR, PDF, checksum) |
| **(d)** | Processes untrusted external input (network sync, remote fetch, archive extraction, external file parsing) |
| **(e)** | Security-sensitive operations (encryption, secure delete, auth, token validation, sandbox boundaries) |

---

## Founding Classifications

These modules were classified at the establishment of this registry (constitution
v1.17.0). The first three derive from the §III original parenthetical list;
the remainder reflect §G.6 new examples added during Q4 clarification.

| # | Module / Engine | §G.6 Criteria | Classification Source | Added |
|---|-----------------|---------------|-----------------------|-------|
| 1 | Duplicate detection engine | (b) large-scale, (c) correctness-critical | §III original parenthetical (illustrative) | v1.17.0 |
| 2 | Secure delete engine | (a) irreversible, (e) security-sensitive | §III original parenthetical (illustrative) | v1.17.0 |
| 3 | Batch processors | (a) irreversible (when destructive), (b) large-scale | §III original parenthetical (illustrative) | v1.17.0 |
| 4 | PDF tools / processors | (c) high-impact transform, (d) external input | §G.6 new examples (Q4) | v1.17.0 |
| 5 | Compression engine | (c) high-impact transform (lossy/lossless) | §G.6 new examples (Q4) | v1.17.0 |
| 6 | Network sync module | (d) untrusted external input | §G.6 new examples (Q4) | v1.17.0 |
| 7 | Archive extractor | (d) untrusted external input (e.g., zip-slip risk) | §G.6 new examples (Q4) | v1.17.0 |
| 8 | OCR engine | (c) correctness-critical transform, (d) external input | §G.6 new examples (Q4) | v1.17.0 |

---

## Modules Reviewed and Not Classified

The following modules have been explicitly reviewed and determined NOT to meet
§G.6 criteria at the time of review. They MUST be re-evaluated if their scope
changes materially.

| Module / Engine | Review Date | Criteria Evaluated | Reviewer | Notes |
|-----------------|-------------|-------------------|----------|-------|
| Theme manager | v1.17.0 | (a)–(e) | — | No data operations; no security surface |
| UI layout / panel manager | v1.17.0 | (a)–(e) | — | Presentation only; no data at risk |
| Settings panel | v1.17.0 | (a)–(e) | — | Preference reads; writes covered by §VI |

---

## Classification Change Log

| Version | Module | Change | Criteria | Maintainer | PR |
|---------|--------|--------|----------|------------|-----|
| v1.17.0 | All founding entries | Initial classification | See table above | — | — |

---

## Adding a New Classification

To add a new classification, open a PR that:

1. Updates the **Founding Classifications** table (or adds a separate section
   for new classifications with appropriate version and date).
2. Updates the **Classification Change Log**.
3. Adds `critical_engine: true` and `critical_engine_criteria` to the module's
   metadata file.
4. Adds a `## Critical Engine Classification` section to the module's README.
5. Includes property-based or scenario edge tests covering all five §III
   scenarios in the PR.
6. References the §G.6 criterion or criteria that apply.

The PR MUST be reviewed by at least one maintainer. If a maintainer override
(§G.6 criterion A6) is being applied, reasoning MUST appear in the PR
description.

---

## CI Integration Notes

The CI pipeline should:

1. Parse all `module.yaml` / `module.json` files for `critical_engine: true`.
2. For each such module, verify that tests covering all five §III scenarios
   are present and passing.
3. Verify that the module appears in this registry with a matching entry.
4. Fail the build if any critical engine module lacks coverage of any of the
   five required scenarios.

See [checklist-critical-engine-classification.md](../.specify/memory/checklist-critical-engine-classification.md)
Section E for the full CI gate specification.

---

## Cross-References

| Reference | Location |
|-----------|----------|
| §G.6 — Critical engine definition | constitution.md §G Normative Glossary |
| §G.4 — Destructive operation | constitution.md §G.4 (criterion (a) source) |
| §III — Test-Driven Quality | constitution.md §III (five-scenario requirement) |
| §III.1 — Classification Authority | constitution.md §III.1 (governance) |
| Reviewer checklist | .specify/memory/checklist-critical-engine-classification.md |
| Side-effect dry-run checklist | .specify/memory/checklist-side-effect-dry-run-compliance.md |
| HMAC token checklist | .specify/memory/checklist-hmac-token-compliance.md |
