# Feature Specification: Login & Password Baseline Integration

**Feature Branch**: `006-baseline-login-password`  
**Created**: 2025-11-15  
**Status**: Draft  
**Input**: User description: "Baseline login/password spec derived from fleeting notes"

## Execution Flow (main)

```text
1. Establish governed user account store with credential hashing, role metadata, and preference linkage.
2. Enforce interactive authentication flow (CLI + Hub) that validates credentials, records attempts, and blocks abusive sessions after 5 failures.
3. Load or initialize the user's preference profile post-authentication; propagate sharing and personalization controls.
4. Provide admin tooling for password resets, account unblocking, and bootstrap of new users plus session recovery.
5. Capture a full audit trail (login attempts, resets, preference exports) with retention ≥ 12 months and operator visibility.
6. Surface reporting/export hooks needed for compliance and downstream integration, deferring unresolved questions to planning.
```

## ⚡ Quick Guidelines

- ✅ Default experience must prioritize credential safety (Argon2-class hashing, no plaintext secrets) and graceful recovery without exposing hashes.
- ✅ Every login outcome (success, failure, block, reset, share) should be auditable with timestamps, actor identity, and originating surface (CLI/UI/service).
- ✅ Preference personalization is inseparable from identity: block access to user-specific configuration until the session is authenticated.
- ❌ Do not introduce password recovery flows that email or display secrets; only admin-triggered resets or future MFA tokens are allowed.
- 👥 Launch roles: `dev` (full debugging/diagnostics control), `admin` (full account + governance control), `user` (day-to-day utility access, replaces `standard`), and `readonly` (view-only access); see 007-upgrade-to-login for lockout prevention details.
- 🔒 Sharing/export tooling must strip identifiers unless `share_preferences` flag is explicitly enabled per user.
- 🛡️ Always-available and break-glass accounts ensure administrators are never locked out (see 007-upgrade-to-login spec for full requirements).

## Clarifications

### Session 2025-11-15

- Q: How many roles must RFU support at launch and what are their capabilities? → A: Four roles: `dev` (full debugging/diagnostics), `admin` (full control), `user` (regular users, replaces `standard`), and `readonly` (view-only access).
- Q: How are new RFU user accounts created and approved? → A: Users self-register but require admin approval before activation.
- Q: Should admin-triggered password resets immediately terminate existing sessions for that user? → A: Yes — reset immediately terminates all live sessions for that user.
- Q: What is the default idle timeout for authenticated sessions? → A: 10 minutes of inactivity.
- Q: How does the system prevent complete administrator lockout? → A: Two always-available accounts (one dev, one admin) and two break-glass accounts (one dev, one admin) ensure operators are never completely locked out. See 007-upgrade-to-login spec for complete requirements.

## User Scenarios & Testing _(mandatory)_

### Primary User Story

An RFU operator launches the hub, authenticates with their username and password, and immediately receives a personalized workspace powered by their stored preference profile. If they mistype credentials, their attempts are counted and the system blocks misuse automatically; an administrator can later reset or unblock them without ever seeing the password.

### Acceptance Scenarios

1. **Given** a registered user with an active account that is not blocked, **When** they supply the correct username/password within the hub login dialog, **Then** the system must hash the provided password, compare it to the stored hash, reset `login_attempts` to zero, record a successful login audit entry, and load the linked preferences into the session.
2. **Given** a user who has entered invalid credentials five consecutive times, **When** the fifth failure is recorded, **Then** the system must set `is_blocked = true`, deny further logins until an administrator intervenes, and emit an alert log so administrators know to unblock or investigate.
3. **Given** an unregistered operator on the hub or CLI with access to the registration surface, **When** they submit a unique username/password combo that passes validation, **Then** the system must create a `UserAccount` in `account_status = pending`, capture metadata/audit entries, return a "pending approval" confirmation, and prevent login until an administrator approves the account.

### Edge Cases

