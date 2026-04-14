# Idle Timeout Specification — Role-Differentiated Session Controls
<!-- Version: 1.0 | Constitution: v1.24.0 | Q11 Applied -->

## 1. Purpose

This document is the canonical specification for idle-session timeout behaviour
in RFU. It prescribes the per-role default idle timeout values, the 60-minute
ceiling, administrative override rules, watchdog requirements, and CI
enforcement criteria.

**Constitutional authority**: §VII.Z (§VII.Z.1–§VII.Z.5) and §G.11.

---

## 2. Role-Differentiated Default Idle Timeouts (§G.11)

The following values are the **constitutional defaults** — the idle timeout
applied when neither the administrator nor the user has configured anything.
These MUST be implemented as distinct per-role constants, never as a single
shared constant.

| Role | Default idle timeout | Rationale |
|------|---------------------|-----------|
| `admin` | 10 minutes | Highest privilege; greatest attack surface if left unattended |
| `dev` | 15 minutes | Elevated privilege; can modify system behaviour |
| `user` | 30 minutes | Standard privilege; balanced security and usability |
| `readonly` | 45 minutes | Read-only access; lowest risk profile |

---

## 3. Timeout Ceiling and Administrative Overrides (§VII.Z.3, §VII.Z.4)

### 3.1 60-Minute Ceiling

No role's idle timeout MAY be configured longer than **60 minutes** unless an
administrator explicitly overrides it. An explicit override requires:

1. A deliberate administrator action (not a silent config default).
2. An audit-log entry recording: actor, role affected, previous value, new
   value, timestamp.

### 3.2 Absolute System Ceiling

The 8-hour absolute system ceiling (§VII Session Controls) applies
independently and is not affected by §VII.Z.3.

### 3.3 Administrative Override Rules

| Constraint | Rule |
|------------|------|
| Overrides MUST be deliberate | No implicit config changes |
| Overrides MUST be logged | All four fields (actor, role, old, new) required |
| Floor enforcement | If an admin sets a minimum floor, users MUST NOT configure below it |
| Ceiling enforcement | Values > 60 min require explicit override flag + audit entry |

---

## 4. Idle Detection and Enforcement

### 4.1 Definition of "Idle"

A session is considered idle when no user input or application-level API call
has been recorded for the duration of the role's configured timeout threshold.
Idle time is measured from the **last activity timestamp**, not from session
login time.

### 4.2 Watchdog Requirements (§VII Session Controls)

- An idle-timeout watchdog MUST monitor session activity.
- The watchdog MUST force logout (or session lock, per deployment policy) when
  the idle threshold is exceeded.
- The watchdog MUST be **unit-testable in isolation** with configurable
  thresholds.
- The watchdog MUST reset the idle timer on each qualifying activity event.

### 4.3 User Warning

The system MUST display a warning at least **60 seconds** before session expiry
due to idle timeout. The warning MUST give the user the opportunity to extend
the session. The exact UI pattern and countdown display beyond the 60-second
minimum are implementation-defined.

---

## 5. Reference Implementation

```python
"""
idle_timeout_reference.py — Constitutional idle timeout defaults
Standard: §VII.Z  |  §G.11  |  Constitution: v1.24.0  |  Spec: docs/idle-timeout-spec.md
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional

# Per-role constitutional defaults (§G.11)
IDLE_TIMEOUT_DEFAULTS: dict[str, int] = {
    "admin":    10,   # minutes
    "dev":      15,
    "user":     30,
    "readonly": 45,
}

IDLE_TIMEOUT_CEILING_MINUTES = 60       # §VII.Z.3
IDLE_TIMEOUT_ABSOLUTE_MAX_HOURS = 8    # §VII Session Controls


def get_default_timeout_minutes(role: str) -> int:
    """Return the constitutional default idle timeout for a role."""
    timeout = IDLE_TIMEOUT_DEFAULTS.get(role)
    if timeout is None:
        raise ValueError(f"Unknown role: {role!r}. Known roles: {list(IDLE_TIMEOUT_DEFAULTS)}")
    return timeout


def validate_timeout_value(
    minutes: int,
    is_explicit_override: bool = False,
) -> None:
    """
    Validate that minutes is within constitutional bounds.
    Raises ValueError if the value violates §VII.Z.3.
    """
    if minutes < 1:
        raise ValueError("Idle timeout must be at least 1 minute.")
    max_minutes = IDLE_TIMEOUT_ABSOLUTE_MAX_HOURS * 60
    if minutes > max_minutes:
        raise ValueError(
            f"Idle timeout {minutes} min exceeds absolute system ceiling "
            f"({max_minutes} min / {IDLE_TIMEOUT_ABSOLUTE_MAX_HOURS} hours)."
        )
    if minutes > IDLE_TIMEOUT_CEILING_MINUTES and not is_explicit_override:
        raise ValueError(
            f"Idle timeout {minutes} min exceeds the 60-minute ceiling. "
            "An explicit administrative override with an audit log entry is required."
        )


class IdleTimeoutWatchdog:
    """
    Minimal watchdog tracking last activity and evaluating expiry.
    Must be unit-testable in isolation with injected time (§VII Session Controls).
    """

    def __init__(self, role: str, configured_minutes: Optional[int] = None) -> None:
        self.role = role
        timeout_minutes = configured_minutes or get_default_timeout_minutes(role)
        validate_timeout_value(timeout_minutes)
        self._timeout = timedelta(minutes=timeout_minutes)
        self._last_activity: datetime = datetime.utcnow()

    def record_activity(self, at: Optional[datetime] = None) -> None:
        self._last_activity = at or datetime.utcnow()

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.utcnow()
        return (now - self._last_activity) >= self._timeout

    def seconds_until_expiry(self, now: Optional[datetime] = None) -> float:
        now = now or datetime.utcnow()
        remaining = self._timeout - (now - self._last_activity)
        return max(0.0, remaining.total_seconds())

    def should_warn(self, now: Optional[datetime] = None, warn_seconds: int = 60) -> bool:
        """True when < warn_seconds remain before expiry (§VII Session Controls)."""
        return 0 < self.seconds_until_expiry(now) <= warn_seconds


def apply_admin_override(
    role: str,
    new_timeout_minutes: int,
    actor: str,
    audit_log,
    is_explicit_override: bool = True,
) -> None:
    """
    Apply an administrative idle-timeout override for a role.
    Logs the change per §VII.Z.4.
    """
    old_timeout = get_default_timeout_minutes(role)
    validate_timeout_value(new_timeout_minutes, is_explicit_override=is_explicit_override)
    audit_log.record(
        event="idle_timeout_override",
        actor=actor,
        role=role,
        old_value_minutes=old_timeout,
        new_value_minutes=new_timeout_minutes,
        timestamp=datetime.utcnow().isoformat(),
    )
    # Persist the new value (implementation-defined)
    # config.set_idle_timeout(role, new_timeout_minutes)
```

