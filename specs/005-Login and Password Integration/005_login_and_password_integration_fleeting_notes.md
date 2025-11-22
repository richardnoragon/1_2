# I. Introduction

The puropose of this file is to maintain a temporary checkpoint log which
tracks all prerequisite items, dependencies, and action items which
must be completed before advancing to the next sequential step
in the tasks.md workflow, ensuring no critical requirements
are overlooked and maintaining clear progress visibility
throughout the task execution process.

---

## 🧩 Outline: Login and Password Integration for File Utilities

### 1. 🔐 Authentication Module

#### 1.1 User Account Structure

- `username`: unique identifier
- `password_hash`: securely hashed password (e.g., bcrypt or Argon2)
- `login_attempts`: counter for failed login attempts
- `is_blocked`: boolean flag if login attempts exceed threshold
- `preferences_id`: reference to associated preferences JSON

#### 1.2 Password Handling

- Hash on creation/reset using a secure algorithm
- Never store plaintext passwords
- No password recovery — only reset by admin
- Admin reset generates a temporary password or triggers user-defined reset flow

#### 1.3 Login Flow

- Validate credentials against stored hash
- Increment `login_attempts` on failure
- Block account after 5 failed attempts (`is_blocked = True`)
- Reset `login_attempts` on successful login

---

### 2. 🧭 Preferences Coupling

#### 2.1 Preferences JSON Schema

- Stored per user, keyed by `preferences_id`
- Includes:
  - UI settings
  - File normalization options
  - Sharing preferences
  - Feature toggles

#### 2.2 Sharing Logic

- `share_preferences`: boolean flag
- If `True`, allow exporting preferences JSON (excluding login credentials)
- Shared preferences are anonymized or pseudonymized
- Include metadata like `shared_by`, `timestamp`, `purpose`

---

### 3. 🛠 Admin Capabilities

#### 3.1 Reset Password

- Triggered via admin interface or CLI
- Generates new hash, replaces old one
- Logs reset event with timestamp and admin ID
- Does not expose password or hash to admin

#### 3.2 Unblock Account

- Reset `login_attempts` and `is_blocked` flags
- Optional audit trail for unblock actions

---

### 4. 🧪 Security and Governance

#### 4.1 Storage and Access

- Store user data in a secure JSON or DB file with access control
- Encrypt sensitive fields at rest (e.g., password hash, preferences if needed)

#### 4.2 Audit and Logging

- Log login attempts, resets, blocks, and sharing actions
- Include timestamps and actor IDs (user/admin)

#### 4.3 Extensibility

- Modular login module (e.g., `auth.py`) with clear separation from preferences logic
- Future support for OAuth or token-based login
- Optional MFA integration

---

## 🧠 Additional Considerations

### 1. 🔄 **Password Reset Flow for Users (Optional)**

- While admin resets are covered, consider a user-initiated reset mechanism:
  - Use a temporary token or challenge question (if offline)
  - Or allow CLI-based reset with a one-time code (if online)
- Log all reset attempts for auditability

### 2. 🧾 **User Registration Flow**

- Define how new users are added:
  - Admin-created only?
  - Self-registration with approval?
- Ensure password is hashed immediately upon creation

### 3. 🧱 **Role-Based Access Control (RBAC)**

- Define roles: e.g., `admin`, `user`, `readonly`
- Restrict access to certain utilities or preferences based on role
- Store role in user account JSON

### 4. 🧼 **Input Validation and Sanitization**

- Sanitize usernames and passwords to prevent injection or malformed data
- Enforce username/password complexity rules (e.g., min length, character types)

### 5. 🧳 **Session Management**

- If the utilities are long-running or interactive:
  - Track login sessions with expiration
  - Store session tokens in memory or temp file
  - Allow logout or session timeout

### 6. 🧩 **Modular Integration**

- Keep `auth.py` separate from `preferences.py`
- Use dependency injection or a shared context object to link user identity to preferences
- Ensure preferences access is gated by successful authentication

### 7. 🧪 **Testing and Recovery**