- What happens when a preference profile referenced by `preferences_id` is missing or corrupt? The system must fall back to defaults while still permitting login and flagging the discrepancy for admins.
- How does the system handle admins resetting a password for a user that is currently logged in? Password reset instantly revokes all active sessions for that user, forcing re-authentication under the new credential.
- What occurs if `share_preferences` is enabled but no anonymization metadata is present? Enforce minimum metadata (`shared_by`, `timestamp`, `purpose`) before export completes.
- How should duplicate self-registration attempts be handled? Return a descriptive error (both in hub UI and CLI) indicating the username already exists and keep existing pending/active record untouched.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST maintain a governed user account record containing `username`, Argon2-hashed `password_hash`, `login_attempts`, `is_blocked`, `role`, and `preferences_id`.
- **FR-002**: System MUST authenticate users via username/password, increment `login_attempts` on each failure, and automatically set `is_blocked = true` after the fifth consecutive failure.
- **FR-003**: System MUST reset the `login_attempts` counter on every successful login and persist the timestamp of last success for auditing.
- **FR-004**: System MUST bind each authenticated session to the user's preference profile so UI/tool settings load from `preferences_id` before unlocking any utilities.
- **FR-005**: System MUST provide administrators with a secure workflow to reset passwords that captures justification, requires dual confirmation, delivers the temporary credential via an approved out-of-band channel, and forces the user to set a new password at next login without ever disclosing the hash outside that channel.
- **FR-006**: System MUST allow administrators to unblock accounts (set `is_blocked = false` and `login_attempts = 0`) while capturing who performed the action and why.
- **FR-007**: System MUST log every login attempt (success/failure), block, unblock, password reset, and preference-sharing action with timestamps, actor identifiers, origin surface, and outcome, storing records for at least 12 months.
- **FR-008**: System MUST include a `share_preferences` flag that, when true, allows exporting a sanitized JSON bundle containing UI/settings data plus metadata (`shared_by`, `timestamp`, `purpose`) but never credential material.
- **FR-009**: System MUST provide self-registration for new users but hold accounts in a pending state until an admin explicitly approves and activates them.
- **FR-010**: System MUST support four roles: `dev` (manage accounts, debugging/diagnostics, break-glass account management), `admin` (manage accounts, reset/unblock, approve sharing), `user` (use utilities, manage own preferences), and `readonly` (view-only access with no write capabilities), ensuring sensitive actions remain dev/admin-only.
- **FR-011**: System MUST sanitize and validate usernames/passwords at entry time (length, allowed characters, password complexity) to prevent injection or weak secrets.
- **FR-012**: System MUST expose CLI hooks parallel to the UI so admins can perform resets/unblocks even when the GUI is unavailable.
- **FR-013**: System MUST support future MFA/token-based enhancements without reworking the storage model (e.g., ability to add secondary credential fields later).

### Non-Functional Requirements

- **NFR-001 (Login Performance)**: Average login round-trip (credential validation + preference hydration) MUST remain below 250 ms on the reference desktop profile defined in the plan.
- **NFR-002 (Preference Load Performance)**: Loading a user's preference profile after authentication MUST complete in under 1 second for datasets with at least 100 preference entries, keeping the GUI responsive.
- **NFR-003 (Audit Export Performance)**: Exporting a 30-day `AdminActionAudit` window through CLI tooling MUST finish within 2 seconds and produce a JSON bundle suitable for compliance ingestion.
- **NFR-004 (Session Safety)**: Idle timeout enforcement MUST trigger within 10 minutes of inactivity, immediately revoking session tokens and returning the user to the login surface.

### Key Entities _(include if feature involves data)_

