# 007 Upgrade to Login - Fleeting Notes

**Feature**: 007-upgrade-to-login
**Date**: 2025-11-29
**Phase**: 3.8 Integration & Wiring (Complete)

---

## Implementation Notes

### T064-T067: Integration & Wiring Phase

Completed implementing Phase 3.8 tasks on 2025-11-29.

**Files Created:**

- `src/core/auth/database_initializer.py` - T064
- `src/core/auth/endpoints/lockout_prevention_controller.py` - T067

**Files Modified:**

- `src/core/auth/endpoints/auth_controller.py` - T065
- `src/core/auth/endpoints/admin_users_controller.py` - T066
- `src/core/auth/endpoints/__init__.py` - Added LockoutPreventionController export

---

## Inconsistencies Found

### Issue 1: AdminIdentityActions Missing Methods

**Status**: Documented for future implementation
**Details**: The `AdminIdentityActions` workflow class is missing:

- `delete_user()` method - T066 endpoint prepared but raises NotImplementedError
- `change_role()` method - T066 endpoint prepared but raises NotImplementedError

The controllers implement the guards and validation logic, but the actual
workflow methods need to be added to `src/core/auth/workflows/admin_actions.py`.

### Issue 2: AlwaysAvailableAccountRepository Constructor

**Status**: Resolved with alternative approach
**Details**: `AlwaysAvailableAccountRepository` expects `db_connection` parameter,
not `db_path`. Updated controller to use `UserAccountRepository` directly with
`LockoutPreventionService` which provides the needed functionality.

---

## Clarifications Needed

_(None at this time)_

---

## Implementation Decisions

### T064: Database Initialization Wiring

- **Decision**: Created a new module `src/core/auth/database_initializer.py` that:
  - Applies 007_lockout_prevention.sql migration if not already applied
  - Calls `AccountBootstrapService.bootstrap_protected_accounts()` after migration
  - Provides idempotent initialization via schema version tracking
  - Integrates with existing database manager pattern
  - Uses `IdentityDatabaseInitializer` class with clear initialization workflow

### T065: Auth Controller Break-Glass Support

- **Decision**: Extended `AuthController` with:
  - New `post_break_glass_login()` method dedicated to break-glass flow
  - Updated `post_login()` to detect break-glass accounts and route appropriately
  - Constants: `BREAK_GLASS_ENV_VAR = "RFU_ENABLE_BREAK_GLASS"`
  - Constants: `MIN_JUSTIFICATION_LENGTH = 10`
  - Returns `session_type: 'break_glass'` and `usage_log_id` in response
  - Creates `break_glass_usage_log` entries with justification
  - Updated `delete_login()` to handle break-glass session logout with rotation info

### T066: Admin Users Controller Enhancements

- **Decision**: Extended `AdminUsersController` with:
  - `PROTECTED_USERNAMES` set with four protected account usernames
  - `ROLE_HIERARCHY` dict for escalation rule enforcement
  - `_handle_role_change()` with escalation validation
  - `_check_protected_account()` guard for modification attempts
  - `_require_dev_role()` for high-privilege operations (deletion)
  - `delete_user()` endpoint stub (requires workflow implementation)

### T067: Lockout Prevention Controller

- **Decision**: Created new controller `LockoutPreventionController` with:
  - `get_health()` - Health check using `LockoutPreventionService.get_health_status()`
  - `get_cli_path()` - Discovery of recovery CLI tool path
  - `post_bootstrap()` - Protected account bootstrapping with dry-run support
  - `post_auto_unblock()` - Manual auto-unblock trigger for always-available accounts
  - `get_protected_accounts()` - List all protected accounts with status
  - Lazy-loaded service properties for efficiency

---

## Test Status

| Task | Tests Needed                        | Status              |
| ---- | ----------------------------------- | ------------------- |
| T064 | Integration tests for DB init       | Pending (T068-T071) |
| T065 | Auth controller break-glass tests   | Pending (T070)      |
| T066 | Admin users controller tests        | Pending (T068)      |
| T067 | Lockout prevention controller tests | Pending (T069)      |

Note: Unit tests are scheduled for Phase 3.9 (T068-T075)

---

## References

- [tasks.md](../../specs/007-upgrade-to-login/tasks.md)
- [plan.md](../../specs/007-upgrade-to-login/plan.md)
- [data-model.md](../../specs/007-upgrade-to-login/data-model.md)
- [research.md](../../specs/007-upgrade-to-login/research.md)
