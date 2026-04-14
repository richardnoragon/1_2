# Direct Database Modification Audit — Canonical Specification

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §17 (Lockout Prevention / Always-Available Accounts), §17.Z
**Source clarification**: constitution_clairification_uiux_harmonny_r8.md — Q19
**Applied in constitution version**: v1.32.0
**Resolves**: TODO(DIRECT_DB_AUDIT) — open since v1.10.0

**See also**:
- `.specify/memory/constitution.md` §17, §17.Z.1–§17.Z.7
- `.specify/memory/checklist-direct-db-audit-compliance.md`
- `docs/audit-origin-metadata-spec.md` (§16.X — unified audit log schema)
- `docs/is-protected-spec.md` (§DW17.X — protected-account guard)

---

## 1. Purpose

§17 permits removal of always-available accounts only by "direct database
modification with audit trail." The phrase "with audit trail" was constitutionally
required but mechanically undefined since v1.10.0 (TODO(DIRECT_DB_AUDIT)).

This document defines the required mechanism, prohibited alternatives, failure
handling, and CI obligations that close that gap.

---

## 2. Required Mechanism: Mandatory CLI Wrapper

### 2.1 Why CLI Wrapper (Not Trigger, Not Manual)

| Mechanism | Sufficient? | Reason |
|---|---|---|
| DB trigger | No — supplemental only | Cannot capture operator intent, ticket ID, or justification. Cannot enforce pre-modification authorization. Cannot block the change on audit failure. |
| Manual procedure | **Forbidden** | Not enforceable, not testable, not reviewer-proof. Violates deterministic auditability. |
| **Mandatory CLI wrapper** | **Yes — MUST** | Captures operator identity + justification. Writes audit before modification. Blocks modification on audit failure. Enforceable and CI-verifiable. |

### 2.2 CLI Wrapper Obligations

The mandatory CLI tool MUST:

1. **Authenticate the operator** before taking any action (OS user, SSO,
   signed token, or equivalent).
2. **Capture and record** all of the following:
   - operator identity (human-attributable; not a generic service account)
   - UTC timestamp
   - target account(s) (username(s) affected)
   - operation type (e.g., `remove_protected_account`)
   - justification / ticket ID (required; no empty string permitted)
3. **Write the audit entry to the unified audit log before executing** the
   database modification.
4. **Execute the modification only after** the audit entry has been
   successfully persisted.
5. **Fail closed**: if the audit entry cannot be written, abort the operation,
   exit with non-zero status, and print a clear stderr message. The database
   MUST NOT be modified.
6. **Provide no bypass flag** (`--force-no-audit`, `--skip-audit`, or
   equivalent). Any such flag is a constitutional violation.

### 2.3 Permitted Single Entry Point

Only the mandatory CLI wrapper may write to protected-account records. No other
path — raw SQL, ORM call, migration script, or DB administration GUI — is
permitted as the primary modification mechanism.

---

## 3. Prohibited Mechanisms

The following MUST NOT be used to satisfy the §17 audit-trail requirement:

- manually written procedure documents (written before or after the fact)
- after-the-fact log entries created by the operator
- database administration GUIs without integrated pre-modification audit logging
- any mechanism that writes the audit entry after the DB modification
- DB triggers used as the sole audit mechanism

---

## 4. Optional DB Triggers (Supplemental Only)

Database-level triggers MAY be implemented as defence-in-depth. They MUST NOT
replace the CLI wrapper as the primary mechanism. Triggers are useful for
catching unanticipated direct-SQL access paths, but their audit entries MUST
be treated as secondary evidence only.

---

## 5. Unified Audit Log

Audit entries written by the CLI wrapper MUST:

- be written to the **same structured audit log** as all other application
  events (same table or stream);
- conform to the same field schema defined in §16 / `docs/audit-origin-metadata-spec.md`;
- be retained under the same retention policy as all other audit events.

A separate log file, spreadsheet, or notes register MUST NOT substitute for
the unified audit log.

---

## 6. Required Audit Entry Fields

Every CLI-wrapper audit entry MUST include at minimum:

| Field | Type | Description |
|---|---|---|
| `event_type` | string | `"direct_db_protected_account_modification"` |
| `utc_timestamp` | ISO 8601 | UTC time at audit-entry creation (second precision or finer) |
| `operator` | string | Human-attributable operator identity |
| `target_username` | string | Username of the protected account being modified |
| `action` | string | Operation type (e.g., `"remove_protected_account"`) |
| `reason` | string | Human-readable justification (MUST NOT be empty) |
| `ticket_id` | string | Issue/ticket reference (MUST NOT be empty) |

---

## 7. Reference Implementation

