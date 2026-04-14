# Anomaly Detection: Sliding 24-Hour Window — Canonical Specification

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §16 (Session Management & Auditing), §16.Y
**Source clarification**: constitution_clairification_uiux_harmonny_r8.md — Q17
**Applied in constitution version**: v1.30.0

**See also**:
- `.specify/memory/constitution.md` §16, §16.Y
- `.specify/memory/checklist-anomaly-detection-compliance.md`
- `docs/audit-origin-metadata-spec.md` (related — §16.X)

---

## 1. Purpose

§16 requires: *"Automated anomaly detection MUST flag >10 failed attempts within
any rolling 24-hour window per user."*

The word *"rolling"* is operationally ambiguous. This document defines the
precise implementation model, time resolution, detection trigger semantics, and
CI obligations that close that ambiguity.

---

## 2. Formal Definitions

### 2.1 Sliding Window (MUST)

The 24-hour window **MUST** be implemented as a **sliding window** evaluated at
the time of each authentication attempt. At every failed login event the system
evaluates:

```
window_start = now − 24h   (UTC, second-level precision)
window_end   = now         (UTC, second-level precision)
```

A failure is counted toward the threshold if and only if:

```
window_start ≤ failure.timestamp ≤ window_end
```

**Fixed-period windows are explicitly forbidden.**  Examples of forbidden
implementations:

| Forbidden model | Why |
|---|---|
| Calendar-day window (midnight reset) | 9 failures at 23:59 + 9 at 00:01 = 18 failures, zero alerts |
| Account-creation-epoch window | predictable reset time; exploitable |
| Hourly bucket aggregation | gaps at bucket boundaries |

### 2.2 Time Resolution (MUST — per-second)

Failure timestamps MUST be stored with **at least second-level precision**.
Sub-second precision is permitted but not required. The sliding window
calculation MUST use this stored timestamp directly; no rounding or truncation
to minutes, hours, or dates is permitted.

### 2.3 Immediate Detection (MUST — per-attempt)

Detection MUST occur **synchronously** at the authentication attempt that causes
the count to exceed 10. Let N be the count of distinct failed attempts in the
sliding window before the current attempt. When N = 10, the current attempt is
the threshold-crossing event:

```
if count_in_window(user_id, now - 24h, now) > 10:
    flag_anomaly_immediately(user_id, now)
```

Detection MUST NOT be deferred to background tasks, periodic cron jobs, or
batch processors.

### 2.4 Threshold Semantics

The threshold is **strict greater-than**: `>10`. The 11th failure within the
sliding 24-hour window triggers the anomaly. The threshold MUST NOT be treated
as `≥10` or any other value.

### 2.5 Background Sweeps (Optional — MUST NOT replace §16.Y.4)

Implementations MAY perform periodic background sweeps for analytics or audit
reporting. Such sweeps MUST NOT be the sole or primary detection path. Real-time
per-attempt evaluation remains mandatory regardless of whether background sweeps
exist.

---

## 3. Alert Channels (from §16)

When the threshold is crossed, the system MUST escalate via **both** channels
concurrently:

1. Emit a `CRITICAL`-level structured log entry (fields: `user_id`,
   `event_type: "ANOMALY_DETECTED"`, `utc_timestamp`, `failure_count`,
   `window_start`, `window_end`).
2. Surface an in-app alert in the RFU hub to all currently logged-in
   `admin`-role and `dev`-role users. The alert MUST appear in real time; no
   queuing or deferred display is permitted for the in-app channel.

No external email, webhook, or out-of-band channel is required by the
constitution.

---

## 4. Independence from Lockout Mechanism

The §16.Y sliding-window anomaly detector and the §VII consecutive-failure
lockout mechanism are **independent** and maintain **separate counters**.
Once the lockout mechanism fires and `is_blocked` is set, anomaly detection
does NOT additionally apply to that account while it remains blocked.

---

## 5. Reference Implementation

```python
from datetime import datetime, timedelta, timezone
from typing import List, Protocol


class FailedAttempt:
    def __init__(self, user_id: str, timestamp: datetime) -> None:
        self.user_id = user_id
        self.timestamp = timestamp


class AttemptStore(Protocol):
    def save(self, attempt: FailedAttempt) -> None: ...
    def get_for_user(self, user_id: str) -> List[FailedAttempt]: ...


class AnomalyChannel(Protocol):
    def critical_log(
        self,
        user_id: str,
        at: datetime,
        count: int,
        window_start: datetime,
        window_end: datetime,
    ) -> None: ...
    def in_app_alert(self, user_id: str, at: datetime, count: int) -> None: ...


THRESHOLD: int = 10
WINDOW: timedelta = timedelta(hours=24)


def record_failed_attempt(
    user_id: str,
    store: AttemptStore,
    channel: AnomalyChannel,
) -> bool:
    """
    Record a failed authentication attempt and evaluate the sliding window.

    Returns True if an anomaly is triggered, False otherwise.

    Requirements met:
    - Sliding window: window_start = now − 24h (per-second resolution, UTC).
    - Per-attempt: called synchronously on every failure.
    - Immediate detection: anomaly flagged in this call if threshold crossed.
    - Strict >10 threshold: 11th failure triggers, not 10th.
    - Per-user scoping: counters are user_id-scoped.
    """
    # §16.Y.3 — UTC timestamp, per-second precision
    now: datetime = datetime.now(tz=timezone.utc).replace(microsecond=0)

    # Persist failure BEFORE evaluating (ensures current attempt is counted)
    store.save(FailedAttempt(user_id, now))

    # §16.Y.2 — Sliding window bounds
    window_start = now - WINDOW
    recent: List[FailedAttempt] = [
        f for f in store.get_for_user(user_id)
        if window_start <= f.timestamp <= now
    ]

    # §16.Y.4 — Strict threshold; immediate detection
    if len(recent) > THRESHOLD:
        channel.critical_log(user_id, now, len(recent), window_start, now)
        channel.in_app_alert(user_id, now, len(recent))
        return True

    return False
```

