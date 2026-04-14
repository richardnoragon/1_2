# Reviewer Checklist — Direct Database Modification Audit Compliance

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §17 (Lockout Prevention / Always-Available Accounts), §17.Z
**Resolves**: TODO(DIRECT_DB_AUDIT) — open since v1.10.0
**Applied in constitution version**: v1.32.0

**See also**:
- `.specify/memory/constitution.md` §17, §17.Z.1–§17.Z.7
- `docs/direct-db-audit-spec.md` (canonical spec, reference implementation,
  CI tests T1–T3)
- `docs/audit-origin-metadata-spec.md` (§16.X — unified audit log schema)
- `docs/is-protected-spec.md` (§DW17.X — protected-account guard)

---

## How to Use This Checklist

Mark each item ✓ (pass), ✗ (fail), or N/A. Any ✗ is a constitutional violation
that MUST be resolved before merge. Every section must be fully signed-off by a
reviewer and the CI pipeline.

---

## Section A — Single Mandatory Path

### A.1 — CLI Wrapper Is the Only Entry Point

- [ ] **A.1.1** A single, documented mandatory CLI tool exists for performing
  direct DB modifications to protected accounts.
- [ ] **A.1.2** Code review confirms no raw SQL, ORM call, migration script,
  or DB administration GUI can modify protected-account records outside the
  CLI wrapper.
- [ ] **A.1.3** CI static analysis scans confirm no code path writes to
  protected-account tables/columns outside the designated CLI implementation.
- [ ] **A.1.4** The CLI tool is documented in the project's operations guide
  as the only sanctioned mechanism for direct protected-account modifications.

### A.2 — No Bypass Flag

- [ ] **A.2.1** No `--force-no-audit`, `--skip-audit`, or semantically
  equivalent flag exists in the CLI tool.
- [ ] **A.2.2** Grep confirms no conditional logic that skips the audit call
  under any flag or environment variable.

*FAIL if*: Any undocumented or documented path can modify protected accounts
without going through the mandatory CLI wrapper.

---

## Section B — Audit Entry Written Before Modification

### B.1 — Pre-Modification Ordering

- [ ] **B.1.1** In all code paths of the CLI tool, the call to `write_audit_event`
  (or equivalent) precedes the database modification call.
- [ ] **B.1.2** No early-return, exception-catch, or try/finally block allows
  the DB modification to execute before the audit entry is confirmed written.
- [ ] **B.1.3** A transaction structure (if applicable) places the audit write
  before the DB mutation in the same transactional boundary, or the audit write
  provides a stricter pre-write guarantee.

*FAIL if*: Any execution path reaches the DB modification before the audit
entry is successfully persisted.

---

## Section C — Fail-Closed on Audit Failure

- [ ] **C.1** When `write_audit_event` (or equivalent) returns failure (any
  exception, `False`, non-zero code), the CLI tool:
  - [ ] **C.1.1** does NOT execute the database modification;
  - [ ] **C.1.2** exits with a non-zero status code;
  - [ ] **C.1.3** prints a clear diagnostic message to stderr identifying the
    audit failure as the reason the modification was prevented.
- [ ] **C.2** No "best-effort" or "log later" path exists where the DB change
  proceeds on audit failure.
- [ ] **C.3** No environment variable or runtime flag can override the
  fail-closed behaviour.

*FAIL if*: The CLI proceeds with the DB modification when audit logging fails,
or exits with code 0 while skipping the audit.

---

## Section D — Unified Audit Log and Schema Conformance

### D.1 — Same Log as Application Events

- [ ] **D.1.1** CLI-wrapper audit entries are written to the same audit log
  table/stream as all other application audit events (per §16).
- [ ] **D.1.2** No separate log file, spreadsheet, or notes register is used
  in place of the unified audit log.

### D.2 — Required Fields Present

Each audit entry written by the CLI wrapper MUST include all of the following:

- [ ] **D.2.1** `event_type` = `"direct_db_protected_account_modification"`
- [ ] **D.2.2** `utc_timestamp` — ISO 8601 with second or finer precision
- [ ] **D.2.3** `operator` — human-attributable identity (not a generic
  service account)
- [ ] **D.2.4** `target_username` — the protected account being modified
- [ ] **D.2.5** `action` — operation type string (e.g., `"remove_protected_account"`)
- [ ] **D.2.6** `reason` — non-empty human-readable justification
- [ ] **D.2.7** `ticket_id` — non-empty issue/ticket reference

*FAIL if*: Any required field is absent, empty, or uses a generic placeholder.

---

## Section E — Operator Authentication and Attribution

- [ ] **E.1** The CLI tool requires operator authentication before accepting
  any input (e.g., OS user check, SSO token validation, signed credential).
- [ ] **E.2** The `operator` field in the audit entry is tied to a real,
  identifiable human — not a generic service account such as `db_admin`.
- [ ] **E.3** An audit entry with `operator = ""` or `operator = "unknown"`
  is rejected by the audit-log schema validator.

---

## Section F — Automated Test Coverage

### F.1 — Required CI Tests

Each test must exist and pass in the CI pipeline:

| Test | Behaviour | Pass condition |
|---|---|---|
| **T1** | Happy path | Audit entry written; DB modified; all required fields present |
| **T2** | Audit failure | DB NOT modified; CLI exits non-zero |
| **T3** | Schema conformance | Audit entry fields match unified app-event schema |

- [ ] **F.1.1** T1 passes.
- [ ] **F.1.2** T2 passes.
- [ ] **F.1.3** T3 passes.

### F.2 — Forbidden Test Anti-Patterns

- [ ] **F.2.1** T2 uses a genuine mock/stub that forces audit-write failure;
  it does NOT merely skip calling the audit function.
- [ ] **F.2.2** T1 asserts the DB is modified AND the audit entry is present —
  not just "no exception thrown."
- [ ] **F.2.3** T3 asserts against the actual unified log schema definition —
  not just the presence of some fields.

### F.3 — CI Static Analysis

- [ ] **F.3.1** CI scan confirms no code path (other than the CLI wrapper)
  writes to protected-account tables.
- [ ] **F.3.2** CI scan confirms no `--force-no-audit` or equivalent flag is
  defined in the CLI argument parser.

---

## Sign-Off

| Role | Reviewer | Date | Pass/Fail |
|---|---|---|---|
| Developer | | | |
| Security reviewer | | | |
| CI pipeline | | | |
