# ComponentGuardian Degradation & Recovery Compliance Checklist

**Applicable constitution sections**: §V.1, §V.2, §V.3, §V.4, §V.5, §V.6 (§V.6.1–§V.6.5)
**Spec reference**: [docs/component-guardian-spec.md](../../docs/component-guardian-spec.md)
**Related checklists**: [checklist-side-effect-dry-run-compliance.md](checklist-side-effect-dry-run-compliance.md)
**Version**: 1.1 (Section H added, constitution v1.19.0, 2026-04-04 Q6)

---

## Purpose

This checklist is used by PR reviewers to verify that any ComponentGuardian-
managed component correctly implements both degradation and recovery behaviour
as required by §V.1–§V.5. All `FAIL` conditions are PR-blocking.

Apply this checklist to any PR that:
- Registers a new component with `ComponentGuardian`
- Modifies an existing registered component's `health_check()` or
  `degraded_fallback` callables
- Changes state-transition logic, polling behaviour, or logging for a
  registered component
- Adds or changes tests for degradation/recovery behaviour

---

## Section A — State Model (§V.2)

| # | Check | Pass / Fail |
|---|-------|-------------|
| A1 | Component has two explicit states: `HEALTHY` and `DEGRADED` | |
| A2 | There is a single authoritative state holder (no duplicated flags or parallel booleans) | |
| A3 | No ad-hoc flags (`is_broken`, `disabled`, `failed_once`, etc.) bypass the official state | |
| A4 | State transitions are driven exclusively by the return value of `health_check()` | |
| A5 | No developer or user API can force the component to `HEALTHY` without a passing `health_check()` | |

**FAIL conditions (any one = PR blocked)**:
- Multiple competing flags represent health state
- A "force healthy" API exists that bypasses `health_check()`

---

## Section B — Entry into Degraded State (§V intro + §V.4)

| # | Check | Pass / Fail |
|---|-------|-------------|
| B1 | Initialization failure transitions component to `DEGRADED` | |
| B2 | `health_check()` returning `False` at runtime transitions `HEALTHY` → `DEGRADED` | |
| B3 | The `degraded_fallback` callable is invoked when degradation occurs | |
| B4 | The component remains visible in the UI after entering degraded state (MUST NOT be hidden or removed) | |
| B5 | Reduced functionality in degraded mode is documented in the tool's implementation docs (`TODO(GUARDIAN_DEGRADED_UX)` resolved or tracked) | |

---

## Section C — Recovery from Degraded State (§V.1, §V.2, §V.3)

| # | Check | Pass / Fail |
|---|-------|-------------|
| C1 | Component is eligible to recover at runtime (degraded state is not treated as permanent) | |
| C2 | Recovery is triggered automatically when `health_check()` returns `True` | |
| C3 | No developer action, user action, or external trigger is required for recovery | |
| C4 | Upon recovery, the component resumes normal operation immediately | |
| C5 | All degraded-state visual or functional indicators are cleared on recovery | |
| C6 | The component re-enters the regular health-check polling cycle after recovery | |
| C7 | No "sticky degraded" logic persists after a successful recovery transition | |

**FAIL conditions (any one = PR blocked)**:
- Recovery requires a developer call or application restart as its only path
- Degraded indicators persist after `health_check()` has returned `True`
- Component remains in a reduced-functionality mode despite returning to healthy state

---

## Section D — Logging Requirements (§V.4)

### D1 — Degradation log entry

| # | Field | Present |
|---|-------|---------|
| D1a | `timestamp` | |
| D1b | `component_id` | |
| D1c | `from_state` = `"healthy"` or `"initializing"` | |
| D1d | `to_state` = `"degraded"` | |
| D1e | `reason` (e.g., `"initialization failure"` or `"health_check() returned False"`) | |

### D2 — Recovery log entry

| # | Field | Present |
|---|-------|---------|
| D2a | `timestamp` | |
| D2b | `component_id` | |
| D2c | `from_state` = `"degraded"` | |
| D2d | `to_state` = `"healthy"` | |
| D2e | `reason` (e.g., `"health_check() returned True"`) | |

### D3 — Log format

| # | Check | Pass / Fail |
|---|-------|-------------|
| D3a | Log entries are structured (JSON/field-based), parseable by the §III structured logging system | |
| D3b | Raw exception stack traces are NOT the sole log artifact for a degradation event | |
| D3c | Full component state is NOT leaked into logs (no internal secrets, no raw widget refs) | |

**FAIL conditions (any one = PR blocked)**:
- Either transition (degradation or recovery) produces no log entry
- Log entry is missing any of the five required fields
- Log is unstructured and cannot be filtered/parsed by the logging system

---

## Section E — Test Coverage (§V.5)

The following test scenarios MUST each be covered by at least one automated
unit test:

| # | Test Scenario | Tests Present | CI Passes |
|---|---------------|---------------|-----------|
| E1 | Initialization failure → component enters `DEGRADED` + degradation log emitted | | |
| E2 | `health_check()` returns `False` from `HEALTHY` → transitions to `DEGRADED` + log emitted | | |
| E3 | `health_check()` returns `True` from `DEGRADED` → transitions to `HEALTHY` + recovery log emitted | | |
| E4 | After recovery, component operates in normal (non-degraded) mode (no sticky degraded behaviour) | | |
| E5 | *(Negative)* Attempt to force `HEALTHY` without passing `health_check()` is impossible or rejected | | |
| E6 | *(Negative)* State transition occurs without a structured log entry → test MUST fail | | |