---

## 6. CI Test Specification (§VII.Z.5)

### 6.1 Unit Tests

| ID | Name | Pass condition |
|----|------|----------------|
| T1 | admin default | `get_default_timeout_minutes("admin")` returns `10` |
| T2 | dev default | `get_default_timeout_minutes("dev")` returns `15` |
| T3 | user default | `get_default_timeout_minutes("user")` returns `30` |
| T4 | readonly default | `get_default_timeout_minutes("readonly")` returns `45` |
| T5 | 60-minute ceiling enforced | `validate_timeout_value(61)` raises without `is_explicit_override=True` |
| T6 | explicit override allowed > 60 min | `validate_timeout_value(90, is_explicit_override=True)` does not raise |
| T7 | watchdog expires correctly | `is_expired()` returns `True` after injected time exceeds threshold |
| T8 | watchdog resets on activity | After `record_activity()`, `is_expired()` returns `False` |
| T9 | warning fires at ≤ 60 s | `should_warn()` returns `True` when 30 s remain |
| T10 | admin override logged | `apply_admin_override()` calls `audit_log.record()` with all four fields |

### 6.2 Static Analysis Rules

CI MUST detect and reject:
- A single shared constant used as the idle timeout for all roles (e.g.,
  `DEFAULT_IDLE_TIMEOUT = 30` applied to every role without branching)
- Any default value > 60 minutes in per-role config without an
  `is_explicit_override` guard
- Missing per-role entries in the timeout configuration (all four roles MUST
  be present)

### 6.3 CI Failure Conditions

CI MUST fail if any of the following are true:
- Any T1–T4 test is absent or failing (role defaults incorrect)
- T5 or T6 is absent or failing (ceiling rule broken)
- T7–T9 absent or failing (watchdog behaviour)
- T10 absent or failing (override not logged)
- Static analysis detects a single global idle timeout constant
- `admin` default ≥ `user` default (privilege ordering violated)
- `dev` default ≥ `user` default (privilege ordering violated)

---

## 7. Migration Plan for Existing Implementations

| Step | Action |
|------|--------|
| 1 | Identify all occurrences of hard-coded idle timeout constants in source (search for `30 * 60`, `IDLE_TIMEOUT`, `SESSION_TIMEOUT`, etc.) |
| 2 | Replace with `IDLE_TIMEOUT_DEFAULTS` mapping keyed by role |
| 3 | Update session-creation logic to call `get_default_timeout_minutes(session.role)` |
| 4 | Update admin config UI to expose per-role timeout fields (not a single global field) |
| 5 | Add `is_explicit_override` flag to any admin config that allows > 60 min |
| 6 | Add audit-log call to all admin timeout override paths |
| 7 | Add tests T1–T10 and static lint rules |

---

## 8. Session Lifecycle Diagram

```
SESSION LIFECYCLE WITH ROLE-BASED IDLE TIMEOUT
───────────────────────────────────────────────

 1. User logs in (role: admin / dev / user / readonly)
        │
        ▼
 2. System assigns idle timeout from §G.11:
    admin → 10 min  |  dev → 15 min
    user  → 30 min  |  readonly → 45 min
        │
        ▼
 3. Activity loop
    Any input or API call → reset last_activity timestamp
        │
        ▼
 4. Watchdog evaluates: now − last_activity ≥ role_timeout?
        │
        ├── NO  → continue activity loop (step 3)
        │
        └── YES → Is remaining time ≤ 60 s?
                        │
                        ├── YES → Show expiry warning, offer extend
                        │           │
                        │           ├── User extends → reset timer
                        │           └── No action → continue to step 5
                        │
                        └── NO → continue evaluating
        │
        ▼
 5. Timeout reached → lock session or log out
    tokens/secrets cleared from memory
```

---

## 9. Cross-References

| Reference | Location |
|-----------|----------|
| §G.11 Role-differentiated idle timeout defaults | constitution.md §G.11 |
| §VII.Z Idle Timeout Requirements | constitution.md §VII.Z |
| §VII Session Controls | constitution.md §VII |
| checklist-idle-timeout-compliance.md | Reviewer checklist |
