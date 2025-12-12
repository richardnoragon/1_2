# Tasks: Login & Password Integration Upgrade — Lockout Prevention

**Input**: `specs/007-upgrade-to-login/plan.md` + supporting artifacts
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓
**Motto**: _"Better many smaller, detailed tasks than fewer large complex ones."_

---

## Progress Summary (Updated 2025-12-01)

| Phase | Description              | Status      | Tasks                     |
| ----- | ------------------------ | ----------- | ------------------------- |
| 3.1   | Setup & Schema Migration | ✅ Complete | T001–T003 done            |
| 3.2   | TDD Contract Tests       | ✅ Complete | T004–T037 done (34 tests) |
| 3.3   | Core Models              | ✅ Complete | T038–T041 done            |
| 3.4   | Repositories             | ✅ Complete | T042–T044 done            |
| 3.5   | Services                 | ✅ Complete | T045–T052 done (8 tasks)  |
| 3.6   | CLI Integration          | ✅ Complete | T053–T059 done (7 tasks)  |
| 3.7   | GUI Integration          | ✅ Complete | T060–T063 done (4 tasks)  |
| 3.8   | Integration & Wiring     | ✅ Complete | T064–T067 done (4 tasks)  |
| 3.9   | Polish & Documentation   | ✅ Complete | T068–T075 done (8 tasks)  |

**Completed**: 75 tasks | **Remaining**: 0 tasks | **Feature Complete** ✅

> **Note**: specs/006-baseline-login-password is now **100% complete** (T001–T117).
> This spec (007) builds upon that foundation with lockout prevention enhancements.

---

## Phase 3.1 – Setup & Schema Migration

- [x] T001 Create migration `scripts/migrations/007_lockout_prevention.sql` with:
  - Add columns to `user_accounts`: `is_always_available BOOLEAN DEFAULT FALSE`, `is_break_glass BOOLEAN DEFAULT FALSE`, `break_glass_justification TEXT`
  - Expand role enum: add `dev`, `readonly`; migrate `standard` → `user`
  - Add `session_type TEXT DEFAULT 'normal'` to `session_tokens`
  - Create `always_available_account_config` table with cooldown tracking
  - Create `break_glass_usage_log` table with session tracking
  - Add indexes for protected account queries
- [x] T002 [P] Create `tests/fixtures/lockout_prevention_fixtures.py` with helpers to seed:
  - Always-available accounts (dev + admin)
  - Break-glass accounts (dev + admin)
  - Standard accounts with each of the four roles
  - Blocked accounts in cooldown state
- [x] T003 [P] Update `requirements.txt` to confirm `argon2-cffi>=21.0.0`, `PyQt5>=5.15.0`, and any new test dependencies

---

## Phase 3.2 – Tests First (TDD Gate)

> ⚠️ CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation

### Contract Tests from `contracts/always_available_accounts.yaml`

- [x] T004 [P] Scaffold failing contract test `tests/contracts/identity/test_always_available_cannot_delete.py`:
  - DELETE on always-available account returns 403
  - Account still exists after attempt
  - AdminActionAudit logged with action_type='delete_attempt_blocked'
- [x] T005 [P] Scaffold failing contract test `tests/contracts/identity/test_always_available_cannot_disable.py`:
  - PATCH with account_status='disabled' returns 403
  - Account status remains 'active'
  - AdminActionAudit logged with action_type='disable_attempt_blocked'
- [x] T006 [P] Scaffold failing contract test `tests/contracts/identity/test_always_available_auto_unblock.py`:
  - Blocked account with expired cooldown auto-unblocks
  - login_attempts reset to 0
  - AdminActionAudit logged with action_type='auto_unblock'
- [x] T007 [P] Scaffold failing contract test `tests/contracts/identity/test_always_available_no_unblock_during_cooldown.py`:
  - Blocked account within cooldown period remains blocked
  - Response reason contains 'cooldown not expired'

### Contract Tests from `contracts/break_glass_accounts.yaml`