- Include test cases for:
  - Login success/failure
  - Account blocking
  - Admin reset
  - Preference sharing
- Provide a recovery CLI or script in case of lockout or corrupted user store

### 8. 📁 **Data Storage Format**

- Consider splitting:
  - `users.json` → login credentials, metadata
  - `preferences/{username}.json` → user preferences
- This separation improves modularity and avoids accidental exposure

---

## 🔄 2025-11-15 Contract Scaffolding Follow-Ups

- [x] Define the `AuthController`, `AdminUsersController`, and `PreferencesShareController` constructors to accept a `db_path` (or dependency container) so the contract database copies used in tests can inject isolation explicitly. _(Tracked via `specs/006-baseline-login-password/tasks.md` task T082.)_
- [x] When implementing logout + reset flows, persist `revoked_at` timestamps and `enforced_password_change` flags exactly as asserted in the new contract suite to avoid interpretation drift between CLI/UI surfaces. _(Tracked via task T083.)_

### 2025-11-16 CLI Approval Flow Notes

- [x] Integration test `tests/integration/identity/test_cli_approval_flow.py` now locks in the expectation that `scripts.admin.rfu_admin` exposes an `approve_user_cli(database_path, username, role, preferences_template)` callable returning an object with `exit_code` and `payload` fields for automation harnesses. _(Tracked via `specs/006-baseline-login-password/tasks.md` task T084.)_
- [x] The test seeds a pending user and requires the CLI to flip `account_status` to `active`, assign a non-null `preferences_id`, and stamp `activated_at` timestamps plus matching `user_preferences` rows. _(Tracked via task T085.)_
- [x] An `admin_action_audit` entry with `action_type='approve_user'` and `origin_surface='cli'` is asserted, so the CLI implementation must pipe approvals through the upcoming audit logger instead of issuing raw SQL. _(Tracked via task T086 — now satisfied via the centralized `AuditLogger`.)_

### 2025-11-15 Role Gate Follow-ups

- [x] Create the `src/core/auth/endpoints` package (AuthController + AdminUsersController shells) so the new contract test `test_admin_role_requirements.py` can import the controllers before role enforcement is implemented. _(Prereq for T065–T068.)_
- [x] Enforce admin role checks in `scripts.admin.rfu_admin` commands, returning `exit_code=1` plus an `admin_action_audit` row tagged as unauthorized whenever a `standard` operator calls reset/approve/unblock helpers. _(Implied by T021 test.)_
- [x] Add `src/rfu/admin_panel.py` with `guard_admin_panel_access` and `open_admin_panel` helpers to gate GUI admin tooling + deep-link routing using the authenticated session role metadata. _(Prereq for T022 & upcoming T063 implementation.)_

✅ Validation: `tests/contracts/identity/test_admin_role_requirements.py` now passes against the venv interpreter, confirming the controllers exist, enforce role metadata, and surface coherent PermissionErrors for standard operators. No new follow-up tasks identified during this verification pass; continue to monitor integration results for regressions.

### 2025-11-17 Self-Registration Coverage Progress

- [x] Contract + GUI + CLI tests (T023–T025) now exist and fail against current builds, locking in `/auth/register`, hub registration surface, and CLI registration script behaviors (pending status, audit entries, duplicate messaging). These tests currently abort earlier due to legacy `user_store.py` syntax errors; fix is prerequisite before service wiring can execute.
- [x] T026–T029 are now implemented: `RegistrationService` handles validation/hash/audit + notification hooks, `scripts/rfu_register.py` prompts interactively, the hub dialog exposes a registration panel with duplicate messaging, and `AuthController.post_register` delegates to the service. The targeted contract + integration tests (T023–T025) pass and serve as regression coverage.
- [x] Registration telemetry needs audit coverage via `admin_action_audit` with `origin_surface` set to `cli`/`gui` and detail payloads describing channel + metadata capture. Capture this in the RegistrationService design to avoid duplicating logic across surfaces. _(RegistrationService now uses `AuditLogger` to persist the telemetry.)_
- [x] Follow-up: once `AuditLogger` (T054) lands, wire the new registration notification hooks to the centralized dispatcher so admin panel + CLI watchers receive pending queue alerts automatically. _(Factory now always injects `PendingRegistrationDispatcher` alongside any custom hooks and shares a single `AuditLogger`; covered by `tests/unit/auth/test_registration_service_factory.py`.)_

