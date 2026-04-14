# ComponentGuardian Specification

**Governing constitution sections**: §V, §V.1–§V.5
**Version**: 1.0 (established constitution v1.18.0, 2026-04-04 Q5)
**PR checklist**: [.specify/memory/checklist-component-guardian-recovery.md](../.specify/memory/checklist-component-guardian-recovery.md)

---

## 1. Purpose

This document is the canonical technical reference for the `ComponentGuardian`
system defined in §V of the project constitution. It provides:

1. The normative state machine for registered components
2. Required API contract
3. CI test specification
4. Migration patch for existing components

It supplements the constitutional text and MUST be kept in sync with it.
Where this document conflicts with the constitution, the constitution governs.

---

## 2. State Machine

### 2.1 States

A `ComponentGuardian`-managed component MUST be in exactly one of the
following states at all times:

| State | Meaning |
|-------|---------|
| `HEALTHY` | Component initialized successfully; `health_check()` returning `True` |
| `DEGRADED` | Component failed to initialize, or `health_check()` returned `False` |

No other states are constitutionally defined. Implementations MAY track
`INITIALIZING` internally for logging purposes but MUST resolve to `HEALTHY`
or `DEGRADED` before any user interaction is possible.

### 2.2 State Machine Diagram

```
+--------------------+
|     HEALTHY        |◄──────────────────────────────────────────────┐
+--------+-----------+                                                |
         |                                                            |
         | health_check() == False                                    |
         | (runtime polling)                                          |
         ▼                                                            |
+--------------------+                                                |
|     DEGRADED       |─────── health_check() == True (polling) ──────┘
+--------------------+

Additional startup transitions:

+--------------------+
|   INITIALIZING     |
+--------+-----------+
         |                               |
         | init success                  | init failure
         ▼                               ▼
+--------------------+          +--------------------+
|     HEALTHY        |          |     DEGRADED       |
+--------------------+          +--------------------+

Rules:
  - Only health_check() drives HEALTHY <-> DEGRADED transitions.
  - No "force HEALTHY" path is permitted without a passing health_check().
  - No "force DEGRADED" path is intended (degradation is a detection event,
    not a manual setpoint).
  - A component in DEGRADED state MUST remain visible in the UI.
```

### 2.3 Transition Table

| From State | Event | To State | Action Required |
|------------|-------|----------|-----------------|
| INITIALIZING | init success | HEALTHY | (no log required for silent success) |
| INITIALIZING | init failure | DEGRADED | Log degradation + invoke `degraded_fallback` |
| HEALTHY | `health_check()` returns `False` | DEGRADED | Log degradation + invoke `degraded_fallback` |
| DEGRADED | `health_check()` returns `True` | HEALTHY | Log recovery + resume normal operation |
| DEGRADED | `health_check()` returns `False` | DEGRADED | Remain in DEGRADED (no re-log unless policy differs) |
| HEALTHY | `health_check()` returns `True` | HEALTHY | Remain in HEALTHY (no log) |

---

## 3. API Contract

### 3.1 Registration

```python
ComponentGuardian.register(
    widget,           # The component instance (QWidget or equivalent)
    health_check,     # zero-argument callable → bool
    degraded_fallback # zero-argument callable invoked on degradation
)
```

**Constraints**:
- `health_check` MUST be a zero-argument callable returning `bool`
- `degraded_fallback` MUST be a zero-argument callable
- `degraded_fallback` MUST render the component visible with reduced
  functionality (MUST NOT hide or remove the component)
- `health_check` is the sole arbiter of state transitions (§V.2)

### 3.2 Polling (§V.6)

The `ComponentGuardian` calls `health_check()` periodically during active use.
Polling bounds are **normative** (resolved by §V.6.5 / Q6, constitution v1.19.0):

| Bound | Value | Constitutional reference |
|-------|-------|--------------------------|
| Maximum frequency | no more than once every **500 ms** | §V.6.2 |
| Minimum frequency | at least once every **5 seconds** | §V.6.1 |
| Implementation strategy | fixed, jitter, backoff, or adaptive — all permitted within bounds | §V.6.3 |

The effective interval MUST never fall outside [500 ms, 5 s] during active use.
TODO(GUARDIAN_POLL_INTERVAL) is **closed** by §V.6.5.

### 3.3 State Enum (Reference Implementation)

```python
from enum import Enum

class HealthState(Enum):
    HEALTHY  = "healthy"
    DEGRADED = "degraded"
```

---

## 4. Required Logging Helpers (§V.4)

Every component MUST use structured log helpers that produce the required
fields. The following is a reference implementation (Python):

