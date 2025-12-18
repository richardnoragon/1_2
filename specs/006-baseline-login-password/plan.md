# Implementation Plan: Login & Password Baseline Integration

**Branch**: `006-baseline-login-password` | **Date**: 2025-11-15 | **Spec**: `specs/006-baseline-login-password/spec.md`
**Input**: Feature specification from `C:/Users/HP1/1_2/specs/006-baseline-login-password/spec.md`

## Execution Flow (/plan command scope)

```text
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

The feature introduces a governed identity subsystem for RFU: Argon2id-hashed credentials, lockout and auditing, self-service registration that lands accounts in a pending queue, admin approval tooling, session invalidation on password reset, 10-minute idle timeout, and preference linkage that ensures each authenticated user loads only their own personalization. The system now supports four roles (`dev`, `admin`, `user`, `readonly`) with lockout prevention via always-available and break-glass accounts (see 007-upgrade-to-login spec). Implementation will prioritize the motto **"better many smaller detailed dedicated tasks than fewer large complex ones"** by decomposing each workflow (registration, login, approval, reset, sharing, lockout prevention) into discrete service, CLI, GUI, and test tickets so work streams can advance independently without coupling.

## Technical Context

**Language/Version**: Python 3.12 (per `.venv312`)  
**Primary Dependencies**: PyQt5, sqlite3, argon2-cffi, pytest, mypy  
**Storage**: SQLite (`user_accounts`, `admin_action_audit`, `user_preferences`) with JSON fallback  
**Testing**: pytest (unit + contract + integration), mypy, flake8, manual GUI smoke  
**Target Platform**: Cross-platform desktop (Windows primary, macOS/Linux secondary)  
**Project Type**: Single desktop application (hub + CLI)  
**Performance Goals**: Login response < 250 ms on reference hardware, preference load < 1 s, audit export < 2 s for 30-day window  
**Constraints**: Lockout after 5 failures, Argon2id `time_cost=3/memory_cost=64MiB`, idle timeout 10 minutes, audit retention ≥12 months, no plaintext secrets  
**Scale/Scope**: Tens of admins, hundreds of operators, thousands of preference profiles, daily login volume < 10k

## Constitution Check

> GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

- **Principle II (Safety & Data Integrity)**: Plan includes dry-run friendly admin tools and ensures resets/unblocks are auditable with rollback; no destructive operations occur without explicit operator confirmation.
- **Principle VI (User Preference Management)**: Preference linkage handled via `preferences_id`, corruption fallback logged, sharing flows enforce metadata and anonymization.
- **Principle VII (Identity & Access Control)**: Argon2id hashing, lockout thresholds, audit retention, session invalidation, and admin approval lifecycle captured explicitly. Session secrets only live in memory/process vaults; the database stores a hashed `session_handle` for revocation & auditing so Principle VII's "tokens in memory only" clause remains satisfied. CLI + GUI tooling ensures reset/unblock controls exist even when hub unavailable. Four-role system (`dev`, `admin`, `user`, `readonly`) with graduated privileges. Always-available and break-glass accounts ensure operators are never completely locked out (see 007-upgrade-to-login spec).
- **Additional Constraints 14–16**: Database schema extensions (user_accounts/admin_action_audit/session) respect canonical storage, lockout counters updated atomically, idle timeout ≤10 minutes, audit retention ≥365 days.

No constitutional violations identified; complexity tracking not required at this stage. These gates will be rechecked after Phase 1 artifacts are produced.

### Identity & Access Control (Principle VII)

> Mandatory when the feature touches authentication, permissions, or user sessions.

- Document how credentials are stored (hashing algorithm + parameters), lockout enforcement, and audit logging.
- Describe the role-to-feature access matrix if a feature adds or changes user roles.
- Specify how the plan links authenticated users to preference namespaces (`preferences_id`).
- Capture reset/unblock flows, including operator tooling and manual verification steps.

## Project Structure

ios/ or android/

### Documentation (this feature)

```text
specs/006-baseline-login-password/
├── plan.md
├── spec.md
├── data-model.md
├── research.md
├── quickstart.md
├── contracts/
│   ├── authentication.yaml
│   └── contract-tests.md
└── tasks.md
```

### Source & Test Footprint (repository root)

```text
src/
├── core/
│   ├── auth/
│   ├── database/
│   ├── preferences/
│   └── log_manager.py
├── database/
│   └── database_manager.py
├── rfu/
│   ├── hub.py
│   ├── login_dialog.py
│   └── admin_panel.py
├── scripts/
│   ├── admin/
│   │   └── rfu_admin.py
│   └── migrations/
└── tools/

