# Implementation Plan: Login & Password Integration Upgrade — Lockout Prevention

**Branch**: `007-upgrade-to-login` | **Date**: 2025-11-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-upgrade-to-login/spec.md`

## Execution Flow (/plan command scope)

```text
1. Load feature spec from Input path ✓
   → Feature spec loaded from specs/007-upgrade-to-login/spec.md
2. Fill Technical Context (scan for NEEDS CLARIFICATION) ✓
   → Project Type: single (Python desktop application with PyQt5 GUI)
   → Structure Decision: Extend existing src/ layout
3. Fill Constitution Check section ✓
   → Principle VII (Identity & Access Control) fully addressed
4. Evaluate Constitution Check section ✓
   → No violations - design aligns with constitution v1.3.0
   → Update Progress Tracking: Initial Constitution Check PASS
5. Execute Phase 0 → research.md ✓
   → No NEEDS CLARIFICATION remain
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, .github/copilot-instructions.md ✓
7. Re-evaluate Constitution Check section ✓
   → No new violations after design phase
   → Update Progress Tracking: Post-Design Constitution Check PASS
8. Plan Phase 2 → Task generation approach described
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

This upgrade extends the existing Login & Password Integration (006-baseline) to prevent operator lockout by introducing:

1. **Four-role system**: `dev`, `admin`, `user`, `readonly` with graduated privileges
2. **Always-available accounts**: Two protected accounts (one dev, one admin) that cannot be deleted/disabled
3. **Break-glass accounts**: Two emergency recovery accounts (one dev, one admin) for disaster recovery
4. **Auto-unblock mechanism**: Always-available accounts use 5-minute cooldown instead of permanent blocking
5. **Enhanced audit logging**: Break-glass usage triggers special audit entries and password rotation

## Technical Context

**Language/Version**: Python 3.8+ (aligned with constitution constraint)
**Primary Dependencies**: PyQt5 (GUI), sqlite3 (storage), argon2-cffi (password hashing)
**Storage**: SQLite database (`data/identity/rfu_identity.sqlite3`)
**Testing**: pytest with markers (unit, integration, contract, gui)
**Target Platform**: Windows, macOS, Linux desktops
**Project Type**: Single (Python desktop application)
**Performance Goals**: Login round-trip < 250ms, preference hydration < 1s
**Constraints**: Session idle timeout ≤ 10 minutes, audit retention ≥ 12 months
**Scale/Scope**: Desktop application supporting multiple local operators

## Constitution Check

> GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

### Identity & Access Control (Principle VII) ✓

**Credential Storage**:

- Passwords hashed with Argon2id (`time_cost=3`, `memory_cost=64MiB`, `parallelism=4`)
- Per-account salts, no plaintext or reversible formats
- Always-available and break-glass accounts have independently rotatable credentials

**Role-Based Access Matrix** (four roles):

| Feature                    | dev | admin | user | readonly |
| -------------------------- | --- | ----- | ---- | -------- |
| View application data      | ✓   | ✓     | ✓    | ✓        |
| Modify application data    | ✓   | ✓     | ✓    | ✗        |
| User management            | ✓   | ✓     | ✗    | ✗        |
| Configuration management   | ✓   | ✓     | ✗    | ✗        |
| Debugging/diagnostics      | ✓   | ✗     | ✗    | ✗        |
| System logs access         | ✓   | ✓     | ✗    | ✗        |
| Break-glass account mgmt   | ✓   | ✗     | ✗    | ✗        |
| Always-available acct mgmt | ✓   | ✗     | ✗    | ✗        |

**Lockout Enforcement**:

- Standard accounts: block after 5 consecutive failures, require admin unblock
- Always-available accounts: 5-minute cooldown auto-unblock mechanism
- Break-glass accounts: same lockout rules but recoverable via alternate emergency account

**Preference Linkage**:

- Each account references `preferences_id` linking to `user_preferences` namespace
- Session binds to preferences immediately after authentication
- No cross-user preference leakage possible

**Reset/Unblock Flows**:

- Admin-triggered resets via CLI (`rfu_admin.py`) or GUI admin panel
- Justification required, dual confirmation, out-of-band credential delivery
- All actions emit `AdminActionAudit` entries with actor, target, timestamps

**Always-Available Accounts** (Constitution §VII.17):

- Two accounts (one dev, one admin) provisioned during database initialization
- Protected via `is_always_available=true` flag, non-deletable/non-deactivatable
- Password initialization via secure operator procedure, never hard-coded

**Break-Glass Emergency Access** (Constitution §VII.18):

- Two accounts (one dev, one admin) disabled by default
- Enablement requires explicit CLI flag or environment variable
- Usage triggers enhanced audit entries and mandatory password rotation
- Credentials stored offline (sealed envelope or secure vault)