```python
import logging

logger = logging.getLogger("component_guardian")

def log_degraded(component_id: str, reason: str, error: str = None) -> None:
    logger.info({
        "event":      "component_degraded",
        "component":  component_id,
        "from_state": "healthy",       # or "initializing" on init failure
        "to_state":   "degraded",
        "reason":     reason,
        "error":      error,           # optional; MUST NOT be the only artifact
    })

def log_recovered(component_id: str, reason: str = "health_check() returned True") -> None:
    logger.info({
        "event":      "component_recovered",
        "component":  component_id,
        "from_state": "degraded",
        "to_state":   "healthy",
        "reason":     reason,
    })
```

**Rules**:
- Raw exception stack traces MUST NOT be the sole log artifact for a
  degradation event: the structured fields MUST always be present.
- Token or secret data MUST NOT appear in log entries.
- Log entries MUST be parseable by the §III structured logging system.

---

## 5. Polling Implementation (Reference)

```python
def poll_health(self) -> None:
    """Called periodically by ComponentGuardian at the configured interval."""
    ok = self.health_check()

    if not ok and self.health_state == HealthState.HEALTHY:
        self.health_state = HealthState.DEGRADED
        log_degraded(
            component_id=self.component_id,
            reason="health_check() returned False"
        )
        self._invoke_degraded_fallback()

    elif ok and self.health_state == HealthState.DEGRADED:
        self.health_state = HealthState.HEALTHY
        log_recovered(component_id=self.component_id)
        self._resume_normal_operation()
        # Component re-enters regular polling cycle automatically
```

---

## 6. CI Test Specification (§V.5)

### 6.1 Required Tests Per Component

For every `ComponentGuardian`-managed component, CI MUST execute the following
tests:

| # | Test Name | Scenario | Assert |
|---|-----------|----------|--------|
| T1 | `test_init_degraded` | Force initialization failure | State == `DEGRADED`; degradation log emitted with all required fields |
| T2 | `test_runtime_degraded` | Start `HEALTHY`; mock `health_check()` → `False` | State == `DEGRADED`; degradation log emitted |
| T3 | `test_runtime_recovery` | From `DEGRADED`; mock `health_check()` → `True` | State == `HEALTHY`; recovery log emitted with all required fields |
| T4 | `test_sticky_degraded_prevention` | T3 follow-on: verify normal operation resumes | No degraded indicators; full functionality available |
| T5 | `test_no_force_healthy` | Attempt to set state = `HEALTHY` without passing `health_check()` | Operation impossible or rejected |
| T6 | `test_no_silent_transitions` | Trigger any state transition | Structured log entry emitted; test fails if absent |

### 6.2 CI Enforcement Rules

| Rule | Description | Failure |
|------|-------------|---------|
| R1 | Each registered component has all 6 state-machine tests present and passing | Build fails |
| R2 | Log entries for transitions contain all §V.4 fields | Build fails |
| R3 | Contract test: only `health_check()` drives `HEALTHY ↔ DEGRADED` | Build fails if alternative path found |
| R4 | Tests are not skipped, disabled, or marked `TODO` | Build fails |
| R5 | Effective polling interval never < 500 ms under load | Build fails |
| R6 | Effective polling interval never > 5 s during active use | Build fails |
| R7 | Polling interval is testable via mock timers / virtual clocks | Build fails if no such test |

---

## 7. Migration Patch for Existing Components

Apply this patch to any existing `ComponentGuardian`-managed component that
predates constitution v1.18.0.

### Step 1 — Add State Enum

```python
from enum import Enum

class HealthState(Enum):
    HEALTHY  = "healthy"
    DEGRADED = "degraded"

# In component __init__:
self.health_state = HealthState.HEALTHY
```

### Step 2 — Wire Degradation on Initialization Failure

```python
def _initialize(self) -> None:
    try:
        # ... existing init logic ...
        self.health_state = HealthState.HEALTHY
    except Exception as e:
        self.health_state = HealthState.DEGRADED
        log_degraded(
            component_id=self.component_id,
            reason="initialization failure",
            error=str(e)
        )
        self._invoke_degraded_fallback()
```

### Step 3 — Wire Recovery in Polling

Replace any ad-hoc health polling logic with the reference `poll_health()`
implementation from Section 5 above.

### Step 4 — Remove Ad-Hoc Flags

Replace any custom `is_broken`, `disabled`, `failed_once`, or equivalent
flags with the unified `health_state`. Ensure no duplicated state holders exist.

### Step 5 — Add Structured Logging Helpers

Import or copy the `log_degraded` / `log_recovered` helpers from Section 4.

### Step 6 — Add Tests

Implement the six tests from Section 6.1 for the migrated component.

### Step 7 — Record Migration Status

Add an entry to the migration tracker below.

---

## 8. Migration Tracker

Track which components have been migrated to the v1.18.0/v1.19.0 recovery
and polling model.

| Component | Module Path | Migrated | §V.1–§V.5 Tests | §V.6 Polling Bounds | Notes |
|-----------|-------------|----------|-----------------|---------------------|-------|
| *(new components registered after v1.19.0 are in-scope from creation)* | | | | | |

