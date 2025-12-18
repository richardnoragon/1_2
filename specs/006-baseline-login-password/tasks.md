# Tasks: Login & Password Baseline Integration

**Input**: `specs/006-baseline-login-password/plan.md` + supporting artifacts
**Motto**: _"Better many smaller, detailed tasks than fewer large complex ones."_

## Phase 3.1 – Setup & Tooling Hardening

- [x] T001 Update `requirements.txt` and `setup.cfg` to pin `argon2-cffi`, `cryptography`, and enable mypy/pytest plugins required by the identity plan.
- [x] T002 Author `scripts/migrations/006_baseline_login_password.sql` to create/alter `user_accounts`, `admin_action_audit`, `user_preferences`, `session_tokens`, `reset_requests`, and `pending_preference_alerts` tables with required indices.
- [x] T003 [P] Create `tests/fixtures/identity_fixtures.py` helper to seed pending users, blocked users, and sample preference payloads for upcoming contract/integration tests.

## Phase 3.2 – Tests First (TDD Gate)

### Contract Tests from `contracts/authentication.yaml` & `contract-tests.md`

- [x] T004 [P] Scaffold failing contract test `tests/contracts/identity/test_login_success.py` covering POST `/auth/login` happy-path payload and response schema.
- [x] T005 [P] Scaffold failing contract test `tests/contracts/identity/test_login_lockout.py` to assert 5th failure blocks account and emits audit entry.
- [x] T006 [P] Scaffold failing contract test `tests/contracts/identity/test_logout_revokes_token.py` for DELETE `/auth/login` session invalidation semantics.
- [x] T007 [P] Scaffold failing contract test `tests/contracts/identity/test_admin_approve_user.py` mirroring `/admin/users` POST approval flow requirements.
- [x] T008 [P] Scaffold failing contract test `tests/contracts/identity/test_admin_reset_password.py` verifying temporary password + audit log contract from `/admin/users` PATCH reset.
- [x] T009 [P] Scaffold failing contract test `tests/contracts/identity/test_preferences_share_guard.py` for `/preferences/share` export guard scenarios.

### Integration Tests from `quickstart.md`

- [x] T010 [P] Add integration test `tests/integration/identity/test_bootstrap_pending_user.py` that seeds admin + pending user via scripts and asserts DB state.
- [x] T011 [P] Add integration test `tests/integration/identity/test_cli_approval_flow.py` to drive `rfu-admin approve-user` and verify `preferences_id` assignment + audit.
- [x] T012 [P] Add GUI login integration test `tests/integration/gui/test_login_personalization.py` ensuring hub loads preference badge on success.
- [x] T013 [P] Add integration test `tests/integration/identity/test_lockout_guard.py` driving failed attempts script and asserting blocked state + audit entries.
- [x] T014 [P] Add integration test `tests/integration/identity/test_password_reset_terminates_sessions.py` validating forced logout after CLI reset.
- [x] T015 [P] Add integration test `tests/integration/identity/test_idle_timeout_watchdog.py` simulating >10 minute inactivity and expecting forced re-auth.
- [x] T016 [P] Add integration test `tests/integration/identity/test_preference_sharing_toggle.py` covering share flag off/on around export CLI.

### Validation & Sanitization Tests for FR-011

- [x] T017 [P] Add unit tests `tests/unit/auth/test_username_validation.py` enforcing minimum length, allowed characters, trimming, and injection guards.
- [x] T018 [P] Add unit tests `tests/unit/auth/test_password_policy.py` covering 12-char minimum, 3-class complexity, and breached-password denylist handling.
- [x] T019 Add integration test `tests/integration/identity/test_credential_validation_gate.py` ensuring both CLI (`rfu-admin`) and hub login reject invalid usernames/passwords before hitting AuthService.

### Role Enforcement Tests for FR-010