- [x] T008 [P] Scaffold failing contract test `tests/contracts/identity/test_break_glass_requires_enablement.py`:
  - Login without enablement flag returns 403
  - Error message contains 'break-glass access not enabled'
- [x] T009 [P] Scaffold failing contract test `tests/contracts/identity/test_break_glass_requires_justification.py`:
  - Login with credentials but no justification returns 422
  - Error message contains 'justification required'
- [x] T010 [P] Scaffold failing contract test `tests/contracts/identity/test_break_glass_creates_usage_log.py`:
  - Valid login creates session with session_type='break_glass'
  - BreakGlassUsageLog entry created with justification
  - Session linked to usage log via usage_log_id
- [x] T011 [P] Scaffold failing contract test `tests/contracts/identity/test_break_glass_logout_triggers_rotation.py`:
  - Logout sets logout_timestamp in BreakGlassUsageLog
  - post_usage_rotation_status set to 'pending'
  - New credentials generated and exported
- [x] T012 [P] Scaffold failing contract test `tests/contracts/identity/test_break_glass_actions_tracked.py`:
  - Actions performed during session appear in actions_performed JSON
  - Each action entry has action, target, timestamp
- [x] T013 [P] Scaffold failing contract test `tests/contracts/identity/test_normal_account_denied_break_glass.py`:
  - Non-break-glass account cannot use break-glass endpoint
  - Returns 403 with 'not a break-glass account'

### Contract Tests from `contracts/role_enforcement.yaml`

- [x] T014 [P] Scaffold failing contract test `tests/contracts/identity/test_dev_can_manage_all_roles.py`:
  - Dev role has all management capabilities
  - Can create, modify, delete admin/user/readonly accounts
- [x] T015 [P] Scaffold failing contract test `tests/contracts/identity/test_admin_can_manage_user_roles.py`:
  - Admin role can create/modify user and readonly accounts
  - Cannot create or modify admin or dev accounts
- [x] T016 [P] Scaffold failing contract test `tests/contracts/identity/test_user_cannot_manage_accounts.py`:
  - User role cannot create, modify, or delete any accounts
  - Can only view own profile
- [x] T017 [P] Scaffold failing contract test `tests/contracts/identity/test_readonly_cannot_modify.py`:
  - Readonly role cannot create, modify, or delete any accounts
  - Cannot change own password
- [x] T018 [P] Scaffold failing contract test `tests/contracts/identity/test_role_hierarchy_enforced.py`:
  - Role levels: dev(4) > admin(3) > user(2) > readonly(1)
  - Cannot escalate own role
  - Cannot modify accounts with equal or higher role
- [x] T019 [P] Scaffold failing contract test `tests/contracts/identity/test_protected_role_immutable.py`:
  - Always-available accounts cannot have role changed
  - Break-glass accounts cannot have role changed
  - Attempt to change role returns 403
- [x] T020 [P] Scaffold failing contract test `tests/contracts/identity/test_role_changes_audited.py`:
  - Role changes create audit log entries
  - Audit log includes: actor, target, old_role, new_role, timestamp
  - Failed role change attempts are also logged
- [x] T021 [P] Scaffold failing contract test `tests/contracts/identity/test_session_role_at_login.py`:
  - Session role is captured at login time
  - Role changes after login do not affect active sessions
  - Session displays correct role in profile

### Contract Tests from `contracts/lockout_prevention.yaml`

- [x] T022 [P] Scaffold failing contract test `tests/contracts/identity/test_failed_login_increments_counter.py`:
  - Each failed login increments login_attempts by 1
  - Counter starts at 0 for new accounts
  - Counter resets to 0 on successful login
- [x] T023 [P] Scaffold failing contract test `tests/contracts/identity/test_account_blocks_after_threshold.py`:
  - Account blocked after MAX_FAILED_ATTEMPTS (default 5)
  - is_blocked flag set to 1
  - blocked_at timestamp recorded
