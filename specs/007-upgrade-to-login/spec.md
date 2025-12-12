# Feature Specification: Login & Password Integration Upgrade — Lockout Prevention

**Feature Branch**: `007-upgrade-to-login`  
**Created**: 2025-11-26  
**Status**: Draft  
**Input**: User description: "Upgrade to login and password integration which exists to prevent lock out using the four roles: dev, admin, user and readonly. Ensuring two users (one dev and one admin) are always active and can be used, as well as ensuring one dev and one admin always has break-glass access."

---

## Execution Flow (main)

```text
1. Parse user description from Input
   → Key concepts: four-role system, always-available accounts, break-glass accounts
2. Extract key concepts from description
   → Actors: dev, admin, user, readonly
   → Actions: lockout prevention, guaranteed access, emergency recovery
   → Data: role metadata, break-glass credentials, always-available account flags
   → Constraints: two accounts always active, break-glass usage audited
3. Fill User Scenarios & Testing section
   → Primary: administrator lockout recovery
   → Secondary: break-glass emergency access
4. Generate Functional Requirements
   → Each requirement is testable
5. Identify Key Entities
   → Extended roles, break-glass account tracking
6. Review Checklist passed
```

---

## ⚡ Quick Guidelines

- ✅ Focus on WHAT: Operators must never be completely locked out of the system
- ✅ Four distinct roles with graduated privileges: `dev`, `admin`, `user`, `readonly`
- ✅ Two accounts (one dev, one admin) are always available and cannot be disabled/blocked
- ✅ Two break-glass accounts (one dev, one admin) exist for emergency recovery
- ❌ Break-glass accounts should NOT be used for routine operations
- 👥 Written for business stakeholders managing RFU access control

---

## User Scenarios & Testing _(mandatory)_

### Primary User Story

An RFU administrator accidentally locks themselves out of the system after multiple failed login attempts. Rather than being permanently blocked, they can use the always-available admin account or, in an emergency, the break-glass admin account to regain access, unblock their primary account, and restore normal operations.

### Acceptance Scenarios

1. **Given** a registered admin user whose account has been blocked (5 failed attempts), **When** they attempt to log in with the always-available admin account, **Then** the system must authenticate them successfully, allow them to unblock the locked account, and log both the login and unblock actions with full audit trail.

2. **Given** both the primary admin and always-available admin accounts are compromised or inaccessible, **When** an authorized operator retrieves the break-glass admin credentials from secure storage and logs in, **Then** the system must authenticate them, flag the session as break-glass emergency access, immediately queue a password rotation requirement, and send alerts to all registered administrators.

3. **Given** a developer account with `dev` role privileges, **When** they access debugging/diagnostic features, **Then** the system must grant full debugging capabilities including log access, system diagnostics, and configuration inspection that are not available to `admin`, `user`, or `readonly` roles.

4. **Given** a user with `readonly` role, **When** they attempt to perform any write/modification operation, **Then** the system must deny the action with a clear permission error and log the attempted operation. Readonly users can authenticate via both CLI and GUI surfaces.

5. **Given** a break-glass account has been used, **When** the emergency session ends, **Then** the system must enforce immediate password rotation for the break-glass account and notify all administrators of the break-glass usage with audit details.

### Edge Cases

- What happens if someone attempts to delete or disable an always-available account? The system must reject the operation and log the attempt as a potential security incident.
- How does the system handle break-glass credential rotation after use? Automatic credential rotation is triggered, and all administrators receive notification of the new credential storage requirements.
- What happens if the break-glass credentials are used without a genuine emergency? Usage is logged and flagged for mandatory review; administrators can investigate and take disciplinary action if warranted.
- How does the system behave when the always-available dev and always-available admin accounts both fail simultaneously? This is a critical system failure scenario that should trigger break-glass access path and external alerting.

---

## Requirements _(mandatory)_

### Functional Requirements

#### Role System (Extended from 006-baseline)

- **FR-001**: System MUST support four distinct roles: `dev` (developer/debugging access), `admin` (user management and configuration), `user` (standard application usage, replaces previous `standard` role), and `readonly` (view-only access with no write capabilities).
- **FR-002**: System MUST enforce role-based access control where `dev` has the highest privilege level including all debugging/diagnostic capabilities, followed by `admin`, `user`, and `readonly` in descending order.
- **FR-003**: System MUST prevent role escalation except through explicit admin/dev approval with audit logging.

#### Always-Available Accounts