- [x] T020 [P] Add contract test `tests/contracts/identity/test_admin_role_requirements.py` asserting admin endpoints return 403 for `standard` role tokens.
- [x] T021 [P] Add integration test `tests/integration/identity/test_cli_admin_role_gate.py` ensuring `rfu-admin` commands reject non-admin operators and log the attempt.
- [x] T022 [P] Add GUI integration test `tests/integration/gui/test_admin_panel_role_gate.py` verifying the hub hides admin panel for standard users and blocks deep-link attempts.

### Self-Registration Coverage for FR-009

- [x] T023 [P] Add contract test `tests/contracts/identity/test_self_registration_pending.py` validating POST `/auth/register` queues accounts with `account_status=pending` and audit trail entries.
- [x] T024 [P] Add GUI integration test `tests/integration/gui/test_self_registration_flow.py` covering user entry, pending confirmation message, and admin approval dependency.
- [x] T025 [P] Add CLI integration test `tests/integration/cli/test_self_registration_cli.py` exercising a headless registration script that submits pending accounts and enforces validation errors.
- [x] T026 [P] Implement `src/core/auth/services/registration_service.py` handling input validation, initial Argon2 hashing, pending account creation, audit logging, and notification hooks.
- [x] T027 Add self-service CLI entrypoint `scripts/rfu_register.py` (or equivalent) that prompts for username/password/preferences, validates locally, and calls the registration endpoint.
- [x] T028 Update hub login dialog `src/rfu/login_dialog.py` to include a registration panel, duplicate-username messaging, and confirmation cues for pending status.
- [x] T029 Implement POST `/auth/register` handler in `src/core/auth/endpoints/auth_controller.py` delegating to `RegistrationService` and returning pending-state contract payloads.

## MFA Readiness Design & Migration (FR-013)

- [x] T030 [P] Author `specs/006-baseline-login-password/mfa-readiness.md` describing storage schema, CLI/GUI touchpoints, and phased rollout plan for optional MFA.
- [x] T031 Update `scripts/migrations/006_baseline_login_password.sql` to add reserved MFA columns/tables (`mfa_enabled`, `mfa_secret_encrypted`, `mfa_recovery_codes`, `mfa_enforced_at`) plus indexes and rollback guidance.
- [x] T032 [P] Add placeholder interfaces `src/core/auth/services/mfa_hook_service.py` and `src/core/auth/endpoints/mfa_placeholder_controller.py` that currently return `501` but lock in routing/contracts for future MFA providers.

## Phase 3.3 – Data Models

- [x] T033 [P] Implement `src/core/auth/models/user_account.py` dataclass/ORM helpers with status enum, timestamps, role metadata, MFA placeholders, pending registration metadata, and lockout counters aligned to `data-model.md`.
- [x] T034 [P] Implement `src/core/preferences/models/preference_profile.py` encapsulating schema version, metadata, and encryption flags.
- [x] T035 [P] Implement `src/core/auth/models/session_token.py` to capture issuance, idle tracking, and revocation state.
- [x] T036 [P] Implement `src/core/auth/models/reset_request.py` with encrypted temporary secret handling.
- [x] T037 [P] Implement `src/core/auth/models/admin_action_audit.py` capturing action metadata and CLI/GUI origin markers.
- [x] T038 [P] Implement `src/core/preferences/models/pending_preference_alert.py` for corruption detection lifecycle.

## Phase 3.4 – Data Access & Persistence

- [x] T039 [P] Build `src/core/auth/repositories/user_account_repository.py` for CRUD, lockout counter updates, role checks, pending registration transitions, and status updates with SQLite transactions.
- [x] T040 [P] Build `src/core/preferences/repositories/preference_profile_repository.py` handling load/save/encrypt operations for preference payloads.
- [x] T041 [P] Build `src/core/auth/repositories/session_store.py` for issuing, revoking, and enumerating `SessionToken` rows with idle timestamps.
- [x] T042 [P] Build `src/core/auth/repositories/reset_request_repository.py` for issuing, encrypting, and expiring reset tokens.
- [x] T043 [P] Build `src/core/auth/repositories/admin_action_audit_repository.py` for append-only logging and 12-month export hooks.
- [x] T044 [P] Build `src/core/preferences/repositories/pending_preference_alert_repository.py` for creating and resolving alerts on corruption.

