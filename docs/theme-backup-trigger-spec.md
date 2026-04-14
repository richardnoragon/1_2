# Theme Backup Trigger — Canonical Specification

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §21 (Theme Security), §21.X
**Source clarification**: constitution_clairification_uiux_harmonny_r8.md — Q18
**Applied in constitution version**: v1.31.0

**See also**:
- `.specify/memory/constitution.md` §21, §21.X.1–§21.X.5
- `.specify/memory/checklist-theme-backup-compliance.md`
- `docs/anomaly-detection-sliding-window-spec.md` (parallel §16.Y spec)
- `docs/audit-origin-metadata-spec.md` (parallel §16.X spec)

---

## 1. Purpose

§21 requires: *"Theme backups MUST be created before applying any system-wide
theme change."*

The phrase *"system-wide theme change"* was previously undefined. Implementations
could erroneously restrict backups to token-value edits only, leaving preset
lifecycle operations (create, delete, switch, rename) without backup protection.
This document closes that ambiguity.

---

## 2. Formal Definition of "System-Wide Theme Change"

A **system-wide theme change** is any operation that alters the effective
system-wide theme state. The following five operations are each a system-wide
theme change and MUST each trigger a backup:

| # | Operation | Description | Backup required |
|---|---|---|---|
| 1 | **Modify tokens** | Edit any token value in an existing system-wide preset | MUST |
| 2 | **Create preset** | Add a new system-wide preset | MUST |
| 3 | **Delete preset** | Remove an existing system-wide preset | MUST |
| 4 | **Switch active preset** | Change which preset is globally applied | MUST |
| 5 | **Rename preset** | Change the name/label of a preset (values unchanged) | MUST |

Limiting the backup obligation to token-value edits only is **explicitly
forbidden**. All five operations change the system-wide theme state.

---

## 3. Backup Requirement

### 3.1 Ordering

The backup MUST be created **before** the theme operation is applied.
Backup-after-change ordering is a constitutional violation.

### 3.2 Abort on Failure

If backup creation fails for any reason, the theme operation MUST be **aborted**.
The change MUST NOT proceed when the backup cannot be successfully persisted.

### 3.3 Full-Snapshot Content

Each backup MUST capture the **complete** system-wide theme state at the moment
of capture, including:

- all system-wide presets and their complete token sets;
- the identity of the currently active preset;
- preset names/labels and unique identifiers.

Partial snapshots (e.g., only the preset being modified, only tokens without
names/identifiers, only the active preset) MUST NOT satisfy the backup
requirement.

### 3.4 Retention (from §21)

At least the **five most recent full-snapshot backups** MUST be retained.
"Five most recent" counts full snapshots; per-preset change records do not
count toward this total.

### 3.5 Storage (from §21)

Backups MUST be stored in a dedicated location separate from the live preference
store (a separate database table or equivalent file).

---

## 4. Alert Channels on Backup Failure

When backup creation fails and the theme operation is aborted, the system MUST:

1. Present a clear error message to the operator/admin explaining that the
   theme change was prevented because a backup could not be created.
2. Log the failure at `ERROR` level in the structured audit log with fields:
   `event_type: "THEME_BACKUP_FAILED"`, `operation`, `utc_timestamp`,
   `reason`.

No silent failures are permitted.

---

## 5. Reference Implementation

```python
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum, auto
from typing import Protocol


class ThemeOperation(Enum):
    MODIFY_TOKENS = auto()
    CREATE_PRESET = auto()
    DELETE_PRESET = auto()
    SWITCH_ACTIVE_PRESET = auto()
    RENAME_PRESET = auto()


class ThemeBackupStore(Protocol):
    def create_full_snapshot(self) -> bool:
        """
        Persist a full snapshot of all system-wide presets, the active preset
        identity, and all preset names/identifiers.

        Returns True if the backup was successfully persisted, False otherwise.
        """
        ...


class AuditLog(Protocol):
    def error(
        self,
        event_type: str,
        operation: str,
        utc_timestamp: datetime,
        reason: str,
    ) -> None: ...


class ThemeOperationGate:
    """
    Gate that enforces §21.X: backup MUST precede any system-wide theme change;
    if backup fails, the operation MUST be aborted.

    Usage pattern:
        gate = ThemeOperationGate(backup_store, audit_log)
        if gate.pre_operation_backup(ThemeOperation.CREATE_PRESET):
            apply_create_preset(...)
        # If pre_operation_backup returns False, do NOT apply the change.
    """

    def __init__(self, store: ThemeBackupStore, audit: AuditLog) -> None:
        self._store = store
        self._audit = audit

    def pre_operation_backup(self, operation: ThemeOperation) -> bool:
        """
        Create a full-snapshot backup before the given theme operation.

        Returns True if backup succeeded → caller MAY proceed with operation.
        Returns False if backup failed → caller MUST abort the operation.

        Requirements met:
        - §21.X.3: backup precedes the change.
        - §21.X.3: operation aborted on backup failure.
        - §21.X.4: full snapshot (delegated to ThemeBackupStore.create_full_snapshot).
        - §21.X.2: all five operations covered via ThemeOperation enum.
        """
        success = self._store.create_full_snapshot()
        if not success:
            self._audit.error(
                event_type="THEME_BACKUP_FAILED",
                operation=operation.name,
                utc_timestamp=datetime.now(tz=timezone.utc),
                reason="Backup creation returned False; theme operation aborted.",
            )
        return success
```

