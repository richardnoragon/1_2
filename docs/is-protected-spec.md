# is_protected Flag — Canonical Specification

**Constitutional authority**: §G.12, §DW §17.X.1–§DW17.X.6  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.25.0)  
**Last updated**: 2026-04-04  

---

## 1. Purpose

The `is_protected` flag designates accounts that MUST remain:
- **Permanently available** — cannot be disabled, deactivated, or suspended
- **Permanently privileged** — role immutable after creation
- **Administratively immutable** — immune to modification by other admins or automated systems

These are the "always-available" accounts (`admin` and `dev`) provisioned during database initialisation. They exist to guarantee that at least one administrative and one developer account remains accessible regardless of system state.

---

## 2. The Six Protected Operations

The `is_protected` flag constitutionally blocks the following six operations when attempted by any actor **other than** the account owner performing self-service actions:

| # | Operation | Blocked? | Notes |
|---|-----------|----------|-------|
| 1 | Account deletion | ✅ BLOCKED | At all layers (UI, API, service, DB) |
| 2 | Account deactivation | ✅ BLOCKED | At all layers |
| 3 | Account suspension | ✅ BLOCKED | At all layers |
| 4 | Password reset by another admin or automated system | ✅ BLOCKED | API/service layer; DB admin channel bypasses with audit trail |
| 5 | Role change (escalation or demotion) | ✅ BLOCKED | Role is immutable after creation |
| 6 | Username change | ✅ BLOCKED | Username is immutable at all layers |

### 2.1 Self-Service Exception

**Self-service password changes by the account owner are permitted.** A user logged in as `admin` or `dev` MAY change their own password through the standard self-service flow. Any *other* actor initiating a password reset against a protected account MUST receive a `protected_account_error`.

---

## 3. Error Contract

All six blocked operations MUST result in an explicit error response. Silent failures (no error, no log) are **PROHIBITED**.

### 3.1 Error Code

```
protected_account_error
```

### 3.2 Response Shape (JSON)

```json
{
  "error": "protected_account_error",
  "message": "Operation blocked: target account is protected.",
  "operation": "<attempted_operation>",
  "target_account_id": "<uuid>",
  "actor_account_id": "<uuid>"
}
```

### 3.3 HTTP Status

Use `403 Forbidden` for all blocked `is_protected` operations (the operation is understood but constitutionally forbidden).

---

## 4. Audit Logging for Blocked Operations

Every blocked operation MUST emit a structured audit-log entry with **all five** of the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `actor` | string (UUID or system ID) | Who attempted the operation |
| `target` | string (UUID) | The protected account targeted |
| `operation` | string (enum) | One of: `delete`, `deactivate`, `suspend`, `password_reset`, `role_change`, `username_change` |
| `reason` | string (literal) | Always `"protected_account_violation"` |
| `timestamp` | ISO 8601 datetime | UTC, millisecond precision |

**Example audit entry:**

```json
{
  "actor": "admin-operator-007",
  "target": "00000000-0000-0000-0000-000000000001",
  "operation": "role_change",
  "reason": "protected_account_violation",
  "timestamp": "2026-04-04T14:32:00.000Z"
}
```

---

## 5. Enforcement Layers

### 5.1 Required: Service / API Layer Guard

The primary enforcement point is the service layer (business logic), checked before any database write is attempted. Every service function that performs any of the six protected operations MUST call the guard function (see Section 6) as the first action.

### 5.2 Recommended: Database Constraints

Database-level constraints are strongly recommended as defence-in-depth:
- `is_protected = true` rows SHOULD be protected by a trigger or constraint that rejects DELETEs
- Username column SHOULD have an immutable-after-insert constraint or trigger for protected accounts
- These constraints supplement — and do not replace — the service layer guard

### 5.3 MUST NOT: Silent Bypass

No internal API, migration script, or batch job MAY bypass the `is_protected` guard unless it also:
1. Creates a structured audit-log entry
2. Requires explicit operator authorisation
3. Is documented in the break-glass procedure (§DW §18)

---

## 6. Python Reference Implementation

### 6.1 Guard Function

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ProtectedOperation(str, Enum):
    DELETE = "delete"
    DEACTIVATE = "deactivate"
    SUSPEND = "suspend"
    PASSWORD_RESET = "password_reset"
    ROLE_CHANGE = "role_change"
    USERNAME_CHANGE = "username_change"


class ProtectedAccountError(Exception):
    """Raised when a blocked operation is attempted on a protected account."""

    def __init__(self, operation: ProtectedOperation, target_id: str, actor_id: str):
        self.operation = operation
        self.target_id = target_id
        self.actor_id = actor_id
        super().__init__(
            f"Operation blocked: '{operation.value}' is forbidden on "
            f"protected account '{target_id}' (actor: '{actor_id}')."
        )