- **UserAccount**: Represents an individual operator; attributes include username, hashed password, role (`dev`, `admin`, `user`, `readonly`), lockout counters, `account_status ∈ {pending, active, blocked, disabled}`, registration channel/metadata, last login metadata, linked `preferences_id`, `share_preferences`, `is_always_available` flag, `is_break_glass` flag, and `break_glass_justification` field.
- **PreferenceProfile**: Stores personalized UI and workflow settings keyed by `preferences_id`, plus metadata for sharing/export control.
- **AdminActionAudit**: Append-only ledger of sensitive actions (approve user, reset password, unblock, export preferences) with actor, target, timestamps, origin surface, and justification text.
- **ResetRequest**: Short-lived record that tracks password-reset operations or pending approvals, including initiator, reason, encrypted temporary secret, dispatch channel metadata, `secret_displayed_at`, and expiration.
- **PendingPreferenceAlert**: Flags corrupted or missing preference payloads for a user, ensuring log visibility and prompting recovery workflows.
- **SessionToken**: Represents an active authenticated session tied to a preference profile; the database stores only a hashed `session_handle`, while the raw secret stays in memory for logout/timeout enforcement. Break-glass sessions receive a special `session_type='break_glass'` marker.
- **BreakGlassUsageLog**: Tracks every break-glass session with `session_id`, `account_username`, `login_timestamp`, `logout_timestamp`, `justification`, `actions_performed`, and `post_usage_rotation_status`.
- **AlwaysAvailableAccountConfig**: Stores metadata about always-available accounts including `last_cooldown_start`, `cooldown_duration_minutes`, and `auto_unblock_enabled`.
- **AdminNotification**: Queue table for administrator notifications about break-glass usage and security incidents.

## Security & Identity Considerations _(mandatory when feature touches authentication or permissions)_

- Passwords must be hashed with Argon2id (memory-hard parameters tuned to RFU's desktop constraints) and salted per account; plaintext passwords may never be stored or logged.
- Lockout policy: automatically block after five consecutive failures, optionally escalating alerts to security operators after three failures within five minutes. Always-available accounts use a 15-minute cooldown auto-unblock mechanism instead of permanent blocking.
- Admin-triggered resets must issue temporary secrets out-of-band (e.g., console print or secure note), enforce a mandatory password change on next login, and immediately invalidate all active sessions for the affected user.
- Break-glass accounts: Two break-glass accounts (one dev, one admin) exist for emergency recovery. Usage triggers enhanced audit logging, immediate password rotation on session end, and administrator notifications. See 007-upgrade-to-login spec for complete requirements.
- Secure reset workflow: Admin flows (CLI + GUI) must prompt for justification, require explicit confirmation that the recipient was verified, and invoke the approved secret dispatcher to present the temporary credential exactly once (console render or encrypted secure-note file). Dispatcher activity must be captured in `ResetRequest` + `AdminActionAudit`, and secrets may never be logged, cached, or stored beyond the encrypted payload.
- Onboarding: users initiate self-registration, but no account becomes active until an administrator reviews and approves the request.
- Self-registration surfaces (hub UI + CLI script) must validate username/password locally, transmit only over secure channels, and immediately show the pending-state status so users know further access requires admin approval.
- Unblock actions must be auditable, require justification, and should optionally notify the affected user when the account is re-enabled.
- Roles: `dev` (accounts, debugging/diagnostics, break-glass management), `admin` (accounts, resets, exports), `user` (utility usage with own preferences), and `readonly` (view-only access); reporting-only roles are now covered by `readonly`.
- Always-available accounts: Two always-available accounts (one dev, one admin) are protected from deletion, disabling, or permanent blocking. They use auto-unblock after 15-minute cooldown instead of permanent lockout. See 007-upgrade-to-login spec for bootstrap and management requirements.
- Session handling must invalidate existing sessions when `is_blocked` toggles to true and enforce a 10-minute idle timeout before requiring re-authentication.
- Preference access is restricted to authenticated sessions whose `preferences_id` matches the requested configuration, preventing cross-user leakage.
- Audit retention: keep identity-related audit logs for ≥12 months with secure backup and review procedures; define who can access these logs and how breaches are reported within SLA.

---

## Review & Acceptance Checklist

> GATE: Automated checks run during main() execution

### Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

> Updated by main() during processing

- [x] User description parsed
- [x] Key concepts extracted
- [ ] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed

---