**FAIL conditions (any one = PR blocked)**:
- Any of E1–E4 has no test coverage
- Any test is skipped, disabled, or marked `TODO`
- E6 negative test missing (silent transitions must be caught)

---

## Section F — CI Enforcement Gates

| # | CI Check | Gate Failure Condition |
|---|----------|------------------------|
| F1 | Transition test coverage | Any of E1–E4 scenarios missing for any registered component |
| F2 | Log field validation | Degradation or recovery log entry missing any required field (§V.4) |
| F3 | State machine contract test | Any path exists where `DEGRADED → HEALTHY` transition occurs without `health_check() == True` |
| F4 | Force-healthy test | Forcing `HEALTHY` without `health_check()` is possible (F5 negative test fails) |
| F5 | Sticky-degraded test | Component remains in degraded mode after `health_check()` returns `True` (E4 test fails) |

---

## Section G — Cross-References

| Reference | Location | Notes |
|-----------|----------|-------|
| §V — Simplicity & Extensible Modularity | constitution.md §V | Main ComponentGuardian requirement |
| §V.1 — Recovery Eligibility | constitution.md §V.1 | Degraded is not permanent |
| §V.2 — Recovery Trigger | constitution.md §V.2 | `health_check()` drives all transitions |
| §V.3 — Recovery Behavior | constitution.md §V.3 | Resume, clear indicators, re-enter polling |
| §V.4 — Recovery Logging | constitution.md §V.4 | Five required fields per transition direction |
| §V.5 — Deterministic Reviewability | constitution.md §V.5 | Unit-testable + CI-enforceable requirement |
| §V.6 — Health-Check Polling Interval | constitution.md §V.6 | 500 ms–5 s constitutional bounds |
| §V.6.1 — Minimum frequency (5 s) | constitution.md §V.6.1 | |
| §V.6.2 — Maximum frequency (500 ms) | constitution.md §V.6.2 | |
| §V.6.5 — TODO(GUARDIAN_POLL_INTERVAL) closed | constitution.md §V.6.5 | Resolved in Q6 |
| TODO(GUARDIAN_DEGRADED_UX) | constitution.md | Per-tool reduced-functionality UX — still open |
| docs/component-guardian-spec.md | docs/ | State machine diagram, CI test spec, migration patch, polling reference |
| §III — logging requirement | constitution.md §III | Structured, levelled, machine-parsable logs |

---

## Section H — Polling Interval Compliance (§V.6)

Apply this section to any PR that introduces or modifies polling logic for a
`ComponentGuardian`-managed component.

### H1 — Interval Bound Compliance

| # | Check | Pass / Fail |
|---|-------|-------------|
| H1a | `health_check()` is invoked at least once every 5 seconds during active use (§V.6.1) | |
| H1b | `health_check()` is NOT invoked more frequently than once every 500 ms (§V.6.2) | |
| H1c | The effective polling interval stays within [500 ms, 5 s] at all times | |

**FAIL conditions (any one = PR blocked)**:
- Effective interval > 5 s during active use
- Effective interval < 500 ms (tight loop / CPU churn)

### H2 — Deterministic Scheduling (§V.6.3)

| # | Check | Pass / Fail |
|---|-------|-------------|
| H2a | Polling interval is explicitly defined (constant, configurable value, or scheduler parameter) | |
| H2b | If jitter, backoff, or adaptive strategy is used: the implementation guarantees the result stays within [500 ms, 5 s] | |
| H2c | Polling interval is NOT derived from unbounded user input or unbounded configuration | |

### H3 — Observability (§V.6.4)

| # | Check | Pass / Fail |
|---|-------|-------------|
| H3a | Each poll is observable via structured logs or metrics | |
| H3b | State transitions caused by polling are logged per §V.4 (degrade / recover entries) | |

### H4 — Polling Testability (§V.6.4)

| # | Test Scenario | Tests Present | CI Passes |
|---|--------------|---------------|-----------|
| H4a | Effective interval between polls never exceeds 5 s (mock timer / virtual clock) | | |
| H4b | Effective interval between polls never falls below 500 ms (mock timer / virtual clock) | | |
| H4c | If jitter/backoff used: no sampled interval violates either bound under load | | |
| H4d | Degrade/recover transitions are triggered by polling (not by external events) | | |

**FAIL conditions (any one = PR blocked)**:
- No polling interval tests exist
- Tests do not use mock timers or an equivalent deterministic approach

### H5 — CI Polling Gates

| # | CI Check | Gate Failure Condition |
|---|----------|------------------------|
| H5a | Static scan: hardcoded interval outside [500 ms, 5 s] | Build fails |
| H5b | Static scan: polling loop with no sleep/delay | Build fails |
| H5c | Unit test: max-interval bound (H4a) | Build fails if absent or failing |
| H5d | Unit test: min-interval bound (H4b) | Build fails if absent or failing |
| H5e | Unit test: jitter/backoff within bounds (H4c, if applicable) | Build fails if applicable and absent |

---

## Reviewer Sign-Off

| Reviewer | Role | Date | Signature |
|----------|------|------|-----------|
| | | | |
| | | | |

**PR MUST NOT merge if any FAIL condition in Sections A–E or Section H is unresolved.**