## Phase 3.5 – Domain Services & Policies

- [x] T045 [P] Add Argon2id utility `src/core/auth/security/password_hasher.py` encapsulating research parameters and verification helpers.
- [x] T046 [P] Add lockout policy engine `src/core/auth/policies/lockout_policy.py` enforcing attempt thresholds + timestamp stamping.
- [x] T047 [P] Implement credential input validator `src/core/auth/policies/input_validator.py` covering username sanitization and password checks defined in FR-011.
- [x] T048 [P] Implement password denylist/complexity policy helper `src/core/auth/security/credential_rules.py` with breach data loader stubs.
- [x] T049 Implement `src/core/auth/services/auth_service.py` login workflow (credential validation, credential verify, lockout handling, session mint, preference linkage).
- [x] T050 Implement `src/core/auth/services/session_service.py` handling logout, session revocation, and idle updates.
- [x] T051 Implement `src/core/auth/services/admin_approval_service.py` for `/admin/users` POST transitions plus preference bootstrap and strict role checks.
- [x] T052 Implement `src/core/auth/services/admin_account_service.py` for reset/unblock actions including credential validation, role enforcement, temporary password generation, and audit logging.
- [x] T053 Implement `src/core/preferences/services/share_service.py` validating `share_preferences` flag, anonymizing payloads, and returning export bundle.
- [x] T054 Implement `src/core/auth/services/audit_logger.py` integrating repositories with structured log_manager outputs + CLI/GUI origin tags, then route CLI/GUI admin workflows, registration, and preference sharing through it.
- [x] T055 Implement idle timeout watchdog `src/core/auth/watchdogs/idle_timeout_watcher.py` that scans `SessionToken` rows every 60s and signals hub/CLI exits.
- [x] T056 Implement preference recovery service `src/core/preferences/services/preference_recovery_service.py` to auto-bootstrap defaults, raise alerts, and notify admins.
- [x] T057 Implement `src/core/auth/services/mfa_hook_service.py` no-op provider enforcing schema readiness, telemetry logging, and dependency injection points for future MFA engines.

## Phase 3.6 – Interfaces, Endpoints & UX Wiring