- [x] T024 [P] Scaffold failing contract test `tests/contracts/identity/test_cooldown_prevents_unblock.py`:
  - LOCKOUT_COOLDOWN_MINUTES (default 15) must pass before unblock
  - Manual unblock during cooldown is denied
  - System shows remaining cooldown time
- [x] T025 [P] Scaffold failing contract test `tests/contracts/identity/test_admin_can_unblock.py`:
  - Admin role can unblock user accounts after cooldown
  - Admin role cannot unblock admin or dev accounts
  - Unblock action is audited
- [x] T026 [P] Scaffold failing contract test `tests/contracts/identity/test_dev_can_unblock_all.py`:
  - Dev role can unblock any account after cooldown
  - Dev role can unblock admin accounts
  - Dev cannot bypass cooldown for security
- [x] T027 [P] Scaffold failing contract test `tests/contracts/identity/test_lockout_events_audited.py`:
  - Account lockout creates audit log entry
  - Failed login attempts are logged (configurable)
  - Unblock attempts (success and failure) are logged

### Integration Tests from `quickstart.md`

- [x] T028 [P] Add integration test `tests/integration/identity/test_protected_accounts_list.py`:
  - CLI `list-protected-accounts` shows all 4 protected accounts
  - Output includes username, role, type, status columns
- [x] T029 [P] Add integration test `tests/integration/identity/test_always_available_protection_guard.py`:
  - Attempt delete via CLI blocked with clear error
  - AdminActionAudit entry created
- [x] T030 [P] Add integration test `tests/integration/identity/test_auto_unblock_after_cooldown.py`:
  - Simulate 5 failed logins on always-available account
  - Account shows auto_unblock_at timestamp
  - After 5 minutes, account auto-unblocks
- [x] T031 [P] Add integration test `tests/integration/identity/test_break_glass_login_flow.py`:
  - Enable break-glass via environment variable
  - Login with break-glass credentials and justification
  - Session created with session_type='break_glass'
  - Usage logged to BreakGlassUsageLog
- [x] T032 [P] Add integration test `tests/integration/identity/test_break_glass_logout_rotation.py`:
  - End break-glass session
  - Password rotation triggered
  - New credentials exported to file
- [x] T033 [P] Add integration test `tests/integration/identity/test_role_permission_check.py`:
  - Readonly user denied write operations
  - Dev user has debugging access
  - User role denied admin operations
- [x] T034 [P] Add integration test `tests/integration/identity/test_lockout_health_check.py`:
  - CLI health-check --lockout-prevention passes
  - Shows all accessible paths

### GUI Integration Tests

- [x] T035 [P] Add GUI integration test `tests/integration/gui/test_break_glass_justification_dialog.py`:
  - Break-glass login prompts for justification
  - Login blocked if justification empty or too short
- [x] T036 [P] Add GUI integration test `tests/integration/gui/test_protected_account_indicators.py`:
  - Admin panel shows lock icon for protected accounts
  - Delete/disable buttons disabled for always-available accounts
- [x] T037 [P] Add GUI integration test `tests/integration/gui/test_readonly_mode_restrictions.py`:
  - Readonly user sees disabled write operation buttons
  - Attempting write via hotkey shows permission error

---

## Phase 3.3 – Data Models

- [x] T038 [P] Implement `src/core/auth/models/always_available_account_config.py`:
  - Dataclass with username, last_cooldown_start, cooldown_duration_minutes, auto_unblock_enabled
  - Method `should_auto_unblock()` implementing cooldown logic from research.md
  - ISO datetime serialization for SQLite
- [x] T039 [P] Implement `src/core/auth/models/break_glass_usage_log.py`:
  - Dataclass with id, session_id, account_username, timestamps, justification, actions_performed, rotation_status
  - JSON serialization for actions_performed array
  - Method `add_action()` for appending action entries