**Key properties satisfied**:

| Requirement | How satisfied |
|---|---|
| Sliding window | `window_start = now − 24h` derived from current-attempt UTC timestamp |
| Per-second resolution | `replace(microsecond=0)` — second-level UTC |
| Per-attempt evaluation | Function called synchronously on each failure |
| Immediate detection | Anomaly flagged inside the same call |
| Strict >10 | `len(recent) > THRESHOLD` where `THRESHOLD = 10` |
| Per-user scoping | Filtered by `user_id` |

---

## 6. CI Tests

### T1 — Below Threshold (no alert)

10 failures within 24 hours → `record_failed_attempt` returns `False`; no
channels called.

```python
def test_t1_below_threshold():
    store = InMemoryStore()
    channel = RecordingChannel()
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    for i in range(10):
        ts = now - timedelta(hours=i)
        store.save(FailedAttempt("u1", ts))
    # 10th (threshold) returns False — threshold is STRICT >10
    result = record_failed_attempt_at("u1", now, store, channel)
    assert result is False
    assert len(channel.in_app_calls) == 0
```

### T2 — Threshold Crossing (alert fires)

11th failure within 24 hours → `record_failed_attempt` returns `True`; both
channels called exactly once.

```python
def test_t2_threshold_crossing():
    store = InMemoryStore()
    channel = RecordingChannel()
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    for i in range(11):
        ts = now - timedelta(minutes=i)
        store.save(FailedAttempt("u1", ts))
    result = record_failed_attempt_at("u1", now, store, channel)
    assert result is True
    assert len(channel.in_app_calls) == 1
    assert channel.critical_log_calls[0]["count"] > 10
```

### T3 — Boundary at Exactly 24h (no alert)

10 failures, then wait just over 24h, then 1 more failure → sliding window
contains only the new failure → no alert.

```python
def test_t3_boundary_at_24h():
    store = InMemoryStore()
    channel = RecordingChannel()
    base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    for i in range(10):
        store.save(FailedAttempt("u1", base - timedelta(hours=1, minutes=i)))
    # now = base + 24h + 1s → the 10 old failures fall outside window
    now = base + timedelta(hours=24, seconds=1)
    result = record_failed_attempt_at("u1", now, store, channel)
    assert result is False
```

### T4 — Straddling Calendar Midnight (alert fires)

Failures before and after midnight but all within 24h → anomaly still triggers
(no fixed-period reset).

```python
def test_t4_straddling_midnight():
    store = InMemoryStore()
    channel = RecordingChannel()
    midnight = datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
    # 6 failures before midnight, 5 failures after midnight (all within 24h)
    for i in range(6):
        store.save(FailedAttempt("u1", midnight - timedelta(hours=i+1)))
    for i in range(5):
        store.save(FailedAttempt("u1", midnight + timedelta(minutes=i+1)))
    now = midnight + timedelta(minutes=6)
    result = record_failed_attempt_at("u1", now, store, channel)
    assert result is True
```

### T5 — Per-User Isolation

User A's failures do NOT count toward User B's threshold.

```python
def test_t5_per_user_isolation():
    store = InMemoryStore()
    channel = RecordingChannel()
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    for i in range(11):
        store.save(FailedAttempt("userA", now - timedelta(minutes=i)))
    # userB has 0 prior failures
    result = record_failed_attempt_at("userB", now, store, channel)
    assert result is False
    assert len(channel.in_app_calls) == 0
```

---

## 7. Cross-References

| Document | Relevant section |
|---|---|
| `.specify/memory/constitution.md` | §16 (anomaly detection bullet), §16.Y.1–§16.Y.6 |
| `.specify/memory/checklist-anomaly-detection-compliance.md` | Reviewer checklist Sections A–E |
| `docs/audit-origin-metadata-spec.md` | §16.X — origin metadata (related §16 sub-chapter) |
| `docs/pii-scan-ux-spec.md` | §VIII.X — PII scan delivery (parallel spec) |
| `docs/file-validation-exemption-spec.md` | §IX.X — validation exemption boundary (parallel spec) |
