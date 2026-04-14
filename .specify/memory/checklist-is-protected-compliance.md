# is_protected Compliance Checklist

**Constitutional authority**: §G.12, §DW §17.X.1–§DW17.X.6  
**Canonical spec**: docs/is-protected-spec.md  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.25.0)  
**Last updated**: 2026-04-04  

Reviewers MUST verify all items before approving any PR that modifies account
management, user service, authentication, or database schema related to user
records.

---

## Section A — Password Reset Protection (§DW17.X.2)

- [ ] A.1  Admin-initiated password reset on a protected account raises `protected_account_error` (does NOT silently succeed or silently fail)
- [ ] A.2  API-initiated (programmatic) password reset on a protected account raises `protected_account_error`
- [ ] A.3  Automated system (e.g., password-rotation job) initiating a reset on a protected account raises `protected_account_error`
- [ ] A.4  Self-service password change by the account owner **succeeds** (no error raised, no blocked-operation audit entry emitted)
- [ ] A.5  CI test T1 (admin reset blocked) passes
- [ ] A.6  CI test T2 (self-service allowed) passes

---

## Section B — Role Change Protection (§DW17.X.3)

- [ ] B.1  Admin-initiated role demotion on a protected account raises `protected_account_error`
- [ ] B.2  Admin-initiated role escalation on a protected account raises `protected_account_error`
- [ ] B.3  Role change via migration script on a protected account raises `protected_account_error` at service layer (or migration is documented as a break-glass exception with audit trail)
- [ ] B.4  No code path allows role mutation on a protected account without triggering the guard function
- [ ] B.5  CI test T3 (role demotion blocked) passes
- [ ] B.6  CI test T4 (role escalation blocked) passes

---

## Section C — Username Protection (§DW17.X.4)

- [ ] C.1  Admin-initiated username change on a protected account raises `protected_account_error`
- [ ] C.2  API username-change endpoint rejects requests targeting a protected account
- [ ] C.3  Database-level constraint or trigger rejects username changes for `is_protected = TRUE` rows (recommended; mark N/A with justification if not implemented)
- [ ] C.4  The fixed usernames `admin` and `dev` are not reassignable via any application flow
- [ ] C.5  CI test T5 (username change blocked) passes

---

## Section D — Deletion, Deactivation, and Suspension (§DW17.X.1, §G.12)

- [ ] D.1  Deletion of a protected account raises `protected_account_error` in the service layer
- [ ] D.2  Deactivation of a protected account raises `protected_account_error`
- [ ] D.3  Suspension of a protected account raises `protected_account_error`
- [ ] D.4  Database DELETE on a protected account row is rejected by DB constraint or trigger (recommended; mark N/A with justification if not implemented)
- [ ] D.5  CI test T6 (deletion blocked) passes
- [ ] D.6  CI test T7 (deactivation blocked) passes
- [ ] D.7  CI test T8 (suspension blocked) passes

---

## Section E — Logging and Auditability (§DW17.X.5)

- [ ] E.1  Every blocked operation (all six) emits a structured audit-log entry
- [ ] E.2  Audit-log entry contains `actor` field (UUID or system ID of the attempter)
- [ ] E.3  Audit-log entry contains `target` field (UUID of the protected account)
- [ ] E.4  Audit-log entry contains `operation` field (one of: `delete`, `deactivate`, `suspend`, `password_reset`, `role_change`, `username_change`)
- [ ] E.5  Audit-log entry contains `reason` field (literal: `"protected_account_violation"`)
- [ ] E.6  Audit-log entry contains `timestamp` field (ISO 8601 UTC)
- [ ] E.7  No blocked operation silently succeeds or silently fails (audit entry exists for each)
- [ ] E.8  CI test T9 (all five audit-log fields present for each blocked operation) passes

---

## Section F — Test Coverage and CI Gate

- [ ] F.1  Tests T1–T9 (as defined in docs/is-protected-spec.md §7) are implemented and passing
- [ ] F.2  CI pipeline includes tests T1–T9 as a required gate (not optional/skippable)
- [ ] F.3  No bypass path exists in internal APIs or migration tooling that omits the `check_protected()` guard:
  - [ ] F.3.1  User-deletion service function calls `check_protected()`
  - [ ] F.3.2  User-deactivation service function calls `check_protected()`
  - [ ] F.3.3  User-suspension service function calls `check_protected()`
  - [ ] F.3.4  Password-reset service function calls `check_protected()` with `self_service` flag correctly set
  - [ ] F.3.5  Role-change service function calls `check_protected()`
  - [ ] F.3.6  Username-change service function calls `check_protected()`
- [ ] F.4  Self-service path sets `self_service=True` (and only the owner's own session triggers it)
- [ ] F.5  Reviewer has read docs/is-protected-spec.md Section 6 (reference implementation) and confirmed `check_protected()` is called before any DB write in all six paths

---

## Reviewer Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Security reviewer | | | |
| Architecture reviewer | | | |

---

## Cross-References

- [Constitution §G.12](../constitution.md) — Normative glossary entry: is_protected scope
- [Constitution §DW17.X](../constitution.md) — Six subsections prescribing full is_protected scope
- [docs/is-protected-spec.md](../../docs/is-protected-spec.md) — Canonical spec, reference implementation, CI tests, migration plan
- [checklist-totp-compliance.md](checklist-totp-compliance.md) — TOTP compliance checklist
- [checklist-fido2-compliance.md](checklist-fido2-compliance.md) — FIDO2 compliance checklist
- [checklist-idle-timeout-compliance.md](checklist-idle-timeout-compliance.md) — Idle timeout compliance checklist