def check_protected(
    account: dict,
    operation: ProtectedOperation,
    actor_id: str,
    audit_logger,
    self_service: bool = False,
) -> None:
    """
    Guard function for is_protected accounts.

    Raises ProtectedAccountError and emits an audit-log entry if the
    operation is blocked. Allows self-service password changes by owner.

    Args:
        account:       The target account dict; must contain 'is_protected',
                       'id', and optionally 'owner_id'.
        operation:     The attempted ProtectedOperation.
        actor_id:      ID of the actor attempting the operation.
        audit_logger:  Callable accepting (actor, target, operation, reason, timestamp).
        self_service:  True when the actor IS the account owner performing a
                       self-initiated password change.
    """
    if not account.get("is_protected"):
        return  # Not a protected account; guard passes.

    # Self-service password change exception
    if operation == ProtectedOperation.PASSWORD_RESET and self_service:
        return  # Owner changing their own password is permitted.

    target_id = account["id"]

    # Emit audit log entry BEFORE raising (so it is always recorded)
    audit_logger(
        actor=actor_id,
        target=target_id,
        operation=operation.value,
        reason="protected_account_violation",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    raise ProtectedAccountError(
        operation=operation,
        target_id=target_id,
        actor_id=actor_id,
    )
```

### 6.2 Service Layer Usage Example

```python
def change_user_role(account: dict, new_role: str, actor_id: str) -> None:
    check_protected(
        account=account,
        operation=ProtectedOperation.ROLE_CHANGE,
        actor_id=actor_id,
        audit_logger=audit_log.record,
    )
    # ... proceed with role change
```

### 6.3 Self-Service Password Change Usage

```python
def self_service_password_change(account: dict, new_password: str) -> None:
    actor_id = account["id"]
    check_protected(
        account=account,
        operation=ProtectedOperation.PASSWORD_RESET,
        actor_id=actor_id,
        audit_logger=audit_log.record,
        self_service=True,  # Owner changing own password — allowed
    )
    # ... proceed with password change
```

---

## 7. CI Tests (T1–T9)

| ID | Description | Expected result |
|----|-------------|----------------|
| T1 | Admin attempts password reset on protected account (non-self-service) | `ProtectedAccountError` raised; audit log entry emitted |
| T2 | Account owner changes own password (self-service) | Succeeds; no audit log entry for blocked operation |
| T3 | Admin attempts role change (demotion) on protected account | `ProtectedAccountError` raised; audit log entry emitted |
| T4 | Admin attempts role change (escalation) on protected account | `ProtectedAccountError` raised; audit log entry emitted |
| T5 | Admin attempts username change on protected account | `ProtectedAccountError` raised; audit log entry emitted |
| T6 | Admin attempts deletion of protected account | `ProtectedAccountError` raised; audit log entry emitted |
| T7 | Admin attempts deactivation of protected account | `ProtectedAccountError` raised; audit log entry emitted |
| T8 | Admin attempts suspension of protected account | `ProtectedAccountError` raised; audit log entry emitted |
| T9 | Audit log entries contain all five required fields for each T1/T3–T8 | All five fields (actor, target, operation, reason, timestamp) present |

---

## 8. Migration Plan

| Step | Action |
|------|--------|
| 1 | Add `is_protected BOOLEAN NOT NULL DEFAULT FALSE` column to the users table (if not present) |
| 2 | Set `is_protected = TRUE` for the `admin` and `dev` always-available accounts via a data migration |
| 3 | Add DB trigger or constraint to reject DELETE on `is_protected = TRUE` rows |
| 4 | Add application-layer `check_protected()` guard to all six service functions |
| 5 | Deploy; run CI tests T1–T9 as a post-deployment gate |
| 6 | Update break-glass documentation to note that `is_protected` bypass requires audit trail and documented operator authorisation |

---

## 9. Cross-References

| Document | Location |
|----------|---------|
| Constitutional glossary entry | §G.12 — is_protected scope |
| Constitutional subsections | §DW §17.X.1–§DW17.X.6 |
| §VII Always-Available Accounts | §VII Identity & Access Control |
| §VII Account Suspension | §VII Identity & Access Control |
| Reviewer checklist | .specify/memory/checklist-is-protected-compliance.md |
| TOTP spec | docs/totp-spec.md |
| FIDO2 spec | docs/fido2-spec.md |
| Idle timeout spec | docs/idle-timeout-spec.md |