- [x] T040 Extend `src/core/auth/models/user_account.py`:
  - Add `is_always_available: bool`, `is_break_glass: bool`, `break_glass_justification: Optional[str]`
  - Expand role enum: `Literal['dev', 'admin', 'user', 'readonly']`
  - Add validation: is_always_available and is_break_glass are mutually exclusive
- [x] T041 Extend `src/core/auth/models/session_token.py`:
  - Add `session_type: Literal['normal', 'break_glass']`
  - Add `usage_log_id: Optional[int]` for break-glass sessions

---

## Phase 3.4 – Data Access & Repositories

- [x] T042 [P] Implement `src/core/auth/repositories/always_available_account_repository.py`:
  - `get_config(username)` → AlwaysAvailableAccountConfig
  - `update_cooldown_start(username, timestamp)`
  - `reset_cooldown(username)`
  - `list_all_configs()` → List[AlwaysAvailableAccountConfig]
- [x] T043 [P] Implement `src/core/auth/repositories/break_glass_usage_log_repository.py`:
  - `create_log(session_id, username, justification)` → int (log id)
  - `update_logout(id, timestamp)`
  - `update_rotation_status(id, status)`
  - `add_action(id, action_entry)`
  - `get_pending_rotations()` → List[BreakGlassUsageLog]
  - `get_usage_since(datetime)` → List[BreakGlassUsageLog]
- [x] T044 Extend `src/core/auth/repositories/user_account_repository.py`:
  - `get_always_available_accounts()` → List[UserAccount]
  - `get_break_glass_accounts()` → List[UserAccount]
  - `is_protected(username)` → bool
  - `update_role(username, new_role)` with audit support

---

## Phase 3.5 – Domain Services & Policies

- [x] T045 [P] Implement `src/core/auth/policies/role_policy.py`:
  - `ROLE_HIERARCHY = {'dev': 4, 'admin': 3, 'user': 2, 'readonly': 1}`
  - `CAPABILITY_MATRIX` matching contracts/role_enforcement.yaml
  - `has_capability(role, capability)` → bool
  - `can_escalate(actor_role, target_role)` → bool
- [x] T046 [P] Implement `src/core/auth/services/lockout_prevention_service.py`:
  - `check_auto_unblock(username)` → AutoUnblockResult
  - `trigger_cooldown(username)` for blocked always-available accounts
  - `get_health_status()` → LockoutPreventionHealth
  - Uses AlwaysAvailableAccountRepository for state
- [x] T047 [P] Implement `src/core/auth/services/break_glass_service.py`:
  - `is_enabled()` → bool (checks env var RFU_ENABLE_BREAK_GLASS)
  - `enable(source: str)` / `disable()`
  - `login(username, password, justification)` → BreakGlassSession
  - `logout(session_id)` → RotationResult
  - `log_action(session_id, action, target)`
  - Integrates with BreakGlassUsageLogRepository
- [x] T048 [P] Implement `src/core/auth/services/account_bootstrap_service.py`:
  - `bootstrap_protected_accounts()` → BootstrapResult
  - Creates rfu_dev_always, rfu_admin_always, rfu_dev_breakglass, rfu_admin_breakglass
  - Generates secure random passwords
  - Exports credentials via console and secure note file
  - Idempotent (checks if accounts exist)
  - **Completed**: Full implementation with BootstrapResult, CreatedAccount, password hashing, credential export
- [x] T049 [P] Implement `src/core/auth/services/role_enforcement_service.py`:
  - `check_permission(role, action)` → PermissionResult
  - `change_role(actor, target_username, new_role, justification)` → RoleChangeResult
  - Enforces escalation rules from role_enforcement.yaml
  - Logs all role changes to AdminActionAudit
  - **Completed**: EnforcedPermissionResult, EnforcedRoleChangeResult, full audit logging (23 tests pass)
- [x] T050 Update `src/core/auth/services/auth_service.py`:
  - Detect break-glass login and delegate to BreakGlassService
  - Call LockoutPreventionService.check_auto_unblock() before blocking always-available
  - Set session_type appropriately
  - **Completed**: Added lockout_prevention_service integration, auto-unblock check, cooldown triggering