### 2025-11-17 MFA Readiness Kickoff

- [x] FR-013 documentation (`mfa-readiness.md`) captures schema deltas, CLI/GUI touchpoints, and the phased rollout so downstream contributors have a reference before coding against the new endpoints.
- [x] Migration 006 now seeds `mfa_enabled`, `mfa_secret_encrypted`, `mfa_recovery_codes`, `mfa_enforced_at`, plus the `user_mfa_recovery_codes` table and rollback guidance so database snapshots stay forward-compatible.
- [x] Placeholder `MFAHookService` + `MFAPlaceholderController` return `501` consistently, letting future CLI/GUI work (T072) bind to stable routes without exposing unfinished behavior.
- [x] Extend `tests/fixtures/identity_fixtures.py` to assert the new columns/tables exist once fixture refresh work resumes (tuck under upcoming repository tasks so migrations stay covered). `assert_mfa_schema_ready()` now fails fast when the MFA columns/table drift from migration 006 and is invoked during contract DB seeding.
- [x] When T072 begins, wire the CLI + REST placeholder commands to the new controller and add contract coverage ensuring we return `status="not_implemented"` with `retry_after="mfa-rollout"` until providers go live.
- [x] Schedule a follow-up task to encrypt `mfa_secret_encrypted` using the secure secret dispatcher from T080 once that component lands, ensuring secrets never sit in plaintext on disk. Recorded as backlog item `FN-MFA-SECURE-DISPATCH` below with dependency on repository task block T041–T044.

### 2025-11-17 Preference Profile Serialization Guardrails

- [x] Ensure the upcoming `PreferenceProfileRepository` (T040) instantiates the new `PreferenceProfile` model helpers so payloads always persist as `'{}'` instead of `NULL`, keeping the NOT NULL `payload` column satisfied. _(Implemented via `PreferenceProfileRepository.save()` defaulting payloads and `ensure_for_user()` bootstrap.)_
- [x] Add focused unit coverage (tie into T073/T075 planning) for `_coerce_payload` and `_serialize_payload` to catch regressions where corrupted JSON should raise `PendingPreferenceAlert` workflows instead of silently clearing metadata. _(New tests live in `tests/unit/preferences/test_preference_profile_helpers.py` and exercise mapping copies, JSON coercion, invalid fallbacks, and `'{}'` serialization defaults.)_

### 2025-11-18 Secure Secret Dispatcher + Docs

- [x] T080 landed `SecureSecretDispatcher` plus CLI wiring so reset flows now
      require `reset_request_id` confirmation before revealing secrets, with
      delivery channel metadata recorded in `reset_requests` and `admin_action_audit`.
- [x] T081 added contract coverage via
      `tests/contracts/identity/test_secure_reset_workflow.py`, confirming
      justification enforcement, console confirmation, single-dispatch semantics,
      and dispatcher audit metadata.
- [x] T077 documentation polish complete: `docs/login_password_baseline.md`
      explains the dispatcher + CLI expectations, and
      `specs/006-baseline-login-password/quickstart.md` now highlights the
      `--confirm-display` requirement, secure note exports, and MFA placeholder
      commands.

### 2025-11-18 Data Model Lifecycle Updates

- [x] T035–T038 implemented the identity/preference models: `SessionToken`
      now exposes idle timeout helpers + revocation timestamps, `ResetRequest`
      enforces non-null `expires_at` and secret lifecycle helpers,
      `AdminActionAudit` stores CLI/GUI origin metadata with JSON payload
      attachments, and `PendingPreferenceAlert` records ISO timestamps with
      escalation + resolution helpers.