### Safety & Data Integrity (Principle II) ✓

- No destructive operations on protected accounts without explicit override
- All account modifications require confirmation and emit audit entries

### Test-Driven Quality (Principle III) ✓

- Existing contract tests (T023–T086) provide baseline coverage
- New tests required for: always-available account protection, break-glass usage logging, auto-unblock mechanism

### User Preference Management (Principle VI) ✓

- Preference profiles bound to authenticated sessions
- `share_preferences` flag controls export with anonymization
- Preference access gated by successful authentication

## Project Structure

### Documentation (this feature)

```text
specs/007-upgrade-to-login/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── always_available_accounts.yaml
│   ├── break_glass_accounts.yaml
│   ├── role_enforcement.yaml
│   └── lockout_prevention.yaml
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```text
src/
├── core/
│   └── auth/
│       ├── models/
│       │   ├── user_account.py       # Extended with is_always_available, is_break_glass
│       │   ├── break_glass_usage_log.py
│       │   └── always_available_account_config.py
│       ├── services/
│       │   ├── account_bootstrap_service.py   # Provisions protected accounts
│       │   ├── break_glass_service.py         # Break-glass session management
│       │   ├── lockout_prevention_service.py  # Auto-unblock mechanism
│       │   └── role_enforcement_service.py    # Four-role permission checks
│       └── repositories/
│           ├── break_glass_usage_log_repository.py
│           └── always_available_account_config_repository.py
├── rfu/
│   ├── admin_panel.py     # GUI admin tooling (extended)
│   └── login_dialog.py    # Login with break-glass support
└── scripts/
    └── admin/
        └── rfu_admin.py   # CLI tooling (extended)

tests/
├── contracts/
│   └── identity/
│       ├── test_always_available_accounts.py
│       ├── test_break_glass_accounts.py
│       ├── test_role_enforcement.py
│       └── test_lockout_prevention.py
├── integration/
│   └── identity/
│       ├── test_account_bootstrap.py
│       └── test_break_glass_flow.py
└── unit/
    └── auth/
        ├── test_account_bootstrap_service.py
        ├── test_break_glass_service.py
        └── test_lockout_prevention_service.py
```

**Structure Decision**: Extend existing `src/core/auth/` structure with new models, services, and repositories for always-available and break-glass account functionality. Tests follow existing contract/integration/unit hierarchy.

## Phase 0: Outline & Research

> All Technical Context items resolved - no NEEDS CLARIFICATION remain.

### Research Tasks Completed

1. **Always-Available Account Protection Patterns**

   - Decision: Use database-level `is_always_available` flag with application-layer enforcement
   - Rationale: Allows deletion guards at service layer while keeping DB schema simple
   - Alternatives: Separate table for protected accounts (rejected: adds complexity, harder to query)

2. **Break-Glass Credential Storage**

   - Decision: Credentials stored offline (sealed envelope or secure vault), enabled via CLI flag or env var
   - Rationale: Prevents accidental break-glass usage while ensuring emergency access
   - Alternatives: Always-enabled with strong passwords (rejected: too easy to misuse for routine ops)

3. **Auto-Unblock Mechanism for Always-Available Accounts**

   - Decision: 5-minute cooldown with timestamp tracking in `AlwaysAvailableAccountConfig`
   - Rationale: Balances security (lockout still triggers) with availability (auto-recovery)
   - Alternatives: Permanent immunity to lockout (rejected: reduces security for brute-force attacks)

4. **Role Migration from 006-baseline**

   - Decision: Rename `standard` → `user`, add `dev` and `readonly` roles
   - Rationale: `user` is clearer terminology; `dev` for debugging access; `readonly` for view-only
   - Alternatives: Keep `standard` (rejected: confusing naming, doesn't scale)

5. **Break-Glass Audit Enhancement**
   - Decision: Create dedicated `BreakGlassUsageLog` table with session tracking
   - Rationale: Enhanced audit separate from general `AdminActionAudit` allows specialized reporting
   - Alternatives: Extend `AdminActionAudit` (rejected: different retention and alerting requirements)

**Output**: research.md generated (see `specs/007-upgrade-to-login/research.md`)

## Phase 1: Design & Contracts

> Prerequisites: research.md complete ✓

### 1. Entities Extracted → `data-model.md`

**UserAccount** (extended from 006-baseline):

- `username`: str (unique, primary key)
- `password_hash`: str (Argon2id)
- `role`: enum {dev, admin, user, readonly}
- `account_status`: enum {pending, active, blocked, disabled}
- `is_always_available`: bool (default: false)
- `is_break_glass`: bool (default: false)
- `break_glass_justification`: str (nullable)
- `preferences_id`: int (FK to user_preferences)
- `login_attempts`: int (default: 0)
- `last_login`: datetime (nullable)
- `last_failed_login`: datetime (nullable)

**BreakGlassUsageLog** (new):

- `id`: int (primary key)
- `session_id`: str (FK to session_tokens)
- `account_username`: str (FK to user_accounts)
- `login_timestamp`: datetime
- `logout_timestamp`: datetime (nullable)
- `justification`: str
- `actions_performed`: json
- `post_usage_rotation_status`: enum {pending, completed, failed}

**AlwaysAvailableAccountConfig** (new):

- `username`: str (FK to user_accounts)
- `last_cooldown_start`: datetime (nullable)
- `cooldown_duration_minutes`: int (default: 5)
- `auto_unblock_enabled`: bool (default: true)

### 2. API Contracts Generated

**Contracts output to `specs/007-upgrade-to-login/contracts/`:**

- `always_available_accounts.yaml`: Bootstrap, protection guards, auto-unblock
- `break_glass_accounts.yaml`: Enable/disable, usage logging, rotation
- `role_enforcement.yaml`: Four-role permission matrix, role escalation
- `lockout_prevention.yaml`: Never-fully-locked invariant, recovery paths

### 3. Contract Tests Generated (must fail initially)

- `test_always_available_accounts.py`: Cannot delete/disable protected accounts
- `test_break_glass_accounts.py`: Usage triggers audit + rotation
- `test_role_enforcement.py`: Dev > Admin > User > Readonly permissions
- `test_lockout_prevention.py`: System never fully locked out

### 4. Test Scenarios from User Stories

| Story                                      | Test Scenario                          |
| ------------------------------------------ | -------------------------------------- |
| Locked admin recovers via always-available | `test_always_available_admin_recovery` |
| Break-glass login triggers audit           | `test_break_glass_audit_trail`         |
| Dev role accesses debugging                | `test_dev_role_debugging_access`       |
| Readonly denied write ops                  | `test_readonly_write_denied`           |
| Break-glass rotation enforced              | `test_break_glass_rotation_required`   |

### 5. Agent Context Update

Execute: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`