- [x] T051 Update `src/core/auth/services/session_service.py`:
  - On logout, check if session_type='break_glass'
  - If break-glass, call BreakGlassService.logout() for rotation
  - Update BreakGlassUsageLog with logout timestamp
  - **Completed**: \_handle_break_glass_logout() with deactivation, notification, rotation requirement
- [x] T052 Update `src/core/auth/policies/lockout_policy.py`:
  - For always-available accounts: trigger cooldown instead of permanent block
  - Call LockoutPreventionService.trigger_cooldown()
  - Return different lockout response with auto_unblock_at timestamp
  - **Completed**: Added LockoutPreventionService integration, cooldown_triggered field, service protocol

---

## Phase 3.6 – CLI Commands

- [x] T053 Add CLI command `bootstrap-protected-accounts` to `scripts/admin/rfu_admin.py`:
  - Calls AccountBootstrapService.bootstrap_protected_accounts()
  - Displays credentials via console
  - Exports to config/protected_credentials_YYYYMMDD.secure
  - Returns exit code 0 on success
- [x] T054 Add CLI command `list-protected-accounts` to `scripts/admin/rfu_admin.py`:
  - Queries UserAccountRepository for protected accounts
  - Displays table: Username | Role | Type | Status
  - Shows always-available vs break-glass distinction
- [x] T055 Add CLI command `break-glass-login` to `scripts/admin/rfu_admin.py`:
  - Requires --enable-break-glass flag or RFU_ENABLE_BREAK_GLASS env var
  - Prompts for --justification
  - Calls BreakGlassService.login()
  - Displays session ID for later logout
- [x] T056 Add CLI command `break-glass-logout` to `scripts/admin/rfu_admin.py`:
  - Requires --session-id
  - Calls BreakGlassService.logout()
  - Displays rotation result and new credentials path
- [x] T057 Add CLI command `rotate-break-glass` to `scripts/admin/rfu_admin.py`:
  - Manual rotation of break-glass credentials
  - Requires dev role
  - Generates new password, exports to secure note
- [x] T058 Add CLI command `health-check --lockout-prevention` to `scripts/admin/rfu_admin.py`:
  - Calls LockoutPreventionService.get_health_status()
  - Displays accessible paths and account status
  - Returns exit code 0 if healthy, 1 if critical
- [x] T059 Add CLI command `check-auto-unblock` to `scripts/admin/rfu_admin.py`:
  - Requires --username for always-available account
  - Calls LockoutPreventionService.check_auto_unblock()
  - Displays result (unblocked or time remaining)

---

## Phase 3.7 – GUI Updates

- [x] T060 Update `src/rfu/login_dialog.py`:
  - Detect if credentials match break-glass account
  - Show justification dialog before proceeding
  - Validate justification minimum length (10 chars)
  - Pass justification to BreakGlassService.login()
- [x] T061 Update `src/rfu/admin_panel.py`:
  - Add "Protected Accounts" section (dev role only)
  - Show lock icon for always-available accounts
  - Show emergency icon for break-glass accounts
  - Disable delete/disable buttons for protected accounts
  - Add "Break-Glass Usage Log" viewer for dev role
- [x] T062 [P] Add readonly mode enforcement to `src/rfu/hub.py`:
  - Check user role on startup
  - Disable write operation buttons for readonly users
  - Show permission toast when blocked action attempted
- [x] T063 [P] Add break-glass session indicator to `src/rfu/hub.py`:
  - Display warning banner during break-glass session
  - Show "Actions logged" reminder
  - Prompt for logout confirmation

---

## Phase 3.8 – Integration & Wiring

- [x] T064 Wire AccountBootstrapService into database initialization:
  - Call bootstrap_protected_accounts() after schema migration
  - Handle first-run vs existing database scenarios
  - Created `src/core/auth/database_initializer.py` with IdentityDatabaseInitializer