- [x] When building repositories (T041–T044), ensure timestamp
      serialization routes through the new `datetime_to_iso` helpers and that
      audit logging callers populate `details` + `correlation_id` fields before
      persisting rows. _(Session, reset request, admin audit, and preference
      alert repositories now normalize timestamps via `datetime_to_iso`, and
      every `AuditLogger.record_action` caller provides a non-empty
      `correlation_id`, enforced by the logger signature.)_
- [x] Add lightweight unit coverage for the new helper methods (target
      T073/T075) so idle deadline math, reset secret clearing, and alert
      escalation/regression flows stay covered. _New suites cover SessionToken
      idle helpers, ResetRequest secret lifecycle methods, PendingPreferenceAlert
      severity/resolution helpers, plus stricter AuditLogger validation._

### 2025-11-18 Implementation Checkpoint

#### Completed

- Pending registration telemetry dispatcher now wired through `RegistrationService` hooks (T054 follow-up). Alerts emit JSONL snapshots under `reports/telemetry/`.
- Contract marker registered in `tests/pytest.ini` and contract timestamp assertions migrated off `datetime.utcnow()`.
- `tests/fixtures/identity_fixtures.py` covers MFA columns/table via `seed_mfa_enabled_user` and `mfa_recovery_code_record` helpers.
- Identity contract suite executed via `pytest tests/contracts/identity -v` to capture regression status.

#### Newly Resolved · 2025-11-20

- [x] `test_admin_reset_password` now passes: `AdminAccountService.patch_user()` propagates the generated `temporary_password` because the `UserStore` + repository stack can target the injected `database_path` (`SQLiteRepository` now falls back to direct file connections). Verified via `pytest tests/contracts/identity/test_admin_reset_password.py -q`.
- [x] `test_login_lockout` passes: failed login counters persist to `user_accounts.account_status='blocked'` once the injected `database_path` reaches the same temp DB the contract suite uses, so lockout timestamps stick instead of updating the wrong file.
- [x] `test_preferences_share_guard` passes: `ShareService` already accepted an `AuditLogger`, and we now instantiate it with the same DB path the controllers receive, eliminating the `_audit_logger` attribute error.
- [x] `test_self_registration_pending` passes: `RegistrationService` audit logging uses the injected `AuditLogger` + valid actor rows, so FK constraints succeed even when the pending user is the actor of record.
- [x] Root-level pytest configuration now lives at `pytest.ini` in the repo root and mirrors the identity/contract marker definitions so `pytest tests/contracts/identity -q` from the workspace root no longer emits `PytestUnknownMarkWarning`. Documented in this log to close out the repeated outstanding task.
- [x] `pytest_lazyfixture` regression resolved: removed the unused dependency from `requirements.txt`, added a defensive `sitecustomize.py` shim for `CallSpec2.funcargs`, and disabled the plugin via both `pytest.ini` files so `pytest tests/unit/preferences/test_preference_profile_helpers.py -q` runs cleanly again.
- [x] Re-installed the workspace dependencies via `pip install -r requirements.txt` (task runner `shell: Install Dependencies`) so all contributors inherit the updated plugin set without `pytest-lazy-fixture`.
- [x] Triage on the full `pytest tests/ -v` run shows three dominant failure buckets: (1) legacy `tools.*` modules that were relocated under `src/` (e.g., `tests/unit/test_file_splitter_logic_corrected.py` importing `tools.file_operations.file_splitter_config`), (2) network connectivity suites still patching `utilities.network...` modules that no longer exist, and (3) OCR/vision suites patching `log_config` and other historical helpers that were removed during consolidation. Documented below with new follow-up tasks.

### 2025-11-20 Legacy Network Shim

- Added the `network_org` namespace as the documented compatibility shim for legacy network connectivity imports (`src/network_org/...`).
- Re-introduced `utilities.network.network_connectivity_complex.core.network_base` as a thin wrapper over `network_org` so the remaining tests can keep importing `utilities.*` until they are migrated.
- Tagged both namespaces with `*_SHIM_NOTICE` constants to make it obvious this is a temporary bridge and to simplify future audits.

