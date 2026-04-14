# Round-Trip Fidelity Compliance Checklist

**Applicable constitution sections**: §G.8, §DW13.1–§DW13.4  
**Spec reference**: [docs/round-trip-fidelity-spec.md](../../docs/round-trip-fidelity-spec.md)  
**Related checklists**: [checklist-export-encryption-compliance.md](checklist-export-encryption-compliance.md)  
**Version**: 1.0 (introduced constitution v1.21.0, 2026-04-04 Q8)  

Apply this checklist to every PR that introduces or modifies:
- preference export code
- preference import code
- round-trip fidelity tests
- preference schema or migration logic

---

## Section A — Scope of "Identical" (§DW13.1 / §DW13.2)

| # | Check | Pass / Fail |
|---|-------|-------------|
| A1 | "Round-trip fidelity" is understood in code and tests as: `preference_category`, `preference_key`, `preference_value`, and `value_type` match exactly | |
| A2 | Code does NOT attempt full-record byte-for-byte equality after an import cycle | |
| A3 | `ROUND_TRIP_FIELDS` constant (from `round_trip_fields.py`) is used in export, import, and test code — no locally redefined field list | |
| A4 | `METADATA_FIELDS` constant (from `round_trip_fields.py`) is used to document excluded fields | |

**FAIL conditions (any one = PR blocked)**:
- Code or tests assert full-record equality including `created_at`, `modified_at`, or `record_id`
- Each PR/module defines its own field list rather than using the canonical constants

---

## Section B — Export Behavior (§DW13.1)

| # | Check | Pass / Fail |
|---|-------|-------------|
| B1 | Exporter emits all four semantic fields for every preference record | |
| B2 | No semantic field (`preference_category`, `preference_key`, `preference_value`, `value_type`) is ever omitted from the export | |
| B3 | Metadata fields, if present in the export artifact, are in a clearly labeled sub-object (e.g., `"meta"`) and are not mixed into the semantic payload | |
| B4 | No sensitive value is exported in plaintext outside the encryption envelope (§VI.4) | |

**FAIL conditions (any one = PR blocked)**:
- Any of the four semantic fields absent from the exported record
- Sensitive value present in plaintext in the export artifact

---

## Section C — Import Behavior (§DW13.1 / §DW13.3)

| # | Check | Pass / Fail |
|---|-------|-------------|
| C1 | Importer reconstructs preferences using only `ROUND_TRIP_FIELDS` | |
| C2 | Metadata fields (`created_at`, `modified_at`, `record_id`, etc.) are treated as non-authoritative; database regenerates them | |
| C3 | Importer does not silently coerce `preference_value` or `value_type` (e.g., int → string) without an explicit, documented migration rule | |
| C4 | If a record is missing any semantic field: importer skips the record AND produces a user-visible skipped-item entry (§VI.1) — no silent drop | |
| C5 | Import does not restore or compare timestamps as part of the import operation | |

**FAIL conditions (any one = PR blocked)**:
- Importer silently coerces a value without an explicit migration rule
- Missing-field record silently dropped (no skipped-item entry)
- Timestamps restored from export artifact rather than regenerated

---

## Section D — Test Compliance (§DW13.3)

### D1 — Required Test Scenarios

| # | Test Scenario | Tests Present | CI Passes |
|---|---------------|---------------|-----------|
| D1a | Simple round-trip: `semantic_set(before) == semantic_set(after)` | | |
| D1b | Metadata explicitly not compared: test passes when timestamps differ | | |
| D1c | Ordering and formatting: shuffled order / reformatted JSON → still passes | | |
| D1d | Partial export/import: subset of categories → only exported prefs present, each with correct semantic fields | | |
| D1e | Missing semantic field in export record → importer skips record + skipped-item entry produced | | |
| D1f | Silent coercion detection: if value or value_type changes without migration rule → test fails | | |

**FAIL conditions (any one = PR blocked)**:
- D1a missing: no explicit round-trip fidelity test
- D1b missing: all tests may be implicitly comparing metadata
- D1e missing: no test for malformed record handling

### D2 — Anti-Pattern Detection

| # | Anti-pattern to reject | Action |
|---|-----------------------|--------|
| D2a | `assert record_before == record_after` (full dict equality) | Replace with `semantic_set()` comparison |
| D2b | `assert df_before.equals(df_after)` (DataFrame with metadata cols) | Replace; exclude METADATA_FIELDS cols |
| D2c | `assert json_before == json_after` (byte-for-byte) | Replace with semantic comparison |
| D2d | `assert len(before) == len(after)` only (count without values) | Add semantic field check |
| D2e | Round-trip test only checks "file exists" or "import did not raise" | Add semantic fidelity assertion |

---

## Section E — CI Enforcement Gates (§DW13.3)

| # | CI Check | Gate Failure Condition |
|---|----------|------------------------|
| E1 | At least one explicit round-trip test comparing `semantic_set()` before and after | Build fails if absent |
| E2 | No test asserts full-record equality including metadata fields | Build fails if found |
| E3 | `ROUND_TRIP_FIELDS` imported from canonical module in all relevant files | Build fails if redefined locally |
| E4 | Importer does not silently coerce value or value_type (static scan + test) | Build fails if detected |
| E5 | Missing-field record skip test (D1e) present and passing | Build fails if absent |

---

## Section F — Cross-References

| Reference | Location | Notes |
|-----------|----------|-------|
| §G.8 — Round-trip fidelity | constitution.md §G.8 | Canonical definition |
| §DW13.1 — Included fields | constitution.md §DW13.1 | category, key, value, value_type |
| §DW13.2 — Excluded fields | constitution.md §DW13.2 | timestamps, IDs, migration flags |
| §DW13.3 — Deterministic reviewability | constitution.md §DW13.3 | CI requirements |
| §DW13.4 — Ordering and formatting | constitution.md §DW13.4 | Order/format differences not fidelity failures |
| §VI.1 — Skipped-item summary | constitution.md §VI.1 | Required for skipped-field reporting |
| §VI.4 — Export Encryption | constitution.md §VI.4 | Export envelope encryption |
| §G.7 — Export encryption envelope | constitution.md §G.7 | Envelope format |
| docs/round-trip-fidelity-spec.md | docs/ | Full spec, constants, tests, migration patch, diagram |
| docs/export-encryption-spec.md | docs/ | Encryption spec (Q7) |
| checklist-export-encryption-compliance.md | .specify/memory/ | Encryption checklist (Q7) |
| TODO(PORTABILITY_FORMAT) | constitution.md | Schema publication still pending |

---

## Reviewer Sign-Off

| Reviewer | Role | Date | Signature |
|----------|------|------|-----------|
| | | | |
| | | | |

**PR MUST NOT merge if any FAIL condition in Sections A–E is unresolved.**