```python
import sys
from datetime import datetime, timezone

from db import get_connection
from audit import write_audit_event
from auth import get_operator_identity


CLI_NAME = "rfu-db-tool"


def remove_protected_account(
    username: str,
    reason: str,
    ticket_id: str,
) -> None:
    """
    Remove a protected account from the database.

    Constitutional requirements met (§17.Z):
    - Operator identity authenticated and captured (§17.Z.2).
    - Audit entry written BEFORE the DB modification (§17.Z.2).
    - Modification blocked and CLI aborts if audit fails (§17.Z.6).
    - Audit entry written to unified audit log (§17.Z.5).
    - No bypass flag exists (§17.Z.6).
    """
    if not reason.strip():
        print(f"{CLI_NAME}: error: --reason is required and must not be empty", file=sys.stderr)
        sys.exit(1)
    if not ticket_id.strip():
        print(f"{CLI_NAME}: error: --ticket-id is required and must not be empty", file=sys.stderr)
        sys.exit(1)

    # §17.Z.2 — Authenticate operator
    operator = get_operator_identity()

    # §17.Z.2 — Build structured audit entry
    audit_event = {
        "event_type": "direct_db_protected_account_modification",
        "utc_timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "operator": operator,
        "target_username": username,
        "action": "remove_protected_account",
        "reason": reason,
        "ticket_id": ticket_id,
    }

    # §17.Z.2 / §17.Z.6 — Write audit entry FIRST; fail closed on failure
    if not write_audit_event(audit_event):
        print(
            f"{CLI_NAME}: FATAL: audit entry could not be written; "
            "database modification aborted (§17.Z.6 fail-closed).",
            file=sys.stderr,
        )
        sys.exit(1)

    # §17.Z.2 — Only now execute the DB modification
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM user_accounts WHERE username = %s AND is_protected = TRUE",
                (username,),
            )


def main(argv: list[str]) -> None:
    if len(argv) < 1:
        print(f"Usage: {CLI_NAME} remove-protected <username> --ticket-id <id> --reason <text>")
        sys.exit(1)

    cmd, *args = argv
    if cmd == "remove-protected":
        # Minimal arg parsing; production tool should use argparse
        username = args[0] if args else ""
        ticket_id = _extract_flag(args, "--ticket-id")
        reason = _extract_flag(args, "--reason")
        remove_protected_account(username, reason, ticket_id)
    else:
        print(f"{CLI_NAME}: unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


def _extract_flag(args: list[str], flag: str) -> str:
    try:
        idx = args.index(flag)
        return args[idx + 1]
    except (ValueError, IndexError):
        return ""


if __name__ == "__main__":
    main(sys.argv[1:])
```

**Key properties satisfied**:

| Requirement | How satisfied |
|---|---|
| Authenticate operator | `get_operator_identity()` called before any action |
| Audit before modification | `write_audit_event()` called before `cur.execute()` |
| Fail closed | `sys.exit(1)` if audit write fails; DB call never reached |
| No bypass flag | No `--force-no-audit` parameter |
| Unified audit log | `write_audit_event()` uses shared audit infrastructure |
| Required fields | All seven required fields populated in `audit_event` dict |
| Non-empty reason/ticket | Validated at entry with explicit error messages |

---

## 8. CI Tests

### T1 — Happy Path: Audit Written and Modification Applied

```python
def test_t1_happy_path():
    db = InMemoryDB()
    audit = RecordingAuditLog()
    db.insert_protected_account("always_admin")

    run_cli(
        ["remove-protected", "always_admin",
         "--ticket-id", "OPS-123",
         "--reason", "Decommission per OPS-123"],
        db=db, audit=audit,
    )

    # Audit entry written
    assert len(audit.events) == 1
    entry = audit.events[0]
    assert entry["event_type"] == "direct_db_protected_account_modification"
    assert entry["target_username"] == "always_admin"
    assert entry["ticket_id"] == "OPS-123"
    assert entry["operator"]  # non-empty

    # DB modification applied
    assert not db.account_exists("always_admin")
```

### T2 — Audit Failure Blocks Modification

```python
def test_t2_audit_failure_blocks_modification():
    db = InMemoryDB()
    audit = FailingAuditLog()   # always returns False
    db.insert_protected_account("always_admin")

    with pytest.raises(SystemExit) as exc_info:
        run_cli(
            ["remove-protected", "always_admin",
             "--ticket-id", "OPS-456",
             "--reason", "Test"],
            db=db, audit=audit,
        )

    assert exc_info.value.code != 0  # non-zero exit
    assert db.account_exists("always_admin")  # DB untouched
```

### T3 — Audit Entry Schema Conforms to Unified Log Schema

```python
def test_t3_schema_conformance():
    db = InMemoryDB()
    audit = RecordingAuditLog()
    db.insert_protected_account("always_dev")

    run_cli(
        ["remove-protected", "always_dev",
         "--ticket-id", "OPS-789",
         "--reason", "Schema conformance test"],
        db=db, audit=audit,
    )

    entry = audit.events[0]
    required_fields = {
        "event_type", "utc_timestamp", "operator",
        "target_username", "action", "reason", "ticket_id",
    }
    assert required_fields.issubset(entry.keys())
    # entry conforms to the same schema as all application audit events
    assert audit.schema_matches_application_events(entry)
```

---

## 9. Cross-References

| Document | Relevant section |
|---|---|
| `.specify/memory/constitution.md` | §17 (audit-trail bullet), §17.Z.1–§17.Z.7 |
| `.specify/memory/checklist-direct-db-audit-compliance.md` | Reviewer checklist Sections A–F |
| `docs/audit-origin-metadata-spec.md` | §16.X — unified audit log schema (field definitions) |
| `docs/is-protected-spec.md` | §DW17.X — protected-account guard (six blocked operations) |
| `docs/anomaly-detection-sliding-window-spec.md` | §16.Y — parallel spec pattern |
| `docs/theme-backup-trigger-spec.md` | §21.X — parallel spec pattern |