**Output**: data-model.md, /contracts/\*, failing tests, quickstart.md, .github/copilot-instructions.md updated

## Phase 2: Task Planning Approach

> This section describes what the /tasks command will do - DO NOT execute during /plan

**Task Generation Strategy**:

Based on Phase 1 design docs, the /tasks command will generate:

1. **Schema Migration Tasks** [P]:

   - Add `is_always_available`, `is_break_glass`, `break_glass_justification` to `user_accounts`
   - Add `role` enum expansion (dev, admin, user, readonly)
   - Create `break_glass_usage_log` table
   - Create `always_available_account_config` table
   - Migrate `standard` → `user` role

2. **Model Tasks** [P]:

   - `BreakGlassUsageLog` model with session tracking
   - `AlwaysAvailableAccountConfig` model with cooldown logic
   - Extend `UserAccount` model with new flags

3. **Repository Tasks** [P]:

   - `BreakGlassUsageLogRepository` with enhanced audit queries
   - `AlwaysAvailableAccountConfigRepository` with cooldown tracking

4. **Service Tasks**:

   - `AccountBootstrapService`: Provision protected accounts on DB init
   - `BreakGlassService`: Enable/disable, usage logging, rotation enforcement
   - `LockoutPreventionService`: Auto-unblock for always-available accounts
   - `RoleEnforcementService`: Four-role permission matrix

5. **Contract Test Tasks** [P]:

   - Always-available account protection tests
   - Break-glass usage logging tests
   - Role enforcement tests
   - Lockout prevention invariant tests

6. **Integration Test Tasks**:

   - Account bootstrap during fresh DB init
   - Break-glass session lifecycle
   - Auto-unblock after cooldown

7. **CLI/GUI Extension Tasks**:
   - `rfu_admin.py`: Break-glass enable/disable commands
   - `admin_panel.py`: Protected account indicators
   - `login_dialog.py`: Break-glass justification prompt

**Ordering Strategy**:

- TDD order: Tests before implementation
- Dependency order: Schema → Models → Repositories → Services → CLI/GUI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

> These phases are beyond the scope of the /plan command

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

> No Constitution Check violations - design fully aligns with constitution v1.3.0

| Consideration                                                           | Justification                                                                                                                                            |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Four account types (regular + always-available + break-glass × 2 roles) | Required by FR-004 through FR-015 and Constitution §VII.17-18; simpler alternatives (single admin) rejected because they create single points of failure |
| Dedicated `BreakGlassUsageLog` table                                    | Enhanced audit requirements differ from general `AdminActionAudit`; specialized reporting and retention needs justify separation                         |

## Progress Tracking

> This checklist is updated during execution flow

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command) — 75 tasks in tasks.md
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---

> Based on Constitution v1.3.0 - See `.specify/memory/constitution.md`