---

## 9. Cross-References

| Reference | Location |
|-----------|----------|
| §V — Simplicity & Extensible Modularity | constitution.md §V |
| §V.1 — Recovery Eligibility | constitution.md §V.1 |
| §V.2 — Recovery Trigger | constitution.md §V.2 |
| §V.3 — Recovery Behavior | constitution.md §V.3 |
| §V.4 — Recovery Logging | constitution.md §V.4 |
| §V.5 — Deterministic Reviewability | constitution.md §V.5 |
| §V.6 — Health-Check Polling Interval | constitution.md §V.6 |
| §V.6.1 — Minimum Polling Frequency (5 s) | constitution.md §V.6.1 |
| §V.6.2 — Maximum Polling Frequency (500 ms) | constitution.md §V.6.2 |
| §V.6.5 — TODO(GUARDIAN_POLL_INTERVAL) closed | constitution.md §V.6.5 |
| TODO(GUARDIAN_DEGRADED_UX) | constitution.md (still open) |
| §III — Structured logging requirement | constitution.md §III |
| PR checklist | .specify/memory/checklist-component-guardian-recovery.md |
| Critical engine classification | .specify/memory/checklist-critical-engine-classification.md |

---

## 10. Polling Reference Implementation

This section provides a reference Python implementation satisfying §V.6.

### 10.1 Constants

```python
MIN_POLL_INTERVAL_S = 0.5   # seconds  (§V.6.2 maximum frequency)
MAX_POLL_INTERVAL_S = 5.0   # seconds  (§V.6.1 minimum frequency)
```

### 10.2 Clamped Polling Loop

```python
import time

def poll_loop(self, desired_interval: float = 1.0) -> None:
    """
    Polling loop for ComponentGuardian-managed component.
    desired_interval: target interval in seconds (must be in [0.5, 5.0]).
    Implementations may pass any value; it is clamped to constitutional bounds.
    """
    running = True
    while running:
        start = time.monotonic()

        # --- health check and state transition ---
        ok = self.health_check()
        if not ok and self.health_state == HealthState.HEALTHY:
            self.health_state = HealthState.DEGRADED
            log_degraded(self.component_id, reason="health_check() returned False")
            self._invoke_degraded_fallback()
        elif ok and self.health_state == HealthState.DEGRADED:
            self.health_state = HealthState.HEALTHY
            log_recovered(self.component_id)
            self._resume_normal_operation()

        # --- sleep within constitutional bounds ---
        elapsed = time.monotonic() - start
        raw_sleep = desired_interval - elapsed
        sleep_time = max(MIN_POLL_INTERVAL_S,
                         min(MAX_POLL_INTERVAL_S, raw_sleep))
        time.sleep(sleep_time)
```

### 10.3 Polling Loop Diagram

```
+-------------------------------------------------------------+
|                     ComponentGuardian                       |
+-------------------------------------------------------------+

            (every 500 ms to 5 s, inclusive — §V.6.1–§V.6.2)
                           |
                           ▼
                +-----------------------+
                |   health_check()      |
                +-----------------------+
                           |
          +----------------+----------------+
          |                                 |
          | ok == True                      | ok == False
          ▼                                 ▼
+-----------------------+        +-----------------------+
|  State = HEALTHY      |        |  State = DEGRADED     |
|  (if prev. degraded   |        |  (if prev. healthy    |
|   → log recovery)     |        |   → log degradation)  |
+-----------------------+        +-----------------------+
          |                                 |
          +----------------+----------------+
                           |
                           ▼
                +-----------------------+
                |   sleep(interval)     |
                |  0.5 s ≤ interval ≤ 5 s |
                +-----------------------+
                           |
                           ▼
                     (next poll)
```

### 10.4 Polling Interval Unit Test Requirements (§V.6.4)

```python
def test_poll_interval_minimum(component, mock_timer):
    """Effective interval between polls MUST NOT exceed 5 s."""
    intervals = measure_poll_intervals(component, mock_timer, n=20)
    assert all(i <= MAX_POLL_INTERVAL_S for i in intervals)

def test_poll_interval_maximum(component, mock_timer):
    """Effective interval between polls MUST NOT be less than 500 ms."""
    intervals = measure_poll_intervals(component, mock_timer, n=20)
    assert all(i >= MIN_POLL_INTERVAL_S for i in intervals)

def test_poll_interval_backoff_within_bounds(component, mock_timer):
    """If jitter/backoff is used, no sampled interval violates bounds."""
    stress_intervals = measure_poll_intervals_under_load(component, mock_timer, n=100)
    assert all(MIN_POLL_INTERVAL_S <= i <= MAX_POLL_INTERVAL_S
               for i in stress_intervals)
```