tests/
├── contracts/
│   └── identity/
├── integration/
│   ├── identity/
│   └── gui/
├── performance/
└── unit/
      └── auth/
```

**Structure Decision**: Single-project desktop application. Work will touch `src/core/auth`, `src/database`, `src/rfu`, admin scripts, and the identity-related folders in `tests/`.

## Phase 0: Outline & Research

1. **Extract unknowns**: Idle timeout enforcement, Argon2 parameter tuning, admin approval tooling, preference corruption fallback, audit retention strategy, and watchdog design were documented.
2. **Research tasks** (kept intentionally small per motto):
   - Argon2id parameter tuning vs desktop constraints.
   - Dual-surface admin tooling (GUI + CLI) best practices.
   - State machine for pending→active lifecycle.
   - Preference corruption response patterns.
   - Audit retention + export approach for SQLite.
   - Idle timeout watchdog implementation options.
3. **Findings** recorded in `research.md`, each with Decision/Rationale/Alternatives sections.

**Output**: `research.md` (complete).

## Phase 1: Design & Contracts

> Prerequisites: research.md complete

1. **Entities**: Documented in `data-model.md` (UserAccount, PreferenceProfile, SessionToken, ResetRequest, AdminActionAudit, PendingPreferenceAlert) with validation/state transitions to facilitate small focused tasks.
2. **Contracts**: `contracts/authentication.yaml` sketches logical service boundaries for login/logout/admin/sharing while `contract-tests.md` defines failing-first pytest modules to be generated.
3. **Quickstart**: Step-by-step validation flows in `quickstart.md` map directly to future integration tests and manual verifications.
4. **Agent context**: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` executed to sync new tech/decisions.

**Output**: `data-model.md`, `contracts/authentication.yaml`, `contracts/contract-tests.md`, `quickstart.md`, Copilot context updated. Contract tests will be materialized during `/tasks` as discrete, failing pytest modules to keep the codebase green until they are added intentionally.

## Phase 2: Task Planning Approach

> This section describes what the /tasks command will do - DO NOT execute during /plan

**Task Generation Strategy**:

- Use `.specify/templates/tasks-template.md` and the “many small tasks” motto as guardrails.
- Each entity (6) yields at least one schema/migration task + one repository/service task.
- Each contract scenario yields a contract test task, then an implementation task, totalling ~12 tasks for auth/admin endpoints.
- Quickstart steps map to integration validation tasks (at least 7) plus CLI/GUI wiring items.
- Additional tasks cover auditing, preference fallback, idle watchdog, and documentation updates.

**Ordering Strategy**:

- Strict TDD order: contract tests → service logic → GUI/CLI wiring → manual verification.
- Schema/migration tasks precede service tasks.
- Mark independent tasks (e.g., CLI vs GUI surfaces) with `[P]` for safe parallelization.

**Estimated Output**: 28-32 granular tasks in `tasks.md`.

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

> These phases are beyond the scope of the /plan command

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |

## Progress Tracking

> This checklist is updated during execution flow

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command) — **117 tasks created and completed**
- [x] Phase 4: Implementation complete — **All T001–T117 finished (2025-11-28)**
- [x] Phase 5: Validation passed — **All tests passing (lockout prevention, CLI recovery, integration)**

**Gate Status**:

- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (not needed)

**Completion Summary (2025-11-28)**:

All 117 tasks completed across 8 phases:

- Phase 3.1: Schema & Migrations (T001–T014)
- Phase 3.2: TDD Contract Tests (T015–T034)
- Phase 3.3: Core Models (T035–T040)
- Phase 3.4: Repositories (T041–T047)
- Phase 3.5: Services (T048–T068)
- Phase 3.6: CLI Integration (T069–T086)
- Phase 3.7: GUI Integration (T087–T108)
- Phase 3.8: Polish & Documentation (T109–T117)

Key deliverables:

- Four-role system (dev > admin > user > readonly)
- Lockout prevention with always-available and break-glass accounts
- CLI headless recovery for disaster scenarios
- Argon2id password hashing with secure salt management
- Session management with idle timeout
- Comprehensive audit logging

---

> Based on Constitution v1.2.0 - See `/memory/constitution.md`
