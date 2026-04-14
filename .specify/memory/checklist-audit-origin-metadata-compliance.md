# Audit Log Origin Metadata — Compliance Checklist

**Constitutional authority**: §16.X.1–§16.X.7  
**Canonical spec**: docs/audit-origin-metadata-spec.md  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.27.0)  
**Last updated**: 2026-04-05  

Reviewers MUST verify all items before approving any PR that modifies audit
logging, session management, authentication flows, or any code path that
emits audit events.

---

## Section A — Minimum Origin Metadata: All Events (§16.X.2)

- [ ] A.1  Every audit event includes `actor_username` in the `origin` block
- [ ] A.2  Every audit event includes `session_id` in the `origin` block
- [ ] A.3  Every audit event includes `device_id` in the `origin` block (pseudonymized — not raw hardware identifier)
- [ ] A.4  Every audit event includes `app_instance_id` in the `origin` block
- [ ] A.5  Background and scheduled tasks use `"system"` as a synthetic `session_id` (not null, not empty)
- [ ] A.6  Headless HMAC token events (§II.5.5) include all four core fields
- [ ] A.7  Break-glass login and rotation events (§18) include all four core fields
- [ ] A.8  `is_protected` blocked-operation events (§DW17.X.5) include all four core fields
- [ ] A.9  CI test T1 (all events include minimum metadata) passes

---

## Section B — Network-Originating Events (§16.X.3)

- [ ] B.1  Network-originating events include `client_ip_hash` (pseudonymized)
- [ ] B.2  Network-originating events include `user_agent` (raw string)
- [ ] B.3  Network-originating events include `protocol` (e.g., `"https"`, `"ssh"`)
- [ ] B.4  Non-network events (background tasks, local operations) do NOT include `client_ip_hash`, `user_agent`, or `protocol`
- [ ] B.5  `client_ip_hash` is a hash output, not a raw IP address
- [ ] B.6  CI test T2 (network events include network metadata) passes
- [ ] B.7  CI test T6 (non-network events omit network fields) passes

---

## Section C — Privacy and GDPR Compliance (§16.X.4)

- [ ] C.1  Raw IP addresses are **absent** from all audit log entries
- [ ] C.2  Hostnames are **absent** from all audit log entries
- [ ] C.3  OS-level usernames are **absent** from all audit log entries
- [ ] C.4  Hardware serial numbers are **absent** from all audit log entries
- [ ] C.5  No unique device identifier beyond a pseudonymized `device_id` is logged
- [ ] C.6  `client_ip_hash` is produced by a keyed, one-way hash (HMAC-SHA-256 or equivalent)
- [ ] C.7  `device_id` is produced by a keyed, one-way hash — raw device identifiers are not stored
- [ ] C.8  The pseudonymization key is stored in a secret store, **not** in source code or config files
- [ ] C.9  CI test T3 (pseudonymization applied — hash ≠ raw input) passes
- [ ] C.10 CI test T4 (raw IP not in log output) passes
- [ ] C.11 CI test T5 (prohibited fields absent from origin block) passes

---

## Section D — Field Consistency (§16.X.5)

- [ ] D.1  `actor_username` uses exactly this name in all modules (no aliases such as `actor_user`, `username`, or `user`)
- [ ] D.2  `session_id` uses exactly this name in all modules
- [ ] D.3  `device_id` uses exactly this name in all modules
- [ ] D.4  `app_instance_id` uses exactly this name in all modules
- [ ] D.5  `client_ip_hash` uses exactly this name in all modules (not `ip_hash`, `hashed_ip`, etc.)
- [ ] D.6  All timestamp fields are ISO 8601 UTC
- [ ] D.7  All ID fields (session_id, device_id, app_instance_id) are consistently typed (UUID v4 string or documented opaque string)
- [ ] D.8  The `origin` block is at the same structural level in all event shapes (not nested differently per module)
- [ ] D.9  CI test T7 (field names consistent across event types) passes

---

## Section E — Pseudonymization Behaviour (§16.X.4)

- [ ] E.1  Pseudonymization is **deterministic** — the same raw value always produces the same hash within a deployment
- [ ] E.2  Pseudonymization is **stable across restarts** — key is loaded from a persistent secret store, not regenerated on startup
- [ ] E.3  Pseudonymization uses a **keyed** algorithm (HMAC-SHA-256 recommended)
- [ ] E.4  CI test T9 (same input → same hash) passes
- [ ] E.5  The pseudonymization helper function is covered by unit tests

---

## Section F — Test Coverage and CI Gate (§16.X.6)

- [ ] F.1  CI tests T1–T9 (as defined in docs/audit-origin-metadata-spec.md §7) are implemented and passing
- [ ] F.2  CI pipeline includes tests T1–T9 as a **required gate** (not optional or skippable)
- [ ] F.3  Tests cover all event types listed in Section A of this checklist (login, logout, reset, unblock, HMAC token, break-glass, is_protected violations)
- [ ] F.4  Static analysis or linting rules flag any direct logging of raw IP addresses or hostnames
- [ ] F.5  Test coverage for the `build_origin_metadata` helper function ≥ 90%
- [ ] F.6  No existing test suite has been weakened or removed to accommodate origin metadata changes

---

## Notes

- For existing audit records logged before v1.27.0: the backward-compatibility clause (§16.X.7) permits omission. Do **not** fail historical record validation on these items.
- For any audit event not explicitly listed in Section A: apply the minimum four-field requirement by default.
- If a field cannot be populated (e.g., `app_instance_id` during standalone test runs), document the exception and use a well-known sentinel value (e.g., `"test"`) rather than `null` or empty string.

---

## Cross-References

| Reference | Location |
|-----------|----------|
| Canonical spec | docs/audit-origin-metadata-spec.md |
| Constitutional authority | §16.X.1–§16.X.7 (.specify/memory/constitution.md) |
| Q14 answer | .specify/memory/constitution_clairification_uiux_harmonny_r8.md |
| is_protected checklist | .specify/memory/checklist-is-protected-compliance.md |
| HMAC token checklist | .specify/memory/checklist-hmac-token-compliance.md |
| TOTP compliance checklist | .specify/memory/checklist-totp-compliance.md |