- **FR-004**: System MUST maintain exactly two always-available accounts: one with `dev` role and one with `admin` role.
- **FR-005**: System MUST prevent deletion, disabling, or permanent blocking of always-available accounts; any such attempt must be rejected and logged as a security incident.
- **FR-006**: System MUST allow temporary blocking of always-available accounts after 5 failed login attempts, but provide an automatic unblock mechanism after a configurable cooldown period (default: 5 minutes).
- **FR-007**: System MUST bootstrap always-available accounts during initial system setup with secure, randomly-generated credentials that must be changed on first login.
- **FR-008**: System MUST mark always-available accounts with a protected flag (`is_always_available=true`) that cannot be modified through normal account management interfaces.

#### Break-Glass Accounts

- **FR-009**: System MUST maintain exactly two break-glass accounts: one with `dev` role and one with `admin` role, separate from always-available accounts.
- **FR-010**: System MUST mark break-glass accounts with a distinct flag (`is_break_glass=true`) and enforce special handling for login, usage logging, and credential management.
- **FR-011**: System MUST flag all sessions initiated with break-glass credentials as emergency access and apply enhanced audit logging for every action performed.
- **FR-012**: System MUST enforce automatic password rotation for break-glass accounts upon session termination; new credentials are auto-generated but require mandatory human acknowledgment (by a dev-role user) before being sealed/exported to secure storage.
- **FR-013**: System MUST log all break-glass usage to the system audit log with enhanced detail (timestamp, username, IP address if available, session duration, actions performed); no active push notifications are required.
- **FR-014**: System MUST generate secure break-glass credentials during system bootstrap and export them via both console output (for immediate operator copy) and a secure note file in a configurable directory for offline storage.
- **FR-015**: Break-glass accounts MUST NOT be usable for routine operations; system SHOULD prompt for justification at login and log the stated reason.

#### Lockout Prevention

- **FR-016**: System MUST never reach a state where all administrative access is blocked simultaneously, ensured by the always-available and break-glass account mechanisms.
- **FR-017**: System MUST provide a CLI-accessible recovery path that does not require GUI authentication, ensuring headless recovery is always possible.
- **FR-018**: System MUST audit all lockout events and recovery actions with retention ≥12 months.

### Key Entities _(include if feature involves data)_

- **UserAccount** (extended): Adds `role ∈ {dev, admin, user, readonly}`, `is_always_available` flag, `is_break_glass` flag, and `break_glass_justification` field.
- **BreakGlassUsageLog**: Tracks every break-glass session with `session_id`, `account_username`, `login_timestamp`, `logout_timestamp`, `justification`, `actions_performed`, and `post_usage_rotation_status`. Serves as the audit trail for break-glass usage (replaces active notifications).
- **AlwaysAvailableAccountConfig**: Stores metadata about always-available accounts including `last_cooldown_start`, `cooldown_duration_minutes`, and `auto_unblock_enabled`.

---

## Security & Identity Considerations _(mandatory)_

### Credential Lifecycle

- All accounts use Argon2id hashing as defined in 006-baseline (`time_cost=3`, `memory_cost=64MiB`, `parallelism=4`).
- Always-available and break-glass accounts must have distinct, independently rotatable credentials.
- Break-glass credentials must be rotated after any use, with the new credentials securely communicated to authorized personnel.

### Role-to-Feature Access Matrix

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

### Authenticated Sessions

- Sessions link to `preferences_id` as defined in 006-baseline.
- Break-glass sessions receive a special `session_type='break_glass'` marker.
- Idle timeout (10 minutes) applies to all session types including break-glass.

### Audit & Compliance

- All login attempts (success, failure, lockout) logged with 12-month retention.
- Break-glass usage generates enhanced audit entries and administrator notifications.
- Lockout prevention measures are testable and verifiable through CLI and GUI.

---

## Migration from 006-baseline

### Role Migration

- `standard` role from 006-baseline maps to `user` role in this upgrade.
- Existing `admin` role retains all privileges.
- New `dev` and `readonly` roles are introduced.

### Schema Updates

- Add `is_always_available` and `is_break_glass` boolean columns to `user_accounts`.
- Add `break_glass_justification` text column.
- Create `break_glass_usage_log` table.
- Update role enum constraint to include all four roles.

### Backward Compatibility

- Existing accounts with `standard` role are automatically migrated to `user` role.
- Existing `admin` accounts remain unchanged.
- Always-available and break-glass accounts are created during migration bootstrap.

---

## Clarifications

### Session 2025-11-26

- Q: How should break-glass usage notifications be delivered? → A: System log entry only (no active notification)
- Q: What should be the default cooldown period for always-available account auto-unblock? → A: 5 minutes
- Q: Who should perform break-glass credential rotation after session ends? → A: Automatic rotation with mandatory human acknowledgment before sealing
- Q: Should readonly role access both CLI and GUI? → A: Both CLI and GUI access allowed
- Q: How should bootstrap credentials be exported for secure storage? → A: Both console output and secure note file

---

## Review & Acceptance Checklist

> GATE: Automated checks run during main() execution

### Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

> Updated by main() during processing

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (none identified)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