- [x] T058 Add CLI command `approve-user` to `scripts/admin/rfu_admin.py` calling `AdminApprovalService` with role + preference options.
- [x] T059 Add CLI command `reset-password` to `scripts/admin/rfu_admin.py` that enforces justification, requires explicit confirmation before showing the temporary secret, and routes delivery through the secure secret dispatcher (console render or encrypted note export).
- [x] T060 Add CLI command `unblock-user` to `scripts/admin/rfu_admin.py` clearing attempts + logging justification.
- [x] T061 Add CLI command `export-preferences` to `scripts/admin/rfu_admin.py` piping JSON to stdout/file with metadata envelope.
- [x] T062 Update hub login dialog `src/rfu/login_dialog.py` to invoke InputValidator before AuthService, handle lockout messaging, and capture idle heartbeat events.
- [x] T063 Add admin management panel `src/rfu/admin_panel.py` for pending approvals, resets, and unblock actions with validator-backed forms, explicit role gates, audit context prompts, and secure secret dispatcher integration for reset flows.
- [x] T064 Update preferences UI `src/rfu/preferences/preferences_view.py` to expose `share_preferences` toggle + metadata capture before exports.
- [x] T065 Implement POST `/auth/login` handler in `src/core/auth/endpoints/auth_controller.py` delegating to validator + AuthService and returning contract payload.
- [x] T066 Implement DELETE `/auth/login` handler in `src/core/auth/endpoints/auth_controller.py` for logout/session revocation.
- [x] T067 Implement POST `/admin/users` handler in `src/core/auth/endpoints/admin_users_controller.py` for approvals with role enforcement.
- [x] T068 Implement PATCH `/admin/users` handler in `src/core/auth/endpoints/admin_users_controller.py` covering reset/unblock actions with strict role enforcement.
- [x] T069 Implement POST `/preferences/share` handler in `src/core/preferences/endpoints/preferences_share_controller.py` delegating to `ShareService`.
- [x] T070 Wire idle timeout watcher into hub event loop via `src/rfu/hub.py` so GUI sessions auto-close and CLI receives exit codes.
- [x] T071 Add CLI audit export command `scripts/admin/rfu_admin.py` (sequential after T058–T061) leveraging `AdminActionAuditRepository` rollups.
- [x] T072 [P] Add placeholder CLI/REST wiring for MFA endpoints (e.g., `rfu-admin mfa-status`, `/auth/mfa/enroll`) that currently raise `NotImplementedError` but verify routing + permission enforcement.
- [x] T082 [P] Update `AuthController`, `AdminUsersController`, and `PreferencesShareController` to accept an injected `db_path`/dependency container so contract tests can pass isolated database copies; adjust hub + CLI wiring to propagate the parameter.
- [x] T083 Ensure logout + reset flows (SessionService, AdminAccountService, CLI + GUI endpoints) persist `revoked_at` timestamps and `enforced_password_change` flags exactly as asserted in the new contract suite.
- [x] T084 Ensure `scripts/admin/rfu_admin.py` exposes an `approve_user_cli(database_path, username, role, preferences_template)` callable returning an object with `exit_code` + `payload` so automation harnesses and `test_cli_approval_flow.py` can drive approvals without shelling out.
- [x] T085 Wire CLI approvals through `AdminApprovalService` so pending users flip to `account_status="active"`, receive `preferences_id`, stamp `activated_at`, and emit matching `user_preferences` rows exactly as required by `tests/integration/identity/test_cli_approval_flow.py`.
- [x] T086 Route CLI approvals through `AuditLogger`/`AdminActionAuditRepository` to record `action_type="approve_user"` entries with `origin_surface="cli"`, eliminating raw SQL writes in the CLI layer.
- [x] T087 Add a headless GUI helper `login_with_preferences(database_path, username, password)` in `src/identity/gui_login_flow.py` (or equivalent) so `tests/integration/gui/test_login_personalization.py` can drive hub logins without a live GUI. _(Implemented in `src/identity/gui_login_flow.py` and now invoked by `src/rfu/login_dialog.py`.)_
- [x] T088 Ensure `login_with_preferences` returns a DTO/mapping containing `status="authenticated"`, `workspace_ready=True`, and a `preference_snapshot` payload with both `preferences_id` and parsed layout/favorite data matching the integration test contract. _(Helper now hydrates snapshots from SQLite or fallback templates.)_
- [x] T089 Populate `preference_badge` metadata (user, `preferences_id`, layout label) when returning from `login_with_preferences` so the GUI can render the badge text asserted by the integration test. _(Badge consumed by the new hub login dialog to surface personalization.)_
- [x] T090 Add admin panel guard + launch helpers in `src/rfu/admin_panel.py` so GUI flows/tests can reuse consistent role gating before instantiating `AdminUsersController`.

## Phase 3.8 – Four-Role System & Lockout Prevention (007-upgrade-to-login)

> These tasks implement the lockout prevention features from spec 007-upgrade-to-login

### Role System Expansion