#### Status Snapshot – 2025-11-21

##### ✅ Completed / Verified

- [x] Substituted the legacy `utilities.*` imports with the `network_org` + `utilities.network` shims and confirmed the `tests/unit/test_network_base_2025-08-28.py` suite now imports `src.tools.network...network_base` without `ModuleNotFoundError`.
- [x] Re-ran `tests/unit/test_network_base_2025-08-28.py -q` after the shim swap to capture the 48 passing cases recorded in `result_system_cleanup_test_summary_2025-08-28.json`.
- [x] Implemented the identity + preferences repositories (T041–T044): `SessionStore`, `ResetRequestRepository`, `AdminActionAuditRepository`, and `PendingPreferenceAlertRepository` persist the FR-013 models with the shared `datetime_to_iso` helpers.
- [x] Added the planned unit coverage (T073/T075): `tests/unit/auth/test_password_hasher.py` locks in Argon2 parameters + denylist enforcement, while `tests/unit/preferences/test_preference_recovery.py` asserts recovery/bootstrap flows end-to-end.
- [x] Ensured reset secrets can only flow through `SecureSecretDispatcher` (T080) via `src/core/auth/services/secure_secret_dispatcher.py`, which already logs deliveries and clears ciphertext after dispatch.
- [x] Re-installed workspace requirements and trimmed unused plugins so contributors inherit the same pytest environment.
- [x] Triaged the full `pytest tests/ -v` run to the three remaining failure buckets (legacy imports, network suites, OCR logger) for easier follow-up.
- [x] Updated all `tests/` imports that previously targeted `tools.*`/`file_utilities_2.*` so they now reference the canonical `src.tools...` modules, eliminating that regression source.

##### ⏳ Outstanding / Next Actions

- [ ] Plan the sunset path for the `network_org` shim (consumer inventory, migration checklist, removal window) once every suite imports `src.tools.network.*` directly.
- [ ] Audit the remaining legacy suites (security validator, performance analyzer, diagnostics runners) for lingering `utilities.*` references and migrate them to `src.tools...`.
- [ ] Restore or replace the historical `log_config` dependency that the OCR suites expect, then verify OpenCV/numpy integration still works.
- [ ] Reintroduce (or modernize) the thin logging shim so OCR tests can patch the canonical logger entry point without import errors.
- [ ] After the network + logging shims are retired, rerun `shell: Run Tests` to capture the next wave of failures.
- [ ] `FN-MFA-SECURE-DISPATCH`: route every `mfa_secret_encrypted` write path (and associated PreferenceManager wiring) through `SecureSecretDispatcher`, update fixtures/tests, and document the enforced encryption flow before enabling MFA.
- [ ] (!) Schedule the PyQt5 GUI validation pass once the harness is ready.
- [ ] (!) Execute the GUI login/preferences validation once the PyQt harness exists so the PreferenceManager wiring stays covered.

Let me know which item you’d like to tackle first.

##### Shim Sunset Plan (2025-11-21)

###### Consumer inventory

