# Phase 0 Research — Login & Password Baseline Integration

Motto: **"Better many smaller, detailed tasks than fewer large complex ones."** Each research thread below maps to an eventual bite-sized implementation task so we can parallelize safely and keep risk contained.

## Decision 1: Argon2id Parameter Baseline

- **Decision**: Use Argon2id with `time_cost=3`, `memory_cost=64 * 1024` (64 MiB), `parallelism=4`, `hash_len=32`, `salt_len=16`.
- **Rationale**: Balances security (memory-hard, resistant to GPU cracking) with expected desktop hardware (≥16 GB RAM). Matches Principle VII requirements and keeps login latency <200 ms on reference hardware.
- **Alternatives Considered**:
  - _bcrypt_: Mature but weaker against memory-hard cracking; would require cost tuning per platform.
  - _PBKDF2_: Easier to FIPS certify but significantly weaker vs. modern attackers.

## Decision 2: Admin Workflow Surfaces

- **Decision**: Provide both GUI modal (within RFU Hub) and CLI commands (`rfu-admin reset-password`, `rfu-admin unblock-user`, `rfu-admin approve-user`).
- **Rationale**: GUI covers day-to-day operations; CLI offers headless recovery when the hub cannot launch, satisfying constitution Principle VII tooling requirements.
- **Alternatives Considered**:
  - _GUI-only_: Blocks recovery on headless servers or break-glass automation.
  - _CLI-only_: Too unfriendly for non-technical admins; violates usability goals.

## Decision 3: Pending Account State Machine

- **Decision**: Introduce `account_status ∈ {pending, active, blocked, disabled}` with explicit timestamps (`created_at`, `activated_at`, `blocked_at`). Only admins can transition from pending→active.
- **Rationale**: Cleanly models self-registration plus admin approval while enabling auditing/reporting. Aligns with Principle VI preference linkage because pending accounts should not create preference rows until activated.
- **Alternatives Considered**:
  - _Boolean flags only_: Harder to audit lifecycle transitions, more error-prone.
  - _Separate tables for pending/active_: Extra migrations with little gain.

## Decision 4: Preference Recovery When Missing

- **Decision**: If `preferences_id` is missing/corrupt, bootstrap a fresh profile using system defaults, log a warning audit event, and notify admins asynchronously.
- **Rationale**: Users keep working (Principle I consistency) while ensuring admins can remediate. Pairs with subtle banner telling user their personalization reverted.
- **Alternatives Considered**:
  - _Login failure_: Blocks productivity for non-critical data loss.
  - _Silent fallback_: Hides data corruption from operators.

## Decision 5: Audit Retention & Review Hooks

- **Decision**: Store auth-related audit logs in `admin_action_audit` with daily rollups exported to `logs/identity/*.json` for 12-month retention; add lightweight CLI `rfu-admin audit --user <id>` to view history.
- **Rationale**: Constitution demands ≥12 months retention with operator visibility; daily rollups keep SQLite size manageable while still accessible.
- **Alternatives Considered**:
  - _Single monolithic table_: Risk of uncontrolled DB growth.
  - _External SIEM integration now_: Overkill for current scope; can be added later via export.

## Decision 6: Idle Timeout Enforcement Mechanics

- **Decision**: Background watchdog thread checks active sessions every 60 seconds and revokes any idle for ≥10 minutes; GUI receives signal to return to login screen, CLI commands exit with code `401` equivalent.
- **Rationale**: Provides deterministic enforcement without relying on user actions; conforms to clarified timeout requirement.
- **Alternatives Considered**:
  - _Event-driven only_: Risk of sessions lingering if no UI events fire (e.g., minimized app).
  - _Shorter intervals (<5 min)_: Unnecessarily disruptive for file utility workflows.

## Decision 7: Four-Role System

- **Decision**: Expand from two roles (`admin`, `standard`) to four roles: `dev` (developer/debugging), `admin` (user management), `user` (standard access, replaces `standard`), and `readonly` (view-only).
- **Rationale**: Provides graduated privilege levels. `dev` role enables debugging/diagnostics and break-glass account management. `readonly` role supports audit/compliance scenarios without write risk. `user` replaces `standard` for clarity.
- **Alternatives Considered**:
  - _Keep two roles_: Insufficient for debugging needs and compliance scenarios.
  - _More granular permissions_: Over-engineering for current scope; can be added later.

## Decision 8: Always-Available Accounts

- **Decision**: Maintain exactly two always-available accounts (one `dev`, one `admin`) that cannot be deleted, disabled, or permanently blocked. Use 15-minute cooldown auto-unblock instead of permanent lockout.
- **Rationale**: Ensures operators are never completely locked out. Cooldown prevents brute-force attacks while guaranteeing recovery path. Protected accounts bootstrap during system setup.
- **Alternatives Considered**:
  - _No protected accounts_: Risk of complete lockout scenario.
  - _Single protected account_: Insufficient redundancy; both dev and admin capabilities needed.

## Decision 9: Break-Glass Accounts

- **Decision**: Maintain exactly two break-glass accounts (one `dev`, one `admin`) separate from always-available accounts. Usage triggers enhanced audit logging, mandatory password rotation, and administrator notifications.
- **Rationale**: Provides emergency recovery path when always-available accounts are compromised. Justification requirement and immediate rotation prevent routine abuse. Notifications ensure visibility.
- **Alternatives Considered**:
  - _No break-glass accounts_: Complete lockout risk if always-available accounts compromised.
  - _Single break-glass account_: Insufficient for scenarios requiring both dev and admin capabilities.
  - _Shared break-glass with always-available_: Conflates routine and emergency access patterns.

## Decision 10: Lockout Prevention Guarantee

- **Decision**: System must never reach a state where all administrative access is blocked. CLI recovery path must work without GUI authentication. Always-available + break-glass accounts ensure this guarantee.
- **Rationale**: Critical business requirement from 005-Login notes. CLI path enables headless recovery for server/automation scenarios.
- **Alternatives Considered**:
  - _GUI-only recovery_: Blocks headless environments.
  - _External recovery tool_: Adds complexity and deployment overhead.