- [x] T065 Update `src/core/auth/endpoints/auth_controller.py`:
  - Add break-glass login endpoint handler
  - Route to BreakGlassService when appropriate
  - Return session with usage_log_id for break-glass
  - Added post_break_glass_login() method with justification validation
  - Added session_type field to login responses
- [x] T066 Update `src/core/auth/endpoints/admin_users_controller.py`:
  - Add role change endpoint with escalation rules
  - Block deletion/disable of protected accounts with 403
  - Log blocked attempts to AdminActionAudit
  - Added PROTECTED_USERNAMES guard
  - Added \_require_dev_role() for high-privilege operations
- [x] T067 [P] Create `src/core/auth/endpoints/lockout_prevention_controller.py`:
  - GET /internal/health/lockout-prevention
  - GET /internal/recovery/cli-path
  - POST /internal/bootstrap/protected-accounts
  - POST /internal/accounts/{username}/auto-unblock
  - Added get_protected_accounts() listing endpoint

---

## Phase 3.9 – Polish, Performance & Documentation

- [x] T068 [P] Add unit tests `tests/unit/auth/test_role_policy.py`:
  - Test all 8 capabilities for all 4 roles
  - Test escalation rules
  - Test demotion always allowed
  - **Completed**: 8 test classes (TestCapabilityEnum, TestRoleHierarchy, TestHasCapability, TestCheckPermission, TestRoleChangePermissions, TestPermissionResult, TestRoleChangeResult, TestCompleteCapabilityMatrix)
- [x] T069 [P] Add unit tests `tests/unit/auth/test_lockout_prevention_service.py`:
  - Test cooldown calculation
  - Test auto-unblock timing
  - Test health status aggregation
  - **Completed**: Pre-existing comprehensive test suite covering service instantiation, cooldown management, health status aggregation
- [x] T070 [P] Add unit tests `tests/unit/auth/test_break_glass_service.py`:
  - Test enablement check
  - Test justification validation
  - Test action logging
  - Test rotation trigger
  - **Completed**: Pre-existing comprehensive test suite covering service instantiation, enablement, login flow, justification, action logging
- [x] T071 [P] Add unit tests `tests/unit/auth/test_account_bootstrap_service.py`:
  - Test idempotent bootstrap
  - Test credential generation
  - Test file export
  - **Completed**: Pre-existing comprehensive test suite covering service instantiation, idempotent bootstrap, credential generation
- [x] T072 [P] Add performance test `tests/performance/test_auto_unblock_latency.py`:
  - Auto-unblock check completes < 50ms
  - Health check completes < 100ms
  - **Completed**: TestAutoUnblockLatency with 50ms/100ms envelope tests, concurrent check stress test
- [x] T073 [P] Add performance test `tests/performance/test_break_glass_login_latency.py`:
  - Break-glass login (with logging) completes < 500ms
  - Usage log write completes < 50ms
  - **Completed**: TestBreakGlassLoginLatency with 500ms login, 50ms log write, 50ms action logging envelope tests
- [x] T074 [P] Update `docs/login_password_baseline.md`:
  - Add section on four-role system
  - Document always-available account behavior
  - Document break-glass procedures with examples
  - Add troubleshooting for lockout scenarios
  - **Completed**: Added Role Capability Matrix section with 8 capabilities × 4 roles, escalation rules table, troubleshooting for common lockout issues
- [x] T075 [P] Create `docs/lockout_prevention_runbook.md`:
  - Step-by-step recovery procedures
  - CLI command reference
  - Break-glass credential rotation process
  - Health check interpretation
  - **Completed**: Comprehensive 550+ line runbook with recovery procedures, CLI reference, rotation process, health check interpretation

---

## Dependencies & Ordering Notes

