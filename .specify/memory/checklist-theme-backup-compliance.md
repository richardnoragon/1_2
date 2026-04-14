# Reviewer Checklist — Theme Backup Trigger Compliance

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §21 (Theme Security), §21.X
**Applied in constitution version**: v1.31.0

**See also**:
- `.specify/memory/constitution.md` §21, §21.X.1–§21.X.5
- `docs/theme-backup-trigger-spec.md` (canonical spec, reference
  implementation, CI tests T1–T7)

---

## How to Use This Checklist

Mark each item ✓ (pass), ✗ (fail), or N/A. Any ✗ is a constitutional violation
that MUST be resolved before merge. Every section must be fully signed-off by a
reviewer and the CI pipeline.

---

## Section A — Backup Trigger Coverage (All Five Operations)

Each of the following operations MUST trigger a full-snapshot backup before
the state change is applied. Verify each one independently.

### A.1 — Modify Token Values

- [ ] **A.1.1** Editing any token value in an existing system-wide preset
  invokes the backup routine before the token update is persisted.
- [ ] **A.1.2** The backup call happens even when a single token is changed
  in a large preset (no "minor edit" exemption).

### A.2 — Create Preset

- [ ] **A.2.1** Adding a new system-wide preset invokes the backup routine
  before the new preset record is created.
- [ ] **A.2.2** Backup is taken even when no existing preset is being modified
  (the "no existing preset changed" argument does not exempt creation).

### A.3 — Delete Preset

- [ ] **A.3.1** Removing an existing system-wide preset invokes the backup
  routine before the record is deleted.
- [ ] **A.3.2** The backup captures the to-be-deleted preset's data (it is
  included in the full snapshot taken immediately before deletion).

### A.4 — Switch Active Preset

- [ ] **A.4.1** Changing which preset is globally active invokes the backup
  routine before the active-preset pointer is updated.
- [ ] **A.4.2** Backup is required even when no preset token values change
  (switching is unconditionally a state change).

### A.5 — Rename Preset

- [ ] **A.5.1** Changing the name/label of a system-wide preset invokes the
  backup routine before the rename is applied.
- [ ] **A.5.2** Backup is required even when no token values change (name is
  part of preset identity and auditability).

*FAIL if*: Any of the five operations can complete without a prior backup being
successfully created.

---

## Section B — Backup Timing and Abort Semantics

### B.1 — Backup Precedes Change

- [ ] **B.1.1** Code review confirms the backup call is made before the
  theme state mutation in all five operation paths.
- [ ] **B.1.2** No operation path exists where the state change is applied
  first and the backup is taken afterward.
- [ ] **B.1.3** Database transaction ordering (if applicable) places the
  backup write before the theme-state write within the same transactional
  boundary or with a stricter pre-write guarantee.

### B.2 — Abort on Backup Failure

- [ ] **B.2.1** When the backup routine returns a failure (exception, False,
  error code), the theme operation is aborted — the state change is NOT applied.
- [ ] **B.2.2** A clear error message is presented to the operator/admin
  explaining why the theme change was prevented.
- [ ] **B.2.3** The failure is logged at `ERROR` level in the structured
  audit log with `event_type: "THEME_BACKUP_FAILED"`, `operation`, and
  `reason` fields.
- [ ] **B.2.4** No "best-effort backup" path exists where the change proceeds
  silently on backup failure.

*FAIL if*: Any operation proceeds despite a backup failure, or failure is
swallowed silently.

---

## Section C — Backup Content (Full Snapshot)

- [ ] **C.1** The backup includes all system-wide presets (not just the one
  being modified).
- [ ] **C.2** Each backed-up preset includes its complete token set.
- [ ] **C.3** The backup records the identity (name/label and unique ID) of
  every preset.
- [ ] **C.4** The backup captures which preset is currently active.
- [ ] **C.5** A partial snapshot (e.g., only the modified preset, only tokens
  without names, only the active preset) is rejected as non-compliant.

*FAIL if*: Backup is scoped to only the preset(s) directly involved in the
operation rather than the full system-wide state.

---

## Section D — Retention and Restore

### D.1 — Retention

- [ ] **D.1.1** At least the five most recent full-snapshot backups are
  retained (per §21).
- [ ] **D.1.2** "Five most recent" is counted in full snapshots; per-preset
  records do not count toward the five-backup minimum.
- [ ] **D.1.3** Storage is in a dedicated location separate from the live
  preference store (separate DB table or equivalent file — per §21).

### D.2 — Restore Capability

- [ ] **D.2.1** A built-in restore action exists within the theme UI (per §21).
- [ ] **D.2.2** Restore returns the system-wide theme to the full state
  captured in the target backup snapshot (all presets, active preset, names).
- [ ] **D.2.3** Restore correctness is covered by an automated test
  (CI test T7 or equivalent).

---

## Section E — Automated Test Coverage

### E.1 — Required CI Tests

Each test must exist and pass in the CI pipeline:

| Test | Behaviour | Pass condition |
|---|---|---|
| **T1** | Modify tokens | Backup called once before token update |
| **T2** | Create preset | Backup called once before preset creation |
| **T3** | Delete preset | Backup called once before preset deletion |
| **T4** | Switch active preset | Backup called once before active pointer update |
| **T5** | Rename preset | Backup called once before rename applied |
| **T6** | Backup failure | Theme operation aborted; audit log records `THEME_BACKUP_FAILED` |
| **T7** | Restore | After change + restore, state matches pre-change snapshot |

- [ ] **E.1.1** T1 passes.
- [ ] **E.1.2** T2 passes.
- [ ] **E.1.3** T3 passes.
- [ ] **E.1.4** T4 passes.
- [ ] **E.1.5** T5 passes.
- [ ] **E.1.6** T6 passes.
- [ ] **E.1.7** T7 passes.

### E.2 — Forbidden Test Anti-Patterns

- [ ] **E.2.1** Tests do NOT only cover token-edit scenarios — all five
  operation types are represented individually.
- [ ] **E.2.2** T6 uses a mock/stub that forces backup failure; it does not
  merely skip the backup call.
- [ ] **E.2.3** T7 asserts full state equality (tokens + preset names + active
  preset), not just "no exception thrown."

---

## Sign-Off

| Role | Reviewer | Date | Pass/Fail |
|---|---|---|---|
| Developer | | | |
| Security reviewer | | | |
| CI pipeline | | | |