| Consumer group                                   | Representative files                                                                                                                                                                                                                                                                                                                                                                                                                   | Current dependency                                                                                                 | Migration notes                                                                                                                                                                                                                                  |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Legacy multi-tool hub                            | `src/tabbed_hub.py`                                                                                                                                                                                                                                                                                                                                                                                                                    | Imports `..utilities.network.*` widgets for the retired tabbed hub shell.                                          | Re-point imports to `src.tools.network.*` or archive the module once `src/rfu/hub.py` fully replaces it. Confirm any downstream packaging scripts skip the legacy hub before deletion.                                                           |
| PyQt network GUI suites                          | `tests/unit/test_network_gui_2025-08-28.py`, `tests/unit/test_network_gui_2025-08-29.py`, `tests/unit/test_network_gui_core_2025-08-29.py`, `tests/unit/network/test_network_gui_2025-08-28.py`                                                                                                                                                                                                                                        | Extensive patching of `utilities.network.gui.*` classes/workers plus dialog helpers.                               | Update `patch()` targets and fixture imports to `src.tools.network.gui`. Validate that helper factories (e.g., `NetworkWorkerThread`) still mount correctly once the new path is used.                                                           |
| Network connectivity + security validator suites | `tests/unit/test_network_complex_real_implementations*.py`, `tests/unit/network/test_network_complex_real_implementations*.py`, `tests/unit/conftest_security_validator_2025-08-30.py`, security validator runners (`run_security_validator_tests*.py`, `execute_security_validator_tests_enhanced_2025-08-30.py`)                                                                                                                     | Patch targets, coverage args, and helper registries point at `utilities.network.network_connectivity(_complex).*`. | Replace every import/patch path with `src.tools.network.network_connectivity_complex.*` (or `src.tools.network.connectivity.*` where appropriate). Refresh coverage config/pytest `.ini` files to the new module paths before re-running suites. |
| Bookmark manager tests                           | `tests/unit/test_bookmark_manager*.py`                                                                                                                                                                                                                                                                                                                                                                                                 | Patches `utilities.network.bookmark_manager.*` for logging toggles, importer wiring, and GUI glue.                 | Switch to `src.tools.network.bookmarks.bookmark_manager` (and `bookmark_manager_gui` where needed). Update fixture patch strings and any `LOGGING_AVAILABLE` references accordingly.                                                             |
| Harness + diagnostics                            | Runner scripts (`tests/unit/run_network_base_tests_2025-08-28.py`, `tests/unit/run_network_base_tests_2025-08-29.py`, `tests/unit/network/run_network_gui_tests_2025-08-28.py`), env diagnostics (`tests/unit/test_environment_setup.py`, `tests/unit/test_env_config.py`, `tests/unit/test_import_system_fixes.py`, `tests/unit/test_utilities_comprehensive_integration.py`, `tests/unit/test_utilities_availability_diagnostic.py`) | Hard-coded module availability lists plus coverage args still enumerate `utilities.network.*`.                     | Update these helpers to assert against the `src.tools.network.*` namespaces (or remove checks entirely if superseded by the modern hub smoke tests). This ensures automated health reports stop re-introducing the shim by mistake.              |

###### Migration checklist

1. Update production code (`src/tabbed_hub.py` plus any residual scripts) to import directly from `src.tools.network.*`; confirm no packaged entry points rely on `utilities.network` after the swap.
2. Migrate the PyQt GUI suites to the new module path, run `pytest tests/unit/test_network_gui_2025-08-28.py tests/unit/test_network_gui_2025-08-29.py -q`, and capture results in this log.
3. Migrate the network connectivity + security validator suites (including pytest configs and helper scripts), then run `pytest tests/unit/test_network_complex_real_implementations_2025-09-01.py tests/unit/conftest_security_validator_2025-08-30.py -q` followed by the `run_security_validator_tests` harness.
4. Update bookmark manager tests and rerun `pytest tests/unit/test_bookmark_manager_2025-08-24.py tests/unit/test_bookmark_manager_basic_2025-08-24.py tests/unit/test_bookmark_manager_advanced_2025-08-24.py -q`.
5. Refresh every runner/config/diagnostic file that hard-codes `utilities.network.*` (coverage args, env reports, metrics generators) so tooling consistently references `src.tools.network.*`.
6. Once the repo-wide `git grep "utilities.network"` check returns only documentation references, delete `src/network_org` and `src/utilities/network` (plus their `__init__.py` breadcrumbs) in a single PR and rerun `shell: Run Tests` to ensure no regressions.

###### Exit criteria

- `git grep "utilities.network"` and `git grep "network_org"` return zero hits outside historical notes.
- `pytest tests/unit/network -q` and the bookmark manager/network validator suites pass while importing only `src.tools.network.*` modules.
- Coverage/runner scripts stop referencing the shim namespace, and packaging scripts (CLI + hub) boot without touching `utilities.network`.
- Removing `src/network_org` and `src/utilities/network` no longer affects import resolution (verified via clean environment + automated import diagnostics).
