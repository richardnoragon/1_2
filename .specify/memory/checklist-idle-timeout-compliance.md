# Reviewer Checklist — Idle Timeout Compliance
<!-- Version: 1.0 | Constitution: v1.24.0 | §VII.Z, §G.11 | Q11 Applied -->

Confirm each item before marking an idle-timeout implementation as
constitutionally compliant. All items marked **MUST** are mandatory; failure
on any MUST item is a compliance block.

---

## A. Role-Differentiated Defaults (§VII.Z.2, §G.11)

| # | Check | Status |
|---|-------|--------|
| A1 | `admin` default is exactly **10 minutes** | ☐ |
| A2 | `dev` default is exactly **15 minutes** | ☐ |
| A3 | `user` default is exactly **30 minutes** | ☐ |
| A4 | `readonly` default is exactly **45 minutes** | ☐ |
| A5 | All four defaults are stored as **distinct per-role constants** (not a single shared constant) | ☐ |
| A6 | Privilege ordering is preserved: `admin` ≤ `dev` ≤ `user` ≤ `readonly` (in minutes) | ☐ |

**Fail if**:
- Any role default does not match §G.11
- A single global constant is applied to all roles
- `admin` or `dev` has a longer default than `user` or `readonly`

---

## B. 60-Minute Ceiling (§VII.Z.3)

| # | Check | Status |
|---|-------|--------|
| B1 | No per-role default exceeds 60 minutes without an explicit override flag | ☐ |
| B2 | The `is_explicit_override` guard (or equivalent) is required for any value > 60 min | ☐ |
| B3 | Attempting to set > 60 min without the explicit flag raises an error | ☐ |
| B4 | Values > 60 min (when override is used) are still ≤ the 8-hour absolute system ceiling | ☐ |

**Fail if**: Any role's timeout can be silently set > 60 minutes without an override flag.

---

## C. Administrative Overrides (§VII.Z.4)

| # | Check | Status |
|---|-------|--------|
| C1 | Admin can configure per-role timeout (not just a single global value) | ☐ |
| C2 | All overrides emit an audit-log entry | ☐ |
| C3 | Audit entry includes: actor, role affected, previous value, new value, timestamp | ☐ |
| C4 | If an admin minimum floor is set, users cannot configure below it | ☐ |
| C5 | Override mechanism is not accessible to non-admin roles | ☐ |

**Fail if**: C2 or C3 fails — unlogged overrides are a constitutional compliance block.

---

## D. Session Watchdog and Enforcement (§VII Session Controls, §VII.Z.1)

| # | Check | Status |
|---|-------|--------|
| D1 | Idle time is measured from **last activity**, not from login time | ☐ |
| D2 | Any user input or qualifying API call resets the idle timer | ☐ |
| D3 | Watchdog is unit-testable in isolation with injected time | ☐ |
| D4 | Watchdog forces logout or session lock on timeout | ☐ |
| D5 | A warning is shown ≥ 60 seconds before expiry | ☐ |
| D6 | Warning gives the user the opportunity to extend the session | ☐ |

**Fail if**: D1, D3, or D4 fails.

---

## E. Test Coverage (§VII.Z.5)

| # | Check | Test ID |
|---|-------|---------|
| E1 | admin default = 10 min | T1 |
| E2 | dev default = 15 min | T2 |
| E3 | user default = 30 min | T3 |
| E4 | readonly default = 45 min | T4 |
| E5 | 60-min ceiling enforced without flag | T5 |
| E6 | Explicit override allows > 60 min | T6 |
| E7 | Watchdog expires correctly | T7 |
| E8 | Watchdog resets on activity | T8 |
| E9 | Warning fires at ≤ 60 s remaining | T9 |
| E10 | Admin override is logged | T10 |

**Fail if**: Any T1–T4 test is absent or failing. Absence of T5–T10 is a compliance block for production-class implementations.

---

## Cross-References

| Document | Section |
|----------|---------|
| constitution.md §G.11 | Role-differentiated idle timeout defaults (normative) |
| constitution.md §VII.Z | Idle Timeout Requirements (§VII.Z.1–§VII.Z.5) |
| constitution.md §VII Session Controls | Session Controls (parent section) |
| docs/idle-timeout-spec.md | Canonical spec, reference implementation, CI tests |