- Phase 3.1 (T001–T003) must complete before any tests
- Contract tests (T004–T027) and integration tests (T028–T037) must exist/fail before implementing models/services
- Data models (T038–T041) unlock repositories (T042–T044)
- Repositories are prerequisites for services (T045–T052)
- CLI commands (T053–T059) depend on services
- GUI updates (T060–T063) depend on services and CLI patterns
- Integration & wiring (T064–T067) depends on all services and repositories
- Polish tasks (T068–T075) run only after core implementation passes

### File Conflict Notes

- T040 and T041 modify existing models → sequential, not [P]
- T050, T051, T052 extend existing services → sequential after new services
- T053–T059 all modify `scripts/admin/rfu_admin.py` → sequential, not [P]
- T060–T061 modify existing GUI files → sequential, not [P]

---

## Parallel Execution Examples

```text
# Example 1: Launch contract test scaffolding together after fixtures exist
/task run specs/007-upgrade-to-login/tasks.md T004
/task run specs/007-upgrade-to-login/tasks.md T005
/task run specs/007-upgrade-to-login/tasks.md T006
/task run specs/007-upgrade-to-login/tasks.md T007
/task run specs/007-upgrade-to-login/tasks.md T008
/task run specs/007-upgrade-to-login/tasks.md T009
...through T027

# Example 2: Parallel model implementations for NEW models after tests fail
/task run specs/007-upgrade-to-login/tasks.md T038
/task run specs/007-upgrade-to-login/tasks.md T039

# Example 3: Parallel repository implementations
/task run specs/007-upgrade-to-login/tasks.md T042
/task run specs/007-upgrade-to-login/tasks.md T043

# Example 4: Parallel service implementations for NEW services
/task run specs/007-upgrade-to-login/tasks.md T045
/task run specs/007-upgrade-to-login/tasks.md T046
/task run specs/007-upgrade-to-login/tasks.md T047
/task run specs/007-upgrade-to-login/tasks.md T048
/task run specs/007-upgrade-to-login/tasks.md T049

# Example 5: Polish tasks in parallel right before release
/task run specs/007-upgrade-to-login/tasks.md T068
/task run specs/007-upgrade-to-login/tasks.md T069
/task run specs/007-upgrade-to-login/tasks.md T070
/task run specs/007-upgrade-to-login/tasks.md T071
/task run specs/007-upgrade-to-login/tasks.md T072
/task run specs/007-upgrade-to-login/tasks.md T073
/task run specs/007-upgrade-to-login/tasks.md T074
/task run specs/007-upgrade-to-login/tasks.md T075
```

Ensure each `/task run ...` command executes only when prerequisites listed above are complete.

---

## Validation Checklist

> GATE: Checked before marking feature complete ✅ ALL GATES PASSED

- [x] All contract tests from contracts/\*.yaml have corresponding test files
- [x] All entities from data-model.md have model tasks
- [x] All tests come before implementation (TDD order)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Identity features include hashing, lockout, reset, and audit tasks ✓
- [x] Four-role enforcement implemented and tested ✓
- [x] Always-available accounts protected and auto-unblock working ✓
- [x] Break-glass accounts require enablement and justification ✓
- [x] Lockout prevention invariant verified via health check ✓
- [x] CLI recovery path documented and tested ✓

---

## Task Count Summary

| Phase            | Tasks        | Parallel        |
| ---------------- | ------------ | --------------- |
| 3.1 Setup        | T001–T003    | 2               |
| 3.2 Tests First  | T004–T037    | 34              |
| 3.3 Data Models  | T038–T041    | 2               |
| 3.4 Repositories | T042–T044    | 2               |
| 3.5 Services     | T045–T052    | 5               |
| 3.6 CLI Commands | T053–T059    | 0               |
| 3.7 GUI Updates  | T060–T063    | 2               |
| 3.8 Integration  | T064–T067    | 1               |
| 3.9 Polish       | T068–T075    | 8               |
| **Total**        | **75 tasks** | **56 parallel** |

---

> Based on Constitution v1.3.0 — See `.specify/memory/constitution.md`
> Extends 006-baseline-login-password per spec.md requirements