**Key properties satisfied**:

| Requirement | How satisfied |
|---|---|
| All five operations covered | `ThemeOperation` enum has all five values |
| Backup before change | `pre_operation_backup` called before state mutation; returns bool to caller |
| Abort on failure | Caller checks return value; False → do not apply change |
| Full snapshot | Delegated to `ThemeBackupStore.create_full_snapshot` contract |
| Audit on failure | `AuditLog.error` called immediately on failure |

---

## 6. CI Tests

### T1 — Modify Tokens Triggers Backup

```python
def test_t1_modify_tokens_triggers_backup():
    store = RecordingBackupStore()
    gate = ThemeOperationGate(store, NullAudit())
    result = gate.pre_operation_backup(ThemeOperation.MODIFY_TOKENS)
    assert result is True
    assert store.snapshot_count == 1
```

### T2 — Create Preset Triggers Backup

```python
def test_t2_create_preset_triggers_backup():
    store = RecordingBackupStore()
    gate = ThemeOperationGate(store, NullAudit())
    result = gate.pre_operation_backup(ThemeOperation.CREATE_PRESET)
    assert result is True
    assert store.snapshot_count == 1
```

### T3 — Delete Preset Triggers Backup

```python
def test_t3_delete_preset_triggers_backup():
    store = RecordingBackupStore()
    gate = ThemeOperationGate(store, NullAudit())
    result = gate.pre_operation_backup(ThemeOperation.DELETE_PRESET)
    assert result is True
    assert store.snapshot_count == 1
```

### T4 — Switch Active Preset Triggers Backup

```python
def test_t4_switch_active_preset_triggers_backup():
    store = RecordingBackupStore()
    gate = ThemeOperationGate(store, NullAudit())
    result = gate.pre_operation_backup(ThemeOperation.SWITCH_ACTIVE_PRESET)
    assert result is True
    assert store.snapshot_count == 1
```

### T5 — Rename Preset Triggers Backup

```python
def test_t5_rename_preset_triggers_backup():
    store = RecordingBackupStore()
    gate = ThemeOperationGate(store, NullAudit())
    result = gate.pre_operation_backup(ThemeOperation.RENAME_PRESET)
    assert result is True
    assert store.snapshot_count == 1
```

### T6 — Backup Failure Aborts Operation

```python
def test_t6_backup_failure_aborts_operation():
    store = FailingBackupStore()   # always returns False
    audit = RecordingAudit()
    gate = ThemeOperationGate(store, audit)
    result = gate.pre_operation_backup(ThemeOperation.MODIFY_TOKENS)
    assert result is False
    # Caller must not apply change when result is False
    assert audit.error_events[0]["event_type"] == "THEME_BACKUP_FAILED"
```

### T7 — Restore Returns to Prior State

```python
def test_t7_restore_returns_to_prior_state():
    store = InMemoryBackupStore()
    initial_state = store.capture_current_state()
    # Apply a change (with backup)
    gate = ThemeOperationGate(store, NullAudit())
    gate.pre_operation_backup(ThemeOperation.MODIFY_TOKENS)
    apply_token_edit(store, preset="default", token="--color-primary", value="#ff0000")
    # Restore from the backup
    store.restore_most_recent_backup()
    assert store.capture_current_state() == initial_state
```

---

## 7. Cross-References

| Document | Relevant section |
|---|---|
| `.specify/memory/constitution.md` | §21 (theme-backup bullet), §21.X.1–§21.X.5 |
| `.specify/memory/checklist-theme-backup-compliance.md` | Reviewer checklist Sections A–E |
| `docs/anomaly-detection-sliding-window-spec.md` | §16.Y — sliding window (parallel spec pattern) |
| `docs/audit-origin-metadata-spec.md` | §16.X — origin metadata (parallel spec pattern) |
| `docs/pii-scan-ux-spec.md` | §VIII.X — PII scan delivery (parallel spec pattern) |
| `docs/file-validation-exemption-spec.md` | §IX.X — validation exemption (parallel spec pattern) |