- [x] T091 [P] Update `src/core/auth/models/user_account.py` to expand role enum from `{admin, standard}` to `{dev, admin, user, readonly}` and add `is_always_available`, `is_break_glass`, `break_glass_justification`, and `auto_unblock_at` fields.
- [x] T092 [P] Create migration `scripts/migrations/007_lockout_prevention.sql` to add new columns, create `break_glass_usage_log`, `always_available_account_config`, and `admin_notification` tables, and migrate existing `standard` role to `user`.
- [x] T093 [P] Update `src/core/auth/policies/role_policy.py` to enforce four-role privilege hierarchy: `dev > admin > user > readonly`.
- [x] T094 [P] Add unit tests `tests/unit/auth/test_role_hierarchy.py` verifying role-based access control for all four roles.

### Always-Available Accounts

- [x] T095 [P] Implement `src/core/auth/models/always_available_account_config.py` dataclass for cooldown tracking and configuration.
- [x] T096 [P] Implement `src/core/auth/repositories/always_available_account_repository.py` for managing always-available account configuration.
- [x] T097 [P] Implement `src/core/auth/services/lockout_prevention_service.py` for protected account management, cooldown logic, and auto-unblock scheduling.
- [x] T098 [P] Update `src/core/auth/policies/lockout_policy.py` to use 15-minute cooldown auto-unblock for always-available accounts instead of permanent blocking.
- [x] T099 Add CLI command `bootstrap-protected-accounts` to `scripts/admin/rfu_admin.py` for initial setup of always-available and break-glass accounts with secure credential generation.
- [x] T100 [P] Add integration test `tests/integration/identity/test_always_available_cooldown.py` verifying automatic unblock after cooldown period.
- [x] T101 [P] Add contract test `tests/contracts/identity/test_always_available_protection.py` ensuring deletion/disable/permanent-block attempts are rejected and logged.

### Break-Glass Accounts

- [x] T102 [P] Implement `src/core/auth/models/break_glass_usage_log.py` dataclass for break-glass session tracking.
- [x] T103 [P] Implement `src/core/auth/repositories/break_glass_usage_log_repository.py` for break-glass usage logging and credential rotation status.
- [x] T104 [P] Implement `src/core/auth/services/break_glass_service.py` for break-glass login handling, justification capture, enhanced audit logging, and post-session credential rotation.
- [x] T105 [P] Implement `src/core/auth/services/admin_notification_service.py` for sending break-glass usage alerts and security incident notifications to administrators.
- [x] T106 Update `src/core/auth/services/auth_service.py` to detect break-glass login, invoke `BreakGlassService`, and mark session with `session_type='break_glass'`.
- [x] T107 Update `src/core/auth/services/session_service.py` to trigger credential rotation on break-glass session logout and update `BreakGlassUsageLog`.
- [x] T108 [P] Add integration test `tests/integration/identity/test_break_glass_workflow.py` covering login with justification, enhanced audit, logout rotation, and admin notification.
- [x] T109 [P] Add contract test `tests/contracts/identity/test_break_glass_justification.py` ensuring break-glass login requires justification and logs the stated reason.

### CLI & GUI Updates for Lockout Prevention

- [x] T110 Add CLI command `rotate-break-glass` to `scripts/admin/rfu_admin.py` for manual break-glass credential rotation with secure export.
- [x] T111 Add CLI command `list-protected-accounts` to `scripts/admin/rfu_admin.py` showing always-available and break-glass account status.
- [x] T112 Update hub login dialog `src/rfu/login_dialog.py` to prompt for justification when break-glass credentials are detected.
- [x] T113 Update admin panel `src/rfu/admin_panel.py` to show break-glass usage history and always-available account status (dev role only).
- [x] T114 [P] Add GUI integration test `tests/integration/gui/test_break_glass_justification_dialog.py` verifying justification prompt and logging.

### Lockout Prevention Verification

- [x] T115 [P] Add integration test `tests/integration/identity/test_lockout_prevention_guarantee.py` verifying system can never reach complete lockout state.
- [x] T116 [P] Add CLI integration test `tests/integration/cli/test_headless_recovery.py` verifying CLI recovery path works without GUI authentication.
- [x] T117 [P] Update documentation `docs/login_password_baseline.md` with lockout prevention features, four-role system, and break-glass procedures.

