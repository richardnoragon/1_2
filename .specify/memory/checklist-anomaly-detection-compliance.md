# Reviewer Checklist — Anomaly Detection Sliding-Window Compliance

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §16 (Session Management & Auditing), §16.Y
**Applied in constitution version**: v1.30.0

**See also**:
- `.specify/memory/constitution.md` §16, §16.Y.1–§16.Y.6
- `docs/anomaly-detection-sliding-window-spec.md` (canonical spec, reference
  implementation, CI tests T1–T5)

---

## How to Use This Checklist

Mark each item ✓ (pass), ✗ (fail), or N/A. Any ✗ is a constitutional violation
that MUST be resolved before merge. Every section must be fully signed-off by a
reviewer and the CI pipeline.

---

## Section A — Sliding Window Implementation

### A.1 — Window Type

- [ ] **A.1.1** The failure counter evaluates failures in the last 24 hours
  relative to the current attempt timestamp (`now − 24h ≤ ts ≤ now`), not
  a fixed or calendar-anchored period.
- [ ] **A.1.2** The window is recalculated fresh on every authentication
  attempt; no cached or pre-computed window boundary is reused across attempts.
- [ ] **A.1.3** No midnight-reset logic exists (`if hour == 0: counter = 0`
  or equivalent patterns).
- [ ] **A.1.4** No epoch-anchored or account-creation-relative window boundary
  exists.

*FAIL if*: Logic groups failures by date, hour-bucket, or any non-sliding period.

### A.2 — Per-Attempt Evaluation

- [ ] **A.2.1** The sliding-window evaluation is invoked synchronously from the
  authentication attempt code path (not only from background/cron code).
- [ ] **A.2.2** Grep confirms the anomaly-detection function is called from the
  login/authentication handler, not exclusively from a scheduled task.

*FAIL if*: Detection only runs in periodic jobs without per-attempt invocation.

---

## Section B — Time Resolution

### B.1 — Timestamp Precision

- [ ] **B.1.1** Failure timestamps are stored with at least second-level UTC
  precision (e.g., `datetime.now(tz=timezone.utc).replace(microsecond=0)` or
  finer).
- [ ] **B.1.2** The window boundary calculation uses the stored timestamp
  directly without rounding to minutes, hours, or calendar dates.
- [ ] **B.1.3** Database schema, log format, or in-memory store records
  timestamps in ISO 8601 with seconds (or finer) granularity.

*FAIL if*: Timestamps are rounded to minutes/hours or stored as dates only.

### B.2 — Window Formula Accuracy

- [ ] **B.2.1** The effective window formula is verified to be:
  `window_start = now − timedelta(hours=24)` (or equivalent in project
  language) where `now` is UTC at the moment of the current attempt.
- [ ] **B.2.2** No off-by-one second exists at the window boundary (inclusive
  lower bound: `≥ window_start`).

---

## Section C — Threshold and Immediate Detection

### C.1 — Threshold Semantics

- [ ] **C.1.1** The threshold is `THRESHOLD = 10` and the comparison is strict
  `count > THRESHOLD` (i.e., 11 failures trigger; 10 do not).
- [ ] **C.1.2** The threshold value is defined as a named constant; no magic
  numbers appear inline.
- [ ] **C.1.3** The threshold is per-user; global aggregates are not used as
  the primary check.

*FAIL if*: Threshold is `≥10`, `>9`, or any value other than strict `>10`.

### C.2 — Immediate Alert

- [ ] **C.2.1** When the threshold is crossed, the anomaly flag/alert is raised
  in the same call that evaluates the window (not queued for later).
- [ ] **C.2.2** Both alert channels fire immediately:
  - [ ] **C.2.2a** `CRITICAL`-level structured log entry is emitted at the
    triggering attempt.
  - [ ] **C.2.2b** In-app alert surfaces in the RFU hub to all currently
    logged-in `admin`-role and `dev`-role users without deferral.
- [ ] **C.2.3** No `asyncio.gather`-deferred or thread-queued alerting replaces
  synchronous firing as the primary alert path.

*FAIL if*: Detection is deferred to batch processing or a background task is
the only alert mechanism.

### C.3 — Background Sweeps (if present)

- [ ] **C.3.1** Any background sweep is documented as supplementary (analytics /
  reporting only).
- [ ] **C.3.2** The background sweep code path does not contain `return` or
  early-exit logic that would prevent per-attempt evaluation from running.

---

## Section D — Per-User Isolation

### D.1 — Counter Scoping

- [ ] **D.1.1** Failed attempts are stored and queried keyed by `user_id` (or
  equivalent unique user identifier); no cross-user aggregation occurs.
- [ ] **D.1.2** A test confirms that User A's failures do not affect User B's
  threshold count (see T5 in spec).

---

## Section E — Independence from Lockout Mechanism (§VII)

- [ ] **E.1** The anomaly-detection counter and the consecutive-failure lockout
  counter are maintained in separate data structures/fields.
- [ ] **E.2** When `is_blocked` is set (lockout fired), anomaly detection does
  not fire again for the same account while it remains blocked.
- [ ] **E.3** Conversely: when anomaly detection fires, it does not set
  `is_blocked` (lockout is not triggered by anomaly detection).

---

## Section F — Automated Test Coverage

### F.1 — Required CI Tests

Each test must exist and pass in the CI pipeline:

| Test | Behaviour | Pass condition |
|---|---|---|
| **T1** | 10 failures within 24h | No anomaly; returns False |
| **T2** | 11th failure within 24h | Anomaly fires; both channels called |
| **T3** | 10 failures → wait >24h → 1 more | No anomaly (old failures outside window) |
| **T4** | Failures straddling calendar midnight (all within 24h) | Anomaly fires |
| **T5** | User A has 11 failures; User B attempted once | No anomaly for User B |

- [ ] **F.1.1** T1 passes.
- [ ] **F.1.2** T2 passes.
- [ ] **F.1.3** T3 passes.
- [ ] **F.1.4** T4 passes.
- [ ] **F.1.5** T5 passes.

### F.2 — Forbidden Test Anti-Patterns

- [ ] **F.2.1** Tests do NOT use `datetime.now()` (naive, no timezone) —
  all timestamps MUST use timezone-aware UTC datetimes.
- [ ] **F.2.2** Tests do NOT assert only "many failures triggers alert" without
  controlling temporal spacing; time-spaced assertions (T3, T4) are present.

---

## Sign-Off

| Role | Reviewer | Date | Pass/Fail |
|---|---|---|---|
| Developer | | | |
| Security reviewer | | | |
| CI pipeline | | | |
