# MFA Readiness Blueprint (FR-013)

**Objective**: prepare the RFU identity stack for optional multi-factor authentication without activating end-user prompts yet. This document captures the storage extensions, interface hooks, and phased rollout needed so later work can focus on actual factor providers (TOTP, hardware keys, etc.).

## 1. Data & Storage Additions

| Component                 | Schema Change                                                              | Notes                                                                                                                     |
| ------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `user_accounts`           | `mfa_enabled INTEGER NOT NULL DEFAULT 0`                                   | Boolean-style guard that flips on once enrollment completes.                                                              |
|                           | `mfa_secret_encrypted BLOB NULL`                                           | Opaque, encrypted payload storing TOTP seeds or hardware binding material.                                                |
|                           | `mfa_recovery_codes TEXT NULL`                                             | JSON document maintained only until dedicated table backfill runs; keeps migration simple while bootstrap scripts evolve. |
|                           | `mfa_enforced_at TEXT NULL`                                                | ISO8601 timestamp showing when MFA became mandatory for the account.                                                      |
| `user_mfa_recovery_codes` | New table capturing `code_hash`, `issued_at`, `redeemed_at`, `revoked_at`. | Enables per-code tracking, revocation, and telemetry before actual factor enforcement launches.                           |

### Indexing & Constraints

- Index `user_mfa_recovery_codes (user_id, redeemed_at)` to quickly enumerate unused codes.
- Add partial index `user_accounts (mfa_enabled) WHERE mfa_enabled = 1` once SQLite version in CI supports it; for now, provide full index to keep tooling simple.
- Foreign keys stay aligned with existing `user_accounts(username)` primary key.

### Rollback Guidance

- Dropping the columns is safe while MFA remains disabled. Documented `DOWN` section truncates and removes the table, then strips columns via `ALTER TABLE ... RENAME TO` pattern to keep SQLite happy.
- Because encrypted secrets never leave the DB, ensure rollback scripts also shred `.bak` copies produced by migration tooling.

## 2. CLI / GUI Touchpoints

| Surface           | Experience Goals                                                                                                                                                                                      | Instrumentation                                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `rfu-admin` CLI   | Add `mfa-status`, `mfa-reset`, `mfa-issue-recovery` commands (T072). For FR-013 we only need stubs that return `501` so automation can verify routing.                                                | Commands log via `AuditLogger` once implemented. For now we emit structured warnings so ops know MFA is not yet active.           |
| Hub GUI           | Add a "Security" card under settings with disabled MFA toggle plus copy explaining upcoming rollout. Dialog calls the placeholder controller so tests can assert HTTP `501` until the provider lands. | Telemetry hooks via `log_manager` so we know how often users explore the feature pre-launch.                                      |
| Registration Flow | No change for FR-013; accounts remain pending until admin approval, and `mfa_enabled` defaults to `0`. Future phases will allow admins to require MFA before approval completes.                      | `RegistrationService` now captures `origin_surface`; when we eventually auto-enroll MFA, we already know which surface to notify. |

## 3. Phased Rollout

1. **Phase A – Schema Only (current tasks)**
   - Land columns/table + placeholder services/controllers (T030–T032).
   - Update migrations and documentation so downstream teams can branch from consistent schema.
2. **Phase B – Preview Hooks**
   - Wire CLI + GUI toggles to the placeholder service.
   - Admin preview flag stored in config enables hidden commands for validation engineers.
   - No user-facing enforcement yet; responses remain `501` but include `retry_after` hints.
3. **Phase C – Provider Enablement**
   - Implement `MFAHookService` to wrap provider SDKs (TOTP initially) and integrate with `AuthService` challenge pipeline.
   - Add enrollment + verification APIs plus CLI automation for break-glass recovery.
4. **Phase D – Enforcement & Telemetry**
   - Flip `mfa_enabled` for selected cohorts, require challenge during login.
   - Populate `mfa_enforced_at`, track recovery code usage, and emit alerts when codes run low.

## 4. Testing & Validation Strategy

- Migration smoke test: extend `tests/fixtures/identity_fixtures.py` to confirm new columns exist.
- Contract placeholder tests: augment `contracts/authentication.yaml` with `/auth/mfa/*` routes returning `501` so future suites already know the endpoints.
- CLI regression: add `pytest.mark.cli` tests ensuring `rfu-admin mfa-status` exits with code `78` (`EX_CONFIG`) until implementation arrives.
- GUI regression: simple Qt harness ensures clicking the disabled MFA toggle describes the phased rollout (copy supplied by Product). This will be part of Phase B tasks.

## 5. Open Questions / Follow-ups

1. **Secret Storage Backend** – final design may move long-term secrets to DPAPI or macOS Keychain for parity with CLI credentials. Track under T080 once secure dispatcher lands.
2. **Recovery Code Printing** – need UX spec for console vs. file export. Document in `docs/login_password_baseline.md` during polish phase (T077).
3. **Telemetry Budget** – confirm logging volume with the Observability team so hook service does not overwhelm current pipeline.

With this blueprint committed, subsequent tasks (T031–T032, T072, T080) have a stable reference for schema names, API placeholders, and rollout checkpoints.