## Phase 3.7 – Polish, Quality, and Documentation

- [x] T073 [P] Add unit tests for hasher + password policy in `tests/unit/auth/test_password_hasher.py` ensuring Argon2 params enforced.
- [x] T074 [P] Add unit tests for lockout policy edge cases in `tests/unit/auth/test_lockout_policy.py`.
- [x] T075 [P] Add unit tests for preference recovery service in `tests/unit/preferences/test_preference_recovery.py`.
- [x] T076 [P] Add performance test `tests/performance/test_login_latency.py` asserting <250ms response on reference hardware.
- [x] T077 [P] Document new flows in `docs/login_password_baseline.md` plus update `quickstart.md` with CLI command references, including MFA readiness notes.
- [x] T078 [P] Add performance test `tests/performance/test_preference_load_latency.py` seeding ≥100 profiles and asserting hub preference load completes <1s on reference hardware; surface regression guidance in failure output.
- [x] T079 [P] Add performance test `tests/performance/test_audit_export_latency.py` generating a 30-day audit window and asserting CLI export (<2s) while validating JSON rollup structure.
- [x] T080 [P] Implement `src/core/auth/services/secure_secret_dispatcher.py` to encapsulate approved out-of-band delivery mechanisms (single-view console render and encrypted secure-note file) plus dispatch metadata persistence.
- [x] T081 [P] Add contract test `tests/contracts/identity/test_secure_reset_workflow.py` ensuring reset flows require justification, enforce administrator confirmation, and only expose temporary secrets via the dispatcher once per request while updating audit metadata.

---

## Dependencies & Ordering Notes

- Phase 3.1 (T001–T003) must complete before any tests.
- Contract tests (T004–T009, T023), integration tests (T010–T016, T024–T025), validation tests (T017–T019), role enforcement tests (T020–T022), self-registration scaffolding (T023–T029), and MFA readiness artifacts (T030–T032) must exist/fail before implementing models/services.
- Data models (T033–T038) unlock repositories (T039–T044); repositories are prerequisites for services (T045–T057).
- CLI/GUI/endpoint tasks (T058–T072) depend on services plus repositories and must respect validator + role/MFA/self-registration guard wiring notes.
- Polish tasks (T073–T077) run only after core implementation and integration tests pass.
- Tasks within the same file (e.g., T058–T061 in `scripts/admin/rfu_admin.py`, T062 + T063 in hub/admin UI, T065 + T066 in `auth_controller.py`) are sequential; do not mark them [P].

## Parallel Execution Examples

```text
# Example 1: Launch contract test scaffolding together once fixtures exist
/task run specs/006-baseline-login-password/tasks.md T004
/task run specs/006-baseline-login-password/tasks.md T005
/task run specs/006-baseline-login-password/tasks.md T006
/task run specs/006-baseline-login-password/tasks.md T007
/task run specs/006-baseline-login-password/tasks.md T008
/task run specs/006-baseline-login-password/tasks.md T009

# Example 2: Parallel model implementations after tests fail
/task run specs/006-baseline-login-password/tasks.md T033
/task run specs/006-baseline-login-password/tasks.md T034
/task run specs/006-baseline-login-password/tasks.md T035
/task run specs/006-baseline-login-password/tasks.md T036
/task run specs/006-baseline-login-password/tasks.md T037
/task run specs/006-baseline-login-password/tasks.md T038

# Example 3: Polish tasks in parallel right before release
/task run specs/006-baseline-login-password/tasks.md T073
/task run specs/006-baseline-login-password/tasks.md T074
/task run specs/006-baseline-login-password/tasks.md T075
/task run specs/006-baseline-login-password/tasks.md T076
/task run specs/006-baseline-login-password/tasks.md T077
```

Ensure each `/task run ...` command executes only when prerequisites listed above are complete.
